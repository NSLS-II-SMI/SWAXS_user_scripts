"""Human-run LIVE beam-down WAXS/OAV single-run acceptance and Tiled verification.

No operations at import. live_test(..., apply=True) yields real hardware commands.
SPDX-License-Identifier: BSD-3-Clause
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import replace

import bluesky.plan_stubs as bps
import numpy as np

from kapton_exposure import (
    LOG_DIRECTORY,
    ExposureMonitor,
    PressureIsolation,
    Settings,
    configure_diode,
    fast_shutter,
    profile_signals,
)
from kapton_single_run import kapton_single_run

log = logging.getLogger(__name__)


def live_test(ns, *, apply=False, duration_s=130, image_period_s=30, trip_after_s=None):
    """Real WAXS/OAV images + fast-shutter cycling, FE closed; ~5 pairs/130 s.

    Call RE(live_test(globals(), apply=True)). Isolated new test database, 1 Hz
    real scalar reads. Skips energy recovery and beam gating; pressure and FE
    closed checks are retained. Removes only the two known beam-dependent
    suspenders for this test and reinstalls exactly those previously installed.
    Temperature and all other suspenders remain in place.
    """
    if not apply:
        log.warning("Preview: real SAXS/WAXS 1 s + OAV, continuous TetrAMM; images every %s s for %s s; fast shutter opens, "
                    "is checked/reopened, then closes. FE must stay CLOSED. New SQLite log; "
                    "no energy moves. Use apply=True to execute.", image_period_s, duration_s)
        if trip_after_s is not None:
            log.warning("At %s s: REAL GV6/GV7 closure; 30 s later IV1 closure, turbo OFF, water CLOSED. "
                        "Images/logging continue after isolation.", trip_after_s)
        return
    if duration_s < image_period_s * 2:
        raise ValueError("Test must span at least two image periods")
    re = ns["RE"]
    monitor = None
    guard = None
    trip_timer = None
    removed = []
    ident = "kapton_beamdown_" + time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    cfg = replace(Settings(), image_period_s=image_period_s)
    signals = profile_signals(ns)
    # Reads only before suspenders are changed or any shutter is opened.
    if signals["fe"].get(timeout=2, connection_timeout=2) != 1:
        raise RuntimeError("Close FE first: live beam-down test requires FE closed readback=1")
    if trip_after_s is not None and not 0 < trip_after_s < duration_s-40:
        raise ValueError("Trip test needs >40 seconds after its scheduled trip")
    try:
        for name in ("susp_beam", "susp_smi_shutter"):
            suspender = ns.get(name)
            if suspender is not None and suspender in re.suspenders:
                re.remove_suspender(suspender)
                removed.append(suspender)
        yield from configure_diode(ns["pin_diode_ext"])
        monitor = ExposureMonitor(signals, cfg, LOG_DIRECTORY / (ident + ".sqlite"),
                                  specimen=ident, photon_open=ns["ph_shutter"].open_val,
                                  photon_closed=ns["ph_shutter"].close_val).start()
        guard = PressureIsolation(monitor, fs=ns["fs"], chamber=ns["chamber_pressure"]).start()
        if trip_after_s is not None:
            trip_timer = threading.Timer(trip_after_s, guard.request_trip,
                                         args=({"acceptance_test": "scheduled real shutdown"},))
            trip_timer.start()
        uids = yield from kapton_single_run(
            monitor, fs=ns["fs"], saxs_detector=ns["pil2M"], waxs_detector=ns["pil900KW"], oav=ns["OAV_writing"],
            experiment_id=ident, beam_down_test=True, duration_s=duration_s,
            md={"purpose": "LIVE beam-down single-run hardware acceptance", "test_id": ident,
                "trip_test": trip_after_s is not None, "tetram": True, "saxs": True})
        log.warning("LIVE acceptance finished: run=%s database=%s; verify through Tiled next", uids, monitor.database)
        return uids
    finally:
        try:
            if monitor is not None:
                yield from fast_shutter(ns["fs"], False, monitor=monitor)
                yield from bps.sleep(1.2)
        finally:
            if trip_timer is not None:
                trip_timer.cancel()
            if guard is not None and guard.tripped.is_set():
                log.warning("Trip test: monitor and latched guard remain running in ns['test_monitor']/ns['test_guard']")
                ns["test_monitor"], ns["test_guard"] = monitor, guard
            elif monitor is not None:
                if guard is not None:
                    guard.stop()
                monitor.close()
            for suspender in removed:
                re.install_suspender(suspender)


def verify_tiled(run, *, read_images=True):
    """Read-only checks on ONE Tiled BlueskyRun; no raw filesystem access.

    Run after the Tiled writer has finished. Returns/prints a compact summary;
    raises on missing image pairs, scalar ID gaps, timestamps, or pending rows.
    read_images=True reads only first/last frames per image field, paced 0.2 s.
    """
    md = run.metadata
    assert md["start"].get("beam_down_test") is True, "Not the beam-down test run"
    assert md.get("stop", {}).get("exit_status") == "success", "Run did not finish successfully"
    assert {"primary", "scalars", "session_summary"} <= set(run), "Required streams missing"
    primary = run["primary"]["data"]
    fields = list(primary)
    images = [key for key in fields if key.endswith("_image")]
    assert any(key.startswith("pil900KW") for key in images), "WAXS image field missing"
    if md["start"].get("saxs"):
        assert any(key.startswith("pil2M") for key in images), "SAXS image field missing"
    assert any(key.startswith("OAV_writing") for key in images), "OAV image field missing"
    walls = np.asarray(primary["kapton_trigger_wall"].read()).ravel()
    reopened = np.asarray(primary["kapton_fast_reopened"].read()).ravel()
    post_trip = (np.asarray(primary["kapton_post_trip"].read()).ravel().astype(bool)
                 if "kapton_post_trip" in fields else np.zeros(len(reopened), dtype=bool))
    assert np.all(reopened[~post_trip] == 1), "Shutter reopen not confirmed per image"
    assert np.all(reopened[post_trip] == 0), "Plan reopened shutter after trip"
    if md["start"].get("trip_test"):
        assert np.any(post_trip), "No post-trip images saved"
    assert len(walls) >= 3 and np.all(np.diff(walls) > 0), "Need >=3 distinct image pairs"
    scalars = run["scalars"]["data"]
    if md["start"].get("tetram"):
        assert "diode" in scalars, "TetrAMM missing"
        assert np.any(np.asarray(scalars["diode_valid"].read()) == 1), "No valid TetrAMM readings"
    ids = np.asarray(scalars["sample_id"].read()).ravel()
    sampled = np.asarray(scalars["sample_wall"].read()).ravel()
    assert len(ids) > len(walls) * 5, "Too few scalar events"
    assert np.all(np.diff(ids) == 1), "Scalar IDs have gaps/duplicates"
    assert np.all(np.diff(sampled) > 0), "Scalar source times not strictly increasing"
    period = float(np.median(np.diff(sampled)))
    assert .8 < period < 1.2, f"Unexpected scalar cadence: {period}"
    assert np.all(np.asarray(scalars["fe_state"].read()) == 0), "FE was not closed throughout test"
    summary = run["session_summary"]["data"]
    assert np.asarray(summary["scalars_pending_ids"].read()).item() == 0, "Unexported scalar backlog"
    assert np.asarray(summary["session_images"].read()).item() == len(walls), "Image count mismatch"
    assert np.asarray(summary["scalars_exported_id"].read()).item() == ids[-1], "Export cursor mismatch"
    assert sampled[0] <= walls[0] and sampled[-1] >= walls[-1], "Scalar coverage does not span images"
    beam = np.asarray(scalars["beam_s"].read()).ravel()
    assert np.all(beam == 0), "Dark test must never accrue beam time"
    fast = np.asarray(scalars["fast_state"].read()).ravel()
    idle = np.ones(len(sampled), dtype=bool)
    for wall in walls:
        idle &= (sampled < wall-1) | (sampled > wall+8)
    idle &= (sampled > walls[0]+8) & (sampled < walls[-1]-1)
    assert np.any(idle), "No between-image samples to check shutter hold-open"
    inhibited = (np.asarray(scalars["exposure_inhibited"].read()).ravel().astype(bool)
                 if "exposure_inhibited" in scalars else np.zeros(len(fast), dtype=bool))
    assert np.all(fast[idle & ~inhibited] == 1), "Fast shutter did not stay open between image pairs"
    assert np.all(fast[idle & inhibited] == 0), "Fast shutter remained open after trip between images"
    assert np.asarray(summary["operations_pending_ids"].read()).item() == 0, "Unexported operation backlog"
    if md["start"].get("trip_test"):
        isolation = run["isolation"]["data"]
        detail = [json.loads(v) for v in np.asarray(isolation["isolation_details"].read()).ravel()]
        times = np.asarray(isolation["isolation_wall"].read()).ravel()
        phases = {record["status"]: (stamp, record) for stamp, record in zip(times, detail)}
        assert "closed" in phases, "Pump/water shutdown not completed successfully within test run"
        assert phases["pump_gate_close_attempted"][0] - phases["boundaries_closed"][0] >= 30, "Pump delay was too short"
        assert phases["turbo_disable_attempted"][0] >= phases["pump_gate_close_attempted"][0]
        assert all(r["confirmed"] for r in phases["closed"][1]["results"])
        assert sampled[-1] > phases["closed"][0], "No scalar coverage after pump/water shutdown"
    raw_shapes = {}
    for key in images:
        node = primary[key]
        shape = tuple(node.structure().shape)
        assert shape[0] == len(walls), f"{key}: wrong event dimension {shape}"
        raw_shapes[key] = shape
        if read_images:
            for index in (0, len(walls)-1):
                image = np.asarray(node.read(slice=index))
                assert image.size > 100 and np.isfinite(image).any(), f"{key}: unresolved/empty image"
                time.sleep(.2)
    result = {"run_uid": md["start"]["uid"], "scan_id": md["start"].get("scan_id"),
              "image_pairs": len(walls), "scalar_samples": len(ids), "median_scalar_period_s": period,
              "median_image_period_s": float(np.median(np.diff(walls))), "image_shapes": raw_shapes,
              "first_sample_id": int(ids[0]), "last_sample_id": int(ids[-1]), "passed": True}
    log.warning("Tiled acceptance:\n%s", json.dumps(result, indent=2))
    return result


def live_isolation_test(guard, *, apply=False):
    """Optional REAL staged shutdown including turbo OFF and cooling water CLOSED.

    Uses an explicit test trip, not fake gauge readings or changed ceilings.
    Requires a separately started monitor + armed PressureIsolation. Leaves the
    guard latched and monitor running; never automatically reopens valves.
    """
    if not apply:
        log.warning("Preview: latch trip, close fast shutter/GV6/GV7; wait 30 s, close IV1, turbo OFF, water CLOSED; "
                    "verify all readbacks and continued pressure logging. apply=True executes.")
        return
    monitor = guard.monitor
    monitor._read("fe", monitor.signals["fe"])
    if monitor.health()["states"]["fe"] is not False:
        raise RuntimeError("Isolation acceptance requires FE confirmed CLOSED")
    guard.assert_untripped()
    # Stop only the watcher to avoid concurrent test/pressure trips. _trip itself
    # still commands the same real close-only response under test.
    guard.stop_event.set()
    guard.thread.join(timeout=2)
    if guard.thread.is_alive():
        raise RuntimeError("Guard is already isolating; wait for it to finish")
    before = monitor.latest["wall"]
    guard.thread = threading.Thread(target=guard._trip,
                                   args=({"acceptance_test": "human-requested live closures"},),
                                   name="kapton-live-isolation-test", daemon=True)
    guard.thread.start()
    while guard.thread.is_alive():
        yield from bps.sleep(.2)
    yield from bps.sleep(1.2)
    assert guard.result and all(r["confirmed"] for r in guard.result), guard.result
    assert monitor.latest["wall"] > before, "Pressure logger did not continue"
    log.warning("Live isolation passed: %s; monitor remains running and guard remains latched", guard.result)
    return guard.result

"""Opt-in single-run Kapton experiment. Existing kapton_images is untouched.

Load via %run after kapton_exposure.py, or import from this directory.
SPDX-License-Identifier: BSD-3-Clause
"""

import json
import math
import time
import uuid

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import Msg
from ophyd import Signal
from smi_plans.session import JournalStream, SnapshotReadable, image_session

from kapton_exposure import (
    PRESSURES,
    _ready,
    _trigger_ready,
    accelerator_ready,
    fast_shutter,
    recover_fe_open,
)


def scalar_data(record_id, sample):
    data = {"sample_id": record_id, "sample_wall": sample["wall"],
            "elapsed_wall_s": sample["elapsed_wall_s"], "unobserved_s": sample["unobserved_s"],
            "pressure_ok": int(sample["pressure_ok"])}
    data["exposure_inhibited"] = int(sample.get("exposure_inhibited", False))
    data["isolation_phase"] = sample.get("isolation_phase", "unarmed")
    data.update(sample["totals"])
    for key in ("fe", "enabled", "ring_current", "ring_mode", "fast", "photon", "bpm", "incident_flux", "diode", *PRESSURES):
        row = sample["readings"].get(key, {})
        text = key in ("photon", "ring_mode")
        value = row.get("value", "" if text else float("nan"))
        data[key] = str(value) if text else float(value)
        data[key + "_timestamp"] = float(row.get("timestamp", float("nan")))
        data[key + "_severity"] = int(row.get("severity", -1))
        data[key + "_alarm_status"] = int(row.get("status", -1))
        data[key + "_error"] = str(row.get("error", ""))
        data[key + "_valid"] = int(key in sample["values"])
    for key in ("fe", "enabled", "fast", "photon", "bpm", "beam"):
        value = sample["states"][key]
        data[key + "_state"] = -1 if value is None else int(value)
    for key in PRESSURES:
        diagnostic = sample.get("pressure_diagnostics", {}).get(key, {})
        age = diagnostic.get("age_s")
        data[key + "_age_s"] = float("nan") if age is None else age
        data[key + "_quality"] = diagnostic.get("state", "legacy")
    return data


def scalar_journal(monitor, *, start_id=None):
    """Read committed SQLite records without sharing the logger's cursor.

    Default includes the current last sample to bracket the first image: earlier experiment segments
    remain in their original runs/SQLite. Pass start_id explicitly to backfill.
    """
    def high_water():
        with monitor.lock:
            return monitor.db.execute("SELECT COALESCE(MAX(id),0) FROM samples").fetchone()[0]

    def fetch(after, through, limit):
        with monitor.lock:
            rows = monitor.db.execute("SELECT id,wall,payload FROM samples WHERE id>? AND id<=? "
                                      "ORDER BY id LIMIT ?", (after, through, limit)).fetchall()
        return [(i, wall, scalar_data(i, json.loads(payload))) for i, wall, payload in rows]

    sample = scalar_data(0, monitor.latest)
    fields = {key: "string" if isinstance(value, str) else "number" for key, value in sample.items()}
    return JournalStream("scalars", SnapshotReadable("kapton_scalars", fields,
                         hinted_fields=("incident_flux", "diode", "waxs_pressure", "maxs_pressure")), fetch, high_water,
                         max(0, high_water()-1) if start_id is None else start_id)


def operation_journal(monitor):
    """Session events with fixed scalar schema and JSON details."""
    with monitor.lock:
        monitor.db.execute("CREATE TABLE IF NOT EXISTS session_operations "
                           "(id INTEGER PRIMARY KEY, wall REAL, kind TEXT, details TEXT)")
        monitor.db.commit()

    def high_water():
        with monitor.lock:
            return monitor.db.execute("SELECT COALESCE(MAX(id),0) FROM session_operations").fetchone()[0]

    def record(kind, **details):
        with monitor.lock:
            monitor.db.execute("INSERT INTO session_operations(wall,kind,details) VALUES (?,?,?)",
                               (time.time(), kind, json.dumps(details)))
            monitor.db.commit()

    def fetch(after, through, limit):
        with monitor.lock:
            rows = monitor.db.execute("SELECT id,wall,kind,details FROM session_operations "
                                      "WHERE id>? AND id<=? ORDER BY id LIMIT ?", (after, through, limit)).fetchall()
        return [(i, wall, {"operation_id": i, "operation_wall": wall, "operation": kind,
                           "operation_details": details}) for i, wall, kind, details in rows]

    fields = {"operation_id": "number", "operation_wall": "number", "operation": "string",
              "operation_details": "string"}
    return JournalStream("operations", SnapshotReadable("kapton_operations", fields), fetch, high_water,
                         high_water()), record


def isolation_journal(monitor):
    """Export the independent guard's durable stages/results during acquisition."""
    def high_water():
        with monitor.lock:
            return monitor.db.execute("SELECT COALESCE(MAX(id),0) FROM isolation").fetchone()[0]

    def fetch(after, through, limit):
        with monitor.lock:
            rows = monitor.db.execute("SELECT id,wall,payload FROM isolation WHERE id>? AND id<=? "
                                      "ORDER BY id LIMIT ?", (after, through, limit)).fetchall()
        return [(i, wall, {"isolation_id": i, "isolation_wall": wall, "isolation_details": payload})
                for i, wall, payload in rows]

    return JournalStream("isolation", SnapshotReadable("isolation", {"isolation_id": "number",
                         "isolation_wall": "number", "isolation_details": "string"}), fetch, high_water,
                         max(0, high_water()-1))


def pressure_journal(monitor):
    """Independent pressure samples remain visible when the main scalar reader lags."""
    def high_water():
        with monitor.lock:
            return monitor.db.execute("SELECT COALESCE(MAX(id),0) FROM pressure_samples").fetchone()[0]

    def fetch(after, through, limit):
        with monitor.lock:
            rows = monitor.db.execute("SELECT id,wall,payload FROM pressure_samples WHERE id>? AND id<=? "
                                      "ORDER BY id LIMIT ?", (after, through, limit)).fetchall()
        return [(i, wall, {"pressure_sample_id": i, "pressure_sample_wall": wall, "pressure_details": payload})
                for i, wall, payload in rows]

    return JournalStream("pressure_samples", SnapshotReadable("pressure_samples", {
        "pressure_sample_id": "number", "pressure_sample_wall": "number", "pressure_details": "string"}),
        fetch, high_water, max(0, high_water()-1))


def kapton_single_run(monitor, *, fs, saxs_detector, waxs_detector, oav, energy=None,
                      experiment_id, duration_s=3*86400, start_sample_id=None,
                      beam_time_offset_s=0, beam_down_test=False, md=None):
    """One staged SAXS/WAXS/OAV run with continuous scalar/TetrAMM logging.

    Same live monitor, pressure guard and recovery as the legacy plan. Offset is
    explicit metadata/label correction, not a mutation of persisted counters.
    No new monitor/guard is started here. See SINGLE_RUN_ACCEPTANCE.md.
    beam_down_test=True bypasses beam/photon gating and energy recovery, but
    requires FE CLOSED and valid pressure on every readiness check. Never sets
    fake beam signals or credits dark acquisition as beam exposure.
    """
    if not experiment_id or not isinstance(experiment_id, str):
        raise ValueError("experiment_id is required")
    if not hasattr(getattr(oav, "tiff", None), "generate_datum"):
        raise ValueError("Use OAV_writing with TIFF asset support")
    if len({id(saxs_detector), id(waxs_detector), id(oav)}) != 3:
        raise ValueError("Supply distinct SAXS, WAXS and OAV detectors")
    if not math.isfinite(beam_time_offset_s) or beam_time_offset_s < 0:
        raise ValueError("beam_time_offset_s must be finite and nonnegative")
    if beam_down_test and (energy is not None or beam_time_offset_s != 0):
        raise ValueError("Beam-down testing takes no energy device or exposure correction")
    cfg = monitor.settings
    journal = scalar_journal(monitor, start_id=start_sample_id)
    operations, record = operation_journal(monitor)
    state = {"active": False, "recovered": None, "start": None, "image_id": ""}
    fields = {key: Signal(name="kapton_"+key, value="" if key == "image_id" else 0.0,
                          kind="hinted" if key == "beam_s" else "normal")
              for key in ("beam_s", "online_beam_s", "beam_end_s", "elapsed_s", "fast_open_s",
                          "trigger_wall", "beam_interrupted", "image_id", "fast_reopened", "post_trip")}
    summary = {"experiment_id": experiment_id, "offset_s": beam_time_offset_s,
               "sample_start_id": journal.cursor}

    def eligibility():
        snapshot, beam = _trigger_ready(monitor, allow_post_trip=True)
        if beam_down_test:
            monitor._read("fe", monitor.signals["fe"])
            snapshot["states"]["fe"] = monitor.snapshot()["states"]["fe"]
            if snapshot["states"]["fe"] is not False:
                raise RuntimeError("Live beam-down test requires FE confirmed closed")
            return snapshot, beam if snapshot.get("post_trip") else True
        return snapshot, beam and (snapshot.get("post_trip", False) or accelerator_ready(snapshot))

    def ready():
        snapshot, beam = eligibility()
        if snapshot.get("post_trip"):
            return beam
        if state["active"]:
            return beam  # monitor faults still raise; never move energy during an exposure
        if snapshot["states"]["fast"] is not True:
            raise RuntimeError("Unexpected idle fast-shutter closure")
        if (energy is not None and snapshot["states"]["fe"] is True and snapshot["states"]["enabled"] is True
                and accelerator_ready(snapshot)
                and snapshot["recovery_generation"] != state["recovered"]):
            record("fe_recovery_started", recovery_generation=snapshot["recovery_generation"])
            # The session is already non-rewindable. Legacy clear_checkpoint is
            # irreversible within a run and would prevent later idle resumes.
            recovery = bpp.msg_mutator(recover_fe_open(monitor, energy),
                                       lambda msg: Msg("null") if msg.command == "clear_checkpoint" else msg)
            state["recovered"] = yield from recovery
            record("fe_recovery_finished", recovery_generation=state["recovered"])
            snapshot, beam = eligibility()
        return beam and (energy is None or state["recovered"] == snapshot["recovery_generation"])

    def before():
        snapshot, beam = eligibility()
        if not beam or (not snapshot.get("post_trip") and energy is not None
                        and snapshot["recovery_generation"] != state["recovered"]):
            return False
        state.update(active=True, start=snapshot, image_id=str(uuid.uuid4()))
        values = {"beam_s": snapshot["totals"]["beam_s"] + beam_time_offset_s,
                  "online_beam_s": snapshot["totals"]["beam_s"],
                  "fast_open_s": snapshot["totals"]["fast_open_s"],
                  "elapsed_s": snapshot["elapsed_wall_s"], "trigger_wall": time.time(),
                   "image_id": state["image_id"], "post_trip": int(snapshot.get("post_trip", False))}
        for key, value in values.items():
            fields[key].put(value)
        monitor.image_record({"image_id": state["image_id"], "status": "pending",
                              "experiment_id": experiment_id, "start": snapshot, "single_run": True})
        record("image_started", image_id=state["image_id"], beam_s=values["beam_s"])
        yield from bps.null()
        return True

    def after():
        end, _ = _ready(monitor, require_fast=False, allow_post_trip=True)
        start = state["start"]
        interrupted = (end["beam_interruptions"] != start["beam_interruptions"]
                       or end["totals"]["unknown_beam_s"] > start["totals"]["unknown_beam_s"]
                       or end["states"]["beam"] is not True)
        fields["beam_interrupted"].put(int(interrupted))
        fields["beam_end_s"].put(end["totals"]["beam_s"] + beam_time_offset_s)
        guard = getattr(monitor, "isolation", None)
        if guard is not None and guard.tripped.is_set():
            fields["fast_reopened"].put(0)
            fields["post_trip"].put(1)
            yield from fast_shutter(fs, False, monitor=monitor)
            record("post_trip_image", image_id=state["image_id"])
        else:
            yield from fast_shutter(fs, True, monitor=monitor)
            fields["fast_reopened"].put(1)
            record("fast_shutter_reopened", image_id=state["image_id"])
        state["active"] = False
        monitor.image_record({"image_id": state["image_id"], "status": "interrupted" if interrupted else "complete",
                              "experiment_id": experiment_id, "single_run": True, "start": start, "end": end})

    def close():
        yield from fast_shutter(fs, False, monitor=monitor)
        record("fast_shutter_closed")
        # Ensure the next durable sample includes the final closed state.
        yield from bps.sleep(monitor.settings.sample_period_s + .2)
        guard = getattr(monitor, "isolation", None)
        if guard is not None and guard.tripped.is_set():
            record("pressure_isolation_latched", results=guard.result)

    def body():
        eligibility()
        guard = getattr(monitor, "isolation", None)
        if guard is None or not guard.thread.is_alive() or guard.tripped.is_set():
            raise RuntimeError("Arm PressureIsolation before starting the single-run experiment")
        isolation = isolation_journal(monitor)
        pressures = pressure_journal(monitor)
        for detector in (saxs_detector, waxs_detector):
            yield from bps.mv(detector.cam.acquire_time, cfg.exposure_s,
                              detector.cam.acquire_period, cfg.exposure_s+.1,
                              detector.cam.num_images, 1, timeout=10)
        yield from bps.mv(oav.cam.num_images, 1, timeout=10)
        yield from fast_shutter(fs, True, monitor=monitor)
        # Stage and open once inside the public session API.
        uid = yield from image_session(
            [oav, saxs_detector, waxs_detector], journals=[journal, operations, isolation, pressures], ready=ready, before_image=before,
            after_image=after, cleanup=close, image_readables=list(fields.values()),
            duration_s=duration_s, period_s=cfg.image_period_s,
            detector_timeout_s=cfg.detector_timeout_s,
            md={**(md or {}), "experiment_id": experiment_id, "specimen": monitor.specimen,
                "sample_name": monitor.specimen + "_beam{kapton_beam_s}s",
                "scan_name": "kapton_single_run", "beam_time_offset_s": beam_time_offset_s,
                "monitor_database": str(monitor.database), "pressure_limits": cfg.pressure_limits,
                "beam_down_test": beam_down_test,
                "scalar_timestamp_field": "sample_wall"})
        summary["run_uid"] = uid
        return uid

    try:
        return (yield from bpp.finalize_wrapper(body(), close()))
    finally:
        summary.update(status="session_finished", exported_sample_id=journal.cursor,
                       cutoff_sample_id=journal.high_water(), single_run=True)
        monitor.image_record(summary)

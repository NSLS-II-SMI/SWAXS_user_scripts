"""Offline tests: real RunEngine, in-memory signals, no EPICS connections."""

import json
import sqlite3
import threading
import time
from dataclasses import replace
from types import SimpleNamespace

import pytest
from bluesky import RunEngine
from bluesky import preprocessors as bpp
from bluesky.utils import FailedStatus
from ophyd import Component as Cpt
from ophyd import Device, Signal
from ophyd.status import DeviceStatus

from kapton_exposure import (
    ExposureClock,
    ExposureMonitor,
    Settings,
    kapton_images,
    profile_signals,
    recover_fe_open,
)


def settings(**kwargs):
    return Settings(beam_threshold=5, pressure_limits={k + "_pressure": 0.009 for k in ("waxs", "maxs", "saxs")},
                    pressure_units={k + "_pressure": "Torr" for k in ("waxs", "maxs", "saxs")}, **kwargs)


def clock():
    c = ExposureClock(settings(), photon_open="Open", photon_closed="Not Open", now=0)
    for k, v in {"fe": 0, "enabled": 1, "ring_current": 400, "ring_mode": "Operations",
                 "fast": 0, "photon": "Open", "bpm": 10}.items():
        c.update(k, v, 0)
    return c


def test_fe_changes_and_freshness_bound_exposure():
    c = clock()
    c.update("fe", 1, 1)
    c.advance(2)
    assert c.totals["fast_open_s"] == 2
    assert c.totals["beam_s"] == 1
    c.update("fe", 0, 2)
    c.advance(100)
    assert c.totals["beam_s"] == 2
    assert c.totals["fast_open_s"] == 3
    assert c.totals["unknown_beam_s"] == 97


def test_bpm_dark_and_unknown_state_do_not_count_beam():
    c = clock()
    c.update("bpm", 0, 1)
    c.update("fast", 3, 2)
    c.advance(3)
    assert c.totals["beam_s"] == 1
    assert c.totals["unknown_fast_s"] == 1
    assert c.totals["unknown_beam_s"] == 1


def test_brief_closure_between_polls_is_counted():
    c = clock()
    c.update("fast", 7, 0.2)
    c.update("fast", 0, 0.3)
    c.advance(1)
    assert c.totals["beam_s"] == pytest.approx(0.9)
    assert c.beam_interruptions == 1


class Command(Signal):
    def __init__(self, status, target, **kwargs):
        super().__init__(value=0, **kwargs)
        self.status = status
        self.target = target
        self.calls = 0

    def put(self, value, *, callback=None, **kwargs):
        self.calls += 1
        self.status.put(self.target)
        if callback:
            callback()


class Cam(Device):
    acquire_time = Cpt(Signal, value=0.1)
    acquire_period = Cpt(Signal, value=0.2)
    num_images = Cpt(Signal, value=1)


class Detector(Device):
    cam = Cpt(Cam, "", kind="omitted")
    counts = Cpt(Signal, value=100)

    def __init__(self, *args, shutter, fail=False, close_fe=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.shutter = shutter
        self.fail = fail
        self.close_fe = close_fe
        self.triggers = 0

    def trigger(self):
        self.triggers += 1
        status = DeviceStatus(self)

        def finish():
            if self.close_fe is not None:
                self.close_fe.put(1)
            self.shutter.put(7)  # real detector-controlled shutter behavior
            if self.fail:
                status.set_exception(RuntimeError("simulated detector failure"))
            else:
                status.set_finished()

        threading.Timer(0.12, finish).start()
        return status


@pytest.fixture
def rig(tmp_path):
    vals = {"fe": 0, "enabled": 1, "fast": 7, "photon": "Open", "bpm": 10, "incident_flux": 25, "diode": .1,
            "ring_current": 400, "ring_mode": "Operations",
            "waxs_pressure": 0.001, "maxs_pressure": 0.001, "saxs_pressure": 0.001}
    signals = {k: Signal(name=k, value=v) for k, v in vals.items()}
    fs = SimpleNamespace(status_pv=signals["fast"],
                         open_cpt=Command(signals["fast"], 0, name="open"),
                         close_cpt=Command(signals["fast"], 7, name="close"))
    cfg = settings(sample_period_s=0.1, image_period_s=0.5, stale_s=3)
    monitor = ExposureMonitor(signals, cfg, tmp_path / "experiment.sqlite", specimen="kapton",
                              photon_open="Open", photon_closed="Not Open").start()
    dets = [Detector(name="waxs", shutter=signals["fast"])]
    saxs = Detector(name="saxs", shutter=signals["fast"])
    yield SimpleNamespace(signals=signals, fs=fs, monitor=monitor, dets=dets, saxs=saxs, cfg=cfg)
    monitor.close()


def test_images_reopen_shutter_and_log_during_exposure(rig):
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.9))
    assert rig.fs.open_cpt.calls >= 2
    assert rig.signals["fast"].get() == 7
    assert rig.monitor.thread.is_alive()
    events = [doc for name, doc in docs if name == "event"]
    assert events and events[0]["data"]["kapton_beam_s"] >= 0
    assert "kapton_beam_s" in next(doc for name, doc in docs if name == "start")["sample_name"]
    samples = rig.monitor.db.execute("SELECT count(*) FROM samples").fetchone()[0]
    assert samples >= 6


def test_fe_closed_skips_both_detectors_but_monitor_continues(rig):
    rig.signals["fe"].put(1)
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.3))
    assert all(det.triggers == 0 for det in rig.dets)
    assert rig.monitor.snapshot()["totals"]["beam_s"] == 0
    assert rig.monitor.snapshot()["totals"]["fast_open_s"] > 0


def test_beam_returns_triggers_due_image(rig):
    rig.signals["fe"].put(1)
    threading.Timer(0.15, lambda: rig.signals["fe"].put(0)).start()
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.8))
    assert all(det.triggers == 1 for det in rig.dets)


def test_fe_closes_during_staging_no_trigger(rig):
    original = rig.dets[0].stage

    def stage():
        result = original()
        rig.signals["fe"].put(1)
        return result

    rig.dets[0].stage = stage
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.3))
    assert all(det.triggers == 0 for det in rig.dets)


def test_failure_closes_without_post_failure_reopen(rig):
    rig.dets[0].fail = True
    with pytest.raises(FailedStatus):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.4))
    assert rig.signals["fast"].get() == 7
    assert rig.fs.open_cpt.calls == 1
    assert rig.monitor.thread.is_alive()


def test_bad_pressure_prevents_opening(rig):
    rig.signals["waxs_pressure"].put(1)
    rig.monitor._pressure_sample()
    rig.monitor._sample()
    with pytest.raises(RuntimeError, match="Pressure"):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.3))
    assert rig.fs.open_cpt.calls == 0


@pytest.mark.parametrize("key,value,valid", [
    ("saxs_pressure", 0, True),
    ("saxs_pressure", -0.001, False),
    ("saxs_pressure", 0.009, False),
    ("waxs_pressure", 0, False),
    ("maxs_pressure", 0, False),
])
def test_saxs_below_range_zero_is_valid_only_for_saxs(rig, key, value, valid):
    rig.signals[key].put(value)
    rig.monitor._pressure_sample()
    rig.monitor._sample()
    assert rig.monitor.snapshot()["pressure_ok"] is valid


def test_saxs_zero_does_not_override_invalid_readback(rig):
    rig.monitor._accept("saxs_pressure", 0, time.time(), good=False)
    assert rig.monitor.snapshot()["pressure_ok"] is False


@pytest.mark.parametrize("key,value,severity,status,accepted", [
    ("photon", "Open", 1, 7, True),
    ("photon", "Not Open", 1, 7, True),
    ("photon", "Unknown", 1, 7, False),
    ("photon", "Open", 2, 7, False),
    ("photon", "Open", 1, 9, False),
    ("waxs_pressure", 0.01, 1, 7, False),
])
def test_only_recognized_photon_minor_state_alarm_is_accepted(rig, key, value, severity, status, accepted):
    assert rig.monitor._alarm_acceptable(key, value, severity, status) is accepted


@pytest.mark.parametrize("mode,allowed", [("Setup", False), ("Operations", True),
                                        ("Accel Studies", True), ("Beamline Studies", True),
                                        ("Failure", False)])
def test_ring_minor_state_validity_is_separate_from_recovery_permission(rig, mode, allowed):
    from kapton_exposure import accelerator_ready

    signal = SimpleNamespace(name="ring_mode", pvname="SR-OPS{}Mode-Sts", connected=True,
                             timestamp=time.time()-86400, metadata={"severity": 1, "status": 7},
                             get=lambda **kwargs: mode)
    rig.monitor.signals["ring_mode"] = signal
    reading = rig.monitor._read("ring_mode", signal)
    snapshot = rig.monitor.snapshot()
    assert snapshot["values"]["ring_mode"] == mode
    assert reading["severity"] == 1 and reading["status"] == 7
    assert accelerator_ready(snapshot) is allowed
    assert not rig.monitor._alarm_acceptable("ring_mode", mode, 2, 7)
    assert not rig.monitor._alarm_acceptable("ring_mode", mode, 1, 9)
    assert not rig.monitor._alarm_acceptable("ring_mode", "Unknown", 1, 7)


def test_photon_minor_state_alarm_allows_open_but_blocks_closed(rig):
    photon = SimpleNamespace(name="photon", pvname="fake:photon", connected=True,
                             timestamp=time.time(), metadata={"severity": 1, "status": 7},
                             enum_strs=("Open", "Not Open"))
    value = "Open"
    photon.get = lambda **kwargs: value
    rig.monitor.signals["photon"] = photon
    rig.signals["fast"].put(0)
    reading = rig.monitor._read("photon", photon)
    assert reading["severity"] == 1 and reading["status"] == 7
    assert rig.monitor.snapshot()["states"]["beam"] is True
    callback = rig.monitor._callback("photon")
    callback(value=1, timestamp=time.time())
    assert rig.monitor.snapshot()["states"]["photon"] is False
    assert rig.monitor.snapshot()["states"]["beam"] is False
    callback(value=0, timestamp=time.time())
    assert rig.monitor.snapshot()["states"]["photon"] is True
    callback(value=0, timestamp=time.time(), severity=2, status=7)
    assert rig.monitor.snapshot()["states"]["photon"] is None


def test_resume_counts_gap_as_unobserved_and_prevents_duplicate_logger(tmp_path):
    signals = {k: Signal(name=k, value=v) for k, v in {
        "fe": 0, "enabled": 1, "fast": 0, "photon": "Open", "bpm": 10, "incident_flux": 25, "diode": .1,
        "ring_current": 400, "ring_mode": "Operations",
        "waxs_pressure": 0.001, "maxs_pressure": 0.001, "saxs_pressure": 0.001}.items()}
    path = tmp_path / "state.sqlite"
    args = {"specimen": "kapton", "photon_open": "Open", "photon_closed": "Not Open"}
    monitor = ExposureMonitor(signals, settings(), path, **args).start()
    with pytest.raises(BlockingIOError):
        ExposureMonitor(signals, settings(), path, resume=True, **args)
    monitor.close()
    time.sleep(0.05)
    resumed = ExposureMonitor(signals, settings(), path, resume=True, **args)
    try:
        assert resumed.unobserved_s >= 0.05
        with sqlite3.connect(path) as db:
            saved = json.loads(db.execute("SELECT payload FROM samples ORDER BY id DESC LIMIT 1").fetchone()[0])
        assert resumed.clock.totals["beam_s"] == saved["totals"]["beam_s"]
    finally:
        resumed.close()


def test_stale_bpm_detected_even_when_connected(rig):
    rig.monitor._accept("bpm", 20, time.time() - 10)
    snapshot = rig.monitor.snapshot()
    assert snapshot["bpm_fresh"] is False
    assert snapshot["states"]["beam"] is None


def test_epics_reads_allow_two_seconds(rig):
    calls = []

    def get(**kwargs):
        calls.append(kwargs)
        if kwargs["timeout"] < 1:
            raise TimeoutError("simulated IOC needs a longer timeout")
        return 0

    signal = SimpleNamespace(pvname="fake:fe", get=get, timestamp=time.time(), metadata={})
    assert Settings().read_timeout_s == 2
    reading = rig.monitor._read("fe", signal)
    assert reading["value"] == 0
    assert calls == [{"timeout": 2.0, "connection_timeout": 2.0, "use_monitor": False}]


def test_configure_diode_matches_live_enum_labels_and_restarts_acquisition():
    from kapton_exposure import configure_diode

    class EnumSignal(Signal):
        def __init__(self, *, choices, **kwargs):
            self.choices = choices
            super().__init__(**kwargs)

        def check_value(self, value):
            if value not in self.choices:
                raise ValueError(f"Unknown enum label {value!r}")

        def set(self, value, **kwargs):
            assert kwargs["timeout"] == 5
            return super().set(value, **kwargs)

    diode = SimpleNamespace(
        acquire=Signal(name="acquire", value=1),
        acquire_mode=EnumSignal(name="mode", value="Single", choices=("Continuous", "Multiple", "Single")),
        trigger_mode=EnumSignal(name="trigger", value="Ext. trig.",
                                choices=("Free run", "Ext. trig.", "Ext. bulb", "Ext. gate")),
        averaging_time=Signal(name="averaging", value=.1),
    )
    changes = []
    diode.acquire.subscribe(lambda value, **kwargs: changes.append(value), run=False)
    RunEngine({})(configure_diode(diode))
    assert changes == [0, 1]
    assert diode.acquire_mode.get() == "Continuous"
    assert diode.trigger_mode.get() == "Free run"
    assert diode.averaging_time.get() == 1.0
    RunEngine({})(configure_diode(diode))
    assert changes == [0, 1]  # already configured: do not stop/start Acquire again


def test_diode_configuration_rejects_existing_pending_set_before_writes():
    from kapton_exposure import configure_diode

    diode = SimpleNamespace(acquire=Signal(name="acquire", value=1),
                            acquire_mode=Signal(name="mode", value="Continuous"),
                            trigger_mode=Signal(name="trigger", value="Free run"),
                            averaging_time=Signal(name="averaging", value=1))
    diode.acquire._set_thread = object()  # model an old stranded ophyd poller
    try:
        with pytest.raises(RuntimeError, match="previous ophyd set is still pending"):
            RunEngine({})(configure_diode(diode))
        assert diode.acquire.get() == 1
    finally:
        diode.acquire._set_thread = None


def test_logger_liveness_budget_does_not_extend_pressure_freshness(rig):
    with rig.monitor.lock:
        rig.monitor.latest["wall"] = time.time() - 4
        rig.monitor.clock.update("waxs_pressure", .001, time.monotonic(), valid_for=0)
        snapshot = rig.monitor.health()
    assert snapshot["pressure_ok"] is False


def test_loss_during_image_is_flagged_and_not_repeated(rig):
    rig.dets[0].close_fe = rig.signals["fe"]
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=0.7))
    assert all(det.triggers == 1 for det in rig.dets)
    event = next(doc for name, doc in docs if name == "event")
    assert event["data"]["kapton_beam_interrupted"] == 1
    assert rig.fs.open_cpt.calls == 2


def test_pressure_trip_during_idle_closes_shutter(rig):
    rig.signals["fe"].put(1)  # no image; hold shutter open
    threading.Timer(0.1, lambda: rig.signals["maxs_pressure"].put(1)).start()
    with pytest.raises(RuntimeError, match="Pressure"):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, duration_s=1))
    assert rig.signals["fast"].get() == 7
    assert rig.fs.close_cpt.calls == 1


def test_logger_runs_when_no_runengine_is_active(rig):
    before = rig.monitor.db.execute("SELECT count(*) FROM samples").fetchone()[0]
    time.sleep(0.25)
    after = rig.monitor.db.execute("SELECT count(*) FROM samples").fetchone()[0]
    assert after >= before + 2


def test_leave_open_only_on_success(rig):
    rig.signals["fe"].put(1)
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets,
                               duration_s=0.2, leave_open_on_success=True))
    assert rig.signals["fast"].get() == 0
    rig.signals["waxs_pressure"].put(1)
    rig.monitor._pressure_sample()
    rig.monitor._sample()
    with pytest.raises(RuntimeError, match="Pressure"):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets,
                                   duration_s=0.2, leave_open_on_success=True))
    assert rig.signals["fast"].get() == 7


def test_unrecognized_shutter_state_does_not_credit_beam(rig):
    rig.signals["fast"].put(4)
    snapshot = rig.monitor.snapshot()
    assert snapshot["states"]["fast"] is None
    assert snapshot["states"]["beam"] is None


class Energy(Device):
    pitch_feedback_disabled = Cpt(Signal, value="1")
    roll_feedback_disabled = Cpt(Signal, value="1")

    def __init__(self, *, bpm, **kwargs):
        super().__init__(**kwargs)
        self.bpm = bpm
        self.moves = []
        self.order = []
        self.finish_hook = None
        self.restore_flux = True
        self.roll_feedback_disabled.subscribe(self.feedback_changed, run=False)

    def feedback_changed(self, value, **kwargs):
        self.order.append(("feedback", value))
        if value == "0" and self.restore_flux:
            self.bpm.put(20)

    def set(self, value, *, timeout=None):
        assert self.pitch_feedback_disabled.get() == "1"
        assert self.roll_feedback_disabled.get() == "1"
        self.moves.append(value)
        self.order.append(("energy", value))
        status = DeviceStatus(self)
        if self.finish_hook:
            self.finish_hook()
        status.set_finished()
        return status

    def stop(self, *, success=False):
        self.order.append(("stop", success))


def test_fe_open_recovers_while_bpm_dark_and_bypasses_managed_object(rig):
    rig.signals["fe"].put(1)
    rig.signals["bpm"].put(0)
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    re = RunEngine({})

    def managed_guard(plan):
        def guard(msg):
            if msg.command == "set" and msg.obj is energy:
                raise AssertionError("Recovery accidentally used managed energy object")
            return msg
        return bpp.msg_mutator(plan, guard)

    re.preprocessors.append(managed_guard)
    threading.Timer(0.1, lambda: rig.signals["fe"].put(0)).start()
    re(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, energy=energy, duration_s=0.9))
    assert energy.moves == [6000]
    assert energy.order.index(("energy", 6000)) < energy.order.index(("feedback", "0"))
    assert all(det.triggers == 1 for det in rig.dets)
    assert re.preprocessors == [managed_guard]
    records = [json.loads(row[0]) for row in rig.monitor.db.execute("SELECT payload FROM recovery")]
    assert [record["status"] for record in records] == ["started", "complete"]


def test_short_fe_cycle_is_latched_between_plan_polls(rig):
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    re = RunEngine({})
    re(recover_fe_open(rig.monitor, energy))
    generation = rig.monitor.snapshot()["fe_openings"]
    rig.signals["fe"].put(1)
    rig.signals["bpm"].put(0)
    rig.signals["fe"].put(0)
    assert rig.monitor.snapshot()["fe_openings"] == generation + 1
    re(recover_fe_open(rig.monitor, energy))
    assert energy.moves == [6000, 6000]


def test_fe_closes_during_recovery_no_feedback_enable_or_image(rig):
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    energy.finish_hook = lambda: rig.signals["fe"].put(1)
    rig.signals["bpm"].put(0)
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets,
                               energy=energy, duration_s=0.3))
    assert energy.moves == [6000]
    assert ("feedback", "0") not in energy.order
    assert all(det.triggers == 0 for det in rig.dets)


def test_recovery_beam_timeout_closes_fast_shutter(rig):
    rig.monitor.settings = settings(sample_period_s=0.1, recovery_timeout_s=0.2)
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    energy.restore_flux = False
    rig.signals["bpm"].put(0)
    with pytest.raises(TimeoutError, match="no photon-shutter-open"):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets,
                                   energy=energy, duration_s=0.5))
    assert energy.moves == [6000]
    assert rig.signals["fast"].get() == 7
    assert rig.monitor.thread.is_alive()
    assert all(det.triggers == 0 for det in rig.dets)


def test_bpm2_default_threshold_is_strictly_above_ten():
    cfg = Settings()
    c = ExposureClock(cfg, photon_open="Open", photon_closed="Not Open", now=0)
    c.update("bpm", 10, 0)
    assert c.states(0)["bpm"] is False
    c.update("bpm", 10.01, 0)
    assert c.states(0)["bpm"] is True


class OpticalDetector(Device):
    cam = Cpt(Cam, "", kind="omitted")
    image_reference = Cpt(Signal, value="fake-optical-datum")

    def __init__(self, *, fail=False, **kwargs):
        super().__init__(**kwargs)
        self.tiff = SimpleNamespace(generate_datum=lambda *args: None)
        self.triggers = 0
        self.fail = fail

    def trigger(self):
        self.triggers += 1
        status = DeviceStatus(self)
        if self.fail:
            status.set_exception(RuntimeError("Optical camera failed"))
        else:
            status.set_finished()
        return status


def test_oav_same_event_preserves_optical_exposure(rig):
    oav = OpticalDetector(name="OAV_writing")
    oav.cam.acquire_time.put(0.025)
    oav.cam.acquire_period.put(0.05)
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, oav=oav, duration_s=0.4))
    assert oav.triggers == 1
    assert all(det.triggers == 1 for det in rig.dets)
    assert oav.cam.acquire_time.get() == 0.025
    assert oav.cam.acquire_period.get() == 0.05
    assert oav.cam.num_images.get() == 1
    event = next(doc for name, doc in docs if name == "event")
    assert {"OAV_writing_image_reference", "waxs_counts", "kapton_beam_s"} <= event["data"].keys()
    assert "saxs_counts" not in event["data"]
    assert rig.fs.open_cpt.calls == 2


def test_oav_skipped_with_fe_closed(rig):
    oav = OpticalDetector(name="OAV_writing")
    rig.signals["fe"].put(1)
    RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, oav=oav, duration_s=0.2))
    assert oav.triggers == 0
    assert all(det.triggers == 0 for det in rig.dets)


def test_oav_failure_closes_without_reopening(rig):
    oav = OpticalDetector(name="OAV_writing", fail=True)
    with pytest.raises(FailedStatus):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, oav=oav, duration_s=0.4))
    assert rig.signals["fast"].get() == 7
    assert rig.fs.open_cpt.calls == 1


def test_nonwriting_oav_is_rejected_before_shutter_opens(rig):
    oav = OpticalDetector(name="OAV")
    del oav.tiff
    with pytest.raises(ValueError, match="TIFF-writing"):
        RunEngine({})(kapton_images(rig.monitor, fs=rig.fs, detectors=rig.dets, oav=oav, duration_s=0.2))
    assert rig.fs.open_cpt.calls == 0


def test_profile_uses_bpm2_gate_and_bpm3_flux_without_tetram(monkeypatch):
    import kapton_exposure as module

    gauge = Signal(name="saxs_pressure", value=0.001)
    monkeypatch.setattr(module, "EpicsSignalRO", lambda pv, **kwargs: gauge)
    bpm = Signal(name="xbpm2_sumX", value=20)
    flux = Signal(name="xbpm3_sumX", value=30)
    ns = {"fe_shutter": SimpleNamespace(status=Signal(name="fe", value=0)),
          "smi_shutter_enable": Signal(name="enabled", value=1),
          "ring": SimpleNamespace(current=Signal(name="ring_current", value=400),
                                  mode=Signal(name="ring_mode", value="Operations")),
          "fs": SimpleNamespace(status_pv=Signal(name="fast", value=0)),
          "ph_shutter": SimpleNamespace(status=Signal(name="photon", value="Open")),
          "xbpm2": SimpleNamespace(sumX=bpm),
          "xbpm3": SimpleNamespace(sumX=flux),
          "pin_diode": SimpleNamespace(current2=SimpleNamespace(mean_value=Signal(name="diode", value=.1))),
          "chamber_pressure": SimpleNamespace(waxs=gauge, maxs=gauge)}
    signals = profile_signals(ns)
    assert signals["bpm"] is bpm
    assert signals["incident_flux"] is flux
    assert set(signals) == {"fe", "enabled", "fast", "photon", "bpm", "incident_flux", "diode",
                            "ring_current", "ring_mode",
                            "waxs_pressure", "maxs_pressure", "saxs_pressure"}


def test_bpm3_flux_is_logged_but_does_not_gate_beam(rig):
    rig.signals["fast"].put(0)
    rig.signals["incident_flux"].put(0)
    rig.monitor._sample()
    assert rig.monitor.latest["readings"]["incident_flux"]["value"] == 0
    assert rig.monitor.snapshot()["states"]["beam"] is True
    rig.monitor._accept("incident_flux", 100, time.time() - 10)
    snapshot = rig.monitor.snapshot()
    assert snapshot["incident_flux_fresh"] is False
    assert snapshot["states"]["beam"] is True
    rig.signals["bpm"].put(0)
    rig.monitor._accept("incident_flux", 100, time.time())
    assert rig.monitor.snapshot()["states"]["beam"] is False


def test_resume_pressure_change_is_explicit_audited_and_preserves_totals(rig, tmp_path):
    path = tmp_path / "pressure_change.sqlite"
    old_cfg = replace(rig.cfg, pressure_limits={k: 0.01 for k in rig.cfg.pressure_limits})
    args = {"specimen": "kapton", "photon_open": "Open", "photon_closed": "Not Open"}
    first = ExposureMonitor(rig.signals, old_cfg, path, **args)
    first.clock.totals["beam_s"] = 123.0
    first._sample()
    first.close()
    with pytest.raises(ValueError, match="settings.pressure_limits.*saved=0.01, requested=0.009"):
        ExposureMonitor(rig.signals, rig.cfg, path, resume=True, **args)
    resumed = ExposureMonitor(rig.signals, rig.cfg, path, resume=True,
                              resume_pressure_limits=True, **args)
    try:
        assert resumed.clock.totals["beam_s"] == 123.0
        record = json.loads(resumed.db.execute("SELECT payload FROM configuration_changes").fetchone()[0])
        assert record["previous"]["settings"]["pressure_limits"]["waxs_pressure"] == 0.01
        assert record["current"]["settings"]["pressure_limits"]["waxs_pressure"] == 0.009
    finally:
        resumed.close()
    with pytest.raises(ValueError, match="settings.beam_threshold"):
        ExposureMonitor(rig.signals, replace(rig.cfg, beam_threshold=99), path, resume=True,
                        resume_pressure_limits=True, **args)
    with pytest.raises(ValueError, match="specimen"):
        ExposureMonitor(rig.signals, rig.cfg, path, resume=True, resume_pressure_limits=True,
                        **{**args, "specimen": "different_holder"})


def test_enable_arriving_after_fe_open_recovers_without_waiting_for_flux(rig):
    rig.signals["enabled"].put(0)
    rig.signals["bpm"].put(0)
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    RunEngine({})(recover_fe_open(rig.monitor, energy))
    assert energy.moves == []
    generation = rig.monitor.snapshot()["recovery_generation"]
    rig.signals["enabled"].put(1)
    assert rig.monitor.snapshot()["recovery_generation"] == generation + 1
    RunEngine({})(recover_fe_open(rig.monitor, energy))
    assert energy.moves == [6000]
    rig.signals["enabled"].put(0)
    rig.signals["enabled"].put(1)
    assert rig.monitor.snapshot()["recovery_generation"] == generation + 2


def test_disable_during_energy_recovery_prevents_feedback_enable(rig):
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    energy.finish_hook = lambda: rig.signals["enabled"].put(0)
    RunEngine({})(recover_fe_open(rig.monitor, energy))
    assert energy.moves == [6000]
    assert ("feedback", "0") not in energy.order


def test_recovery_waits_for_375ma_and_non_setup_mode(rig):
    energy = Energy(name="energy", bpm=rig.signals["bpm"])
    rig.signals["ring_current"].put(0)
    rig.signals["ring_mode"].put("Setup")
    re = RunEngine({})
    re(recover_fe_open(rig.monitor, energy))
    assert energy.moves == []
    rig.signals["ring_current"].put(375)
    re(recover_fe_open(rig.monitor, energy))
    assert energy.moves == []
    rig.signals["ring_mode"].put("Operations")
    generation = rig.monitor.snapshot()["recovery_generation"]
    re(recover_fe_open(rig.monitor, energy))
    assert energy.moves == [6000]
    rig.signals["ring_current"].put(374.9)
    re(recover_fe_open(rig.monitor, energy))
    assert energy.moves == [6000]
    rig.signals["ring_current"].put(375)
    assert rig.monitor.snapshot()["recovery_generation"] == generation + 1


def test_install_reuses_profile_suspenders_without_duplicates():
    from kapton_exposure import install_acquisition_suspenders

    ring_suspender, enable_suspender = object(), object()
    installed = [ring_suspender]
    re = SimpleNamespace(state="idle", suspenders=installed, install_suspender=installed.append)
    ns = {"RE": re, "susp_beam": ring_suspender, "susp_smi_shutter": enable_suspender}
    install_acquisition_suspenders(ns)
    install_acquisition_suspenders(ns)
    assert installed == [ring_suspender, enable_suspender]
    re.state = "running"
    with pytest.raises(RuntimeError, match="idle prompt"):
        install_acquisition_suspenders(ns)


@pytest.mark.parametrize("mode", ["Operations", "Setup", "Accel Studies", "Beamline Studies",
                                  "Failure", "Maintenance", "Shutdown", "Unscheduled Ops", "Decay Mode Ops"])
def test_operations_and_approved_studies_modes_allow_recovery(mode):
    from kapton_exposure import accelerator_ready

    allowed = mode in ("Operations", "Beamline Studies", "Accel Studies")
    assert accelerator_ready({"values": {"ring_current": 375, "ring_mode": mode}}) is allowed
    assert not accelerator_ready({"values": {"ring_current": 374.9, "ring_mode": mode}})
    assert not accelerator_ready({"values": {"ring_current": 0, "ring_mode": mode}})


def test_weekend_migration_preserves_totals_and_audits_only_allowed_changes(rig, tmp_path):
    path = tmp_path / "migration.sqlite"
    pvnames = {"enabled": "SR:C12-EPS{PLC:1}Sts:ID_BE_Enbl-Sts",
               "diode": "XF:12ID:2{EM:Tetr1}Current2:MeanValue_RBV",
               "ring_current": "SR:C03-BI{DCCT:1}I:Real-I", "ring_mode": "SR-OPS{}Mode-Sts"}
    for key, pv in pvnames.items():
        rig.signals[key].name = pv
    args = {"specimen": "kapton", "photon_open": "Open", "photon_closed": "Not Open"}
    initial = ExposureMonitor(rig.signals, rig.cfg, path, **args)
    initial.clock.totals["beam_s"] = 17846.29573118966
    initial._sample()
    identity = json.loads(initial.db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()[0])
    for key in pvnames:
        del identity["signals"][key]
    identity["settings"]["pressure_limits"] = dict.fromkeys(rig.cfg.pressure_limits, .05)
    identity["settings"]["read_timeout_s"] = .2
    initial.db.execute("UPDATE metadata SET value=? WHERE key='identity'", (json.dumps(identity),))
    initial.db.commit()
    initial.close()
    resumed = ExposureMonitor(rig.signals, rig.cfg, path, resume=True, resume_weekend_update=True, **args)
    try:
        assert resumed.clock.totals["beam_s"] == 17846.29573118966
        assert resumed.db.execute("SELECT count(*) FROM samples").fetchone()[0] == 1
        assert resumed.db.execute("SELECT count(*) FROM configuration_changes").fetchone()[0] == 1
    finally:
        resumed.close()
    with pytest.raises(ValueError, match="beam_threshold"):
        ExposureMonitor(rig.signals, replace(rig.cfg, beam_threshold=99), path,
                        resume=True, resume_weekend_update=True, **args)

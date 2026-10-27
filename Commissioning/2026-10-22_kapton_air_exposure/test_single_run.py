import time

import pytest
from bluesky import RunEngine

from kapton_single_run import kapton_single_run
from test_kapton_exposure import OpticalDetector
from test_kapton_exposure import rig as _rig
from test_pressure_isolation import chamber

rig = _rig


@pytest.fixture(autouse=True)
def armed_guard(rig, monkeypatch):
    from kapton_exposure import PressureIsolation

    monkeypatch.setattr("kapton_exposure.PUMP_SHUTDOWN_DELAY_S", .1)
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber()).start()
    yield guard
    guard.stop()


def test_beam_down_one_run_and_no_beam_credit(rig):
    rig.signals["fe"].put(1)
    rig.signals["bpm"].put(0)
    oav = OpticalDetector(name="OAV_writing")
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0], oav=oav,
                         experiment_id="offline", beam_down_test=True, duration_s=1.8))
    descriptors = {doc["uid"]: doc["name"] for name, doc in docs if name == "descriptor"}
    events = [doc for name, doc in docs if name == "event"]
    scalar = [e for e in events if descriptors[e["descriptor"]] == "scalars"]
    images = [e for e in events if descriptors[e["descriptor"]] == "primary"]
    assert len(images) >= 3
    assert len([1 for name, _ in docs if name == "start"]) == 1
    assert all(e["data"]["beam_s"] == 0 for e in scalar)
    assert all(e["data"]["kapton_fast_reopened"] == 1 for e in images)
    assert rig.signals["fast"].get() == 7
    assert rig.monitor.thread.is_alive()
    ids = [e["data"]["sample_id"] for e in scalar]
    assert ids == list(range(ids[0], ids[-1]+1))
    assert all(e["timestamps"]["sample_wall"] == e["data"]["sample_wall"] for e in scalar)
    stream_docs = {doc["name"]: doc for name, doc in docs if name == "descriptor"}
    assert stream_docs["scalars"]["hints"]["kapton_scalars"]["fields"] == [
        "incident_flux", "diode", "waxs_pressure", "maxs_pressure"]
    assert stream_docs["operations"]["hints"]["kapton_operations"]["fields"] == []
    assert stream_docs["session_summary"]["hints"]["session_summary"]["fields"] == []
    primary_hints = stream_docs["primary"]["hints"]
    assert primary_hints["kapton_beam_s"]["fields"] == ["kapton_beam_s"]
    assert primary_hints["kapton_image_id"]["fields"] == []
    assert "photon_error" in stream_docs["scalars"]["data_keys"]
    assert "kapton_image_id" in images[0]["data"]


def test_live_beam_down_refuses_fe_open(rig):
    with pytest.raises(RuntimeError, match="FE confirmed closed"):
        RunEngine({})(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0],
                                       oav=OpticalDetector(name="OAV_writing"), experiment_id="test",
                                       beam_down_test=True, duration_s=.3))
    assert rig.fs.open_cpt.calls == 0


def test_journal_can_drain_pause_backlog_in_original_order(rig):
    from kapton_single_run import scalar_journal

    journal = scalar_journal(rig.monitor)
    start = journal.cursor
    time.sleep(.35)
    cutoff = journal.high_water()
    assert cutoff >= start+3

    def plan():
        import bluesky.plan_stubs as bps

        yield from bps.open_run()
        while journal.cursor < cutoff:
            yield from journal.drain(limit=2, through=cutoff)
        yield from bps.close_run()

    RunEngine({})(plan())
    assert journal.cursor == cutoff


def test_beam_down_fe_open_mid_session_closes_and_fails(rig):
    import threading

    rig.signals["fe"].put(1)
    threading.Timer(.4, lambda: rig.signals["fe"].put(0)).start()
    with pytest.raises(RuntimeError, match="FE confirmed closed"):
        RunEngine({})(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0],
                                       oav=OpticalDetector(name="OAV_writing"), experiment_id="test",
                                       beam_down_test=True, duration_s=1))
    assert rig.signals["fast"].get() == 7
    assert rig.monitor.thread.is_alive()


def test_verifier_uses_tiled_slice_api_and_checks_structure(monkeypatch):
    from types import SimpleNamespace

    import numpy as np

    import beam_down_acceptance as acceptance

    class Array:
        def __init__(self, value):
            self.value = np.asarray(value)

        def read(self, slice=None):
            return self.value if slice is None else self.value[slice]

        def structure(self):
            return SimpleNamespace(shape=self.value.shape)

    class Run(dict):
        def __init__(self, *args):
            super().__init__(*args)
            self.metadata = {"start": {"beam_down_test": True, "uid": "test"}, "stop": {"exit_status": "success"}}

    walls = np.array([2, 32, 62])
    scalars = {"sample_id": np.arange(1, 71), "sample_wall": np.arange(70),
               "fe_state": np.zeros(70), "beam_s": np.zeros(70), "fast_state": np.ones(70)}
    primary = {"kapton_trigger_wall": walls, "kapton_fast_reopened": [1, 1, 1],
               "pil900KW_image": np.zeros((3, 1, 20, 20)), "OAV_writing_image": np.ones((3, 1, 20, 20, 3))}
    summary = {"scalars_pending_ids": [0], "operations_pending_ids": [0],
               "session_images": [3], "scalars_exported_id": [70]}
    run = Run({name: {"data": {k: Array(v) for k, v in data.items()}} for name, data in
               (("primary", primary), ("scalars", scalars), ("session_summary", summary))})
    monkeypatch.setattr(acceptance.time, "sleep", lambda seconds: None)
    assert acceptance.verify_tiled(run)["passed"]
    run["primary"]["data"]["kapton_fast_reopened"] = Array([1, 0, 1])
    with pytest.raises(AssertionError, match="reopen"):
        acceptance.verify_tiled(run)


def test_pause_resume_keeps_one_run_and_no_replayed_scalar_ids(rig):
    import threading

    from bluesky.utils import RunEngineInterrupted

    rig.signals["fe"].put(1)
    re = RunEngine({})
    docs = []
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    timer = threading.Timer(.35, lambda: re.request_pause(defer=True))
    timer.start()
    with pytest.raises(RunEngineInterrupted):
        re(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0],
                            oav=OpticalDetector(name="OAV_writing"), experiment_id="pause_test",
                            beam_down_test=True, duration_s=1.8))
    timer.join()
    before = rig.monitor.latest["wall"]
    time.sleep(.3)
    assert rig.monitor.latest["wall"] > before
    re.resume()
    names = {d["uid"]: d["name"] for name, d in docs if name == "descriptor"}
    ids = [d["data"]["sample_id"] for name, d in docs if name == "event" and names[d["descriptor"]] == "scalars"]
    assert ids == list(range(ids[0], ids[-1]+1))
    assert len([1 for name, d in docs if name == "start"]) == 1


def test_trip_keeps_images_and_scalars_but_never_reopens(rig, armed_guard):
    import threading

    rig.signals["fe"].put(1)
    timer = threading.Timer(.7, lambda: rig.signals["waxs_pressure"].put(.01))
    timer.start()
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0],
                        oav=OpticalDetector(name="OAV_writing"), experiment_id="trip_images",
                        beam_down_test=True, duration_s=2))
    timer.join()
    events = [d for name, d in docs if name == "event" and "kapton_post_trip" in d["data"]]
    post = [d for d in events if d["data"]["kapton_post_trip"] == 1]
    assert len(post) >= 2
    assert all(d["data"]["kapton_fast_reopened"] == 0 for d in post)
    assert all("saxs_counts" in d["data"] and "waxs_counts" in d["data"] for d in post)
    assert armed_guard.shutdown_done.is_set()
    assert rig.monitor.thread.is_alive()
    assert rig.monitor.snapshot()["states"]["beam"] is False
    assert next(d for name, d in docs if name == "stop")["exit_status"] == "success"


def test_trip_between_detector_triggers_skips_partial_then_continues(rig, armed_guard):
    rig.signals["fe"].put(1)
    oav = OpticalDetector(name="OAV_writing")
    original = oav.trigger

    def trigger():
        result = original()
        if oav.triggers == 1:
            armed_guard.request_trip({"test": "between triggers"})
        return result

    oav.trigger = trigger
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(kapton_single_run(rig.monitor, fs=rig.fs, saxs_detector=rig.saxs, waxs_detector=rig.dets[0],
                        oav=oav, experiment_id="mid_trigger", beam_down_test=True, duration_s=1.5))
    post = [doc for name, doc in docs if name == "event" and "kapton_post_trip" in doc["data"]]
    assert len(post) >= 2
    assert all(doc["data"]["kapton_post_trip"] == 1 for doc in post)
    assert all(doc["data"]["kapton_fast_reopened"] == 0 for doc in post)
    assert rig.fs.open_cpt.calls == 1

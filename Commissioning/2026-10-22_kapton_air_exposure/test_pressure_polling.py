"""Dedicated pressure reader regression: reproduce a slow unrelated scalar read."""

import json
import threading
import time
from dataclasses import replace

import pytest

from kapton_exposure import PRESSURES, ExposureMonitor, PressureIsolation, Settings
from test_kapton_exposure import rig as _rig
from test_pressure_isolation import chamber

rig = _rig


def test_slow_scalar_read_does_not_expire_pressures_and_high_pressure_still_trips(rig, monkeypatch):
    monkeypatch.setattr("kapton_exposure.PUMP_SHUTDOWN_DELAY_S", .1)
    entered, release = threading.Event(), threading.Event()
    original = rig.signals["diode"].read

    def blocked_read():
        entered.set()
        assert release.wait(10)
        return original()

    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber()).start()
    monkeypatch.setattr(rig.signals["diode"], "read", blocked_read)
    try:
        assert entered.wait(2)
        old_sample = rig.monitor.latest["wall"]
        time.sleep(3.9)  # reproduces the ~3.87 s gap that caused the original trip
        assert rig.monitor.latest["wall"] == old_sample
        snapshot = rig.monitor.health()
        assert snapshot["pressure_ok"]
        assert all(snapshot["pressure_diagnostics"][k]["age_s"] < .5 for k in PRESSURES)
        assert not guard.tripped.is_set()
        rig.signals["waxs_pressure"].put(.009)
        assert guard.tripped.wait(2), "A slow diode must not delay a real vacuum trip"
        assert rig.monitor.latest["wall"] == old_sample
        rig.monitor._pressure_sample()  # wait for that pressure sweep's durable audit
        with rig.monitor.lock:
            records = rig.monitor.db.execute("SELECT payload FROM pressure_samples ORDER BY id DESC LIMIT 3").fetchall()
        assert any(json.loads(row[0])["pressure_diagnostics"]["waxs_pressure"]["state"] == "overpressure"
                   for row in records)
    finally:
        release.set()
        guard.stop()


def test_brief_transport_failure_keeps_only_unexpired_last_good_value(rig, monkeypatch):
    original = rig.signals["waxs_pressure"].read

    def fail():
        raise TimeoutError("simulated transient CA timeout")

    rig.monitor.settings = replace(rig.monitor.settings, pressure_stale_s=.8)
    rig.monitor._pressure_sample()  # install the shorter expiry for the last good sample
    monkeypatch.setattr(rig.signals["waxs_pressure"], "read", fail)
    rig.monitor._pressure_sample()
    snapshot = rig.monitor.snapshot()
    assert snapshot["pressure_ok"]
    assert snapshot["pressure_diagnostics"]["waxs_pressure"]["state"] == "read_error_grace"
    assert "simulated transient" in snapshot["pressure_diagnostics"]["waxs_pressure"]["reading"]["error"]
    time.sleep(.2)
    monkeypatch.setattr(rig.signals["waxs_pressure"], "read", original)
    rig.monitor._pressure_sample()
    assert rig.monitor.snapshot()["pressure_diagnostics"]["waxs_pressure"]["state"] == "ok"


def test_repeated_transport_failures_expire_without_refreshing_good_timestamp(rig, monkeypatch):
    monkeypatch.setattr("kapton_exposure.PUMP_SHUTDOWN_DELAY_S", .1)
    rig.monitor.settings = replace(rig.monitor.settings, pressure_stale_s=.5)
    rig.monitor._pressure_sample()
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber()).start()

    def fail():
        raise TimeoutError("persistent CA failure")

    monkeypatch.setattr(rig.signals["waxs_pressure"], "read", fail)
    try:
        assert guard.tripped.wait(2)
        with rig.monitor.lock:
            rows = rig.monitor.db.execute("SELECT payload FROM isolation ORDER BY id").fetchall()
        reason = next(json.loads(row[0])["reason"] for row in rows if json.loads(row[0])["status"] == "tripped")
        diag = reason["pressure_diagnostics"]["waxs_pressure"]
        assert diag["age_s"] >= .5
        assert diag["state"] == "stale_or_invalid"
        assert reason["pressure_stale_s"] == .5
    finally:
        guard.stop()


def test_invalid_gauge_value_has_no_communication_grace(rig, monkeypatch):
    monkeypatch.setattr(rig.signals["waxs_pressure"], "read", lambda: {
        "waxs_pressure": {"value": float("nan"), "timestamp": time.time()}})
    rig.monitor._pressure_sample()
    assert not rig.monitor.snapshot()["pressure_ok"]


def test_gauge_alarm_has_no_communication_grace(rig, monkeypatch):
    from types import SimpleNamespace

    signal = SimpleNamespace(pvname="fake:pressure", get=lambda **kwargs: .001,
                             timestamp=time.time(), metadata={"severity": 2, "status": 4})
    monkeypatch.setitem(rig.monitor.signals, "waxs_pressure", signal)
    rig.monitor._pressure_sample()
    snapshot = rig.monitor.snapshot()
    assert not snapshot["pressure_ok"]
    assert snapshot["pressure_diagnostics"]["waxs_pressure"]["state"] == "alarm"


def test_pressure_thread_is_joined_and_cannot_silently_die(rig):
    rig.monitor.pressure_stop_event.set()
    rig.monitor.pressure_thread.join(2)
    with pytest.raises(RuntimeError, match="pressure reader is not running"):
        rig.monitor.health()


def test_resume_new_pressure_timeout_preserves_data_and_counters(rig, tmp_path):
    path = tmp_path / "old_pressure.sqlite"
    args = {"specimen": "holder", "photon_open": "Open", "photon_closed": "Not Open"}
    first = ExposureMonitor(rig.signals, Settings(), path, **args)
    first.clock.totals["beam_s"] = 12345
    first._pressure_sample()
    first._sample()
    identity = json.loads(first.db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()[0])
    del identity["settings"]["pressure_stale_s"]
    first.db.execute("UPDATE metadata SET value=? WHERE key='identity'", (json.dumps(identity),))
    first.db.commit()
    first.close()
    with pytest.raises(ValueError, match="pressure_stale_s"):
        ExposureMonitor(rig.signals, Settings(), path, resume=True, **args)
    resumed = ExposureMonitor(rig.signals, Settings(), path, resume=True, resume_weekend_update=True, **args)
    try:
        assert resumed.clock.totals["beam_s"] == 12345
        assert resumed.db.execute("SELECT count(*) FROM samples").fetchone()[0] == 1
        assert resumed.db.execute("SELECT count(*) FROM configuration_changes").fetchone()[0] == 1
    finally:
        resumed.close()

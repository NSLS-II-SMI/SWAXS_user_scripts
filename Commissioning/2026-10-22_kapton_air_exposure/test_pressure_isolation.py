"""Offline close-only pressure guard checks; no EPICS or RunEngine required."""

import time
from types import SimpleNamespace

import pytest
from ophyd import Signal

from kapton_exposure import PressureIsolation, weekend_settings
from test_kapton_exposure import Command
from test_kapton_exposure import rig as _rig

rig = _rig


@pytest.fixture(autouse=True)
def short_shutdown_delay(monkeypatch):
    monkeypatch.setattr("kapton_exposure.PUMP_SHUTDOWN_DELAY_S", .1)


def valve(name, *, value="Open", fail=False):
    status = Signal(name=name + "_status", value=value)

    class CloseCommand(Command):
        def put(self, value, **kwargs):
            if fail:
                raise TimeoutError("simulated valve failure")
            return super().put(value, **kwargs)

    return SimpleNamespace(name=name, status=status, open_val="Open", close_val="Not Open",
                           cmd_actuate_val=1, close_cmd=CloseCommand(status, "Not Open", name=name + "_close"))


def chamber(*, isolated=False, fail=False):
    class TurboSignal(Signal):
        def put(self, value, *, wait=None, **kwargs):
            return super().put(value, **kwargs)

    return SimpleNamespace(upstream_valve=valve("gv6", fail=fail),
                           waxs_saxs_valve=valve("gv7", value="Not Open" if isolated else "Open"),
                           turbo_valve=valve("iv1"), turbo_enable=TurboSignal(name="turbo", value=1),
                           turbo_cooling_valve=valve("water"))


def wait_trip(guard):
    assert guard.tripped.wait(3)
    assert guard.shutdown_done.wait(3)
    guard.thread.join(3)
    assert not guard.thread.is_alive()


def test_trip_closes_all_valves_without_runengine_and_keeps_logging(rig):
    ch = chamber()
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=ch).start()
    try:
        rig.signals["fast"].put(0)
        rig.signals["waxs_pressure"].put(.06)
        wait_trip(guard)
        assert all(result["confirmed"] for result in guard.result)
        assert rig.signals["fast"].get() == 7
        for item in (ch.upstream_valve, ch.waxs_saxs_valve, ch.turbo_valve):
            assert item.status.get() == "Not Open"
        before = rig.monitor.latest["wall"]
        time.sleep(.2)
        assert rig.monitor.latest["wall"] > before
        rig.signals["waxs_pressure"].put(.001)
        with pytest.raises(RuntimeError, match="latched"):
            guard.assert_untripped()
        with pytest.raises(RuntimeError, match="guard explicitly"):
            rig.monitor.close()
    finally:
        guard.stop()


def test_one_failed_valve_does_not_prevent_other_closures(rig):
    ch = chamber(fail=True)
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=ch).start()
    try:
        rig.signals["maxs_pressure"].put(.06)
        wait_trip(guard)
        result = {r["device"]: r["confirmed"] for r in guard.result}
        assert result == {"fast_shutter": True, "upstream_gv6": False, "saxs_gv7": True,
                          "pump_iv1": True, "turbo_enable": True, "turbo_water": True}
        with pytest.raises(RuntimeError, match="isolation failed"):
            guard.imaging_ready()
    finally:
        guard.stop()


def test_backup_mode_and_gv7_validation(rig):
    cfg = weekend_settings("waxs_isolated")
    assert cfg.pressure_limits == {"waxs_pressure": .009, "maxs_pressure": .009, "saxs_pressure": .009}
    assert weekend_settings().pressure_limits["waxs_pressure"] == .009
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber(), mode="waxs_isolated")
    rig.monitor.settings = cfg
    with pytest.raises(RuntimeError, match="requires GV7"):
        guard.start()
    assert guard.thread is None


def test_trip_prevents_fast_shutter_reopen_even_after_pressure_falls(rig):
    from bluesky import RunEngine

    from kapton_exposure import fast_shutter

    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber()).start()
    try:
        rig.signals["waxs_pressure"].put(.06)
        wait_trip(guard)
        rig.signals["waxs_pressure"].put(.001)
        with pytest.raises(RuntimeError, match="latched"):
            RunEngine({})(fast_shutter(rig.fs, True, monitor=rig.monitor))
        assert rig.fs.open_cpt.calls == 0
    finally:
        guard.stop()


def test_previous_trip_requires_acknowledgment_to_rearm(rig):
    ch = chamber()
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=ch).start()
    rig.signals["waxs_pressure"].put(.06)
    wait_trip(guard)
    guard.stop()
    rig.signals["waxs_pressure"].put(.001)
    rig.monitor._pressure_sample()
    rig.monitor._sample()
    ch.waxs_saxs_valve.status.put("Open")
    replacement = PressureIsolation(rig.monitor, fs=rig.fs, chamber=ch)
    with pytest.raises(RuntimeError, match="acknowledge_previous_trip"):
        replacement.start()
    replacement.start(acknowledge_previous_trip=True)
    replacement.stop()


def test_monitor_failure_trips_guard_and_stale_pressure_does_not_pass(rig):
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber()).start()
    try:
        rig.monitor.error = RuntimeError("simulated storage failure")
        wait_trip(guard)
        assert all(result["confirmed"] for result in guard.result)
    finally:
        guard.stop()


def test_backup_pressure_between_old_and_new_ceiling_keeps_guard_armed(rig):
    rig.monitor.settings = weekend_settings("waxs_isolated")
    rig.signals["waxs_pressure"].put(.008)
    rig.monitor._pressure_sample()
    rig.monitor._sample()
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=chamber(isolated=True), mode="waxs_isolated").start()
    try:
        time.sleep(.3)
        assert not guard.tripped.is_set()
        rig.signals["waxs_pressure"].put(.009)
        wait_trip(guard)
        assert all(result["confirmed"] for result in guard.result)
    finally:
        guard.stop()


def test_delayed_shutdown_order_and_logging(rig, monkeypatch):
    monkeypatch.setattr("kapton_exposure.PUMP_SHUTDOWN_DELAY_S", .3)
    ch = chamber()
    guard = PressureIsolation(rig.monitor, fs=rig.fs, chamber=ch).start()
    try:
        rig.signals["waxs_pressure"].put(.009)
        assert guard.boundaries_closed.wait(3)
        assert ch.turbo_valve.status.get() == "Open"
        assert ch.turbo_enable.get() == 1
        assert ch.turbo_cooling_valve.status.get() == "Open"
        sample = rig.monitor.latest["wall"]
        wait_trip(guard)
        assert rig.monitor.latest["wall"] > sample
        assert ch.turbo_valve.status.get() == "Not Open"
        assert ch.turbo_enable.get() == 0
        assert ch.turbo_cooling_valve.status.get() == "Not Open"
        with rig.monitor.lock:
            import json

            rows = [(wall, json.loads(payload)) for wall, payload in
                    rig.monitor.db.execute("SELECT wall,payload FROM isolation ORDER BY id")]
        boundary = next(w for w, r in rows if r["status"] == "boundaries_closed")
        pump = next(w for w, r in rows if r["status"] == "pump_gate_close_attempted")
        assert pump-boundary >= .3
        phases = [r["status"] for _, r in rows]
        assert phases.index("pump_gate_close_attempted") < phases.index("turbo_disable_attempted") < phases.index("closed")
    finally:
        guard.stop()

"""Multi-day Kapton irradiation: independent scalar logger and Bluesky images.

Importing this module creates no devices and performs no hardware operations.
See README.md for required PV verification and the explicit start/stop workflow.
SPDX-License-Identifier: BSD-3-Clause
"""

import fcntl
import json
import logging
import math
import re
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from ophyd import EpicsSignalRO, Signal
from ophyd.status import Status
from smi_plans._core import one_sample_run

log = logging.getLogger(__name__)
SAXS_PRESSURE_PV = "XF:12IDC-VA:2{Det:1M-TCG:8}P-I"
LOG_DIRECTORY = Path(__file__).resolve().parent / "logs"
PRESSURES = ("waxs_pressure", "maxs_pressure", "saxs_pressure")
PRESSURE_CEILING_TORR = 9e-3
PUMP_SHUTDOWN_DELAY_S = 30.0
RECOVERY_CURRENT_MA = 375.0
RECOVERY_RING_MODES = ("Operations", "Beamline Studies", "Accel Studies")
KNOWN_RING_MODES = ("Operations", "Setup", "Accel Studies", "Beamline Studies", "Failure",
                    "Maintenance", "Shutdown", "Unscheduled Ops", "Decay Mode Ops")
TOTALS = ("observed_s", "fast_open_s", "fe_fast_open_s", "beam_s",
          "unknown_fast_s", "unknown_beam_s")


def _pressure_in_range(key, value, ceiling):
    # SAXS TCG:8 reports zero normally below its measurement range.
    return (value >= 0 if key == "saxs_pressure" else value > 0) and value < ceiling


@dataclass(frozen=True)
class Settings:
    """Pressure limits use each gauge's verified native engineering units."""

    beam_threshold: float = 10.0
    pressure_limits: dict = field(default_factory=lambda: dict.fromkeys(PRESSURES, PRESSURE_CEILING_TORR))
    pressure_units: dict = field(default_factory=lambda: dict.fromkeys(PRESSURES, "Torr"))
    sample_period_s: float = 1.0
    image_period_s: float = 300.0
    exposure_s: float = 1.0
    stale_s: float = 3.0
    pressure_stale_s: float = 10.0
    read_timeout_s: float = 2.0
    detector_timeout_s: float = 30.0
    recovery_timeout_s: float = 120.0

    def __post_init__(self):
        for name in ("sample_period_s", "image_period_s", "exposure_s", "stale_s",
                      "pressure_stale_s", "read_timeout_s", "detector_timeout_s", "recovery_timeout_s"):
            if not math.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.sample_period_s < 0.1 or self.stale_s < 2 * self.sample_period_s:
            raise ValueError("Use >=0.1 s polling and stale_s >=2 polling periods")
        if self.pressure_stale_s < 2 * self.sample_period_s:
            raise ValueError("pressure_stale_s must be >=2 polling periods")
        if not math.isfinite(self.beam_threshold) or self.beam_threshold < 0:
            raise ValueError("A measured, nonnegative BPM dark/beam threshold is required")
        if set(self.pressure_limits) != set(PRESSURES) or set(self.pressure_units) != set(PRESSURES):
            raise ValueError(f"Supply limits and units for exactly {PRESSURES}")
        for key in PRESSURES:
            if not math.isfinite(self.pressure_limits[key]) or self.pressure_limits[key] <= 0:
                raise ValueError(f"Invalid pressure ceiling: {key}")
            if not self.pressure_units[key]:
                raise ValueError(f"Missing pressure units: {key}")


def profile_signals(ns, *, saxs_pressure_pv=SAXS_PRESSURE_PV):
    """BPM2 SumX gates beam presence; BPM3 SumX records incident flux separately.

    Call only in the live session. Instantiating EpicsSignalRO starts CA discovery.
    FE closed bit: 0=open, 1=not open. Fast controller DAC: 0=open, 7=closed.
    """
    if not saxs_pressure_pv or not isinstance(saxs_pressure_pv, str):
        raise ValueError("Supply the verified SAXS pressure PV from CSS/IOC")
    return {
        "fe": ns["fe_shutter"].status,
        "enabled": ns["smi_shutter_enable"],
        "ring_current": ns["ring"].current,
        "ring_mode": ns["ring"].mode,
        "fast": ns["fs"].status_pv,  # NOT fs.status (a cached software Signal)
        "photon": ns["ph_shutter"].status,
        "bpm": ns["xbpm2"].sumX,
        "incident_flux": ns["xbpm3"].sumX,
        "diode": ns["pin_diode"].current2.mean_value,
        "waxs_pressure": ns["chamber_pressure"].waxs,
        "maxs_pressure": ns["chamber_pressure"].maxs,
        "saxs_pressure": EpicsSignalRO(saxs_pressure_pv, name="kapton_saxs_pressure"),
    }


def weekend_settings(mode="saxs_connected"):
    """All modes now use 0.009 Torr; mode only checks the starting GV7 position."""
    if mode not in ("saxs_connected", "waxs_isolated"):
        raise ValueError("mode must be saxs_connected or waxs_isolated")
    return Settings()


def install_acquisition_suspenders(ns):
    """Reinstall the existing beam and FE-permit suspenders, without replacing them.

    Call at the idle prompt before launching production. The profile's existing
    ring hysteresis (100/350 mA + 600 s) remains; recovery additionally requires
    >=375 mA in this script. This helper does not change the BEAM_DOWN flag.
    """
    re = ns["RE"]
    if re.state != "idle":
        raise RuntimeError("Install acquisition suspenders at the idle prompt before launching the plan")
    for name in ("susp_beam", "susp_smi_shutter"):
        suspender = ns[name]
        if suspender not in re.suspenders:
            re.install_suspender(suspender)
    log.info("Existing ring-current and FE-permit suspenders installed")


def accelerator_ready(snapshot):
    """Recovery prerequisite independent of optional RE suspenders.

    Operations, Beamline Studies and Accel Studies permit automatic recovery.
    Ring current remains
    a recovery gate, not a dose gate: delivered beam below 375 mA still counts.
    """
    values = snapshot["values"]
    mode = values.get("ring_mode")
    return (values.get("ring_current", -1) >= RECOVERY_CURRENT_MA
            and mode in RECOVERY_RING_MODES)


def pressure_trip_reason(snapshot):
    return {"pressure_values": {k: snapshot["values"].get(k) for k in PRESSURES},
            "pressure_diagnostics": snapshot.get("pressure_diagnostics", {}),
            "pressure_stale_s": snapshot.get("pressure_stale_s")}


def configure_diode(pin_diode_ext, *, averaging_s=1.0):
    """Configure continuous TetrAMM channel reads, never stage/trigger QuadEMV33.

    Bias, gain, offsets and calibration are untouched. IOC enum labels must be
    Continuous / Free run. Acquisition remains on when the image plan ends.
    """
    if not math.isfinite(averaging_s) or averaging_s <= 0:
        raise ValueError("averaging_s must be positive")
    device = pin_diode_ext
    for signal in (device.acquire, device.acquire_mode, device.trigger_mode, device.averaging_time):
        if getattr(signal, "_set_thread", None) is not None:
            raise RuntimeError(f"{signal.name}: previous ophyd set is still pending; wait for it to finish "
                               "or restart the idle Bluesky session before configuring TetrAMM")

    def read(signal):
        if hasattr(signal, "pvname"):
            return signal.get(timeout=2, connection_timeout=2, use_monitor=False)
        return signal.get()

    def matches(signal, expected):
        value = read(signal)
        enums = getattr(signal, "enum_strs", None)
        if isinstance(expected, str) and not isinstance(value, str) and enums:
            value = enums[int(value)]
        return value == expected

    mode = getattr(device, "acquire_mode_readback", device.acquire_mode)
    trigger = getattr(device, "trigger_mode_readback", device.trigger_mode)
    averaging = getattr(device, "averaging_time_readback", device.averaging_time)
    if (matches(mode, "Continuous") and matches(trigger, "Free run")
            and math.isclose(float(read(averaging)), averaging_s, rel_tol=1e-6, abs_tol=1e-6)
            and matches(device.acquire, 1)):
        log.info("TetrAMM already running Continuous / Free run at %s s; no configuration writes", averaging_s)
        return

    # abs_set forwards timeout to ophyd.set; mv(timeout=...) only bounds RE.wait
    # and can strand a polling set thread after RE has already aborted.
    for signal, value in ((device.acquire, 0), (device.acquire_mode, "Continuous"),
                          (device.trigger_mode, "Free run"), (device.averaging_time, averaging_s),
                          (device.acquire, 1)):
        log.info("TetrAMM: setting %s to %r (5 s signal completion timeout)", signal.name, value)
        yield from bps.abs_set(signal, value, timeout=5, wait=True)


class PressureIsolation:
    """Explicitly armed, close-only pressure guard independent of the RunEngine.

    The monitor remains its own read/log thread. Each closure gets an independent
    worker so a failed valve never prevents commanding the other valves.
    Close fast shutter/GV6/GV7; 30 s after boundary closure attempts finish,
    close IV1, disable turbo, then close cooling water. No vents or auto rearm.
    """

    def __init__(self, monitor, *, fs, chamber, mode="saxs_connected", timeout=10):
        if mode not in ("saxs_connected", "waxs_isolated"):
            raise ValueError("Unknown isolation mode")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive")
        self.monitor, self.fs, self.mode, self.timeout = monitor, fs, mode, timeout
        self.valves = {"upstream_gv6": chamber.upstream_valve,
                       "saxs_gv7": chamber.waxs_saxs_valve,
                       "pump_iv1": chamber.turbo_valve}
        self.turbo_enable = chamber.turbo_enable
        self.water_valve = chamber.turbo_cooling_valve
        self.thread = None
        self.stop_event = threading.Event()
        self.tripped = threading.Event()
        self.control_lock = threading.RLock()
        self.result = None
        self.phase = "unarmed"
        self.boundaries_closed = threading.Event()
        self.boundaries_failed = threading.Event()
        self.shutdown_done = threading.Event()
        self._trip_lock = threading.Lock()
        self.trip_thread = None

    def _get(self, signal):
        if hasattr(signal, "pvname"):
            return signal.get(timeout=2, connection_timeout=2, use_monitor=False)
        return signal.get()

    def valve_state(self, valve):
        value = self._get(valve.status)
        if not isinstance(value, str) and getattr(valve.status, "enum_strs", None):
            value = valve.status.enum_strs[int(value)]
        return value

    def assert_untripped(self):
        if self.tripped.is_set():
            raise RuntimeError("Pressure isolation is latched; inspect valves and explicitly rearm")

    def _journal(self, record):
        try:
            with self.monitor.lock:
                self.monitor.db.execute("INSERT INTO isolation (wall,payload) VALUES (?,?)",
                                        (time.time(), json.dumps(record)))
                self.monitor.db.commit()
        except Exception:
            # Closing must still happen if storage has failed.
            log.exception("Could not persist pressure isolation record")

    def request_trip(self, reason):
        """Latch immediately and launch shutdown once, without blocking the image plan."""
        with self._trip_lock:
            if self.tripped.is_set():
                return
            self._latch()
            self.trip_thread = threading.Thread(target=self._shutdown, args=(reason,),
                                                name="kapton-shutdown", daemon=True)
            self.trip_thread.start()

    def _latch(self):
        with self.control_lock:
            self.tripped.set()
            self.phase = "closing_boundaries"
        # Upstream BPMs may stay bright after GV6 closes. Stop crediting beam at
        # the trip; conservatively exclude the brief unverified closing interval.
        with self.monitor.lock:
            self.monitor.clock.advance(time.monotonic())
            self.monitor.clock.exposure_inhibited = True

    def imaging_ready(self):
        """Post-trip images need current boundary readbacks, not just past success."""
        if self.boundaries_failed.is_set():
            raise RuntimeError("GV6/GV7 isolation failed; post-trip images inhibited; monitor remains running")
        if not self.boundaries_closed.is_set():
            return False
        for name in ("upstream_gv6", "saxs_gv7"):
            valve = self.valves[name]
            if self.valve_state(valve) != valve.close_val:
                raise RuntimeError(f"{name} no longer confirms closed; post-trip images inhibited")
        return True

    def _close_one(self, name, valve=None):
        command = self.fs.close_cpt if valve is None else valve.close_cmd
        target = 7 if valve is None else valve.close_val
        value = 1 if valve is None else valve.cmd_actuate_val
        read = (lambda: self._get(self.fs.status_pv)) if valve is None else (lambda: self.valve_state(valve))
        try:
            # Send a close even if already closed, then verify. Two bounded
            # attempts handle a transient command loss without an endless retry.
            for attempt in range(2):
                with self.control_lock:
                    command.put(value, wait=True, timeout=2)
                deadline = time.monotonic() + self.timeout
                while time.monotonic() < deadline:
                    actual = read()
                    if actual == target:
                        return {"device": name, "confirmed": True, "readback": actual,
                                "attempts": attempt + 1}
                    time.sleep(.1)
                time.sleep(.2)
            raise TimeoutError(f"{name}: close readback did not confirm {target!r}")
        except Exception as exc:
            log.exception("Pressure isolation failed for %s", name)
            return {"device": name, "confirmed": False, "error": repr(exc)}

    def _trip(self, reason):
        """Synchronous entry for the watcher and explicit human acceptance test."""
        with self._trip_lock:
            if self.tripped.is_set():
                return
            self._latch()
        self._shutdown(reason)

    def _turbo_off(self):
        try:
            self.turbo_enable.put(0, wait=True, timeout=2)
            deadline = time.monotonic() + self.timeout
            while time.monotonic() < deadline:
                actual = self._get(self.turbo_enable)
                enums = getattr(self.turbo_enable, "enum_strs", None)
                off = actual == 0 or (enums and actual == enums[0])
                if off:
                    return {"device": "turbo_enable", "confirmed": True, "readback": actual}
                time.sleep(.1)
            raise TimeoutError("Turbo OnOff did not confirm off")
        except Exception as exc:
            log.exception("Turbo disable failed")
            return {"device": "turbo_enable", "confirmed": False, "error": repr(exc)}

    def _shutdown(self, reason):
        self._journal({"status": "tripped", "reason": reason, "mode": self.mode})
        log.error("PRESSURE TRIP: closing fast shutter/GV6/GV7, delayed pump shutdown: %s", reason)
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="kapton-isolate") as pool:
            jobs = [pool.submit(self._close_one, "fast_shutter")]
            jobs += [pool.submit(self._close_one, name, self.valves[name]) for name in ("upstream_gv6", "saxs_gv7")]
            self.result = [job.result() for job in jobs]
        boundaries_ok = all(r["confirmed"] for r in self.result if r["device"] in ("upstream_gv6", "saxs_gv7"))
        (self.boundaries_closed if boundaries_ok else self.boundaries_failed).set()
        self.phase = "pump_delay"
        self._journal({"status": "boundaries_closed" if boundaries_ok else "boundary_close_failed",
                       "results": list(self.result), "pump_delay_s": PUMP_SHUTDOWN_DELAY_S})
        # stop() never cancels this delay or the mandatory pump shutdown.
        time.sleep(PUMP_SHUTDOWN_DELAY_S)
        self.phase = "closing_pump"
        self.result.append(self._close_one("pump_iv1", self.valves["pump_iv1"]))
        self._journal({"status": "pump_gate_close_attempted", "result": self.result[-1]})
        self.result.append(self._turbo_off())
        self._journal({"status": "turbo_disable_attempted", "result": self.result[-1]})
        self.result.append(self._close_one("turbo_water", self.water_valve))
        self.phase = "shutdown_complete" if all(r["confirmed"] for r in self.result) else "shutdown_failed"
        self._journal({"status": "closed" if all(r["confirmed"] for r in self.result) else "close_failed",
                       "results": self.result, "mode": self.mode})
        self.shutdown_done.set()

    def _watch(self):
        while not self.stop_event.wait(.2):
            try:
                sample = self.monitor.health()
                if sample["pressure_ok"]:
                    continue
                reason = pressure_trip_reason(sample)
            except Exception as exc:  # noqa: BLE001 -- loss of monitoring also isolates
                reason = {"monitor_error": repr(exc)}
            self._trip(reason)
            return

    def start(self, *, acknowledge_previous_trip=False):
        """Explicitly arm only after pumpdown and the required GV7 geometry check."""
        if self.thread is not None or getattr(self.monitor, "isolation", None) is not None:
            raise RuntimeError("Isolation guard already attached; stop it before replacing")
        if self.monitor.settings.pressure_limits != weekend_settings(self.mode).pressure_limits:
            raise ValueError("Pressure ceilings do not match the selected weekend mode")
        if not self.monitor.health()["pressure_ok"]:
            raise RuntimeError("Cannot arm isolation until all pressures are valid and below ceilings")
        gv7 = self.valves["saxs_gv7"]
        expected = gv7.open_val if self.mode == "saxs_connected" else gv7.close_val
        if self.valve_state(gv7) != expected:
            raise RuntimeError(f"{self.mode} requires GV7 readback {expected!r}; position it manually first")
        with self.monitor.lock:
            self.monitor.db.execute("CREATE TABLE IF NOT EXISTS isolation "
                                    "(id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
            last = self.monitor.db.execute("SELECT payload FROM isolation ORDER BY id DESC LIMIT 1").fetchone()
            if (last and json.loads(last[0])["status"] in ("tripped", "closed", "close_failed")
                    and not acknowledge_previous_trip):
                raise RuntimeError("Previous isolation trip requires acknowledge_previous_trip=True after inspection")
        self._journal({"status": "armed", "mode": self.mode,
                       "pressure_limits": self.monitor.settings.pressure_limits,
                       "valves": {k: getattr(v, "prefix", v.name) for k, v in self.valves.items()}})
        self.monitor.isolation = self
        with self.monitor.lock:
            self.monitor.clock.advance(time.monotonic())
            self.monitor.clock.exposure_inhibited = False
        self.phase = "armed"
        self.thread = threading.Thread(target=self._watch, name="kapton-pressure-guard", daemon=True)
        self.thread.start()
        return self

    def stop(self):
        """Disarm explicitly after ending irradiation; never cancels an in-flight trip."""
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=PUMP_SHUTDOWN_DELAY_S + 6 * self.timeout + 30)
            if self.thread.is_alive():
                raise RuntimeError("Isolation still closing valves; leave monitor running")
        if self.trip_thread is not None:
            self.trip_thread.join(timeout=PUMP_SHUTDOWN_DELAY_S + 6 * self.timeout + 30)
            if self.trip_thread.is_alive():
                raise RuntimeError("Delayed pump shutdown still active; leave monitor running")
        if not self.tripped.is_set():
            self._journal({"status": "disarmed", "mode": self.mode})
        if getattr(self.monitor, "isolation", None) is self:
            self.monitor.isolation = None


class ExposureClock:
    """Integrate callback-arrival times using a monotonic clock, not wall-clock deltas.

    No extrapolation beyond the last verified read's freshness window. Photon
    status polarity is supplied by the existing shutter's open_val/close_val.
    """

    def __init__(self, settings, *, photon_open, photon_closed, now=None, totals=None):
        self.settings = settings
        self.photon_open = photon_open
        self.photon_closed = photon_closed
        self.values = {}
        self.totals = dict.fromkeys(TOTALS, 0.0)
        self.totals.update(totals or {})
        self.last = time.monotonic() if now is None else now
        self.beam_interruptions = 0
        self.exposure_inhibited = False
        self.fe_openings = 0
        self.recovery_generation = 0

    def _state(self, key, now):
        entry = self.values.get(key)
        if entry is None or now >= entry[1]:
            return None
        value = entry[0]
        if key == "fe":
            return True if value == 0 else False if value == 1 else None
        if key == "enabled":
            return True if value == 1 else False if value == 0 else None
        if key == "fast":
            return True if value == 0 else False if value == 7 else None
        if key == "photon":
            return True if value == self.photon_open else False if value == self.photon_closed else None
        if key == "bpm":
            return value > self.settings.beam_threshold
        raise KeyError(key)

    def states(self, now):
        states = {k: self._state(k, now) for k in ("fe", "enabled", "fast", "photon", "bpm")}
        # Unknown inputs remain explicitly unknown, even if another shutter is closed.
        states["beam"] = None if None in states.values() else all(states.values())
        if self.exposure_inhibited:
            states["beam"] = False
        return states

    def recovery_permitted(self, now):
        values = {key: value for key, (value, expiry) in self.values.items() if now < expiry}
        return (self._state("fe", now) is True and self._state("enabled", now) is True
                and accelerator_ready({"values": values}))

    def advance(self, now):
        if now < self.last:
            raise ValueError("Monotonic time moved backwards")
        # Split at expiration boundaries so cached values never accrue days of beam.
        edges = sorted({self.last, now} | {expiry for _, expiry in self.values.values()
                                         if self.last < expiry < now})
        for start, stop in pairwise(edges):
            dt = stop - start
            s = self.states(start)
            self.totals["observed_s"] += dt
            self.totals["fast_open_s"] += dt if s["fast"] is True else 0
            self.totals["fe_fast_open_s"] += dt if s["fe"] is True and s["fast"] is True else 0
            self.totals["beam_s"] += dt if s["beam"] is True else 0
            self.totals["unknown_fast_s"] += dt if s["fast"] is None else 0
            self.totals["unknown_beam_s"] += dt if s["beam"] is None else 0
        self.last = now

    def update(self, key, value, now, *, valid_for=None):
        before = self.states(self.last)["beam"]
        fe_before = self._state("fe", now)
        permitted_before = self.recovery_permitted(now)
        self.advance(now)
        self.values[key] = (value, now + (self.settings.stale_s if valid_for is None else valid_for))
        if key == "fe" and fe_before is not True and self._state("fe", now) is True:
            self.fe_openings += 1
        if key in ("fe", "enabled", "ring_current", "ring_mode") and not permitted_before and self.recovery_permitted(now):
            self.recovery_generation += 1
        if before is True and self.states(now)["beam"] is not True:
            self.beam_interruptions += 1


def _configuration_differences(saved, requested, prefix=""):
    """Return changed identity leaves with their saved and requested values."""
    changes = {}
    for key in sorted(saved.keys() | requested.keys()):
        path = f"{prefix}.{key}" if prefix else key
        before, after = saved.get(key), requested.get(key)
        if isinstance(before, dict) and isinstance(after, dict):
            changes.update(_configuration_differences(before, after, path))
        elif before != after:
            changes[path] = (before, after)
    return changes


class ExposureMonitor:
    """Independent scalar/pressure readers, bounded memory and durable sample logs.

    Continues while RE is paused, suspended, imaging, or idle. No hardware writes.
    Use a different database for a different specimen; resume=True is explicit.
    resume_pressure_limits=True permits only pressure-ceiling changes on resume,
    preserving totals and recording a configuration_changes audit entry.
    """

    def __init__(self, signals, settings, database, *, specimen, photon_open,
                 photon_closed, resume=False, resume_pressure_limits=False, resume_added_diode=False,
                 resume_weekend_update=False):
        if resume_pressure_limits and not resume:
            raise ValueError("resume_pressure_limits requires resume=True")
        if resume_added_diode and not resume:
            raise ValueError("resume_added_diode requires resume=True")
        if resume_weekend_update and not resume:
            raise ValueError("resume_weekend_update requires resume=True")
        expected = {"fe", "enabled", "ring_current", "ring_mode", "fast", "photon", "bpm", "incident_flux", "diode", *PRESSURES}
        if set(signals) != expected:
            raise ValueError(f"Expected signals {expected}")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", specimen):
            raise ValueError("Use letters, digits, hyphens and underscores in specimen")
        self.signals = signals
        self.settings = settings
        self.database = Path(database).expanduser().resolve()
        if not self.database.parent.is_dir():
            raise ValueError("Create the experiment data directory first")
        self.specimen = specimen
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.thread = None
        self.error = None
        self.pressure_thread = None
        self.pressure_error = None
        self.pressure_stop_event = threading.Event()
        self._pressure_poll_lock = threading.Lock()
        self._pressure_readings = {}
        self._pressure_last_good = {}
        self._pressure_last_good_wall = {}
        self._pressure_attempts = {}
        self.latest = None
        self._pressure_ok = None
        self.subscriptions = []
        self._file_lock = self.database.with_suffix(self.database.suffix + ".lock").open("a")
        try:
            fcntl.flock(self._file_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            exists = self.database.exists()
            if exists != resume:
                raise ValueError("Existing database requires resume=True; new database requires resume=False")
            self.db = sqlite3.connect(self.database, timeout=5, check_same_thread=False)
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS recovery (id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS pressure_samples (id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
            identity = {"specimen": specimen, "settings": settings.__dict__,
                        "signals": {k: getattr(v, "pvname", v.name) for k, v in signals.items()},
                        "photon_open": photon_open, "photon_closed": photon_closed}
            encoded = json.dumps(identity, sort_keys=True)
            old = self.db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
            if old and json.loads(old[0]) != identity:
                previous_identity = json.loads(old[0])
                differences = _configuration_differences(previous_identity, identity)
                def allowed_change(key, values):
                    if resume_weekend_update:
                        if key == "settings.pressure_stale_s" and values == (None, 10.0):
                            return True
                        if key.startswith("settings.pressure_limits.") and values[1] == PRESSURE_CEILING_TORR:
                            return True
                        additions = {"signals.diode": "XF:12ID:2{EM:Tetr1}Current2:MeanValue_RBV",
                                     "signals.enabled": "SR:C12-EPS{PLC:1}Sts:ID_BE_Enbl-Sts",
                                     "signals.ring_current": "SR:C03-BI{DCCT:1}I:Real-I",
                                     "signals.ring_mode": "SR-OPS{}Mode-Sts"}
                        if key in additions and values == (None, additions[key]):
                            return True
                        if key == "settings.read_timeout_s" and values[1] == 2.0:
                            return True
                    return ((resume_pressure_limits and key.startswith("settings.pressure_limits."))
                            or (resume_added_diode and key == "signals.diode" and values[0] is None))

                limits_only = all(key.startswith("settings.pressure_limits.") for key in differences)
                if not all(allowed_change(k, v) for k, v in differences.items()):
                    detail = "; ".join(f"{key}: saved={values[0]!r}, requested={values[1]!r}"
                                       for key, values in differences.items())
                    hint = ("; use resume_pressure_limits=True to record and accept this ceiling change"
                            if limits_only else "")
                    raise ValueError("Resume configuration/specimen differs: " + detail + hint)
                self.db.execute("CREATE TABLE IF NOT EXISTS configuration_changes "
                                "(id INTEGER PRIMARY KEY, wall REAL, payload TEXT)")
                self.db.execute("INSERT INTO configuration_changes (wall, payload) VALUES (?, ?)",
                                (time.time(), json.dumps({"reason": "explicit acquisition configuration update",
                                                         "previous": previous_identity, "current": identity})))
                self.db.execute("UPDATE metadata SET value=? WHERE key='identity'", (encoded,))
            self.db.execute("INSERT OR IGNORE INTO metadata VALUES ('identity', ?)", (encoded,))
            row = self.db.execute("SELECT wall, payload FROM samples ORDER BY id DESC LIMIT 1").fetchone()
            previous = json.loads(row[1]) if row else {}
            self.started_wall = previous.get("started_wall", time.time())
            self.unobserved_s = previous.get("unobserved_s", 0.0)
            if row:
                self.unobserved_s += max(0, time.time() - row[0])
            self.clock = ExposureClock(settings, photon_open=photon_open,
                                        photon_closed=photon_closed, totals=previous.get("totals"))
            self.clock.exposure_inhibited = previous.get("exposure_inhibited", False)
            self.db.commit()
        except BaseException:
            if hasattr(self, "db"):
                self.db.close()
            self._file_lock.close()
            raise


    def _normalize(self, key, value):
        if key == "ring_mode":
            if not isinstance(value, str):
                enums = getattr(self.signals[key], "enum_strs", None)
                if not enums:
                    raise ValueError("Ring mode requires a recognized enum string")
                value = enums[int(value)]
            return value
        if key == "photon":
            # TwoButtonShutter subscription callbacks may return numeric enums.
            enums = getattr(self.signals[key], "enum_strs", None)
            if not isinstance(value, str) and enums:
                return enums[int(value)]
            return value
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite {key}")
        return number

    def _accept(self, key, value, timestamp, *, good=True):
        freshness = self.settings.pressure_stale_s if key in PRESSURES else self.settings.stale_s
        valid_for = freshness if good else 0.0
        if key in ("bpm", "incident_flux", "diode"):
            # A stopped electrometer can keep serving a perfectly connected old PV.
            age = max(0, time.time() - timestamp)
            valid_for = min(valid_for, max(0, self.settings.stale_s - age))
        with self.lock:
            normalized = self._normalize(key, value)
            now = time.monotonic()
            self.clock.update(key, normalized, now, valid_for=valid_for)
            if key in PRESSURES and good:
                self._pressure_last_good[key] = now
                self._pressure_last_good_wall[key] = time.time()

    def _alarm_acceptable(self, key, value, severity, status):
        if severity == 0:
            return True
        # Photon Pos-Sts and ring Mode-Sts use MINOR STATE for valid enum states.
        # Accept only this specific combination, never general MINOR alarms.
        if key == "ring_mode":
            return severity == 1 and status == 7 and self._normalize(key, value) in KNOWN_RING_MODES
        return (key == "photon" and severity == 1 and status == 7
                and self._normalize(key, value) in
                (self.clock.photon_open, self.clock.photon_closed))

    def _callback(self, key):
        def changed(value=None, timestamp=None, **kwargs):
            try:
                signal = self.signals[key]
                metadata = signal.metadata
                severity = kwargs.get("severity", metadata.get("severity")) or 0
                status = kwargs.get("status", metadata.get("status")) or 0
                good = signal.connected and self._alarm_acceptable(key, value, severity, status)
                self._accept(key, value, timestamp or 0, good=good)
            except (ValueError, TypeError, IndexError):
                with self.lock:
                    self.clock.update(key, 0, time.monotonic(), valid_for=0)
        return changed

    def _read(self, key, signal):
        timeout = self.settings.read_timeout_s
        if hasattr(signal, "pvname"):
            value = signal.get(use_monitor=False, timeout=timeout, connection_timeout=timeout)
            stamp = signal.timestamp
            metadata = signal.metadata
            severity = metadata.get("severity") or 0
            status = metadata.get("status") or 0
            self._accept(key, value, stamp,
                         good=self._alarm_acceptable(key, value, severity, status))
            return {"value": self._normalize(key, value), "timestamp": float(stamp),
                    "severity": int(severity), "status": int(status)}
        reading = signal.read()[signal.name]  # simulation only
        self._accept(key, reading["value"], reading["timestamp"])
        return dict(reading, severity=0, status=0)

    def snapshot(self):
        with self.lock:
            now = time.monotonic()
            self.clock.advance(now)
            states = self.clock.states(now)
            values = {k: v for k, (v, expiry) in self.clock.values.items() if now < expiry}
            pressure_ok = all(k in values and _pressure_in_range(k, values[k], self.settings.pressure_limits[k])
                              for k in PRESSURES)
            diagnostics = {}
            for key in PRESSURES:
                value = values.get(key)
                reading = self._pressure_readings.get(key, {})
                if key not in self.clock.values:
                    reason = "unavailable"
                elif reading.get("severity", 0) != 0:
                    reason = "alarm"
                elif value is None:
                    reason = "stale_or_invalid"
                elif not _pressure_in_range(key, value, self.settings.pressure_limits[key]):
                    reason = "overpressure" if value >= self.settings.pressure_limits[key] else "invalid_value"
                else:
                    reason = "read_error_grace" if "error" in reading else "ok"
                last = self._pressure_last_good.get(key)
                diagnostics[key] = {"state": reason, "age_s": None if last is None else max(0, now-last),
                                    "last_good_wall": self._pressure_last_good_wall.get(key),
                                    "last_attempt_wall": self._pressure_attempts.get(key),
                                    "reading": dict(reading), "ceiling": self.settings.pressure_limits[key]}
            return {"wall": time.time(), "started_wall": self.started_wall,
                    "elapsed_wall_s": time.time() - self.started_wall,
                    "totals": dict(self.clock.totals), "unobserved_s": self.unobserved_s,
                    "states": states, "values": values, "pressure_ok": pressure_ok,
                    "pressure_diagnostics": diagnostics, "pressure_stale_s": self.settings.pressure_stale_s,
                    "bpm_fresh": "bpm" in values,
                    "incident_flux_fresh": "incident_flux" in values,
                    "diode_fresh": "diode" in values,
                    "exposure_inhibited": self.clock.exposure_inhibited,
                    "isolation_phase": getattr(getattr(self, "isolation", None), "phase", "unarmed"),
                    "fe_openings": self.clock.fe_openings,
                    "recovery_generation": self.clock.recovery_generation,
                    "beam_interruptions": self.clock.beam_interruptions}

    def _pressure_sample(self):
        """Separate pressure I/O; errors retain last valid value only until expiry.

        Alarms/negative values/overpressure are not debounced. A good high-pressure
        read requests isolation before the next gauge is read, capturing even a
        one-poll excursion while the other scalar reader is blocked.
        """
        with self._pressure_poll_lock:
            for key in PRESSURES:
                try:
                    reading = self._read(key, self.signals[key])
                except (ValueError, TypeError, IndexError, OverflowError) as exc:
                    reading = {"error": f"{type(exc).__name__}: {exc}"}
                    with self.lock:
                        self.clock.update(key, 0, time.monotonic(), valid_for=0)
                except Exception as exc:  # noqa: BLE001 -- transport failure: keep only unexpired last-good data
                    reading = {"error": f"{type(exc).__name__}: {exc}"}
                with self.lock:
                    self._pressure_readings[key] = reading
                    self._pressure_attempts[key] = time.time()
                    snapshot = self.snapshot()
                guard = getattr(self, "isolation", None)
                if guard is not None and not snapshot["pressure_ok"]:
                    guard.request_trip(pressure_trip_reason(snapshot))
            with self.lock:
                snapshot = self.snapshot()
                self.db.execute("INSERT INTO pressure_samples (wall,payload) VALUES (?,?)",
                                (snapshot["wall"], json.dumps({"wall": snapshot["wall"],
                                 "pressure_ok": snapshot["pressure_ok"],
                                 "pressure_diagnostics": snapshot["pressure_diagnostics"]}, allow_nan=False)))
                self.db.commit()

    def _pressure_worker(self):
        deadline = time.monotonic()
        try:
            while not self.pressure_stop_event.is_set():
                self._pressure_sample()
                deadline += self.settings.sample_period_s
                if deadline < time.monotonic():
                    deadline = time.monotonic() + self.settings.sample_period_s
                self.pressure_stop_event.wait(max(0, deadline-time.monotonic()))
        except Exception as exc:
            self.pressure_error = exc
            log.exception("Dedicated pressure polling failed")

    def _sample(self):
        readings = {}
        for key, signal in self.signals.items():
            if key in PRESSURES:
                continue
            try:
                readings[key] = self._read(key, signal)
            except Exception as exc:  # noqa: BLE001 -- persist driver errors and invalidate this channel
                readings[key] = {"error": f"{type(exc).__name__}: {exc}"}
                with self.lock:
                    self.clock.update(key, 0, time.monotonic(), valid_for=0)
        with self.lock:
            readings.update({key: dict(self._pressure_readings.get(key, {"error": "No pressure sample yet"}))
                             for key in PRESSURES})
            sample = self.snapshot()
            sample["readings"] = readings
            self.db.execute("INSERT INTO samples (wall, payload) VALUES (?, ?)",
                            (sample["wall"], json.dumps(sample, allow_nan=False)))
            self.db.commit()
            self.latest = sample
            if sample["pressure_ok"] != self._pressure_ok:
                self._pressure_ok = sample["pressure_ok"]
                if not self._pressure_ok:
                    log.error("Kapton pressure ceiling exceeded or gauge unavailable: %s",
                              {key: readings[key] for key in PRESSURES})
                else:
                    log.info("Kapton pressures within configured ceilings")

    def _worker(self):
        deadline = time.monotonic()
        try:
            while not self.stop_event.is_set():
                self._sample()
                deadline += self.settings.sample_period_s
                if deadline < time.monotonic():
                    deadline = time.monotonic() + self.settings.sample_period_s
                self.stop_event.wait(max(0, deadline - time.monotonic()))
        except Exception as exc:
            self.error = exc
            log.exception("Kapton monitoring stopped; image plan will fail its health check")

    def start(self):
        if self.thread is not None:
            raise RuntimeError("Monitor already started")
        try:
            for key in ("fe", "enabled", "ring_current", "ring_mode", "fast", "photon", "bpm"):
                signal = self.signals[key]
                cid = signal.subscribe(self._callback(key), run=False)
                self.subscriptions.append((signal, cid))
            self._pressure_sample()
            self.pressure_thread = threading.Thread(target=self._pressure_worker, name="kapton-pressure-reader", daemon=True)
            self.pressure_thread.start()
            self._sample()  # pressure thread continues even through slow scalar startup reads
            self.thread = threading.Thread(target=self._worker, name="kapton-monitor", daemon=True)
            self.thread.start()
        except BaseException:
            self.close()
            raise
        return self

    def health(self):
        if self.pressure_error is not None:
            raise RuntimeError("Dedicated pressure polling failed") from self.pressure_error
        if self.pressure_thread is None or not self.pressure_thread.is_alive():
            raise RuntimeError("Dedicated pressure reader is not running")
        if self.error is not None:
            raise RuntimeError("Continuous monitor failed") from self.error
        if self.thread is None or not self.thread.is_alive():
            raise RuntimeError("Start the continuous monitor before acquisition")
        if self.latest is None or time.time() - self.latest["wall"] > self.sample_timeout_s:
            raise RuntimeError("Continuous monitor has stopped updating")
        return self.snapshot()

    @property
    def sample_timeout_s(self):
        # Allow a sequential connection + read timeout for each signal, SQLite's
        # 5 s busy timeout, and the sampling period. This is logger liveness only;
        # pressure freshness uses pressure_stale_s on the independent reader.
        return max(self.settings.stale_s,
                   2 * len(self.signals) * self.settings.read_timeout_s
                   + 5 + self.settings.sample_period_s)

    def image_record(self, payload):
        with self.lock:
            self.db.execute("INSERT INTO images (wall, payload) VALUES (?, ?)",
                            (time.time(), json.dumps(payload, allow_nan=False)))
            self.db.commit()

    def recovery_record(self, payload):
        with self.lock:
            self.db.execute("INSERT INTO recovery (wall, payload) VALUES (?, ?)",
                            (time.time(), json.dumps(payload, allow_nan=False)))
            self.db.commit()

    def close(self):
        """Stop logging explicitly AFTER closing the fast shutter and recording that state."""
        if getattr(self, "isolation", None) is not None:
            raise RuntimeError("Stop the pressure isolation guard explicitly before closing the monitor")
        self.stop_event.set()
        self.pressure_stop_event.set()
        if self.pressure_thread is not None:
            self.pressure_thread.join(timeout=2 * len(PRESSURES) * self.settings.read_timeout_s + 6)
            if self.pressure_thread.is_alive():
                raise RuntimeError("Pressure reader did not stop; database remains open")
        if self.thread is not None:
            self.thread.join(timeout=self.sample_timeout_s + 1)
            if self.thread.is_alive():
                raise RuntimeError("Monitor reader did not stop; database remains open")
        for signal, cid in self.subscriptions:
            signal.unsubscribe(cid)
        self.subscriptions.clear()
        with self.lock:
            self.db.close()
            self._file_lock.close()


class _Command:
    """Self-resetting EPICS command: wait for put completion, not value equality."""

    def __init__(self, signal, guard=None):
        self.signal = signal
        self.guard = guard
        self.name = signal.name + "_kapton_command"

    def set(self, value):
        status = Status(timeout=5)

        def complete(**kwargs):
            if not status.done:
                status.set_finished()

        try:
            if self.guard is None:
                self.signal.put(value, use_complete=True, callback=complete, timeout=5)
            else:
                with self.guard.control_lock:
                    self.guard.assert_untripped()
                    self.signal.put(value, use_complete=True, callback=complete, timeout=5)
        except Exception as exc:  # noqa: BLE001 -- propagate asynchronous put failure via Status
            if not status.done:
                status.set_exception(exc)
        return status


def fast_shutter(fs, opened, *, monitor=None):
    """Issue one command and confirm the real DAC readback with a bounded wait."""
    target = 0 if opened else 7
    guard = getattr(monitor, "isolation", None) if opened else None
    if guard is not None:
        guard.assert_untripped()
    if (yield from bps.rd(fs.status_pv)) == target:
        if monitor is not None:
            monitor._accept("fast", target, time.time())
        return
    yield from bps.abs_set(_Command(fs.open_cpt if opened else fs.close_cpt, guard), 1, wait=True)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if (yield from bps.rd(fs.status_pv)) == target:
            if monitor is not None:
                monitor._accept("fast", target, time.time())
            return
        yield from bps.sleep(0.1)
    raise TimeoutError(f"Fast shutter did not confirm {'open' if opened else 'closed'}")


def _ready(monitor, *, require_fast=True, allow_post_trip=False):
    guard = getattr(monitor, "isolation", None)
    snapshot = monitor.health()
    if guard is not None and not snapshot["pressure_ok"]:
        guard.request_trip(pressure_trip_reason(snapshot))
    if guard is not None and guard.tripped.is_set() and allow_post_trip:
        # Beam is physically blocked by verified boundary valves. Detectors may
        # cycle their own shutter output; the plan does not open it.
        snapshot["post_trip"] = True
        return snapshot, guard.imaging_ready()
    if guard is not None:
        guard.assert_untripped()
    if not snapshot["pressure_ok"]:
        problems = []
        for key in PRESSURES:
            value = snapshot["values"].get(key)
            limit = monitor.settings.pressure_limits[key]
            units = monitor.settings.pressure_units[key]
            if value is None:
                last = (monitor.latest or {}).get("readings", {}).get(key)
                problems.append(f"{key}: unavailable/stale/alarmed; last reading={last!r}")
            elif not _pressure_in_range(key, value, limit):
                lower = "<=" if key == "saxs_pressure" else "<"
                problems.append(f"{key}={value:g} {units}; requires 0 {lower} pressure < {limit:g} {units}")
        raise RuntimeError("Pressure check failed: " + "; ".join(problems))
    states = snapshot["states"]
    beam = all(states[k] is True for k in ("fe", "enabled", "photon", "bpm"))
    return snapshot, beam and (not require_fast or states["fast"] is True)


def _trigger_ready(monitor, *, allow_post_trip=False):
    # Explicit fresh reads supplement callbacks immediately before starting an image.
    # Finite-time software reads cannot provide a hardware-atomic FE shutter veto.
    guard = getattr(monitor, "isolation", None)
    if allow_post_trip and guard is not None and guard.tripped.is_set():
        return _ready(monitor, allow_post_trip=True)
    for key in ("fe", "enabled", "ring_current", "ring_mode", "fast", "photon", "bpm"):
        monitor._read(key, monitor.signals[key])
    return _ready(monitor, allow_post_trip=allow_post_trip)


class _UnmanagedEnergy:
    """Forward to Energy.set without matching the managed preprocessor's obj identity.

    Still uses RE set/wait/stop and the normal device's harmonic/limit checks.
    The profile's preprocessor only rewrites messages whose obj is energy itself.
    """

    def __init__(self, energy, timeout):
        self.energy = energy
        self.timeout = timeout
        self.name = energy.name + "_kapton_unmanaged"
        self.parent = None

    def set(self, value):
        return self.energy.set(value, timeout=self.timeout)

    def stop(self, *, success=False):
        return self.energy.stop(success=success)


def recover_fe_open(monitor, energy):
    """On FE open AND EPS enabled: 6000 eV unmanaged, feedback, THEN BPM beam.

    Return the permitted-generation ID, or None if FE/enable/current/mode changes.
    Initial FE-open on startup is treated as a recovery too. No BPM prerequisite.
    """
    monitor._read("fe", monitor.signals["fe"])
    monitor._read("enabled", monitor.signals["enabled"])
    monitor._read("ring_current", monitor.signals["ring_current"])
    monitor._read("ring_mode", monitor.signals["ring_mode"])
    start, _ = _ready(monitor, require_fast=False)
    if (start["states"]["fe"] is not True or start["states"]["enabled"] is not True
            or not accelerator_ready(start)):
        return None
    generation = start["recovery_generation"]
    record = {"recovery_generation": generation, "fe_openings": start["fe_openings"],
              "target_eV": 6000, "status": "started"}
    monitor.recovery_record(record)
    log.info("FE-open + EPS-enabled generation %s: unmanaged 6000 eV before feedback", generation)
    pitch, roll = energy.pitch_feedback_disabled, energy.roll_feedback_disabled
    deadline = time.monotonic() + monitor.settings.recovery_timeout_s

    def still_open():
        monitor._read("fe", monitor.signals["fe"])
        monitor._read("enabled", monitor.signals["enabled"])
        monitor._read("ring_current", monitor.signals["ring_current"])
        monitor._read("ring_mode", monitor.signals["ring_mode"])
        state, _ = _ready(monitor, require_fast=False, allow_post_trip=True)
        return (not state.get("post_trip") and state["states"]["fe"] is True
                and state["states"]["enabled"] is True and state["recovery_generation"] == generation
                and accelerator_ready(state))

    try:
        # No replay of a recovery sequence following an RE suspension.
        yield from bps.clear_checkpoint()
        yield from bps.mv(pitch, "1", roll, "1", timeout=5)
        if not still_open():
            record["status"] = "fe_changed"
            return None
        move = _UnmanagedEnergy(energy, monitor.settings.recovery_timeout_s)
        group = "kapton-recovery-" + str(uuid.uuid4())
        status = yield from bps.abs_set(move, 6000, group=group)
        while not status.done:
            if not still_open():
                yield from bps.stop(move)
                yield from bps.mv(pitch, "1", roll, "1", timeout=5)
                record["status"] = "fe_changed"
                return None
            if time.monotonic() >= deadline:
                yield from bps.stop(move)
                raise TimeoutError("6000 eV recovery move timed out")
            yield from bps.sleep(0.1)
        yield from bps.wait(group=group, timeout=5)
        if not still_open():
            yield from bps.mv(pitch, "1", roll, "1", timeout=5)
            record["status"] = "fe_changed"
            return None
        # Explicit even if Energy.move short-circuits at an already-correct energy.
        yield from bps.mv(pitch, "0", roll, "0", timeout=5)
        while time.monotonic() < deadline:
            if not still_open():
                yield from bps.mv(pitch, "1", roll, "1", timeout=5)
                record["status"] = "fe_changed"
                return None
            monitor._read("bpm", monitor.signals["bpm"])
            snapshot, beam = _ready(monitor, require_fast=False, allow_post_trip=True)
            if snapshot.get("post_trip"):
                record["status"] = "pressure_trip"
                return None
            if beam:
                record.update(status="complete", beam_s=snapshot["totals"]["beam_s"])
                return generation
            yield from bps.sleep(0.1)
        raise TimeoutError("FE recovery: no photon-shutter-open / fresh BPM2 SumX > threshold after feedback")
    except BaseException:
        record["status"] = "failed"
        raise
    finally:
        monitor.recovery_record(record)


def kapton_images(monitor, *, fs, detectors, duration_s=3 * 86400,
                  energy=None, oav=None, md=None, leave_open_on_success=False):
    """Hold the fast shutter open, image WAXS and optional OAV every five minutes.

    A due image waits for beam; missed slots are coalesced, never burst replayed.
    No valve/FE/photon-shutter writes. On failure/abort close the fast shutter;
    the independent monitor remains running. Existing RE suspenders stay installed.
    Supply the profile energy device to recover each FE opening at 6000 eV.
    energy=None explicitly omits energy recovery (e.g. offline/other-energy work).
    oav=OAV_writing adds one TIFF snapshot to each run, preserving its optical
    acquire_time/acquire_period. Do not pass the non-writing OAV view.
    """
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("duration_s must be finite and positive")
    detectors = list(detectors)
    if not 1 <= len(detectors) <= 2 or len({id(det) for det in detectors}) != len(detectors):
        raise ValueError("Supply distinct SAXS/WAXS detectors: detectors=[pil2M, pil900KW]")
    if oav is not None:
        if any(oav is det for det in detectors):
            raise ValueError("OAV must be distinct from the WAXS detector")
        if not hasattr(getattr(oav, "tiff", None), "generate_datum"):
            raise ValueError("Use the TIFF-writing OAV_writing device, not live-view OAV")
    # Trigger optical camera first so a fast detector's shutter closure cannot
    # prevent starting the OAV snapshot. Acquisition is concurrent, not hardware-synchronized.
    image_detectors = ([oav] if oav is not None else []) + detectors
    cfg = monitor.settings
    done = False
    deadline = time.monotonic() + duration_s
    due = time.monotonic()  # initial beam-on image, then five-minute cadence
    recovered_generation = None

    def cleanup():
        if not done or not leave_open_on_success:
            yield from fast_shutter(fs, False, monitor=monitor)

    def body():
        nonlocal due, done, recovered_generation
        _ready(monitor, require_fast=False)
        # Set the WAXS exposure independently of the optical camera settings.
        for det in detectors:
            yield from bps.mv(det.cam.acquire_time, cfg.exposure_s,
                              det.cam.acquire_period, cfg.exposure_s + 0.1,
                              det.cam.num_images, 1, timeout=10)
        if oav is not None:
            yield from bps.mv(oav.cam.num_images, 1, timeout=10)
        yield from fast_shutter(fs, True, monitor=monitor)
        while time.monotonic() < deadline:
            yield from bps.checkpoint()
            snapshot, beam = _ready(monitor, allow_post_trip=True)
            if not snapshot.get("post_trip"):
                beam = beam and accelerator_ready(snapshot)
            # An unexpected idle closure is not automatically fought/reopened.
            if not snapshot.get("post_trip") and snapshot["states"]["fast"] is not True:
                raise RuntimeError("Fast shutter closed outside image acquisition; inspect before restarting")
            if (not snapshot.get("post_trip") and energy is not None and snapshot["states"]["fe"] is True
                    and snapshot["states"]["enabled"] is True and accelerator_ready(snapshot)
                    and snapshot["recovery_generation"] != recovered_generation):
                recovered_generation = yield from recover_fe_open(monitor, energy)
                # Return to the scheduler to recheck deadlines and all readbacks.
                continue
            if time.monotonic() >= due and beam:
                image_id = str(uuid.uuid4())
                fields = {key: Signal(name="kapton_" + key, value=0.0) for key in
                          ("beam_s", "fast_open_s", "elapsed_s", "beam_end_s", "beam_interrupted", "post_trip")}
                outcome = {"image_id": image_id, "status": "pending", "database": str(monitor.database)}
                monitor.image_record(outcome)

                def measure(fields=fields, outcome=outcome, image_id=image_id,
                            recovered_generation=recovered_generation):
                    # After staging/open_run/baseline: FE may have changed while they ran.
                    start, allowed = _trigger_ready(monitor, allow_post_trip=True)
                    if not allowed or (not start.get("post_trip") and energy is not None and start["recovery_generation"] != recovered_generation):
                        outcome["status"] = "skipped_beam_off"
                        return
                    # Clear checkpoint to prevent a suspender replaying an old exposure label.
                    yield from bps.clear_checkpoint()
                    for key, value in (("beam_s", start["totals"]["beam_s"]),
                                       ("fast_open_s", start["totals"]["fast_open_s"]),
                                       ("elapsed_s", start["elapsed_wall_s"])):
                        fields[key].put(value)
                    outcome["start"] = start
                    fields["post_trip"].put(int(start.get("post_trip", False)))
                    group = "kapton-" + image_id
                    statuses = []
                    # Check immediately before each trigger (software gate, not a hardware veto).
                    for det in image_detectors:
                        trigger_state, allowed = _trigger_ready(monitor, allow_post_trip=True)
                        if not allowed or (not trigger_state.get("post_trip") and energy is not None
                                           and trigger_state["recovery_generation"] != recovered_generation):
                            outcome["status"] = "partial_beam_loss"
                            break
                        statuses.append((yield from bps.trigger(det, group=group)))
                    if not statuses:
                        outcome["status"] = "skipped_beam_off"
                        return
                    wait_deadline = time.monotonic() + cfg.detector_timeout_s
                    while not all(status.done for status in statuses):
                        _ready(monitor, require_fast=False, allow_post_trip=True)
                        if time.monotonic() > wait_deadline:
                            raise TimeoutError("Image detectors did not finish")
                        yield from bps.sleep(0.1)
                    yield from bps.wait(group=group, timeout=cfg.detector_timeout_s)
                    end = monitor.health()
                    interrupted = (len(statuses) != len(image_detectors)
                                   or end["beam_interruptions"] != start["beam_interruptions"]
                                   or end["totals"]["unknown_beam_s"] > start["totals"]["unknown_beam_s"]
                                   or end["states"]["beam"] is not True)
                    fields["beam_end_s"].put(end["totals"]["beam_s"])
                    fields["beam_interrupted"].put(int(interrupted))
                    outcome.update(status="interrupted" if interrupted else "complete", end=end)
                    yield from bps.create(name="primary")
                    for det in image_detectors[:len(statuses)]:
                        yield from bps.read(det)
                    for signal in fields.values():
                        yield from bps.read(signal)
                    yield from bps.save()

                try:
                    uid = yield from one_sample_run(
                        measure, image_detectors,
                        sample_name=monitor.specimen + "_beam{kapton_beam_s}s",
                        scan_name="kapton_air_irradiation", geometry="transmission",
                        md={**(md or {}), "kapton_image_id": image_id,
                            "kapton_monitor_database": str(monitor.database),
                            "kapton_exposure_s": cfg.exposure_s,
                            "kapton_fe_recovery_eV": 6000 if energy is not None else None,
                            "kapton_oav_detector": oav.name if oav is not None else None,
                            "kapton_beam_threshold": cfg.beam_threshold})
                    outcome["run_uid"] = uid
                    # Detector/IOC may close the shutter at completion or unstage.
                    # Reopen only after SUCCESSFUL acquisition/unstage and valid gauges.
                    _ready(monitor, require_fast=False, allow_post_trip=True)
                    guard = getattr(monitor, "isolation", None)
                    yield from fast_shutter(fs, not (guard is not None and guard.tripped.is_set()), monitor=monitor)
                except BaseException:
                    outcome["status"] = "failed"
                    raise
                finally:
                    monitor.image_record(outcome)
                due += (math.floor(max(0, time.monotonic() - due) / cfg.image_period_s) + 1) * cfg.image_period_s
            yield from bps.sleep(min(0.5, max(0, deadline - time.monotonic())))
        done = True

    return (yield from bpp.finalize_wrapper(body(), cleanup()))

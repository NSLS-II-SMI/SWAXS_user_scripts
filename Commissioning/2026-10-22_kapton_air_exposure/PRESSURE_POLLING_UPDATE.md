# Pressure-read isolation — October 24

## Observed cause

At 10:00:45.260 EDT the guard tripped with all three pressure values absent.
Adjacent samples at 10:00:42.091 and 10:00:45.958 both reported normal pressure:
WAXS 0.0026 Torr, MAXS 0.0016 Torr, SAXS zero. A 3.87-second scalar-sweep delay
exceeded the former shared 3-second freshness window. No high pressure or gauge
alarm was recorded at that trip. The later 10:37:49 recovery excursion is separate.

## New behavior

- A dedicated `kapton-pressure-reader` polls only the three gauges; shutter,
  ring, BPM and TetrAMM calls cannot block it. Both readers target 1 Hz.
- `Settings.pressure_stale_s = 10.0` is a **last-good read deadline**, measured by
  monotonic time. A transport timeout does not refresh it. The last valid value
  may be used during this grace window, explicitly marked `read_error_grace`.
- No last-good reading at startup: pressure is unavailable, and guard arming fails.
- Any valid reading at/above **0.009 Torr** trips immediately when observed, before
  reading the next gauge. No multi-point debounce is applied to actual overpressure.
- Gauge alarms, negative/nonfinite values and zero WAXS/MAXS remain immediate
  faults. SAXS zero remains valid below range. The grace applies only to read/
  transport failures, not to explicit bad gauge values.
- Pressure-reader failure or expiry of a gauge deadline requests the same latched
  shutdown. Normal non-pressure stale readings still use the existing 3 s rule.
- Scalar collection may still be delayed by a slow non-pressure read. Independent
  pressure records remain in SQLite `pressure_samples`, and the single-run plan
  drains them into Tiled's `pressure_samples` stream after RE can proceed.
- SQLite pressure records and trip reasons include per-gauge age, last-good wall
  time, last-attempt wall time, value/error/alarm, classification, and ceiling.
  The scalar stream also includes `<gauge>_age_s` and `<gauge>_quality`.

The three gauge reads themselves are sequential with 2 s connection/read limits;
the reader is independent of non-pressure I/O, not independent of all possible
IOC/storage/host delays. EPS remains independent of this software guard.

## Apply between runs, preserving continuity

Do not hot-reload a running monitor. End/abort the current image run, confirm RE
idle and fast shutter closed, then preserve the database and stop services:

```python
EXPERIMENT_DATABASE = monitor.database
SPECIMEN = monitor.specimen
guard.stop()       # waits for any already-started delayed shutdown
monitor.close()    # stops both old readers before reopening the database

import importlib
import smi_plans.session
import kapton_exposure as ke
import kapton_single_run as ks
importlib.reload(smi_plans.session)
importlib.reload(ke)
importlib.reload(ks)

cfg = ke.Settings()
monitor = ke.ExposureMonitor(
    ke.profile_signals(globals()), cfg, EXPERIMENT_DATABASE,
    specimen=SPECIMEN, photon_open=ph_shutter.open_val,
    photon_closed=ph_shutter.close_val,
    resume=True, resume_weekend_update=True,
).start()
```

The explicit migration permits adding `pressure_stale_s=10.0` and audits the
old/new configuration. Existing counters and records are preserved. Earlier rows
have no new diagnostics; they are not fabricated. The new table is additive.

After verifying restored pumping, GV6/GV7/IV1 positions and pressures below the
ceiling, rearm (acknowledging the previously investigated trip):

```python
guard = ke.PressureIsolation(monitor, fs=fs, chamber=chamber_pressure).start(
    acknowledge_previous_trip=True,
)
ke.install_acquisition_suspenders(globals())
print(monitor.pressure_thread.is_alive())
print(monitor.health()["pressure_diagnostics"])

uids = RE(ks.kapton_single_run(
    monitor, fs=fs, saxs_detector=pil2M, waxs_detector=pil900KW,
    oav=OAV_writing, energy=energy, experiment_id="kapton_air_holder_01",
    duration_s=3*86400, beam_time_offset_s=116.02907729661092,
))
```

This starts a new Bluesky run and three-day duration with continuous cumulative
database totals. No live process or hardware was modified while developing this fix.

# Current procedure — 0.009 Torr, SAXS + WAXS + OAV + TetrAMM

This supersedes the earlier isolated-WAXS/0.05–0.10 Torr recipes. Historical
report numbers and completed-run acceptance records describe the actual older
settings and have not been rewritten.

## Pressure response

All three current ceilings are **9e-3 Torr**; readings at or above that value
trip. SAXS zero remains accepted as below range. Invalid/stale gauges also trip.
The independent guard must be armed, with **GV7 confirmed open** before starting.

1. Latch the trip and inhibit beam-time accumulation (upstream BPMs may remain bright).
2. Command fast shutter closed and **GV6/GV7 closed**; verify their readbacks.
3. **Wait 30 seconds after the boundary closure attempts finish.**
4. Close **pump isolation IV1** and check its readback.
5. Set **`chamber_pressure.turbo_enable` to 0**, check OnOff reads disabled.
6. Close **`chamber_pressure.turbo_cooling_valve`** and check its readback.

No vent, air-supply, nitrogen-supply or detector-power commands are sent. OnOff=0
confirms the disable setting, not rotor spin-down. The cooling-water closure is
the requested sequence; confirm it is appropriate for the turbo's cooldown
requirements in the live trial. Failure of one closure is logged and does not
prevent attempting the later pump shutdown. A stop request does not cancel the
30-second delayed shutdown. `guard.result` and SQLite `isolation` retain outcomes.

**After GV6/GV7 confirm isolation**, periodic SAXS/WAXS/OAV images continue, including
while pressure is high, along with continuous pressure/BPM/TetrAMM logging. They
are explicitly labelled `kapton_post_trip=1`. There is no energy recovery and
no explicit fast-shutter opening after the trip; detector hardware may still
cycle its shutter output. The plan closes the fast shutter after each image set.
`kapton_fast_reopened=0` identifies these post-trip image sets. No beam time is
credited after the latch. The boundary readbacks are rechecked before each set;
failed/unconfirmed isolation inhibits images rather than exposing the chamber.

The guard and monitor remain independent of RE. An actual detector error or failed
boundary isolation can stop images, while pressure logging and delayed shutdown
continue. A paused RE cannot take pictures until resumed; the guard still acts.
Software/IOC failures cannot guarantee closure; EPS remains independent.

## Load updates in idle Bluesky

Stop/abort the prior plan first. Close the fast shutter. If replacing services,
call `guard.stop()` (waits for a pending shutdown) then `monitor.close()`.

```python
import importlib
import kapton_exposure, smi_plans.session, kapton_single_run, beam_down_acceptance
importlib.reload(kapton_exposure)
importlib.reload(smi_plans.session)
importlib.reload(kapton_single_run)
importlib.reload(beam_down_acceptance)
from kapton_exposure import Settings, ExposureMonitor, PressureIsolation, profile_signals, configure_diode
from kapton_single_run import kapton_single_run
from beam_down_acceptance import live_test, verify_tiled
```

Use the local-package search-path workaround in `SINGLE_RUN_ACCEPTANCE.md` if the
Git-installed `smi_plans` cannot find `session`.

## Both live beam-down tests

FE must remain closed; GV7 must initially be open; pressures below 0.009 Torr.
Both tests configure continuous TetrAMM averaging at 1 s and take real SAXS/WAXS
1 s exposures plus OAV at its current optical exposure. Only the known ring/FE
beam suspenders are temporarily removed; temperature/other suspenders remain.

```python
# A: five image sets in one run; normal reopen/hold-open behavior.
uids = RE(live_test(globals(), apply=True))
uid = (uids.run_start_uids if hasattr(uids, "run_start_uids") else uids)[0]
verify_tiled(tiled_reading_client[uid])

# B: same hardware acquisition, but a real shutdown at ~45 seconds.
# It WILL close GV6/GV7, then IV1 and disable turbo/water after 30 seconds.
uids = RE(live_test(globals(), apply=True, trip_after_s=45, duration_s=160))
uid = (uids.run_start_uids if hasattr(uids, "run_start_uids") else uids)[0]
verify_tiled(tiled_reading_client[uid])
test_guard.result
test_monitor.health()
```

The second test keeps its monitor and latched guard accessible as `test_monitor`
and `test_guard` after the test image run ends. Verify pressure updates continue.
No valves, turbo or water reopen automatically. After inspection/recovery, stop
these test services explicitly before configuring the production run.
The Tiled verifier checks all three image arrays, valid diode data, normal
reopen flags before the trip and zero reopen flags after it, plus continuing
post-trip images and complete scalar IDs.

## Production start / resume

At the idle prompt restore the SAME profile ring and FE-enable suspenders:

```python
kapton_exposure.install_acquisition_suspenders(globals())
```

The existing `susp_beam` has a 100 mA suspend floor, 350 mA resume threshold,
and 600 s recovery delay. Those settings are not silently changed. The plan
additionally requires **ring current >=375 mA** before energy recovery and
pre-trip images, even if suspenders were disabled. Continuous logging and the
independent guard work while the RunEngine is suspended. Any suspender can delay
post-trip imaging until RE resumes; it does not delay independent pump shutdown.
If all suspenders were disabled, use the profile's `turn_on_suspenders()` at the
idle prompt to restore temperature protection as well. No BEAM_DOWN flag is
changed by the helper.

`ring.current` (`SR:C03-BI{DCCT:1}I:Real-I`) and `ring.mode`
(`SR-OPS{}Mode-Sts`) are now logged. **`Operations`, `Beamline Studies`, and
`Accel Studies` are allowed** for automatic recovery, including the weekend
studies shifts. Setup, Failure, Maintenance, Shutdown, Unscheduled Ops and
Decay Mode Ops wait. Staff must explicitly approve any
additional operating mode before adding it to `RECOVERY_RING_MODES`. The >=375 mA
check, FE and EPS enable are independent prerequisites. Ring/mode changes
create a new recovery generation when all prerequisites become satisfied.
The machine-mode record's **MINOR STATE** alarm (severity 1, status 7) is accepted
for recognized enum labels, as confirmed on the live IOC. This makes `Setup` a
valid logged state, not an allowed recovery mode. Only Operations/Beamline Studies/
Accel Studies satisfy the mode gate. Other alarm combinations remain invalid.
The ring-current threshold does not erase physically delivered beam below 375 mA
from exposure accounting; BPM2/shutter/enable remain the dose-time proxy.

Reuse the overnight database for continuity. The explicit migration below
preserves all samples/counters and records the old/new identity in
`configuration_changes`. It permits only ceilings to 0.009 Torr, read timeout
to 2 s, and adding the exact TetrAMM, EPS-enable, ring-current and ring-mode PVs. It does not fabricate
historical readings. Existing PVs, specimen and beam threshold must match.

```python
cfg = Settings()  # 0.009 Torr all chambers, 2 s PV read timeouts
signals = profile_signals(globals())
RE(configure_diode(pin_diode_ext, averaging_s=1))
EXPERIMENT_DATABASE = (
    kapton_exposure.LOG_DIRECTORY / "kapton_air_holder_01_bpm2_bpm3_waxs_oav.sqlite"
)

monitor = ExposureMonitor(
    signals, cfg, EXPERIMENT_DATABASE, specimen="kapton_air_holder_01",
    photon_open=ph_shutter.open_val, photon_closed=ph_shutter.close_val,
    resume=True, resume_weekend_update=True,
).start()
guard = PressureIsolation(monitor, fs=fs, chamber=chamber_pressure).start()

RE(kapton_single_run(
    monitor, fs=fs, saxs_detector=pil2M, waxs_detector=pil900KW, oav=OAV_writing,
    energy=energy, experiment_id="kapton_air_holder_01", duration_s=3*86400,
    beam_time_offset_s=116.02907729661092,
))
```

Other identity differences still fail with details. For a new database use
`resume=False` without resume migration flags. The offset is the separately
documented early exposure correction, applied only for the same physical holder.

TetrAMM `pin_diode` is **never staged or triggered** with the image detectors.
Its free-running channel-2 signal is sampled in `scalars` and SQLite, including
after a trip; raw current, IOC timestamp, validity and errors are recorded. It
does not gate beam presence (BPM2 > 10 still does that). Do not run other plans
which stage this same TetrAMM while the experiment is logging.

## FE position AND EPS enable for recovery

`smi_shutter_enable` already exposes **`SR:C12-EPS{PLC:1}Sts:ID_BE_Enbl-Sts`**.
It is now logged as `enabled` with timestamp, validity and alarms. Only **1**
grants permission; 0, unrecognized, stale or alarmed inputs do not.

Before pressure trip, **FE open AND enabled** is required to initiate unmanaged
6000 eV recovery, followed by feedback. Enabling while FE stays open triggers
recovery even while BPMs are dark. Brief disable/re-enable cycles are latched as
new recovery generations. Losing enable during recovery stops the move when
possible and leaves feedback disabled; the next permitted generation recovers
again. Beam accounting and pre-trip images also require enable.

Beam-down tests require FE closed and bypass the beam gate, logging the real
enable without changing it. After pressure trip there is no recovery regardless
of FE/enable; images require GV6/GV7 confirmed isolated instead.

The existing Energy device has its own completion callback which can re-enable
feedback when motion ends, including failures. The recovery plan re-disables
feedback on observed permission loss; it is not an atomic hardware interlock on
energy motion. Actual permission/interlock enforcement remains with the IOC/EPS.

Images run for the requested duration unless explicitly stopped or a detector/
isolation error occurs. The monitor remains running until explicitly stopped:

```python
RE(kapton_exposure.fast_shutter(fs, False, monitor=monitor))
guard.stop()
monitor.close()
```

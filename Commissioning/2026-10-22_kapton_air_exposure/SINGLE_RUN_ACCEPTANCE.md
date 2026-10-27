# LIVE beam-down acceptance: human-run in Bluesky

Current settings and trip sequence are in **LOW_PRESSURE_CONTINUATION.md**.
Both test variants now collect SAXS/WAXS/OAV and continuous TetrAMM with GV7 open
initially, at a **0.009 Torr** ceiling. The staged trip test uses
`live_test(globals(), apply=True, trip_after_s=45, duration_s=160)` and leaves
logging active afterward. It closes GV6/GV7, waits 30 s, then closes IV1, disables
turbo and closes water. Post-trip images continue without explicit shutter reopening.

This tests **real SAXS/WAXS/OAV images, real fast-shutter behavior, real scalar PVs,
and the actual Tiled run**. It is separate from the old `kapton_images` plan.
No commands run when these scripts are imported.

## New design

`kapton_single_run.py` uses `smi_plans.session.image_session` to create one run and
stage each camera once. It records:

- `primary`: each SAXS + WAXS + OAV image set, timestamp, beam labels, interruption flag,
  and `kapton_fast_reopened` confirmation;
- `scalars`: original ~1 Hz SQLite samples (pressures, BPM2/BPM3, shutter states,
  counters, quality flags and per-PV timestamps);
- `operations`: image starts, shutter-reopen confirmations, energy recovery and
  final shutter closure;
- `isolation`: pressure-trip stage timestamps and valve/pump/water results;
- `session_summary`: image count, starting/exported/cutoff record IDs, pending backlog.

Live display is deliberately small: `scalars` hints BPM3 `incident_flux`, `diode`,
`waxs_pressure`, and `maxs_pressure`; primary adds only `kapton_beam_s` to the
detectors' own hints. Other counters, timestamps, IDs and error strings remain
recorded as normal fields. Operations and summary explicitly have empty hints,
preventing BestEffortCallback's fallback to plotting every field. Restart the
test after reloading `smi_plans.session`, `kapton_single_run`, then
`beam_down_acceptance` to update descriptor hints; existing run descriptors do
not change retroactively.

`sample_wall` and each reading timestamp preserve sampling time, even if emission
was delayed. The Event's own time reflects emission time. Journal draining is
bounded and happens between images and during detector completion waits. SQLite
continues buffering during RE suspension. Final draining uses a fixed high-water
cutoff and reports any backlog; no unbounded in-memory queue is used.

This is an opt-in candidate requiring today's acceptance. The existing acquisition
and guard are retained. The test creates a **new uniquely named database** and
does not change the Kapton specimen's exposure totals.

## Phase A — images, shutter, scalar stream and Tiled (~130 seconds)

EPICS explicit reads allow **2 s read and 2 s connection timeouts** by default.
This is an allowance, not a sleep: normal sampling still targets 1 Hz. Slow reads
can delay a scalar sample or a pre-trigger check. Logger liveness allows a full
sequential read sweep. Pressure polling is independent with a 10 s last-good
deadline for communication failures; other scalar freshness remains 3 s. Gauge
alarms, invalid pressures and overpressure still trip immediately. Reload `kapton_exposure` before the other
modules to update these defaults. The live test creates fresh settings and a
fresh test database each time.

In the normal beamline Bluesky session, with the RunEngine idle, FE closed,
pressures valid, camera illumination/exposure ready and no other client acquiring
the cameras:

```python
# Ensure the working-tree smi-plans with the new session module is importable:
import sys
sys.path.insert(0, "/home/xf12id/smi-plans/src")
sys.path.insert(0, "/home/xf12id/SWAXS_user_scripts/Commissioning/2026-10-22_kapton_air_exposure")
from smi_plans.session import image_session
from beam_down_acceptance import live_test, verify_tiled

# Preview only:
RE(live_test(globals()))

# LIVE: 1-second WAXS and current optical exposure, 30-second cadence:
uids = RE(live_test(globals(), apply=True))
```

Expected behavior:

1. FE must read closed, GV7 open, and TetrAMM continuous configuration is applied.
   Beam/photon-current checks and energy recovery are omitted;
   **real pressure checks and FE-closed checks remain active**. No fake beam PVs.
2. Only installed `susp_beam` and `susp_smi_shutter` are temporarily removed and
   restored afterward. Temperature/other suspenders remain installed. The startup
   `BEAM_DOWN` flag is not changed.
3. Fast shutter opens. SAXS, WAXS and OAV stage once. About five image sets occur near
   0, 30, 60, 90, 120 s after staging/run opening.
4. The fast shutter is confirmed open again after every pair and checked while idle.
   Watch the shutter controller/CSS and camera file counters during this phase.
5. Normal end or failure closes the fast shutter and unstages both cameras. The
   test's own scalar monitor stops after recording the final closed state.
6. Exactly one test run is produced; beam counters stay zero because FE is closed.

If FE opens or an idle fast-shutter closure occurs, the test fails/closes rather
than silently continuing. A beam-down test does not mean bypassing physical
vacuum protection. The threshold is 0.009 Torr by default, with SAXS zero accepted.

### Tiled verification

Use the returned UID after Tiled ingestion finishes. If the profile returns a
RunEngineResult, use its `.run_start_uids`; otherwise `uids` is the UID tuple.

```python
uid = (uids.run_start_uids if hasattr(uids, "run_start_uids") else uids)[0]
run = tiled_reading_client[uid]  # already authenticated SMI raw client in profile
result = verify_tiled(run)
```

The verifier requires success, >=3 image sets, SAXS and valid TetrAMM data for the
new configuration, contiguous scalar sample IDs,
~1 Hz source timestamps, zero credited beam time, per-image shutter-reopen
confirmation, open shutter in sampled idle intervals, no final journal backlog,
matching image event counts and first/last image arrays resolvable through Tiled.
It reads only the first/last frame of each detector, not the full image sequence.
If ingestion is still pending, wait and repeat; the verifier does not flood Tiled
with an indefinite retry loop.

Also inspect the user-facing TIFF links for different event beam/time labels and
distinct image numbering, and confirm OAV live view returns after unstage.
The beam labels are zero in this test, so scan/event numbering must distinguish
files. If links overwrite, investigate naming before live irradiation.

## Phase B — optional live valve-isolation trial

This phase **closes real GV6/GV7 and fast shutter, then after 30 s closes IV1,
disables the turbo and closes cooling water**. Coordinate the
starting valve positions/pump state, keep FE closed, and use the existing
`PressureIsolation` setup from `WEEKEND_OPERATION.md`. Do not provoke a vacuum
leak or write fabricated readings to pressure PVs.

With a separate test monitor and armed guard prepared:

```python
from beam_down_acceptance import live_isolation_test
RE(live_isolation_test(guard))              # preview
RE(live_isolation_test(guard, apply=True))  # explicit synthetic trip; real closures
guard.result
monitor.health()                            # pressures must still update
```

The guard remains latched, all valves remain closed, and the monitor remains
running. Confirm actual valve readbacks in CSS. Failure of any one closure is
reported; other closures are still attempted. Explicitly stop/rearm the guard
only after inspection, as documented in the weekend procedure.

## Optional pause trial

Repeat Phase A at `duration_s=190`; pause RE between image pairs for ~10 s and
resume. The independent SQLite logger continues. After resuming, scalar records
should catch up with original timestamps and no duplicate/gapped sample IDs.
A non-rewindable wrapper prevents replaying image triggers and scalar events.
An immediate pause during an image may stop its detector and fail that exposure.
Use the normal
abort/close procedure before starting a new test run.

## Live irradiation after acceptance

Use `kapton_single_run(..., saxs_detector=pil2M, waxs_detector=pil900KW,
oav=OAV_writing, beam_down_test=False, energy=energy, ...)` with the
existing independent monitor/armed pressure guard and a persistent experiment ID.
The default image cadence comes from `monitor.settings.image_period_s` (300 s).
`beam_time_offset_s=116.02907729661092` can explicitly label the operator-confirmed
early exposure correction; the online counter is also recorded and unmodified.
Each process restart creates a new run linked by experiment ID, not an append to
an already-closed run. Previously unexported SQLite rows may be backfilled using
an explicit `start_sample_id`; record that intent to avoid double-counting runs.

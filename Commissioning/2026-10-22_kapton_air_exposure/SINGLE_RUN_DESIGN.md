# Continuation design discussion: one run per irradiation session

Status: proposed improvement, not a change to the currently commissioned image plan.

Updated operating requirements (0.009 Torr, SAXS/WAXS/OAV + TetrAMM, staged pump
shutdown and continued post-trip images) are specified in LOW_PRESSURE_CONTINUATION.md.

An opt-in implementation is now in `kapton_single_run.py`, backed by
`smi_plans.session`; the live hardware acceptance procedure and current limitations
are in `SINGLE_RUN_ACCEPTANCE.md`. Adoption awaits the human-run beam-down check.

## Recommended document layout

One Bluesky run per continuous session (or daily segment if operationally useful),
linked across restarts by `experiment_id` and `specimen`:

| Stream | Cadence | Contents |
|---|---|---|
| `primary` | 300 s, beam gated before trip | SAXS + WAXS + OAV references, image ID, trigger timestamps, exposure totals, post-trip flags |
| `scalars` | sampled ~1 Hz, including beam-off | BPM2 gate value, BPM3 incident flux, TetrAMM, WAXS/MAXS/SAXS pressures, shutter states, raw IOC timestamps, quality flags, exposure counters |
| `operations` | on transitions | FE recovery start/end, pressure trip, closure attempts/confirmations, log gaps |
| `baseline` | run open/close | energy, geometry, attenuation, pressure ceilings, vacuum mode, PV identities, software version |

Keep `primary` for images initially because the beamline's naming/symlink
preprocessor expects image filename tokens in that stream. Keeping scalars in
their own stream prevents hundreds of thousands of scalar events from pretending
to be image points. A 3-day run has ~259,200 scalar events and ~864 image pairs.

## First improvement: put the images in one run

Move `one_sample_run(...)` outside the five-minute loop. Stage WAXS and OAV once,
open the run once, and create/save one image event per pair. Use per-event
`kapton_beam_s` filename substitution, not a value frozen in the start document.
The existing run's resource/datum ownership remains intact. One stage per run is
the simplest approach; repeated stage cycles inside the same run can also produce
valid additional resources but require deliberate plugin/filename handling.

Before multi-day use, test both TIFF plugins and the file writer for repeated
triggers, datum numbering, dimensions, fixed file paths across midnight, and OAV
streaming/live-view restoration. Always wait for both detectors and confirm the
fast shutter reopens after each pair, not only after run-level unstage.
Preserve FE-opening recovery and checks immediately before each trigger.

## Scalars: sample at 1 Hz rather than blindly subscribe

`bps.monitor(signal)` emits updates at the signal's update cadence. It does not
itself enforce 1 Hz, and unchanged gauges may not emit at all. Subscribing to eight
PVs can also create eight asynchronous streams rather than one coherent sample.
Keep the current ~1 Hz sampling worker and publish each recorded snapshot as a
coherent scalar event with an explicit `sample_wall` plus per-PV timestamps.
Do not make a raw image PV a monitor stream.

The independent logger is already a durable buffer. The RunEngine can drain new
SQLite sample IDs in bounded batches to the `scalars` stream without rereading
EPICS. This avoids an unbounded in-memory queue during long suspensions and lets
each record be marked as exported. Preserve the original sample timestamps
instead of assigning the time at which a backlog is drained. Cap catch-up work
per loop so acquisition and pressure checks remain responsive.

Publishing arbitrary Bluesky documents from the logger thread needs a dedicated
document-emission component with serialization and resource ownership guarantees;
do not call the same RunEngine concurrently from the monitor thread. A proper
flyer (`kickoff/complete/collect`) is another suitable implementation, but must
support incremental collection to avoid buffering days of records until complete.

## Suspension, failure and shutdown

RunEngine suspension can delay scalar emission to Tiled; SQLite and the independent
pressure guard continue. The guard must remain independent of document publishing.
Never defer a protective closure until a `collect()` call or run cleanup.

On normal completion, drain the remaining scalar/operation records, close the run,
unstage, then explicitly disarm/stop services as appropriate. On abort, best-effort
flush what can be emitted and record the unexported sample-ID range for recovery.
A hard process restart creates a NEW run linked to the same experiment; it does
not reopen or append to a run that already emitted a stop document.

## Verification before adoption

1. Several image pairs in one run: WAXS/OAV resources and datum IDs resolve through
   Tiled; exposure-labelled links vary correctly from event to event.
2. One-Hz scalar cadence remains complete during image acquisition, FE outage,
   RE pause/suspension, and bounded backlog catch-up.
3. Pressure trip during each phase closes fast shutter/GV6/GV7/IV1, keeps SQLite
   logging, and prevents automatic reopen after pressure recovery.
4. Abort/process-restart boundaries preserve experiment totals and make missing
   or unexported intervals explicit rather than double-counting them.

This is a reusable acquisition/flyer feature when implemented: shared APIs and
tests should live in `smi-plans`, with this experiment retaining its configuration
and launch script in `SWAXS_user_scripts/Commissioning/`.

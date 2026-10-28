# Murray temperature-series review and corrective plan

**Status:** Review and future work only, 2026-10-28. The Murray script and shared
base are in use. Do not edit, reload, replace, or run either as part of this
review. Any deployment needs beamline-scientist and user approval after beamtime
or in an agreed maintenance window. This document is not a run sheet or a
hardware-recovery procedure.

## Scope and evidence

This is a review of the **whole current Murray implementation**, including its
committed code and the shared base on which it depends. Committed is not a
proxy for conforming to SMI tenets. The working-tree snapshot also had a modified
`2026C3_Murray.py` and an untracked `tmp.py`: the diff adds run notes, changes
`LINKAM_POS['sz']` from -15 to -18 mm, and changes the spot grid from 5 by 1 to
3 by 3. `tmp.py` is plain operational scratch text despite its `.py` extension.
Line references describe the reviewed snapshot and may move as beamtime
continues. Findings on the base affect other group scripts too, but this is not
a complete audit of every experiment in the directory.

References:

- [User-script ownership](../../README.md) and [repository agent guidance](../../AGENTS.md).
- [SMI user-script tenets](../../templates/_analysis/BEST_PRACTICES_DRAFT.md)
  (working draft); `../../../smi-plans/skills/composing-smi-experiments.md`,
  `legacy-swaxs-patterns.md`, and `naming-and-filename-tokens.md`.
- `../../../smi-plans/docs/BEAMTIME_DEBRIEF_2026_10.md` and
  `../../../smi-plans/docs/SCAN_ERROR_RECOVERY.md` for motion, dose and recovery.
- [Group README](README.md), [Murray script](2026C3_Murray.py),
  [shared base](YZhang_SMI_Base.py), and
  [simulation tests](tests/test_yz_base.py).

The NSLS-II facility docs lookup could not be completed: no token was mounted.
Ask the user to run `n2c-token` on the host and consult those docs before
implementation. This assessment is based on static inspection, not a test run,
live device state, or an audit of every Yugang script.

## What the experiment is trying to do

Measure transmission SAXS and WAXS simultaneously at a chosen WAXS arc while a
Linkam stage on the Huber moves through temperatures, including continuous
measurement during ramps. Move the sample between exposures to distribute dose,
keep elapsed time and temperature information, and produce names the group's
existing analysis can parse. The same script also supports a room-temperature
multi-slot holder and a manually positioned calibrant. The notes report a Huber
motor warming problem; they are historical observations, not proof of present
hardware state.

## Whole-workflow inventory

| Part | Current design and assessment |
| --- | --- |
| Load/configuration | Murray updates shared globals and builds sample/grid settings at load time; reloading the experiment retains and mutates an existing sample/counter, while loading the base initializes shared state again. Convenient interactively, but intent and recovery depend on load order and prior session state (`Murray :151-238`, base `:48-72,833`). |
| Sample setup | `new_sample` captures live coordinates and immediately moves by default, resets counters before that move, and sets global sample state (`Murray :241-257`). This is an explicit console action, but a failed move can leave changed software state. |
| Manual measurement | `measure_T` builds spot samples and delegates to `run_trans`; the base loops over arc/sample/offset then calls `expose`. Spot counters are allocated before the delegated measurement (`Murray :292-303`, base `:368-403`). |
| Isothermal series | `track_T` calls a hand-written `_track` loop that moves arc and Huber spots and opens one run per frame (`Murray :306-314,482-527`). Useful continuous time tracking, but per-frame run fragmentation and mutable counters violate the target design. |
| Stepped temperature program | `run_T_list` drives the Linkam, then runs a separate track for every target (`Murray :317-351`). It is not a single coherent run and continues after the base's default temperature timeout. |
| Continuous ramp program | `run_T_ramp` starts the controller and measures between targets through `_track` (`Murray :354-436`). This preserves the user's important science, but includes custom scheduling, global mutable state, timeout progression, and no explicit stop/abort cleanup policy for the Linkam. `off_at_end` is commented out here even though present in shared configuration; normal completion stays at the final setpoint unless `return_RT=True`. |
| Room-temperature holder and calibrant | `run_rt` and `collect_twsaxs` delegate to the same `run_trans`/`expose` stack (`Murray :439-453`). Multiple arcs/spots therefore also create one run per image, although the arc-outer order preserves slow-axis economy. The room-temperature positions are currently empty, not verified usable defaults. |
| Shared GI/other workflows | Base `run_gi`, `run_gi_temperatures`, `run_series` and `run_ec` also delegate to `expose` (`base :676-719,782-813,844-990`), so the run-per-point/naming debt is shared across experiments, not just Murray. Their alignment and other details require a separate scoped review before replacement. |
| Preview/logs | The custom preview manually interprets a subset of messages and may read current hardware; it isn't a simulated RunEngine. It replaces failed read attempts with `0.0` and shows only a few series points (`base :1104-1155`). The base also writes a separate CSV after each exposure (`:1217-1235`); a log failure warns but data collection continues. These are conveniences, not proof of correct acquisition, limits, total dose, or recoverability. |

## Assessment, with priorities

### P0: protect the active experiment and make the consequences visible

1. **Verify the changed motion and grid with the operators, not by guessing.**
   `2026C3_Murray.py:164,188,241-256` makes -18 mm a real Huber Z target when
   `new_sample()` moves, not a comment. A 3 by 3 grid contains **9** spots over
   0.4 by 0.2 mm, not the adjacent comment's 25 over 0.8 by 0.4 mm; the previous
   5 by 1 grid had 5 spots over 0.8 by 0 mm. The new grid adds Y-row changes,
   relevant to the script's warning about Huber heating; it does not establish a
   safe operating envelope. Confirm the actual sample/window, cable clearance,
   limits, motor temperatures, approved duty cycle and repeat-dose policy with
   staff. Do not turn old coordinates into defaults.
2. **Fresh is not guaranteed after nine frames.** `_next_spot()` wraps modulo
   grid length with only a warning (`:467-479`); long ramps can repeatedly dose
   the same nine positions. Preview's two frames per temperature are illustrative,
   not a complete exposure or motion count (`:410-419,500-502`). Do not treat
   the nominal frame estimate as proof of actual cadence or dose.
   For each tracked frame `_track()` passes the sample's `sx`, `sy`, and `sz`
   to `move_to()` (`Murray :512-515`, base `:173-180`), which issues sets for
   all provided coordinates even when a target is unchanged. This means more
   Huber commands than just the grid's row changes; whether the devices
   physically move or heat from repeated same-position commands is unverified.
3. **A continuation cannot be inferred from a counter.** The in-memory spot
   counter advances before motion/exposure (`:467-479,509-515`); a failure may
   consume a counter without a saved event, or expose without a saved event.
   Reloading after changing grid order preserves a count but changes its mapping
   to physical spots (`:233-238`). A new sample resets it. Before any recovery,
   inspect relevant bounded logs and run/event evidence, distinguish triggered,
   saved, failed and uncertain points, and ask staff about ambiguous dose; do
   not automatically repeat or skip an uncertain spot.
4. **Controller errors deserve a deliberate policy.** `_put()` in the shared
   base (`:725-729`) waits with `error_on_timeout=False` without checking the
   outcome; `linkam_goto()` defaults to warning and continuing, and the ramp
   similarly advances after its deadline (`Murray :406-419`). A successful
   setpoint message is not proof of readback, controller health, or arrival.
   Wall-clock ramp timeouts also include pauses/suspensions. Do not change the
   running policy unilaterally; define a staff-approved fail/hold/continue policy
   and safe recovery state for command timeouts, controller errors, and thermal
   timeouts before developing an alternative.
   There is no general `finally`/finalizer around the continuous-ramp control
   path (`Murray :422-436`); stop, abort or exception can leave whatever
   controller state was last commanded. The correct safe state is an operational
   decision, not something an agent should invent or impose during acquisition.

### P1: bring acquisition architecture into line with the tenets

5. **One coherent run per sample/measurement, not one per image.**
   `YZhang_SMI_Base.py:237-290` explicitly implements `expose()` as one
   `bp.count()` run per exposure. Murray's `_track` calls it in a loop
   (`Murray :482-527`). The script is a generator and triggers via Bluesky, but
   long series are still fragmented. Choose the logical measurement boundary
   with the scientist (e.g. one continuous temperature program per sample;
   separate manual measurements may legitimately be separate runs). One run per
   sample is a design target, not a reason to merge unrelated sessions.
6. **Keep event data authoritative; names remain compatible conveniences.**
   `expose()` reads positions and T through `bps.rd` before the run, formats
   literal values into a name, and places snapshots in `user_hints`; T and its
   setpoint are also read in primary events. These are useful records, but the
   pre-exposure name/hints can differ from the actual event after a pause or
   during a ramp (the group README `:171-173` acknowledges timing drift).
   Record changing position, temperature readback, commanded target, elapsed
   time, frame/spot identity and other required context in each image event;
   keep constant intent in run metadata/baseline. Use validated event-backed
   filename tokens where supported; verify real data keys and avoid duplicate
   reads. Preserve and test the group's existing filename grammar and current
   production export/analysis path before adopting a new template: the older
   linker described in `smi-plans/docs/STREAMS_AND_WORKFLOW.md` is marked legacy,
   so its behavior alone does not prove today's output compatibility.
7. **Prefer reusable `smi_plans` components over a parallel acquisition stack.**
   The shared base reimplements sample handling, detector/arc selection, naming,
   temperature sequencing and acquisition instead of calling `smi_plans`. Its
   thin user-facing run sheet and per-experiment settings are appropriate here;
   reusable behavior belongs in the sibling library. Evaluate the actual
   installed/public APIs and their compatibility first. The existing stepped
   `temperature_axis`/temperature preset waits for a setpoint and is **not** a
   drop-in continuous-ramp measurement. `linkam_heater()` currently calls device
   methods in its set plan (`technique_C_temperature.py:139-159`), so do not
   assume it meets the message-only tenet or matches this IOC. If needed, design
   a reusable, message-based continuous-ramp/time/spot primitive and test it in
   `smi-plans`; don't silently substitute a stepped scan or copy a new stack
   into the user script.
8. **Separate plan state and console actions.** `new_sample()` and `set_T()`
   are explicitly console helpers that call `RE`, not `RE()` nested inside a
   generator. That distinction is good. However, mutable `YZ`, `LK_SAMPLE`,
   `LK_SPOT`, and `YZ_SERIES` make state and restart behavior session-dependent.
   For a replacement, pass a frozen sample/program/configuration explicitly;
   record a batch identifier, grid geometry/version, sample identity, target
   sequence and continuation provenance. Avoid hidden global state and direct
   hardware calls inside plans; use RunEngine messages for hardware I/O.
9. **Review persistence and alignment debt as shared-library work, not an
   assumed-safe feature.** The base saves alignment files from within the
   alignment plan, overwrites a `latest` file, catches write failures, and can
   fall back to in-memory alignment (`base :506-550,595-607,646-659`). The
   temperature/GI path may retain a previous alignment after a new failure
   (`:816-827`). These paths are not part of Murray's transmission scan, but
   other users of this base depend on them. Validate alignment identity, stage,
   readback, failure handling and safe persistence with staff; avoid automatic
   reuse of stale/failed alignment merely because a file exists. Do not rewrite
   other users' currently active plans as collateral work.

### P2: maintain usability without creating false confidence

10. Preserve real strengths: clear console/plan distinction, simultaneous detector
   selection, arc/beamstop guards, snake ordering, message-based reads/moves in
   the reviewed path, structured `user_hints`, temperature in primary events,
   an operator run sheet, and simulated tests. Preserve these behaviors rather
   than deleting them to meet an abstract style rule. Console `.get()` calls are
   not by themselves evidence of direct device access inside a generator.
11. Update the stale grid description in the **future reviewed version** and
    move scratch/run notes to clearly labeled, dated non-executable notes when
    the user agrees. `tmp.py` is not valid Python, but it may be active user
    work; do not rename, delete, or execute it during this review. Keep
    experiment-specific notes and tests alongside the scripts.

## Agent implementation sequence — after approval

1. **Capture requirements without modifying the live session.** Inventory the
   exact current settings, sample/window geometry and allowed Huber movement;
   document desired ramp cadence, hold behavior, dose/reuse limits, timeout and
   stop/abort policies, detector/arc/beamstop rules, output format, and how users
   interpret their existing filenames. Ask where unsure; do not infer equipment
   safety from this document or old coordinates.
2. **Prototype separately.** Keep the live files intact. Create a versioned
   experiment-specific candidate and its tests beside the current user script;
   implement any generally reusable API and library tests in `smi-plans`.
   Validate installed-vs-checkout versions and device interfaces. Compose
   existing tested primitives only where their semantics match the required
   continuous ramp, interleaved fresh spots and detector workflow. Write down
   gaps rather than claiming unsupported functionality.
3. **Design for failure before writing controls.** Validate finite positive
   rates/cadences, nonempty grids, target ranges, bounds and limits before
   motion. Require explicit sample-specific spot capacity/reuse policy and
   report the planned absolute path, estimated move count, exposure count and
   uncertainty. Do not auto-retry failed hardware moves or override interlocks.
   Define controller write/readback validation, timeout and safe-state behavior
   with staff, including pause/resume, stop, abort and disconnect. Avoid changing
   sample state merely by loading a file.
4. **Add durable identity and conservative recovery.** Record unique logical
   run/program, target leg, point/frame and physical spot identity, grid version,
   setpoint and readback. Design continuation from documented evidence and a
   reviewed snapshot; distinguish unexposed, exposed, saved and unknown. Never
   assume no event means no exposure; never overwrite existing data. Verify
   changes in geometry or operator selection cannot silently reuse the old grid.
5. **Test offline before proposing deployment.** Use simulated RunEngine
   documents and fake devices, never EPICS or live setup. Cover balanced
   start/stop and multi-event runs; both detectors; arc selection/guards;
   changing T/target/positions/spot identity in actual events; correct naming
   keys and parser/export compatibility; first and final ramp legs and holds;
   bounded preview; grid capacity/reuse; failure before/after trigger; command
   timeout, readback mismatch, temperature timeout, controller error, and
   pause/resume/stop/abort with cleanup. Check motor move counts/order and that
   preview/load causes no hardware commands or shared-file writes. Existing
   `tests/test_yz_base.py:844-1068` offers useful simulation coverage, but its
   per-exposure-run assertions and permissive timeout/reuse expectations are
   legacy behavior, not acceptance criteria for a replacement.
6. **Human review and controlled commissioning.** Have the user and beamline
   scientist review the proposed mapping, motor/dose and controller policies,
   output names and test evidence. Only they approve a separate low-risk live
   checkout and any transition; simulation cannot certify geometry, detector
   export, hardware timing, or safety. Keep an explicit rollback to the
   existing workflow and do not reload any code into an active RunEngine.

## Instructions for the agent learning from this review

- Start with the repository `AGENTS.md`, the working-draft tenets and the
  sibling composition, legacy-pattern and naming skills. Trace the **entire
  call chain** through shared helpers; a generator, a passing test, or a commit
  does not establish one-run-per-sample or event-backed provenance. In this
  case, `run_T_ramp → _track → expose → bp.count` is the decisive chain.
- Before creating new framework code, map each requested concern to an existing
  `smi_plans` API and check its actual semantics, implementation and tests.
  Explicitly document missing behavior and device debt; do not make a short
  wrapper around incompatible stepped-temperature code and call it continuous.
- At design review, show an expected run/event/stream diagram, the source of
  every filename field, the metadata schema, hardware-motion order, dose policy,
  and abort/recovery behavior. Have tests assert those requirements, not only
  current output strings or legacy per-frame run counts. Every image event must
  contain the recorded keys needed for its filename and analysis.
- Classify evidence honestly: code inspection, simulation, actual production
  pipeline compatibility, and live commissioning are different claims. An
  illustrative preview cannot certify runtime, dose, hardware limits or even
  the total number of measurements.
- Preserve existing user-facing science and file compatibility while reducing
  technical debt. Distinguish console helpers from generator plans, and valid
  experimental exceptions from undocumented architectural shortcuts. Get human
  agreement for any behavior change, especially motion and failure handling.
- Apply the lessons to other clients of the shared base through a separately
  scoped inventory and migration, not an unreviewed bulk edit. Never present
  today's committed implementation as the standard merely because it exists.

## Completion criteria

- [ ] Approved experiment semantics and safe-state/reuse decisions are written down.
- [ ] A separate candidate preserves the agreed science and existing downstream
      data usability; reusable additions live and are tested in `smi-plans`.
- [ ] Tests demonstrate event-backed provenance, appropriate run grouping,
      bounded preview, robust failure handling and conservative recovery.
- [ ] Staff review and separately authorized commissioning are complete before
      retiring or modifying the active files. Record what was actually tested.

# SMI-SWAXS Best Practices for User Scripts (Working Draft)

**Status:** Draft for discussion. Grounded in a full survey of `SWAXS_user_scripts/`
(see `USE_CASE_TAXONOMY.md` and the `legacy_batch_*.md` / `folder_*.md` reports in this
directory for the per-file evidence).

**Audience:** SMI staff and power users writing/refactoring Bluesky data-acquisition plans.

**Goal:** define what a "good" SMI user script looks like, so that (a) new scripts are
written this way and (b) we can build tooling (a template/skill + migration helpers) to move
the ~230 legacy scripts toward it.

---

## 0. Why this exists (the problem in one paragraph)

The vast majority of SMI user scripts open and close a **separate Bluesky run for every data
point** (nested `for` loops ending in `bp.count(dets, num=1)`), label files by mutating
**global state** (`sample_id(...)`, `RE.md['sample_name']`), and record experimental context
(temperature, energy, beam current, incident angle, SDD, transmission, RH, strain, prs angle)
by **formatting it into the filename string** via `.get()`/`.value()`/`.position` at the
moment of acquisition. The result is data whose provenance lives in filenames rather than in
the data broker, that is hard to re-process or search, and that fragments one logical
experiment into thousands of disconnected runs. A smaller but important set of scripts goes
further off the rails by calling `RE(...)` inside Python loops or triggering detectors
outside the RunEngine entirely (no documents at all). This document defines the target we are
migrating toward.

---

## 1. The Tenets (principles)

Each tenet states the principle, the rationale, the **anti-pattern** it replaces, and a
**concrete exemplar** from the repo.

### Tenet 1 — One run per logical experiment, not per data point
**A single Bluesky run should hold all the data for one coherent measurement of one sample.**
Use a single `@bpp.run_decorator(md={...})` + `@bpp.stage_decorator(dets)` around an `inner()`
generator, and emit data points with `yield from bps.trigger_and_read(dets + [...])` (or a
coordinated `bp.scan`/`list_scan`/`grid_scan` where appropriate). Nested loops belong
**inside** one run, not as a sequence of `bp.count()` calls each opening a new run.

- *Rationale:* a run is the natural container for an experiment. One energy sweep, one
  temperature ramp, one phi rock, one map = **one run** with many events — not hundreds of
  one-event runs. This makes the data searchable, re-processable, and self-describing.
- *Anti-pattern (retire):* `for ...: for ...: yield from bp.count(dets, num=1)`.
- *Exemplar:* `nist/richter/Cl_nexafs.py` — a 101-point up+down energy sweep is **one run**.
  `templates/tender.py` — one run per sample wrapping the full arc×angle×energy nest.

### Tenet 2 — Capture everything as a device in the run; nothing important lives only in a filename
**All motions and all context — even context that comes verbally from the user ("I set the
temperature to 35 °C") — should be captured as a Bluesky device/Signal in the run:** in the
**baseline** if constant for the run, or in the **primary stream** if it changes.

- *Rationale:* the data broker, not the filename, is the source of truth. Temperature,
  energy, incident angle, beam current (xbpm), SDD, transmission, attenuator state, RH,
  strain, and prs angle must be *recorded*, so they can be plotted/normalized/searched later.
- *Verbal context becomes a Signal:* if a user reports a value the beamline can't read
  (e.g. an offline-set humidity, a sample-prep temperature, a doping level), create a small
  `Signal(name='...', value=...)` and include it in `trigger_and_read` (changing) or in the
  baseline (constant). Don't put it only in the filename or only in `md` prose.
- *Anti-pattern (retire):* `T = ls.input_A.get()-273.15; name = f"{sample}_{T}C"` (and all
  `.get()`/`.value()`/`.position`/`time.time()`/`db[-1].table()`-into-string variants).
- *Exemplar:* `templates/tender.py` records `incident_angle`, `energy_direction`, and the
  `target_file_name` as Signals via `trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] +
  atts + [s, incident_angle, energy_direction])`. The 2026 Harvard plans record
  `ls.input_A` as a device in the scan.

### Tenet 3 — Filenames are *derived from recorded data*, not hard-coded strings
**The output filename is built from `sample_name` plus mappings onto recorded stream/baseline
fields**, using the beamline's `{field_name}` templating — not assembled by hand from `.get()`
calls. Place changing components (e.g. `{energy_energy}`, a `{target_file_name}` that changes
through the scan) as templated references resolved from the actual event data.

- *Rationale:* this guarantees the filename matches what was actually recorded, and keeps the
  human-readable label and the machine-readable data in sync.
- *Anti-pattern (retire):* `sample_name = name_fmt.format(energy="%6.2f"%e, xbpm=xbpm3.sumX.get())`
  baked in at definition time; and the throwaway `Signal('target_file_name')` carrying a
  pre-formatted string while `md={'sample_name':'{target_file_name}'}` is left as an
  unsubstituted literal.
- *Exemplar (gold):* `nist/richter/Cl_nexafs.py`:
  ```python
  name = "CL_calibration_{energy_energy}eV_pd{pin_diode_current2_mean_value}_bpm2{xbpm2_sumX}_bpm3{xbpm3_sumX}_"
  @bpp.run_decorator(md={'sample_name': name})
  ```
  The `{...}` fields are filled from the recorded primary stream, not from `.get()`.

### Tenet 4 — Intent lives in `md={}`, passed at the plan call — not hard-coded in `RE.md`
**Standard metadata (`sample_name`, `project_name`, `geometry`, `scan_name`, and any
experiment-specific keys) belongs in the `md={}` dict passed into the run**, ideally supplied
at the plan *call* site (`my_plan(..., md={...})`) rather than mutated globally.

- *Rationale:* `md={}` is per-run, explicit, and composable. Global `RE.md` mutation and
  `sample_id(...)` are hidden state that leaks across runs, makes plans non-reentrant, and is
  a frequent source of mislabeled data.
- *Standard fields to populate:* `sample_name`, `project_name` (cf. `project_set`/`proposal`),
  `geometry` (`'transmission'`/`'reflection'`), `scan_name` (the plan's purpose), plus
  technique-specific keys. Keep these in *standard places* so they're discoverable.
- *Anti-pattern (retire):* `sample_id(user_name=..., sample_name=...)`,
  `RE.md['sample_name'] = ...`, `RE.md['sample']` used as an interprocess carrier.
- *Exemplar:* `templates/tranmission.py::multi_transmission` —
  `@bpp.run_decorator(md={'file_name':'{target_file_name}', 'scan_name':'multi_hexapod_swaxs',
  'sample_name': name, 'geometry': 'transmission'})`. (Target form additionally accepts a
  caller-supplied `md` and merges it.)

### Tenet 5 — Generally one sample per run
**A run should describe a single sample.** Multi-sample campaigns are expressed as a loop that
opens/closes a run *per sample* (Tenet 1 applied per sample), not as one giant run mixing
samples, and not as one run per point.

- *Rationale:* "one sample per run" keeps `sample_name`/baseline coherent and makes
  per-sample search/processing trivial.
- *Exemplar:* `templates/tender.py` / `tranmission.py` — `for name, ... in zip(...):` then a
  fresh decorated `inner()` run per sample.
- *Important exception → Tenet 6.*

### Tenet 6 — Minimize motion of slow / in-vacuum axes; if needed, keep multiple runs open at once
**Design scans so slow and in-vacuum axes move as little as possible.** `waxs.arc`, `prs`
(phi), and `stage.phi`/`stage.th` are slow and/or in-vacuum and should be the **outermost**
loop, traversed once, with direction reversal (`[::-1]`) to avoid backtracking. Fast axes
(`piezo.*`) go innermost.

When honoring this conflicts with "one sample per run" — e.g. you want to move the WAXS arc
**once** but collect that arc position for **every** sample on the bar — the correct solution
is to **keep one run open per sample simultaneously** and write into the appropriate sample's
run at each arc position, using run keys.

- *Rationale:* moving `waxs.arc`/`prs` per sample per angle dominates overhead and wears
  in-vacuum hardware. Interleaving lets the slow axis move N× fewer times for N samples while
  preserving one-sample-per-run.
- *Anti-pattern (retire):* `for sample: for arc: align; bp.count` (moves the arc once per
  sample) and its run-per-point cousin.
- *Exemplar (the multi-open-run template):* `legacy/30-user-Gann.py` lines 1138–1239,
  "multirun code prototype from Tom":
  ```python
  for j, md in enumerate(mds):                       # open one run per sample
      yield from bpp.set_run_key_wrapper(bps.open_run({..., **md}), f"run {j}")
      yield from bpp.set_run_key_wrapper(bps.declare_stream(..., name="primary"), f"run {j}")
  for wa in waxs_arc:                                # SLOW axis: moved once, outermost
      yield from bps.mv(waxs, wa)
      for j in range(n):                             # each sample
          yield from bpp.set_run_key_wrapper(bps.trigger_and_read([...]), f"run {j}")
  for j in range(n):
      yield from bpp.set_run_key_wrapper(bps.close_run(), f"run {j}")
  ```
  Note: with multiple runs open, use a `RunRouter`/per-run `BestEffortCallback` and disable
  interleaved tables; wrap open→…→close in `finalize_wrapper` so all runs close on error.

### Tenet 7 — Plans are generators end-to-end; never call `RE()` from inside a plan
**A plan must be a single generator the RunEngine consumes.** Never call `RE(...)` inside a
`for`/`while` loop or helper function, and never trigger detectors with `cam.acquire.put(1)` +
busy-wait outside the RunEngine.

- *Rationale:* `RE()`-in-loops and raw `cam.put` break pause/resume, suspenders, and document
  generation — and in the `cam.put` case, **no data documents are recorded at all**.
- *Anti-pattern (retire):* `for x in xs: RE(measure_one(x))`; `trigger_alldet()` doing
  `cam.acquire.put(1)`; hand-rolled `fly_scan` poking `det.trigger()`.
- *Worst offenders flagged:* SSYang, OGang, QYu, Mao, HZhang, AFurst, JiaLu, SWong*,
  chen_xpcs, Gergaud `fly_scan_ai`, CFN 2024 drivers.

### Tenet 8 — Separate input selection from the plan logic
**Keep "what to measure" (sample names, coordinates, energies, angles) out of the plan body.**
Provide it via an input-selection function or plan arguments, so the plan itself is reusable
and the per-experiment data is editable in one obvious place.

- *Rationale:* the corpus is full of plans with hard-coded coordinate tables and huge
  commented-out alternates; this makes plans un-reusable and error-prone.
- *Anti-pattern (retire):* hard-coded `names=[...]; x_piezo=[...]` inside the plan, guarded by
  `assert len(...)==len(names)` (keep the assert; move the data out).
- *Exemplar:* `templates/experiment_plan_template.py` (`get_experiment_inputs()` vs
  `main_experiment_plan(...)`) and `templates/grazing_fakhraai_template.py`.

### Tenet 9 — Preserve hard-won operational idioms (don't lose the physics when modernizing)
Modernization must **keep** the beamline knowledge embedded in legacy code, just expressed
correctly (as in-stream moves / configured signals / baseline):
- **Fresh-spot dose management** (move to unexposed spot per energy/frame) — keep as motor
  moves inside the run; the new spot position is then recorded automatically.
- **Arc-conditional detectors** (`[pil900KW] if arc<~15 else [pil900KW, pil2M]`) — keep;
  prefer separate declared SAXS/WAXS streams.
- **Beam-loss re-seek** (`if xbpm.sumX < thr: re-move energy`) and DCM suspenders — keep.
- **Align-once/measure-many** with offset caching and failure logging — keep; record alignment
  offsets as baseline/signals rather than `RE.md` lists.
- **GI in-vacuum choreography** (GV7/attenuator/beamstop sequencing) — keep.
- **Up/down energy passes, HDR brackets** — keep.

### Tenet 10 — Centralize shared infrastructure; don't copy-paste it into user files
Helpers like alignment routines, metadata builders, mode/attenuator/beamstop control, and
environment wrappers should live in **one shared place** and be imported — not duplicated into
every `30-user-*.py`. Copy-paste is *how the legacy idiom propagated* (e.g. the Patryk macro
library, `YZhang_SMI_Base.py`). Fix the idiom at the source and the corpus benefits.

---

## 2. The canonical shape (annotated skeleton)

```python
def measure_sample(name, *, t=1.0, energies=None, waxs_arc=(0,), md=None):
    """One run per sample. Context recorded in-stream. Filename from recorded fields."""
    user_md = md or {}
    dets = [pil2M, pil900KW, xbpm2, xbpm3, pin_diode]   # declare SAXS/WAXS streams as needed

    det_exposure_time(t, t)

    # Verbal / non-readable context as Signals (baseline if constant, stream if changing):
    incident_angle = Signal(name='incident_angle', value=piezo.th.position)

    # Filename templated from RECORDED fields (resolved from the event data, not .get()):
    name_tmpl = name + "_{energy_energy}eV_ai{incident_angle}_bpm{xbpm2_sumX}_"

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={
        'sample_name': name_tmpl,
        'scan_name': 'measure_sample',
        'geometry': 'reflection',
        **user_md,                     # caller-supplied intent (project_name, etc.) wins/merges
    })
    def inner():
        for wa in waxs_arc:            # SLOW axis outermost (Tenet 6)
            yield from bps.mv(waxs, wa)
            for e in energies:        # fast context innermost
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                incident_angle.put(piezo.th.position)
                yield from bps.trigger_and_read(dets + [energy, waxs, incident_angle])

    return (yield from bpp.finalize_wrapper(inner(), _cleanup()))   # always clean up on error
```

For **multi-sample + slow-axis-once**, use the run-key interleave from Tenet 6 instead of a
per-sample run.

---

## 3. Migration playbook (how to move a legacy plan up the tiers)

The acquisition-maturity tiers are defined in `USE_CASE_TAXONOMY.md` §2. Typical path:

1. **Tier 0 → 1:** replace `RE(...)`-in-loops and `cam.put` triggering with a real generator
   that yields plan messages. (Highest priority — these don't record data correctly.)
2. **Tier 1 → 2/3:** collapse the innermost `bp.count(num=1)` nest into one run: wrap the
   loops in `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)` + `inner()` and switch
   the innermost call to `bps.trigger_and_read(...)`.
3. **Tier 3 → 4:** (a) move every `.get()`/`.value()`/`.position` that was going into the
   filename into the `dets`/read list so it's *recorded*; (b) rebuild the filename as a
   `{field}`-template over those recorded fields; (c) delete `sample_id`/`RE.md` filename
   mutation; (d) pass intent via `md={}` (merging caller `md`).
4. **Throughout:** move sample tables out of the plan body (Tenet 8); keep the physics idioms
   (Tenet 9); reorder loops so slow/in-vacuum axes are outermost (Tenet 6).
5. **Where slow-axis economy matters:** convert per-sample runs into the interleaved
   multi-open-run form (Tenet 6).

### Good migration starting points (already close)
- **NEXAFS / energy sweeps:** mirror `nist/richter/Cl_nexafs.py`.
- **Multi-sample GI/transmission:** start from `templates/tender.py` / `tranmission.py`,
  then lift to Tier 4 (filename-from-fields, `md={}` merge, drop throwaway Signal).
- **Micro-mapping:** `Commissioning/microlistscan.py` + the Tier-2 mapping cohort (Aiello,
  Ferron/Fergerson which already pass `md=user_dict`).
- **XRR:** `Commissioning/bounce_down_mirror.py` (records `incident_angle`).
- **CD-SAXS:** `CDSAXS/.../test.py::cd_saxs_modern` / `simplePRS` (single `rel_scan(prs,...)`).

---

## 4. Open questions for the team (to refine before finalizing)

These came out of the survey and need beamline-staff decisions before we lock the
best-practices + build tooling:

1. **Filename templating contract.** What is the exact, supported set of `{stream_field}`
   keys the file-naming machinery resolves (e.g. `{energy_energy}`,
   `{pin_diode_current2_mean_value}`, `{xbpm2_sumX}`)? We should document the canonical list and
   the naming convention (`{device_signal_subfield}`), since the gold exemplar relies on it.
2. **Baseline vs primary stream policy.** Recommend a default baseline set (energy, SDD,
   attenuator state, sample positions, alignment offsets, temperature setpoint) so users don't
   have to think about it, and a clear rule for what must additionally go in the primary stream.
3. **Multi-open-run ergonomics.** "Tom's" prototype (Gann §1138) is the right pattern but is
   raw. Should we ship a thin helper (e.g. `multi_run(samples, slow_axis, plan_per_point,
   md_per_sample)`) plus the `RunRouter`/`finalize_wrapper` boilerplate so users don't
   re-implement it? What's the policy on the slow axis (arc/prs) granularity?
4. **Separate SAXS/WAXS streams vs arc-conditional det lists.** Do we standardize on
   `declare_stream` per detector (Gann's commented scaffold) and retire the
   `[pil900KW] if arc<15 else [...]` idiom, or keep the conditional? Affects every GI script.
5. **Shared library location & ownership.** Where do the centralized helpers (alignment,
   metadata, mode/beamstop/attenuator, environment) live, and how do user folders import them?
   `YZhang_SMI_Base.py` and the Patryk/Commissioning utilities are candidates to consolidate.
6. **In-situ / long-lived "monitoring" plans** (3D-printing, autonomous synthesis, kinetics)
   don't fit "one run per sample" cleanly. Do we standardize on **monitor streams** / fly
   scans / a "session run with many event streams" pattern for these? The printer and
   DropletReactor workflows in particular need a sanctioned shape.
7. **XPCS / burst acquisition.** `chen_xpcs` writes to `/ramdisk/` outside the document model.
   What is the sanctioned high-frame-rate capture path that still records documents?
8. **Scope of the migration tooling.** Given ~230 files, do we want (a) a `template`/skill that
   generates new Tier-4 plans, (b) an automated *linter* that flags the Tier-0/1 anti-patterns
   (`RE()`-in-loop, `bp.count(num=1)`, `sample_id`, `.get()`-into-name), and/or (c) assisted
   per-file refactors? (Recommendation: start with the linter + template/skill; the corpus is
   too large and too physics-laden for blind auto-rewrite.)

---

## 5. Pointers
- **Use-case taxonomy & per-file evidence:** `USE_CASE_TAXONOMY.md` (this directory).
- **Per-batch raw analysis:** `legacy_batch_01..10.md`, `folder_CFN.md`, `folder_CDSAXS.md`,
  `folder_small_groups.md` (this directory).
- **Gold exemplar:** `nist/richter/Cl_nexafs.py`.
- **Multi-sample templates:** `templates/tender.py`, `templates/tranmission.py`.
- **Multi-open-run prototype:** `legacy/30-user-Gann.py` (lines ~1138–1239).
- **Input/plan separation:** `templates/experiment_plan_template.py`,
  `templates/grazing_fakhraai_template.py`.
- **Closed-loop / simulated dev model:** `CDSAXS/` (esp. `DummyBluSky/`).

# smi_plans — modular, composable SMI-SWAXS acquisition

A library for building SMI-SWAXS Bluesky experiments by **composing concerns**, plus a set of
ready-made presets. This is the **target style** for new user scripts and the reference for
migrating legacy ones.

It is the practical, runnable counterpart to the analysis in `../_analysis/`:
- `../_analysis/USE_CASE_TAXONOMY.md` — the use-case archetypes seen across the corpus.
- `../_analysis/BEST_PRACTICES_DRAFT.md` — the 10 tenets these templates implement.

---

## How to think about an experiment (the composition model)

A real SMI experiment is **not** "one of A–O". It is an assembly of independent concerns,
exactly the way you plan a beamtime:

1. **Beam / q-range** — which energ(ies)? which detectors + WAXS-arc positions (the q reach)?
2. **Apparatus / geometry** — transmission or grazing? Linkam/Lakeshore? RH cell? e-chem?
3. **Sampling / scanning** — a single spot, 5 locations, a grid, a phi rock, a temperature
   ramp, an energy sweep — usually *several of these nested together*.
4. **Manual / interactive** — "swap the bar and type the thickness", "I set T=35 °C, confirm",
   "wait until I start the pump" — captured as recorded values, not lost prose.
5. **What to record** — the detectors + context Signals captured at every point.

`smi_plans._compose` lets you express this directly: a **measurement core** wrapped by a
**stack of scan axes** you nest in any order. The `technique_*` files are *presets* assembled
from these same pieces — and a GUI assembles them on the fly.

```python
from smi_plans._compose import (acquire, energy_axis, temperature_axis,
                                 incidence_axis, motor_axis)
from smi_plans.technique_C_temperature import linkam_heater

# Beam/q: SAXS+WAXS; geometry: grazing (align in setup); scanning: T -> arc -> ai -> energy -> x
heater = linkam_heater()
th0 = piezo.th.position
axes = [
    temperature_axis(heater, [30, 60, 90]),                 # slow  -> outermost
    motor_axis("arc", waxs, [0, 20], speed=2),              # slow, in-vacuum
    incidence_axis(piezo.th, th0, [0.10, 0.20]),
    energy_axis(np.linspace(2470, 2490, 41),                # DCM energy sweep
                flux_signal=xbpm2.sumX, flux_threshold=50),
    motor_axis("x", piezo.x, [0, 30, 60, 90, 120], speed=0),  # 5 fresh spots -> innermost
]
RE(acquire("PS40nm", [pil2M, pil900KW, xbpm2, xbpm3], axes,
           reads=[energy, waxs], setup=lambda: alignement_gisaxs_hex(0.1),
           geometry="reflection", scan_name="giwaxs_Tramp_NEXAFS_5loc",
           md={"project_name": "311234"}))
```

That single call is **one Bluesky run** for the whole sample experiment: temperature is moved
3×, the in-vacuum arc 6×, and every moved/changed quantity is recorded so the filename can
reference any of it — with no `sample_id`, no per-point runs, no `.get()` strings. Swap, drop,
reorder, or add axes (a `manual_step`, an `rh_axis`, a `potential_axis`) to get a different
experiment. See `recipes_combined.py` for fully-worked combinations.

> Axis order is **yours to choose**, but `acquire` warns (does not block) if you nest a slow
> axis inside a faster one (i.e. move it more often than necessary). Slow/in-vacuum axes
> (`waxs.arc`, `prs`, temperature) belong outermost.

### Presets for the common single-concern cases

When you just want the standard thing, the `technique_*` presets pre-assemble it:

```python
from smi_plans import SampleList, technique_A_energy_edge as A
bar = SampleList.from_columns(names=["s1", "s2"], piezo_x=[-56000, -45000], piezo_y=[4000, 4000])
RE(A.nexafs_bar(bar, A.energy_grid(2822), t=1.0, flux_signal=xbpm2.sumX, flux_threshold=50))
```

---

## Why this exists (the 10 tenets, enforced)

Every template — composed or preset — obeys these (see `BEST_PRACTICES_DRAFT.md` for rationale
+ the legacy anti-patterns each replaces):

1. **One run per logical sample** (or interleaved runs for slow-axis economy) — never one run
   per data point.
2. **Context is recorded as devices/Signals** in the primary stream (or baseline if constant)
   — never read with `.get()`/`.position` into a filename. *This includes values the user
   types* (a manual step puts them on a recorded Signal).
3. **Filenames are templated from recorded fields** (`{energy_energy}`, `{xbpm2_sumX}`, …)
   via `fname()` — never hand-formatted strings.
4. **Intent travels in `md={}`** — never `sample_id(...)` / `RE.md` mutation.
5. **Plans are generators end-to-end** — never `RE()` inside a plan, never `cam.acquire.put`
   + busy-wait. (User prompts use `bps.input_plan`, which the RunEngine drives.)
6. **Slow / in-vacuum axes move sparingly** (`waxs.arc`, `prs`, temperature outermost;
   interleaved runs when needed). The composition layer's guardrail enforces this culturally.
7. **Hard-won physics idioms are preserved** (fresh-spot, beam-loss re-seek, ensure-in,
   baseline) — via reusable preprocessors + axis hooks, not copy-paste.
8. **Sample tables live outside plan bodies** — in a `SampleList`.
9–10. **Shared infrastructure is centralized** in `_compose` / `_core` / `_preprocessors` /
   `_samples`.

---

## Module layout

```
smi_plans/
├── __init__.py            Package API: exposes Sample, SampleList, _compose, _core, _preprocessors.
├── _samples.py            Sample / SampleList  (PURE PYTHON — safe to import in a GUI).
├── _preprocessors.py      Opt-in plan-mutating decorators (the reusable idioms).
├── _core.py               Run-shaping primitives (one_sample_run, multi_sample_run, …).
├── _compose.py            ★ The composition layer: ScanAxis + axis builders + acquire().
├── recipes_combined.py    ★ Worked CROSS-CONCERN examples + a GUI-style spec→axes bridge.
└── technique_<A–O>_*.py   PRESET RECIPES — one per concern-bundle; assembled from _compose.
```

### `_compose.py` — the composition layer (start here)
- `ScanAxis(name, values, move=…/device=…, record=…, settle=…, per_point=…, speed=…)` — one
  loop dimension: the values, how to *visit* each, and what Signal to *record*.
- `acquire(name, dets, axes, *, reads, setup, geometry, scan_name, md, baseline, …)` — compose
  ONE run for ONE sample = `setup` + nested `axes` + `trigger_and_read`, filename auto-built
  from what the axes record, with the ordering guardrail.
- `acquire_bar(samples, dets, axes_for, …)` — one run per sample on a `SampleList`.
- Ready-made axes: `energy_axis`, `temperature_axis`, `incidence_axis`, `motor_axis`
  (arc/prs/piezo), `spatial_grid_axes` (single/line/grid), `potential_axis`, `rh_axis`,
  `time_axis`.
- Manual / interactive: `manual_step` / `manual_value` (collect a hand-set value into a
  recorded Signal), `manual_axis` (user-driven enumerated loop), `manual_loop` (open-ended
  "keep going until I stop"), `pause_for_user`.
- `nest_axes`, `SPEED_SLOW/MEDIUM/FAST`.

### `recipes_combined.py` — worked cross-concern experiments
- `giwaxs_tempramp_energy_5loc` — grazing + temperature + tender energy + incidence + microraster.
- `transmission_rh_kinetics` — RH program × time-series.
- `operando_echem_energy` — applied potential × energy sweep.
- `giwaxs_manual_swap_bar` — open-ended user-paced bar (manual swaps + typed thickness).
- `build_axes_from_spec(spec, context)` — turn a declarative axis list (from a GUI/JSON) into a
  nested `ScanAxis` stack. **This is the GUI ↔ plans bridge.**

### `_samples.py` — the sample data model (pure Python, GUI-safe)
- `Sample(name, piezo_x=…, piezo_y=…, …, hexa_x=…, …, incident_angles=[…], md={…})`
- `SampleList.from_columns(names, piezo_x=[…], …, incident_angles=…, md=…)` — paste legacy
  parallel-array tables straight in, with length validation.
- `SampleList.from_csv(path)` — header columns map to `Sample` fields; unknown columns fold
  into `md`; `incident_angles` may be space/`;`-separated in a cell.
- `SampleList.from_dicts([...])` / `.to_dicts()` — round-trips JSON for a GUI table.

### `_preprocessors.py` — opt-in, composable plan wrappers
Each is `wrapper(plan, …) -> plan` (most also have a `_decorator` form). They inject behavior
at specific message types and stay inside the document model.

| Wrapper | What it does | Replaces legacy idiom |
|---|---|---|
| `fresh_spot_wrapper(plan, motor, step)` | nudge `motor` by `step` after each event (fresh spot) | `piezo.x = xs - counter*30µm` dose walk |
| `ensure_in_wrapper(plan, setup, teardown=None)` | run `setup()` right after `open_run` (e.g. attenuators in after alignment) | manual att-close before each measurement |
| `beam_loss_reseek_wrapper(plan, flux, thr, recover)` | re-seek before an event if I0 < `thr` | `if xbpm2.sumX.get()<50: re-move energy` |
| `baseline_wrapper(plan, devices)` | record constants once at run open/close | (SDD/atten/setpoint into filename) |
| `cleanup_wrapper(plan, cleanup)` | always restore safe state on success/error/abort | bare cleanup that skips on Ctrl-C |
| `extra_dets_wrapper(plan, extra)` | append readables to every event | threading `xbpm` through every read |

### `_core.py` — run-shaping primitives
- `one_sample_run(measure, dets, *, sample_name, scan_name, geometry=None, md=None, baseline=None)`
  — the canonical Tier-4 envelope. `measure` is a zero-arg generator (a closure over your
  loop). Wraps it in one staged, decorated run with merged `md` + templated `sample_name`.
- `multi_sample_run(samples, slow_axis, slow_positions, point, *, dets, scan_name, …)`
  — **multiple runs open at once**: opens one run per sample, sweeps `slow_axis` once for the
  whole bar, writes each sample's frame into its own run via run keys. The sanctioned way to
  minimize `waxs.arc`/`prs` travel. (Generalized from the "Tom" prototype in
  `legacy/30-user-Gann.py`, with a `finalize` that closes only still-open runs on error.)
- `goto_sample(sample, …)` — expand a `Sample` into `bps.mv` for the axes that are set.
- `saxs_waxs_dets(*, use_saxs=True, use_waxs=True, arc_block_deg=15, …)` — the arc-aware
  detector list (`[pil900KW]` and `pil2M` only when the arc doesn't occlude it).
- `fname(base, *tokens)` / `COMMON_TOKENS` — build `{device_field}` filename templates.
- `merge_md(*dicts)` — shallow-merge metadata (later wins).

---

## The preset recipes (A–O) — concern-bundles, not exclusive categories

These files are **presets**: the common single-concern (or common-combination) cases,
pre-assembled from the composition layer so you can call one function for the standard thing.
They are **not** a taxonomy you must classify your experiment into — most real experiments
combine several of these concerns, which is what `_compose` / `recipes_combined` are for. Each
preset's "main axis" is named in the last column; combine it with others by dropping to
`acquire(...)`.

Each file: a module docstring (concern + gold/legacy reference), plan functions, and runnable
`example()`s. First arg of a `*_run` plan is the sample's human `name` (string); `*_bar` plans
take a `SampleList`.

| File | Concern | Main scan axis | Key plans |
|---|---|---|---|
| `technique_A_energy_edge.py` | Tender/NEXAFS edge | `energy_axis` | `energy_grid`, `nexafs_run`, `nexafs_bar` |
| `technique_B_grazing.py` | GISAXS/GIWAXS + alignment | `incidence_axis` + arc | `giwaxs_run`, `giwaxs_bar`, `giwaxs_bar_arc_economy` |
| `technique_C_temperature.py` | Temperature ramp/anneal/melt | `temperature_axis` | `lakeshore_heater`, `linkam_heater`, `temperature_ramp_run`, `isothermal_kinetics_run`, `temperature_bar` |
| `technique_D_mapping.py` | Microfocus raster | `spatial_grid_axes` | `map_line_run`, `map_grid_run`, `map_spiral_run`, `map_grid_manual_run`, `map_bar` |
| `technique_E_transmission.py` | Transmission SAXS/WAXS | (geometry + spatial) | `transmission_run`, `transmission_bar` |
| `technique_F_kinetics.py` | In-situ time-series | `time_axis` | `time_series_run`, `kinetics_run`, `blade_coating_run`, `time_series_bar` |
| `technique_G_humidity.py` | RH / solvent-vapor anneal | `rh_axis` | `set_rh`, `rh_step_series_run`, `rh_swelling_kinetics_run` |
| `technique_H_echem.py` | Electrochemistry / operando | `potential_axis` | `potential_step_run`, `operando_kinetics_run`, `doping_state_run` |
| `technique_I_cdsaxs.py` | CD-SAXS grating metrology | `prs` rock (`motor_axis`) | `cdsaxs_rock_run`, `cd_gisaxs_rock_run`, `cdsaxs_pitch_survey`, `cdsaxs_ystitch_run`, `cdsaxs_bar` |
| `technique_J_xrr.py` | X-ray reflectivity | `incidence_axis` | `xrr_run`, `xrr_resonant_run`, `xrr_liquid_run`, `xrr_bar` |
| `technique_K_tomography.py` | Tomography & texture | `prs` rotation (`motor_axis`) | `tomography_run`, `texture_pole_figure_run`, `tomography_bar` |
| `technique_L_printing.py` | In-situ 3D-printing | external trigger (monitoring run) | `printer_triggered_run`, `print_crystallization_followup_run` |
| `technique_M_autonomous.py` | Closed-loop / ML / agent | controller loop (not an axis) | `measure_for_agent`, `autonomous_loop`, `align_loop`, `ask_tell_loop` |
| `technique_N_xpcs.py` | XPCS / speckle bursts | configured burst | `xpcs_burst_run`, `xpcs_resonant_burst_run`, `xpcs_bar` |
| `technique_O_commissioning.py` | Staff calibration | (various) | `agbh_calibration_run`, `attenuator_ladder_run`, `direct_beam_scan_run` |

> **Combining presets:** to e.g. run a NEXAFS energy sweep *at each temperature in grazing*,
> you don't call three preset functions in sequence (that would make three runs); you build one
> axis stack (`temperature_axis` + `incidence_axis` + `energy_axis`) and `acquire(...)` it as
> ONE run. `recipes_combined.py` has these worked out. The presets exist for when one concern
> dominates; `_compose` exists for everything else.

Three concerns are **not** plain nested-axis scans and keep their own run shape (see open
question #6 in the best-practices draft):
- **`technique_L_printing.py`** — an "external-master monitoring run": one long-lived run that
  records a frame each time the *printer* fires (EPICS trigger bit), polled via a generator
  (`bps.sleep`), never a busy-wait.
- **`technique_M_autonomous.py`** — the decision loop is a plain Python function that is the
  **one sanctioned place** `RE(...)` is called; all acquisition still goes through proper
  single-run plans (it can call `acquire`/`measure_for_agent`), results read back from the
  broker. This is the *opposite* of the Tenet-7 anti-pattern (`RE()` inside a plan).
- **`technique_N_xpcs.py`** — high-frame-rate capture by configuring `cam.num_images` + a
  staged `trigger_and_read` so documents are emitted (fixes the legacy `cam.acquire.put` +
  busy-wait + `/ramdisk/` that recorded nothing).

---

## How to build an experiment (composition-first)

For a bespoke experiment (the common case), assemble axes — don't write a monolith:

1. **Beam / q:** choose `dets` (e.g. `saxs_waxs_dets()` or an explicit list) and the `reads`
   you always want recorded (e.g. `[energy, waxs, xbpm2, xbpm3]`).
2. **Apparatus / geometry:** write a `setup` plan run once per run (align, heater on, atten in,
   beamstop). Its moves are recorded.
3. **Sampling / scanning:** build a list of axes (`temperature_axis`, `motor_axis("arc", …)`,
   `incidence_axis`, `energy_axis`, `spatial_grid_axes`, `time_axis`, …) **outermost first**
   (slow/in-vacuum first).
4. **Manual / interactive (if any):** add `manual_step(...)` in `setup` to capture a hand-set
   value, a `manual_axis(...)` for a user-stepped dimension, or wrap the whole thing in
   `manual_loop(...)` for an open-ended user-paced bar. Typed values land on recorded Signals.
5. `acquire(name, dets, axes, reads=…, setup=…, geometry=…, scan_name=…, md=…, baseline=…)`.
   The filename is auto-built from what the axes record; the order guardrail warns if a slow
   axis is nested too deep.
6. For a bar, loop with `acquire_bar(samples, dets, axes_for, …)` (one run/sample) or use
   `multi_sample_run` for slow-axis economy across the whole bar.

Copy a function from `recipes_combined.py` and edit it. To add a brand-new *kind* of axis
(some apparatus we don't have yet), construct a `ScanAxis` directly: give it `values`, a
`move=` plan (how to reach a value) and a `record=` Signal (what to log).

### Authoring a new PRESET (when one concern recurs)

If a single concern keeps coming up, wrap the composition in a preset like the `technique_*`
files do: build the relevant axis (e.g. `energy_axis`) inside a function and call `acquire`.
`technique_A_energy_edge.py` is the reference for "preset = a thin recipe over `_compose`".

### Special run shapes (not nested-axis scans)

For an external-master monitoring run (printing), a closed-loop controller (autonomous), or a
configured detector burst (XPCS), you bypass `acquire` and use `one_sample_run` (or the
controller pattern) directly — see `technique_L/M/N`. These still obey all the tenets.

---

## Filename templating contract (important)

The SMI file writer substitutes `{<field>}` tokens in the `sample_name` metadata from each
frame's **recorded primary-stream event**. The token text is the data key of a read signal,
conventionally `<device-name>_<signal-attr>` — e.g. `energy_energy`,
`pin_diode_current2_mean_value`, `xbpm2_sumX`. A small artificial `Signal(name="incident_angle")`
that you `.put(...)` and include in `trigger_and_read` resolves as `{incident_angle}` (its
values need not be strings).

**Consequence: anything in the filename MUST be in your `trigger_and_read` list.** This is the
mechanism proven by the gold reference `nist/richter/Cl_nexafs.py`.

> Confirm with beamline staff the exact supported token set for your deployment (this is open
> question #1 in the best-practices draft).

---

## Manual / interactive steps (asking the user, capturing what they say)

Many experiments need a human in the loop: swap a sample bar, dial a hot stage by hand, start a
pump, or read a value off a prep sheet. These are first-class, composable, and — crucially —
the value the user types is **recorded as a Signal** (Tenet 2), not lost or baked into a name.

All prompts go through `bps.input_plan` (RunEngine-driven, so pause/resume still works) — never
a raw `input()`.

- **A hand-set value as run context** — put it in `setup` + `baseline`:
  ```python
  thickness = Signal(name="thickness_nm", value=0.0)
  acquire("S1", dets, axes,
          setup=lambda: manual_step("Load S1; read the prep sheet", signals=[thickness]),
          baseline=[thickness])              # -> recorded; usable as {thickness_nm}
  ```
- **A user-stepped scan dimension** (e.g. temperatures you dial by hand) — a `manual_axis`:
  ```python
  axes = [manual_axis("temp_manual", "Dial the hot stage to", values=[35, 50, 65]),
          energy_axis(energies)]             # T (manual, outer) x energy (inner), ONE run/T-block
  ```
- **An open-ended, user-paced bar** ("keep loading samples until I stop") — `manual_loop`
  wraps the per-sample plan; see `recipes_combined.giwaxs_manual_swap_bar`.
- **Just wait** — `pause_for_user("Start the pump, then <enter>")`.

Put manual steps **outermost** (they are the slowest thing in any experiment); the guardrail
treats them as slow by default.

---

## Running with multiple runs open at once (`multi_sample_run`)

When N per-sample runs are open simultaneously, the default `BestEffortCallback` table is
meaningless (it assumes one open run). Configure a `RunRouter` that builds a fresh per-run
callback and disables tables, e.g.:

```python
from bluesky.callbacks.best_effort import BestEffortCallback
from event_model import RunRouter

def _factory(name, doc):
    bec = BestEffortCallback()
    bec.disable_table()          # interleaved tables are useless
    return [bec], []

RE.subscribe(RunRouter([_factory]))
```

(The `multi_sample_run` primitive already wraps everything in `finalize`/`stage` so all runs
close and detectors unstage even on error/abort.)

---

## Environment & compatibility notes

- These modules reference beamline globals injected by the **SMI profile collection** at
  runtime (`bps`, `bpp`, `Signal`, `np`, `piezo`, `stage`, `waxs`, `prs`, `energy`, `pil2M`,
  `pil900KW`, `xbpm2/3`, `pin_diode`, `pil2M_pos`, `det_exposure_time`, alignment routines,
  …). Import/run them **inside the live beamline IPython session**. The top-of-file
  `.. important::` block in each module lists its specific requirements.
- `_samples.py` is **pure Python** (no bluesky/ophyd) and importable anywhere — including a GUI
  process. `_core` / `_preprocessors` import bluesky lazily so the package still exposes the
  sample model off-beamline.
- Validated against **bluesky 1.8.3 / ophyd 1.6.4** using simulated devices: every technique
  plan generates a well-formed message stream (balanced `open_run`/`close_run`, balanced
  `create`/`save`), and `multi_sample_run` correctly holds multiple runs open concurrently.
- `_core.declare_saxs_waxs_streams` uses `bps.declare_stream`, which requires a **newer
  bluesky** than 1.8.3. The arc-aware `saxs_waxs_dets` works everywhere; prefer it unless your
  deployment has `declare_stream`.
- Python 3.7+ (dataclasses). No 3.10+ syntax is used.

---

## Toward a GUI

The split is deliberate: a GUI builds `Sample`/`SampleList` objects (pure data), lets the user
pick a technique + parameters, and calls the corresponding `*_run` / `*_bar` plan. Because
inputs are typed and serializable (`to_dicts`/`from_dicts`/`from_csv`) and the plans take plain
keyword arguments, the same building blocks back both the CLI and a future GUI without
duplication.

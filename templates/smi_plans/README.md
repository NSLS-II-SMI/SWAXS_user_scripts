# smi_plans — modern SMI-SWAXS acquisition templates

A modular, GUI-ready library of Bluesky data-acquisition plan templates for the NSLS-II
SMI-SWAXS beamline. This is the **target style** for new user scripts and the reference for
migrating legacy ones.

It is the practical, runnable counterpart to the analysis in `../_analysis/`:
- `../_analysis/USE_CASE_TAXONOMY.md` — the A–O use-case archetypes (what users do).
- `../_analysis/BEST_PRACTICES_DRAFT.md` — the 10 tenets these templates implement.

---

## TL;DR

```python
# In the beamline IPython session (where bps, piezo, energy, pil2M ... are defined):
import sys; sys.path.append('/home/xf12id/SWAXS_user_scripts/templates')
from smi_plans import SampleList
from smi_plans import technique_A_energy_edge as A

bar = SampleList.from_columns(
    names=["P3HT_undoped", "P3HT_topdope"],
    piezo_x=[-56000, -45000], piezo_y=[4000, 4000],
    md={"project_name": "311234_Demo"},
)
energies = A.energy_grid(2822)                 # fine near the Cl K-edge
RE(A.nexafs_bar(bar, energies, t=1.0, flux_signal=xbpm2.sumX, flux_threshold=50))
```

That single call produces **one Bluesky run per sample**, records `energy`, `xbpm2/3`,
`pin_diode` in the stream, names files from those recorded fields, walks to a fresh spot each
frame, and re-seeks the beam if I0 drops — with no `sample_id`, no per-point runs, no `.get()`
strings.

---

## Why this exists (the 10 tenets, enforced)

Every template obeys these (see `BEST_PRACTICES_DRAFT.md` for the full rationale + the legacy
anti-patterns each replaces):

1. **One run per logical sample** (or interleaved runs for slow-axis economy) — never one run
   per data point.
2. **Context is recorded as devices/Signals** in the primary stream (or baseline if constant)
   — never read with `.get()`/`.position` into a filename.
3. **Filenames are templated from recorded fields** (`{energy_energy}`, `{xbpm2_sumX}`, …)
   via `fname()` — never hand-formatted strings.
4. **Intent travels in `md={}`** — never `sample_id(...)` / `RE.md` mutation.
5. **Plans are generators end-to-end** — never `RE()` inside a plan, never `cam.acquire.put`
   + busy-wait.
6. **Slow / in-vacuum axes move sparingly** (`waxs.arc`, `prs` outermost; interleaved runs
   when needed).
7. **Hard-won physics idioms are preserved** (fresh-spot, beam-loss re-seek, ensure-in,
   baseline) — via reusable preprocessors, not copy-paste.
8. **Sample tables live outside plan bodies** — in a `SampleList`.
9–10. **Shared infrastructure is centralized** in `_core` / `_preprocessors` / `_samples`.

---

## Module layout

```
smi_plans/
├── __init__.py            Package API: exposes Sample, SampleList, _core, _preprocessors.
├── _samples.py            Sample / SampleList  (PURE PYTHON — safe to import in a GUI).
├── _preprocessors.py      Opt-in plan-mutating decorators (the reusable idioms).
├── _core.py               Run-shaping primitives (one_sample_run, multi_sample_run, …).
└── technique_<A–O>_*.py   One file per use-case archetype; clean composable plans + examples.
```

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

## The technique files (A–O)

Each file: a module docstring (archetype + gold/legacy reference), composable plan functions,
and runnable `example()`s. First arg of a `*_run` plan is the sample's human `name` (string);
`*_bar` plans take a `SampleList`.

| File | Archetype | Key plans |
|---|---|---|
| `technique_A_energy_edge.py` | Tender/NEXAFS edge sweeps | `energy_grid`, `nexafs_run`, `nexafs_bar` |
| `technique_B_grazing.py` | GISAXS/GIWAXS + alignment | `giwaxs_run`, `giwaxs_bar`, `giwaxs_bar_arc_economy` |
| `technique_C_temperature.py` | Temperature ramp / anneal / melt | `lakeshore_heater`, `linkam_heater`, `temperature_ramp_run`, `isothermal_kinetics_run`, `temperature_bar` |
| `technique_D_mapping.py` | Microfocus raster mapping | `map_line_run`, `map_grid_run`, `map_spiral_run`, `map_grid_manual_run`, `map_bar` |
| `technique_E_transmission.py` | Transmission SAXS/WAXS, capillaries | `transmission_run`, `transmission_bar` |
| `technique_F_kinetics.py` | In-situ time-series (flow, tensile, drying) | `time_series_run`, `kinetics_run`, `blade_coating_run`, `time_series_bar` |
| `technique_G_humidity.py` | RH / solvent-vapor annealing | `set_rh`, `rh_step_series_run`, `rh_swelling_kinetics_run` |
| `technique_H_echem.py` | Electrochemistry / operando doping | `potential_step_run`, `operando_kinetics_run`, `doping_state_run` |
| `technique_I_cdsaxs.py` | CD-SAXS grating metrology | `cdsaxs_rock_run`, `cd_gisaxs_rock_run`, `cdsaxs_pitch_survey`, `cdsaxs_ystitch_run`, `cdsaxs_bar` |
| `technique_J_xrr.py` | X-ray reflectivity (incl. tender, liquid) | `xrr_run`, `xrr_resonant_run`, `xrr_liquid_run`, `xrr_bar` |
| `technique_K_tomography.py` | SAXS/WAXS tomography & texture | `tomography_run`, `texture_pole_figure_run`, `tomography_bar` |
| `technique_L_printing.py` | In-situ 3D-printing (external master) | `printer_triggered_run`, `print_crystallization_followup_run` |
| `technique_M_autonomous.py` | Closed-loop / ML / agent-driven | `measure_for_agent`, `autonomous_loop`, `align_loop`, `ask_tell_loop` |
| `technique_N_xpcs.py` | XPCS / coherent speckle bursts | `xpcs_burst_run`, `xpcs_resonant_burst_run`, `xpcs_bar` |
| `technique_O_commissioning.py` | Staff calibration / commissioning | `agbh_calibration_run`, `attenuator_ladder_run`, `direct_beam_scan_run` |

Three files implement **special, explicitly-flagged run shapes** (see open question #6 in the
best-practices draft):
- **`technique_L_printing.py`** — an "external-master monitoring run": one long-lived run that
  records a frame each time the *printer* fires (EPICS trigger bit), polled via a generator
  (`bps.sleep`), never a busy-wait.
- **`technique_M_autonomous.py`** — the decision loop is a plain Python function that is the
  **one sanctioned place** `RE(...)` is called; all acquisition still goes through proper
  single-run plans, results read back from the broker. This is the *opposite* of the Tenet-7
  anti-pattern (`RE()` inside a plan).
- **`technique_N_xpcs.py`** — high-frame-rate capture done by configuring `cam.num_images` +
  a staged `trigger_and_read` so documents are emitted (fixes the legacy `cam.acquire.put` +
  busy-wait + `/ramdisk/` that recorded nothing).

---

## How to author a new technique (recipe)

1. Define `SampleList` inputs in an `example()` (never hard-code tables in the plan body).
2. Write an inner `_measure()` closure that yields `bps.mv(...)` and ends each data point with
   `yield from bps.trigger_and_read(dets + [context signals])`. Put **everything you want
   recorded or in the filename** into that read list (including small
   `Signal(name="...", value=...)` objects you `.put()` each frame).
3. Build the filename template with `fname(name, "{energy_energy}eV", "ai{incident_angle}", …)`.
4. Wrap with `one_sample_run(_measure, dets, sample_name=…, scan_name=…, geometry=…, md=…,
   baseline=[constants])`. For slow-axis economy across a bar, use `multi_sample_run` instead.
5. Layer opt-in idioms (`fresh_spot_wrapper`, `beam_loss_reseek_wrapper`, `ensure_in_wrapper`)
   as needed — innermost effect first.
6. Provide a `*_bar(samples, …)` that loops the run over a `SampleList`.

Copy `technique_A_energy_edge.py` (simplest) or `technique_B_grazing.py` (alignment +
arc-economy) as your starting point.

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

# Folder Analysis: `CDSAXS/` — CD-SAXS Metrology + Auto-Alignment + Agentic-AI

**Scope:** NSLS-II SMI (12-ID, SWAXS) sub-project for **CD-SAXS** (Critical-Dimension SAXS,
semiconductor grating/line-space metrology). What began as a stack of `30-user-*` data-taking
scripts has grown into a four-part software effort: (1) classic CD-SAXS rocking-curve plans,
(2) an **auto-alignment subsystem** driven by LLM "visual sketchpad" agents, (3) a
**DummyBluSky digital-twin simulator**, and (4) a **local_ranking VLM image-ranking** pipeline.
Thousands of `*.npz`/`*.png` data files and the auto-generated `sketchpad_tmp*/` agent outputs
are intentionally ignored; this report classifies the **Python source only**.

> Classification only — no fixes proposed. Beamline vocabulary throughout.

---

## 1. Architecture overview — four sub-systems

```
                       getPV.py  (PV frame grabber)
                          │  records OAV/top-down frames → .npz, keyed by motor RBVs
                          ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │ (A) DATA-TAKING PLANS                                             │
   │  30-user-CDSAXS_Philipp.py  — production CD-SAXS/NEXAFS/GISAXS    │
   │  30-user-CDSAXS_Auto.py     — pushpin/rotation-center align scan  │
   │  Auto_alignment.../test.py  — measure(), cd_saxs_modern (NEW way) │
   └──────────────────────────────────────────────────────────────────┘
                          │ real frames (.npz)              ▲
                          ▼  convert_sample.py              │ deploy verified plans
   ┌──────────────────────────────────────────────┐        │
   │ (C) DummyBluSky  —  "digital twin"            │        │
   │  RunEngine + ophyd sim devices + KDTree image │        │
   │  library replayed from real beamline data.    │   ┌────┴──────────────────────────┐
   │  ZMQ server ⇄ AI coding-agent client.         │   │ (B) AUTO-ALIGNMENT SUBSYSTEM   │
   │  EPICS (caproto IOC, 445 PV) + in-mem modes.  │──▶│  slope_chase_{chi,theta}       │
   └──────────────────────────────────────────────┘   │  roi_alignment / gaussian_fit  │
              develop & test agents offline           │  sketchpad_agent(_v2) = AutoGen│
                                                       │  Vision-LLM Jupyter loop       │
                                                       └────────────────────────────────┘
                          ▲
                          │ OAV_writing_image stacks via Tiled
   ┌──────────────────────────────────────────────────────────────────┐
   │ (D) local_ranking  —  VLM "best-of-window" rotation-center align  │
   │  main.py / at_beamline.py / vlm_functions.py / utils.py           │
   │  Superimpose all-PRS-angle needle images → rank with Claude/GPT/  │
   │  Gemini → step toward best (x,z) → repeat (closed loop).          │
   └──────────────────────────────────────────────────────────────────┘
```

**How they relate (the through-line):**
- **(A) data-taking** is the scientific workhorse: phi/prs rocking curves of nano-gratings.
- All alignment efforts exist to make (A) faster/hands-free, since CD-SAXS demands the grating
  be precisely on the **center of rotation** and aligned in **chi/theta** before the phi rock.
- **(C) DummyBluSky** is the offline sandbox where (B) and (D) agents are developed: real OAV
  frames captured by `getPV.py` are converted into a replayable HDF5 "sample" (KDTree
  nearest-neighbor on motor coords), so an agent can "run scans" with zero beam time. The same
  device/PV names as the real beamline mean a verified plan moves to production unchanged.
- **(B) sketchpad** and **(D) local_ranking** are two competing *closed-loop alignment*
  strategies — both vision-LLM driven, both targeting the same physical goals (needle/grating
  centering, chi/theta detector-peak leveling), but with different mechanics (agent-writes-code
  vs. VLM-ranks-images).

---

## 2. CD-SAXS technique characterization

CD-SAXS is **transmission SAXS used as a metrology tool** for periodic semiconductor structures
(line/space gratings, FinFET arrays, contact-hole patterns). The measurable is the set of
**diffraction orders** from the grating pitch; their intensity-vs-tilt behavior inverts to the
cross-section profile (CD = critical dimension, sidewall angle, height, LER/roughness).

### 2.1 The phi/prs rocking curve (core measurement)
- **`prs`** = **P**recision **R**otation **S**tage (PV `XF:12IDC-OP:2{HEX:PRS-Ax:Rot}`), the slow
  axis that tilts the wafer about the vertical, sweeping the grating through Bragg conditions for
  successive diffraction orders. Synonymous with **phi** in the code (e.g. `phi_offest`).
- A measurement = **rock `prs` from −60° to +60°** (canonically **121 points**, 1°/step), taking
  one detector frame per angle on **`pil2M`** (Pilatus 2M, SAXS). Each angle samples a different
  qz slice of the reciprocal-space rod; the stack is the rocking curve.
- Variants observed:
  - `cd_saxs_new` — the standard 121-pt rock with rich filename metadata.
  - `cd_saxs_linqz` — angles chosen so **qz = tan(phi)** is *linearly* spaced (`sample_linqz`),
    giving uniform reciprocal-space sampling rather than uniform angle.
  - `cd_saxs_newLigang` — **cos(theta) exposure correction** (`exp_t/|cos|`) to flatten
    transmission-path-length variation at high tilt.
  - `..._simplePRS` — modern minimal form: `rel_scan([pil2M, pin_diode, xbpm3], prs, -60, 60, 121)`.
- **Detector y-stitch:** at large tilt the rod walks off the 2M; scripts shift `pil2M_pos.y` by
  4.3 mm and re-count (`_up`/`_down`) to stitch two detector positions.
- **Dose series** (`dose`, `mesure_rugo`): hundreds/thousands of frames at fixed angle to track
  beam-damage / measure roughness scattering.
- **Auxiliary detectors in the rock:** `pin_diode` (transmitted-beam normalization) and `xbpm3`
  (incident-flux monitor, `sumX`/`sumY`) — used for I0 normalization.

### 2.2 Sample alignment (the prerequisite, and the automation target)
Before rocking, the grating must be put on the **center of rotation** and leveled:
- **chi / theta leveling** (`piezo.ch`, `piezo.th`): a misaligned grating makes the row of
  diffraction peaks on the 2M *tilted*; aligned ⇒ the peak line is *horizontal* (slope = 0).
  Chi has a near **1:1** motor→detector-angle mapping; **theta is geometrically scaled** (the
  stage only rotates ~60°, so a non-trivial factor is learned from measurement history).
- **Rotation-center (x/z) alignment** (`piezo.x`, `piezo.z`): the grating/needle must sit on the
  prs/phi rotation axis so it stays in-beam across the whole rock. Diagnostic = **needle-tip
  "spread"** across PRS angles (−60..+60): on-axis (`OAV`/`OAV_writing`) camera images of a sharp
  needle/capillary; when centered, the tip stays put across rotation; when off-center, the tip
  traces an arc. Minimizing spread (or ranking superimposed images) finds the center.
- **Hexapod + Smaract stack:** coarse `stage`/HEX (PVs `XF:12ID...{HEX:Stg...}`), fine `piezo`
  Smaract (x,y,z,ch,th); `stage_pseudo` (in DummyBluSky) models a **lab-frame pseudo-positioner**
  with explicit rotation-center compensation matrices (Rx/Ry/Rz about theta/chi/phi centers).

### 2.3 Grating metrology workflow (end-to-end)
```
align hexapod/piezo to grating box (x,y,z) → level chi/theta (peaks horizontal)
→ put grating on rotation center (minimize tip spread) → set phi_offset (zero-order)
→ rock prs −60..+60 (121 pts) on pil2M [+pin_diode, xbpm3]  → optional qz-linear / dose / y-stitch
→ repeat per grating pitch / per sample box across the wafer
```
Multi-grating campaigns (`cdsaxsstd_2025_*`, `cdsaxs_IBM_*`, `*_yager`) iterate this over arrays
of named samples with per-sample (x, y, z, chi, theta) lookup tables and length-asserted lists.

---

## 3. Per-key-file analysis

### (A) Data-taking scripts

#### `30-user-CDSAXS_Philipp.py` — production CD-SAXS / NEXAFS / GISAXS  (≈1450 lines)
- **Use-cases:** the main user beamline file. Dozens of campaign plans: standard rocks
  (`cd_saxs_new`), qz-linear (`cd_saxs_linqz`), cos-corrected (`cd_saxs_newLigang`), pitch sweeps
  (`scan_boite_pitch`, `cdsaxs_all_pitch`), dose (`dose`), roughness (`mesure_rugo`), direct-beam
  (`mesure_db`), Ti/P-edge **NEXAFS** energy scans, **GISAXS** boxes, IBM/Yager/Philipp std runs.
- **Acquisition pattern: LEGACY (canonical).**
  - Per-angle `bps.mv(prs, theta)` then `bp.count([pil2M, pin_diode], num=...)` inside a Python
    `for` loop ⇒ **one Bluesky run per rocking *point*** (121 runs per curve).
  - Global **`sample_id(sample_name=...)`** with **context read into the filename string** via
    `.position` / `.get()`:
    ```python
    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)
        sample_name = "{sample}_num{num}_{th}deg_x{x}_y{y}_z{z}_bpm{bpm}{md}".format(
            ..., x="%.2f"%piezo.x.position, bpm="%1.3f"%xbpm3.sumX.get(), md=get_scan_md())
        sample_id(sample_name=sample_name)
        yield from bp.count(det, num=nume)      # ← per-point run
    ```
  - **Exception (more modern):** `cdsaxsstd_2025_10_simplePRS*` use a single
    `rel_scan([pil2M, pin_diode, xbpm3], prs, -60, 60, 121)` — the whole rock as **one run** with
    the flux monitor `xbpm3` as a stream detector. This is the closest-to-best example in (A).
- **Notable hardware:** `pil2M` (SAXS), `pil300KW`/`pil900KW` (WAXS, NEXAFS), `prs` (rotation),
  `piezo`(.x/.y/.z/.ch/.th), `stage`(HEX), `pil2M_pos`(.x/.y detector stitch), `pin_diode`,
  `xbpm3`, `energy`, `waxs`.

#### `30-user-CDSAXS_Auto.py` — pushpin / rotation-center alignment + VLM driver  (434 lines)
- **Use-cases:** (i) `scan_pushpin` raster of `piezo.x × piezo.z × prs` to align the rotation
  center on a pushpin/needle; (ii) end-to-end **VLM auto-alignment** `auto()` that scans, reads
  the `OAV_writing` image stack from Tiled, builds CLAHE-enhanced **all-angle-superimposed**
  images, ranks them with Claude/GPT/Gemini, and moves `piezo.x/z` to the best (x,z).
- **Acquisition pattern: MIXED, leaning MODERN-acquire / legacy-id.**
  - The scan itself is a **single multi-dim run**: `bp.list_scan([OAV_writing, OAV2_writing,
    piezo, prs], piezo.x, X, piezo.z, Z, prs, P)` (and commented `rel_grid_scan` with
    `snake_axes=True`) — **prs/x/z all in one run**, with motors carried as devices in the stream.
  - Still uses global `sample_id(... f"test000_{get_scan_md()}")` and reads back the run from
    `db.v2[scan_id]['primary']['data']['OAV_writing_image']` for downstream VLM processing.
  - `auto()` closes the loop in pure Python (no `RE()`-in-loop; it `yield from bps.mv(...)` at the
    end) — agentic post-processing layered on a single acquisition run.
- **Notable hardware:** `OAV_writing` / `OAV2_writing` (on-axis + top-down cameras whose frames
  are written into Tiled), `piezo`, `prs`. Heavy `cv2` (CLAHE, grayscale superposition).

#### `getPV.py` — raw PV frame grabber  (65 lines)
- **Use-cases:** a **standalone (non-Bluesky)** infinite loop using `p4p`/`caget` to grab
  `Cam:HEX` (top-down) and `Cam:SAM` (on-axis) frames + all hexapod/piezo/prs RBVs, saving
  `*.npz` named with every motor position. This is the **data-collection feedstock** for the
  DummyBluSky sample library and the local_ranking offline studies (`ManualAlign260128/210/`).
- **Acquisition pattern: N/A (bypasses RE entirely)** — direct Channel Access + PVAccess polling,
  1 Hz, context baked into filenames. Legacy-by-construction but deliberately so (a logger).

#### `Auto_alignment_CD-SAXS/test.py` — the MODERN reference plans  (84 lines)
- **Use-cases:** scratch file but contains the **best-practice templates**: `measure()`,
  `cd_saxs_modern()`, `phi_xz_scan()`.
- **Acquisition pattern: MODERN-leaning.** Context is added as **stream detectors**, not strings:
  ```python
  dets = det + [piezo.x, piezo.y, piezo.z, pil2M.sample_distance_mm, stage_pseudo, xbpm3.sumX]
  yield from bp.list_scan(dets, stage_pseudo.phi, np.linspace(th_ini, th_fin, th_st))  # one run
  ```
  i.e. the whole phi rock is a **single run** and SDD/phi/flux/positions ride in the document
  stream. Still uses `sample_id` for the filename, but this is the clear migration direction.
- **Notable hardware:** `stage_pseudo.phi` (lab-frame compensated rocking), `pil2M.sample_distance_mm`.

### (B) Auto-alignment subsystem (LLM sketchpad agents)

#### `sketchpad_agent.py` / `sketchpad_agent_v2.py` — the agent engine  (~825 / 845 lines)
- **Purpose (from header + first 200 lines):** a single-file **"Visual Sketchpad" agent** built on
  **AutoGen/ag2** ConversableAgents + a **Jupyter code executor**. It feeds a multimodal LLM a
  detector image and a task prompt, lets the model **iteratively write/run/inspect OpenCV+numpy
  code** (display intermediate figures, self-verify) until it prints `DONE/TERMINATE`. Multi-provider:
  Claude (Anthropic/Bedrock/Azure-Foundry/Abacus), GPT (Azure), Gemini (Abacus); image
  auto-resize to fit base64 limits. `v2` targets ag2 ≥ 0.6 / py3.12 with import shims.
- **Role:** the shared backend (`from sketchpad_agent[_v2] import run_agent`) for all four
  `*_beamline.py` alignment scripts below.

#### `slope_chase_alignment.py` — unified chi/theta slope-chase  (761 lines)
- **Use-case:** make grating diffraction peaks horizontal by adjusting **chi OR theta** (one
  `run_slope_chase(angle=...)` for both). **Phase 1:** LLM *discovers* a `measure_peak_slope(img)`
  from a raw `pil2M` frame. **Phase 2:** at each step, measure slope → **LLM verifies** the fit
  (re-detects peaks, can rewrite the function) and **predicts the next angle** (linear
  interp of detector-angle vs motor over history) → move → repeat until |slope|<0.002 or patience.
- **Acquisition pattern: MODERN-as-plan.** It is itself a **Bluesky plan** (`yield from
  bp.count([pil2M], num=1)`, `yield from bps.mv(motor, val)`, invoked `RE(run_slope_chase(...))`).
  Each measurement is a clean single-point `count`; the agentic logic wraps the plan, not the RE.
- **Notable hardware:** `pil2M`, `piezo.ch`, `piezo.th`; reads images via `db.v2[-1].primary...`.

#### `slope_chase_chi_verified_beamline.py` (1017 ln) / `..._theta_..._beamline.py` (964 ln)
- **Use-case:** standalone live-beamline variants of the above, one per angle. Chi version notes
  the ~1:1 chi↔detector-angle mapping; theta version explicitly handles the **non-1:1 stage
  geometry** (60° rotation scaling, LLM learns the factor). `snap_chi/snap_theta` quantize to a
  0.1° grid in [−4°, 4°]; `--start-*`/`--max-evals`/`--model` CLI (gpt-4o/5/5.4, claude-opus-4-5/6,
  gemini-3-pro).
- **Acquisition pattern: MIXED.** The acquisition primitives are written **both ways**: the
  documented intent is `RE(bp.count([pil2M]))`, but the in-body `acquire_detector_image` calls a
  **bare `bp.count([pil2M], num=1)`** (un-yielded generator) before reading
  `db.v2[-1].primary.read()['pil2M_image']` — a transitional, partially-wired beamline glue.
  Stubs (`get_current_position`, `move_chi`) are filled with `piezo.ch.position` /
  `yield from bps.mv(...)`. Net: a single-point `count` per eval — appropriate granularity.

#### `gaussian_fit_alignment_beamline.py` — rotation-center via paraboloid fit  (732 ln)
- **Use-case:** find optimal **x/z** (rotation center) by measuring **needle-tip spread** across
  `PRS_VALUES = [-60,-30,0,30,60]` at points on a **plus/cross pattern**, fitting a **2D
  paraboloid** `a·x²+b·z²+d·x+e·z+f` (lstsq), and predicting the minimum `(-d/2a, -e/2b)`;
  Phase-1 LLM discovers `find_needle_tip(img)`. Verification re-measures at the predicted minimum.
- **Acquisition pattern: TEMPLATE/legacy-doc.** Beamline I/O functions are **NotImplemented stubs**
  whose docstrings show `RE(bps.mv(...))` + `RE(bp.count([camera]))` per PRS angle. Designed to be
  filled in; pattern is **per-(x,z,prs) `count`** — many small runs (acceptable for camera frames).
- **Notable hardware:** on-axis camera, `piezo.x/.z`, `prs` (rotation). `scipy` paraboloid fit.

#### `roi_alignment_beamline.py` — drive needle tip into ROI box  (851 ln)
- **Use-case:** 1-D coarse step: move `piezo.x` so the needle tip lands inside a fixed **green ROI
  box** in the on-axis image. Phase-1 LLM discovers `measure_distance(img)` (green-mask centroid
  vs needle-tip topmost point, signed px); Phase-2 LLM-verified iterate with linear px↔micron
  model until |dist|<15 px. `snap_x` to 100-µm grid.
- **Acquisition pattern: TEMPLATE/legacy-doc** — same NotImplemented-stub style; per-x `count`.

**Cross-cutting (B):** all four follow the same **two-phase "discover-then-verify" recipe** and
share boilerplate: `extract_pipeline` (pull ```python blocks from agent `output.json`),
`templatize_pipeline` (lift the discovered function + hoist imports), `run_pipeline_code`
(subprocess-exec the function on a PNG, overlay detections), per-run `results.json` +
convergence PNG. The companion **`SKILL.md` / `SKILL_stage.md`** are **agent "skill" cards** (for
Claude-Code/Codex) describing slope-chase and gaussian-fit alignment in prose, including a **ZMQ
`BlueskyClient`** bridge (`client.count`, `client.move("piezo.ch", ...)`). `sketchpad_tmp*/`
contain the auto-generated `pipeline.py` outputs (20 under `sketchpad_tmp/`): one inspected
example is an LLM-written **RANSAC near-horizontal line fit** over CLAHE/connected-component peaks.

### (C) DummyBluSky — the digital-twin simulator

#### `devices.py` (394 ln) — simulated ophyd hardware
- **Purpose:** in-memory ophyd devices matching SMI names: `piezo` (SMARACT x/y/z/ch/th),
  `stage`, `waxs` (arc/bs_x/bs_y), `pil2M`/`pil900KW` (area dets), `OAV`/`OAV2` (cameras).
- **Standouts:** `SampleDetector`/`SimCamera` **trigger → read current motor positions → query a
  sample library for the nearest pre-recorded image** (threaded `Status`). `STG_pseudo` is a real
  **`PseudoPositioner`** implementing lab-frame **rotation-center compensation** (forward/inverse
  with Rx/Ry/Rz about per-axis centers) — a faithful model of the physical alignment geometry.

#### `sample.py` (184 ln) — KDTree image library
- **Purpose:** load an HDF5 "sample" (`/det/images`, `/det/coords`, `/det/coord_names`), build a
  **`scipy.spatial.KDTree`** per detector, and return the **nearest image to a motor-position
  query**. `to_xarray()` export, global `load_sample`/`get_current_sample`. This is how *real*
  beamline scans (recorded by `getPV.py`, packed by `convert_sample.py`) become a replayable
  environment for offline agent development.

#### `startup.py` (158 ln) — session wiring
- **Purpose:** `RunEngine` + `BestEffortCallback` + **suitcase-jsonl** serializer + an in-memory
  **`DocCollector` `db`** that mimics Tiled (`db[-1]`, `db.last_image()`, `db.ls()`, scan_id
  resolution). Wires every motor to every detector's lookup dict; loads first `samples/*.h5`.
  **Acquisition pattern: MODERN.** Standard `RE(bp.scan([pil2M], piezo.x, ...))` single-run idiom.

#### `experiment.py` (16 ln) / `plans.py` (33 ln) — examples + reusable plans
- `plans.py`: clean, parameterized **proper plans** (`saxs_scan`, `waxs_scan`, `saxs_waxs_scan`,
  `sample_scan`, `theta_scan` — a `piezo.th` rocking curve), each a single `bp.scan` run.
  This is the **canonical "good" shape** the project is converging toward.

**Also present (not deep-read, noted for completeness):** `devices_epics.py` /`startup_epics.py`
/`ioc.py` (caproto IOC, **445 PVs**, `WritingProsilica`→`OAV_writing` that stores frames in Tiled),
`convert_sample.py` (NPZ-folder → HDF5, grayscale+4× downsample+Blosc2/Zstd),
`user_scripts/bluesky_server.py` + `zmq_client.py` (**ZMQ RE remote control for AI agents**),
`pixi.toml`/`pixi.lock` (reproducible env). README documents an explicit **"Remote Control via AI
Agent (ZMQ)"** workflow — the simulator is purpose-built for agentic experimentation.

### (D) local_ranking — VLM best-of-window rotation-center alignment

#### `vlm_functions.py` (397 ln) / `utils.py` — multi-provider VLM ranking core
- **Purpose:** wrappers to send **N images + a system prompt** to Claude (extended-thinking
  streaming), GPT (Azure), or Gemini (Abacus) and parse a JSON **ranking** (`Rank-1..N`). Task:
  "Rank these superimposed images in terms of better needle alignment." System prompt:
  `sys_prompt_all_angles_superimposed_ranking.md`.
  - **Caveat noted (not fixed):** hard-coded API keys are committed in `vlm_functions.py`.

#### `at_beamline.py` (623 ln) — the live closed-loop driver
- **Use-case:** the production agentic alignment. `auto()` is a **Bluesky plan** that, per step:
  scans a **3×3 (x,z) raster × 5 PRS angles** via `rel_grid_scan([OAV_writing, OAV2_writing,
  piezo, prs], prs,-60,60,5, piezo.x,-s,s,3, piezo.z,-s,s,3, snake_axes=True)` (**one run**),
  pulls the `OAV_writing_image` stack from **Tiled** (`from_uri('https://tiled.nsls2.bnl.gov')`),
  builds CLAHE all-angle-superimposed PNGs per (x,z), **ranks with claude-opus-4-5 via Bedrock**,
  moves `piezo.x/z` to the winner, logs to `coordinates.txt`/`trajectory_*`, and **converges when
  the best (x,z) repeats 3×**.
- **Acquisition pattern: MIXED — MODERN acquire, legacy/agentic control loop.** The acquisition is
  a **single `rel_grid_scan` run per step** (good: prs/x/z in one run, cameras as stream
  detectors). The outer step loop is Python-level closed-loop (no `RE()`-in-loop; `yield from
  bps.mv`), reading results back through Tiled — a hybrid scan-process-decide cycle.

#### `main.py` (105 ln) — offline replay / benchmarking harness
- **Use-case:** the **offline twin** of `at_beamline.auto()`. Pulls a historical scan
  (`db2.v2[1060175]`) from Tiled, replays the same best-coordinate search over recorded frames,
  and renders the trajectory to MP4 (`video_maker.make_animation`) — used to **benchmark models**
  (`gemini-2.5-flash`, claude-opus-4-5, gpt-5, ...) without beam time.
- **Acquisition pattern: N/A (replay)** — reads Tiled `db2`, no live acquisition.

**Supporting (noted):** `azure_anthropic.py`, `db_tiled.py`, `coordinates.txt`,
`sys_prompt_all_angles_superimposed_ranking.md`, `video_maker.py`, `trajectory_*` outputs.

---

## 4. Acquisition-pattern assessment

| Layer | File(s) | Pattern | Verdict |
|---|---|---|---|
| Production CD-SAXS | `30-..._Philipp.py` (most) | per-point `bps.mv(prs)`+`bp.count`; global `sample_id` w/ `.position`/`.get()` in filenames | **LEGACY** |
| Production CD-SAXS | `..._simplePRS*` | single `rel_scan([pil2M,pin_diode,xbpm3], prs, ...)` | **MODERN-ish** (one run, flux in stream) |
| Pushpin/VLM scan | `30-..._Auto.py` | one `bp.list_scan`/`rel_grid_scan` run + agentic post-proc; still `sample_id` | **MIXED** |
| Reference templates | `test.py` (`cd_saxs_modern`,`measure`) | one `bp.list_scan`, context as **stream detectors** | **MODERN** (the target) |
| Slope-chase plans | `slope_chase_alignment.py` | proper plan, `RE(run_slope_chase)`, per-pt `count` | **MODERN-as-plan** |
| Beamline align glue | `*_verified_beamline.py`, `gaussian/roi` | NotImplemented stubs / bare `bp.count`; per-pt `count` | **MIXED / template** |
| local_ranking live | `at_beamline.py` | one `rel_grid_scan` run/step + Tiled read + VLM | **MIXED** (modern acquire) |
| DummyBluSky | `plans.py`,`startup.py` | clean single-run `bp.scan` | **MODERN** |
| PV logger | `getPV.py` | raw caget/p4p loop, no RE | **N/A by design** |

**Maps onto "single run per experiment":**
- **Legacy reality of (A):** a CD-SAXS rocking curve is *physically* one logical experiment, but
  the dominant `cd_saxs_new`-family encodes it as **121 separate runs** (one `bp.count` per prs
  angle), with the rocking angle + x/y/z/SDD/flux **stuffed into the filename string** rather than
  the document stream. This is the textbook "BAD/legacy" shape.
- **The fix is already prototyped in-repo:** `simplePRS` (`rel_scan(..., prs, -60, 60, 121)`),
  `cd_saxs_modern` (`bp.list_scan(dets+context, stage_pseudo.phi, ...)`), and the alignment
  `rel_grid_scan`s all express **prs as the outermost scanned axis of a single run** with context
  (`piezo.*`, `pil2M.sample_distance_mm`, `xbpm3.sumX`, `stage_pseudo`) carried as **stream
  Signals/devices** — i.e. the modern "one run per rock" target. Slow axes (prs/phi, and in
  campaigns the per-sample x/z/chi/th setup) are correctly outermost.
- **Net:** the *acquisition primitives* for the modern pattern exist and work; production user
  scripts simply predate them. The agentic layers (B/D) already adopt single-run `*grid_scan`
  acquisition, only differing in that their *control loop* lives in Python (read-back via Tiled),
  which is reasonable for closed-loop optimization.

---

## 5. The auto-alignment & agentic-AI angle

This folder is, in effect, a **closed-loop autonomous-alignment research platform** layered on a
metrology beamline — an emerging best-practice direction (self-driving alignment). Three angles:

- **`sketchpad_agent` (B) — "agent writes the CV code."** A vision-LLM (AutoGen + Jupyter
  executor) is shown a raw `pil2M`/OAV frame and **authors + self-verifies** the analysis function
  (`measure_peak_slope`, `find_needle_tip`, `measure_distance`) live, then a deterministic Python
  loop uses it to chase the objective (peak slope→0, tip-spread→min, ROI distance→0). The LLM also
  **proposes the next motor setpoint** from measurement history (learning the chi/theta/x↔detector
  mapping). Targets: **chi/theta leveling** (slope-chase), **rotation-center** (gaussian-fit tip
  spread), **coarse ROI capture**. The `SKILL*.md` cards package these as reusable agent skills
  with a ZMQ beamline bridge.
- **`local_ranking` (D) — "agent ranks the images."** No code-writing; instead, per (x,z) it builds
  **all-PRS-angle superimposed, CLAHE-enhanced** needle images and asks a VLM to **rank a 3×3
  window** by alignment quality, stepping toward the best cell — a derivative-free, vision-judged
  hill-climb to the **rotation center**. Multi-model (Claude/GPT/Gemini, Bedrock/Azure/Abacus) so
  models can be benchmarked.
- **`DummyBluSky` (C) — "the sandbox that makes it safe."** The crucial enabler: real OAV frames
  (`getPV.py`) become a **KDTree-replayed digital twin** with identical device/PV names, a caproto
  IOC, and a **ZMQ server letting an AI coding agent drive the RunEngine remotely**. Agents (B/D)
  are developed/benchmarked offline (`main.py` replays scan 1060175, renders MP4 trajectories),
  then the *named* `*_beamline.py` scripts run the verified logic on the real `pil2M`/piezo/prs.

Together they form the loop: **record real data → build twin → develop/verify agent offline →
deploy to beamline → close the loop (scan → VLM/agent decide → move → repeat → converge).** The
two strategies (code-writing sketchpad vs. image-ranking) are parallel bets on the same goal.

---

## 6. FOLDER SYNTHESIS

- **One technique, two eras of code.** CD-SAXS = **prs/phi rocking-curve** grating metrology on
  `pil2M`; the science is stable, but the data-taking spans a clear **legacy→modern arc** within
  the same repo.
- **Legacy is dominant in production** (`30-..._Philipp.py`): **121 `bp.count` runs per rock**,
  global `sample_id`, and **context (x/y/z/SDD/flux/angle) serialized into filenames** via
  `.position`/`.get()` — the canonical anti-pattern. No `run_decorator`/`stage_decorator`/
  `trigger_and_read`/`bpp.` appears anywhere in `CDSAXS/`.
- **The modern target already exists in-repo**, just under-adopted: `simplePRS`
  (`rel_scan(..., prs, -60,60,121)`), `cd_saxs_modern`/`measure` in `test.py`
  (`bp.list_scan(dets+[piezo.*, pil2M.sample_distance_mm, stage_pseudo, xbpm3.sumX], stage_pseudo.phi, ...)`),
  and DummyBluSky `plans.py` — **single run, prs outermost, context as stream devices.**
- **`prs` is the heart of the instrument:** the Precision Rotation Stage (=phi) is the slow
  rocking axis; `cd_saxs_linqz` (qz-linear sampling) and `cd_saxs_newLigang` (cos-tilt exposure
  correction) show real reciprocal-space-aware refinements layered on the basic rock.
- **Alignment is the bottleneck the whole effort attacks:** chi/theta **detector-peak leveling**
  (1:1 vs geometric scaling) and **rotation-center (x/z) tip-spread minimization** — the two
  prerequisites for a clean rock — are exactly what (B) and (D) automate.
- **Two competing agentic strategies, same goals.** (B) `sketchpad` = **LLM writes+verifies CV
  code** then optimizes (slope-chase / paraboloid tip-spread / ROI); (D) `local_ranking` = **VLM
  ranks superimposed images** in a 3×3 hill-climb. Both are closed-loop, multi-model, convergence-gated.
- **DummyBluSky is a genuinely strong asset:** a faithful **digital twin** (KDTree image replay
  from real frames, lab-frame `PseudoPositioner` rotation-center math, caproto 445-PV IOC,
  suitcase-jsonl, Tiled-like `db`) **plus a ZMQ AI-agent control bridge** — purpose-built so
  autonomous-alignment agents can be developed and benchmarked **without beam time**, then deployed
  unchanged (same PV/device names).
- **A clean record→twin→develop→deploy pipeline** ties it together: `getPV.py` (raw PV logger) →
  `convert_sample.py` → HDF5 sample → DummyBluSky → offline agent dev (`main.py` MP4 benchmarks) →
  live `*_beamline.py` / `at_beamline.auto()`.
- **The agentic acquisition is already modern** where it matters: both `30-..._Auto.py` and
  `at_beamline.py` use **single `bp.list_scan`/`rel_grid_scan` runs** (prs×x×z, cameras as stream
  detectors) and read back via Tiled — only the *decision loop* is in Python, which is appropriate
  for closed-loop optimization.
- **OAV_writing is the alignment data path:** the on-axis Prosilica variant that **writes frames
  into Tiled** is what every alignment scan (sketchpad image capture, local_ranking superposition)
  consumes — distinct from passive `getPV.py` PVAccess grabs.
- **Multi-vendor LLM/VLM abstraction is a recurring theme** (Anthropic/Bedrock/Azure-Foundry/
  Abacus/OpenAI), enabling model benchmarking — but note **committed API keys** in
  `local_ranking/vlm_functions.py` (flagged, not fixed) and several partially-wired beamline glue
  stubs (`*_verified_beamline.py`, `gaussian/roi`) still carrying `NotImplementedError` templates.
- **Bottom line:** a metrology beamline (legacy per-point rocking scans) onto which a complete,
  modern **autonomous-alignment + digital-twin + agentic-AI** stack has been grafted; modernizing
  the production rock to the `cd_saxs_modern`/`simplePRS` single-run shape would align (A) with the
  already-modern (B/C/D) layers.

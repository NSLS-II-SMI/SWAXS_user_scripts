# SMI-SWAXS User-Script Use-Case Taxonomy

A consolidated map of *what users actually do* at the NSLS-II SMI-SWAXS beamline,
synthesized from a full pass over `SWAXS_user_scripts/` (233 Python files: 134 in
`legacy/`, plus the per-group folders CFN, CDSAXS, Cornell, LBL, nist, SBU, UVA,
Commissioning, and `templates/`).

> Source material: the per-batch reports `legacy_batch_01..10.md`, `folder_CFN.md`,
> `folder_CDSAXS.md`, and `folder_small_groups.md` in this directory. Each lists the
> per-file evidence behind the archetypes below.

The purpose of this document is to enumerate the **totality of user needs** so the
best-practices effort can be validated against real demand — i.e. any "good script"
template/skill must be expressive enough to cover everything here.

---

## 1. Hardware & detector vocabulary (the shared substrate)

Almost every script is built from the same building blocks. A migration template must
support all of these.

**Detectors**
- `pil2M` — SAXS (in-vacuum Pilatus 2M).
- `pil900KW` — WAXS (the primary/priority detector in most modern work).
- `pil300KW` — older/secondary WAXS detector (older scripts, some transmission).
- `rayonix` — MAXS (medium-angle). Appears in a minority of groups (Tenney, Fakhraai,
  Clark, NIST_sept18, Kraus, Bolmat, Tsai, Neb, Mao, Beaucage, CMS).
- `amptek` — energy-dispersive SDD for fluorescence-yield XAS (Stingelin, Gomez_Oskar,
  Guillaume, Greer, Meli, Richter).
- `pin_diode` / `pdcurrent1` / `pdcurrent2` — transmission flux (beamstop diode).
- `xbpm2`, `xbpm3` (`.sumX`, `.sumY`) — beam-position monitors used as I0.

**Geometry / motion stages**
- **GI "double-stack":** SmarAct fine stage `piezo.{x,y,z,th}` + hexapod coarse stage
  `stage.{x,y,z,th,phi}`. `piezo.th` / `stage.th` are the incident-angle axes.
- `waxs` / `waxs.arc` — in-air WAXS detector arc; the **slow axis**. SAXS (`pil2M`) is
  routinely dropped when the arc occludes it (`[pil900KW] if waxs.arc.position < ~15
  else [pil900KW, pil2M]`).
- `prs` — Precision Rotation Stage (= phi). The rocking/rotation axis for CD-SAXS,
  pole-figure/texture GIWAXS, and SAXS/WAXS tomography. **Slow, in-vacuum.**
- `smaract` long-range x (Guillaume, CD-SAXS).
- `energy` — DCM, spanning **tender (~2.1–5 keV)** through **hard (≥11–16 keV)**.

**Beam conditioning / safety**
- Attenuator ladders `att2_5/6/9/...`, `SMIBeam().insertFoils`, `atten_move_in/out`.
- `GV7` SAXS gate-valve interlock; `pil2M.insert_beamstop('rod'|'pd'|'pin')` /
  `restore_beamstop` (newer facility API); `pil2M_bs_rod`.
- `SMI_Beamline().modeAlignment` / `modeMeasurement`, `det_exposure_time(frame, period)`.

**Environment / in-situ rigs**
- Temperature: Lakeshore `ls` (`ls.input_A`, `ls.output1.mv_temp`, `ls.ch1_read/ch1_sp`),
  Linkam `LThermal` (incl. tensile **MFS** and cryo), Instec, Gang thermal
  abstraction (`gotoT`/`getT`), cryo to ~-70 °C / Kelvin set.
- Humidity/RH: Moxa mass-flow controllers, `setDryFlow`/`setWetFlow`/`readHumidity`,
  `set_humidity`.
- Flow/solution: `syringe_pu` syringe pumps, blade-coater (Thorlabs translator),
  liquid/flow cells, droplet reactors.
- Electrochemistry: gate-bias / potential ladders (Meli, Karen, Richter doping).
- 3D-printer: EPICS digital-IO handshake (`XF:11ID-CT{M1}bi2/3/4`), nozzle/filament
  alignment.
- `OAV_writing` / `OAV2_writing` — on-axis optical camera, writes frames to Tiled.

---

## 2. The acquisition-pattern spectrum (maturity axis)

Independent of *what* science is done, every script sits somewhere on this axis. This is
the axis the best-practices effort is trying to move the corpus along.

| Tier | Name | Signature | Prevalence |
|------|------|-----------|------------|
| 0 | **Outside the document model** | `cam.acquire.put(1)` + busy-wait on raw PV; or `RE(...)` called inside a Python `for`/`while`; data to `/ramdisk/` | Small but important: `chen_xpcs`, Yu-Chung `trigger_alldet`, Gergaud `fly_scan_ai`, SSYang, OGang, QYu, Mao, HZhang, AFurst, JiaLu, SWong/SWong2/XZhang2, NIST_sept18 `fly_scan` |
| 1 | **Legacy run-per-point** | nested `for` loops, innermost `yield from bp.count(dets, num=1)` → one Bluesky run per data point; `sample_id(user_name, sample_name)` global filename state; context (T, energy, xbpm, SDD, angle) read via `.value`/`.get()`/`.position` and **string-formatted into the filename** | **The overwhelming majority** of all files |
| 2 | **Coordinated single scan** | one `bp.scan`/`rel_scan`/`list_scan`/`grid_scan`/`rel_grid_scan`/`inner_product_scan` per logical unit, with readbacks recorded as detector channels; still `sample_id` naming | The "best legacy": micro-mapping cohort (Ferron, Fergerson, Luo, IIT, Aiello, Hegmann, Chopra), `cd_saxs_modern`/Kline2, Telles, Greer, Kiick |
| 3 | **Modern envelope, legacy interior** | correct `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md={...})` + `inner()` + `bps.trigger_and_read(...)`, BUT hard-coded bars, `.get()`-into-string filenames, throwaway `target_file_name` Signal, unsubstituted `'{target_file_name}'` placeholder | The leading edge of most groups' 2025–2026 code: `tender.py`/`tranmission.py` templates, Richter 2025+, Guillaume 2025_3, McNeil `*_newsecurity`, Gomez 2026_1, Su 2025–26, `multi_giwaxs_tender.py`, `s_edge_grazing.py` |
| 4 | **Fully modern (target)** | single run per logical sample/experiment; context recorded as Signals/devices in the **primary stream** (or baseline if constant); **filename templated from recorded stream fields** (`{energy_energy}`, `{pin_diode_current2_mean_value}`, `{xbpm2_sumX}`); `md={}` carries intent | **Rare.** Best in-repo exemplars: `nist/richter/Cl_nexafs.py` (gold), `p_nexafs.py`, `Commissioning/bounce_down_mirror.py` XRR, `Commissioning/microlistscan.py`, DummyBluSky `plans.py`, `CDSAXS/.../test.py::cd_saxs_modern` |

**Key empirical findings about the axis:**
- The corpus is migrating, but unevenly. **No folder is uniformly Tier 4.**
- "Refactoring" has mostly meant *reorganization* (carving small purpose-named files out
  of the giant `30-user-*.py` run-books) **without** changing the acquisition tier.
  `bladecoating.py`, `capillary_transmission_saxs.py`, `temperature.py`,
  `micro_tempstage.py` are renamed but still Tier 1.
- The **single biggest data-provenance gap** is universal: experimental context
  (temperature, energy, beam current, SDD, incident angle, transmission, elapsed time,
  RH, strain, prs angle) is read with `.get()`/`.value`/`.position` and **baked into the
  filename string** instead of being recorded as a device in the stream or baseline.
- Several mature *operational* idioms recur **inside otherwise-legacy bodies** and must be
  preserved by any template (see §5).

---

## 3. Scientific use-case archetypes (the "what")

These are the high-level intents. Counts are approximate "files where this is a primary
mode"; many files span several.

### A. Tender-energy resonant scattering & NEXAFS (TReXS / edge scanning) — **most common**
- **Intent:** energy sweep across an absorption edge while collecting scattering and/or
  fluorescence-yield, in grazing or transmission geometry. Resonant/anomalous SAXS/WAXS.
- **Edges seen:** S K (~2470–2490), Cl K (~2820–2890), P K (~2145), Ca K (~4030–4150),
  K K, Ti L (~5000), Fe, Co, Cu, Zn, Se, Br K (~13.5 keV), Rb (~15.2), Ag L3, Cd, Sn L3,
  Te L3, Ru L (~2840), Pt L3 (~11.5), In, Ir, Bi, Zr, Ce, Mn, As, Cr, Mo. Fine grids
  (~0.2–0.5 eV) near the edge, coarse in the pre/post-edge.
- **Hallmarks:** `for e in energies: mv(energy, e); sleep; <acquire>`; up+down ("upsweep/
  downsweep") passes for reversibility; fresh-spot x/y dose-walk per energy point;
  `xbpm.sumX < threshold` beam-loss re-seek; `amptek` fluorescence; pin-diode I0
  calibration vs xbpm.
- **Representative files:** Richter (huge), Guillaume, Gregory, Reynolds, Meli, Stingelin,
  Hoang, Gordon, Gomez_Oskar, Zhengxing, McNeil, Collins, Brett, Berlinger, Hanqiu, Zhang,
  Ruan, Toney, Cordova, Tiwale, Billinge, JiaLu, JKim, Chaney, RLi, Gomez_Sintu, Su, Gann,
  Gu, NIST, Francisco, Sprunt; `nist/richter/*` (the cleanest), `Commissioning/s_edge_grazing.py`.

### B. Grazing-incidence thin-film scattering (GISAXS / GIWAXS) + alignment — **most common**
- **Intent:** thin films / surfaces measured at one or more incident angles, often across
  multiple WAXS-arc positions, with per-sample alignment.
- **Hallmarks:** sample alignment routine (`alignement_gisaxs_doblestack`,
  `alignement_gisaxs_hex`, `alignCai`, `alignBoc`, `alignement_xrr_xmotor`); incident-angle
  loop (`ai0 + ai`); WAXS-arc loop; SAXS dropped when arc occludes.
- **Representative files:** nearly every group. Fakhraai/Harvard, Giri, Headrick, Reuther,
  ETsai, Braunschweig, Kim2/3/4/5/Kim, Fernandez, Ocko, PPGwang, Herzig, Kumacheva, QYu,
  Thomas, White, Thedford, Andrew, Gill, Netzke, Neb, Tsai, dudenas, QChen, CFN GIWAXS bars.
- **Sub-mode — multi-sample "bar":** hard-coded parallel arrays `names[]/x_piezo[]/
  y_piezo[]/z_piezo[]/x_hexa[]/...` guarded by `assert len(...)==len(names)`, looped to
  align+measure each sample. This is the dominant orchestration shape across the corpus and
  the one the **"multiple open runs / one sample per run"** discussion most directly affects.

### C. In-situ temperature ramping / annealing / melting kinetics — **very common**
- **Intent:** measure scattering vs temperature (ramp, isothermal hold, melting Tm, ODT,
  crystallization, glass transition).
- **Hallmarks:** Lakeshore/Linkam/Instec setpoint + equilibration-with-timeout; per-setpoint
  re-alignment / x-creep; temperature usually written into the filename (legacy) — should be
  a streamed/baseline device.
- **Representative files:** Tenney, RPI, SSYang, Reven, Gordon, Clark, Stingelin (cryo),
  Harvard 2026_1 (best — records `ls.input_A` as a device), Gu, OGang, Kumacheva, Bolmat,
  Andrew, Marino, Gorecka, Cai, AFurst (DNA-NP Tm), White, Thomas, AFRL, CFN Linkam bars,
  UVA Cai `temperature.py`, nist Aiello `micro_tempstage.py`.

### D. Microfocus / raster mapping (spatial) — **common**
- **Intent:** map a heterogeneous sample (tissue, fibers, films, gratings, printed parts)
  with a microbeam over an x/y (or x/z) grid, line, or spiral.
- **Hallmarks:** `bp.rel_grid_scan` / `rel_scan` / `rel_spiral` / `scan_nd` / `cycler` —
  these are the **Tier-2 "best legacy"** files (one run per map). Often paired with live
  transmission and OAV snapshots.
- **Representative files:** Aiello (line/grid/spiral), Hegmann, Tenney, ETsai, Pollozi,
  XZhang, Kraus, NIST, OGang, EHu, UCR (biomineral), Clark (teeth/chiton), Ferron, Fergerson,
  Luo, IIT, Chopra, Thedford, Patryk, Tsai, Cai, Cornell/Singer (grain mapping), CFN
  `getSamMap`, `Commissioning/microfocus.py` / `microlistscan.py`.

### E. Transmission SAXS/WAXS — capillaries, wells, solution/bio, multi-sample bars — **common**
- **Intent:** transmission scattering of solutions, suspensions, capillaries, well-plates;
  often multi-spot averaging and quantitative transmission.
- **Hallmarks:** pin-diode / beamstop-diode transmission; `db[-1].table()` reach-back to
  compute transmission online (legacy provenance smell); multi-position averaging along a
  capillary; HDR multi-exposure brackets.
- **Representative files:** Telles, Sarkar, Xu, Kiick, HZhang, Katz, Quan, Foster, Bolmat,
  Fang, EHu, Kraus, Herzig, Liu-Akron (quantitative T), Reuther, Pollozi (hydrated peptides),
  SWong/SWong2/XZhang2 (nanoparticle synthesis), UVA Cai `capillary_transmission_saxs.py`,
  SBU Takeuchi, CFN transmission "static bar" template, `templates/tranmission.py`.

### F. In-situ kinetics / time-series (non-thermal) — **common**
- **Intent:** follow a process in time — solvent evaporation/drying, blade-coating,
  flow/mixing, tensile/strain, UV exposure, swelling, self-assembly, nanoparticle growth.
- **Hallmarks:** `for i in range(N): ... sleep` or wall-clock `t0=time.time()` loops; frame
  index/elapsed-time folded into filename; burst-mode "warm-up" dummy counts.
- **Representative files:** Modestino (syringe flow), Harvard (tensile/pull), Reynolds, Murray
  (50000-iter colloid assembly), Chaney (Linkam + syringe oscillation), Wenkai/Cai (tensile),
  Mao (RH cycling), SSYang (liquid-interface NP + UV), Zhang (`song_tensile_*`), Jones (RH),
  LBL `bladecoating.py`, CFN `NanoSyn` / `InSituGrowth` / `InSituDemo`.

### G. Humidity / RH-controlled in-situ (SVA) — **niche but recurring**
- **Intent:** solvent-vapor annealing / controlled humidity swelling kinetics.
- **Hallmarks:** dry/wet N2 mixing via MFCs, long equilibration, `readHumidity`.
- **Representative files:** Richter (SVA), ETsai, Jones, Mao, (offline-hydrated: Gomez_Sintu).

### H. Electrochemistry / operando doping — **niche**
- **Intent:** scattering/NEXAFS vs applied potential or chemical doping state.
- **Representative files:** Meli (operando + fluorescence), Karen (operando, ≤5000 frames),
  Richter (gate-bias mV ladders, FeCl3/KClO4 doping).

### I. CD-SAXS / CD-GISAXS — critical-dimension grating metrology — **specialized, its own subsystem**
- **Intent:** reconstruct nanograting line/space cross-section (CD, sidewall angle, LER,
  pitch walking, overlay) by rocking the grating through reciprocal space.
- **Hallmarks:** `prs` (phi) rocking curve, canonically **-60°→+60° in 121 points** (up to
  2001 for CD-GISAXS) on `pil2M`; bracketing reference frames at a `phi_offset`; detector
  y-stitch (`pil2M_pos.y ±4.3 mm`) for the module gap; multi-pitch x-offset surveys; qz-linear
  sampling; cos-tilt exposure correction.
- **The dominant legacy form is one run per rocking angle** (121 runs/grating). The modern
  single-`rel_scan(prs, ...)` form already exists in-repo but is under-adopted.
- **Representative files:** `30-user-CDSAXS.py`, Gergaud, Yager+Kline (shared `cd_saxs`
  toolkit), Kline2 (`cd_saxs_modern`), the entire `CDSAXS/` subsystem (see §4).

### J. X-ray reflectivity (XRR) — **niche**
- **Intent:** specular reflectivity vs incident angle (incl. resonant/tender, liquid surfaces).
- **Representative files:** Gann (resonant XRR), Cordova (Sn-edge XRR), Richter (`xrr_spol_waxs`),
  `Commissioning/bounce_down_mirror.py` (the clean modern reference — records `incident_angle`
  as a Signal), `Commissioning/bounce_down_mirror` BDM toolkit.

### K. SAXS/WAXS tomography & texture/pole-figure — **emerging / niche**
- **Intent:** rotation series (`prs`) for tomographic reconstruction or texture/orientation.
- **Representative files:** CFN `2026C1_Tomo.py` (`run_tomo`), Kang, Tiwale (`allprs`),
  34-oleg / 35-oleg (`inner_product_scan` coupled rotation).

### L. In-situ 3D-printing / additive manufacturing (operando) — **niche, distinctive**
- **Intent:** follow crystallization/structure during extrusion printing; printer is the
  master, beamline reacts to print events.
- **Hallmarks:** long-lived polling generator gated by external EPICS trigger bits; beam
  positioned at the middle of the extruded filament (height offset from derivative-edge
  substrate alignment); ~30-min repeated WAXS-arc sweeps to track crystallization.
- **Representative files:** `30-user-ECD-3dprinterLutz*.py`, `3dprinterLutz`, Printer, Cai
  (continuous-acquisition), Yu-Chung, Headrick (roll-to-roll), Hegmann.

### M. Autonomous / closed-loop / ML-driven — **emerging frontier**
- **Intent:** ML/optimizer (BoTorch) or LLM/VLM agent drives the experiment — autonomous
  droplet nanoparticle synthesis, or autonomous CD-SAXS alignment.
- **Representative files:** CFN `DropletReactor`/`DropletHolder` (npz/BoTorch closed loop,
  2024C3_Drop, 2025C2_SMI, CMS_2025C1); the `CDSAXS/Auto_alignment_CD-SAXS/` agentic stack
  + `local_ranking/` VLM ranking + `DummyBluSky/` digital twin (see §4).

### N. XPCS (coherent / speckle) — **rare**
- **Intent:** speckle time-series for g2 correlation (resonant, single-spot bursts).
- **Representative files:** `chen_xpcs` (`grid_scan_xpcs`, 0.03 s frames over 30 s,
  outside the document model — the prime modernization target), LBL Su `xpcs_2025_1`.
  (Note: Cornell/Singer, despite the "coherent" association, is microbeam grain-mapping here,
  not XPCS.)

### O. Commissioning / calibration utilities (beamline staff) — **infrastructure**
- AgBehenate SDD/beam-center calibration (`AGB_scan.py`), attenuator transmission ladders
  (`attenuation_testing.py`), mirror bounce-down (`bounce_down_mirror.py`), microfocus GUI
  templates (`microlistscan.py`), the Oleg utility files (`33/34/35-oleg`), `new_ivu_gap`
  undulator commissioning.

---

## 4. The CDSAXS sub-project (a special case worth calling out)

`CDSAXS/` is not just user scripts — it is a 4-part software effort and a useful model for
where "best practice" is heading (closed-loop, simulated, agentic):

1. **Data-taking plans** (`30-user-CDSAXS_Philipp.py`, `_Auto.py`, `getPV.py`) — the prs/phi
   rocking metrology (mostly Tier 1; `_Auto.py` and `test.py::cd_saxs_modern` are Tier 2–4).
2. **Auto-alignment subsystem** (`slope_chase_*`, `roi_alignment`, `gaussian_fit`) driven by
   `sketchpad_agent` — an AutoGen + Jupyter **vision-LLM that writes and self-verifies OpenCV
   code** to level chi/theta and minimize rotation-center tip-spread.
3. **DummyBluSky** — a faithful **digital twin** (KDTree image replay from real frames,
   lab-frame `PseudoPositioner` rotation math, caproto 445-PV IOC, Tiled-like `db`) **plus a
   ZMQ AI-agent bridge**, so agents can be developed/benchmarked **without beam time** and
   deployed unchanged.
4. **local_ranking** — a multi-vendor **VLM image-ranking** rotation-center aligner.

It forms a clean **record → twin → develop → deploy** loop. The agentic acquisition is
already modern where it matters (single `bp.list_scan`/`rel_grid_scan` runs, cameras as stream
detectors, Tiled readback); only the *decision loop* is in Python, which is appropriate.

> Flagged (not fixed): committed API keys in `local_ranking/vlm_functions.py`; several
> `*_verified_beamline.py` glue stubs still carry `NotImplementedError`; thousands of
> auto-generated `sketchpad_tmp*/.../pipeline.py` outputs and npz/png data files bloat the dir.

---

## 5. Mature idioms to PRESERVE in any migration (hard-won, correct-in-spirit)

These appear inside otherwise-legacy bodies and encode real beamline knowledge. The target
template must keep them (as in-stream motor moves / configured signals / baseline), not drop them:

1. **Fresh-spot dose management:** move to an unexposed sample spot each
   energy/frame/temperature (`piezo.x = xs - counter*30µm`, `np.meshgrid`/`np.linspace`
   position walk, fresh-y per energy on solutions). Beam-damage mitigation.
2. **Arc-conditional detector lists:** `[pil900KW] if waxs.arc.position < ~15 else
   [pil900KW, pil2M]` — drop SAXS when the WAXS arc blocks it. (Modern form: separate declared
   SAXS/WAXS streams.)
3. **Slow-axis-outermost ordering:** `waxs.arc`, `prs`/`stage.phi`, `stage.th` placed in outer
   loops with `[::-1]` direction reversal to minimize travel of slow/in-vacuum axes; `piezo.*`
   (fast) innermost. (Directly supports the "move slow/in-vacuum axes sparingly" tenet.)
4. **Beam-loss recovery:** `if xbpm2.sumX.get() < 50: re-move energy; sleep` re-seek; DCM-move
   suspenders (`susp_xbpm2_sum`).
5. **Align-once / measure-many caching:** alignment offsets cached per sample (`Aligned_Dict`,
   `RE.md['ai_0']`), with failures logged (`RE.md['misaligned_samples']`) and triple-retry +
   `RE.clear_suspenders()`. (Modern form: alignment results as baseline/offset signals.)
6. **GI in-vacuum choreography:** `GV7` open→align→close; attenuator close/open; beamstop
   insert/restore — sequenced moves protecting the SAXS detector in reflection.
7. **Up/down ("upsweep/downsweep") energy passes** for reversibility checks; HDR multi-exposure
   brackets for dynamic range.

---

## 6. Anti-patterns to RETIRE (highest-priority migration targets)

In rough priority order:

1. **`RE(...)` called inside Python `for`/`while` loops** (not a generator end-to-end): SSYang,
   OGang, QYu, Mao, HZhang, AFurst, JiaLu, SWong/SWong2/XZhang2, CFN 2024 drivers. Breaks
   pause/resume/suspenders and composability.
2. **Detector triggering outside the RunEngine** (no documents recorded): `chen_xpcs`
   (`cam.acquire.put(1)` + busy-wait → `/ramdisk/`), Yu-Chung `trigger_alldet`, Gergaud
   `fly_scan_ai`, NIST_sept18 hand-rolled `fly_scan`.
3. **Run-per-data-point** nested loops (`bp.count(dets, num=1)` innermost): the bulk of the
   corpus. Collapse into a single coordinated/decorated run per logical sample.
4. **Filename as global mutable state** (`sample_id(...)`, `RE.md['sample'|'sample_name']`,
   including as an interprocess carrier between functions): universal. Replace with `md={}` +
   filename templated from recorded stream fields.
5. **Context baked into filename strings** via `.get()`/`.value()`/`.position`/`time.time()`/
   `db[-1].table()` instead of recorded as devices/baseline: universal; the biggest provenance
   gap.
6. **Hard-coded coordinate/sample tables in plan bodies** (with large commented-out alternates):
   universal. Separate input-selection from the plan (cf. `experiment_plan_template.py`).
7. **Module-level `global` / `RE.md` mutation** for alignment LUTs, timestamps, sample state.
8. **Same function redefined many times** in one file (last-def-wins): Karen (6×), Patryk (3×),
   Gomez (2×).
9. **Direct `cam.file_path.put(...)`** write-path overrides (pre-Tiled): Headrick, AFRL.
10. **Deprecated APIs / scratch code:** `np.int`, uncompiled snippets (Cordova), committed API
    keys (CDSAXS).

---

## 7. Reusable infrastructure that should be centralized (not copy-pasted)

Much of the legacy idiom propagated because shared helpers live inside user files and get
copy-pasted. Candidates to formalize into a shared library / the template/skill:

- **Metadata/naming:** `get_scan_md()`, `get_scan_md(tender=True)`, `get_more_md()`,
  `sample_id` (→ should become `md={}` + Signal-templated filenames).
- **Alignment toolkits:** `alignement_gisaxs_doblestack` / `_hex`, `alignCai` /
  `alignmentmodeCai`, `alignBoc`, `alignement_xrr_xmotor`, the `30-user_Petterson.py`
  manual-GISAXS-alignment recipe docstring, `peizo_th_correction`.
- **Beam/mode helpers:** `SMI_Beamline().modeAlignment/Measurement`, `SMIBeam().insertFoils`,
  `atten_move_in/out`, `det_exposure_time`, `insert_beamstop`/`restore_beamstop`,
  `proposal_swap`/`project_set` (facility data-management — good, keep).
- **Environment helpers:** `go_to_temp`/`gotoT`/`getT`, Lakeshore/Linkam wrappers,
  `set_humidity`/`readHumidity`, syringe-pump and printer-handshake devices.
- **CD-SAXS:** promote the `cd_saxs` rocking helper to a proper plan stub; adopt the
  `cd_saxs_modern`/`simplePRS` single-run shape.
- **CFN `YZhang_SMI_Base.py`:** the group's portable `sample_dict`/`pxy_dict` model,
  `get_motor()` piezo-vs-hexapod abstraction, transmission/GI/map primitives — a good basis,
  but it currently codifies the legacy idiom and should be modernized at the source.
- **Commissioning library:** BDM/XRR toolkit, AgBehenate calibration, attenuator ladder,
  micro-mapping GUI templates — the strongest existing modern infra.

---

## 8. Gold-reference exemplars (study these when writing the template/skill)

- **`nist/richter/Cl_nexafs.py`** — the single cleanest Tier-4 file. One staged run, up/down
  energy sweep, `bps.trigger_and_read(dets + [energy])`, and crucially a filename **templated
  from recorded stream fields**: `"..._{energy_energy}eV_pd{pin_diode_current2_mean_value}_
  bpm2{xbpm2_sumX}_..."`. This is the concrete proof-of-pattern for the user's tenet that
  filenames derive from `sample_name` + primary-stream mappings.
- **`nist/richter/p_nexafs.py`** — same pattern, P-edge.
- **`Commissioning/bounce_down_mirror.py`** — XRR with `incident_angle` recorded as a Signal.
- **`Commissioning/microlistscan.py`** — single-run-per-region grid/list scans (micro-mapping).
- **`templates/tender.py` / `tranmission.py`** — Tier-3 reference for the **multi-sample,
  multiple-open-run** structure (one `run_decorator` per sample, `target_file_name` /
  `incident_angle` / `energy_direction` Signals in-stream, `trigger_and_read`). These are the
  closest existing templates to the desired multi-sample pattern, but still carry the
  throwaway-Signal + hard-coded-bar habits that Tier 4 removes.
- **`templates/experiment_plan_template.py` / `grazing_fakhraai_template.py`** — the
  **separate-inputs-from-plan** structure (input-selection function vs `main_experiment_plan`).
- **`CDSAXS/DummyBluSky/plans.py` + `.../test.py::cd_saxs_modern`** — modern CD-SAXS single-run
  rocking; and the whole CDSAXS stack as a model for simulated + closed-loop development.

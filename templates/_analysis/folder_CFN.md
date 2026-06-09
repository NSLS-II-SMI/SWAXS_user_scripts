# CFN / Yugang Zhang Group — Plan Analysis (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for the
**CFN/Yugang** folder (Center for Functional Nanomaterials, Y. Zhang group) plus two
adjacent CFN files. Detector vocabulary: `pil2M` = SAXS (Pilatus 2M, ~5–9 m);
`pil900KW` / `pil300KW` = WAXS (arc-mounted on `waxs`/`waxs.arc`, in-vacuum);
`rayonix` = MAXS (referenced only, not used here); `pin_diode`/`pdcurrent1`/`pil2M_bs_pd`
= beamstop / transmission diodes; `xbpm2`/`xbpm3` = beam-position monitors (`sumX` baked
into filenames). Goniometry is split between `piezo.*` (SmarAct fast nano-stage:
x/y/z/th) and `stage.*` (coarse hexapod, also called via `stage.phi`); plus `MDrive.m5`
(X) / `MDrive.m3` (Z) for the droplet/reactor stages, and `prs` = **precision rotation
stage** (φ about the beam, ~-95°…+95°) used for tomography. `LThermal` (Linkam,
sub-/super-ambient, LN2) and `ls`/Lakeshore = temperature controllers. `energy` = DCM
(16.1 keV, low divergence is the house standard). `SMI_Beamline()`/`smi.modeAlignment()`
/`smi.modeMeasurement()` are the facility alignment-mode helpers.

**Pattern legend** — **MODERN**: `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)`
around `inner()` with `bps.trigger_and_read(dets + [signals])`, one run per logical sample,
context as Signals/baseline, metadata via `md={}`. **LEGACY**: nested `for` loops, each
iteration calls `bp.count`/`bp.scan`/`bp.rel_scan` → one Bluesky run per data point;
filenames via global mutable `sample_id(...)` / `RE.md["sample_name"]`; temperature/φ read
via `.get()`/`.temperature()`/`.position` into the filename string. **MIXED**: both present.

> **FOLDER-WIDE FINDING (verified by grep):** A search for
> `run_decorator` / `stage_decorator` / `trigger_and_read` / `declare_stream` /
> `run_wrapper` / `@bpp.` across **all 21 files returns ZERO hits.** There is **no
> genuinely MODERN decorated single-run plan body anywhere in this folder.** Every data
> acquisition is per-point `bp.count`/`bp.scan`. What *is* new in 2025–2026 is the
> **facility run-management *scaffolding* in the file headers** —
> `proposal_swap(...)`, `project_set('<project>')`, `get_scan_md()`, `pil2M.insert_beamstop('rod'|'pd'|'pin')`,
> `startWAXS()` — i.e. the beamline migrated to project-scoped data folders and a smarter
> beamstop/detector API, but the Zhang-group **plan logic did not migrate** with it.
> The single closest-to-modern *idiom* is `temp_series_grid()` (a `Signal('target_file_name')`
> carried as a detector: `bp.count(dets + [s])`), copied verbatim into several GI files but
> still wrapped in nested loops (one run per grid/temperature point).

---

## 0. YZhang_SMI_Base.py — reusable infrastructure (characterization)
1. **Size / plans:** ~1100 lines, ~45 `def`s + module state. The shared toolkit that every
   `2024*/2025*/2026*` Zhang file builds on (loaded first via `%run -i ...YZhang_SMI_Base.py`).
2. **Sub-group/PI:** Group-wide base (Y. Zhang / `YZ`).
3. **What it provides (the reusable API):**
   - **Module state / sample model:** global `motor='pizeo'` vs `'stage'` switch; `user_name`;
     the `sample_dict` / `pxy_dict` → `x_list` / `y_list` / `sample_list` convention reused by
     *every* downstream file; `get_motor()` returns `(M, TH, YH)` for piezo or hexapod.
   - **Transmission measure primitives:** `measure_transmission_xs()` and thin wrappers
     `measure_saxs` / `measure_waxs` / `measure_wsaxs` (build `dets`, set `waxs` angle,
     `det_exposure_time`, format a long `{sample}_x..y..z..det..m_waxs..expt..s` name, then
     `bp.count(dets, num=1)`); `snap_saxs`/`snap_waxs` quick shots.
   - **GI (grazing-incidence) engine:** `measure_one_gix`/`_gisaxs`/`_giwaxs`,
     `run_gix_loop_samples`, `run_gix_loop_waxs`, `align_gix_loop_samples(x_list, sample_list,...)`,
     and the alignment routines `yz_alignement_gisaxs`/`_hex`/`_height` wrapping
     `SMI_Beamline().modeAlignment()` + `align_gisaxs_height/th` + `ps.peak/cen`. Produces the
     `Aligned_Dict = {ii: {'th':…, 'y':…}}` object that the per-PI files consume.
   - **Mapping / raster:** `getSamMap(xlim,ylim,step_size,rot_angle)` (rotatable grid),
     `Measure_Map_Trans`, `measure_saxs_loop_sample`, `measure_multi_waxs_loop_angles`.
   - **Line scans:** `do_line_trans_scan`, `do_gix_line_scan` (V/H stepping with OAV save).
   - **Temperature (Lakeshore):** `setT/getT/startT/stopT/gotoT` (°C↔K, tolerance-poll loop).
   - **Motion conveniences:** `movx/movy/mov_xy/get_posxy`, `mov_sam`/`mov_sam_re`/`name_sam`
     (set `RE.md["sample"]`), `move_waxs(_on/_off)`, `measure_pindiol_current`.
   - **Cameras / paths:** `save_ova`/`save_hex` (caput JPEG/TIFF write), `setup_ova`/`setup_hex`;
     a (commented-out) `proposal_id()` that made `/1M`, `/900KW`, `/OAV`, `/HEX`, `/Results` dirs.
   - **Misc:** `get_current_time`, `run_time`, `sort_dict_by_value`, a `help_dict`.
4. **Acquisition pattern: LEGACY (defines the legacy idiom).** Every primitive ends in
   `bp.count(dets, num=1)` keyed by `sample_id(user_name, sample_name)`; many helpers wrap
   `RE(...)` *inside* a non-plan function (e.g. `mov_sam`, `Measure_Map_Trans`), mixing the
   RunEngine call with generator code.
5. **Notable:** piezo-vs-hexapod abstraction via `get_motor()`; `Aligned_Dict` is the central
   data structure threaded through all GI experiments; reflected-beam ROI alignment via SMI helpers.
6. **Intent:** The group's portable SAXS/WAXS + GISAXS/GIWAXS + map + Linkam toolbox; the
   single source of the legacy "loop-and-`bp.count`, name-via-`sample_id`" pattern inherited folder-wide.

---

## 1. liquids.py
1. **Size / plans:** 1 line (`import numpy as np`). Empty stub / placeholder.
2. **Sub-group/PI:** Y. Zhang (liquid/flow work).
3. **Use-cases:** none implemented (intended liquid/droplet helper, never populated).
3b. **Detectors:** none.
4. **Acquisition pattern: N/A.**
5. **Notable:** placeholder only — actual liquid handling lives in `2024C3_Drop.py` / `2025C2_SMI.py` (`DropletReactor`).
6. **Intent:** Reserved module for liquids; effectively empty.

---

## 2. 2024C3.py
1. **Size / plans:** ~1118 lines, ~30 `def`s. Microfocus + multi-sample-bar + in-situ T workhorse, Nov-2024 cycle.
2. **Sub-group/PI:** Y. Zhang (`YZ`); positions tagged for `FTeng`/`FLu` (DAPHNE / Mingxin collaborators in docstrings).
3. **Use-cases:** transmission SAXS/WAXS; **microfocus raster mapping** (`getSamMap`/`Measure_Map`, 50–100 µm step grids); **temperature ramping / melting kinetics** (`run_melting`, `run_HT_time_temperature`, `run_RT_temperature`, `run_Tm`/`run_melting_Tm` — DNA-melting-style nanoparticle assembly); **in-situ time series** (`run_time_series`); multi-sample bar.
3b. **Detectors:** `pil2M` (SAXS), `pil900KW` (WAXS @ 20°); `pil2M_pos.z` for SDD in name.
4. **Acquisition pattern: LEGACY (with a notable anti-pattern).** Two parallel families:
   `RE(...)`-wrapping driver functions (`run_melting`, `run_HT_time_temperature`) **call the
   RunEngine from inside a `while`/`for` loop**, and `RE_run_*` generator twins that `yield from`.
   Temperature is read into the filename via `getT()`:
   ```python
   for T in tlist:
       RE(gotoT(T)); time.sleep(sleep_time_per_dtemp)
       for k in ks:
           mov_sam(k); pos_list = getSamMap(xlim=lim_dict[k][0], ylim=lim_dict[k][1])
           RE(bps.mv(piezo.x, pos_list[i_dict[k]%N][0])); ...
           RE(measure_saxs(exposure_t, sample=RE.md['sample'] + '_T_%.2f'%getT()))   # T baked into name
   ```
5. **Notable:** spatially-resolved "spot rotation" (`i_dict[k]%N`) to avoid beam-damaged points across a melting ramp; rotatable `getSamMap`; SDD captured in filename.
6. **Intent:** Multi-sample, microfocus SAXS/WAXS with temperature-resolved melting/annealing kinetics and raster mapping; canonical legacy per-point counting with T-in-filename.

---

## 3. 2024C3_Drop.py
1. **Size / plans:** very large (capped ~1421+ lines), `class DropletReactor` (~20 methods) + helpers. Droplet-microreactor autonomous-synthesis controller, 2024.
2. **Sub-group/PI:** Y. Zhang autonomous-synthesis program (`YZ`); Cu/Cu2O/Au nanoparticle chemistry.
3. **Use-cases:** **droplet/liquid handling** (well-plate `A1..F9` + Kapton-tube `K1..K25` reactor geometry computed from corner fiducials + flow-rate→volume→reaction-time maps `Reactor_pos_vol`); **in-situ time-series / reaction kinetics**; **electrochemistry/flow synthesis**; **autonomous/ML-driven experiment** (`AutoRun_batch`, `Run_one_batch`, `Run_manual_batch*` poll `Batch_push.npz`/`Batch_T_t_dict.npz` from a BoTorch optimizer); nanoparticle self-assembly.
3b. **Detectors:** `pil2M` + `pil900KW` (WAXS @ 15°) via `DR.measure()`.
4. **Acquisition pattern: LEGACY (object-oriented closed-loop).** `DropletReactor.measure()` ends in `RE(bp.count(dets))` and is driven by `time.time()`-bounded `while` loops; cross-process coordination via `.npz` files:
   ```python
   def measure(self, sample_name=None, t=1, take_camera=True):
       dets = [pil2M, pil900KW]; sample_name = self.sample_pref + '_loc_%s'%pos + extra
       sample_id(user_name=user_name, sample_name=sample_name)
       RE(bp.count(dets)); save_ova(sample=user_name+'_'+sample_name+'id_%s'%RE.md["scan_id"])
   ```
   `Run_time_dependent_scan`/`Run_one_batch` block until `new_batch_num in batch_push.keys()`.
5. **Notable:** geometric tube-position solver (`get_points_on_line`, per-tubing `ID`/`step_len`/`jump_len` volume model for PTFE/Kapton/glass); `Find_new_pos_fr` picks the reactor cell matching a target reaction time; OAV snapshot per measurement; BoTorch hand-off via npz.
6. **Intent:** Autonomous closed-loop droplet/flow nanoparticle synthesis with in-situ SAXS/WAXS and ML-suggested batches; legacy per-shot counting inside a polling control loop.

---

## 4. 2025C2_SMI.py
1. **Size / plans:** very large (capped ~1391+ lines). Essentially the **2024C3_Drop `DropletReactor` carried into 2025** + a long interactive-history header.
2. **Sub-group/PI:** Y. Zhang (`YZ`/SMI in-house); Cu2O synthesis (`DR = DropletReactor(sample='Cu2O_')`).
3. **Use-cases:** droplet/flow synthesis (well-plate + Kapton + new `'falcon'` tube position); **autonomous/ML** (`Run_Cu2O_synthesis` polling `Batch_push.npz`); in-situ time series; electrochemistry. Header also shows **GISAXS alignment / XRR-style rocking** scratch commands (`rel_scan(piezo.th/y)`, `ps(der=True)`, `continous_run_change_xpos_thpos`) and the **new `insert_beamstop('rod'|'pin')` / `restore_beamstop` API**.
3b. **Detectors:** `pil2M` + `pil900KW` (WAXS @ 16°).
4. **Acquisition pattern: LEGACY.** Identical `DropletReactor` engine (`RE(bp.count(dets))` in a `while` loop) as §3; new in 2025 is the `proposal_swap(316412)` + `pil2M.insert_beamstop('rod')` scaffolding in the header (facility infra), not the plan body.
5. **Notable:** shows the 2025 beamstop-state machine (`pil2M.active_beamstop`, `rod`/`pin`/`pd` positions, `pd_safe_pos`) and `project_set('20250630_op_a_*')` project folders — early evidence of the new run-management layer.
6. **Intent:** 2025 continuation of autonomous Cu2O droplet synthesis; legacy acquisition with modern *facility* beamstop/project plumbing bolted onto the header.

---

## 5. 2025C2_PGuo.py
1. **Size / plans:** ~864 lines, ~10 `def`s. Multi-sample-bar **GIWAXS/GISAXS + Linkam temperature** suite (perovskite/halide thin films).
2. **Sub-group/PI:** **P. Guo** group (header `PGuo`; active `username='BW'`/Bowen). FAPbBr3 / BAI / NPB perovskite films (`sample_dict` of FAPBBR3_G, BAIn1_G, CuPc_q1, …).
3. **Use-cases:** **GIWAXS / GISAXS** (`align_gix_loop_samples` → `run_gix_loop_wsaxs`, incident-angle arcs 0.05–0.6°, `waxs` 0/10/15/20°); **temperature ramping/annealing** (`Temperature_Linkam_Fast_ThreeTs`, `Temperature_Linkam_Step`, `collect_data_atT` — phase transitions vs T); **in-situ time-series GI** (`insitu_tgix_samples`); **temperature×spatial grid** (`temp_series_grid`); multi-sample bar; alignment.
3b. **Detectors:** `pil900KW`/`pil300KW` (WAXS), `pil2M` (SAXS at max angle); `xbpm2.sumX` in some names.
4. **Acquisition pattern: LEGACY (MIXED idiom).** GI plans are nested `waxs × sample × x × θ` loops each `bp.count(dets, num=1)`, with **Linkam T read into the filename** (`LThermal.temperature()` → `_T{lt:.2f}c_`):
   ```python
   for waxs_angle in waxs_angle_array:
     yield from bps.mv(waxs, waxs_angle)
     for ii,(x,sample) in enumerate(zip(x_list,sample_list)):
        yield from bps.mv(M.th, Aligned_Dict[ii]['th'] + th); ...
        sample_id(user_name=user_name, sample_name=..._T{lt:.2f}c_...); yield from bp.count(dets, num=1)
   ```
   `temp_series_grid` is the lone **half-modern** idiom: `s = Signal('target_file_name'); ...; yield from bp.count(dets + [s])` (filename as a *device*, but still per-point in nested loops, `RE.md["sample_name"]` still mutated).
5. **Notable:** `Aligned_Dict` reuse; `GIWAXS_TD_run` adds cryo cooling with **alignment-drift guards** (`raise ValueError` if cold-T θ/y drift > tolerance) and a stepwise `waxs` arc-retraction sequence; xbpm sum logged.
6. **Intent:** Temperature-resolved GIWAXS/GISAXS of perovskite thin films on a sample bar via Linkam; legacy per-angle counting with T-in-filename (one `temp_series_grid` gesture toward Signal-based naming).

---

## 6. 2025C2_SZhang.py
1. **Size / plans:** 120 lines, `class NanoSyn` (3 methods). Minimal nanoparticle-synthesis time-series controller.
2. **Sub-group/PI:** **S. Zhang** (`SZ`).
3. **Use-cases:** **in-situ time-series** transmission SAXS+WAXS of a single sample (nanoparticle synthesis monitoring); no mapping/alignment.
3b. **Detectors:** `pil2M` + `pil900KW` (WAXS @ 16°).
4. **Acquisition pattern: LEGACY (minimal).** `NanoSyn.measure()` → `RE(bp.count(dets))`; `NanoSyn.run()` is a `while (time()<t0+run_time)` loop calling `measure` + `time.sleep`:
   ```python
   def run(self, sample_name='X', sleep_time=5, run_time=...):
       while time.time() < t0 + run_time:
           self.measure(sample_name=sample_name); time.sleep(sleep_time)
   ```
5. **Notable:** the stripped-down `NanoSyn` archetype later cloned into the 2025C3/2026 "static-bar" files; reuses the 2024_3 Dropbox base path.
6. **Intent:** Repeated single-sample SAXS/WAXS time monitoring of a nanoparticle synthesis; legacy counting in a wall-clock loop.

---

## 7. 2025C2_Kim.py
1. **Size / plans:** ~897 lines, ~10 `def`s. **GIWAXS/GISAXS + Linkam** suite — twin of `2025C2_PGuo.py`.
2. **Sub-group/PI:** **H. Kim** group (header toggles `Kim`→`Duan`); CsPbBr3 / Mica / RTA-annealed oxide films (`6nm_RTA_350/400/450C`, `Zr25_41_2Pr50`).
3. **Use-cases:** **GIWAXS/GISAXS** multi-sample bar; **annealing / RTA series**; **temperature ramping** (same Linkam `Temperature_Linkam_*` / `collect_data_atT`); **in-situ time GI** (`insitu_tgix_samples`); temperature×spatial grid (`temp_series_grid`); alignment; **microfocus** (`run_giwaxs_Kim`: high `waxs` 7/27/47° to reach ~6.8 Å⁻¹).
3b. **Detectors:** `pil900KW`/`pil300KW` (WAXS), `pil2M`; `xbpm2.sumX`.
4. **Acquisition pattern: LEGACY (MIXED idiom).** Same nested `waxs × sample × x × θ` → `bp.count` as §5; adds explicit beamstop placement inside the plan (`yield from bps.mv(pil2M.beamstop.x_rod, 5.5)`):
   ```python
   yield from bps.mv(pil2M.beamstop.x_rod, 5.5)
   for waxs_angle in waxs_angle_array:
       yield from bps.mv(waxs, waxs_angle); dets = get_dets(waxs_angle, mode)
       for ii,(x,sample) in ...: yield from bp.count(dets, num=1)
   ```
5. **Notable:** `run_giwaxs_Kim` alternates angle direction per sample (`inverse_angle`) and encodes ±waxs sign (`waxsP`/`waxsN`) in names; `GIWAXS_TD_run` cryo with drift guards (identical to PGuo).
6. **Intent:** Temperature-/annealing-resolved GIWAXS/GISAXS of halide-perovskite and RTA-oxide films on a bar (Kim/Duan); legacy per-angle counting, beamstop driven inline.

---

## 8. 2025C3_XLin.py
1. **Size / plans:** ~448 lines, ~10 `def`s. Transmission SAXS/WAXS multi-sample + `NanoSyn` time-series; reactor/capillary work.
2. **Sub-group/PI:** **X. Lin** (header toggles `YZ`/`DM`/`XL`); Au-nanoparticle (`Au110225A1`, `ASP`, Toluene) + reactor.
3. **Use-cases:** **transmission SAXS/WAXS** multi-angle bar surveys (`measure_multi_waxs_loop_angles`, `measure_multi_saxs_loop_angles`); **in-situ time-series** synthesis (`NanoSyn.run` with a serpentine dither over a small x/y grid to spread dose); alignment scratch in header (`rel_scan([pil2M,pin_diode], piezo.x, …)`); droplet/reactor capillary positions.
3b. **Detectors:** `pil2M`, `pil900KW`; `pin_diode` (header h-scans).
4. **Acquisition pattern: LEGACY.** `measure_transmission_xs` → `bp.count(dets, num=1)`; `NanoSyn.run` dithers MDrive between shots:
   ```python
   while time.time() < t0 + run_time:
       self.measure(sample_name=sample_name)
       x, y = Dxy[I%N]; RE(bps.mvr(motorX, x)); RE(bps.mvr(motorZ, y)); I+=1; time.sleep(sleep_time)
   ```
   Header adopts the new `proposal_swap(318919)` / `project_set('static')` / `get_scan_md()` plumbing.
5. **Notable:** introduces the serpentine **anti-beam-damage dither** (`Dxy` zig-zag) reused into all 2026 files; `pin_diode` added to transmission/alignment scans.
6. **Intent:** Transmission SAXS/WAXS bar surveys + dithered in-situ NP-synthesis monitoring (X. Lin); legacy counting with new project-folder header conventions.

---

## 9. 2026C1_EHu.py
1. **Size / plans:** ~420 lines, ~10 `def`s. **Template "static-bar" transmission SAXS/WAXS** file (the canonical 2026 clone).
2. **Sub-group/PI:** **E. Hu** project slot (header cycles `BLi`/`YZhou`/blank); generic `S1..S14` bar + AgBH/Capillary calibration.
3. **Use-cases:** **transmission SAXS/WAXS** multi-sample bar + multi-angle (`measure_multi_waxs_loop_angles`, `measure_multi_saxs_loop_angles`); in-situ time-series (`NanoSyn`); calibration (AgBH); alignment (header h-scan).
3b. **Detectors:** `pil2M`, `pil900KW` (`pin_diode` in header).
4. **Acquisition pattern: LEGACY.** Verbatim `measure_transmission_xs` + `measure_multi_*` + `NanoSyn` engine (same as §8 minus reactor specifics):
   ```python
   for waxs_angle in waxs_angles:
     for k in ks:
        yield from mov_sam_re(k); RE.md["sample_name"]=sample_dict[k]
        yield from measure_waxs(t=ti, waxs_angle=waxs_angle, ...)   # one run/sample/angle
   ```
   Header: `proposal_swap(318527)` + `project_set('static')` + `pass-318527/.../projects/static/user_data/2M`.
5. **Notable:** this file is the **2026 "base template"** — EHu/OGang/InSituDemo/InSituGrowth/ThreeGroups are near-identical copies that differ only in `sample_dict`/`pxy_dict` and `project_set` name.
6. **Intent:** Standard 2026 transmission-bar SAXS/WAXS survey for E. Hu; legacy counting, project-scoped folders.

---

## 10. 2026C1_OGang.py
1. **Size / plans:** ~461 lines. Clone of §9 (static-bar transmission template).
2. **Sub-group/PI:** **O. Gang** (DNA-origami / nanoparticle superlattice self-assembly); header active `CL`/`DR`, commented `OG`; 9-meter SDD note.
3. **Use-cases:** **transmission SAXS** (self-assembly / nanoparticle superlattices, large q-range at 9 m); multi-angle WAXS; **manual raster** (header inline `for j…for i: measure_saxs; movx/movy` grids); calibration.
3b. **Detectors:** `pil2M` (9 m SAXS), `pil900KW`.
4. **Acquisition pattern: LEGACY.** Identical engine to §9; header documents 9 m geometry and `saxs rod X --> 6.8`. Manual nested `movx/movy` raster snippets in the docstring.
   ```python
   for j in range(max_x):
     for i in range(max_y): RE(measure_saxs(t=tim, sample=samname, user_name='DR')); movy(ystep)
     movy(-ystep*max_y); movx(xstep)
   ```
5. **Notable:** O. Gang = nanoparticle/DNA self-assembly archetype; 9 m long-SDD SAXS for large superlattice d-spacings; `project_set('OGang')`.
6. **Intent:** Long-SDD transmission SAXS of self-assembled nanoparticle superlattices (O. Gang); legacy counting + manual raster macros.

---

## 11. 2026C1_InSituDemo.py
1. **Size / plans:** ~435 lines. Clone of §9 (static-bar template), demo project.
2. **Sub-group/PI:** Y. Zhang in-situ **demonstration** (header `CL`/`DR`; `project_set('InSitu_Demo')`).
3. **Use-cases:** **in-situ time-series** demo + transmission SAXS/WAXS bar; manual raster snippets; calibration. (Demonstration variant of the in-situ workflow.)
3b. **Detectors:** `pil2M`, `pil900KW`.
4. **Acquisition pattern: LEGACY.** Byte-for-byte the §9 engine (`measure_transmission_xs`/`measure_multi_*`/`NanoSyn`); only header `project_set` and `sample_dict` differ.
5. **Notable:** essentially a copy of EHu/InSituGrowth; exists to seed an in-situ demo project folder.
6. **Intent:** Demo scaffold for in-situ transmission SAXS/WAXS; legacy counting.

---

## 12. 2026C1_ThreeGroups.py
1. **Size / plans:** ~472 lines. Clone of §9; shared bar across three user groups.
2. **Sub-group/PI:** **Multi-PI** shared bar — `QWang` (cells S1–S4), `MZheng`, `CAT`, `SY` (MXene Ti3C2 / InP / Cu3P), `Jules` (header blocks). Catalysis + 2D-material + battery samples co-loaded.
3. **Use-cases:** **transmission SAXS/WAXS** survey across heterogeneous samples (MXenes, phosphides, catalysts, battery cells); multi-angle WAXS; manual vertical raster (`for j: measure_saxs; movy(120)`); calibration.
3b. **Detectors:** `pil2M`, `pil900KW`.
4. **Acquisition pattern: LEGACY.** Same §9 engine; only the (multiple, overwritten) `sample_dict`/`pxy_dict` blocks and `project_set('ThreeGroups')` differ.
5. **Notable:** illustrates the **shared-bar / multi-tenant** mode (several PIs' samples in one `sample_dict`); a couple of `pxy_dict` entries use `{...}` set-literals (latent bug, not in scope).
6. **Intent:** One transmission-SAXS/WAXS bar shared among three groups (QWang/MZheng/SY/Jules); legacy counting.

---

## 13. 2026C1_InSituGrowth.py
1. **Size / plans:** ~439 lines. Clone of §9 with a **piezo-fine dither** added to `NanoSyn.run`.
2. **Sub-group/PI:** Y. Zhang in-situ **growth** project (header `CL`/`DR`; `project_set('InSitu')`).
3. **Use-cases:** **in-situ growth time-series / kinetics** (repeated SAXS/WAXS while a film/particle grows), transmission bar; solvent/flow-adjacent; calibration.
3b. **Detectors:** `pil2M`, `pil900KW`.
4. **Acquisition pattern: LEGACY.** §9 engine; `NanoSyn.run` now selects `motor='piezo'` (fine ±400 step serpentine) vs `'mdrive'`, dithering between time-points to spread dose:
   ```python
   while time.time() < t0 + run_time:
       self.measure(sample_name=sample_name, t=t)
       x,y = Dxy[I%N]
       RE(bps.mv(piezo.x, x0+x)); RE(bps.mv(piezo.y, y0+y)); I+=1; time.sleep(sleep_time)
   ```
5. **Notable:** piezo-vs-mdrive dither switch (vs the MDrive-only dither in EHu/OGang); growth monitoring.
6. **Intent:** In-situ growth-kinetics SAXS/WAXS with dose-spreading dither; legacy wall-clock counting loop.

---

## 14. 2026C1_Tomo.py  *(tomography)*
1. **Size / plans:** ~593 lines, ~12 `def`s. Static-bar template **+ a dedicated `run_tomo()` rotation-series plan**.
2. **Sub-group/PI:** Y. Zhang / **F. Lu** SAXS-tomography (`project_set('Tomo')`, samples `FL_S3Cube`, `FL_S1NaCl`, `FL_S2CsCl` cubes/crystals; `CWang` sample); microfocus.
3. **Use-cases:** **SAXS/WAXS tomography** (rotation series about `prs`, the φ axis); microfocus (23×3 µm beam per header); **fine y-line scans** (`yline_scan`, 3 µm `stage.y` steps); plus the inherited transmission-bar + `NanoSyn` machinery.
3b. **Detectors:** `pil2M` + `pil900KW` (`det=[pil2M,pil900KW]` in `run_tomo`); `xbpm3.sumX` baked into name; `pin_diode` (header).
4. **Acquisition pattern: LEGACY (rotation series = per-angle run).** `run_tomo` is the defining plan — `prs` stepped over a θ range, `bp.count` at each projection (cf. CD-SAXS `prs` rocking in the legacy CDSAXS file; here it's a full ±90° tomographic sweep, up to 1801 projections):
   ```python
   def run_tomo(th_ini=-90, th_fin=90, th_st=30, exp_t=1, sample='test', nume=1, det=[pil2M,pil900KW]):
       det_exposure_time(exp_t, exp_t*nume)
       for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
           yield from bps.mv(prs, theta)
           sample_name = "{sample}_5.0m_16.1keV_num{num}_{th}deg_bpm{bpm}".format(..., bpm=xbpm3.sumX.get())
           sample_id(sample_name=sample_name); yield from bp.count(det, num=1)   # ONE run / projection
   ```
   Header documents a **`prs` -90/0/+90 self-alignment** procedure to put the sample on the rotation axis, and `pil2M.insert_beamstop('pd'|'rod')` for microfocus.
5. **Notable:** `prs` (precision rotation stage) tomographic sweep -90°→+90° at 181–1801 steps; microfocus + pin-diode beamstop; per-projection `xbpm3` normalization in the filename; "LargeBeam"/"Fine" naming for resolution.
6. **Intent:** SAXS/WAXS computed tomography of single crystals/cubes via `prs` rotation series (F. Lu); legacy per-projection counting that should be one coordinated `prs` scan per tomogram.

---

## 15. 2026C1_PGuo.py
1. **Size / plans:** ~982 lines, ~14 `def`s. **In-vacuum GIWAXS/GISAXS + Linkam** suite (2025C2_PGuo carried to 2026, vacuum-chamber procedure).
2. **Sub-group/PI:** **P. Guo** (header active `CM`; `4gF/4gS/4CF/4CS/CD131/CD101`; commented MAPbBr/MAPbI perovskite recipes).
3. **Use-cases:** **GIWAXS/GISAXS** multi-sample bar in **vacuum** (`waxs` 0/15/20°, arc 0.05–0.6°); **temperature ramping** (Linkam `Temperature_Linkam_Step`/`_Fast_ThreeTs`, `run_linkam_samples_oneT`); **in-situ time-series GI** (`insitu_tgix_samples`, `insitu_fix_pos_angle` — fixed-spot kinetics); temperature×spatial grid; alignment; microfocus (`run_giwaxs_Kim` 7/27/47°).
3b. **Detectors:** `pil900KW`/`pil300KW` (WAXS), `pil2M`; `xbpm2.sumX`.
4. **Acquisition pattern: LEGACY (MIXED idiom).** Same nested GI loops + `bp.count`; T read into name (`_T{lt:.2f}c_`); `temp_series_grid` Signal idiom present (and slightly broken: re-formats `sample_name` with an undefined `ais`/`bpm`). New: detailed **vacuum-chamber operating header** (vent/evacuate/`startWAXS()`/`shopen()`/`modeAlignment`) and `BEAMSTOP_X=6.55` set via `pil2M.beamstop.x_rod.set(...)`.
   ```python
   def collect_data_atT(T, Aligned_Dict, ...):
       LThermal.setTemperature(T); LThermal.on()
       while abs(LThermal.temperature()-T) > .5: time.sleep(3)
       RE(_run(Aligned_Dict, sample_name=..., waxs_angle_array=...))   # GI bar at one T
   ```
5. **Notable:** `insitu_fix_pos_angle` (single fixed spot/angle repeated for kinetics) vs `insitu_tgix_samples` (bar loop); `run_giwaxs_Kim` ±angle alternation; full vacuum operating checklist; uses `alignment_gisaxs*` (note: renamed from `alignement_*`).
6. **Intent:** In-vacuum temperature-resolved GIWAXS/GISAXS of perovskite/CD films on a bar (P. Guo, 2026); legacy per-angle counting with T-in-filename and vacuum scaffolding.

---

## 16. 2026C1_CNam.py
1. **Size / plans:** ~1037 lines, ~14 `def`s. **In-vacuum GIWAXS/GISAXS + Linkam** suite — twin of §15.
2. **Sub-group/PI:** **C. Nam** (header active `CNam`/`TZhu`; long `S1_1…S2_23` thin-film series).
3. **Use-cases:** **GIWAXS/GISAXS** multi-sample bar in vacuum (`run_gix_loop_wsaxs`, mode `['waxs','saxs']`, `waxs` 0/20/40°, arc 0.05–0.3°); **temperature ramping** (Linkam suite); **in-situ time GI** (`insitu_tgix_samples`/`insitu_fix_pos_angle`); temperature×spatial grid; alignment; microfocus.
3b. **Detectors:** `pil900KW`/`pil300KW`, `pil2M`; `xbpm2.sumX`.
4. **Acquisition pattern: LEGACY (MIXED idiom).** Same engine as §15; the most thorough **operating-procedure header** in the folder (numbered vent→load→evacuate→`startWAXS()`→`shopen()`→`modeAlignment()`→align→measure). `x_list`/`y_list` derived with global `xpos`/`ypos` offsets.
   ```python
   for waxs_angle in waxs_angle_array:
     yield from bps.mv(waxs, waxs_angle); dets = get_dets(waxs_angle, mode)
     for ii,(x,sample) in enumerate(zip(x_list,sample_list)):
        yield from bps.mv(M.th, Aligned_Dict[ii]['th']+th); ...; yield from bp.count(dets, num=1)
   ```
5. **Notable:** `mode=['waxs','saxs']` so both detectors run together; `BEAMSTOP_X=6.55`; `xpos`/`ypos` bar-origin offsets; identical Linkam/`temp_series_grid`/`GIWAXS_TD_run` machinery as PGuo (copy lineage).
6. **Intent:** In-vacuum temperature-/angle-resolved GIWAXS/GISAXS of thin-film bars (C. Nam/TZhu, 2026); legacy per-angle counting with extensive vacuum SOP.

---

## 17. 2026C1_XDuan.py
1. **Size / plans:** ~1138 lines, ~16 `def`s. **In-vacuum GIWAXS/GISAXS + Linkam, with cryogenic (LN2) T-series.** Richest 2026 GI file.
2. **Sub-group/PI:** **X. Duan** (header `XD`/`UCLA`; UCLA samples `BZ/CL/HT/YL` series).
3. **Use-cases:** **GIWAXS/GISAXS** vacuum bar (`run_gix_loop_wsaxs`, `waxs` 0/15/20/40°); **temperature ramping incl. low-T / LN2** (`run_Linkam_Tseries` over `[200,100,80,100,200,300,360] K`, `set_T` with K→°C conversion); **in-situ time GI**; temperature×spatial grid; transmission SAXS/WAXS (`measure_multi_waxs_loop_angles`); alignment; microfocus.
3b. **Detectors:** `pil900KW`/`pil300KW`, `pil2M` (conditional both ≥15° waxs); `xbpm2.sumX`.
4. **Acquisition pattern: LEGACY.** Same GI engine + Linkam; `run_Linkam_Tseries` loops temperatures, soaks, then drives the bar plan per T:
   ```python
   for T in Ts:                       # Ts in Kelvin
       set_T(T); time.sleep(20*60); lt = LThermal.temperature()
       RE(run_linkam_samples_oneT(Aligned_Dict, waxs_angle_array=[0,15,20,40],
                                  dets=[pil900KW,pil2M], t=1))   # GI bar at this T
   set_T(300); turn_off_T()
   ```
   Header documents **LN2 Linkam-in-vacuum hardware setup**, hexapod homing, and saved `Aligned_Dict` snapshots (cryo θ/y).
5. **Notable:** explicit **cryogenic** workflow (LN2 plumbing, K-based setpoints, `XDuan_LT` project); conditional dets inside the inner loop (`waxs>15 → +pil2M`); two large hard-coded `Aligned_Dict` snapshots retained in comments.
6. **Intent:** Cryo + variable-T in-vacuum GIWAXS/GISAXS of UCLA thin-film bars (X. Duan, 2026); legacy per-angle counting with Kelvin T-series and LN2 setup.

---

## 18. 2026C1_FLu.py
1. **Size / plans:** ~447 lines, ~10 `def`s. Static-bar **transmission SAXS/WAXS** clone (in-air, 2026).
2. **Sub-group/PI:** **F. Lu** (header `FL`; `JO_S*`, `FL_20260405_S*`, `HZ_S*_Pd*` Pd / H2-loading samples, `FL_Wat` water).
3. **Use-cases:** **transmission SAXS/WAXS** multi-sample bar + multi-angle (`measure_multi_waxs_loop_angles`); **in-situ time-series** (`NanoSyn`, MDrive dither); gas/**H2-loading** chemistry (Pd1/Pd2 ± H2 ± release naming); calibration; alignment.
3b. **Detectors:** `pil2M`, `pil900KW`.
4. **Acquisition pattern: LEGACY.** Byte-identical to the §9 static-bar engine (`measure_transmission_xs`/`measure_multi_*`/`NanoSyn` with MDrive serpentine dither); header `proposal_swap(318527)`/`project_set('FLu')`, vacuum→air switch noted.
   ```python
   for waxs_angle in waxs_angles:
     for k in ks:
        yield from mov_sam_re(k); RE.md["sample_name"]=sample_dict[k]
        yield from measure_wsaxs(t=ti, waxs_angle=waxs_angle, ...) if both else measure_waxs(...)
   ```
5. **Notable:** Pd hydrogenation in-situ naming (`Pd1_H2`, `Pd1H_Rel`); precise per-sample (x,y) tables; same dither as XLin.
6. **Intent:** In-air transmission SAXS/WAXS bar survey + Pd/H2 in-situ monitoring (F. Lu, 2026); legacy counting.

---

## 19. CFN/CMS_2025C1.py  *(sister beamline: CMS 11-BM)*
1. **Size / plans:** ~1206 lines, `class DropletHolder(PositionalHolder)` (~25 methods) + helpers. **CMS-beamline (11-BM) port** of the Zhang droplet program.
2. **Sub-group/PI:** Y. Zhang autonomous synthesis, **run at CMS** (`/nsls2/data/cms/.../2025_1/Yuzhang`); Cu/PVP/UV nanoparticle batches.
3. **Use-cases:** **droplet/liquid handling** (9×6 well-plate `A1..F9` `DropletHolder` with `Reactor` flow→time model); **autonomous/ML closed-loop** (`run_batch`/`run`/`run_continue*`/`run_time_dependent_*` polling `Batch_push.npz`/`Batch_T_t_dict.npz`); **in-situ time-series**; **SAXS+MAXS+WAXS** simultaneous (CMS `pilatus2M`+`pilatus8002`); capillary z-scans (`quick_z_measurement`).
3b. **Detectors:** **CMS** `pilatus2M` (SAXS) + `pilatus8002` (MAXS via `maxs_on`/`smaxs_on`), `WAXSx/y`,`MAXSx/y` motors; uses CMS `cms.SAXS.setCalibration`, `Sample`/`PositionalHolder` SciAnalysis framework.
4. **Acquisition pattern: LEGACY (CMS SciAnalysis idiom).** Uses CMS's `sam.measure(exposure_time, extra=...)` (Naming via SciAnalysis `Sample`, not `sample_id`), driven by `while time()<t0+run_time` batch-polling loops:
   ```python
   while time.time() < t0 + run_time:
       Batch_push = try_load_npz(self.base+'Batch_push.npz', ...)
       if self.new_batch_num in Batch_push['df'].item().keys(): measure = True
       if measure: detselect([pilatus2M, pilatus8002]); sam.measure(exposure_time, extra=get_current_time())
       else: time.sleep(10)
   ```
5. **Notable:** **different framework** (CMS SciAnalysis `Holder`/`Sample`/`Reactor`/`detselect`/`cms.modeMeasurement`) vs the SMI `sample_id`/`SMI_Beamline` stack — same autonomous-droplet science, beamline-specific plumbing; manual per-cell position table (`manual_pos['A1'..'F9']`); `detselect([pilatus2M, pilatus8002])` toggles SAXS+MAXS.
6. **Intent:** CMS(11-BM) implementation of autonomous Cu/PVP droplet nanoparticle synthesis with SAXS/MAXS and ML batch hand-off; legacy SciAnalysis-style per-shot measurement in a polling loop.

---

## 20. CFN/30-user-Kim5.py
1. **Size / plans:** ~469 lines, ~8 `def`s. Older (2022-cycle) **GIWAXS microfocus** sample-bar macro.
2. **Sub-group/PI:** **H. Kim** group (2022_1, `308251_Kim`; also Gao samples) — predates the `YZhang_SMI_Base` toolkit.
3. **Use-cases:** **GIWAXS / GISAXS** multi-sample bar (the original `run_giwaxs_Kim`); **microfocus / high-q WAXS** (`waxs` 7/27/47° → ~6.8 Å⁻¹); **vertical line scan** (`vertical_scan` over `piezo.y`, large-beam); air-vs-vacuum comparison runs; manual single-sample measurement.
3b. **Detectors:** `pil900KW` + `pil300KW` (WAXS), `pil2M` (SAXS at max angle); `pil2M_bs_pd` pin-diode beamstop.
4. **Acquisition pattern: LEGACY (the ancestral GIWAXS loop).** The `run_giwaxs_Kim` that all later GI files inherit — nested `sample × waxs × x × θ`, `alignement_gisaxs(0.1)` per sample, `bp.count(dets, num=1)` per point, `scan_id` in name:
   ```python
   for ii,(x,sample) in enumerate(zip(x_list, sample_list)):
       yield from bps.mv(piezo.x, x); yield from alignement_gisaxs(0.1)
       for waxs_angle in Waxs_angle_array:
           yield from bps.mv(waxs, waxs_angle)
           for x_meas in x_pos_array:
               for i, th in enumerate(th_meas):
                   sample_id(user_name=username, sample_name=...sid{scan_id:08d}); yield from bp.count(dets, num=1)
   ```
5. **Notable:** plain `x_list`/`sample_list` (pre-`pxy_dict`); `inverse_angle` boustrophedon; air/vacuum and large-beam test naming; this is the **lineage root** of `run_giwaxs_Kim` seen in §5/§7/§15–18.
6. **Intent:** Microfocus GIWAXS/GISAXS of thin-film sample bars (Kim, 2022); the original legacy per-point GI loop that propagated into the whole group.

---

## FOLDER SYNTHESIS

- **Distinct archetypes (5):** (1) **GIWAXS/GISAXS sample-bar + Linkam** (`run_gix_loop_wsaxs` + `Temperature_Linkam_*`, threaded by `Aligned_Dict`) — PGuo/Kim/CNam/XDuan/Kim5; (2) **transmission SAXS/WAXS "static bar"** template (`measure_transmission_xs`/`measure_multi_*`/`NanoSyn`) — EHu/OGang/InSituDemo/InSituGrowth/ThreeGroups/FLu/XLin; (3) **autonomous droplet/flow nanoparticle synthesis** (`DropletReactor`/`DropletHolder`, npz/BoTorch closed loop) — 2024C3_Drop/2025C2_SMI/CMS_2025C1; (4) **microfocus raster + temperature melting kinetics** — 2024C3; (5) **SAXS/WAXS tomography** (`run_tomo` `prs` rotation series) — 2026C1_Tomo. Plus the `YZhang_SMI_Base` toolkit and an empty `liquids.py` stub.
- **Legacy-vs-modern prevalence: ~100% LEGACY plan bodies.** Grep for `run_decorator`/`stage_decorator`/`trigger_and_read`/`@bpp.` over all 21 files = **0 hits.** Every acquisition is per-point `bp.count`/`bp.scan`; filenames via global `sample_id(...)` / `RE.md["sample_name"]`; temperature (`LThermal.temperature()`/`getT()`), incident angle, energy, SDD and `xbpm` sum are **read into the filename string**, not recorded as devices/streams — the exact BAD pattern the beamline is migrating away from.
- **The only gesture toward modern naming** is `temp_series_grid()` (a `Signal('target_file_name')` passed as a detector: `bp.count(dets + [s])`), copied into the GI files — but it is still per-point inside nested loops and still mutates `RE.md["sample_name"]`; in 2026C1_PGuo/CNam it is even subtly broken (undefined `ais`/`bpm`). No `run_decorator`/`stage_decorator`/`trigger_and_read` anywhere.
- **`YZhang_SMI_Base.py` infrastructure:** provides the group's portable API — the `sample_dict`/`pxy_dict`→`x_list/y_list/sample_list` sample model; `get_motor()` piezo-vs-hexapod abstraction; transmission primitives (`measure_saxs/waxs/wsaxs`); the GI engine + `align_gix_loop_samples`→`Aligned_Dict`; `getSamMap` rasters; Lakeshore `setT/gotoT`; OAV/HEX camera saves; motion conveniences. It also **codifies the legacy idiom** (everything terminates in `bp.count(dets, num=1)` keyed by `sample_id`, and several helpers wrap `RE(...)` inside ordinary functions), so the whole folder inherits that style.
- **A real *facility* modernization is visible in headers, not plans.** 2025–2026 files adopt `proposal_swap(<id>)`, `project_set('<project>')`, `get_scan_md()`, `pil2M.insert_beamstop('rod'|'pd'|'pin')`/`restore_beamstop`/`active_beamstop`, and `startWAXS()`. This is the beamline's new project-scoped data-management + beamstop/detector state machine — adopted by the group, but the **plan logic was not rewritten** to single-run/decorated form.
- **2024 → 2025 → 2026 maturity trend (mostly *operational*, not architectural):**
  - **2024 (`2024C3*`, `2024C3_Drop`):** legacy `RE(...)`-inside-loops, melting/temperature in filenames, SmarAct/MDrive raster, autonomous droplet via npz. Heavy use of `RE(bps.mv(...))` *inside* driver functions (worst-practice mixing).
  - **2025 (`2025C2_*`, `2025C3_XLin`):** same plan bodies, but cleaner `yield from`-based generators dominate; **facility scaffolding appears** (`proposal_swap`, `project_set`, `insert_beamstop`, `pin_diode` in alignment); `NanoSyn` minimal time-series archetype emerges; serpentine dose-dither introduced (XLin).
  - **2026 (`2026C1_*`):** **most operationally mature** — project-scoped folders everywhere, detailed numbered vacuum/cryo SOP headers (CNam/XDuan), beamstop-X set programmatically, conditional multi-detector logic, Kelvin-based cryo T-series (XDuan), and a **new capability (`run_tomo` tomography)**. But the **core acquisition is byte-for-byte the 2022–2024 legacy loop** (the 2026 transmission files are clones of one template; `run_giwaxs_Kim` traces unbroken to `30-user-Kim5.py` from 2022).
- **Net assessment:** the group's **2026 scripts are MORE modern only in *facility integration and operational tooling*** (project data management, beamstop API, vacuum/cryo procedures, tomography) — **NOT in Bluesky run-management architecture.** On the GOOD-vs-BAD axis (one run per sample, `md={}`, context as devices/baseline), the 2026 CFN/Yugang code is **still fully legacy**, indistinguishable in plan structure from the 2022 Kim macros and the legacy-folder files. Migration targets are uniform: collapse the nested `waxs×sample×x×θ` (and `prs` tomo/CD) loops into single coordinated scans per sample/tomogram, move T/θ/energy/SDD/xbpm into the primary stream or baseline, and replace `sample_id`/`RE.md` mutation with `md={}` + a filename Signal carried in `trigger_and_read`.
- **Cross-beamline note:** `CMS_2025C1.py` is the same autonomous-droplet science expressed in the **CMS 11-BM SciAnalysis framework** (`Holder`/`Sample`/`detselect`/`cms.modeMeasurement`, SAXS+MAXS) rather than the SMI `sample_id`/`SMI_Beamline` stack — useful as the portability reference, but equally legacy (per-shot `sam.measure` in a polling loop).

# Legacy Bluesky/Ophyd Plan Analysis — Batch 07 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 16 legacy
user/utility macro files. Detectors: `pil2M` = SAXS (Pilatus 2M, in-vacuum),
`pil900KW`/`pil300KW` = WAXS (arc-mounted), `rayonix` = MAXS, `amptek`/`pin_diode`
(`pdcurrent1`) = transmission/fluorescence, `xbpm2/3.sumX/sumY` = beam-position
monitors, `ls` (Lakeshore, `input_A`/`output1`/`ch1_read`) = temperature.
`waxs.arc` (a.k.a. `waxs`) and `piezo.th`/`stage.th`/`stage.phi`/`prs` are slow /
in-vacuum axes. Goniometry split between `piezo.*` (fast nano SmarAct: x/y/z/th/ch=chi)
and `stage.*` (coarse hexapod). Tender/edge work via `energy` (DCM). `prs` = sample
rotation stage (CD-SAXS pitch/azimuth). `SMI_Beamline()` = alignment-mode helper class.

Pattern legend: **LEGACY** = nested `for` loops, each iteration calls
`bp.count`/`bp.scan`/`bp.rel_scan` → one Bluesky run per data point; filenames via
global mutable `sample_id(user_name, sample_name)` and/or `RE.md[...]`; context
(T, bpm, SDD, energy, humidity) read via `.value`/`.get()` and formatted into the
filename string. **MODERN** = `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)`
around `inner()` with `bps.trigger_and_read(dets + [signals])`. **MIXED** = both.

> Batch-wide finding: a grep for `run_decorator|stage_decorator|trigger_and_read|declare_stream|Signal(|baseline` across **all 16 files returned ZERO matches**. This entire batch is pre-migration: there is **no MODERN code anywhere**. The only gradation is LEGACY (per-point `bp.count`) vs LEGACY-with-coordinated-scan (`bp.scan`/`rel_scan`/`grid_scan`/`rel_grid_scan`/`inner_product_scan` — one run per line/map, naming aside).

---

## 1. 30-user-Gergaud.py
1. **Size / plans:** ~135 KB, ~52 `def`s (largest in batch; CEA-Leti program 2020→2026).
2. **User/group:** Patrice Gergaud / CEA-Leti semiconductor metrology (`PG`; guests Paul, Sophie, Nischal, Ulysse, Olivier, Nicolas; IBM). Operator `GF`.
3. **Use-cases:** **CD-SAXS** (critical-dimension SAXS — the defining technique: rocking the wafer in azimuth/`prs` from −60→+60° per nano-grating "pitch", `pitch112…128 nm`, defectivity/overlay/OCD structures), **CD-GISAXS** (`cd_gisaxs_phi`/`cd_gisaxs_alphai` — phi & incident-angle rocking on `stage.th`+`prs`+`piezo.ch` chi, up to 2001 points), **line-edge roughness** (`mesure_rugo`, `bp.count num=100–200`), **transmission GISAXS poly-period scan** (`GISAXS_scan_boite`, 81 x-positions), **NEXAFS** at unusual edges (Ti L ~4950–5050 eV, P K ~2145, S), direct-beam reference (`mesure_db`), an experimental **detector fly-scan** (`fly_scan_ai`).
   - **Detectors:** almost always `[pil2M]` (SAXS only; CD-SAXS is a transmission grating technique); `pil300KW` for NEXAFS/WAXS.
4. **Acquisition pattern: LEGACY (uniform).** Canonical CD-SAXS = sample-list loop → azimuthal rocking loop → per-angle count; rotation angle and pitch baked into filename:
   ```python
   for theta in np.linspace(th_ini, th_fin, th_st):
       yield from bps.mv(prs, theta)
       sample_id(user_name="PG", sample_name=f"{sample}_{theta}deg")
       yield from bp.count(det, num=10)   # det=[pil2M]
   ```
   - 2026 plans (`cdsaxsstd_2026_1_*`) add ref-before/ref-after frames and 8-axis per-sample positioning (`piezo.z/ch/x/y, stage.y`) but remain per-point counts via `cd_saxs_new`.
   - `fly_scan_ai` is an anti-pattern: stages/triggers the detector by hand (`det.stage()`, `det.cam.acquire_time.put`, `det.trigger()`) with an empty-detector `list_scan([], motor,...)` to sweep angle during one long exposure — outside normal document flow.
5. **Notable techniques/hardware:** `prs` azimuthal rotation; `piezo.ch` (chi) + `stage.th` for GI CD; huge per-sample chi/z/x/y/hexa coordinate tables (often dozens of commented wafer/champs variants); ref-frame bracketing for normalization; pitch arrays via `x_off` stepping; nightly composite macros (`macro_dinner`, `night_*`).
6. **Intent:** Semiconductor nano-grating **CD-SAXS / CD-GISAXS metrology** (pitch/overlay/defectivity/LER) plus Ti/P/S NEXAFS; deep legacy azimuthal-rocking per-point archive — the most domain-specific file in the repo.

---

## 2. 30-user-Fakhraai.py
1. **Size / plans:** ~82 KB, ~13 `def`s (2019→2024; most lines are commented multi-bar coordinate registries).
2. **User/group:** Zahra Fakhraai group, U-Penn (`YJ`,`AZ`; guests Luo `PL`, Kritika, Peng) — **stable/ultrastable organic glasses** (TPD, vapor-deposited amorphous films).
3. **Use-cases:** **GIWAXS/GISAXS thin-film** with per-spot auto-alignment, **spatial gradient mapping** along vapor-deposited films (`gFak1/2/3` "hot/middle/cold" zones; `grazing_gradient_Luo` steps in mm across a thermal gradient), **multi incident-angle** + **multi waxs-arc** (0/2/18/20°) sweeps, **double-stack sample holders** (Peng — top+bottom bars, ~24 samples × deposition-temperature series), x-walk anti-damage dosing.
   - **Detectors:** `pil2M`+`pil300KW`(+`rayonix` MAXS in early gFak); conditional `[pil900KW] if wa<15 else [pil900KW,pil2M]`.
4. **Acquisition pattern: LEGACY.** Two flavors: (a) `bp.scan(dets, waxs, *waxs_range)` per spot (one run per arc-sweep — slightly better), and (b) arc-loop → per-point `bp.count`. Alignment via `alignement_gisaxs`/`quickalign_gisaxs`; bpm/E/SDD into filename:
   ```python
   for i, wa in enumerate(angles):
       yield from bps.mv(waxs, wa)
       dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
       yield from bps.mvr(piezo.x, (i+1)*step_across_sample)   # fresh spot
       bpm = xbpm2.sumX.get(); e = energy.energy.position/1000
       sample_id(user_name="PL", sample_name=f"{name}_{e}keV_..._wa{wa}_ai{ai}_bpm{bpm}")
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** gradient-film position list generated from sample edges + step; `atten_move_in/out` Sn-60µm attenuator ladders (`att1_6`/`att1_7`) with status-polling `while` loops; `engage_detectors` warm-up; `try/except` fallback alignment angle; `stage.x` hexapod + `piezo` GI geometry; filename sanitization `translate`.
6. **Intent:** Grazing-incidence S/WAXS spatial + thermal-gradient mapping of vapor-deposited organic glasses with per-spot alignment; broad legacy GI archive across many guest campaigns.

---

## 3. 30-user-Katz.py
1. **Size / plans:** ~61 KB (not deep-read; characterized by structure & batch context).
2. **User/group:** Katz (operator-shared file).
3. **Use-cases (inferred from size class & batch siblings):** large multi-plan macro of the same family — transmission SWAXS multi-sample bars, GI sweeps, temperature/energy series. (Flagged for targeted follow-up; not individually inspected this pass per the "sample representative" directive.)
   - **Detectors:** `pil2M`/`pil900KW`/`pil300KW` (expected).
4. **Acquisition pattern: LEGACY (expected from batch homogeneity; no modern decorators present in any file per global grep).**
5. **Notable techniques/hardware:** TBD on focused read.
6. **Intent:** Large user macro collection; treat as LEGACY pending detailed pass.

---

## 4. 30-user-Zhang.py
1. **Size / plans:** ~40 KB, ~22 `def`s (Song Zhang / G. Freychet, 2020→2022).
2. **User/group:** Song Zhang (`SZ`,`GF`,`WZ`) — **conjugated-polymer / SEBS block-copolymer** mechanics & electronics.
3. **Use-cases:** **tender S K-edge resonant WAXS / NEXAFS** (dense grid 2445–2521 eV with fine 0.25–0.5 eV step across 2470–2480; `song_waxs_S_edge_*`, `song_nexafs_S_*`), **in-situ tensile / strain** kinetics on Linkam MFS stage (`song_tensile_*` — infinite `for i in range(2000)` loops, `strain=` arg into filename), **transmission/GI WAXS multi-sample bars** (up to 33 samples A1…G3), **fresh-spot energy×position meshgrid** rastering, **S-edge spatial mapping** (`mapping_S_edge_zhang`), GIWAXS double-stack with align (`hardxray_song_2022_3`).
   - **Detectors:** `pil300KW`+`pil2M`; `pil900KW` at tender edge; conditional SAXS-drop when arc<10–15.
4. **Acquisition pattern: LEGACY (uniform).** Signature = position+energy `np.meshgrid` flattened so each energy hits a fresh (x,y) spot (anti beam-damage), then per-point count with `xbpm2.sumX.value` into name:
   ```python
   yss, xss = np.meshgrid(np.linspace(ys, ys+620, len(energies)), [xs]); yss=yss.ravel(); xss=xss.ravel()
   for e, xsss, ysss in zip(energies, xss, yss):
       yield from bps.mv(energy, e); yield from bps.mv(piezo.y, ysss); yield from bps.mv(piezo.x, xsss)
       bpm = xbpm2.sumX.value
       sample_id(user_name="GF", sample_name=f"{name}_{e}eV_wa{wa}_bpm{bpm}")
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** GV7 gate-valve close before tender scans; energy direction-aware ramp (`if energy>2475: reversed`); `xbpm2.sumX<50` beam-loss re-try; SDD via `pil2M_pos.z.position`; Linkam MFS `strain` metadata (manual); `prs`/`stage.x` tensile. No Signals/decorators.
6. **Intent:** Resonant S-edge SWAXS/NEXAFS + in-situ tensile mechanics on conjugated-polymer/SEBS films; textbook legacy energy×fresh-spot meshgrid raster.

---

## 5. 30-user-Telles.py
1. **Size / plans:** ~32 KB, ~7 plans (mostly enormous hard-coded coordinate tables; 2022).
2. **User/group:** Telles (`RT`,`ED`; guests Rodrigo, Alice) — proposal 309101; thin-film / filament soft-matter.
3. **Use-cases:** **transmission SWAXS multi-sample bar — very large arrays** (`sample_bar_2022_1`: rows 7–10, ~54 samples each with individual x/y/y_range/y_hexa), **per-sample vertical line-scans** (`bp.rel_scan(piezo.y, *y_range)` — 10 µm step, one run per sample), **2-D grid maps** (`alice_grid_scans`, `bp.rel_grid_scan` over y×x), **filament y-scans**, unattended overnight wrapper (`run_overnight_exsitu_2022_2` chaining proposals).
   - **Detectors:** `pil900KW`+`pil2M`; conditional `[pil900KW] if wa<15 else [pil900KW,pil2M]`.
4. **Acquisition pattern: LEGACY (coordinated line/grid scans).** arc-outer → sample-inner → one `rel_scan`/`rel_grid_scan` per sample (better than per-point); metadata (E/wa/SDD/scan_id) into filename via `db[-1].start["scan_id"]+1`:
   ```python
   for wa in waxs_arc:
       dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
       yield from bps.mv(waxs, wa)
       for x, y, hy, sample, y_r in zip(x_list, y_list, y_hexa, sample_names, y_range):
           yield from bps.mv(piezo.x, x, piezo.y, y); yield from bps.mv(stage.y, hy)
           sample_id(user_name="RT", sample_name=f"{bar}_{sample}_wa{wa}_dy10um_1s_yscan")
           yield from bp.rel_scan(dets, piezo.y, *y_r)
   ```
5. **Notable techniques/hardware:** per-sample variable y-range/step-count (sample-height-aware); hexapod `stage.y` row offsets; `db[-1].start["scan_id"]` transient-ID-into-name; proposal-switching overnight chain with `try/except`. No Signals/decorators.
6. **Intent:** High-throughput transmission SWAXS line-scan/grid survey of large multi-row sample bars; legacy but already using coordinated per-sample scans.

---

## 6. 30-user-Jones.py
1. **Size / plans:** ~25 KB, ~13 plans (2023→2025).
2. **User/group:** Jones (`ZC`,`GI`,`Insitu`,`SF`; chiral materials) — proposals 312283/312437/318110; Td/TBP chiral & achiral thin films.
3. **Use-cases:** **GISWAXS** with full reflected-beam auto-alignment (`alignement_gisaxs`/`_hex` via `SMI_Beamline().modeAlignment/modeMeasurement`, direct + reflected ROI, derivative peak-find), **multi incident-angle** (0.08–0.5°) + **multi waxs-arc** (15/25°), **in-situ humidity GISWAXS time-series** (`run_gi_humid`/`_new` — `readHumidity()`, dry/wet MFC `setWetFlow`/`setDryFlow`, long `for nn in range(Nmax)` polling with 3-tier sleep schedule, hexapod `stage.x/y/th`), transmission SAXS arrays (`measure_saxs_array`).
   - **Detectors:** `pil2M`+`pil900KW`; conditional `[pil900KW, pil2M] if waxs_angle>=15 else [pil900KW]`.
4. **Acquisition pattern: LEGACY.** Sample→align→arc→x-walk→incident-angle nested loops, per-point `bp.count`; humidity & elapsed-time formatted into name; alignment offsets persisted to a text file (not as device):
   ```python
   for sample, x_hexa, th_hexa, y_hexa in zip(sample_list, x_hexa_list, th_hexa_aligned, y_hexa_aligned):
       for xr in xr_list:
           yield from bps.mv(stage.x, x_hexa+xr); yield from bps.mv(stage.y, y_hexa)
           for th in th_meas:
               yield from bps.mv(stage.th, th)
               humidity = "%3.2f" % readHumidity(verbosity=0)
               sample_id(user_name='Insitu', sample_name=f"{sample}_n{nn}_t{...}s_..._waxs{wa}_x{...}")
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `SMI_Beamline()` alignment-mode class (direct/reflected ROI, `bec._calc_derivative_and_stats`); `saxs_bs.rod_in` beam-stop insertion; pre-aligned y/th dictionaries (align-once / measure-many across in-situ time); RH chamber MFC dry/wet flow + `readHumidity`; aligned-position logging to disk; angle-dependent x/y anti-damage walk; copious `RE(...)`-in-comments operator runbook header. No Signals/decorators.
6. **Intent:** Humidity-controlled in-situ GISWAXS kinetics on chiral thin films with reflected-beam auto-alignment; mature-legacy (helper-rich) per-point counts.

---

## 7. 30-user-Xu.py
1. **Size / plans:** ~15 KB, 5 plans (2023→2024).
2. **User/group:** Xu (operators `AG` Alexandra, `TC` Chen; guests HY, Chen) — solution/capillary scattering (NAP, EC organics, PN series).
3. **Use-cases:** **transmission SAXS/WAXS multi-capillary bar** (`run_capillaries_*` — x/y/z piezo per capillary), **two/three-exposure bracketing** (short+long, e.g. 0.5/5 s or 10/20/30 s for dynamic range), **transmission readout** (pin-diode current with fast-shutter pulse), **temperature-series SAXS** (`run_temp_capillaries_*` — Lakeshore equilibration), **SAXS time-study** (`bp.count(dets, num, delay_sec)`).
   - **Detectors:** `[pil2M]` (SAXS) / `[pil900KW]` (WAXS); conditional `[pil900KW] if waxs.arc<15 else [pil2M,pil900KW]`.
4. **Acquisition pattern: LEGACY.** sample→arc→y-offset→exposure nested loops with per-point `bp.count`; pin-diode current + `get_scan_md()` appended to filename; temperature read into name:
   ```python
   for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):
       yield from bps.mv(piezo.x, x, piezo.y, y, piezo.z, z)
       for wa in waxs_arc:
           yield from bps.mv(waxs, wa)
           if waxs.arc.position > 15: fs.open(); pd_curr=pdcurrent1.value; fs.close()
           for yy, y_of in enumerate(y_off):
               for exp in exposures:
                   det_exposure_time(exp, exp)
                   sample_id(user_name, sample_name=f"{name}_exp{exp}_loc{yy}_pd{pd}{get_scan_md()}")
                   yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** multi-exposure HDR bracketing; transmission via `pdcurrent1` + `fs` fast shutter (arc-gated); Lakeshore `ls.output1.mv_temp`/`input_A.get()` equilibration with 15-min timeout + T-band extra hold; `get_scan_md()` helper appends transient metadata to name; per-capillary x/y/z registry. No Signals/decorators.
6. **Intent:** Transmission SAXS/WAXS of solution capillaries with HDR exposure bracketing, transmission monitoring, and optional temperature series; clean legacy.

---

## 8. 30-user-HZhang.py
1. **Size / plans:** ~13 KB, ~20 `def`s (2021; mostly `RE()`-wrapping helpers).
2. **User/group:** H. Zhang (`HZ`) — Au-nanoparticle / PEG-grafted colloids in silicone oil & salt (microfocus).
3. **Use-cases:** **microfocus transmission SAXS 2-D mapping** (`measure_saxs_map` x×y nested, `do_one_map` 18×51 grids "Up"/"Bot"), **vertical line-scans** (`measure_saxs_scany`, `do_one_yscan`, N=220 points), **multi-angle WAXS** (`measure_waxs_multi_angles` 0/6.5/13°), `sample_dict`/`pxy_dict` coordinate registry, snap helpers.
   - **Detectors:** `[pil2M]` (SAXS map) / `[pil300KW]`/`[pil900KW]` (WAXS).
4. **Acquisition pattern: LEGACY + anti-pattern (`RE()` inside helpers).** Map/scan plans are generators (per-point `bp.count`), BUT the orchestration helpers (`mov_sam`, `movx`, `do_one_map`, `measure_series_*`) call **`RE(...)` directly inside Python functions** and stash names in `RE.md["sample"]`:
   ```python
   def mov_sam(pos):
       px, py = pxy_dict[pos]; RE(bps.mv(piezo.x, px)); RE(bps.mv(piezo.y, py))
       RE.md["sample"] = sample_dict[pos]
   def do_one_map(sam_id, xstart, ...):
       mov_sam(sam_id)
       RE(measure_saxs_map(xlist, ylist, sample=RE.md["sample"]+"Up", ...))
   # measure_saxs_map: filename built from piezo.x/y, pil2M_pos.z, RE.md["scan_id"]
   ```
5. **Notable techniques/hardware:** `sample_dict`/`pxy_dict` per-sample position registry; SAXS distance (`pil2M_pos.z`) + scan_id baked into name; iterative anti-damage map-position notes in comments; a logged y-scan bug (`mv` vs `mvr`); pin-diode current helper. Heaviest `RE()`-in-loop / `RE.md` reliance after OGang. No Signals/decorators.
6. **Intent:** Microfocus transmission SAXS mapping + line-scans of grafted-Au colloids; legacy with blocking `RE()` orchestration (not composable generators).

---

## 9. 30-user-Subh.py
1. **Size / plans:** ~11 KB, ~12 plans (guests "NIST"/`AK`/`FA`).
2. **User/group:** Subh (`AK`, `NIST`, `FA`) — fluoropolymer / membrane GI (PVDF, BTBT, BW30 RO-membrane, P75/P50 blends).
3. **Use-cases:** **GISAXS/GIWAXS** with bespoke height/theta auto-align (`alignsubhgi`, ROI-Y tracking, `ps()` derivative/peak/centroid), **tender resonant grazing** (`do_grazing1` — e-list 2460/2477/2500 eV), **angle-offset arc series** (`do_grazingsubh`, x-walk over 41 spots), **temperature GIWAXS** (`do_grazingtemp` — per-stripe `grid_scan` + re-align), single-image WAXS (`bp.grid_scan(dets, waxs, *waxs_arc)`).
   - **Detectors:** `[pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]` (WAXS + ROI + bpm in det list); `pil2M`+ROIs for alignment.
4. **Acquisition pattern: LEGACY.** align → energy×angle×x-walk nested → `bp.scan(dets, waxs, *waxs_arc)` per spot (one run per arc-sweep), real incident angle into name:
   ```python
   for i_e, e in enumerate(e_list):
       for j, ang in enumerate(a_off - np.array(angle_offset)):
           yield from bps.mv(piezo.x, xloc + x_offset[offset_idx]); offset_idx += 1
           real_ang = 0.200 + angle_offset[j]/1000
           yield from bps.mv(piezo.th, ang)
           sample_id(user_name="NIST", sample_name=f"{name}_{e}eV_{real_ang}deg")
           yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable techniques/hardware:** `GV7` gate valve; alignment/measurement beam-stop modes (`alignmentmodesubh`/`measurementmodesubh`, `pil2M_bs_rod.x` in/out, att1_2/att1_3 insert/retract); ROI-Y specular tracking; `bp.grid_scan` over `piezo.x`×`waxs` stripes with re-align between (`do_grazingtemp`); `xbpm*.sumY` + `pil300kwroi2` recorded in det list. No Signals/decorators.
6. **Intent:** Tender/hard GI-S/WAXS on fluoropolymer & membrane films with custom alignment and stripe-mapping; legacy per-spot arc scans.

---

## 10. 30-user-Taylor.py
1. **Size / plans:** ~9 KB, 3 plans (2019→2020; OPV & 2D-materials).
2. **User/group:** Taylor (`AT`; guests JM, ZQ) — perovskites, organic PV (PM6:Y6:ASSQ), MXene 2D flakes.
3. **Use-cases:** **GIWAXS multi-sample bar** (`run_giwaxs_2020_3`/`run_giwaxs` — per-sample `alignement_gisaxs`, incident angles 0.08–0.30°, waxs-arc 0–19.5°, x-walk), **transmission/GI WAXS x-line scan** (`do_twaxs_scanx` — `pil300KW`, MXene, 31-point x raster). Extensive commented multi-run sample/x registries (RUN 2–8).
   - **Detectors:** `[pil300KW]` (waxs; comment notes `waxs,maxs,saxs=[pil300KW,rayonix,pil2M]`).
4. **Acquisition pattern: LEGACY.** sample→align→waxs-arc→incident-angle→x-walk nested, per-point `bp.count`; th/x/waxs/exposure into name:
   ```python
   for x, sample in zip(x_list, sample_list):
       yield from bps.mv(piezo.x, x); yield from alignement_gisaxs(0.1)
       th_meas = angle_arc + piezo.th.position
       for waxs_angle in waxs_angle_array:
           yield from bps.mv(waxs, waxs_angle)
           for i, th in enumerate(th_meas):
               yield from bps.mv(piezo.th, th); yield from bps.mv(piezo.x, x_meas + i*200)
               sample_id(user_name="AT", sample_name=f"{sample}_deg{th_real[i]:5.3f}_x{x_meas}_waxs{waxs_angle:05.2f}_{t}s")
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `alignement_gisaxs` per sample; `angle_arc + piezo.th.position` relative-angle convention; x-shift dose-spreading (`i*200`); q-range annotations from arc+angle geometry. No Signals/decorators.
6. **Intent:** Grazing-incidence WAXS survey of OPV/perovskite/MXene films; early legacy multi-sample GI loop.

---

## 11. 30-user-Ruan.py
1. **Size / plans:** ~7 KB, 6 plans (`ZR`,`OS` operators; solution biophysics).
2. **User/group:** Ruan (`ZR`,`OS`) — protein/buffer solutions, halide-containing samples (Le/Phil series).
3. **Use-cases:** **tender/edge NEXAFS on solutions** (`NEXAFS_S_edge` 2450–2500, `NEXAFS_Cl_edge` 2800–2850, `NEXAFS_Br_edge` 13450–13500 — three distinct edges incl. Br K), **resonant/anomalous SAXS at edges** (`SAXS_Cl_edge`/`SAXS_Br_edge`/`SAXS_s_edge` — discrete energies × multi waxs-arc, with pre/post-measurement reference frames and fresh-spot y-walk).
   - **Detectors:** `[pil300KW]` (NEXAFS, waxs@60°) / `[pil300KW, pil2M]` (resonant SAXS).
4. **Acquisition pattern: LEGACY (uniform).** energy loop (NEXAFS) or arc×energy loop (SAXS), per-point `bp.count`, `xbpm3.sumY.value` into name, energy-return + post-meas reference at end:
   ```python
   for wax in wa:
       yield from bps.mv(waxs, wax)
       for k, (e, yss) in enumerate(zip(energies, ys)):
           yield from bps.mv(energy, e); yield from bps.mv(piezo.y, yss)   # fresh spot per energy
           sample_id(user_name="OS", sample_name=f"{name}_{e}eV_xbpm{xbpm3.sumY.value}_wa{wax}")
           yield from bp.count(dets, num=1)
   # then a "_postmeas" reference frame at the edge-foot energy per arc
   ```
5. **Notable techniques/hardware:** WAXS arc parked at 60° for NEXAFS geometry; GV7 close before S-edge; fresh-spot `np.linspace(y0, y0+750, 6)` per energy (radiation-damage on solutions); pre/post reference frames for normalization; `xbpm3.sumY` beam normalization into name. No Signals/decorators.
6. **Intent:** Multi-edge (S/Cl/Br) NEXAFS + resonant/anomalous SAXS on biological solutions with damage-aware fresh-spot dosing; pure legacy.

---

## 12. 30-user-Kiick.py
1. **Size / plans:** ~6 KB, ~9 plans (RPI/Linkam capillary; `JA`,`SL`,`HH`,`LC`).
2. **User/group:** Kiick (`user`/`JA`/`SL`/`HH`/`LC`) — liquid-crystal (LC-O3x) & solution capillaries, Linkam-stage temperature.
3. **Use-cases:** **transmission SAXS/WAXS multi-capillary bar** (`run_caps_fastRPI` — arc-sweep × 4 capillaries), **Linkam temperature SAXS** (`run_saxs_cap_temp_2022_2` — full attenuator/pin-diode transmission protocol, single `rel_scan`), **continuous time-series** (`run_contRPI` — N×`bp.count`+sleep; `run_waxs_linkamRPI_2022_1` — time-gated arc snaps), capillary y-scans, temperature-into-name snaps (`acq_tem`/`acq_bd`).
   - **Detectors:** `[pil2M]`/`[pil2M, pil300KW]`/`[pil2M, pil900KW]`; `pdcurrent1` in temp plan.
4. **Acquisition pattern: LEGACY (mix of per-point count + line scan).** arc→capillary per-point count, and a well-documented temperature plan doing attenuator-in → shutter-pulse pin-diode → attenuator-out → `rel_scan`:
   ```python
   for att in attenuators: yield from bps.mv(att.open_cmd, 1)
   fs.open(); pd_current = pdcurrent1.get(); fs.close()
   for att in attenuators: yield from bps.mv(att.close_cmd, 1)
   e = energy.position.energy/1000; wa = waxs.arc.position; sdd = pil2M_pos.z.position/1000
   scan_id = db[-1].start["scan_id"] + 1
   sample_id(user_name=user, sample_name=f"{name}_{e}keV_{temp}degC_wa{wa}_sdd{sdd}m_id{scan_id}_pd{pd_current}")
   yield from bp.rel_scan([pil2M, pdcurrent1], stage.y, *y_range, n_points)
   ```
5. **Notable techniques/hardware:** `att2_1/att2_2` Mo-20µm attenuator ladder; pin-diode transmission via fast-shutter pulse; Linkam-on-laptop with Lakeshore (`ls.ch1_read`) T readout; E/wa/SDD/scan_id/pd all into filename; time-gated continuous snaps. No Signals/decorators.
6. **Intent:** Temperature-controlled transmission SAXS/WAXS of LC/solution capillaries with attenuator transmission protocol; legacy with good per-measurement metadata-in-name.

---

## 13. 30-user-Greer.py
1. **Size / plans:** ~3 KB, 2 plans (`JG`).
2. **User/group:** Greer (`JG`) — oriented samples (SP/BO, X/Y/Z orientations, 90°).
3. **Use-cases:** **transmission SAXS/WAXS 2-D micro-mapping** (`mapping_saxs_Greer` — per-sample `rel_grid_scan` over piezo.x×y, variable map dims), **multi waxs-arc** (0–26°, 5 steps). Includes `amptek` (fluorescence/energy-dispersive) alongside Pilatus.
   - **Detectors:** `[pil2M, pil300KW, amptek]` (SAXS + WAXS + Amptek SDD — one of few using `amptek`).
4. **Acquisition pattern: LEGACY (coordinated grid scan).** arc-outer → sample-inner → one `rel_grid_scan` per sample (one run per map — good form, naming aside):
   ```python
   for wa in waxs_range:                       # np.linspace(0, 26, 5)
       yield from bps.mv(waxs, wa)
       for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
           yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y)
           sample_id(user_name="JG", sample_name=f"{sample}_wa{wa:2.1f}deg")
           yield from bp.rel_grid_scan(dets, piezo.x, *x_r, piezo.y, *y_r, 0)   # 0=not-snake
   ```
5. **Notable techniques/hardware:** `amptek` energy-dispersive detector in primary det list; per-sample variable grid extents/step-counts; assertion-guarded coordinate lists; `_test` dry-run twin. No Signals/decorators.
6. **Intent:** Orientation-dependent SAXS/WAXS micro-mapping (+Amptek) of textured samples; compact legacy grid-scan macro.

---

## 14. 30-user-Sarkar.py
1. **Size / plans:** ~3 KB, 1 plan (`AS`; smallest user file).
2. **User/group:** Sarkar (`AS`) — HSL / liquid-crystal-like samples (HSL2LAM, HSLS2HEX, furan/PO; mostly commented out, active = kapton background).
3. **Use-cases:** **transmission SAXS/WAXS multi-sample bar** (`run_Sarkar` — arc-sweep 0/6.5/13/19.5° × sample list at fixed SDD 8.3 m / 16.1 keV). Currently reduced to a single `kapton_bkg`.
   - **Detectors:** `[pil300KW, pil2M]`.
4. **Acquisition pattern: LEGACY (minimal).** arc(reversed)→sample, per-point `bp.count`; arc into name; resets to test afterward:
   ```python
   for wa in waxs_arc[::-1]:
       yield from bps.mv(waxs, wa)
       for x, y, s in zip(x_list, y_list, samples):
           yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y); yield from bps.sleep(2)
           det_exposure_time(t, t)
           sample_id(user_name="AS", sample_name=f"{s}_wa{wa:02d}_sdd8.3m_16.1keV")
           yield from bp.count(dets, num=1)
           sample_id(user_name="test", sample_name="test")   # reset between points (!)
   ```
5. **Notable techniques/hardware:** arc-direction reversal (`[::-1]`) to minimize travel; SDD/energy hard-coded into name; resets `sample_id` to "test" inside the loop. No Signals/decorators.
6. **Intent:** Simple multi-sample transmission SWAXS arc-sweep on LC-type bar; minimal canonical legacy loop.

---

## 15. 33-oleg.py  ⚙️ INFRASTRUCTURE / BEAMLINE-SCIENTIST UTILITY
1. **Size / plans:** ~18 KB, ~8 plans (Oleg Gang–era beamline-scientist scratch file; users `BM` Brian, `AM` Aaron).
2. **User/group:** Oleg (SMI beamline scientist) — generic/guest utility macros, **not a single science program**. Flag as **infrastructure/template precursor**.
3. **Use-cases:** **transmission SAXS multi-capillary bars** (`brian_caps*` — many variants, big x/y/z tables, num=1…240 frames), **beam-damage time-series** (`brian_caps_damage_2021_1` — `det_exposure_time(1,180)` then count+`sleep(200)` per capillary), **micro-mesh raster mapping** (`run_mesh_aaron*` — x×y `np.linspace` per-pixel count, or `rel_grid_scan`), **rotation/tomography line-scans** (`aaron_rot` — `inner_product_scan` coupling `prs` rotation + `stage.x`/`piezo`).
   - **Detectors:** `[pil2M]` (SAXS) / `[pil900KW, pil2M]`.
4. **Acquisition pattern: LEGACY (template-grade).** The reference forms later users copied: capillary-bar loop, mesh double-`linspace` per-pixel count, and coordinated `inner_product_scan`/`rel_grid_scan`:
   ```python
   yield from bp.inner_product_scan([pil2M], 24, prs, 45, 22, stage.x, 0.23, 0.15, piezo.y, -1792.6, -1792.6)
   ...
   for xs in np.linspace(x_r[0], x_r[1], x_r[2]):
       for ys in np.linspace(y_r[0], y_r[1], y_r[2]):
           yield from bps.mv(piezo.x, xs); yield from bps.mv(piezo.y, ys)
           sample_id(user_name="AM", sample_name=f"{sample}_8.3m_16.1keV_pos{i:04d}_up")
           yield from bp.count(dets, num=1); i += 1
   ```
5. **Notable techniques/hardware:** `prs`-coupled `inner_product_scan` (rotation tomography / azimuthal); beam-damage protocol (1 s + 180 s exposures, sleep-gated); `pil2M_pos.y` detector-position toggling between up/down map passes; assertion-guarded coordinate tables; the `brian_caps`/`run_mesh_aaron` idioms are clearly the ancestors of the user-file patterns. No Signals/decorators.
6. **Intent:** **Beamline-scientist utility/scratch file** of canonical capillary-bar, mesh-map, beam-damage, and rotation-scan templates — the source idioms the legacy user macros inherited. Treat as INFRASTRUCTURE, not a science program.

---

## 16. 35-oleg-cube.py  ⚙️ INFRASTRUCTURE / BEAMLINE-SCIENTIST UTILITY
1. **Size / plans:** ~3.5 KB, 3 plans (Oleg scratch; users `AM` Aaron).
2. **User/group:** Oleg (beamline scientist) — small utility companion to `33-oleg.py`. Flag as **infrastructure**.
3. **Use-cases:** **rotation/azimuthal line-scans** (`aaron_rot` — chained `inner_product_scan` coupling `prs` rotation with `piezo.x`/`stage.x`, "cube"/tetrahedral nano-object orientation series; ID-30 nano-positioning), **undulator-gap test ramp** (`test_scan` — pokes `new_ivu_gap.set()` directly, IVU insertion-device commissioning), **GIWAXS-style positioned counts** (`waxs_aaron_2021_3` — sample/arc/offset nested per-point count).
   - **Detectors:** `[pil2M]` / `[pil900KW, pil2M]`.
4. **Acquisition pattern: LEGACY + hardware-commissioning anti-pattern.** Coupled rotation scans plus a raw insertion-device poke outside the RE:
   ```python
   yield from bp.inner_product_scan([pil2M], 45, prs, 45, 0, piezo.x, 5580, 5640)   # azimuth+x couple
   ...
   def test_scan(start=11800, t=10, step=10):
       for i in range(t):
           new_ivu_gap.set(start - i*step); yield from bps.sleep(2)   # IVU gap commissioning (no detector)
   ```
5. **Notable techniques/hardware:** `prs`+`piezo`/`stage` inner-product azimuthal coupling for 3-D/cube nano-object orientation; `new_ivu_gap` undulator-gap direct control (beamline commissioning, not user science); GIWAXS arc/offset positioning. No Signals/decorators.
6. **Intent:** **Beamline-scientist commissioning/utility file** — azimuthal "cube" rotation scans + undulator-gap test ramp. Treat as INFRASTRUCTURE.

---

# BATCH SYNTHESIS

- **Distinct scientific archetypes in this batch (≈8):** (1) **CD-SAXS / CD-GISAXS semiconductor metrology** — azimuthal/`prs` rocking of nano-gratings for pitch/overlay/defectivity/LER, the unique signature of **Gergaud** (and the `prs`+`inner_product_scan` roots in the Oleg files); (2) **GISAXS/GIWAXS thin-film** with per-spot auto-alignment + incident-angle + waxs-arc sweeps (Fakhraai, Jones, Taylor, Subh, Zhang `hardxray`); (3) **tender/edge NEXAFS & resonant/anomalous SWAXS** — S K (~2475), Cl K (~2820), P K (~2145), Ti L (~5000), Br K (~13470) edges with fine ~0.25–0.5 eV grids (Zhang, Ruan, Gergaud); (4) **transmission SWAXS multi-sample/capillary bar** survey (Telles, Sarkar, Xu, Kiick, HZhang, Katz, Oleg `brian_caps`); (5) **spatial raster / micro-mapping** (HZhang, Greer, Telles grids, Oleg `run_mesh_aaron`, Zhang `mapping_S_edge`); (6) **in-situ time-series / kinetics** — tensile/strain (Zhang `song_tensile_*` 2000-iter loops), humidity/RH (Jones `run_gi_humid`), temperature (Xu/Kiick Linkam), beam-damage (Oleg, Xu); (7) **multi-exposure HDR + transmission monitoring** (Xu, Kiick — short/long brackets + pin-diode/`pdcurrent1` via fast-shutter pulse); (8) **environment control** — Lakeshore/Linkam temperature, RH MFC dry/wet flow, attenuator ladders.
- **Legacy is total — there is NO modern code in this batch.** A repo-wide grep for `run_decorator|stage_decorator|trigger_and_read|declare_stream|Signal(|baseline` across all 16 files returned **zero matches**. Unlike Batch 05 (where Su/Gann had genuine MODERN/MIXED plans), Batch 07 is **uniformly pre-migration**. The only quality gradient is per-point `bp.count(num=1)` (most files) vs. one-run-per-line/map coordinated scans (`bp.scan`/`rel_scan`/`grid_scan`/`rel_grid_scan`/`inner_product_scan` — Telles, Greer, Kiick temp, Subh, Oleg, Fakhraai `bp.scan` flavor).
- **Universal legacy signature confirmed:** nested Python `for` loops (commonly arc → sample → angle/energy/x-walk → exposure) where the innermost call emits one Bluesky run per data point; the run-per-logical-sample model is **absent everywhere**.
- **Filename = global mutable state in 100% of files:** every file routes the output filename through `sample_id(user_name, sample_name)` and/or `RE.md["sample"|"sample_name"|"scan_id"]`. None promotes the target filename to an ophyd `Signal`. HZhang even uses `RE.md["sample"]` as the *interprocess* carrier between `mov_sam()` and `measure_*()`.
- **Context read as `.value`/`.get()` into strings, never recorded as a device — the dominant provenance gap:** beam current (`xbpm2.sumX.value`/`xbpm3.sumY.value`) appears in Zhang/Ruan/Gergaud/Fakhraai names; temperature (`ls.input_A.get()-273.15`, `ls.ch1_read.value`), humidity (`readHumidity()`), strain (manual `strain=` arg), SDD (`pil2M_pos.z.position`), energy (`energy.position.energy/1000`), pin-diode current (`pdcurrent1.value`), and transient `db[-1].start["scan_id"]+1` are all formatted into filenames rather than captured as baseline/primary-stream signals.
- **Three anti-patterns beyond plain legacy:** (a) **`RE(...)` called inside Python functions/loops** — HZhang (`mov_sam`, `movx`, `do_one_map`, `measure_series_*`), giving blocking, re-entrant, non-composable "plans"; (b) **manual detector triggering outside the RunEngine** — Gergaud `fly_scan_ai` (`det.stage()`/`det.cam.acquire_time.put`/`det.trigger()` with empty `list_scan([], motor, ...)`); (c) **direct insertion-device pokes** — `35-oleg-cube.py` `test_scan` drives `new_ivu_gap.set()` with no detector (commissioning).
- **Infrastructure / utility files flagged (2):** **`33-oleg.py`** and **`35-oleg-cube.py`** are Oleg-era beamline-scientist scratch/utility files (guest users `BM` Brian, `AM` Aaron; capillary-bar, mesh-map, beam-damage, and `prs`-coupled rotation/`inner_product_scan` templates; `new_ivu_gap` commissioning). They are **the ancestral idioms** the user macros copied (note `brian_caps`/`run_mesh_aaron` ≈ later `run_caps_*`/mapping plans). **`30-user-Katz.py`** (~61 KB) was not deep-read per the "sample representative" directive — flagged for a focused follow-up pass, but expected LEGACY given the zero-decorator grep.
- **Conditional detector lists are ubiquitous and correct-in-spirit:** `dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]` (Telles, Xu, Fakhraai, Jones, Zhang, Subh) — the desired modern form is separate declared SAXS/WAXS streams. Notable detector breadth: **`rayonix` (MAXS)** in Fakhraai `gFak*`; **`amptek` (energy-dispersive)** in Greer; ROI/bpm objects placed directly in det lists (Subh `[pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]`).
- **Anti-beam-damage rastering is a recurring, well-engineered instinct** the modern template should formalize: energy×position `np.meshgrid` fresh-spot indexing (Zhang, Gergaud GISAXS_scan_boite), x-walk per angle (`piezo.x + i*200`, Taylor/Fakhraai/Subh/Jones), fresh-y per energy on solutions (Ruan `np.linspace(y0, y0+750, 6)`), and explicit beam-damage exposure protocols (Oleg/Xu). Slow/in-vacuum-axis ordering (`waxs.arc` outer, `[::-1]` reversal — Sarkar/Telles/Fakhraai) and align-once/measure-many caching (Jones aligned-position dicts/file, Subh re-align between stripes) are also respected informally.
- **Migration priorities (from this batch):** retire HZhang's `RE()`-in-loop orchestration, Gergaud's hand-rolled `fly_scan_ai` trigger, and the Oleg `new_ivu_gap` poke; convert the dominant arc→sample→energy/angle per-point `bp.count` loops to single decorated runs with target-filename + xbpm + T + humidity + SDD + energy + strain promoted to Signals/baseline. Best-shaped legacy starting points (already coordinated single-run-per-unit): Telles line/grid scans, Greer/Kiick grid+rel_scan, Subh/Fakhraai `bp.scan(waxs)`, and the Oleg `inner_product_scan`/`rel_grid_scan` templates.

# Legacy Bluesky/Ophyd Script Analysis — Batch 02 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 12 legacy
user scripts. Goal: characterize DISTINCT plan/scan archetypes and legacy-vs-modern
acquisition style. No fixes proposed.

**Reference patterns** (from `templates/`):
- **MODERN** (`tender.py`, `tranmission.py`, modern Guillaume 2025_3 plans): one Bluesky
  run per sample via `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md={...})` around
  `inner()`, data through `yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, ... , target_file_name_signal])`. Context (incident angle, energy direction, target
  filename) captured as ophyd `Signal`s in the primary stream.
- **LEGACY** (`grazing_fakhraai_template.py`): nested `for` loops, each iteration calling
  `yield from bp.count(dets)` / `bp.scan` / `bp.rel_scan` (a separate run per point); global
  mutable `sample_id(user_name=..., sample_name=...)` for filenames; temperature / xbpm read
  via `.value`/`.get()` into the filename string; hard-coded coordinate/sample lists in plan body.

Detector legend: `pil2M` = SAXS (1M/2M Pilatus), `pil900KW`/`pil300KW` = WAXS (arc),
`rayonix` = MAXS, `amptek` = energy-dispersive fluorescence (XAS yield), `pin_diode`/`xbpm2`/`xbpm3` = I0/beam-position monitors.

---

## 1. 30-user-Guillaume.py
1. **Size / count:** ~332 KB, ~8350 lines, **~149 top-level plan functions** (largest file in batch; sampled, not exhaustive).
2. **User/group:** Guillaume Freychet (beamline scientist, "GF"); umbrella file hosting many guest groups (Fleury, Amalie, McNeil, Song, Su, Gu, Zhengxing, Saroj, Pauldumas, etc.).
3. **Use-cases (tags):** tender/edge XAS + NEXAFS (S, Cl, Sn, Zn, Pt, Co, Ru, Te, Fe, Br, Cr, Ag, Mo K/L edges), GISAXS/GIWAXS (grazing, smaract + hexapod double-stack alignment), transmission SWAXS, **CD-SAXS** (`cd_saxs_Coedge`, phi rotation `prs` + energy), **pole-figure** (181-pt phi rotation), microfocus x-raster (beam-damage stepping `x - counter*xstep`), temperature series (Linkam `LThermal`), fluorescence-yield XAS (`amptek`), **pin_diode vs bpm I0 calibration** (`bpmvspindiode_*`), **XRR** (`xrr_Pedge_2025_6`), rocking/fly scans for CD-GISAXS, multi-sample bar, alignment routines.
3b. **Detectors:** pil2M, pil900KW, pil300KW (+ pil300kwroi2), amptek, xbpm2/xbpm3, pin_diode; attenuator banks (att2_5, att2_6, att2_9).
4. **Pattern: MIXED (clear chronological migration).** ~134 `bp.count/scan` (legacy) calls vs ~39 `inner()` + ~41 `trigger_and_read` (modern). 2020–2024 plans are legacy; 2025_3-era plans (`giwaxs_Gu/Su/Milo/NV/chris_2025_3`, `sevralai_giwaxs_*_edge_2025_3`) are modern.
   ```python
   # MODERN (giwaxs_Gu_2025_3):
   s = Signal(name='target_file_name', value='')
   @bpp.stage_decorator(dets)
   @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
   def inner():
       ...
       yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
   # LEGACY (waxs_S_edge_guil): for e in energies: ... sample_id(...); yield from bp.count(dets, num=1)
   ```
5. **Notable hardware:** `smaract` long-range x + hexapod (`stage.x/y/th`) "double-stack" GI alignment; `prs` phi rotation stage (CD-SAXS / pole figure); `energy` mono with up/down sweeps + `bps.sleep` settle; GV7 SAXS gate-valve interlock; per-point xbpm flux gating (`if xbpm2.sumX.get() < 50: ...`); `amptek` MCA fluorescence.
6. **Intent:** Beamline-scientist master cookbook spanning the full SMI technique portfolio (tender XAS, GI-SWAXS, CD-SAXS, XRR), captured live across cycles and mid-migration to the modern single-run idiom.

---

## 2. 30-user-ETsai.py
1. **Size / count:** ~30 KB, 751 lines, ~11 plan functions (incl. alignment helpers).
2. **User/group:** Esther Tsai (beamline scientist, "ET"); drives proposals tagged KM/SF/CK/GI/NEA/Insitu (Jones block-copolymer S2VP work).
3. **Use-cases (tags):** GISAXS/GIWAXS multi-sample bar with per-sample auto-alignment; **humidity/RH in-situ time-series/kinetics** (`run_gi_humid`, `run_gi_humid_new`, `readHumidity`, `setWetFlow`/`setDryFlow`); microfocus x/y arrays (`measure_saxs_array`, `measure_waxs`); thermal block-copolymer series (S2VP/PS/P2VP, sample names encode anneal temperature); alignment routines (piezo + hexapod variants).
3b. **Detectors:** pil2M (SAXS), pil900KW (WAXS, added when `waxs_angle >= 15`).
4. **Pattern: LEGACY.** Deeply nested loops (sample x waxs x incident-angle x time-point) all terminating in `bp.count`; global `sample_id`; humidity read into filename string.
   ```python
   for nn in range(Nmax):                  # time index (kinetics)
     for sample, x_hexa, th_hexa, y_hexa in zip(...):
       for i, th in enumerate(th_meas):    # incident angles
         humidity = "%3.2f" % readHumidity(verbosity=0)
         sample_id(user_name='Insitu', sample_name=sample_name)
         yield from bp.count(dets, num=1)
   ```
5. **Notable hardware:** humidity chamber via Moxa wet/dry mass-flow controllers (`moxa_in.ch1_sp`, `setWetFlow/setDryFlow`); hexapod GI alignment (`stage.x/y/th`); aligned positions logged to external `aligned_positions.txt`; adaptive sleep schedule (`time_hr`/`time_sleep_sec`) for log-spaced kinetics; sparse x-offset jitter every N frames to mitigate beam damage.
6. **Intent:** In-situ humidity-swelling kinetics of block-copolymer thin films by GISAXS/GIWAXS over a multi-sample bar, with periodic re-sampling over hours.

---

## 3. 30-user-ECD-3dprinterLutz.py
1. **Size / count:** ~20 KB, 662 lines, ~14 functions (module-level `names`/`height`/`waxs_arc` globals).
2. **User/group:** Lutz group / ECD = electrochemical-deposition 3D-printing ("ED"); shares Headrick/Hegmann printer codebase lineage.
3. **Use-cases (tags):** **3D-printing in-situ** time-resolved SWAXS triggered by the printer (`track_printer`, `track_printer_timeRes`); microfocus **raster mapping** of a 39-sample bar (`sample_bar`, per-sample `rel_scan` over `piezo.y`); ex-situ multi-sample WAXS-arc scans; **temperature ramp** (`ex_situ_temp`, Lakeshore `ls.ch1_sp`, 30->170 C); nozzle/height alignment; beam-damage study.
3b. **Detectors:** pil300KW (WAXS) + pil2M (SAXS).
4. **Pattern: LEGACY.** External-trigger `while` loop + nested for over waxs_arc/samples; `bp.rel_scan`/`bp.scan`/`bp.count`; global `sample_id`.
   ```python
   trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", name="trigger_signal")
   while monitor_pv.get() == 1:
       if trigger_signal_pv.get() == 1:
           experimental_adjustement()                 # sets sample_id
           yield from data_acquisition(exp_t, meas_t) # -> bp.count(det, num=1)
   ```
5. **Notable hardware:** external printer handshake via EpicsSignals `XF:11ID-CT{M1}bi2/3/4` (monitor / ready / trigger); `SMI_Beamline()` mode switching + `setDirectBeamROI`; hexapod (`stage.y/x`) film/nozzle alignment; `height` offset from nozzle baked into filenames; Lakeshore for ex-situ thermal map.
6. **Intent:** Operando WAXS/SAXS during electrochemical/extrusion 3D printing, hardware-triggered per printed layer, plus ex-situ bar mapping and thermal annealing.

---

## 4. 30-user-Hegmann.py
1. **Size / count:** ~16 KB, 532 lines, ~14 functions (module-level printer globals).
2. **User/group:** Hegmann group (Patryk "MP" / "EH"); same printer infrastructure family.
3. **Use-cases (tags):** **microfocus SAXS raster mapping** (`saxs_hegmann_gird/grid2/grid_2021_2` via `bp.rel_grid_scan`, snake toggle); **3D-printer in-situ** trigger-synced (`track_printer_hegmann`); height/filament profiling (`height_scan`, `scan_fil_height`); ex-situ multi-sample bar (`ex_situ_hegmann`, `ex_situ_xscan_hegmann`) with WAXS-arc scans; nozzle/substrate alignment.
3b. **Detectors:** pil2M (SAXS, microbeam ~3.2 m), pil300KW (WAXS) for ex-situ.
4. **Pattern: LEGACY.** Per-sample `rel_grid_scan` inside a for loop; global `sample_id`; hard-coded x/y/z + per-sample `x_range`/`y_range` lists.
   ```python
   for x, y, sample, x_r, y_r in zip(xlocs, ylocs, names, x_range, y_range):
       yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y)
       sample_id(user_name=user, sample_name=sample_name)
       yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)  # 0=not-snake
   ```
5. **Notable hardware:** piezo x/y raster (2D maps up to ~250x100 pts); hexapod (`stage.y/x/th`) for height; printer EpicsSignal handshake (`XF:11ID-CT{M1}bi*`); GV7 gate valve; `SMI_Beamline()` alignment modes; `np.int` (legacy NumPy) usage.
6. **Intent:** High-resolution microfocus SAXS mapping of printed/molded polymer structures plus operando printing, with ex-situ orientation surveys.

---

## 5. 30-user-Headrick.py
1. **Size / count:** ~15 KB, 476 lines, ~14 functions.
2. **User/group:** Headrick group; bylines "JW", "RH" (Hegmann?), "AD" (proposal GU-308850).
3. **Use-cases (tags):** **GIWAXS in-situ heating / roll-to-roll printing kinetics** (`giwaxs_insitu_heating`, `giwaxs_insitu_roll`, `..._cooling`, single-frame long-exposure time series); multi-sample GIWAXS bar (`giwaxs_headrick_2022_1/2`, per-sample auto-align); beam-damage long counts (`run_BD`, num=300); WAXS-arc full scans (`run_fullgiwaxs`).
3b. **Detectors:** pil900KW (WAXS) primary; pil2M (SAXS) when WAXS arc retracted; pil300KW + ROI channels (`pil300kwroi2/3/4`) for beam-damage kinetics.
4. **Pattern: LEGACY (notably old).** Direct `pil2M.cam.file_path.put(...)` to ramdisk/GPFS paths (pre-Tiled), `ls.ch1_read.value` into filename, `bp.count`/`bp.scan`, global `sample_id`.
   ```python
   pil2M.cam.file_path.put(f"/ramdisk/images/users/2019_3/304549_Headrick/1M/%s" % sample)
   temp = ls.ch1_read.value
   sample_id(user_name=name, sample_name=name_fmt.format(samp=sample, temperature=temp))
   yield from bp.count([pil2M, pil300KW], num=1)
   ```
5. **Notable hardware:** Lakeshore temperature (`ls.ch1_read`/`ls.ch1_sp`); hexapod GI alignment (`alignement_gisaxs_hex`); roi-readout WAXS for time-resolved kinetics; long single-exposure "roll" measurements (continuous casting/printing).
6. **Intent:** In-situ GIWAXS of polymer crystallization during heating/cooling and roll-to-roll/solution casting, plus ex-situ multi-sample orientation mapping.

---

## 6. 30-user-Sprunt.py
1. **Size / count:** ~13 KB, 381 lines, ~6 functions.
2. **User/group:** Sprunt group ("GF"-aligned tender work; proposal RT12127A); bylines reference "cherun".
3. **Use-cases (tags):** **tender S-edge resonant WAXS + NEXAFS** (`waxs_S_edge_cherun`, `nexafs_S_edge_cherun`, ~2450-2510 eV fine grid, y-drift to spread beam damage); **in-situ temperature** ramping with **Instec** stage, both hard-xray (`instec_insitu_hard_xray`) and tender (`instec_insitu_tender_xray`); single-shot temperature snapshots (`single_scan_instec_insitu_*`).
3b. **Detectors:** pil300KW (WAXS, tender) + pil2M (SAXS).
4. **Pattern: LEGACY.** Temperature/energy/waxs nested loops -> `bp.count`; global `sample_id`; T read (`ls.input_A/C.value`) into filename; large commented-out sample-bar blocks.
   ```python
   for i_t, t in enumerate(temperatures):
       yield from ls.output3.mv_temp(t + 273.15)
       while abs(temp - t_kelvin) > 0.25: yield from bps.sleep(10); temp = ls.input_A.value
       for wa in wa_arc:
           yield from bps.mv(waxs, wa); sample_id(...); yield from bp.count(dets, num=1)
   ```
5. **Notable hardware:** **Instec** hot/cold stage via Lakeshore `ls.output3.mv_temp` + `ls.input_A/C` (Kelvin, converted to C in filenames); energy mono for tender edge; `waxs.arc` direction-aware ordering to save motion; y-creep (`mvr(stage.y, 0.025)`) between temperatures to avoid radiation damage.
6. **Intent:** Resonant tender-energy S-edge WAXS/NEXAFS combined with Instec-controlled thermal ramps to follow temperature-dependent molecular orientation/ordering.

---

## 7. 30-user-Reuther.py
1. **Size / count:** ~9.5 KB, 270 lines, ~5 functions.
2. **User/group:** Reuther group ("JR"; proposal 310643).
3. **Use-cases (tags):** **transmission SWAXS multi-position averaging** of capillaries/films (`run_swaxs_reuther_*_cap/slide`, x/y offset grids per sample for statistics); **hard-xray GIWAXS** on a Lakeshore heating bar (no active heating) (`reuter_giwaxs_2023_1`); GI alignment helpers (`zihan_giwaxs_alignment`, theta-rocking).
3b. **Detectors:** pil900KW (WAXS) + pil2M (SAXS, enabled only when `waxs.arc.position >= 15`).
4. **Pattern: LEGACY.** waxs x sample x y_off x x_off nested loops -> `bp.count`; `sample_id` global; metadata (energy, sdd, waxs) assembled into filename string each point.
   ```python
   for wa in waxs_arc:
       yield from bps.mv(waxs, wa)
       dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
       for name, x, y, hy in zip(names, piezo_x, piezo_y, hexa_y):
           for yy, y_of in enumerate(y_off):
               for xx, x_of in enumerate(x_off):
                   sample_id(user_name=user, sample_name=sample_name); yield from bp.count(dets)
   ```
5. **Notable hardware:** piezo x/y + hexapod y (`stage.y`); WAXS-arc-gated detector selection; per-sample multi-spot averaging (radiation-sensitive solution/biological samples implied by mg/ml, NATIVE, water-blank names); `RE.md['SAF_number']` set at module scope (legacy global metadata).
6. **Intent:** Statistical transmission SAXS/WAXS of (likely protein/solution) capillaries and films via multi-spot averaging, with optional hard-xray GIWAXS on a heatable bar.

---

## 8. 30-Tenney.py
1. **Size / count:** ~7 KB, 181 lines, 4 functions.
2. **User/group:** Tenney / Harward collaboration ("ST", "HarvTempRe"/"HarvPoly"/"HarvMicro").
3. **Use-cases (tags):** transmission SWAXS line/grid scans on a sample bar; **temperature ramping/annealing** (Lakeshore `ls.ch1_sp`, 25->150 C with soak); **microfocus** x-offset raster + y-`rel_scan` mapping (`run_harv_micro`); isothermal **time-series/kinetics** (`run_harv_poly`, 600x `bp.count` with 30 s spacing at fixed T).
3b. **Detectors:** **rayonix (MAXS)**, pil300KW (WAXS), pil2M (SAXS), plus `ls.ch1_read` and `xbpm3.sumY` recorded as "detectors" in the list.
4. **Pattern: LEGACY (zero modern constructs).** Temperature x sample x offset nested loops -> `bp.count` / `bp.scan(waxs,...)` / `bp.rel_scan(piezo.y,...)`; global `sample_id`; `ls.ch1_read.value` into filename.
   ```python
   for i_t, t in enumerate(temperatures):
       yield from bps.mv(ls.ch1_sp, t)
       for x, y, s in zip(x_list, y_list, samples):
           for i_o, o in enumerate(x_offset):
               sample_id(user_name=name, sample_name=sample_name)
               yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable hardware:** **rayonix** large-area MAXS detector in the det list (distinctive); Lakeshore setpoint ramp with `bps.sleep(600)` soak; piezo x microfocus offsets (e.g. -704..704 um); `ls.ch1_read`/`xbpm3.sumY` as in-stream scalars (a step toward modern, but still legacy filename use).
6. **Intent:** Temperature-resolved transmission SAXS/WAXS/MAXS of polymer films/blends with microfocus mapping and isothermal crystallization kinetics.

---

## 9. 30-user_Reven.py
1. **Size / count:** ~6 KB, 166 lines, 3 functions (all `temp_series` variants).
2. **User/group:** Reven group (transmission SAXS thermal; mirrors Guillaume's `temp_series`).
3. **Use-cases (tags):** **temperature ramping/annealing + in-situ thermal time-series** via Linkam (`LThermal`); plain single-position (`temp_series`), multi-position (`temp_series_withpos`), and **x/y grid x temperature** (`temp_series_grid`) variants.
3b. **Detectors:** pil2M (SAXS) default; extensible via `dets` arg.
4. **Pattern: LEGACY (with a partial-modern tell).** Uses `RE.md["sample_name"]='{target_file_name}'` + a `target_file_name` Signal fed into `bp.count(dets + [s])`, but still per-temperature `bp.count` loop and global `RE.md` mutation (no `run_decorator`).
   ```python
   s = Signal(name='target_file_name', value='')
   RE.md["sample_name"] = '{target_file_name}'
   for i, temp in enumerate(temps):
       LThermal.setTemperature(temp)
       while abs(LThermal.temperature()-temp) > 0.2: yield from bps.sleep(10)
       s.put(sample_name); yield from bp.count(dets + [s])
   ```
5. **Notable hardware:** **Linkam** (`LThermal.setTemperature/temperature/on/off`); equilibration wait loop (0.2 deg tol, double soak on first point); `pil2M_pos.z` read for SDD; filename sanitized via `str.translate`; stage x/y for grid.
6. **Intent:** In-situ transmission SAXS/WAXS during Linkam thermal cycling (cooling ramps), with optional spatial-grid sampling at each temperature.

---

## 10. 30-user-3dprinterLutz.py
1. **Size / count:** ~5 KB, 176 lines, ~8 functions (module-level printer globals).
2. **User/group:** Lutz 3D-printer ("EH"); parent of the ECD-3dprinterLutz script.
3. **Use-cases (tags):** **3D-printing in-situ** WAXS triggered by the printer (`track_printer`); film/nozzle height alignment (`sample_alignment`, `nozzle_alignment`, `align_height_hexa`, `align_x_hexa`); beam-damage study; filament height profiling.
3b. **Detectors:** pil300KW (WAXS) only (`det = [pil300KW]`).
4. **Pattern: LEGACY.** External-trigger `while` loop calling `data_acquisition -> bp.count(det, num=1)`; global `sample_id`; `bp.rel_scan` for alignment.
   ```python
   while monitor_pv.get() == 1:
       if trigger_signal_pv.get() == 1:
           trigger_count += 1; experimental_adjustement()
           yield from data_acquisition(exp_t, meas_t)   # -> bp.count(det, num=1)
       yield from bps.sleep(0.5)
   ```
5. **Notable hardware:** printer EpicsSignal handshake (`XF:11ID-CT{M1}bi2/3/4`); `SMI_Beamline().modeAlignment/modeMeasurement`, `setDirectBeamROI`; hexapod `stage.y/x` for nozzle->film-interface alignment with `height` offset; GV7 gate valve; `np.int` legacy.
6. **Intent:** Operando WAXS during polymer/ink 3D printing, hardware-synchronized to nozzle passes, with hexapod height tracking of the print.

---

## 11. 30-user-Giri.py
1. **Size / count:** ~3.5 KB, 121 lines, 1 plan function (`giwaxs_giri_2021_3`).
2. **User/group:** Giri group ("GG"), 2021_3 cycle.
3. **Use-cases (tags):** **GIWAXS multi-sample bar** with per-sample auto-alignment; single incident angle (0.15 deg), single WAXS arc (9 deg); hard x-ray (16.1 keV).
3b. **Detectors:** pil900KW (WAXS) only.
4. **Pattern: LEGACY.** sample x waxs x incident-angle nested loops -> `bp.count(dets, num=1)`; global `sample_id`; hard-coded piezo x/y/z + hexapod x lists with length asserts.
   ```python
   for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
       yield from bps.mv(piezo.x, xs); ...; yield from alignement_gisaxs(angle=0.1)
       for wa in waxs_arc:
           for i, an in enumerate(angle):
               sample_id(user_name=user, sample_name=sample_name); yield from bp.count(dets, num=1)
   ```
5. **Notable hardware:** piezo (x/y/z/th) + hexapod (`stage.x`) GI stack; `alignement_gisaxs` direct+reflected-beam routine; minimal/templated structure (effectively the canonical legacy GIWAXS-bar template).
6. **Intent:** Hard-xray GIWAXS survey of a thin-film sample series on a bar at fixed incident angle.

---

## 12. 30-user-Pollozi.py
1. **Size / count:** ~2.5 KB, 65 lines, 1 plan function (`saxs_waxs_Shejla`).
2. **User/group:** Pollozi group ("GF"-assisted; sample "Shejla"); hydration study (DHH/HHH, rehyd/wet/dry).
3. **Use-cases (tags):** transmission **SAXS+WAXS multi-sample with 3x3 micro-raster averaging** (`list_scan` meshgrid over piezo.x/y); WAXS-arc series (0-26 deg, 5 pts); **humidity/hydration** sample states (rehyd vs dry vs wet, implied by names).
3b. **Detectors:** pil300KW (WAXS) + pil2M (SAXS).
4. **Pattern: LEGACY.** waxs x sample nested loops, with a 3x3 `bp.list_scan` meshgrid for spatial averaging; global `sample_id`.
   ```python
   for wa in waxs_arc:
       yield from bps.mv(waxs, wa)
       for name, xs, ys, zs in zip(names, x, y, z):
           yss, xss = np.meshgrid(...); 
           sample_id(user_name="GF", sample_name=sample_name)
           yield from bp.list_scan(dets, piezo.x, xss.tolist(), piezo.y, yss.tolist())
   ```
5. **Notable hardware:** piezo x/y/z + hexapod `stage.y/th`; meshgrid raster for radiation-sensitive (hydrated peptide/biological) sample averaging; large commented-out second sample set (dry/wet/blank-water bar).
6. **Intent:** Transmission SAXS/WAXS of hydrated/rehydrated peptide-assembly samples with multi-spot averaging across WAXS arc angles.

---

# BATCH SYNTHESIS

- **Distinct use-case archetypes observed (8):** (1) **multi-sample bar GISAXS/GIWAXS** with per-sample auto-alignment + incident-angle/WAXS-arc loops (Giri, Headrick, Reuther, ETsai, Guillaume); (2) **tender/resonant edge XAS + NEXAFS** energy sweeps (Guillaume = S/Cl/Sn/Zn/Pt/Co/Ru/Te/Fe/Br/Cr/Ag/Mo; Sprunt = S-edge), including fluorescence-yield (`amptek`) and pin_diode-vs-bpm I0 calibration; (3) **in-situ temperature ramping/annealing & isothermal kinetics** via Linkam (Reven, Guillaume), Instec (Sprunt), and Lakeshore (Tenney, ECD-Lutz, Headrick); (4) **microfocus raster/grid mapping** (Hegmann 2D `rel_grid_scan`, Tenney/ETsai/Pollozi x/y offset arrays); (5) **operando 3D-printing** with EPICS hardware-trigger handshake (3dprinterLutz, ECD-3dprinterLutz, Hegmann, Headrick roll-to-roll); (6) **humidity/RH in-situ swelling kinetics** (ETsai Moxa wet/dry flow + `readHumidity`); (7) **CD-SAXS / pole-figure / XRR** specialty reciprocal-space scans using the `prs` phi rotation stage (Guillaume); (8) **transmission solution/biological SAXS-WAXS with multi-spot averaging** (Reuther capillaries, Pollozi hydrated peptides).
- **Legacy is dominant:** 11 of 12 files are predominantly LEGACY — nested `for` loops, one `bp.count`/`bp.scan`/`bp.rel_scan`/`bp.list_scan`/`rel_grid_scan` run per data point, global `sample_id(user_name=, sample_name=)` filename state, and context (T, humidity, xbpm, energy, sdd) read via `.value`/`.get()` and baked into the filename string rather than recorded in-stream.
- **Only Guillaume.py is MIXED**, and uniquely shows a live migration: 2020–2024 plans are legacy, while 2025_3-era plans (`giwaxs_*_2025_3`, `sevralai_giwaxs_*_edge_2025_3`) adopt the modern `@bpp.stage_decorator`/`@bpp.run_decorator(md=...)` + `inner()` + `trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, ...] + [target_file_name_signal])` idiom — matching the `tender.py`/`tranmission.py` templates.
- **Transitional half-step:** Reven (and Guillaume's `temp_series`) introduce a `target_file_name` ophyd `Signal` and read it in `bp.count(dets + [s])`, but still mutate global `RE.md["sample_name"]` and loop per-point — a partial move toward stream-captured metadata without the single-run decorator.
- **Detector usage:** pil2M (SAXS) + pil900KW/pil300KW (WAXS) are near-universal, with the recurring WAXS-arc-gated rule `dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]`; `rayonix` (MAXS) appears only in Tenney; `amptek` (fluorescence) and `pin_diode` only in Guillaume; xbpm2/xbpm3 are pervasive as I0 references.
- **Hardware vocabulary:** piezo (x/y/z/th) fine stage + hexapod (`stage.x/y/th`) coarse stage form the GI "double-stack"; Guillaume adds long-range `smaract` x and the `prs` phi rotation stage; GV7 SAXS gate-valve interlock and `SMI_Beamline()` modeAlignment/modeMeasurement + ROI setup recur throughout; attenuator banks (att2_5/6/9) gate flux on edges.
- **External triggering & environment control** appear via raw `EpicsSignal("XF:11ID-CT{M1}bi*")` printer handshakes (all 3D-printer scripts) and Moxa mass-flow / Lakeshore / Linkam / Instec devices — environment is driven imperatively (`.setTemperature`, `mv_temp`, `setWetFlow`) and polled, not orchestrated as baseline/monitored streams.
- **Common legacy anti-patterns to flag for migration:** hard-coded coordinate/sample lists in plan bodies (every file; huge commented-out alternates in ECD-Lutz, Hegmann, Sprunt, ETsai); module-level `RE.md` mutation (Reuther `SAF_number`, Reven `sample_name`); direct `pilXX.cam.file_path.put(...)` to ramdisk/GPFS (Headrick, pre-Tiled); and deprecated `np.int` (3dprinterLutz, Hegmann, ECD-Lutz).
- **Radiation-damage mitigation is a cross-cutting motif** implemented ad hoc: per-energy x-stepping (`x - counter*xstep`), y-creep between temperatures, multi-spot averaging grids, and xbpm flux gating — strong candidates for standardized helper plans.

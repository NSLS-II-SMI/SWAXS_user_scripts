# Legacy Bluesky/Ophyd Plan Analysis — Batch 08 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 16 legacy
user macro files. Detector legend: `pil2M` = SAXS (Pilatus 1M/2M), `pil900KW`/`pil300KW`
= WAXS (arc-mounted in-vacuum, `pil300KW` is the older WAXS), `rayonix` = MAXS,
`pdcurrent*`/`pin_diode` = transmission diodes, `xbpm2`/`xbpm3` = beam-position
monitors, `OAV(_writing)` = on-axis optical camera (written into the run for
microfocus/printing), `ls` (Lakeshore) / `LThermal` (Linkam) = temperature
controllers, `syringe_pu` = syringe pump, `moxa`/`readHumidity` = RH MFC system.
Goniometry: `piezo.*` (fast nano-stage x/y/z/th), `stage.*` (coarse hexapod),
`prs`/`stage.phi` (in-plane rotation, slow), `waxs`/`waxs.arc` (slow in-vacuum WAXS
arc), `energy` (DCM, tender S/Cl/Ca/Fe edges).

Pattern legend: **LEGACY** = nested `for` loops, each iteration calls
`bp.count`/`bp.scan`/`bp.rel_grid_scan` → one Bluesky run per data point; filenames
via global mutable `sample_id(...)` / `RE.md['sample_name']`; context (T, BPM, energy,
position) read via `.value`/`.get()` and baked into the filename string.
**MODERN** = `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)` around an
`inner()` generator with `bps.trigger_and_read(dets + [signals])` and a
`target_file_name` Signal. **MIXED** = both present (documented migration in progress).

---

## 1. 30-user-Patryk.py
1. **Size / plans:** ~129 KB, ~68 `def`s (largest file in batch; campaign-named plans 2023→2026). **Beamline-scientist file — reusable infra, see flag below.**
2. **User/group:** Patryk (`PW`/`BP`); beamline scientist running/ servicing many guest campaigns (Paren, Das, Andrew, Dominik, Ray, Slk, Par). Soft-matter / ionomer / tender-resonant program.
3. **Use-cases:** transmission **SWAXS** (multi-position, capillaries, multi-SAXS-distance), **tender S-edge NEXAFS + resonant SWAXS** (`run_*_Paren_tender_nexafs`, fine 0.25 eV grid 2470–2480), **GISAXS/GIWAXS** (`grazing`, double-stack holder, incident-angle series), **raster microfocus mapping** (`overnight_mapping`/`overday_mapping`, 290×29-pt `rel_grid_scan`), **temperature ramp/annealing** (Linkam `run_Linkam_temp_run`, `run_Paren_temperature_hard`, `go_to_temp`), **in-situ time series/kinetics** (`insitu_*mapping_Das`, frame loops), **RH/humidity** (`rh`, `take_bkg N2`), **flat-field** detector calibration (`run_Paren_flatfield*`).
   - **Detectors:** conditional `[pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]`; `OAV_writing` appended for mapping/printing; `xbpm2/3` read for energy-stability gating.
4. **Acquisition pattern: LEGACY (uniform, but well-factored).** Per-point `bp.count` inside nested sample×waxs×energy loops; metadata via the helper `get_more_md()`/`get_scan_md()` that injects temp+xbpm into the filename; `RE.md['tstamp']`/`RE.md['misaligned_samples']` global state.
   ```python
   for i, nrg in enumerate(energies):
       yield from bps.mv(energy, nrg); yield from bps.sleep(2)
       if xbpm2.sumX.get() < 50: ...                 # energy re-seek
       sample_name = f'{name}{get_more_md()}_loc{loc}'
       sample_id(user_name=user, sample_name=sample_name)
       yield from bp.count(dets)
   ```
   - Mapping plans are slightly better (one `rel_grid_scan` run per sample/waxs) but still use global `sample_id`.
5. **Notable techniques/hardware:** xbpm energy-stability re-seek loop (`if xbpm2.sumX.get()<50: re-move energy`); `get_more_md`/`get_scan_md` filename-metadata helpers (reused across many SMI files); `OAV_writing` snapshots; double-stack GI holder + `alignement_gisaxs_doblestack`; per-energy flat-field runs; `go_to_temp` Linkam helper; assertion-guarded coordinate lists.
6. **Intent:** Master beamline-scientist macro library for tender-resonant SWAXS/NEXAFS + GI + microfocus mapping + Linkam/RH in-situ on ionomers/soft matter; canonical legacy per-point engine that the modern run-per-sample template targets.
   - **>> INFRA FLAG:** `get_more_md()` / `get_scan_md()` (filename metadata builders), the xbpm re-seek idiom, the assert-guarded `names/piezo_x/piezo_y/piezo_z` coordinate-table convention, and `go_to_temp` are reusable utilities replicated (often verbatim) across the whole user-file corpus. Prime candidates to centralize into shared infra / replace with `md={}` + baseline devices.

---

## 2. 30-user-Cai.py
1. **Size / plans:** ~89 KB, ~40 `def`s (2020→2024 accretion).
2. **User/group:** Cai / Christine Cai (`LC`,`DR`); polymer / fiber / textile / additive-manufacturing soft-matter.
3. **Use-cases:** **in-situ 3D-printing SWAXS** (`cai_printing*`, continuous `stage.x` line-scans synced to nozzle, time-evolution rasters), **in-situ tensile** (`cai_tensile_continous_hard_*` on Linkam **MFS** tensile stage, continuous stretch), **temperature ramp/annealing** (`cai_*temperature_scan_*` via Lakeshore `ls.output1.mv_temp` + equilibration), **GIWAXS/GISWAXS** (`gisaxs_cai`, `run_giwaxs_cai*`), **transmission SAXS/WAXS** (capillaries, fibers, textiles), **microfocus mapping** (`mapping_saxs_Cai`).
   - **Detectors:** `pil900KW`+`pil2M` (+`OAV_writing` for printing); conditional SAXS-add when `waxs.arc>15`.
4. **Acquisition pattern: LEGACY.** Two sub-styles: (a) classic per-point `bp.count` for static/temperature/GI, (b) **continuous-acquisition** for printing/tensile that re-purposes `bp.scan` over `stage.x`/`stage.y` and manually sets `cam.acquire_period`/`num_images` for fly-like fast frames.
   ```python
   # in-situ printing: fast line scan, period/num_images tuned for streaming
   pil2M.cam.acquire_period.set(...); pil2M.cam.num_images.set(2)
   yield from bp.scan([pil2M, pil900KW, OAV_writing], stage.x,
                      cur_x, cur_x - total_points*xstep, total_points)
   ```
   ```python
   yield from ls.output1.mv_temp(t_kelvin)
   while abs(ls.input_A.get() - t_kelvin) > ...: yield from bps.sleep(...)
   temp_degC = ls.input_A.get() - 273.15           # T into filename
   ```
5. **Notable techniques/hardware:** Linkam **MFS** tensile + Lakeshore `ls` thermal; `OAV_writing` printer camera; manual `acquire_period`/`num_images` continuous streaming; `give_sample_name`/`get_scan_md` filename helpers; `atten_move_in/out`, `engage_detectors`; serpentine (boustrophedon) raster (`np.mod(yy,2)`).
6. **Intent:** Additive-manufacturing + mechanical (tensile) + thermal in-situ SWAXS on polymers/fibers; LEGACY throughout with a notable hand-rolled continuous-acquisition idiom for printing/stretch kinetics.

---

## 3. 30-user-Gomez.py
1. **Size / plans:** ~57 KB, ~30 `def`s (2024-era legacy core + a fully migrated 2026 block).
2. **User/group:** Gomez (`NR`,`FN`,`AO`; Louis/Agatha sub-projects); tender-resonant thin-film & solution soft-matter.
3. **Use-cases:** **tender multi-edge NEXAFS + resonant SWAXS** (Fe, Ag, **Ca**, P, S, **Cl** edges), **GISAXS/GIWAXS** (`GISAXS_Ca_edge`, `giwaxs_2026_1` incident-angle×waxs series with double-stack alignment), **transmission SAXS** (capillaries `saxs_cap_2026_1`), **humidity/RH SAXS** (`saxs_humidity_2026_1`, dry/wet flow + `swaxs_humidity_Cl_edge`), multi-sample bar.
   - **Detectors:** `pil900KW`+`pil2M` conditional; records `energy, waxs, xbpm2, xbpm3, att2_9, piezo/stage axes` in the modern streams.
4. **Acquisition pattern: MIXED → clearest "before/after" in this batch.**
   - LEGACY core (lines 1–1060, e.g. `SAXS_Ca_edge_dry*`, `gomez_S_edge_new`): per-point `bp.count`, bpm/energy into filename via `name_fmt`.
   - **MODERN (2026_1 block, lines ~1062–1626):** `target_file_name` Signal + decorated single run with `trigger_and_read` recording context devices — textbook modern SMI form:
     ```python
     s = Signal(name='target_file_name', value='')
     @bpp.stage_decorator(dets)
     @bpp.run_decorator(md={'sample_name': '{target_file_name}'})
     def inner():
         ... s.put(sample_name)
         yield from bps.trigger_and_read(
             dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
     yield from inner()
     ```
   - Applied across `nexafs_Caedge_2026_1`, `swaxs_Cl_edge_2026_1`, `saxs_humidity_2026_1`, `saxs_cap_2026_1`, `swaxs_humidity_Cl_edge_2026_1`, `giwaxs_2026_1`.
5. **Notable techniques/hardware:** double-stack GI alignment (`alignement_gisaxs_doblestack`); RH dry/wet flow; per-edge fine energy grids; `att2_9` recorded as device in modern streams (attenuator state captured, not in filename).
6. **Intent:** Tender multi-edge resonant SWAXS/NEXAFS + GI + RH on soft-matter films; **reference example of the completed legacy→modern migration** (Signal + run/stage decorators + trigger_and_read).

---

## 4. 30-user-Karen.py
1. **Size / plans:** ~42 KB, ~40 `def`s (many same-named `continous_run_prealigned_positions_2025_2` overloads = per-cell copies).
2. **User/group:** Karen / Karen Chen-Wiegart collaboration (operando battery/corrosion); also Chen-Wiegart & Dean grazing sub-projects.
3. **Use-cases:** **operando / in-situ electrochemistry time series** (`*_op_*_echem`, frames up to 5000, long `wait` between scans — battery/Na-Cu corrosion cells), **GISAXS/GIWAXS** (`grazing_Chen_Wiegart_2023_3`, `grazing_Dean_2025_3`, prealigned variants), **multi-ROI prealigned mapping** with per-region incident-angle fans, **transmission SWAXS** snapshots.
   - **Detectors:** `pil900KW` (primary operando), `pil2M` conditional (`waxs.arc<15`); `pil2M.beamstop.x_rod` alignment-mode control.
4. **Acquisition pattern: LEGACY + RE.md alignment look-up-table anti-pattern.** Time-loop × ROI × x-offset × incident-angle nested loops, per-point `bp.count`; alignment coords and sample name stashed in `RE.md` (LUT) and mutated mid-plan:
   ```python
   alignment = RE.md['alignment_LUT']            # {'0': {'x':...,'y':...,'th':...}}
   for i in range(frames):
       for key, value in alignment.items():
           yield from bps.mv(piezo.x, value['x'], piezo.y, value['y'], piezo.th, value['th'])
           for ai in ai_off:
               name_sample(sname, tstamp)
               RE.md['sample_name'] = RE.md['sample_name'] + f'_ai_{ai:.3f}'
               yield from bp.count([pil900KW])
   ```
5. **Notable techniques/hardware:** persistent alignment LUT in `RE.md`; `tstamp`-based elapsed-time naming for operando kinetics; `alignment_on/off`, `atten_move_in/out`, beamstop-rod mode switching; nth-frame full-SWAXS interleave (`saxs_frame` cadence).
6. **Intent:** Operando electrochemistry (battery/corrosion) GISAXS/GIWAXS time-series over prealigned cell ROIs; LEGACY with heavy `RE.md` global state for alignment + naming.

---

## 5. 30-user-dudenas.py
1. **Size / plans:** ~33 KB, 11 `def`s.
2. **User/group:** dudenas / Pete Dudenas (`GF`); also Lee sub-run. Tender-resonant thin-film GIWAXS.
3. **Use-cases:** **tender S-edge GIWAXS / resonant GIWAXS** (`giwaxs_S_edge_Pete*`, fine S-edge grid 2473–2481), **S-edge NEXAFS** (`nexafs_S_edge_Pete`), **incident-angle GIWAXS** (`giwaxs_ai_S_edge`), **multi-PRS/azimuthal GIWAXS** (`giwaxs_multiprsangles`, 0°/90° film orientations), **vertical-geometry GIWAXS** (`giwaxs_vert_S_edge`).
   - **Detectors:** `pil2M`+`pil300KW` (older WAXS).
4. **Acquisition pattern: LEGACY.** sample×waxs×incident-angle×energy nested loops, per-point `bp.count`, `att2_9` toggled by `mv("Insert")`, bpm into filename, fresh-spot anti-damage x-stepping (`piezo.x, xs + k*400`):
   ```python
   for i, wa in enumerate(waxs_arc):
       yield from bps.mv(waxs, wa)
       for k, ais in enumerate(ai_list):
           yield from bps.mv(piezo.th, ai0 + ais); yield from bps.mv(piezo.x, xs + k*400)
           for e in energies:
               yield from bps.mv(energy, e); bpm = xbpm2.sumX.value
               sample_id(user_name="GF", sample_name=name_fmt.format(...))
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** custom `alignement_special` per sample; `att2_9` attenuator insert; piezo+hexapod GI geometry; energy descent return-sequence after each block (2490→2470→2450); 0°/90° azimuthal pairs.
6. **Intent:** Per-cycle tender resonant S-edge GIWAXS + NEXAFS on thin films; textbook legacy multi-sample resonant-GI loop with fresh-spot rastering.

---

## 6. 30-user-Wenkai.py
1. **Size / plans:** ~25 KB, 13 `def`s.
2. **User/group:** Wenkai / Wenkai Chen (`GF`); also Lee sub-run. Conjugated-polymer / mechanical-deformation tender program.
3. **Use-cases:** **in-situ tensile under tender beam** (`wenkai_*tensile_tender_*`, continuous incremental `stage.y` stretch with elapsed-time naming), **S-edge GIWAXS** (`giwaxs_S_edge_wenkai`), **S-edge NEXAFS** (`nexafs_S_edge_wenkai`, `S_edge_measurments_2022_3`), **hard-Xray SWAXS** (`hardxray_wenkai*`), tensile at hard energy (`wenkai_saxs_waxs_tensile_hard`).
   - **Detectors:** `pil300KW`+`pil2M` (tender SWAXS/tensile).
4. **Acquisition pattern: LEGACY.** Tight `for i in range(N)` stretch loops; each step nudges `stage.y` then per-waxs `bp.count`; elapsed time `(t1-t0)` written into the filename for kinetics:
   ```python
   for i in range(60):
       yield from bps.mvr(stage.y, 0.03)            # incremental stretch
       for wax in wa:
           yield from bps.mv(waxs, wax)
           sample_name = name_fmt.format(sample=names, time="%1.1f"%(t1-t0), i="%3.3d"%i, wa=...)
           sample_id(user_name="GF", sample_name=sample_name)
           yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** incremental-strain `mvr(stage.y)` as a pseudo-tensile actuator; arc-direction-aware waxs ordering (`if waxs.arc>5: reverse`); fixed tender energies hard-coded in filename (2455/2484.25 eV); long loops (up to 1000 frames).
6. **Intent:** In-situ tensile-deformation tender SWAXS + S-edge GIWAXS/NEXAFS on stretched polymer films; canonical legacy time/strain-into-filename kinetics.

---

## 7. 30-user-Netzke.py
1. **Size / plans:** ~17 KB, ~7 active `def`s (+ several commented-out variants).
2. **User/group:** Netzke (`SN`); also `LC`. Ferroelectric / oxide thin-film (HfO2/HZO, TiN) GISAXS/GIWAXS.
3. **Use-cases:** **GIWAXS/GISAXS with azimuthal (phi/`prs`) rotation** (`gisaxsnetzke*`, phi = 0/-20/-40/-60 with per-phi `ai` offsets), **incident-angle series**, **2-energy resonant pair** (9540/9580 eV — near a metal edge), per-phi **re-alignment** (`gisaxsnetzke3`).
   - **Detectors:** `pil300KW` (+`pil2M` conditional).
4. **Acquisition pattern: LEGACY (deeply nested).** sample×waxs×angle×phi×energy (5 nested loops), per-point `bp.count`; phi-dependent incident-angle corrections (`phi_aioff`); `alignement_gisaxs`/`_hex` called inside loop.
   ```python
   for j, wa in enumerate(waxs_arc):
       yield from bps.mv(waxs, wa)
       for an in angle:
           for ph, aioff in zip(phi, phi_aioff):
               yield from bps.mv(prs, ph); yield from bps.mv(stage.th, an + aioff)
               for en in energ:
                   yield from bps.mv(energy, en)
                   sample_id(user_name="SN", sample_name=name_fmt.format(...))
                   yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `prs` in-plane rotation for texture/pole-figure GIWAXS; per-phi alignment (`alignement_gisaxs_hex_short`); per-sample aligned `incident_angles`/`y_piezo_aligned` cached as module globals (`alignement_netzke`); frame averaging `num=4`.
6. **Intent:** Azimuthally-resolved (phi/pole-figure) GIWAXS/GISAXS on ferroelectric oxide thin films at a metal edge; deeply-nested legacy multi-sample/phi/energy loop.

---

## 8. 30-user-Mao.py
1. **Size / plans:** ~15 KB, ~30 `def`s (mostly thin helpers).
2. **User/group:** Mao (`YM`); also `XZ`. Wood / biomaterial humidity program.
3. **Use-cases:** **in-situ humidity (RH) cycling SWAXS** (`measure_one_humidity*`, MFC dry/wet flow, `set_humidity` chart, multi-hour cycling), **transmission SAXS/WAXS** of wood/crab/cellulose samples, **multi-WAXS-angle arc series** (`measure_waxs_multi_angles`), SAXS-distance presets (2/5/8 m).
   - **Detectors:** `pil900KW`+`pil300KW`+`pil2M` (uses `stage` not `piezo`); `pdcurrent1` pin-diode for flux.
4. **Acquisition pattern: LEGACY + nested-`RE()` anti-pattern.** Helpers call `RE(bp.count(...))` and `RE(bps.mv(...))` *inside* Python loops (plans are not pure generators end-to-end); humidity + scan_id read into filename; sample name in `RE.md['sample']`:
   ```python
   def _measure_one(t0, ks, dets, waxs_angle, ...):
       for k in ks:
           mov_sam(k); sample = RE.md["sample"]
           h = readHumidity(...); ...
           sample_id(user_name=user_name, sample_name=name_fmt.format(..., h=h, scan_id=RE.md["scan_id"]))
           RE(bp.count(dets, num=1))               # RE() inside a loop
   ```
5. **Notable techniques/hardware:** `set_humidity` MFC dry/wet flow look-up chart with documented equilibration times; `readHumidity` (V→%RH) into filename; SAXS-distance move helpers (`move_2m/5m/8m`); detailed waxs-angle→beam-center calibration comments; `mov_sam` dict-based bar navigation; SAXS-y stitching (`mvr(SAXS.y, 30*0.172)`).
6. **Intent:** Long-duration RH-cycling transmission SWAXS on wood/biomaterials; LEGACY with `RE()`-in-loop and humidity-into-filename (mixes orchestration and acquisition).

---

## 9. 30-user-Marino.py
1. **Size / plans:** ~14 KB, ~7 `def`s.
2. **User/group:** E. Marino (UPenn, Murray group; refs Chopra/Clark; `EM`,`EM2_Bar24`,`GVD`). Colloidal nanocrystal (PbS QD) superlattice program.
3. **Use-cases:** **in-situ kinetics / solvent-evaporation time series** (`insitu_EM`, `while number<9000` loop with `wait_time_sec`), **transmission SAXS** of QD assemblies, **multi-sample bar** (`exsitu_EM` over `sample_list`/`x_list`), **pin-diode flux normalization / attenuator tuning** (`test_pdcurrent`), optional WAXS.
   - **Detectors:** `pil2M` (SAXS) + `pdcurrent`/`pdcurrent1`/`pdcurrent2` (pin diodes); `pil300KW` for optional WAXS.
4. **Acquisition pattern: LEGACY.** Time/sample loops with per-point `bp.count`; before each frame, **attenuators inserted to read transmitted pin-diode current** (open `fs`, read `pdcurrent1`, close `fs`), then removed; T (Linkam `LThermal.temperature()`), pd current, elapsed time, x/y baked into filename:
   ```python
   fs.open(); yield from bps.sleep(0.3); pd_curr = pdcurrent1.value; fs.close()
   curr_tempC = LThermal.temperature()
   name_fmt = "{sample}_{number}_{temperature}C_t{time}_pd{pd_curr}_x{x}_y{y}{md}"
   sample_id(user_name="EM", sample_name=name_fmt.format(...))
   yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** fast-shutter-gated pin-diode flux read with attenuator ladder (`att1_9..12`, `Natt` redundancy); adaptive repeat count (`Nscan = ceil(pd_ref/pd)`) to equalize dose; `get_scan_md()` filename helper; Linkam `LThermal` temperature into filename.
6. **Intent:** In-situ solvent-evaporation / ex-situ multi-sample transmission SAXS on PbS QD superlattices with pin-diode flux normalization; LEGACY per-frame count + attenuator/diode bracketing.

---

## 10. 30-user-Tsai.py
1. **Size / plans:** ~12 KB, ~6 `def`s (heavy alignment/log commentary).
2. **User/group:** Tsai / Esther Tsai (`ET`,`ET2`,`ET3`,`AB2`); microbeam GISAXS/GIWAXS + tomography.
3. **Use-cases:** **microfocus GISAXS/GIWAXS raster mapping** (`run_scan_ET`, dense `piezo.x`×`piezo.z` grids ~30 µm step with small 50×2 µm beam), **GI-tomography** (`run_tomo_ET`, `prs` zig-zag rotation series `bp.scan(dets, prs, ...)` per x), **incident-angle GISAXS** (`run_gisaxsAngle_ET`), custom `alignment_gisaxs_stage` (hexapod-based).
   - **Detectors:** `pil900KW`/`pil300KW` (WAXS) + `pil2M` (SAXS) + `rayonix` (MAXS).
4. **Acquisition pattern: LEGACY.** x×z (or angle×waxs) nested loops, per-point `bp.count`; `stage.th`/`prs` into filename; tomography uses per-x `bp.scan(prs, ...)`:
   ```python
   for ii, x in enumerate(x_list):
       yield from bps.mv(piezo.x, x)
       for jj, z in enumerate(z_list):
           yield from bps.mv(piezo.z, z)
           sample_id(user_name="ET3", sample_name="{sample}_..._x{x}_z{z}_th{th}_{t}s".format(...))
           yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** very small beam (50×2 µm) → tilt-sensitive alignment notes; `prs` zig/zag rotation tomography (`prs_angles_zig`/`zag`); SMI_Beamline alignment helper; extensive inline alignment/position logbook.
6. **Intent:** Microfocus GISAXS/GIWAXS spatial mapping + GI-tomography (prs rotation) on thin films; LEGACY dense raster + per-x rotation scans.

---

## 11. 30-user-QChen_2024C3_GIX.py
1. **Size / plans:** ~7.7 KB, 3 `def`s (+ large alignment-coordinate header block).
2. **User/group:** QChen (`QChen`); grazing-incidence Au-on-Si self-assembly.
3. **Use-cases:** **in-situ GI-SWAXS time series** (`insitu_tgix_samples`, `while time<run_time` over sample bar with per-sample prealigned th/y), **GIWAXS/GISAXS multi-angle** (`run_gix_loop_wsaxs`, incident-angle fan + x-offset spread + waxs-angle loop), per-sample **GI alignment loop** (`align_gix_loop_samples` builds `Aligned_Dict`).
   - **Detectors:** `pil2M`+`pil900KW` via `get_dets(waxs_angle, mode)`.
4. **Acquisition pattern: LEGACY + nested-`RE()` in alignment.** Acquisition plans are generators (per-point `bp.count`), but alignment driver calls `RE(...)` inside a Python loop; uses an abstract motor handle `M` from `get_motor()` (piezo vs hexapod) and a prealigned-dict pattern; rich filename with x/y/z/det-distance/waxs/exposure:
   ```python
   Aligned_Dict = align_gix_loop_samples()          # RE() called inside
   while (time.time()-t0) < run_time:
       for k in ks:
           yield from bps.mv(M.x, x); yield from bps.mv(M.y, YH); yield from bps.mv(M.th, TH)
           for x_meas in x_pos_array:
               for th in th_meas:
                   sample_id(user_name=user_name, sample_name=name_fmt.format(...))
                   yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** prealigned-per-sample `Aligned_Dict` (th/y cache); abstract `M = get_motor()` (piezo/hexapod switch via `motor` global); optional OAV/hexapod camera snapshots (`save_ova`/`save_hex`); detailed AgBH/pin alignment coordinate header.
6. **Intent:** In-situ time-resolved GI-SWAXS over a prealigned sample bar (Au/Si assembly); LEGACY with prealignment-dict + `RE()`-in-loop alignment driver.

---

## 12. 30-user-chen_xpcs.py  ⟵ XPCS characterization
1. **Size / plans:** ~6.5 KB, 5 `def`s.
2. **User/group:** Chen (`Chen`,`WC`,`GF`); 2019/2020-era tender resonant + **XPCS** soft-matter (PSBMA polymer).
3. **Use-cases:** **XPCS at the S-edge** (`grid_scan_xpcs` — resonant tender XPCS, multi-position grid at fixed edge energies), **tender S-edge NEXAFS / resonant SAXS-WAXS** (`NEXAFS_SAXS_S_edge`, `grid_scan_static` energy sweep 2450–2500), **multi-sample S-edge WAXS bar** (`waxs_S_edge_chen_2020_3`, 21 samples).
   - **Detectors:** `pil2M` (SAXS — XPCS speckle) and `pil300KW` (WAXS); energies [2450,2472,2476,2490] = S K-edge resonant set.
4. **Acquisition pattern: LEGACY + bespoke XPCS burst OUTSIDE the document model.** The static/NEXAFS plans are ordinary per-point `bp.count`. The **XPCS plan bypasses `bp.count` entirely**: it sets the camera file path to a fast `/ramdisk/`, sets a short frame / long acquire-period via `det_exposure_time(0.03, 30)` (30 s burst of 0.03 s frames), fires `cam.acquire.put(1)`, and **busy-waits on the raw `Acquire` PV** until done — no Bluesky run/documents are generated for the XPCS series:
   ```python
   pil2M.cam.file_path.put(f"/ramdisk/images/users/2019_3/{folder}/1M/{name}_pos{i}")
   det_exposure_time(0.03, 30)                       # 0.03 s frame, 30 s acquire window
   pil2M.cam.acquire.put(1); yield from bps.sleep(5)
   pv = EpicsSignal("XF:12IDC-ES:2{Det:1M}cam1:Acquire", name="pv")
   while pv.get() == 1: yield from bps.sleep(5)       # busy-wait, no documents
   ```
   **Characterization:** classic single-spot, many-frame fast detector burst for speckle/correlation (g2) analysis, deliberately written *around* the run engine to stream rapid frames to ramdisk; metadata still via global `sample_id`. This is the most non-Bluesky acquisition in the batch — modern equivalent would be a fly/monitor stream or a decorated multi-frame `trigger_and_read` with the frame count as a configured signal.
5. **Notable techniques/hardware:** `/ramdisk/` fast image streaming; raw-PV `EpicsSignal` busy-wait; resonant (S-edge) XPCS energy selection; `det_exposure_time(frame, period)` repurposed as (exposure, burst-window).
6. **Intent:** Resonant (S-edge) XPCS speckle bursts + tender NEXAFS/SAXS-WAXS on polymer films; the XPCS plan is a hand-rolled fast-detector burst outside the Bluesky document model (key migration target).

---

## 13. 30-user-Marks.py
1. **Size / plans:** ~4.9 KB, 2 `def`s (+ commented syringe-pump device stub).
2. **User/group:** Marks (`TC`,`SM`); tender S-edge resonant SWAXS, in-situ flow.
3. **Use-cases:** **tender S-edge resonant SWAXS** (`waxs_S_edge_marks_2025_1_coarse`, fine 0.25 eV grid 2470–2480 over waxs=0/20), **S-edge NEXAFS** (`nexafs_S_edge_marks`), **in-situ solvent/flow** (syringe pump `syringe_pu.go`/`stop_flow` bracketing the energy scan).
   - **Detectors:** `pil900KW`+`pil2M` conditional (`wa==0 → WAXS only`).
4. **Acquisition pattern: LEGACY.** sample×waxs×energy nested loops, per-point `bp.count`; xbpm re-seek; fresh-spot x-drift (`np.linspace(x, x+2000, len(energies))`); bpm into filename; syringe pump started/stopped around the loop:
   ```python
   yield from bps.mv(syringe_pu.go, 1)               # start flow
   for e, xss, yss in zip(energies, xsss, ysss):
       yield from bps.mv(piezo.x, xss); yield from bps.mv(energy, e); yield from bps.sleep(2)
       if xbpm2.sumX.get() < 50: ...                  # energy re-seek
       sample_id(user_name="TC", sample_name=name_fmt.format(..., xbpm=xbpm3.sumX.get()))
       yield from bp.count(dets, num=1)
   ...
   yield from bps.mv(syringe_pu.stop_flow, 1)         # stop flow
   ```
5. **Notable techniques/hardware:** `syringe_pu` flow control during resonant scan; fresh-spot anti-beam-damage x-rastering across the energy grid; xbpm energy-stability re-seek; energy-descent return sequence.
6. **Intent:** Tender S-edge resonant SWAXS/NEXAFS with in-situ syringe-pump flow; LEGACY fresh-spot energy-raster (clone of the Patryk/Gorecka resonant template).

---

## 14. 30-user-Neb.py
1. **Size / plans:** ~4.7 KB, ~9 `def`s (mostly Cai-style alignment helpers).
2. **User/group:** Neb (`ET`; imports Francisco macro; uses `alignCai` toolkit — borrowed). Grazing thin-film / ionomer (Nafion) bar.
3. **Use-cases:** **GISAXS/GIWAXS multi-sample bar** (`do_grazing`, per-sample align then incident-angle×waxs-arc series on Nafion/C1a/C2B1 films), per-sample **GI alignment** (`alignCai`, ROI-driven), alignment/measurement mode switching.
   - **Detectors:** `pil2M`+`pil300KW`+`rayonix` (MAXS) in `do_grazing`; `pil2M` for alignment.
4. **Acquisition pattern: LEGACY.** xloc×name list → per-sample `alignCai()` → incident-angle×waxs-arc nested loops, per-point `bp.count`; fresh-spot `mvr(piezo.x, 200)` between frames; energy/angle/waxs/x baked into filename:
   ```python
   for xloc, name in zip(xlocs, names):
       yield from bps.mv(piezo.x, xloc); yield from alignCai()
       for j, ang in enumerate(a_off + np.array(angle_offset)):
           yield from bps.mv(piezo.th, ang)
           for waxs_pos in waxs_arc:
               yield from bps.mv(waxs, waxs_pos)
               sample_id(user_name="ET", sample_name=name_fmt.format(...))
               yield from bp.count(dets, num=1); yield from bps.mvr(piezo.x, 200)
   ```
5. **Notable techniques/hardware:** borrowed `alignCai` GISAXS alignment (ROI min_x/min_y set, derivative th/height scans, `SMIBeam().insertFoils` mode switch); beamstop-rod alignment/measurement positions (`alignbspos`/`measurebspos`); 3-detector (SAXS+WAXS+MAXS) GI.
6. **Intent:** Multi-sample GISAXS/GIWAXS on Nafion/ionomer films with Cai-toolkit alignment; small LEGACY multi-sample GI loop reusing shared alignment infra.

---

## 15. 30-user-Chopra.py
1. **Size / plans:** ~2.6 KB, 3 `def`s.
2. **User/group:** Chopra (`GVD`); colloidal/nanoparticle transmission SAXS (Murray-adjacent, ref by Marino).
3. **Use-cases:** **transmission SAXS grid mapping** (`run_bu_2022_2`, 9-point `rel_grid_scan`), **SAXS background** (`run_background_bu_2022_2`), **pin-diode-bracketed line scan** (`bu`, attenuator-gated diode read per y-position).
   - **Detectors:** `pil2M` (+`pdcurrent`/`pdcurrent1`/`pdcurrent2`).
4. **Acquisition pattern: MIXED-leaning (still legacy naming).** `run_bu_2022_2` uses a single coordinated `rel_grid_scan` (one run for the 3×3 map — good form), but filename via global `sample_id` and `scan_id` pre-computed from `db[-1]`; `bu` is per-point `bp.count` with fast-shutter diode bracketing:
   ```python
   scan_id = db[-1].start["scan_id"] + 1
   sample_id(user_name=user, sample_name="{sample}_{energy}keV_sdd{sdd}m_id{scan_id}".format(...))
   yield from bp.rel_grid_scan([pil2M], piezo.x, *x_range, piezo.y, *y_range, 0)
   ```
5. **Notable techniques/hardware:** `rel_grid_scan` for the 3×3 SAXS map; fast-shutter-gated pin-diode flux read with `att1_9/att1_10` (`bu`); `db[-1]` scan-id pre-fetch into filename; explicit background-around-sample plan.
6. **Intent:** Transmission SAXS spatial mapping + flux-normalized line scans on colloids/nanoparticles; mostly LEGACY naming but uses a single grid-scan run for the map.

---

## 16. 30-user-Gorecka.py
1. **Size / plans:** ~1.8 KB (truncated mid-plan), 2 `def`s.
2. **User/group:** Gorecka (`Gorecka`,`CM`); tender S-edge resonant SWAXS, Linkam.
3. **Use-cases:** **tender S-edge resonant SWAXS** (`saxs_S_edge_linkam_2024_1`, waxs=0/20, 63-point fresh-spot y-raster across the energy grid), **temperature snapshot** (`temp_snapshop`, `LThermal.temperature()` into filename, `RE.md['temp']`), Linkam in-situ.
   - **Detectors:** `pil900KW`+`pil2M` conditional (`wa==0 → WAXS only`).
4. **Acquisition pattern: LEGACY.** waxs×energy nested loops, per-point `bp.count`; xbpm re-seek; T into filename + `RE.md['temp']`; fresh-spot y-raster (`np.linspace(ys, ys+1500, 63)`):
   ```python
   sample_id(user_name='Gorecka', sample_name=f'{name_base}_{LThermal.temperature()}degC_{en}eV')
   RE.md['temp'] = LThermal.temperature()
   yield from bp.count(dets)
   ...
   for e, xsss, ysss in zip(energies, xss, yss):
       yield from bps.mv(energy, e); ...
       if xbpm2.sumX.get() < 50: ...                  # re-seek
       sample_id(user_name="CM", sample_name=name_fmt.format(..., xbpm=xbpm3.sumX.get()))
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** Linkam `LThermal` temperature into filename + `RE.md`; xbpm re-seek; fresh-spot anti-damage y-raster; energy-descent return sequence — a near-verbatim clone of the shared tender-S-edge resonant template (cf. Marks/Patryk/Su).
6. **Intent:** Tender S-edge resonant SWAXS with Linkam temperature on (likely) ionomer/polymer; minimal LEGACY clone of the resonant fresh-spot energy-raster template.

---

# BATCH SYNTHESIS

- **Dominant archetypes (8):** (1) **tender resonant S/Cl/Ca/Fe-edge SWAXS + NEXAFS** with a *shared fresh-spot energy-raster + xbpm re-seek template* (Patryk, Gomez, Marks, Gorecka, dudenas, chen_xpcs, Wenkai, Cai) — by far the most common, and clearly copy-pasted across files; (2) **GISAXS/GIWAXS multi-sample bar** with per-sample alignment + incident-angle×waxs-arc fans (Netzke, Neb, Tsai, dudenas, QChen, Gomez, Patryk, Karen); (3) **microfocus/raster mapping** via `rel_grid_scan` or dense x/z loops (Patryk, Tsai, Cai, Chopra); (4) **in-situ kinetics time-series** (Marino solvent-evap, Wenkai/Cai tensile, Mao RH-cycling, QChen/Karen time-loops); (5) **operando electrochemistry** (Karen, frames≤5000); (6) **3D-printing in-situ** continuous-acquisition (Cai); (7) **temperature ramp/annealing** via Linkam `LThermal`/Lakeshore `ls` (Cai, Patryk, Marino, Gorecka, Gu-adjacent); (8) **resonant XPCS** speckle burst (chen_xpcs).

- **Legacy-vs-modern prevalence:** **15 of 16 are LEGACY; only Gomez is genuinely MIXED→MODERN.** Universal legacy markers: nested `for`-loop per-point `bp.count(dets, num=1)`, global `sample_id(...)`/`RE.md['sample_name']` for filenames, and context (T, BPM, energy, position, elapsed time, humidity) read via `.value`/`.get()` and concatenated into the filename string rather than recorded as devices. Chopra and Patryk's mapping plans are marginally better (single `rel_grid_scan` per sample) but retain legacy naming.

- **The migration target (Gomez 2026_1):** the only file demonstrating the full modern pattern — a `target_file_name` Signal + `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md={'sample_name':'{target_file_name}'})` + `trigger_and_read(dets + [energy, waxs, xbpm2/3, att2_9, piezo/stage] + [s])`. It captures the exact context (energy, arc, attenuator state, BPM, position) that every legacy file is shoving into filenames. **Use Gomez 2026_1 as the reference implementation.**

- **>> INFRA FLAG (Patryk + corpus-wide utilities):** Patryk (~68 plans) is the **beamline-scientist macro library**, not a single user campaign — it both runs guest experiments (Paren/Das/Andrew/Ray) and houses reusable utilities replicated across the whole corpus: `get_more_md()`/`get_scan_md()` (filename-metadata builders), the **xbpm energy-stability re-seek idiom** (`if xbpm2.sumX.get()<50: re-move energy; sleep`), the assert-guarded `names/piezo_x/piezo_y/piezo_z` coordinate-table convention, `go_to_temp` (Linkam), and `OAV_writing` snapshotting. Other shared infra borrowed across files: `alignment_gisaxs*`/`alignement_gisaxs_doblestack`/`alignCai` (alignment toolkits, Neb imports Cai's; QChen abstracts `M=get_motor()`), `atten_move_in/out`, `SMI_Beamline()/SMIBeam().insertFoils` mode switching, `det_exposure_time(frame, period)`, `set_humidity`/`readHumidity` (Mao/Patryk MFC). These should be centralized and the filename-metadata helpers replaced by `md={}` + baseline devices.

- **>> XPCS FLAG (chen_xpcs):** `grid_scan_xpcs` is the batch's only XPCS and the **only acquisition deliberately written outside the Bluesky document model** — it sets `pil2M.cam.file_path` to `/ramdisk/`, uses `det_exposure_time(0.03, 30)` (0.03 s frames over a 30 s burst window), fires `cam.acquire.put(1)`, and **busy-waits on the raw `Acquire` EpicsSignal PV** so no run/event documents are emitted for the speckle series. It is resonant (S-edge energy set) single-spot multi-frame XPCS for g2 correlation. Modern equivalent: a fly/monitor stream or decorated multi-frame `trigger_and_read` with frame-count as a configured signal and proper document capture.

- **Cross-cutting anti-patterns to retire:** (a) **`RE()` called inside Python `for`/`while` loops** (Mao `_measure_one`, QChen `align_gix_loop_samples`) — plans are not pure generators end-to-end; (b) **mutable global state in `RE.md`** for sample name, timestamp, alignment LUTs and misaligned-sample lists (Karen `alignment_LUT`, Mao `RE.md['sample']`, Patryk `tstamp`/`misaligned_samples`, Gorecka `RE.md['temp']`); (c) **same function name redefined many times** (Karen has 6× `continous_run_prealigned_positions_2025_2`, Patryk 3× `overnight_mapping`, Gomez 2× `waxs_S_edge`) — last-def-wins, fragile.

- **Detector/geometry conventions (consistent across batch):** `[pil900KW] if waxs.arc.position < ~15 else [pil900KW, pil2M]` is the near-universal conditional (drop SAXS when the WAXS arc occludes it); `rayonix` (MAXS) appears only in Tsai/Neb/Mao; `pil300KW` is the older-WAXS detector (chen_xpcs, dudenas, Wenkai, Mao). Slow/in-vacuum axes (`waxs.arc`, `prs`/`stage.phi`) are correctly placed outermost; `piezo.*` (fast) innermost. `pdcurrent*` pin diodes used for transmission flux normalization (Marino, Chopra, Mao) with fast-shutter+attenuator bracketing.

- **In-situ environment hardware seen:** Linkam (`LThermal`, tensile **MFS**), Lakeshore (`ls.output1.mv_temp`), RH MFC (`moxa`/`set*Flow`/`readHumidity`), syringe pump (`syringe_pu`), electrochemistry cells (Karen operando), `prs` azimuthal rotation (texture/pole-figure GIWAXS, GI-tomography), OAV on-axis camera (printing/microfocus). Energy ranges: tender S K-edge ~2470–2490 eV (most files), Ca/Fe/Cl/Ag/P edges (Gomez), and a 9540/9580 eV resonant pair (Netzke, oxide films).

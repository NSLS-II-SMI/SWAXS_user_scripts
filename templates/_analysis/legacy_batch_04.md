# Legacy Batch 04 — SMI (SWAXS) Data-Acquisition Pattern Classification

Beamline: NSLS-II 12-ID SMI (SWAXS = small/wide angle X-ray scattering).
Scope: classify scientific use-cases and acquisition patterns; **no fixes proposed**.
Detector legend: `pil2M`=SAXS (Pilatus 1M/2M, in-vacuum flight tube), `pil900KW`/`pil300KW`=WAXS (Pilatus arc, `waxs`/`waxs.arc`), `rayonix`=MAXS, `amptek`=Si-drift fluorescence detector (FY-XAS/NEXAFS), `pin_diode`/`pdcurrent1/2`=transmission/I0, `xbpm2/3`=beam-position monitors (`.sumX/.sumY` used as I0). `ssacurrent`/`pdcurrent`=ion/diode currents.

Pattern key:
- **MODERN**: `@bpp.run_decorator(md={...})` + `@bpp.stage_decorator(dets)` wrapping `inner()`; one run per logical sample; data via `bps.trigger_and_read(dets + [signals])`; context (energy, waxs, xbpm, target filename Signal) recorded in-stream.
- **LEGACY**: nested `for` loops each calling `bp.count`/`bp.scan`/`bp.rel_scan`/`bp.rel_grid_scan` (one run per data point); global mutable `sample_id(user_name=..., sample_name=...)` for filenames; temperature/BPM/energy read via `.value`/`.get()`/`.position` and baked into filename strings; hard-coded coordinate/sample lists in plan body; `RE.md['...']` set globally.

---

## 1. `30-user-Stingelin.py`
1. **Size / plans**: ~263 KB, **52 top-level plan functions** (~5878 lines). Largest in batch; NOT read fully — characterized via `def` index + representative plan bodies (Cl/S-edge NEXAFS, BPM-vs-pindiode, GIWAXS, in-vacuum GIWAXS, Linkam TD series).
2. **User/group**: Stingelin (conjugated/semiconducting polymers, doped organics, ionic liquids). User codes `NS`, with `LR` (Reven), `PT`, embedded.
3. **Use-cases**: tender-energy NEXAFS/XAS at **Cl K-edge (~2820-2890 eV)** and **S K-edge (~2445-2515 eV)** (`Cl_edge_*`, `S_edge_*`, `nexafs_*`); GISAXS/GIWAXS & GISWAXS multi-sample bars (`GIWAXS_2024_*`, `GISWAXS_2024_*`); **in-vacuum GIWAXS** (`GIWAXS_2024_vacuum_*`, many group-specific: IL/PN/PT/PF/NCSU); **Linkam temperature/cryo ramping** with LN2 pump down to -70 °C (`GIWAXS_TD_run`..`run11`, `S_edge_*_Linkam`); **transmission Cl-edge** (`Cl_edge_transmission_*`); **BPM-vs-pindiode I0 calibration** (`bpmvspindiode_Cledge/Sedge_*`); manual GI snaps (`take_manual_waxs/saxs`).
   - **3b. Detectors**: `pil2M`+`pil900KW` (SAXS+WAXS, SAXS dropped when `wa<10`); `amptek` for fluorescence-yield XAS at each edge maximum; `pdcurrent2`+`xbpm2`/`xbpm3` for I0/transmission calibration.
4. **Pattern**: **LEGACY** (0 decorators, 0 `trigger_and_read`; 109 `bp.count`, 111 `sample_id`). Energy/angle/BPM/temperature -> filename strings; beam-recovery `if xbpm2.sumX.get()<50: re-set energy`.
   ```python
   for e in energies:                       # tender XAS edge scan
       yield from bps.mv(energy, e); yield from bps.sleep(2)
       if xbpm2.sumX.get() < 50: ...        # I0 dropout recovery
       bpm = xbpm2.sumX.get()
       sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai=..., wax=wa, xbpm="%4.3f"%bpm)
       sample_id(user_name="NS", sample_name=sample_name)
       yield from bp.count(dets, num=1)      # one run per energy point
   ```
5. **Notable**: dual-edge tender XAS (Cl + S) with simultaneous GIWAXS + Amptek FY; `alignement_gisaxs_doblestack`/`_hex` per sample; **Linkam cryostage** (`LThermal`, `lnp_mode_set='Auto'`, `setTemperatureRate`, `ramptime`) with cold-vs-warm re-alignment guard (`raise ValueError` if `ai0`/`y` drift); incremental piezo.x walk (`xs - counter*30`) to dose-spread; staircased `waxs` arc re-insertion (in-vacuum). `RE.md['temp']` set globally in some TD plans.
6. **Intent**: Tender-edge (S/Cl) NEXAFS + GI-SWAXS structure/orientation of doped conjugated polymers & ionic-liquid blends across temperature, on multi-sample bars in vacuum.

---

## 2. `30-user-SSYang.py`
1. **Size / plans**: ~44 KB, 34 defs (~1638 lines); top ~850 lines are an **electronic-logbook** of >47 numbered in-situ "Runs" as comments + reassigned globals.
2. **User/group**: S.S. Yang (`SSY`) — nanoparticle (Au, Fe3O4, Pt, Co3O4, PbS, azobenzene-grafted) self-assembly at **liquid/air interface**.
3. **Use-cases**: **in-situ GISAXS at a liquid interface** with kinetics/time-series (`run_gisaxs_in_situ_evap`, `_SVP`, `_HT`); **solvent evaporation** and **UV-light-triggered** azobenzene switching (`run_in_situ_RT_UV_swaxs`, `uv_time`/toluene logged in comments); HT (heating) variants; multi-sample bar GISAXS; transmission SAXS/WAXS; pin-diode current snaps; alignment routine (`alignement_gisaxs` via `SMI_Beamline`).
   - **3b. Detectors**: `pil900KW`+`pil2M`(+`pil300KW`); `pindiol`/pin-diode current; `xbpm3`.
4. **Pattern**: **LEGACY+++ (worst anti-pattern)** — plan functions call **`RE(bps.mv(...))` / `RE(bp.count(...))` nested inside the function** instead of `yield from` (driving the RunEngine recursively), plus `time.sleep()` (blocking, not `bps.sleep`), and `RE.md["scan_id"]` baked into 14 metadata-laced filename templates. 14 `RE.md`, 20 `sample_id`, 13 `bp.count`, 0 decorators.
   ```python
   for i in range(N):                         # outer kinetic loop, blocking
       for ii,(x,sample) in enumerate(zip(x_list, sample_list)):
           RE(bps.mv(piezo.x, x))             # RE() called INSIDE the plan
           if i==0: RE(alignement_gisaxs(0.1)); YPOS[ii]=piezo.y.position
           for th in th_meas:
               name_fmt = "{sample}_{th}deg_ts{ts}_dt{dt}_..._sid{scan_id:08d}"
               RE(bp.count(dets, num=1))      # one run per (x, incidence angle)
       time.sleep(sleep_time)
   ```
5. **Notable**: liquid-interface cell (volume/interface-y logged: "6 ml, py=3100"); UV actinic light timing; multi-incident-angle (0.05/0.15/0.3°) GISAXS; `scan_id` self-reference; rich filename context (ts/dt/x/y/z/sdd) but as strings, not recorded devices.
6. **Intent**: Time-resolved in-situ GISAXS of nanoparticle superlattice assembly/kinetics at a liquid surface under solvent-evaporation, heating, and UV stimuli.

---

## 3. `30-user-Gomez_Oskar.py`
1. **Size / plans**: ~34 KB, 8 defs (~969 lines, heavily commented sample-block history).
2. **User/group**: Oskar Gomez (`OS`) — biomineral / PLA composites, calcium-bearing samples.
3. **Use-cases**: **transmission SAXS/WAXS multi-sample bar** (`ex_situ_hardxray*`, 16.1 keV, sdd 8.3 m); **Ca K-edge NEXAFS/XAS (~4030-4150 eV, tender)** with WAXS+SAXS (`saxs/waxs/nexafs_prep_multisample_nov`, `NEXAFS_Ca_edge_multi`); WAXS-arc sweeps over many `waxs` angles for powder coverage.
   - **3b. Detectors**: `pil2M`+`pil300KW` (SWAXS); `pil300KW` alone for Ca-edge WAXS; `amptek` (fluorescence; `RE.md['filename_amptek']` set); `xbpm3.sumY` as I0.
4. **Pattern**: **LEGACY** (24 `sample_id`, 1 `bp.count`, mostly `bp.rel_scan` over `piezo.y` as a **dose-spreading "smear"** rather than a true profile; 0 decorators). Hard-coded x/y/z lists per sample bar; energy stepped manually with sleep.
   ```python
   for wa in waxs_range:                       # WAXS arc coverage
       yield from bps.mv(waxs, wa)
       for sam,x,y,z in zip(samples, x_list, y_list, z_list):
           yield from bps.mv(piezo.x,x); ...; yield from bps.mv(piezo.z,z)
           sample_id(user_name="OS", sample_name=f"{sam}_wa{wa}")
           yield from bp.rel_scan(dets, piezo.y, *ypos)   # y-smear @ each station
   ```
5. **Notable**: Ca K-edge (calcium, biomineralization-relevant) NEXAFS; `amptek` FY filename pushed via `RE.md['filename_amptek']`; gentle energy walk-down at end of each edge scan; `stage.th` tilt presets per sample row.
6. **Intent**: Ex-situ multi-sample SWAXS + Ca K-edge NEXAFS of biomineral/PLA composites to correlate calcium speciation with nano/meso structure.

---

## 4. `30-user-Gordon.py`
1. **Size / plans**: ~30 KB, 10 defs (~699 lines).
2. **User/group**: Gordon / Su group (`MG`, `GF`, `PT`) — doped conjugated polymers (P3HT, PBTTT, PEDOT, DPP), polyelectrolytes (PVA/TiO).
3. **Use-cases**: **GISAXS/GIWAXS multi-sample bar** with double-stack (top/bottom) positions (`gisaxs1/2_gordon_*`, `gisaxs_gordon_2021_3`, `_2022_1`); **S K-edge WAXS NEXAFS (~2445-2500 eV)** (`waxs_S_edge_gordon_*`); transmission SWAXS (`gordon_saxswaxs_*`); **temperature ramp** GIWAXS 30-120 °C via Lakeshore (`temp_2021_3`); alignment (`alignement_gordon_*`, `alignement_gisaxs*`).
   - **3b. Detectors**: `pil2M`+`pil900KW`+`pil300KW` (multi-arc GI); `pil300KW` alone for S-edge.
4. **Pattern**: **LEGACY** (9 `bp.count`, 15 `sample_id`, 0 decorators). Aligns once -> stores `ai0=piezo.th.position`, loops `waxs_arc` x incidence-angle list; per-angle x-offset to dose-spread; `energy.energy.position`/`pil2M_pos.z.position` -> filename.
   ```python
   yield from alignement_gisaxs(angle=0.15); ai0 = piezo.th.position
   for wa in waxs_arc:                           # [0,2,20,22,40,42] dual-side arc
       yield from bps.mv(waxs, wa)
       for i,an in enumerate(angle):             # [0.1,0.15,0.2] incidence
           yield from bps.mv(piezo.x, xs+i*200); yield from bps.mv(piezo.th, ai0+an)
           sample_id(user_name="PT", sample_name=name_fmt.format(...))
           yield from bp.count(dets, num=1)
   ```
5. **Notable**: paired WAXS-arc angles (0/2, 20/22, 40/42) to fill detector gaps; `att1_9.open_cmd` attenuator toggling; `SMI_Beamline.modeAlignment/Measurement`; Lakeshore `ls.output1.mv_temp`, `ls.input_A`; huge commented coordinate archives (multi-cycle bars).
6. **Intent**: GI-SWAXS + S K-edge structure/orientation/doping study of conjugated polymers vs incidence angle and temperature on multi-sample bars.

---

## 5. `30-user-Clark.py`
1. **Size / plans**: ~19 KB, 14 defs (~601 lines).
2. **User/group**: Clark / UCol collaborators (`NC`, `GS`, `VM`, `DK`) — liquid-crystal materials (RM734, DIO), capillaries, biological tissue.
3. **Use-cases**: **microfocus raster mapping** (`mapping*_waxs_ucol`, `rel_grid_scan`/`scan_nd` with skewed "`crazy_mapping`" trajectories) over WAXS arc; **in-situ temperature** SWAXS with Instec/Lakeshore heating (`instec_insitu_hard_xray*`, `instec_insitu_t_step_*`, ramp + meshgrid dose-walk); transmission WAXS angle scans on biological/empty cells; continuous time-series (`run_contRPI`); MAXS (`rayonix`).
   - **3b. Detectors**: `pil2M`+`pil300KW`(+`rayonix`); `ls.ch1_read`/`ls.input_A` recorded as temperature.
4. **Pattern**: **LEGACY/MIXED** — true raster via `bp.rel_grid_scan`/`bp.scan_nd` (multi-point run = acceptable mapping idiom) BUT in-situ-T plans use nested `for` + `bp.count(num=1)` with meshgrid position-walk and temperature read via `ls.input_A.value`. 9 `bp.count`, 21 `sample_id`, 0 decorators. Also raw `pil2M.cam.file_path.put(...)` path injection.
   ```python
   yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)   # mapping (multi-pt run)
   # ... vs in-situ-T:
   cur_temp = ls.input_A.value                       # read into filename, not stream
   for wa in wa_arc:
       sample_id(user_name="NC", sample_name="{name}_{T}C_t{t}_wa{wa}_sdd1.6m")
       yield from bp.count(dets, num=1)
   ```
5. **Notable**: `crazy_mapping()` builds angle-skewed snake trajectories via `cycler`; meshgrid `(xss,yss)` dose-walk so each frame hits fresh material; Instec/Lakeshore (`ls.output3.mv_temp`, `ls.input_A`) ramp+equilibrate loops; reverses `waxs_arc` based on current arc position; `rayonix` MAXS.
6. **Intent**: Microfocus WAXS/MAXS raster mapping of tissue/capillaries and temperature-resolved SWAXS of liquid-crystal phases (RM734/DIO).

---

## 6. `30-user-Hoang.py`
1. **Size / plans**: ~16 KB, 6 defs (~557 lines).
2. **User/group**: Hoang / Fukuto-adjacent (`JH`, `GF`) — liquid crystals / blue phases (BPI-III), OBA mesogens, cholesteric films.
3. **Use-cases**: **S K-edge NEXAFS/RSoXS-like (~2445-2500 eV)** transmission + GI (`nexafs_S_edge`, `S_edge_SAXSWAXS_*`, `saxs_S_edge_Hoang_*`); **S-edge + temperature** ramp 30-200 °C (`saxs_S_edge_temperature_*`, Lakeshore `ls.output1`); **in-situ tensile** stretching time-series (`tensile_continous_*`, `tensile_single_*` with `t0` sync to external Linkam tensile plan, sample rotation `prs`, hexapod presets per rotation).
   - **3b. Detectors**: `pil900KW`(+`pil2M` when `wa>=10`); `xbpm2`/`xbpm3.sumX` as I0; sdd from `pil2M_pos.z.position`.
4. **Pattern**: **LEGACY** (6 `bp.count`, 9 `sample_id`, 0 decorators). Energy + BPM + sdd + rotation -> filename; multi-sample (a/b rows) hard-coded; gentle energy walk-down; `piezo.y` linspace dose-spread across the edge to avoid beam damage.
   ```python
   yss = np.linspace(ys, ys+1500, len(energies))   # spread dose along edge scan
   for e, ysss in zip(energies, yss):
       yield from bps.mv(piezo.y, ysss); yield from bps.mv(energy, e); yield from bps.sleep(2)
       bpm = xbpm3.sumX.get(); sdd = pil2M_pos.z.position/1000
       sample_id(user_name="JH", sample_name="{sample}_{e}eV_wa{wa}_sdd{sdd}m_bpm{bpm}")
       yield from bp.count(dets, num=1)
   ```
5. **Notable**: tensile-stage frame-time sync via external `t0=time.time()` correlation; per-rotation hexapod dict (`hexa_poistions`); filename sanitation via `str.translate`; SAXS suppressed while WAXS arc blocks (`dets=[pil900KW] if wa<10`).
6. **Intent**: S K-edge resonant SWAXS of blue-phase/cholesteric liquid crystals and OBA mesogens vs temperature and tensile strain.

---

## 7. `30-user_Petterson.py`
1. **Size / plans**: ~14 KB, 8 defs + a long manual-alignment docstring (~422 lines).
2. **User/group**: Pettersson / KTH (`TP`, `PT`) — multilayer polyelectrolyte films (PEI/CNF/PAH), Langmuir/interface samples.
3. **Use-cases**: **GISAXS/GIWAXS at buried interface & surface** (`run_gi_sweden_SAXS/GISAXS`, interface-vs-surface y-scans); multi-sample GISAXS with per-sample alignment (`gisaxs_KTH_2021_1` via `SMI_Beamline.modeAlignment`); **in-situ pump/flow loop kinetics** (`run_loop_measurement` — pump_t/total_t cycles, SAXS+WAXS, two incidence angles); alignment helpers (`alignment_start`/`_start_angle`/`_stop`, direct/reflected-beam ROI).
   - **3b. Detectors**: `pil2M`(+`pil2Mroi2`); `pil900KW` when arc in; SAXS dropped when `waxs.arc<15`.
4. **Pattern**: **LEGACY/MIXED** — uses `bp.rel_scan(dets, piezo.y, ...)` profiles (multi-pt) and `bp.count(num=1)`; BUT shows **partial-modern hygiene**: stores incident-angle in `RE.md['ai_0']` and passes `md=dict(ai=ai)` to `rel_scan`; alignment via `SMI_Beamline` mode helpers. 3 `bp.count`, 12 `sample_id`, 8 `RE.md`, 0 decorators.
   ```python
   try: ai0 = RE.md['ai_0']                  # alignment cached in RE.md
   except: ...; ai0 = db[-1].start['ai_0']
   for wa in waxs_arc:
       for ai in incident_angles:
           yield from bps.mv(piezo.th, ai0+ai); yield from bps.mvr(piezo.x, -jump_x)
           yield from bp.rel_scan(dets, piezo.y, *y_range, md=dict(ai=ai))   # md passed!
   ```
5. **Notable**: contains a **canonical manual GISAXS alignment recipe** (multi-line docstring: half-cut on direct beam, th-rocking, reflected-beam ROI, `ps()`/`ps(der=True)` peak-stats) — useful template content; pump-then-measure loop with progress prints; `get_scan_md()` helper for filenames.
6. **Intent**: GISAXS/GIWAXS of polyelectrolyte multilayer films at surface vs buried interface, with in-situ pumping/flow kinetics and reflected-beam alignment.

---

## 8. `30-user-UCR.py`
1. **Size / plans**: ~13 KB, 5 defs (~309 lines).
2. **User/group**: UCR/UCI collaborators (`DK`, `TW`, `WY`/Yang) — biomineralized tissue (teeth, chiton, gypsum, wood, chitin).
3. **Use-cases**: **microfocus WAXS/SAXS raster mapping** of biological/mineral samples (`run_mesh_fastUCR/UCI`, `mesh_UCI_2020_3`, `_2021_2`, `_2021_3`) — `bp.rel_grid_scan` over piezo.x/y at multiple WAXS arc angles; multi-sample bars with per-sample x/y/z/chi/hexapod-y and per-sample mesh extents.
   - **3b. Detectors**: `pil300KW`/`pil900KW`/`pil2M` combinations (WAXS-led mapping).
4. **Pattern**: **LEGACY (mapping idiom)** — `bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)` per (sample, waxs-angle); 0 `bp.count`, 10 `sample_id`, 0 decorators. Heavy hard-coded per-sample coordinate/range tables (many commented prior runs); `proposal_id(...)` reset mid-loop.
   ```python
   for x,y,sample,x_r,y_r in zip(x_list,y_list,samples,x_range,y_range):
       yield from bps.mv(piezo.x,x); yield from bps.mv(piezo.y,y)
       for wa in waxs_range:                       # multiple arc angles
           yield from bps.mv(waxs, wa)
           sample_id(user_name=name, sample_name=f"{sample}_wa{wa}")
           yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)  # raster
   ```
5. **Notable**: per-sample WAXS-arc lists (0..26°) for texture/orientation mapping of mineralized tissue; per-sample snake disabled (`...,0`); hexapod-y + chi presets; large archival coordinate blocks; mid-plan `proposal_id` switching.
6. **Intent**: Spatially-resolved (microfocus raster) WAXS/SAXS crystallographic mapping of biomineralized tissues (teeth/chiton/chitin) at multiple detector arc angles.

---

## 9. `30-user-NIST_sept18.py`
1. **Size / plans**: ~8 KB, 9 defs (~234 lines).
2. **User/group**: NIST (Sept 2018) (`DB`, `name`-parameterized) — lipids (POPC), surfactants/caps, gratings, GIWAXS films.
3. **Use-cases**: **transmission SAXS multi-sample** (`run_saxs_lipids`, `run_saxs_caps`, energy/`e_grid_scan`); **temperature-series SAXS** with Lakeshore (`run_saxs_caps_temp`, 30-50 °C, `ls.ch1_sp`/`ls.ch1_read`); **GIWAXS** films (`run_ben_giwaxs`, incidence presets + offset); **grating / fly-scan kinetics** (`grating_rana`, `fly_scan` — detector-triggered continuous sweep of `prs`/motor over -40..+40, multi-cycle); MAXS (`rayonix`) in `run_waxs_multi`.
   - **3b. Detectors**: `pil2M`+`pil300KW`(+`rayonix`); `ssacurrent`, `ls.ch1_read`, `xbpm3.sumX/Y` recorded.
4. **Pattern**: **LEGACY/MIXED** — combines `bp.scan`/`escan`/`e_grid_scan` (multi-pt), `bp.count`, and a **hand-rolled `fly_scan`** that manually stages/triggers the detector and runs `list_scan([], motor, [start,stop])` (continuous acquisition). 0 `bp.count` calls direct (uses `count([det],num=1)`), 13 `sample_id`, 2 `RE.md`, 0 decorators.
   ```python
   def fly_scan(det, motor, cycle, cycle_t, phi):
       det.stage(); det.cam.acquire_time.put(cycle*cycle_t); st = det.trigger()
       for i in range(cycle): yield from list_scan([], motor, [start, stop])  # sweep during 1 exposure
       while not st.done: pass
       det.unstage()
   ```
5. **Notable**: manual fly/sweep acquisition (single long exposure while rocking `prs`/`motor`); `attn_shutter` Insert/Retract gating; `e_grid_scan`/`escan` custom energy-grid plans; nested temperature x sample x angle cycles; `rayonix` MAXS.
6. **Intent**: NIST lipid/surfactant transmission SAXS + grating GIWAXS with temperature series and continuous rocking (fly) acquisition.

---

## 10. `30-user-Reven.py`
1. **Size / plans**: ~6 KB, **3 plans** (~166 lines).
2. **User/group**: Reven (`temp`-named; user code via `RE.md`) — temperature-driven phase transitions (SAXS).
3. **Use-cases**: **temperature ramping / annealing SAXS time-at-temperature** (`temp_series`, `temp_series_withpos`, `temp_series_grid`) — Linkam (`LThermal`) setpoints with equilibration hold; optional XY position list and XY grid variants.
   - **3b. Detectors**: `[pil2M]` (SAXS only); sdd from `pil2M_pos.z.position`.
4. **Pattern**: **LEGACY but transitional** — uses `LThermal` Linkam, sets `RE.md["sample_name"]='{target_file_name}'` and creates a `Signal('target_file_name')` **`s` appended to dets** (`bp.count(dets+[s])`) — i.e. the **target filename is recorded as a Signal in-stream** (a step toward modern). Still: temperature read via `LThermal.temperature()` into filename; nested loops; no run/stage decorators; no `sample_id` (0). 3 `bp.count`, 6 `RE.md`.
   ```python
   s = Signal(name='target_file_name', value='')
   RE.md["sample_name"] = '{target_file_name}'
   for i, temp in enumerate(temps):
       LThermal.setTemperature(temp)
       while abs(LThermal.temperature()-temp) > 0.2: yield from bps.sleep(10)
       s.put(sample_name); yield from bp.count(dets + [s])   # filename Signal in-stream
   ```
5. **Notable**: closest-to-modern filename handling in batch (`target_file_name` Signal + md template) yet still per-point `bp.count`; equilibration hold (2x on first point); grid variant nests x/y/temp; Linkam temperature NOT recorded as a device (only as string).
6. **Intent**: Temperature-resolved (Linkam) SAXS of thermal phase transitions, optionally over XY positions/grids.

---

## 11. `example_scripts.py`  ⭐ CANONICAL / TEMPLATE
1. **Size / plans**: ~5.5 KB, **2 example plans** (`single_scan_test`, `single_scan_giwaxs`) (~136 lines).
2. **User/group**: beamline staff example (`CM`/`Test`) — GIWAXS / tender-edge demo.
3. **Use-cases**: demonstration of **energy/edge scan + GIWAXS** with the **modern acquisition idiom**; multi-sample GIWAXS with per-sample alignment (`alignement_gisaxs_doblestack`).
   - **3b. Detectors**: `[pil2M]`/`[pil900KW, pil2M]`.
4. **Pattern**: **MODERN** (the only modern file in the target batch) — `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md={'sample_name':'{target_file_name}'})` around `inner()`; **one run per sample**; data via **`bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])`**; target filename as `Signal('target_file_name')` put into the stream; context devices recorded in-stream (NOT filename strings). 2 `run_decorator`, 2 `trigger_and_read`, 0 `bp.count`.
   ```python
   s = Signal(name='target_file_name', value='', kind=3)
   @bpp.stage_decorator(dets)
   @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
   def inner():
       for e in energies:
           yield from bps.mv(energy, e); yield from bps.sleep(2)
           bpm = yield from bps.rd(xbpm2.sumX)
           s.put(sample_name)
           yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
   return (yield from inner())
   ```
5. **Notable**: **reference implementation** for migrating legacy plans — shows correct decorator stacking, `bps.rd()` for reads, in-stream context recording, md-based filename, `sample_id(...)` commented out. Beam-recovery (`xbpm2.sumX.get()<50`) and `det_exposure_time` retained.
6. **Intent**: Canonical template demonstrating the GOOD (modern) one-run-per-sample GIWAXS / energy-scan acquisition pattern for the beamline.

---

## 12. `30-user-Zhang-NIST.py`
1. **Size / plans**: ~14 KB, **3 plans** (~145 lines).
2. **User/group**: F. Zhang / NIST (`FZ`) — continuous SWAXS, standards/blanks.
3. **Use-cases**: **continuous in-situ time-series SWAXS** (`run_continous_Zhang` — fixed interval `td`, infinite-ish loop, step/elapsed-time filenames); **with pin-diode transmission** (`run_continous_pindiode_Zhang` — opens `fs`, reads `pdcurrent1` per frame); **standard SWAXS** of Kapton/air/standard blanks at WAXS in/out (`run_standard_swaxs_Zhang_2023_3`).
   - **3b. Detectors**: `pil900KW`(+`pil2M` when arc>15); `pdcurrent1` pin-diode for transmission.
4. **Pattern**: **LEGACY** (3 `bp.count`, 6 `sample_id`, 0 decorators). `time.time()` elapsed + step + pin-diode current -> filename via `get_scan_md()`; busy-wait interval loop with `bps.sleep(0.1)`; `pdcurrent1.value` read into name.
   ```python
   for i in range(99999):                       # continuous kinetic series
       fs.open(); yield from bps.sleep(0.3); pd_curr = pdcurrent1.value; fs.close()
       sample_name = f'{name}_step{step}_time{time_sname}s_pd{pd}{get_scan_md()}'
       sample_id(user_name=user, sample_name=sample_name)
       yield from bp.count(dets)
       while (time.time()-t_measurement) < td: yield from bps.sleep(0.1)
   ```
5. **Notable**: shutter-gated pin-diode I0/transmission read per frame; `get_scan_md()` filename helper; WAXS-arc-dependent detector selection (`<14.9` -> WAXS only); x-offset triplet for blanks.
6. **Intent**: Continuous interval-based in-situ SWAXS kinetics with per-frame pin-diode transmission, plus standard/blank calibration scans.

---

## 13. `30-user-Zhengxing.py`
1. **Size / plans**: ~3 KB, **1 plan** (~66 lines).
2. **User/group**: Zhengxing (`ZP`) — Ru-edge resonant scattering.
3. **Use-cases**: **Ru L-edge / tender-energy resonant SWAXS (~2800-2881 eV)** mapping (`Ru_edge_zhengxing_2024_2`) at WAXS arc 0/20, multi-temperature samples (P1_120C series), per-energy meshgrid position-walk; SAXS suppressed when WAXS arc in beam.
   - **3b. Detectors**: `pil2M`+`pil900KW` (SAXS dropped when `wa<10`).
4. **Pattern**: **LEGACY** (1 `bp.count`, 1 `sample_id`, 0 decorators). Energy stepped with I0 dropout recovery; `xbpm2.sumX.get()` -> filename; meshgrid `(xss,yss)` dose-walk so each energy hits fresh spot; gentle energy walk-down at end.
   ```python
   for e, xsss, ysss in zip(energies, xss, yss):
       yield from bps.mv(energy, e); yield from bps.sleep(2)
       if xbpm2.sumX.get() < 50: ...               # I0 recovery
       yield from bps.mv(stage.y, ysss); yield from bps.mv(stage.x, xsss)
       bpm = xbpm2.sumX.get()
       sample_id(user_name="ZP", sample_name="{name}_pos1_{e}eV_wa{wa}_bpm{bpm}_sdd3m")
       yield from bp.count(dets, num=1)
   ```
5. **Notable**: Ru-edge (transition-metal L-edge) resonant scattering; `np.meshgrid` dose-walk identical idiom to Stingelin/Hoang; commented prior sample table; sdd 3 m noted in name.
6. **Intent**: Ru L-edge resonant SWAXS mapping of (polymer-electrolyte?) samples at fixed temperature with energy-stepped dose-walk.

---

## 14. `34-oleg.py`
1. **Size / plans**: ~2 KB, **2 plans** (~49 lines).
2. **User/group**: Oleg / staff (`AM`, parameterized) — single-crystal/faceted object orientation.
3. **Use-cases**: **coupled rotation+translation line/orientation scans** (`aaron_rot` — `bp.inner_product_scan` coupling `prs` rotation with `stage.x` + `piezo.y` along a faceted "octahedron plate" trajectory); **custom single-shot transmission SAXS** at current position (`custo_scan`).
   - **3b. Detectors**: `[pil2M]` (SAXS).
3b restated. 
4. **Pattern**: **LEGACY (small/utility)** — `bp.inner_product_scan` (multi-axis coupled, multi-pt) chained as a staircase of segments; `custo_scan` does `bp.count([pil2M], num=1)` with position->filename. 1 `bp.count`, 2 `sample_id`, 0 decorators.
   ```python
   yield from bp.inner_product_scan([pil2M], 11, prs, 45, 35, stage.x, 0.3834, 0.318, piezo.y, -580, -580)
   yield from bp.inner_product_scan([pil2M], 10, prs, 34, 25, stage.x, 0.318, 0.254, piezo.y, -580, -580)
   # ... staircase of coupled rotation/translation segments
   ```
5. **Notable**: `inner_product_scan` multi-motor coupling for rotational tomography-like / faceted-object orientation sweep; hard-coded segment endpoints; trivial `custo_scan` utility with position-string filename.
6. **Intent**: Coupled rotation/translation orientation scan of a faceted single object plus a quick single-shot transmission utility.

---

# BATCH SYNTHESIS

- **Legacy dominance is near-total.** 13 of 14 target files are **LEGACY**; only `example_scripts.py` is **MODERN** (the lone `bpp.run_decorator`/`stage_decorator`/`trigger_and_read` user — confirmed 0 decorators in all 13 others, 109 `bp.count` in Stingelin alone). Beamline-wide, the modern idiom is otherwise concentrated in `30-user-Richter.py` (~10.4k lines, NOT in this batch) — the de-facto migration reference.

- **Canonical/template flag:** `example_scripts.py` is the **GOLDEN template** (one-run-per-sample, in-stream context, `target_file_name` Signal + `md={'sample_name':'{target_file_name}'}`, `bps.rd()` reads). `30-user_Petterson.py` contains a **canonical manual-GISAXS-alignment recipe docstring** (half-cut/th-rock/reflected-ROI + `ps()` peak stats) worth preserving as alignment documentation.

- **Distinct archetypes identified:**
  1. **Tender-energy resonant XAS/NEXAFS + scattering** — S K-edge (~2445-2515), Cl K-edge (~2820-2890), Ca K-edge (~4030-4150), Ru L-edge (~2800-2881): Stingelin, Hoang, Gordon, Gomez_Oskar, Zhengxing (+example). Universal idioms: `for e in energies: bps.mv(energy,e); sleep`, `xbpm.sumX.get()<50` I0-dropout recovery, gentle energy walk-down, `amptek` fluorescence yield (Stingelin/Gomez_Oskar).
  2. **GISAXS/GIWAXS multi-sample bar** with per-sample alignment + incidence-angle stacks + dual-side WAXS-arc pairs (0/2/20/22/40/42): Stingelin, Gordon, Petterson, SSYang, example.
  3. **Microfocus raster mapping** (`rel_grid_scan`/`scan_nd`/skewed `cycler`): UCR, Clark (biomineral tissue, teeth, chiton, capillaries).
  4. **Temperature ramping / annealing** (Linkam `LThermal` & Lakeshore `ls`): Reven, Gordon, Hoang, Clark (Instec), Stingelin (incl. LN2 cryo to -70 °C with re-alignment guards).
  5. **In-situ time-series / kinetics** — liquid-interface NP assembly + UV/solvent (SSYang), continuous interval SWAXS + pin-diode (Zhang-NIST), pump/flow loops (Petterson), tensile (Hoang), in-situ-T dose-walk (Clark/Stingelin).
  6. **Continuous/fly acquisition** — hand-rolled `fly_scan` (NIST_sept18) and `inner_product_scan` coupled rotation (34-oleg).

- **Pervasive legacy anti-patterns (migration targets):** (a) per-data-point `bp.count(dets, num=1)` inside nested `for` loops -> a separate Bluesky run per frame; (b) global mutable `sample_id(user_name=, sample_name=)` for filenames (Stingelin 111x, total >180 across batch); (c) context (energy/`waxs`/`xbpm`/temperature/sdd) read via `.value`/`.get()`/`.position` and **string-formatted into filenames instead of recorded as devices**; (d) hard-coded per-sample x/y/z coordinate + range tables in plan bodies (huge commented archives in Gordon/UCR/Gomez_Oskar).

- **Worst offender:** `30-user-SSYang.py` calls **`RE(...)` recursively inside plan functions** and uses blocking `time.sleep()` plus `RE.md["scan_id"]` self-reference in filenames — the furthest from generator-based plans; high-priority rewrite.

- **Transitional/best-of-legacy:** `30-user-Reven.py` already uses a `target_file_name` **Signal appended to `dets`** and an `md` filename template (mirrors the modern example) but still issues per-point `bp.count`; `30-user_Petterson.py` caches alignment in `RE.md['ai_0']` and passes `md=dict(ai=ai)` into `rel_scan`. These two are the lowest-effort migrations.

- **Dose-management is a recurring scientific constraint:** `np.meshgrid`/`np.linspace` position-walk (move to fresh sample spot per energy/frame) appears in Stingelin, Hoang, Gordon, Zhengxing, Clark — a beam-damage mitigation idiom that any modern rewrite must preserve (as motor moves inside the run, recorded in-stream).

- **Hardware/technique vocabulary present:** `pil2M`(SAXS in-vacuum), `pil900KW`/`pil300KW`(WAXS arc), `rayonix`(MAXS; Clark/NIST_sept18), `amptek`(SDD FY-XAS), `xbpm2/3`(BPM I0), `pdcurrent1/2`+`fs`(pin-diode transmission), `LThermal`(Linkam ±cryo), `ls`(Lakeshore/Instec), `prs`(rotation), `piezo.{x,y,z,th}`+`stage`(hexapod, in-vacuum outer axes), `waxs.arc`(slow in-air arc), `SMI_Beamline.modeAlignment/Measurement`, `att*`(attenuators), `attn_shutter`. No XPCS, no explicit CD-SAXS/3D-printing/electrochemistry/RH in THIS batch (those live in other beamline scripts, e.g. `30-user-CDSAXS.py`, `30-user-ECD-3dprinterLutz*.py`).

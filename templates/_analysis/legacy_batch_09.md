# Legacy Bluesky/Ophyd Plan Analysis — Batch 09 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 16 legacy
user macro files. Detectors: `pil2M` = SAXS (Pilatus 1M/2M, on `pil2M_pos`), `pil900KW`/`pil300KW`
= WAXS (arc-mounted in-vacuum; `pil300kwroi2`/`pil2Mroi2-4` = ROI sub-streams), `rayonix`
= MAXS, `xbpm2`/`xbpm3` (`sumX`/`sumY`) = beam-position monitors, `pdcurrent1`/`pin_diode`
= transmitted-flux diode, `ls`/`LThermal` = Lakeshore / Linkam temperature controllers,
`syringe_pu` = syringe pump. `waxs` (a.k.a. `waxs.arc`) and `piezo.th`/`stage.th`/`prs`
are slow / in-vacuum axes. Goniometry split between `piezo.*` (fast nano-stage: x/y/z/th/ch)
and `stage.*` (coarse hexapod). Energy via `energy` (DCM) for tender/edge work.
`prs`/`stage_pseudo.phi` = CD-SAXS rotation (sample phi). `GV7` = SAXS gate valve.

Pattern legend: **LEGACY** = nested `for` loops, each iteration calls
`bp.count`/`bp.scan`/`bp.rel_scan` → one Bluesky run per data point; filenames via global
mutable `sample_id(...)`/`RE.md`; context (temperature, bpm, energy) read via `.value`/
`.get()`/`.position` into strings. **MODERN** = `@bpp.run_decorator(md=...)` +
`@bpp.stage_decorator(dets)` around `inner()` with `bps.trigger_and_read(dets + [signals])`.
**MIXED** = both present / documented migration in progress. A distinct sub-failure mode
seen in this batch: **RE()-in-loop** (plans that are not generators end-to-end; they call
`RE(...)` inside Python `for`/`while` loops and stash state in `RE.md` — worse than legacy
because they cannot be composed, suspended, or nested by the RunEngine).

---

## 1. 30-user-Kline2.py
1. **Size / plans:** ~123 KB, ~40 `def`s (largest in batch; campaign-dated `cdsaxs_Nov2025_*` and `cdsaxs_May2026_*` families).
2. **User/group:** Kline / CD-SAXS program (`CW` Caitlyn, `JK` imec, `KD`, `MW_Q` Qnity); semiconductor-metrology guests (imec gate/fin/CFET, Intel, ITRI, DuPont, Chicago, SRM standards).
3. **Use-cases:** **CD-SAXS** (critical-dimension small-angle scattering on lithographic gratings/fins) — the defining technique. Sample-phi (`prs`/`stage_pseudo.phi`) rocking from −60°→+60°, with bracketing reference frames; round-robin SRM standards; beam-damage walk studies (`QnityBeamDamage`); misalignment (chi/th) sweeps; grid scans; x-position checks. Transmission geometry, fixed 16.1 keV.
   - **Detectors:** `pil2M` (SAXS) only; readback Signals (`piezo.x/y/z`, `pil2M.sample_distance_mm`, `xbpm3.sumX`, `stage_pseudo`) folded into detector list in the newer plans.
4. **Acquisition pattern: MIXED — clearest in-file legacy→modern split in the batch.**
   - LEGACY core `cd_saxs()`: per-phi-step `bp.count`, filename built from `.get()`/`.position`, plus a side-channel CSV log:
     ```python
     for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
         yield from bps.mv(prs, theta)
         sample_name = name_fmt.format(..., bpm="%1.3f"%xbpm3.sumX.get(), th="%2.2d"%theta, ...)
         sample_id(sample_name=sample_name)
         write_to_log_file(log_filename=log_filepath, sample_filename=sample_name, sample_phi_deg=theta, ...)
         yield from bp.count(det, num=1)
     ```
   - TRANSITIONAL `cd_saxs_modern()` / `x_scan()`: a single coordinated `bp.list_scan` over phi with readbacks recorded as channels and a `{stage_phi_real}` placeholder left in the filename template (the `May2026` templates call this version):
     ```python
     dets = det + [piezo.x, piezo.y, piezo.z, pil2M.sample_distance_mm, stage_pseudo, xbpm3.sumX]
     name_fmt = "{sample}_..._phi_{{stage_phi_real}}"
     yield from bp.list_scan(dets, stage_pseudo.phi, np.linspace(th_ini, th_fin, th_st))
     ```
   - Note: no `@bpp.run_decorator`/`stage_decorator` anywhere; "modern" here means one-run-per-rock via `list_scan` + recorded readbacks, not the full decorated-`inner()` template.
5. **Notable techniques/hardware:** ref-A/measure/ref-B bracketing per sample; `pil2M.sample_distance_mm` ophyd readback (good); per-sample `start_at`/`repeats` restart knobs; `while abs(piezo.y.position-ys)>=1` settle-retry loops; external `.csv` log of phi/exposure keyed to filename (legacy provenance crutch). Odd/even phi-interleave (`_odds_evens`) for grating symmetry.
6. **Intent:** Dedicated CD-SAXS metrology macro library for semiconductor gratings/fins; actively migrating from per-angle `bp.count` to single `list_scan`-per-rock with recorded motor/bpm channels.

---

## 2. 30-user-Gomez_Sintu.py
1. **Size / plans:** ~93 KB, ~26 `def`s (`ex_situ_*edge_*`, `*_prep_multisample_*`, `giwaxs_*`).
2. **User/group:** Gomez group / Sintu (`SR`,`GS`); guests Matt (`*_matt`), JDM, Ryan (`giwaxs_Ryan`). Soft-matter / organic-electronic thin films + organic-acid (ARA) / SAM series.
3. **Use-cases:** **tender-energy resonant SAXS/WAXS + NEXAFS at multiple edges** — Ca K-edge (~4030–4105 eV), Zn K-edge, La L-edge, S-edge; **microfocus hard-X-ray mapping** (`ex_situ_hardxray_micro*`, 16.1 keV); **transmission SWAXS** multi-sample bars (26-sample R1–R7 trays); **GIWAXS** (`giwaxs_Ryan`, `giwaxs_chaney`-style 14 keV angle series); **"humidity" sample sets** (`*_humidity_*`) — but these are *hydrated samples prepared offline* (`Hyd_*` names), NOT active RH/MFC control. `*_nosmaract` variants run on coarse hexapod when the SmarAct nano-stage is unavailable.
   - **Detectors:** `pil2M`+`pil300KW`; SAXS detector y repositioned (`pil2M_pos.y` −60↔−55.7) for arc up/down stitching.
4. **Acquisition pattern: LEGACY (uniform).** Outer waxs loop → sample loop → energy loop → per-point `bp.count`; bpm via `.value`/`.get()` into filename; energy-dropout re-issue guard:
   ```python
   for wa in waxs_range:
       yield from bps.mv(waxs, wa)
       for sam, x, y, z in zip(samples, x_list, y_list, z_list):
           yield from bps.mv(piezo.x, x); ...
           for k, e in enumerate(energies):
               yield from bps.mv(energy, e); yield from bps.sleep(1)
               bpm1 = xbpm3.sumX.value
               sample_id(user_name="SR", sample_name=name_fmt.format(..., bpm="%1.3f"%bpm1))
               yield from bp.count(dets, num=1)
   ```
   - Some NEXAFS variants use `bp.rel_scan(dets, stage.y, *ypos)` (small y-sweep per energy) and `bp.scan(..., energy, ...)`, but still one run per (sample, energy).
5. **Notable techniques/hardware:** coarse Ca/Zn/La edge grids vs fine across-edge steps; arc up/down SAXS-y offsets for tiling; `xbpm2.sumX<50` beam-loss re-move guard; SmarAct-vs-hexapod fallback branches; offline-hydrated sample naming convention. No decorators/Signals.
6. **Intent:** Multi-edge resonant tender SWAXS/NEXAFS + microfocus mapping on organic-electronic / SAM / organic-acid films; canonical legacy energy×position raster.

---

## 3. 30-user-Chaney.py
1. **Size / plans:** ~70 KB, ~19 `def`s (`swaxs_S_edge_*`, `waxs_S_edge_chaney_*`, `temp_series`, pump helpers).
2. **User/group:** Chaney / Gomez-adjacent (`CM`,`GS`,`Chaney`,`chris`); OPV donor/acceptor polymers (PM6/PM7, ITIC, P25 TiO2).
3. **Use-cases:** **tender S K-edge (~2445–2560 eV) resonant SWAXS** in transmission (fine 0.25 eV steps across edge), **S-edge resonant GIWAXS** (`giwaxs_S_edge_chaney_*` with alignment), **S-edge liquid-cell** flow SAXS (`*_liquidcell_*` with syringe pump), and **in-situ temperature ramping/kinetics** (`temp_series`: Linkam `LThermal` ramp + hold + measure) coupled with **solvent oscillation** (syringe-pump infuse/withdraw per frame to refresh solution / mitigate beam damage). `prs`-various studies (`variousprs`).
   - **Detectors:** `pil900KW`+`pil2M`; conditional `[pil900KW] if wa<10 else [pil900KW,pil2M]`.
4. **Acquisition pattern: LEGACY.** Energy/temperature loops with per-point `bp.count`; temperature read into both filename AND `RE.md['temp']` (global), bpm via `.get()`; fresh-spot y-meshgrid anti-damage rastering:
   ```python
   for e, xsss, ysss in zip(energies, xss, yss):
       yield from bps.mv(energy, e); yield from bps.sleep(2)
       yield from bps.mv(piezo.y, ysss); yield from bps.mv(piezo.x, xsss)
       sample_id(user_name="CM", sample_name=name_fmt.format(..., xbpm="%4.3f"%xbpm3.sumX.get()))
       yield from bp.count(dets, num=1)
   # temp_series: RE.md['temp'] = LThermal.temperature(); yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** Linkam `LThermal` (setTemperature/Rate, `status_code` bit-2 stable-wait), `syringe_pu` (dir/go/stop_flow) per-frame infuse/withdraw oscillation, `SMIBeam().insertFoils("Alignement"/"Measurement")` attenuator presets, `pil2M_bs_rod.mv_in` beamstop choreography per frame, energy-dropout re-issue guard. Helper `set_pump_rate`/`set_pump_vol` plans.
6. **Intent:** Resonant S-edge transmission/GI SWAXS on OPV blends plus in-situ Linkam-temperature + flow-cell kinetics; legacy energy/temperature raster with rich in-vacuum/pump hardware sequencing.

---

## 4. 30-user-Ferron.py
1. **Size / plans:** ~36 KB; `def` count not enumerated (large coordinate tables; representative plan `alice_grid_scans_2022_3`). Derived from `30-user-Telles.py`.
2. **User/group:** Ferron / Alice Ferron (`AF`); proposal 311050_Fergerson. Polymer thin-film (shear/draw/anneal) processing study.
3. **Use-cases:** **microfocus raster mapping** of processed polymer films — transmission SAXS over a 41×41 (10 µm step) grid per sample, multiple sample rows (A–G) with per-sample shear/draw/anneal metadata. WAXS parked out of the way (transmission-SAXS-only).
   - **Detectors:** `pil2M` (SAXS).
4. **Acquisition pattern: MIXED (relatively good legacy).** Outer sample loop, but the actual mapping is a single coordinated `bp.rel_grid_scan` per sample (one run per map, not per pixel), AND it passes structured `md=user_dict` (shear/draw/anneal/ranges) — partially modern metadata practice. Filename still via `sample_id`, energy/sdd via `.position`:
   ```python
   user_dict = {'sample name':name, 'shear':sh, 'draw':dr, 'annealed':ann, 'user_macro':macro_user_name, 'x_range':x_range, 'y_range':y_range}
   yield from bps.mv(piezo.x, x, piezo.y, y, stage.y, h_y)
   e = energy.position.energy/1000; sdd = pil2M_pos.z.position/1000
   sample_id(user_name="AF", sample_name=name_fmt.format(...))
   yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0, md=user_dict)
   ```
5. **Notable techniques/hardware:** per-sample experimental factors (shear rate, draw ratio, anneal bool) carried as md; hexapod `stage.y` coarse height + `piezo` fine; arc-park guard `if waxs.arc.position<19.5: mv(waxs,20)`; extensive commented row A–G coordinate libraries. No decorators/Signals; grid-scan + md is the modern-leaning element.
6. **Intent:** Processing-structure mapping (shear/draw/anneal vs morphology) by transmission micro-SAXS grids; good candidate for the modern template since it already uses grid_scan + md.

---

## 5. 10-user-Beaucage.py  *(NOTE: `10-` prefix = older/infrastructure-convention file)*
1. **Size / plans:** ~31 KB, ~30 `def`s. The `10-` prefix (vs `30-user-`) marks it as an older-convention macro that also *defines* shared GI-alignment infrastructure (`alignBoc`, `alignmentmodeBoc`, `GV7` device, ROI PV strings) rather than being purely a user run file.
2. **User/group:** Beaucage / Peter Beaucage (`PB`,`PT`,`BP`); NIST. Membrane / block-copolymer (Dow/SWC, SVPS-PEO/P2VP) program.
3. **Use-cases:** **resonant GIWAXS at Br/Rb edges** (energy arcs ~13450–13550 eV Br, ~15150–15275 eV Rb), **tender NEXAFS** (`nexafs_scan` energy sweeps), **GISAXS incident-angle series**, **transmission resonant SAXS/WAXS** of ion-exchanged membranes (RbBr/RbCl/NaBr/NaCl salt series), **transmission SAXS mapping** (`run_saxsmapBoc`), and an **in-situ GIWAXS heating/time-series** (`heatingLoop` with `ls.ch1_read` temperature, continual re-align + x-walk anti-damage). Many time-of-day "campaign" wrappers (`afterlunchrun`, `mondaynightmaps`).
   - **Detectors:** `pil300KW`+`pil2M`; `rayonix` (MAXS) in `run_giwaxsBocBulk`; `pil300kwroi2` for NEXAFS.
4. **Acquisition pattern: LEGACY (with self-defined alignment infra).** Sample loop → align → angle/energy loop → `bp.scan(dets, waxs, *waxs_arc)` (a real arc-scan, one run per condition); energy moves wrapped in suspender remove/install; temperature via `.value`:
   ```python
   for x, sample in zip(x_list, sample_list):
       yield from bps.mv(piezo.x, x); yield from alignement_gisaxs(0.1)
       for k, e in enumerate(energy_arc_waxs):
           yield from remove_suspender(susp_xbpm2_sum); yield from bps.mv(energy, e); yield from bps.sleep(10); yield from install_suspender(susp_xbpm2_sum)
           sample_id(user_name="PB", sample_name="{sample}_{th:5.4f}deg_{e:5d}eV_{num}".format(...))
           yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable techniques/hardware:** defines `GV7` TwoButtonShutter + `alignBoc`/`alignBocBulk` (ROI-Y reflectivity-tracking GI alignment) reused by other files; `susp_xbpm2_sum` beam-current suspender toggled around DCM energy moves; `SMIBeam().insertFoils` in-vac attenuators; waxs-arc snake-stitch (`waxs_arc[1],waxs_arc[0]=...`); x-walk + periodic re-align in `heatingLoop`; ROI PV strings exposed. `counter%n is 0` (identity-compare bug, not in scope).
6. **Intent:** Resonant (Br/Rb-edge) GIWAXS/NEXAFS + ion-exchanged-membrane transmission SWAXS, doubling as the SMI GI-alignment-infrastructure source; thoroughly legacy run bodies built on shared align primitives.

---

## 6. 30-user-SWong.py
1. **Size / plans:** ~18 KB, ~25 `def`s (mostly thin `measure_*`/`run*` wrappers + huge commented run-history).
2. **User/group:** S. Wong (`SS` Sunita guest); proposal 309075. Surfactant-templated nanowire/nanoparticle (Pt, CTAB/DTAB/KBr) synthesis.
3. **Use-cases:** **in-situ time-series / reaction kinetics** via *ex-situ capillary bar* of timepoints (CTAB_rxn_5min…480min, washes) — transmission SAXS + WAXS at arc 0/20/40; **multi-sample capillary bar**; **AgBH calibration**; capillary-diameter (1/2/3 mm) series. 16.1 keV.
   - **Detectors:** `pil900KW`+`pil300KW` (WAXS), `pil2M` (SAXS); combined at max arc angle.
4. **Acquisition pattern: RE()-in-loop (worst legacy sub-mode) + LEGACY generators.** Driver `run*`/`measure_series_*` are plain functions calling `RE()` per point; the underlying `measure_waxs/saxs/wsaxs` are generators with `RE.md['sample']` filenames:
   ```python
   def measure_series_waxs(t=[1], waxs_angle=0, dys=[...]):
       for k in list(sample_dict.keys()):
           mov_sam(k)                       # mov_sam itself calls RE(bps.mv(...)) and sets RE.md['sample']
           for dy in dys:
               for ti in t:
                   RE(measure_waxs(t=ti, waxs_angle=waxs_angle, att='None', dy=dy))
   ```
   - `measure_waxs_loop_sample` (a partial generator refactor) is present but buggy (`for pos in ks: mov_sam(k)` undefined `k`; `waxs_angle_array` undefined) — evidence of an abandoned migration.
5. **Notable techniques/hardware:** dict-based `sample_dict`/`pxy_dict` position bookkeeping; `dys` y-offset list for fresh-spot/multi-shot; `mov_sam` mutates `RE.md`; `measure_pindiol_current` (`pdcurrent1.value`) transmission; manual per-arc snake. No decorators/Signals.
6. **Intent:** Surfactant nanowire-synthesis kinetics by capillary-bar transmission SWAXS; textbook RE()-in-loop anti-pattern with mutable global sample state.

---

## 7. 30-user-SWong2.py
1. **Size / plans:** ~21 KB, ~24 `def`s (near-duplicate of SWong.py; different sample bars).
2. **User/group:** S. Wong (`SS`); proposal 309075_SWong2. Same Pt/CTAB/KBr nanowire chemistry, SAXS distance 1.8 m.
3. **Use-cases:** identical to SWong.py — **reaction-kinetics timepoint capillary bar** (KBr/CTAB 30s…480min), **multi-sample bar**, **AgBH calibration**, capillary-diameter series, Cu-dilute/concentrate (`FL_Cu*`). Transmission SAXS+WAXS.
   - **Detectors:** `pil900KW`+`pil300KW`, `pil2M`.
4. **Acquisition pattern: RE()-in-loop + LEGACY.** Same structure as SWong.py:
   ```python
   def measure_series_swaxs_one_sample(sam_pos=1, dys=[0]):
       mov_sam(sam_pos)
       for dy in dys:
           RE(measure_wsaxs(t=1, waxs_angle=20, att='None', dy=dy))
   ```
   - Same broken partial-refactor `measure_waxs_loop_sample`.
5. **Notable techniques/hardware:** as SWong.py — `sample_dict`/`pxy_dict`, `RE.md['sample']`, `dys` offsets, pin-diode current. Heavy stacked-and-overwritten `sample_dict` reassignments documenting successive bars in-file.
6. **Intent:** Sibling of SWong.py for the 1.8 m-SAXS nanowire-kinetics runs; same RE()-in-loop legacy idiom.

---

## 8. 30-user-XZhang2.py
1. **Size / plans:** ~15 KB, ~35 `def`s (utility-heavy; `measure_*`, `do_one_map`, helpers).
2. **User/group:** X. Zhang / H. Zhang (`XZ`,`HZ`); guests YG, Dinca (MOF powders). Biopolymer / natural-fiber (chitin/chitosan/cellulose/wood) + MOF powder scattering.
3. **Use-cases:** **transmission WAXS/SAXS of biopolymers & powders** (chitin, cellulose, Cu-loaded fibers), **microfocus SAXS mapping** (`measure_saxs_map`, `do_one_map`: x×y grids + y-line scans), **Al2O3 / AgBH standards**, **chi-rotation** (fiber-texture) measurements, multi-angle WAXS arc series.
   - **Detectors:** `pil900KW`+`pil300KW` (WAXS), `pil2M` (SAXS); `pil2Mroi2-4` ROI streams.
4. **Acquisition pattern: RE()-in-loop + LEGACY generators (mixed within file).** Map/driver functions call `RE()` in `for` loops; the `measure_saxs_map`/`measure_saxs`/`measure_waxs` are generators using `RE.md['sample']`:
   ```python
   def measure_Al2O3():
       for wa in WA:
           for pz in pz_list:
               RE(bps.mv(piezo.z, pz))
               RE(measure_waxs(t=1, waxs_angle=wa, att='None', dy=0, sample=sample+'_PZ_%.0f'%piezo.z.position))
   # measure_saxs_map: nested px/py for-loops, per-point sample_id + bp.count(dets,num=1)
   ```
5. **Notable techniques/hardware:** `sample_dict`/`pxy_dict`; `mov_sam`/`name_sam` mutate `RE.md`; fresh-spot trial commentary ("NO peaks beam damage?"); chi rotation for fiber texture; `pdcurrent1` transmission. Both RE()-in-loop drivers and clean generator-map plans coexist (transitional, leaning legacy).
6. **Intent:** Biopolymer-fiber & MOF-powder transmission SWAXS + SAXS micro-mapping; mixed RE()-in-loop / nested-`bp.count` legacy with beam-damage-aware spot hunting.

---

## 9. 30-user-Andrew.py
1. **Size / plans:** ~13 KB, 7 `def`s.
2. **User/group:** Andrew / Patryk-adjacent (`PT`,`GF`); proposal-internal "sampleNN". Conjugated-polymer / organic thin films.
3. **Use-cases:** **GIWAXS multi-sample bar** (incident-angle 0.08–0.2°, waxs-arc tiling), **GIWAXS + temperature** (`Andrew_temp_2021_1`: Lakeshore ramp at 105/145/190 °C with re-align per setpoint), **AgBH waxs calibration** (`waxs_andrew_2022_1`), plus a full SMI-object alignment workflow (`SMI_Beamline().modeAlignment/modeMeasurement`).
   - **Detectors:** `pil300KW`/`pil900KW` (WAXS); SAXS not used.
4. **Acquisition pattern: LEGACY.** Align all samples → store incident angles/heights in globals → nested waxs×sample×angle loops with per-point `bp.count`; temperature via `ls.input_A.value`/`.get()` into filename:
   ```python
   t_kelvin = t + 273.15; yield from ls.output1.mv_temp(t_kelvin)
   while abs(ls.input_A.get()-t_kelvin) > 1: yield from bps.sleep(10)
   for wa in waxs_arc:
       yield from bps.mv(waxs, wa)
       for name, xs_piezo, ys_piezo, aiss in zip(names, x_piezo, y_piezo_aligned, incident_angles):
           ... for num, an in enumerate(angle):
               yield from bps.mv(piezo.th, aiss+an); yield from bps.mv(piezo.x, xs_piezo-num*300)
               sample_id(user_name="PT", sample_name=name_fmt.format(..., temperature="%3.1f"%t))
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `SMI_Beamline()` mode objects; per-angle x-walk (`xs-num*300`) anti-damage; `global names/x_piezo/incident_angles/y_piezo_aligned` shared between align and measure plans (fragile); hexapod `stage.x` + `piezo` GI geometry; `ls.output1.mv_temp`. No decorators/Signals.
6. **Intent:** Multi-sample GIWAXS + thermal-annealing on organic films; legacy nested GI loop with global align-state and temperature-into-filename.

---

## 10. 30-user-Kim3.py
1. **Size / plans:** ~14 KB, ~5 `def`s; dominated by a giant commented run-log + stacked sample/position lists (74-sample June-2021 campaign).
2. **User/group:** Kim (`Kim`, guest `ABosc`/`Dennis`/`Anibal`); proposal 304841/308651_Kim. Thin-film GIWAXS user.
3. **Use-cases:** **GIWAXS multi-sample bar** (`run_giwaxs_Kim`) — incident-angle triplets, waxs-arc array to ~6.76 A⁻¹ (q reach annotated), x-shift multi-spot averaging, alternating arc-direction snake; SAXS added only at max arc. 16.1 keV.
   - **Detectors:** `pil300KW` (WAXS) + `pil2M` (SAXS at max arc).
4. **Acquisition pattern: LEGACY.** Sample loop → `alignement_gisaxs` → waxs×x-position×angle nested loops, per-point `bp.count`; `RE.md['scan_id']` into filename:
   ```python
   for waxs_angle in Waxs_angle_array:
       yield from bps.mv(waxs, waxs_angle)
       dets = [pil300KW, pil2M] if waxs_angle==max_waxs_angle else [pil300KW]
       for x_meas in x_pos_array:
           yield from bps.mv(piezo.x, x_meas)
           for i, th in enumerate(th_meas):
               yield from bps.mv(piezo.th, th)
               sample_id(user_name=username, sample_name=name_fmt.format(..., scan_id=RE.md["scan_id"]))
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** module-level `x_list`/`sample_list` (repeatedly overwritten per bar — last-assignment-wins global state); `mov_sam`/`check_saxs_sample_loc` use bare `RE(...)`; waxsP/waxsN naming encodes arc-sweep direction; q-reach comments tie arc steps to detector stitching; per-sample alternating `inverse_angle` snake. No decorators/Signals.
6. **Intent:** High-throughput multi-bar GIWAXS thin-film survey; legacy nested GI loop driven by mutable module-global sample tables.

---

## 11. 30-user-Fergerson.py
1. **Size / plans:** ~7 KB, 1 plan (`alice_grid_scans_2022_3`). (Companion to Ferron.py / Telles.py lineage — note near-identical Fergerson/Ferron proposal IDs 311050.)
2. **User/group:** Fergerson / Alice (`AF`); proposal 311050_Fergerson. Polymer thin-film shear/draw/anneal study.
3. **Use-cases:** **microfocus raster mapping** — transmission SAXS grids (rows A–G of sheared/drawn/annealed films), WAXS parked out. Essentially the same experiment as Ferron.py.
   - **Detectors:** `pil2M` (SAXS).
4. **Acquisition pattern: MIXED (good legacy — identical to Ferron.py).** Per-sample single `bp.rel_grid_scan` (one run per map) with structured `md=user_dict`:
   ```python
   user_dict = {'sample name':name, 'shear':sh, 'draw':dr, 'annealed':ann, 'user_macro':macro_user_name, 'x_range':x_range, 'y_range':y_range}
   sample_id(user_name="AF", sample_name=name_fmt.format(sample=name, energy=..., sdd=..., dy=dy, dx=dx))
   yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0, md=user_dict)
   ```
5. **Notable techniques/hardware:** shear/draw/anneal factors as md; computed dy/dx step encoded in filename; arc-park guard; rich commented A–G coordinate libraries; docstring documents proposal/load workflow. No decorators/Signals; grid_scan+md modern-leaning.
6. **Intent:** Processing-structure micro-SAXS mapping of shear/draw/annealed polymer films (Ferron sibling); already uses grid_scan + md, prime modern-template candidate.

---

## 12. 30-user-RLi.py
1. **Size / plans:** ~6 KB, ~12 `def`s.
2. **User/group:** R. Li (`RL`); Yale (`snapYale`,`ROI_yale`). Resonant grazing-incidence organic-electronic films; reuses Cai's GI-align suite.
3. **Use-cases:** **resonant GISAXS/GIWAXS near S-edge** (energies 2460–2500 eV), incident-angle offset series with per-energy x-walk anti-damage; **GI alignment** (`alignCai` suite: ROI-Y specular tracking, height/th iterations). Records xbpm sums.
   - **Detectors:** `pil300KW`/`pil2M` (+ `pil300kwroi2`, `xbpm3.sumY`, `xbpm2.sumY` as channels) — bpm/ROI folded into detector list (good).
4. **Acquisition pattern: MIXED.** `do_grazing` uses a coordinated `bp.inner_product_scan` (waxs + piezo.x stepped together — one run per angle/energy, with xbpm channels recorded); `do_grazing_fine` reverts to per-point `bp.count`:
   ```python
   dets = [pil2M, pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]
   for i_e, e in enumerate(e_list):
       yield from bps.mv(energy, e)
       for j, ang in enumerate(a_off - np.array(angle_offset)):
           yield from bps.mv(piezo.th, ang)
           sample_id(user_name="RL", sample_name=name_fmt.format(sample=name, angle=real_ang, energ=e))
           yield from bp.inner_product_scan(dets, int(waxs_arc[2]), waxs, ..., piezo.x, x_offset-600, x_offset+600)
   ```
5. **Notable techniques/hardware:** `alignCai`/`alignmentmodeCai` (ROI1 min_y specular-band tracking, `att2_11` insert/retract, `pil2M_bs_rod` beamstop swap between align/measure positions); xbpm sums as recorded detectors; per-energy x-offset fresh-spot stepping. Filename via `sample_id` only (no bpm-into-name). No decorators/Signals.
6. **Intent:** Resonant S-edge GI scattering on organic films with reused Cai GI-alignment; mixed inner_product_scan (good) + per-point count (legacy).

---

## 13. 30-user-Murray.py
1. **Size / plans:** ~6 KB, 3 `def`s.
2. **User/group:** Murray / E. Murray (`EM`,`EM_insitu`). Colloidal-nanocrystal (PbS, Fe3O4, FICO) superlattice / SDS-templated assembly.
3. **Use-cases:** **multi-sample capillary bar transmission SAXS** (`ex_situ`: PbS/Fe3O4 binary mixtures), **in-situ time-series / kinetics** (`in_situ`: 50000-iteration loop over a 4-sample bar at 70 °C, timestamped filenames) of SDS-emulsion superlattice formation, with an error-retry self-wrapper.
   - **Detectors:** `pil2M` (SAXS); `pil300KW` added in-situ.
4. **Acquisition pattern: LEGACY.** Nested `for ii in range(50000): for y,sample in zip(...)` → per-point `bp.count`; positions/sdd/time/scan_id via `.position`/`RE.md` into filename:
   ```python
   for ii in range(50000):
       for y, sample in zip(y_list, sample_list):
           yield from bps.mv(piezo.y, y); det_exposure_time(meas_t, meas_t)
           sample_name = name_fmt.format(sample=sample, x_pos=np.round(piezo.x.position,2), ..., t=np.round(time.time()-t0,0), scan_id=scan_id0+count)
           sample_id(user_name="EM_insitu", sample_name=sample_name)
           yield from bps.sleep(1); yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** manual elapsed-time `t=time.time()-t0` into filename (no time device); `in_situ_wrap` try/except-recurse fault tolerance; flow-cell heating noted in trailing comments (20 ml/min, 70 °C). No decorators/Signals.
6. **Intent:** Colloidal-nanocrystal binary superlattice assembly kinetics by capillary-bar transmission SAXS; legacy infinite-loop time-series with timestamp-in-filename.

---

## 14. 30-user-Luo.py
1. **Size / plans:** ~4 KB, 1 plan (`mapping_Luo`).
2. **User/group:** Luo / A. Luo (`AL`); proposal 307948_Luo. Sequence-defined / block polymer (TMA, iPrMeP statistics) thin films.
3. **Use-cases:** **microfocus raster mapping** with **waxs-arc series per map** — transmission SAXS (`pil2M`) + WAXS (`pil300KW`) grids (21×101, 500 µm) at each of 3 arc positions per sample. 16.1 keV.
   - **Detectors:** `pil300KW`+`pil2M`.
4. **Acquisition pattern: MIXED (legacy with grid_scan core).** Sample loop → arc loop → single `bp.rel_grid_scan` per (sample, arc) — one run per map. Filename via `sample_id`; also sets detector `file_path` PVs directly (legacy folder routing):
   ```python
   pil2M.cam.file_path.put("/nsls2/.../1M/%s" % sample)
   for wa in np.linspace(wax_ra[0], wax_ra[1], wax_ra[2]):
       yield from bps.mv(waxs, wa)
       yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y+500)
       sample_id(user_name=user, sample_name=name_fmt.format(sam=sample, waxs="%2.1f"%wa))
       yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)
   ```
5. **Notable techniques/hardware:** direct `cam.file_path.put` per-sample subfolders (bypasses sample_id routing); per-sample x/y/z/range/arc parallel lists with asserts; `proposal_id` switch on first sample. No decorators/Signals; grid_scan modern-leaning.
6. **Intent:** Block/sequence-polymer thin-film SWAXS micro-mapping with arc tiling; legacy framing around grid_scan, with manual file-path routing.

---

## 15. 30-user-IIT.py
1. **Size / plans:** ~3 KB, 1 plan (`mesh_IIT_2022_1`).
2. **User/group:** IIT / J. O (`JO`); proposal 310511_Zhernenkov (Wang). Large-area GISAXS samples.
3. **Use-cases:** **microfocus raster mapping (GISAXS)** — `bp.rel_grid_scan` mesh over piezo.y×piezo.x per large-area sample, waxs-arc 0/20, SAXS+WAXS. 16.1 keV, 3 m SAXS.
   - **Detectors:** `pil900KW` (WAXS), `pil2M` + `pil2Mroi2/3/4` (SAXS with ROI streams).
4. **Acquisition pattern: MIXED (legacy with grid_scan core).** Sample loop → arc loop → single `bp.rel_grid_scan` per (sample, arc); `proposal_id`/`sample_id` for routing:
   ```python
   for wa in waxs_range:
       dets = [pil900KW] if wa<10 else [pil900KW, pil2M, pil2Mroi2, pil2Mroi3, pil2Mroi4]
       yield from bps.mv(waxs, wa)
       proposal_id("2022_1", "310511_Zhernenkov/%s" % sample)
       sample_id(user_name=name, sample_name=name_fmt.format(sam=sample, waxs="%2.1f"%wa))
       yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)
   ```
5. **Notable techniques/hardware:** per-sample x/y/z/chi/hexapod-y + per-sample mesh-range parallel lists with asserts; ROI sub-detectors as live channels; arc-conditional SAXS-drop. No decorators/Signals; grid_scan modern-leaning.
6. **Intent:** Large-area GISAXS mesh mapping; compact legacy grid_scan-per-sample plan.

---

## 16. 30-user-Gill.py
1. **Size / plans:** ~2 KB, 2 `def`s.
2. **User/group:** Gill / S. Gill (`SG`). Grazing-incidence WAXS, cellulose/"CEll" sample (overnight RT).
3. **Use-cases:** **GIWAXS multi-condition** — incident-angle list (0.12–0.40°) × waxs-arc (0/20/40) per sample, plus a y-stepped **background** plan (`gill_giwaxs_bkg`). Uses `alignement_gisaxs_hex` (hexapod GI align) gated by `GV7` open/close.
   - **Detectors:** `pil300KW`+`pil900KW` (WAXS).
4. **Acquisition pattern: LEGACY.** x → align → waxs × angle nested loops, per-point `bp.count`; filename via `sample_id`:
   ```python
   yield from alignement_gisaxs_hex(angle=0.2)
   ai_0 = stage.th.position
   for wa in waxs_arc:
       yield from bps.mv(waxs, wa)
       for incident_angle in inc_angle:
           yield from bps.mv(stage.th, ai_0 + incident_angle)
           sample_id(user_name="SG", sample_name=name_fmt.format(sample=name, pos=..., angle=..., wa=...))
           det_exposure_time(exp_time, exp_time); yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `GV7` gate-valve open/close bracketing alignment (in-vac SAXS protection); hexapod `stage.x/y/th` GI geometry (no piezo); y-step background series. No decorators/Signals.
6. **Intent:** Small GIWAXS angle/arc survey + background on a cellulose film; minimal textbook legacy GI loop.

---

## BATCH SYNTHESIS

- **Dominant archetype = legacy nested-loop GIWAXS multi-sample bar** (Andrew, Kim3, Gill, Gomez_Sintu `giwaxs_*`, Beaucage GI, Chaney GI): `for sample → align → for waxs → for angle → bp.count(dets, num=1)` with `sample_id(...)` filenames and `stage.x` hexapod + `piezo.th` fine geometry. This is the single most common pattern across the batch and the clearest target for the decorated-`inner()` template.

- **Tender resonant edge work is heavily represented and uniformly legacy:** S K-edge (~2470–2480 eV: Chaney, RLi, Gomez_Sintu S), Ca/Zn/La edges (Gomez_Sintu), and Br/Rb edges (~13.5/15.2 keV: Beaucage). All use `for e in energies: mv(energy,e); sleep; bp.count`, read `xbpm2/3.sumX` via `.get()`/`.value` into filenames, and add fresh-spot y/x rastering to fight beam damage — exactly the context-into-string anti-pattern the modern template removes by recording `energy`/`xbpm` devices.

- **A distinct, worse-than-legacy sub-mode — `RE()`-inside-Python-loops — clusters in the nanoparticle/biopolymer transmission files** (SWong, SWong2, XZhang2). Driver functions are not generators; they call `RE(measure_*())` per point and carry `RE.md['sample']` mutable state via `mov_sam`. These also contain abandoned half-refactors (`measure_waxs_loop_sample` with undefined `k`/`waxs_angle_array`), signaling incomplete migration.

- **The microfocus raster-mapping cohort is the "best legacy"** (Ferron, Fergerson, Luo, IIT, Beaucage maps): each sample maps via a single coordinated `bp.rel_grid_scan` (one run per map, not per pixel). Ferron/Fergerson additionally pass structured `md=user_dict` (shear/draw/anneal) — the only files in the batch already doing dict-metadata — making them the readiest modern-template candidates.

- **Kline2 (CD-SAXS) is the standout in-file migration exemplar:** legacy `cd_saxs()` (per-phi `bp.count` + CSV side-log + `sample_id`) coexists with transitional `cd_saxs_modern()`/`x_scan()` that do one `bp.list_scan` per phi-rock and fold `piezo.x/y/z`, `pil2M.sample_distance_mm`, `stage_pseudo`, `xbpm3.sumX` into the detector list as recorded channels (with a `{stage_phi_real}` filename placeholder). It is the closest to modern but still lacks `@bpp.run_decorator`/`stage_decorator`.

- **In-situ kinetics / temperature ramping appears in several flavors, all legacy:** Linkam `LThermal` flow-cell with per-frame syringe-pump infuse/withdraw oscillation (Chaney `temp_series`), Lakeshore `ls` annealing with per-setpoint re-align (Andrew), `ls.ch1_read` GI heating with x-walk (Beaucage `heatingLoop`), and infinite-loop timestamped colloid assembly (Murray). Temperature is written into filenames and/or `RE.md['temp']` rather than recorded as a baseline/streamed device.

- **MODERN (full decorated `run_decorator`+`stage_decorator`+`trigger_and_read`) pattern is ENTIRELY ABSENT** in this batch — zero hits for `bpp.`/`run_decorator`/`trigger_and_read`/`declare_stream`/`Signal(`. The most advanced practice present is "one-run-per-scan via `list_scan`/`grid_scan`/`inner_product_scan` with readbacks recorded as detector channels" (Kline2 modern, RLi `do_grazing`, the mapping cohort).

- **Prevalence tally (16 files): pure LEGACY ≈ 7** (Andrew, Kim3, Gill, Gomez_Sintu, Chaney, Beaucage, Murray); **RE()-in-loop legacy ≈ 3** (SWong, SWong2, XZhang2); **MIXED/transitional ≈ 6** (Kline2, Ferron, Fergerson, Luo, IIT, RLi); **MODERN = 0**. Migration maturity correlates with technique: CD-SAXS and micro-mapping are furthest along; resonant-edge and capillary-kinetics files are least migrated.

- **Cross-cutting hardware vocabulary:** arc-conditional detector lists (`[pil900KW] if waxs<10/15 else [..., pil2M]`) are near-universal; `xbpm2.sumX<50` beam-loss re-move guards (Chaney, Gomez_Sintu); `susp_xbpm2_sum` suspender toggling around DCM moves (Beaucage); `SMIBeam().insertFoils`/`att2_*` attenuator presets and `pil2M_bs_rod`/`GV7` beamstop+gate-valve choreography for GI in-vacuum protection (Beaucage, Chaney, RLi, Gill); `rayonix` (MAXS) only in Beaucage bulk-GIWAXS. Shared GI-alignment primitives (`alignBoc`, `alignCai`, `alignement_gisaxs*`, `SMI_Beamline().mode*`) are imported across files — Beaucage's `10-` file is partly their definition source.

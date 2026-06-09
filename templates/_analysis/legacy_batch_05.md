# Legacy Bluesky/Ophyd Plan Analysis — Batch 05 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 14 legacy
user macro files. Detectors: `pil2M` = SAXS (Pilatus 1M/2M), `pil900KW`/`pil300KW` =
WAXS (arc-mounted in-vacuum), `rayonix` = MAXS, `xbpm2/3` = beam-position monitors,
`ls` (Lakeshore) / `LThermal` (Linkam) = temperature controllers. `waxs.arc` (a.k.a. `waxs`)
and `stage.phi`/`piezo.th` are slow / in-vacuum axes. Goniometry split between `piezo.*`
(fast nano-stage: x/y/z/th) and `stage.*`/hexapod (coarse). Energy via `energy` (DCM)
for tender/edge work.

Pattern legend: **LEGACY** = nested `for` loops, each iteration calls
`bp.count`/`bp.scan` → one Bluesky run per data point; filenames via global mutable
`sample_id(...)`/`RE.md`; context read via `.value`/`.get()` into strings.
**MODERN** = `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)` around `inner()`
with `bps.trigger_and_read(dets + [signals])`. **MIXED** = both present, often a
documented migration in progress.

---

## 1. 30-user-Su.py
1. **Size / plans:** ~178 KB, ~95 `def`s (largest file; ~5 yrs of accreted plans 2021→2026).
2. **User/group:** Su / Greg Su group (`GF`,`JJS`,`ML`,`GS`,`CM`,`GP` operators) — PFSA/Nafion ionomer & conjugated-polymer electronic-materials program; also services many guest groups (MRL, Kelvin, Jose, Pierre, Yunfei, Matt).
3. **Use-cases:** tender-energy **NEXAFS** (S K-edge ~2472 eV, Cl, K, Co, Fe, Ce L3, Zr L3, Ti, Ag, Se, Br, As, Mn, Zr edges), **resonant SWAXS** at edges, **transmission hard-Xray SAXS/WAXS** (16.1 keV capillaries/MRL), **GIWAXS/GISWAXS** (in-vacuum), **XRR**, **humidity/RH** GISAXS (dry/wet MFC flow + `readHumidity`), **in-situ blade-coating** (syringe pump + Thorlabs translator), **temperature ramp** (Linkam `LThermal` `temp_series`), **XPCS** (long single-frame exposure).
   - **Detectors:** `pil900KW`+`pil2M` (edge SWAXS), `pil300KW` (older WAXS), conditional `[pil900KW] if waxs<10 else [pil900KW,pil2M]`.
4. **Acquisition pattern: MIXED → clearest evolution case in the batch.**
   - LEGACY core (2021–2024): dense energy×position raster with per-point `bp.count`, bpm into filename:
     ```python
     for e, xsss, ysss in zip(energies, xss, yss):
         yield from bps.mv(energy, e); yield from bps.sleep(2)
         bpm = xbpm2.sumX.value
         sample_id(user_name="GF", sample_name=name_fmt.format(...,xbpm=bpm))
         yield from bp.count(dets, num=1)
     ```
   - MODERN (2025–2026, e.g. `swaxs_S_edge_nafion_2026_1`, `single_scan_giwaxs`): target filename as a `Signal`, single run:
     ```python
     s = Signal(name='target_file_name', value='')
     @bpp.stage_decorator(dets)
     @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
     def inner():
         ... s.put(sample_name)
         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
     ```
   - `temp_series` is transitional: uses `Signal` but writes `RE.md["sample_name"]` globally.
5. **Notable techniques/hardware:** spread-out NEXAFS energy grids (fine 0.25 eV step across edge); fresh-spot anti-beam-damage rastering (`np.linspace(ys, ys+1500, len(energies))`); attenuator ladders; `set_energy_cam` for detector flatfield vs energy; `syringe_pu`, `thorlabs_su`, MFC dry/wet, `LThermal` Linkam; experimental `multi_scan`/`factory` (multi-run sub-document) prototypes.
6. **Intent:** Master beamline macro for resonant tender-edge SWAXS/NEXAFS + GI + in-situ environments on ionomers/OPV materials; actively being migrated from per-point legacy counts to single-run decorated streams.

---

## 2. 30-user-Gu.py
1. **Size / plans:** ~75 KB, ~25 `def`s.
2. **User/group:** Gu / shared temperature-program file (operators `YW`,`GF`, Wang, Guorong, Yunfei) — soft-matter / polymer-solution & conjugated-polymer thermal studies.
3. **Use-cases:** dominantly **temperature ramping/annealing** (Lakeshore `ls.output1.mv_temp`, equilibration loops, `status` heating range), at both **hard X-ray (16.1 keV)** and **tender (S-edge)** energies; transmission **SAXS** (`saxs_gu_*`), **SWAXS** capillaries, **NEXAFS S-edge**. In-situ time/temperature series over multi-sample bars.
   - **Detectors:** `pil2M`, `pil900KW`, `pil300KW`; conditional SAXS-drop when arc<15.
4. **Acquisition pattern: LEGACY (uniform).** Temperature outer loop → wait-for-setpoint → sample loop → waxs loop → per-point `bp.count`; temperature read into filename:
   ```python
   yield from ls.output1.mv_temp(t_kelvin)
   while abs(ls.input_A.get()-t_kelvin) > 2.5: yield from bps.sleep(10)
   temp_degC = ls.input_A.get() - 273.15
   sample_id(user_name=user_name, sample_name=f"...{temp_degC}C...")
   yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** Lakeshore `ls` (input_A, output1.status), bs-rod position logged into name, `read_pd_current`, `turn_off_heating` cleanup. No decorators, no Signals.
6. **Intent:** Per-cycle thermal-annealing SWAXS/NEXAFS campaigns; canonical legacy temperature-into-filename pattern that the modern template should replace with a baseline `ls` device.

---

## 3. 30-user-Gann.py
1. **Size / plans:** ~49 KB, ~39 `def`s.
2. **User/group:** Gann / Eliot Gann (NIST, `EG`,`Eliot`); guest Nikhil (`NT`). Tender-resonant thin-film soft-matter.
3. **Use-cases:** **tender-energy GIWAXS / RSoXS-style NEXAFS** (S, Zn, Bi, Ti edges), **specular X-ray reflectivity (XRR)** with attenuator-laddered angle sweeps, **S-edge resonant XRR** (`xrr_sedge_2025_1`), GISWAXS on IBM polymer film series.
   - **Detectors:** `pil900KW` (+ ROI/stats4/stats1 centroid hinting for reflectometry), `pil2M` conditional.
4. **Acquisition pattern: MIXED + explicitly self-documenting migration.** Production XRR is MODERN-leaning single multi-axis scan; commented `inner()` scaffolds spell out the intended refactor verbatim:
   ```python
   # add run decorator and stage decorators here ()
   def inner():
       dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
       yield from bps.declare_stream(...)        # separate SAXS/WAXS streams
       ... yield from bp.count(dets)
       # change count to trigger_and_read(), stage list of detector, run decorator
   ```
   - XRR uses a true coordinated `bp.list_scan` over angle + 3 attenuators (good multi-axis form):
     ```python
     yield from bp.list_scan([pil900KW,...centroid_total,...total],
         piezo.th, angles0, att2_11, att11o, att2_10, att10o, att2_9, att9o)
     ```
5. **Notable techniques/hardware:** angle-dependent attenuator logic `att9/10/11(angle)`, ROI-Y tracking of specular spot vs angle (`roiy`), `set_energy_cam` per energy, detector `.stats.*.kind='hinted'` for live reflectivity curve. Rich commented alignment/position tables.
6. **Intent:** Tender resonant GIWAXS + (resonant) reflectivity on polymer films; file is a partial reference implementation of the SMI modern run-per-sample pattern (with TODO scaffolds).

---

## 4. 30-user-Herzig.py
1. **Size / plans:** ~35 KB, ~14 `def`s.
2. **User/group:** Herzig (`EH`); guest `LR`. Grazing-incidence thin-film group.
3. **Use-cases:** **GIWAXS/GISAXS** angle series (incident-angle scans 0.05–0.20°), **transmission SWAXS** of films, **S-edge NEXAFS** (`run_Herzi_Sedge`, `nexafs_herzig`, glass background). Custom alignment routines.
   - **Detectors:** `pil300KW`+`pil2M`.
4. **Acquisition pattern: LEGACY.** Custom `alignement_herzig*` then sample/waxs/angle nested loops with high-averaging `bp.count(dets, num=20)` and per-point single counts:
   ```python
   for wa in waxs_range:
       yield from bps.mv(waxs, wa)
       for ang in angl:
           yield from bps.mv(piezo.th, ai0 + ang)
           sample_id(user_name="EH", sample_name=name_fmt.format(...))
           yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** hexapod (`stage.x/y`) coarse + `piezo` fine GI geometry; arc-direction-aware `waxs_range[::-1]`; `num=20` frame averaging for weak GI signal. No decorators/Signals.
6. **Intent:** Per-cycle grazing-incidence WAXS/SAXS + S-edge NEXAFS on thin films; textbook legacy multi-sample GI loop.

---

## 5. 30-user-OGang-2024C2_Thermal.py
1. **Size / plans:** ~30 KB, ~35 `def`s (many thin wrappers + `RE_`-prefixed variants).
2. **User/group:** Oleg Gang group (`FLu`,`FLu`) — DNA / nanoparticle self-assembly lattices (melting/recrystallization).
3. **Use-cases:** **in-situ temperature kinetics — melting-point (Tm) / annealing** (slow 0.1 °C/min ramps, hold-and-measure, time-temperature series), **transmission SAXS** of superlattices, **raster sample-mapping** with anti-damage fresh-spot indexing (`getSamMap`, `i_dict` per-sample spot counter).
   - **Detectors:** `pil2M` (+`pil900KW` in map/wsaxs).
4. **Acquisition pattern: LEGACY + anti-pattern (nested `RE(...)`).** Plans are *not* generators end-to-end; they call `RE()` inside Python `for`/`while` loops and stash sample names in `RE.md`:
   ```python
   while time.time() < t0 + t_total:
       for k in ks:
           mov_sam(k); RE(bps.mv(piezo.x, pos_list[i_dict[k]%N][0]))
           sample = RE.md['sample']
           RE(measure_saxs(exposure_t, sample=sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-t0)))
           i_dict[k]+=1
       time.sleep(t_interval ...)
   ```
5. **Notable techniques/hardware:** Thermal stage abstraction `gotoT/setT/getT/startT/stopT`; per-sample position-map cycling to avoid beam damage during long thermal runs; temperature & elapsed-time baked into filename strings. Heaviest reliance on global mutable state in the batch.
6. **Intent:** Long unattended DNA-NP lattice melting/annealing SAXS with fresh-spot mapping; furthest from the modern single-run model (uses blocking `RE()` + `RE.md`).

---

## 6. 30-user-EHu_2024C2.py
1. **Size / plans:** ~19 KB, 2 in-file plans (`measure_series_multi_angle_wsaxs`, `do_line_trans_scan`) atop imported `measure_waxs/wsaxs`, `mov_sam_re`, `sample_dict` helpers.
2. **User/group:** Enyuan Hu (BNL) — GUP-311773, Li-metal-battery liquid/polymer **electrolyte** microstructure (`EHu`).
3. **Use-cases:** **transmission micro-SWAXS multi-sample bar** (5 m, in-air, ~15-sample `sample_dict`/`pxy_dict`), **multi-angle WAXS arc series** (0/15/20°), **line transmission scans** (V/H mapping across a sample, microfocus). Battery-electrolyte (in-situ-capable) program.
   - **Detectors:** `pil900KW`+`pil2M`.
4. **Acquisition pattern: LEGACY (dict-driven).** Angle→sample(dict)→dy→exposure nested loops; sample name via `RE.md["sample_name"]`; per-point `bp.count`:
   ```python
   for waxs_angle in waxs_angles:
       yield from bps.mv(waxs, waxs_angle)
       for k in ks:
           yield from mov_sam_re(k)
           RE.md["sample_name"] = sample_dict[k]
           yield from measure_wsaxs(t=ti, waxs_angle=waxs_angle, sample=sample_dict[k])
   ```
5. **Notable techniques/hardware:** `sample_dict`/`pxy_dict` coordinate registry (RUN-block commented variants); `camera`/`save_ova`/`save_hex` on-axis & hexapod snapshots; line-scan with positions formatted into filename. Header carries `proposal_id` + beam-center/SAXS-distance notes.
6. **Intent:** Microfocus transmission SWAXS survey + line-mapping of battery electrolytes across a multi-sample bar; legacy dict/`RE.md` style.

---

## 7. 30-user-NIST.py
1. **Size / plans:** ~16 KB, 7 `def`s.
2. **User/group:** NIST (`PB` = Peter Beaucage / `PT`, `BP`) — soft-matter & thin-film.
3. **Use-cases:** **temperature SWAXS series** (`tswaxs`, multi-arc 26→0°, large sample bar, `ls.ch1_read` Lakeshore), **SAXS raster mapping** (`run_saxsmapPT`, x×y meshgrid per sample), **GIWAXS S-edge** (`giwaxs_S_edge`, attenuator-switched at wa=0), **transmission WAXS S-edge**, helper `heatingLoop`.
   - **Detectors:** `pil2M`, `pil300KW` (conditional/standalone).
4. **Acquisition pattern: LEGACY.** Raster via explicit `np.linspace` double loop with per-pixel `bp.count(num=1)`; tswaxs arc-outer + sample-inner; comments admit intent (`# should just be a single point "scan"`):
   ```python
   for xrs in np.linspace(x_r[0], x_r[1], x_r[2]):
       yield from bps.mv(piezo.x, x + xrs)
       for yrs in np.linspace(y_r[0], y_r[1], y_r[2]):
           yield from bps.mv(piezo.y, y + yrs)
           sample_id(user_name=name, sample_name=f"{sample}_x{...}_y{...}")
           yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** beam-stop-aware safety (`if waxs.arc.position<6 and bsx_pos>0`), attenuator insert/retract per arc angle for S-edge, Lakeshore `ls.ch1_read`/`ch1_sp`. No decorators.
6. **Intent:** Temperature-resolved + spatial-map SWAXS and S-edge GIWAXS on thin films; legacy raster (manual meshgrid) that should become a single gridded run.

---

## 8. 30-user-Yu-Chung.py
1. **Size / plans:** ~14 KB, 5 `def`s.
2. **User/group:** Yu-Chung (`YC`, `GF`) — additive-manufacturing / printed-materials in-situ.
3. **Use-cases:** **in-situ 3D-printing scattering** (`postprint_yscan` — vertical hexapod scan through a printed part; "ex situ vertical scan"), **time-resolved kinetics** (`timeresolved`, long total exposure single multi-det frame), **2D position list-scan** SWAXS (`saxs_waxs_yuchung` via `bp.list_scan` over meshgrid), tri-detector simultaneous trigger.
   - **Detectors:** `pil300KW`+`pil2M`(+`pil900KW` for time-resolved/triggers).
4. **Acquisition pattern: MIXED-legacy.** Uses coordinated `bp.list_scan`/`bp.scan` (better than pure per-point) but still mutable `sample_id` and waxs-loop wrapper; also a raw `.put` multi-detector trigger bypassing the RE:
   ```python
   for wa in waxs_arc:
       yield from bps.mv(waxs, wa)
       dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]
       yield from bp.scan(dets, stage.y, *y_range)   # post-print z-profile
   # trigger_alldet(): pil2M.cam.acquire.put(1); pil900KW.cam.acquire.put(1); ...
   ```
5. **Notable techniques/hardware:** hexapod `stage.y` profiling of printed object; energy/SDD into filename; `trigger_alldet` ad-hoc free-run of all detectors (outside Bluesky).
6. **Intent:** In-situ / post-print SWAXS profiling and kinetics for 3D-printed materials; mix of list-scan + legacy naming + non-RE triggering.

---

## 9. 30-user-Kraus.py
1. **Size / plans:** ~13 KB, 12 `def`s.
2. **User/group:** Kraus (`AAK`,`SChan`,`RZA`) — nanoparticle / core-shell colloid (multi-core particles).
3. **Use-cases:** **transmission SAXS/WAXS/MAXS 2-D micro-mapping** (`bp.rel_grid_scan` over piezo.x×y per sample), microfocus raster (`run_saxs_kraus_micro`), single y-line scans, `waxs` arc scan; capillary/film bar.
   - **Detectors:** `pil2M` + `pil300KW` + **`rayonix` (MAXS)** simultaneously — only file in batch routinely using all three q-ranges.
4. **Acquisition pattern: MIXED (uses real grid scans, but per-sample mutable naming).** Coordinated `rel_grid_scan` is good multi-axis form; still nested in a Python sample loop with `sample_id`:
   ```python
   dets = [pil2M, pil300KW, rayonix]
   for x, y, sample, x_range, y_range in zip(x_list, y_list, samples, x_range, y_range):
       yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y)
       sample_id(user_name=name, sample_name=sample)
       yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)
   ```
   - `linkam_fast` = quick `bp.scan` over `stage.y`.
5. **Notable techniques/hardware:** three-detector SAXS+WAXS+MAXS combined acquisition; per-sample variable map dimensions/step counts; `bp.rel_scan`/`bp.scan` for line profiles.
6. **Intent:** Spatially-resolved combined SAXS/WAXS/MAXS mapping of colloidal/core-shell particle films; grid-scan based (one run per map) — relatively closer to acceptable, naming aside.

---

## 10. 30-user-QYu_2024C3_GIX.py
1. **Size / plans:** ~9 KB, 3 plans (`align_gix_loop_samples`, `run_gix_loop_wsaxs`, `insitu_tgix_samples`).
2. **User/group:** Q. Yu / P. Guo / NREL (`PGuo`,`NREL_SR`) — GIX thin-film, Au-on-Si self-assembly.
3. **Use-cases:** **GISAXS/GIWAXS (GIX) multi-sample** automated alignment + measurement loop, **multi incident-angle** sweeps (0.08–1°), **multi waxs-arc** (0/10/15°), **x-shift averaging**, **in-situ time GIX** (`insitu_tgix_samples`, run_time loop). Uses generic motor abstraction `get_motor()` (piezo vs hexapod selectable).
   - **Detectors:** `pil2M`+`pil900KW`; `get_dets(waxs_angle, mode)` helper.
4. **Acquisition pattern: LEGACY (with helper abstraction) + nested-`RE()` in alignment.** Align loop wraps `RE(...)` per sample; measurement loop is waxs→sample→x-shift→angle nested with per-point `bp.count`:
   ```python
   for waxs_angle in waxs_angle_array:
       yield from bps.mv(waxs, waxs_angle)
       dets = get_dets(waxs_angle=waxs_angle, mode=mode)
       for ii,(x,sample) in enumerate(zip(x_list,sample_list)):
           yield from bps.mv(M.th, Aligned_Dict[ii]['th'])
           for x_meas in x_pos_array:
               for th in th_meas:
                   sample_id(user_name=user_name, sample_name=name_fmt.format(...))
                   yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** pre-computed `Aligned_Dict{th,y}` per sample (align once, measure many); `get_motor()`/`get_dets()` generic device selection; `save_ova`/`save_hex` camera capture; `sample_dict`/`pxy_dict` RUN-block registry. In-situ `while time<run_time` repeat.
6. **Intent:** Automated GIX (GISAXS+GIWAXS) survey of patterned thin-film/Au-assembly samples with persisted alignment and optional in-situ time loop; legacy per-point counts behind helper functions.

---

## 11. 30-user-Francisco.py
1. **Size / plans:** ~7 KB, 10 `def`s.
2. **User/group:** Francisco / Yale (`FA`,`FA2`) — organic photovoltaic blends (PDCBT:ITIC, ASSQ).
3. **Use-cases:** **tender S/Cl-edge resonant GIWAXS** (`do_grazing`, e-list 2460–2486 eV around S K-edge), **GISAXS** with custom alignment (`alignCai`), angle-offset series, x-position averaging, beam-stop/attenuator mode switching, snap.
   - **Detectors:** `pil300KW`(+`pil300kwroi2`), `pil2M`, `xbpm2/3.sumY`.
4. **Acquisition pattern: MIXED-legacy.** One plan uses coordinated `inner_product_scan` (good), another decays to per-point `bp.count` with energy×angle×arc loops:
   ```python
   yield from bp.inner_product_scan(dets, int(waxs_arc[2]), waxs, waxs0, waxs1,
                                    piezo.x, x_offset-600, x_offset+600)
   # vs do_grazing_fine: nested e × angle × waxs_pos → bp.count(det1, num=1), mvr piezo.x 200
   ```
5. **Notable techniques/hardware:** elaborate custom GI alignment `alignCai` (ROI min-Y tracking, height/th iterative `ps()` peak/centroid, alignment-vs-measurement beam-stop modes `alignmentmodeCai`/`measurementmodeCai`, GV7 gate valve, att2_11); angle-dependent exposure (0.5 s low-arc vs 5 s high-arc); x-walk to spread dose.
6. **Intent:** Resonant tender-edge GIWAXS/GISAXS on OPV thin films with bespoke alignment; mixed coordinated-scan vs legacy count.

---

## 12. 30-user-Fang.py
1. **Size / plans:** ~6 KB, 6 `def`s.
2. **User/group:** Fang / Murray group (`EM`,`EM_insitu`,`Fang`) — nanocrystal superlattices (PbS, Fe3O4, FICO).
3. **Use-cases:** **transmission SAXS multi-sample bar** (`ex_situ`, 14 NC samples), **in-situ time-series/kinetics** (`in_situ` — infinite loop over sample y-positions, elapsed time in filename, self-restarting `in_situ_wrap`), single-shot `measure_saxs` with attenuator label.
   - **Detectors:** `pil2M` (+`pil300KW` in-situ).
4. **Acquisition pattern: LEGACY.** Per-sample `bp.count(num=1)`; `scan_id`/positions/time read into filename via `RE.md["scan_id"]`; in-situ is `for ii in range(50000)` polling loop:
   ```python
   for ii in range(50000):
       for y, sample in zip(y_list, sample_list):
           yield from bps.mv(piezo.y, y)
           sample_name = name_fmt.format(..., t=np.round(time.time()-t0,0), scan_id=scan_id0+count)
           sample_id(user_name="EM_insitu", sample_name=sample_name)
           yield from bps.sleep(1); yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** crash-resilient `try/except` recursive `in_situ_wrap`; manual `scan_id` bookkeeping; SDD/x/y/exposure formatted into names; commented bsx/saxs_z setup notes.
6. **Intent:** Ex-situ and long in-situ time-resolved transmission SAXS of nanocrystal-superlattice formation; pure legacy polling loop.

---

## 13. 30-user-Kumacheva.py
1. **Size / plans:** ~5 KB, 2 `def`s.
2. **User/group:** Kumacheva / Morozova (`SM`) — ionic-liquid polymers (PIL) thin films.
3. **Use-cases:** **temperature-ramp GISWAXS** (`morozova_giswaxs_temp_2023_2`) — Lakeshore-controlled heating bar through a 15-point thermal cycle (26→145→30 °C with up/down legs), **multi incident-angle** (0.075–0.25°), **multi waxs-arc** (0/20°), per-sample auto-align, x-walk anti-damage; `equalise_temperature` helper.
   - **Detectors:** `pil900KW` (+`pil2M` when arc≥15).
4. **Acquisition pattern: LEGACY.** temperature→sample→arc→angle nested loops with per-point `bp.count`; temperature read into filename; alignment per sample:
   ```python
   for i, temperature in enumerate(temperatures):
       yield from equalise_temperature(temperature)
       for name,x,y,z,hx in zip(...):
           yield from alignement_gisaxs()
           temp_degC = ls.input_A.get() - 273.15
           for wa in waxs_arc:
               for ai in incident_angles:
                   yield from bps.mvr(piezo.x, step_across_sample)   # fresh spot
                   sample_id(user_name='SM', sample_name=f'{name}_{temp}degC_run{i}...')
                   yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** `equalise_temperature` (Kelvin convert, `ls.output1.status` range, equilibration + extra hold by T band, 5400 s timeout escape); filename sanitization `translate`; `step_across_sample` dose-spreading; arc-direction reversal each temperature; turn-off heating on exit.
6. **Intent:** Thermal-cycle GISWAXS on ionic-liquid polymer films with auto-align and fresh-spot dosing; clean but fully legacy.

---

## 14. 30-user-Bolmat.py
1. **Size / plans:** ~3 KB, 4 plans (oldest, Nov-2018).
2. **User/group:** Bolmatov (`DB`,`LC`,`LCF`) — liquid-crystal / capsule (RPI) samples.
3. **Use-cases:** **transmission SAXS/WAXS multi-sample bar** (`run_saxs_capsRPI`, `run_saxsRPI`), **temperature + energy-series SAXS** (`run_saxs_caps_temp_Bolm` — 3 temperatures × 14 samples × 3 energies, Lakeshore + `energy`), uses both `escan` and `bp.grid_scan` over arc+y.
   - **Detectors:** `pil2M`, `rayonix` (MAXS), `pil300KW`, `ls.ch1_read`, `xbpm3.sumY`.
4. **Acquisition pattern: LEGACY (earliest idiom).** Custom `escan` helper per sample, and a temperature×sample×energy nested loop driving `bp.grid_scan`; temperature into filename via `.value`:
   ```python
   for i_t, t in enumerate(temperatures):
       yield from bps.mv(ls.ch1_sp, t)
       for x, s in zip(x_list, samples):
           temp = ls.ch1_read.value
           for i_e, e in enumerate(e_list):
               yield from bps.mv(energy, e)
               sample_id(user_name=name, sample_name=name_fmt.format(sample=s,temperature=temp,energ=e))
               yield from bp.grid_scan(dets, waxs, *waxs_arc, piezo.y, *y_range, 0)
   ```
5. **Notable techniques/hardware:** `escan` custom scan, `ls.ch1_sp`/`ch1_read` (older Lakeshore channel), piezo vs stage mix, `xbpm3.sumY` + rayonix in det list; multi-energy (13450–13520 eV) anomalous SAXS contrast.
6. **Intent:** Multi-sample transmission SAXS/WAXS with temperature + (anomalous) energy series on LC/capsule samples; foundational legacy nested-loop template (2018).

---

# BATCH SYNTHESIS

- **Dominant archetypes (≈7):** (1) tender-energy **NEXAFS / resonant SWAXS at absorption edges** (Su, Gann, Gu, NIST, Francisco — S/Cl/K/Co/Fe/Ce/Zr/Ti/Zn/Bi/Se/Br/As/Mn, with fine ~0.25 eV grids and fresh-spot rastering); (2) **GISAXS/GIWAXS thin-film** with per-sample auto-alignment + incident-angle + waxs-arc sweeps (Herzig, Kumacheva, QYu, Francisco, Gann, Su); (3) **temperature ramping / melting / annealing kinetics** via Lakeshore or Linkam (Gu, OGang, Kumacheva, NIST, Bolmat, Su `temp_series`); (4) **transmission SWAXS multi-sample bar** survey (Bolmat, Fang, EHu, Kraus, Herzig); (5) **spatial raster / micro-mapping** (Kraus, NIST, OGang, EHu line-scan, Su microfocus); (6) **in-situ time-series** — polling/`run_time` loops (Fang, QYu, Yu-Chung, OGang, EHu); (7) **specular XRR / resonant reflectivity** (Gann only) and **in-situ 3D-printing** (Yu-Chung only).
- **Legacy is overwhelmingly prevalent:** 9/14 files are essentially pure **LEGACY** (Gu, Herzig, OGang, EHu, NIST, Fang, Kumacheva, Bolmat, QYu); 5 are **MIXED** (Su, Gann, Francisco, Yu-Chung, Kraus); only Su (2026 plans) and Gann (XRR) contain genuinely **MODERN** decorated single-run code.
- **Universal legacy signature:** nested Python `for` loops where each innermost iteration calls `yield from bp.count(dets, num=1)` → one Bluesky run per data point; the run-per-logical-sample model is absent except in Su's 2025–2026 `inner()` plans and Su's experimental `multi_scan/factory` (sub-document) prototypes.
- **Filename = global mutable state everywhere:** all 14 files set the output filename through `sample_id(user_name, sample_name)` and/or `RE.md["sample_name"]`/`RE.md["sample"]`; only Su's modern plans promote the target filename to an ophyd `Signal('target_file_name')` read into the primary stream via `trigger_and_read`.
- **Context read as `.value`/`.get()` into strings, not recorded as devices:** temperature (`ls.input_A.get()-273.15`, `getT()`), beam current (`xbpm2.sumX.value`), humidity (`readHumidity`), SDD (`pil2M_pos.z.position`), energy and scan_id are formatted into filenames rather than captured as baseline/primary-stream signals — the single biggest data-provenance gap.
- **Two notable anti-patterns beyond plain legacy:** OGang and QYu call **`RE(...)` inside `for`/`while` loops** (blocking re-entrant runs, not composable generators); Yu-Chung's `trigger_alldet` pokes `cam.acquire.put(1)` to free-run detectors **outside the RunEngine** entirely (no documents recorded).
- **Conditional detector lists are ubiquitous and correct-in-spirit:** `dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]` (Gann, Gu, Kumacheva, QYu, Yu-Chung) — the desired modern form is separate declared SAXS/WAXS streams (Gann's commented `bps.declare_stream(...)`/`trigger_and_read` scaffold shows the intended target).
- **Slow/in-vacuum axis ordering is informally respected:** `waxs.arc` and `piezo.th`/`stage.phi` tend to sit in outer loops with `[::-1]` direction reversal to minimize arc travel, and alignment-results are cached per sample (`Aligned_Dict`, QYu) — good instincts that the modern template should formalize (arc/phi outermost, baseline alignment offsets).
- **Hardware breadth to support in a modern template:** SAXS `pil2M` + WAXS `pil900KW`/`pil300KW` + MAXS `rayonix` (Kraus, Bolmat) tri-range; environment controllers (Lakeshore `ls`, Linkam `LThermal`, Oleg-Gang thermal `gotoT/getT`); in-situ rigs (syringe pump + Thorlabs translator for blade-coating, MFC dry/wet humidity, hexapod print-profiling); tender DCM `energy` with per-energy detector flatfield (`set_energy_cam`); attenuator ladders (`att2_*`) with angle-dependent logic for XRR.
- **Migration maturity gradient (oldest→newest):** Bolmat 2018 `escan`/`grid_scan` → 2020–2023 dense per-point `bp.count` loops (Herzig/Gu/NIST/Fang/Kumacheva) → 2024 helper-abstracted dict loops (EHu/QYu) → 2025–2026 decorated `inner()` + `Signal` single runs (Su) and self-documenting refactor scaffolds (Gann). Su.py and Gann.py are the best in-repo references for the modern SMI pattern; OGang.py and the `RE()`-in-loop / `cam.put` cases are the priorities to retire.

# Legacy Bluesky/Ophyd Plan Analysis — Batch 06 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 16 legacy
user macro files. Detector key: `pil2M` = SAXS (Pilatus 1M/2M), `pil900KW`/`pil300KW`
= WAXS (arc-mounted, in-vacuum or in-air), `rayonix` = MAXS, `xbpm2`/`xbpm3`
(`.sumX`/`.sumY`) = beam-position/intensity monitors, `pin_diode`/`pdcurrent1`/
`pil2M_bs_pd` = beamstop pin-diode (transmission), `ls`/`LThermal` = Lakeshore/Linkam
temperature controllers. Slow / in-vacuum axes: `waxs`(=`waxs.arc`), `stage.*`
(hexapod coarse), `prs` (polarization/phi rotation stage). Fast nano-stage:
`piezo.x/y/z/th/ch`. `energy` = DCM (tender/edge work, S 2472 eV, Cl, Se, Br, Ag, Cd).

**Pattern legend.** **LEGACY** = nested `for` loops each calling
`bp.count`/`bp.scan`/`bp.rel_scan` → one Bluesky run per data point; filenames via
global mutable `sample_id(...)` / `RE.md`; context (temp, bpm, energy, angle) read via
`.value`/`.get()` and baked into the filename string; hard-coded coordinate/sample
lists in plan body. **MODERN** = `@bpp.run_decorator(md=...)` +
`@bpp.stage_decorator(dets)` around an `inner()` generator with
`bps.trigger_and_read(dets + [signals])`; target filename carried as an ophyd
`Signal`. **MIXED** = both present (documented migration in progress).

> Several files in this batch additionally use the **`RE(...)`-inside-Python-loop**
> anti-pattern (plans that are not generators end-to-end), which is worse than the
> standard legacy loop and explicitly breaks pause/resume/suspenders.

---

## 1. 30-user-McNeil.py
1. **Size / plans:** ~137 KB, ~66 `def`s (largest in batch; ~2021→2025 accretion).
2. **User/group:** McNeil / Chris McNeil group (`GF`, operators) — conjugated-polymer
   (P3HT, D18, OPV) thin-film electronic materials; serves guests (Ruipeng, Amalie).
3. **Use-cases:** tender-resonant **NEXAFS / GIWAXS** at multiple absorption edges
   — **S K-edge** (~2472 eV, dominant), **Cl**, **Se**, **Br**, with **oriented /
   polarization-dependent (dichroic) NEXAFS** via the `prs` rotation stage
   (`nexafs_oriented_S_edge_corr_only_allprs`, `prs 0/30 deg`); **microfocus raster /
   fresh-spot anti-beam-damage** mapping (`xstep`/`ystep` linspace rasters,
   `beamdamage_*`, `fluo_scan_*`); **incident-angle scans** (`incident_scan_giwaxs`,
   `calibrate_ai_ver/hor`, dense ai grids 0.2→4°); **energy sweeps at fixed position**
   (`fixedposition_energysweep_ver/hor`); **doublestack** GI geometry; hard-Xray GIWAXS.
   - **Detectors:** `pil900KW` (S-edge WAXS, primary), `pil300KW` (older WAXS),
     `pil2M`; energy-conditional det lists.
3b. **Detectors:** pil900KW / pil300KW (WAXS) + pil2M (SAXS); xbpm2/xbpm3 for I0.
4. **Acquisition pattern: MIXED — one of the clearest migration cases in the batch.**
   - LEGACY core (2021–2024): edge×position rasters with per-point `bp.count`, bpm into
     filename, meshgrid fresh-spot indexing:
     ```python
     for e, xsss, ysss in zip(energies, xss, yss):
         yield from bps.mv(energy, e); yield from bps.mv(piezo.x, xsss)
         bpm = xbpm2.sumX.value
         sample_id(user_name="GF", sample_name=name_fmt.format(...,xbpm=bpm))
         yield from bp.count(dets, num=1)
     ```
   - MODERN (2025, `*_newsecurity`, `*_scan` families): `Signal` target name +
     decorators + `trigger_and_read`, single run per plan:
     ```python
     s = Signal(name='target_file_name', value='')
     @bpp.stage_decorator(dets)
     @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
     def inner():
         ... s.put(sample_name)
         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
     (yield from inner())
     ```
   - **Composable architecture:** high-level `sequence_scan_*` orchestrators chain
     alignment + `incident_energy_scan` + `sevralai_giwaxs_*` sub-plans per sample —
     unusually well-factored for legacy code.
5. **Notable techniques/hardware:** `prs` polarization-resolved NEXAFS (par/per/45°
   films); `track_max`/`aipeak` specular-peak tracking; beam-damage characterization
   plans; fine NEXAFS energy grids (0.1–0.25 eV across edge); energy-move retry guards
   (`if xbpm3.sumX.get()<20: re-move`); `alignement_gisaxs_doblestack`.
6. **Intent:** Master resonant tender-edge GIWAXS/NEXAFS macro for OPV polymer films
   (S/Cl/Se/Br edges, dichroism, microfocus anti-damage), mid-migration from per-point
   legacy counts to single-run decorated `Signal` streams.

---

## 2. 30-user-RPI.py
1. **Size / plans:** ~76 KB, ~37 `def`s (cycle-stamped `*_2021_1` … `*_2024_3`).
2. **User/group:** RPI / Rensselaer (Koratkar/Ramanath-adjacent; operators `JA`,`SL`,
   `LC`) — epoxy/amine thermoset networks, PVP/Ce ionomers, polystyrene; capillaries
   and "plaque" bulk specimens.
3. **Use-cases:** **temperature-resolved SAXS/WAXS** via **Linkam capillary stage**
   (`run_saxs_linkam*`, `ls.ch1_read`/`ls.input_A`), **transmission SAXS/SWAXS on
   capillaries** (`run_caps*`, `run_saxs_caps*`), **multi-position plaque SWAXS**
   averaging (`run_plaq_swaxs_*`, x/y offset grids), **continuous time-series**
   (`run_contRPI` N×count+sleep), **beam-damage tests** (`acq_bd`), in-air vs in-vacuum
   variants (`*_Vac`).
3b. **Detectors:** pil2M (SAXS) + pil900KW/pil300KW (WAXS); SAXS conditionally dropped
    when `waxs.arc<15`; `ls` Linkam temperature.
4. **Acquisition pattern: LEGACY (uniform).** WAXS-arc outer loop → sample loop →
   position-offset loop → per-point `bp.count`/`bp.rel_scan`; temperature + energy +
   sdd + scan_id all formatted into the filename string:
   ```python
   temp = str(np.round(float(temp),1)).zfill(5)
   sample_name = "{sample}_{energy}keV_{temp}degC_wa{wax}_sdd{sdd}m_id{scan_id}".format(...)
   sample_id(user_name=user, sample_name=sample_name)
   yield from bp.rel_scan(dets, stage.y, *y_range, n_points)
   ```
5. **Notable techniques/hardware:** Linkam (off-Bluesky, temp passed manually as arg or
   read via `ls.ch1_read.value`); huge commented sample-coordinate tables ("Sample set
   1–6"); hexapod `stage.y` linescans across capillaries; SAXS/WAXS conditional det.
6. **Intent:** Per-cycle thermoset/ionomer thermal SAXS/WAXS campaigns on
   capillaries+plaques; canonical legacy "Linkam-temperature-into-filename" file.

---

## 3. 30-user-Kline.py
1. **Size / plans:** ~52 KB, ~18 `def`s (mostly cycle/guest-stamped `cdsaxs_2025_2_*`).
2. **User/group:** Kline / R. Joseph Kline (NIST) **CD-SAXS** program; many guest
   variants (`*_dupont1/2`, `*_KD`, `*_int4`, `*_NSH1`, `*_FSH1/2/3`, `*_Matt`).
   `user_name="JK"`.
3. **Use-cases:** **CD-SAXS (critical-dimension / transmission rotation SAXS)** of
   nano-patterned gratings/lithography line-space structures — rocking the sample in
   `prs` (phi) from −60°→+60° (121 frames) with bracketing reference frames; also
   **CD-GISAXS** (`cd_gisaxs`, grazing geometry + attenuator-laddered ai 0.15/0.2/0.3/0.5,
   dense phi sweep ±5°).
3b. **Detectors:** pil2M (SAXS) only; `xbpm3.sumX` into filename for I0 normalization.
4. **Acquisition pattern: LEGACY (per-frame count over rotation).** Shared helper
   `cd_saxs()` loops `prs` and counts each angle as its own run; multi-axis alignment
   scans (`cdsaxs_2025_1_scan` y/z/th/chi sub-scans) likewise per-point:
   ```python
   for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
       yield from bps.mv(prs, theta)
       sample_name = "{sample}_5.2m_16.1keV_num{num}_{th}deg_bpm{bpm}".format(...)
       sample_id(sample_name=sample_name)
       yield from bp.count(det, num=1)
   ```
5. **Notable techniques/hardware:** `prs` rotation stage as the CD-SAXS goniometer;
   hard-coded per-sample x/y/z/chi/th tables (hexapod + piezo); reference-frame
   bracketing (`measure_ref-A/B`); `piezo.y` position-error retry guard
   (`while abs(piezo.y.position-ys)>=1`). **NOTE: this file is near-identical in
   structure to 30-user-Yager.py** (same `cd_saxs`/`cd_gisaxs`/`measure` helpers) — a
   shared CD-SAXS toolkit cloned and extended per cycle.
6. **Intent:** Production CD-SAXS/CD-GISAXS of semiconductor gratings via phi-rocking;
   legacy per-frame counting that the modern template should fold into one rocking run.

---

## 4. 30-user-Collins.py
1. **Size / plans:** ~42 KB, ~20 `def`s (cycle-stamped 2020_3 → 2021_2).
2. **User/group:** Collins / Brian Collins group (`BC`); guests Terry, Gomez.
   Conjugated-polymer / NFA OPV blends (PM6, Y6, D18, P3HT, PTQ10).
3. **Use-cases:** **S K-edge NEXAFS** (very fine energy grids, 0.1 eV across white
   line) — incl. `prs`-resolved oriented variants — and **resonant GIWAXS** (incident
   angle ~0.15°, waxs-arc series); `WAXS_S_edge_rad_dmg_test` (radiation-damage),
   "night" batch wrappers; multi-set bar surveys (`*_set1/set2`, ~32 samples).
3b. **Detectors:** pil300KW + pil900KW (S-edge WAXS), pil2M (SAXS); xbpm3.sumY for I0.
4. **Acquisition pattern: LEGACY (uniform).** Sample loop → meshgrid fresh-spot
   y-stepping → energy loop → per-point `bp.count`; writes BOTH `sample_id(...)` and
   `RE.md["filename"]`:
   ```python
   for e, xsss, ysss in zip(energies, xss, yss):
       yield from bps.mv(energy, e); yield from bps.mv(piezo.y, ysss)
       sample_name = "nexafs_90deg_wa59deg_{sample}_{energy}eV_xbpm{xbpm}".format(...)
       RE.md["filename"] = sample_name
       sample_id(user_name="BC", sample_name=sample_name)
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `alignement_special`/`alignement_gisaxs`; very dense
   S-edge energy lists (≥6 concatenated `np.arange` segments); fresh-spot y-raster
   (95-pt `linspace`) for beam-damage avoidance; `prs` for oriented NEXAFS.
6. **Intent:** Resonant S-edge NEXAFS + GIWAXS on OPV donor/acceptor films; textbook
   legacy edge-survey with double filename bookkeeping (`sample_id` + `RE.md`).

---

## 5. 30-user-SSYang_2022C2.py
1. **Size / plans:** ~32 KB, ~39 `def`s (full self-contained GISAXS+thermal framework).
2. **User/group:** S.S. Yang (`SY`/`username`) — grazing-incidence thin-film + block
   copolymer / order-disorder thermal studies.
3. **Use-cases:** **GISAXS/GIWAXS** (`run_gisaxs`, `run_giwsaxs`, custom alignment),
   **temperature-resolved (melting / order-disorder) SWAXS** with up-AND-down hysteresis
   ramps (`run_T_wsaxs`, `run_T_giwsaxs`; Lakeshore `ls.output1` range-3 heating,
   ±0.25 °C equilibration), **multi-incident-angle WSAXS** (`measure_series_multi_angle_
   wsaxs`), transmission SAXS/WAXS, pin-diode transmission (`measure_pindiol_current`).
3b. **Detectors:** pil900KW/pil300KW (WAXS) + pil2M (SAXS, conditional); `ls` Lakeshore.
4. **Acquisition pattern: LEGACY + `RE(...)`-in-loop anti-pattern.** Temperature outer
   loop (generator `setT/startT/getT` + busy-wait) → sample/angle loops → per-point
   `bp.count`; sample tracked in `RE.md["sample"]`; some helpers wrap `RE(...)`:
   ```python
   for cts, T in enumerate(Tlist):
       yield from setT(T); yield from startT()
       while abs(getT()-T) > 0.25: yield from bps.sleep(10)
       yield from measure_series_multi_angle_wsaxs_yield(t=[t], waxs_angles=..., dys=[0])
   ```
5. **Notable techniques/hardware:** local copies of `alignement_gisaxs`, `SMI_Beamline()`
   alignment mode / `setDirectBeamROI`; hysteresis `Tlist` (ramp up then down for Tm/ODT);
   `smi.modeAlignment(technique="gisaxs")`. Self-contained — duplicates beamline infra.
6. **Intent:** GISAXS + temperature-cycling SWAXS framework for BCP/thin-film phase
   transitions; legacy temp-into-filename with embedded (duplicated) alignment utilities.

---

## 6. 30-user-Yager.py
1. **Size / plans:** ~28 KB, 8 `def`s.
2. **User/group:** **Yager (beamline-scientist name) — but content is CD-SAXS for the
   Kline/NIST-style program** (`user_name="JK"`/`KY_GI`). This is effectively the parent
   of 30-user-Kline.py (shared `measure`/`cd_saxs`/`cd_gisaxs` helpers).
   ⚠️ *Despite the Yager filename, this is NOT general beamline infrastructure — it is a
   CD-SAXS user macro; see synthesis flag.*
3. **Use-cases:** **CD-SAXS** phi-rocking (`cd_saxs`: prs −60→+60°, 121 frames, ref
   brackets), guest variants (`cdsaxs_2024_1`, `2025_1`, `*_Karen`, `*_Matt`,
   `*_scan`), and **CD-GISAXS** (`cd_gisaxs`: grazing ai 0.15–0.5 with attenuator ladder,
   ±5° dense phi).
3b. **Detectors:** pil2M (SAXS) only; xbpm3.sumX for I0.
4. **Acquisition pattern: LEGACY (per-frame count over `prs`).**
   ```python
   def cd_saxs(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil2M]):
       for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
           yield from bps.mv(prs, theta)
           sample_id(sample_name="{sample}_..._num%2.2d_%2.2ddeg_bpm%1.3f"%(...))
           yield from bp.count(det, num=1)
   ```
5. **Notable techniques/hardware:** `prs` CD-SAXS goniometer; hexapod+piezo per-sample
   tables; `alignement_gisaxs_hex` (external infra); `cdsaxs_*_scan` performs
   y/z/th/chi alignment sub-scans selectable via a `scan=[1,1,1,1,1]` flag list.
6. **Intent:** CD-SAXS/CD-GISAXS toolkit (the canonical `cd_saxs` helper later cloned
   into Kline); legacy per-frame rocking acquisition.

---

## 7. 30-user-XZhang.py
1. **Size / plans:** ~16 KB, ~29 `def`s.
2. **User/group:** XZhang / Xin Zhang & Hua/Hao Zhang (`XZ`,`HZ`,`YZhang2`) —
   cellulose/chitosan-Cu fibers & films, carbon fiber, Au-nanoparticle solutions.
3. **Use-cases:** **microfocus SAXS raster mapping** (`measure_saxs_map`, `do_one_map`,
   220 nm-step x-grids × y-grids over fibers/films), **transmission SAXS/WAXS** of
   capillaries/films, **multi-angle WAXS** (`measure_waxs_multi_angles`), beam-damage
   y-scan series, pin-diode transmission (`measure_pindiol_current`).
3b. **Detectors:** pil2M (SAXS), pil900KW/pil300KW (WAXS), rayonix occasionally;
    `pdcurrent1` pin-diode.
4. **Acquisition pattern: LEGACY + heavy `RE(...)`-in-loop anti-pattern.** Most
   "series"/"map" orchestrators call `RE(measure_*())` inside plain Python `for` loops
   and stash names in `RE.md["sample"]`; inner `measure_*` are generators with per-point
   `bp.count`:
   ```python
   def measure_waxs0_XZ_scany(N=10):
       sample = RE.md["sample"]
       for i in range(N):
           RE(measure_waxs(t=1, waxs_angle=0, sample=sample))
           RE(bps.mvr(piezo.y, 500))
   ```
5. **Notable techniques/hardware:** `pxy_dict`/`sample_dict` mutable globals + `mov_sam`;
   220 nm microfocus step (matches beam size); scan-id/det-distance baked into filename;
   `measure_pindiol_current` opens/closes fast shutter around diode read.
6. **Intent:** Microfocus SAXS mapping + transmission SWAXS of fibers/films/NP solutions;
   legacy with the worst-offender `RE()`-inside-`for` orchestration.

---

## 8. 30-user-Kim5.py
1. **Size / plans:** ~14 KB, ~14 `def`s.
2. **User/group:** Kim / Nam-Kim group (`Kim`,`Gao`) — high-k dielectric oxide thin
   films (HfO2, ZrO2, MIM stacks) on a multi-sample bar.
3. **Use-cases:** **GIWAXS multi-sample bar survey** (`run_giwaxs_Kim`): incident-angle
   array [0.05–0.3°] × waxs-arc [7,27,47] × x-offset positions; per-bar **alignment**
   (`alignement_gisaxs`); **vertical (height) scan** (`vertical_scan`); manual
   single-sample measure; snap utilities.
3b. **Detectors:** pil900KW + pil300KW (WAXS), pil2M (SAXS at max waxs angle), rayonix.
4. **Acquisition pattern: LEGACY + `RE(...)`-in-loop helpers.** Generator `run_giwaxs_Kim`
   uses nested sample→waxs→x→angle loops with per-point `bp.count`; but `mov_sam`,
   `manually_measure_one_sample`, `move_waxs` wrap `RE(...)`:
   ```python
   for waxs_angle in Waxs_angle_array:
       yield from bps.mv(waxs, waxs_angle)
       for x_meas in x_pos_array:
           for i, th in enumerate(th_meas):
               sample_id(user_name=username, sample_name=name_fmt.format(..., scan_id=RE.md["scan_id"]))
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** serpentine `inverse_angle` toggling per sample;
   conditional SAXS only at max waxs angle; many commented per-bar `x_list` blocks (RUN
   1–6); `RE.md["scan_id"]` into filename; large-beam vacuum/air comparison runs.
6. **Intent:** High-throughput GIWAXS bar survey of dielectric oxide films; legacy
   nested-loop GI with `RE()`-wrapped motion helpers.

---

## 9. 30-user-Printer.py
1. **Size / plans:** ~13 KB, ~20 `def`s + a custom `Printer_3D` ophyd Device.
2. **User/group:** Printer / in-situ **3D-printing** group (`RT`) — extrusion / FFF
   nozzle deposition studied operando.
3. **Use-cases:** **in-situ 3D-printing WAXS/SAXS** with several geometries —
   **through-nozzle** scan (`through_nozzle_exp`, capillary + tapered sections,
   height×radial raster), **below-nozzle** time-resolved deposition
   (`start_acq_below_nozzle`), **across-beam** and **downstream-of-nozzle** time series;
   **hardware-triggered** acquisition waiting on a digital input
   (`triggered_series`/`start_printing_below_nozzle` via `caget('XF:11ID-CT{M3}bi2')`).
3b. **Detectors:** pil900KW (WAXS, primary); pil2M (SAXS) noted as optional when
    `waxs.arc<10`.
4. **Acquisition pattern: LEGACY + `RE(...)`-in-loop + EPICS caget/caput trigger.**
   Time loops of single `bp.count`s; nozzle/beam geometry tracked in `RE.md` keys
   (`"nozzle 0"`,`"beam height"`,`"beam_x"`) read into the filename:
   ```python
   for j in range(N_imgs):
       sample_name = f"below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_nh{nozzle_height:3.3f}mm_t{td}"
       sample_id(user_name="RT", sample_name=sample_name)
       yield from bps.sleep(dwell); yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** custom `Printer_3D(Device)` (6-axis bed/head EpicsMotors,
   PV `XF:11IDM2-3D{3D:`); nozzle/platform/beam-height calibration helpers storing zero
   refs in `RE.md`; external digital-trigger handshake (`caget/caput`); filename
   character sanitization.
6. **Intent:** Operando 3D-printing SWAXS (in-nozzle, below/across/downstream of nozzle)
   with external print-machine triggering; legacy time-series + `RE.md` geometry state.

---

## 10. 30-user-Kim4.py
1. **Size / plans:** ~10 KB, ~13 `def`s (older sibling of Kim5).
2. **User/group:** Kim group (`Kim`) — multi-sample GIWAXS bar (2021C3 sample series,
   ~74 samples across bars).
3. **Use-cases:** **GIWAXS multi-sample bar survey** (`run_giwaxs_Kim`, same engine as
   Kim5: ai [0.05–0.3°] × waxs [7,27,47] × x-offsets), manual single-sample measure,
   snap WAXS/SAXS, `check_sample_loc` bar tour.
3b. **Detectors:** pil900KW + pil300KW (WAXS), pil2M (SAXS at max waxs angle).
4. **Acquisition pattern: LEGACY + `RE(...)`-in-loop helpers** (identical to Kim5;
   nested loops + per-point `bp.count`, `RE.md["scan_id"]` in name, serpentine angle
   toggle). See Kim5 snippet.
5. **Notable techniques/hardware:** extensive commented operator runbook (camserver
   `setthreshold energy 16100`, beamstop save, vent/pump procedure, per-bar timing);
   many `x_list` RUN blocks reassigned in place (last assignment wins).
6. **Intent:** 2021-cycle GIWAXS bar survey of thin-film series; near-duplicate of Kim5,
   canonical legacy GI bar loop.

---

## 11. 30-user-Foster.py
1. **Size / plans:** ~7 KB, 4 `def`s (2 acquisition plans + 2 attenuator helpers).
2. **User/group:** Foster (`MF`) — solution/film SWAXS with quantitative transmission.
3. **Use-cases:** **transmission SAXS/WAXS of capillaries** as linescans/grids
   (`run_swaxs_Foster_2023_2/_3`) with **in-line transmission measurement** (attenuator
   in, beamstop-rod retract, sample-vs-direct-beam ratio from `pil2M_stats1_total`);
   sample-camera snapshots (`OAV_writing`).
3b. **Detectors:** pil900KW (WAXS) + pil2M (SAXS, conditional `waxs.arc<15`);
    `OAV_writing` optical camera; Sn 60 µm attenuators (`att1_6/att1_7`).
4. **Acquisition pattern: LEGACY (per-point count) — but with good ad-hoc transmission
   logic.** waxs→sample→y-off→x-off nested loops; transmission computed live from db,
   folded into the filename:
   ```python
   yield from bp.count([pil2M]); stats1_sample = db[-1].table(...)['pil2M_stats1_total'][0]
   yield from bps.mv(piezo.x, x + dx); yield from bp.count([pil2M]); stats1_direct = ...
   trans = np.round(stats1_sample/stats1_direct, 5)
   sample_id(user_name="MF", sample_name=f'{name}{get_scan_md()}_loc{loc}_trs{trans}')
   yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** beamstop-rod retract (`pil2M_bs_rod.x`) for direct
   beam; attenuator state machines (`atten_move_in/out` with status polling);
   `get_scan_md()` helper; conditional SAXS det; OAV image capture per sample.
6. **Intent:** Quantitative-transmission SAXS/WAXS linescan/grid of capillaries; legacy
   per-point but with self-contained absolute-transmission bookkeeping.

---

## 12. 30-user-Brett.py
1. **Size / plans:** ~5 KB, ~11 `def`s.
2. **User/group:** Brett / Calvin Brett (`CB`) — CdSe/CdS nanorods, P3HT:Ag thin films.
3. **Use-cases:** **NEXAFS** at **S, Ag (L2/L3), Cd** edges (`NEXAFS_S/Ag/Cd_edge`,
   dense `linspace` energy grids), **resonant GIWAXS** at S/Ag edges with x-offset
   fresh-spot (`giwaxs_*_calvin`), **time-resolved S-edge** (UV-on kinetics,
   `time_resolved_S_edge`), a **fly-scan** prototype (`fly_scan_prsx`: manual
   stage/trigger over `piezo.x`), "night_shift" batch wrappers with in-situ UV exposure.
3b. **Detectors:** pil300KW (WAXS/NEXAFS) + pil2M (SAXS); xbpm3.sumX/sumY for I0.
4. **Acquisition pattern: LEGACY (energy loop → per-point count); + manual fly prototype.**
   ```python
   for e in energies:
       yield from bps.mv(energy, e); yield from bps.sleep(2)
       sample_id(user_name="CB", sample_name=name_fmt.format(..., xbpm="%3.1f"%xbpm3.sumY.value))
       yield from bp.count(dets, num=1)
   ```
   `fly_scan_prsx` hand-rolls `pil2M.stage()/trigger()` + `list_scan` (continuous expo).
5. **Notable techniques/hardware:** multi-edge NEXAFS (S/Ag/Cd); in-situ **UV
   illumination** kinetics; manual detector stage/trigger fly-scan; energy "park"
   sequence at plan end to protect optics.
6. **Intent:** Multi-edge NEXAFS + resonant GIWAXS + UV-kinetics on QD/polymer films;
   legacy energy loops with an experimental fly-scan.

---

## 13. 30-user-Berlinger.py
1. **Size / plans:** ~5 KB, 3 `def`s.
2. **User/group:** Berlinger / (Hammond/Berlinger; operator `GF`) — Nafion / sulfonated
   ionomer (nPA, SPES) membranes.
3. **Use-cases:** tender **S K-edge resonant WAXS/NEXAFS** of Nafion at SDD 2 m
   (`Nafion_waxs_S_edge`: fine S-edge grid + fresh-spot meshgrid raster) and **hard-Xray
   (16.1 keV) WAXS+SAXS** survey (`Su_nafion_waxs_hard`, `sara_nafion_waxs_hard`;
   waxs-arc 0→32.5°).
3b. **Detectors:** pil2M (SAXS), pil300KW (WAXS); xbpm2.sumX for I0.
4. **Acquisition pattern: LEGACY (uniform).** Sample→waxs→energy nested loops, meshgrid
   fresh-spot, bpm into filename, per-point `bp.count`; energy-move try/except retry:
   ```python
   for e, xsss, ysss in zip(energies, xss, yss):
       try: yield from bps.mv(energy, e)
       except: yield from bps.sleep(30); yield from bps.mv(energy, e)
       bpm = xbpm2.sumX.value
       sample_id(user_name="GF_sdd2m", sample_name=name_fmt.format(...,xbpm=bpm))
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** fresh-spot meshgrid (`np.linspace(ys, ys+1000, 15)`)
   anti-beam-damage; energy-move exception guard; DCM park to 2470/2450 after edge.
6. **Intent:** S-edge resonant + hard-Xray SWAXS of Nafion/SPES membranes; legacy
   edge-raster (clearly forked from the shared Su/`GF` Nafion template).

---

## 14. 30-user-Elb.py
1. **Size / plans:** ~4 KB, 8 `def`s (1 survey + Cai-style alignment suite).
2. **User/group:** Elb / (`CM`/`KE`, "Cai") — dye-loaded nanoparticle (DiR) GISAXS films.
3. **Use-cases:** **GISAXS/GIWAXS incident-angle survey** (`gisaxsElb`: ai offsets
   [0.02,0.12,0.32] × x-positions, waxs-arc scan) and a full **GISAXS alignment suite**
   (`alignCai`/`alignfine`/`align_gisaxs_height_Cai`/`align_gisaxs_th_Cai`,
   alignment-vs-measurement foil modes).
3b. **Detectors:** pil2M (SAXS), pil300KW (WAXS), rayonix (MAXS); xbpm3.sumY; reads
    Lakeshore `ls.ch1_read` into name.
4. **Acquisition pattern: LEGACY (per-point count) + dedicated alignment plans (these
   ARE proper generators using `bp.rel_scan` + `ps()` peak-stats).**
   ```python
   for k in range(0,3,1):
       for j, ang in enumerate(a_off + np.array(angle_offset)):
           yield from bps.mv(piezo.th, ang)
           sample_id(user_name=dude, sample_name=name_fmt.format(...))
           yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable techniques/hardware:** `SMIBeam().insertFoils("Alignement"/"Measurement")`
   attenuator-foil mode switch; ROI-Y peak tracking of specular spot vs angle
   (`pil2M.roi1.min_xyz.min_y`); `ps` peak-finder (cen/peak) for th/height; `GV7`
   gate-valve TwoButtonShutter; `waxs` arc scan as the data axis (`bp.scan(dets, waxs,...)`).
6. **Intent:** GISAXS angle survey + reusable GISAXS auto-alignment (height/theta/ROI)
   for DiR-NP films; legacy survey but contains clean alignment-routine building blocks.

---

## 15. 30-user-Kim.py
1. **Size / plans:** ~2 KB, 1 plan (`run_giwaxs_Kim`).
2. **User/group:** Kim group (`Kim`) — oxide dielectric MIM stacks (Hf0.75/0.25, ZrO2).
3. **Use-cases:** **GIWAXS multi-sample bar survey** (the original minimal version of the
   Kim4/Kim5 engine): ai [0.1,0.15,0.19°] × waxs-angle array (15 pts to q≈4.7) × x-offset,
   with per-sample alignment.
3b. **Detectors:** pil300KW (WAXS), rayonix (MAXS), pil2M (SAXS).
4. **Acquisition pattern: LEGACY (uniform nested loops, per-point count).**
   ```python
   for waxs_angle in waxs_angle_array:
       yield from bps.mv(waxs, waxs_angle)
       for x_meas in x_pos_array:
           for i, th in enumerate(th_meas):
               sample_id(user_name="Kim", sample_name="{sample}_{th}deg_waxs{...}_x{x}_{t}s".format(...))
               yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `alignement_gisaxs(0.1)` per sample; q-coverage
   comments tying waxs-angle count to qmax; hard-coded `sample_list`/`x_list`.
6. **Intent:** Minimal GIWAXS oxide-film bar survey (progenitor of Kim4/Kim5); plain
   legacy GI loop.

---

## 16. 30-user-Hanqiu.py
1. **Size / plans:** ~1 KB, 1 plan (`run_waxs_Hanqiu`).
2. **User/group:** Hanqiu (`HJ`) — fuel-cell membrane/electrode (Cell48 EE/FF) S-edge.
3. **Use-cases:** tender **S K-edge resonant WAXS** of fuel-cell cells via **waxs-arc
   scan at fixed energies** (energies [2470,2485,2500]; `waxs` arc 3→39).
3b. **Detectors:** pil300KW (WAXS); xbpm3.sumY recorded as a det channel.
4. **Acquisition pattern: LEGACY (per-energy `bp.scan` over waxs arc).** Mildly better
   than per-point counts — uses a coordinated `bp.scan(dets, waxs, *waxs_arc)`:
   ```python
   for x, s, y in zip(x_list, samples, y_list):
       yield from bps.mv(piezo.x, x); yield from bps.mv(piezo.y, y)
       for i_e, e in enumerate(e_list):
           yield from bps.mv(energy, e)
           sample_id(user_name="HJ", sample_name=name_fmt.format(sample=s, energ=e, ycoord=y))
           yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable techniques/hardware:** `xbpm3.sumY` included in the det list (recorded, not
   just filename-baked) — a small step toward modern practice; per-sample x/y + energy
   table; `det_exposure_time` reset at end.
6. **Intent:** Quick S-edge waxs-arc scan of fuel-cell cells; minimal legacy with one
   redeeming `bp.scan` (arc-swept) and an I0 channel recorded.

---

## BATCH SYNTHESIS

- **Distinct archetypes in this batch (8):** (1) **Tender-edge NEXAFS + resonant
  GIWAXS** on OPV/ionomer films — McNeil, Collins, Brett, Berlinger, Hanqiu (S/Cl/Se/
  Br/Ag/Cd edges, fine sub-eV energy grids, fresh-spot anti-damage rasters); (2)
  **CD-SAXS / CD-GISAXS** phi-rocking metrology of nano-gratings — Yager + Kline (shared
  `cd_saxs` toolkit, `prs` goniometer); (3) **Temperature-resolved SAXS/WAXS** (Linkam/
  Lakeshore, melting/ODT hysteresis ramps) — RPI, SSYang; (4) **GIWAXS multi-sample bar
  surveys** of dielectric/thin-film series — Kim, Kim4, Kim5; (5) **Microfocus SAXS
  raster mapping** of fibers/films — XZhang (+ McNeil xstep rasters); (6) **In-situ
  3D-printing operando SWAXS** with external triggering — Printer; (7) **Quantitative-
  transmission SWAXS** of capillaries — Foster (+ XZhang/RPI); (8) **GISAXS auto-
  alignment building blocks** — Elb (Cai suite), SSYang, Kim* (`alignement_gisaxs*`).

- **Legacy-vs-modern prevalence: overwhelmingly LEGACY.** 15 of 16 files are pure
  LEGACY (nested `for` + per-point `bp.count`/`bp.scan`/`bp.rel_scan`, one run per data
  point, `sample_id(...)` global filename state, context `.value`-baked into strings).
  Only **McNeil is MIXED**, and is the single migration exemplar in the batch.

- **McNeil is the lighthouse:** its 2025 `*_newsecurity`/`*_scan` families implement the
  exact MODERN target pattern — `Signal(name='target_file_name')` +
  `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md=...)` + `bps.trigger_and_read(dets
  + [energy, waxs, xbpm2, xbpm3, s])` in a single `inner()` run. It also shows the best
  legacy architecture (composable `sequence_scan_*` orchestrators calling sub-plans).
  Recommend mining McNeil's modern blocks as the canonical template for edge/GI work.

- **⚠️ Filename ≠ infrastructure flag — 30-user-Yager.py:** despite carrying the
  beamline-scientist's name, this is **a CD-SAXS user macro (user_name "JK"), not
  reusable beamline infrastructure.** It is the parent of the near-identical
  30-user-Kline.py (same `measure`/`cd_saxs`/`cd_gisaxs` helpers). The genuinely reusable
  bit is the `cd_saxs()` phi-rocking helper — worth promoting into a proper CD-SAXS
  plan-stub, but the file itself should not be treated as a foundational utility module.

- **Worst anti-pattern cluster — `RE(...)` inside Python loops:** XZhang (most
  egregious), SSYang, Kim4, Kim5, Printer define "orchestrator" functions that call
  `RE(plan())` / `RE(bps.mv(...))` from plain `for`/`while` loops and pass sample state
  via `RE.md["sample"]`. These are not generators end-to-end and break pause/resume,
  suspenders, and the run-engine model — higher-priority refactors than the standard
  per-point legacy loop.

- **Pervasive global filename state:** every file routes data naming through
  `sample_id(user_name=..., sample_name=...)` (often resetting to `"test"`/`"test"` on
  exit) and bakes live context — temperature (`ls.input_A`/`ch1_read`), beam position
  (`xbpm2/3.sumX/sumY`), energy, incident angle, SDD, `RE.md["scan_id"]` — into the
  string instead of recording the devices. Collins additionally double-writes
  `RE.md["filename"]`. The modern template should replace all of this with `md={}` +
  primary-stream/baseline device recording.

- **Fresh-spot anti-beam-damage rastering is a recurring (and important) scientific
  idiom:** McNeil, Collins, Berlinger, Brett, XZhang all step `piezo.x/y` across a fresh
  region per energy/frame (meshgrid `linspace`, 200–300 µm steps matched to beam size).
  Any migration must preserve this fresh-spot indexing inside the single-run `inner()`.

- **Reusable hardware/technique blocks worth templatizing (not whole-file infra):**
  Printer's `Printer_3D(Device)` ophyd class + `caget/caput` external trigger handshake;
  Foster's absolute-transmission routine (beamstop-rod retract + sample/direct ratio
  from `stats1_total`); Elb's `ps()`-based GISAXS height/theta/ROI auto-alignment and
  `SMIBeam().insertFoils()` mode switching; SSYang's Lakeshore `setT/getT/startT` range-3
  thermal control with equilibration. These are the genuine "infrastructure-like"
  fragments embedded in otherwise legacy user files.

- **Detector/geometry conventions are consistent across the batch** and match prior
  batches: `pil2M`=SAXS, `pil900KW`/`pil300KW`=WAXS (arc), `rayonix`=MAXS,
  `pil2M_bs_pd`/`pdcurrent1`=beamstop pin-diode transmission, `xbpm2/3`=I0; conditional
  `dets = [pil900KW] if waxs.arc.position < 10–15 else [pil900KW, pil2M]` (SAXS dropped
  when the WAXS arc occludes it). `waxs`(arc), `stage.*`(hexapod), and `prs` are the slow
  axes and should be outermost / baseline in any modern rewrite.

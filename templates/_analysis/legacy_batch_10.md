# Legacy Bluesky/Ophyd Plan Analysis — Batch 10 (NSLS-II SMI / SWAXS)

Classification of scientific use-cases and data-acquisition patterns for 16 legacy
user macro files. Detectors: `pil2M` = SAXS (Pilatus 1M/2M), `pil900KW`/`pil300KW` =
WAXS (arc-mounted, in-vacuum), `rayonix` = MAXS, `amptek` = fluorescence (XAS/XRF),
`xbpm2/3` = beam-position monitors, `pin_diode`/`pdcurrent*`/`pil2M_bs_pd` = beamstop /
transmission diodes, `OAV_writing` = on-axis sample camera. `ls` (Lakeshore) = temperature
controller. `waxs`/`waxs.arc` and `piezo.th`/`stage.th`/`stage.phi` are slow/in-vacuum
axes. Goniometry split between `piezo.*` (fast nano-stage: x/y/z/th/ch) and `stage.*`
(coarse hexapod). `energy` = DCM (tender/edge work). `prs` = **precision rotation stage**
(sample rotation / phi about the beam, range ~ -95°…+95°) — the axis used for CD-SAXS
rocking and fiber/texture rotation. `GV7` = gate valve protecting the in-vacuum flight
path during in-air alignment. `att1_*`/`att2_*` = attenuator ladders.

Pattern legend: **LEGACY** = nested `for` loops, each iteration calls
`bp.count`/`bp.scan` → one Bluesky run per data point; filenames via global mutable
`sample_id(...)`/`RE.md`; context read via `.value`/`.get()` into strings.
**MODERN** = `@bpp.run_decorator(md=...)` + `@bpp.stage_decorator(dets)` around `inner()`
with `bps.trigger_and_read(dets + [signals])`. **MIXED** = both present.

> **Batch-wide note:** A repo-wide grep for `run_decorator`/`stage_decorator`/
> `trigger_and_read`/`declare_stream` across all 16 files returns **zero hits**. There is
> **no genuinely MODERN decorated single-run code anywhere in this batch.** The spectrum
> runs from pure-LEGACY per-point counting to MIXED files that at least use coordinated
> `bp.*_scan` / `bp.grid_scan` / `bp.list_scan` (one run per scan rather than per point).

---

## 1. 30-user-CDSAXS.py
1. **Size / plans:** ~110 KB, ~50 `def`s (shared multi-year CD-SAXS workhorse, 2020→2025).
2. **User/group:** Patrice Gergaud / CEA-LETI semiconductor metrology consortium (`PG`,`PT`); guest cycles for IBM, Olivier, Paul/Sophie, Nicolas, Nischal, **Yager** (2025). Critical-dimension metrology of nanopatterned gratings / line-space arrays.
3. **Use-cases:** **CD-SAXS rocking (critical-dimension)** — the defining technique; **CD-WAXS**; **CD-GISAXS** (phi-scan + alpha_i-scan variants); **transmission SAXS** roughness/line-edge ("rugo") averaging; tender **NEXAFS** (Ti, P edges) + resonant SAXS; multi-pitch grating surveys; det-y stitching.
   - **Detectors:** `pil2M` (SAXS, dominant); `pil300KW` (WAXS per header).
3b. **Detectors:** `pil2M` for nearly all CD-SAXS; `pil300KW` for CD-WAXS.
4. **Acquisition pattern: LEGACY (uniform, all eras).** Core engine `cd_saxs_new()` rocks `prs` across the rocking range and counts at each angle; beam-current baked into name:
   ```python
   for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):   # th typ. -60→+60, 121 pts
       yield from bps.mv(prs, theta)
       sample_name = "{sample}_..._num{num}_{th}deg_bpm{bpm}".format(..., bpm=xbpm3.sumX.get())
       sample_id(sample_name=sample_name)
       yield from bp.count([pil2M], num=nume)        # ONE run per rocking angle
   ```
   - 2025 `cdsaxsstd_2025_1*_yager` still call `cd_saxs_new` per-theta (incl. ±phi_offset reference frames and a `pil2M_pos.y` ±4.3 mm detector y-stitch); CD-GISAXS `cd_gisaxs_phi`/`cd_gisaxs_alphai` rock `prs`/`stage.th` the same way (up to 2001 pts).
5. **Notable techniques/hardware:** `prs` rocking is the heart of CD-SAXS — tilting the grating about the beam samples reciprocal-space rods at many incidences to reconstruct the line/space cross-section (sidewall angle, CD, LER); per-sample geometry tables (x/y/z piezo.ch/piezo.th); reference frames at phi_offset before/after each rock; multi-pitch x-offset surveys (`cdsaxs_all_pitch`); name sanitization.
6. **Intent:** Multi-tenant CD-SAXS/CD-GISAXS critical-dimension metrology of semiconductor gratings via `prs` rocking; canonical legacy per-rocking-angle counting that should become a single coordinated `prs` scan per grating.

### CD-SAXS rocking technique (characterization)
CD-SAXS measures **transmission** SAXS through a nanopatterned grating while the sample is
**rocked about the precision rotation stage `prs` (the phi axis perpendicular to the
beam)**, typically **-60° → +60° in 121 steps** (finer/wider in GISAXS variants, up to
2001 pts). Each rocking angle intersects a different set of the grating's vertical
reciprocal-space truncation rods, so the angular series is effectively a tomographic
sampling of reciprocal space from which the line/space **cross-section** (critical
dimension, sidewall angle, line-edge/line-width roughness, pitch walking) is reconstructed.
In this file every rocking angle is its **own Bluesky run** (`bp.count` inside the
`np.linspace(prs)` loop) — the single biggest legacy signature here. Workflow extras:
bracketing **reference frames** at a fixed `phi_offset` before and after the rock, a
detector **y-stitch** (`pil2M_pos.y ±4.3 mm`) to fill the module gap, **multi-pitch**
x-offset surveys on a single chip, and a **CD-GISAXS** mode that instead rocks `prs` (phi)
and/or `stage.th` (alpha_i) at grazing incidence. The modern target is a single coordinated
`prs` (and/or `stage.th`) scan per grating with `prs`/`xbpm` recorded in-stream.

---

## 2. 30-user-Thedford.py
1. **Size / plans:** ~97 KB, ~33 `def`s (2021→2025, PT/Fei lineage).
2. **User/group:** Thedford / Wiesner-group & collaborators (`PT`,`PT_gisaxs`,`FY`/Fei) — block-copolymer / mesoporous-film / well-plate solution soft-matter.
3. **Use-cases:** **transmission SAXS micro-mapping** (`mapping*_saxs_Thed`), **GISAXS** multi-sample bars w/ incident-angle + waxs-arc sweeps, **well-plate SAXS** (multi-well rasters, rotated variants), **capillary SWAXS**, **temperature/PT series** (`run_*PT`, `gisaxs_tempPT`), multi-cycle **SWAXS sample-bar averaging** (`run_swaxs_Fei_20xx`, 9-spot per sample).
3b. **Detectors:** `pil2M` (SAXS) + `pil300KW`/`pil900KW` (WAXS); conditional SAXS-drop when arc<15.
4. **Acquisition pattern: MIXED.** Mapping plans use coordinated `bp.rel_grid_scan` (one run/map — good); GISAXS, capillary, well, and SWAXS-bar plans use per-point `bp.count`:
   ```python
   yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)   # GOOD (mapping_saxs_Thed)
   # vs run_swaxs_Fei_2025_1: arc → sample → y_off → x_off nested → bp.count(dets)  per spot
   ```
   - Uses `get_scan_md()` / `get_scan_md(tender=...)` helper to append metadata to names.
5. **Notable techniques/hardware:** `dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]`; 3×3 fresh-spot offset grid per sample for averaging; `stage.x` hexapod coarse + `piezo` fine; huge commented sample-coordinate tables (well plates A–P).
6. **Intent:** Block-copolymer/mesoporous-film GISAXS + transmission SAXS mapping + well-plate + temperature SWAXS; grid-scan mapping is near-modern, but bars/wells remain per-point legacy.

---

## 3. 30-user-Toney.py
1. **Size / plans:** ~73 KB, ~34 `def`s (Zihan/Toney group, 2023→2024).
2. **User/group:** Toney group (`ZZ`/Zihan, `CD`) — halide-perovskite & organic-semiconductor thin films (PVSK-on-ITO).
3. **Use-cases:** **hard-Xray GIWAXS** multi-sample bars w/ per-sample auto-alignment; **temperature GIWAXS** (Lakeshore melt/anneal cycles, `zihan_temperature_giwaxs`); tender **NEXAFS** at **S K-edge** (2445–2550 eV), **Cl-edge**, **P-edge** + edge transitions (`transition_Cl_S_edges`); resonant GIWAXS; **grazing SWAXS**; bespoke alignment library (`zihan_*alignment`, `alignment_stage_Zihan`, double-stack).
3b. **Detectors:** `pil900KW`+`pil2M` (SWAXS); arc-conditional `[pil900KW] if wa<10 else [pil2M, pil900KW]`.
4. **Acquisition pattern: LEGACY (uniform).** temperature→sample(align)→arc→incident-angle→energy(±x-walk) nested loops; temperature/energy/bpm/sdd read via `.get()`/`.position` into filename; per-point `bp.count`:
   ```python
   yield from ls.output1.mv_temp(t_kelvin); while abs(ls.input_A.get()-t_kelvin)>5: sleep
   temp_degC = ls.input_A.get() - 273.15
   for e in energies:
       yield from bps.mv(energy, e); bpm = xbpm2.sumX.get()
       sample_id(user_name="CD", sample_name=f"{name}_{temp}degC_..._{e}eV_..._bpm{bpm}")
       yield from bp.count(dets, num=1)
   ```
   - fwd + reverse energy sweeps (`energies[::-1]`), low-flux re-poll (`if xbpm2.sumX.get()<50`).
5. **Notable techniques/hardware:** `turn_off_heating` cleanup; per-sample `zihan_giwaxs_alignment` caching `ai0`; fine ~0.5 eV S-edge grids; fresh-spot `x + counter*30` dose-spreading; double-stack grazing alignment.
6. **Intent:** Hard-Xray + tender-resonant temperature GIWAXS/NEXAFS on perovskite/OSC films; textbook legacy temperature-into-filename + per-point energy/angle counting.

---

## 4. 30-user-AFurst-2024C3_Thermal.py
1. **Size / plans:** ~40 KB, ~45 `def`s (Oleg-Gang thermal framework instance).
2. **User/group:** A. Furst program on the Gang thermal stage (`FLu`,`HKim`,`MH`,`WLiu`) — DNA / nanoparticle superlattice self-assembly (melting/recrystallization).
3. **Use-cases:** **in-situ temperature kinetics — melting-point (Tm) / annealing** (slow 0.1 °C/min ramps, hold-and-measure, time-temperature series `run_melting`/`run_Tm`/`run_melting_Tm`); **transmission SAXS** of superlattices; **micro-mapping** with anti-damage fresh-spot indexing (`getSamMap`, `i_dict`); multi-sample bar (`sample_dict`/`pxy_dict`); multi-angle WAXS arc series; line transmission scans.
3b. **Detectors:** `pil2M` (+`pil900KW`/`pil300KW` for wsaxs; `ls.ch1_read`).
4. **Acquisition pattern: LEGACY + anti-pattern (nested `RE(...)`).** Plans are *not* generators end-to-end — they call `RE()` inside Python `for`/`while` loops and stash names in `RE.md`:
   ```python
   while time.time() < t0 + t_total_T40:
       for k in ks:
           mov_sam(k); RE(bps.mv(piezo.x, pos_list[i_dict[k]%N][0]))
           sample = RE.md['sample']
           RE(measure_saxs(exposure_t, sample=sample+'_T_%.2f'%getT()+'_runt_%.0fs'%(time.time()-tt0)))
           i_dict[k]+=1
   ```
   - `RE_`-prefixed twins wrap blocking `RE()`; `Measure_Map` also `RE(bp.count(...))` per pixel.
5. **Notable techniques/hardware:** thermal abstraction `gotoT/setT/getT/startT/stopT`; per-sample position-map cycling (`i_dict[k]%N`) to dodge beam damage over long thermal runs; temperature + elapsed-time baked into filename; heaviest global-mutable-state reliance in the batch.
6. **Intent:** Long unattended DNA-NP lattice melting/annealing SAXS with fresh-spot mapping; furthest from the single-run model (blocking `RE()` + `RE.md`).

---

## 5. 30-user-Thomas.py
1. **Size / plans:** ~37 KB, ~25 `def`s (Subramanian/Thomas + Harvard-poly + NT/PT guests).
2. **User/group:** Thomas / Subramanian (`VS`,`NT`,`PT`,`HarvPoly`,`Static`) — polymer-electrolyte (S2VP, ionic-liquid-doped) bulk & thin films.
3. **Use-cases:** **GISWAXS** w/ alignment + reflectivity flags (`run_giswaxs`), **temperature SWAXS** (`run_tswaxs`, `run_Thomas_temp`), **isothermal time-series** (`run_isothermal`, Nmax frames w/ y-step), **cryo-SAXS** (`saxs_cryo*`), **rotation scans** (`rotscan_Thomas` over `prs`), capillary SWAXS, GISAXS bars.
3b. **Detectors:** `pil2M`+`pil900KW`(+`pil300KW` commented); arc-conditional.
4. **Acquisition pattern: MIXED.** Several plans use coordinated `bp.list_scan` (x/y position lists) and `bp.rel_grid_scan` (rotation map); GISWAXS / isothermal / cryo decay to per-point `bp.count`:
   ```python
   yield from bp.list_scan(dets, piezo.x, xss.tolist(), piezo.y, yss.tolist())   # GOOD
   yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)            # GOOD (rotscan)
   # vs run_giswaxs: sample(align)→arc→incident-angle nested → bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** alignment results appended to an external `aligned_positions.txt`; `alignement_gisaxs(..., flag_reflect=...)`; `RE.md['SAXS_setup']` geometry dict in header; per-sample incident-angle arrays (0.12/0.16/0.20°).
6. **Intent:** Polymer-electrolyte GISWAXS + temperature/isothermal/cryo SWAXS; partially coordinated (list/grid scans) but GI/in-situ legs are per-point legacy.

---

## 6. 30-user-Cordova.py
1. **Size / plans:** ~22 KB, ~16 `def`s.
2. **User/group:** Cordova (`IC`) — multilayer thin films / buried-interface (YAVE/YAHY, "ML") resonant-reflectivity work.
3. **Use-cases:** **tender resonant X-ray reflectivity (XRR)** at the **Sn L-edge** (~3900–4100 eV; ai 0.1–5°, fwd/rev sweeps); **resonant WAXS/NEXAFS** films at Sn edge; **incident-angle (ai) scans on multilayers** (`ai_scan_multilayer*`); **fluorescence scan** (`fluo_scan`); attenuator-management + energy-stepping helpers (`function_att`, `mv_energy`).
3b. **Detectors:** `pil300KW` (WAXS/reflectivity), `pil2M`.
4. **Acquisition pattern: LEGACY.** Reflectivity = sample(align)→energy→direction(fwd/rev)→angle nested loops with per-point `bp.count`; Al attenuator ladder + GV7 alignment handshake:
   ```python
   yield from bps.mv(att2_9,'Insert'); ... ; yield from bps.mv(att2_12,'Insert')
   for e in energies:
       for d in ['fwd','rev']:
           for inc_ang in (incident_angle if d=='fwd' else incident_angle[::-1]):
               yield from bps.mv(piezo.th, ai0 + inc_ang)
               sample_id(user_name='IC', sample_name=...)
               yield from bp.count([pil300KW], num=1)   # ONE run per reflectivity angle
   ```
   - `fly_scan_ai` present but commented; one plan body has Python syntax errors (missing `:`) — clearly a scratch/night file.
5. **Notable techniques/hardware:** GV7 open→align (`alignement_gisaxs`)→close gate-valve sequence per sample; resonant (energy-tuned) reflectivity; multi-Al `att2_9..12` ladder for dynamic-range; resonant energies bracketed around the Sn edge.
6. **Intent:** Tender-resonant XRR + NEXAFS on multilayer buried interfaces (Sn edge); fully legacy per-angle reflectivity counting (XRR archetype for this batch).

---

## 7. 30-user-Tiwale.py
1. **Size / plans:** ~21 KB, ~13 `def`s (Tiwale + Nikhil).
2. **User/group:** Tiwale (`SR`) / guest Nikhil — lithography resist & sequential-infiltration materials (SU-8, ZEP, UV6, PAG photoresists; EUV/e-beam exposed).
3. **Use-cases:** tender **NEXAFS** at **S K-edge** (2430–2520 eV, fine 0.5 eV), **Cl-edge** (2800–2850), **Zn K-edge** (9640–9750 eV) on infiltrated resists; **resonant SAXS** at S-edge; **GISAXS** w/ per-sample alignment; **prs-rotation SAXS** (`SAXS_S_edge_allprs`); multi-sample S-edge surveys; ex-situ SIS Zn-edge series.
3b. **Detectors:** `pil300KW` (NEXAFS/WAXS), `pil2M` (SAXS).
4. **Acquisition pattern: LEGACY.** energy (and/or `prs`) loops with per-point `bp.count`; beam current `xbpm3.sumX.value` into filename; GV7 + attenuator alignment handshake:
   ```python
   energies = [...2475..2485 @0.5eV...]
   for e in energies:
       yield from bps.mv(energy, e); yield from bps.sleep(1)
       bpm = xbpm3.sumX.value
       sample_id(user_name="SR", sample_name=f"nexafs_{name}_{e}eV_angle{ai}_bpm{bpm}")
       yield from bp.count([pil300KW], num=1)
   ```
   - `SAXS_S_edge_allprs` instead loops `prs` (texture/rotation) per point.
5. **Notable techniques/hardware:** `alignement_Tiwale` caches per-sample th/y via `global`; GV7 open→align→close; `att2_9` insert for grazing NEXAFS; fine multi-segment energy grids; multi-edge coverage (S/Cl/Zn) on resist chemistry.
6. **Intent:** Tender multi-edge NEXAFS + resonant/rotation SAXS + GISAXS on lithography resists; clean but fully legacy per-energy counting.

---

## 8. 30-user-Liu-Akron.py
1. **Size / plans:** ~13 KB, 6 `def`s (Liu / Akron, 2023→2024).
2. **User/group:** Liu group, U. Akron (`TB`,`PW`) — capillary polymer/solution samples (transmission SWAXS with quantitative transmission).
3. **Use-cases:** **transmission SWAXS capillary multi-sample bar** w/ V-line scans (3 pts/capillary), **quantitative transmission measurement** (attenuated direct-beam vs sample via beamstop-diode/stats), multi-arc (0/20°), on-axis camera snapshot per sample.
3b. **Detectors:** `pil2M`+`pil900KW`; `pil2M_bs_pd` beamstop photodiode; `OAV_writing` camera.
4. **Acquisition pattern: LEGACY (with in-plan transmission normalization).** arc→sample→point nested; transmission computed by reading `pil2M_stats1_total` back out of `db[-1].table()` and folded into the filename; per-point `bp.count`:
   ```python
   yield from atten_move_in()
   yield from bp.count([pil2M]); stats1_direct = db[-1].table('primary')['pil2M_stats1_total'].values[0]
   ...
   trans = np.round(stats1_sample/stats1_direct, 5)
   sample_id(user_name=user, sample_name=f"{name}{get_scan_md()}_loc{i}_trs{trans}")
   yield from bp.count(dets)
   ```
5. **Notable techniques/hardware:** Sn-attenuator in/out helpers (`atten_move_in/out`, status-polled); beamstop x-shift to expose direct beam for transmission; `OAV_writing` sample image as a separate count; `get_scan_md()` metadata helper.
6. **Intent:** Transmission SWAXS of polymer capillaries with per-sample quantitative transmission; legacy per-point counting plus clever (but global-state) databroker-readback normalization.

---

## 9. 30-user-Billinge.py
1. **Size / plans:** ~14 KB, 4 `def`s (2023_3 cycle).
2. **User/group:** Billinge group (`IB`) — alkali-halide salt partitioning between organic/aqueous phases (LiBr/NaBr/KBr/RbBr in DIPA/TOA solvents).
3. **Use-cases:** **anomalous/resonant tender-edge NEXAFS** at **Br K-edge** (13450–13530 eV) and **Rb K-edge** (15175–15260 eV); **resonant (anomalous) SWAXS** at the same edges (energy lists clustered at the absorption feature, ~0.5 eV step); multi-arc (0/20/40°); fresh-spot meshgrid raster vs energy.
3b. **Detectors:** `pil900KW`(NEXAFS) + `pil2M` (resonant SAXS); arc-conditional.
4. **Acquisition pattern: LEGACY.** sample→arc→energy nested with a per-energy fresh-spot meshgrid; bpm into name; arc-direction reversal; per-point `bp.count`:
   ```python
   yss = np.linspace(ys, ys+350, len(energies)); yss, xss = np.meshgrid(yss, xss)  # fresh spot/energy
   for e, xsss, ysss in zip(energies, xss.ravel(), yss.ravel()):
       yield from bps.mv(energy, e); if xbpm2.sumX.get()<50: re-poll
       yield from bps.mv(piezo.y, ysss, piezo.x, xsss)
       sample_name = f'{name}_pos{pos}{get_scan_md(tender=True)}_bpm{bpm}'
       yield from bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `engage_detectors()`; `get_scan_md(tender=True)` helper; energy "rest" parking between samples (drives DCM back to pre-edge); anti-damage spread via `linspace`-meshgrid; multi-edge anomalous contrast for ion speciation.
6. **Intent:** Anomalous tender-edge NEXAFS + resonant SWAXS for ion partitioning in liquid–liquid extraction; pure-legacy per-energy fresh-spot counting.

---

## 10. 30-user-White.py
1. **Size / plans:** ~9 KB, 5 `def`s (2022, RT/DD).
2. **User/group:** White / Toney-adjacent (`RT`,`DD`) — halide-perovskite (CsPbBr3) thin films + self-assembled-monolayer (SAM) molecules on TiO2/sapphire (2PACz/BPA derivatives).
3. **Use-cases:** **in-situ temperature-ramp GIWAXS/GISAXS** (in-vacuo & in-air heating; `temp_ramp`→`temp_align_waxs/saxs`), **static multi-sample GIWAXS bar** (`giwaxs_White`) w/ per-sample alignment + multi-arc (0/2/20/22°) + multi incident-angle.
3b. **Detectors:** `pil900KW`(+`pil2M` when arc≥15).
4. **Acquisition pattern: LEGACY.** temperature ramp uses a **pre-tabulated per-temperature alignment LUT** (`ai_offset`/`y_offset` vs `temp_list`) then a single `bp.count`; static bar = sample(align)→arc→angle nested per-point `bp.count`; temperature + elapsed-time into filename:
   ```python
   idx = np.argmin(abs(np.asarray(temp_list)-temp))
   yield from bps.mvr(piezo.th, 0.2+ai_offset[idx]); yield from bps.mvr(piezo.y, y_offset[idx])
   sample_id(user_name='DD', sample_name='...CsPbBr3..._%.1f_..._%.1fs'%(temp, time.time()-t0))
   yield from bp.count([pil900KW])
   ```
5. **Notable techniques/hardware:** tabulated thermal-drift correction (alignment offset vs temperature, both WAXS- and SAXS-geometry tables); `att2_1` open; fresh-spot `piezo.x += 50`; in-vacuo vs in-air heating modes.
6. **Intent:** In-situ thermal-ramp GIWAXS/GISAXS of perovskites + SAM-on-oxide bars with hard-coded thermal-drift LUT; fully legacy (global `t0`, time-into-name).

---

## 11. 30-user_Ruan.py
1. **Size / plans:** ~9 KB, 6 `def`s.
2. **User/group:** Ruan / Su-adjacent (`ZR`,`OS`) — solution/buffer samples for ion-edge spectroscopy.
3. **Use-cases:** **solution NEXAFS** at **S K-edge** (2450–2500), **Cl-edge** (2800–2850), **Br K-edge** (13450–13500); **resonant SAXS** at each edge (energy lists at the absorption features) with multi-arc (0/6.5/13/19.5°); post-measurement reference frame at pre-edge.
3b. **Detectors:** `pil300KW` (NEXAFS) + `pil2M` (resonant SAXS).
4. **Acquisition pattern: LEGACY.** energy (and arc) loops with per-point `bp.count`; beam current `xbpm3.sumY.value` into name; some plans step `piezo.y` per energy (fresh spot):
   ```python
   for e in energies:                          # np.linspace(2450, 2500, 51) etc.
       yield from bps.mv(energy, e)
       sample_id(user_name="ZR", sample_name=f"{name}_{e}eV_xbpm{xbpm3.sumY.value}")
       yield from bp.count([pil300KW], num=1); yield from bps.sleep(2)
   ```
5. **Notable techniques/hardware:** GV7 close before in-vacuum SAXS; energy parking back to pre-edge between sweeps; resonant energies hand-picked at edge features; `xbpm3.sumY` flux into name.
6. **Intent:** Solution multi-edge NEXAFS + resonant SAXS for ion speciation; clean but pure-legacy per-energy counting.

---

## 12. 30-user-Kang.py
1. **Size / plans:** ~3 KB, 3 `def`s.
2. **User/group:** Kang (`MK`) — additively-fabricated / fiber-textured samples (AGIB AuPd "hopper"/"disc" structures).
3. **Use-cases:** **rotation (prs) SAXS/WAXS texture mapping** — full `prs` rotation (-90°→+90°) per sample at multiple heights (top/mid/bot/cen) and multiple waxs arc positions; attenuated-WAXS variant taking SAXS first then attenuated WAXS.
3b. **Detectors:** `pil2M`+`pil300KW` (rayonix/MAXS commented).
4. **Acquisition pattern: MIXED.** Production plan uses coordinated `bp.grid_scan` over `prs` × `waxs` (one run/sample — good); "fast" and "att" variants regress to per-point `bp.count` over the same axes:
   ```python
   yield from bp.grid_scan(dets, prs, *prs_range, waxs, *waxs_range, 1)   # GOOD (rotation_saxs)
   # vs rotation_saxs_fast: for wa: for pr: mv(prs,pr); bp.count(dets, num=1)
   ```
5. **Notable techniques/hardware:** `prs` full ±90° rotation for orientation/texture distribution; multi-height sampling per object; `att1_5/att1_6` insert + `pil2M_pos.x/y` reposition for attenuated multi-arc WAXS stitching.
6. **Intent:** Rotation-resolved SAXS/WAXS texture of fiber/AM AuPd structures; grid-scan version is near-modern, the per-point variants are legacy.

---

## 13. 30-user-JiaLu_XAS.py
1. **Size / plans:** ~6 KB, 2 `def`s + extensive run-log header.
2. **User/group:** Jia Lu / Y. Zhang / W. Liu (`JLi`,`YZhang`,`WL`) — XAS on multi-sample bars (Ir / S edge).
3. **Use-cases:** **XAS / NEXAFS** at **Ir L3-edge** (11150–11400 eV, very fine 0.2 eV) and **S K-edge** (2460–2480 eV); fluorescence XAS via **`amptek`**; full-beam vs **attenuated-beam (4×) + beamstop-out** configurations; fwd + reverse energy sweeps; multi-sample bar (`sample_dict`/`pxy_dict`).
3b. **Detectors:** `pil2M`(+`pil900KW`+`amptek` fluorescence in commented runs).
4. **Acquisition pattern: LEGACY + nested `RE()`.** Driver `run()` loops samples calling blocking `RE(S_edge_one_sample(...))`; inner plan loops energy with per-point `bp.count`; bpm into name:
   ```python
   def run():
       for k in ks:
           mov_sam(k); RE(S_edge_one_sample(sample=RE.md['sample']))
   # inner: for e in Elist: mv(energy,e); if xbpm2.sumX.get()<100: re-poll; bp.count([pil2M], num=1)
   ```
5. **Notable techniques/hardware:** `amptek` SDD fluorescence channel for dilute XAS; beam-stop-out + 4× attenuation for transmission XAS dynamic range; reverse-scan repeat for radiation-damage / hysteresis check; threshold/autog detector setup notes in header.
6. **Intent:** Transmission + fluorescence XAS (Ir L3 / S K) on solution/sample bars; legacy per-energy counting wrapped in blocking `RE()` driver.

---

## 14. 30-user-JKim.py
1. **Size / plans:** ~5 KB, 5 `def`s.
2. **User/group:** J. Kim (`KR`) — operando electrochemistry (Cu nanoparticle full-cell, applied potential).
3. **Use-cases:** **operando XAS / energy scan** at **Cu K-edge** (8900–9100 eV, fine 1 eV near edge) on a full electrochemical cell (`-noVapp`/Vapp); **in-situ time-series** (`continous_run`, frames with delay, elapsed-time in name); SWAXS at multi-arc.
3b. **Detectors:** `pil900KW`(+`pil2M` when arc≥15).
4. **Acquisition pattern: LEGACY.** energy loop (per-point `bp.count`) and a frame-count time-series loop; `get_more_md()` helper + `RE.md['tstamp']` global timestamp folded into names:
   ```python
   create_timestamp()  # RE.md['tstamp'] = time.time()
   for i in range(frames):
       name_sample(sname, tstamp)   # appends _t{elapsed}
       yield from bp.count([pil900KW, pil2M]); yield from bps.sleep(wait)
   ```
5. **Notable techniques/hardware:** `RE.md`-stored alignment LUT/`sample_pos0`/`tstamp` (and `clear_md` to reset per cell change); low-flux energy re-poll (`if xbpm2.sumX.get()<20`); operando full-cell (electrochemistry) context.
6. **Intent:** Operando Cu K-edge XAS + in-situ time-series on electrochemical cells; legacy per-energy / per-frame counting with global timestamp/alignment state.

---

## 15. 30-user-AFRL.py
1. **Size / plans:** ~1 KB, 1 `def` (smallest; scratch).
2. **User/group:** AFRL / Schantz (proposal `305934_Schantz`) — liquid (water) reference / long time-series.
3. **Use-cases:** **in-situ transmission SAXS/WAXS time-series** of a liquid (water), temperature-logged, very long polling loop (`num=10000`, 2 s spacing).
3b. **Detectors:** `pil2M`+`pil300KW`+`ls.ch1_read` (temperature in det list).
4. **Acquisition pattern: LEGACY (polling).** `for i in range(10000)` with per-iteration `bp.count`; temperature `ls.ch1_read.value` into name; raw `pil2M.cam.file_path.put(...)` write-path override; commented fast-shutter/pin-diode transmission:
   ```python
   for i in range(num):                       # num = 10000
       temp = ls.ch1_read.value
       sample_id(user_name=sample, sample_name="{i}_{temperature}C".format(...))
       yield from bp.count([pil2M, pil300KW, ls.ch1_read], num=1); yield from bps.sleep(2)
   ```
5. **Notable techniques/hardware:** Lakeshore temperature in the detector list (recorded — unusually good) but also `.value` into filename; manual `cam.file_path.put` to a ramdisk path; commented `fs.open()/close()` + `pdcurrent2` transmission.
6. **Intent:** Long unattended transmission SWAXS time-series of a liquid reference; minimal legacy polling loop.

---

## 16. 30-user-ECD-3dprinterLutz_OffsetStart.py
1. **Size / plans:** ~11 KB, ~11 `def`s (ECD = extrusion / direct-write; Lutz, offset-start variant).
2. **User/group:** Lutz / ECD 3D-printing program (`ED`) — in-situ small/wide-angle scattering during direct-ink-write / extrusion 3D printing.
3. **Use-cases:** **in-situ 3D-printing scattering** (hardware-triggered acquisition synchronized to the printer), **time-resolved crystallization/kinetics** during/after extrusion, **post-print height-profile** scans, **ex-situ raster** of a printed bar, alignment to the substrate/film & nozzle.
3b. **Detectors:** `pil300KW`+`pil2M` (WAXS+SAXS together; arc 0/6.5/13°).
4. **Acquisition pattern: LEGACY + external hardware-trigger handshake.** A `while` loop watches EPICS bits set by the printer; on each trigger it counts at the filament:
   ```python
   monitor_pv        = EpicsSignal("XF:11ID-CT{M1}bi2", ...)   # printer "running"
   trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", ...)   # printer "shoot now"
   while monitor_pv.get() == 1:
       if trigger_signal_pv.get() == 1:
           experimental_adjustement()          # sets sample_id from names[0]
           yield from data_acquisition(exp_t, meas_t)    # det_exposure_time + bp.count(det, num=1)
       yield from bps.sleep(0.5)
   ```
   - `track_printer_timeRes` adds a long-dynamics leg: after the trigger, `while t1-t0<=1800: bp.scan(dets, waxs, 0,13,3)` (arc sweep loop, ~30 min).
   - ex-situ / post-print legs use coordinated `bp.scan(dets, waxs, *arc)` and `bp.rel_scan(dets, piezo.y, *y_range)` (one run/scan — better).
5. **Notable techniques/hardware:** printer↔beamline **digital-IO handshake** (`XF:11ID-CT{M1}bi2/3/4`); `height` = half-filament-width offset so the beam sits in the **middle of the extruded filament** (returns to nozzle via `mvr(stage.y, -height)`); `SMI_Beamline().modeAlignment/modeMeasurement`, `setDirectBeamROI`, derivative-based height alignment (`align_height_hexa` w/ `ps(der=True)`), nozzle-center alignment; beam-damage study (`bp.count(num=it, delay=sleep_time)`).
6. **Intent:** Trigger-synchronized in-situ SWAXS during extrusion 3D printing + post-print profiling; legacy per-trigger counting gated by an external printer state machine.

### 3D-printing in-situ workflow (characterization)
The printer is the **acquisition master**. Three EPICS digital-input PVs on the control
chassis (`XF:11ID-CT{M1}bi2` = printer running, `bi3` = ready-for-trigger, `bi4` = fire)
form a handshake: the plan **polls in a `while` loop** (`bps.sleep(0.5)` between checks) and,
each time the printer asserts `bi4`, refreshes the filename and **counts SAXS+WAXS at the
filament** (`bp.count([pil300KW, pil2M], num=1)`), clearing the trigger after the requested
number of shots. Geometry is keyed to the extrusion: alignment finds the **substrate/film
interface** (derivative-edge `align_height_hexa`), then the beam is offset **up by
`height` = half the filament width** so it interrogates the **middle of the freshly-printed
filament**; on exit the plan steps back down to the nozzle. The time-resolved variant
(`track_printer_timeRes`) follows the initial extrusion burst with a **~30-minute
long-dynamics loop** that repeatedly sweeps the WAXS arc (`bp.scan(waxs, 0,13,3)`) to track
crystallization/relaxation. Ex-situ/post-print legs (`ex_situ*`, height-profile, bkg)
use coordinated `bp.scan`/`bp.rel_scan` and are closer to acceptable. The whole thing runs
**outside the one-run-per-sample model**: it is a long-lived monitoring generator with the
filename as global mutable state and the printer driving cadence.

---

# BATCH SYNTHESIS

- **Distinct archetypes (≈8) in this batch:** (1) **CD-SAXS / CD-GISAXS rocking critical-dimension metrology** (CDSAXS — `prs` rocking of nanopatterned gratings, the signature technique of the batch); (2) **tender resonant NEXAFS / anomalous SWAXS at absorption edges** (Toney, Cordova, Tiwale, Billinge, Ruan, JiaLu, JKim — S/Cl/P/Ti/Zn/Br/Rb/Sn/Ir/Cu edges with fine ~0.2–0.5 eV grids); (3) **GISAXS/GIWAXS thin-film** with per-sample auto-alignment + incident-angle + waxs-arc sweeps (Toney, Thomas, White, Tiwale, Thedford); (4) **in-situ temperature ramping / melting / annealing kinetics** (AFurst DNA-NP Tm, Toney, White, Thomas, AFRL); (5) **transmission SWAXS multi-sample / capillary bars** (Liu-Akron w/ quantitative transmission, Thedford wells/caps, JiaLu, AFRL); (6) **spatial raster / micro-mapping** (Thedford `rel_grid_scan`, AFurst `getSamMap`); (7) **tender resonant X-ray reflectivity (XRR)** (Cordova — Sn-edge ai sweeps); (8) **in-situ 3D-printing scattering** (ECD-3dprinterLutz — hardware-triggered) and **rotation/texture SAXS** (Kang, Tiwale `allprs`).
- **Legacy is overwhelmingly prevalent; zero MODERN code:** No file in this batch contains `run_decorator`/`stage_decorator`/`trigger_and_read`/`declare_stream`. ~12/16 are essentially pure **LEGACY** (CDSAXS, Toney, AFurst, Cordova, Tiwale, Billinge, White, Ruan, JiaLu, JKim, AFRL, ECD-3dprinterLutz); 4 are **MIXED** only in the sense that they use coordinated `bp.grid_scan`/`bp.list_scan`/`bp.rel_grid_scan` (one run per scan) somewhere (Thedford, Thomas, Kang) — and even those fall back to per-point `bp.count` for GI/in-situ/bar legs. This is the least-migrated batch reviewed so far.
- **Universal legacy signature — one run per data point:** the dominant idiom is nested Python `for` loops (`prs` rocking angle / incident angle / energy / waxs-arc / sample) whose innermost statement is `yield from bp.count(dets, num=1)`. CD-SAXS is the extreme case: a 121-point (`prs` -60→+60°) rocking curve = 121 separate Bluesky runs per grating, repeated with bracketing reference frames and detector y-stitch.
- **Filename = global mutable state everywhere:** all 16 files set the output filename via `sample_id(user_name, sample_name)` and/or `RE.md["sample"]`/`RE.md["sample_name"]`. None promotes the target filename to an ophyd `Signal`. Several files lean on metadata helpers (`get_scan_md()`, `get_scan_md(tender=True)`, `get_more_md()`) that still string-format into the name rather than recording devices.
- **Context read as `.value`/`.get()`/`.position` into strings, not recorded as devices:** temperature (`ls.input_A.get()-273.15`, `getT()`, `ls.ch1_read.value`), beam current (`xbpm2.sumX.get()`, `xbpm3.sumY.value`), energy (`energy.position.energy`), SDD (`pil2M_pos.z.position`), and even computed **transmission** (Liu-Akron) and `prs` rocking angle are formatted into filenames — the single biggest data-provenance gap. (AFRL is a partial exception: it puts `ls.ch1_read` into the detector list, so temperature is at least recorded — though also duplicated into the name.)
- **Notable anti-patterns beyond plain legacy:** **AFurst** and **JiaLu** call **`RE(...)` inside `for`/`while` loops** (blocking, re-entrant, non-composable — the AFurst Tm framework is the worst offender, with `RE_`-prefixed twins); **ECD-3dprinterLutz** runs a **long-lived polling generator gated by external EPICS trigger bits** (printer is the master, no run-per-sample); **AFRL** does a raw `pil2M.cam.file_path.put(...)` write-path override; **Cordova** contains uncompiled scratch code (missing `:` on `for`/`if`).
- **CD-SAXS rocking — the defining technique:** transmission SAXS through a grating while rocking the **`prs` precision rotation stage (phi)** ~ -60°→+60° in 121 steps (up to 2001 in GISAXS variants) to tomographically sample the grating's reciprocal-space rods → reconstruct line/space cross-section (CD, sidewall angle, LER, pitch walking). Workflow: bracketing reference frames at a fixed `phi_offset`, detector y-stitch (`pil2M_pos.y ±4.3 mm`) for the module gap, multi-pitch x-offset surveys, and a CD-GISAXS mode rocking `prs`/`stage.th` at grazing incidence. Every rocking angle is its own run — the prime modernization target (→ single coordinated `prs` scan per grating, `prs`/`xbpm` in-stream). `prs` rocking/rotation also recurs as texture/orientation sampling in Kang and Tiwale.
- **3D-printing in-situ — the other distinctive workflow:** the printer drives a **digital-IO handshake** (`XF:11ID-CT{M1}bi2/3/4`); the plan polls and, on each printer "fire", counts SAXS+WAXS **at the middle of the extruded filament** (beam offset up by `height` = half-filament-width from the substrate interface found by derivative-edge alignment). A time-resolved leg follows the burst with a ~30-min repeated WAXS-arc sweep to track crystallization; post-print legs use coordinated `bp.scan`/`bp.rel_scan`. It is fundamentally a long-lived monitoring generator outside the run-per-sample model.
- **Conditional detector lists are ubiquitous and correct-in-spirit:** `dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]` (Toney, Thedford, Thomas, White, Liu-Akron, Billinge, JKim) drops SAXS when the WAXS detector blocks it — the desired modern form is separate declared SAXS/WAXS streams. Tender-edge work adds attenuator/gate-valve choreography (GV7 open→align→close; `att2_9..12` ladders) and low-flux energy re-polling (`if xbpm*.sum*<threshold: re-set energy`).
- **Hardware breadth to support in a modern template:** SAXS `pil2M` + WAXS `pil900KW`/`pil300KW` (+ `rayonix` MAXS, `amptek` fluorescence for XAS); the **`prs` rotation stage** (CD-SAXS rocking + texture); Lakeshore `ls` + Gang thermal abstraction (`gotoT/getT`) for temperature; **printer digital-IO trigger** + nozzle/filament alignment for in-situ 3D printing; beamstop diode (`pil2M_bs_pd`) + `db[-1].table()` readback for quantitative transmission; on-axis camera (`OAV_writing`); tender DCM `energy` across S→Rb→Ir edges with attenuator/GV7 handshakes. The modern SMI pattern (single decorated run, target filename as a `Signal`, temperature/energy/bpm/prs/transmission as in-stream signals or baseline, slow `waxs.arc`/`prs`/`stage.th` outermost) is **absent throughout this batch** and would benefit every file here.

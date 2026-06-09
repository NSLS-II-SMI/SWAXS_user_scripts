# Legacy SMI/SWAXS Acquisition Scripts — Classification (Batch 03)

Beamline: NSLS-II SMI (12-ID), SWAXS. Bluesky/Ophyd plan scripts.
Scope: scientific use-case and acquisition-pattern classification only (no fixes).
Detector legend: `pil2M`=SAXS, `pil900KW`/`pil300KW`=WAXS, `rayonix`=MAXS,
`amptek`=fluorescence/SDD (tender XAS), `pdcurrent*`=pin-diode, `xbpm2/3`=X-ray BPM,
`OAV_writing`=on-axis video. Stages: `piezo.*` (SmarAct GI sample stack x/y/z/th),
`stage.*` (hexapod/coarse), `waxs.arc` (in-vacuum WAXS arc), `energy` (DCM tender/hard),
`ls.*` (Lakeshore), `LThermal` (Linkam GI thermal stage), `syringe_pu` (syringe pump).

**Batch-wide headline:** 0/13 files use the modern run-per-experiment pattern
(`@bpp.run_decorator`/`stage_decorator` + `inner()` + `trigger_and_read`). All use the
legacy idiom: nested `for` loops, one `bp.count`/`bp.scan`/`bp.rel_*` per data point
(= one Bluesky run per point), global mutable `sample_id(user_name, sample_name)` for
filenames, `RE.md`/`.get()`/`.value` reads folded into filename strings, and hard-coded
sample/coordinate lists in the plan body. The only forward-leaning material is in
`30-Harward.py` (2026 `inner_*` sub-generators + temperature recorded as a device via
`dets + [ls.input_A]`) and a commented-out `temp_series_grid` that records the filename
as a `Signal`. `30-templates-Patryk.py` is a snippet/reference library, not modern plans.

---

## 1. 30-Harward.py
1. ~6,680 lines (~270 KB); ~100 plan functions (largest by far). Multi-year accretion 2021_1 → 2026_1.
2. **User/group:** Fakhraai/SMI polymer-thin-film group; many operators — "MW" (Milan), Reena, Mustafa, Fritz, Fotini, Jacopo, "ML". (Filename "Harward"=Harvard-style omnibus notebook.)
3. **Use-cases:** temperature ramping/annealing (dominant) on GI thermal stages — both Lakeshore (`ls.output1`) and **Linkam** (`LThermal`); GISAXS/GIWAXS + transmission SWAXS; microfocus **raster mapping** (mesh/grid/linescan via `rel_grid_scan`/`rel_scan`); **multi-sample "puck"/disc bars** (4-pt per sample); in-situ **time-series/kinetics** (burst + loop "single_measurement"); **tensile/pull mechanical** in-situ (`tensile_*`, `pull_measurement_*`); alignment routines (`alignement_gisaxs*`).
3b. **Detectors:** `pil2M` (SAXS, wa≥~15) + `pil900KW`/`pil300KW` (WAXS); 2 stray `rayonix` (MAXS) refs. Some plans append `ls.input_A` (temp) to det list.
4. **Pattern: LEGACY → MIXED.** Bulk is legacy nested loops + `bp.count`. The 2026_1 plans are transitional:
   ```python
   def inner_go_to_temp(temperature, ...): LThermal.setTemperature(...); ... yield from bps.sleep(...)
   def inner_measure_samples():
       ... yield from bp.rel_grid_scan(dets + [ls.input_A], piezo.y, *yr, piezo.x, *xr)   # T recorded as device
   yield from main_experimental_logic()   # structured cleanup/go_to_temp/measure orchestration
   ```
   Most-modern (but **commented out**, lines ~6063-6122) `temp_series_grid`:
   `s = Signal(name='target_file_name'); ... s.put(sample_name); yield from bp.count(dets + [s])` — filename recorded as a device. Still uses `RE.md["sample_name"]`.
5. **Notable:** dual thermal back-ends (`ls` Lakeshore + `LThermal` Linkam); in-vacuum `waxs.arc` as outer/slow axis; hexapod tilt for transmission ("hexa tilt"); GI `piezo.x/y/z/th` stack; `det_exposure_time_old` burst mode for kinetics; `bps.finalize_wrapper` mentioned (commented) for Ctrl-C-safe temp shutdown; `get_scan_md()` helper for metadata-in-filename.
6. **Intent:** Group "lab-notebook" of T-resolved GI/transmission SWAXS, microfocus maps, multi-sample pucks and in-situ tensile/kinetics for polymer thin films — incremental yearly copy-edit per beamtime.

---

## 2. 30-user-Gregory.py
1. ~1,140 lines; 14 plan functions.
2. **User/group:** Gregory (GU-309504); operators "AA", "SG". Based on prior `30-user-Gordon`.
3. **Use-cases:** **TReXS / resonant tender-&-hard-energy GIWAXS+SAXS edge scans** across many elements: Sulphur K, Chlorine K, **Platinum L**, **Tellurium L**, **Calcium K**, **Silver L** edges; energy/XAS edge series with WAXS-arc sweep; beam-damage mitigation by stepping `piezo.y` across the energy list.
3b. **Detectors:** `pil2M`+`pil900KW` (SAXS gated off when WAXS arc <10–15°); `xbpm3.sumX` flux normalization in filename.
4. **Pattern: LEGACY.** Per-energy separate runs:
   ```python
   for wa in waxs_arc:
       for e, xsss, ysss in zip(energies, xss, yss):
           yield from bps.mv(energy, e); yield from bps.sleep(2)
           yield from bps.mv(piezo.y, ysss); ... yield from bp.count(dets, num=1)
   ```
5. **Notable:** per-element hard-coded `energies = np.arange(...)` edge grids; `meshgrid` y-walk to spread dose; `move_E_slowly` ramp helper; "go back gently with energy" de-tuning at end.
6. **Intent:** Multi-edge resonant (tender + Pt/hard) GIWAXS/SAXS of doped conjugated-polymer films to get element-specific contrast.

---

## 3. 30-user-Meli.py
1. ~697 lines; 8 plan functions.
2. **User/group:** Meli; operator "LR" (Reynolds-Meli group), one "DM" diode-calibration plan.
3. **Use-cases:** **In-situ electrochemistry tender-XAS GIWAXS** — Sulphur K & **Chlorine K** edge measurements on electrochemically doped/dedoped organic semiconductors (pgBTTT, pedot, PG2T, NaPSS/KCl); **K-edge x-scan & time-scan kinetics** under applied bias (Vds/Vgs in names); fluorescence-yield XAS; flux-vs-diode edge calibration.
3b. **Detectors:** `pil2M`+`pil900KW` + **`amptek`** (energy-dispersive fluorescence/SDD); `xbpm2.sumX` + `pdcurrent2` for normalization/calibration.
4. **Pattern: LEGACY.** Two-direction (pos1 fwd / pos2 reverse) energy loops with dose-walk in `piezo.x`/`stage.x`:
   ```python
   for e in energies:
       yield from bps.mv(energy, e); yield from bps.sleep(2)
       if xbpm2.sumX.get() < 50: ... (re-tune)
       yield from bps.mv(piezo.x, xs - counter*20); yield from bp.count(dets, num=1)
   ```
5. **Notable:** **hexapod GISAXS** double-stack alignment (`alignement_gisaxs_doblestack`); Sn/Al attenuator inserts (`att2_9/10`); flux-dropout re-tuning guard; bias encoded in sample name only.
6. **Intent:** Operando electrochemical tender-edge (S/Cl) GIWAXS + fluorescence on conjugated-polymer transistors/electrodes.

---

## 4. 30-user-Reynolds.py
1. ~662 lines; ~10 plan functions.
2. **User/group:** Reynolds; operators "GF", "PN" (Phong/Nguyen), "SZ" (Song), "PW" (Patryk).
3. **Use-cases:** **Sulphur K-edge tender NEXAFS/TReXS WAXS** on multi-sample bars (transmission & GI); **tensile-stage** tender in-situ loops (`song_*tensile*`, infinite time loops); SAXS/WAXS mechanical kinetics; high-res energy surveys with WAXS-arc sweep.
3b. **Detectors:** `pil300KW`/`pil900KW` (WAXS) + `pil2M` (SAXS); `xbpm2.sumX` normalization.
4. **Pattern: LEGACY.** Heavy hard-coded sample arrays + per-energy `bp.count`; `meshgrid` y-walk; `for i in range(2000): ... time.sleep(20)` infinite kinetics loops:
   ```python
   for wa in waxs_arc:
       for e, xsss, ysss in zip(energies, xss, yss):
           yield from bps.mv(energy, e); ... yield from bp.count(dets, num=1)
   ```
5. **Notable:** extensive commented "exposure 1–6" beamtime history in `phong_waxs_Sedge_multi_2022_3`; `new_folder()` wraps `proposal_id`; MFS tensile stage on `stage.x/y`; strain only in filename.
6. **Intent:** S-edge resonant WAXS/NEXAFS of doped polymers, incl. tensile-strained operando, on multi-sample SiNx/washer bars.

---

## 5. 30-user-PPGwang.py
1. ~422 lines; 8 plan functions.
2. **User/group:** PPG / "CW" (Chenhui Wang); SAF 311180.
3. **Use-cases:** **Transmission SAXS of capillaries/films** (multi-sample bars, x/y/z lists); **temperature ramping** (Lakeshore `ls.output1`) of capillaries; **humidity-free low-divergence in-vacuum SAXS** (8.3 m, 6.51 keV); in-situ **evaporation-film WAXS time loop**; Linkam-slide creep (`stage.y` micro-step time series).
3b. **Detectors:** `pil2M` (SAXS) primarily; `pil300KW`/`pil900KW` for WAXS-arc films; no xbpm.
4. **Pattern: LEGACY.** Sample-bar `for ... zip(x_list,y_list,z_list)` + `bp.count`; T loop reads `ls.input_A.value` into name:
   ```python
   for x,y,z,sample in zip(x_list,y_list,z_list,samples):
       yield from bps.mv(piezo.x,x); ... sample_id("CW...", sample); yield from bp.count(dets, num=1)
   ```
5. **Notable:** dozens of commented "holder 5–11" coordinate tables (classic legacy notebook); `det_exposure_time` low-div config; later plans adopt `get_scan_md()` for filenames; WAXS moved to 20° to clear SAXS.
6. **Intent:** Capillary/film transmission SAXS (±WAXS, ±T) of PPG polymer series in low-div vacuum.

---

## 6. 30-user-Aiello.py
1. ~273 lines; 6 plan functions.
2. **User/group:** NIST (Aiello); operators "AA", "JS". 3D-printing/additive references in names (PET, PP, nozzle temps 180/210/240).
3. **Use-cases:** **Microfocus raster mapping** of (likely additively-manufactured) PET/PP — **line scans** (`rel_scan`), **grid maps** (`rel_grid_scan`), **spiral maps** (`rel_spiral`); in-line **transmission measurement** with attenuator insert + direct-beam ratio for per-sample transmission factor.
3b. **Detectors:** `pil2M`+`pil900KW` (SAXS gated by WAXS arc); `OAV_writing` appended for video; `pil2M_stats1_total` read from `db[-1].table()` for transmission.
4. **Pattern: LEGACY (multi-dim scans).** Uses real Bluesky scan plans but one run per sample inside hand loops; in-loop `db[-1]` reads:
   ```python
   yield from bp.count([pil2M]); stats1_direct = db[-1].table(...)['pil2M_stats1_total'].values[0]
   ...
   yield from bp.rel_grid_scan(dets, piezo.x, *rx, piezo.y, *ry)   # / rel_spiral / rel_scan
   ```
5. **Notable:** Sn 60 µm attenuator move-in/out helpers polling `att1_6/7.status`; transmission computed live (`stats1_sample/stats1_direct`); `get_scan_md()`; beamstop rod positioning (`pil2M_bs_rod.x`).
6. **Intent:** Microbeam SAXS/WAXS mapping (line/grid/spiral) with on-the-fly transmission of NIST polymer/3D-printed coupons.

---

## 7. 30-user-Modestino.py
1. ~397 lines; 7 plan functions.
2. **User/group:** Modestino (GU-313379, 2023_3); operator "MM"; SAF 312127.
3. **Use-cases:** **Transmission SAXS/WAXS** on sample bars; **in-situ solvent/flow kinetics with syringe pump** (`syringe_pu.x3` infuse); time-series/burst with static pre/post frames; **raster** in-situ scan (mod/floor x-y stepping); electrochemistry-adjacent flow cells.
3b. **Detectors:** `pil2M` (SAXS) + `pil900KW` (WAXS); no xbpm/diode.
4. **Pattern: LEGACY (time-series).** Long `for nn in range(Nmax)` with sleeps + per-frame `bp.count`; time/position folded into filename:
   ```python
   for nn in range(Nmax):
       if nn==0 and syringe: yield from bps.mv(syringe_pu.x3, 1)   # trigger flow
       ... sample_id("Insitu", f"{sample}_n{nn}_t{...}s..."); yield from bp.count(dets, num=1)
       yield from bps.sleep(time_sleep_sec)
   ```
5. **Notable:** **syringe-pump** triggering inside plan; burst-mode "warm-up" dummy counts ("helps data saving in burst mode"); explicit hutch/abort runbook in header; `t0=time.time()` wall-clock kinetics.
6. **Intent:** In-situ flow/solvent-driven transmission SAXS kinetics (syringe-pump) plus sample-bar surveys.

---

## 8. 30-templates-Patryk.py
1. ~383 lines; ~6 callable defs + large docstring/template library. **Reference/snippet file, not a user plan set.**
2. **User/group:** Patryk Wasik (beamline staff "PW"); template authority for SMI macros.
3. **Use-cases (as templates):** metadata-string construction; sample-name formatting; **NEXAFS energy grids for S K / Cl K / Ag L3 / Ca K / Te L3 / Pt L3 edges**; Lakeshore control (range 1 vs 3, equilibration loop with timeout); WAXS-gated detector selection; name sanitization; worked examples `saxs_S_edge_temperature_Hoang_2022_2` (T×energy×WAXS GIWAXS) and `song_waxs_hard_2022_2` (MFS tensile).
3b. **Detectors (in examples):** `pil2M`+`pil900KW`; `xbpm3.sumX`.
4. **Pattern: LEGACY templates (snippets are the canonical legacy idiom).** Example bodies still `bp.count` per point; provides `startT/stopT/turn_off_heating` Linkam-style helpers. **Reusable but NOT modern** — this is the template that propagated the legacy pattern across users.
5. **Notable:** authoritative **tender-edge energy tables** (with absorption-edge references); equilibration loop with `time.time()` escape; "calculate WAXS beamstop" pointers to `36-Guillaume-beam.py` / `21-pilatus.py`.
6. **Intent:** Beamline staff cookbook of metadata/naming/temperature/NEXAFS snippets reused when writing per-user macros. **Flag: template-like / high reuse.**

---

## 9. 30-user-Ocko.py
1. ~198 lines; ~12 functions (incl. alignment library).
2. **User/group:** Ocko ("BO"); references Cai/Chopra/Clark alignment lineage. ~13.47 keV and tender (~5 keV) energies.
3. **Use-cases:** **GISAXS/GIWAXS with WAXS-arc `bp.scan`** at several incident-angle offsets; **resonant/energy-dependent** GI (commented `ener` Br/K-edge-region energies ~5008–5023 eV); extensive **GISAXS alignment routine library** (`alignCai`, height/th centroid scans, `modeAlignment`/`modeMeasurement`); solvent-vapor-annealing-style sample series (THF/DCM in names).
3b. **Detectors:** `pil300KW`/`pil2M`; `xbpm3.sumY`; ROI on `pil2M.roi1` for alignment.
4. **Pattern: LEGACY/MIXED.** Mixes `bp.scan(dets, waxs, *waxs_arc)` (a true arc scan = good) with per-angle outer loops and global `sample_id`:
   ```python
   for j, ang in enumerate(a_off + np.array(angle_offset)):
       yield from bps.mv(piezo.th, ang); sample_id("BO...", name); yield from bp.scan(dets, waxs, *waxs_arc)
   ```
5. **Notable:** rich peak-finding GI alignment (`ps()` centroid/derivative, ROI `min_y` walk for arc geometry); custom `GV7 = TwoButtonShutter(...)` device defined in-file; beamstop-rod align/measure modes; foil insert via `SMIBeam().insertFoils`.
6. **Intent:** Aligned GISAXS/GIWAXS (some near-edge) of solvent-treated films, with a substantial reusable Cai-style GI alignment toolkit.

---

## 10. 30-user-Braunschweig.py
1. ~170 lines; 2 plan functions.
2. **User/group:** Braunschweig (GU-306008, 2020C1); operators "AB", "AB2".
3. **Use-cases:** **Multi-sample-bar GIWAXS** with per-sample auto-alignment; incident-angle series × WAXS-arc series; organic semiconductor (MeDPP) solvent-vapor-annealing (VSADCM/PEDOTPSS) study.
3b. **Detectors:** `pil300KW` (WAXS); commented `rayonix` (MAXS) option; no SAXS in active path.
4. **Pattern: LEGACY.** Canonical sample-bar GIWAXS:
   ```python
   for x, sample in zip(x_list, sample_list):
       yield from bps.mv(piezo.x, x); yield from alignement_gisaxs(0.1)
       for waxs_angle in waxs_angle_array:
           for i, th in enumerate(th_meas): ... yield from bp.count(dets, num=1)
   ```
5. **Notable:** WAXS move retry/except guard; x-shift-per-shot dose mitigation; `alignement_gisaxs` per sample; angle/q comment cheatsheet.
6. **Intent:** Aligned multi-sample GIWAXS incident-angle/arc survey of solvent-annealed small-molecule films.

---

## 11. 30-user-Fernandez.py
1. ~160 lines; 1 plan function.
2. **User/group:** Fernandez ("LF").
3. **Use-cases:** **GIWAXS multi-sample bar with two-row hexapod offset geometry** (top/bottom rows via `stage.x` hexa + `piezo` stack); fine **incident-angle scan** (15 angles) per sample; per-sample pre-aligned incident angles & y baked into arrays.
3b. **Detectors:** `pil300KW`+`pil2M`; sdd 5 m, 12 keV (hard GIWAXS).
4. **Pattern: LEGACY.** Alignment loop commented out; uses stored `incident_angles`/`y_piezo_aligned` arrays:
   ```python
   for wa in waxs_arc[::-1]:
       for name, xs, zs, aiss, ys, xs_hexa in zip(...):
           yield from bps.mv(piezo.th, aiss); ...
           for num, an in enumerate(angle): yield from bps.mv(piezo.th, aiss+an); yield from bp.count(dets, num=1)
   ```
5. **Notable:** **hexapod `stage.x` per-sample offset** combined with piezo GI stack (two-deck sample bar); persisted alignment results as literal lists; multisample alignment helpers (`alignement_gisaxs_multisample[_special]`).
6. **Intent:** Hard-X-ray GIWAXS incident-angle mapping over a two-row pre-aligned sample bar.

---

## 12. 30-user-Kim2.py
1. ~126 lines; 1 plan function.
2. **User/group:** Kim (GU-304841); operator "Kim".
3. **Use-cases:** **GIWAXS multi-sample bar** of HfZrO/HZO ALD ferroelectric films; per-sample alignment; incident-angle array × **WAXS-arc array** × few x-positions (dose spread); q-range planning comments.
3b. **Detectors:** `pil300KW`+`pil2M`; commented `rayonix` (MAXS) option.
4. **Pattern: LEGACY (deeply nested).** 4-level loop → one run per (sample×wa×x×th):
   ```python
   for x,sample in zip(x_list,sample_list):
       yield from alignement_gisaxs(0.1)
       for waxs_angle in waxs_angle_array:
           for x_meas in x_pos_array:
               for i,th in enumerate(th_meas): ... yield from bp.count(dets, num=1)
   ```
5. **Notable:** SmarAct Y staging note in runbook; q-vs-arc-angle conversion comments; `assert len()==len()` list guards.
6. **Intent:** Multi-sample GIWAXS arc/incident-angle survey of ALD HfO2/ZrO2 ferroelectric thin films.

---

## 13. 30-user-Quan.py
1. ~95 lines; 1 plan function (+ runbook header).
2. **User/group:** Marino/Murray (UPenn; "YQ"); proposal 315975_Gonzalez/309930_Murray. Derived from Chopra/Clark.
3. **Use-cases:** **Transmission SAXS/WAXS of nanocrystal/colloid samples** (PbS QD superlattices) with **pin-diode transmission readout**; attenuator-combination tuning for diode; single-shot per sample; ex-situ + in-situ (`insitu_EM` referenced in header) evaporation/assembly.
3b. **Detectors:** `pil2M` (SAXS) + `pil900KW`/`pil300KW` (WAXS); **`pdcurrent1`/`pdcurrent2`** pin-diode; `xbpm3.sumX`.
4. **Pattern: LEGACY.** Single `bp.count`, diode read via `.value`/`.get()` into filename:
   ```python
   fs.open(); pd_curr = pdcurrent1.value; fs.close()
   sample_id("YQ", f"{name}_..._pd{pd_curr}...")
   yield from bp.count(dets, num=1)
   ```
5. **Notable:** attenuator open/close sequencing for diode dynamic range (`att1_9/10`, "diode saturates at 125k"); fast-shutter (`fs`) gated transmission read; piezo position folded into name.
6. **Intent:** Transmission SAXS/WAXS with pin-diode transmission of PbS nanocrystal films (ex/in-situ assembly).

---

## BATCH SYNTHESIS

- **Archetype A — Tender-edge resonant / NEXAFS GIWAXS+SAXS (TReXS):** Gregory, Reynolds, Meli, and the Patryk energy tables. Hallmarks: hard-coded per-element `energies` grids (S K / Cl K / Ca K / Ag L3 / Te L3 / Pt L3), `for e in energies: mv(energy,e); count`, `piezo.y`/`x` dose-walk, `xbpm`/`amptek` normalization, fwd+reverse energy passes. Meli adds operando **electrochemistry** + fluorescence (`amptek`).

- **Archetype B — Multi-sample-bar GISAXS/GIWAXS with per-sample alignment:** Braunschweig, Kim2, Fernandez, Ocko, PPGwang, plus Harvard's GI plans. Hallmarks: parallel `sample_list`/`x_list`/`y_list`(/`z`,/`hexa`) arrays, `alignement_gisaxs*` per sample, nested incident-angle × `waxs.arc` loops. Fernandez/Meli add **hexapod two-deck** geometry; Ocko ships a reusable **Cai-style GI alignment library**.

- **Archetype C — Temperature-resolved annealing SWAXS:** Harvard (dominant), PPGwang, Patryk example. Two thermal back-ends coexist: **Lakeshore (`ls.output1`/`input_A`)** and **Linkam (`LThermal`)**, with copy-pasted equilibration-with-timeout loops; T almost always read into the filename (legacy), occasionally appended as a device in 2026 Harvard plans.

- **Archetype D — Microfocus raster mapping:** Aiello (line/grid/**spiral** via `rel_scan`/`rel_grid_scan`/`rel_spiral`, + live transmission and `OAV_writing`) and Harvard (mesh/grid/linescan pucks). These use real multi-dim Bluesky scan plans but still one run per sample.

- **Archetype E — In-situ time-series / kinetics:** Modestino (**syringe-pump flow**), Harvard (burst/loop "single_measurement", **tensile/pull**), Reynolds/Quan (`for i in range(2000)` + `sleep`). Wall-clock `t0=time.time()` and frame index folded into filename; burst-mode dummy "warm-up" counts recur.

- **Archetype F — Transmission SAXS/WAXS with diode:** Quan (PbS nanocrystals, pin-diode + attenuator tuning) and Modestino/PPGwang (capillary/film bars). Fast-shutter-gated `pdcurrent.value` → filename.

- **Legacy-vs-modern prevalence:** **LEGACY ≈ 12.5/13.** Zero use of `run_decorator`/`stage_decorator`/`trigger_and_read`/`bpp`/`md={}`. Universal anti-patterns: global `sample_id(...)` filename state, `.value`/`.get()`/`db[-1].table()` reads into strings, hard-coded coordinate lists, nested loops = one run per point. Only **Harvard 2026_1** is MIXED/transitional (structured `inner_*` sub-generators, Ctrl-C-safe `finalize_wrapper` noted, temperature recorded via `dets + [ls.input_A]`).

- **Reusable / template-like code to flag:**
  - **`30-templates-Patryk.py`** — the canonical SMI snippet library (metadata, naming, NEXAFS energy tables, Lakeshore control). It is the **source of the propagated legacy idiom**; modernizing it would cascade. High reuse, NOT modern.
  - **Harvard `temp_series_grid`** (commented out, ~L6063) — the only example recording the **filename as an ophyd `Signal`** (`s.put(name); count(dets+[s])`); closest seed for the target modern pattern.
  - **Harvard 2026_1 `inner_*` orchestration** (`linkam_sweep_reena_2026_1`, `linkam_transmission_temp_mustafa_2026_1`) — best structural template for migration (sub-generators + device-recorded temperature).
  - **Ocko `alignCai` / `align_gisaxs_*` / `alignmentmodeCai`** — reusable GI alignment toolkit (peak-finding, ROI arc geometry).
  - **Aiello** attenuator-helpers + live-transmission and **`rel_spiral`/`rel_grid_scan`** usage — reusable microfocus mapping reference.

- **Cross-cutting hardware vocabulary:** in-vacuum `waxs.arc` consistently treated as the slow/outer axis (and SAXS `pil2M` gated off when arc <10–15°); SmarAct GI `piezo.x/y/z/th` stack; hexapod `stage.*` for coarse/transmission tilt; `energy` DCM spanning tender (~2.4–5 keV S/Cl/Ag/Ca/Te) to hard (≥11.5 keV Pt); flux via `xbpm2/3` and `pdcurrent`/`amptek`; `syringe_pu`, Linkam/Lakeshore, MFS tensile, `OAV_writing` for in-situ.

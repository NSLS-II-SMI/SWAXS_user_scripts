# Legacy Plan Analysis - Batch 01 (SMI / SWAXS)

Beamline: NSLS-II SMI (12-ID), SWAXS. Scope: classify scientific use-cases and
data-acquisition patterns. This is a classification pass only; no fixes proposed.

---

## File: `legacy/30-user-Richter.py`

**1. Size / plan count**
- ~482 KB, 10,415 lines.
- 138 `def` blocks (135 top-level plan functions + 3 nested `inner()` generators).
- Counted pattern markers: `bp.count(...)` x141; `bp.scan/rel_scan` x0;
  `run_decorator`/`stage_decorator` x80 (40 modern envelopes); `trigger_and_read` x75;
  `sample_id(...)` x142.

**2. User / group**
- User: **Lukas Richter (initials "LR")** - `sample_id(user_name="LR", ...)`.
  Filename `30-user-Richter`.
- Collaborators visible in plan names / `project_set()`: Lee, Guillaume, Amalie,
  Freychet (`project_set('314483_Freychet_NN')`). Samples are conjugated/doped
  semiconducting polymers (P3HT, PBTTT/PBTTTC14, pgBTTT, P3MEEMT, PB2T-TEG, BBL,
  MM389/MM460/MM461 series) and 2D materials (MoS2), often FeCl3-/KClO4-doped.

**3. High-level use-cases present**
- **Tender-energy resonant GIWAXS / NEXAFS across multiple absorption edges** (dominant).
  Edge inventory (occurrence count): Cl-K x78, S-K x39, K-K x24, P-K x5, Ca-K x3,
  In-L x2, Fe-K x1, plus ClO4/KCl/KClO4 variants. Energy lists ~2140 eV (P) to
  ~3820 eV (In). Resonant/anomalous scattering by fine energy stepping over the edge.
- **GISAXS / GIWAXS (grazing incidence)** - the backbone. Every measurement plan runs
  `alignement_gisaxs*` then loops incident angle `ai_list` (e.g. 0.8/1.6/3.2 deg) on
  `piezo.th` or `stage.th`. Both reflection geometries (piezo double-stack and hexapod).
- **NEXAFS energy scans** - dedicated `scan_nexafs_Moedge/Caedge/Pedge`,
  `nexafs_Inedge_2026_1`: fine `np.linspace` energy sweep at fixed angle, WAXS only.
- **Transmission SAXS/WAXS** - `*_transmission` plans (S-edge, Cl-edge): no grazing
  alignment, three detectors, energy sweep through the edge in transmission.
- **Multi-sample bar measurement** - every plan iterates a hard-coded `names[]` list
  against `x_piezo[]`/`x_hexa[]` coordinate arrays (8-13 samples per bar), guarded by
  `assert len(...) == len(names)`.
- **Sample-alignment routines (grazing)** - `alignement_gisaxs`,
  `alignement_gisaxs_doblestack` (piezo dual-stack, most common),
  `alignement_gisaxs_hex` / `_hex_roughsample` (hexapod), `alignement_special`.
  (Defined in beamline profile, not in this file.)
- **Solvent Vapor Annealing (SVA) / controlled humidity / RH in-situ** - `*_sva*`,
  `SVA_night_*`: `setDryFlow()`/`setWetFlow()` dry+wet N2 mixing,
  `readHumidity()` read back into the filename, `bps.sleep(40*60)` equilibration
  between RH steps (humidity-resolved kinetics / time series).
- **Electrochemistry / in-situ doping** - sample names encode applied gate bias
  (`pgBTTT_KClO4_n300mV ... p600mV`) and chemical doping ladders
  (`Doped-FeCl3-0p02 ... 1p0`); KClO4 electrolyte, dedoped/doped/pristine states.
- **Solvent / flow / liquid cell** - `run_waxs_waitwater_*`,
  `Cl_edge_measurments_liquid_cell`, `KClO4_..._flowing_300ssleep`, AuNPs in flow.
- **Beam-diagnostic / flat-field / intensity calibration** - `bpmvspindiode_*edge`,
  `flatfield_S_scan`, `flatfield_Cl_scan`: sweep energy with `fs.open()/fs.close()`
  fast shutter, log `xbpm2`/`xbpm3` sums and `pdcurrent2` photodiode vs energy
  (I0 normalization / monochromator-glitch mapping across the edge).
- **Night-batch orchestrators** - `night_<date>`, `SVA_night_*`: thin wrappers that
  `project_set(...)` then chain several edge-measurement plans unattended overnight.
- **XRR (reflectivity)** - incidentally invoked: `night_2021_12_15` calls
  `xrr_spol_waxs()` (s-pol reflectivity; helper defined elsewhere).
- Incident-angle / x-position survey utilities - `x_scan`, `ai_scan`, `*_xscan_*`,
  `*_incidentangle` (alignment-check / angle-series scans).
- NOT observed: XPCS, CD-SAXS / rocking, microfocus raster mapping, 3D-printing in-situ,
  Linkam/heater temperature ramping (sample T appears only as a label like "170C",
  i.e. pre-annealed ex-situ, not ramped in-plan), Rayonix/MAXS.

**3b. Detectors used**
- `pil900KW` (WAXS, x199) - primary, used in almost every recent plan.
- `pil2M` (SAXS, x132) - SAXS; frequently dropped when WAXS arc is in the SAXS path
  (`dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]`).
- `pil300KW` (WAXS, x25) - added in transmission/3-detector plans.
- Diagnostics / context read into stream: `xbpm2`, `xbpm3` (beam-position monitors,
  `.sumX`), `pdcurrent2` (pin/photodiode), `att2_9` (attenuator), `energy`, `waxs` (arc).
- No `rayonix`/MAXS in this file.

**4. Acquisition pattern: MIXED (chronological migration legacy -> modern envelope)**
- Early era (2021-2024, lines ~1-6390): pure **LEGACY** - deeply nested `for` loops
  (sample -> waxs_arc -> incident angle -> energy) where each innermost energy point
  fires `yield from bp.count(dets, num=1)` (a separate Bluesky run per point) and the
  file is labeled via global mutable `sample_id(user_name="LR", sample_name=...)`.
  Context (xbpm/photodiode/energy) is read with `.value`/`.get()` and formatted into
  the filename string, not recorded as a stream.

  Representative LEGACY snippet (`P_edge_measurments`, lines ~106-120):
  ```python
  for e, xbpm3_ys in zip(energies, xbpm3_y):
      yield from bps.mv(energy, e)
      bpm = xbpm2.sumX.value
      sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, ...)
      sample_id(user_name="LR", sample_name=sample_name)   # global mutable label
      yield from bp.count(dets, num=1)                      # one run PER energy point
  ```

- Later era (2025-2026, from line ~6470 onward): **MODERN ENVELOPE around LEGACY
  interior**. A per-sample `@bpp.stage_decorator(dets)` + `@bpp.run_decorator(md=...)`
  + `def inner()` + `bps.trigger_and_read(...)` now wraps one logical sample in a single
  run, with `energy/waxs/xbpm2/xbpm3/att2_9` recorded as a stream. BUT the interior is
  still legacy: hard-coded `names[]`/coordinate arrays, `xbpm2.sumX.get()` formatted into
  a string, and the target filename smuggled in via a throwaway
  `s = Signal(name='target_file_name'); s.put(sample_name)`. The `md` value is the
  literal unsubstituted string `'{target_file_name}'` (placeholder never formatted).

  Representative MODERN-envelope snippet (`scan_nexafs_Moedge`, lines ~6692-6717):
  ```python
  @bpp.stage_decorator(dets)
  @bpp.run_decorator(md={'sample_name': '{target_file_name}'})   # literal placeholder
  def inner():
      for e in energies:
          yield from bps.mv(energy, e)
          s.put(sample_name)                                     # filename via Signal
          yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
  (yield from inner())
  ```

- The two patterns COEXIST: `bp.count` spans lines 120-9819, `trigger_and_read` starts at
  6500. As late as 2026 the diagnostic plans (`bpmvspindiode_*`,
  `S_edge_measurments_2026_March01`) still use legacy `bp.count`, while the science plans
  have moved to the modern run envelope. Net: **MIXED**, trending modern, legacy still
  present in diagnostics and the entire pre-2025 corpus. Even modern plans keep legacy
  bar-coordinate lists, string-filename labeling, and global `project_set()` md.

**5. Notable techniques / hardware**
- Two grazing-incidence sample stacks: **piezo** (`piezo.x/y/z/th`, the "doblestack")
  and **hexapod** (`stage.x/y/z/th/phi`); plans pick `alignement_gisaxs_doblestack`
  vs `alignement_gisaxs_hex`/`_hex_roughsample` accordingly.
- `waxs`/`waxs.arc` WAXS detector arc moved as outer loop; SAXS detector dropped when the
  arc blocks the SAXS path - the one place sound "slow axis outermost" practice appears.
- Tender-energy mono: `energy` (DCM) moved over edge with `bps.sleep(2)` settle and a
  beam-loss recovery hack (`if xbpm2.sumX.get() < 50: re-move energy`) to survive
  flux dropouts / mono glitches at the edge.
- `att2_9` attenuator opened/closed in-plan (`att2_9.open_cmd`) and recorded.
- `fs.open()/fs.close()` fast shutter gating in the BPM-vs-photodiode I0 calibrations.
- Controlled-humidity SVA rig: `setDryFlow()`/`setWetFlow()` mass-flow control +
  `readHumidity()`; long `bps.sleep(40*60)` equilibrations -> RH-resolved kinetics.
- Heavy use of global mutable state imported from the beamline profile
  (`sample_id`, `project_set`, `det_exposure_time`, `setDry/WetFlow`, `readHumidity`);
  alignment helpers also profile-level, not in this file.
- Anti-pattern flourishes: module-level `global names, x_hexa, ...`; alignment results
  hand-cached as literal lists (`y_hexa_aligned=[...]`, `incident_angles=[...]`) and even
  threaded between plans via `return aiss, yss` to skip re-alignment.

**6. One-line summary**
- A multi-year personal "run book" of tender-energy resonant GIWAXS/NEXAFS edge scans
  (Cl/S/K/P/Ca/In) on doped semiconducting-polymer & MoS2 sample bars, with SVA/humidity,
  electrochemical-bias and flow-cell variants plus BPM/photodiode I0 calibrations -
  migrating from per-point `bp.count`+`sample_id` to a per-sample `run_decorator`
  + `trigger_and_read` envelope that still carries legacy hard-coded lists and
  string-filename labeling.

---

## BATCH SYNTHESIS

- **Distinct use-case archetypes seen:** (1) tender-energy resonant GIWAXS / NEXAFS edge
  scans (Cl/S/K/P/Ca/In/Fe-K & L edges, ~2.1-3.8 keV) - the overwhelming majority;
  (2) grazing-incidence sample alignment (piezo double-stack vs hexapod);
  (3) multi-sample "bar" surveys driven by hard-coded name/coordinate arrays;
  (4) SVA / controlled-humidity (RH) in-situ with dry/wet N2 mixing and long
  equilibration time series; (5) in-situ electrochemistry / chemical doping ladders
  (gate-bias mV, FeCl3, KClO4); (6) solvent / flow / liquid-cell; (7) transmission
  SAXS/WAXS edge scans; (8) BPM-vs-photodiode flat-field / I0 calibration across the edge;
  (9) overnight batch orchestrators chaining many plans via `project_set`;
  (10) incidental XRR (s-pol) helper call.
- **Geometry split:** predominantly **grazing incidence (GISAXS/GIWAXS)** with explicit
  incident-angle loops; a smaller **transmission** subset. No microfocus raster, XPCS,
  CD-SAXS/rocking, or in-situ printing/heating present.
- **Detector convention:** pil900KW = WAXS (primary), pil2M = SAXS, pil300KW = added WAXS
  in transmission; xbpm2/xbpm3 and pdcurrent2 used for I0/diagnostics. No Rayonix/MAXS.
- **Legacy is the majority by line count and by plan count.** ~140 per-point
  `bp.count` calls and ~142 global `sample_id()` labels dominate the 2021-2024 corpus;
  zero `bp.scan/rel_scan` (everything is `mv` + `count`).
- **A genuine modern transition exists from ~2025 onward** (~40 `run_decorator`/`inner()`
  envelopes, ~75 `trigger_and_read`), but it is a *thin* modernization: the run envelope
  is correct (one run per sample, context recorded as a stream) while the interior keeps
  legacy bar-coordinate lists, `.get()`-into-string filenames, and a throwaway
  `target_file_name` Signal carrying the label.
- **Cross-cutting legacy smells:** module-level `global` state, hand-cached alignment
  result lists smuggled between plans, filename strings as the primary metadata channel,
  unsubstituted `md={'sample_name':'{target_file_name}'}` placeholder, and reliance on
  profile-level mutable helpers (`sample_id`, `project_set`, `setDry/WetFlow`).
- **Migration priority signal:** converting the recurring nested
  sample->arc->angle->energy loop into a single staged run with
  `trigger_and_read(dets + [energy, waxs, xbpm*, att*, ai/T/humidity signals])` and md
  passed per-sample would modernize the bulk of this file in one templated pattern, since
  ~all 135 plans are structural clones of that loop.

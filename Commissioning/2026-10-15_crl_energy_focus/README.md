# CRL energy-focus commissioning — 15 October 2026

## Combined measurement report — 16 October

Next experiment: [attenuator microfocus comparison](ATTENUATOR_MICROFOCUS_TEST.md),
with reference-bracketed filter exchanges, matched-thickness controls and
energy-specific qualification criteria.

**[Illustrated eight-page PDF](CRL_measurement_report_2026-10-16.pdf)** — focus curves,
all-energy edge heatmaps, selected raw counts and derivatives, and geometry interpretation.
Rebuild offline with `python make_measurement_pdf.py` from this folder
(requires NumPy, pandas and Matplotlib; available in the workstation Python).

See [the measurement report](MEASUREMENT_REPORT.md) and
[interactive raw-edge/focus plots](measurement_report.html) for scans 1170759,
1170763, 1170765 and 1170769, with partial attempts and geometry comparisons.
The report uses actual recorded settings and coverage; the proposed-acquisition
notes below describe intent and should not substitute for the measurement record.

## Scan 1170759 analysis

Open [the interactive Bokeh report](scan_1170759_crl_focus.html).
The scan completed all 441 frames. Holder 3 was inserted at −0.22 mm, CRL Z was
+200 mm, SSA horizontal gap was 0.030 mm, and vertical gap was about 0.050 mm.
The minimum sampled derivative FWHM was **5.39 µm at 16.20 keV**, versus a model
focus energy of **16.426 keV** at Z=+200 mm. With 50 eV energy spacing and 2 µm
knife-edge steps, this is a sampled minimum, not a precision focus calibration.

Widths from 16.85 through 17.00 keV are omitted because the edge window does not
provide reliable half-height coverage. In particular, automatically choosing
derivative polarity on these broad clipped profiles can report a false narrow
width; this report explicitly analyzes the positive derivative of rising edges.
Intensity is the final-three-point mean divided by 0.5 s. Fixed Sn attenuation
changes with energy; harmonic 13 changes to 15 at 16.15 keV. The intensity curve
therefore includes source/attenuation effects as well as lens transmission.

## Proposed acquisition

Per-holder alignment is pre-filled in **`HOLDER_ALIGNMENT` at the top of
`crl_focus_series.py`** from the four beam-position snapshots. Each holder needs its
own `crl.x` and `crl.y` (the focused beam is steered onto the fixed knife edge), not
just a lens insertion. **All holders run at `crl.z = 0`** — the goal is the real focus
at z=0. The plan validates every needed position (lens IN, crl.x, crl.y) before motion,
for subset runs too. Lenses withdraw to the CRL device's nominal OUT positions
(+10 mm for holders 1–6, −10 mm for 7–12), which stay inside the soft limits.

| Holder | Elements (R50 µm Be) | lens IN (mm) | crl.x (mm) | crl.y (mm) | Model focus @ z=0 (keV) | Scan (keV) |
|---|---|---:|---:|---:|---:|---:|
| 5 | 2  | −0.6993 | −12.667 | −9.82   | 6.150  | 6.000–6.650 |
| 4 | 4  | −0.8099 | −9.447  | −9.77   | 8.698  | 8.000–9.400 |
| 2 | 8  | −1.1801 | −8.5766 | −9.75   | 12.300 | 11.300–13.300 |
| 3 | 16 | −0.22   | −8.5764 | −9.9878 | 17.395 | 16.000–18.800 |

The default is these four individual-holder windows in ascending-energy order
**5 → 4 → 2 → 3** (one holder per run — the per-holder x/y alignment requires it).
crl.x/crl.y come from the snapshots; crl.x in particular is only a starting guess
(holder 3's x/y were snapshotted at z=+200), so the coarse scan below actually locates
the edge. Holder 3's crl.y (vertical) at z=0 is a carried-over guess the horizontal
knife-edge scan does not refine — treat its vertical focus as approximate.

Source: profile collection `docs/CRL_MICROFOCUSING.md` / `docs/crl_report`, and
public `CRLModel` calculations. The current report uses sample distance 1600 mm
at Z=0, SSA distance 10.5 m, and Z travel −300 to +300 mm. The older
`crl_report_1350mm` geometry is not used. Focus windows are ±8% of each calculated
center (rounded outward to 50 eV), clipped to 6–24 keV. These are experimental
search windows, not the report's energy bands for switching holders while
continuously changing Z. `ENERGY_RANGES_EV` allows manual range overrides.

Each run:

- Withdraws all holders, moves the CRL body to **z = 0 mm**, moves **crl.x / crl.y** to
  the holder's values, inserts the one selected holder, and waits 2 s. z, x, y and the
  holder stay fixed throughout the run.
- **Coarse edge scan first:** one knife-edge (piezo.x) scan **±400 µm** around
  `EDGE_CENTER_UM` (**81 points, 10 µm steps**) at the holder's model-focus energy,
  using `pil2M.stats1.total`. The edge center is located from the peak of
  |d(total)/dx| and reused for the fine scan. If the edge sits at the search boundary
  the plan raises — widen `COARSE_HALF_RANGE_UM`.
- **Fine scan:** **21 energies × 61 piezo-x positions**, 0.5 s exposure, over a
  **±60 µm** window centered on the found edge (120 µm wide, 2 µm steps). The found and
  nominal edge centers are recorded in run metadata (`coarse_edge_center_um`).
- Locks one validated undulator harmonic across the energy interval, using the
  public profile harmonic wrapper. The preview validates the interval against
  the current calibration; adjust a window if no harmonic spans it.
- Uses ordinary waited energy-plan moves, which the beamline RE's installed
  managed-energy-move preprocessor handles for long approaches and feedback.
- **Attenuation: one fixed foil per holder, inserted once and left for the whole
  sweep** (coarse + fine). Changing foils between energies can disturb the focused
  beam, so a single foil is chosen that gives **≥ `ATTENUATION_MIN_FACTOR` (default
  1500×)** across the window — sized at the *brightest* (highest) energy, since a
  fixed foil attenuates least there. At lower energies the same foil attenuates more;
  that varying factor is **read and recorded at every point, not corrected**. 1500×
  is calibrated from scan 1170759 (538× → ~38M counts): bright-end counts stay
  ≤ ~7M (safe headroom) and every window's dim end stays measurable (≥ ~900 counts).
  A single fixed foil swings 100–1000× across a window, so a much higher target (e.g.
  1e5×) would over-attenuate the dim ends to ~0 counts. `FOIL_OVERRIDE={holder: "1_9"}`
  forces a specific foil. The chosen foil per holder is printed by `preview_crl_series()`.
- Sets Pilatus sensitivity once per holder to its **theoretical central energy**
  (6.150, 8.698, 12.300, or 17.395 keV), with threshold=central energy/2 and gain
  from the profile's energy policy (gain 2 below 7 keV, 1 below 20 keV, 0 above).
  These settings stay fixed throughout that holder's energy sweep. Waits for
  readback confirmation before acquisition; records the central-energy policy
  in run metadata and the sensitivity readbacks in primary.

CRL angles, SSA gaps, sample Y/Z, and detector geometry are kept (crl.x/crl.y are now
set per holder). The beamline should already be in the intended knife-edge
configuration. Exposure settings, attenuation selection policy, and harmonic lock are
restored on completion/error/RE abort. Energy, physical foils, detector threshold, lens
positions, crl.x/crl.y, and piezo x remain at the last reached settings.

Total: **5,448 frames** (per holder: 81 coarse + 21×61 fine = 1,362; ×4),
45.4 minutes exposure-only, roughly **two hours** at scan 1170759's observed cadence,
plus lens/x/y and long-energy moves, one extra energy settle per coarse scan, and row setup.

## Live focus report (optional)

Pass `report_path` to get a **single self-refreshing HTML page** that is rewritten as
each energy sweep finishes — derivative-FWHM vs energy overlaid across holders, plus a
best-focus table. Open the file once in a browser; it reloads itself every 15 s, so no
new tab is opened per sweep. It reuses the same width convention as the offline report
(`smi_plans.analysis.analyze_xy`), and a rendering error never interrupts acquisition.
The live callback (`live_focus_report.py`) is imported lazily, only when requested.

```python
# True → writes live_crl_focus.html next to the script; or pass an explicit path.
RE(crl_focus_series(report_path=True))
```

## Review, then run in bsui

```python
%run -i ~/SWAXS_user_scripts/Commissioning/2026-10-15_crl_energy_focus/crl_focus_series.py

preview_crl_series()  # prints settings, harmonics, coarse+fine frame count; no motion
RE(crl_focus_series(report_path=True))

# Or acquire only selected individual holders, with the same settings:
RE(crl_focus_series(holder_sets=[(5,)], report_path=True))
RE(crl_focus_series(holder_sets=[(2,), (3,)]))
```

Loading the script does not launch acquisition. Acquisition has **not** been
executed by the analysis agent; verification uses only in-memory simulated devices.

## Reproduce analysis / offline checks

From `~/smi-plans`:

```bash
pixi run python ../SWAXS_user_scripts/Commissioning/2026-10-15_crl_energy_focus/analyze_1170759.py --cached
PYTHONPATH=$HOME/.ipython/profile_collection/src pixi run pytest -q ../SWAXS_user_scripts/Commissioning/2026-10-15_crl_energy_focus/test_crl_focus_series.py
```

Omit `--cached` to reload the recorded scalar data from Tiled. No detector images
are needed for this analysis.

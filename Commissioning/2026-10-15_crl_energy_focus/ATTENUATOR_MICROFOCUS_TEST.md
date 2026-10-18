# Attenuator microfocus comparison — proposed commissioning experiment

## Question and experimental logic

Does inserting a particular physical attenuator change the focused beam's shape,
position or repeatability, beyond changing its intensity? Can we identify
preferred filters for each microfocus energy/configuration?

Start with an already demonstrated focus, hold the optics fixed, exchange
filters, and bracket every candidate with a reference. Measure the full knife-edge
profile rather than only transmission or an automatic minimum width. This is a
proposed experiment, not an executed acquisition or an existing foil qualification.

The test can demonstrate a reproducible **filter-dependent effect**. At one energy
it does not alone distinguish thickness/phase variations, small-angle scattering,
spectral filtering, thermal effects or feedback-mediated steering. Those mechanisms
have different follow-up controls below.

**Updated geometry from the operator:** the attenuators are approximately 1.5 m
upstream of the CRLs. In the documented SSA–CRL geometry, this places them downstream
of the SSA, in the beam propagating toward the lenses. Foil-induced spatial amplitude,
phase or scattering changes therefore act on the illumination arriving at the CRLs.
The exact separation of the two banks has not been supplied.

## Preferred pilot: combinatorial Sn exchange at 16.20 keV

The operator proposes combinations rather than assuming a set of additional known-good
filters. Start with holder 3 at z=+200 mm and the demonstrated `att1_7` reference.
The most informative combinations initially preserve **material and total nominal
thickness**, not merely similar integrated attenuation.

At 16.20 keV, compare all of the following 240 µm total-Sn configurations:

| Code | Inserted physical filters | Nominal Sn thicknesses | Predicted attenuation |
|---|---|---|---:|
| R | `att1_7` | 240 | 510.08× |
| A | `att1_12` | 240 | 510.23× |
| B | `att1_6` + `att1_11` | 120 + 120 | 510.15× |
| C | `att1_6` + `att1_5` + `att1_10` | 120 + 60 + 60 | 510.12× |
| D | `att1_11` + `att1_5` + `att1_10` | 120 + 60 + 60 | approximately 510× |

Tiny differences in the model arise from separately tabulated base thicknesses and
rounding, not a prediction of a physically significant transmission difference.
Ideally these combinations have the same spectral transmission at every energy,
which is a stronger control than matching only the fundamental attenuation across
different materials. Real thickness, contamination, spacing and scatter can differ.

Use `R–A–R–B–R–C–R–D–R`, with an extra R removal/reinsertion control and repeated
passes in different orders. The acquisition and shape metrics below apply unchanged.
This is now the preferred combinatorial pilot; the 8.77 keV material panel remains
the complementary experiment for expanding to Cu, Mo and Al.

### How the overlapping combinations help

- R versus A tests two physical implementations of 240 µm Sn directly.
- C versus D exchanges the two 120 µm filters on an identical 60+60 µm backing.
- B versus C exchanges `att1_11` (120 µm) for the 60+60 µm pair while retaining
  `att1_6`; B versus D makes the analogous exchange retaining `att1_11`.
- If B is good but C and D are poor, the common 60+60 µm pair, its interaction
  with the backings, or the additional surfaces become suspects. Neither 60 µm
  filter can be individually blamed from that result.

This is an overlapping-substitution experiment, not binary group testing in which
one bad component is guaranteed to spoil every group. FWHM and halo do not combine
linearly. Two distorted illuminations can interact or mask one another. Record
configuration outcomes first; assign individual-filter labels only where direct,
repeated contrasts support them. The five configurations cannot identify arbitrary
individual effects plus all pair interactions.

### Avoiding the weak-filter qualification trap

A good combination does **not** qualify every constituent. Attach a strength-of-test
record to each physical filter at each energy:

```text
tau_i(E) = -ln(T_i(E))
tau_stack = sum(tau_i)
optical-depth share_i = tau_i / tau_stack
```

These quantities describe absorption leverage, not a measured wavefront error or
the fraction of the beam that encounters the filter. In this pilot tau_stack is
approximately 6.23: a 60 µm constituent contributes ~1.56 (25%), a 120 µm
constituent ~3.12 (50%), and a 240 µm filter the full depth. Each tested constituent
therefore makes a substantial absorption contribution at this energy.

For later low-optical-depth candidates, report **no detectable incremental effect
in the tested stack**, not universally good. Select additional demonstrated-focus
energies where that filter has appreciable optical depth and sufficient transmitted
counts. As an experimental planning heuristic, tau_i around 0.5–3 is often useful,
but it is not a physical qualification threshold and stronger filters remain testable
when counting statistics permit. Do not qualify thickness variants that were not
actually measured, and do not assume stacking different thin foils constitutes a
stronger test of any one physical foil.

Low absorption does not guarantee little distortion: phase gradients, roughness,
scattering or clipping can affect a weakly absorbing foil. Optical depth is a useful
coverage coordinate, not a substitute for measured profiles. Preserve both the
direct operating-combination results and the narrower individual-filter evidence.

For broader inventory coverage, choose balanced, overlapping configurations with
similar total optical depth, and ensure each candidate appears against more than
one backing. Use the pilot to select promising backings rather than declare them
good in advance. Match-material substitutions take priority where available;
different-material substitutions retain spectral filtering as a possible cause.
Follow up a failing group with controlled exchanges rather than attempting an
unconstrained fit of all foil effects from a handful of combinations.

## References supported by the existing measurements

| Setup | Reference filter | Evidence | Status before retesting |
|---|---|---|---|
| Holder 4, z=0, 8.77 keV, harmonic 7 | `att2_3`, 80 µm Mo | Scan 1170765: 4.70 µm core, 5.03 µm whole-edge Gaussian width | Best initial reference candidate |
| Holder 3, z=+200 mm, 16.20 keV, harmonic 15 | `att1_7`, 240 µm Sn | Scan 1170759: 5.39 µm core with wings | Demonstrated narrow-core configuration |
| Holder 5, z=0, 6.325 keV | `att1_9`, 30 µm Sn | Scan 1170763: 6.38 µm core on a broad pedestal | Diagnostic condition, not a clean reference |
| Holder 2, z=0, 12.30 keV, harmonic 9 | No qualified reference yet | Scan 1170769 was weak and poorly covered | Establish a reference; do not assume one |

An important existing control: `att1_7` was compatible with a narrow core at
16.2 keV but was present in the problematic 12 keV sweep. That does not exonerate
it at 12 keV, but rules out calling it universally unsuitable from these data.

The operator optimized mirror bending for maximum flux through the 30 × 49.9 µm
SSA. Preserve those settings and the same SSA illumination within each comparison
block. Recover and verify each reference focus at the start; stored positions alone
do not prove the current beam is focused.

## 1. First experiment: prove or disprove the effect at a known focus

### Start at 8.77 keV / holder 4

Reference **R = `att2_3` (80 µm Mo)**. Use harmonic 7 for both coarse and fine
measurements, with fixed detector sensitivity. Keep CRL x/y/z, insertion and angles,
mirror bending, SSA gaps, sample orientation, detector geometry and ROI fixed.
Record all physical inserted filters; disable automatic foil reselection during
the comparison using the existing beamline attenuation-policy controls.

First reproduce the approximately 5 µm reference profile and verify adequate
plateaus. Then run a small, useful replacement-filter panel:

| Filter | Contents | Predicted attenuation at 8.77 keV | Reason to include |
|---|---|---:|---|
| `att2_3` | 80 µm Mo | 15,970× | Reference |
| `att1_3` | 272 µm Cu | 14,020× | Similar attenuation, different material |
| `att1_5` | 60 µm Sn | 4,672× | Candidate; paired physical-filter control |
| `att1_10` | 60 µm Sn, separate position | 4,672× | Same material/thickness as `att1_5` |
| `att2_8` | 816 µm Al | 3,064× | Different material with practical attenuation |

Numbers are rounded outputs of the current `attenuator_data` model, not measured
transmission. Cu lies below its K edge at this test energy: do not transfer this
table across the edge or assume matched attenuation at another energy.

Example screening order:

```text
R → R(reinserted) → Cu → R → Sn-A → R → Al → R → Sn-B → R
```

The reinserted-reference control measures insertion repeatability. Repeat the
candidate set in a different recorded order for at least three independent
candidate insertions before assigning a confirmed ranking. Screening with one
insertion gives provisional results only. For a suspicious filter, use an explicit
R–X–R–X–R sequence to demonstrate reversibility.

At a reference return, do not automatically realign to recover a good curve.
Failure to recover is evidence of drift, hysteresis, or another changed state;
flag that block and investigate it before attributing the change to X alone.

### Per insertion: rate scout, wide edge, fine edge

1. Read back the complete foil state and acquisition settings; allow a consistent
   settling interval. At an established open-edge position, acquire a short rate
   scout and detector image. Check peak-pixel response as well as integrated counts.
2. Choose exposure/repeats to obtain comparable counting precision across filters.
   Keep exposure fixed within each edge scan. Initially aim for the statistics of
   the reference, then refine from actual repeatability, not only a predicted
   attenuation factor. Longer exposure cannot restore photons lost to extreme
   attenuation or fix rate-dependent detector response. Shorter exposure reduces
   integrated counts but does **not** reduce instantaneous photon rate or pile-up.
3. Record a wide profile to establish both plateaus and locate the edge, e.g.
   ±100 µm at 5 µm steps (41 points), widened if necessary. A wide scan must use
   the same foil, harmonic and detector state as its fine scan.
4. Record a fine profile, initially ±20 µm about the measured center in 1 µm steps
   (41 points). Retain absolute motor coordinates and center shift relative to R.
   Recenter the *measurement window* if needed; do not steer or realign the optics.
   A broadened candidate requires a wider sufficiently sampled fine scan, not a
   forced narrow-core fit to a clipped window.
5. Repeat open- and closed-edge measurements before/after the profile. Retain
   images at least for closed, transition and open positions, preferably all
   frames if the normal acquisition already saves them. Assess halo structure,
   clipping and detector linearity alongside scalar totals.

At the previous ~1.3 s/frame cadence, 82 positions per insertion take ~1.8 minutes
before scouts, setting changes or longer exposures. Ten insertions are roughly
18 minutes of scan cadence; budget approximately 25–40 minutes for this pilot,
then revise from measured overhead and count requirements. Three-pass qualification
will take longer. Begin horizontally; repeat vertically for the reference and any
candidate that looks promising or problematic before assigning a 2-D microfocus label.

## 2. Highest-value filter-specific controls

### Same nominal material and thickness, different physical filters

These pairs are particularly valuable because their ideal spectral transmission
should be approximately the same, unlike a Cu–Mo comparison:

| Pair | Total nominal thickness | Suitable starting setup |
|---|---|---|
| `att1_5` vs `att1_10` | 60 µm Sn | 8.77 keV panel |
| `att1_6` vs `att1_11` | 120 µm Sn | 12.3 keV follow-up or suitable fixed backing |
| `att1_7` vs `att1_12` | 240 µm Sn | 16.20 keV / holder 3 reference setup |

At 16.20 keV, `att1_7` and `att1_12` each predict about **510×** attenuation.
Use `att1_7 → att1_12 → att1_7` and repeat. Add `att1_2` (136 µm Cu,
~1535×) as a different-material comparison when counts permit.

If equal-thickness Sn filters give repeatably different normalized profiles under
stable reference returns, that supports a physical-filter/mount-specific effect
over ideal spectral transmission alone. Actual thickness, contamination and beam
footprint can differ, so this is strong evidence, not a uniquely identified mechanism.

### Survey weak filters with a fixed backing stack

For thin Al and other weak filters, use an independently checked, fixed backing
filter B and compare **B** against **B+X**, changing only X. Keep B and its physical
position identical through the block. This measures the *incremental effect* of X
in that stack, not the standalone performance of X. A backing filter can mask
spectral or spatial effects, so validate important operating combinations separately.

Do not use automatic compensation that swaps several other foils whenever X changes:
that would make it impossible to attribute a profile change to X. Do not adjust
SSA gaps, bending or upstream focus to match counts during the experiment.

The attenuators are approximately 1.5 m upstream of the CRLs, as confirmed by
the operator. Record any more precise bank separation and whether a downstream
detector-protection filter exists; neither is assumed here.

## 3. Return to the 12 keV problem

Once a reference comparison is established, test holder 2 at fixed **12.30 keV**
and harmonic **9**, without an energy sweep initially. All searches and comparisons
must share that harmonic. Use the wide edge to capture any centroid displacement.

Candidate substitutions, with rounded predicted attenuation at 12.30 keV:

| Filter | Contents | Factor |
|---|---|---:|
| `att1_7` | 240 µm Sn, original condition | 645,700× |
| `att1_12` | 240 µm Sn, separate position | 645,500× |
| `att1_6` / `att1_11` | 120 µm Sn pair | ~804× |
| `att1_1` | 68 µm Cu | 2,291× |
| `att2_4` | 160 µm Mo | 2,058× |

Cu and Mo give a useful near-matched-attenuation comparison here, while the original
240 µm Sn condition is much dimmer. Determine exposure/detector configuration from
scouts. Compare the original condition with adequate statistics if feasible; otherwise
classify its shape as inconclusive rather than broad merely because it is noisy.

If a narrow core appears under an alternative filter and disappears reproducibly
when the original Sn filter returns, **the attenuation configuration is causally
involved**. This still does not by itself separate wavefront distortion from
spectral contamination or count-rate effects. If all adequately counted profiles
remain broad, investigate holder alignment and focus before condemning the filters.

After the fixed-optics comparison, a separate small energy or Z scan with R and
the suspect filter can distinguish a shifted best focus from a loss of achievable
focus. Keep those results distinct from the fixed-setting qualification.

## 4. Quantify shape, position and repeatability separately

Use measured dark/closed and open plateaus, not just the last three points of an
arbitrary scan window. Fit the cumulative profile with uncertainties and inspect
residuals. Use unsmoothed derivatives as diagnostics, but avoid ranking filters by
the narrowest noisy derivative spike. Analyze candidates and references identically.

For every insertion report:

- Core FWHM and its repeat/fit uncertainty, with the width method recorded.
- 10–90% cumulative edge width: sensitive to broad profile contributions that a
  narrow core FWHM misses. Report only when both plateaus and crossings are resolved.
- Edge midpoint/center displacement in absolute sample coordinates relative to
  the reference; distinguish steering from broadening.
- Wing fraction outside a predeclared core window, for example ±10 µm around each
  profile center. Estimate from the normalized cumulative edge, not integration
  of clipped/noisy derivatives. Record window size; mark unmeasured tails as such.
- Open-side rate, measured rate ratio to R, model transmission, and any monitor
  normalization. Rate ratios are not absolute foil transmissions without a valid
  reference and stable/monitored incident intensity.
- Image halo/asymmetry, per-pixel rate checks and detector settings.
- Variation across independently reinserted repeats, and between the bracketing
  reference measurements.

Compare against a time-interpolated reference only when the two bracketing R scans
are mutually consistent. If references drift beyond their measured repeatability
or a practical tolerance, invalidate the candidate comparison for qualification.
Raw measurements should remain available, with the reason for an inconclusive result.

### Proposed practical classification, to set before the qualification pass

These are suggested beamline-use tolerances, not measured uncertainties or universal
optical standards. Confirm them after the pilot establishes reference repeatability.

| Dimension | Example tolerance relative to R |
|---|---|
| Core broadening | ≤max(1 µm, 20% of reference FWHM) |
| 10–90% broadening | ≤20% |
| Increase in wing fraction | ≤5 percentage points |
| Steering | ≤2 µm center shift for fixed-position work |

Require uncertainty bounds small enough to resolve these tolerances. For a preferred
label, the upper uncertainty bound on degradation should lie within tolerance; an
unresolved difference is **inconclusive**, not evidence of equivalence. A degradation
label should reflect repeatable effects beyond measurement uncertainty with stable
reference returns. Three independent insertions are a starting point, not an automatic
statistical guarantee; add repeats if the result remains uncertain.

Store separate flags for **shape preserved**, **steering**, **halo increased**,
**insertion unstable**, and **insufficient signal/coverage**. A sharp but shifted beam
may be usable with recentering; it should not receive the same label as a broadened beam.
Initial evidence from the existing scans is “demonstrated in this configuration,”
not “qualified across energies.”

Registry fields:

```text
physical foil ID(s), material/thickness, energy, harmonic, bank/location,
backing stack, CRL holder/Z/alignment, SSA/bending snapshot,
direction (horizontal/vertical), reference ID, run UIDs, date,
FWHM ratio and difference, 10–90 width ratio, wing-fraction difference,
center shift, insertion repeatability, uncertainties, validity flags,
classification, scope/limitations
```

Do not reduce this to a single permanent good/bad bit. An attenuator-selection
policy can eventually prefer qualified combinations **within the tested energy
and configuration range**, once enough evidence exists.

## 5. Distinguish mechanisms after a reproducible effect is found

- **Physical filter/mount:** compare the matched Sn pairs; repeat removal/insertion.
  If a translation or alternate beam footprint is available, test it explicitly
  and record the position. Do not assume the present insertion devices provide it.
- **Steering or feedback response:** record feedback state and its relevant
  readbacks, upstream/downstream monitors where available, and settling versus
  time after insertion. Keep the feedback policy fixed within the main comparison.
  A later controlled feedback-state comparison is a separate experiment.
- **Spectrum:** compare matched-material/thickness filters first. For material-
  dependent differences, use a validated spectral/harmonic diagnostic if available.
  A detector-threshold scan alone is not a quantitative spectrum. The current
  transmission table ends at 25 keV and clamps out-of-range energies; do not use
  it to predict transmission at 3×12 or 3×16 keV.
- **Detector artifact/statistics:** verify the response regime, match useful count
  precision, and reanalyze repeat sums. Shorter exposures alone do not address
  instantaneous rate nonlinearity. Image ROIs must follow the same stated policy.

## Before turning this into an acquisition plan

No additional filters are assumed known good. Confirm the available open-beam
detector/monitor, any downstream attenuation, and whether a vertical knife edge is
ready. Begin with the five 240 µm-equivalent Sn configurations at 16.20 keV after
recovering the reference focus; then expand to the 8.77 keV material panel and
12.3 keV diagnostic substitutions.

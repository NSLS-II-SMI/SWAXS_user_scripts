# Kapton air-holder commissioning — final recorded weekend status

**Report date:** October 26, 2026. All times EDT (America/New_York).
**Specimen:** `kapton_air_holder_01`. Nominal irradiation energy: 6 keV.

[Download the nine-page PDF](kapton_final_report_2026-10-26.pdf).
Numeric provenance and audit: [JSON](kapton_final_report_2026-10-26.json).
Deduplicated image-attempt journal: [CSV](kapton_final_report_2026-10-26.csv).

**Scattering addendum:** [SAXS/WAXS waterfall PDF](kapton_scattering_addendum_2026-10-26.pdf)
and [findings/methods](SCATTERING_ADDENDUM.md) now provide per-frame reductions,
exposure-dependent change maps, and the complete detector-frame audit.

## Conclusion

The recorded campaign accumulated **25 h 42 min 17 s of estimated beam-on
exposure**, including **20 h 42 min 54 s added after Friday's vacuum repair**.
Post-repair beam-on pressures remained below the 0.009 Torr ceiling in the
recorded samples. The independent guard completed both recorded weekend
shutdown sequences, and the logger retained data through Monday 08:14:02.

This establishes prolonged irradiation with stable indicated vacuum during
beam-on periods and functioning staged shutdown readbacks. First/last beam-on
SAXS, WAXS and OAV arrays from both Saturday runs have now been retrieved through
Tiled. The PDF includes both WAXS/OAV comparisons on the original fixed scale.
The long session's RunStop confirms a detector timeout. A final material-damage
pass/fail assessment and resolution of the export backlog remain separate from
these verified acquisition results.

**Diode-based result for the Saturday–Monday long session (scan 1185490):**
at least approximately **9.19 × 10¹⁶ transmitted photons before the Al**, and
a conservative model dose of **1.38 × 10¹⁰ Gy (13.8 GGy)** averaged over both
Kapton sheets in the **40 × 300 µm** bounding rectangle. The rear-sheet mean is
**1.20 × 10¹⁰ Gy**; the lowest-depth, exit-face area mean is **1.05 × 10¹⁰ Gy**.
These exclude all earlier exposure and assume the confirmed geometry and passive
silicon response. The full derivation and limits are below.

## Exposure and coverage

| Quantity | Recorded result |
|---|---:|
| Log coverage | Oct 22 17:01:14 – Oct 26 08:14:02 |
| Scalar samples | 295,950 |
| Wall span | 87 h 12 min 48 s |
| Observed monitor time | 82 h 12 min 26 s |
| Unobserved restart gaps | 5 h 00 min 22 s |
| Online beam counter | 92,420.760 s — 25 h 40 min 21 s |
| Previously documented early correction | +116.029 s |
| Best-estimate campaign exposure | 92,536.789 s — **25 h 42 min 17 s** |
| Post-repair addition | 74,574.464 s — **20 h 42 min 54 s** |
| Fast-controller-open time | 63 h 10 min 45 s |

The early correction is the operator-confirmed October 22 photon MINOR-alarm
interval described in `REPORT_AND_MOVIES.md`. It is applied once; stored counters
are unchanged. Beam time alone is a shutter/BPM proxy; the dose calculation below
uses integrated diode charge independently of the early beam-time correction.
Open-shutter time includes beam outages and must not be substituted for exposure.
No unobserved gap or time after the last sample is credited.

| Main delivery window | Added exposure (h:mm:ss) |
|---|---:|
| Oct 22 initial evening | 4:59:22, including early correction |
| Oct 23 22:28 – Oct 24 10:00 | 11:17:44 |
| Oct 24 10:45 – 12:26 | 1:37:31 |
| Oct 25 01:06 – 08:07 | 6:59:25 |
| Oct 26 05:33 – 06:21 | 0:48:14 |

These selected windows omit approximately 0.10 s credited near Oct 26 02:55;
the full campaign total includes it. Independently rounded durations need not sum
exactly. Friday night's 8.88-hour continuous beam interval has scalar records but
no image records in this journal.

## Vacuum and flux

| Post-repair beam-on pressure | Median | Recorded range |
|---|---:|---:|
| WAXS | 0.0026 Torr | 0.0025–0.0027 Torr |
| MAXS | 0.0016 Torr | 0.0015–0.0017 Torr |
| SAXS | 0 | 0, accepted below gauge range |

No over-ceiling pressure was recorded in the post-repair beam-on samples.
This does not establish absence of microscopic damage or quantify outgassing.

BPM3 beam-time-weighted mean was **49.973 ± 0.571 native units** over the
campaign (weighted standard deviation, CV 1.14%); post-repair mean was
**50.053 ± 0.596**. Integrated BPM3 was 4,624,364 signal·s, not photons.
TetrAMM channel 2 was logged continuously. Its filtered beam-on median was
33,956 native units, selecting fresh readings above 1000. This is an analysis
filter, not a physical calibration or a guarantee that every transition is removed.
Episode-to-episode diode changes do not alone establish damage or realignment.

## Recorded events

### Saturday: stale-read trip and recovery

`PRESSURE_POLLING_UPDATE.md` identifies a 3.87 s scalar-sweep delay against the
former shared 3 s freshness window. The guard tripped at **Oct 24 10:00:45.259**
with all pressure values unavailable. Adjacent scalar samples recorded normal
WAXS/MAXS/SAXS pressures of 0.0026/0.0016/0 Torr.

- Boundary readbacks confirmed at 10:00:48.526.
- Pump IV1 confirmation at 10:01:19.327, after the specified 30 s delay.
- Turbo disable at 10:01:19.853; cooling-water closure at 10:01:21.275.
- Eight post-trip image end records, 10:01–10:36, with zero added beam time.
- A separate pressure excursion began at 10:37:49 during the documented recovery
  period; all pressures were below the ceiling again by 10:41:08.
- Guard rearmed at 10:45:04.730.

**Deployment finding:** the dedicated pressure-reader fix is present in the
source tree, but the final database has neither `pressure_samples` nor the
`pressure_stale_s` identity setting. Its use during this recorded campaign is
not established. The latest procedure must not be treated as proof of the code
actually running over the weekend.

### Monday: incomplete image, then later pressure trip

The last image with an end record started at **06:16:42.666** and ended at
06:16:47.535. The next attempt started at **06:21:44.845** and remained pending.
The first closed-shutter scalar sample is **06:21:47.284**; the counter stops at
92,420.760 s. A close operation at 06:22:18.929 follows the attempt by about
34 s. Tiled now confirms scan 1185490 failed with **“Image detector completion
timed out”**, after 113 primary image events.
The session-finalization journal was written at 06:31:22.270.

At **08:13:15.218**, a separate high-pressure trip recorded WAXS 22 Torr and
MAXS 0.82 Torr. Boundary readbacks confirmed at 08:13:16.689; IV1 at
08:13:47.561, turbo disable at 08:13:47.575, and complete shutdown at
08:13:47.603. The shutter had already been closed for nearly two hours, so this
event added no beam exposure. Final readings at 08:14:02 were WAXS 200 Torr,
MAXS 130 Torr and SAXS zero. **The pressure-rise cause, including whether it was
intentional venting, requires operator confirmation.** These are final logged
states, not a present-time hardware check.

Valve confirmation uses the profile's `Not Open` status, not an independent
closed limit. Turbo OnOff=0 confirms disable, not rotor spin-down.

## Image and export accounting

- Initial campaign: 63 attempts; 62 returned run UIDs previously verified through
  Tiled, one failed attempt.
- Weekend single-run journal: 151 attempts; 149 end records (141 pre-trip,
  eight post-trip), two pending attempts.
- Combined: **211 image end records out of 214 attempts**. Every end record
  carries `interrupted`; normal detector shutter cycling can set that flag.
  First/last pre-trip arrays now resolve for all three detectors in scans 1185487
  and 1185490. This checks those selected arrays, not every array in every run.
- Final session export cursor: **234025**; cutoff: **289790**; difference:
  **55,765 pending scalar IDs** according to the local journal. Another 6,160
  samples were recorded after that cutoff through the end of logging.
- Tiled scan 1185490 confirms 101,417 scalar events. Its in-run summary reports
  **55,222** pending IDs at cutoff **289247**, versus **55,765** at the later local
  cutoff **289790**. The difference is 543 samples logged during finalization.
- Oct 25 15:01:55.918 is the **source timestamp** of sample 234025, not the time
  exporting stopped. The reason for the backlog is unverified; SQLite retains
  these samples for analysis and export reconciliation.

## Before/after images for the good-vacuum sessions

The original October 22 pair remains on page 5. Its first image already includes
2 min 21 s irradiation. New comparisons are:

| PDF | Run | First image | Last displayed image | Added beam time between images |
|---|---|---|---|---|
| Page 6 | 1185487, first Saturday low-pressure run | Oct 24 07:46:07, event 1 | Oct 24 09:56:02, event 27 | 2 h 09 min 41 s |
| Page 7 | 1185490, Saturday–Monday long session | Oct 24 10:51:45, event 1 | Oct 26 06:16:42, event 113 | 9 h 17 min 17 s |

Run 1185487's final eight events were post-trip and are not used as an irradiated
“after” reference. Run 1185490's final 06:21 attempt timed out and is excluded.
Both Saturday runs had good vacuum before their respective terminations; both
are included to resolve the session-label ambiguity. The timing of the small
move is not established by the scalar journal, so no dose from preceding runs
is assigned to the long-session spot.

All WAXS panels use **the same 496–18,068.518-count logarithmic yellow-hot scale**
as the October 22 pair, with nonpositive pixels masked. The Saturday detector
configurations confirm 1 s SAXS/WAXS exposure and 1 s OAV exposure. OAV uses
original RGB; no per-frame normalization or spatial registration is applied.
Campaign exposure counters printed over the panels are not spot-specific dose.

UIDs: `fca35755-e42b-4d04-9d0b-8d2c57e96702` (1185487) and
`3b958206-68d7-4659-9dac-164624aa3911` (1185490). Full-resolution selected arrays,
baseline/configuration and RunStop metadata are in `logs/weekend_image_cache/`.

## Diode current → photons → dose in gray

### Confirmed inputs and physical model

The operator confirmed **beam → two Kapton sheets → 110 µm Al → passive silicon
PIN diode**, and that the IOC current scale was unchanged during the weekend.
The read-only Oct 26 IOC check found `CurrentScale2 = 1e9`: the driver transmits
amperes and applies `Raw × CurrentScale − CurrentOffset`, so saved values are
**nA**. A value of 34,000 corresponds to **34 µA**, not 34 nA or 34 pA.
The IOC offset was already applied; it is not undone here.

The operator's microscopy establishes an approximate **40 × 300 µm** outer beam
size. We use that full rectangle (0.012 mm²), with two **5-thou = 127 µm** sheets,
total thickness 254 µm. At density 1.42 g/cm³ this is **4.32816 µg = 4.32816 ×
10⁻⁹ kg** of Kapton. This broad area reduces the inferred average relative to a
smaller beam core; it is not a lower limit on the dose at every lateral point.

At exactly 6 keV, the NIST elemental mixture gives:

| Coefficient or transmission | Value |
|---|---:|
| Al total mass attenuation μ/ρ | 115.3 cm²/g |
| Kapton total mass attenuation μ/ρ | 14.69982567 cm²/g |
| Kapton mass energy-absorption μ_en/ρ | 14.23997111 cm²/g |
| 110 µm Al transmission, density 2.699 g/cm³ | 0.03260982 (3.261%) |
| One 127 µm Kapton sheet transmission | 0.76713180 |
| Two Kapton sheets transmission | 0.58849120 (58.849%) |

Kapton weight fractions are H 0.026362, C 0.691133, N 0.073270 and O 0.209235.
Silicon generates approximately one electron–hole pair per **3.6 eV** deposited.
Assuming ideal absorption/collection gives the largest charge per incident
6-keV photon for a passive PIN diode, hence the smallest inferred photon count.
No additional correction for incomplete diode absorption or collection is made.

### Conservative integration

The largest fresh dark reading after at least five seconds continuously
fast-closed was 3.4817 nA; round upward and subtract **3.5 nA**. The dark median
was −8.54 nA, which is deliberately **not added back**. This is an empirical
background envelope, not a confidence interval on all possible baseline drift.

For each interval, require fresh valid diode values and confirmed beam at both
ends, discard gaps over two seconds, and exclude the first three seconds after
each sampled beam-on transition. Use the smaller adjacent current, clipped at
zero after background subtraction, and the minimum of the wall-time,
diode-source-timestamp and online beam-time increments. Duplicate source
timestamps add no charge. Do not extrapolate into missing time, pre-diode
measurements, the early photon-alarm correction or earlier positions.

For scan 1185490 this retains **33,262.97 s (9.2397 h)** of integration out of
33,741.74 s (9.3727 h) online beam time, giving **Q = 0.800512 C**. A conventional
endpoint beam-time-weighted integration would give 0.813557 C; the smaller
conservative integral is used for all headline figures.

### Equations

With `e = 1.602176634e-19 C`, `E = 6000 eV × 1.602176634e-19 J/eV`, and the transmissions above:

```text
N_diode >= (Q/e) × 3.6/6000
N_transmitted_after_Kapton >= N_diode / T_Al
N_incident_on_Kapton >= N_transmitted_after_Kapton / T_Kapton

E_abs = N_incident × E × (mu_en / mu) × (1 − T_Kapton)
D_two_sheet_mean = E_abs / illuminated_mass_kg       [Gy = J/kg]
```

Using **μ_en**, rather than treating all attenuation as deposited energy, excludes
the nonabsorbed part of primary-beam removal. The first sheet gets energy
`N_incident × E × (mu_en/mu) × (1 − T_sheet)`; the rear sheet gets that amount
times `T_sheet`. Divide each by half the total illuminated mass for sheet doses.

### Results

| Selected exposure | Conservative Q (C) | Photons after Kapton / before Al | Two-sheet mean dose (Gy) | Rear-sheet mean dose (Gy) |
|---|---:|---:|---:|---:|
| All recorded diode exposure, across positions | 2.209238 | 2.5371 × 10¹⁷ | 3.8171 × 10¹⁰ equivalent* | 3.3141 × 10¹⁰ equivalent* |
| Saturday morning run 1185487 only | 0.267747 | 3.0748 × 10¹⁶ | 4.6261 × 10⁹ | 4.0165 × 10⁹ |
| **Saturday–Monday run 1185490 only** | **0.800512** | **9.1931 × 10¹⁶** | **1.3831 × 10¹⁰** | **1.2008 × 10¹⁰** |
| Between the displayed 1185490 images | 0.793471 | 9.1122 × 10¹⁶ | 1.3709 × 10¹⁰ | 1.1903 × 10¹⁰ |

*Photon counts across positions can be summed, but the all-exposure dose is an
**equivalent single-footprint** value, not confirmed dose to a moved spot.

For the long session alone:

- At the diode, **≥2.9978 × 10¹⁵ photons**, with accepted-time mean flux
  **≥9.01 × 10¹⁰ photons/s**.
- After Kapton and before Al, **≥9.1931 × 10¹⁶ photons**.
- Before Kapton, **≥1.5621 × 10¹⁷ photons**.
- Model energy absorbed in both sheets: **59.863 J**.
- Front-sheet mean: **1.5654 × 10¹⁰ Gy**; rear-sheet mean: **1.2008 × 10¹⁰ Gy**.
- The model's exit-plane area-mean dose, the lowest-depth value, is
  **1.0487 × 10¹⁰ Gy (10.5 GGy)**. Thus **roughly 10 GGy** is the most conservative
  quoted depth-specific area-average estimate for this run under these assumptions;
  the full two-sheet mass average is **13.8 GGy**.

These are **diode-confirmed exposure, conservative sampled model-dose estimates**,
not statistically certified bounds. They assume 6-keV photons, passive Si/no
internal gain, unchanged nA calibration, the stated thicknesses and density,
the full relevant beam within the microscopy rectangle, and local energy
deposition/charged-particle equilibrium. Finite diode efficiency or additional
downstream loss raises inferred photons; electron escape, footprint uncertainty
and unresolved sub-second variation are not quantitatively bounded here.

### Physics sources

- [NIST Kapton composition and density](https://physics.nist.gov/cgi-bin/Star/compos.pl?matno=179).
- NIST exact 6-keV mass attenuation and mass energy-absorption rows:
  [H](https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z01.html),
  [C](https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z06.html),
  [N](https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z07.html),
  [O](https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z08.html),
  [Al](https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z13.html).
- [LBNL X-ray Data Booklet, §4.5](https://xdb.lbl.gov/Section4/Sec_4-5.pdf):
  silicon electron–hole pair creation energy and current-mode detectors.
- [EPICS quadEM database documentation](https://github.com/epics-modules/quadEM/blob/master/docs/source/databases.rst):
  TetrAMM raw amperes and CurrentScale conversion.

## Provenance and reproduction

Source: `logs/kapton_air_holder_01_bpm2_bpm3_waxs_oav_2026-10-26_snapshot.sqlite`,
a checkpointed analysis snapshot including the copied WAL. SQLite `quick_check`
passed. The source database/WAL had stable modification times during inspection;
checkpointing and backup were performed on the analysis copy.

SHA-256:
`7396e156d448cd138120ed1ec07461330f07aa84880549cc064afd3684d3854b`

Supporting notes: `WEEKEND_OPERATION.md`, `LOW_PRESSURE_CONTINUATION.md`,
`PRESSURE_POLLING_UPDATE.md`, `ACCEPTANCE_1185485.md`, and `REPORT_AND_MOVIES.md`.

From this directory, regenerate the PDF, JSON and image-audit CSV offline:

```bash
pixi run python final_weekend_report.py --apply --replace-existing
pixi run python -m unittest test_kapton_dose -v
```

The cache downloader is `pixi run python weekend_reference_images.py --apply`;
it reuses cached files, reads only selected detector frames, and records run
provenance. `kapton_dose.py` performs the offline charge/transport/dose calculation.
The Markdown narrative is maintained alongside the generated artifacts. Final
follow-up is quantitative damage interpretation, export reconciliation, and
confirmation of the circumstances of Monday's pressure rise.

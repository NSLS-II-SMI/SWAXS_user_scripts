# Kapton SAXS/WAXS scattering addendum — October 26, 2026

[Nine-page PDF](kapton_scattering_addendum_2026-10-26.pdf)

## Coverage

All **211 recorded image sets from 65 runs** were retrieved or reused from the
existing caches and reduced with `smi-tiled`, using Pixi:

| Scan ID(s) | Acquired images | Used in exposure figures |
|---|---:|---:|
| 1185420–1185481 | 62 WAXS | 61 WAXS |
| 1185487 | 35 SAXS + 35 WAXS | 27 SAXS + 27 WAXS |
| 1185489 | 1 SAXS + 1 WAXS | 0 — detector-dark |
| 1185490 | 113 SAXS + 113 WAXS | 113 SAXS + 113 WAXS |

Thus **211 WAXS and 149 SAXS patterns are reduced**, and **201 WAXS and 140 SAXS
patterns** enter the exposure figures. The PDF contains five waterfall/change-map
pages, q-band trends, detector/mask checks, and the scan index.

- Scan **1185427** has only 46 nonnegative WAXS counts; **1185489** has 27 WAXS
  counts and 48 SAXS counts. Both are detector-dark despite pre-trigger beam-on
  readbacks and are excluded from the exposure trends.
- **1185487 events 28–35** are post-trip. Their WAXS arrays retain substantial
  signal while SAXS is nearly dark; they are not dark-background references.
- **1185419, 1185486 and 1185488** have no primary images. **1185482–1185485** are
  separate beam-down acceptance tests. The incomplete final attempt in 1185490
  produced no primary image.

## Observed changes

The exposure axis is the campaign beam-on counter, including the documented
116.029 s correction. It is not wall time or spot-specific dose. The sampled
long session spans **9.288 h added beam exposure between its first and last images**.

For scan **1185490**, means of the last three versus first three patterns give:

| Detector | q band (Å⁻¹) | BPM3-normalized change |
|---|---|---:|
| SAXS | 0.002–0.008 | +21.30% |
| SAXS | 0.010–0.025 | +23.70% |
| SAXS | 0.030–0.060 | +26.69% |
| WAXS | 0.4–0.8 | +8.16% |
| WAXS | 1.0–1.8 | +2.69% |

The evolution is **non-monotonic**, with large changes across overnight beam gaps
(events 19→20 and 104→105). Broad-WAXS endpoint values are particularly sensitive
to the averaging window: the final three have 3.40% CV, and the single first/last
comparison is −0.72%. The waterfalls and full-series change maps are therefore
more informative than an endpoint percentage alone.

Saturday morning scan 1185487 changes by approximately −0.7% to +1.2% across the
reported SAXS/WAXS bands. The October 22 WAXS series changes by +14.39% in
0.4–0.8 Å⁻¹ and −1.85% in 1.0–1.8 Å⁻¹.

These are measured scattering changes. Background, transmission, sample/beam
position changes and material changes are not separated by these data. No unique
radiation-damage or local-dose attribution is made.

## Reduction and audit

Recorded 6 keV energy; 1 s detector exposures; SAXS pin mask; calibrated SAXS and
3-panel WAXS geometry; solid-angle correction; 2×2 pixel splitting. Figures are
scaled to incident BPM3 = 50, without per-pattern area normalization or
downstream-diode normalization. SAXS and WAXS are shown independently.

The WAXS `bsx` readback is the overflow value −2147.483648 mm. The unshifted bundled
beamstop polygon matches the visible stationary shadow; it is held fixed rather
than shifted using that invalid motor value. The mask and calibration provenance
are saved per run.

- [Frame audit and scan/UID mapping](kapton_scattering_addendum_2026-10-26.csv)
- [Accepted reduced profiles](kapton_scattering_addendum_2026-10-26_iq.csv)
- [Metrics, validation and provenance](kapton_scattering_addendum_2026-10-26.json)
- Per-run raw metadata, arrays, all-frame reduced NPZ files and geometry:
  `logs/scattering_cache/`; existing image caches are reused.

From this folder, reproduce offline:

```bash
pixi run --manifest-path ../../../smi-tiled/pyproject.toml python scattering_addendum.py --apply --reduce --report
```

Add `--download` to retrieve missing arrays from Tiled. Without `--apply`, the
script previews its outputs. The report validates complete RunStop event
coverage, unique identifiers, q/exposure ordering and intensity normalization.

Analysis prepared with OpenCode (GPT-6 Astra).

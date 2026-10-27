# Kapton irradiation commissioning

## Scattering-versus-exposure addendum — October 26

- [SAXS/WAXS waterfall PDF](kapton_scattering_addendum_2026-10-26.pdf):
  per-frame reductions of the initial WAXS-only series and the later combined
  SAXS/WAXS sessions, exposure-colored waterfalls, change maps, and mask checks.
- [Findings and methods](SCATTERING_ADDENDUM.md): coverage, exclusions, measured
  changes and interpretation of the non-monotonic exposure series.
- [Frame/scan/UID audit CSV](kapton_scattering_addendum_2026-10-26.csv),
  [reduced I(q) CSV](kapton_scattering_addendum_2026-10-26_iq.csv), and
  [metrics/provenance JSON](kapton_scattering_addendum_2026-10-26.json).
- Reproduce using the sibling reduction project's Pixi environment, from this
  directory:

  ```bash
  pixi run --manifest-path ../../../smi-tiled/pyproject.toml python scattering_addendum.py --apply --reduce --report
  ```

  Add `--download` to retrieve missing raw frames and metadata through Tiled.
  Without `--apply`, the script previews its outputs. Cached reductions and
  images are under `logs/scattering_cache/`; the original image caches are reused.

## Final recorded weekend report — October 26

- [Nine-page PDF](kapton_final_report_2026-10-26.pdf) and
  [Markdown report](kapton_final_report_2026-10-26.md): exposure through Monday
  morning, Tiled-verified Saturday before/after images on a common scale, and
  diode-derived photon/dose estimates.
- Scan 1185490 alone: conservative two-sheet mean dose **1.38e10 Gy**, with
  6 keV, two 127 µm Kapton sheets, 110 µm downstream Al, and the operator's
  40 × 300 µm bounding footprint. See the report for the lower rear-sheet and
  exit-plane estimates, current-unit confirmation, method and model limits.
- Reproduce offline: `pixi run python final_weekend_report.py --apply --replace-existing`.
  Tiled reference cache: `pixi run python weekend_reference_images.py --apply`.

## Current acquisition after vacuum repair

**All pressure ceilings: 9e-3 Torr.** Valid WAXS/MAXS pressure is positive and
below the ceiling; SAXS zero is accepted as below range. `Settings()` and both
`weekend_settings()` modes use this ceiling. EPICS read/connection timeouts are 2 s.

Pressure polling has its own thread, independent of shutter/ring/diode reads.
Transport failures get a **10 s deadline from the last valid pressure read**
(`pressure_stale_s`); high readings, gauge alarms and invalid values still trip
immediately when observed. Pressure samples and age/error diagnostics are stored
separately in SQLite and exported in the new single-run `pressure_samples` stream.
See `PRESSURE_POLLING_UPDATE.md` for the in-place database migration and reload.

Follow **[LOW_PRESSURE_CONTINUATION.md](LOW_PRESSURE_CONTINUATION.md)** for setup,
resume, normal live tests, and the staged-shutdown live test.

- Images: **SAXS (`pil2M`), WAXS (`pil900KW`), OAV (`OAV_writing`)**; one-second
  scattering exposures every five minutes, OAV retains its optical exposure.
- Continuous ~1 Hz scalars: **BPM2 SumX** (beam-present threshold >10 at 6 keV),
  **BPM3 SumX** (incident flux only), **TetrAMM channel 2**, three pressures,
  shutter states, timestamps, validity/alarm flags and exposure counters.
- FE open **and EPS enabled**: unmanaged 6000 eV move, feedback on, then beam
  confirmation. Enabling while FE stays open also triggers recovery.
- Pressure trip: close fast shutter and **GV6/GV7**, wait **30 seconds** after
  boundary closure attempts, close **pump IV1**, **turbo OFF**, **water CLOSED**.
- After verified boundary isolation, periodic images and monitoring continue.
  The plan never explicitly opens the fast shutter after a trip; detector
  automatic shutter pulses are allowed and the plan closes it after images.
  Beam time is inhibited after the trip even if upstream BPMs remain bright.
  No vent commands are issued. See the current procedure for failure handling.

The single-run candidate is `kapton_single_run.py`, using the public
`smi_plans.session` API. The legacy `kapton_images` remains available for separate
runs per image set and accepts `detectors=[pil2M, pil900KW]`. Both use the same
monitor and explicit independent pressure guard. Arm the guard before acquisition.
Neither importing a script nor constructing Settings operates hardware.

## Device map

| Role | Ophyd interface / PV |
|---|---|
| FE closed bit (0 open, 1 not open) | `fe_shutter.status`, `XF:12ID-PPS{Sh:FE}Sts:Cls-Sts` |
| EPS enable (1 enabled, 0 disabled) | `smi_shutter_enable`, `SR:C12-EPS{PLC:1}Sts:ID_BE_Enbl-Sts` |
| Fast controller (0 open, 7 closed) | `fs.status_pv`, `XF:12IDA-BI:2{EM:BPM1}DAC3` |
| Fast commands | `fs.open_cpt` / `fs.close_cpt`, `XF:12IDC-ES:2{PSh:ES}pz:sh:open` / `...:close` |
| Photon position | `ph_shutter.status`, `XF:12IDA-PPS:2{PSh}Pos-Sts` |
| Beam-present gate | `xbpm2.sumX`, `XF:12IDA-BI:2{EM:BPM2}SumX:MeanValue_RBV` |
| Incident flux | `xbpm3.sumX`, `XF:12IDB-BI:2{EM:BPM3}SumX:MeanValue_RBV` |
| TetrAMM | `pin_diode.current2.mean_value`, `XF:12ID:2{EM:Tetr1}Current2:MeanValue_RBV` |
| WAXS pressure | `chamber_pressure.waxs`, `XF:12IDC-VA:2{Det:300KW-TCG:7}P:Raw-I` |
| MAXS pressure | `chamber_pressure.maxs`, `XF:12IDC-VA:2{B1:WAXS-TCG:9}P:Raw-I` |
| SAXS pressure | `XF:12IDC-VA:2{Det:1M-TCG:8}P-I` |
| GV6 | `chamber_pressure.upstream_valve`, `XF:12IDC-VA:2{Mir:BDM-GV:6}` |
| GV7 | `chamber_pressure.waxs_saxs_valve`, `XF:12IDC-VA:2{Det:1M-GV:7}` |
| Pump IV1 | `chamber_pressure.turbo_valve`, `XF:12IDC-VA:2{Det:300KW-IV:1}` |
| Turbo disable | `chamber_pressure.turbo_enable`, `XF:12IDC-VA:2{Det:300KW-TMP:1}OnOff` |
| Cooling water | `chamber_pressure.turbo_cooling_valve`, `XF:12IDC-PU{PCHW-Vlv:Supply}` |

Use the TIFF-writing OAV view, not plain `OAV`. Do not stage or trigger the
TetrAMM with image detectors: configure its continuous mode once via
`RE(configure_diode(pin_diode_ext))` and sample the scalar signal.

## Data and exposure accounting

The independent monitor writes one SQLite transaction per sample. Use the existing
`logs/` folder on a local filesystem, not NFS for SQLite WAL. The monitor survives
RE pauses, not process/host failure. Resume restores persisted counters and marks
restart gaps unobserved. New specimen = new database. One file lock prevents two
writers. `resume_pressure_limits=True` explicitly audits pressure-limit changes;
`resume_added_diode=True` permits adding the restored diode PV without discarding
totals. `resume_weekend_update=True` permits the specific 0.009 Torr / 2 s /
diode + enable migration while preserving the same database and auditing changes.
Other identity mismatches still fail with details.

`fast_open_s` counts controller-open time; `beam_s` requires FE/photon/fast-open, EPS enabled,
and fresh BPM2 >10, and is forced off when isolation trips. Unknown inputs/time
are tracked separately. Photon `Open`/`Not Open` with MINOR STATE alarm is an
accepted enum; `Not Open` still blocks pre-trip beam/images. BPM3 and TetrAMM are
measurements, not beam gates. These counters are not calibrated absorbed dose.

The single-run streams are `primary`, `scalars`, `operations`, `isolation`, and
`session_summary`; details and Tiled verification are in `SINGLE_RUN_ACCEPTANCE.md`.
Scalar hints are limited to BPM3, diode, WAXS/MAXS pressure. All other fields are
recorded without excessive live plotting.

## Historical report and development notes

- `kapton_overnight_report_2026-10-23.pdf`: five-page historical report and before/after images.
- `REPORT_AND_MOVIES.md`: Tiled-derived images, fixed log yellow-hot movies, Pixi reproduction.
- `ACCEPTANCE_1185483.md`: successful WAXS/OAV-only live test before the new SAXS/TetrAMM configuration.
- `SINGLE_RUN_DESIGN.md`: original architecture discussion; current behavior is in the live procedure.

Hardware protection is implemented by the independent guard, not RE document
emission. It still depends on the host, EPICS and working actuators; existing
EPS protection remains independent. Verify valve identity, polarity, turbo/water
sequence and detector behavior in the supervised test before unattended use.

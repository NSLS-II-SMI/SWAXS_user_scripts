# Initial holder2 multi-edge timing calibration

Examined 2026-09-30 using the configured Tiled `auto` profile, `smi/raw`.
Query: `scan_name == 'holder2_multi_edge_grid'`, scan IDs 1170294–1170400.
Snapshot contained scans 1170294–1170368. Times use America/New_York.

## Data and exclusions

- 72 successful full-length runs: 6,166 recorded exposures.
- Seven complete samples, each with 856 exposures and ten runs.
- Two successful S5 runs are included in per-edge calibration.
- Excluded one success-marked run with zero events (1170294), the failed
  five-event Co run (1170367), and the open continuation (1170368).
  Open runs are not read or assigned a completed duration.
- The 17,870.99-second gap before S5 (~4 h 58 min) and 648.18-second
  failure-to-restart gap are interruption time, not normal scan overhead.
- Representative detector configurations from 1170295, 1170300 and 1170367
  confirm acquire_time=1.0 s, acquire_period=1.001 s, num_images=1, including
  both SAXS and WAXS at 20 degrees. The plan specifies 2 s energy settling.

## Observed run durations

Median start-to-stop duration, including the initial energy move, events,
and in-run closing/baseline work. Excludes the gap before opening the run.

| Edge | Points | WAXS 0° (min) | WAXS 20° + SAXS (min) |
|---|---:|---:|---:|
| Mn K | 87 | 10.40 | 10.67 |
| Fe K | 87 | 8.93 | 9.12 |
| Co K | 87 | 9.09 | 9.33 |
| Ni K | 87 | 8.97 | 9.23 |
| Zn K | 80 | 8.87 | 8.98 |

Seven complete sample spans (first run start through last run stop):
s1 92.54 min; S2 95.02; S3 94.43; S4 94.98; S8 94.95; s7 95.10; s6 95.44.
The first sample's initial Mn run was faster, consistent with a shorter initial
energy move; use the other samples for repeated-sample planning.

## Timing components

- Event-to-event cadence: mean ~6.13 s at 0°, ~6.26 s at 20°; medians ~6.07
  and ~6.13 s. These include exposure, energy motion/settling, XY motion,
  detector/readout, and callback/document handling.
- Step-size medians for 1, 3 and 5 eV are similar. 5 eV steps have a longer
  mean/tail (observed maxima ~13.5–14.1 s), which should not be discarded
  from a realistic operating estimate.
- No large extra column-transition cost is evident: median X transitions
  ~6.10/6.21 s versus Y steps ~6.07/6.12 s at 0°/20° respectively.
- Start to first event: Mn ~96–99 s, Zn ~42 s, other edges ~10–12 s.
  This is consistent with the large Zn→Mn reset and Ni→Zn jump. It is a
  measured combined startup time, not an independently measured motor duration.
- Last event to stop: ~2.4–2.5 s.
- Between adjacent successful full runs: same-angle edge transition median
  0.79 s; same-sample 0→20° transition 67.94 s; routine sample transition
  75.19 s (also includes 20→0°). These are combined overheads, not isolated
  arc or translation motor times.

## First planning estimate

For this exact list/angle/ordering/exposure configuration:

```
per_sample = sum(ten median run durations) + 8 * 0.79 s + 67.94 s
           = 94.82 min
batch(N)   = N * 94.82 min + (N - 1) * 75.19 s
batch(8)   = 12.79 h  (~12 h 47 min)
```

This excludes initial positioning/staging before the first run and interruptions.
Allowing a planning margin of 10–15% gives approximately 14–14.7 h for eight
samples; that margin is a scheduling choice, not a measured confidence interval
or allowance for multi-hour failures.

For different list lengths, an initial component model is:

```
sum_over_runs(startup_for_energy_jump + (n_points - 1) * mean_point_interval
              + closing_overhead)
+ inter_run_edge_gaps + arc_changes + sample_changes
```

Do not add the exposure or 2 s settle again: they are already inside the measured
point interval. Extrapolation to different exposure times is not yet calibrated;
`new_interval ≈ old_interval + (new_exposure - 1 s)` is only a first approximation.
Different energy ranges/harmonics, detector frame counts and plan order require
additional calibration, especially for large energy resets.

## What Tiled supplies, and what is still needed

Tiled provides start/stop timestamps, status, event timestamps, energy setpoints,
grid point/XY/arc readbacks, sample/edge/list metadata and detector configuration.
Only scalar columns were downloaded; no images are required.

For future batch estimates, supply sample count, energy lists and their order,
angle order, exposure/frame count, settle settings, grid pitch, and any added
alignment/apparatus operations. Run UIDs or a scan-ID interval identify the
calibration dataset; the current batch was discoverable from its scan_name.

To attribute overhead precisely to energy vs XY vs detector vs callbacks, we
need RunEngine message timing or correlated beamline logs. Event timestamps
alone cannot split these components or establish the cause of an outlier.
Known beam-loss, manual-pause and recovery periods should be labeled separately.
An experiment/batch UID in future run metadata would make grouping automatic.

## Reproduce

```
pixi run python ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/examine_scan_timing.py
```

The script regenerates `holder2_timing_runs.csv`, `holder2_timing_intervals.csv`
and `holder2_timing_summary.json`. It explicitly requests the real `time` field:
reading an xarray dimension named time without its coordinate can otherwise
produce positional indices instead of event timestamps. Timestamp bounds are
checked against run start/stop to catch that error.

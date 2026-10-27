# Overnight report and movies

## Deliverables

- `kapton_overnight_report_2026-10-23.pdf`: compact five-page report, pressure/flux
  graphs, integrated statistics, trip detail, matched WAXS/OAV before-and-after images,
  and a linear-scale post-closure drift analysis (23:00–06:30 EDT).
- `kapton_waxs_2026-10-22.mp4`: 960×720 H.264, 62 frames at 5 fps, ~0.5 MB.
- `kapton_oav_2026-10-22.mp4`: 960×720 H.264, 62 frames at 5 fps, ~6.3 MB.
- `waxs_before.png`, `waxs_after.png`, `oav_before.png`, `oav_after.png`:
  annotated stills. These correspond to scans 1185420 and 1185481.
- Report JSON: numeric statistics, settings, provenance and source SHA-256.
- Report CSV: all 63 image attempts, including the one failed early attempt.
- `movie_scale.json`: exact fixed scattering display limits and palette definition.

All 62 returned image runs were downloaded through Tiled; raw file directories
were not used. Cached full-resolution arrays and per-run metadata live under
`logs/image_cache/`, ignored by git. Both movies cover 17:16:26–22:56:27 EDT on
October 22. A displayed frame is not a real-time playback interval: the outage
causes a timestamp jump, labeled with elapsed minutes since the preceding frame.
The first returned image already had **2 min 21 s** of corrected exposure; it is
not a virgin/unirradiated reference. The final frame has **4 h 58 min 19 s**;
the subsequent exposure before shutter closure brings the total to **4 h 59 min 22 s**.

WAXS uses a fixed **logarithmic yellow-hot** map (black → red → orange → yellow →
white), with limits **496–18,068.518 counts** derived from pooled sampled positive
pixels across all frames (1st and 99.8th percentiles). Zero/negative pixels are
masked. The color scale never rescales per frame. High pixels above the display
maximum saturate visually; raw cached arrays retain the original counts.
OAV uses the original RGB values; no per-frame brightness normalization is applied.

Beam-time labels include the operator-confirmed **116.03 s** early correction
where the fast shutter was open and BPM3 was near 49 despite the photon MINOR
alarm. Online database counters are preserved unchanged.

## Reproduce with Pixi

This directory has `pixi.toml` and `pixi.lock` for the report/image environment.

```bash
pixi run preview-report
pixi run images       # Tiled authentication if uncached; then movies
pixi run movies       # regenerate from cache, no Tiled requests
pixi run report       # regenerate PDF + JSON + CSV with before/after images
```

The downloader uses bounded retries, request timeouts and pacing, one run at a
time. Original arrays are cached so rendering never rereads Tiled. Rerendering
explicitly overwrites derived movies/stills; report replacement is explicit in
the Pixi task. The SQLite source is read immutably only when no nonempty WAL is
present; a live session requires an owner-created consistent SQLite backup.

For continuation controls see `WEEKEND_OPERATION.md`; the single-run image/scalar
stream proposal is in `SINGLE_RUN_DESIGN.md`.

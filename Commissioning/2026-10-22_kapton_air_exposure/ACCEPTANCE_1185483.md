# Live beam-down acceptance — scan 1185483

Run UID: `9051d8ce-6085-4c54-adbc-a57298b68b1e`

Verified through Tiled on 2026-10-23, using Pixi and `verify_tiled()`.
The RunStop reports **success**.

| Check | Result |
|---|---|
| Primary image pairs in one run | 5 |
| Scalar events | 133, contiguous IDs 1–133 |
| Median scalar source interval | 0.999939 s |
| Median image interval | 29.907483 s |
| Operations | 11: five image starts, five reopen confirmations, final shutter close |
| Pending scalar / operation records at final cutoff | 0 / 0 |
| FE state | Closed throughout scalar stream |
| Credited beam time | Zero |
| Shutter between image pairs | Open in checked idle samples |
| Per-image shutter reopen confirmation | All five |
| OAV image array | `(5, 1, 2472, 3296, 3)` |
| WAXS image array | `(5, 1, 619, 1475)` |
| First/last arrays resolved through Tiled | Both detectors |
| Max WAXS / MAXS / SAXS pressure | 0.003 / 0.0019 / 0 Torr |

## Remaining observations

- The final shutter closure is recorded in `operations`. The final five scalar
  samples still report fast-open: the in-run cutoff preceded the next 1 Hz sample
  after closure. The test logger continues briefly afterward in SQLite. Thus this
  run verifies the close operation but not a post-close scalar sample in Tiled.
- WAXS `stats1_total=-2` is not an image-data integrity check. First/last arrays
  resolve, contain 58,369 negative pixels (including detector gap/mask codes),
  and are predominantly zero outside those pixels: only 11 / 14 positive pixels.
  Both frames contain a maximum of 1,736,200 counts. Inspect hot pixels, mask and
  ROI placement before interpreting WAXS dark intensities; do not call this a
  quantitative detector-background acceptance solely from the saved arrays.
- User-facing TIFF naming links, long-run midnight behavior, and the separate
  live pressure/valve-isolation phase remain to be checked by the operator.

The live test establishes the single-run image/scalar structure and basic shutter
cycling. It does not automatically activate the new plan for irradiation.

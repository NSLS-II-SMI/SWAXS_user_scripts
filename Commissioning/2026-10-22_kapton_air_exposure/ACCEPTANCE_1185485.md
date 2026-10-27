# Live staged-shutdown acceptance — scan 1185485

Run `79a1a03f-186d-4768-940c-c564bf62949e`, October 23, 2026.
Verified through Tiled using Pixi and `verify_tiled()`: **passed**, RunStop success.
All times below are EDT.

| Action | Logged time / confirmation |
|---|---|
| Scheduled test trip | 11:57:33.322 |
| Fast shutter, GV6, GV7 closure confirmed | 11:57:35.486; all first attempt |
| Pump IV1 closure confirmed | 11:58:06.380; 30.893 s after boundary confirmation |
| Turbo OnOff disabled | 11:58:06.811; readback 0 |
| Cooling-water closure / shutdown complete | 11:58:07.419; all results confirmed |

- Six SAXS/WAXS/OAV sets in one run; **two pre-trip, four post-trip**.
- Post-trip flags: `[0, 0, 1, 1, 1, 1]`.
- Explicit fast-shutter reopen flags: `[1, 1, 0, 0, 0, 0]`.
- 169 scalar events, contiguous IDs 1–169; median interval **1.000053 s**.
- Median image interval **29.903071 s**.
- First/last arrays resolved through Tiled for all three detectors:
  OAV `(6,1,2472,3296,3)`, SAXS `(6,1,1679,1475)`, WAXS `(6,1,619,1475)`.
- TetrAMM valid in every exported scalar sample; raw dark readings ranged from
  −7.0637 to −2.1031 in the channel's native units. This tests acquisition, not
  a calibrated current/background acceptance.
- Zero credited beam time; FE closed. Scalar/operation cutoff exports complete.
- Pressure logging remained running as `test_monitor`; guard remains latched as
  `test_guard`. A later WAXS reading of exactly 0.009 Torr is at the configured
  threshold, but does not rearm or retrigger an already-latched shutdown.

Closure confirmation uses the profile's `Not Open` valve status, not an independent
closed limit. Turbo OnOff=0 confirms disable, not rotor speed. Automatic detector
shutter pulses remain possible during post-trip image acquisition as requested.
Pumpdown and valve/turbo/water restoration must be explicit before irradiation.

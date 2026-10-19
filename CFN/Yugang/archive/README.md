# CFN/Yugang archive (2024 – 2026C1)

**Historical beamtime scripts.** They were moved here on 2026-10-18, when the folder was reorganized
around the new `YZhang_SMI_Base.py`. They are kept for their recipes and their header notes, which
hold the beamtime records. Do not load them as current code.

They were written for the **pre-2026 SMI profile**. Against the current profile (`smi_beamline`
package) they break in several ways:

| What the old scripts do | What the current profile does |
|---|---|
| Call `det_exposure_time(t, t)` bare | It is now a plan, so a bare call **does nothing** and the exposure time is not set |
| Name files with `sample_id(user, name)` | Deprecated: it mutates `RE.md`. The beamline also appends `_eV_wa_sdd` to every name |
| Treat `stage` as the hexapod (`alignement_gisaxs_hex`) | `stage` is now the **Huber** stack, in mm |
| Use `SMI_Beamline()`, `alignement_gisaxs` and `pil300KW` | Use `smi` / `SMI`, `alignment_gisaxs`; `pil300KW` is gone |
| Use WAXS arcs such as 7, 10 or 15 deg | Arc must be 0 or >= 14.5 deg while the WAXS beamstop X motor is unplugged (since 2026-06) |
| Set `BEAMSTOP_X` by hand after alignment | `smi.modeMeasurement()` restores the 2M beamstop itself |

Most of the 2026C1 transmission files are copies of one template. They differ only in the
sample tables and `project_set`.

| File | Beamtime / group | Setup and assumptions | Replaced by |
|---|---|---|---|
| `YZhang_SMI_Base_2024-2026C1.py` | old shared base | Global `sample_dict`/`pxy_dict`; `motor='pizeo'` switch; hexapod; legacy OAV paths (2024_x); bare `det_exposure_time` | `../YZhang_SMI_Base.py` |
| `2024C3.py` | 2024-3, YZ (FTeng/FLu samples) | Microfocus maps (`getSamMap`); Lakeshore melting / annealing T series; `RE()` inside loops | `run_trans`, `grid_cells` (maps), Lakeshore not ported |
| `2024C3_Drop.py`, `2025C2_SMI.py` | 2024-3 / 2025-2, YZ autonomous droplet synthesis | `DropletReactor`; MDrive m5 (X) / m3 (Z); well plate and Kapton tube geometry; npz hand-off to the BO loop; header has the 2025 beamstop API history | not ported (special purpose) |
| `2025C2_SZhang.py` | 2025-2, S. Zhang | `NanoSyn` in-situ time series on MDrive | `run_series` |
| `2025C2_Kim.py`, `2025C2_PGuo.py` | 2025-2, H. Kim / P. Guo | GI bar + Linkam; `Aligned_Dict` keyed by index; `GIWAXS_TD_run` cryo with drift guards (hexapod) | `align_gi_samples`, `run_gi`, `run_gi_temperatures` |
| `2025C3_XLin.py` | 2025-3, X. Lin | Transmission bar on MDrive (mm); `NanoSyn` with a serpentine dose dither | `run_trans`, `run_series(spots=...)` |
| `2026C1_CNam.py`, `2026C1_PGuo.py`, `2026C1_XDuan.py` | 2026-1, C. Nam / P. Guo / X. Duan (UCLA) | GI in vacuum + Linkam (XDuan with LN2, setpoints in K); `BEAMSTOP_X`; the vacuum and Linkam procedures are copied into `../README.md` | `2026C3_PGuo.py` |
| `2026C1_EHu.py`, `2026C1_FLu.py`, `2026C1_OGang.py`, `2026C1_ThreeGroups.py`, `2026C1_InSituDemo.py`, `2026C1_InSituGrowth.py` | 2026-1, pass-318527, several groups | Static transmission bar on piezo, `measure_multi_waxs_loop_angles`; ThreeGroups has `{x, y}` set literals as positions (bug) | `run_trans` |
| `2026C1_Tomo.py` | 2026-1, F. Lu SAXS tomography | `prs` rotation stage (not in the current profile); microfocus 23 x 3 um; alignment procedure for the rotation axis in the header | not ported |

`git log --follow archive/<file>` shows the history from before the move.

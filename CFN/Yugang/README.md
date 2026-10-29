# CFN / Yugang Zhang — SMI acquisition scripts

There is one shared base, `YZhang_SMI_Base.py`, plus one short script per experiment that
holds that experiment's sample table, settings and run sheet. Old beamtime scripts are in
[`archive/`](archive/README.md).

| File | What |
|---|---|
| `YZhang_SMI_Base.py` | Base: samples, file names and metadata; transmission, GI, Linkam, in-situ/EC and multi-cell-holder plans |
| `2026C3_HZheng.py` | Mon 10-19 AM: H. Zheng, GISAXS + GIWAXS, RT, Al bar, air, piezo; then transmission SAXS/WAXS of the films (`run_trans_samples`) |
| `2026C3_PGuo.py` | Mon 10-19 PM: P. Guo, vacuum, piezo: GIWAXS + GISAXS at RT on the Al bar without the Linkam (`LINKAM = False`, `run_gi_rt`), GIWAXS vs T on the Linkam + LN2, one sample (`LINKAM = True`; T set by hand: `run_gi_at_T`) |
| `2026C3_TSAXS384.py` | Tue 10-20: RT TSAXS/TWAXS, 384-cell holder, 3–4 bars, Huber + piezo; UPenn B001 Au–Ag–Cu array after screening, 55 spots × 13-point cross + on-axis images (`run_holder_55after`); ORNL C. Liu powders, Box 1 384-well plate mapped from 4 corner wells (`run_cliu_box1`, one arc at a time, Huber y temperature guard; row P after pushing the plate down: `run_cliu_box1_P`); the as-prepared B001 piece, mapped from its photo through ≥ 3 centred spots (`run_holder_55before`); ORNL Box 2 suspensions + AgBH and two DNA superlattices (`run_cliu_box2`); W. Liu Au NP solutions, Box 3 (`run_wliu_box3`) and Box 4 with the Huber at one position, piezo only, SAXS arc first (`run_wliu_box4`) — all plates and the as-prepared piece ordered for few Huber moves, one arc at a time |
| `2026C3_JMayer.py` | Wed 10-21: J. Mayer (Yale), EC cell, one sample at a time: ex situ, then in-situ GISAXS + GIWAXS at arc 20 (`run_cell`, `run_insitu`); quick tests `snap_saxs/waxs/swaxs` |
| `2026C3_Murray.py` | Murray group (321244), TSAXS + TWAXS at arc 20: Linkam (LN2) on the Huber (no piezo; names carry Huber sx/sy/sz), about −50 … 50 °C, one sample at a time (`new_sample`), every frame on a fresh Huber sx/sy spot (`POS_XY_LIST`, snake order from `snake_xy`): T by hand (`set_T`, `measure_T`, time track `track_T`), then an automatic T list with the JMayer time track (`run_T_list`); RT multi-sample holder on the piezo, ~14 slots (`run_rt`); calibrant at the current position, WAXS 0/20/40 + SAXS at 40 (`collect_twsaxs`); on-axis camera images from every plan with `ova=` (default `OVA`) |
| `2026C3_OGang.py` | O. Gang group, TSAXS only (2M, no WAXS) on the Linkam, one 1 mm capillary at a time: self-assembly kinetics of DNA-origami NP superlattices on cooling from the melt, 49 → 41.5 °C in 0.1 °C steps, 3 min each (`run_T_steps`: T steps and frames on one clock, a 0.1 s frame every 60 s); beam-sensitive, so every frame on a fresh spot of a large map (`SPOT_MAP`: Y first, then the next X column, snake; `per_spot`), only changed axes move, Huber y waits while its motor is hot; Huber or piezo (`STAGE`); test frames `measure_T`, calibrant `collect_saxs`, camera images `ova=` |
| `tests/` | Offline simulation tests (no beamline needed) |
| `archive/` | 2024 – 2026C1 scripts and the old base |

All of these use 16.1 keV low-divergence beam with the SAXS 2M at 5 m. Each experiment
script's docstring is its run sheet: setup, calibrant, alignment, measurement and recovery,
with copy-paste commands.

## Start

```python
proposal_swap(<pass id>); project_set('<Project>')        # data go to .../projects/<Project>/
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_HZheng.py
preflight()        # energy, sdd, WAXS arc, 2M beamstop state, sample count, log folder
yz_help()
```

After editing positions or names, save the file and run the experiment script again.
There is no need to reload the base.

Before any real run, dry-run it. `preview` prints every file name the plan would write and
the exposure count. It moves nothing, takes no data and writes no logs. A bad arc, a
missing alignment or a removed beamstop raises the same error it would in the real run.

```python
preview(run_gi(**GI))                       # moves=True also lists the motor moves
```

## Concepts

**Axes.** These follow the console magics:

- piezo (SmarAct): `x y z th ch`, in µm and deg
- Huber stack under the piezo: `sx sy sz sth sch sph`, in mm and deg

A sample is a dict such as `{'name': 'S1', 'x': -47400, 'y': 23321}`, or for the Huber
`{'sx': 12.5, 'sy': 3.0, 'x': 0}`. `move_to` moves every axis the dict defines, in
parallel.

**Samples.** `make_samples(NAMES, POS, y=..., z=...)` accepts the old `sample_dict` /
`pxy_dict` style. It cleans the names, rejects duplicates and malformed positions, and
gives one ordered list (`SAMPLES`). `grid_cells(...)` builds cells for plates and
multi-cell bars from a 3-point calibration. `select(SAMPLES, 1, 'S7')` picks a subset.

**Plans versus console helpers.**

- Anything that takes data is a plan, run with `RE(...)`: `run_gi`, `run_trans`,
  `run_gi_temperatures`, `run_series`, `run_ec`, `measure_saxs/waxs/wsaxs`, `snap`,
  `linkam_goto`.
- `RE(ova_snap('name'))` saves the on-axis camera image (the JPEG plugin of the SAM camera, as
  the old `save_ova`) to `YZ['ova_dir']` (default `<proposal>/projects/<project>/user_data/OVA`),
  named `<user>_<sample>_x.._y.._sx.._sy.._OVA_NNN.jpg`, with a logbook row. The camera must be
  acquiring. `run_trans(..., at_sample=...)` runs such a plan at each sample's center.
- Console helpers call `RE` themselves: `align_gi_samples`, `mov_sam`, `movx`, `movy`,
  `here`, `preflight`.

**Detectors and WAXS arc.**

- The WAXS arc is the outermost loop, so each arc position is visited once. Samples are
  traversed in serpentine order.
- The 2M is read only where the WAXS detector does not shadow it (arc ≥ 16°,
  `YZ['saxs_min_arc']`). By default (`saxs='max'`) it is read once, at the largest arc.
- Arcs other than 0 or ≥ 14.5° are rejected up front while the WAXS beamstop X motor is
  unplugged (`YZ['arc_check']`).
- Nothing is exposed while the 2M beamstop is removed (alignment mode, attenuators in).
  A failed or aborted alignment restores the measurement mode itself; if the guard still
  fires, run `RE(smi.modeMeasurement())`. With no 2M beamstop selected (`'none'`), 2M
  frames are refused: `RE(pil2M.insert_beamstop('rod'))`.

**GI alignment.**

- `align_gi_samples()` runs `alignment_gisaxs` on each sample (piezo), or
  `alignement_gisaxs_hex` on the Huber with `stage='huber'`.
- The result is keyed by sample name and saved as JSON
  (`alignment_<experiment>_latest.json`) after every sample. `run_gi`, `run_series` and
  `run_ec` use that file when `aligned` is not given, so a Ctrl-C / `RE.resume()`, a crash
  or a bsui restart loses nothing. `load_alignment()` shows it.
- Re-aligning a subset (`align_gi_samples(select(SAMPLES, 3, 7))`) keeps the others.
- If a sample fails to align, it is flagged and skipped. th/y go back to where its scan
  started, the beamstop is put back and the attenuators are pulled. Abort/stop
  (`RE.abort()`) during an alignment also restores the measurement mode.
- To align a sample by hand, align it and then call `mark_aligned('S3')` (key or name).
- Other alignments are named by holder: `align_gi_samples(holder='PGuo_m100C')`, then
  `run_gi(aligned='PGuo_m100C')`.

## File names and metadata

The tools that read these files (pySAXSAI, pyScattViz, pyDataOrg) parse **only the file
name**, so every condition that matters is in it. The format follows what those parsers
accept:

```
<user>_<sample>[_<ai>deg][_<cycle>_<t>s]_x<x>_y<y>_z<z>[_T<T>C][_E<E>V]_expt<t>s   (this code)
         ..._<energy>eV_wa<arc>_sdd<mm>mm_id<scan>_<frame>_<SAXS2M|WAXS>.tif       (appended by the beamline)

HZheng_S1_0.1500deg_x45000.00_y12.34_z0.00_expt1s_16100.00eV_wa20.0_sdd5000.0mm_id...
PGuo_S2_0.1000deg_x3000.00_y5.10_z0.00_T-150.0C_expt1s_...
CFN_Water_B2-A02_x-47250.00_y-6750.00_z0.00_expt1s_...
JMayer_S1_insitu_0.1500deg_0012_360.0s_x200.00_y-400.00_z-8400.00_E-0.500V_expt1s_...
```

- **Groups.** SAXS groups on the text before `_x`, and GI on the text before `_<ai>deg`.
  Series files are found by `_<idx>_<t>s_x`. The temperature token needs a capital `C`.
- **Positions.** `x`/`y`/`z` are the piezo positions in µm (`YZ['name_xyz']`). Huber
  positions are in the metadata and the baseline. When the Huber does the spot moves (GI on
  `stage='huber'`), set `YZ['name_xyz'] = ('sx', 'sy', 'sz')` (mm) so that spots get
  different names.
- **Sample names.** `clean_name` keeps sample names to `[A-Za-z0-9-]`, with `_` between
  fields. It rewrites anything a parser would misread: `PS_xylene` → `PS-xylene`,
  `film_th5nm` → `film-th5nm`, `1.5mM` → `1p5mM`, `S1+2` → `S1-2`. Names containing
  `test`, `trash` or `dir` are skipped by the default analysis filters, which is why
  `snap()` uses `test`.
- **Metadata.** Every run's start document also carries `user_hints`:
  - sample, incident angle, temperature, potential, exposure, WAXS arc, detectors
  - all piezo and Huber positions, the sample's extra fields (cell, holder, …)
  - for series: frame index, elapsed time, and series t0 (unix and ISO)

  It also carries `geometry`, `experiment`, `user_group` and `YZ['md']` (beam,
  environment, cell). Piezo, Huber, energy, slits, attenuators and XBPMs are in the
  beamline baseline. Linkam T and the EC signals are recorded in the primary stream when
  they are used.
- **Logs.** A CSV logbook (`logbook_<user>.csv`) has one row per exposure: time, scan_id,
  uid, name, conditions and positions. The alignment JSONs go next to it, in
  `/nsls2/data/smi/proposals/<cycle>/<pass>/projects/<project>/yz_logs/`. If that is not
  writable, they go to `~/yz_smi_logs/<pass>_<project>/`. `preflight()` prints which one
  is used.

## Experiment notes

**Linkam (`LThermal`, °C).**

- `RE(linkam_goto(T, rate=10, lnp='Auto', settle=300))` sets the temperature and waits
  until it is within `tol`. It never hangs on the IOC.
- On timeout it warns and continues, and the names carry the real T. Pass
  `on_timeout='raise'` to stop instead.
- `run_gi_temperatures(TEMPS, ...)` re-aligns at each T, starting each sample from its
  previous alignment (the alignment scans are relative). It prints the drift, and if a
  re-alignment fails it keeps the previous values. Each T's alignment is saved as
  `alignment_<experiment>_T<T>C_latest.json`.
- The timeout counts only the time spent waiting for T; a pause or a beam-dump suspension
  does not use it up.
- Transmission vs T: `run_trans(..., T=LThermal.temperature_current)` puts the T read at each
  frame in its name; `run_series(..., T=LThermal.temperature_current)` adds the time track
  (`2026C3_Murray.py`: `measure_T`, `track_T`, `run_T_list`).

**In situ and EC.**

- `ec_start()` (or `series_start()`) sets t = 0.
- `run_series` / `run_ec` repeat cycles over the samples. Each cycle moves to a fresh spot
  (`spots=`), and `swaxs_every=N` adds a periodic arc-20 frame with WAXS + SAXS.
- The potential in the name comes from, in order:
  1. an analog readback, `EC['readback']` (e.g. `moxa_out.chN_read`, the Moxa analog
     input), times `EC['scale']`
  2. a programmed schedule, `EC['schedule'] = [(t_s, V), ...]`
  3. `ec_set_potential(V)`; during a run use Ctrl-C, then `ec_set_potential(V)`, then
     `RE.resume()`
- The elapsed time, T and E in a name are read just before the exposure. After a pause or a
  beam-dump suspension the frame is taken later than its name says. For exact EC timing use
  the event timestamp minus `user_hints.series_t0`.

**Multi-cell holder.** A bar is a rows × cols grid. Its Huber position goes in `base`, and
the cells are placed on the piezo from 3 measured cells (A01, the end of row A, the start
of the last row), so rotation and pitch errors are absorbed. Names come from a
`cell,sample` CSV; unnamed cells are skipped.

## Beamline procedures (from the 2025–2026 runs)

**Vacuum chamber (air → vacuum)**

1. `RE(shclose())`
2. On CSS, "Vent WAXS Sample Chamber".
3. Open the hutch (SBE Access, then Open).
4. Open the chamber when 1:WAXS 2:TCG:9 reads about 780–800.
5. Load the holder or Linkam on the piezo, then close the chamber.
6. On CSS, "Auto Evacuation".
7. Search and close the hutch.
8. When the B1:WAXS LED turns green, open 2GV-7.
9. `RE(startWAXS())`, then `RE(shopen())`.

To go back to air: close 2GV-7, open the valve by hand, remove the window, and close the
valve again.

**Linkam + LN2 in vacuum**

1. Connect the controller to the small computer upstream of the chamber with the white
   USB cable.
2. Connect the controller to the LN2 pump with the instrument pin cable, and run the
   data/control pin cable through the feedthrough port.
3. Route the two LN2 tubes through the main port of the feedthrough pad (two clamps).
   Run the pump tubing to the small port.
4. Connect the tubes to the stage. The GI stage mounts directly on the piezo.
5. Power the controller and the LN2 pump.
6. Reboot the IOC: CSS `XF:12ID-ES{LINKAM}:SysReset`.
7. Watch the LN2 level during long series.

**WAXS**

- WAXS beamstop at arc 0 should be at −54.8. Its X motor has been unplugged since
  2026-06 (arc 0 or ≥ 14.5° only), so `RE(bps.mv(waxs, 0))` moves the arc alone. If the
  beamstop is off:
  1. In the hutch, push the beamstop base to the inboard limit.
  2. On SmarAct, home forward.
  3. Check the beamstop with beam and attenuators in.
- WAXS detector IOC restart: in the terminal select WAXS, press Ctrl-X and wait about
  2 min.

**Other**

- Detector threshold at 16.1 keV: `setthreshold energy 16100 autog 11000`.
- If the gap is off: `energy.move(16100)` (eV).
- After moving the SAXS beamstop: `beamstop_save()`.
- Jupyter on the beamline: `ssh -NL 8888:localhost:8888 yuzhang@xf12id2-srv1`.

## Old → new

| Old (archive) | New |
|---|---|
| `sample_dict`, `pxy_dict`, `x_list`, `sample_list` | `SAMPLES = make_samples(NAMES, POS)` |
| `align_gix_loop_samples()` → `Aligned_Dict[ii]` | `align_gi_samples()` → saved JSON, `load_alignment()['S1']` |
| `run_gix_loop_wsaxs(Aligned_Dict=...)` | `RE(run_gi(angles=..., arcs=...))` (latest saved alignment) |
| `measure_multi_waxs_loop_angles()` | `RE(run_trans(arcs=(0, 20)))` |
| `measure_saxs/waxs/wsaxs(t, sample=...)` | `RE(measure_saxs('name', t))` etc. |
| `collect_data_atT`, `Temperature_Linkam_*`, `run_Linkam_Tseries` | `RE(run_gi_temperatures(TEMPS))` |
| `insitu_tgix_samples`, `NanoSyn.run`, Karen's `continous_run_*` | `RE(run_series(...))`, `RE(run_ec(...))` |
| `get_motor()` / `motor='pizeo'` | `stage='piezo'` or `'huber'` per call |
| `sample_id(...)`; bare `det_exposure_time(t, t)` (a no-op now) | handled inside `expose()` |

## Data reduction

The pySAXSAI notebooks for this cycle will live in
`/nsls2/users/yuzhang/Transfer/XSacttering/2026_3/SMI`; the 2026_2 ones are the template.
The names above work with the pySAXSAI SMI parsers as they are: SAXS `_x` grouping, the
WAXS arc and condition keys, GI `deg`, `_T..C_`, and the in-situ series pattern.

For the pyScattViz org of SMI `Results/`, use the `products` layout with:

```
^(?P<sample>.+?)(?:_(?P<th>\d+\.\d+)deg)?(?:_(?P<index>\d+)_(?P<elapsed_s>\d+(?:\.\d+)?)s)?_x(?P<x>-?\d+(?:\.\d+)?)(?:.*?_T(?P<T_C>-?\d+(?:\.\d+)?)C_)?.*?_expt(?P<exposure_s>\d+(?:\.\d+)?)s.*_id(?P<scan>\d+)_(?P<frame>\d+)
```

No parser reads the `_E..V` potential yet. It is in the name and in
`user_hints.potential_V`.

## Tests

The simulation tests use fake devices with the beamline names. They load the base and
the experiment scripts and run their flows; nothing touches EPICS:

```
cd CFN/Yugang
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /nsls2/conda/envs/2025-3.0-py312-tiled/bin/python -m pytest -q -p no:cacheprovider tests
```

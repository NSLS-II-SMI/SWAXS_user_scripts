"""
bar_plans.py -- ready-to-run bar plans driven by the Redis-backed holder store.

Each plan takes the HOLDER NAME and the PROJECT NAME as its two main inputs, builds the bar
from Redis (so there is nothing to copy/paste and a crash never loses alignment), and runs.

    from bar_plans import transmission_bar_grid, transmission_bar_energies, giwaxs_bar_energy

    RE(transmission_bar_grid("OPV_bar_1", "NR_OPV"))
    RE(transmission_bar_energies("OPV_bar_1", "NR_OPV", energies=[2470, 2475, 2480, 2482, 2485]))
    RE(transmission_bar_energies("OPV_bar_1", "NR_OPV", energies="S_K_XANES"))   # named list
    RE(giwaxs_bar_energy("OPV_bar_1", "NR_OPV",
                         incident_angles=[0.08, 0.12, 0.16],
                         energies=[2470, 2475, 2478, 2480, 2482, 2485, 2490]))

All three:
  * position each sample from its stored coordinates,
  * record energy / WAXS-arc / incident-angle into the data (so the file name can template them),
  * print a friendly "what is running" line per sample.

This is a THIN wrapper over the ``smi_plans`` backend: the holder loading, alignment persistence,
energy stepping, spatial grid, and positioning all live there now (this file only carries the scan
*structure* + friendly prints).  ``energies`` / ``incident_angles`` / ``waxs_arc`` accept either an
explicit list OR the NAME of a stored list (resolved via ``smi_plans.resolve_list``).

Requires the live beamline session (devices pil2M/pil900KW/piezo/stage/energy/waxs/... and
det_exposure_time/alignment_gisaxs in the namespace) and a CURRENT ``smi_plans`` install
(needs ``load_holder``/``resolve_list``/the gutted ``energy_axis``/``spatial_grid_axes(center=)``;
deploy the updated smi-plans into the beamline env before running this).
"""



'''
2026/6/29 1:00 pm
Samples:
UConn, Prof. Gao Group
Jose

Sample holder 1: 45 samples
From S1 - S45
Using Eliot's new data acq software
pass-318919

317437	Standard	Approved	GU-318919: Autonomous Fluidic Synthesis of Cu-Based Colloidal Nanocrystals with Real-Time SAXS/WAXS/ASAXS/XAS: Correlating Processing, Electronic State, and Structure	Hyeong Jin Kim	

RE(shopen())
RE(restartWAXS())
proposal_swap(318919)
project_set('calibration')
sample_id(user_name='EG', sample_name=f'AGB')
set_energy(en_ev=16150)
RE(det_exposure_time(1,1))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.mv(waxs,15))
RE(bps.mv(waxs,15))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(bp.count([pil2M,pil900KW,pin_diode]))
RE(shclose())
RE.md
%run -i /home/xf12id/SWAXS_user_scripts/bar_plans.py
%run -i /home/xf12id/SWAXS_user_scripts/bar_plans.py
summarize_plan(transmission_bar_grid('holder1',None,waxs_arc=(0,20,40),nx=1,ny=1))
RE(transmission_bar_grid('holder1',None,waxs_arc=(0,20,40),nx=1,ny=1))
RE.stop()
RE(shopen())
RE(transmission_bar_grid('holder1',None,waxs_arc=(0,20,40),nx=1,ny=1))
RE.stop()
RE(bps.mv(waxs,0))
RE(bps.mv(waxs,0))
RE(transmission_bar_grid('holder1',None,waxs_arc=(15,35),nx=1,ny=1))
%run -i /home/xf12id/SWAXS_user_scripts/bar_plans.py
RE.abort()


data are saved in 
/nsls2/data/smi/proposals/2026-2/pass-318919/projects

sample info are through Eliot's webgui
http://localhost:5098/acquire_app



RE(transmission_bar_grid('holder1','PGao',waxs_arc=(15,25,35),nx=1,ny=1))

%run -i /home/xf12id/SWAXS_user_scripts/bar_plans.py


RE(transmission_bar_grid('holder1','PGao',waxs_arc=(15,35),nx=1,ny=1,name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x}", "
                                               ⋮ py_{piezo_y}, pz_{piezo_z}"],'name_prefix':'','include_exposure':True}))

                                               

RE(transmission_bar_grid('holder1','PGao',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))



RE(transmission_bar_grid('WL_Holder1','YZhang',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'YZhang','include_exposure':True}))


RE(transmission_bar_grid('WL_Holder1','YZhang',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'YZhang','include_exposure':True}))

RE(transmission_bar_grid('Holder3','PGao',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))

RE(transmission_bar_grid('Holder3','PGao',waxs_arc=(25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))

RE(transmission_bar_grid('Holder3','PGao',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))


RE(transmission_bar_grid('holder4','PGao',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))
 
RE(transmission_bar_grid('holder5','PGao',waxs_arc=(15, 25, 35),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))



RE(transmission_bar_grid('holder5','PGao',waxs_arc=(0,),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))


RE(transmission_bar_grid('holder4','PGao',waxs_arc=(0,),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Gao','include_exposure':True}))







RE(transmission_bar_grid('SY_H1','SYang',waxs_arc=(0,15, 25, 35 ),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'SYang','include_exposure':True}))



RE(transmission_bar_grid('AgBH_H1','Standard',waxs_arc=(0,15, 25, 35 ),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'Standard','include_exposure':True}))




RE(transmission_bar_grid('ChemH1','WaterOxidation',waxs_arc=(0,15, 25, 35 ),nx=1,ny=1,
name_spec={'include_energy':False,"arc_fmt": "waxs_{:.0f}","extra_tokens": ["px_{piezo_x:.1f}", "py_{piezo_y:.1f}", "pz_{piezo_z:.1f}"],
'name_prefix':'ChemH1','include_exposure':True}))



'''










import bluesky.plan_stubs as bps

from smi_plans._compose import acquire, acquire_bar, incidence_axis, energy_axis, spatial_grid_axes
from smi_plans._core import goto_sample
from smi_plans._preprocessors import fresh_spot_wrapper
from smi_plans import (load_holder, get_aligned, needs_alignment, save_aligned,
                       sample_center, resolve_list)
# Technique bars used by the ultra-thin rewrites at the bottom of this file (reference versions).
from smi_plans.technique_E_transmission import transmission_bar
from smi_plans.technique_A_energy_edge import nexafs_bar
import numpy as np


# ---------------------------------------------------------------------------
# Pull the live beamline device globals into THIS module's namespace.
# ---------------------------------------------------------------------------
# A function resolves bare names (energy, waxs, piezo, ...) against the module it was DEFINED in
# -- i.e. this file's globals -- NOT the IPython namespace it is called from.  So `%run` alone
# leaves these undefined inside the functions below (NameError).  The profile's startup.py does
# the same "inject devices into the module dict" trick for the smi_plans package; we do it here
# for this user script.  Runs at import/%run time, when the console already has the devices.
def _pull_beamline_globals():
    try:
        from IPython import get_ipython
        ns = get_ipython().user_ns
    except Exception:
        return
    for _name in ("energy", "waxs", "piezo", "stage",
                  "pil2M", "pil900KW", "pin_diode", "xbpm2", "xbpm3",
                  "det_exposure_time", "alignment_gisaxs", "Signal", "SMI"):
        if _name in ns:
            globals()[_name] = ns[_name]


_pull_beamline_globals()


# ---------------------------------------------------------------------------
# shared defaults
# ---------------------------------------------------------------------------
ARC_SAXS_BLOCK_DEG = 30 # 15        # below this WAXS arc angle pil2M (SAXS) is blocked -> don't read it


def _dets_at_arc(arc_value, *, use_saxs=True, use_waxs=True):
    # OUTDATED: detector selection now belongs in smi_plans helpers / the clean root bar_plans.py.
    # Keep this copy only as historical beamtime notes.
    """WAXS always (if wanted); SAXS only when the arc isn't blocking it.

    (``use_*`` names so they don't shadow the ``waxs`` device global.)"""
    d = []
    if use_waxs:
        d.append(pil900KW)                                  # noqa: F821
    if use_saxs and arc_value >= ARC_SAXS_BLOCK_DEG:
        d.append(pil2M)                                     # noqa: F821
    return d


def _grid_offsets(nx, ny, dx, dy):
    # OUTDATED: root bar_plans.py now keeps only a small example wrapper around smi_plans.
    """Absolute-ish offset lists: nx by ny points centered on 0, spacing dx/dy (microns)."""
    xs = (np.arange(nx) - (nx - 1) / 2.0) * dx if nx > 1 else np.array([0.0])
    ys = (np.arange(ny) - (ny - 1) / 2.0) * dy if ny > 1 else np.array([0.0])
    return list(xs), list(ys)


def _grid_axes(cx, cy, ox, oy, *, snake=True):
    # OUTDATED: use smi_plans._compose.spatial_grid_axes(center=...) directly.
    """Spot-grid axes centered on ``(cx, cy)`` that record relative ``{x}``/``{y}`` tokens.

    Thin wrapper over the backend ``spatial_grid_axes(center=...)`` (which records a relative-offset
    Signal named ``x``/``y`` so the filename tokens ``{x}``/``{y}`` resolve -- the absolute positions
    are ``cx + ox`` / ``cy + oy``).
    """
    return spatial_grid_axes(
        x_motor=piezo.x, x=[cx + d for d in ox],            # noqa: F821 (absolute positions)
        y_motor=piezo.y, y=[cy + d for d in oy],            # noqa: F821
        center=(cx, cy), snake=snake)


def _goto_grazing(s):
    # OUTDATED: use smi_plans._core.goto_sample(..., skip={piezo.y, piezo.th}) directly.
    """Move a GIWAXS sample's coarse position EXCEPT piezo.y/th (those come from alignment).

    Uses the backend ``goto_sample`` (reads the runnable nominal/refined Position) with the
    alignment-owned piezo y/th skipped."""
    yield from goto_sample(s, skip={piezo.y, piezo.th})     # noqa: F821

# ===========================================================================
# 1) Pure transmission, a grid of spots around each sample (no alignment, no angles)
# ===========================================================================
def transmission_bar_grid(holder_name, project, *, t=1.0,
                          waxs_arc=(0,),
                          nx=3, ny=3, dx=150.0, dy=150.0,
                          use_saxs=True, use_waxs=True, store=None):
    # OUTDATED: use /home/xf12id/SWAXS_user_scripts/bar_plans.py instead.  This copy predates the
    # smi_plans helper ingestion and is retained only as the Gao/Yugang beamtime command log.
    """ONE transmission run per (sample, WAXS arc): a ``nx`` x ``ny`` grid of spots around each
    sample center, repeated at each WAXS arc angle.

    No alignment and no incident-angle handling -- straight transmission SAXS/WAXS.  The grid is
    centered on the sample's stored ``piezo_x``/``piezo_y`` with spacing ``dx``/``dy`` microns.

    Parameters
    ----------
    holder_name, project : str
        The Redis holder name and the project name (-> ``md['project_name']``).
    t : float
        Exposure time (s).
    waxs_arc : sequence
        WAXS arc angle(s) to measure at (the arc is the OUTER loop, moved once per value).
        Default ``(0,)`` = a single arc.  Pass e.g. ``(0, 20)`` for two.
    nx, ny : int
        Grid points in x and y (1 => no walk in that axis).
    dx, dy : float
        Grid spacing in microns.
    use_saxs, use_waxs : bool
        Which detectors to use (arc-aware: SAXS dropped if the WAXS arc occludes it).
    """
    bar = load_holder(holder_name, store=store)
    n = len(bar)
    run_md = {"project_name": project}
    # NOTE: energy + waxs.arc are read into the primary stream automatically by the beamline's
    # default scan-naming preprocessor (for {energy_energy}/{waxs_arc}); do NOT also list them
    # here or trigger_and_read double-reads them -> 'Data keys ... collide'.
    reads = [xbpm2, xbpm3, pin_diode, piezo]                       # noqa: F821 (I0 + transmission + pos)
    ox, oy = _grid_offsets(nx, ny, dx, dy)
    arcs = list(waxs_arc)

    print(f"\n=== Transmission grid: holder {holder_name!r}, project {project!r}, "
          f"{n} samples, {nx}x{ny} spots/sample, arcs {arcs} ===")
    yield from det_exposure_time(t, t)                            # noqa: F821

    for arc_value in arcs:
        dets = _dets_at_arc(arc_value, use_saxs=use_saxs, use_waxs=use_waxs)
        print(f"\n=== WAXS arc = {arc_value} deg (dets: {', '.join(d.name for d in dets)}) ===")
        yield from bps.mv(waxs.arc, arc_value)                    # noqa: F821 (arc OUTER)
        yield from bps.sleep(1)
        for i, s in enumerate(bar, 1):
            cx, cy = sample_center(s)                            # from runnable Position (nominal/refined)
            if cx is None or cy is None:
                print(f"  !! Sample {i}/{n}: {s.name} has no x/y position in the store -- skipping")
                continue
            print(f"  >>> Sample {i}/{n}: {s.name}  @ arc {arc_value}  "
                  f"({nx}x{ny} spots @ x0={cx:.0f}, y0={cy:.0f})")
            yield from goto_sample(s)                          # move to the sample's stored position
            axes = _grid_axes(cx, cy, ox, oy)   # records {x}/{y} relative offsets
            yield from acquire(
                s.name, dets, axes,
                reads=reads, geometry="transmission", scan_name="transmission",
                sample=s, md=run_md,
                # {energy_energy}/{waxs_arc} go in the file name and are read ONCE by the naming
                # preprocessor; the plan itself does not read energy/waxs (avoids a collision).
                # {x}/{y} resolve to the relative-offset Signals recorded by spatial_grid_axes(center=...).
                name_tokens=(["{energy_energy:.1f}eV", f"wa{arc_value:04.1f}"]
                             + (["x{x}", "y{y}"] if nx * ny > 1 else [])),
                check_order=False)


# ===========================================================================
# 2) Transmission + a list of energies moved over (no alignment, no angles)
# ===========================================================================
def transmission_bar_energies(holder_name, project, *, energies, t=1.0,
                              waxs_arc=(0,),
                              nx=1, ny=1, dx=150.0, dy=150.0,
                              fresh_step=1.0,
                              use_saxs=True, use_waxs=True, store=None):
    # OUTDATED: use the clean root bar_plans.py wrapper.  Energy moves, holder loading,
    # fresh-spot behavior, and filename-token validation now come from smi_plans.
    """ONE transmission run per (sample, WAXS arc), stepping through ``energies`` (energy OUTER),
    optionally with a grid of spots per energy, with a fresh-spot walk on ``piezo.y`` per frame.

    Like :func:`transmission_bar_grid` but adds an energy axis.  Energy is recorded so the file
    name can template ``{energy_energy}``.  (Large energy moves are managed by the beamline's
    energy-move preprocessor; nothing extra is needed here.)

    Beam-damage mitigation: after every recorded frame ``piezo.y`` is nudged by ``fresh_step``
    microns (default 1) so each energy point lands on fresh sample; ``piezo.y`` is returned to
    its start when each run finishes.  (Disabled automatically if you request a y-grid
    ``ny > 1``, since the grid already moves ``piezo.y``.)

    Parameters
    ----------
    holder_name, project : str
        Redis holder name and project name.
    energies : sequence
        Photon energies (eV), in visiting order.
    t : float
        Exposure time (s).
    waxs_arc : sequence
        WAXS arc angle(s); the arc is the OUTER loop (moved once per value).  Default ``(0,)``.
    nx, ny, dx, dy : grid (default 1x1 = single spot per energy).
    fresh_step : float
        piezo.y step (microns) after each recorded frame (fresh spot; default 1).  Set to 0 (or
        use a y-grid ``ny > 1``) to disable.
    use_saxs, use_waxs : bool
        Detector selection.
    """
    bar = load_holder(holder_name, store=store)
    n = len(bar)
    run_md = {"project_name": project}
    reads = [xbpm2, xbpm3, pin_diode, piezo]                       # noqa: F821 (I0 + transmission + pos)
    energies = resolve_list(energies, kind="energy")              # accept a list OR a named list
    ox, oy = _grid_offsets(nx, ny, dx, dy)
    arcs = list(waxs_arc)
    # Fresh-spot on piezo.y, unless a y-grid already moves y (ny > 1) or it's turned off.
    do_fresh = bool(fresh_step) and ny <= 1
    fresh_note = f", fresh-spot y {fresh_step:+g}um/frame" if do_fresh else ""

    print(f"\n=== Transmission + energy: holder {holder_name!r}, project {project!r}, "
          f"{n} samples, {len(energies)} energies ({energies[0]}..{energies[-1]} eV), "
          f"arcs {arcs}{fresh_note} ===")
    yield from det_exposure_time(t, t)                            # noqa: F821

    for arc_value in arcs:
        dets = _dets_at_arc(arc_value, use_saxs=use_saxs, use_waxs=use_waxs)
        print(f"\n=== WAXS arc = {arc_value} deg (dets: {', '.join(d.name for d in dets)}) ===")
        yield from bps.mv(waxs.arc, arc_value)                    # noqa: F821 (arc OUTER)
        yield from bps.sleep(1)
        for i, s in enumerate(bar, 1):
            cx, cy = sample_center(s)                           # from runnable Position (nominal/refined)
            if cx is None or cy is None:
                print(f"  !! Sample {i}/{n}: {s.name} has no x/y position in the store -- skipping")
                continue
            print(f"  >>> Sample {i}/{n}: {s.name}  @ arc {arc_value}  ({len(energies)} energies"
                  f"{'' if nx*ny == 1 else f', {nx}x{ny} spots/energy'})")
            yield from goto_sample(s)
            axes = [
                # energy outer (within the run). energy_axis steps energy with a plain
                # bps.mv(energy, E) -- the energy device keeps the IVU gap on the flux peak and
                # manages feedback/harmonic itself. (energy auto-read by the naming preprocessor.)
                energy_axis(energies, settle=2.0, record=False),
            ]
            # Only add the spot-grid axes when there's an ACTUAL grid (nx*ny > 1).  For a single
            # spot, goto_sample already positioned the sample; adding a 1-point grid would
            # re-home piezo.x/y to the center BEFORE EVERY energy step, which fights (and cancels)
            # the fresh-spot y-walk -- the bug where every step lands back at start + one nudge.
            if nx * ny > 1:
                axes += _grid_axes(cx, cy, ox, oy)  # records {x}/{y} rel offsets
            run = acquire(
                s.name, dets, axes,
                reads=reads, geometry="transmission", scan_name="transmission_energy",
                sample=s, md=run_md,
                # {energy_energy}/{waxs_arc} go in the file name and are read ONCE by the naming
                # preprocessor; the plan itself does not read energy/waxs (avoids a collision).
                # {x}/{y} resolve to the relative-offset Signals recorded by spatial_grid_axes(center=...).
                name_tokens=(["eV_{energy_energy}", f"waxs_{arc_value:04.1f}", 'px_{px:.1f}', 'py_{py:.1f}', 'pz_{}' ]
                             + (["x{x}", "y{y}"] if nx * ny > 1 else [])),
                check_order=False)
            if do_fresh:
                run = fresh_spot_wrapper(run, piezo.y, fresh_step)   # noqa: F821 (1um/frame on y)
            yield from run


# ===========================================================================
# 3) Grazing incidence at N angles + energy scan, with the fresh-spot walk
# ===========================================================================
def giwaxs_bar_energy(holder_name, project, *,
                      incident_angles=(0.08, 0.12, 0.16),
                      energies, t=1.0,
                      waxs_arc=(0, 20), align_arc=20,
                      align_angle=0.15, realign=False,
                      fresh_step=-100.0, use_saxs=True, use_waxs=True, store=None):
    # OUTDATED: use the clean root bar_plans.py wrapper.  Alignment persistence and the GIWAXS
    # energy/incidence axes have been moved into smi_plans-backed examples.
    """Grazing-incidence energy scan over a bar at one or more WAXS arc angles.

    Aligns each sample ONCE (at ``align_arc``; cached/persisted to Redis -- skipped on re-run
    unless ``realign=True``), then for each WAXS arc (OUTER) and each sample, steps energy x
    incident angle, walking to a fresh spot per frame.  One run per (sample, arc).

    Alignment is read from / written to Redis (``holder_bar``), so a crash + restart costs no
    alignment time.  The aligned theta-zero is the sample tilt and is independent of the WAXS
    arc, so a single alignment is reused at every measured arc.

    Parameters
    ----------
    holder_name, project : str
        Redis holder name and project name.
    incident_angles : sequence
        Grazing incidence angles (deg), relative to each sample's aligned theta-zero.
    energies : sequence
        Photon energies (eV), in visiting order (energy is the OUTER axis within each run).
    t : float
        Exposure time (s).
    waxs_arc : sequence
        WAXS arc angle(s) to MEASURE at (the arc is the outermost loop).  Default ``(0, 20)``.
    align_arc : float
        WAXS arc position used for the one-time alignment pass (default 20).
    align_angle : float
        Angle passed to ``alignment_gisaxs``.
    realign : bool
        If True, re-align every sample even if a cached alignment exists.
    fresh_step : float
        piezo.x step (microns) after each recorded frame (fresh spot; negative walks "down").
    use_saxs, use_waxs : bool
        Detector selection (arc-aware: SAXS dropped at low arc where it is blocked).
    """
    bar = load_holder(holder_name, store=store)
    n = len(bar)
    run_md = {"project_name": project}
    energies = resolve_list(energies, kind="energy")             # accept a list OR a named list
    ais = resolve_list(incident_angles, kind="incidence")        # accept a list OR a named list
    arcs = list(waxs_arc)
    reads = [xbpm2, xbpm3, piezo]                                 # noqa: F821 (I0 + pos; energy/waxs auto-read by naming preprocessor)

    # --- 1) PRE-pass: align each sample ONCE at align_arc (skip if cached); persist th + y. ---
    print(f"\n=== GIWAXS energy scan: holder {holder_name!r}, project {project!r}, {n} samples ===")
    print(f"    aligning at WAXS arc = {align_arc} deg, then measuring arcs {arcs} "
          f"({len(ais)} angles x {len(energies)} energies per sample per arc)")
    yield from bps.mv(waxs.arc, align_arc)                       # noqa: F821
    yield from bps.sleep(1)
    for i, s in enumerate(bar, 1):
        if needs_alignment(s, force=realign):
            print(f"  [align {i}/{n}] {s.name} ...")
            yield from goto_sample(s)                          # move to the sample's stored position
            yield from alignment_gisaxs(align_angle)             # noqa: F821 (aligns piezo.th + piezo.y)
            yield from save_aligned(bar, s, piezo.th.position, piezo.y.position)   # noqa: F821
        else:
            th0, y0 = get_aligned(s)
            print(f"  [skip  {i}/{n}] {s.name}: already aligned (th0={th0:.4f}, y={y0:.1f})")

    yield from det_exposure_time(t, t)                           # noqa: F821

    # --- 2) Measure: WAXS arc OUTER, sample, then energy x incident angle (fresh-spot walk). ---
    for arc_value in arcs:
        dets = _dets_at_arc(arc_value, use_saxs=use_saxs, use_waxs=use_waxs)
        print(f"\n=== Measuring at WAXS arc = {arc_value} deg "
              f"(dets: {', '.join(d.name for d in dets)}) ===")
        yield from bps.mv(waxs.arc, arc_value)                   # noqa: F821 (arc OUTER)
        yield from bps.sleep(1)
        for i, s in enumerate(bar, 1):
            th0, y0 = get_aligned(s)
            print(f"  >>> Sample {i}/{n}: {s.name}  @ arc {arc_value}  (th0={th0:.4f}, "
                  f"{len(energies)} energies x {len(ais)} angles)")
            # coarse x/z + full stage (NOT piezo.y/th -- those are alignment-owned), then the
            # aligned height; backend goto_sample(skip=...) reads the runnable Position.
            yield from _goto_grazing(s)                         # noqa: F821 (x/z/stage, skip y/th)
            yield from bps.mv(piezo.y, y0)                      # noqa: F821 (aligned height)
            axes = [
                # energy_axis: plain bps.mv(energy, E); the energy device keeps the IVU gap on the
                # flux peak + manages feedback/harmonic (no gap freeze/accumulate needed).
                energy_axis(energies, settle=2.0, record=False),
                incidence_axis(piezo.th, th0, ais),             # noqa: F821 (anchored at aligned zero)
            ]
            yield from fresh_spot_wrapper(
                acquire(
                    s.name, dets, axes,
                    reads=reads, geometry="reflection", scan_name="giwaxs_energy",
                    sample=s, md=run_md,
                    # These {tokens} go in the file name AND tell the naming preprocessor which
                    # devices to read once into the stream (energy/waxs_arc); the plan itself must
                    # NOT also read energy/waxs (it doesn't -- see reads + energy axis record=False)
                    # or trigger_and_read would double-read them ('Data keys ... collide').
                    name_tokens=["{energy_energy}eV", "ai{incident_angle}", f"wa{arc_value:04.1f}"],
                    check_order=False),
                piezo.x, fresh_step)                             # noqa: F821


# ###########################################################################
# ULTRA-THIN REWRITES (reference) -- "if we fully accept the smi_plans calls"
# ###########################################################################
# The three functions above keep the field-tuned scan STRUCTURE in this file (arc-as-outer loop,
# arc-aware SAXS drop, friendly prints, skip-if-no-position).  Below is the OTHER extreme: the
# smallest call that delegates everything to the smi_plans technique bars.  These are kept as a
# REFERENCE to show the potential reduction -- the originals above remain the working versions.
#
# What you GAIN by going thin: ~1 line of intent per plan; one place (the backend) owns the idioms.
# What you GIVE UP vs the originals (so you can decide per plan):
#   * per-arc SAXS drop (ARC_SAXS_BLOCK_DEG): the bars take a fixed `dets`, not arc-aware.  (To keep
#     it, pass dets per call, or measure low/high arcs in separate calls with different dets.)
#   * the friendly per-sample prints + "skip sample with no stored x/y".
#   * the relative {x}/{y} filename tokens: the transmission bar records absolute {piezo_x}/{piezo_y}.
#   * #3 (GIWAXS x energy x incidence over a holder) has NO single backend bar yet -- see note below.


def transmission_bar_grid_thin(holder_name, project, *, t=1.0, waxs_arc=(0,),
                               nx=3, ny=3, dx=150.0, dy=150.0, store=None):
    # OUTDATED REFERENCE: kept only to show the migration direction during the beamtime.
    """Thin: ONE transmission run per (sample, arc), nx*ny spot grid.  == transmission_bar_grid.

    Maps directly onto smi_plans.technique_E.transmission_bar:
      * holder -> SampleList via load_holder
      * grid   -> points_fast/points_slow + d_fast/d_slow (piezo.y fast, piezo.x slow)
      * arcs   -> waxs_arc (swept OUTERMOST, one run per (sample, arc))
    """
    yield from transmission_bar(
        load_holder(holder_name, store=store),
        t=t, waxs_arc=list(waxs_arc),
        points_fast=ny, points_slow=nx, d_fast=dy, d_slow=dx,
        md={"project_name": project})


def transmission_bar_energies_thin(holder_name, project, *, energies, t=1.0, store=None):
    # OUTDATED REFERENCE: root bar_plans.py now shows the supported clean examples.
    """Thin: transmission energy sweep over a bar (single spot/sample).  ~= transmission_bar_energies.

    Maps onto smi_plans.technique_A.nexafs_bar (an energy axis per sample, one run each).
    `energies` accepts a list OR a stored-list name (resolve_list).
    NOTE: nexafs_bar does up+down by default and does NOT sweep waxs.arc or do the per-energy
    fresh-spot y-walk -- if you need those, use the structured transmission_bar_energies above.
    """
    yield from nexafs_bar(
        load_holder(holder_name, store=store),
        resolve_list(energies, kind="energy"),
        t=t, geometry="transmission",
        md={"project_name": project})


def giwaxs_bar_energy_thin(holder_name, project, *, incident_angles=(0.08, 0.12, 0.16),
                           energies, align=None, align_angle=0.15, waxs_arc=(0, 20),
                           fresh_step=-100.0, store=None):
    # OUTDATED REFERENCE: root bar_plans.py now shows the supported clean example.
    """Thin-ish: GIWAXS x energy x incidence over a bar.  ~= giwaxs_bar_energy.

    There is NO single backend bar that does energy x incidence x arc over a holder (technique_B
    giwaxs_bar measures incidence x arc but NOT energy).  So this composes the backend axes via
    acquire_bar -- still far thinner than the structured original, but it needs an `align` callable
    (e.g. alignement_gisaxs_hex) and uses acquire_bar's own per-sample goto/align hooks.

    This is the honest "closest thin form"; if/when a backend giwaxs_energy_bar lands, this becomes
    a one-liner like the two above.
    """
    bar = load_holder(holder_name, store=store)
    es = resolve_list(energies, kind="energy")
    ais = resolve_list(incident_angles, kind="incidence")

    def axes_for(s):
        th0, _y = get_aligned(s)
        return [energy_axis(es, settle=2.0, record=False),
                incidence_axis(piezo.th, th0, ais)]                 # noqa: F821

    for arc_value in waxs_arc:                                      # arc OUTER, one run per (s, arc)
        yield from bps.mv(waxs.arc, arc_value)                     # noqa: F821
        yield from bps.sleep(1)
        yield from acquire_bar(
            bar, _dets_at_arc(arc_value), axes_for,
            reads=[xbpm2, xbpm3, piezo],                           # noqa: F821
            geometry="reflection", scan_name="giwaxs_energy",
            name_tokens=["{energy_energy}eV", "ai{incident_angle}", f"wa{arc_value:04.1f}"],
            md={"project_name": project}, check_order=False)

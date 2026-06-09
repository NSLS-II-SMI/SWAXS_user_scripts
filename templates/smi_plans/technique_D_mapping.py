"""
technique_D_mapping
==================

Archetype D -- Microfocus / raster spatial mapping (line / 2D grid / spiral).

Map a heterogeneous sample (tissue, fibers, films, gratings, printed parts) with a microbeam
over an x/y (or x/z) grid, line, or spiral.  This is the **"best legacy" tier**: it already
uses *coordinated* Bluesky scan plans (``bp.rel_grid_scan`` / ``bp.rel_scan`` / ``bp.rel_spiral``)
so each map is ONE run with the scanned positions recorded automatically as event fields.  The
only modernization needed is (1) build the filename from those recorded fields (``{piezo_x}``,
``{piezo_y}``) via ``md={'sample_name': ...}`` rather than ``sample_id`` global state, and
(2) record transmission/OAV context *in the stream* instead of a ``db[-1].table()`` reach-back.

Gold reference: ``Commissioning/microlistscan.py`` (the modern ``grid_scan`` /
``list_scan`` form with ``md={'sample_name': name+'_x{piezo_x}_y{piezo_y}'}``) and
``nist/aiello`` ``run_nist_linescans`` / ``_grids`` / ``_spirals`` (line/grid/spiral idioms,
arc-aware dets, transmission, ``OAV_writing``).

What this file gives you
------------------------
* :func:`map_line_run`  -- ONE run, 1-D line scan (``bp.rel_scan`` on one fast axis).
* :func:`map_grid_run`  -- ONE run, 2-D raster (``bp.rel_grid_scan``); positions in-stream.
* :func:`map_spiral_run` -- ONE run, Archimedean spiral (``bp.rel_spiral``).
* :func:`map_grid_manual_run` -- ONE run via :func:`_core.one_sample_run` + explicit
  ``mv`` / ``trigger_and_read`` for when you need EXTRA per-point context (transmission,
  OAV, a verbal Signal) beyond what the coordinated scan records.
* :func:`map_bar` -- loop a chosen map plan over a :class:`SampleList` (one map-run/sample).
* :func:`example`, :func:`example_manual` -- runnable examples.

Idioms preserved: arc-conditional detector lists (SAXS dropped when the WAXS arc occludes it),
``OAV_writing`` on-axis snapshot, live transmission via ``pin_diode`` recorded in-stream,
fresh sample positioning per map, baseline capture of the SDD.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bp`` (bluesky.plans), ``Signal``, ``piezo``,
    ``stage``, ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``,
    ``pin_diode``, ``pil2M_pos``, ``det_exposure_time``, and optionally ``OAV_writing``.
"""

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, saxs_waxs_dets, fname, merge_md)
from ._preprocessors import baseline_wrapper, cleanup_wrapper

try:
    import bluesky.plan_stubs as bps
    import bluesky.plans as bp
except Exception:  # pragma: no cover
    bps = None
    bp = None


__all__ = [
    "map_dets", "map_line_run", "map_grid_run", "map_spiral_run",
    "map_grid_manual_run", "map_bar", "example", "example_manual",
]


# ---------------------------------------------------------------------------
# Detector selection for maps
# ---------------------------------------------------------------------------
def map_dets(*, saxs=True, waxs=True, transmission=False, oav=False, arc_block_deg=15):
    """Arc-aware detector list for a map, optionally adding ``pin_diode`` and ``OAV_writing``.

    Reproduces the legacy ``[pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]`` plus
    the Aiello ``dets.append(OAV_writing)`` habit -- but as an explicit helper.  When
    ``transmission`` is set, ``pin_diode`` is recorded *as a detector in the stream* (replacing
    the legacy ``db[-1].table()`` reach-back), so transmission is computed later from data.
    """
    dets = saxs_waxs_dets(use_saxs=saxs, use_waxs=waxs, arc_block_deg=arc_block_deg)
    if transmission:
        dets = dets + [pin_diode]                                     # noqa: F821 (global)
    if oav:
        try:
            dets = dets + [OAV_writing]                               # noqa: F821
        except Exception:
            pass
    return dets


def _map_baseline():
    """Default baseline for a map: the SDD if available."""
    try:
        return [pil2M_pos.z]                                          # noqa: F821 (SDD)
    except Exception:
        return []


def _map_md(name, scan_name, geometry, md, *, pos_tokens):
    """Build the run md with a filename templated from the scanned-position fields.

    ``pos_tokens`` are appended after ``name`` (e.g. ``("x{piezo_x}", "y{piezo_y}")``) so the
    per-point filename carries the *recorded* scan positions.  Caller md merges in; the
    ``sample_name`` template is authoritative (added last).
    """
    sample_name = fname(name, *pos_tokens)
    return merge_md(
        {"scan_name": scan_name},
        {"geometry": geometry} if geometry else {},
        md,
        {"sample_name": sample_name},
    )


# ---------------------------------------------------------------------------
# Thin coordinated-scan maps (one run each, positions recorded automatically)
# ---------------------------------------------------------------------------
def map_line_run(name, motor, start, stop, num, *, t=0.5, dets=None, geometry="transmission",
                 relative=True, transmission=False, oav=False, baseline=None, md=None,
                 pos_token=None):
    """ONE run: a 1-D line scan along ``motor`` (``bp.rel_scan`` / ``bp.scan``).

    The scanned ``motor`` position is recorded automatically by the scan, so the filename can
    reference ``{<motor_field>}`` (e.g. ``{piezo_y}``).  Mirrors Aiello ``run_nist_linescans``
    (``bp.rel_scan(dets, piezo.y, *y_range)``).

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    motor : ophyd positioner
        Fast axis to scan (e.g. ``piezo.y``).
    start, stop, num :
        Scan extent.  When ``relative`` these are offsets about the current position.
    t : float
        Exposure time (s).
    dets : list, optional
        Default :func:`map_dets` (arc-aware, +pin_diode/OAV per flags).
    relative : bool
        ``bp.rel_scan`` (offsets) vs ``bp.scan`` (absolute).
    transmission, oav : bool
        Add ``pin_diode`` / ``OAV_writing`` to the recorded detectors.
    baseline : list, optional
        Constants (default: SDD).  Recorded via ``baseline_wrapper`` around the scan.
    md : dict, optional
        Caller intent.
    pos_token : str, optional
        Filename token for the scanned position (default inferred from ``motor.name``).
    """
    if dets is None:
        dets = map_dets(transmission=transmission, oav=oav)
    if pos_token is None:
        pos_token = "{" + str(getattr(motor, "name", "pos")) + "}"
    if baseline is None:
        baseline = _map_baseline()

    det_exposure_time(t, t)                                           # noqa: F821
    run_md = _map_md(name, "map_line", geometry, md, pos_tokens=(pos_token,))

    scan = bp.rel_scan if relative else bp.scan
    plan = scan(dets, motor, start, stop, num, md=run_md)
    if baseline:
        plan = baseline_wrapper(plan, baseline)
    return (yield from plan)


def map_grid_run(name, m1, m1_start, m1_stop, m1_num, m2, m2_start, m2_stop, m2_num, *,
                 t=0.5, dets=None, geometry="transmission", relative=True, snake=True,
                 transmission=False, oav=False, baseline=None, md=None, pos_tokens=None):
    """ONE run: a 2-D raster over ``m1`` (outer/slow) x ``m2`` (inner/fast) via ``bp.rel_grid_scan``.

    The recommended modern mapping form: a single coordinated grid scan whose per-point
    positions are recorded as ``{m1_field}`` / ``{m2_field}``.  Mirrors Aiello
    ``run_nist_grids`` (``bp.rel_grid_scan(dets, piezo.x, *rx, piezo.y, *ry)``) and the
    ``microlistscan.py`` ``grid_scan(..., md={'sample_name': name+'_x{piezo_x}_y{piezo_y}'})``.

    Within the single run the per-point position changes, so a ``{piezo_x}`` token in the name
    resolves to the *scanned motor's recorded field*, giving a distinct filename per frame.

    Parameters
    ----------
    name : str
    m1, m1_start, m1_stop, m1_num :
        Outer (slow) axis and its extent.  Put the *slower* travel here.
    m2, m2_start, m2_stop, m2_num :
        Inner (fast) axis and its extent.
    snake : bool
        Serpentine the inner axis (``bp.rel_grid_scan(..., snake_axes=True)``) to avoid fly-back.
    pos_tokens : tuple of str, optional
        Filename tokens for the two scanned positions (default inferred from motor names, e.g.
        ``("x{piezo_x}", "y{piezo_y}")``).
    (others as in :func:`map_line_run`)
    """
    if dets is None:
        dets = map_dets(transmission=transmission, oav=oav)
    if pos_tokens is None:
        n1 = str(getattr(m1, "name", "m1"))
        n2 = str(getattr(m2, "name", "m2"))
        pos_tokens = ("{" + n1 + "}", "{" + n2 + "}")
    if baseline is None:
        baseline = _map_baseline()

    det_exposure_time(t, t)                                           # noqa: F821
    run_md = _map_md(name, "map_grid", geometry, md, pos_tokens=pos_tokens)

    grid = bp.rel_grid_scan if relative else bp.grid_scan
    plan = grid(dets, m1, m1_start, m1_stop, m1_num,
                m2, m2_start, m2_stop, m2_num, snake_axes=snake, md=run_md)
    if baseline:
        plan = baseline_wrapper(plan, baseline)
    return (yield from plan)


def map_spiral_run(name, x_motor, y_motor, x_range, y_range, dr, nth, *, t=0.5, dets=None,
                   geometry="transmission", relative=True, transmission=False, oav=False,
                   baseline=None, md=None, pos_tokens=None):
    """ONE run: an Archimedean spiral map via ``bp.rel_spiral``.

    Mirrors Aiello ``run_nist_spirals`` (``bp.rel_spiral(dets, piezo.x, piezo.y, x, y, dr, nth)``).
    Both scanned axes are recorded, so the filename can reference ``{piezo_x}`` / ``{piezo_y}``.

    Parameters
    ----------
    x_motor, y_motor : ophyd positioners
    x_range, y_range : float
        Spiral extent in each axis.
    dr : float
        Radial step between rings.
    nth : float
        Number of theta steps in the first ring.
    (others as in :func:`map_grid_run`)
    """
    if dets is None:
        dets = map_dets(transmission=transmission, oav=oav)
    if pos_tokens is None:
        nx = str(getattr(x_motor, "name", "x"))
        ny = str(getattr(y_motor, "name", "y"))
        pos_tokens = ("{" + nx + "}", "{" + ny + "}")
    if baseline is None:
        baseline = _map_baseline()

    det_exposure_time(t, t)                                           # noqa: F821
    run_md = _map_md(name, "map_spiral", geometry, md, pos_tokens=pos_tokens)

    spiral = bp.rel_spiral if relative else bp.spiral
    plan = spiral(dets, x_motor, y_motor, x_range, y_range, dr, nth, md=run_md)
    if baseline:
        plan = baseline_wrapper(plan, baseline)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Manual grid (one run, explicit mv/trigger_and_read) -- full per-point control
# ---------------------------------------------------------------------------
def map_grid_manual_run(name, m1, m1_positions, m2, m2_positions, *, t=0.5, dets=None,
                        reads=None, geometry="transmission", snake=True, transmission=True,
                        oav=False, extra_signals=None, baseline=None, md=None,
                        pos_tokens=None):
    """ONE run: a 2-D raster built by hand (``mv`` + ``trigger_and_read``) for extra context.

    Use this when the coordinated :func:`map_grid_run` does not give you enough per-point
    control -- e.g. you want to record live transmission (``pin_diode``), an OAV frame, and a
    verbal context ``Signal`` on *every* point, or step axes in a custom order.  Built on
    :func:`_core.one_sample_run`, so it shares the one-run-per-map + baseline + md machinery.

    The scanned motors are included in ``reads`` so their positions are recorded (the manual
    form does not auto-hint them the way ``grid_scan`` does), keeping ``{piezo_x}`` tokens valid.

    Parameters
    ----------
    name : str
    m1, m1_positions :
        Outer (slow) axis and the explicit list of absolute positions.
    m2, m2_positions :
        Inner (fast) axis and its explicit positions.
    reads : list, optional
        Extra readables each event (default ``[energy, waxs, xbpm2, xbpm3, m1, m2]``).
    snake : bool
        Serpentine the inner axis to avoid fly-back.
    transmission : bool
        Record ``pin_diode`` in-stream (the modern replacement for ``db[-1].table()``).
    extra_signals : list of ophyd Signal, optional
        Additional artificial Signals to record each point (e.g. a ``Signal('roi_label')``);
        reference them as ``{name_value}`` in ``pos_tokens``.
    pos_tokens : tuple of str, optional
        Filename tokens (default the two motor position fields).
    (others as in :func:`map_grid_run`)
    """
    if dets is None:
        dets = map_dets(transmission=transmission, oav=oav)
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3, m1, m2]                  # noqa: F821
    else:
        reads = list(reads) + [m1, m2]
    extra_signals = list(extra_signals or [])
    if pos_tokens is None:
        n1 = str(getattr(m1, "name", "m1"))
        n2 = str(getattr(m2, "name", "m2"))
        pos_tokens = ("{" + n1 + "}", "{" + n2 + "}")
    if baseline is None:
        baseline = _map_baseline()

    det_exposure_time(t, t)                                           # noqa: F821
    sample_name = fname(name, *pos_tokens)

    def _measure():
        if transmission:
            try:
                yield from bps.mv(pin_diode.averaging_time, t)       # noqa: F821
            except Exception:
                pass
        for j, p1 in enumerate(m1_positions):                        # outer/slow axis
            yield from bps.mv(m1, p1)
            inner_positions = m2_positions
            if snake and (j % 2 == 1):
                inner_positions = list(m2_positions)[::-1]
            for p2 in inner_positions:                               # inner/fast axis
                yield from bps.mv(m2, p2)
                yield from bps.trigger_and_read(
                    list(dets) + list(reads) + extra_signals)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="map_grid_manual", geometry=geometry,
                          md=md, baseline=baseline)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one map-run per sample)
# ---------------------------------------------------------------------------
def map_bar(samples, map_plan, *, md=None):
    """Run a per-sample map (ONE run per sample) for every sample on the bar.

    ``samples`` is a :class:`SampleList`.  ``map_plan`` is a callable
    ``map_plan(sample) -> plan`` that builds one of the ``map_*_run`` plans for a given sample
    (so the caller decides line vs grid vs spiral and the per-sample extents).  Each sample is
    coarse-positioned first; the map plan's own relative extents then apply about that origin.

    Example
    -------
    >>> def per_sample(s):
    ...     return map_grid_run(s.name, piezo.x, -250, 250, 11, piezo.y, -150, 150, 16,
    ...                         t=0.3, md=s.md)
    >>> yield from map_bar(bar, per_sample)
    """
    for s in samples:
        yield from goto_sample(s)
        yield from map_plan(s)


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """3-sample microfocus bar: a 2-D grid map per sample, transmission + OAV recorded.

    Each map is ONE ``rel_grid_scan`` run with ``{piezo_x}``/``{piezo_y}`` in the filename.
    Run with::

        RE(technique_D_mapping.example())
    """
    bar = SampleList.from_columns(
        names=["240_100_PP", "240_100_N1", "180_10_PP"],
        piezo_x=[43230, 33395, -9434],
        piezo_y=[-1035, -740, -170],
        md={"project_name": "311234_Demo"},
    )

    def per_sample(s):
        # 11 x 16 fine raster about the sample origin; SAXS auto-dropped if arc occludes.
        return map_grid_run(
            s.name, piezo.x, -250, 250, 11, piezo.y, -150, 150, 16,   # noqa: F821
            t=0.3, geometry="transmission", transmission=True, oav=True, md=s.md)

    yield from map_bar(bar, per_sample, md={"technique": "microfocus_map"})


def example_manual():
    """Single grid map with full per-point context (transmission + a verbal ROI label).

    Uses the manual form so every point records ``pin_diode`` and an artificial ``roi_label``
    Signal.  Run with::

        RE(technique_D_mapping.example_manual())
    """
    import numpy as np                                                # noqa: F811 (np global)
    roi = Signal(name="roi_label", value="tissue_A")                 # noqa: F821

    yield from goto_sample(SampleList.from_columns(
        names=["chiton_tooth"], piezo_x=[12000], piezo_y=[-900])[0])

    xs = list(np.linspace(11750, 12250, 11))
    ys = list(np.linspace(-1050, -750, 16))
    yield from map_grid_manual_run(
        "chiton_tooth", piezo.x, xs, piezo.y, ys, t=0.5,             # noqa: F821
        geometry="transmission", transmission=True, oav=True,
        extra_signals=[roi], pos_tokens=("x{piezo_x}", "y{piezo_y}", "{roi_label_value}"),
        md={"project_name": "311234_Demo", "specimen": "chiton_radula"})

"""
technique_E_transmission
=======================

Archetype E -- Transmission SAXS/WAXS (capillaries, wells, solution / bio bars).

Transmission-geometry scattering of solutions, suspensions, capillaries and well plates,
usually as a multi-sample "bar" with multi-spot averaging along each capillary and optional
quantitative transmission from a beamstop diode.  The legacy form computes transmission
*online* via a ``db[-1].table()`` reach-back into the previous run's stats and bakes the
result into the filename; here we instead **record ``pin_diode`` (and ``xbpm``) in the primary
stream** and leave the transmission ratio to be computed in analysis from recorded data.

**This file is a PRESET RECIPE built on the composition layer (``_compose``).**  The multi-spot
capillary average is just a (fast) spatial sampling concern: :func:`transmission_run` assembles
the serpentine dither as :func:`_compose.spatial_grid_axes` (slow dither axis outer, fast dither
axis inner) nested inside ONE :func:`_compose.acquire` per sample.  The spatial concern is
independent and freely combinable with others (energy, temperature, incidence); to mix them,
assemble the axes directly -- see ``recipes_combined.py`` and the README.

Gold reference: UVA ``Cai`` ``capillary_transmission_saxs.py`` (multi-spot capillary averaging,
direct-beam / sample transmission), ``templates/tranmission.py`` ``multi_transmission`` (the
serpentine x/y dither), Telles / Quan / Foster / Liu-Akron (quantitative T).

What this file gives you
------------------------
* :func:`transmission_dets` -- arc-aware detectors with ``pin_diode`` recorded in-stream.
* :func:`transmission_point` -- one event: ``trigger_and_read`` with ``pin_diode`` + ``xbpm``.
* :func:`transmission_run` -- ONE run per sample, optional multi-spot averaging by dithering
  ``piezo.x``/``piezo.y`` over a small grid INSIDE the single run (each spot an event).
* :func:`transmission_bar` -- loop :func:`transmission_run` over a :class:`SampleList`.
* :func:`example`, :func:`example_multispot` -- runnable examples.

Idioms preserved: multi-position averaging along a capillary (serpentine dither to spread
dose / average heterogeneity), arc-conditional detectors, baseline capture of the SDD.

Provenance note
---------------
The legacy ``stats1_sample / stats1_direct`` transmission computed from ``db[-1].table()`` is
**deliberately not reproduced**.  ``pin_diode`` (transmitted flux, token
``{pin_diode_current2_mean_value}``) and ``xbpm2``/``xbpm3`` (I0) are recorded as devices on
every event, so the transmission ratio is reconstructable from the data broker -- no online
reach-back, no value baked into a filename string.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``Signal``, ``piezo``, ``stage``, ``waxs``,
    ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pin_diode``, ``pil2M_pos``,
    ``att2_9``, ``det_exposure_time``.
"""

from ._samples import SampleList
from ._core import (goto_sample, saxs_waxs_dets, merge_md)
from ._compose import acquire, spatial_grid_axes
from ._preprocessors import (fresh_spot_wrapper, ensure_in_wrapper, cleanup_wrapper)

try:
    import bluesky.plan_stubs as bps
except Exception:  # pragma: no cover
    bps = None


__all__ = [
    "transmission_dets", "transmission_point", "transmission_run",
    "transmission_bar", "example", "example_multispot",
]


# ---------------------------------------------------------------------------
# Detector selection for transmission
# ---------------------------------------------------------------------------
def transmission_dets(*, saxs=True, waxs=True, arc_block_deg=15):
    """Arc-aware transmission detector list, always including ``pin_diode``.

    Reproduces the legacy ``[pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW,
    pin_diode]`` choice but always records ``pin_diode`` (the transmitted-flux diode) so the
    transmission can be computed offline from the stream.
    """
    dets = saxs_waxs_dets(use_saxs=saxs, use_waxs=waxs, arc_block_deg=arc_block_deg)
    return dets + [pin_diode]                                         # noqa: F821 (global)


def _spot_offsets(points_x, points_y, dx, dy, *, snake=True):
    """Build the list of (dx, dy) dither offsets for multi-spot averaging.

    A small serpentine raster (default) over the sample to spread dose and average
    heterogeneity along a capillary, generalizing the legacy ``for i in range(points):
    new_y = y + i*dy`` line and the ``multi_transmission`` x/y nest.
    """
    offsets = []
    for ix in range(int(points_x)):
        col = range(int(points_y))
        if snake and (ix % 2 == 1):
            col = reversed(range(int(points_y)))
        for iy in col:
            offsets.append((ix * dx, iy * dy))
    return offsets


# ---------------------------------------------------------------------------
# Inner per-spot measurement
# ---------------------------------------------------------------------------
def transmission_point(dets, reads, *, settle=0.0):
    """Record ONE transmission event (``pin_diode`` + ``xbpm`` are in ``dets``/``reads``).

    ``reads`` is the list of extra readables (beyond ``dets``); include ``xbpm2``/``xbpm3`` so
    ``{xbpm2_sumX}`` resolves and the I0 normalization is recorded.  ``pin_diode`` is expected
    to be in ``dets`` (see :func:`transmission_dets`) so ``{pin_diode_current2_mean_value}``
    resolves for the filename.
    """
    if settle:
        yield from bps.sleep(settle)
    yield from bps.trigger_and_read(list(dets) + list(reads))


# ---------------------------------------------------------------------------
# One run = one sample, optional multi-spot averaging
# ---------------------------------------------------------------------------
def transmission_run(name, *, t=1.0, dets=None, reads=None, geometry="transmission",
                     fast_axis=None, slow_axis=None, points_fast=1, points_slow=1,
                     d_fast=150.0, d_slow=0.0, snake=True, settle=0.0, dose_step=None,
                     atten_in=None, baseline=None, md=None,
                     name_tokens=("pd{pin_diode_current2_mean_value}", "bpm{xbpm2_sumX}")):
    """ONE run: a transmission measurement of one sample, with optional multi-spot averaging.

    All spots for one sample live in a SINGLE run; each dither position is one event with the
    transmitted flux (``pin_diode``) and I0 (``xbpm``) recorded.  The filename is templated
    from those recorded fields -- the transmission ratio itself is computed in analysis (see
    the provenance note in the module docstring).

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    t : float
        Exposure / averaging time (s).  Applied to detectors and ``pin_diode``.
    dets : list, optional
        Default :func:`transmission_dets` (arc-aware + ``pin_diode``).
    reads : list, optional
        Extra readables recorded each event.  Default ``[energy, waxs, xbpm2, xbpm3,
        piezo]`` -- ``piezo`` records the dithered spot position automatically.
    geometry : str
        Defaults to ``"transmission"``.
    fast_axis, slow_axis : ophyd positioners, optional
        Axes to dither for multi-spot averaging (default ``piezo.y`` fast, ``piezo.x`` slow --
        i.e. step along the capillary).  Only used when the corresponding ``points_*`` > 1.
    points_fast, points_slow : int
        Number of spots along each axis (1 = no dither on that axis).  ``points_fast=5,
        points_slow=1`` reproduces the classic 5-spot capillary average.
    d_fast, d_slow : float
        Spot spacing (microns for piezo).
    snake : bool
        Serpentine the dither to avoid fly-back.
    settle : float
        Sleep before each frame.
    dose_step : float, optional
        If given, additionally walk ``fast_axis`` by this step after every frame (extra fresh
        spot on top of the dither -- useful for beam-sensitive solutions).
    atten_in : callable() -> plan, optional
        Put attenuators/beamstop into the measurement configuration at run open.
    baseline : list, optional
        Constants (default: SDD ``pil2M_pos.z``).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename (must correspond to recorded fields).
    """
    if dets is None:
        dets = transmission_dets(saxs=True, waxs=True)
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3, piezo]                   # noqa: F821
    if fast_axis is None:
        fast_axis = piezo.y                                           # noqa: F821 (along capillary)
    if slow_axis is None:
        slow_axis = piezo.x                                           # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                                  # noqa: F821 (SDD)
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                           # noqa: F821

    # Record the dither origin so absolute spot positions reconstruct from origin + piezo read.
    x0 = slow_axis.position
    y0 = fast_axis.position

    # The multi-spot dither as compose axes: slow dither axis OUTER, fast dither axis INNER,
    # serpentined when `snake` -- this is exactly the legacy `_spot_offsets` serpentine raster
    # (slow varies outer, fast varies inner) re-expressed declaratively, over absolute
    # positions origin + i*step.  `record=False`: the parent ``piezo`` in `reads` already
    # records the dithered spot position (its sub-axes), so we keep the recorded fields
    # identical to the hand-rolled form rather than adding separate piezo.x/piezo.y reads.
    x_vals = [x0 + ix * d_slow for ix in range(int(points_slow))]
    y_vals = [y0 + iy * d_fast for iy in range(int(points_fast))]
    axes = spatial_grid_axes(x_motor=slow_axis, x=x_vals,
                             y_motor=fast_axis, y=y_vals, snake=snake, record=False)
    # `settle` is applied just before each event -> put it on the innermost (fast) axis.
    if settle and axes:
        axes[-1].settle = settle

    def _setup():
        try:
            yield from bps.mv(pin_diode.averaging_time, t)           # noqa: F821
        except Exception:
            yield from bps.null()
        if atten_in is not None:
            yield from atten_in()

    plan = acquire(name, dets, axes, reads=reads, setup=_setup,
                   geometry=geometry, scan_name="transmission",
                   md=md, baseline=baseline, name_tokens=list(name_tokens),
                   check_order=False)

    if dose_step is not None:
        plan = fresh_spot_wrapper(plan, fast_axis, dose_step)

    def _with_return():
        yield from plan
        # Return the dither axes to the sample origin (hardware hygiene; no event recorded).
        yield from bps.mv(slow_axis, x0, fast_axis, y0)

    return (yield from _with_return())


# ---------------------------------------------------------------------------
# Multi-sample bar (one run per sample)
# ---------------------------------------------------------------------------
def transmission_bar(samples, *, t=1.0, dets=None, reads=None, geometry="transmission",
                     points_fast=1, points_slow=1, d_fast=150.0, d_slow=0.0, snake=True,
                     dose_step=None, atten_in=None, md=None, waxs_arc=None, settle_arc=1.0):
    """Run :func:`transmission_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned (piezo/hexapod)
    then measured with the requested multi-spot averaging.

    Parameters
    ----------
    waxs_arc : sequence, optional
        If given, sweep ``waxs.arc`` OUTERMOST (slow axis) and measure the whole bar at each
        arc position -- so the in-vacuum arc moves ``len(waxs_arc)`` times for the bar rather
        than per sample.  Each (arc, sample) is still its own one-sample run.  If ``None``
        (default), the arc is left where it is and each sample is measured once.
    settle_arc : float
        Sleep after each ``waxs.arc`` move.
    (others as in :func:`transmission_run`)
    """
    def _measure_bar_once():
        for s in samples:
            yield from goto_sample(s)
            yield from transmission_run(
                s.name, t=t, dets=dets, reads=reads, geometry=geometry,
                points_fast=points_fast, points_slow=points_slow,
                d_fast=d_fast, d_slow=d_slow, snake=snake, dose_step=dose_step,
                atten_in=atten_in, md=merge_md(md, s.md))

    if waxs_arc is None:
        yield from _measure_bar_once()
    else:
        for wa in waxs_arc:                                          # SLOW axis outermost
            yield from bps.mv(waxs, wa)                              # noqa: F821
            if settle_arc:
                yield from bps.sleep(settle_arc)
            yield from _measure_bar_once()


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """8-capillary solution bar, single-spot transmission, arc swept once for the whole bar.

    ``pin_diode`` + ``xbpm`` recorded per event; transmission computed offline.  Run with::

        RE(technique_E_transmission.example())
    """
    bar = SampleList.from_columns(
        names=["BzMA-9.06", "BzMA-8.07", "BzMA-7.26", "BzMA-6.25",
               "BzMA-4.72", "BzMA-2.7", "BzMA-1.0", "Empty"],
        piezo_x=[42500, 30000, 19000, 3000, -6500, -21000, -34500, -42000],
        piezo_y=[-2550, -1950, -2250, -2250, -2100, -2100, -1800, -1800],
        piezo_z=[7800, 7800, 7800, 7800, 11000, 11000, 11000, 11000],
        md={"project_name": "311234_Demo"},
    )

    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                        # noqa: F821
        yield from bps.sleep(1)

    yield from transmission_bar(
        bar, t=1.0, geometry="transmission",
        waxs_arc=[20, 0],                          # arc moves twice total for the whole bar
        atten_in=_atten_in,
        md={"geometry_note": "capillary_solution"})


def example_multispot():
    """Single capillary, 5-spot average along its length (the classic transmission idiom).

    Five events in ONE run, dithering ``piezo.y`` by 150 um, each with ``pin_diode``/``xbpm``
    recorded.  Run with::

        RE(technique_E_transmission.example_multispot())
    """
    yield from goto_sample(SampleList.from_columns(
        names=["NIPAM-2.1"], piezo_x=[16200], piezo_y=[0], piezo_z=[0])[0])

    yield from transmission_run(
        "NIPAM-2.1", t=1.0, geometry="transmission",
        points_fast=5, d_fast=150.0,               # 5 spots, 150 um apart along the capillary
        dose_step=None,
        md={"project_name": "311234_Demo", "container": "capillary_1.5mm"})

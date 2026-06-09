"""
technique_B_grazing
==================

Archetype B -- Grazing-incidence thin-film scattering (GISAXS / GIWAXS) + alignment.

Thin films / surfaces measured at one or more incident angles, across one or more WAXS-arc
positions, with per-sample alignment.  The dominant SMI orchestration shape is the
multi-sample "bar".

**This file is a PRESET RECIPE built on the composition layer (``_compose``).**  Grazing
incidence is just two scan axes -- a (slow) WAXS-arc :func:`_compose.motor_axis` outermost and
a grazing-angle :func:`_compose.incidence_axis` inside it -- nested inside ONE
:func:`_compose.acquire` per sample.  Each concern (arc, incidence) is independent and freely
combinable with others (energy, temperature, spatial); to mix them, assemble the axes directly
-- see ``recipes_combined.py`` and the README.

This file demonstrates BOTH sanctioned multi-sample strategies:

1. :func:`giwaxs_bar` -- ONE run per sample (simple, the default).  Good when the arc set is
   small or alignment dominates.
2. :func:`giwaxs_bar_arc_economy` -- MULTIPLE runs open at once so ``waxs.arc`` (slow,
   in-vacuum) moves only once per arc position for the WHOLE bar.  Use when arc travel
   dominates overhead.  (Built on :func:`_core.multi_sample_run`; a different run topology, so
   it is *not* expressed via :func:`_compose.acquire`.)

Alignment uses the profile-collection routines (``alignement_gisaxs_hex`` /
``alignement_gisaxs_doblestack``) -- we call them, we do not reimplement them.  Because
alignment may leave attenuators out, every measurement run restores the measurement
configuration via :func:`_compose.acquire`'s ``setup=`` hook (ensure-attenuators-in).

.. important::
    Beamline globals required at runtime: ``np``, ``bps``, ``Signal``, ``piezo``, ``stage``,
    ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``,
    ``att2_9``, ``det_exposure_time``, and an alignment routine such as
    ``alignement_gisaxs_hex`` / ``alignement_gisaxs_doblestack`` (passed in as ``align``).
"""

from ._samples import SampleList
from ._core import (multi_sample_run, goto_sample, saxs_waxs_dets, merge_md)
from ._compose import acquire, incidence_axis, motor_axis, SPEED_SLOW
from ._preprocessors import ensure_in_wrapper, fresh_spot_wrapper, cleanup_wrapper

try:
    import bluesky.plan_stubs as bps
except Exception:  # pragma: no cover
    bps = None


__all__ = [
    "default_atten_in", "align_sample", "giwaxs_run",
    "giwaxs_bar", "giwaxs_bar_arc_economy", "example", "example_arc_economy",
]


# ---------------------------------------------------------------------------
# Measurement-configuration guard (attenuators in after alignment)
# ---------------------------------------------------------------------------
def default_atten_in():
    """Put the standard attenuator in for a measurement (override per experiment)."""
    yield from bps.mv(att2_9.close_cmd, 1)                      # noqa: F821
    yield from bps.sleep(1)


# ---------------------------------------------------------------------------
# Alignment wrapper
# ---------------------------------------------------------------------------
def align_sample(sample, *, align, angle=0.1, piezo_th=True):
    """Coarse-position a sample and run the GI alignment routine, returning aligned th0.

    ``align`` is the profile-collection alignment *plan-function* (e.g.
    ``alignement_gisaxs_hex`` or ``alignement_gisaxs_doblestack``), called as ``align(angle)``.
    After alignment, the aligned incident-angle zero is read from the relevant theta axis and
    returned so the caller can offset incident angles from it.

    This is a setup step, run *outside* the measurement run (alignment opens its own short
    runs).  Alignment offsets should be recorded in the measurement run's baseline by the
    caller if desired.
    """
    yield from goto_sample(sample)
    yield from align(angle)
    th0 = piezo.th.position if piezo_th else stage.th.position  # noqa: F821
    return th0


# ---------------------------------------------------------------------------
# One run = one sample, all (arc x incident-angle)  -- assembled from compose axes
# ---------------------------------------------------------------------------
def giwaxs_run(name, *, th0, incident_angles, waxs_arc=(0,), t=1.0, dets=None, reads=None,
               th_axis=None, dose_motor=None, dose_step=None, atten_in=None, baseline=None,
               md=None, name_tokens=("ai{incident_angle}", "wa{waxs_arc}", "bpm{xbpm2_sumX}")):
    """ONE run: all incident angles x WAXS-arc positions for a single (pre-aligned) sample.

    Recipe (built on :func:`_compose.acquire`): a (slow) WAXS-arc
    :func:`_compose.motor_axis` OUTERMOST and a grazing-angle :func:`_compose.incidence_axis`
    inside it -- consistent with the slow-axis-economy tenet (``waxs.arc`` moves the fewest
    times).  ``th0`` is the aligned incident-angle zero (from :func:`align_sample`); measured
    angles are ``th0 + ai``.  Attenuators are restored for the measurement via ``acquire``'s
    ``setup=`` hook; an optional dose walk keeps a fresh spot.

    The kwargs/defaults/behavior are unchanged from the hand-rolled version; only the
    implementation now assembles axes and calls :func:`_compose.acquire`.
    """
    if th_axis is None:
        th_axis = piezo.th                                     # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                   # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                            # noqa: F821 (SDD)
        except Exception:
            baseline = []

    dets = dets or _arc_dets()
    det_exposure_time(t, t)                                    # noqa: F821

    # The axis stack (outermost first): waxs.arc (slow) -> incident angle.  The incidence axis
    # records the *relative* angle on an `incident_angle` Signal (-> {incident_angle} token);
    # the arc motor is recorded via `reads` (so {waxs_arc} resolves).
    axes = [
        motor_axis("arc", waxs, list(waxs_arc), record=True, speed=SPEED_SLOW),  # noqa: F821
        incidence_axis(th_axis, th0, list(incident_angles)),
    ]

    # Restore the measurement configuration (attenuators in) once, just after the run opens.
    _atten = atten_in or default_atten_in

    def _setup():
        yield from _atten()

    plan = acquire(name, dets, axes, reads=reads, setup=_setup,
                   geometry="reflection", scan_name="giwaxs",
                   md=md, baseline=baseline, name_tokens=list(name_tokens),
                   check_order=False)

    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    return (yield from plan)


def _arc_dets():
    """Default arc-aware detector set (SAXS dropped when the arc occludes it)."""
    return saxs_waxs_dets(use_saxs=True, use_waxs=True)


# ---------------------------------------------------------------------------
# Multi-sample bar -- strategy 1: one run per sample
# ---------------------------------------------------------------------------
def giwaxs_bar(samples, *, align, align_angle=0.1, waxs_arc=(0,), t=1.0, dets=None,
               th_axis=None, dose_step=None, atten_in=None, md=None,
               default_incident_angles=(0.1, 0.2)):
    """Align + measure each sample on the bar; ONE run per sample.

    Per-sample ``incident_angles`` from the :class:`SampleList` are used when present, else
    ``default_incident_angles``.  Alignment offset (``th0``) is recorded in each run's
    baseline via an ``aligned_th0`` Signal.
    """
    for s in samples:
        th0 = yield from align_sample(s, align=align, angle=align_angle,
                                      piezo_th=(th_axis is None))
        aligned = Signal(name="aligned_th0", value=float(th0))  # noqa: F821
        angles = s.incident_angles or list(default_incident_angles)
        dose_motor = piezo.x if dose_step else None            # noqa: F821
        yield from giwaxs_run(
            s.name, th0=th0, incident_angles=angles, waxs_arc=waxs_arc, t=t, dets=dets,
            th_axis=th_axis, dose_motor=dose_motor, dose_step=dose_step,
            atten_in=atten_in, baseline=[aligned] + (
                [pil2M_pos.z] if _has_sdd() else []),           # noqa: F821
            md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Multi-sample bar -- strategy 2: arc economy (multiple runs open at once)
# ---------------------------------------------------------------------------
def giwaxs_bar_arc_economy(samples, *, align, align_angle=0.1, waxs_arc=(0, 20), t=1.0,
                           dets=None, th_axis=None, atten_in=None, md=None,
                           default_incident_angles=(0.1, 0.2)):
    """Align all samples first, THEN sweep ``waxs.arc`` once for the whole bar.

    Opens one run per sample simultaneously and writes each sample's frames into its own run
    at each arc position, so the slow in-vacuum arc moves ``len(waxs_arc)`` times total
    instead of ``len(waxs_arc) * n_samples`` times.

    Alignment happens up front (each sample's ``th0`` cached); the interleaved acquisition
    then needs no further alignment moves.  Incident angles per sample are taken from the
    :class:`SampleList` (or ``default_incident_angles``).
    """
    if th_axis is None:
        th_axis = piezo.th                                     # noqa: F821
    samples = list(samples)

    # Phase 1: align everything, cache th0 + angles on each sample's md.
    th0_by_name = {}
    for s in samples:
        th0 = yield from align_sample(s, align=align, angle=align_angle,
                                      piezo_th=(th_axis is piezo.th))  # noqa: F821
        th0_by_name[s.name] = th0
        s.md.setdefault("aligned_th0", float(th0))

    dets = dets or _arc_dets()

    # The per-(sample, arc) measurement: loop that sample's incident angles at this arc value.
    def _point(sample, arc_value):
        th0 = th0_by_name[sample.name]
        incident_angle = Signal(name="incident_angle", value=float(th0))  # noqa: F821
        angles = sample.incident_angles or list(default_incident_angles)
        reads = [energy, waxs, xbpm2, xbpm3]                   # noqa: F821
        for ai in angles:
            yield from bps.mv(th_axis, th0 + ai)
            incident_angle.put(float(ai))
            yield from bps.trigger_and_read(list(dets) + reads + [incident_angle])
        yield from bps.mv(th_axis, th0)

    det_exposure_time(t, t)                                    # noqa: F821

    # ensure attenuators in for the whole interleaved block
    def _go():
        yield from multi_sample_run(
            samples, slow_axis=waxs, slow_positions=list(waxs_arc),    # noqa: F821
            point=_point, dets=dets, scan_name="giwaxs_arc_economy",
            geometry="reflection", md=md, settle=1.0)

    plan = ensure_in_wrapper(_go(), atten_in or default_atten_in)
    return (yield from plan)


def _has_sdd():
    try:
        _ = pil2M_pos.z                                        # noqa: F821
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """5-sample GIWAXS bar, one run per sample, arc=[0,20], align each at 0.1 deg.

    ``alignement_gisaxs_hex`` is a profile-collection global; pass whichever routine your
    geometry uses.  Run with::

        RE(technique_B_grazing.example())
    """
    bar = SampleList.from_columns(
        names=["s01", "s02", "s03", "s04", "s05"],
        piezo_x=[55000, 42000, 25000, 7000, -10000],
        piezo_y=[5000, 5000, 5000, 5000, 5000],
        piezo_z=[7000, 7000, 7000, 7000, 7000],
        hexa_x=[10, 10, 10, 10, 10],
        incident_angles=[0.1, 0.2],
        md={"project_name": "311234_Demo"},
    )
    yield from giwaxs_bar(bar, align=alignement_gisaxs_hex, align_angle=0.1,  # noqa: F821
                          waxs_arc=[0, 20], t=1.0, dose_step=30)


def example_arc_economy():
    """Same bar, but move ``waxs.arc`` only twice total (once per arc) for all 5 samples."""
    bar = SampleList.from_columns(
        names=["s01", "s02", "s03", "s04", "s05"],
        piezo_x=[55000, 42000, 25000, 7000, -10000],
        piezo_y=[5000, 5000, 5000, 5000, 5000],
        hexa_x=[10, 10, 10, 10, 10],
        incident_angles=[0.1, 0.2],
        md={"project_name": "311234_Demo"},
    )
    yield from giwaxs_bar_arc_economy(bar, align=alignement_gisaxs_hex,  # noqa: F821
                                      waxs_arc=[0, 20], t=1.0)

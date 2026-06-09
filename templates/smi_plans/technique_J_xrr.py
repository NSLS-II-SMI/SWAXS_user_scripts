"""
technique_J_xrr
==============

Archetype J -- X-ray reflectivity (XRR), including tender / resonant and liquid surfaces.

Measure **specular reflectivity vs incident angle**: sweep the grazing incidence angle and
record the specular intensity (plus I0 and transmitted flux) as one run per sweep.  Geometry
varies -- the incidence axis may be ``piezo.th`` (solid substrate, direct beam), ``stage.th``,
``prs``, or a bounce-down-mirror (BDM) ``bdm.th`` for liquid surfaces -- so it is passed in as
``th_axis``.

Gold reference: ``Commissioning/bounce_down_mirror.py`` -- READ IT; this file mirrors its
structure exactly:

* ``incident_angle`` is recorded as a **Signal** in the stream (so ``{incident_angle}`` is a
  filename token), not baked into the name;
* the whole angle sweep is **ONE run** (``@run_decorator`` + ``trigger_and_read`` per angle);
* an **angle-dependent attenuator ladder** (``att_selection_8keV(angle)``) keeps the specular
  peak in the detector's dynamic range as reflectivity falls -- the HDR/attenuator-ladder
  idiom;
* ``peizo_th_correction(angle)`` corrects the geometric theta-motion scaling for solid
  substrates;
* the **liquid-surface technique** reflects the beam off a bounce-down mirror so a flat liquid
  can be measured at a finite effective angle (``move_bdm_sample`` couples ``bdm.th`` +
  ``piezo.y``).

Other legacy refs: ``legacy/30-user-Gann.py`` (resonant XRR ``xrr_spol_waxs``),
``legacy/30-user-Cordova.py`` (Sn-edge resonant XRR), the Commissioning BDM toolkit
(``move_bdm_sample``, ``att_selection_8keV``, ``peizo_th_correction``,
``run_xrr_bdm_saxs`` / ``run_xrr_solid_substrate_using_direct_beam``).

What this file gives you
------------------------
* :func:`xrr_point` -- inner per-angle measurement (stamps ``incident_angle`` + flux, one
  event).
* :func:`att_ladder_8keV` -- the canonical 8 keV angle->attenuator selection *plan* (you pass
  your own ``atten_for_angle`` to override; this preserves the BDM ladder).
* :func:`xrr_run` -- ONE run sweeping incident angle on one sample, recording angle + I0 +
  transmitted flux, with optional angle-dependent attenuation and theta-motion correction.
* :func:`xrr_resonant_run` -- resonant/tender XRR: set a fixed energy near an edge, then sweep
  angle (ONE run); or a 2D energy x angle map (nested, still ONE run).
* :func:`xrr_liquid_run` -- liquid-surface XRR using the bounce-down mirror (``move_bdm`` couples
  ``bdm.th`` + ``piezo.y`` per angle), ONE run.
* :func:`xrr_bar` -- loop :func:`xrr_run` over a :class:`SampleList` (one sweep/sample).
* :func:`example` / :func:`example_resonant` -- runnable, fully-specified examples.

Idioms preserved (via _preprocessors): angle-dependent attenuator ladder (HDR), ensure
attenuators/measurement-config in, baseline capture of constants, cleanup (return the incidence
axis) on error.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bpp``, ``Signal``, ``piezo``, ``stage``, ``prs``,
    ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pin_diode``, ``pil2M_pos``,
    ``att2_1``, ``att2_2``, ``att2_3``, ``det_exposure_time``.  The bounce-down mirror ``bdm``
    (``.th`` / ``.y`` / ``.x``) and the ROI helper ``smi`` are needed only for
    :func:`xrr_liquid_run`.
"""

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, fname, merge_md)
from ._preprocessors import (ensure_in_wrapper, cleanup_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "xrr_point", "att_ladder_8keV", "peizo_th_correction", "xrr_run",
    "xrr_resonant_run", "xrr_liquid_run", "xrr_bar", "example", "example_resonant",
    "example_bar",
]


# ---------------------------------------------------------------------------
# Theta-motion correction (solid substrate; legacy peizo_th_correction)
# ---------------------------------------------------------------------------
def peizo_th_correction(th_target, *, slope=1.281629, intercept=0.001648, th_aligned=0.1):
    """Correct the geometric theta-motion scaling for a solid substrate.

    Direct port of ``Commissioning/bounce_down_mirror.py::peizo_th_correction``: the sample is
    aligned at ``piezo.th = th_aligned`` and the commanded motion is scaled to land the
    specular at the requested ``th_target`` (the stage geometry is not 1:1).  This is a plain
    helper (not a plan).
    """
    return (th_target - th_aligned) * slope + intercept + th_aligned


# ---------------------------------------------------------------------------
# Angle-dependent attenuator ladder (HDR) -- the 8 keV selection plan
# ---------------------------------------------------------------------------
def att_ladder_8keV(angle):
    """Insert/remove attenuators appropriate for ``angle`` (deg) at 8 keV (Mo 20 um ladder).

    Direct port of ``Commissioning/bounce_down_mirror.py::att_selection_8keV`` -- preserves the
    HDR / attenuator-ladder idiom so the specular peak stays in range as reflectivity drops with
    angle::

        angle      filters in
        0-0.3      x4 + x1   (att2_3, att2_1)
        0.3-0.55   x4        (att2_3)
        0.55-0.9   x2 + x1   (att2_2, att2_1)
        0.9-1.1    x2        (att2_2)
        1.1-1.28   x1        (att2_1)
        1.28-2     none

    Pass this (or your own ``atten_for_angle(ai)`` plan) to :func:`xrr_run` as ``atten_ladder``.
    """
    if angle < 0:
        print("att_ladder_8keV: angle is negative; no change")
        return
    elif angle < 0.3:
        att_in, att_out = [att2_3, att2_1], [att2_2]               # noqa: F821
    elif angle < 0.55:
        att_in, att_out = [att2_3], [att2_1, att2_2]               # noqa: F821
    elif angle < 0.9:
        att_in, att_out = [att2_2, att2_1], [att2_3]               # noqa: F821
    elif angle < 1.1:
        att_in, att_out = [att2_2], [att2_1, att2_3]               # noqa: F821
    elif angle < 1.28:
        att_in, att_out = [att2_1], [att2_2, att2_3]               # noqa: F821
    elif angle < 2:
        att_in, att_out = [], [att2_1, att2_2, att2_3]             # noqa: F821
    else:
        print("att_ladder_8keV: angle too big; no change")
        return
    for att in att_in:
        yield from bps.mv(att.open_cmd, 1)
        yield from bps.sleep(1)
    for att in att_out:
        yield from bps.mv(att.close_cmd, 1)
        yield from bps.sleep(1)


# ---------------------------------------------------------------------------
# Inner per-angle measurement (records incident_angle + flux as Signals)
# ---------------------------------------------------------------------------
def xrr_point(th_axis, th_value, dets, reads, incident_angle_sig, *, settle=1.0,
              atten_ladder=None, th_correction=None):
    """Move to one incident angle, optionally set attenuators, record ONE event.

    Mirrors the body of ``run_xrr_bdm_saxs`` / ``run_xrr_solid_substrate_using_direct_beam``:
    optionally run the attenuator ladder for this angle, optionally apply the theta-motion
    correction, settle, stamp ``incident_angle`` and ``trigger_and_read`` so the angle + flux
    ride in the stream.

    Parameters
    ----------
    th_axis : positioner
        The incidence axis (``piezo.th`` / ``stage.th`` / ``prs`` / ``bdm.th``).
    th_value : float
        Incident angle (deg) to move to (the *physical* angle; the recorded ``incident_angle``).
    atten_ladder : callable(angle) -> plan, optional
        Angle-dependent attenuator selection (e.g. :func:`att_ladder_8keV`).
    th_correction : callable(angle) -> float, optional
        Map requested angle -> commanded motor value (e.g. :func:`peizo_th_correction` for solid
        substrates).  ``incident_angle`` records the *requested* angle, not the corrected motor.
    """
    if atten_ladder is not None:
        yield from atten_ladder(th_value)
    commanded = th_correction(th_value) if th_correction is not None else th_value
    yield from bps.mv(th_axis, commanded)
    if settle:
        yield from bps.sleep(settle)
    incident_angle_sig.put(float(th_value))
    yield from bps.trigger_and_read(list(dets) + list(reads) + [incident_angle_sig])


# ---------------------------------------------------------------------------
# One run = one incident-angle sweep on one sample
# ---------------------------------------------------------------------------
def xrr_run(name, angles, *, t=1.0, dets=None, reads=None, th_axis=None, th0=0.0,
            atten_ladder=None, th_correction=None, settle=1.0, geometry="reflection",
            atten_in=None, baseline=None, md=None,
            name_tokens=("ai{incident_angle}", "bpm{xbpm2_sumX}")):
    """ONE run: sweep the incident angle on a single sample, recording angle + I0 + flux.

    The whole reflectivity curve is a single run (Tenet 1).  ``incident_angle`` is recorded as a
    Signal each event so ``{incident_angle}`` resolves in the filename -- mirroring
    ``bounce_down_mirror.py::run_xrr_bdm_saxs``.

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    angles : sequence
        Incident angles (deg), relative to ``th0``.  Build with ``np.linspace(0, 0.45, 181)``
        for the canonical solid-substrate sweep.
    t : float
        Exposure time (s) per angle.
    dets : list, optional
        Detectors.  Default ``[pil2M, xbpm2, xbpm3, pin_diode]`` (specular SAXS + I0 +
        transmission).  Use ``pil900KW`` for WAXS-geometry XRR.
    reads : list, optional
        Extra readables each event (default ``[energy]`` so the photon energy is recorded too).
    th_axis : positioner, optional
        Incidence axis (default ``piezo.th``).
    th0 : float
        Aligned incidence zero; the measured angle is ``th0 + ai`` (recorded as ``ai``).
    atten_ladder : callable(angle) -> plan, optional
        Angle-dependent attenuator selection (e.g. :func:`att_ladder_8keV`).  Preserves the HDR
        ladder.
    th_correction : callable(angle) -> float, optional
        Theta-motion correction (e.g. :func:`peizo_th_correction`).
    settle : float
        Sleep after each angle move (let the piezo settle).
    atten_in : callable () -> plan, optional
        Put the measurement attenuator/beamstop config in once at run open (after any prior
        alignment); runs inside the run.
    baseline : list, optional
        Constants to record (default includes SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename (recorded fields: angle + I0 here).
    """
    if dets is None:
        dets = [pil2M, xbpm2, xbpm3, pin_diode]                    # noqa: F821
    incident_angle = Signal(name="incident_angle", value=float(th0))  # noqa: F821
    if reads is None:
        reads = [energy]                                           # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821 (SDD)
        except Exception:
            baseline = []
    if th_axis is None:
        th_axis = piezo.th                                         # noqa: F821

    det_exposure_time(t, t)                                        # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        for ai in angles:
            yield from xrr_point(th_axis, th0 + ai, dets, reads, incident_angle,
                                 settle=settle, atten_ladder=atten_ladder,
                                 th_correction=th_correction)
        yield from bps.mv(th_axis, th0)                            # return to aligned zero

    plan = one_sample_run(_measure, dets, sample_name=sample_name, scan_name="xrr",
                          geometry=geometry, md=md, baseline=baseline)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)

    def _cleanup():
        yield from bps.mv(th_axis, th0)                            # restore incidence on error

    return (yield from cleanup_wrapper(plan, _cleanup))


# ---------------------------------------------------------------------------
# Resonant / tender XRR (fixed energy near an edge, or 2D energy x angle)
# ---------------------------------------------------------------------------
def xrr_resonant_run(name, angles, *, edge_energy, energies=None, t=1.0, dets=None,
                     reads=None, th_axis=None, th0=0.0, atten_ladder=None, th_correction=None,
                     settle=1.0, atten_in=None, baseline=None, md=None,
                     name_tokens=("{energy_energy}eV", "ai{incident_angle}", "bpm{xbpm2_sumX}")):
    """ONE run: resonant / tender XRR at a fixed edge energy, or a 2D energy x angle map.

    Reproduces Gann resonant XRR / Cordova Sn-edge XRR: set the DCM energy near an absorption
    edge and sweep angle.  If ``energies`` is given, the energy is the *outer* loop (a 2D
    energy x angle map) -- still ONE run -- with both ``energy`` and ``incident_angle`` recorded
    each event (so ``{energy_energy}`` and ``{incident_angle}`` both resolve).

    Parameters
    ----------
    name : str
        Human label.
    angles : sequence
        Incident angles (deg) relative to ``th0``.
    edge_energy : float
        The energy (eV) to set when ``energies is None`` (fixed-energy resonant XRR).
    energies : sequence, optional
        If given, loop these energies (outer) x angles (inner) as a 2D resonant map in ONE run.
    t, dets, reads, th_axis, th0, atten_ladder, th_correction, settle, atten_in, baseline, md,
    name_tokens :
        As in :func:`xrr_run`.
    """
    if dets is None:
        dets = [pil2M, xbpm2, xbpm3, pin_diode]                    # noqa: F821
    incident_angle = Signal(name="incident_angle", value=float(th0))  # noqa: F821
    if reads is None:
        reads = [energy]                                           # noqa: F821 (records {energy_energy})
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821
        except Exception:
            baseline = []
    if th_axis is None:
        th_axis = piezo.th                                         # noqa: F821

    det_exposure_time(t, t)                                        # noqa: F821
    sample_name = fname(name, *name_tokens)
    e_list = list(energies) if energies is not None else [edge_energy]

    def _measure():
        for e in e_list:                                           # energy OUTER (slow optic)
            yield from bps.mv(energy, e)                           # noqa: F821
            yield from bps.sleep(settle)
            for ai in angles:
                yield from xrr_point(th_axis, th0 + ai, dets, reads, incident_angle,
                                     settle=settle, atten_ladder=atten_ladder,
                                     th_correction=th_correction)
            yield from bps.mv(th_axis, th0)
        yield from bps.mv(th_axis, th0)

    plan = one_sample_run(_measure, dets, sample_name=sample_name, scan_name="xrr_resonant",
                          geometry="reflection", md=md, baseline=baseline)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)

    def _cleanup():
        yield from bps.mv(th_axis, th0)                            # restore incidence on error

    return (yield from cleanup_wrapper(plan, _cleanup))


# ---------------------------------------------------------------------------
# Liquid-surface XRR via the bounce-down mirror
# ---------------------------------------------------------------------------
def xrr_liquid_run(name, angles, *, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183,
                   t=1.0, dets=None, reads=None, atten_ladder=None, settle=1.0,
                   move_bdm=None, baseline=None, md=None,
                   name_tokens=("ai{incident_angle}", "bpm{xbpm2_sumX}")):
    """ONE run: liquid-surface XRR using the bounce-down mirror (BDM) bounced beam.

    A flat liquid surface cannot be tilted, so the **beam** is tilted down onto it by the BDM:
    ``move_bdm(alpha)`` couples ``bdm.th`` and ``piezo.y`` so the bounced beam strikes the
    liquid at effective angle ``alpha`` while keeping it in the beam path (the geometry in
    ``bounce_down_mirror.py::move_bdm_sample`` / ``xrr_scan_liquid_using_bounced_beam``).  The
    whole sweep is ONE run with ``incident_angle`` recorded per event.

    Parameters
    ----------
    name : str
        Human label.
    angles : sequence
        Effective incidence angles (deg) for the bounced beam.
    piezo_y_origin, bdm_th_origin : float
        The liquid ``piezo.y`` zero and the BDM ``bdm.th`` zero (both at origin before the run).
    bdm_sample_distance : float
        BDM-to-sample distance (mm) used in the y-coupling geometry.
    move_bdm : callable(alpha) -> plan, optional
        The BDM coupling plan; default builds the ``move_bdm_sample`` geometry inline
        (``y_offset = tan(2*alpha) * distance``).  Override to use the profile-collection
        ``move_bdm_sample`` if available.
    t, dets, reads, atten_ladder, settle, baseline, md, name_tokens :
        As in :func:`xrr_run`.
    """
    if dets is None:
        dets = [pil2M, xbpm2, xbpm3]                               # noqa: F821
    incident_angle = Signal(name="incident_angle", value=float(angles[0]))  # noqa: F821
    if reads is None:
        reads = [energy]                                           # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821
        except Exception:
            baseline = []

    def _default_move_bdm(alpha):
        # tan(2*alpha) geometry from bounce_down_mirror.move_bdm_sample (y in microns).
        y_offset = np.tan(np.deg2rad(2 * alpha)) * bdm_sample_distance * 1000   # noqa: F821
        yield from bps.mv(bdm.th, bdm_th_origin + alpha,           # noqa: F821
                          piezo.y, piezo_y_origin - y_offset)      # noqa: F821

    _move = move_bdm if move_bdm is not None else _default_move_bdm

    det_exposure_time(t, t)                                        # noqa: F821
    sample_name = fname(name + "_liquid", *name_tokens)

    def _measure():
        for alpha in angles:
            yield from _move(alpha)                                # couple bdm.th + piezo.y
            if atten_ladder is not None:
                yield from atten_ladder(2 * alpha)                 # ladder vs 2*alpha (BDM)
            yield from bps.sleep(settle)
            incident_angle.put(float(alpha))
            yield from bps.trigger_and_read(list(dets) + list(reads) + [incident_angle])
        yield from _move(0)                                        # return liquid + BDM to origin

    return (yield from one_sample_run(_measure, dets, sample_name=sample_name,
                                      scan_name="xrr_liquid_bdm", geometry="reflection",
                                      md=md, baseline=baseline))


# ---------------------------------------------------------------------------
# Multi-sample bar (one sweep per sample)
# ---------------------------------------------------------------------------
def xrr_bar(samples, angles, *, t=1.0, dets=None, th_axis=None, atten_ladder=None,
            th_correction=None, settle=1.0, atten_in=None, md=None):
    """Run :func:`xrr_run` for each sample on the bar (ONE angle sweep per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned (piezo/hexapod) then
    swept.  The aligned incidence zero ``th0`` may be supplied per sample as ``piezo_th`` (used
    as the aligned zero) or in the sample md as ``{"th0": <deg>}``; otherwise 0.
    """
    for s in samples:
        yield from goto_sample(s)
        th0 = float(s.md.get("th0", s.piezo_th if s.piezo_th is not None else 0.0))
        yield from xrr_run(
            s.name, angles, t=t, dets=dets, th_axis=th_axis, th0=th0,
            atten_ladder=atten_ladder, th_correction=th_correction, settle=settle,
            atten_in=atten_in, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """Solid-substrate XRR: a single 0 -> 0.45 deg sweep (181 pts) with the 8 keV ladder.

    Mirrors ``bounce_down_mirror.py::run_xrr_solid_substrate_using_direct_beam`` -- ONE run,
    ``incident_angle`` recorded as a Signal, angle-dependent attenuators, theta-motion
    correction.  Run with::

        RE(technique_J_xrr.example())
    """
    angles = np.linspace(0, 0.45, 181)                            # noqa: F821
    yield from xrr_run(
        "Si_substrate_film", angles, t=1.0, th_axis=piezo.th, th0=0.1,  # noqa: F821
        atten_ladder=att_ladder_8keV, th_correction=peizo_th_correction,
        md={"project_name": "Demo_XRR", "geometry": "reflection"})


def example_resonant():
    """Resonant Sn-L3 XRR: fixed near-edge energy, 0 -> 0.6 deg sweep, ONE run.

    Mirrors Cordova Sn-edge resonant XRR (Gann-style).  For a full 2D energy x angle resonant
    map, pass ``energies=`` an array instead of a single ``edge_energy``.
    """
    angles = np.linspace(0, 0.6, 121)                             # noqa: F821
    yield from xrr_resonant_run(
        "SnOx_film", angles, edge_energy=4040, t=2.0, th_axis=piezo.th, th0=0.1,  # noqa: F821
        atten_ladder=att_ladder_8keV,
        md={"project_name": "Demo_resonant_XRR", "edge": "Sn_L3"})


def example_bar():
    """A 3-sample XRR bar: one 0 -> 0.45 deg sweep per sample (one run each).

    Each sample's aligned incidence zero is taken from its ``piezo_th`` column.  Run with::

        RE(technique_J_xrr.example_bar())
    """
    bar = SampleList.from_columns(
        names=["filmA", "filmB", "filmC"],
        piezo_x=[-20000, -5000, 12000],
        piezo_y=[4000, 4000, 4000],
        piezo_th=[0.1, 0.1, 0.1],                  # aligned incidence zero per sample
        md={"project_name": "Demo_XRR_bar"},
    )
    angles = np.linspace(0, 0.45, 181)                            # noqa: F821
    yield from xrr_bar(bar, angles, t=1.0, atten_ladder=att_ladder_8keV,
                       th_correction=peizo_th_correction, md={"technique": "XRR"})

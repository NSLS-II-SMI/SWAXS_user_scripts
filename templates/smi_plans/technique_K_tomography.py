"""
technique_K_tomography
=====================

Archetype K -- SAXS/WAXS tomography & texture / pole-figure.

Rotation series on the ``prs`` (Precision Rotation Stage = phi) axis for **tomographic
reconstruction** or **texture / pole-figure** analysis:

* **Tomography:** rock ``prs`` through a full ``-90 -> +90 deg`` series (recording one frame per
  angle) and reconstruct a SAXS/WAXS cross-section.  With a coupled translation this becomes a
  sinogram.
* **Texture / pole-figure GIWAXS:** rock ``prs`` (in-plane orientation) at a *fixed grazing
  incidence* to map crystallographic texture, optionally across WAXS-arc positions.

THE KEY POINT (Tenet 1): a rotation series is ONE logical experiment = ONE run.  The legacy
form (``CFN/Yugang/2026C1_Tomo.py::run_tomo``) does ``for theta: mv(prs, theta);
bp.count(num=1)`` -> 181 separate runs with ``prs`` and ``xbpm3.sumX`` baked into the filename.
Here a whole series is a single ``bp.rel_scan(prs, ...)`` (or one :func:`_core.one_sample_run`
with ``inner()`` doing ``mv(prs)`` + ``trigger_and_read``), so ``prs`` and the flux monitor ride
in the document stream.

``prs`` is slow and in-vacuum, so it is the **scanned / outermost axis**; any coarse
positioning, alignment, and WAXS-arc setup stay outside the rotation.

Gold reference: ``CFN/Yugang/2026C1_Tomo.py::run_tomo`` (the ``prs`` rotation series, ``pil2M``
+ ``pil900KW``, ``xbpm3`` flux).  Coupled rotation/translation: ``legacy/34-oleg.py::aaron_rot``
and ``legacy/35-oleg-cube.py`` (``bp.inner_product_scan([pil2M], N, prs, ..., stage.x, ...,
piezo.y, ...)`` -- the sinogram idiom).  Texture/pole-figure: ``legacy/30-user-Kang.py::
rotation_saxs`` (``bp.grid_scan(dets, prs, *prs_range, waxs, *waxs_range, 1)``) and
``legacy/30-user-Tiwale.py::SAXS_S_edge_allprs`` (rock ``prs`` 1001 pts at fixed grazing
``prs0 = 1.275``).

What this file gives you
------------------------
* :func:`tomo_dets` -- the standard tomography detector + flux-monitor list.
* :func:`tomography_run` -- ONE run: a ``prs`` rotation series on a single sample
  (``bp.rel_scan`` over ``prs``), with the option to *couple a translation* for a sinogram
  (``bp.inner_product_scan`` / ``scan_nd`` -- the 34/35-oleg idiom) still as ONE run.
* :func:`texture_pole_figure_run` -- ONE run: rock ``prs`` at a fixed incidence angle (recording
  ``prs`` + incident angle), optionally across WAXS-arc positions.
* :func:`tomography_bar` -- loop :func:`tomography_run` over a :class:`SampleList` (one
  series/sample), with ``prs`` as the scanned slow axis.
* :func:`example` / :func:`example_texture` / :func:`example_sinogram` -- runnable examples.

Idioms preserved: ``prs`` slow/in-vacuum as the scanned axis (outermost), coupled
rotation/translation sinograms (oleg ``inner_product_scan``), arc-conditional dets / arc as a
second axis for texture (Kang), ``xbpm3`` flux recorded in-stream, baseline capture of the SDD,
cleanup (return ``prs``) on error.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bp`` (bluesky.plans), ``Signal``, ``prs``,
    ``piezo``, ``stage``, ``waxs``, ``pil2M``, ``pil900KW``, ``pil2M_pos``, ``xbpm3``,
    ``pin_diode``, ``det_exposure_time``.
"""

from ._samples import SampleList
from ._core import (goto_sample, fname, merge_md)
from ._preprocessors import baseline_wrapper, cleanup_wrapper

try:
    import bluesky.plan_stubs as bps
    import bluesky.plans as bp
except Exception:  # pragma: no cover
    bps = None
    bp = None


__all__ = [
    "tomo_dets", "tomography_run", "texture_pole_figure_run", "tomography_bar",
    "example", "example_texture", "example_sinogram",
]


# ---------------------------------------------------------------------------
# Detector + flux-monitor list
# ---------------------------------------------------------------------------
def tomo_dets(*, saxs=True, waxs=True, pin=True, xbpm=True):
    """Return the tomography detector list: SAXS and/or WAXS + flux-monitor channels.

    The ``run_tomo`` reference uses ``[pil2M, pil900KW]``; here ``pin_diode`` and ``xbpm3`` are
    added *as detectors* so the transmitted-beam and incident-flux normalization ride in the
    stream (replacing ``xbpm3.sumX.get()``-into-filename).  Both SAXS and WAXS are kept; for a
    pure SAXS tomogram pass ``waxs=False``.
    """
    dets = []
    if saxs:
        dets.append(pil2M)                                         # noqa: F821
    if waxs:
        dets.append(pil900KW)                                      # noqa: F821
    if pin:
        dets.append(pin_diode)                                     # noqa: F821
    if xbpm:
        dets.append(xbpm3)                                         # noqa: F821
    return dets


# ---------------------------------------------------------------------------
# One run = one prs rotation series (optionally coupled to a translation)
# ---------------------------------------------------------------------------
def tomography_run(name, prs_range=(-90, 90, 181), *, t=1.0, dets=None, reads=None,
                   translate_axis=None, translate_range=None, geometry="transmission",
                   baseline=None, md=None,
                   name_tokens=("sdd{pil2M_sample_distance_mm}", "bpm{xbpm3_sumX}")):
    """ONE run: a ``prs`` rotation series on a single sample (tomography / sinogram).

    The whole rotation is a single run (Tenet 1).  ``prs`` is the scanned axis and is recorded
    automatically; ``xbpm3`` / ``pin_diode`` ride in the stream as detectors.

    Two modes:
      * **Pure rotation** (``translate_axis is None``): ``bp.rel_scan(dets, prs, start, stop,
        n)`` -- a tomographic projection series (mirrors ``run_tomo``).
      * **Coupled rotation + translation** (sinogram): if ``translate_axis`` and
        ``translate_range`` are given, the translation is swept *together with* ``prs`` in a
        single ``bp.inner_product_scan`` (the 34/35-oleg ``aaron_rot`` idiom) -- still ONE run,
        with both ``prs`` and the translation recorded per event.

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    prs_range : (start, stop, n)
        Rotation series in degrees.  Default ``(-90, 90, 181)`` (1 deg/step); use a finer ``n``
        (e.g. 1801) for high-resolution tomograms as in ``run_tomo(..., 1801)``.
    t : float
        Exposure time (s) per angle.
    dets : list, optional
        Detectors.  Default :func:`tomo_dets` (SAXS + WAXS + ``pin_diode`` + ``xbpm3``).
    reads : list, optional
        Extra readables each event (default ``[]``; the scanned axes are recorded automatically).
    translate_axis : positioner, optional
        If given (with ``translate_range``), couple this translation to ``prs`` for a sinogram
        (e.g. ``stage.x`` or ``piezo.x``).
    translate_range : (start, stop), optional
        Start/stop for the coupled translation (same number of points as ``prs``, ``n``).
    geometry : str
        ``"transmission"`` (SAXS/WAXS tomography) or ``"reflection"``.
    baseline : list, optional
        Constants to record (default includes SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename (recorded fields: SDD + flux here).
    """
    if dets is None:
        dets = tomo_dets()
    reads = list(reads or [])
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821 (SDD)
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                        # noqa: F821
    start, stop, n = prs_range
    sample_name = fname(name, *name_tokens)
    all_dets = list(dets) + reads
    run_md = merge_md(
        {"scan_name": "tomography"},
        {"geometry": geometry} if geometry else {},
        md,
        {"sample_name": sample_name},
    )

    def _plan():
        if translate_axis is not None and translate_range is not None:
            # Coupled rotation + translation -> sinogram, ONE run (oleg inner_product_scan).
            ts, tf = translate_range
            yield from bp.inner_product_scan(                      # noqa: F821
                all_dets, n, prs, start, stop, translate_axis, ts, tf, md=run_md)  # noqa: F821
        else:
            # Pure rotation series, ONE run (run_tomo modernized).
            yield from bp.rel_scan(all_dets, prs, start, stop, n, md=run_md)   # noqa: F821

    body = _plan()
    if baseline:
        body = baseline_wrapper(body, baseline)

    # Record the prs start so we can restore it on error/abort.
    prs_start_pos = {}

    def _capture():
        prs_start_pos["pos"] = prs.position                       # noqa: F821
        yield from bps.null()

    def _cleanup():
        if "pos" in prs_start_pos:
            yield from bps.mv(prs, prs_start_pos["pos"])           # noqa: F821

    def _go():
        yield from _capture()
        yield from body

    return (yield from cleanup_wrapper(_go(), _cleanup))


# ---------------------------------------------------------------------------
# Texture / pole-figure: rock prs at a fixed incidence angle
# ---------------------------------------------------------------------------
def texture_pole_figure_run(name, prs_range=(-90, 90, 91), *, ai0=0.0, ai=0.0, th_axis=None,
                            waxs_arc=(0,), t=1.0, dets=None, reads=None, geometry="reflection",
                            baseline=None, md=None,
                            name_tokens=("ai{incident_angle}", "bpm{xbpm3_sumX}")):
    """ONE run: rock ``prs`` at a fixed grazing incidence for texture / a pole figure.

    Sets the grazing incidence once (``th_axis`` -> ``ai0 + ai``), records it as a Signal, then
    rocks ``prs`` over ``prs_range`` -- the in-plane orientation sweep that builds a pole figure
    (Kang ``rotation_saxs``; Tiwale ``SAXS_S_edge_allprs`` at fixed ``prs0``).  Optionally sweep
    the WAXS arc as a *second* scanned axis (``bp.grid_scan(dets, prs, *prs_range, waxs,
    *waxs_arc_grid, 1)``) so the whole texture map is still ONE run.

    Parameters
    ----------
    name : str
        Human label.
    prs_range : (start, stop, n)
        In-plane rotation series in degrees.  Default ``(-90, 90, 91)`` (2 deg/step).
    ai0 : float
        Aligned grazing-incidence zero.
    ai : float
        Incident angle (deg) above ``ai0`` to hold during the rock (recorded as a Signal).
    th_axis : positioner, optional
        Grazing-incidence axis (default ``piezo.th``).
    waxs_arc : sequence
        WAXS-arc positions.  If a single value, ``prs`` is the only scanned axis; if multiple,
        the arc becomes a coupled outer axis via ``bp.grid_scan`` (one run).
    t, dets, reads, baseline, md, name_tokens :
        As in :func:`tomography_run`.  ``incident_angle`` is recorded so ``{incident_angle}``
        resolves.
    """
    if th_axis is None:
        th_axis = piezo.th                                         # noqa: F821
    if dets is None:
        dets = tomo_dets()
    incident_angle = Signal(name="incident_angle", value=float(ai))  # noqa: F821
    reads = list(reads or []) + [incident_angle]
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                        # noqa: F821
    start, stop, n = prs_range
    sample_name = fname(name + "_texture", *name_tokens)
    all_dets = list(dets) + reads
    run_md = merge_md(
        {"scan_name": "texture_pole_figure"},
        {"geometry": geometry} if geometry else {},
        md,
        {"sample_name": sample_name},
    )
    arc_vals = list(waxs_arc)

    def _plan():
        yield from bps.mv(th_axis, ai0 + ai)                       # set grazing incidence once
        incident_angle.put(float(ai))
        if len(arc_vals) > 1:
            # prs (in-plane) x waxs.arc texture map, ONE run (Kang grid_scan).
            wa0, wa1 = arc_vals[0], arc_vals[-1]
            yield from bp.grid_scan(all_dets, prs, start, stop, n,      # noqa: F821
                                    waxs, wa0, wa1, len(arc_vals))      # noqa: F821
        else:
            if arc_vals:
                yield from bps.mv(waxs, arc_vals[0])               # noqa: F821
            yield from bp.rel_scan(all_dets, prs, start, stop, n, md=run_md)   # noqa: F821

    body = _plan()
    if baseline:
        body = baseline_wrapper(body, baseline)

    def _cleanup():
        yield from bps.mv(th_axis, ai0)

    return (yield from cleanup_wrapper(body, _cleanup))


# ---------------------------------------------------------------------------
# Multi-sample bar (one rotation series per sample)
# ---------------------------------------------------------------------------
def tomography_bar(samples, *, prs_range=(-90, 90, 181), t=1.0, dets=None,
                   translate_axis=None, translate_range=None, md=None):
    """Run :func:`tomography_run` for each sample on the bar (ONE rotation series per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned (piezo/hexapod) then
    rotated.  ``prs`` is the slow / in-vacuum scanned axis (the rotation series), traversed once
    per sample.  Pass ``translate_axis`` / ``translate_range`` to make each series a coupled
    sinogram.
    """
    for s in samples:
        yield from goto_sample(s)
        yield from tomography_run(
            s.name, prs_range=prs_range, t=t, dets=dets, translate_axis=translate_axis,
            translate_range=translate_range, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """SAXS/WAXS tomography: a -90..+90 deg, 181-pt ``prs`` rotation series on one sample.

    Mirrors ``CFN/Yugang/2026C1_Tomo.py::run_tomo(-90, 91, 181, ...)`` but as ONE run with
    ``prs`` + ``xbpm3`` recorded in-stream.  Run with::

        RE(technique_K_tomography.example())
    """
    bar = SampleList.from_columns(
        names=["FL_S3Cube_2025Q3"],
        piezo_x=[0],
        piezo_y=[0],
        piezo_z=[-9000],
        md={"project_name": "318527_Tomo", "energy_eV": 16100},
    )
    yield from tomography_bar(bar, prs_range=(-90, 90, 181), t=1.0,
                              md={"technique": "SAXS_tomography"})


def example_texture():
    """Texture / pole-figure GIWAXS: rock ``prs`` -90..+90 deg at 0.2 deg incidence, arc=[0,26].

    Mirrors Kang ``rotation_saxs`` (``prs`` x ``waxs.arc`` grid) -- ONE run, with the incident
    angle recorded as a Signal.
    """
    yield from bps.mv(piezo.y, 4810)                              # noqa: F821 (coarse height)
    yield from texture_pole_figure_run(
        "AGIB3N_1mid", prs_range=(-90, 90, 91), ai0=0.0, ai=0.2, waxs_arc=[0, 6.5, 13, 19.5, 26],
        t=1.0, md={"project_name": "Demo_texture"})


def example_sinogram():
    """SAXS sinogram: ``prs`` rotation coupled to a ``stage.x`` translation, ONE run.

    Mirrors the ``legacy/34-oleg.py::aaron_rot`` ``inner_product_scan`` coupling (prs + stage.x
    swept together) collapsed into a single tomography run.
    """
    yield from tomography_run(
        "octahedron_plate_cut", prs_range=(45, -50, 96), t=8.0,
        translate_axis=stage.x, translate_range=(0.3834, -0.0175),  # noqa: F821
        md={"project_name": "Demo_sinogram"})

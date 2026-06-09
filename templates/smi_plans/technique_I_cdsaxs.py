"""
technique_I_cdsaxs
=================

Archetype I -- CD-SAXS / CD-GISAXS critical-dimension grating metrology.

Reconstruct a nanograting line/space cross-section (CD, sidewall angle, height, LER, pitch
walking, overlay) by **rocking the** ``prs`` **(Precision Rotation Stage = phi) through reciprocal
space** and recording one detector frame per angle.  The canonical measurement is ``prs``
**-60 deg -> +60 deg in 121 points** on ``pil2M`` (SAXS); CD-GISAXS rocks ``prs`` (and/or the
grazing incidence axis) at a shallow incidence with many more points (up to ~2001).

THE KEY FIX for CD-SAXS (Tenet 1): a phi rocking curve is **ONE logical experiment = ONE run**.
The dominant legacy form (``legacy/30-user-CDSAXS.py::cd_saxs_new``, ``CFN .../run_tomo``)
encodes a 121-point rock as **121 separate** ``bp.count`` **runs**, with the rocking angle /
x / y / z / SDD / flux stuffed into the filename string via ``.position`` / ``.get()``.  Here a
whole rock is a single ``bp.rel_scan(prs, ...)`` (or one :func:`_core.one_sample_run` with an
``inner()`` doing ``mv(prs)`` + ``trigger_and_read`` per angle), so ``prs`` and the flux
monitors ride in the document stream.

Gold reference: ``CDSAXS/.../test.py::cd_saxs_modern`` and ``legacy/30-user-Kline2.py::
cd_saxs_modern`` -- ``bp.list_scan(dets + [piezo.x, piezo.y, piezo.z, pil2M.sample_distance_mm,
stage_pseudo, xbpm3.sumX], stage_pseudo.phi, ...)``: the whole phi rock is one run with SDD /
phi / flux / positions as stream channels.  Also ``..._simplePRS``
(``rel_scan([pil2M, pin_diode, xbpm3], prs, -60, 60, 121)``).
Legacy per-angle form: ``legacy/30-user-CDSAXS.py`` (``cd_saxs_new``, ``cdsaxs_all_pitch``,
``mesure_rugo`` y-stitch, ``cd_gisaxs_phi`` / ``cd_gisaxs_alphai``), Gergaud, the ``CDSAXS/``
subsystem (``30-user-CDSAXS_Philipp.py``, ``DummyBluSky/plans.py``).

What this file gives you
------------------------
* :func:`cdsaxs_dets` -- the standard CD-SAXS detector + flux-monitor list (``pil2M`` +
  ``pin_diode`` + ``xbpm3``), the reciprocal-space normalization channels.
* :func:`cdsaxs_rock_run` -- ONE run = one full ``prs`` rocking curve on a single grating box.
  Absolute or ``phi_offset``-centered; optional zero-order reference brackets (ref-A/ref-B).
* :func:`cd_gisaxs_rock_run` -- CD-GISAXS: rock ``prs`` (or the grazing th axis) at a fixed
  shallow incidence, ONE run, more points.
* :func:`cdsaxs_pitch_survey` -- multi-pitch x-offset survey: ONE rock-run per pitch column.
* :func:`cdsaxs_ystitch_run` -- detector y-stitch (``pil2M_pos.y`` +/- 4.3 mm) to cover the 2M
  module gap, as two sub-scans (commented tradeoff: across runs vs within one run).
* :func:`cdsaxs_bar` -- loop :func:`cdsaxs_rock_run` over a :class:`SampleList` (one rock/sample),
  with ``prs`` as the scanned slow axis.
* :func:`example` / :func:`example_gisaxs` -- runnable, fully-specified examples.

Idioms preserved (via _preprocessors): zero-order reference brackets (``phi_offset``), the
``pil2M_pos.y`` y-stitch for the module gap, ``xbpm3``/``pin_diode`` I0 normalization recorded
in-stream, baseline capture of the SDD, cleanup (return ``prs`` to its start) on error.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bp`` (bluesky.plans), ``Signal``, ``prs``,
    ``piezo``, ``stage``, ``pil2M``, ``pil2M_pos``, ``pin_diode``, ``xbpm3``,
    ``det_exposure_time``.  ``prs`` is slow and in-vacuum, so it is the scanned axis and the
    coarse (per-box) setup stays outside the rock.
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
    "cdsaxs_dets", "cdsaxs_rock_run", "cd_gisaxs_rock_run", "cdsaxs_pitch_survey",
    "cdsaxs_ystitch_run", "cdsaxs_bar", "example", "example_gisaxs",
]


# ---------------------------------------------------------------------------
# Detector + flux-monitor list
# ---------------------------------------------------------------------------
def cdsaxs_dets(*, saxs_det=None, pin=True, xbpm=True):
    """Return the standard CD-SAXS detector list: SAXS + flux-monitor channels.

    The canonical rock records ``pil2M`` (SAXS) together with ``pin_diode`` (transmitted-beam
    normalization) and ``xbpm3`` (incident-flux monitor).  Both monitors are returned *as
    detectors* so their readings ride in the stream (and ``{xbpm3_sumX}`` /
    ``{pin_diode_current2_mean_value}`` resolve as filename tokens), reproducing the
    ``cd_saxs_modern`` / ``simplePRS`` channel set without baking ``xbpm3.sumX.get()`` into a
    string.
    """
    sdet = saxs_det if saxs_det is not None else pil2M             # noqa: F821
    dets = [sdet]
    if pin:
        dets.append(pin_diode)                                     # noqa: F821
    if xbpm:
        dets.append(xbpm3)                                         # noqa: F821
    return dets


# ---------------------------------------------------------------------------
# Helper: a single rock as one run (rel_scan over prs)
# ---------------------------------------------------------------------------
def _rock_one_run(sample_name, dets, prs_start, prs_stop, n, *, reads=None, baseline=None,
                  scan_name="cdsaxs_rock", geometry="transmission", md=None, relative=True):
    """ONE run: rock ``prs`` from ``prs_start`` to ``prs_stop`` in ``n`` points.

    Uses a coordinated ``bp.rel_scan`` / ``bp.scan`` so ``prs`` (and any extra ``reads``) are
    recorded automatically as event fields -- the whole rocking curve is a single run.  The SDD
    and other constants are recorded once via the baseline.  This is the workhorse the public
    rock plans build on.
    """
    scan = bp.rel_scan if relative else bp.scan
    all_dets = list(dets) + list(reads or [])
    run_md = merge_md(
        {"scan_name": scan_name},
        {"geometry": geometry} if geometry else {},
        md,
        {"sample_name": sample_name},
    )

    def _plan():
        yield from scan(all_dets, prs, prs_start, prs_stop, n, md=run_md)   # noqa: F821

    body = _plan()
    if baseline:
        body = baseline_wrapper(body, baseline)
    return (yield from body)


# ---------------------------------------------------------------------------
# One run = one full rocking curve on a single grating box
# ---------------------------------------------------------------------------
def cdsaxs_rock_run(name, prs_range=(-60, 60, 121), *, t=1.0, dets=None, reads=None,
                    phi_offset=0.0, absolute=False, ref_brackets=True, geometry="transmission",
                    baseline=None, md=None,
                    name_tokens=("sdd{pil2M_sample_distance_mm}", "bpm{xbpm3_sumX}")):
    """ONE run: a full ``prs`` rocking curve (-60 -> +60 deg, 121 pts canonical) on one box.

    The grating box must already be coarse-positioned and aligned (chi/theta leveled, on the
    rotation center) by the caller / :func:`cdsaxs_bar`; this plan only does the rock.  ``prs``
    is the scanned axis and is recorded automatically.

    Parameters
    ----------
    name : str
        Human sample/box label (start of the templated filename).
    prs_range : (start, stop, n)
        Rocking-curve definition in degrees relative to ``phi_offset`` (unless ``absolute``).
        Default ``(-60, 60, 121)`` -- the canonical 1 deg/step rock.
    t : float
        Exposure time (s) per angle.  Use the cos-tilt-corrected variant downstream if you need
        ``exp_t/|cos(phi)|`` flattening at high tilt (legacy ``cd_saxs_newLigang``).
    dets : list, optional
        Detectors.  Default :func:`cdsaxs_dets` (``[pil2M, pin_diode, xbpm3]``).
    reads : list, optional
        Extra readables recorded each angle (default: positions ``[piezo.x, piezo.y, piezo.z]``
        so the box coordinates are in the data, as in ``cd_saxs_modern``).
    phi_offset : float
        The zero-order ``prs`` angle for this grating (legacy ``phi_offset`` / ``theta_zer``);
        the rock is centered here unless ``absolute``.
    absolute : bool
        If True, ``prs_range`` is absolute ``prs`` angles (uses ``bp.scan``); else it is
        relative to the current ``prs`` after moving to ``phi_offset`` (uses ``bp.rel_scan``).
    ref_brackets : bool
        If True (default), bracket the rock with a single-frame zero-order reference *in the
        SAME run sequence* before and after (the legacy ref-A / ref-B brackets, Kline2
        ``measure_ref-A`` / ``measure_ref-B``) -- these are separate short runs so they get their
        own filenames, the standard practice for reference frames.
    geometry : str
        ``"transmission"`` (CD-SAXS) or ``"reflection"`` (CD-GISAXS; prefer
        :func:`cd_gisaxs_rock_run`).
    baseline : list, optional
        Constants to record (default includes SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename (must be recorded fields; SDD + flux here).
    """
    if dets is None:
        dets = cdsaxs_dets()
    if reads is None:
        reads = [piezo.x, piezo.y, piezo.z]                        # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821 (SDD)
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                        # noqa: F821
    start, stop, n = prs_range
    sample_name = fname(name, *name_tokens)

    def _go():
        # Move to the zero-order phi first so a relative rock is centered on it.
        yield from bps.mv(prs, phi_offset)                         # noqa: F821
        # Optional zero-order reference frame BEFORE the rock (own short run / filename).
        if ref_brackets:
            yield from _rock_one_run(
                fname(name + "_ref-A", *name_tokens), dets, 0, 0, 1, reads=reads,
                baseline=baseline, scan_name="cdsaxs_ref", geometry=geometry, md=md,
                relative=True)
        # The rocking curve itself: ONE run over prs.
        yield from _rock_one_run(
            sample_name, dets, start, stop, n, reads=reads, baseline=baseline,
            scan_name="cdsaxs_rock", geometry=geometry, md=md, relative=not absolute)
        # Optional zero-order reference frame AFTER the rock.
        if ref_brackets:
            yield from bps.mv(prs, phi_offset)                     # noqa: F821
            yield from _rock_one_run(
                fname(name + "_ref-B", *name_tokens), dets, 0, 0, 1, reads=reads,
                baseline=baseline, scan_name="cdsaxs_ref", geometry=geometry, md=md,
                relative=True)

    # Always return prs to the zero-order angle, even on error/abort.
    def _cleanup():
        yield from bps.mv(prs, phi_offset)                         # noqa: F821

    return (yield from cleanup_wrapper(_go(), _cleanup))


# ---------------------------------------------------------------------------
# CD-GISAXS: rock at a fixed shallow incidence, more points
# ---------------------------------------------------------------------------
def cd_gisaxs_rock_run(name, *, ai0, ai, phi_offset=0.0, prs_range=(-5, 5, 2001),
                       th_axis=None, t=1.0, dets=None, reads=None, baseline=None, md=None,
                       name_tokens=("ai{incident_angle}", "bpm{xbpm3_sumX}")):
    """ONE run: CD-GISAXS phi rock at a fixed grazing incidence (legacy ``cd_gisaxs_phi``).

    Sets the grazing incidence angle once (``th_axis`` -> ``ai0 + ai``), records it as a Signal,
    then rocks ``prs`` over ``prs_range`` (relative to ``phi_offset``) in a single run.  Far more
    points than transmission CD-SAXS (the legacy default is 2001 over +/-5 deg) because the GI
    rod is sampled finely.

    Parameters
    ----------
    name : str
        Human label.
    ai0 : float
        The aligned grazing-incidence zero for this sample (from alignment).
    ai : float
        Incident angle (deg) above ``ai0`` to hold during the rock.
    phi_offset : float
        Zero-order ``prs`` angle (legacy ``phi0``).
    prs_range : (start, stop, n)
        Rock definition relative to ``phi_offset``.  Default ``(-5, 5, 2001)``.
    th_axis : positioner, optional
        Grazing-incidence axis (default ``stage.th``, the GI double-stack incidence axis used
        in ``cd_gisaxs_phi``).
    t, dets, reads, baseline, md, name_tokens :
        As in :func:`cdsaxs_rock_run`.  ``incident_angle`` is recorded as a Signal so
        ``{incident_angle}`` resolves.
    """
    if th_axis is None:
        th_axis = stage.th                                         # noqa: F821
    if dets is None:
        dets = cdsaxs_dets()
    incident_angle = Signal(name="incident_angle", value=float(ai))  # noqa: F821
    if reads is None:
        reads = [piezo.x, piezo.z, incident_angle]                 # noqa: F821
    else:
        reads = list(reads) + [incident_angle]
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                        # noqa: F821
    start, stop, n = prs_range
    sample_name = fname(name + "_gisaxs", *name_tokens)

    def _go():
        yield from bps.mv(th_axis, ai0 + ai)                       # set grazing incidence once
        yield from bps.mv(prs, phi_offset)                         # noqa: F821
        incident_angle.put(float(ai))
        yield from _rock_one_run(
            sample_name, dets, start, stop, n, reads=reads, baseline=baseline,
            scan_name="cd_gisaxs_rock", geometry="reflection", md=md, relative=True)

    def _cleanup():
        yield from bps.mv(prs, phi_offset)                         # noqa: F821

    return (yield from cleanup_wrapper(_go(), _cleanup))


# ---------------------------------------------------------------------------
# Multi-pitch x-offset survey: ONE rock-run per pitch column
# ---------------------------------------------------------------------------
def cdsaxs_pitch_survey(name, x0, pitches, x_offsets, *, prs_range=(-60, 60, 121), t=1.0,
                        dets=None, phi_offset=0.0, ref_brackets=False, md=None):
    """A multi-pitch survey: step ``piezo.x`` across pitch columns, ONE full rock per column.

    Reproduces ``legacy/30-user-CDSAXS.py::cdsaxs_all_pitch`` (loop ``x + x_off`` over the
    pitch columns, full rock at each), but each pitch column's rock is its OWN run (Tenet 1),
    not 121 runs/column.

    Parameters
    ----------
    name : str
        Base label; the pitch tag is appended per column.
    x0 : float
        ``piezo.x`` of the first pitch column.
    pitches : sequence of str
        Pitch labels (e.g. ``["p112nm", ..., "p128nm"]``), one per column.
    x_offsets : sequence of float
        ``piezo.x`` offset (from ``x0``) for each pitch column.  Same length as ``pitches``.
    prs_range, t, dets, phi_offset, ref_brackets, md :
        Forwarded to :func:`cdsaxs_rock_run` for each column.
    """
    if len(pitches) != len(x_offsets):
        raise ValueError("pitches ({}) and x_offsets ({}) must be the same length"
                         .format(len(pitches), len(x_offsets)))
    for pitch, x_off in zip(pitches, x_offsets):
        yield from bps.mv(piezo.x, x0 + x_off)                     # noqa: F821
        yield from cdsaxs_rock_run(
            name + "_" + pitch, prs_range=prs_range, t=t, dets=dets, phi_offset=phi_offset,
            ref_brackets=ref_brackets, md=merge_md(md, {"pitch": pitch}))


# ---------------------------------------------------------------------------
# Detector y-stitch (cover the 2M module gap)
# ---------------------------------------------------------------------------
def cdsaxs_ystitch_run(name, prs_range=(-60, 60, 121), *, t=1.0, dets=None, phi_offset=0.0,
                       y_shift_mm=4.3, md=None):
    """Two rocks at ``pil2M_pos.y`` +/- ``y_shift_mm`` to stitch across the 2M module gap.

    At large tilt the rod walks off the 2M onto the inter-module gap; the legacy fix
    (``mesure_rugo`` ``_up`` / ``_down``) shifts the detector by 4.3 mm and re-rocks, then
    stitches the two stacks offline.

    Tradeoff (commented on purpose):
      * **Two runs** (the form used here) -- the SDD/detector-position differs between the two
        halves, so they are genuinely different *configurations*; each gets its own baseline
        (``pil2M_pos.y`` is constant *within* each run) and its own filename ``_yA`` / ``_yB``.
        This is the cleaner choice and the one Tenet 2 favors (constant-per-run -> baseline).
      * **One run, two streams** -- you *could* keep both halves in a single run if you declared
        a separate stream per detector position and recorded ``pil2M_pos.y`` in the primary
        stream (since it then *changes* within the run).  That couples two configurations into
        one run for the convenience of a single id; we avoid it here.
    """
    if dets is None:
        dets = cdsaxs_dets()
    # Half A: detector at +y_shift_mm/2.
    yield from bps.mvr(pil2M_pos.y, y_shift_mm)                    # noqa: F821
    yield from cdsaxs_rock_run(name + "_yA", prs_range=prs_range, t=t, dets=dets,
                               phi_offset=phi_offset, ref_brackets=False,
                               md=merge_md(md, {"ystitch": "A"}))
    # Half B: detector back and at -y_shift_mm/2 relative to A (net -y_shift_mm from A).
    yield from bps.mvr(pil2M_pos.y, -y_shift_mm)                   # noqa: F821
    yield from cdsaxs_rock_run(name + "_yB", prs_range=prs_range, t=t, dets=dets,
                               phi_offset=phi_offset, ref_brackets=False,
                               md=merge_md(md, {"ystitch": "B"}))


# ---------------------------------------------------------------------------
# Multi-sample bar (one rocking-curve run per grating box)
# ---------------------------------------------------------------------------
def cdsaxs_bar(samples, *, prs_range=(-60, 60, 121), t=1.0, dets=None, phi_offset=0.0,
               ref_brackets=True, md=None):
    """Rock each grating box on the bar; ONE run (one full ``prs`` rock) per box.

    ``samples`` is a :class:`SampleList`.  Each box is coarse-positioned (piezo x/y/z and, if
    set, chi via ``hexa_*`` or the sample md) and then rocked.  ``prs`` is the slow / in-vacuum
    scanned axis (the rocking curve), traversed once per box.  Per-sample ``phi_offset`` can be
    supplied in the sample's md as ``{"phi_offset": <deg>}``; otherwise the shared default is
    used.

    Note: chi/theta leveling and rotation-center alignment are prerequisites (see
    ``folder_CDSAXS.md`` and the ``CDSAXS/`` auto-alignment subsystem); this plan assumes each
    box is already aligned, recording the box coordinates per angle so provenance is complete.
    """
    for s in samples:
        yield from goto_sample(s)
        phi = float(s.md.get("phi_offset", phi_offset))
        yield from cdsaxs_rock_run(
            s.name, prs_range=prs_range, t=t, dets=dets, phi_offset=phi,
            ref_brackets=ref_brackets, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """3-box CD-SAXS bar: full -60..+60 deg 121-pt rock per box, with ref brackets.

    ``prs`` (the in-vacuum rotation stage) is the scanned axis; each box's rock is ONE run with
    ``pil2M`` + ``pin_diode`` + ``xbpm3`` and the box coordinates recorded in-stream.  Run
    with::

        RE(technique_I_cdsaxs.example())
    """
    bar = SampleList.from_columns(
        names=["w03_c0_p113", "w03_c1_p113", "w03_c2_p113"],
        piezo_x=[-35050, -9150, 16950],
        piezo_y=[-4400, -4400, -4500],
        piezo_z=[10900, 10000, 9100],
        md={"project_name": "311003_CDSAXS_Demo", "energy_eV": 16100},
    )
    yield from cdsaxs_bar(bar, prs_range=(-60, 60, 121), t=1.0, phi_offset=0.0,
                          ref_brackets=True, md={"technique": "CD-SAXS"})


def example_gisaxs():
    """CD-GISAXS: a fine 2001-pt phi rock at a 0.45 deg grazing incidence on one grating.

    Mirrors ``legacy/30-user-CDSAXS.py::nigh_cdgisaxs`` -> ``cd_gisaxs_phi`` but as ONE run with
    the incident angle recorded as a Signal.
    """
    yield from bps.mv(piezo.x, 23000, piezo.z, 6300)               # noqa: F821 (coarse box)
    yield from cd_gisaxs_rock_run(
        "w03_c-3_p100nm", ai0=0.29614, ai=0.45, phi_offset=-3.33,
        prs_range=(-5, 5, 2001), t=0.5, md={"project_name": "311003_CDGISAXS_Demo"})

"""
technique_O_commissioning
=========================

Archetype O -- Beamline-staff calibration / commissioning utilities.

Reusable *staff* tools -- detector-distance / beam-center calibration, attenuator-ladder
characterization, direct-beam checks -- written in the modern single-run style so the
commissioning data is as well-provenanced as user data (recorded context, ``md={}`` intent,
filenames templated from recorded fields).  These replace the Tier-1 commissioning scripts
(``bp.count`` per point + ``sample_id`` + ``.get()``-into-name) with single coordinated runs.

Gold / legacy references (READ THESE):

* ``Commissioning/AGB_scan.py`` -- AgBehenate SDD scan (``AGB_scan`` steps ``pil2M.motor.z``
  1.7--9 m with attenuators in; ``AGB_scan2`` is a ``grid_scan`` x/y/z survey).  Modernized in
  :func:`agbh_calibration_run` (records SDD + energy; one run).
* ``Commissioning/attenuation_testing.py`` -- attenuator-ladder transmission
  (``attenuation_test_on_pindiode`` steps ``att1_5..att1_12`` recording ``pin_diode``).
  Modernized in :func:`attenuator_ladder_run` (one run; transmitted flux + the combination
  label recorded as Signals).
* ``Commissioning/bounce_down_mirror.py`` -- mirror bounce-down XRR (NOT duplicated here; see
  :func:`technique_J_xrr.xrr_liquid_run` / ``run_xrr_bdm_saxs`` for the modern XRR form).

What this file gives you
------------------------
* :func:`agbh_calibration_run` -- AgBehenate calibration: SAXS+WAXS count(s) on the AgBH
  standard, SDD (``pil2M_pos.z``) + energy + beam-center ROI totals recorded; optional SDD scan.
* :func:`attenuator_ladder_run` -- step through attenuator combinations recording transmitted
  flux (``pin_diode``) + the combination label, to characterize the ladder; ONE run.
* :func:`direct_beam_scan_run` -- a quick direct-beam center / intensity check (knife-edge-free
  beam-center via a small ``rel_grid_scan``, or a simple direct-beam count).
* :func:`example` / :func:`example_attenuators` -- runnable examples.

XRR / mirror bounce-down
------------------------
This file deliberately does **not** re-implement the bounce-down-mirror XRR toolkit.  For
specular reflectivity (incl. liquid surfaces via ``bdm.th``) use **``technique_J_xrr``** --
``xrr_run`` / ``xrr_liquid_run`` mirror ``Commissioning/bounce_down_mirror.py`` exactly
(``incident_angle`` recorded as a Signal, angle-dependent attenuator ladder, one run per sweep).

Idioms preserved (via _preprocessors): ensure attenuators in (calibration is always done WITH
the right attenuation), baseline capture of constants (SDD, energy, beam-center), cleanup
(restore exposure / attenuator state) on error.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bp`` (bluesky.plans), ``Signal``, ``piezo``,
    ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``pil2M_pos``, ``pin_diode``, ``xbpm2``,
    ``xbpm3``, ``det_exposure_time``, and the attenuator devices (``att1_5``..``att1_12`` /
    ``att2_*``) you pass in.  ``pil2M.motor.z`` (detector translation) is used for the SDD scan.
"""

from ._samples import SampleList
from ._core import (one_sample_run, fname, merge_md)
from ._preprocessors import (ensure_in_wrapper, cleanup_wrapper, baseline_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.plans as bp
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bp = None
    bpp = None


__all__ = [
    "agbh_calibration_run", "attenuator_ladder_run", "direct_beam_scan_run",
    "example", "example_attenuators",
]


# ---------------------------------------------------------------------------
# AgBehenate SDD / beam-center calibration
# ---------------------------------------------------------------------------
def agbh_calibration_run(*, name="AgBH", t=1.0, dets=None, reads=None, sdd_positions=None,
                         sdd_axis=None, atten_in=None, baseline=None, geometry="transmission",
                         md=None, name_tokens=("sdd{pil2M_pos_z}mm", "{energy_energy}eV")):
    """ONE run: AgBehenate SDD / beam-center calibration with SAXS + WAXS.

    AgBehenate (silver behenate) is the standard calibrant: its sharp, known d-spacing rings let
    you solve the sample-to-detector distance (SDD) and beam center.  This records a count on
    the AgBH standard with both detectors, with the **SDD (``pil2M_pos.z``) and energy in the
    baseline** (the calibration constants) and the beam-center ROI totals in the stream --
    instead of the legacy ``AGB_scan`` which baked ``get_scan_md()`` into the name and ran
    ``bp.count`` per detector-z step.

    Optionally sweep the detector distance (``sdd_positions``): each distance is recorded as an
    event (SDD is a *changing* primary-stream field then), so one run captures the whole SDD
    series with ``{pil2M_pos_z}`` resolving per frame.

    Parameters
    ----------
    name : str
        Label (start of the templated filename); default ``"AgBH"``.
    t : float
        Exposure time (s).
    dets : list, optional
        Default ``[pil2M, pil900KW, xbpm2, xbpm3]`` (SAXS + WAXS + I0).
    reads : list, optional
        Extra readables recorded each event.  Default ``[energy, pil2M_pos.z, xbpm2, xbpm3]`` so
        ``{energy_energy}`` and ``{pil2M_pos_z}`` resolve.
    sdd_positions : sequence of float, optional
        If given, detector ``sdd_axis`` is stepped through these (mm) and one event recorded at
        each (an SDD scan, e.g. ``np.linspace(1700, 9000, 74)`` -- the ``AGB_scan`` range in
        mm).  If ``None``, a single count at the current SDD.
    sdd_axis : ophyd positioner, optional
        The detector-distance axis to scan.  Default ``pil2M.motor.z`` (the SAXS detector z).
    atten_in : callable () -> plan, optional
        Plan that puts the calibration attenuator in (AgBH is bright; you usually attenuate).
        Runs once at run open.  E.g. ``lambda: bps.mv(att1_7, "insert")`` wrapped.
    baseline : list, optional
        Constants recorded once.  ``energy`` and (if not scanned) SDD ``pil2M_pos.z`` are added.
    geometry : str
        Default ``"transmission"`` (AgBH is a transmission standard).
    md : dict, optional
        Caller intent merged in.
    name_tokens : tuple of str
        ``{field}`` tokens; default references recorded ``{pil2M_pos_z}`` and ``{energy_energy}``.
    """
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                  # noqa: F821
    if reads is None:
        try:
            reads = [energy, pil2M_pos.z, xbpm2, xbpm3]         # noqa: F821
        except Exception:
            reads = [energy, xbpm2, xbpm3]                      # noqa: F821
    _sdd_axis = sdd_axis if sdd_axis is not None else pil2M.motor.z  # noqa: F821

    base = list(baseline) if baseline else []
    base = base + [energy]                                      # noqa: F821 (calibration energy)
    if sdd_positions is None:
        try:
            base = base + [pil2M_pos.z]                        # noqa: F821 (constant SDD)
        except Exception:
            pass

    det_exposure_time(t, t)                                     # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        if sdd_positions is None:
            yield from bps.trigger_and_read(list(dets) + list(reads))
        else:
            for z in sdd_positions:                             # SDD scan: one event per distance
                yield from bps.mv(_sdd_axis, z)
                yield from bps.sleep(0.5)                        # let the detector settle
                yield from bps.trigger_and_read(list(dets) + list(reads))

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="agbh_calibration", geometry=geometry,
                          md=merge_md({"calibrant": "AgBehenate"}, md), baseline=base)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Attenuator-ladder transmission characterization
# ---------------------------------------------------------------------------
def attenuator_ladder_run(attenuators, *, name="atten_ladder", t=2.0, dets=None, reads=None,
                          flux_det=None, in_cmd="insert", out_cmd="retract", settle=1.0,
                          always_in=None, baseline=None, geometry="transmission", md=None,
                          name_tokens=("{atten_label}", "pd{pin_diode_current2_mean_value}")):
    """ONE run: step through attenuator combinations, recording transmitted flux per setting.

    Characterizes the attenuator ladder by inserting each attenuator (one at a time), recording
    the transmitted flux on ``flux_det`` (``pin_diode``), then retracting it -- the
    ``attenuation_testing.py`` procedure, but as a single run where the **combination label and
    the transmitted flux are recorded** (label as a string Signal -> ``{atten_label}`` token;
    ``pin_diode`` in the stream) instead of ``sample_id('direct_beam', f'..._att1_{j}_...')`` +
    ``bp.count`` per setting.

    Parameters
    ----------
    attenuators : sequence
        The attenuator devices to characterize one at a time (e.g.
        ``[att1_5, att1_6, ..., att1_12]``).  Each must accept ``bps.mv(att, in_cmd/out_cmd)``.
    name : str
        Label (start of the templated filename).
    t : float
        Exposure / averaging time (s); applied to detectors and ``pin_diode.averaging_time``.
    dets : list, optional
        Detectors to STAGE.  Default ``[flux_det, pil2M]`` (flux monitor + an image for the
        direct beam, as ``attenuation_testing`` records ``[pin_diode, pil2M]``).
    reads : list, optional
        Extra readables recorded each event.  Default ``[flux_det, xbpm2, xbpm3]``.
    flux_det : ophyd readable, optional
        The transmitted-flux detector.  Default ``pin_diode``.
    in_cmd, out_cmd : str
        Commands to insert / retract an attenuator (default ``"insert"`` / ``"retract"`` per
        ``attenuation_testing``; some ladders use ``"in"`` / ``"out"``).
    settle : float
        Sleep (s) after moving an attenuator before measuring.
    always_in : callable () -> plan, optional
        Plan to put a fixed set in for the whole scan (e.g. keep ``att1_6``/``att1_7`` in the
        whole time, as ``attenuation_test_no_beamstop`` does).  Runs once at run open.
    baseline : list, optional
        Constants recorded once (energy added).
    geometry : str
        Default ``"transmission"`` (direct-beam characterization).
    md : dict, optional
        Caller intent merged in.
    name_tokens : tuple of str
        ``{field}`` tokens; default references recorded ``{atten_label}`` and the pin-diode flux.

    Notes
    -----
    A baseline frame with **no** test attenuator is taken first (label ``"none"``) so you have a
    reference flux to normalize transmissions against, all within the one run.
    """
    fdet = flux_det if flux_det is not None else pin_diode      # noqa: F821
    if dets is None:
        dets = [fdet, pil2M]                                    # noqa: F821
    if reads is None:
        reads = [fdet, xbpm2, xbpm3]                            # noqa: F821

    # The active-attenuator label as a recorded (string) Signal -> {atten_label} token.
    atten_label = Signal(name="atten_label", value="none")     # noqa: F821
    reads = list(reads) + [atten_label]

    base = list(baseline) if baseline else []
    base = base + [energy]                                      # noqa: F821

    det_exposure_time(t, t)                                     # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        # pin_diode averaging follows the exposure time (legacy idiom).
        try:
            yield from bps.mv(fdet.averaging_time, t)           # noqa: F821
        except Exception:
            pass
        # 1) reference frame with no test attenuator in.
        atten_label.put("none")
        yield from bps.sleep(settle)
        yield from bps.trigger_and_read(list(dets) + list(reads))
        # 2) each attenuator in turn: insert -> record -> retract.
        for att in attenuators:
            yield from bps.mv(att, in_cmd)
            atten_label.put(getattr(att, "name", str(att)))
            yield from bps.sleep(settle)
            yield from bps.trigger_and_read(list(dets) + list(reads))
            yield from bps.mv(att, out_cmd)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="attenuator_ladder", geometry=geometry,
                          md=merge_md({"purpose": "attenuator_characterization"}, md),
                          baseline=base)
    if always_in is not None:
        plan = ensure_in_wrapper(plan, always_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Quick direct-beam center / intensity check
# ---------------------------------------------------------------------------
def direct_beam_scan_run(*, name="direct_beam", t=0.3, dets=None, reads=None, mode="count",
                         x_axis=None, y_axis=None, x_range=3, y_range=3, x_num=7, y_num=7,
                         atten_in=None, baseline=None, geometry="transmission", md=None,
                         name_tokens=("db", "bpm{xbpm2_sumX}")):
    """ONE run: a quick direct-beam center / intensity check.

    Two modes:

    * ``mode="count"`` -- a single short count on the direct beam (with attenuators in) to read
      the beam-center ROI totals / intensity; the fast "is the beam where I expect, how bright?"
      check.
    * ``mode="map"`` -- a small ``rel_grid_scan`` of the detector position (or any provided
      ``x_axis``/``y_axis``) to map the direct-beam center as a single run (the modern,
      run-per-map form, vs. the legacy per-point ``bp.count``).

    Parameters
    ----------
    name : str
        Label (start of the templated filename).
    t : float
        Exposure time (s); default 0.3 (a quick check, matching the commissioning idiom).
    dets : list, optional
        Default ``[pil2M, xbpm2, xbpm3]``.
    reads : list, optional
        Default ``[xbpm2, xbpm3]``.
    mode : {"count", "map"}
        ``"count"`` for a single direct-beam frame; ``"map"`` for a beam-center grid scan.
    x_axis, y_axis : ophyd positioners, optional
        Axes to scan in ``"map"`` mode.  Default ``pil2M.motor.x`` / ``pil2M.motor.y``
        (detector translation) -- the ``AGB_scan2`` x/y survey idea.
    x_range, y_range : float
        Half-ranges for the ``rel_grid_scan`` (in the axis' units).
    x_num, y_num : int
        Point counts per axis in ``"map"`` mode.
    atten_in : callable () -> plan, optional
        Put attenuators in before measuring the direct beam (you should -- it is bright).
    baseline : list, optional
        Constants recorded once (energy + SDD added if available).
    geometry : str
        Default ``"transmission"``.
    md : dict, optional
        Caller intent merged in.
    name_tokens : tuple of str
        ``{field}`` tokens; default references the recorded ``{xbpm2_sumX}``.

    Notes
    -----
    In ``"map"`` mode the scanned axes are carried in the run as stream detectors automatically
    by ``rel_grid_scan``; the beam-center is then derived from the recorded ROI-total vs
    position, not from a hand-formatted filename.
    """
    if dets is None:
        dets = [pil2M, xbpm2, xbpm3]                            # noqa: F821
    if reads is None:
        reads = [xbpm2, xbpm3]                                 # noqa: F821
    _x = x_axis if x_axis is not None else pil2M.motor.x        # noqa: F821
    _y = y_axis if y_axis is not None else pil2M.motor.y        # noqa: F821

    base = list(baseline) if baseline else []
    base = base + [energy]                                      # noqa: F821
    try:
        base = base + [pil2M_pos.z]                            # noqa: F821 (SDD)
    except Exception:
        pass

    det_exposure_time(t, t)                                     # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        if mode == "map":
            # A single-run beam-center map (rel_grid_scan emits its own events).
            yield from bp.rel_grid_scan(                        # noqa: F821
                list(dets) + list(reads),
                _y, -y_range, y_range, int(y_num),             # outer (slow)
                _x, -x_range, x_range, int(x_num),             # inner (fast)
                snake_axes=True)
        else:
            yield from bps.trigger_and_read(list(dets) + list(reads))

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="direct_beam_check", geometry=geometry,
                          md=merge_md({"purpose": "direct_beam"}, md), baseline=base)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """AgBehenate calibration with an SDD scan from 1.7 m to 9 m, attenuators in.

    Modern replacement for ``Commissioning/AGB_scan.py``: ONE run, SDD recorded per frame as
    ``{pil2M_pos_z}``, energy in the baseline.  Run with::

        RE(technique_O_commissioning.example())
    """
    def _atten_in():
        yield from bps.mv(att1_7, "insert")                    # noqa: F821
        yield from bps.sleep(1)

    yield from agbh_calibration_run(
        name="AgBH", t=1.0,
        sdd_positions=np.linspace(1700, 9000, 74),             # noqa: F821 (mm; AGB_scan range)
        atten_in=_atten_in,
        md={"project_name": "commissioning", "operator": "staff"},
    )


def example_attenuators():
    """Characterize the att1 ladder (att1_5..att1_12, skipping att1_8) on the pin diode.

    Modern replacement for ``Commissioning/attenuation_testing.py``: ONE run, transmitted flux
    + combination label recorded per setting.  ``att1_5``..``att1_12`` are profile-collection
    globals; pass whichever subset you want to characterize.  Run with::

        RE(technique_O_commissioning.example_attenuators())
    """
    from IPython import get_ipython
    ns = get_ipython().user_ns
    attenuators = [ns["att1_{}".format(j)] for j in range(5, 13) if j != 8]

    # Keep the standard pair in the whole time (as attenuation_test_no_beamstop does).
    def _always_in():
        yield from bps.mv(att1_6, "insert")                    # noqa: F821
        yield from bps.mv(att1_7, "insert")                    # noqa: F821
        yield from bps.sleep(1)

    yield from attenuator_ladder_run(
        attenuators, name="att1_ladder", t=2.0,
        always_in=_always_in,
        md={"project_name": "commissioning", "ladder": "att1"},
    )

"""
technique_G_humidity
====================

Archetype G -- Humidity / RH-controlled in-situ (solvent-vapor annealing, SVA).

Solvent-vapor annealing and controlled-humidity swelling kinetics.  The relative humidity at
the sample is set by mixing **dry and wet N2** through two mass-flow controllers (MFCs); the
sample equilibrates (minutes to tens of minutes) and is then measured -- often as an
RH *program* (a ladder of setpoints) or an RH-held *swelling kinetics* time series.

The dominant legacy form (``legacy/30-user-ETsai.py::run_gi_humid``,
``legacy/30-user-Jones.py::run_gi_humid``, ``legacy/30-user-Richter.py::SVA_night_*``,
``legacy/30-user-Mao.py``) reads the live humidity with ``readHumidity()`` and **bakes the
number into the filename string** (``humidity = "%3.2f" % readHumidity(verbosity=0)``), then
takes ``bp.count(num=1)`` per point inside ``for nn in range(Nmax)`` -- one run per frame.

This file fixes both: each RH setpoint / kinetics window is ONE run; the *live* humidity is
recorded as an ``rh`` ``Signal`` (set from ``readHumidity()`` just before each event) so
``{rh}`` is a filename token resolved from the recorded stream, while the *setpoint* (and the
dry/wet flow setpoints) go in the baseline as constants for that run.

Gold / legacy reference: ``legacy/30-user-Richter.py::SVA_night_12_02`` (dry/wet flow program +
40-min equilibration + Cl-edge measurement), ``legacy/30-user-ETsai.py::run_gi_humid`` and
``legacy/30-user-Jones.py::run_gi_humid`` (per-frame ``readHumidity`` into the name),
``legacy/30-user-Mao.py`` (RH cycling).  Profile-collection MFC helpers used bare:
``setDryFlow``, ``setWetFlow``, ``readHumidity``, ``set_humidity``.

What this file gives you
------------------------
* :func:`set_rh` -- ramp the dry/wet flows toward a target and wait (poll ``readHumidity`` with
  a timeout) for equilibration.  A setup plan, used by the runs below.
* :func:`rh_point` -- inner per-event measurement that stamps the *live* ``rh`` from
  ``readHumidity()`` and records one event (so ``{rh}`` resolves).
* :func:`rh_step_series_run` -- ONE run spanning an RH *program* for a sample: for each RH
  setpoint, equilibrate then take ``measure_at_rh`` events recording live RH.
* :func:`rh_swelling_kinetics_run` -- ONE run: hold one RH setpoint and follow swelling as a
  time series of events (each recording live RH + elapsed time).
* :func:`rh_step_series_bar` -- loop :func:`rh_step_series_run` over a :class:`SampleList`.
* :func:`example` / :func:`example_swelling` -- runnable, fully-specified examples.

Pairing with grazing geometry
------------------------------
GISAXS/GIWAXS swelling under RH is common.  This file imports nothing from
``technique_B_grazing`` (to stay decoupled), but the runs accept ``geometry="reflection"`` and
a per-event ``measure`` so you can compose them with grazing positioning: align the sample
first (``align_sample`` in ``technique_B_grazing``), pass ``geometry="reflection"`` and a
``reads`` list including the incident-angle Signal, and the RH machinery here handles the
humidity program around your grazing measurement.

Idioms preserved (via _preprocessors): ensure attenuators in, baseline capture of the RH /
flow setpoints, cleanup (restore dry-flush) on error.  Long equilibration is done with
``bps.sleep`` inside the generator, never wall-clock ``time.sleep`` outside it.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bpp``, ``Signal``, ``piezo``, ``stage``,
    ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``,
    ``att2_9``, ``det_exposure_time``, and the MFC / humidity profile functions ``setDryFlow``,
    ``setWetFlow``, ``readHumidity``, ``set_humidity``.
"""

import time

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, saxs_waxs_dets, fname, merge_md)
from ._preprocessors import (ensure_in_wrapper, cleanup_wrapper, baseline_wrapper,
                             fresh_spot_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "set_rh", "rh_point", "rh_step_series_run", "rh_swelling_kinetics_run",
    "rh_step_series_bar", "example", "example_swelling",
]


# ---------------------------------------------------------------------------
# RH control: ramp the MFC flows and equilibrate (poll with a timeout)
# ---------------------------------------------------------------------------
def set_rh(target, *, dry_flow=None, wet_flow=None, total_flow=5.0, tol=2.0,
           timeout=1800.0, poll=10.0, settle=0.0):
    """Drive the dry/wet MFCs toward ``target`` %RH and wait for equilibration.

    Two ways to set the flows:

    * If ``dry_flow`` and ``wet_flow`` are given, those exact flows are commanded (the
      explicit Richter ``setDryFlow``/``setWetFlow`` form).
    * Otherwise the wet fraction is estimated as ``target/100`` of ``total_flow`` and the dry
      fraction is the remainder (a reasonable first guess; the *measured* RH is what gets
      recorded, so the estimate need not be exact).

    Then poll ``readHumidity()`` every ``poll`` seconds until it is within ``tol`` of
    ``target`` or ``timeout`` seconds elapse (whichever first).  This is a *setup* plan; run it
    before opening the measurement run (the setpoint is recorded in the run's baseline).

    Parameters
    ----------
    target : float
        Target relative humidity (%RH).
    dry_flow, wet_flow : float, optional
        Explicit MFC flows (overrides the estimate).
    total_flow : float
        Total N2 flow when estimating the wet/dry split.
    tol : float
        Consider equilibrated when ``|readHumidity() - target| <= tol``.
    timeout : float
        Give up waiting after this many seconds (proceed anyway; the recorded RH tells the
        truth).
    poll : float
        Seconds between humidity polls.
    settle : float
        Extra sleep after equilibration (let the film catch up to the gas).

    Notes
    -----
    Returns nothing; the *live* RH is recorded per event by :func:`rh_point`, and the
    *setpoint* should be put in the run baseline by the caller.
    """
    if dry_flow is not None and wet_flow is not None:
        wet = float(wet_flow)
        dry = float(dry_flow)
    else:
        frac = max(0.0, min(1.0, float(target) / 100.0))
        wet = total_flow * frac
        dry = total_flow * (1.0 - frac)

    # MFC profile helpers are plain functions (not plan stubs); call them, then sleep in-plan.
    setWetFlow(wet)                                              # noqa: F821
    setDryFlow(dry)                                             # noqa: F821

    waited = 0.0
    while waited < timeout:
        try:
            rh_now = float(readHumidity(verbosity=0))           # noqa: F821
        except Exception:
            rh_now = None
        if rh_now is not None and abs(rh_now - float(target)) <= tol:
            break
        yield from bps.sleep(poll)
        waited += poll
    if settle:
        yield from bps.sleep(settle)


# ---------------------------------------------------------------------------
# Inner per-event measurement (records LIVE humidity)
# ---------------------------------------------------------------------------
def rh_point(dets, reads, rh_sig, *, settle=0.0, elapsed_sig=None, t0=None):
    """Read the live humidity into ``rh_sig`` and record ONE event (so ``{rh}`` resolves).

    ``rh_sig`` is a ``Signal``; its value is set from ``readHumidity()`` here and then read, so
    the *recorded* humidity (not a string) drives the ``{rh}`` filename token.  If
    ``elapsed_sig``/``t0`` are given, the elapsed time is also stamped (for kinetics).
    """
    if settle:
        yield from bps.sleep(settle)
    try:
        rh_sig.put(float(readHumidity(verbosity=0)))            # noqa: F821
    except Exception:
        pass                                                    # keep last value on a read glitch
    extra = [rh_sig]
    if elapsed_sig is not None and t0 is not None:
        elapsed_sig.put(time.monotonic() - t0)
        extra.append(elapsed_sig)
    yield from bps.trigger_and_read(list(dets) + list(reads) + extra)


# ---------------------------------------------------------------------------
# One run = one sample, an RH program (ladder of setpoints)
# ---------------------------------------------------------------------------
def rh_step_series_run(name, rh_setpoints, *, measure_at_rh=1, t=1.0, dets=None, reads=None,
                       geometry="transmission", equilibration_timeout=1800.0,
                       equilibration_tol=2.0, settle=0.0, measure=None, dose_motor=None,
                       dose_step=None, atten_in=None, baseline=None, md=None,
                       name_tokens=("rh{rh}", "set{rh_setpoint}")):
    """ONE run: step through ``rh_setpoints`` for a single sample, recording live RH.

    For each setpoint: ramp the flows + equilibrate (:func:`set_rh`), then take
    ``measure_at_rh`` events -- each recording the *live* ``rh`` and the (baseline-constant)
    ``rh_setpoint``.  This collapses the legacy "set flow, sleep, ``bp.count`` per frame across
    a ladder" into a single, searchable run spanning the whole RH program.

    Parameters
    ----------
    name : str
        Human sample label.
    rh_setpoints : sequence of float
        The RH ladder (%RH), in the order to visit them (consider an up- then down-ramp to
        check hysteresis).
    measure_at_rh : int
        Number of events to record at each (equilibrated) setpoint.  Ignored if ``measure`` is
        given.
    t : float
        Exposure time (s).
    dets : list, optional
        Default ``[pil2M, pil900KW, xbpm2, xbpm3]``.
    reads : list, optional
        Default ``[energy, waxs, xbpm2, xbpm3]``.
    geometry : str
        ``"transmission"`` or ``"reflection"`` (pair with grazing positioning for GISAXS-SVA).
    equilibration_timeout, equilibration_tol : float
        Passed to :func:`set_rh`.
    settle : float
        Extra sleep after each event (e.g. let a slow film relax).
    measure : callable(rh_setpoint, rh_sig) -> plan, optional
        Custom per-setpoint measurement (e.g. an energy sweep at each RH).  It must record
        events itself (typically via :func:`rh_point` so ``{rh}`` still resolves), but must NOT
        open/close runs.  Overrides ``measure_at_rh``.
    dose_motor, dose_step : optional
        Fresh-spot dose walk after every frame.
    atten_in : callable () -> plan, optional
        Measurement-configuration guard (runs once at run open).
    baseline : list, optional
        Constants recorded once.  The RH setpoint Signal is always added.
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens; default references recorded ``{rh}`` (live) and ``{rh_setpoint}``.
    """
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821

    # Live RH (changes -> stream) and the setpoint (constant per event -> recorded too).
    rh = Signal(name="rh", value=0.0)                          # noqa: F821
    rh_setpoint = Signal(name="rh_setpoint", value=0.0)        # noqa: F821

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                             # noqa: F821 (SDD)
    except Exception:
        pass
    base = base + [rh_setpoint]                                 # setpoint travels in baseline

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        for sp in rh_setpoints:
            yield from set_rh(sp, tol=equilibration_tol, timeout=equilibration_timeout)
            rh_setpoint.put(float(sp))
            if measure is not None:
                yield from measure(sp, rh)
            else:
                for _ in range(int(measure_at_rh)):
                    yield from rh_point(dets, reads + [rh_setpoint], rh, settle=settle)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="rh_step_series", geometry=geometry,
                          md=md, baseline=base)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# One run = one sample, hold RH and follow swelling in time
# ---------------------------------------------------------------------------
def rh_swelling_kinetics_run(name, target_rh, *, n_frames=None, duration=None, period=5.0,
                             t=1.0, dets=None, reads=None, geometry="reflection",
                             equilibration_timeout=1800.0, equilibration_tol=2.0,
                             ramp_during=False, dose_motor=None, dose_step=None, atten_in=None,
                             baseline=None, md=None,
                             name_tokens=("rh{rh}", "t{elapsed_s}s", "n{frame_index}")):
    """ONE run: hold ``target_rh`` and follow swelling as a time series (live RH + elapsed).

    Combines this archetype with the time-series idea of ``technique_F``: optionally let the
    RH ramp toward ``target_rh`` *while measuring* (``ramp_during=True``, to capture the
    swelling transient as the humidity rises), or equilibrate first then hold.  Each event
    records the live ``rh`` and ``elapsed_s`` -- both as recorded Signals, never strings.

    Parameters
    ----------
    name : str
        Human sample label.
    target_rh : float
        RH setpoint (%RH) to hold.
    n_frames : int, optional
        Number of timed events (or use ``duration``).
    duration : float, optional
        Total run length (s); frames until elapsed >= duration.
    period : float
        Sleep (s) between frames.
    t : float
        Exposure time (s).
    ramp_during : bool
        If True, command the flows then begin the time series immediately (capture the rise).
        If False, equilibrate (:func:`set_rh`) before the first frame.
    dets, reads, geometry, dose_motor, dose_step, atten_in, baseline, md, name_tokens :
        As in :func:`rh_step_series_run` / :func:`technique_F_kinetics.time_series_run`.
    """
    if n_frames is None and duration is None:
        raise ValueError("Pass either n_frames or duration to bound the kinetics series.")
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821

    rh = Signal(name="rh", value=0.0)                          # noqa: F821
    rh_setpoint = Signal(name="rh_setpoint", value=float(target_rh))  # noqa: F821
    elapsed = Signal(name="elapsed_s", value=0.0)              # noqa: F821
    frame_index = Signal(name="frame_index", value=0)         # noqa: F821

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                             # noqa: F821
    except Exception:
        pass
    base = base + [rh_setpoint]

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        if ramp_during:
            # Start the flows, do not wait -- capture the swelling transient as RH rises.
            yield from set_rh(target_rh, tol=equilibration_tol, timeout=0.0)
        else:
            yield from set_rh(target_rh, tol=equilibration_tol, timeout=equilibration_timeout)
        t0 = time.monotonic()
        i = 0
        while True:
            if duration is not None and (time.monotonic() - t0) >= duration:
                break
            if n_frames is not None and i >= n_frames:
                break
            frame_index.put(i)
            yield from rh_point(dets, reads + [rh_setpoint, frame_index], rh,
                                elapsed_sig=elapsed, t0=t0)
            i += 1
            if n_frames is not None and i >= n_frames:
                break
            yield from bps.sleep(period)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="rh_swelling_kinetics", geometry=geometry,
                          md=md, baseline=base)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one run per sample)
# ---------------------------------------------------------------------------
def rh_step_series_bar(samples, rh_setpoints, *, measure_at_rh=1, t=1.0, dets=None, reads=None,
                       geometry="transmission", equilibration_timeout=1800.0,
                       equilibration_tol=2.0, dose_step=None, atten_in=None, md=None):
    """Run :func:`rh_step_series_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned then run through
    the same RH ladder.  Note that because RH equilibration is slow and shared (one gas line),
    it is usually more efficient to keep one sample mounted per RH program; if you must share
    a chamber across samples at a fixed RH, interleave runs (``_core.multi_sample_run``) so the
    flows settle once for all samples.
    """
    for s in samples:
        yield from goto_sample(s)
        ds_motor = piezo.x if dose_step else None               # noqa: F821 (fresh-spot in x)
        yield from rh_step_series_run(
            s.name, rh_setpoints, measure_at_rh=measure_at_rh, t=t, dets=dets, reads=reads,
            geometry=geometry, equilibration_timeout=equilibration_timeout,
            equilibration_tol=equilibration_tol, dose_motor=ds_motor, dose_step=dose_step,
            atten_in=atten_in, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """SVA RH program on one sample: 0 -> 50 -> 90 -> 50 -> 0 %RH, 3 frames each, transmission.

    Live RH is recorded as ``{rh}`` each frame; the setpoint rides in baseline.  Run with::

        RE(technique_G_humidity.example())
    """
    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                  # noqa: F821
        yield from bps.sleep(1)

    yield from rh_step_series_run(
        "PS_b_PMMA_SVA", rh_setpoints=[0, 50, 90, 50, 0], measure_at_rh=3, t=1.0,
        geometry="transmission",
        equilibration_timeout=40 * 60, equilibration_tol=2.0,   # ~40-min equilibration
        atten_in=_atten_in,
        md={"project_name": "311234_Demo", "process": "solvent_vapor_annealing"},
    )


def example_swelling():
    """RH swelling kinetics: hold 90 %RH, ramp-during, 80 frames @ 5 s, reflection (GISAXS).

    Align the sample first (e.g. ``alignement_gisaxs_hex``) for true grazing geometry.  Run::

        RE(technique_G_humidity.example_swelling())
    """
    yield from rh_swelling_kinetics_run(
        "PS_b_PMMA_swell90", target_rh=90, n_frames=80, period=5.0, t=1.0,
        geometry="reflection", ramp_during=True,
        md={"project_name": "311234_Demo", "process": "rh_swelling"},
    )

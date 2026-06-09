"""
technique_F_kinetics
====================

Archetype F -- In-situ time-series / kinetics (NON-thermal).

Follow a process *in time*: solvent evaporation / drying, blade-coating, flow / mixing,
tensile / strain, UV exposure, swelling, self-assembly, nanoparticle growth.  The hallmark of
the legacy form is a wall-clock loop ``for i in range(N): ...; sleep`` whose innermost call is
``bp.count(num=1)`` -- i.e. *one Bluesky run per frame* -- with the elapsed time
(``time.time()-t0``) and frame index baked into the filename string.

This file replaces that with ONE run holding a **time series of events**.  Elapsed time is
recorded as a small ``Signal`` (``elapsed_s``) put fresh each frame, so ``{elapsed_s}`` is a
filename *token* resolved from the recorded stream -- never formatted into the name with
``time.time()``.  Timing is done with ``bps.sleep`` *inside* the generator (consumed by the
RunEngine), never a wall-clock ``time.sleep`` outside it.

Gold / legacy reference: the run-per-frame kinetics loops in ``legacy/30-user-Modestino.py``
(``measure_insitu`` -- syringe flow), ``legacy/30-user-Murray.py`` (a ``range(50000)`` colloid
self-assembly loop with ``t=time.time()-t0`` in the name), ``legacy/30-user-Chaney.py``
(``temp_series`` -- Linkam + per-frame syringe infuse/withdraw oscillation),
``LBL/bladecoating.py`` (Thorlabs translator ``thorlabs_su`` + syringe ``syringe_pu``), and the
CFN ``2026C1_InSituGrowth.py`` / ``2026C1_InSituDemo.py`` growth drivers.  Rigs vary a lot, so
the plans here stay deliberately generic: you pass in *what* to measure and *what* (if
anything) to do between frames.

What this file gives you
------------------------
* :func:`time_series_run` -- ONE run, N timed events (by ``n_frames`` or by ``duration``),
  recording ``{elapsed_s}`` per frame.  The kinetics workhorse.
* :func:`kinetics_run` -- like :func:`time_series_run` but fires an optional in-situ
  ``action(i)`` plan between frames (e.g. a syringe-pump infuse / withdraw on ``syringe_pu``).
* :func:`blade_coating_run` -- a blade-coating variant: deposit ink with a syringe pump, move
  a Thorlabs translator (``thorlabs_su``), and follow the drying as a time series.
* :func:`time_series_bar` -- loop :func:`time_series_run` over a :class:`SampleList` (one run
  per sample, measured back-to-back).
* :func:`syringe_infuse`, :func:`syringe_withdraw` -- thin, abstracted pump action plans.
* :func:`example` / :func:`example_blade_coating` -- runnable, fully-specified examples.

Idioms preserved (via _preprocessors): fresh-spot dose walking (move to an unexposed spot each
frame), ensure attenuators in, baseline capture of constants, cleanup on error.  Slow-axis
economy is mostly moot here (time is the axis) but the WAXS arc, if scanned, stays outermost.

Async alternative (mention)
---------------------------
For *truly asynchronous* readbacks (a load cell, a thermocouple, an RH probe that updates on
its own clock) consider ``bp.monitor`` / ``bluesky.preprocessors.monitor_during_wrapper``
instead of -- or in addition to -- the periodic ``trigger_and_read`` here: open the run, start
monitoring the async signal, run the time series, and the monitor emits its own events whenever
the signal changes.  That keeps the detector cadence and the environment cadence decoupled.
See :func:`time_series_run`'s ``monitors`` argument.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bpp``, ``Signal``, ``piezo``, ``stage``,
    ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``,
    ``att2_9``, ``det_exposure_time``, and (for the in-situ variants) the rig devices
    ``syringe_pu`` (syringe pump) and ``thorlabs_su`` (Thorlabs translator).
"""

import time

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, saxs_waxs_dets, fname, merge_md)
from ._preprocessors import (fresh_spot_wrapper, ensure_in_wrapper, cleanup_wrapper,
                             baseline_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "syringe_infuse", "syringe_withdraw", "time_series_point",
    "time_series_run", "kinetics_run", "blade_coating_run",
    "time_series_bar", "example", "example_blade_coating",
]


# ---------------------------------------------------------------------------
# Abstracted syringe-pump action plans (the rig varies; keep these thin)
# ---------------------------------------------------------------------------
def syringe_infuse(seconds, *, pump=None):
    """Infuse (push) on the syringe pump for ``seconds``, then stop.

    Wraps the legacy ``syringe_pu.dir=0; syringe_pu.go=1; sleep; syringe_pu.stop_flow=1``
    idiom from ``LBL/bladecoating.py`` as one plan.  ``pump`` defaults to the global
    ``syringe_pu``.  Use as an ``action(i)`` for :func:`kinetics_run` (often only on frame 0).
    """
    pu = pump if pump is not None else syringe_pu                # noqa: F821
    yield from bps.mv(pu.dir, 0)                                 # 0 = infuse (push)
    yield from bps.mv(pu.go, 1)                                  # start pump
    yield from bps.sleep(seconds)
    yield from bps.mv(pu.stop_flow, 1)                           # stop pump


def syringe_withdraw(seconds, *, pump=None):
    """Withdraw (pull) on the syringe pump for ``seconds``, then stop (mirror of infuse)."""
    pu = pump if pump is not None else syringe_pu                # noqa: F821
    yield from bps.mv(pu.dir, 1)                                 # 1 = withdraw (pull)
    yield from bps.mv(pu.go, 1)
    yield from bps.sleep(seconds)
    yield from bps.mv(pu.stop_flow, 1)


# ---------------------------------------------------------------------------
# Inner per-frame measurement
# ---------------------------------------------------------------------------
def time_series_point(dets, reads, elapsed_sig, t0, *, frame_index_sig=None, frame_i=None):
    """Stamp the elapsed time (and optional frame index) and record ONE event.

    ``elapsed_sig`` is a ``Signal`` whose value is set to ``time.monotonic() - t0`` here and
    then read, so ``{elapsed_s}`` resolves in the filename from the *recorded* field -- this is
    the whole point of the archetype.  ``reads`` is the list of extra readables (beyond
    ``dets``) recorded each event.
    """
    elapsed_sig.put(time.monotonic() - t0)
    extra = [elapsed_sig]
    if frame_index_sig is not None and frame_i is not None:
        frame_index_sig.put(int(frame_i))
        extra.append(frame_index_sig)
    yield from bps.trigger_and_read(list(dets) + list(reads) + extra)


# ---------------------------------------------------------------------------
# One run = one sample, a timed series of events
# ---------------------------------------------------------------------------
def time_series_run(name, *, n_frames=None, duration=None, period=1.0, t=0.5, dets=None,
                    reads=None, geometry="transmission", warmup=2, dose_motor=None,
                    dose_step=None, atten_in=None, monitors=None, baseline=None, md=None,
                    name_tokens=("t{elapsed_s}s", "n{frame_index}")):
    """ONE run: a time series of N events on a single sample (the kinetics workhorse).

    Replaces the legacy ``for i in range(N): ...; sleep; bp.count(num=1)`` (one run per frame,
    ``t0=time.time()`` into the filename) with a single staged run whose events carry the
    elapsed time as a recorded ``elapsed_s`` Signal.

    You bound the series *either* by a frame count (``n_frames``) *or* by a wall-clock
    ``duration`` in seconds (whichever you pass; ``duration`` wins if both given).  Frames are
    spaced by ``period`` seconds using ``bps.sleep`` (so the spacing is *between* the end of
    one event and the start of the next -- exposure time is separate).

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    n_frames : int, optional
        Number of timed events.  Mutually-exclusive-ish with ``duration``.
    duration : float, optional
        Total run length (s); frames are taken until elapsed >= duration.
    period : float
        Sleep (s) between frames (the kinetics cadence).
    t : float
        Exposure / averaging time (s) applied to detectors.
    dets : list, optional
        Detectors.  Default ``[pil2M, pil900KW, xbpm2, xbpm3]`` (SAXS + WAXS + I0).
    reads : list, optional
        Extra readables recorded each event.  Default ``[energy, waxs, xbpm2, xbpm3]``.
    geometry : str
        ``"transmission"`` or ``"reflection"``.
    warmup : int
        Number of throwaway frames taken *before* ``t0`` is latched (the legacy "burst-mode
        warm-up dummy counts" that settle the detector / file writer).  These are recorded but
        carry negative-ish/near-zero elapsed times; set 0 to disable.
    dose_motor, dose_step : optional
        If both given, walk ``dose_motor`` by ``dose_step`` after every frame (fresh spot) --
        important for drying/UV/assembly where the beam would otherwise damage one spot.
    atten_in : callable () -> plan, optional
        Plan that puts attenuators into the measurement configuration after any prior
        alignment (runs once at run open).
    monitors : list, optional
        Async signals to ``monitor_during`` the run (e.g. a load cell or RH probe that updates
        on its own clock).  These emit their own events independent of the frame cadence.
    baseline : list, optional
        Constants recorded once (default includes SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename.  Default references the recorded
        ``{elapsed_s}`` and ``{frame_index}``.

    Notes
    -----
    Use :func:`kinetics_run` instead if you need an in-situ action *between* frames.
    """
    if n_frames is None and duration is None:
        raise ValueError("Pass either n_frames or duration to bound the time series.")
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                             # noqa: F821 (SDD)
        except Exception:
            baseline = []

    # Recorded context: elapsed time + frame index (so {elapsed_s}/{frame_index} resolve).
    elapsed = Signal(name="elapsed_s", value=0.0)               # noqa: F821
    frame_index = Signal(name="frame_index", value=0)          # noqa: F821

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        # Warm-up frames (settle the detector/file writer) BEFORE we start the clock.
        for w in range(int(warmup)):
            yield from time_series_point(dets, reads, elapsed, time.monotonic(),
                                         frame_index_sig=frame_index, frame_i=-(warmup - w))
        t0 = time.monotonic()
        i = 0
        while True:
            if duration is not None and (time.monotonic() - t0) >= duration:
                break
            if n_frames is not None and i >= n_frames:
                break
            yield from time_series_point(dets, reads, elapsed, t0,
                                         frame_index_sig=frame_index, frame_i=i)
            i += 1
            # Stop *after* the last frame without an extra sleep.
            if n_frames is not None and i >= n_frames:
                break
            yield from bps.sleep(period)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="time_series_kinetics", geometry=geometry,
                          md=md, baseline=baseline)

    # Layer opt-in idioms (innermost effect first).
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if monitors:
        plan = bpp.monitor_during_wrapper(plan, monitors)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)

    return (yield from plan)


# ---------------------------------------------------------------------------
# One run = one sample, time series WITH an in-situ action between frames
# ---------------------------------------------------------------------------
def kinetics_run(name, *, action=None, n_frames=10, period=5.0, t=0.5, dets=None, reads=None,
                 geometry="transmission", action_on=None, warmup=2, dose_motor=None,
                 dose_step=None, atten_in=None, baseline=None, md=None,
                 name_tokens=("t{elapsed_s}s", "n{frame_index}")):
    """ONE run: time series that fires ``action(i)`` between frames (flow / mixing / strain).

    Generalizes the legacy in-situ kinetics loops that trigger a syringe pump (Modestino,
    Chaney) -- but as a single run with recorded elapsed time, and with the action expressed
    as a *plan* you pass in.

    Parameters
    ----------
    name : str
        Human sample label.
    action : callable(i) -> plan, optional
        Plan run *before* frame ``i`` (e.g. ``lambda i: syringe_infuse(2.5)`` to push ink, or
        an oscillation ``lambda i: syringe_infuse(1) if i % 2 else syringe_withdraw(1)``).  If
        ``None``, this degenerates to a plain time series.
    n_frames : int
        Number of timed events.
    period : float
        Sleep (s) between frames.
    t : float
        Exposure time (s).
    dets, reads, geometry, warmup, dose_motor, dose_step, atten_in, baseline, md, name_tokens :
        As in :func:`time_series_run`.
    action_on : iterable of int, optional
        Restrict the action to these frame indices (e.g. ``[0]`` to infuse only once at the
        start, the common Modestino case).  Default: every frame.
    """
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                             # noqa: F821
        except Exception:
            baseline = []

    elapsed = Signal(name="elapsed_s", value=0.0)               # noqa: F821
    frame_index = Signal(name="frame_index", value=0)          # noqa: F821
    action_frames = set(action_on) if action_on is not None else None

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        for w in range(int(warmup)):
            yield from time_series_point(dets, reads, elapsed, time.monotonic(),
                                         frame_index_sig=frame_index, frame_i=-(warmup - w))
        t0 = time.monotonic()
        for i in range(int(n_frames)):
            if action is not None and (action_frames is None or i in action_frames):
                yield from action(i)
            yield from time_series_point(dets, reads, elapsed, t0,
                                         frame_index_sig=frame_index, frame_i=i)
            if i < int(n_frames) - 1:
                yield from bps.sleep(period)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="kinetics_action_series", geometry=geometry,
                          md=md, baseline=baseline)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Blade-coating variant (Thorlabs translator + syringe pump)
# ---------------------------------------------------------------------------
def blade_coating_run(name, *, coat_start=10.0, measure_pos=87.0, infuse_seconds=2.5,
                      n_frames=120, period=2.5, t=0.5, dets=None, reads=None,
                      translator=None, geometry="reflection", atten_in=None, baseline=None,
                      md=None, name_tokens=("t{elapsed_s}s", "n{frame_index}")):
    """ONE run: blade-coat (deposit + translate), then follow drying as a time series.

    Modernizes ``LBL/bladecoating.py`` (which deposited ink with the syringe pump, moved
    ``thorlabs_su`` to the measurement position, then took ``bp.count(num=120, delay=2.5)``):
    here the deposit + translate happen *inside* one run, the translator position is recorded
    every frame (include it in ``reads``), and elapsed time is a recorded Signal rather than a
    string in the name.  Alignment is assumed to have been done already (call
    ``alignement_gisaxs_hex`` outside this plan, as the legacy file does).

    Parameters
    ----------
    name : str
        Human sample label.
    coat_start : float
        Translator position (mm) where the blade starts the coating stroke.
    measure_pos : float
        Translator position (mm) the film is parked at for measurement.
    infuse_seconds : float
        Seconds to run the syringe pump to dispense the ink bead (rig/concentration specific).
    n_frames, period, t :
        Drying time-series parameters (see :func:`time_series_run`).
    translator : positioner, optional
        Defaults to the global ``thorlabs_su``.  Recorded each frame so its position is in the
        data.
    dets, reads, geometry, atten_in, baseline, md, name_tokens :
        As elsewhere.
    """
    tr = translator if translator is not None else thorlabs_su  # noqa: F821
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3, tr]                 # include translator position
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                             # noqa: F821
        except Exception:
            baseline = []

    elapsed = Signal(name="elapsed_s", value=0.0)               # noqa: F821
    frame_index = Signal(name="frame_index", value=0)          # noqa: F821

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        # 1) Move to coating start, dispense ink, draw the blade to the measurement position.
        yield from bps.mv(tr, coat_start)
        yield from syringe_infuse(infuse_seconds)
        yield from bps.mv(tr, measure_pos)
        # 2) Follow the drying as a time series (no extra warm-up; coating is the trigger).
        t0 = time.monotonic()
        for i in range(int(n_frames)):
            yield from time_series_point(dets, reads, elapsed, t0,
                                         frame_index_sig=frame_index, frame_i=i)
            if i < int(n_frames) - 1:
                yield from bps.sleep(period)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="blade_coating_drying", geometry=geometry,
                          md=md, baseline=baseline)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one run per sample, measured back-to-back)
# ---------------------------------------------------------------------------
def time_series_bar(samples, *, n_frames=None, duration=None, period=1.0, t=0.5, dets=None,
                    reads=None, geometry="transmission", dose_step=None, atten_in=None,
                    md=None):
    """Run :func:`time_series_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned (piezo / hexapod)
    then followed in time.  Useful when several rigs / spots dry or react sequentially.  For
    *simultaneous* multi-sample kinetics you would instead interleave runs (see
    ``_core.multi_sample_run``), but most kinetics rigs are one-at-a-time.
    """
    for s in samples:
        yield from goto_sample(s)
        ds_motor = piezo.x if dose_step else None               # noqa: F821 (fresh-spot in x)
        yield from time_series_run(
            s.name, n_frames=n_frames, duration=duration, period=period, t=t, dets=dets,
            reads=reads, geometry=geometry, dose_motor=ds_motor, dose_step=dose_step,
            atten_in=atten_in, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """Drying kinetics: one sample, 60 frames @ 5 s, fresh spot each frame, transmission.

    Records ``{elapsed_s}`` and ``{frame_index}`` from the stream (no ``time.time()`` in the
    name).  Run with::

        RE(technique_F_kinetics.example())
    """
    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                  # noqa: F821
        yield from bps.sleep(1)

    yield from time_series_run(
        "PS_tol_drying", n_frames=60, period=5.0, t=0.5, geometry="transmission",
        dose_motor=piezo.x, dose_step=30,                       # noqa: F821 (fresh spot)
        atten_in=_atten_in,
        md={"project_name": "311234_Demo", "process": "solvent_drying"},
    )


def example_blade_coating():
    """Blade-coat one film then follow drying for 120 frames @ 2.5 s, reflection.

    Assumes the sample is already GI-aligned (call ``alignement_gisaxs_hex`` first, as in
    ``LBL/bladecoating.py``).  Run with::

        RE(technique_F_kinetics.example_blade_coating())
    """
    yield from blade_coating_run(
        "P3HT_bladecoat", coat_start=10.0, measure_pos=87.0, infuse_seconds=2.5,
        n_frames=120, period=2.5, t=0.5,
        md={"project_name": "311234_Demo", "process": "blade_coating"},
    )

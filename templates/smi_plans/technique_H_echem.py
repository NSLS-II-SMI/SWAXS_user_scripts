"""
technique_H_echem
=================

Archetype H -- Electrochemistry / operando doping.

Scattering (SAXS/WAXS/GIWAXS) and/or NEXAFS measured **versus applied potential** or chemical
doping state: potential ladders, operando time loops at a held bias, and chemical doping
(FeCl3 / KClO4) series.  The potentiostat / source-measure unit is *not* a standard SMI
beamline device and the rig varies a lot, so it is abstracted here: you pass in a
``set_potential(V)`` *plan* and a ``potential_readback`` ``Signal`` (the measured cell
voltage), and the plans record both so ``{potential_v}`` is a filename token.

The legacy form bakes the applied potential into the filename as a **hand-typed string** --
``"pgBTTT_KCl_sample3_Vds500mV_Vgs200mV_..."`` (``legacy/30-user-Meli.py``),
``"PB2T_TEG_doped400mV"`` / ``"MM389_n500mV"`` (``legacy/30-user-Richter.py``) -- with
``amptek`` fluorescence and ``for i in range(100): bp.count(num=1)`` operando time loops
(Meli), or ``for i in range(frames=5000): ...`` continuous runs (Karen).  This file records the
potential (and current, if available) as devices in the stream instead, and makes each
potential ladder / operando hold ONE run.

Gold / legacy reference: ``legacy/30-user-Meli.py`` (operando + ``amptek`` fluorescence,
``K_edge_timescan``), ``legacy/30-user-Karen.py`` (operando ``continous_run_*`` with
``frames=5000`` time loops), ``legacy/30-user-Richter.py`` (gate-bias mV ladders; FeCl3 /
KClO4 chemical doping).

What this file gives you
------------------------
* :func:`potential_point` -- inner per-event measurement that stamps the applied + readback
  potential and records one event (so ``{potential_v}`` resolves).
* :func:`potential_step_run` -- ONE run stepping through a list of potentials for a sample;
  each step records V.  Accepts an optional ``measure(V, ...)`` callable so you can compose a
  NEXAFS energy sweep (or any sub-plan) *at each potential*.
* :func:`operando_kinetics_run` -- ONE run: hold a potential and follow the response as a time
  series of events (frames <= 5000, the Karen operando shape), recording elapsed time + V.
* :func:`doping_state_run` -- ONE run over a sequence of (named) chemical doping states with a
  user ``apply(state)`` plan (FeCl3/KClO4), recording the state label as a Signal.
* :func:`potential_step_bar` -- loop :func:`potential_step_run` over a :class:`SampleList`.
* :func:`example` / :func:`example_operando` -- runnable, fully-specified examples.

Composing with an energy sweep
------------------------------
To do NEXAFS *at each potential* (operando resonant), pass ``measure=`` a callable that runs
the energy sweep and records events itself.  A tiny helper closure is shown in
:func:`example`; for the full edge-grid machinery import ``technique_A_energy_edge`` and call
its ``nexafs_point`` inside your ``measure`` (kept out of here to avoid coupling).

Idioms preserved (via _preprocessors): ``amptek`` fluorescence detector support (just include
it in ``dets``), ensure attenuators in, baseline capture of constants, fresh-spot dose walking,
cleanup (return the cell to a safe potential) on error.  Timing uses ``bps.sleep`` inside the
generator, never wall-clock ``time.sleep``.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bpp``, ``Signal``, ``piezo``, ``stage``,
    ``waxs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``,
    ``att2_9``, ``amptek``, ``det_exposure_time``.  The potentiostat is supplied by the caller
    as a ``set_potential(V)`` plan + a ``potential_readback`` Signal (NOT a built-in global).
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
    "potential_point", "potential_step_run", "operando_kinetics_run",
    "doping_state_run", "potential_step_bar", "example", "example_operando",
]


# ---------------------------------------------------------------------------
# Inner per-event measurement (records applied + readback potential)
# ---------------------------------------------------------------------------
def potential_point(dets, reads, applied_sig, *, readback=None, settle=0.0,
                    elapsed_sig=None, t0=None):
    """Record ONE event with the applied (and optional readback) potential in the stream.

    ``applied_sig`` is a ``Signal`` holding the *commanded* potential (set by the caller before
    this point); it is read here so ``{potential_v}`` resolves in the filename.  ``readback``,
    if given, is an ophyd ``Signal``/readable for the *measured* cell voltage (and/or current)
    and is recorded alongside.  ``elapsed_sig``/``t0`` add an elapsed-time stamp for operando
    kinetics.
    """
    if settle:
        yield from bps.sleep(settle)
    extra = [applied_sig]
    if readback is not None:
        extra.append(readback)
    if elapsed_sig is not None and t0 is not None:
        elapsed_sig.put(time.monotonic() - t0)
        extra.append(elapsed_sig)
    yield from bps.trigger_and_read(list(dets) + list(reads) + extra)


# ---------------------------------------------------------------------------
# One run = one sample, step through a list of potentials
# ---------------------------------------------------------------------------
def potential_step_run(name, potentials, *, set_potential, potential_readback=None,
                       measure_at_v=1, t=1.0, dets=None, reads=None, geometry="reflection",
                       equilibration=5.0, settle=0.0, measure=None, dose_motor=None,
                       dose_step=None, atten_in=None, baseline=None, md=None,
                       name_tokens=("V{potential_v}", "bpm{xbpm2_sumX}")):
    """ONE run: step through ``potentials`` on a single sample, recording V at each step.

    Replaces the legacy "one filename string per hand-typed bias + ``bp.count`` per point" with
    a single run whose events carry the applied potential as a recorded ``potential_v`` Signal
    (and the measured readback, if you wire one).  Loop is a simple ladder; pass ``measure`` to
    do something richer (e.g. a NEXAFS sweep) at each potential.

    Parameters
    ----------
    name : str
        Human sample label.
    potentials : sequence of float
        The potential ladder (V), in visiting order (e.g. a CV-like up/down ramp).
    set_potential : callable(V) -> plan
        Plan that commands the potentiostat to ``V`` (rig-specific; you provide it).  It is
        called once per step before measuring.
    potential_readback : ophyd readable, optional
        Measured cell voltage (and/or current) device; recorded each event if given.
    measure_at_v : int
        Events recorded at each potential.  Ignored if ``measure`` is given.
    t : float
        Exposure time (s).
    dets : list, optional
        Default ``[pil900KW, xbpm2, xbpm3]`` (WAXS + I0; add ``amptek`` for fluorescence-yield,
        ``pil2M`` for SAXS).
    reads : list, optional
        Default ``[energy, waxs, xbpm2, xbpm3]``.
    geometry : str
        ``"reflection"`` (GIWAXS operando) or ``"transmission"``.
    equilibration : float
        Sleep (s) after commanding each potential, before measuring (let the cell settle).
    settle : float
        Extra sleep inside each event.
    measure : callable(V, applied_sig) -> plan, optional
        Custom per-potential measurement (e.g. an energy sweep).  It must record events itself
        (typically via :func:`potential_point` so ``{potential_v}`` resolves) but must NOT
        open/close runs.  Overrides ``measure_at_v``.
    dose_motor, dose_step : optional
        Fresh-spot dose walk after every frame.
    atten_in : callable () -> plan, optional
        Measurement-configuration guard (runs once at run open).
    baseline : list, optional
        Constants recorded once (SDD added if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens; default references recorded ``{potential_v}`` and ``{xbpm2_sumX}``.
    """
    if dets is None:
        dets = [pil900KW, xbpm2, xbpm3]                          # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821

    # Applied (commanded) potential as a recorded Signal -> drives {potential_v}.
    potential_v = Signal(name="potential_v", value=0.0)        # noqa: F821

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                             # noqa: F821 (SDD)
    except Exception:
        pass

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        for v in potentials:
            yield from set_potential(v)
            potential_v.put(float(v))
            if equilibration:
                yield from bps.sleep(equilibration)
            if measure is not None:
                yield from measure(v, potential_v)
            else:
                for _ in range(int(measure_at_v)):
                    yield from potential_point(dets, reads, potential_v,
                                               readback=potential_readback, settle=settle)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="potential_step", geometry=geometry,
                          md=md, baseline=base)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# One run = one sample, hold a potential and follow the response in time
# ---------------------------------------------------------------------------
def operando_kinetics_run(name, hold_potential, *, set_potential, potential_readback=None,
                          n_frames=100, period=2.0, t=1.0, dets=None, reads=None,
                          geometry="reflection", equilibration=0.0, max_frames=5000,
                          dose_motor=None, dose_step=None, atten_in=None, baseline=None,
                          md=None, name_tokens=("V{potential_v}", "t{elapsed_s}s",
                                                "n{frame_index}")):
    """ONE run: hold ``hold_potential`` and follow the response as a time series.

    The operando shape from ``legacy/30-user-Karen.py`` (``continous_run_*``, ``frames=5000``)
    and ``legacy/30-user-Meli.py`` (``K_edge_timescan``, ``range(100)``), but as a single run
    with the applied potential, optional readback, and elapsed time recorded as Signals --
    never strings.  ``n_frames`` is clamped to ``max_frames`` (default 5000) to match the Karen
    bound and avoid pathological run lengths.

    Parameters
    ----------
    name : str
        Human sample label.
    hold_potential : float
        Potential (V) to command and hold for the whole series.
    set_potential : callable(V) -> plan
        Plan that commands the potentiostat (you provide it).
    potential_readback : ophyd readable, optional
        Measured cell voltage/current; recorded each event if given.
    n_frames : int
        Number of timed events (clamped to ``max_frames``).
    period : float
        Sleep (s) between frames.
    t : float
        Exposure time (s).
    equilibration : float
        Sleep (s) after commanding the hold potential, before the first frame.
    max_frames : int
        Hard cap on frame count (Karen-style <= 5000).
    dets, reads, geometry, dose_motor, dose_step, atten_in, baseline, md, name_tokens :
        As in :func:`potential_step_run` / the time-series archetype.
    """
    n_frames = min(int(n_frames), int(max_frames))
    if dets is None:
        dets = [pil900KW, xbpm2, xbpm3]                          # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821

    potential_v = Signal(name="potential_v", value=float(hold_potential))  # noqa: F821
    elapsed = Signal(name="elapsed_s", value=0.0)              # noqa: F821
    frame_index = Signal(name="frame_index", value=0)         # noqa: F821

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                             # noqa: F821
    except Exception:
        pass

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        yield from set_potential(hold_potential)
        potential_v.put(float(hold_potential))
        if equilibration:
            yield from bps.sleep(equilibration)
        t0 = time.monotonic()
        for i in range(n_frames):
            frame_index.put(i)
            yield from potential_point(dets, reads + [frame_index], potential_v,
                                       readback=potential_readback,
                                       elapsed_sig=elapsed, t0=t0)
            if i < n_frames - 1:
                yield from bps.sleep(period)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="operando_kinetics", geometry=geometry,
                          md=md, baseline=base)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# One run = one sample, sequence of (named) chemical doping states
# ---------------------------------------------------------------------------
def doping_state_run(name, states, *, apply, measure_per_state=1, t=1.0, dets=None, reads=None,
                     geometry="reflection", equilibration=0.0, settle=0.0, measure=None,
                     dose_motor=None, dose_step=None, atten_in=None, baseline=None, md=None,
                     name_tokens=("{dope_state}", "bpm{xbpm2_sumX}")):
    """ONE run over a sequence of named chemical doping states (FeCl3 / KClO4 / ...).

    Replaces the legacy habit of typing the doping state into the filename
    (``..._doped400mV``, ``..._KClO4_redoped``) with a recorded ``dope_state`` Signal.  Because
    a doping *state* is usually a string label, the ``dope_state`` Signal carries that string
    and resolves the ``{dope_state}`` token directly.

    Parameters
    ----------
    name : str
        Human sample label.
    states : sequence
        The doping states to visit.  Each may be a plain label (str/number) or any value your
        ``apply`` understands; the label is also what fills ``{dope_state}``.
    apply : callable(state) -> plan
        Plan that drives the sample into ``state`` (e.g. expose to FeCl3 vapor, set a CV hold,
        rinse / de-dope).  You provide it; called once per state.
    measure_per_state : int
        Events recorded at each state.  Ignored if ``measure`` is given.
    t : float
        Exposure time (s).
    equilibration : float
        Sleep (s) after applying a state, before measuring.
    settle : float
        Extra sleep inside each event.
    measure : callable(state, dope_sig) -> plan, optional
        Custom per-state measurement (e.g. NEXAFS); records events itself, no open/close.
    dets, reads, geometry, dose_motor, dose_step, atten_in, baseline, md, name_tokens :
        As elsewhere.
    """
    if dets is None:
        dets = [pil900KW, xbpm2, xbpm3]                          # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                     # noqa: F821

    # Doping state label as a recorded Signal -> drives {dope_state} (value may be a string).
    dope_state = Signal(name="dope_state", value="")           # noqa: F821

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                             # noqa: F821
    except Exception:
        pass

    det_exposure_time(t, t)                                      # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        for st in states:
            yield from apply(st)
            dope_state.put(st)
            if equilibration:
                yield from bps.sleep(equilibration)
            if measure is not None:
                yield from measure(st, dope_state)
            else:
                for _ in range(int(measure_per_state)):
                    yield from potential_point(dets, reads, dope_state, settle=settle)

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="doping_state_series", geometry=geometry,
                          md=md, baseline=base)
    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one run per sample)
# ---------------------------------------------------------------------------
def potential_step_bar(samples, potentials, *, set_potential, potential_readback=None,
                       measure_at_v=1, t=1.0, dets=None, reads=None, geometry="reflection",
                       equilibration=5.0, dose_step=None, atten_in=None, md=None):
    """Run :func:`potential_step_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned then stepped through
    the same potential ladder.  (If the cells share a single potentiostat channel you usually
    measure one cell per run anyway; for a shared bias across samples, interleave runs via
    ``_core.multi_sample_run``.)
    """
    for s in samples:
        yield from goto_sample(s)
        ds_motor = piezo.x if dose_step else None               # noqa: F821 (fresh-spot in x)
        yield from potential_step_run(
            s.name, potentials, set_potential=set_potential,
            potential_readback=potential_readback, measure_at_v=measure_at_v, t=t, dets=dets,
            reads=reads, geometry=geometry, equilibration=equilibration, dose_motor=ds_motor,
            dose_step=dose_step, atten_in=atten_in, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """Gate-bias ladder on one sample, GIWAXS + fluorescence, -0.6 -> +0.6 V in 0.2 V steps.

    The potentiostat is abstracted: ``_set_potential`` is a stand-in plan (replace with your
    rig's command).  Applied V is recorded as ``{potential_v}``.  Run with::

        RE(technique_H_echem.example())
    """
    # Stand-in potentiostat command (replace with your rig: e.g. mv a bias Signal / call a fn).
    def _set_potential(v):
        # e.g. yield from bps.mv(gate_bias_setpoint, v); yield from bps.sleep(1)
        yield from bps.null()                                   # noqa: F821 (placeholder)

    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                  # noqa: F821
        yield from bps.sleep(1)

    potentials = [-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6]
    yield from potential_step_run(
        "PB2T_TEG_operando", potentials, set_potential=_set_potential,
        measure_at_v=1, t=1.0, dets=[pil900KW, amptek, xbpm2, xbpm3],  # noqa: F821 (amptek)
        geometry="reflection", equilibration=5.0, dose_motor=piezo.x, dose_step=30,  # noqa: F821
        atten_in=_atten_in,
        md={"project_name": "311234_Demo", "electrolyte": "KClO4", "doping": "electrochemical"},
    )


def example_operando():
    """Operando kinetics: hold +0.4 V and take 300 frames @ 2 s, GIWAXS (Karen-style).

    Run with::

        RE(technique_H_echem.example_operando())
    """
    def _set_potential(v):
        yield from bps.null()                                   # noqa: F821 (placeholder)

    yield from operando_kinetics_run(
        "PB2T_TEG_hold400mV", hold_potential=0.4, set_potential=_set_potential,
        n_frames=300, period=2.0, t=1.0, geometry="reflection",
        md={"project_name": "311234_Demo", "doping": "electrochemical"},
    )

"""
smi_plans._compose
=================

The **composable experiment model** for SMI-SWAXS.

A real SMI experiment is not "one of A-O".  It is an assembly of independent concerns:

    beam / q-range      -- which energies, which detectors + WAXS-arc (the q reach)
    apparatus / geometry -- grazing vs transmission, Linkam/Lakeshore, RH cell, e-chem ...
    sampling / scanning  -- a single spot, 5 locations, a grid, a phi rock ...
    manual / interactive -- "swap the sample and type its thickness", "I set T=35C, confirm",
                            "wait until I start the pump" -- captured as recorded Signals
    what to record       -- the detectors + context Signals captured at each point

This module lets you express an experiment as a **measurement core** wrapped by a **stack of
nested scan axes**, in an order you choose.  The A-O ``technique_*`` files are then just
*preset recipes* that assemble these same pieces -- and a GUI can assemble them on the fly.

Mental model
------------
An experiment is nested loops around one ``trigger_and_read``::

    for sample:                         # outer (handled by acquire / *_bar)
        <apparatus setup: geometry, align, heater on, atten in>   (once per run)
        for arc in waxs_arc:            # ScanAxis (slow, in-vacuum -> outer)
            for T in temperatures:      # ScanAxis (slow -> outer)
                for ai in incidence:    # ScanAxis
                    for e in energies:  # ScanAxis
                        at 5 x-locations # ScanAxis (fast -> inner)
                            trigger_and_read(dets + context)   # the core

Each loop level is a :class:`ScanAxis`.  You build the axes you want, put them in the order
you want (slow outermost), and :func:`acquire` nests them inside ONE run with the filename
templated from whatever the axes record.

Key types
---------
* :class:`ScanAxis` -- one loop dimension: values, how to move to a value, what Signal to
  record, settle, optional per-point hook, and a "slowness" hint for the ordering guardrail.
* :func:`nest_axes` -- turn a list of axes + a measurement core into a single nested plan.
* :func:`acquire` -- the experiment builder: ONE run for ONE sample = setup + nested axes +
  ``trigger_and_read``, with merged ``md`` and a templated filename.
* axis constructors -- :func:`energy_axis`, :func:`temperature_axis`, :func:`incidence_axis`,
  :func:`motor_axis`, :func:`spatial_grid_axes`, :func:`potential_axis`, :func:`rh_axis`,
  :func:`time_axis` -- ready-made axes for the common concerns.
* manual / interactive -- :func:`manual_step` / :func:`manual_value` (collect a hand-set value
  into a recorded Signal), :func:`manual_axis` (a user-driven enumerated loop),
  :func:`manual_loop` (open-ended "keep going until I stop"), :func:`pause_for_user`.

.. important::
    References beamline globals injected by the SMI profile collection at runtime (``bps``,
    ``Signal``, ``np``, ``energy``, ``waxs``, ``piezo``, ``xbpm2`` ...).  ``ScanAxis`` itself
    is plain data (GUI-safe to construct); only *running* a plan needs the live environment.
"""

import warnings

from ._core import one_sample_run, goto_sample, fname, merge_md

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "ScanAxis",
    "nest_axes",
    "acquire",
    "acquire_bar",
    "energy_axis",
    "temperature_axis",
    "incidence_axis",
    "motor_axis",
    "spatial_grid_axes",
    "potential_axis",
    "rh_axis",
    "time_axis",
    "manual_step",
    "manual_value",
    "manual_axis",
    "manual_loop",
    "pause_for_user",
    "SPEED_SLOW", "SPEED_MEDIUM", "SPEED_FAST",
]


# Slowness hints used by the ordering guardrail (higher = slower / costlier to move).
SPEED_FAST = 0      # piezo.x/y/z, fast Signals
SPEED_MEDIUM = 1    # incident angle, energy (DCM), potential, RH
SPEED_SLOW = 2      # waxs.arc, prs, temperature (equilibration), anything in-vacuum


class ScanAxis(object):
    """One dimension of a scan: a set of values plus how to *visit* and *record* each.

    A ``ScanAxis`` is essentially a ``for`` loop turned into data.  You can construct it by
    hand, or use the ready-made constructors (:func:`energy_axis`, etc.).

    Parameters
    ----------
    name : str
        Human / metadata label (e.g. ``"energy"``, ``"temperature"``, ``"x_grid"``).
    values : sequence
        The points to visit, in order.  ``None`` / empty means a single pass with no move
        (a degenerate axis -- useful so a recipe can "turn off" a dimension uniformly).
    move : callable(value) -> plan, optional
        How to get to a value.  Default: ``bps.mv(device, value)`` if ``device`` is given.
        Pass a custom plan for non-trivial moves (e.g. ``goto_temperature`` with
        equilibration, or "incident angle = th0 + value").
    device : ophyd positioner, optional
        Shortcut: if given and ``move`` is None, the axis does ``bps.mv(device, value)``.
    record : ophyd Signal, optional
        A Signal ``.put(value)`` at each point so the value is recorded in the primary stream
        (and thus usable as a ``{record.name}`` filename token).  If you set ``device`` and it
        is itself a readable you include in ``reads``, you may not need a separate ``record``.
    settle : float
        Sleep (s) after moving, before descending to the inner axis.
    per_point : callable() -> plan, optional
        Extra plan run at this level *after* moving + settling, before the inner axis (e.g. a
        beam-loss re-seek tied to energy, or a fresh-spot nudge tied to this loop).
    reads : list, optional
        Extra readables to add to the event *because of this axis* (rarely needed; usually the
        ``record`` Signal is enough).  Collected and merged by :func:`acquire`.
    speed : int
        Slowness hint (:data:`SPEED_FAST` / ``MEDIUM`` / ``SLOW``) used to warn when a slow
        axis is nested too far inside (i.e. moved too often).  Does not constrain order.
    reverse_alternate : bool
        If True, reverse this axis's direction on every other pass of the *outer* axes
        (boustrophedon / snake) to avoid backtracking.  Useful for slow axes.
    """

    def __init__(self, name, values, *, move=None, device=None, record=None,
                 settle=0.0, per_point=None, reads=None, speed=SPEED_MEDIUM,
                 reverse_alternate=False):
        self.name = name
        self.values = list(values) if values is not None else []
        self.device = device
        self._move = move
        self.record = record
        self.settle = settle
        self.per_point = per_point
        self.reads = list(reads) if reads else []
        self.speed = speed
        self.reverse_alternate = reverse_alternate

    def __repr__(self):
        return "ScanAxis({!r}, n={}, speed={})".format(self.name, len(self.values), self.speed)

    def is_degenerate(self):
        """True if this axis has 0/1 points and nothing to move (a no-op pass)."""
        return len(self.values) == 0

    def move_to(self, value):
        """Plan: move to ``value`` (custom ``move``, else ``bps.mv(device, value)``).

        The custom ``move`` may be a *plan* (generator-function) or a plain function that just
        sets some software state (e.g. updates a Signal with no hardware move); both are
        handled.
        """
        if self._move is not None:
            ret = self._move(value)
            if ret is not None:          # a generator/iterable -> it yields plan messages
                yield from ret
            # else: a plain function that already did its (software-only) work
        elif self.device is not None:
            yield from bps.mv(self.device, value)
        # else: nothing to move (a pure "record" axis)
        if self.record is not None:
            self.record.put(value)
        if self.settle:
            yield from bps.sleep(self.settle)
        if self.per_point is not None:
            pp = self.per_point()
            if pp is not None:
                yield from pp

    def token(self, fmt=None):
        """Convenience: the ``{field}`` filename token for this axis's recorded value.

        Returns ``"{<record.name>}"`` if a ``record`` Signal is set, else ``""``.  ``fmt`` may
        wrap it, e.g. ``axis.token("ai{}")`` -> ``"ai{incident_angle}"``.
        """
        if self.record is None:
            return ""
        tok = "{" + self.record.name + "}"
        return fmt.format(tok) if fmt else tok


# ---------------------------------------------------------------------------
# Nesting
# ---------------------------------------------------------------------------
def nest_axes(axes, measure):
    """Build the nested-loop plan: ``axes[0]`` outermost ... ``measure()`` innermost.

    Parameters
    ----------
    axes : list of ScanAxis
        Outermost first.  Degenerate axes (no values) are skipped but still execute their
        single move-to-None pass if they have a device (so a recipe can pass an "off" axis).
    measure : callable() -> plan
        The innermost measurement (typically ``trigger_and_read``).

    Returns
    -------
    A plan (generator); ``yield from`` it.
    """
    # filter to axes that actually do something, but keep order
    active = [a for a in axes if not a.is_degenerate()]

    def _build(i, reverse=False):
        if i >= len(active):
            yield from measure()
            return
        axis = active[i]
        vals = list(axis.values)
        if reverse and axis.reverse_alternate:
            vals = vals[::-1]
        for j, v in enumerate(vals):
            yield from axis.move_to(v)
            # alternate inner direction for snaking if the inner axis asked for it
            yield from _build(i + 1, reverse=(j % 2 == 1))

    return (yield from _build(0))


# ---------------------------------------------------------------------------
# Ordering guardrail
# ---------------------------------------------------------------------------
def _check_axis_order(axes):
    """Warn (do not raise) if a slow axis is nested inside a faster one (moved too often).

    Best practice: slow / in-vacuum axes (waxs.arc, prs, temperature) outermost so they move
    the fewest times.  This computes how many times each axis moves given the nesting and warns
    if a slower axis moves more often than a faster one inside it.
    """
    active = [a for a in axes if not a.is_degenerate()]
    # moves(i) = product of lengths of all axes at or outside i (i.e. how often axis i moves)
    for i, a in enumerate(active):
        moves_i = 1
        for outer in active[:i + 1]:
            moves_i *= max(1, len(outer.values))
        for k in range(i + 1, len(active)):
            inner = active[k]
            if inner.speed < a.speed:
                continue  # a faster axis inside a slower one is fine
            if inner.speed > a.speed:
                moves_inner = moves_i * 1
                for mid in active[i + 1:k + 1]:
                    moves_inner *= max(1, len(mid.values))
                warnings.warn(
                    "Scan-axis order: slow axis '{}' (speed {}) is nested inside faster "
                    "axis '{}' (speed {}); it will move {} times. Consider putting slower "
                    "axes outermost to minimize travel of in-vacuum hardware."
                    .format(inner.name, inner.speed, a.name, a.speed, moves_inner),
                    stacklevel=3)


# ---------------------------------------------------------------------------
# The experiment builder
# ---------------------------------------------------------------------------
def acquire(name, dets, axes, *, reads=None, setup=None, geometry=None, scan_name="acquire",
            md=None, baseline=None, name_tokens=None, check_order=True, sample=None):
    """Compose ONE run for ONE sample: setup + nested ``axes`` + ``trigger_and_read``.

    This is the compositional heart.  You provide the *beam/q config* (``dets`` + ``reads``),
    the *apparatus/geometry* (``setup`` plan, run once after the run opens), and the
    *sampling/scanning* (``axes``, nested in the given order).  Everything an axis records is
    available as a ``{field}`` filename token.

    Parameters
    ----------
    name : str
        Human sample label; the start of the templated filename.
    dets : list
        Detectors (the q-range / which-detector choice).  Staged for the run.
    axes : list of ScanAxis
        The scan dimensions, OUTERMOST FIRST.  Slow/in-vacuum axes (arc, prs, temperature)
        should come first; a guardrail warns otherwise (see ``check_order``).
    reads : list, optional
        Extra readables recorded at every event (e.g. ``[energy, waxs, xbpm2, xbpm3]``).  The
        axes' own ``record`` Signals and ``reads`` are merged in automatically.
    setup : callable() -> plan, optional
        Apparatus/geometry setup run ONCE just after ``open_run`` (e.g. set grazing geometry,
        turn the heater on, ensure attenuators in).  Its moves are recorded in the run.
    geometry : str, optional
        ``"reflection"`` / ``"transmission"`` (goes in md).
    scan_name : str
        Names the run (e.g. ``"giwaxs_tempramp"``).
    md : dict, optional
        Caller intent merged into the run md (``project_name`` etc.).
    baseline : list, optional
        Constants recorded once (SDD, setpoints, alignment offsets ...).
    name_tokens : sequence of str, optional
        ``{field}`` tokens appended to the filename.  If None, auto-build from each axis's
        recorded Signal (``ai{incident_angle}`` etc.) so the filename reflects the scan.
    check_order : bool
        If True (default), warn when slow axes are nested inside faster ones.
    sample : _samples.Sample, optional
        If given, ``name`` defaults to ``sample.name`` and its ``md`` is merged.

    Returns
    -------
    The plan; ``yield from`` it (or ``RE(acquire(...))``).
    """
    if sample is not None:
        name = name or sample.name
        md = merge_md(md, sample.md)

    if check_order:
        _check_axis_order(axes)

    reads = list(reads) if reads else []
    # auto-collect the axes' recorded Signals + extra reads so every event captures them
    axis_reads = []
    for a in axes:
        if a.record is not None and a.record not in reads and a.record not in axis_reads:
            axis_reads.append(a.record)
        for r in a.reads:
            if r not in reads and r not in axis_reads:
                axis_reads.append(r)
    all_reads = reads + axis_reads

    # auto filename tokens from the recording axes (unless caller overrides)
    if name_tokens is None:
        toks = []
        for a in axes:
            if a.record is not None:
                toks.append(a.name + a.token("{}"))   # e.g. "energy{energy}" -> "energy{energy}"
        name_tokens = toks
    sample_name = fname(name, *name_tokens)

    def _measure():
        yield from bps.trigger_and_read(list(dets) + all_reads)

    def _body():
        if setup is not None:
            yield from setup()
        yield from nest_axes(axes, _measure)

    return (yield from one_sample_run(
        _body, dets, sample_name=sample_name, scan_name=scan_name,
        geometry=geometry, md=md, baseline=baseline))


def acquire_bar(samples, dets, axes_for, *, reads=None, setup_for=None, geometry=None,
                scan_name="acquire", md=None, baseline_for=None, name_tokens=None,
                check_order=True, goto=None):
    """Run :func:`acquire` for each sample on a bar (ONE run per sample).

    ``axes_for(sample) -> list[ScanAxis]`` and (optionally) ``setup_for(sample) -> plan`` /
    ``baseline_for(sample) -> list`` are callables so per-sample coordinates (e.g. an aligned
    incidence zero, per-sample energy lists) can vary.  Each sample is coarse-positioned via
    ``goto`` (default :func:`_core.goto_sample`) before its run.

    For slow-axis economy across the WHOLE bar (move ``waxs.arc`` once for all samples), use
    :func:`_core.multi_sample_run` instead -- that is a different run topology (N runs open at
    once) and is offered separately.
    """
    _goto = goto if goto is not None else (lambda s: goto_sample(s))
    for s in samples:
        yield from _goto(s)
        axes = axes_for(s)
        setup = (lambda: setup_for(s)) if setup_for is not None else None
        baseline = baseline_for(s) if baseline_for is not None else None
        yield from acquire(
            s.name, dets, axes, reads=reads, setup=setup, geometry=geometry,
            scan_name=scan_name, md=merge_md(md, s.md), baseline=baseline,
            name_tokens=name_tokens, check_order=check_order)


# ===========================================================================
# Ready-made axis constructors (the common concerns)
# ===========================================================================
def energy_axis(energies, *, settle=2.0, reverse_alternate=False, flux_signal=None,
                flux_threshold=None, max_reseek=3, record_name="energy_set"):
    """A DCM energy scan axis.  Records energy via a Signal so ``{energy_set}`` is a token.

    The DCM ``energy`` device itself is also typically in ``reads`` (giving ``{energy_energy}``);
    this axis additionally records the *commanded* setpoint and can re-seek the beam.

    Parameters
    ----------
    energies : sequence
        Energies (eV), in visiting order (e.g. up, or up+down -- just concatenate).
    settle : float
        Sleep after each energy move.
    flux_signal, flux_threshold : optional
        If both given, re-seek (re-command energy + wait) when I0 drops below threshold.
    """
    sig = Signal(name=record_name, value=0.0)                     # noqa: F821

    def _per_point():
        if flux_signal is not None and flux_threshold is not None:
            tries = 0
            while flux_signal.get() < flux_threshold and tries < max_reseek:
                yield from bps.mv(energy, energy.position)        # noqa: F821 (re-seek)
                yield from bps.sleep(settle)
                tries += 1
        else:
            yield from bps.null()

    return ScanAxis("energy", energies, device=energy,           # noqa: F821
                    record=sig, settle=settle, per_point=_per_point,
                    reads=[energy],                              # noqa: F821 (gives {energy_energy})
                    speed=SPEED_MEDIUM, reverse_alternate=reverse_alternate)


def temperature_axis(heater, setpoints, *, tol=1.0, poll=10.0, timeout=7200.0, soak=60.0,
                     first_soak=None, reverse_alternate=False):
    """A temperature ramp axis using a ``Heater`` (see ``technique_C_temperature``).

    ``heater`` must provide ``set_plan(setpoint)``, ``read_value()``, ``units`` and a
    recordable ``readback`` Signal (the C-technique ``Heater`` abstraction).  Each point sets
    the temperature and equilibrates (with timeout) before descending inward.  Temperature is
    SLOW -> put this axis outermost.

    The heater's read-back Signal is recorded, so the *measured* temperature lands in the
    stream at each event.
    """
    def _move(setpoint):
        import time
        first = (setpoints and setpoint == setpoints[0])
        use_soak = (first_soak if (first and first_soak is not None) else soak)
        yield from heater.set_plan(setpoint)
        start = time.time()
        t = heater.read_value()
        heater.sync_readback()
        while abs(t - setpoint) > tol:
            yield from bps.sleep(poll)
            t = heater.read_value()
            heater.sync_readback()
            if time.time() - start > timeout:
                break
        if use_soak:
            yield from bps.sleep(use_soak)
        heater.sync_readback()

    # the recordable readback is the heater's own Signal; add it to reads
    return ScanAxis("temperature", setpoints, move=_move,
                    record=None, reads=[heater.readback],
                    speed=SPEED_SLOW, reverse_alternate=reverse_alternate)


def incidence_axis(th_axis, th0, incident_angles, *, settle=0.0, record_name="incident_angle"):
    """A grazing-incidence-angle axis: visit ``th0 + ai`` for each ``ai``.

    Records the *relative* incident angle (``ai``) via a Signal so ``{incident_angle}`` is a
    token, while moving the absolute axis to ``th0 + ai``.  Medium speed.
    """
    sig = Signal(name=record_name, value=0.0)                    # noqa: F821

    def _move(ai):
        yield from bps.mv(th_axis, th0 + ai)
        sig.put(ai)
        if settle:
            yield from bps.sleep(settle)

    return ScanAxis("incidence", incident_angles, move=_move, record=sig,
                    speed=SPEED_MEDIUM)


def motor_axis(name, device, values, *, settle=0.0, record=True, speed=SPEED_FAST,
               reverse_alternate=False):
    """A generic single-motor axis (e.g. ``waxs`` arc, ``prs``, a piezo).

    If ``record`` is True, the device is added to ``reads`` so its position is in the stream
    (``{<device.name>_<...>}``).  Set ``speed=SPEED_SLOW`` for ``waxs``/``prs`` so the
    guardrail keeps them outermost.
    """
    return ScanAxis(name, values, device=device, settle=settle,
                    reads=([device] if record else []),
                    speed=speed, reverse_alternate=reverse_alternate)


def spatial_grid_axes(*, x_motor=None, x=None, y_motor=None, y=None, snake=True,
                      record=True, dose=False):
    """Build 1-D or 2-D spatial-sampling axes (a single spot, a line, or a grid).

    Returns a LIST of axes (0, 1, or 2) you splice into your axis stack -- usually innermost
    (fast piezo).  ``x``/``y`` are the absolute positions to visit; pass just one for a line,
    both for a grid, neither for a single spot.

    Parameters
    ----------
    x_motor, y_motor : positioners (e.g. piezo.x, piezo.y)
    x, y : sequences of absolute positions
    snake : bool
        Snake the inner (y) axis to avoid backtracking.
    record : bool
        Record the motor positions in the stream.
    dose : bool
        Mark these as the dose-walk axes (purely informational here; the fresh-spot behavior
        is better applied via the ``_preprocessors.fresh_spot_wrapper`` at the run level).
    """
    axes = []
    if x_motor is not None and x is not None:
        axes.append(motor_axis("x", x_motor, x, record=record, speed=SPEED_FAST))
    if y_motor is not None and y is not None:
        axes.append(motor_axis("y", y_motor, y, record=record, speed=SPEED_FAST,
                               reverse_alternate=snake))
    return axes


def potential_axis(set_potential, potentials, *, equilibration=5.0, readback=None,
                   record_name="potential_v"):
    """An applied-potential (electrochemistry) axis.

    ``set_potential(V) -> plan`` is your rig-specific potentiostat command.  Records the
    commanded ``V`` (``{potential_v}``); add ``readback`` to also record measured cell V/I.
    """
    sig = Signal(name=record_name, value=0.0)                    # noqa: F821

    def _move(v):
        yield from set_potential(v)
        sig.put(v)
        if equilibration:
            yield from bps.sleep(equilibration)

    reads = [readback] if readback is not None else []
    return ScanAxis("potential", potentials, move=_move, record=sig, reads=reads,
                    speed=SPEED_MEDIUM)


def rh_axis(set_rh, rh_setpoints, *, record_name="rh", live_rh=None):
    """A relative-humidity (SVA) axis.

    ``set_rh(target) -> plan`` ramps the MFCs and equilibrates.  Records the *commanded* RH;
    pass ``live_rh`` (a Signal you update from ``readHumidity()``) to record the measured RH
    at each event instead/also.
    """
    sig = Signal(name=record_name, value=0.0)                    # noqa: F821

    def _move(target):
        yield from set_rh(target)
        sig.put(target)

    reads = [live_rh] if live_rh is not None else []
    return ScanAxis("rh", rh_setpoints, move=_move, record=sig, reads=reads,
                    speed=SPEED_SLOW)


def time_axis(n_frames, *, period=0.0, record_name="frame", elapsed_signal=None):
    """A time-series axis: ``n_frames`` points, ``period`` seconds apart.

    Records the frame index (``{frame}``).  Pass ``elapsed_signal`` (a Signal you update with
    elapsed seconds) to also record wall-clock elapsed time per event.  The ``period`` sleep is
    applied as the axis settle.
    """
    sig = Signal(name=record_name, value=0)                      # noqa: F821
    t0 = {}

    def _move(i):
        # Software-only "move": no hardware motion, just stamp the frame index + elapsed time.
        # (ScanAxis.move_to tolerates a plain function here; the period wait is the axis settle.)
        import time
        if i == 0:
            t0["t"] = time.monotonic()
        sig.put(int(i))
        if elapsed_signal is not None:
            elapsed_signal.put(time.monotonic() - t0.get("t", time.monotonic()))

    reads = [elapsed_signal] if elapsed_signal is not None else []
    return ScanAxis("time", list(range(int(n_frames))), move=_move, record=sig,
                    settle=period, reads=reads, speed=SPEED_FAST)


# ===========================================================================
# Manual / interactive concern (prompt the user; capture what they tell us)
# ===========================================================================
# Real experiments often have steps the beamline cannot automate: "swap the sample bar and
# type the new thickness", "I set the Linkam to 35 C by hand -- confirm", "wait until I start
# the syringe pump".  These must be (a) composable like any other layer and (b) honor Tenet 2:
# a value the user types becomes a RECORDED Signal, not a filename string or lost prose.
#
# We use ``bps.input_plan(prompt)`` -- the RunEngine-driven prompt (NOT a raw ``input()``), so
# pause/resume and the document model still work.

def _coerce(value, cast):
    if cast is None:
        return value
    try:
        return cast(value)
    except Exception:
        return value


def pause_for_user(prompt="Press <enter> to continue"):
    """Plan: stop and wait for the user to acknowledge, recording nothing.

    For the pure "wait until I tell you to go" case (e.g. "start the pump, then <enter>").
    Use as a ``setup`` step or splice into a sequence.  Nothing is recorded.
    """
    yield from bps.input_plan(prompt + ": ")


def manual_value(prompt, signal, *, cast=float, echo=True):
    """Plan: prompt the user for a value and ``.put`` it onto a recordable ``signal``.

    The value the user types is captured on ``signal`` (e.g. ``Signal(name="thickness_nm")``)
    so it is recorded the next time ``signal`` is read -- include ``signal`` in your ``reads``
    or ``baseline`` so it lands in the data (and is then a ``{thickness_nm}`` filename token).

    Parameters
    ----------
    prompt : str
        What to ask, e.g. ``"Measured film thickness (nm)"``.
    signal : ophyd Signal
        Recordable destination for the entered value (named whatever you want; the value need
        not be a string).
    cast : callable or None
        Coerce the typed string (default ``float``).  Pass ``str`` to keep text, ``int``, etc.
        If coercion fails, the raw string is stored.
    echo : bool
        Print the captured value.
    """
    raw = yield from bps.input_plan("{} = ".format(prompt))
    val = _coerce(raw, cast)
    signal.put(val)
    if echo:
        print("recorded {} = {!r}".format(signal.name, val))
    return val


def manual_step(prompt, *, signals=None, casts=None, confirm=True):
    """Plan: a one-shot manual checkpoint -- optionally collect several values into Signals.

    Use as a ``setup`` step (run once after the run opens, inside the run so values are
    recorded) or anywhere in a sequence.  Combines an acknowledgement and zero or more typed
    values.

    Parameters
    ----------
    prompt : str
        Instruction shown first, e.g. ``"Swap to the annealed bar"``.
    signals : list of ophyd Signal, optional
        One prompt per signal; each entered value is ``.put`` onto it (and should be in your
        ``baseline``/``reads`` to be recorded).  The prompt text uses each signal's name.
    casts : list, optional
        Per-signal coercion (default ``float`` for all).  Same length as ``signals``.
    confirm : bool
        If True, also require a final <enter> acknowledgement.

    Examples
    --------
    >>> thickness = Signal(name="thickness_nm", value=0.0)
    >>> temp_set  = Signal(name="temperature_set_manual", value=0.0)
    >>> # as a setup step, recording both values in the run baseline:
    >>> acquire("S1", dets, axes,
    ...         setup=lambda: manual_step("Load S1; read off the prep sheet",
    ...                                   signals=[thickness, temp_set]),
    ...         baseline=[thickness, temp_set])
    """
    print("\n*** MANUAL STEP: {} ***".format(prompt))
    signals = signals or []
    casts = casts or [float] * len(signals)
    out = []
    for sig, cast in zip(signals, casts):
        val = yield from manual_value(sig.name, sig, cast=cast)
        out.append(val)
    if confirm:
        yield from bps.input_plan("Done? <enter> to proceed: ")
    return out


def manual_axis(name, prompt, values=None, *, signal=None, cast=float,
                action_each=None, speed=SPEED_SLOW, record_name=None):
    """A scan axis driven by the USER at each point (manual swaps / hand-set conditions).

    Two modes:

    * **Enumerated** (``values`` given): iterate a known list (e.g. sample labels, hand-set
      temperatures the user dials in).  At each point the user is prompted to set up that point
      (``prompt`` shown with the value), then optionally to type a measured value onto
      ``signal``.  If ``signal`` is None but ``values`` are given, the value itself is recorded
      via an auto Signal (``{<name>}``), so e.g. the hand-set temperature is in the data.
    * **Open-ended** (``values`` None): repeat until the user signals stop.  Each iteration
      prompts for setup + a value; entering an empty/``stop`` value ends the axis.  Useful for
      "keep going as long as I keep loading samples".

    Parameters
    ----------
    name : str
        Axis label.
    prompt : str
        Instruction per point, e.g. ``"Set the sample to position"`` or ``"Dial the hot stage to"``.
    values : sequence or None
        The points (e.g. ``[35, 50, 65]`` for hand-set temperatures, or sample labels).  None
        = open-ended loop until the user stops.
    signal : ophyd Signal, optional
        Where to record a value the user types at each point.  If None and ``values`` given,
        an auto Signal records the enumerated value.
    cast : callable
        Coercion for the typed value (default ``float``).
    action_each : callable(value) -> plan, optional
        Extra plan run after the prompt (e.g. trigger something, or move a motor the user's
        value implies).
    speed : int
        Defaults to SLOW (manual swaps are the slowest thing in any experiment -> outermost).
    record_name : str, optional
        Name for the auto Signal (default ``name``).

    Notes
    -----
    Open-ended axes have unknown length; the ordering guardrail treats them as length 1 for
    its estimate.  Put manual axes outermost (they are slow) -- this is also where they make
    sense (you do not want to hand-swap a sample inside an energy loop).
    """
    rec = signal
    auto = None
    if rec is None and (values is not None):
        auto = Signal(name=(record_name or name), value=0.0)     # noqa: F821
        rec = auto

    def _move_enum(v):
        # show the instruction with the target value, then optionally capture a typed value
        yield from bps.input_plan("{} {}  -- ready? <enter>: ".format(prompt, v))
        if signal is not None:
            typed = yield from bps.input_plan("  enter {} = ".format(signal.name))
            signal.put(_coerce(typed, cast))
        elif auto is not None:
            auto.put(_coerce(v, cast) if not isinstance(v, str) else v)
        if action_each is not None:
            yield from action_each(v)

    if values is not None:
        ax = ScanAxis(name, values, move=_move_enum, record=rec, speed=speed)
        return ax

    # open-ended: build a generator-of-values lazily is awkward for ScanAxis (which wants a
    # concrete list); instead we return a *plan factory* the recipe runs directly.  To keep a
    # uniform interface we expose it as a ScanAxis with a sentinel and a custom nesting helper
    # is overkill -- so for open-ended use, prefer composing ``manual_loop`` (below).
    raise ValueError(
        "manual_axis with values=None is open-ended; use manual_loop(...) instead, which "
        "yields the inner plan repeatedly until the user stops.")


def manual_loop(prompt, inner, *, signal=None, cast=float, stop_words=("", "stop", "q")):
    """Repeat ``inner()`` once per user-driven iteration until the user stops (open-ended).

    The composable counterpart to an open-ended manual axis (unknown count).  Each iteration:
    prompt the user to set up the next point, optionally capture a typed value onto ``signal``
    (recorded if ``signal`` is in your reads/baseline), run ``inner()`` (e.g. the rest of the
    nested axes + measurement), and ask whether to continue.

    Because the count is unknown, this is its own small driver rather than a :class:`ScanAxis`;
    splice it where a manual outer loop belongs (outermost).

    Parameters
    ----------
    prompt : str
        Per-iteration instruction, e.g. ``"Load the next sample"``.
    inner : callable() -> plan
        What to do for each manually-staged point (typically the inner axes + trigger_and_read,
        or a whole :func:`acquire` body).
    signal : ophyd Signal, optional
        Capture a per-iteration typed value (recorded if read/baselined).
    cast : callable
        Coercion for the typed value.
    stop_words : tuple of str
        Entering any of these (at the continue prompt) ends the loop.
    """
    i = 0
    while True:
        yield from bps.input_plan("{} (#{}) -- ready? <enter>: ".format(prompt, i))
        if signal is not None:
            typed = yield from bps.input_plan("  enter {} = ".format(signal.name))
            signal.put(_coerce(typed, cast))
        yield from inner()
        again = yield from bps.input_plan("Another? <enter>=yes, type 'stop' to finish: ")
        if again.strip().lower() in stop_words and again.strip() != "":
            break
        # treat empty as "yes, continue"; an explicit stop word ends it
        if again.strip().lower() in ("stop", "q", "n", "no"):
            break
        i += 1

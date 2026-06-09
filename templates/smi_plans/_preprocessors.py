"""
smi_plans._preprocessors
=========================

Reusable, **opt-in** Bluesky plan preprocessors (decorators / wrappers) for the
NSLS-II SMI-SWAXS beamline.

Design goals
------------
* Each preprocessor is a *plan-mutating wrapper*: it takes a plan (generator) and
  returns a new plan, injecting behavior at specific message types (e.g. just before
  each ``trigger_and_read``, or right after ``open_run``).  They are built on
  ``bluesky.preprocessors`` (``plan_mutator`` / ``msg_mutator`` / ``finalize_wrapper`` /
  ``baseline_wrapper``) so they compose cleanly and stay inside the RunEngine document
  model (no ``RE()``-in-loops, no raw ``cam.put``).
* They are **opt-in and composable**: a technique plan applies only the ones it needs,
  in a well-defined order.  Nothing here mutates global state.
* They encode the *hard-won operational idioms* from the legacy corpus (fresh-spot dose
  walking, ensure-attenuators-in, beam-loss re-seek, slow-axis economy, baseline capture)
  so those behaviors can be reused without copy-paste.

How the message-level injection works
-------------------------------------
The bluesky RunEngine consumes a stream of ``Msg`` objects.  A measurement
(``trigger_and_read``) expands into a ``trigger`` / ``create`` / ``read`` / ``save``
group.  We hook on the ``'save'`` message (emitted once per event, *after* the readings
are taken) to advance per-event side effects like the fresh-spot nudge -- so the *next*
event lands on a new spot, and the position that was actually read is the one recorded.
We hook on ``'open_run'`` to inject run-scoped setup (e.g. ensure attenuators in).

.. important::
    This module references beamline globals that are injected by the SMI profile
    collection at runtime and are **not importable standalone** (``bps``, ``bpp``,
    ``Signal``, ``att2_9``, ``xbpm2``/``xbpm3``, ``energy``, ``np`` ...).  Import / run
    these only inside the live beamline IPython environment.

Required runtime globals
------------------------
``bps`` (bluesky.plan_stubs), ``bpp`` (bluesky.preprocessors), ``np``, plus whatever
device objects you pass in as arguments.  Functions take the *device* as an argument
wherever possible so this module has no hard device dependencies of its own.
"""

from functools import wraps

try:  # let the file import for tooling outside the beamline, but never silently no-op at runtime
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover - only hit outside the beamline env
    bps = None
    bpp = None


__all__ = [
    "fresh_spot_wrapper",
    "fresh_spot_decorator",
    "ensure_in_wrapper",
    "ensure_in_decorator",
    "beam_loss_reseek_wrapper",
    "beam_loss_reseek_decorator",
    "baseline_wrapper",
    "cleanup_wrapper",
    "extra_dets_wrapper",
    "extra_dets_decorator",
]


# ---------------------------------------------------------------------------
# 1. Fresh-spot dose walking
# ---------------------------------------------------------------------------
def fresh_spot_wrapper(plan, motor, step, *, axis_label=None, per="event", reset=True):
    """Nudge ``motor`` by ``step`` after every measurement to land on a fresh spot.

    This generalizes the ubiquitous legacy idiom ``piezo.x = xs - counter*30um`` /
    ``np.linspace`` dose walk used to mitigate beam damage.  Because the nudge happens on
    the ``'save'`` message (after the event is recorded), the position that was actually
    illuminated is the one in the data, and the *next* event moves on.

    Parameters
    ----------
    plan : generator
        The plan to wrap.
    motor : ophyd positioner
        The fast axis to step (e.g. ``piezo.x``, ``piezo.y``, ``stage.x``).
    step : float
        Signed increment applied per ``per`` unit (negative walks "down").
    axis_label : str, optional
        Only used for a human-readable log line.
    per : {"event"}
        Currently steps once per recorded event.  Reserved for future "per-energy" etc.
    reset : bool
        If True, return ``motor`` to its starting position when the plan finishes.

    Notes
    -----
    The position is recorded automatically if ``motor`` is in your ``trigger_and_read``
    list; you generally do *not* need to format it into the filename.
    """
    start = {}

    def _mutate(msg):
        if msg.command == "open_run":
            # capture the starting position the first time a run opens
            start.setdefault("pos", motor.position)
            return None, None                     # let open_run pass through unmodified
        if msg.command == "save":
            # Insert the nudge AFTER the event is saved (the original 'save' passes through;
            # we only append a tail).  -> the recorded spot is the illuminated one; the
            # *next* event lands fresh.
            def _tail():
                yield from bps.mvr(motor, step)
            return None, _tail()
        return None, None                         # no-op for every other message

    def _inner():
        yield from bpp.plan_mutator(plan, _mutate)
        if reset and "pos" in start:
            yield from bps.mv(motor, start["pos"])

    return (yield from _inner())


def fresh_spot_decorator(motor, step, *, axis_label=None, per="event", reset=True):
    """Decorator form of :func:`fresh_spot_wrapper`."""
    def _dec(plan_func):
        @wraps(plan_func)
        def _wrapped(*args, **kwargs):
            return (yield from fresh_spot_wrapper(
                plan_func(*args, **kwargs), motor, step,
                axis_label=axis_label, per=per, reset=reset))
        return _wrapped
    return _dec


# ---------------------------------------------------------------------------
# 2. Ensure-a-device-is-in (attenuators, beamstop, gate valve) for the measurement
# ---------------------------------------------------------------------------
def ensure_in_wrapper(plan, setup, *, teardown=None):
    """Run ``setup`` right after the run opens, and optionally ``teardown`` at the end.

    Solves the recurring footgun where an alignment routine leaves attenuators *out*
    (or a gate valve open / beamstop in the wrong place), and the subsequent measurement
    silently runs in the wrong configuration.  Pass a small plan that puts things in the
    state the *measurement* requires; it executes once per run, after ``open_run`` so it
    is inside the run (its moves are recorded), but before the first event.

    Parameters
    ----------
    plan : generator
    setup : generator-function (no args) returning a plan
        e.g. ``lambda: bps.mv(att2_9.close_cmd, 1)`` wrapped, or a named ``_atten_in``
        plan.  Called fresh each run.
    teardown : generator-function (no args), optional
        Restores the pre-measurement state; runs in a ``finalize`` so it executes even on
        error/abort.

    Examples
    --------
    >>> def _atten_in():
    ...     yield from bps.mv(att2_9.close_cmd, 1)
    ...     yield from bps.sleep(1)
    >>> plan = ensure_in_wrapper(inner(), _atten_in)
    """
    def _mutate(msg):
        if msg.command == "open_run":
            # Let open_run pass through (its uid response must reach the host plan), then
            # inject the setup plan immediately after, inside the run.
            def _tail():
                yield from setup()
            return None, _tail()
        return None, None

    body = bpp.plan_mutator(plan, _mutate)
    if teardown is not None:
        return (yield from bpp.finalize_wrapper(body, teardown()))
    return (yield from body)


def ensure_in_decorator(setup, *, teardown=None):
    """Decorator form of :func:`ensure_in_wrapper`."""
    def _dec(plan_func):
        @wraps(plan_func)
        def _wrapped(*args, **kwargs):
            return (yield from ensure_in_wrapper(
                plan_func(*args, **kwargs), setup, teardown=teardown))
        return _wrapped
    return _dec


# ---------------------------------------------------------------------------
# 3. Beam-loss re-seek (recover when the ring/optics drop I0 mid-scan)
# ---------------------------------------------------------------------------
def beam_loss_reseek_wrapper(plan, flux_signal, threshold, recover, *, max_tries=3):
    """Before each event, if ``flux_signal`` reads below ``threshold``, run ``recover``.

    Generalizes the legacy ``if xbpm2.sumX.get() < 50: re-move energy; sleep`` guard.
    The check runs on the ``'create'`` message (just before readings are latched), so a
    recovered beam is what gets recorded.

    Parameters
    ----------
    plan : generator
    flux_signal : ophyd Signal
        Readback used as I0, e.g. ``xbpm2.sumX`` or ``xbpm3.sumX``.
    threshold : float
        Re-seek if the reading is below this.
    recover : generator-function (no args) -> plan
        e.g. re-set the DCM energy and sleep, or nudge the mirror.  Called fresh each time.
    max_tries : int
        Give up after this many recovery attempts for a single event (avoids infinite loops
        if the beam is truly down).
    """
    def _mutate(msg):
        if msg.command == "create":
            def _head():
                tries = 0
                while flux_signal.get() < threshold and tries < max_tries:
                    yield from recover()
                    tries += 1
                yield msg
            return _head(), None
        return None, None

    return (yield from bpp.plan_mutator(plan, _mutate))


def beam_loss_reseek_decorator(flux_signal, threshold, recover, *, max_tries=3):
    """Decorator form of :func:`beam_loss_reseek_wrapper`."""
    def _dec(plan_func):
        @wraps(plan_func)
        def _wrapped(*args, **kwargs):
            return (yield from beam_loss_reseek_wrapper(
                plan_func(*args, **kwargs), flux_signal, threshold, recover,
                max_tries=max_tries))
        return _wrapped
    return _dec


# ---------------------------------------------------------------------------
# 4. Baseline capture (constants recorded once at run start & end)
# ---------------------------------------------------------------------------
def baseline_wrapper(plan, devices):
    """Record ``devices`` in a 'baseline' stream at run open & close.

    Thin pass-through to ``bluesky.preprocessors.baseline_wrapper`` so technique files have
    one import surface.  Use this for everything that is *constant during the run* but
    should still be in the data: SDD (``pil2M_pos.z``), attenuator state, sample positions,
    temperature setpoint, alignment offsets, mirror/undulator config, etc.

    Anything that *changes* during the run must instead go in your ``trigger_and_read``
    list (primary stream), not here.
    """
    return (yield from bpp.baseline_wrapper(plan, devices))


# ---------------------------------------------------------------------------
# 5. Cleanup / finalize (always restore safe state, even on Ctrl-C / error)
# ---------------------------------------------------------------------------
def cleanup_wrapper(plan, cleanup):
    """Run ``cleanup`` after ``plan`` whether it succeeds, errors, or is aborted.

    Thin pass-through to ``finalize_wrapper``.  Use for "reset exposure time", "close the
    SAXS gate valve", "return the slow axis", "att out" etc.  ``cleanup`` is a
    generator-function (no args) returning a plan, called once at teardown.
    """
    return (yield from bpp.finalize_wrapper(plan, cleanup()))


# ---------------------------------------------------------------------------
# 6. Extra detectors / signals on every event (e.g. always read xbpm + energy)
# ---------------------------------------------------------------------------
def extra_dets_wrapper(plan, extra):
    """Append ``extra`` readables to every ``read`` bundle in ``plan``.

    Lets a technique declare "always also record ``[energy, waxs, xbpm2, xbpm3]``" once,
    instead of threading them through every ``trigger_and_read`` call.  Works by injecting
    ``read`` messages for ``extra`` right before each ``save``.

    Parameters
    ----------
    plan : generator
    extra : list of readables
        Devices/Signals to add to the primary event (these become available as
        ``{device_field}`` filename tokens because they are recorded).
    """
    def _mutate(msg):
        if msg.command == "save":
            def _head():
                for dev in extra:
                    yield from bps.read(dev)
                yield msg
            return _head(), None
        return None, None

    return (yield from bpp.plan_mutator(plan, _mutate))


def extra_dets_decorator(extra):
    """Decorator form of :func:`extra_dets_wrapper`."""
    def _dec(plan_func):
        @wraps(plan_func)
        def _wrapped(*args, **kwargs):
            return (yield from extra_dets_wrapper(plan_func(*args, **kwargs), extra))
        return _wrapped
    return _dec

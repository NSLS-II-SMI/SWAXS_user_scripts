"""
technique_L_printing
===================

Archetype L -- In-situ 3D-printing / additive manufacturing (operando).

Follow crystallization / structure development during extrusion printing.  Unlike every other
archetype, **the printer is the MASTER**: it drives the experiment and the beamline *reacts* to
print events signaled over EPICS digital-IO bits (``XF:11ID-CT{M1}bi2`` = monitor/"keep
running", ``bi3`` = ready-for-trigger, ``bi4`` = fire/trigger).  The X-ray beam is positioned at
the **middle of the extruded filament** -- a height offset of *half the filament width* below the
substrate interface found by derivative-edge height alignment (``height`` in
``legacy/30-user-ECD-3dprinterLutz.py``).  After a print, ~30-minute repeated WAXS-arc sweeps
track post-print crystallization.

.. note::

   ===========================================================================================
   THE "EXTERNAL-MASTER MONITORING RUN" PATTERN  (sanctioned; see BEST_PRACTICES open question #6)
   ===========================================================================================
   The other techniques follow "one run per sample".  An operando print does NOT fit that:
   there is no a-priori list of samples/points -- the printer fires when *it* is ready, an
   unknown number of times, over a long session.  The sanctioned shape is a **single, long-lived
   "monitoring run"** that stays open and records ONE frame each time the printer fires, stamping
   a ``print_event`` index (and the filament position) as a Signal per frame.

   Crucially the wait for the trigger is done **as a generator INSIDE the run**, not as a
   busy-wait outside the RunEngine:

       * legacy ``track_printer`` polls with ``while ...: if trigger.get()==1: <acquire>;
         bps.sleep(0.5)`` -- correct *shape* but it wraps ``bp.count`` (run-per-frame) and the
         polling is a bare ``while`` in a plan that opens many runs;
       * legacy ``triggered_series`` / ``start_printing_below_nozzle`` call ``RE(...)`` inside a
         Python ``while`` -- the Tenet-7 anti-pattern (breaks pause/resume; no single run).

   Here the whole monitoring session is ONE ``@run_decorator`` run; the trigger wait is a
   generator (``bps.sleep`` polling, or ``bps.wait_for`` on a status that resolves when the bit
   flips), and each fire emits a ``trigger_and_read`` event into that one run.  This keeps the
   acquisition inside the document model (pausable, resumable, fully recorded) while letting the
   external master gate it.  This pattern is FLAGGED in ``BEST_PRACTICES_DRAFT.md`` open question
   #6 as the sanctioned shape for printer / autonomous-synthesis / long-kinetics sessions.
   ===========================================================================================

Gold / legacy reference: ``legacy/30-user-ECD-3dprinterLutz.py`` (``track_printer`` polling
generator gated by ``XF:11ID-CT{M1}bi2/3/4``; ``height`` half-filament offset
``bps.mvr(stage.y, -height)``; ``track_printer_timeRes`` post-print 1800 s WAXS-arc sweep),
``legacy/30-user-ECD-3dprinterLutz_OffsetStart.py``, ``legacy/30-user-Printer.py``
(``Printer_3D`` device; ``caget``/``caput`` handshake on ``XF:11ID-CT{M3}bi2``).

What this file gives you
------------------------
* :func:`printer_trigger_signals` -- build the three EPICS trigger-bit Signals by hand-off.
* :func:`wait_for_printer_fire` -- generator that waits for the next "fire" bit INSIDE the run
  (``bps.sleep`` polling; never a busy-wait outside RE).
* :func:`printer_triggered_run` -- the monitoring run: ONE long-lived run that records a frame
  per printer fire, stamping ``print_event`` index + filament position, until ``n_events`` is
  reached or the master clears the monitor bit (``until_stopped``).
* :func:`print_crystallization_followup_run` -- after a print, ONE run with a repeated WAXS-arc
  sweep time-series (~30 min) tracking crystallization.
* :func:`beam_to_filament_middle` -- move the beam to the filament middle (half-width offset).
* :func:`example` / :func:`example_followup` -- runnable, fully-specified examples.

Idioms preserved: the printer EPICS-bit handshake, the half-filament-width height offset, the
arc-aware detector list, the post-print 30-min WAXS-arc crystallization sweep, baseline capture
of constants, cleanup (clear the trigger bit, return the beam off the filament) on error.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``bpp``, ``Signal``, ``EpicsSignal``, ``stage``,
    ``waxs``, ``pil2M``, ``pil900KW``, ``pil300KW``, ``xbpm3``, ``pil2M_pos``,
    ``det_exposure_time``.  The printer trigger bits are EPICS PVs (defaults
    ``XF:11ID-CT{M1}bi2/3/4``); pass your own Signals to override.
"""

import time

from ._core import (one_sample_run, saxs_waxs_dets, fname)
from ._preprocessors import cleanup_wrapper

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "printer_trigger_signals", "wait_for_printer_fire", "beam_to_filament_middle",
    "printer_triggered_run", "print_crystallization_followup_run", "example",
    "example_followup",
]


# Default printer digital-IO PVs (1st-gen printer cabinet M1).  bi2 = monitor/keep-running,
# bi3 = ready-for-trigger (handshake back to the printer), bi4 = fire/trigger.
DEFAULT_MONITOR_PV = "XF:11ID-CT{M1}bi2"
DEFAULT_READY_PV = "XF:11ID-CT{M1}bi3"
DEFAULT_TRIGGER_PV = "XF:11ID-CT{M1}bi4"


# ---------------------------------------------------------------------------
# Trigger-bit Signals
# ---------------------------------------------------------------------------
def printer_trigger_signals(*, monitor_pv=DEFAULT_MONITOR_PV, ready_pv=DEFAULT_READY_PV,
                            trigger_pv=DEFAULT_TRIGGER_PV):
    """Build the three printer EPICS digital-IO ``Signal`` objects.

    Returns ``(monitor, ready, trigger)`` ``EpicsSignal`` objects wrapping the printer
    handshake bits.  ``monitor`` (bi2) is the master "keep monitoring" flag, ``ready`` (bi3) is
    handed back to the printer to say the beamline is armed, ``trigger`` (bi4) is the printer's
    "fire now" bit.  Mirrors ``track_printer``'s three ``EpicsSignal(...)`` constructions.
    """
    monitor = EpicsSignal(monitor_pv, name="printer_monitor")      # noqa: F821
    ready = EpicsSignal(ready_pv, name="printer_ready")            # noqa: F821
    trigger = EpicsSignal(trigger_pv, name="printer_trigger")      # noqa: F821
    return monitor, ready, trigger


# ---------------------------------------------------------------------------
# Wait for the next printer "fire" -- INSIDE the run, as a generator
# ---------------------------------------------------------------------------
def wait_for_printer_fire(trigger, monitor, *, poll=0.5, ready=None, timeout=None):
    """Wait (as a plan) for the next printer fire; return True on fire, False if monitoring ends.

    This is the sanctioned generator form of the trigger wait (see the module ``note``): it
    polls the trigger bit with ``yield from bps.sleep(poll)`` -- a *generator* the RunEngine
    drives, NOT a busy-wait outside ``RE``.  (For a status-object alternative you would
    ``yield from bps.wait_for([status])`` where ``status`` resolves when the bit flips; polling
    is used here because the legacy bits are plain ``bi`` PVs without a subscription helper.)

    Behavior:
      * returns ``True`` as soon as ``trigger`` reads 1 (printer fired);
      * returns ``False`` if ``monitor`` drops to 0 (master ended the session) or ``timeout``
        (s) elapses;
      * if ``ready`` is given, it is set to 1 between fires to hand the "armed" state back to the
        printer.

    The caller acknowledges the fire (clears ``trigger``) after recording the frame, so the next
    poll waits for the *next* fire.
    """
    t0 = time.time()
    if ready is not None:
        yield from bps.mv(ready, 1)                                # arm: tell printer we're ready
    while True:
        if monitor.get() != 1:
            return False                                           # master ended monitoring
        if trigger.get() == 1:
            return True                                            # printer fired
        if timeout is not None and (time.time() - t0) > timeout:
            return False
        yield from bps.sleep(poll)                                 # generator poll (inside RE)


# ---------------------------------------------------------------------------
# Beam-to-filament-middle height offset (half filament width)
# ---------------------------------------------------------------------------
def beam_to_filament_middle(height, *, axis=None):
    """Move the beam DOWN to the middle of the extruded filament by ``height`` (mm).

    After derivative-edge alignment to the substrate/film interface, the beam sits at the top of
    the filament; the print is measured at its *middle*, half the filament width below -- the
    legacy ``bps.mvr(stage.y, height)`` (and the matching ``-height`` restore on the way out).
    ``height`` is half the filament width (e.g. 0.059 mm for a ~118 um filament).
    """
    ax = axis if axis is not None else stage.y                     # noqa: F821
    yield from bps.mvr(ax, height)


# ---------------------------------------------------------------------------
# THE monitoring run: one long-lived run, a frame per printer fire
# ---------------------------------------------------------------------------
def printer_triggered_run(name, *, n_events=None, until_stopped=False, t=1.0, dets=None,
                          reads=None, trigger=None, monitor=None, ready=None,
                          height=None, height_axis=None, poll=0.5, geometry="reflection",
                          baseline=None, md=None,
                          name_tokens=("evt{print_event}", "wa{waxs_arc}")):
    """ONE long-lived monitoring run: record a frame each time the printer fires.

    The sanctioned external-master pattern (see the module ``note``).  A single
    ``@run_decorator`` run stays open; inside it, :func:`wait_for_printer_fire` waits (as a
    generator) for each printer fire, then a ``trigger_and_read`` records one frame stamped with
    a ``print_event`` index Signal (and the filament position).  The run ends when ``n_events``
    fires have been recorded, or -- with ``until_stopped`` -- when the master clears the monitor
    bit.

    Parameters
    ----------
    name : str
        Human label (start of the templated filename); the per-fire index makes frames unique.
    n_events : int, optional
        Stop after this many printer fires.  Mutually-complementary with ``until_stopped``.
    until_stopped : bool
        If True, keep recording until the master drops the monitor bit (``bi2`` -> 0).  Use this
        when the print length is not known in advance.
    t : float
        Exposure time (s) per recorded frame.
    dets : list, optional
        Detectors.  Default arc-aware ``[pil300KW(/pil900KW), pil2M]`` (WAXS priority; SAXS
        dropped when the arc occludes it).
    reads : list, optional
        Extra readables each frame (default ``[xbpm3]`` for incident flux; the filament position
        is added automatically).
    trigger, monitor, ready : Signals, optional
        Printer handshake bits.  Default :func:`printer_trigger_signals` (``XF:11ID-CT{M1}
        bi4/bi2/bi3``).
    height : float, optional
        If given, move the beam to the filament middle (``height`` mm) at run open and back out
        on teardown.
    height_axis : positioner, optional
        Axis for the height offset (default ``stage.y``).
    poll : float
        Trigger-poll interval (s) inside the wait generator.
    geometry : str
        ``"reflection"`` (the printing geometry).
    baseline : list, optional
        Constants to record (default includes SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename (recorded fields: print-event index + arc).
    """
    if trigger is None or monitor is None or ready is None:
        _mon, _ready, _trig = printer_trigger_signals()
        monitor = monitor if monitor is not None else _mon
        ready = ready if ready is not None else _ready
        trigger = trigger if trigger is not None else _trig
    if dets is None:
        dets = saxs_waxs_dets(use_saxs=True, use_waxs=True)
    # print_event is the per-fire index; recorded each frame so {print_event} resolves.
    print_event = Signal(name="print_event", value=0)             # noqa: F821
    waxs_pos = waxs                                                # noqa: F821 (record arc angle)
    if reads is None:
        reads = [xbpm3]                                            # noqa: F821
    reads = list(reads) + [waxs_pos, print_event]
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821 (SDD)
        except Exception:
            baseline = []
    if n_events is None and not until_stopped:
        n_events = 1                                               # safe default: one fire

    det_exposure_time(t, t)                                        # noqa: F821
    sample_name = fname(name, *name_tokens)

    def _measure():
        # Optional: drop the beam to the filament middle inside the run (so the move is recorded).
        if height is not None:
            yield from beam_to_filament_middle(height, axis=height_axis)
        count = 0
        while True:
            fired = yield from wait_for_printer_fire(trigger, monitor, poll=poll, ready=ready)
            if not fired:
                break                                              # master ended monitoring
            count += 1
            print_event.put(count)
            # Record ONE frame for this print event into the single open run.
            yield from bps.trigger_and_read(list(dets) + list(reads))
            # Acknowledge the fire so the next wait sees the NEXT fire (clear bi4).
            yield from bps.mv(trigger, 0)
            print("printer fire #{} recorded".format(count))
            if n_events is not None and count >= n_events:
                break

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="printer_monitoring_run", geometry=geometry,
                          md=md, baseline=baseline)

    # Always: clear the trigger bit and return the beam off the filament, even on error/abort.
    def _cleanup():
        yield from bps.mv(trigger, 0)
        if height is not None:
            ax = height_axis if height_axis is not None else stage.y   # noqa: F821
            yield from bps.mvr(ax, -height)

    return (yield from cleanup_wrapper(plan, _cleanup))


# ---------------------------------------------------------------------------
# Post-print crystallization followup: repeated WAXS-arc sweeps (~30 min)
# ---------------------------------------------------------------------------
def print_crystallization_followup_run(name, *, duration_s=1800, waxs_arc=(0, 13, 3), t=1.0,
                                       dets=None, reads=None, geometry="reflection",
                                       baseline=None, md=None,
                                       name_tokens=("t{elapsed_s}s", "wa{waxs_arc}")):
    """ONE run: a repeated WAXS-arc sweep time-series tracking post-print crystallization.

    After the print finishes, follow the structure for ~30 min by sweeping the WAXS arc
    repeatedly and recording each frame, stamping the elapsed time as a Signal -- the modern
    single-run form of ``track_printer_timeRes``'s ``while t1 - t0 <= 1800: bp.scan(dets, waxs,
    *waxs_arc)`` post-print loop (which opened a new run per sweep).  Here the entire
    time-series is ONE run; each arc step within each sweep is one event with ``elapsed_s`` and
    ``waxs_arc`` recorded.

    Parameters
    ----------
    name : str
        Human label.
    duration_s : float
        Total follow-up duration (s).  Default 1800 (30 min).
    waxs_arc : (start, stop, n)
        WAXS-arc sweep definition (deg) repeated each cycle.  Default ``(0, 13, 3)``.
    t : float
        Exposure time (s) per arc step.
    dets : list, optional
        Detectors.  Default ``[pil300KW, pil2M]`` (WAXS priority + SAXS).
    reads : list, optional
        Extra readables each event (default ``[xbpm3]``; ``waxs`` arc + elapsed time are added
        automatically).
    geometry, baseline, md, name_tokens :
        As elsewhere.  ``elapsed_s`` is recorded so ``{elapsed_s}`` resolves.
    """
    if dets is None:
        dets = [pil300KW, pil2M]                                   # noqa: F821
    elapsed = Signal(name="elapsed_s", value=0.0)                 # noqa: F821
    waxs_pos = waxs                                                # noqa: F821
    if reads is None:
        reads = [xbpm3]                                            # noqa: F821
    reads = list(reads) + [waxs_pos, elapsed]
    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                               # noqa: F821
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                        # noqa: F821
    start, stop, n = waxs_arc
    arc_positions = list(np.linspace(start, stop, n))             # noqa: F821
    sample_name = fname(name + "_crystallization", *name_tokens)

    def _measure():
        t0 = time.time()
        cycle = 0
        # Repeat the arc sweep until the follow-up duration elapses -- ONE run, many events.
        while (time.time() - t0) <= duration_s:
            for wa in arc_positions:
                yield from bps.mv(waxs, wa)                        # noqa: F821
                elapsed.put(float(time.time() - t0))
                yield from bps.trigger_and_read(list(dets) + list(reads))
            cycle += 1
            print("crystallization sweep cycle #{} (t={:.0f}s)".format(cycle, time.time() - t0))

    return (yield from one_sample_run(_measure, dets, sample_name=sample_name,
                                      scan_name="print_crystallization_followup",
                                      geometry=geometry, md=md, baseline=baseline))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """Operando print monitoring: record one WAXS/SAXS frame per printer fire (3 fires).

    The single monitoring run waits (as a generator) for each fire on ``XF:11ID-CT{M1}bi4``,
    records a frame stamped with the print-event index, and stops after 3 fires.  The beam is
    dropped to the filament middle (half-width 0.059 mm) for the session.  Run with::

        RE(technique_L_printing.example())
    """
    yield from printer_triggered_run(
        "ECD_2.5mms5psi2_h118w13bar23", n_events=3, t=1.0, height=0.059,
        md={"project_name": "Demo_3Dprint", "filament_width_mm": 0.118})


def example_followup():
    """Post-print crystallization: a 30-min repeated WAXS-arc sweep time-series, ONE run.

    Mirrors ``track_printer_timeRes`` post-print dynamics but as a single recorded run with
    elapsed time in the stream.
    """
    yield from print_crystallization_followup_run(
        "ECD_2.5mms5psi2_h118w13bar23", duration_s=1800, waxs_arc=(0, 13, 3), t=1.0,
        md={"project_name": "Demo_3Dprint"})

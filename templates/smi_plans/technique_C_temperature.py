"""
technique_C_temperature
=======================

Archetype C -- In-situ temperature ramping / annealing / melting kinetics.

Measure scattering (SAXS/WAXS) as a function of temperature: stepped ramps, isothermal
holds, melting/ODT/crystallization/glass-transition studies.  The dominant legacy shape is a
``for T in temperatures:`` loop that sets a Lakeshore/Linkam setpoint, *equilibrates with a
timeout*, then bakes the read-back temperature into the filename.  The modernization keeps the
equilibration choreography but **records temperature as a device in the run** and templates the
filename from that recorded field.

**This file is a PRESET RECIPE built on the composition layer (``_compose``).**  Temperature
is just one (slow, outermost) scan axis: :func:`temperature_ramp_run` assembles a temperature
:class:`_compose.ScanAxis` (driven by the preserved :func:`goto_temperature` equilibration) and
:func:`isothermal_kinetics_run` assembles a :func:`_compose.time_axis`, each nested inside ONE
:func:`_compose.acquire` per sample.  The temperature concern is independent and freely
combinable with others (energy, incidence, spatial); to mix them, assemble the axes directly --
see ``recipes_combined.py`` (e.g. ``giwaxs_tempramp_energy_5loc``) and the README.

Gold reference: UVA ``Cai`` 2026 plans + ``legacy/30-Harward.py`` / ``legacy/30-user-Reven.py``.
The "best" legacy detail (Harvard 2026_1, Cai ``run_swaxs_Cai_2026_1``) records
``ls.input_A_celsius`` as a *detector* in the scan -- exactly the device-in-stream form below.

What this file gives you
------------------------
* :func:`lakeshore_heater` / :func:`linkam_heater` -- build a small ``Heater`` abstraction
  (setpoint plan + live read-back signal + setpoint signal) for either controller.
* :func:`goto_temperature` -- set a setpoint and equilibrate-with-timeout (preserved idiom).
* :func:`temperature_point` -- the inner per-temperature measurement (one event; T recorded).
* :func:`temperature_ramp_run` -- ONE run spanning a whole stepped ramp on a single sample.
* :func:`isothermal_kinetics_run` -- ONE run: hold one temperature, sample vs elapsed time.
* :func:`temperature_bar` -- loop :func:`temperature_ramp_run` over a :class:`SampleList`.
* :func:`example`, :func:`example_kinetics` -- runnable examples.

Idioms preserved (via _preprocessors + the Heater abstraction): equilibration-with-timeout,
extra post-equilibration soak (longer on the first setpoint), per-setpoint optional re-align
hook, fresh-spot dose walking, ensure-attenuators-in, baseline capture of the setpoint.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``Signal``, ``piezo``, ``stage``, ``waxs``,
    ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pin_diode``, ``pil2M_pos``,
    ``att2_9``, ``det_exposure_time``, and a temperature controller -- Lakeshore ``ls``
    (``ls.output1.mv_temp`` / ``ls.input_A`` / ``ls.input_A_celsius`` / ``ls.ch1_sp`` /
    ``ls.ch1_read``) or Linkam ``LThermal`` (``.setTemperature`` / ``.on`` / ``.off`` /
    ``.temperature``).
"""

from ._samples import SampleList
from ._core import (goto_sample, saxs_waxs_dets, merge_md)
from ._compose import acquire, ScanAxis, SPEED_SLOW
from ._preprocessors import (fresh_spot_wrapper, ensure_in_wrapper, cleanup_wrapper)

try:
    import bluesky.plan_stubs as bps
except Exception:  # pragma: no cover
    bps = None


__all__ = [
    "Heater", "lakeshore_heater", "linkam_heater",
    "goto_temperature", "temperature_point",
    "temperature_ramp_run", "isothermal_kinetics_run", "temperature_bar",
    "example", "example_kinetics",
]


# ---------------------------------------------------------------------------
# Heater abstraction (one shape for Lakeshore AND Linkam)
# ---------------------------------------------------------------------------
class Heater(object):
    """A controller-agnostic temperature handle: setpoint *plan* + read-back + setpoint signal.

    Rather than special-casing Lakeshore vs Linkam (vs Instec) throughout the plans, we pass
    one small object that knows how to (a) command a setpoint *as a plan* and (b) expose the
    live read-back as a recordable ophyd signal.

    Parameters
    ----------
    set_plan : callable(value) -> plan
        Generator-function that commands the controller to ``value`` (in ``units``).  E.g.
        ``lambda T: ls.output1.mv_temp(T + 273.15)`` for Lakeshore (Kelvin),
        or a small plan that does ``LThermal.setTemperature(T); LThermal.on()`` for Linkam.
    readback : ophyd Signal
        Live temperature read-back recorded in the primary stream.  This is the device whose
        ``{<name>_value}`` token goes in the filename (e.g. ``ls.input_A_celsius`` ->
        ``{ls_input_A_celsius_value}`` ... read its data-key once at the beamline).
    read_value : callable() -> float, optional
        Plain function returning the current temperature (controller native units) for the
        equilibration loop's convergence test.  Defaults to ``readback.get()``.
    setpoint_sig : ophyd Signal, optional
        The *setpoint* signal/device to record in the **baseline** (constant per event but
        worth keeping).  Optional.
    units : str
        Human label ("degC" / "K") for log lines only.
    """

    def __init__(self, set_plan, readback, *, read_value=None, setpoint_sig=None,
                 units="degC"):
        self.set_plan = set_plan
        self.readback = readback
        self._read_value = read_value if read_value is not None else (lambda: readback.get())
        self.setpoint_sig = setpoint_sig
        self.units = units

    def read_value(self):
        """Current temperature (controller native units) for the convergence test."""
        return self._read_value()

    def sync_readback(self):
        """Mirror the controller reading onto the recordable ``readback`` Signal if needed.

        For Lakeshore the read-back is already an ophyd device that updates itself; for the
        Linkam wrapper we mirror ``LThermal.temperature()`` onto the artificial Signal so the
        recorded value matches the convergence test.  Safe to call before each event.  (Also
        available as the module-level :func:`_sync_readback` for back-compat.)
        """
        _sync_readback(self)


def lakeshore_heater(*, kelvin_setpoint=True, celsius_readback=True):
    """Build a :class:`Heater` for the Lakeshore ``ls`` controller.

    Uses ``ls.output1.mv_temp`` (a plan) for the setpoint and ``ls.input_A`` (Kelvin) for the
    convergence test.  By default the *recorded* read-back is ``ls.input_A_celsius`` (the
    device the best 2026 legacy plans add to ``dets``); pass ``celsius_readback=False`` to
    record ``ls.input_A`` (Kelvin) instead.

    The setpoint command goes through Kelvin (``T + 273.15``) when ``kelvin_setpoint`` -- the
    universal legacy convention -- so callers pass Celsius everywhere.
    """
    rb = ls.input_A_celsius if celsius_readback else ls.input_A       # noqa: F821 (global)
    offset = 273.15 if kelvin_setpoint else 0.0

    def _set(T):
        yield from ls.output1.mv_temp(T + offset)                     # noqa: F821
        # Lakeshore heating range: low range below 50 degC, high range above (legacy idiom).
        try:
            yield from bps.mv(ls.output1.status, 1 if T < 50 else 3)  # noqa: F821
        except Exception:
            pass

    # Convergence test must compare in the controller's native (Kelvin) units.
    return Heater(_set, rb,
                  read_value=(lambda: ls.input_A.get()),              # noqa: F821 (Kelvin)
                  setpoint_sig=getattr(ls, "ch1_sp", None),           # noqa: F821
                  units="degC")


def linkam_heater():
    """Build a :class:`Heater` for the Linkam ``LThermal`` controller (Celsius throughout).

    Setpoint is ``LThermal.setTemperature(T)`` followed by ``LThermal.on()``; the live
    read-back ``LThermal.temperature()`` is wrapped in a tiny ``Signal`` so it can be recorded
    (its ``{linkam_temperature_value}`` token then resolves in the filename).
    """
    sig = Signal(name="linkam_temperature", value=0.0)                # noqa: F821 (global)

    def _set(T):
        LThermal.setTemperature(T)                                    # noqa: F821
        LThermal.on()                                                 # noqa: F821
        yield from bps.null()                                         # keep it a generator

    return Heater(_set, sig,
                  read_value=(lambda: LThermal.temperature()),        # noqa: F821
                  units="degC")


# ---------------------------------------------------------------------------
# Equilibration-with-timeout (the preserved physics idiom)
# ---------------------------------------------------------------------------
def goto_temperature(heater, setpoint, *, tol=1.0, poll=10.0, timeout=7200.0,
                     soak=0.0, log=True):
    """Command ``setpoint`` and block until the read-back is within ``tol`` (or ``timeout``).

    Generalizes the ubiquitous ``while abs(T - sp) > tol: sleep(10)`` loop, but with the
    ``time.time()`` escape hatch the better legacy plans added (Cai 2026:
    ``if time.time() - start > 120*60: break``).  The live read-back is updated on the
    ``heater``'s ``Signal`` so a subsequent ``trigger_and_read`` records the equilibrated
    temperature.

    Parameters
    ----------
    heater : Heater
    setpoint : float
        Target temperature (in the heater's caller-facing units, conventionally Celsius).
    tol : float
        Converged when ``abs(readback - setpoint) <= tol``.
    poll : float
        Sleep between checks (s).
    timeout : float
        Give up waiting after this many seconds (records whatever temperature is reached).
    soak : float
        Extra equilibration sleep after convergence (let the sample, not just the stage,
        reach temperature).  The first setpoint of a ramp typically wants a longer soak --
        the caller decides.
    log : bool
        Print progress lines.

    Notes
    -----
    Uses ``time.time()`` only for the *timeout clock*; the temperature itself is never baked
    into a name here -- it is recorded as a device at acquisition time.
    """
    import time  # local: only for the timeout clock, never for naming

    yield from heater.set_plan(setpoint)

    start = time.time()
    temp = heater.read_value()
    # Refresh the recordable read-back signal with the controller's native reading.
    _sync_readback(heater)
    while abs(temp - setpoint) > tol:
        if log:
            print("dT = {:.1f} {} (T={:.1f}, set={:.1f}); waiting {:.0f}s"
                  .format(abs(temp - setpoint), heater.units, temp, setpoint, poll))
        yield from bps.sleep(poll)
        temp = heater.read_value()
        _sync_readback(heater)
        if time.time() - start > timeout:
            if log:
                print("goto_temperature: timeout after {:.1f} min; proceeding at {:.1f}"
                      .format((time.time() - start) / 60.0, temp))
            break

    if log:
        print("reached {:.1f} {} in {:.1f} min".format(
            setpoint, heater.units, (time.time() - start) / 60.0))
    if soak:
        if log:
            print("soaking {:.0f}s at setpoint".format(soak))
        yield from bps.sleep(soak)


def _sync_readback(heater):
    """Push the controller's native read-back onto the recordable ``Signal`` (Linkam case).

    For Lakeshore the read-back *is* an ophyd device already (``ls.input_A_celsius``) and
    updates itself; for the Linkam wrapper we mirror ``LThermal.temperature()`` onto our
    artificial ``Signal`` so the value recorded matches the convergence test.
    """
    rb = heater.readback
    if hasattr(rb, "put") and not hasattr(rb, "read_configuration"):
        # Heuristic: an artificial Signal we own (no full Device API) -> mirror the reading.
        try:
            rb.put(float(heater.read_value()))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Inner per-temperature measurement
# ---------------------------------------------------------------------------
def temperature_point(dets, reads, heater, *, settle=0.0):
    """Record ONE event with the live temperature in the stream (-> filename token).

    ``reads`` is the list of extra readables (beyond ``dets``) recorded each event; the
    ``heater.readback`` signal is always appended so the temperature is captured.  Call this
    *after* :func:`goto_temperature` has equilibrated.
    """
    if settle:
        yield from bps.sleep(settle)
    _sync_readback(heater)
    yield from bps.trigger_and_read(list(dets) + list(reads) + [heater.readback])


# ---------------------------------------------------------------------------
# One run = one sample, stepped temperature ramp
# ---------------------------------------------------------------------------
def temperature_ramp_run(name, heater, setpoints, *, t=1.0, dets=None, reads=None,
                         geometry="transmission", tol=1.0, poll=10.0, timeout=7200.0,
                         soak=60.0, first_soak=None, settle=0.0, align=None,
                         dose_motor=None, dose_step=None, atten_in=None, baseline=None,
                         md=None, name_tokens=None):
    """ONE run: a stepped temperature ramp on a single sample (each setpoint -> one event).

    The whole ramp is a single Bluesky run; temperature is recorded per event via
    ``heater.readback`` and the filename is templated from it.  Loop is temperature-outermost
    (the slow environmental axis), consistent with the slow-axis-economy tenet.

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    heater : Heater
        From :func:`lakeshore_heater` / :func:`linkam_heater`.
    setpoints : sequence
        Temperatures to step through (caller units, conventionally Celsius).  Use a
        there-and-back list (e.g. ``[30, 60, 90, 60, 30]``) for hysteresis studies.
    t : float
        Exposure / averaging time (s).  Applied to detectors and ``pin_diode``.
    dets : list, optional
        Detectors.  Default arc-aware ``saxs_waxs_dets()`` + ``[xbpm2, xbpm3]``.
    reads : list, optional
        Extra readables recorded each event (default ``[energy, waxs, xbpm2, xbpm3]``).  The
        ``heater.readback`` is added automatically.
    geometry : str
        ``"transmission"`` or ``"reflection"``.
    tol, poll, timeout, soak :
        Equilibration controls (see :func:`goto_temperature`).
    first_soak : float, optional
        Override ``soak`` for the *first* setpoint only (legacy used ``2*hold_delay`` there).
        Defaults to ``2 * soak``.
    settle : float
        Extra sleep right before each frame (after the soak).
    align : callable() -> plan, optional
        Per-setpoint re-alignment / x-creep correction hook, run after equilibration and
        before measuring (e.g. re-find the film, recentre a capillary).  Kept as a hook so
        the technique never reimplements alignment.
    dose_motor, dose_step : optional
        If both given, walk ``dose_motor`` by ``dose_step`` after every frame (fresh spot).
    atten_in : callable() -> plan, optional
        Put attenuators/beamstop into the measurement configuration at run open.
    baseline : list, optional
        Constants to record (defaults to the SDD ``pil2M_pos.z`` and the setpoint signal if
        available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str, optional
        ``{field}`` tokens appended to the filename.  Defaults to the temperature read-back
        token + ``bpm{xbpm2_sumX}``.  Read the read-back's exact data-key at the beamline; we
        compute a best-effort token from ``heater.readback.name``.
    """
    if dets is None:
        dets = saxs_waxs_dets(use_saxs=True, use_waxs=True) + [xbpm2, xbpm3]   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                           # noqa: F821
    if first_soak is None:
        first_soak = 2.0 * soak

    if baseline is None:
        baseline = []
        if heater.setpoint_sig is not None:
            baseline.append(heater.setpoint_sig)
        try:
            baseline.append(pil2M_pos.z)                               # noqa: F821 (SDD)
        except Exception:
            pass

    if name_tokens is None:
        # Best-effort token from the read-back's name; verify the exact data-key on the floor.
        t_token = "{" + str(getattr(heater.readback, "name", "temperature")) + "_value}"
        name_tokens = (t_token + "degC", "bpm{xbpm2_sumX}")

    det_exposure_time(t, t)                                            # noqa: F821

    # TEMPERATURE is the (only) scan axis: SLOW, so outermost.  Built as a ScanAxis whose
    # `move` reuses the preserved :func:`goto_temperature` equilibration (index-aware soak so a
    # there-and-back ramp gives the longer `first_soak` only to the *first* setpoint), and
    # whose `per_point` reproduces :func:`temperature_point`'s pre-read sequence (optional
    # re-align, settle, sync the recordable read-back) just before the event.  `heater.readback`
    # is recorded each event via the axis `reads` so the measured T lands in the stream.
    counter = {"i": 0}

    def _goto(sp):
        i = counter["i"]
        counter["i"] += 1
        this_soak = first_soak if i == 0 else soak
        yield from goto_temperature(heater, sp, tol=tol, poll=poll,
                                    timeout=timeout, soak=this_soak)

    def _per_point():
        if align is not None:
            yield from align()
        if settle:
            yield from bps.sleep(settle)
        _sync_readback(heater)
        yield from bps.null()

    t_axis = ScanAxis("temperature", list(setpoints), move=_goto,
                      record=None, per_point=_per_point, reads=[heater.readback],
                      speed=SPEED_SLOW)

    def _setup():
        try:
            yield from bps.mv(pin_diode.averaging_time, t)            # noqa: F821
        except Exception:
            yield from bps.null()
        if atten_in is not None:
            yield from atten_in()

    plan = acquire(name, dets, [t_axis], reads=reads, setup=_setup,
                   geometry=geometry, scan_name="temperature_ramp",
                   md=md, baseline=baseline, name_tokens=list(name_tokens),
                   check_order=False)

    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    return (yield from plan)


# ---------------------------------------------------------------------------
# One run = one sample, isothermal hold / kinetics (time series)
# ---------------------------------------------------------------------------
def isothermal_kinetics_run(name, heater, setpoint, *, n_frames=60, period=10.0, t=1.0,
                            dets=None, reads=None, geometry="transmission", tol=1.0,
                            poll=10.0, timeout=7200.0, soak=0.0, settle=0.0,
                            dose_motor=None, dose_step=None, atten_in=None, baseline=None,
                            md=None, name_tokens=None):
    """ONE run: equilibrate at one temperature, then sample vs *elapsed time* (kinetics).

    For crystallization / drying / melting kinetics at fixed T: a single run with ``n_frames``
    events spaced by ``period`` seconds.  Both the temperature read-back *and* an elapsed-time
    ``Signal`` are recorded per event (so the filename can carry ``{kinetics_elapsed_s_value}``
    instead of ``time.time()`` formatting).

    Parameters
    ----------
    name : str
    heater : Heater
    setpoint : float
        Hold temperature.
    n_frames : int
        Number of time-series frames.
    period : float
        Target spacing between frames (s).  Measured from the start of the previous frame.
    t : float
        Exposure / averaging time (s).
    (others as in :func:`temperature_ramp_run`)
    """
    import time  # local: only to time the inter-frame period

    if dets is None:
        dets = saxs_waxs_dets(use_saxs=True, use_waxs=True) + [xbpm2, xbpm3]   # noqa: F821
    if reads is None:
        reads = [energy, waxs, xbpm2, xbpm3]                           # noqa: F821

    elapsed = Signal(name="kinetics_elapsed_s", value=0.0)             # noqa: F821 (global)

    if baseline is None:
        baseline = []
        if heater.setpoint_sig is not None:
            baseline.append(heater.setpoint_sig)
        try:
            baseline.append(pil2M_pos.z)                               # noqa: F821
        except Exception:
            pass

    if name_tokens is None:
        t_token = "{" + str(getattr(heater.readback, "name", "temperature")) + "_value}"
        name_tokens = (t_token + "degC", "t{kinetics_elapsed_s_value}s")

    det_exposure_time(t, t)                                            # noqa: F821

    # The scan axis is TIME: a custom time :class:`_compose.ScanAxis` reproducing the original
    # frame pacing exactly -- spacing consecutive frame *starts* by ~`period` (accounting for
    # the time a frame itself takes, and with no trailing wait after the final frame), and
    # recording wall-clock elapsed seconds on the `elapsed` Signal.  `heater.readback` and
    # `elapsed` are recorded each event so {kinetics_elapsed_s_value} resolves.  Equilibration
    # at the hold setpoint happens once, in `setup`, before the first frame.
    clk = {}

    def _frame(i):
        # Runs just before each event; pace relative to the previous frame's start.
        now = time.time()
        if i == 0:
            clk["t0"] = now
            clk["fs"] = now
        else:
            remaining = period - (now - clk["fs"])
            if remaining > 0:
                yield from bps.sleep(remaining)
            clk["fs"] = time.time()
        elapsed.put(round(clk["fs"] - clk["t0"], 3))

    def _per_point():
        if settle:
            yield from bps.sleep(settle)
        _sync_readback(heater)
        yield from bps.null()

    time_kinetics_axis = ScanAxis("time", list(range(int(n_frames))), move=_frame,
                                  record=None, per_point=_per_point,
                                  reads=[heater.readback, elapsed], speed=SPEED_SLOW)

    def _setup():
        try:
            yield from bps.mv(pin_diode.averaging_time, t)            # noqa: F821
        except Exception:
            yield from bps.null()
        if atten_in is not None:
            yield from atten_in()
        yield from goto_temperature(heater, setpoint, tol=tol, poll=poll,
                                    timeout=timeout, soak=soak)

    plan = acquire(name, dets, [time_kinetics_axis], reads=reads, setup=_setup,
                   geometry=geometry, scan_name="isothermal_kinetics",
                   md=md, baseline=baseline, name_tokens=list(name_tokens),
                   check_order=False)

    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one ramp-run per sample)
# ---------------------------------------------------------------------------
def temperature_bar(samples, heater, setpoints, *, t=1.0, dets=None, reads=None,
                    geometry="transmission", tol=1.0, poll=10.0, timeout=7200.0,
                    soak=60.0, first_soak=None, align=None, dose_step=None,
                    atten_in=None, md=None, restore=None):
    """Run :func:`temperature_ramp_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned then ramped.  The
    heater is shared; positions move between samples, but the ramp is per sample so each run's
    ``sample_name``/baseline stay coherent (Tenet 5).

    Parameters
    ----------
    restore : float, optional
        If given, command the heater back to this temperature once the whole bar is done
        (e.g. 25 degC) -- wrapped in a cleanup so it runs even on error.
    (others as in :func:`temperature_ramp_run`)
    """
    def _body():
        for s in samples:
            yield from goto_sample(s)
            dose_motor = piezo.x if dose_step else None               # noqa: F821
            yield from temperature_ramp_run(
                s.name, heater, setpoints, t=t, dets=dets, reads=reads, geometry=geometry,
                tol=tol, poll=poll, timeout=timeout, soak=soak, first_soak=first_soak,
                align=align, dose_motor=dose_motor, dose_step=dose_step,
                atten_in=atten_in, md=merge_md(md, s.md))

    if restore is not None:
        def _cool():
            yield from heater.set_plan(restore)
        return (yield from cleanup_wrapper(_body(), _cool))
    return (yield from _body())


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """3-sample bar, stepped Lakeshore ramp 30->90->30 degC, transmission, SDD in baseline.

    Run with::

        RE(technique_C_temperature.example())
    """
    heater = lakeshore_heater()                     # records ls.input_A_celsius as a device
    bar = SampleList.from_columns(
        names=["BB40", "BB39", "BB38"],
        piezo_x=[-44950, -31950, -19350],
        piezo_y=[-8767, -8817, -8917],
        piezo_z=[7000, 7000, 7000],
        md={"project_name": "311234_Demo"},
    )

    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                         # noqa: F821
        yield from bps.sleep(1)

    yield from temperature_bar(
        bar, heater, setpoints=[30, 60, 90, 60, 30], t=2.0,
        geometry="transmission", tol=1.0, soak=60.0,
        atten_in=_atten_in, restore=25.0,
        md={"environment": "Lakeshore_vacuum"},
    )


def example_kinetics():
    """Isothermal crystallization kinetics: hold 120 degC, 120 frames every 5 s (Linkam).

    Run with::

        RE(technique_C_temperature.example_kinetics())
    """
    heater = linkam_heater()
    yield from goto_sample(SampleList.from_columns(
        names=["PEO_film"], piezo_x=[-12500], piezo_y=[-2298])[0])

    yield from isothermal_kinetics_run(
        "PEO_film", heater, setpoint=120.0, n_frames=120, period=5.0, t=1.0,
        geometry="transmission", soak=30.0,
        dose_step=None,                              # solution-free film: usually no walk
        md={"project_name": "311234_Demo", "process": "isothermal_crystallization"})

"""
recipes_combined
===============

**Worked examples of COMPOSING concerns** -- the answer to "my experiment is a combination,
not one of A-O".

Each function here is a *bespoke experiment* assembled from the composition layer
(:mod:`smi_plans._compose`): you pick the beam/q config (dets + reads), the apparatus/geometry
(a ``setup`` plan), and a stack of scan axes (energy, temperature, incidence, spatial, manual
...), nested in the order you want.  The ``technique_*`` files are *presets*; this file shows
how to mix their pieces freely -- exactly what a composable GUI will do under the hood.

Read these top-to-bottom as a tutorial; copy one and edit it for your beamtime.

.. important::
    Beamline globals required at runtime (SMI profile collection; not importable standalone):
    ``bps``, ``Signal``, ``np``, ``energy``, ``waxs``, ``prs``, ``piezo``, ``stage``,
    ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pin_diode``, ``pil2M_pos``, ``att2_9``,
    ``ls`` / ``LThermal``, ``det_exposure_time``, and an alignment routine
    (``alignement_gisaxs_hex``).
"""

from ._samples import Sample, SampleList
from ._core import goto_sample, saxs_waxs_dets, merge_md
from ._compose import (acquire, acquire_bar, ScanAxis,
                       energy_axis, temperature_axis, incidence_axis, motor_axis,
                       spatial_grid_axes, potential_axis, rh_axis, time_axis,
                       manual_step, manual_value, manual_axis, manual_loop, pause_for_user,
                       SPEED_SLOW, SPEED_MEDIUM, SPEED_FAST)
from ._preprocessors import fresh_spot_wrapper, ensure_in_wrapper
from .technique_C_temperature import lakeshore_heater, linkam_heater

try:
    import bluesky.plan_stubs as bps
except Exception:  # pragma: no cover
    bps = None


__all__ = [
    "giwaxs_tempramp_energy_5loc",
    "transmission_rh_kinetics",
    "operando_echem_energy",
    "giwaxs_manual_swap_bar",
    "build_axes_from_spec",
]


# ===========================================================================
# 1. The flagship combination:
#    tender energy sweep  +  Linkam temperature  +  grazing incidence  +  5 x-locations
# ===========================================================================
def giwaxs_tempramp_energy_5loc(
        name, *, edge_energies, temperatures, incident_angles=(0.1, 0.2),
        waxs_arc=(0, 20), x_locations=5, x_step=30, t=1.0, align=None, align_angle=0.1,
        heater=None, md=None):
    """ONE run: grazing-incidence GIWAXS, ramping temperature, sweeping tender energy, at
    several incident angles, across N fresh x-locations per point -- on one sample.

    This is the kind of bespoke script users hand-write today.  Here it is composed from
    reusable axes.  Loop order (outer -> inner) honors slow-axis economy:

        temperature (slowest, equilibration)
          -> waxs.arc (slow, in-vacuum)
            -> incident angle
              -> energy (DCM)
                -> x-location (fast piezo, fresh spot)
                  -> trigger_and_read(SAXS+WAXS + energy + arc + bpm + T + ai + x)

    Everything moved/changed is recorded in the stream, so the filename can reference any of
    it, and there is exactly ONE run for the whole (sample) experiment.

    Parameters
    ----------
    name : str
        Sample label.
    edge_energies : sequence
        Energies (eV) across the edge (e.g. ``technique_A_energy_edge.energy_grid(2472)``).
    temperatures : sequence
        Setpoints (degC) to ramp through.
    incident_angles : sequence
        Grazing angles (deg), relative to the aligned zero.
    waxs_arc : sequence
        WAXS arc positions (deg).
    x_locations : int
        Number of fresh x spots per (T, arc, ai, energy) point (dose spreading).
    x_step : float
        Spacing of the fresh x spots (piezo units).
    t : float
        Exposure time.
    align : callable(angle) -> plan, optional
        Alignment routine (e.g. ``alignement_gisaxs_hex``).  Run once in ``setup``.
    heater : Heater, optional
        Default :func:`linkam_heater` (Linkam ``LThermal``).  Pass
        :func:`lakeshore_heater` for the Lakeshore.
    md : dict, optional
        Caller intent.
    """
    heater = heater if heater is not None else linkam_heater()
    dets = saxs_waxs_dets(use_saxs=True, use_waxs=True)
    det_exposure_time(t, t)                                       # noqa: F821

    # --- apparatus / geometry setup: align, then ensure attenuators in -------------------
    def _setup():
        if align is not None:
            yield from align(align_angle)
        yield from bps.mv(att2_9.close_cmd, 1)                    # noqa: F821 (atten in)
        yield from bps.sleep(1)

    # aligned incidence zero (read after alignment in setup would be cleaner; here use current)
    th0 = piezo.th.position                                       # noqa: F821

    # --- the axis stack (outermost first) -------------------------------------------------
    axes = [
        temperature_axis(heater, list(temperatures), soak=120.0, first_soak=300.0),
        motor_axis("arc", waxs, list(waxs_arc), record=True, speed=SPEED_SLOW),  # noqa: F821
        incidence_axis(piezo.th, th0, list(incident_angles)),    # noqa: F821
        energy_axis(list(edge_energies), settle=2.0,
                    flux_signal=xbpm2.sumX, flux_threshold=50),  # noqa: F821
        motor_axis("x", piezo.x,                                  # noqa: F821
                   [th0 * 0 + i * x_step for i in range(x_locations)],
                   record=True, speed=SPEED_FAST),
    ]
    # NOTE: the x-location list above is relative offsets added to the *current* x via the
    # device move; for absolute fresh spots, build from piezo.x.position + i*x_step instead.

    reads = [energy, waxs, xbpm2, xbpm3]                          # noqa: F821
    baseline = []
    try:
        baseline = [pil2M_pos.z]                                  # noqa: F821 (SDD)
    except Exception:
        pass

    yield from acquire(
        name, dets, axes, reads=reads, setup=_setup, geometry="reflection",
        scan_name="giwaxs_tempramp_energy_5loc",
        md=merge_md(md, {"technique": "GIWAXS+Tramp+NEXAFS+microraster"}),
        baseline=baseline)


# ===========================================================================
# 2. Transmission SAXS/WAXS  +  RH program  +  time-series kinetics at each RH
# ===========================================================================
def transmission_rh_kinetics(name, *, rh_setpoints, frames_per_rh=20, period=10.0, t=1.0,
                             set_rh=None, live_rh=None, md=None):
    """ONE run: step relative humidity, and at each RH record a swelling time-series.

    Composes :func:`rh_axis` (outer, slow) with :func:`time_axis` (inner) -- no GISAXS here,
    pure transmission.  RH (commanded + optionally live) and elapsed time are recorded.

    Parameters
    ----------
    set_rh : callable(target) -> plan
        Ramp the MFCs + equilibrate (rig-specific; e.g. wrap ``setDryFlow``/``setWetFlow``).
    live_rh : ophyd Signal, optional
        A Signal you update from ``readHumidity()`` to record measured RH per event.
    """
    dets = saxs_waxs_dets(use_saxs=True, use_waxs=False) + [pin_diode, xbpm2, xbpm3]  # noqa: F821
    det_exposure_time(t, t)                                       # noqa: F821
    elapsed = Signal(name="elapsed_s", value=0.0)                # noqa: F821

    axes = [
        rh_axis(set_rh, list(rh_setpoints), live_rh=live_rh),     # outer, slow
        time_axis(frames_per_rh, period=period, elapsed_signal=elapsed),  # inner
    ]
    reads = [energy, pin_diode, xbpm2, xbpm3]                     # noqa: F821
    yield from acquire(
        name, dets, axes, reads=reads, geometry="transmission",
        scan_name="transmission_rh_kinetics",
        md=merge_md(md, {"technique": "transmission+RH+kinetics"}))


# ===========================================================================
# 3. Operando electrochemistry  +  energy sweep at each potential
# ===========================================================================
def operando_echem_energy(name, *, potentials, edge_energies, set_potential, readback=None,
                          t=1.0, geometry="reflection", md=None):
    """ONE run: step applied potential, and at each potential run an energy sweep.

    Composes :func:`potential_axis` (outer) with :func:`energy_axis` (inner).  Both the applied
    potential and the energy are recorded per event.
    """
    dets = saxs_waxs_dets(use_saxs=False, use_waxs=True) + [xbpm2, xbpm3]  # noqa: F821
    det_exposure_time(t, t)                                       # noqa: F821
    axes = [
        potential_axis(set_potential, list(potentials), readback=readback, equilibration=5.0),
        energy_axis(list(edge_energies), settle=2.0),
    ]
    reads = [energy, xbpm2, xbpm3]                                # noqa: F821
    yield from acquire(
        name, dets, axes, reads=reads, geometry=geometry,
        scan_name="operando_echem_energy",
        md=merge_md(md, {"technique": "operando_echem+NEXAFS"}))


# ===========================================================================
# 4. A MANUAL bar: user swaps each sample by hand, types its thickness, then it's measured
# ===========================================================================
def giwaxs_manual_swap_bar(*, waxs_arc=(0, 20), incident_angles=(0.1,), t=1.0, align=None,
                           align_angle=0.1, md=None):
    """Open-ended: keep prompting the user to load a sample + type its thickness, then GIWAXS
    it -- until the user says stop.  Each sample is ONE run.

    Demonstrates the manual/interactive concern as the OUTER loop (:func:`manual_loop`): the
    user-supplied thickness is captured on a recorded ``Signal`` (so it lands in the data and
    is a ``{thickness_nm}`` token), and alignment + measurement run per loaded sample.

    Run with ``RE(recipes_combined.giwaxs_manual_swap_bar(align=alignement_gisaxs_hex))`` and
    follow the prompts.
    """
    thickness = Signal(name="thickness_nm", value=0.0)           # noqa: F821
    dets = saxs_waxs_dets(use_saxs=True, use_waxs=True)
    det_exposure_time(t, t)                                       # noqa: F821
    counter = {"n": 0}

    def _measure_one():
        # name carries an incrementing index; thickness is recorded in baseline.
        counter["n"] += 1
        nm = "manual_sample_{:02d}".format(counter["n"])

        def _setup():
            if align is not None:
                yield from align(align_angle)
            yield from bps.mv(att2_9.close_cmd, 1)               # noqa: F821
            yield from bps.sleep(1)

        th0 = piezo.th.position                                  # noqa: F821
        axes = [
            motor_axis("arc", waxs, list(waxs_arc), record=True, speed=SPEED_SLOW),  # noqa: F821
            incidence_axis(piezo.th, th0, list(incident_angles)),  # noqa: F821
        ]
        yield from acquire(
            nm, dets, axes, reads=[energy, waxs, xbpm2, xbpm3],  # noqa: F821
            setup=_setup, geometry="reflection", scan_name="giwaxs_manual_swap",
            md=merge_md(md, {"thickness_nm_note": "user-entered"}),
            baseline=[thickness])

    # manual_loop drives the open-ended user-paced outer loop, capturing thickness each time.
    yield from manual_loop("Load the next sample on the bar",
                           inner=_measure_one, signal=thickness, cast=float)


# ===========================================================================
# 5. Spec-driven assembly (what a GUI does): build an axis stack from a dict
# ===========================================================================
def build_axes_from_spec(spec, *, context):
    """Turn a declarative ``spec`` (e.g. from a GUI / JSON) into an ordered list of ScanAxis.

    This is a sketch of the GUI <-> plans bridge: the GUI emits a list of axis specs (type +
    params), and this assembles the corresponding axes IN THE GIVEN ORDER.  ``context`` carries
    the live devices/callables the axes need (so this stays free of beamline globals).

    Parameters
    ----------
    spec : list of dict
        Each dict: ``{"type": <name>, ...params}``.  ``type`` in
        ``{"energy","temperature","incidence","motor","spatial","potential","rh","time",
        "manual"}``.  Order = nesting (outermost first).
    context : dict
        Live handles, e.g.::

            {"energy": energy, "th_axis": piezo.th, "th0": 0.0, "waxs": waxs, "prs": prs,
             "heater": linkam_heater(), "set_potential": my_set_v, "set_rh": my_set_rh,
             "piezo_x": piezo.x, "piezo_y": piezo.y}

    Returns
    -------
    list of ScanAxis (and/or callables for open-ended manual loops -- those the caller runs).

    Notes
    -----
    A real GUI would also validate ordering via the same guardrail :func:`_compose.acquire`
    uses (it warns automatically).  This is intentionally small/illustrative.
    """
    out = []
    for s in spec:
        kind = s["type"]
        if kind == "energy":
            out.append(energy_axis(s["values"], settle=s.get("settle", 2.0),
                                   flux_signal=context.get("flux_signal"),
                                   flux_threshold=s.get("flux_threshold")))
        elif kind == "temperature":
            out.append(temperature_axis(context["heater"], s["values"],
                                        soak=s.get("soak", 60.0),
                                        first_soak=s.get("first_soak")))
        elif kind == "incidence":
            out.append(incidence_axis(context["th_axis"], context.get("th0", 0.0),
                                      s["values"]))
        elif kind == "motor":
            out.append(motor_axis(s.get("name", "motor"), context[s["device"]], s["values"],
                                  record=s.get("record", True),
                                  speed=s.get("speed", SPEED_FAST)))
        elif kind == "spatial":
            out.extend(spatial_grid_axes(
                x_motor=context.get("piezo_x"), x=s.get("x"),
                y_motor=context.get("piezo_y"), y=s.get("y"),
                snake=s.get("snake", True)))
        elif kind == "potential":
            out.append(potential_axis(context["set_potential"], s["values"],
                                      equilibration=s.get("equilibration", 5.0),
                                      readback=context.get("potential_readback")))
        elif kind == "rh":
            out.append(rh_axis(context["set_rh"], s["values"],
                               live_rh=context.get("live_rh")))
        elif kind == "time":
            out.append(time_axis(s["n_frames"], period=s.get("period", 0.0),
                                 elapsed_signal=context.get("elapsed_signal")))
        elif kind == "manual":
            out.append(manual_axis(s.get("name", "manual"), s["prompt"],
                                   values=s.get("values"),
                                   signal=context.get("manual_signal"),
                                   record_name=s.get("record_name")))
        else:
            raise ValueError("unknown axis type: {!r}".format(kind))
    return out

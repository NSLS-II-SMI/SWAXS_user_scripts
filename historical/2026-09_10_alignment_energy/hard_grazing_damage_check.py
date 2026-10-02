"""HISTORICAL AD HOC PLAN — September/October 2026; see this directory's README.

SAXS + WAXS Au L3 scan with hex alignment and stage-theta incidence scans.

Matched before/after beam-damage checks share the aligned stage-theta zero.

In the configured Bluesky session:
    %run -i ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/hard_grazing_damage_check.py
    RE(run_plan())  # Default ~10x attenuation at the starting energy.
"""

import json
import uuid
from pathlib import Path

import bluesky.plan_stubs as bps
import numpy as np

from smi_plans import ListStore, Position, bar_name_tokens, load_holder, resolve_list
from smi_plans._compose import acquire, energy_axis, incidence_axis, move_energy_fb
from smi_plans._core import goto_sample, position_moves, saxs_waxs_dets

HOLDER = "Hard"
WAXS_ARC = 20.0
EXPOSURE = 1.0
ENERGY_SETTLE = 2.0
THETA_TOLERANCE = 0.002  # deg; check actual stage theta before each exposure.
INCIDENCE_ANGLES = [0.05, 0.10, 0.15, 0.20, 0.25]
TENDER_INCIDENCE_ANGLES = [0.3, 0.4, 0.5, 0.6]
ENERGIES = np.concatenate([
    np.arange(11860, 11900, 3),
    np.arange(11900, 11960, 1),
    np.arange(11960, 12060, 3),
]).astype(float).tolist()

bar = load_holder(HOLDER)
name_tokens = bar_name_tokens(
    WAXS_ARC, include_energy=True, include_arc=True,
    include_incidence=True, arc_fmt="wa{:04.1f}",
    extra_tokens=["bpm3{xbpm3_sumX}"],
)


def run_plan(attenuation_factor=10, harmonic=None):
    """One check before, full energy scan, one check after, for each sample.

    Checks scan the five incidence angles at ENERGIES[0]. Foils are selected
    once per sample after alignment, and held fixed across all measurement runs.
    Factor is 1/transmission: 10 means approximately 10% transmission at E0.
    The live profile's with_harmonic_lock selects one harmonic for the full
    interval before motion, establishes it at E0, and restores the previous
    lock on exit. harmonic=None selects automatically; supply an odd integer
    to request an exact harmonic. All samples and checks share the same lock.
    """
    attenuation_factor = float(attenuation_factor)
    if not np.isfinite(attenuation_factor) or attenuation_factor < 1:
        raise ValueError("attenuation_factor must be finite and >= 1")
    # Live profile convenience wrapper supplies the energy device. Wrap outside
    # all open_run calls, including the separate runs made by alignment.
    return (yield from with_harmonic_lock(
        _run_measurements(attenuation_factor),
        start=min(ENERGIES), stop=max(ENERGIES), harmonic=harmonic,
    ))


def _measurement_reads():
    return [energy, waxs, xbpm2, xbpm3, pin_diode,
            piezo.x, piezo.y, piezo.th, stage.y, stage.theta, attenuation]


def _acquire_phase(s, dets, th0, group_id, phase, energies, angles,
                   attenuation_factor, extra_md=None, suffix="", reference_energy=None):
    """One fixed-theta energy run, or a short incidence-only damage check."""
    for ai in angles:
        if not np.isfinite(th0 + ai):
            raise ValueError("Theta targets must be finite")
    ai_axis = incidence_axis(stage.theta, th0, angles)
    e_axis = energy_axis(energies, settle=ENERGY_SETTLE)

    def verify_theta():
        ai = float((yield from bps.rd(ai_axis.record)))
        actual = float((yield from bps.rd(stage.theta)))
        if not np.isfinite(actual) or abs(actual - (th0 + ai)) > THETA_TOLERANCE:
            raise RuntimeError(
                f"Stage theta readback {actual:g} does not match {th0 + ai:g}; "
                "stopping before exposure."
            )

    if phase == "energy_scan":
        # Theta moves ONCE before descending into the entire energy list.
        original_hook = e_axis.per_point

        def energy_hook():
            if original_hook is not None:
                yield from original_hook()
            yield from verify_theta()

        e_axis.per_point = energy_hook
        axes = [ai_axis, e_axis]
    else:
        # Checks hold E0 fixed, visiting each angle only once.
        ai_axis.per_point = verify_theta
        axes = [e_axis, ai_axis]
    print(f"{s.name}: {phase}, angles={angles}, energies={len(energies)}")
    yield from acquire(
        f"{s.name}_{phase}{suffix}", dets, axes, sample=s, reads=_measurement_reads(),
        geometry="reflection",
        scan_name=("gisaxs_giwaxs_NEXAFS" if phase == "energy_scan" else
                   "blank_measurement" if phase == "blank_measurement" else "beam_damage_check"),
        name_tokens=name_tokens,
        md={
            "sample_id": s.id, "holder_id": s.holder_id,
            "damage_check_group": group_id, "measurement_phase": phase,
            "aligned_theta_zero": th0, "incidence_motor": "stage.theta",
            "alignment_plan": "alignement_gisaxs_hex",
            "attenuation_factor_requested": attenuation_factor,
            "attenuation_reference_energy_eV": ENERGIES[0] if reference_energy is None else reference_energy,
            "attenuation_mode": "fixed_foils", "exposure_s": EXPOSURE,
            "scan_order": "theta_then_energy", "theta_tolerance_deg": THETA_TOLERANCE,
            **(extra_md or {}),
        },
    )


def _run_measurements(attenuation_factor, samples=None, energies=None, *, blank_only=False,
                      extra_md=None, angles=None, first_sample_theta_zero=None):
    energies = ENERGIES if energies is None else energies
    angles = INCIDENCE_ANGLES if angles is None else angles
    # The wrapper has already established the harmonic at the start energy.
    yield from bps.sleep(ENERGY_SETTLE)
    yield from bps.mv(waxs.arc, WAXS_ARC)
    dets = saxs_waxs_dets(use_saxs=True, use_waxs=True)

    for index, s in enumerate(bar if samples is None else samples):
        reuse_alignment = index == 0 and first_sample_theta_zero is not None
        if reuse_alignment:
            # Already sitting at the first sample's freshly aligned position.
            # goto_sample would overwrite its aligned height/angle with nominal values.
            th0 = first_sample_theta_zero
            print(f"{s.name}: reusing current alignment; stage theta zero={th0:g} deg")
        else:
            yield from goto_sample(s)
            yield from move_energy_fb(energies[0], settle=ENERGY_SETTLE)
            # Alignment owns its separate runs, exposure and foil setup.
            yield from alignement_gisaxs_hex(0.2)
            # Capture ONCE: the checks and main scan share the same theta zero.
            th0 = float((yield from bps.rd(stage.theta)))
            theta_target = float((yield from bps.rd(stage.theta.setpoint)))
            if (not np.isfinite([th0, theta_target]).all()
                    or abs(th0 - theta_target) > THETA_TOLERANCE):
                raise RuntimeError(
                    f"Alignment did not reach its final theta: readback {th0:g}, "
                    f"setpoint {theta_target:g}. Resolve stage motion before continuing."
                )
        sample_md = {**(extra_md or {}), "alignment_reused": reuse_alignment}
        yield from det_exposure_time(EXPOSURE, EXPOSURE)
        yield from move_energy_fb(energies[0], settle=ENERGY_SETTLE)
        yield from bps.mv(attenuation, attenuation_factor)

        group_id = uuid.uuid4().hex
        if blank_only:
            yield from _acquire_phase(
                s, dets, th0, group_id, "blank_measurement", energies, angles,
                attenuation_factor, reference_energy=energies[0], extra_md=sample_md,
            )
            continue
        yield from _acquire_phase(s, dets, th0, group_id, "beam_damage_check_before",
                                  [energies[0]], angles, attenuation_factor,
                                  reference_energy=energies[0], extra_md=sample_md)
        for ai in angles:
            yield from _acquire_phase(s, dets, th0, group_id, "energy_scan",
                                      energies, [ai], attenuation_factor,
                                      reference_energy=energies[0], extra_md=sample_md)
        yield from _acquire_phase(s, dets, th0, group_id, "beam_damage_check_after",
                                  [energies[0]], angles[::-1], attenuation_factor,
                                  reference_energy=energies[0], extra_md=sample_md)


def _run_selected(samples, energies, attenuation_factor, harmonic, *, blank_only=False, md=None,
                  angles=None, reuse_first_alignment=False):
    """Validate all selected X coordinates before the harmonic approach or alignment."""
    if not samples:
        raise ValueError("No matching sample positions")
    values = np.asarray(energies, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Energy list must be finite, nonempty, and one-dimensional")
    factor = float(attenuation_factor)
    if not np.isfinite(factor) or factor < 1:
        raise ValueError("attenuation_factor must be finite and >= 1")
    for index, s in enumerate(samples):
        if index == 0 and reuse_first_alignment:
            continue  # This sample's stored X will not be commanded.
        x = s.runnable_position().piezo_x
        if x is None or not np.isfinite(x):
            raise ValueError(f"{s.name}: missing/invalid piezo X")
        try:
            piezo.x.check_value(x)
        except Exception as exc:
            raise ValueError(f"{s.name}: stored piezo X {x:g} um fails the motor limit check") from exc
    print("Selected:", [s.name for s in samples])
    print(f"Energy range: {values.min():g}–{values.max():g} eV; {len(values)} points")
    print("Incidence angles:", INCIDENCE_ANGLES if angles is None else angles)
    first_zero = None
    if reuse_first_alignment:
        # Capture before the wrapper's energy approach. Caller must still be at
        # the aligned zero left by alignement_gisaxs_hex for samples[0].
        first_zero = float((yield from bps.rd(stage.theta)))
        if not np.isfinite(first_zero):
            raise ValueError("Current stage theta zero is not finite")
    return (yield from with_harmonic_lock(
        _run_measurements(factor, samples=samples, energies=values.tolist(),
                          blank_only=blank_only, extra_md=md, angles=angles,
                          first_sample_theta_zero=first_zero),
        start=float(values.min()), stop=float(values.max()), harmonic=harmonic,
    ))


def run_hard_blank(attenuation_factor=10, harmonic=None):
    """BlankSi_11keV at 11900 eV, one exposure at each of the five angles."""
    samples = [s for s in load_holder("Hard") if s.name == "BlankSi_11keV"]
    if len(samples) != 1:
        raise ValueError("Expected exactly one BlankSi_11keV position in Hard")
    return (yield from _run_selected(
        samples, [11900.0], attenuation_factor, harmonic, blank_only=True,
        md={"scan_selection": "hard_blank", "reference_energy_eV": 11900.0},
    ))


def run_hard_sparse(attenuation_factor=10, harmonic=None):
    """All sparse Hard positions, original 108-point Au grid at each fixed theta."""
    samples = [s for s in load_holder("Hard") if "sparse" in s.name.casefold()]
    return (yield from _run_selected(
        samples, ENERGIES, attenuation_factor, harmonic,
        md={"scan_selection": "hard_sparse", "edge_label": "AuL3"},
    ))


def run_tender_indium(attenuation_factor=10, harmonic=None, *, holder="Tender",
                      reuse_first_alignment=False):
    """All current entries in holder, including blanks, at 0.3/0.4/0.5/0.6 degrees.

    Reloads the named holder at execution time and uses the stored In L3 80-point list.
    Example: RE(run_tender_indium(holder="Tender_remount", attenuation_factor=1))
    reuse_first_alignment=True leaves the first sample at its CURRENT aligned
    position and treats CURRENT stage.theta as zero; no goto or alignment for it.
    Use only immediately after alignment, before any manual incidence/position move.
    Run after the beamline is configured for tender operation. This plan changes
    energy and acquisition settings, not the beamline's hard/tender optical setup.
    """
    samples = list(load_holder(holder))
    list_name = "In L3 1ev 80 pts"
    energies = resolve_list(list_name, kind="energy", store=ListStore.from_redis())
    return (yield from _run_selected(
        samples, energies, attenuation_factor, harmonic,
        angles=TENDER_INCIDENCE_ANGLES,
        reuse_first_alignment=reuse_first_alignment,
        md={"scan_selection": "tender_indium", "edge_label": "InL3",
            "energy_list": list_name, "holder_name": holder},
    ))


def run_tender_resume_1170553():
    """Restart the unexposed In2O3_c8x and finish the original Tender batch.

    Source: b85b41f8-ab74-4469-a288-9287e98f8f90, before-check, zero primary events.
    The old alignment's final theta move did not reach its target, so align again
    after resolving the stage motion problem. Uses original harmonic 3, factor 1.
    This is a fixed recovery selection, not automatic tracking of subsequent runs.
    """
    ids = [
        "a3987f291eea4e49b2ca14e8499f7f69",  # In2O3_c8x
        "9bc664e66e064043bb244dc083cfdcb9",  # In2O3_c8x_2
        "319866b5290d4b1fbb0d4e75cf045c9b",  # BlankSi_3p7keV
        "1d3e647ca5cc4dedafa3dea35e9a7e78",  # In2O3_sparse_leftc4x
    ]
    return (yield from _resume_tender_samples(
        ids, "b85b41f8-ab74-4469-a288-9287e98f8f90",
        "No source measurement events; repeat alignment because final theta was not reached",
    ))


def run_tender_resume_1170565():
    """Continue with In2O3_c8x_2 after its initial height-alignment fit failed.

    In2O3_c8x completed through its after-check (1170564). Reposition and align
    the three remaining samples using the currently loaded profile routine.
    """
    return (yield from _resume_tender_samples(
        ["9bc664e66e064043bb244dc083cfdcb9",  # In2O3_c8x_2
         "319866b5290d4b1fbb0d4e75cf045c9b",  # BlankSi_3p7keV
         "1d3e647ca5cc4dedafa3dea35e9a7e78"],  # In2O3_sparse_leftc4x
        "a8d300ff-cd02-41e8-bc08-fa50152eb7c5",
        "Initial height-alignment fit failed; no damage-check or energy-scan measurements on this sample",
    ))


def _resume_tender_samples(ids, source_uid, note):
    by_id = {s.id: s for s in load_holder("Tender")}
    if any(sid not in by_id for sid in ids):
        raise ValueError("A remaining sample is missing from Tender; review the recovery selection")
    list_name = "In L3 1ev 80 pts"
    energies = resolve_list(list_name, kind="energy", store=ListStore.from_redis())
    expected = np.concatenate([
        np.arange(3671, 3721, 5), np.arange(3721, 3771), np.arange(3771, 3871, 5),
    ]).astype(float).tolist()
    if list(energies) != expected:
        raise ValueError("The In L3 energy list changed since the original Tender scans")
    return (yield from _run_selected(
        [by_id[sid] for sid in ids], energies, attenuation_factor=1, harmonic=3,
        angles=[0.3, 0.4, 0.5, 0.6],
        md={
            "scan_selection": "tender_indium", "edge_label": "InL3", "energy_list": list_name,
            "continuation_of": source_uid,
            "recovery_note": note,
        },
    ))


def run_resume_1170456():
    """One-time continuation from the supplied stopped run; no repeated pairs.

    After the stage has cooled, run RE(run_resume_1170456()). Restores Au_c4x's
    recorded aligned position/zero without re-aligning or repeating its before
    check. Completes Au_c8x and Au_c8x_2 afterwards, including their alignments.
    The coverage snapshot is fixed: do not rerun after acquiring additional data.
    """
    snapshot = json.loads(Path(__file__).with_name("hard_resume_1170456.json").read_text())
    if snapshot["energies"] != ENERGIES or snapshot["angles"] != INCIDENCE_ANGLES:
        raise ValueError("Energy/angle settings changed since the interrupted scan")
    by_id = {s.id: s for s in bar}
    ids = [snapshot["sample_id"]] + snapshot["remaining_sample_ids"]
    if any(sid not in by_id for sid in ids):
        raise ValueError("Original samples are missing from holder Hard")
    current = by_id[snapshot["sample_id"]]
    recorded = {tuple(pair) for pair in snapshot["recorded_pairs"]}
    pending = [(ai, [e for e in ENERGIES if (e, ai) not in recorded]) for ai in INCIDENCE_ANGLES]
    factor = snapshot["attenuation_factor"]

    def continuation():
        yield from bps.sleep(ENERGY_SETTLE)
        yield from bps.mv(waxs.arc, WAXS_ARC)
        dets = saxs_waxs_dets(use_saxs=True, use_waxs=True)
        yield from det_exposure_time(EXPOSURE, EXPOSURE)
        # Reestablish the original foils at E0; verify the actual combination.
        yield from bps.mv(attenuation, factor)
        yield from bps.read(attenuation)
        inserted = yield from bps.rd(attenuation.inserted)
        if set(str(inserted).split(",")) != set(snapshot["attenuation_inserted"].split(",")):
            raise RuntimeError("Foil combination differs from the original Au_c4x run")
        # Use recorded setpoints, not current nominal holder height or theta.
        pos = Position(**snapshot["position"])
        yield from bps.mv(*position_moves(pos, piezo, stage))
        md = {"continuation_of": snapshot["source_uid"],
              "alignment_reused": True,
              "flagged_events_not_repeated": snapshot["flagged_events_not_repeated"]}
        for ai, values in pending:
            if values:
                yield from _acquire_phase(
                    current, dets, snapshot["theta_zero"], snapshot["group_id"],
                    "energy_scan", values, [ai], factor, extra_md=md, suffix="_continuation",
                )
        yield from _acquire_phase(
            current, dets, snapshot["theta_zero"], snapshot["group_id"],
            "beam_damage_check_after", [ENERGIES[0]], INCIDENCE_ANGLES[::-1], factor,
            extra_md=md, suffix="_continuation",
        )
        yield from _run_measurements(factor, samples=[by_id[sid] for sid in snapshot["remaining_sample_ids"]])

    return (yield from with_harmonic_lock(
        continuation(), start=min(ENERGIES), stop=max(ENERGIES), harmonic=snapshot["harmonic"],
    ))


print("Samples:", [s.name for s in bar])
print(f"Per sample: {len(INCIDENCE_ANGLES)} before + "
      f"{len(ENERGIES) * len(INCIDENCE_ANGLES)} main + "
      f"{len(INCIDENCE_ANGLES)} after events, plus alignment")
print("Run: RE(run_plan()) or RE(run_plan(attenuation_factor=10))")
print("Continue the interrupted Au_c4x and original remaining samples: RE(run_resume_1170456())")
print("Additional scans: RE(run_hard_blank()), RE(run_hard_sparse()), RE(run_tender_indium())")

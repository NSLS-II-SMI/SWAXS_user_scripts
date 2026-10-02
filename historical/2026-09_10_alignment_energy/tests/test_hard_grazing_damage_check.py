"""Checks and main scan must share alignment zero, foil setting, and exposure."""

import json
import runpy
from pathlib import Path

import numpy as np
import pytest

from smi_plans import Sample


@pytest.mark.parametrize("failure,requested,previous", [
    (None, None, 0), (None, 3, 7), ("gap", None, 0), ("alignment", None, 7),
    ("alignment_target", None, 0),
])
def test_damage_check_conditions(failure, requested, previous, sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    monkeypatch.setattr(smi_plans, "load_holder", lambda name: [
        Sample("Au", piezo_x=100, piezo_y=200, piezo_th=0),
    ])
    atten = sim.Signal(name="attenuation", value=1)
    sim.energy.target_harmonic = sim.Signal(name="target_harmonic", value=21)
    sim.energy.locked_harmonic = sim.Signal(name="locked_harmonic", value=previous)
    sim.energy.enableivu = sim.Signal(name="enableivu", value=True)
    selected = requested or 5

    def select(start, stop, *, harmonic=None, **kwargs):
        assert (start, stop) == (11860, 12059)
        assert harmonic == requested
        if failure == "gap":
            raise RuntimeError("No harmonic covers the interval")
        return selected

    sim.energy.harmonic_for_range = select
    # Exercise the actual hardware-independent profile wrapper when available.
    wrapper_path = (Path.home() / ".ipython/profile_collection/src/smi_beamline/plans/harmonic_lock.py")
    if not wrapper_path.exists():
        pytest.skip("Local profile harmonic-lock integration requires profile_collection")
    wrapper = runpy.run_path(str(wrapper_path))["with_harmonic_lock"]

    def live_wrapper(plan, *args, **kwargs):
        return (yield from wrapper(plan, *args, energy=sim.energy, **kwargs))

    moves = []
    original_energy_set = sim.energy.set

    def set_energy(value, **kwargs):
        moves.append((value, sim.energy.locked_harmonic.get()))
        return original_energy_set(value, **kwargs)

    monkeypatch.setattr(sim.energy, "set", set_energy)
    theta_moves = []
    theta_set = sim.stage.theta.set

    def set_theta(value, **kwargs):
        theta_moves.append(value)
        return theta_set(value, **kwargs)

    monkeypatch.setattr(sim.stage.theta, "set", set_theta)

    def align(angle):
        assert sim.energy.locked_harmonic.get() == selected
        if failure == "alignment":
            raise RuntimeError("Alignment failed")
        assert angle == .2
        yield from sim.det_exposure_time(.5, .5)
        yield from sim.bps.mv(sim.stage.theta, 1.2, sim.stage.y, .25, atten, 1)
        if failure == "alignment_target":
            # Model a motor reporting completion without reaching its final target.
            signal = sim.stage.theta.setpoint
            original_read = signal.read

            def wrong_target():
                reading = original_read()
                reading[signal.name]["value"] = -.19
                return reading

            monkeypatch.setattr(signal, "read", wrong_target)

    g = sim.globals_dict()
    g.update(attenuation=atten, alignement_gisaxs_hex=align, with_harmonic_lock=live_wrapper)
    path = Path(__file__).resolve().parents[1] / "hard_grazing_damage_check.py"
    ns = runpy.run_path(str(path), init_globals=g)
    settings = []
    original_set = atten.set

    def capture(value, **kw):
        settings.append((sim.energy.position, value))
        return original_set(value, **kw)

    monkeypatch.setattr(atten, "set", capture)
    if failure == "gap":
        with pytest.raises(RuntimeError, match="No harmonic"):
            sim.run(ns["run_plan"](harmonic=requested))
        assert settings == []
        assert moves == []
        assert sim.energy.locked_harmonic.get() == previous
        return
    if failure == "alignment":
        with pytest.raises(RuntimeError, match="Alignment failed"):
            sim.run(ns["run_plan"](harmonic=requested))
        assert sim.energy.locked_harmonic.get() == previous
        return
    if failure == "alignment_target":
        with pytest.raises(RuntimeError, match="Alignment did not reach"):
            sim.run(ns["run_plan"](harmonic=requested))
        assert settings == [(11860, 1)]  # No measurement foil setup/acquisition.
        assert sim.energy.locked_harmonic.get() == previous
        return
    result = sim.run(ns["run_plan"](harmonic=requested))
    assert sim.energy.locked_harmonic.get() == previous
    assert sim.energy.target_harmonic.get() == 21
    assert moves[:2] == [(11860, previous), (11860, selected)]
    assert all(lock == selected for _, lock in moves[2:])
    assert result.run_count() == (7, 7)
    starts = [d for n, d in result.docs if n == "start"]
    descs = {d["uid"]: d for n, d in result.docs if n == "descriptor"}
    data = {s["uid"]: [] for s in starts}
    for name, doc in result.docs:
        if name == "event" and descs[doc["descriptor"]]["name"] == "primary":
            data[descs[doc["descriptor"]]["run_start"]].append(doc["data"])
    before = data[starts[0]["uid"]]
    main = [d for s in starts[1:-1] for d in data[s["uid"]]]
    after = data[starts[-1]["uid"]]
    assert [len(data[s["uid"]]) for s in starts[1:-1]] == [108] * 5
    assert len(theta_moves) == 16  # Alignment + 5 before + 5 fixed-angle scans + 5 after.
    for s, ai in zip(starts[1:-1], ns["INCIDENCE_ANGLES"]):
        assert {d["incident_angle"] for d in data[s["uid"]]} == {ai}
    assert [len(before), len(main), len(after)] == [5, 540, 5]
    assert settings == [(11860, 1), (11860, 10)]
    assert len({s["damage_check_group"] for s in starts}) == 1
    assert all(s["harmonic_lock"] == {
        "harmonic": selected, "start_eV": 11860, "stop_eV": 12059, "gap_margin_um": 0,
    } for s in starts)
    assert all("bpm3{xbpm3_sumX}" in s["sample_name"] for s in starts)
    assert all(s["incidence_motor"] == "stage.theta" for s in starts)
    assert all(s["alignment_plan"] == "alignement_gisaxs_hex" for s in starts)
    for rows in (before, main, after):
        for d in rows:
            assert d["attenuation"] == 10
            assert d["piezo_x"] == 100 and d["piezo_y"] == 200
            assert d["piezo_th"] == 0
            assert d["stage_y"] == .25
            assert np.isclose(d["stage_theta"], 1.2 + d["incident_angle"])
    for check, angles in ((before, ns["INCIDENCE_ANGLES"]), (after, ns["INCIDENCE_ANGLES"][::-1])):
        assert [d["energy_set"] for d in check] == [11860] * 5
        np.testing.assert_allclose([d["incident_angle"] for d in check], angles)
    assert starts[0]["scan_name"] == starts[-1]["scan_name"] == "beam_damage_check"
    assert "beam_damage_check_before" in starts[0]["sample_name"]
    assert "beam_damage_check_after" in starts[-1]["sample_name"]
    assert sim.pil2M.cam.acquire_time.get() == 1
    assert any(k.startswith("pil2M_") for k in main[0])
    assert any(k.startswith("pil900KW_") for k in main[0])


def test_recorded_continuation_skips_pairs(sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    path = Path(__file__).resolve().parents[1] / "hard_grazing_damage_check.py"
    snapshot = json.loads(path.with_name("hard_resume_1170456.json").read_text())
    ids = [snapshot["sample_id"]] + snapshot["remaining_sample_ids"]
    samples = [Sample(name, id=sid, piezo_x=i * 100, piezo_y=200, piezo_th=0)
               for i, (sid, name) in enumerate(zip(ids, ["Au_c4x", "Au_c8x", "Au_c8x_2"]))]
    extra = Sample("new_extra_sample", piezo_x=9999)
    monkeypatch.setattr(smi_plans, "load_holder", lambda name: samples + [extra])
    atten = sim.Signal(name="attenuation", value=1)
    atten.inserted = sim.Signal(name="attenuation_inserted", value=snapshot["attenuation_inserted"])
    alignments = []

    def align(angle):
        alignments.append(sim.piezo.x.position)
        yield from sim.bps.mv(sim.stage.theta, .5, sim.stage.y, .3)

    def wrapper(plan, *, start, stop, harmonic):
        assert (start, stop, harmonic) == (11860, 12059, 11)
        yield from sim.bps.mv(sim.energy, start)
        return (yield from plan)

    g = sim.globals_dict()
    g.update(attenuation=atten, alignement_gisaxs_hex=align, with_harmonic_lock=wrapper)
    ns = runpy.run_path(str(path), init_globals=g)
    result = sim.run(ns["run_resume_1170456"]())
    assert result.run_count() == (20, 20)
    assert sim.primary_events(result) == 1257  # 152+5 continuation, 2*(540+10) new.
    assert alignments == [100, 200]  # Not the partially measured sample or new holder entries.
    starts = [d for n, d in result.docs if n == "start"]
    descs = {d["uid"]: d for n, d in result.docs if n == "descriptor"}
    by_run = {s["uid"]: [] for s in starts}
    for name, d in result.docs:
        if name == "event" and descs[d["descriptor"]]["name"] == "primary":
            by_run[descs[d["descriptor"]]["run_start"]].append(d["data"])
    main = starts[:5]
    assert [len(by_run[s["uid"]]) for s in main] == [30, 30, 30, 31, 31]
    resumed = [d for s in main for d in by_run[s["uid"]]]
    old_pairs = {tuple(pair) for pair in snapshot["recorded_pairs"]}
    new_pairs = {(d["energy_set"], d["incident_angle"]) for d in resumed}
    assert not (old_pairs & new_pairs)
    assert old_pairs | new_pairs == {(e, a) for e in ns["ENERGIES"] for a in ns["INCIDENCE_ANGLES"]}
    assert len(new_pairs) == 152
    assert all(s["continuation_of"] == snapshot["source_uid"] for s in starts[:6])
    for d in resumed:
        assert d["piezo_x"] == snapshot["position"]["piezo_x"]
        assert d["stage_y"] == snapshot["position"]["stage_y"]
        assert np.isclose(d["stage_theta"], snapshot["theta_zero"] + d["incident_angle"])


@pytest.mark.parametrize("which", ["blank", "sparse", "tender", "limit", "reuse", "resume_tender", "resume_1170565"])
def test_additional_selections(which, sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    hard = [Sample(n, piezo_x=i * 100, piezo_y=200, piezo_th=0) for i, n in enumerate([
        "Au_c1x", "Au_c1x_sparse_left", "Au_c4x_sparse_right", "BlankSi_11keV",
    ])]
    tender = [Sample(n, piezo_x=-59145 if i == 0 else i * 100, piezo_y=200, piezo_th=0)
              for i, n in enumerate(["In2O3_c1x", "In2O3_4x", "In2O3_c8x", "In2O3_c8x_2", "BlankSi_3p7keV"])]
    loaded_holders = []

    def load_test_holder(name):
        loaded_holders.append(name)
        return hard if name == "Hard" else tender

    monkeypatch.setattr(smi_plans, "load_holder", load_test_holder)
    in_energies = np.concatenate([np.arange(3671,3721,5), np.arange(3721,3771),
                                 np.arange(3771,3871,5)]).astype(float).tolist()
    monkeypatch.setattr(smi_plans.ListStore, "from_redis", lambda: object())
    monkeypatch.setattr(smi_plans, "resolve_list", lambda name, **kw: in_energies)
    atten = sim.Signal(name="attenuation", value=1)
    alignments, locks, theta_moves, foil_settings = [], [], [], []

    def align(angle):
        alignments.append(sim.piezo.x.position)
        yield from sim.bps.mv(sim.stage.theta, .4)

    def lock(plan, *, start, stop, harmonic):
        locks.append((start, stop))
        yield from sim.bps.mv(sim.energy, start)
        yield from plan

    old_theta = sim.stage.theta.set
    old_atten = atten.set

    def theta_set(value, **kw):
        theta_moves.append(value)
        return old_theta(value, **kw)

    def atten_set(value, **kw):
        foil_settings.append((sim.energy.position, value))
        return old_atten(value, **kw)

    def check_x(value):
        if which in ("limit", "reuse") and value < -58164.9:
            raise ValueError("Below limit")

    monkeypatch.setattr(sim.stage.theta, "set", theta_set)
    monkeypatch.setattr(atten, "set", atten_set)
    monkeypatch.setattr(sim.piezo.x, "check_value", check_x)
    g = sim.globals_dict()
    g.update(attenuation=atten, alignement_gisaxs_hex=align, with_harmonic_lock=lock)
    path = Path(__file__).resolve().parents[1] / "hard_grazing_damage_check.py"
    ns = runpy.run_path(str(path), init_globals=g)
    # Added after loading the script: the Tender plan must discover it at execution.
    tender.append(Sample("In2O3_sparse_leftc4x", piezo_x=-49350.388, piezo_y=200, piezo_th=0))
    if which in ("resume_tender", "resume_1170565"):
        for s, sid in zip(tender[2:], [
            "a3987f291eea4e49b2ca14e8499f7f69", "9bc664e66e064043bb244dc083cfdcb9",
            "319866b5290d4b1fbb0d4e75cf045c9b", "1d3e647ca5cc4dedafa3dea35e9a7e78",
        ]):
            s.id = sid
        resume_scan = "1170565" if which == "resume_1170565" else "1170553"
        ns = runpy.run_path(str(path.with_name(f"tender_resume_{resume_scan}.py")), init_globals=g)
    command = {"blank": "run_hard_blank", "sparse": "run_hard_sparse",
               "tender": "run_tender_indium", "limit": "run_tender_indium",
               "reuse": "run_tender_indium", "resume_tender": "run_tender_resume_1170553",
               "resume_1170565": "run_tender_resume_1170565"}[which]
    if which == "limit":
        with pytest.raises(ValueError, match="In2O3_c1x.*limit"):
            sim.run(ns[command]())
        assert locks == alignments == foil_settings == []
        return
    if which == "reuse":
        sim.stage.theta.set(.4).wait()
        sim.stage.y.set(1.234).wait()
        sim.piezo.x.set(-57000).wait()
        sim.piezo.y.set(4321).wait()
        theta_moves.clear()
    kwargs = {"reuse_first_alignment": True} if which == "reuse" else {}
    if which == "tender":
        kwargs["holder"] = "Tender_remounted"
    result = sim.run(ns[command](**kwargs))
    if which == "tender":
        assert loaded_holders[-1] == "Tender_remounted"
    starts = [d for n, d in result.docs if n == "start"]
    expected = {"blank": (1, 5, [hard[-1]], 11900, 11900),
                "sparse": (14, 1100, hard[1:3], 11860, 12059),
                "tender": (36, 1968, tender, 3671, 3866),
                "reuse": (36, 1968, tender, 3671, 3866),
                "resume_tender": (24, 1312, tender[2:], 3671, 3866),
                "resume_1170565": (18, 984, tender[3:], 3671, 3866)}[which]
    runs, events, selected, lo, hi = expected
    assert result.run_count() == (runs, runs)
    assert sim.primary_events(result) == events
    assert {s["sample_id"] for s in starts} == {s.id for s in selected}
    assert locks == [(lo, hi)]
    assert foil_settings == [(lo, 1 if which.startswith("resume") else 10)] * len(selected)
    assert all(s["attenuation_reference_energy_eV"] == lo for s in starts)
    assert len(alignments) == len(selected) - (which == "reuse")
    moves_per_sample = 13 if which in ("tender", "reuse", "resume_tender", "resume_1170565") else 16
    assert len(theta_moves) == (6 if which == "blank" else moves_per_sample * len(selected) - (which == "reuse"))
    if which == "blank":
        assert starts[0]["scan_name"] == "blank_measurement"
    if which == "tender":
        assert all(s["holder_name"] == "Tender_remounted" for s in starts)
    if which.startswith("resume"):
        source = ("a8d300ff-cd02-41e8-bc08-fa50152eb7c5" if which == "resume_1170565"
                  else "b85b41f8-ab74-4469-a288-9287e98f8f90")
        assert all(s["continuation_of"] == source for s in starts)
        assert all(not s["alignment_reused"] for s in starts)
        assert alignments == [s.piezo_x for s in selected]
    if which in ("tender", "reuse", "resume_tender", "resume_1170565"):
        assert all(s["energy_list"] == "In L3 1ev 80 pts" for s in starts)
        descs = {d["uid"]: d for name, d in result.docs if name == "descriptor"}
        by_run = {s["uid"]: [] for s in starts}
        for name, doc in result.docs:
            if name == "event" and descs[doc["descriptor"]]["name"] == "primary":
                by_run[descs[doc["descriptor"]]["run_start"]].append(doc["data"])
        for sample in selected:
            sample_runs = [s for s in starts if s["sample_id"] == sample.id]
            before, *main, after = [by_run[s["uid"]] for s in sample_runs]
            assert [len(before), *map(len, main), len(after)] == [4, 80, 80, 80, 80, 4]
            assert [d["incident_angle"] for d in before] == [.3, .4, .5, .6]
            assert [d["incident_angle"] for d in after] == [.6, .5, .4, .3]
            for rows, ai in zip(main, [.3, .4, .5, .6]):
                assert {d["incident_angle"] for d in rows} == {ai}
                np.testing.assert_allclose([d["stage_theta"] for d in rows], .4 + ai)
            if which == "reuse" and sample is selected[0]:
                assert all(s["alignment_reused"] for s in sample_runs)
                for s in sample_runs:
                    for d in by_run[s["uid"]]:
                        assert d["piezo_x"] == -57000
                        assert d["piezo_y"] == 4321
                        assert d["stage_y"] == 1.234

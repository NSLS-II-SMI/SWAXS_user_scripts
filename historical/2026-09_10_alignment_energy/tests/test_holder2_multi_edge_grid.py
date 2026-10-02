"""Full-length multi-edge acquisition on two simulated samples."""

import runpy
from pathlib import Path

import numpy as np
import pytest

from smi_plans import Position, Sample


@pytest.mark.parametrize("recovery", [False, True])
def test_multi_edge_grid(recovery, sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    bar = [
        Sample("s1", piezo_x=100, piezo_y=200,
               refined=Position(piezo_x=1000, piezo_y=2000, piezo_z=3000)),
        Sample("s2", piezo_x=-5000, piezo_y=-6000, piezo_z=4000),
    ]
    centers = [(1000, 2000, 3000), (-5000, -6000, 4000)]
    if recovery:
        bar[1] = Sample("S5", piezo_x=-58189.565, piezo_y=-6789.968, piezo_z=4000)
        centers[1] = (-58189.565, -6789.968, 4000)
    counts = [87, 87, 87, 87, 80]
    labels = ["MnK", "FeK", "CoK", "NiK", "ZnK"]
    names = [f"{el} K 1ev 87 pts" for el in ["Mn", "Fe", "Co", "Ni"]] + ["Zinc 1ev 80 pts"]
    grids = {name: (edge + np.arange(n)).tolist() for name, edge, n in
             zip(names, [6480, 7053, 7650, 8274, 9600], counts)}
    monkeypatch.setattr(smi_plans, "load_holder", lambda name: bar)
    monkeypatch.setattr(smi_plans.ListStore, "from_redis", lambda: object())
    monkeypatch.setattr(smi_plans, "resolve_list", lambda name, **kw: grids[name])
    path = Path(__file__).resolve().parents[1] / "holder2_multi_edge_grid.py"
    ns = runpy.run_path(str(path), init_globals=sim.globals_dict())
    assert (ns["nx"], ns["ny"], ns["events_per_sample"]) == (10, 86, 856)
    sim.waxs.arc.set(20).wait()
    x_targets = []
    original_set = sim.piezo.x.set

    def checked_set(value, **kwargs):
        x_targets.append(value)
        if recovery:
            assert value > -58164.9
        return original_set(value, **kwargs)

    monkeypatch.setattr(sim.piezo.x, "set", checked_set)
    result = sim.run(ns["run_s5_edges" if recovery else "run_holder2_edges"]())
    selected = bar[1:] if recovery else bar
    selected_centers = centers[1:] if recovery else centers
    assert result.run_count() == (10 * len(selected), 10 * len(selected))
    assert sim.primary_events(result) == 856 * len(selected)
    if recovery:
        assert min(x_targets) == pytest.approx(-58089.565)
        assert max(x_targets) == pytest.approx(-57189.565)
    starts = [d for name, d in result.docs if name == "start"]
    descriptors = {d["uid"]: d for name, d in result.docs if name == "descriptor"}
    events = {s["uid"]: [] for s in starts}
    for name, doc in result.docs:
        if name == "event":
            desc = descriptors[doc["descriptor"]]
            if desc["name"] == "primary":
                events[desc["run_start"]].append(doc["data"])
    for sample_index, (sample, (cx, cy, cz)) in enumerate(zip(selected, selected_centers)):
        point = 0
        all_data = []
        for run_index, start in enumerate(starts[sample_index * 10:(sample_index + 1) * 10]):
            edge_index = run_index % 5
            arc = 0 if run_index < 5 else 20
            assert start["sample_id"] == sample.id
            assert start["edge_label"] == labels[edge_index]
            assert start["energy_list"] == names[edge_index]
            assert f"wa{arc:04.1f}" in start["sample_name"]
            assert labels[edge_index] in start["sample_name"]
            assert start["grid"]["first_point"] == point
            assert start["grid"]["anchor"] == (
                "top_left_minimum_y" if recovery else "top_middle_minimum_y"
            )
            data = events[start["uid"]]
            assert len(data) == counts[edge_index]
            assert [d["energy_set"] for d in data] == grids[names[edge_index]]
            assert [d["grid_point"] for d in data] == list(range(point, point + len(data)))
            for d in data:
                assert d[sim.waxs.arc.name] == arc
                assert any(k.startswith("pil2M_") for k in d) == (arc == 20)
                assert any(k.startswith("pil900KW_") for k in d)
            all_data.extend(data)
            point += len(data)
        xy = np.array([(d["piezo_x"], d["piezo_y"]) for d in all_data])
        assert len(np.unique(xy, axis=0)) == 856
        left = cx + 100 if recovery else cx - 450
        np.testing.assert_allclose(xy.min(axis=0), [left, cy])
        np.testing.assert_allclose(xy.max(axis=0), [left + 900, cy + 850])
        assert np.all(xy[:, 1] >= cy)
        # All consecutive exposures are one Y nudge or one X column transition,
        # including the boundaries between edges and the two WAXS angles.
        delta = np.diff(xy, axis=0)
        assert set(map(tuple, np.round(delta, 6))) == {(0, 10), (0, -10), (100, 0)}
        np.testing.assert_allclose(xy[0], [left, cy])
    assert sim.piezo.z.position == centers[-1][2]

    # Grid construction also handles smaller and non-full-column scans.
    for n in (1, 2, 80, 100, 857):
        offsets, _, _ = ns["top_middle_grid"](n)
        assert len(np.unique(offsets, axis=0)) == n
        assert offsets[:, 1].min() >= 0


@pytest.mark.parametrize("start_point", [179, 428, 855])
def test_s5_continuation(start_point, sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    sample = Sample("S5", piezo_x=-58189.565, piezo_y=-6789.968)
    names = [f"{el} K 1ev 87 pts" for el in ["Mn", "Fe", "Co", "Ni"]] + ["Zinc 1ev 80 pts"]
    grids = {}
    for name, edge in zip(names[:4], [6539, 7112, 7709, 8333]):
        grids[name] = np.concatenate([
            np.arange(edge - 59, edge - 9, 5), np.arange(edge - 9, edge + 41),
            np.arange(edge + 41, edge + 91, 3), np.arange(edge + 91, edge + 141, 5),
        ]).tolist()
    grids[names[-1]] = np.concatenate([
        np.arange(9600, 9650, 5), np.arange(9650, 9700), np.arange(9700, 9800, 5),
    ]).tolist()
    monkeypatch.setattr(smi_plans, "load_holder", lambda name: [sample])
    monkeypatch.setattr(smi_plans.ListStore, "from_redis", lambda: object())
    monkeypatch.setattr(smi_plans, "resolve_list", lambda name, **kw: grids[name])
    path = Path(__file__).resolve().parents[1] / "holder2_multi_edge_grid.py"
    ns = runpy.run_path(str(path), init_globals=sim.globals_dict())
    targets = []
    original_set = sim.piezo.x.set

    def checked_set(value, **kwargs):
        assert value > -58164.9
        targets.append(value)
        return original_set(value, **kwargs)

    monkeypatch.setattr(sim.piezo.x, "set", checked_set)
    result = sim.run(ns["run_s5_edges"](start_point=start_point))
    starts = [d for name, d in result.docs if name == "start"]
    descriptors = {d["uid"]: d for name, d in result.docs if name == "descriptor"}
    data = [d["data"] for name, d in result.docs
            if name == "event" and descriptors[d["descriptor"]]["name"] == "primary"]
    assert [d["grid_point"] for d in data] == list(range(start_point, 856))
    full_energies = [v for name in names for v in grids[name]] * 2
    assert [d["energy_set"] for d in data] == full_energies[start_point:]
    expected_xy = ns["offsets"][start_point:] + [sample.piezo_x + 550, sample.piezo_y]
    np.testing.assert_allclose([[d["piezo_x"], d["piezo_y"]] for d in data], expected_xy)
    assert targets[0] == pytest.approx(expected_xy[0, 0])
    assert starts[0]["grid"]["first_point"] == start_point
    assert all(s["grid"]["resume_start_point"] == start_point for s in starts)
    if start_point == 179:
        assert result.run_count() == (8, 8)
        assert data[0]["energy_set"] == 7675
        assert starts[0]["edge_label"] == "CoK"
        assert starts[0]["waxs_arc_target"] == 0
    if start_point == 428:
        assert result.run_count() == (5, 5)
        assert all(s["waxs_arc_target"] == 20 for s in starts)
    if start_point == 855:
        assert result.run_count() == (1, 1)

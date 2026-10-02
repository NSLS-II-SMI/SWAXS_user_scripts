"""Exercise the field plan with simulated devices and in-memory scan inputs."""

import runpy
from pathlib import Path

import numpy as np
import pytest

from smi_plans import Position, Sample


@pytest.mark.parametrize("n", [80, 100])
@pytest.mark.parametrize("mode,start_block", [("simultaneous", 0), ("waxs0", 1), ("both", 0)])
def test_endpoint_agb_and_correlated_snake(n, mode, start_block, sim, inject, monkeypatch):
    import smi_plans

    inject("smi_plans._compose")
    bar = [
        Sample("sample1", piezo_x=1000, piezo_y=2000,
               refined=Position(piezo_x=1100, piezo_y=2100)),
        Sample(" AGB ", piezo_x=500, piezo_y=600),
        Sample("sample2", piezo_x=3000, piezo_y=4000),
    ]
    # Descending order ensures endpoints use min/max but samples retain list order.
    energies = np.linspace(2500, 2400, n)
    monkeypatch.setattr(smi_plans, "load_holder", lambda name: bar)
    monkeypatch.setattr(smi_plans.ListStore, "from_redis", lambda: object())
    monkeypatch.setattr(smi_plans, "resolve_list", lambda *a, **kw: energies)
    path = Path(__file__).resolve().parents[1] / "saxs_nexafs_snake.py"
    ns = runpy.run_path(str(path), init_globals=sim.globals_dict())
    # Start at the opposite arc to catch selection before the move.
    sim.waxs.arc.set(20 if mode == "waxs0" else 0).wait()
    if mode == "waxs0":
        result = sim.run(ns["run_plan"]())  # Recovery is the default.
    else:
        result = sim.run(ns["run_plan"](mode=mode, start_block=start_block))

    arcs = {"simultaneous": [20], "waxs0": [0], "both": [20, 0]}[mode]
    assert result.run_count() == (3 * len(arcs), 3 * len(arcs))
    descriptors = {d["uid"]: d for name, d in result.docs if name == "descriptor"}
    starts = [d for name, d in result.docs if name == "start"]
    events = {start["uid"]: [] for start in starts}
    for name, doc in result.docs:
        if name == "event":
            descriptor = descriptors[doc["descriptor"]]
            if descriptor["name"] == "primary":
                events[descriptor["run_start"]].append(doc["data"])
    pitch = 400 if n == 80 else 500
    old_x_max = 150 if n == 80 else 200
    for pass_index, arc in enumerate(arcs):
        block = start_block + pass_index
        run_starts = starts[pass_index * 3:(pass_index + 1) * 3]
        agb, first, second = [events[start["uid"]] for start in run_starts]
        assert [len(agb), len(first), len(second)] == [2, n, n]
        for start in run_starts:
            assert start["position_block"] == block
            assert f"wa{arc:04.1f}" in start["sample_name"]
            for d in events[start["uid"]]:
                assert d[sim.waxs.arc.name] == arc
                assert any(k.startswith("pil2M_") for k in d) == (arc == 20)
                assert any(k.startswith("pil900KW_") for k in d)
        assert [d["energy_set"] for d in agb] == [2400, 2500]
        assert [(d["piezo_x"], d["piezo_y"]) for d in agb] == [(500 + block * 100, 600)] * 2
        for data, (cx, cy) in [(first, (1100, 2100)), (second, (3000, 4000))]:
            np.testing.assert_allclose([d["energy_set"] for d in data], energies)
            xy = np.array([(d["piezo_x"], d["piezo_y"]) for d in data])
            assert len(np.unique(xy, axis=0)) == n
            np.testing.assert_allclose(
                (xy.min(axis=0) + xy.max(axis=0)) / 2, [cx + block * pitch, cy],
            )
            if block > 0:
                # The entire new block lies beyond the previous block, 100 um away.
                assert xy[:, 0].min() == cx + (block - 1) * pitch + old_x_max + 100
            # First 20 Y nudges, an X-only transition, then 20 Y nudges upward.
            delta = np.diff(xy, axis=0)
            np.testing.assert_allclose(delta[:20], np.tile([0, -10], (20, 1)))
            np.testing.assert_allclose(delta[20], [100, 0])
            np.testing.assert_allclose(delta[21:41], np.tile([0, 10], (20, 1)))
            np.testing.assert_allclose(delta[41], [100, 0])

"""Offline RunEngine verification with in-memory devices only."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import bluesky.preprocessors as bpp
import numpy as np
import pytest
from bluesky import RunEngine
from bluesky.utils import Msg
from ophyd import Signal
from ophyd.sim import SynAxis, SynSignal
from ophyd.status import Status
from smi_beamline.devices.attenuator_data import FOIL_LAYOUT, attenuation_factor


@pytest.fixture
def script():
    spec = importlib.util.spec_from_file_location("crl_series", Path(__file__).with_name("crl_focus_series.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def live_report():
    spec = importlib.util.spec_from_file_location(
        "live_focus_report", Path(__file__).with_name("live_focus_report.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_namespace():
    energy = SynAxis(name="energy", value=16150)
    energy.energy = energy.readback
    energy.enableivu = Signal(name="enableivu", value=True)
    energy.locked_harmonic = Signal(name="locked_harmonic", value=0)
    energy.harmonic_for_range = lambda start, stop, **kwargs: kwargs.get("harmonic") or 7
    crl = SimpleNamespace(z=SynAxis(name="crl_z", value=200),
                          x=SynAxis(name="crl_x", value=0),
                          y=SynAxis(name="crl_y", value=0))
    for i in range(1, 13):
        setattr(crl, f"lens{i}", SynAxis(name=f"crl_lens{i}", value=10 if i <= 6 else -10))
    piezo = SimpleNamespace(x=SynAxis(name="piezo_x", value=-14705))
    # Knife-edge intensity rises through an edge 50 µm off the nominal coarse center,
    # well inside the ±400 µm search, so _edge_center finds a non-boundary peak.
    edge0 = -14705 + 50.0
    detector = SynSignal(
        name="pil2M",
        func=lambda: 1000.0 / (1.0 + np.exp(-(piezo.x.position - edge0) / 8.0)),
    )
    # The coarse scan reads pil2M.stats1.total; in the fake it is the same edge signal.
    detector.stats1 = SimpleNamespace(total=detector)
    detector.cam = SimpleNamespace(**{
        k: Signal(name=k, value=v) for k, v in {
            "acquire_time": 0.2, "acquire_period": 0.201,
            "num_images": 1, "energyset": 16.15,
        }.items()
    })
    for name, val in [("cam_energy", 16.15), ("threshold", 8.075), ("gain", 1), ("apply", 1)]:
        setattr(detector, name, Signal(name=f"pil2M_{name}", value=val))
    detector.energy_read = detector.cam_energy
    detector.threshold_read = detector.threshold
    detector.gain_read = detector.gain

    # The plan no longer drives attenuation by factor; it just reads the device and
    # inserts one foil per holder via the two banks. Model those minimally.
    attenuation = SynSignal(name="attenuation", func=lambda: 1.0e6)

    class FakeBank:
        def __init__(self, name):
            self.name = name
            self.parent = None
            self.inserted = []

        def set(self, inserted):
            self.inserted = list(inserted)
            st = Status()
            st.set_finished()
            return st

    return {"energy": energy, "crl": crl, "pil2M": detector, "piezo": piezo,
            "attenuation": attenuation,
            "attenuators1": FakeBank("attenuators1"),
            "attenuators2": FakeBank("attenuators2")}


def no_sleep(plan):
    return bpp.msg_mutator(plan, lambda msg: Msg("null") if msg.command == "sleep" else msg)


def test_windows_and_single_foil(script):
    specs = script.scan_specs()
    assert [s["holders"] for s in specs] == [(5,), (4,), (2,), (3,)]
    assert specs[0]["start_eV"] == 6000 and specs[-1]["stop_eV"] == 18800
    for spec in specs:
        assert spec["start_eV"] < spec["focus_eV"] < spec["stop_eV"]
        foil = script._single_foil(spec["start_eV"], spec["stop_eV"], spec["holders"][0])
        assert foil in FOIL_LAYOUT
        # The chosen foil clears the minimum attenuation across the whole window.
        for e in np.linspace(spec["start_eV"], spec["stop_eV"], script.ENERGY_POINTS):
            assert attenuation_factor([foil], e) >= script.ATTENUATION_MIN_FACTOR


def test_edge_center_finds_offset_edge(script):
    x = np.linspace(-400, 400, 81)
    y = 1000.0 / (1.0 + np.exp(-(x - 37.0) / 5.0))
    assert script._edge_center(x, y) == pytest.approx(37.0, abs=5.0)
    # Order-independence: a shuffled profile locates the same edge.
    idx = np.argsort(np.sin(x))
    assert script._edge_center(x[idx], y[idx]) == pytest.approx(37.0, abs=5.0)


def test_edge_center_rejects_boundary(script):
    x = np.linspace(-400, 400, 81)
    y = np.zeros_like(x)
    y[-1] = 1000.0  # edge jammed against the search boundary
    with pytest.raises(RuntimeError, match="widen"):
        script._edge_center(x, y)


def test_missing_positions_prevents_all_motion(script):
    ns = fake_namespace()
    del script.HOLDER_ALIGNMENT[5]
    with pytest.raises(ValueError, match="HOLDER_ALIGNMENT"):
        next(script.crl_focus_series([(5,)], namespace=ns))
    assert ns["attenuators1"].inserted == [] and ns["attenuators2"].inserted == []
    assert ns["crl"].z.position == 200
    assert ns["crl"].x.position == 0 and ns["crl"].y.position == 0


def test_mv_settle_retries_on_failed_status(script):
    ax = SynAxis(name="ax")
    calls = {"n": 0}
    real_set = ax.set

    def flaky_set(val, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:  # first attempt reports a settle/following miss
            st = Status()
            st.set_exception(RuntimeError("settle miss"))
            return st
        return real_set(val, **kwargs)

    ax.set = flaky_set
    re = RunEngine({})
    re(no_sleep(script._mv_settle(ax, 5.0)))
    assert calls["n"] == 2 and ax.position == 5.0


def test_combined_holder_rejected(script):
    ns = fake_namespace()
    with pytest.raises(ValueError, match="single-holder"):
        next(script.crl_focus_series([(4, 5)], namespace=ns))
    assert ns["attenuators1"].inserted == [] and ns["attenuators2"].inserted == []


def test_coarse_then_fine_events_and_restoration(script):
    ns = fake_namespace()
    script.HOLDER_ALIGNMENT = {
        5: {"in_mm": -0.5, "crl_x_mm": -12.0, "crl_y_mm": -9.8},
        4: {"in_mm": 0.4, "crl_x_mm": -9.4, "crl_y_mm": -9.7},
    }
    script.ENERGY_POINTS = 3
    script.EDGE_POINTS = 5
    script.COARSE_POINTS = 41  # 20 µm steps over ±400 µm — resolves the fake edge
    docs = []
    re = RunEngine({})
    re.subscribe(lambda name, doc: docs.append((name, doc)))
    re(no_sleep(script.crl_focus_series([(5,), (4,)], namespace=ns)))

    starts = [d for n, d in docs if n == "start"]
    fine = [d for d in starts if d["scan_name"] == "crl_energy_focus_commissioning"]
    coarse = [d for d in starts if d["scan_name"] == "crl_energy_focus_coarse"]
    events = [d for n, d in docs if n == "event"]
    assert len(fine) == 2 and len(coarse) == 2
    assert len(events) == 2 * script.COARSE_POINTS + 2 * script.ENERGY_POINTS * script.EDGE_POINTS
    assert [d["crl_holders"] for d in fine] == [[5], [4]]
    assert [d["crl_holders"] for d in coarse] == [[5], [4]]
    assert all(d["harmonic_lock"]["harmonic"] == 7 for d in fine)
    # Every fine run carries the edge found by its coarse scan, near the fake edge (-14655).
    for d in fine:
        assert d["coarse_edge_center_um"] == pytest.approx(-14655.0, abs=12.0)
    # x/y and lenses ended at the last holder's (holder 4) alignment.
    assert ns["crl"].x.position == pytest.approx(-9.4)
    assert ns["crl"].y.position == pytest.approx(-9.7)
    assert ns["crl"].lens4.position == pytest.approx(0.4)
    assert ns["crl"].lens5.position == pytest.approx(script.OUT_POSITIONS_MM[5])
    # Each holder inserts exactly one foil; the last holder's (holder 4) foil remains in.
    specs = {s["holders"]: s for s in script.scan_specs([(5,), (4,)])}
    foil4 = script._single_foil(specs[(4,)]["start_eV"], specs[(4,)]["stop_eV"], 4)
    bank, pos = foil4.split("_")
    assert (ns[f"attenuators{bank}"]).inserted == [f"f{pos}"]
    assert all(d["attenuation_foil"] == foil4 for d in fine if d["crl_holders"] == [4])
    # Fine-run sensitivity follows each holder's model-focus energy.
    for d in fine:
        central = specs[tuple(d["crl_holders"])]["focus_eV"]
        assert d["pilatus_sensitivity_energy_eV"] == pytest.approx(central)
    fine_events = [d for d in events if "pil2M_cam_energy" in d["data"]]
    assert len(fine_events) == 2 * script.ENERGY_POINTS * script.EDGE_POINTS
    # Exposure/harmonic restored on completion.
    assert ns["energy"].locked_harmonic.get() == 0
    assert ns["pil2M"].cam.acquire_time.get() == 0.2


def test_report_path_loads_and_runs_cleanly(script, tmp_path):
    # The loader lazily imports the sibling module and returns the callback.
    path = tmp_path / "live.html"
    cb = script._live_report_callback(str(path))
    assert type(cb).__name__ == "LiveFocusReport" and cb.path == str(path)
    # Wiring it through the plan runs to completion; the callback is exception-safe even
    # when the in-memory fakes do not emit the real primary field names (so no file here).
    ns = fake_namespace()
    script.HOLDER_ALIGNMENT = {5: {"in_mm": -0.5, "crl_x_mm": -12.0, "crl_y_mm": -9.8}}
    script.ENERGY_POINTS = 3
    script.EDGE_POINTS = 5
    script.COARSE_POINTS = 7
    re = RunEngine({})
    re(no_sleep(script.crl_focus_series([(5,)], namespace=ns, report_path=str(path))))
    assert ns["crl"].lens5.position == pytest.approx(-0.5)


def test_failure_restores_policy_and_harmonic(script):
    ns = fake_namespace()
    script.HOLDER_ALIGNMENT = {5: {"in_mm": 0.1, "crl_x_mm": -12.0, "crl_y_mm": -9.8}}
    script.ENERGY_POINTS = 3
    script.EDGE_POINTS = 5
    script.COARSE_POINTS = 7

    def fail():
        raise RuntimeError("simulated detector failure")

    ns["pil2M"].trigger = fail
    re = RunEngine({})
    with pytest.raises(RuntimeError, match="simulated detector failure"):
        re(no_sleep(script.crl_focus_series([(5,)], namespace=ns)))
    assert ns["energy"].locked_harmonic.get() == 0
    assert ns["pil2M"].cam.acquire_time.get() == 0.2


def _feed_sweep(cb, holder, edge, widths, focus_eV):
    cb.start({"scan_name": "crl_energy_focus_commissioning", "crl_holders": [holder],
              "model_focus_eV": focus_eV, "coarse_edge_center_um": edge})
    for e_eV, w in widths.items():
        x = np.linspace(edge - 60, edge + 60, 31)
        y = 1000.0 / (1.0 + np.exp(-(x - edge) / w))
        for xi, yi in zip(x, y):
            cb.event({"data": {"energy_energy_setpoint": float(e_eV),
                               "piezo_x": float(xi), "pil2M_stats1_total": float(yi)}})
    cb.stop({})


def test_live_report_overwrites_single_html(live_report, tmp_path):
    path = tmp_path / "live.html"
    cb = live_report.LiveFocusReport(path, refresh_s=10)
    _feed_sweep(cb, 5, -14655.0, {6000: 4.0, 6150: 2.0, 6300: 5.0}, 6150.0)
    html1 = path.read_text()
    assert 'http-equiv="refresh"' in html1 and 'content="10"' in html1
    assert "holder 5" in html1 and "1 sweep" in html1
    # A second sweep overwrites the same file and now shows both holders.
    _feed_sweep(cb, 4, -14650.0, {8000: 4.0, 8698: 2.5, 9400: 6.0}, 8698.0)
    html2 = path.read_text()
    assert "holder 4" in html2 and "holder 5" in html2 and "2 sweep" in html2
    # Non-fine runs (the coarse scan) are ignored: the page is unchanged.
    cb.start({"scan_name": "crl_energy_focus_coarse", "crl_holders": [2]})
    cb.stop({})
    assert path.read_text() == html2

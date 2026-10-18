"""Offline checks of the recorded dataset and report interpretation."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("measurement_report", HERE / "measurement_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def test_known_gaussian_edge_and_clipping():
    x = np.linspace(-40, 40, 161)
    y = report.edge_model(x, 100, 10000, 0, 4)
    result = report.characterize(x, y)
    assert result["erf_fwhm_um"] == pytest.approx(4 * 2.354820045, rel=1e-4)
    assert result["derivative_fwhm_um"] == pytest.approx(4 * 2.354820045, rel=0.03)
    assert result["fit_coverage"]
    clipped = x <= 2
    result = report.characterize(x[clipped], y[clipped])
    assert not result["fit_coverage"]


def test_actual_coverage_overrides_exit_status():
    manifest = pd.read_csv(report.CACHE / "manifest.csv").set_index("scan_id")
    assert len(manifest) == 13
    for scan in report.COMPLETE:
        item = manifest.loc[scan]
        data = pd.read_csv(report.CACHE / f"{scan}_primary.csv")
        meta = json.loads((report.CACHE / f"{scan}_metadata.json").read_text())
        assert len(data) == item.actual_points == item.expected_points
        assert not data[["energy_energy_setpoint", "piezo_x"]].duplicated().any()
        sizes = data.groupby("energy_energy_setpoint").size()
        assert len(sizes) == 21
        assert (sizes == meta["start"]["shape"][-1]).all()
        assert np.isfinite(data[["piezo_x", "pil2M_stats1_total"]]).all().all()
    for scan, points in ((1170761, 105), (1170771, 53)):
        assert manifest.loc[scan, "exit_status"] == "success"
        assert manifest.loc[scan, "actual_points"] == points < manifest.loc[scan, "expected_points"]


def test_clean_minima_and_holder5_false_minimum():
    edges = pd.read_csv(HERE / "measurement_edges.csv")
    for scan, energy, width in ((1170759, 16.2, 5.3906), (1170765, 8.77, 4.7013)):
        s = edges[edges.scan_id == scan]
        best = s.loc[s.derivative_fwhm_um.idxmin()]
        assert best.energy_keV == pytest.approx(energy)
        assert best.derivative_fwhm_um == pytest.approx(width, abs=0.002)
    h5 = edges[edges.scan_id == 1170763]
    false_minimum = h5.loc[h5.derivative_fwhm_um.idxmin()]
    assert false_minimum.energy_keV == pytest.approx(6.1625)
    assert false_minimum.largest_downstep_fraction > 0.3
    # It is preserved as a diagnostic but never used in the geometry comparison.
    geometry = pd.read_csv(HERE / "measurement_geometry.csv")
    assert geometry.set_index("holder").loc[5, "sampled_core_energy_keV"] == pytest.approx(6.325)
    assert 2 not in set(geometry.holder)


def test_geometry_assumptions_are_explicit():
    geometry = pd.read_csv(HERE / "measurement_geometry.csv").set_index("holder")
    assert geometry.loc[3, "inferred_d0_SSA_mm"] == pytest.approx(1556.85, abs=0.1)
    assert geometry.loc[4, "inferred_d0_SSA_mm"] == pytest.approx(1630.85, abs=0.1)
    assert geometry.loc[3, "inferred_d0_collimated_mm"] < 1450
    assert geometry.loc[4, "inferred_d0_collimated_mm"] < 1450

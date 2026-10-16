"""Generate an offline Bokeh focus report; --cached uses saved scalar data."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from bokeh.embed import file_html
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    Div,
    HoverTool,
    Select,
    TabPanel,
    Tabs,
)
from bokeh.plotting import figure
from bokeh.resources import INLINE

from smi_plans.analysis import analyze_xy, make_figure

OUT = Path(__file__).resolve().parent
UID = "b73577b8-1712-4f89-9279-5cee108e184c"


def load(cached):
    if cached:
        return pd.read_csv(OUT / "scalar_data_1170759.csv"), json.loads(
            (OUT / "metadata_1170759.json").read_text())
    from tiled.client import from_profile

    run = from_profile("auto")["smi"]["raw"][UID]
    start, stop = run.metadata["start"], run.metadata["stop"]
    assert stop["exit_status"] == "success" and start["shape"] == [21, 21]
    primary = run["primary"]
    data = primary["data"].read(variables=[
        "time", "energy_energy", "energy_energy_setpoint", "energy_harmonic",
        "piezo_x", "pil2M_stats1_total",
    ]).to_dataframe().reset_index(drop=True)
    exposure = np.asarray(primary["config"]["pil2M"]["pil2M_cam_acquire_time"].read())
    assert np.allclose(exposure, 0.5)
    baseline = run["baseline"]["data"]
    fields = [k for k in baseline if k.startswith("crl_") and "setpoint" not in k]
    fields += ["ssa_hg", "ssa_vg", "attenuation_description"]
    meta = {"uid": UID, "scan_id": 1170759, "start": start["time"],
            "stop": stop["time"], "exposure_s": float(exposure.flat[0]),
            "attenuation": start["beamline_attenuators"],
            "baseline": baseline.read(variables=fields).to_dataframe().to_dict(orient="list")}
    data.to_csv(OUT / "scalar_data_1170759.csv", index=False)
    (OUT / "metadata_1170759.json").write_text(json.dumps(meta, indent=2) + "\n")
    return data, meta


def report(data, meta):
    assert len(data) == 441 and np.isfinite(data.to_numpy()).all()
    results, records, groups = [], [], []
    for i in range(21):
        s = data.iloc[i * 21:(i + 1) * 21].sort_values("piezo_x")
        assert np.ptp(s.energy_energy_setpoint) < 1e-6
        x, y = s.piezo_x.to_numpy(), s.pil2M_stats1_total.to_numpy()
        assert np.allclose(np.diff(x), 2)
        # The rising edge polarity is known. Analyze its positive derivative directly:
        # pf's automatic derivative polarity can invert a broad, truncated profile.
        dx = np.diff(x)
        result = analyze_xy(
            (x[1:] + x[:-1]) / 2, np.diff(y) / dx,
            yerr=np.sqrt(np.maximum(y[1:], 1) + np.maximum(y[:-1], 1)) / dx,
            model="none", profile="peak", x_sigma=0,
            motor="piezo_x (µm)", detector="d(counts)/dx (counts/µm)",
            scan_id=1170759, uid=UID,
        )
        result.derivative = True
        half = result.baseline + (max(result.y) - result.baseline) / 2
        complete = (result.y[0] < half and result.y[-1] < half
                    and np.isfinite(result.fwhm))
        if not complete:
            result.fwhm = result.cen = float("nan")
        records.append({
            "energy_keV": float(s.energy_energy_setpoint.median()) / 1000,
            "energy_readback_eV": float(s.energy_energy.mean()),
            "beam_fwhm_um": result.fwhm, "center_um": result.cen,
            "intensity_mcps": float(y[-3:].mean()) / meta["exposure_s"] / 1e6,
            "harmonic": int(s.energy_harmonic.iloc[0]),
            "width_status": "measured FWHM" if complete else "incomplete half-height coverage",
        })
        results.append(result)
        groups.append(s)
    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "summary_1170759.csv", index=False)
    source = ColumnDataSource(frame)
    plots = []
    for field, label, title, color in [
        ("beam_fwhm_um", "Beam FWHM (µm)", "CRL focus versus energy", "#105C78"),
        ("intensity_mcps", "Detector rate (million counts/s)", "Open-edge transmitted intensity", "#769E2D"),
    ]:
        p = figure(width=560, height=370, title=title, x_axis_label="Energy (keV)",
                   y_axis_label=label, tools="pan,wheel_zoom,box_zoom,reset,save",
                   background_fill_color="#F2F5F7")
        p.line("energy_keV", field, source=source, color=color, line_width=2)
        dots = p.scatter("energy_keV", field, source=source, color=color, size=8)
        p.add_tools(HoverTool(renderers=[dots], tooltips=[
            ("Energy", "@energy_keV{0.000} keV"), ("FWHM", "@beam_fwhm_um{0.00} µm"),
            ("Rate", "@intensity_mcps{0.00} Mcps"), ("Harmonic", "@harmonic"),
            ("Width status", "@width_status"),
        ]))
        plots.append(p)
    panels = []
    for i, (result, s) in enumerate(zip(results, groups)):
        energy = frame.energy_keV.iloc[i]
        raw = figure(width=560, height=410, title=f"Knife edge at {energy:.2f} keV",
                     x_axis_label="piezo_x (µm)", y_axis_label="Detector rate (Mcps)",
                     tools="pan,wheel_zoom,box_zoom,reset,save")
        raw.line(s.piezo_x, s.pil2M_stats1_total / meta["exposure_s"] / 1e6, color="#105C78")
        raw.scatter(s.piezo_x, s.pil2M_stats1_total / meta["exposure_s"] / 1e6, color="#105C78")
        deriv = make_figure(result, width=560, height=410,
                            title=f"pf derivative · {energy:.2f} keV · {frame.width_status.iloc[i]}")
        if np.isfinite(result.fwhm):
            half = result.baseline + (max(result.y) - result.baseline) / 2
            deriv.segment(x0=[result.cen - result.fwhm / 2], x1=[result.cen + result.fwhm / 2],
                          y0=[half], y1=[half], color="#769E2D", line_width=4)
        panels.append(row(raw, deriv, visible=i == 4))
    select = Select(title="Inspect energy", value="4", width=300,
                    options=[(str(i), f"{e:.2f} keV") for i, e in enumerate(frame.energy_keV)])
    select.js_on_change("value", CustomJS(args={"panels": panels}, code="""
        panels.forEach((p, i) => {p.visible = i === Number(cb_obj.value);});
    """))
    harmonic_groups = data.groupby("energy_energy_setpoint").energy_harmonic.first()
    header = Div(width=1120, text="""
        <div style="background:#1A5B7D;color:white;padding:20px;border-bottom:4px solid #B2D33B">
        <h1>SMI · CRL energy-focus scan 1170759</h1><p>15 October 2026 · 21 energies × 21 positions</p></div>
        <p>Holder 3 (16 × R50 µm Be) · CRL Z = +200 mm · SSA H/V gaps ≈0.030/0.050 mm<br>
        Recorded knife edge: <b>piezo_x</b>, −14718 to −14678 µm in 2 µm steps · 0.5 s exposure.</p>
        <p><b>Narrowest sampled beam: 5.39 µm FWHM at 16.20 keV.</b>
        Broad high-energy profiles lack reliable half-height coverage; these widths are omitted.</p>
    """)
    notes = Div(width=1120, text=f"""
        <h2>Method and interpretation</h2>
        <p>Width is the unsmoothed, model-free derivative FWHM relative to pf's estimated
        derivative baseline. Positive polarity is specified for these rising edges.
        Widths with an endpoint above half height are omitted rather than reporting a
        spurious narrow peak. Sampling is 2 µm; numerical decimals do not imply that precision.
        The finite scan window increasingly clips the broad tails away from focus.</p>
        <p>Intensity is the mean of the final three edge positions / 0.5 s, without dark,
        monitor, or attenuation correction. It is a finite-open-edge detector count rate,
        not calibrated flux. Fixed 240 µm Sn has energy-dependent transmission.
        Undulator harmonic changes also affect the intensity trend.</p>
        <p>Harmonics by commanded energy (eV): {harmonic_groups.to_dict()}</p>
        <p><a href="summary_1170759.csv">Summary CSV</a> ·
        <a href="scalar_data_1170759.csv">Scalar data</a> ·
        <a href="metadata_1170759.json">Metadata</a></p>
    """)
    table = Div(text=frame.round(3).to_html(index=False), width=1120)
    tabs = Tabs(tabs=[TabPanel(title="Overview", child=row(*plots)),
                      TabPanel(title="Individual knife edges / pf", child=column(select, *panels)),
                      TabPanel(title="Numerical results", child=table)])
    html = file_html(column(header, tabs, notes), INLINE, "SMI 1170759 — CRL focus versus energy")
    target = OUT / "scan_1170759_crl_focus.html"
    target.write_text(html)
    print(frame.to_string(index=False))
    print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cached", action="store_true")
    args = parser.parse_args()
    report(*load(args.cached))

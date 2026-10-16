"""Read-only scan analysis; run with the smi-plans Pixi environment.

    pixi run python ../SWAXS_user_scripts/Commissioning/2026-10-15_ssa_knife_edge_1170758/analyze.py

Writes a self-contained Bokeh HTML report and scalar CSVs beside this script.
Use --cached to regenerate from the saved scalar data without accessing Tiled.
"""

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
    DataTable,
    Div,
    HoverTool,
    NumberFormatter,
    Range1d,
    Select,
    TableColumn,
    TabPanel,
    Tabs,
)
from bokeh.palettes import Viridis256
from bokeh.plotting import figure
from bokeh.resources import INLINE

from smi_plans.analysis import analyze_xy, make_figure

OUT = Path(__file__).resolve().parent
UID = "f733330d-1a46-490d-a8f5-17897e20514c"
BLUE = "#105C78"
GREEN = "#769E2D"


def load_data(cached=False):
    if cached:
        return pd.read_csv(OUT / "scalar_data.csv"), json.loads(
            (OUT / "metadata.json").read_text())
    from tiled.client import from_profile

    run = from_profile("auto")["smi"]["raw"][UID]
    start, stop = run.metadata["start"], run.metadata["stop"]
    assert start["scan_id"] == 1170758 and stop["exit_status"] == "success"
    assert start["motors"] == ["ssa_hg", "piezo_x"]
    primary = run["primary"]
    data = primary["data"].read(variables=[
        "time", "ssa_hg", "ssa_hg_user_setpoint", "piezo_x",
        "pil2M_stats1_total",
    ]).to_dataframe().reset_index(drop=True)
    exposure = np.asarray(primary["config"]["pil2M"]["pil2M_cam_acquire_time"].read())
    assert np.allclose(exposure, exposure.flat[0])
    keys = primary.metadata["descriptors"][0]["data_keys"]
    assert keys["piezo_x"]["units"] == "um" and keys["ssa_hg"]["units"] == "mm"
    metadata = {
        "uid": UID, "scan_id": 1170758, "start_time": start["time"],
        "shape": list(start["shape"]), "motors": start["motors"],
        "exposure_s": float(exposure.flat[0]), "exit_status": stop["exit_status"],
        "attenuators": start["beamline_attenuators"],
        "units": {k: keys[k]["units"] for k in ("ssa_hg", "piezo_x")},
    }
    data.to_csv(OUT / "scalar_data.csv", index=False)
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return data, metadata


def analyze(data, metadata):
    ngap, npos = metadata["shape"]
    assert len(data) == ngap * npos == 399
    assert np.isfinite(data.to_numpy()).all()
    results, records, sweeps = [], [], []
    for i in range(ngap):
        # Group by grid row, not jittering gap readbacks.
        sweep = data.iloc[i * npos:(i + 1) * npos].sort_values("piezo_x")
        assert np.ptp(sweep.ssa_hg_user_setpoint) < 1e-8
        assert np.allclose(np.diff(sweep.piezo_x), 2)
        gap = float(sweep.ssa_hg_user_setpoint.median())
        counts = sweep.pil2M_stats1_total.to_numpy()
        result = analyze_xy(
            sweep.piezo_x, counts, der=True, model="none", profile="peak",
            smooth=False, x_sigma=0, scan_id=1170758, uid=UID,
            motor="piezo_x (µm)", detector="d(counts)/dx (counts/µm)",
        )
        # The closed slit records only one count in the entire sweep: no width.
        valid = np.ptp(counts) > 10 * np.sqrt(max(float(counts.max()), 1))
        intensity = float(counts[-3:].mean() / metadata["exposure_s"])
        records.append({
            "ssa_gap_setpoint_mm": max(gap, 0),
            "ssa_gap_readback_mm": float(sweep.ssa_hg.median()),
            "beam_fwhm_um": float(result.fwhm) if valid else np.nan,
            "derivative_baseline_counts_per_um": float(result.baseline),
            "center_um": float(result.cen) if valid else np.nan,
            "intensity_counts_per_s": intensity,
            "endpoint_spread_counts_per_s": float(counts[-3:].std(ddof=1) / metadata["exposure_s"]),
            "blocked_end_counts_per_s": float(counts[:3].mean() / metadata["exposure_s"]),
            "width_status": "measured derivative half maximum" if valid else "no signal",
        })
        results.append(result)
        sweeps.append(sweep)
    summary = pd.DataFrame(records)
    summary["relative_intensity_percent"] = 100 * summary.intensity_counts_per_s / summary.intensity_counts_per_s.iloc[-1]
    summary.to_csv(OUT / "summary.csv", index=False)
    return summary, results, sweeps


def chart(title, y_label):
    p = figure(title=title, width=560, height=360, x_axis_label="SSA horizontal gap (mm)",
               y_axis_label=y_label, tools="pan,wheel_zoom,box_zoom,reset,save",
               background_fill_color="#F2F5F7")
    p.title.text_color = BLUE
    return p


def build_report(summary, results, sweeps, metadata):
    source = ColumnDataSource(summary)
    width = chart("Beam size from knife-edge derivative", "Beam FWHM (µm)")
    intensity = chart("Open-edge transmitted intensity", "Detector count rate (million counts/s)")
    width.x_range = intensity.x_range = Range1d(-0.005, 0.205)
    source.data["intensity_mcps"] = summary.intensity_counts_per_s.to_numpy() / 1e6
    for p, field, color in [(width, "beam_fwhm_um", BLUE), (intensity, "intensity_mcps", GREEN)]:
        p.line("ssa_gap_setpoint_mm", field, source=source, color=color, line_width=2)
        dots = p.scatter("ssa_gap_setpoint_mm", field, source=source, color=color, size=8)
        p.add_tools(HoverTool(renderers=[dots], tooltips=[
            ("Gap (mm)", "@ssa_gap_setpoint_mm{0.0000}"),
            ("FWHM (µm)", "@beam_fwhm_um{0.00}"),
            ("Rate (Mcps)", "@intensity_mcps{0.00}"),
            ("Intensity vs 0.20 mm", "@relative_intensity_percent{0.0}%"),
        ]))
    width.y_range.start = intensity.y_range.start = 0

    profiles, options = [], []
    overlay = figure(width=1120, height=380, title="Normalized knife-edge sweeps",
                     x_axis_label="piezo_x (µm)", y_axis_label="Counts / open-edge mean",
                     tools="pan,wheel_zoom,box_zoom,reset,save")
    for i, (result, sweep) in enumerate(zip(results, sweeps)):
        gap = summary.ssa_gap_setpoint_mm.iloc[i]
        options.append((str(i), f"SSA gap {gap:.4f} mm"))
        raw = figure(width=560, height=400, title=f"Knife edge: SSA gap {gap:.4f} mm",
                     x_axis_label="piezo_x (µm)", y_axis_label="Detector count rate (million counts/s)",
                     tools="pan,wheel_zoom,box_zoom,reset,save")
        x = sweep.piezo_x.to_numpy()
        counts = sweep.pil2M_stats1_total.to_numpy()
        rate = counts / metadata["exposure_s"] / 1e6
        raw.line(x, rate, color=BLUE)
        raw.scatter(x, rate, color=BLUE, size=7)
        deriv = make_figure(result, width=560, height=400,
                            title=f"pf derivative: SSA gap {gap:.4f} mm")
        if i == 0:
            # Suppress meaningless single-count spike width in the closed-slit panel.
            deriv = Div(text="<p>Closed SSA: one count in 21 exposures. Beam width unavailable.</p>",
                        width=560, height=400)
        else:
            half = result.baseline + (np.max(result.y) - result.baseline) / 2
            left, right = result.cen - result.fwhm / 2, result.cen + result.fwhm / 2
            deriv.segment(x0=[left], y0=[half], x1=[right], y1=[half],
                          color=GREEN, line_width=4, legend_label="measured FWHM")
            color = Viridis256[int((i - 1) * 255 / 17)]
            renderer = overlay.line(x, counts / counts[-3:].mean(), color=color,
                                    line_width=2, legend_label=f"{gap:.3f} mm")
            overlay.add_tools(HoverTool(renderers=[renderer], tooltips=[
                ("Gap", f"{gap:.4f} mm"), ("piezo_x", "$x{0.0} µm"),
                ("Normalized signal", "$y{0.000}"),
            ]))
        profiles.append(row(raw, deriv, visible=i == 9))
    overlay.legend.click_policy = "hide"
    overlay.legend.label_text_font_size = "8pt"
    overlay.legend.ncols = 3
    overlay.legend.location = "bottom_right"
    select = Select(title="Inspect a gap", value="9", options=options, width=300)
    select.js_on_change("value", CustomJS(args={"profiles": profiles}, code="""
        for (let i = 0; i < profiles.length; i++) {
            profiles[i].visible = (i === Number(cb_obj.value));
        }
    """))
    columns = [TableColumn(field=field, title=title, formatter=NumberFormatter(format=fmt))
               for field, title, fmt in [
                   ("ssa_gap_setpoint_mm", "SSA gap (mm)", "0.0000"),
                   ("beam_fwhm_um", "FWHM (µm)", "0.00"),
                   ("intensity_mcps", "Intensity (Mcps)", "0.00"),
                   ("relative_intensity_percent", "Intensity (%)", "0.0"),
               ]]
    table = DataTable(source=source, columns=columns, width=1120, height=560, index_position=None)
    header = Div(text="""
        <div style="background:#1A5B7D;color:white;padding:20px;border-bottom:4px solid #B2D33B">
        <h1 style="margin:0;font-weight:500">SMI · SSA gap / beam-size scan</h1>
        <p>Scan 1170758 · 15 October 2026 · 19 gaps × 21 knife-edge positions</p></div>
        <p><b>Recorded knife-edge axis: piezo_x (µm), not piezo_z.</b>
        Detector: pil2M_stats1_total · exposure: 0.5 s · energy: 16.15 keV.</p>
    """, width=1120)
    methods = Div(text="""
        <h2 style="color:#105C78;font-weight:500">How to read these results</h2>
        <p><b>Beam size:</b> model-free FWHM of Δcounts/Δx at interval midpoints,
        using <code>smi_plans.analysis.analyze_xy(der=True, model='none', smooth=False)</code>.
        Half maximum is relative to pf's estimated derivative baseline. The asymmetric
        profiles have broad tails; this measures the central beam width, not its full support.
        No Gaussian shape or resolution deconvolution is imposed. The 2 µm step limits
        width precision, especially for the narrowest beams. No fit-error bars are implied.</p>
        <p><b>Intensity:</b> mean of the last three, most-open knife-edge positions
        (−14682, −14680, −14678 µm), divided by the recorded 0.5 s exposure.
        This is a finite-open-edge detector count rate, not calibrated incident photon flux.
        Tails may extend beyond the scan window; the blocked end is not treated as a dark
        background. No monitor or attenuation correction is applied (recorded attenuation
        factor ≈538.27, 240 µm Sn). Percent intensity is relative to the 0.20 mm gap.</p>
        <p><b>Closed gap:</b> one count across 21 frames; beam width is omitted.
        Gap coordinates use commanded values to avoid splitting sweeps on readback jitter.
        Hover for values; drag/scroll to zoom; click overlay legend entries to hide curves.
        The individual derivatives use the same Bokeh figure builder as pf.</p>
        <p><a href="summary.csv">Summary CSV</a> · <a href="scalar_data.csv">Scalar data CSV</a>
        · <a href="metadata.json">Scan metadata</a></p>
    """, width=1120)
    tabs = Tabs(tabs=[
        TabPanel(title="Overview", child=column(row(width, intensity), overlay)),
        TabPanel(title="Individual knife edges / pf", child=column(select, *profiles)),
        TabPanel(title="Numerical results", child=table),
    ])
    layout = column(header, tabs, methods)
    html = file_html(layout, INLINE, "SMI scan 1170758 — beam size and intensity vs SSA gap")
    html = html.replace("</head>", "<style>body{font-family:Arial,sans-serif;color:#494B4D;"
                        "max-width:1160px;margin:24px auto;background:white}"
                        "a{color:#105C78}h2{font-size:20px}</style></head>")
    target = OUT / "scan_1170758_beam_size_intensity.html"
    target.write_text(html)
    print(summary.to_string(index=False))
    print(f"\nReport: {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cached", action="store_true")
    args = parser.parse_args()
    data, metadata = load_data(args.cached)
    summary, results, sweeps = analyze(data, metadata)
    build_report(summary, results, sweeps, metadata)

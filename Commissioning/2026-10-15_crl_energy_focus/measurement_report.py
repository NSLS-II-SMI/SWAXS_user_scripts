"""Read-only Tiled export and offline analysis of the October CRL measurements.

Run from smi-plans with .pixi/envs/default/bin/python; --fetch downloads missing
scalar/configuration cache entries. No profile startup or hardware devices are imported.
"""

import argparse
import importlib.util
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, root
from scipy.special import erf
from zoneinfo import ZoneInfo

from smi_plans.analysis import analyze_xy

HERE = Path(__file__).resolve().parent
CACHE = HERE / "measurement_cache"
REFERENCE = "b73577b8-1712-4f89-9279-5cee108e184c"
COMPLETE = (1170759, 1170763, 1170765, 1170769)


def edge_model(x, background, amplitude, center, sigma):
    return background + amplitude * (1 + erf((x - center) / (np.sqrt(2) * sigma))) / 2


def characterize(x, y):
    """Independent sampled derivative and Gaussian cumulative-edge diagnostics."""
    order = np.argsort(x)
    x, y = np.asarray(x)[order], np.asarray(y)[order]
    dx = np.diff(x)
    result = {"derivative_fwhm_um": np.nan, "erf_fwhm_um": np.nan,
              "fit_center_um": np.nan, "fit_nrmse": np.nan,
              "fit_coverage": False, "derivative_coverage": False}
    if len(x) < 5 or np.any(dx <= 0) or np.ptp(y) <= 0:
        return result
    deriv = np.diff(y) / dx
    result["largest_downstep_fraction"] = float(max(0, -np.diff(y).min()) / np.ptp(y))
    try:
        r = analyze_xy((x[1:] + x[:-1]) / 2, deriv,
                       yerr=np.sqrt(np.maximum(y[1:], 1) + np.maximum(y[:-1], 1)) / dx,
                       model="none", profile="peak", x_sigma=0)
        half = r.baseline + (max(r.y) - r.baseline) / 2
        covered = r.y[0] < half and r.y[-1] < half and np.isfinite(r.fwhm)
        result.update(derivative_fwhm_um=float(r.fwhm) if covered else np.nan,
                      derivative_coverage=bool(covered))
    except (ValueError, RuntimeError):
        pass
    # Normalize to avoid badly conditioned fits at count levels spanning many decades.
    scale = np.ptp(y)
    yn = (y - y.min()) / scale
    x0 = np.mean(x)
    try:
        fit, _ = curve_fit(edge_model, x - x0, yn,
                           p0=[0, 1, x[np.argmin(abs(yn - 0.5))] - x0, 10],
                           bounds=([-2, 0, x.min()-x0, 0.2],
                                   [2, 5, x.max()-x0, np.ptp(x)*2]), maxfev=10000)
        b, a, c, sigma = fit
        covered = x.min() - x0 < c - 2*sigma and x.max() - x0 > c + 2*sigma
        result.update(erf_fwhm_um=2.354820045*sigma, fit_center_um=c+x0,
                      fit_nrmse=float(np.sqrt(np.mean((yn-edge_model(x-x0, *fit))**2))/a),
                      fit_coverage=bool(covered), fit_background=b*scale+y.min(),
                      fit_amplitude=a*scale)
    except (ValueError, RuntimeError):
        pass
    return result


def optics_model():
    source = HERE.parents[2] / "profile_collection/src/smi_beamline/devices/crl_optics.py"
    spec = importlib.util.spec_from_file_location("crl_report_optics", source)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze():
    manifest = pd.read_csv(CACHE / "manifest.csv")
    rows = []
    for item in manifest.to_dict("records"):
        scan = item["scan_id"]
        if item["scan_name"] == "crl_energy_focus_coarse":
            continue
        data = pd.read_csv(CACHE / f"{scan}_primary.csv")
        meta = json.loads((CACHE / f"{scan}_metadata.json").read_text())
        baseline = pd.read_csv(CACHE / f"{scan}_baseline.csv")
        exposure = np.asarray(meta["config"]["pil2M"]["pil2M_cam_acquire_time"]).ravel()[0]
        for energy, group in data.groupby("energy_energy_setpoint", sort=True):
            s = group.sort_values("piezo_x")
            r = characterize(s.piezo_x.to_numpy(), s.pil2M_stats1_total.to_numpy())
            rows.append(dict(scan_id=scan, holder=item["holder"], energy_keV=energy/1000,
                             z_mm=baseline.crl_z.mean(), points=len(s),
                             row_complete=len(s) == meta["start"]["shape"][-1],
                             exposure_s=exposure, harmonic=s.energy_harmonic.iloc[0],
                             energy_error_eV=float(abs(s.energy_energy-energy).max()),
                             open_counts=s.pil2M_stats1_total.iloc[-3:].mean(),
                             closed_counts=s.pil2M_stats1_total.iloc[:3].mean(),
                             attenuation=s.get("attenuation_attenuation_factor", pd.Series([np.nan])).mean(),
                             x_min=s.piezo_x.min(), x_max=s.piezo_x.max(), **r))
        print(f"\nSCAN {scan}, h{item['holder']} z={baseline.crl_z.mean():.4f}, "
              f"SSA={baseline.ssa_hg.tolist()}/{baseline.ssa_vg.tolist()}, "
              f"piezo y/z={baseline.piezo_y.tolist()}/{baseline.piezo_z.tolist()}")
    results = pd.DataFrame(rows)
    results.to_csv(HERE / "measurement_edges.csv", index=False)
    return results


def comparisons(results):
    optics = optics_model()
    model = optics.CRLModel()
    records = []
    for scan, energy in ((1170759, 16.2), (1170765, 8.77), (1170763, 6.325)):
        s = results[(results.scan_id == scan) & np.isclose(results.energy_keV, energy)].iloc[0]
        holder, z = int(s.holder), float(s.z_mm)
        power = model.power_per_m(energy, [holder])
        r = {"scan_id": scan, "holder": holder, "z_mm": z,
             "sampled_core_energy_keV": energy, "derivative_fwhm_um": s.derivative_fwhm_um,
             "geometry_evidence": "conditional: core only" if holder == 5 else "primary",
             "inferred_d0_SSA_mm": z+1000/(power-1/(10.5+z/1000)),
             "inferred_d0_collimated_mm": z+1000/power,
             "power_scale_at_1600_SSA": model.geometry.required_power_per_m(z)/power}
        for d, c, label in ((1600, 1/10.5, "1600_SSA"), (1350, 1/10.5, "1350_SSA"),
                            (1600, 0, "1600_collimated"), (1350, 0, "1350_collimated")):
            geometry = optics.CRLGeometry(sample_distance_mm=d, incident_curvature_per_m=c)
            r[f"predicted_{label}_keV"] = 10*math.sqrt(
                model.power_per_m(10, [holder])/geometry.required_power_per_m(z))
        # Adjacent sampled energies are a resolution bracket, NOT a confidence interval.
        es = results[results.scan_id == scan].energy_keV.to_numpy()
        k = np.argmin(abs(es-energy))
        for e, label in ((es[k-1], "low"), (es[k+1], "high")):
            r[f"adjacent_{label}_energy_keV"] = e
            r[f"adjacent_{label}_d0_SSA_mm"] = z + 1000/(
                model.power_per_m(e, [holder])-1/(10.5+z/1000))
        records.append(r)
    frame = pd.DataFrame(records)
    frame.to_csv(HERE / "measurement_geometry.csv", index=False)
    # Two reliable holders at two Z positions: illustrate the distance/curvature
    # ambiguity, not a calibrated geometry fit (zero degrees of freedom).
    degeneracy = []
    for e3 in (16.15, 16.2, 16.25):
        for e4 in (8.7, 8.77, 8.84):
            p3, p4 = model.power_per_m(e3, [3]), model.power_per_m(e4, [4])
            def residual(t, p3=p3, p4=p4):
                d, c = t
                return [1/d+c-p4, 1/(d-0.2)+c/(1+0.2*c)-p3]
            fit = root(residual, [1.4, 0])
            if not fit.success:
                raise RuntimeError("distance/curvature illustration did not converge")
            degeneracy.append({"h3_energy_keV": e3, "h4_energy_keV": e4,
                               "d0_mm": 1000*fit.x[0], "curvature_per_m": fit.x[1]})
    pd.DataFrame(degeneracy).to_csv(HERE / "measurement_geometry_degeneracy.csv", index=False)
    print(frame.round(4).to_string(index=False))
    return frame


def acquisition_table():
    rows = []
    manifest = pd.read_csv(CACHE / "manifest.csv")
    for item in manifest.to_dict("records"):
        scan = item["scan_id"]
        data = pd.read_csv(CACHE / f"{scan}_primary.csv")
        base = pd.read_csv(CACHE / f"{scan}_baseline.csv")
        meta = json.loads((CACHE / f"{scan}_metadata.json").read_text())
        config = meta["config"]["pil2M"]
        rows.append({**item,
                     "local_start": datetime.fromtimestamp(item["time"], ZoneInfo("America/New_York")).isoformat(),
                     "duration_min": (meta["stop"]["time"]-item["time"])/60,
                     "z_mm": base.crl_z.mean(), "crl_x_mm": base.crl_x.mean(),
                     "crl_y_mm": base.crl_y.mean(),
                     "lens_in_mm": base[f"crl_lens{item['holder']}"].mean(),
                     "crl_ph": base.crl_ph.mean(), "crl_th": base.crl_th.mean(),
                     "ssa_hg_mm": base.ssa_hg.mean(), "ssa_vg_mm": base.ssa_vg.mean(),
                     "exposure_s": np.asarray(config["pil2M_cam_acquire_time"]).ravel()[0],
                     "energy_min_keV": data.energy_energy_setpoint.min()/1000,
                     "energy_max_keV": data.energy_energy_setpoint.max()/1000,
                     "harmonics": ",".join(map(str, sorted(data.energy_harmonic.unique()))),
                     "attenuation_description": meta["start"]["beamline_attenuators"]["description"],
                     "sensitivity_readbacks_present": "pil2M_energy_read" in data,
                     "exit_reason": meta["stop"].get("reason", "")})
    table = pd.DataFrame(rows)
    table.to_csv(HERE / "measurement_runs.csv", index=False)
    return table


def interactive_report(results, geometry, runs):
    from bokeh.core.validation import check_integrity
    from bokeh.embed import file_html
    from bokeh.layouts import column, row
    from bokeh.models import (
        ColumnDataSource,
        CustomJS,
        Div,
        HoverTool,
        Select,
        Span,
        TabPanel,
        Tabs,
    )
    from bokeh.plotting import figure
    from bokeh.resources import INLINE

    plots, inspectors = [], []
    colors = ("#105C78", "#769E2D", "#B24700", "#5B2C83")
    for scan, color in zip(COMPLETE, colors):
        s = results[results.scan_id == scan].copy()
        holder = int(s.holder.iloc[0])
        src = ColumnDataSource(s)
        p = figure(width=560, height=350, title=f"{scan} · holder {holder} · z={s.z_mm.iloc[0]:.0f} mm",
                   x_axis_label="Energy (keV)", y_axis_label="Apparent width (µm)",
                   tools="pan,wheel_zoom,box_zoom,reset,save", background_fill_color="#F2F5F7")
        p.line("energy_keV", "derivative_fwhm_um", source=src, color=color, legend_label="Sampled derivative")
        dots = p.scatter("energy_keV", "derivative_fwhm_um", source=src, color=color, size=7)
        p.line("energy_keV", "erf_fwhm_um", source=src, color="#858889", line_dash="dashed",
               legend_label="Whole-edge Gaussian fit (diagnostic)")
        p.add_tools(HoverTool(renderers=[dots], tooltips=[("Energy", "@energy_keV{0.0000}"),
            ("Derivative FWHM", "@derivative_fwhm_um{0.00}"), ("Fit FWHM", "@erf_fwhm_um{0.00}"),
            ("Fit covers ±2σ?", "@fit_coverage"), ("Largest down-step / span", "@largest_downstep_fraction{0.000}")]))
        model = optics_model().CRLModel()
        prediction = 10*math.sqrt(model.power_per_m(10, [holder])/model.geometry.required_power_per_m(s.z_mm.iloc[0]))
        p.add_layout(Span(location=prediction, dimension="height", line_color="#105C78", line_dash="dotted"))
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        plots.append(p)

    for scan in results.scan_id.unique():
        data = pd.read_csv(CACHE / f"{scan}_primary.csv")
        panels, options = [], []
        for i, (energy, s) in enumerate(data.groupby("energy_energy_setpoint")):
            s = s.sort_values("piezo_x")
            x, y = s.piezo_x.to_numpy(), s.pil2M_stats1_total.to_numpy()
            r = results[(results.scan_id == scan) & np.isclose(results.energy_keV, energy/1000)].iloc[0]
            p = figure(width=560, height=330, title=f"{scan} · {energy/1000:.4f} keV · {len(x)} points",
                       x_axis_label="piezo_x (µm)", y_axis_label="Recorded counts / frame")
            p.line(x, y, color="#105C78")
            p.scatter(x, y, size=4, color="#105C78")
            if np.isfinite(r.erf_fwhm_um):
                xf = np.linspace(x.min(), x.max(), 300)
                yf = edge_model(xf, r.fit_background, r.fit_amplitude, r.fit_center_um, r.erf_fwhm_um/2.354820045)
                p.line(xf, yf, color="#858889", line_dash="dashed")
            d = figure(width=560, height=330, title="Unsmoothed positive derivative (no polarity flipping)",
                       x_axis_label="piezo_x (µm)", y_axis_label="d(counts)/dx")
            d.line((x[1:]+x[:-1])/2, np.diff(y)/np.diff(x), color="#769E2D")
            panels.append(row(p, d, visible=i == 0))
            options.append((str(i), f"{energy/1000:.4f} keV"))
        select = Select(title="Inspect energy", value="0", options=options, width=300)
        select.js_on_change("value", CustomJS(args={"panels": panels}, code=
            "panels.forEach((p,i) => {p.visible = i === Number(cb_obj.value);});"))
        inspectors.append(TabPanel(title=str(scan), child=column(select, *panels)))

    rate = figure(width=560, height=350, y_axis_type="log", x_axis_label="Energy (keV)",
                  y_axis_label="Final-three-position counts / second", title="Finite-window count rates (not flux)")
    center = figure(width=560, height=350, x_axis_label="Energy (keV)", y_axis_label="Fitted edge-center shift (µm)",
                    title="Whole-edge fit center relative to first energy")
    for scan, color in zip(COMPLETE, colors):
        s = results[results.scan_id == scan]
        rate.line(s.energy_keV, s.open_counts/s.exposure_s, color=color, legend_label=str(scan))
        center.line(s.energy_keV, s.fit_center_um-s.fit_center_um.iloc[0], color=color, legend_label=str(scan))
    header = Div(width=1120, text="""
      <div style="background:#1A5B7D;color:white;padding:20px;border-bottom:4px solid #B2D33B">
      <h1>SMI · CRL commissioning measurements</h1><p>15–16 October 2026 · four complete energy scans</p></div>
      <p><b>Demonstrated:</b> holder 4: 4.70 µm at 8.77 keV; holder 3 at z=+200: 5.39 µm at 16.20 keV.
      These support an approximately 1.6 m geometry <b>conditional on the SSA-source and nominal-lens model</b>.</p>
      <p>The operator adjusted <b>mirror bending voltages</b> for maximum flux through the
      <b>30 × 49.9 µm SSA aperture</b>, bringing the upstream focus near the SSA.
      This supports the SSA as the effective secondary source and makes the SSA-based geometry
      the primary interpretation; collimated calculations are sensitivity checks only.</p>
      <p><b>Holder 5:</b> narrow core around 6.3 keV on a broad pedestal; the 1.65 µm automatic minimum
      at 6.1625 keV is an intensity-drop artifact. <b>Holder 2:</b> no defensible best focus from this scan.</p>
      <p>All plotted widths are diagnostics, not automatically accepted measurements. Dashed curves are whole-edge
      Gaussian fits; dotted vertical lines mark the 1600 mm/SSA prediction. Read the interpretation and limitations
      in <a href="MEASUREMENT_REPORT.md">MEASUREMENT_REPORT.md</a>.</p>
    """)
    selected = runs[["scan_id", "holder", "local_start", "expected_points", "actual_points", "exit_status",
                     "energy_min_keV", "energy_max_keV", "harmonics", "attenuation_description"]]
    tables = column(Div(text="<h2>Run inventory (actual points take precedence over success status)</h2>"),
                    Div(text=selected.to_html(index=False), width=1120),
                    Div(text="<h2>Conditional thin-lens comparisons</h2>"),
                    Div(text=geometry.round(4).to_html(index=False), width=1120))
    from markdown_it import MarkdownIt
    interpretation = MarkdownIt("commonmark").enable("table").render(
        (HERE / "MEASUREMENT_REPORT.md").read_text())
    tabs = Tabs(tabs=[TabPanel(title="Interpretation", child=Div(text=interpretation, width=1120)),
                      TabPanel(title="Focus overview", child=column(row(*plots[:2]), row(*plots[2:]))),
                      TabPanel(title="Raw edges / derivatives", child=Tabs(tabs=inspectors)),
                      TabPanel(title="Counts / edge motion", child=row(rate, center)),
                      TabPanel(title="Provenance / models", child=tables)])
    layout = column(header, tabs)
    validation = check_integrity(layout.references())
    if validation.error:
        raise RuntimeError(f"Invalid Bokeh report: {validation.error}")
    html = file_html(layout, INLINE, "SMI CRL measurements · October 2026")
    html = html.replace("</head>", "<style>body{font-family:Roboto,Arial,sans-serif;color:#494B4D;}"
                        "a{color:#105C78;}th{background:#F2F5F7;}td,th{padding:5px;}"
                        "h1{font-weight:600;}h2{font-weight:500;}img{max-width:100%;}</style></head>")
    (HERE / "measurement_report.html").write_text(html)


def diagnostic_plots():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for scan in COMPLETE:
        data = pd.read_csv(CACHE / f"{scan}_primary.csv")
        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        for i, (energy, s) in enumerate(data.groupby("energy_energy_setpoint")):
            s = s.sort_values("piezo_x")
            x, y = s.piezo_x.to_numpy(), s.pil2M_stats1_total.to_numpy()
            color = plt.cm.viridis(i / 20)
            yn = (y-y[:3].mean()) / max(y[-3:].mean()-y[:3].mean(), 1)
            axes[0, 0].plot(x, yn, color=color, label=f"{energy/1000:.3f}")
            axes[0, 1].plot((x[1:]+x[:-1])/2, np.diff(yn)/np.diff(x), color=color)
            axes[1, 0].plot(x, y, color=color)
            axes[1, 1].plot(x, y, color=color)
        axes[1, 1].set_yscale("log")
        for ax, title in zip(axes.flat, ("Endpoint-normalized edges", "Derivative (normalized)",
                                        "Raw counts", "Raw counts (log)")):
            ax.set_title(title)
            ax.set_xlabel("piezo_x (µm)")
        axes[0, 0].legend(fontsize=6, ncol=3)
        fig.suptitle(f"CRL scan {scan}")
        fig.tight_layout()
        fig.savefig(HERE / f"diagnostic_{scan}.png", dpi=140)
        plt.close(fig)


def fetch(profile="smi"):
    from tiled.client import from_profile
    from tiled.queries import Key

    root = from_profile(profile)
    cat = root["smi"]["raw"]
    runs = {REFERENCE: cat[REFERENCE]}
    for name in ("crl_energy_focus_commissioning", "crl_energy_focus_coarse"):
        for uid, run in cat.search(Key("scan_name") == name).items():
            if 1792022400 <= run.metadata["start"]["time"] < 1792281600:
                runs[uid] = run
    CACHE.mkdir(exist_ok=True)
    manifest = []
    for uid, run in sorted(runs.items(), key=lambda kv: kv[1].metadata["start"]["time"]):
        start, stop = dict(run.metadata["start"]), dict(run.metadata.get("stop") or {})
        scan = start["scan_id"]
        if (CACHE / f"{scan}_metadata.json").exists():
            meta = json.loads((CACHE / f"{scan}_metadata.json").read_text())
            data = pd.read_csv(CACHE / f"{scan}_primary.csv")
            manifest.append({"scan_id": scan, "uid": uid,
                             "scan_name": start.get("scan_name", "reference"),
                             "holder": start.get("crl_holders", [3])[0],
                             "expected_points": start["num_points"], "actual_points": len(data),
                             "exit_status": stop.get("exit_status", "missing"), "time": start["time"]})
            print(f"using cache {scan}", flush=True)
            continue
        primary = run["primary"]["data"]
        # Image arrays are deliberately not downloaded for this scalar edge analysis.
        fields = [k for k in primary if k != "pil2M_image"]
        data = primary.read(variables=fields).to_dataframe().reset_index(drop=True)
        data.to_csv(CACHE / f"{scan}_primary.csv", index=False)
        baseline = run["baseline"]["data"].read().to_dataframe().reset_index(drop=True)
        baseline.to_csv(CACHE / f"{scan}_baseline.csv", index=False)
        config = {}
        for device in ("pil2M", "energy", "attenuation"):
            if device in run["primary"]["config"]:
                wanted = {"pil2M_cam_acquire_time", "pil2M_cam_num_images",
                          "pil2M_cam_num_exposures", "energy_locked_harmonic",
                          "energy_target_harmonic", "attenuation_select_mode"}
                config[device] = {
                    k: np.asarray(v.read()).tolist()
                    for k, v in run["primary"]["config"][device].items()
                    if k in wanted
                }
        # Retain acquisition provenance without the verbose device reprs.
        start = {k: v for k, v in start.items() if k not in ("plan_args", "plan_pattern_args")}
        meta = {"uid": uid, "start": start, "stop": stop, "config": config,
                "primary_fields": fields}
        (CACHE / f"{scan}_metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
        item = {"scan_id": scan, "uid": uid, "scan_name": start.get("scan_name", "reference"),
                "holder": start.get("crl_holders", [3])[0],
                "expected_points": start["num_points"], "actual_points": len(data),
                "exit_status": stop.get("exit_status", "missing"),
                "time": start["time"]}
        manifest.append(item)
        print(item, flush=True)
    pd.DataFrame(manifest).to_csv(CACHE / "manifest.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--profile", default="smi")
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch(args.profile)
    if args.plots:
        diagnostic_plots()
    else:
        results = analyze()
        geometry = comparisons(results)
        runs = acquisition_table()
        interactive_report(results, geometry, runs)

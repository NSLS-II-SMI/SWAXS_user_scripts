"""Build the illustrated CRL report offline from measurement_report.py's CSVs.

Requires numpy, pandas and matplotlib. Run with the workstation Python:
    python make_measurement_pdf.py
Optional --preview-dir writes page PNGs for layout review.
"""

import argparse
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
BLUE, BAND, GREEN = "#105C78", "#1A5B7D", "#769E2D"
LIME, GRAY, TEXT, TINT = "#B2D33B", "#858889", "#494B4D", "#F2F5F7"
ORANGE, PURPLE = "#B24700", "#5B2C83"
SCANS = [1170759, 1170765, 1170763, 1170769]
COLORS = dict(zip(SCANS, [BLUE, GREEN, ORANGE, PURPLE]))
BEST = {1170759: 16.2, 1170765: 8.77, 1170763: 6.325}
PICKS = {1170759: [16, 16.2, 16.5, 16.8], 1170765: [8.28, 8.7, 8.77, 9.12],
         1170763: [6.0325, 6.1625, 6.325, 6.585], 1170769: [11.3, 12, 12.8, 13.3]}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "text.color": TEXT,
    "axes.labelcolor": TEXT, "axes.edgecolor": "#C0C0C0", "axes.titlecolor": BLUE,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": TEXT, "ytick.color": TEXT, "axes.titlesize": 11,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "legend.frameon": False,
    "pdf.fonttype": 42, "savefig.facecolor": "white",
})


def text(fig, x, y, words, size=10, width=None, color=TEXT, weight="normal"):
    if width:
        words = "\n".join(textwrap.fill(p, width) for p in words.split("\n"))
    return fig.text(x, y, words, fontsize=size, color=color, weight=weight,
                    va="top", linespacing=1.5)


def page(number, section, title, subtitle):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patches.extend([
        Rectangle((0, .95), 1, .05, transform=fig.transFigure, color=BAND, zorder=-1),
        Rectangle((.065, .929), .87, .004, transform=fig.transFigure, color=LIME),
    ])
    text(fig, .065, .982, "NSLS-II  /  SMI", 11, color="white", weight="bold")
    fig.text(.935, .97, section.upper(), ha="right", va="center", color="white", fontsize=8)
    text(fig, .065, .905, title, 22, color=BLUE)
    text(fig, .065, .863, subtitle, 9, width=103)
    fig.text(.065, .035, "CRL COMMISSIONING  •  15–16 OCTOBER 2026", fontsize=7, color=GRAY)
    fig.text(.935, .035, f"{number:02d} / 08", fontsize=8, color=BLUE, ha="right")
    return fig


def note(fig, y, heading, body, height=.115, color=BLUE):
    fig.patches.extend([
        Rectangle((.065, y-height), .87, height, transform=fig.transFigure, color=TINT, zorder=-1),
        Rectangle((.065, y-height), .005, height, transform=fig.transFigure, color=color),
    ])
    text(fig, .087, y-.015, heading, 11, color=color, weight="bold")
    text(fig, .087, y-.043, body, 9, width=98)


def clean(ax):
    ax.grid(axis="y", color="#E5E9EB", linewidth=.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=3)


def width_plot(ax, s, scan, prediction=True):
    color = COLORS[scan]
    widths = s.derivative_fwhm_um.copy()
    if scan == 1170763:
        bad = np.isclose(s.energy_keV, 6.1625)
        widths[bad] = np.nan
        ax.scatter(s.energy_keV[bad], s.derivative_fwhm_um[bad], marker="x", s=60,
                   color=ORANGE, zorder=6, label="Intensity-dip artifact")
    if scan == 1170769:
        color = GRAY
    ax.plot(s.energy_keV, widths, "o-", color=color, markersize=3.5,
            linewidth=1.4, label="Sampled derivative FWHM")
    ax.plot(s.energy_keV, s.erf_fwhm_um, "--", color=GRAY, linewidth=1.1,
            label="Whole-edge Gaussian fit")
    if scan in BEST:
        b = s[np.isclose(s.energy_keV, BEST[scan])].iloc[0]
        ax.scatter([b.energy_keV], [b.derivative_fwhm_um], s=65, facecolor="white",
                   edgecolor=COLORS[scan], linewidth=2, zorder=7)
    if prediction:
        predicted = {1170759: 16.4262, 1170765: 8.6977, 1170763: 6.1502, 1170769: 12.3004}[scan]
        ax.axvline(predicted, color=BLUE, linestyle=":", linewidth=1, label="1600 mm / SSA model")
    ax.set(xlabel="Photon energy (keV)", ylabel="Apparent width (µm)", ylim=(0, None))
    clean(ax)


def table(fig, rect, headings, rows, widths=None, size=9):
    ax = fig.add_axes(rect)
    ax.axis("off")
    tab = ax.table(cellText=rows, colLabels=headings, cellLoc="left", colLoc="left",
                   colWidths=widths, bbox=[0, 0, 1, 1])
    tab.auto_set_font_size(False)
    tab.set_fontsize(size)
    for (r, _), cell in tab.get_celld().items():
        cell.set_edgecolor("white")
        cell.PAD = .08
        cell.set_facecolor(BAND if r == 0 else (TINT if r % 2 else "white"))
        cell.get_text().set_color("white" if r == 0 else TEXT)
        if r == 0:
            cell.get_text().set_weight("bold")
    return tab


def cover(edges, geometry):
    fig = page(1, "Measurement report", "A focus at the sample", "Four complete CRL energy sweeps · horizontal knife-edge measurements · SMI")
    text(fig, .065, .795, "Two clear foci. A geometry near 1.6 m.", 19, color=BLUE)
    text(fig, .065, .745,
         "Holders 3 and 4 produce clear, energy-bracketed narrow cores. "
         "With the deliberately focused small SSA as the secondary source, their "
         "measured best energies support the documented 1600 mm geometry.", 11, width=86)
    for x, scan, label in ((.065, 1170765, "HOLDER 4 · Z = 0"), (.515, 1170759, "HOLDER 3 · Z = +200 mm")):
        s = edges[(edges.scan_id == scan) & np.isclose(edges.energy_keV, BEST[scan])].iloc[0]
        fig.patches.append(Rectangle((x, .49), .42, .145, transform=fig.transFigure, color=TINT, zorder=-1))
        text(fig, x+.02, .618, label, 9, color=COLORS[scan], weight="bold")
        text(fig, x+.02, .583, f"{s.derivative_fwhm_um:.2f} µm", 31, color=COLORS[scan])
        text(fig, x+.02, .525, f"at {s.energy_keV:.2f} keV  |  sampled core FWHM", 9)
    table(fig, [.065, .277, .87, .17], ["MEASUREMENT", "RESULT", "INTERPRETATION"], [
        ["Holder 3 · 1170759", "16.20 keV / 5.39 µm", "Narrow core; visible wings"],
        ["Holder 4 · 1170765", "8.77 keV / 4.70 µm", "Cleanest new focus"],
        ["Holder 5 · 1170763", "6.325 keV / 6.38 µm", "Core on a broad pedestal"],
        ["Holder 2 · 1170769", "No accepted optimum", "Low counts; moving / clipped edge"],
    ], [.29, .28, .43], 8)
    d = geometry.set_index("holder")
    note(fig, .235, "The setup matters",
         "Mirror bending voltages were optimized for maximum flux through the 30 × 49.9 µm "
         "SSA aperture. This supports an upstream waist at or near the SSA. Nominal lens powers "
         f"then imply Z=0 distances of {d.loc[3, 'inferred_d0_SSA_mm']:.0f} and "
         f"{d.loc[4, 'inferred_d0_SSA_mm']:.0f} mm; their difference remains unresolved.", .13)
    text(fig, .065, .083, "Widths are sampled horizontal line-profile measurements; decimals do not imply submicron precision.", 8)
    return fig


def overview(edges):
    fig = page(2, "Focus versus energy", "The four energy sweeps", "A common analysis convention, with different levels of physical interpretability.")
    positions = [[.11, .555, .35, .225], [.60, .555, .35, .225], [.11, .235, .35, .225], [.60, .235, .35, .225]]
    for rect, scan in zip(positions, SCANS):
        s = edges[edges.scan_id == scan]
        ax = fig.add_axes(rect)
        width_plot(ax, s, scan)
        ax.set_title(f"Holder {int(s.holder.iloc[0])}  /  {scan}", loc="left", pad=12)
        ax.legend(fontsize=6.5, loc="upper left")
    note(fig, .16, "Read the curves together with the raw profiles",
         "Dashed widths are whole-edge Gaussian diagnostics, not accepted optical spot sizes. "
         "Holder 5's crossed-out minimum is an intensity artifact. All holder-2 widths are diagnostic; "
         "no best-focus energy is assigned.", .10)
    return fig


DESCRIPTIONS = {
    1170759: ("A narrow core with wings", "Holder 3 · 16 nominal R50 µm Be elements · CRL z = +200 mm",
              "5.39 µm at 16.20 keV",
              ("Neighboring widths are 5.54 and 5.61 µm at 16.15 and 16.25 keV. The whole-edge "
              "Gaussian width is 9.27 µm at the minimum, exposing broader wings. Above 16.80 keV, "
              "half-height coverage fails. Harmonic 13 changes to 15 at 16.15 keV.")),
    1170765: ("The cleanest new focus", "Holder 4 · 4 nominal R50 µm Be elements · CRL z = 0 mm",
              "4.70 µm at 8.77 keV",
              ("Widths broaden on both sides of the minimum: 5.40 µm at 8.70 and 6.69 µm at 8.84 keV. "
              "The whole-edge Gaussian width is 5.03 µm at 8.77 keV. Harmonic 7 remains fixed. "
              "This is the strongest new evidence for near-nominal lens power.")),
    1170763: ("A focused core, a broad pedestal", "Holder 5 · 2 nominal R50 µm Be elements · CRL z = 0 mm",
              "Core minimum near 6.325 keV",
              ("The core reaches 6.38 µm, but the whole-edge width there is 42.5 µm. Broad-profile "
              "widths instead bottom near 6.5–6.6 keV. At 6.1625 keV, a large intensity drop and "
              "recovery creates a false 1.65 µm derivative minimum; it is not a focus.")),
    1170769: ("An unresolved alignment", "Holder 2 · 8 nominal R50 µm Be elements · CRL z = 0 mm",
              "No defensible best-focus energy",
              ("The fitted edge center shifts by about 50 µm across the sweep. Open-side counts "
              "rise from roughly 58 to 15,300 per frame, while the high-energy tail is clipped. "
              "The automatic 34.7 µm minimum at 12.8 keV is not a reliable focus calibration.")),
}


def detail(number, scan, edges):
    title, subtitle, headline, body = DESCRIPTIONS[scan]
    fig = page(number, f"Scan {scan}", title, subtitle)
    s = edges[edges.scan_id == scan]
    data = pd.read_csv(HERE / "measurement_cache" / f"{scan}_primary.csv")
    groups = list(data.groupby("energy_energy_setpoint", sort=True))
    # A single fixed position origin is used for the whole run; no per-energy recentering.
    origin = float(np.median(data.piezo_x))
    ax = fig.add_axes([.11, .58, .35, .21])
    width_plot(ax, s, scan)
    ax.set_title("01  Focus versus energy", loc="left", pad=10)
    ax.legend(fontsize=6.1)
    heat = fig.add_axes([.60, .58, .31, .21])
    normalized = []
    for _, row in groups:
        row = row.sort_values("piezo_x")
        y = row.pil2M_stats1_total.to_numpy()
        normalized.append((y-y[:3].mean()) / (y[-3:].mean()-y[:3].mean()))
    x = groups[0][1].sort_values("piezo_x").piezo_x.to_numpy()-origin
    energies = np.array([e/1000 for e, _ in groups])
    mesh = heat.pcolormesh(x, energies, np.array(normalized), cmap="viridis", vmin=0, vmax=1,
                          shading="nearest", rasterized=True)
    heat.set(xlabel="Edge position offset (µm)", ylabel="Energy (keV)")
    heat.set_title("02  Every measured edge", loc="left", pad=10)
    cbax = fig.add_axes([.925, .58, .012, .21])
    fig.colorbar(mesh, cax=cbax, ticks=[0, .5, 1])
    cbax.tick_params(labelsize=6, length=2)
    raw = fig.add_axes([.11, .275, .35, .21])
    deriv = fig.add_axes([.60, .275, .35, .21])
    norm = Normalize(energies.min(), energies.max())
    for requested in PICKS[scan]:
        e, row = min(groups, key=lambda v: abs(v[0]/1000-requested))
        row = row.sort_values("piezo_x")
        x, y = row.piezo_x.to_numpy()-origin, row.pil2M_stats1_total.to_numpy()
        color = plt.cm.viridis(norm(e/1000))
        raw.plot(x, y, ".-", color=color, linewidth=1, markersize=2.5, label=f"{e/1000:g} keV")
        yn = (y-y[:3].mean())/(y[-3:].mean()-y[:3].mean())
        deriv.plot((x[1:]+x[:-1])/2, np.diff(yn)/np.diff(x), color=color, linewidth=1.2)
    raw.set(xlabel="Edge position offset (µm)", ylabel="Recorded counts / 0.5 s frame")
    raw.set_title("03  Selected raw profiles", loc="left", pad=12)
    raw.legend(fontsize=6.8, ncol=2, loc="upper left")
    if scan == 1170769:
        raw.set_yscale("log")
        raw.set_ylabel("Recorded counts / frame (log)")
    else:
        raw.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
    deriv.set(xlabel="Edge position offset (µm)", ylabel="Normalized derivative (µm⁻¹)")
    deriv.set_title("04  Profile shape / derivative", loc="left", pad=12)
    deriv.axhline(0, color=GRAY, linewidth=.6)
    for a in (raw, deriv):
        clean(a)
    text(fig, .065, .225,
         f"Position origin: {origin:.2f} µm (fixed for this run). Map and derivatives use endpoint normalization;\n"
         "0 and 1 denote the first/last three-point means, not proven closed/open plateaus. Map color clips at 0–1.",
         7.4)
    note(fig, .17, headline, body, .115, COLORS[scan])
    return fig


def geometry_page(geometry):
    fig = page(7, "Optical interpretation", "What the focus says about distance", "Primary model: nominal two-sided Be lens power, with the effective secondary source at the SSA.")
    ax = fig.add_axes([.12, .61, .79, .16])
    ax.set(xlim=(-.7, 12.8), ylim=(-1, 1))
    ax.axis("off")
    for x, label in ((0, "SSA\n30 × 49.9 µm"), (10.5, "CRL\nz = 0"), (12.1, "Knife edge\nsample plane")):
        ax.plot([x, x], [-.23, .23], color=BLUE, lw=3)
        ax.text(x, .4, label, ha="center", fontsize=9, color=BLUE)
    ax.plot([0, 10.5, 12.1], [0, .23, 0], color=GREEN, lw=1.3)
    ax.plot([0, 10.5, 12.1], [0, -.23, 0], color=GREEN, lw=1.3)
    for a, b, label in ((0, 10.5, "p₀ = 10.5 m"), (10.5, 12.1, "d₀ ≈ 1.6 m")):
        ax.annotate("", (a, -.55), (b, -.55), arrowprops={"arrowstyle": "<->", "color": GRAY})
        ax.text((a+b)/2, -.82, label, ha="center", fontsize=9)
    text(fig, .065, .817, "Mirror bending optimized for transmission through the small SSA", 11, color=BLUE, weight="bold")
    rows = []
    for holder, label in ((3, "3 / +200 mm"), (4, "4 / 0 mm")):
        r = geometry[geometry.holder == holder].iloc[0]
        rows.append([label, f"{r.sampled_core_energy_keV:.2f} keV",
                     f"{r.predicted_1600_SSA_keV:.3f} keV", f"{r.predicted_1350_SSA_keV:.3f} keV"])
    table(fig, [.065, .44, .87, .13], ["HOLDER / Z", "MEASURED", "1600 mm + SSA", "1350 mm + SSA"],
          rows, [.23, .24, .27, .26], 8.5)
    text(fig, .065, .42, "Inferred Z=0 distance: 1557 mm (holder 3) versus 1631 mm (holder 4).", 9)
    text(fig, .065, .367, "Near-nominal power; not yet a precision distance calibration", 13, color=BLUE, weight="bold")
    text(fig, .065, .328,
         "At fixed 1600 mm geometry, the clean measurements imply effective lens-power scales "
         "of 0.973× nominal (holder 3) and 1.017× (holder 4). The agreement is at the few-percent "
         "level, but the holder-to-holder distance discrepancy is larger than the neighboring-energy "
         "sampling brackets. Principal-plane offsets, actual radii, alignment and the width metric "
         "remain relevant.", 10, width=100)
    note(fig, .205, "The spot-size scale also makes sense",
         "Geometrically imaging a fully illuminated 30 µm horizontal SSA gives about 4.57 µm "
         "at z=0 and 3.93 µm at z=+200 mm. The measured cores lie on this few-micron scale. "
         "These aperture-image extents are not Gaussian FWHM predictions.", .105)
    text(fig, .065, .081,
         "Sensitivity only: collimated input would imply ~1.40–1.41 m. The known SSA-focusing procedure favors\n"
         "the SSA model; focus energies alone cannot independently determine distance, curvature and lens strength.", 7.7)
    return fig


def methods():
    fig = page(8, "Methods & provenance", "A measurement record you can revisit", "Tiled smi/raw · scalar counts and motor positions · acquisition configuration and baseline snapshots")
    text(fig, .065, .805, "Acquisition", 13, color=BLUE, weight="bold")
    text(fig, .065, .771,
         "All four complete scans: 21 energies, 0.5 s exposure and 2 µm edge steps. "
         "The initial scan spans 40 µm (441 frames); new scans span 120 µm (1281 frames each). "
         "SSA gaps and mirror bending settings are consistent across acquisition snapshots. "
         "CRL angles differ between holders.", 10, width=100)
    text(fig, .065, .665, "How the widths were measured", 13, color=BLUE, weight="bold")
    text(fig, .065, .632,
         "Sampled core width: unsmoothed positive first differences, then model-free derivative "
         "FWHM using smi_plans.analysis.analyze_xy. Both endpoints must be below half height. "
         "Raw-profile inspection is essential: this test alone does not reject intensity spikes, "
         "noise or multi-component beams. Dashed curves show an independent cumulative-Gaussian "
         "edge fit; they are diagnostic, not a substitute for core width.", 10, width=100)
    note(fig, .492, "Interpretation limits",
         "A 4.7 µm width spans only ~2.4 steps. These are horizontal knife-edge widths, without "
         "deconvolution or a vertical measurement. Count rates are not calibrated flux or lens "
         "transmission. Per-frame detector sensitivity readbacks are absent from the saved primary fields.", .115)
    table(fig, [.065, .23, .87, .11], ["PARTIAL RUN", "RECORDED / PLANNED", "USE IN THIS REPORT"], [
        ["1170761 · holder 5", "105 / 1281", "Attenuation / signal-loss diagnostic"],
        ["1170767 · holder 2", "1037 / 1281", "Failed pitch recovery; corroborating data"],
        ["1170771 · holder 3", "53 / 1281", "Incomplete first edge; no focus minimum"],
    ], [.28, .27, .45], 7.5)
    text(fig, .065, .197, "Reproducibility & next step", 12, color=BLUE, weight="bold")
    text(fig, .065, .166,
         "Companions: MEASUREMENT_REPORT.md, measurement_report.html, measurement_edges.csv, "
         "measurement_geometry.csv and measurement_runs.csv. The measurement_cache folder preserves "
         "scalar data and full run UIDs for 13 runs, including six coarse scans. This PDF is generated "
         "offline by make_measurement_pdf.py; it does not access hardware. Next: repeat clean holder 4 "
         "at several Z positions under the same small-SSA illumination to refine the geometry.", 9, width=98)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-dir", type=Path)
    args = parser.parse_args()
    if args.preview_dir and not args.preview_dir.is_dir():
        parser.error("--preview-dir must already exist")
    edges = pd.read_csv(HERE / "measurement_edges.csv")
    geometry = pd.read_csv(HERE / "measurement_geometry.csv")
    runs = pd.read_csv(HERE / "measurement_runs.csv")
    for scan in SCANS:
        run = runs[runs.scan_id == scan].iloc[0]
        assert run.actual_points == run.expected_points
        assert len(edges[edges.scan_id == scan]) == 21
    target = HERE / "CRL_measurement_report_2026-10-16.pdf"
    pages = [cover(edges, geometry), overview(edges)]
    pages.extend(detail(i, scan, edges) for i, scan in enumerate(SCANS, 3))
    pages.extend([geometry_page(geometry), methods()])
    with PdfPages(target, metadata={"Title": "SMI CRL commissioning — focus measurements",
                                   "Author": "NSLS-II SMI",
                                   "Subject": "15–16 October 2026; four complete energy-focus sweeps",
                                   "Keywords": "CRL, SMI, knife edge, SSA, focus, commissioning"}) as pdf:
        for number, fig in enumerate(pages, 1):
            pdf.savefig(fig)
            if args.preview_dir:
                fig.savefig(args.preview_dir / f"crl_pdf_page_{number}.png", dpi=110)
            plt.close(fig)
    print(f"Wrote {target} ({len(pages)} pages)")


if __name__ == "__main__":
    main()

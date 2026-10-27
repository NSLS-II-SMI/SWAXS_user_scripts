"""Reproducible, read-only analysis of the October 22--23 Kapton log.

No hardware imports. Preview by default; --apply creates report artifacts.
Requires numpy and matplotlib; optional pymupdf for independent PDF inspection.
SPDX-License-Identifier: BSD-3-Clause
"""

import argparse
import csv
import hashlib
import json
import logging
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

TZ = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "logs/kapton_air_holder_01_bpm2_bpm3_waxs_oav.sqlite"
NAVY, TEAL, ORANGE, RED, GRAY = "#12334B", "#008C95", "#DA8731", "#BA414B", "#657584"
log = logging.getLogger(__name__)


def local(t, fmt="%b %d, %H:%M:%S"):
    return datetime.fromtimestamp(float(t), TZ).strftime(fmt)


def duration(seconds):
    seconds = round(seconds)
    return f"{seconds // 3600} h {(seconds % 3600) // 60:02d} min {seconds % 60:02d} s"


def load(database):
    """Immutable reader: never creates/chmods source WAL/SHM. Require checkpointed source."""
    wal = Path(str(database) + "-wal")
    if wal.exists() and wal.stat().st_size:
        raise RuntimeError("Database has an active WAL; supply a completed SQLite backup instead")
    before = database.stat()
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro&immutable=1", uri=True, timeout=2) as db:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("SQLite quick_check failed")
        identity = json.loads(db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()[0])
        samples = [json.loads(p) for p, in db.execute("SELECT payload FROM samples ORDER BY id")]
        images = [dict(json.loads(p), audit_wall=w) for w, p in db.execute("SELECT wall,payload FROM images ORDER BY id")]
        recovery = [dict(json.loads(p), audit_wall=w) for w, p in db.execute("SELECT wall,payload FROM recovery ORDER BY id")]
    after = database.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("Source changed during analysis; retry with a completed backup")
    with database.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return samples, images, recovery, identity, digest


def spans(t, condition):
    condition = np.asarray(condition, dtype=bool)
    starts = np.flatnonzero(condition & ~np.r_[False, condition[:-1]])
    stops = np.flatnonzero(condition & ~np.r_[condition[1:], False]) + 1
    return [(int(a), int(b), float(t[min(b, len(t) - 1)] - t[a])) for a, b in zip(starts, stops)]


def analyze(samples, images):
    t = np.array([s["wall"] for s in samples])
    dt = np.diff(t, prepend=t[0])
    if np.any(dt < 0):
        raise ValueError("Wall time not monotonic")
    raw = {key: np.array([s["readings"].get(key, {}).get("value", np.nan) for s in samples], float)
           for key in ("bpm", "incident_flux", "waxs_pressure", "maxs_pressure", "fast", "fe")}
    totals = {key: np.array([s["totals"][key] for s in samples]) for key in samples[-1]["totals"]}
    delta = {key: np.diff(value, prepend=value[0]) for key, value in totals.items()}
    if any(np.any(value < -1e-6) for value in delta.values()):
        raise ValueError("Counter reset detected; segment accounting is required")
    # Recover only independently supported early MINOR STATE enum intervals.
    # Earlier script versions did not record alarm status; observed diagnostic
    # metadata in the commissioning session establishes STATE for this record.
    evidence = np.array([
        s["states"]["photon"] is None
        and s["readings"]["photon"].get("value") == "Open"
        and s["readings"]["photon"].get("severity") == 1
        and s["readings"]["fe"].get("value") == 0
        and s["states"]["bpm"] is True
        and 45 <= s["readings"]["incident_flux"].get("value", -1) <= 55
        for s in samples])
    correction = np.where(evidence & np.r_[False, evidence[:-1]],
                          np.minimum(delta["fast_open_s"], delta["unknown_beam_s"]), 0)
    corrected_delta = delta["beam_s"] + correction
    corrected = totals["beam_s"] + np.cumsum(correction)
    opened = np.array([s["states"]["fast"] is True for s in samples])
    beam = np.array([s["states"]["beam"] is True for s in samples])
    final_open = np.flatnonzero(opened)[-1]
    close_idx = final_open + 1
    close_bracket = [float(t[final_open]), float(t[close_idx])]
    # Refine with the monotonic fast-open counter increment: no state transition
    # occurs between the prior open sample and the persistent closure besides close.
    close_estimate = t[final_open] + delta["fast_open_s"][close_idx]
    outage = max(spans(t, (raw["bpm"] <= 10) & opened), key=lambda x: x[2])
    trip_idx = int(np.flatnonzero((raw["waxs_pressure"] >= .05) & (t > t[final_open] - 10))[0])
    image_final = {im["image_id"]: im for im in images}
    saved = [im for im in image_final.values() if im.get("run_uid")]
    image_t = np.array([im["start"]["wall"] for im in saved])
    # Reading ending each interval weights the corresponding beam-time increment.
    flux_valid = np.array([s.get("incident_flux_fresh", False) for s in samples])
    weights = np.where(flux_valid & np.isfinite(raw["incident_flux"]), corrected_delta, 0)
    flux_mean = np.average(np.nan_to_num(raw["incident_flux"]), weights=weights)
    flux_sd = np.sqrt(np.average((np.nan_to_num(raw["incident_flux"]) - flux_mean) ** 2, weights=weights))
    flux_integral = np.sum(np.nan_to_num(raw["incident_flux"]) * weights)
    active = (t >= image_t[0]) & (t <= t[final_open]) & beam
    pressure_stats = {key: {"median": float(np.median(raw[key][active])),
                            "p95": float(np.percentile(raw[key][active], 95)),
                            "max": float(np.max(raw[key][active]))}
                      for key in ("waxs_pressure", "maxs_pressure")}
    gap_indices = np.flatnonzero(dt > 3)
    # Separate the slow post-closure drift from the rapid rise after ~06:41.
    drift_start = datetime(2026, 10, 22, 23, 0, tzinfo=TZ).timestamp()
    drift_stop = datetime(2026, 10, 23, 6, 30, tzinfo=TZ).timestamp()
    drift_mask = (t >= drift_start) & (t < drift_stop)
    drift = {}
    bin_id = ((t[drift_mask]-drift_start)//300).astype(int)
    for key in ("waxs_pressure", "maxs_pressure"):
        medians = np.array([np.median(raw[key][drift_mask][bin_id == i]) for i in np.unique(bin_id)])
        hours = np.array([np.mean(t[drift_mask][bin_id == i])-drift_start for i in np.unique(bin_id)])/3600
        slope, intercept = np.polyfit(hours, medians, 1)
        initial = float(np.median(raw[key][(t >= drift_start) & (t < drift_start+900)]))
        final = float(np.median(raw[key][(t >= drift_stop-900) & (t < drift_stop)]))
        drift[key] = {"first_15min_median_torr": initial, "last_15min_median_torr": final,
                      "change_torr": final-initial, "change_percent": 100*(final/initial-1),
                      "slope_torr_per_hour": float(slope), "intercept_torr": float(intercept)}
    summary = {
        "timezone": "America/New_York (EDT, UTC-04:00)", "samples": len(samples),
        "first_sample": local(t[0]), "last_sample": local(t[-1]),
        "final_close_first_closed_sample": local(t[close_idx]),
        "final_close_bracket_epoch": close_bracket, "final_close_estimate_epoch": float(close_estimate),
        "beam_counter_s": float(totals["beam_s"][-1]),
        "minor_alarm_correction_s": float(correction.sum()),
        "early_correction_flux_band": [45, 55],
        "best_estimate_beam_s": float(corrected[-1]),
        "fast_open_s": float(totals["fast_open_s"][-1]),
        "shutter_open_without_beam_s": float(totals["fast_open_s"][-1] - corrected[-1]),
        "unknown_beam_counter_s": float(totals["unknown_beam_s"][-1]),
        "unobserved_s": samples[-1]["unobserved_s"],
        "outage_start": local(t[outage[0]]), "outage_end": local(t[outage[1]]),
        "outage_sample_duration_s": outage[2],
        "pressure_trip_sample": local(t[trip_idx]), "pressure_trip_waxs_torr": float(raw["waxs_pressure"][trip_idx]),
        "image_attempts": len(image_final), "image_runs_returned": len(saved),
        "image_outcomes": dict(Counter(im["status"] for im in image_final.values())),
        "first_returned_image": local(image_t[0]), "last_returned_image": local(image_t[-1]),
        "median_image_spacing_s": float(np.median(np.diff(image_t))),
        "bpm3_beam_weighted_mean": float(flux_mean), "bpm3_beam_weighted_sd": float(flux_sd),
        "bpm3_beam_weighted_cv_percent": float(100 * flux_sd / flux_mean),
        "bpm3_integral_signal_seconds": float(flux_integral),
        "bpm3_weighted_coverage_s": float(weights.sum()), "pressure_beam_on_stats_torr": pressure_stats,
        "gaps_over_3s": [{"before": local(t[i-1]), "after": local(t[i]), "seconds": float(dt[i])} for i in gap_indices],
        "post_closure_drift": {"start": local(drift_start), "stop": local(drift_stop),
                               "fit": "OLS on 5-minute medians; no independent-point error bars", "pressures": drift},
    }
    return {"t": t, "raw": raw, "totals": totals, "corrected": corrected, "correction": correction,
            "corrected_delta": corrected_delta, "opened": opened, "beam": beam, "outage": outage,
            "close_idx": close_idx, "trip_idx": trip_idx, "saved": saved, "images": image_final,
            "image_t": image_t, "summary": summary}


def figure_header(page, title, subtitle, total=4):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="#FAFCFD")
    fig.text(.08, .955, "SMI  /  COMMISSIONING", color=TEAL, fontsize=10, weight="bold")
    fig.text(.08, .916, title, color=NAVY, fontsize=24, weight="bold")
    fig.text(.08, .887, subtitle, color=GRAY, fontsize=9)
    fig.text(.08, .034, "KAPTON AIR HOLDER  •  22–23 OCT 2026  •  ALL TIMES EDT", color=GRAY, fontsize=8)
    fig.text(.92, .034, f"{page:02d} / {total:02d}", ha="right", color=GRAY, fontsize=8)
    return fig


def card(fig, x, y, width, value, label, detail):
    fig.add_artist(FancyBboxPatch((x, y), width, .09, boxstyle="round,pad=0.012",
                                 facecolor="#EAF2F5", edgecolor="none", transform=fig.transFigure))
    fig.text(x+.005, y+.058, value, fontsize=17, color=NAVY, weight="bold")
    fig.text(x+.005, y+.033, label, fontsize=9, color=TEAL, weight="bold")
    fig.text(x+.005, y+.012, detail, fontsize=7.5, color=GRAY)


def style(ax, title, ylabel):
    ax.set_title(title, loc="left", fontsize=11, color=NAVY, weight="bold", pad=12)
    ax.set_ylabel(ylabel, fontsize=9, color=GRAY)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C8D3DA")
    ax.grid(axis="y", color="#DCE4E9", lw=.5)
    ax.tick_params(labelsize=8, colors=GRAY)
    ax.set_facecolor("white")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=TZ))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1, tz=TZ))


def plot_envelope(ax, t, values, *, color, label, seconds=30):
    """Minute-scale envelope preserves excursions while limiting PDF complexity."""
    bins = np.floor((t-t[0])/seconds).astype(int)
    groups = np.unique(bins)
    centers, med, lo, hi = [], [], [], []
    for group in groups:
        mask = bins == group
        v = values[mask]
        centers.append(np.mean(t[mask]))
        med.append(np.nanmedian(v))
        lo.append(np.nanmin(v))
        hi.append(np.nanmax(v))
    x = mdates.date2num([datetime.fromtimestamp(ts, TZ) for ts in centers])
    ax.fill_between(x, lo, hi, color=color, alpha=.16, linewidth=0)
    ax.plot(x, med, color=color, lw=1.25, label=label)


def report(data, identity, digest, output):
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42,
                         "axes.labelcolor": GRAY, "text.color": NAVY})
    d, s = data, data["summary"]
    t, raw = d["t"], d["raw"]
    x = mdates.date2num([datetime.fromtimestamp(ts, TZ) for ts in t])
    a, b, _ = d["outage"]
    close = d["close_idx"]
    window = t <= t[close] + 90
    outage_color = "#F8E2C5"
    cache = ROOT / "logs/image_cache"
    has_images = (cache / "manifest.json").exists() and (ROOT / "movie_scale.json").exists()
    total_pages = 5 if has_images else 4
    with PdfPages(output, metadata={"Title": "Kapton irradiation | Overnight commissioning",
                                   "Author": "SMI commissioning analysis", "Subject": "Exposure, flux, pressure and shutter audit"}) as pdf:
        fig = figure_header(1, "An evening of exposure", "Kapton atmospheric-air holder  |  6 keV  |  WAXS + on-axis imaging", total_pages)
        card(fig, .09, .765, .245, duration(s["best_estimate_beam_s"]), "BEST ESTIMATE · BEAM ON", "Includes early alarm correction")
        card(fig, .375, .765, .245, local(t[close], "%H:%M:%S"), "FINAL FAST-SHUTTER CLOSE", "22 October · first closed sample")
        card(fig, .66, .765, .245, "41 min 41 s", "BEAM INTERRUPTION", "17:49:15 → 18:30:56")
        ax = fig.add_axes([.10, .525, .82, .18])
        plot_envelope(ax, t[window], raw["incident_flux"][window], color=TEAL, label="BPM3 SumX · incident flux")
        plot_envelope(ax, t[window], raw["bpm"][window], color=NAVY, label="BPM2 SumX · gate")
        ax.axhline(10, color=GRAY, ls=":", lw=.8)
        ax.axvspan(x[a], x[b], color=outage_color, zorder=0)
        ax.axvline(x[close], color=RED, lw=1, ls="--")
        style(ax, "01  Incident beam disappeared well before 18:30", "BPM signal · native units")
        ax.legend(loc="lower right", fontsize=8, frameon=False)
        ax.set_xlim(x[0], x[close]+90/86400)
        ax = fig.add_axes([.10, .285, .82, .17])
        ax.plot(x[window][::8], d["corrected"][window][::8]/3600, color=TEAL, lw=1.8, label="Best estimate")
        ax.plot(x[window][::8], d["totals"]["beam_s"][window][::8]/3600, color=NAVY, lw=1, ls="--", label="Saved counter")
        ax.axvspan(x[a], x[b], color=outage_color, zorder=0)
        ax.scatter(mdates.date2num([datetime.fromtimestamp(v, TZ) for v in d["image_t"]]),
                   np.interp(d["image_t"], t, d["corrected"])/3600, s=6, color=ORANGE, label="Returned image run", zorder=3)
        style(ax, "02  Exposure accumulated; outage and shutter gaps excluded", "Cumulative beam time · h")
        ax.set_xlim(x[0], x[close]+90/86400)
        ax.legend(loc="upper left", fontsize=8, frameon=False)
        fig.text(.10, .220, "THE RESULT", fontsize=10, weight="bold", color=TEAL)
        fig.text(.10, .190, f"Saved counter: {duration(s['beam_counter_s'])}  •  Early correction: {s['minor_alarm_correction_s']:.1f} s", fontsize=10)
        fig.text(.10, .166, f"Fast shutter open: {duration(s['fast_open_s'])}  •  {s['image_runs_returned']} image runs returned", fontsize=10)
        fig.text(.10, .143, "Beam loss started at 17:49:15; 18:30:56 is the return, not the loss onset.\n"
                 "Both BPMs dropped while FE stayed open. This is compatible with the reported\n"
                 "upstream valve trip; no gate-valve readback was logged to identify the valve.", fontsize=9, linespacing=1.5, va="top")
        fig.text(.10, .063, "Exposure is a shutter/BPM proxy, not calibrated absorbed dose. No time after the\n"
                 "last sample or across unobserved restart gaps is added to the estimate.", fontsize=8, color=GRAY)
        pdf.savefig(fig)
        plt.close(fig)

        fig = figure_header(2, "A short spike ended the run", "Pressure evolution  |  WAXS and MAXS only  |  SAXS isolated, per operator", total_pages)
        ax = fig.add_axes([.11, .645, .80, .18])
        for key, color, label in [("waxs_pressure", TEAL, "WAXS"), ("maxs_pressure", NAVY, "MAXS")]:
            plot_envelope(ax, t[window], raw[key][window], color=color, label=label)
        ax.axhline(.05, color=RED, lw=1, ls="--", label="Ceiling 0.05 Torr")
        ax.axvline(x[close], color=RED, lw=.8)
        style(ax, "03  WAXS approached the ceiling through the evening", "Pressure · Torr")
        ax.set_xlim(x[0], x[close]+90/86400)
        ax.legend(fontsize=8, frameon=False, loc="lower right", ncol=3)
        ax = fig.add_axes([.11, .405, .80, .16])
        near = (t > t[close]-15) & (t < t[close]+15)
        ax.step(x[near], raw["waxs_pressure"][near], where="post", color=TEAL, lw=1.5, label="WAXS")
        ax.scatter(x[near], raw["waxs_pressure"][near], color=TEAL, s=12)
        ax.axhline(.05, color=RED, ls="--", lw=1)
        ax.axvspan(x[close-1], x[close], color=RED, alpha=.15, label="Closure bracket")
        style(ax, "04  0.054 Torr for one logged sample; then shutter closed", "WAXS · Torr")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=TZ))
        ax.xaxis.set_major_locator(mdates.SecondLocator(interval=5))
        ax.legend(fontsize=8, frameon=False, loc="upper left")
        ax = fig.add_axes([.11, .165, .75, .16])
        for key, color, label in [("waxs_pressure", TEAL, "WAXS"), ("maxs_pressure", NAVY, "MAXS")]:
            plot_envelope(ax, t, raw[key], color=color, label=label, seconds=60)
        ax.set_yscale("log")
        ax.axhline(.05, color=RED, ls="--", lw=.8)
        ax.axvline(x[close], color=RED, ls="--", lw=.8)
        style(ax, "05  Overnight pressure and incident flux", "Pressure · Torr (log)")
        ax.set_xlim(x[0], x[-1])
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=3, tz=TZ))
        flux_ax = ax.twinx()
        plot_envelope(flux_ax, t, raw["incident_flux"], color=ORANGE,
                      label="BPM3 SumX (right)", seconds=60)
        flux_ax.set_ylabel("BPM3 SumX · native units", fontsize=8, color=ORANGE)
        flux_ax.tick_params(axis="y", labelsize=8, colors=ORANGE)
        flux_ax.spines["top"].set_visible(False)
        flux_ax.spines["right"].set_color(ORANGE)
        flux_ax.set_ylim(-3, 60)
        lines, labels = ax.get_legend_handles_labels()
        flux_lines, flux_labels = flux_ax.get_legend_handles_labels()
        ax.legend(lines + flux_lines, labels + flux_labels, fontsize=7.5,
                  frameon=False, loc="upper left", ncol=3)
        fig.text(.11, .105, "22:57:32.284: WAXS = 0.054 Torr; MAXS = 0.045 Torr.\n"
                 "22:57:33.285: fast shutter closed; WAXS had returned to 0.049 Torr.\n"
                 "Morning pressure rise occurred with the shutter closed; cause is not established.", fontsize=9, linespacing=1.5)
        pdf.savefig(fig)
        plt.close(fig)

        fig = figure_header(3, "Statistics & the audit trail", "Measured totals, quality limits and what the image records establish", total_pages)
        rows = [
            ["Best estimate of beam-on time", duration(s["best_estimate_beam_s"])],
            ["Saved online beam counter", duration(s["beam_counter_s"])],
            ["Added early MINOR-alarm interval", f"{s['minor_alarm_correction_s']:.2f} s"],
            ["Total fast-controller-open time", duration(s["fast_open_s"])],
            ["Open shutter, no detected beam", duration(s["shutter_open_without_beam_s"])],
            ["BPM3 beam-weighted mean ± SD", f"{s['bpm3_beam_weighted_mean']:.3f} ± {s['bpm3_beam_weighted_sd']:.3f} native units"],
            ["BPM3 relative variability (weighted CV)", f"{s['bpm3_beam_weighted_cv_percent']:.2f}%"],
            ["Integrated BPM3 × beam time", f"{s['bpm3_integral_signal_seconds']:,.0f} signal·s (not photons)"],
            ["WAXS / MAXS median while acquiring beam", f"{s['pressure_beam_on_stats_torr']['waxs_pressure']['median']:.3f} / {s['pressure_beam_on_stats_torr']['maxs_pressure']['median']:.3f} Torr"],
            ["Image runs returned / attempts", f"{s['image_runs_returned']} / {s['image_attempts']}"],
            ["Median image spacing", f"{s['median_image_spacing_s']:.2f} s"],
            ["Logged samples / typical interval", f"{s['samples']:,} / ~1 s"],
            ["Unobserved restart time", f"{s['unobserved_s']:.2f} s (not credited)"],
        ]
        ax = fig.add_axes([.09, .49, .83, .36]); ax.axis("off")
        table = ax.table(cellText=rows, colWidths=[.58, .42], cellLoc="left", bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False); table.set_fontsize(8.5)
        for (r, _c), cell in table.get_celld().items():
            cell.set_facecolor("#EDF3F6" if r % 2 == 0 else "white")
            cell.set_edgecolor("white"); cell.set_text_props(color=NAVY); cell.PAD=.045
        fig.text(.10, .455, "INTERPRETATION", fontsize=10, color=TEAL, weight="bold")
        fig.text(.10, .424,
                 "• Final closure is bracketed by 22:57:32.284 and 22:57:33.285 EDT.\n"
                 f"  Counter interpolation estimates {local(s['final_close_estimate_epoch'], '%H:%M:%S.%f')[:-3]}; use ~1 s timing precision.\n"
                 "• The first WAXS threshold crossing immediately preceded closure. The sequence\n"
                 "  matches software pressure-stop behavior; no RunEngine traceback was supplied.\n"
                 "• All 62 returned image runs carry the conservative 'interrupted' flag. The\n"
                 "  detector's normal end-of-exposure shutter closure can set this flag; it is not\n"
                 "  evidence that all images are unusable. One early attempt failed.\n"
                 f"• First returned image {s['first_returned_image']}; last {s['last_returned_image']}.",
                 fontsize=9, linespacing=1.6, va="top")
        fig.text(.10, .255, "METHOD & LIMITS", fontsize=10, color=TEAL, weight="bold")
        fig.text(.10, .235,
                 "Use the final cumulative counters, never sum their per-sample values. The early\n"
                 "116 s correction uses fast-open increments with BPM3 in 45–55 (near 49),\n"
                 "FE=0, photon='Open'/MINOR and BPM2>10. This follows the operator's\n"
                 "confirmed interpretation of beam on the Kapton despite the photon alarm.\n"
                 "No downtime is recovered. Transition latency and sub-sample changes limit\n"
                 "accuracy; downstream valve position and absorbed dose were not measured.\n"
                 "BPM3 statistics weight fresh readings by corrected beam-time increments.\n"
                 "Plots show 30–60 s medians and min–max envelopes; spike panel uses raw data.\n"
                 "SAXS pressure is omitted: the branch was isolated and zero was below range.\n"
                 + ("Image counts come from returned run UIDs; before/after frames are on page 4."
                    if has_images else "Image counts come from returned run UIDs; raw frames pending."),
                 fontsize=8.0, linespacing=1.22, va="top")
        fig.text(.10, .104, "NEXT SEGMENT: leak repair; SAXS-connected operation if vacuum permits.\n"
                 "Backup: WAXS isolated, ~0.10 Torr trip. Add close-only chamber/pump isolation.",
                 fontsize=7.5, color=TEAL, linespacing=1.4, va="top")
        fig.text(.10, .075, f"Source: {DATABASE.name}\nSHA-256: {digest[:40]}…\n"
                 f"Coverage: {s['first_sample']} → {s['last_sample']} EDT · specimen {identity['specimen']}",
                 fontsize=6.9, color=GRAY, linespacing=1.3, va="top")
        pdf.savefig(fig)
        plt.close(fig)
        if has_images:
            from matplotlib.colors import LogNorm

            from tiled_images import yellowhot

            manifest = json.loads((cache / "manifest.json").read_text())
            scale = json.loads((ROOT / "movie_scale.json").read_text())
            fig = figure_header(4, "Before & after exposure", "Matched scale  |  Earliest and latest returned WAXS + OAV frames", total_pages)
            for col, meta in enumerate((manifest[0], manifest[-1])):
                frames = np.load(cache / f"{meta['uid']}.npz")
                x0 = .08 + col * .46
                fig.text(x0, .84, "BEFORE" if col == 0 else "AFTER", color=TEAL, fontsize=12, weight="bold")
                fig.text(x0, .815, meta["local_time"] + " EDT", fontsize=9)
                fig.text(x0, .792, "Beam on: " + duration(meta["corrected_beam_s"]), fontsize=9, weight="bold")
                ax = fig.add_axes([x0, .465, .38, .30])
                ax.set_axis_off()
                cmap = yellowhot()
                cmap.set_bad("black")
                im = ax.imshow(np.ma.masked_less_equal(frames["waxs"], 0), cmap=cmap,
                               norm=LogNorm(scale["vmin"], scale["vmax"], clip=True), interpolation="nearest")
                ax.set_title(f"WAXS · scan {meta['scan_id']}", fontsize=10, color=NAVY)
                ax = fig.add_axes([x0, .17, .38, .23])
                ax.set_axis_off()
                ax.imshow(frames["oav"], cmap="gray", interpolation="nearest")
                ax.set_title("On-axis view", fontsize=10, color=NAVY)
                frames.close()
            cax = fig.add_axes([.22, .432, .56, .012])
            cb = fig.colorbar(im, cax=cax, orientation="horizontal")
            cb.set_label("WAXS counts · fixed logarithmic yellow-hot scale", fontsize=8)
            cb.ax.tick_params(labelsize=7)
            fig.text(.09, .107, "'Before' means first successfully returned frame, not an unirradiated reference.\n"
                     "The final frame precedes shutter closure by about 66 seconds. Negative/zero\n"
                     "WAXS pixels are masked. Movies use this same fixed scale and annotated totals.",
                     fontsize=8.5, linespacing=1.4)
            pdf.savefig(fig)
            plt.close(fig)

        fig = figure_header(total_pages, "The slow overnight rise", "Fast shutter closed throughout  |  Linear pressure scale  |  Before the rapid morning rise", total_pages)
        begin = datetime(2026, 10, 22, 23, 0, tzinfo=TZ).timestamp()
        end = datetime(2026, 10, 23, 6, 30, tzinfo=TZ).timestamp()
        mask = (t >= begin) & (t < end)
        for i, (key, color, name) in enumerate((("waxs_pressure", TEAL, "WAXS"), ("maxs_pressure", NAVY, "MAXS"))):
            stats = s["post_closure_drift"]["pressures"][key]
            ax = fig.add_axes([.12, .60-i*.255, .76, .18])
            plot_envelope(ax, t[mask], raw[key][mask], color=color, label=f"{name} · 1-minute median / range", seconds=60)
            trend = stats["intercept_torr"] + stats["slope_torr_per_hour"]*(t[mask]-begin)/3600
            ax.plot(x[mask][::120], trend[::120], color=ORANGE, ls="--", lw=1.4, label="Linear fit to 5-minute medians")
            style(ax, f"{name}: gradual rise of {stats['slope_torr_per_hour']*1000:.3f} mTorr/hour", "Pressure · Torr")
            ax.set_ylim(np.min(raw[key][mask])-.0005, np.max(raw[key][mask])+.0005)
            ax.set_xlim(x[mask][0], x[mask][-1])
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1, tz=TZ))
            ax.legend(fontsize=8, loc="lower right", frameon=False)
        fig.text(.12, .835, "23:00 EDT, Oct 22 → 06:30 EDT, Oct 23 · 7.5 hours", fontsize=11, weight="bold")
        fig.text(.12, .285, "A SHARED UPWARD TREND, NOT CONTINUED IRRADIATION", fontsize=10, color=TEAL, weight="bold")
        lines = []
        for key, name in (("waxs_pressure", "WAXS"), ("maxs_pressure", "MAXS")):
            stats = s["post_closure_drift"]["pressures"][key]
            lines.append(f"{name}: {stats['first_15min_median_torr']:.3f} → {stats['last_15min_median_torr']:.3f} Torr "
                         f"({stats['change_torr']*1000:+.1f} mTorr, {stats['change_percent']:+.1f}%).")
        fig.text(.12, .255, "\n".join(lines) + "\nEndpoint values are the first and last 15-minute medians.",
                 fontsize=10, linespacing=1.6, va="top")
        fig.text(.12, .185,
                 "Both gauges rise in step-like increments of about 0.001 Torr. The long plateaus\n"
                 "and correlated samples do not support precise statistical error bars on a fit.\n"
                 "The fast shutter remained closed, so this interval adds no Kapton beam exposure;\n"
                 "BPM3 near 49 reports upstream flux, not beam reaching the sample.\n\n"
                 "The data establish increasing indicated pressure in both regions. They do not\n"
                 "separate changing leak/outgassing load, pumping performance, temperature or\n"
                 "gauge response. The rapid rise beginning around 06:41 is excluded from this fit.",
                 fontsize=9, linespacing=1.45, va="top")
        pdf.savefig(fig)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DATABASE)
    parser.add_argument("--output", type=Path, default=ROOT / "kapton_overnight_report_2026-10-23.pdf")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--replace-existing", action="store_true", help="Replace previously generated report artifacts")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("fontTools").setLevel(logging.WARNING)
    samples, images, recovery, identity, digest = load(args.database)
    data = analyze(samples, images)
    summary = {**data["summary"], "database_sha256": digest, "identity": identity, "recovery": recovery}
    log.info("%s", json.dumps(summary, indent=2))
    if not args.apply:
        log.info("Preview only. Use --apply to create %s and statistics/audit sidecars.", args.output)
        return
    outputs = [args.output, args.output.with_suffix(".json"), args.output.with_suffix(".csv")]
    if any(p.exists() for p in outputs) and not args.replace_existing:
        raise FileExistsError("Choose a new output name; existing reports are never overwritten")
    report(data, identity, digest, args.output)
    with outputs[1].open("w" if args.replace_existing else "x") as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
    with outputs[2].open("w" if args.replace_existing else "x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["image_id", "status", "local_start", "run_uid", "beam_s"])
        writer.writeheader()
        for image in data["images"].values():
            start = image.get("start", {})
            writer.writerow({"image_id": image["image_id"], "status": image["status"],
                             "local_start": local(start["wall"]) if start else "",
                             "run_uid": image.get("run_uid", ""),
                             "beam_s": start.get("totals", {}).get("beam_s", "")})
    log.info("Created %s", args.output)


if __name__ == "__main__":
    main()

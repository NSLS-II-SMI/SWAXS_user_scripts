"""Reproducible, read-only final commissioning report for the October 22--26 Kapton log.

No hardware or network imports. Preview by default; --apply creates PDF, JSON, and CSV artifacts.
Requires numpy and matplotlib.
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
DEFAULT_DB = ROOT / "logs/kapton_air_holder_01_bpm2_bpm3_waxs_oav_2026-10-26_snapshot.sqlite"
NAVY, TEAL, ORANGE, RED, GRAY, PURPLE = "#12334B", "#008C95", "#DA8731", "#BA414B", "#657584", "#5C4B8B"
log = logging.getLogger(__name__)


def local(t, fmt="%b %d, %H:%M:%S"):
    return datetime.fromtimestamp(float(t), TZ).strftime(fmt)


def duration(seconds):
    seconds = round(float(seconds))
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
        samples = [dict(json.loads(p), sample_id=i) for i, p in db.execute("SELECT id, payload FROM samples ORDER BY id")]
        images = [dict(json.loads(p), row_id=i, audit_wall=w) for i, w, p in db.execute("SELECT id, wall, payload FROM images ORDER BY id")]
        recovery = [dict(json.loads(p), row_id=i, audit_wall=w) for i, w, p in db.execute("SELECT id, wall, payload FROM recovery ORDER BY id")]
        isolation = [dict(json.loads(p), row_id=i, audit_wall=w) for i, w, p in db.execute("SELECT id, wall, payload FROM isolation ORDER BY id")]
        operations = [
            {"row_id": i, "wall": w, "kind": k, "details": json.loads(d)}
            for i, w, k, d in db.execute("SELECT id, wall, kind, details FROM session_operations ORDER BY id")
        ]
        config_changes = [
            dict(json.loads(p), row_id=i, audit_wall=w)
            for i, w, p in db.execute("SELECT id, wall, payload FROM configuration_changes ORDER BY id")
        ]
    after = database.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError("Source changed during analysis; retry with a completed backup")
    with database.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "samples": samples,
        "images": images,
        "recovery": recovery,
        "isolation": isolation,
        "operations": operations,
        "config_changes": config_changes,
        "identity": identity,
        "digest": digest,
    }


def analyze(bundle):
    samples = bundle["samples"]
    images = bundle["images"]
    ids = np.array([s["sample_id"] for s in samples], dtype=int)
    t = np.array([s["wall"] for s in samples], dtype=float)
    dt = np.diff(t, prepend=t[0])
    if np.any(dt < 0):
        raise ValueError("Wall time not monotonic")

    keys_num = ("bpm", "incident_flux", "diode", "waxs_pressure", "maxs_pressure", "saxs_pressure", "fast", "fe", "enabled", "ring_current")
    raw = {
        key: np.array([s["readings"].get(key, {}).get("value", np.nan) for s in samples], dtype=float)
        for key in keys_num
    }
    ring_mode = [str(s["readings"].get("ring_mode", {}).get("value", "")) for s in samples]
    totals = {key: np.array([s["totals"][key] for s in samples], dtype=float) for key in samples[-1]["totals"]}
    unobserved = np.array([s["unobserved_s"] for s in samples], dtype=float)
    delta = {key: np.diff(value, prepend=value[0]) for key, value in totals.items()}
    if any(np.any(value < -1e-6) for value in delta.values()):
        raise ValueError("Counter reset detected; segment accounting is required")

    # Early Oct 22 photon MINOR STATE alarm correction (116.03 s)
    evidence = np.array([
        s["states"]["photon"] is None
        and s["readings"]["photon"].get("value") == "Open"
        and s["readings"]["photon"].get("severity") == 1
        and s["readings"]["fe"].get("value") == 0
        and s["states"]["bpm"] is True
        and 45 <= s["readings"]["incident_flux"].get("value", -1) <= 55
        for s in samples
    ])
    correction = np.where(evidence & np.r_[False, evidence[:-1]], np.minimum(delta["fast_open_s"], delta["unknown_beam_s"]), 0.0)
    corrected_delta = delta["beam_s"] + correction
    corrected = totals["beam_s"] + np.cumsum(correction)

    opened = np.array([s["states"].get("fast") is True for s in samples])
    beam = np.array([s["states"].get("beam") is True for s in samples])
    fe_open = np.array([s["states"].get("fe") is True for s in samples])
    enabled = np.array([s["states"].get("enabled") is True for s in samples])
    p_ok = np.array([bool(s.get("pressure_ok", False)) for s in samples])
    inhibited = np.array([bool(s.get("exposure_inhibited", False)) for s in samples])

    # Weighted BPM3 statistics across entire campaign and post-repair weekend
    flux_valid = np.array([bool(s.get("incident_flux_fresh", False)) for s in samples])
    w_all = np.where(flux_valid & np.isfinite(raw["incident_flux"]), corrected_delta, 0.0)
    flux_mean = float(np.average(np.nan_to_num(raw["incident_flux"]), weights=w_all))
    flux_sd = float(np.sqrt(np.average((np.nan_to_num(raw["incident_flux"]) - flux_mean) ** 2, weights=w_all)))
    flux_integral = float(np.sum(np.nan_to_num(raw["incident_flux"]) * w_all))

    post_repair = ids >= 57136
    w_wk = np.where(post_repair & flux_valid & np.isfinite(raw["incident_flux"]), delta["beam_s"], 0.0)
    flux_wk_mean = float(np.average(np.nan_to_num(raw["incident_flux"]), weights=w_wk))
    flux_wk_sd = float(np.sqrt(np.average((np.nan_to_num(raw["incident_flux"]) - flux_wk_mean) ** 2, weights=w_wk)))

    diode_valid = np.array([bool(s.get("diode_fresh", False)) for s in samples])
    w_diode = np.where(post_repair & diode_valid & np.isfinite(raw["diode"]), delta["beam_s"], 0.0)
    diode_mean = float(np.average(np.nan_to_num(raw["diode"]), weights=w_diode))
    diode_sd = float(np.sqrt(np.average((np.nan_to_num(raw["diode"]) - diode_mean) ** 2, weights=w_diode)))
    diode_beam_vals = raw["diode"][post_repair & diode_valid & np.isfinite(raw["diode"]) & beam]
    diode_steady_vals = diode_beam_vals[diode_beam_vals > 1000]

    # Exposure episodes
    episode_defs = [
        ("Episode 1: Thu Oct 22 evening (pre-repair, 0.05 Torr ceiling, WAXS+OAV)", 1, 21098),
        ("Episode 2: Fri–Sat Oct 23–24 overnight (post-repair, 0.009 Torr, SAXS+WAXS+OAV+TetrAMM)", 88317, 129555),
        ("Episode 3: Sat Oct 24 late morning (post-10:00 false-stale trip recovery)", 132254, 138303),
        ("Episode 4: Sun Oct 25 overnight (01:07–08:07 Accel Studies delivery)", 183929, 209165),
        ("Episode 5: Mon Oct 26 early morning (05:33–06:21 before incomplete image attempt)", 286294, 289215),
    ]
    episodes = []
    for label, id0, id1 in episode_defs:
        m = (ids >= id0) & (ids <= id1)
        bm = m & beam
        w_ep = np.where(m & flux_valid & np.isfinite(raw["incident_flux"]), corrected_delta, 0.0)
        ep_b3 = float(np.average(np.nan_to_num(raw["incident_flux"]), weights=w_ep)) if w_ep.sum() > 0 else float("nan")
        d_vals = raw["diode"][bm & diode_valid & np.isfinite(raw["diode"]) & (raw["diode"] > 1000)]
        episodes.append({
            "label": label,
            "start_sample_id": id0,
            "end_sample_id": id1,
            "start_local": local(t[id0 - 1], "%Y-%m-%d %H:%M:%S"),
            "end_local": local(t[id1 - 1], "%Y-%m-%d %H:%M:%S"),
            "wall_span_s": float(t[id1 - 1] - t[id0 - 1]),
            "online_beam_s": float(delta["beam_s"][m].sum()),
            "corrected_beam_s": float(corrected_delta[m].sum()),
            "cumulative_corrected_beam_s": float(corrected[id1 - 1]),
            "bpm3_weighted_mean": ep_b3,
            "diode_steady_median": float(np.median(d_vals)) if len(d_vals) else None,
            "waxs_pressure_median_torr": float(np.median(raw["waxs_pressure"][bm])),
            "maxs_pressure_median_torr": float(np.median(raw["maxs_pressure"][bm])),
        })

    # Image records and sessions
    image_final = {}
    session_records = []
    for im in images:
        if im.get("status") == "session_finished":
            session_records.append(im)
        elif "image_id" in im:
            image_final[im["image_id"]] = im

    legacy_images = [im for im in image_final.values() if not im.get("single_run")]
    single_images = [im for im in image_final.values() if im.get("single_run")]
    single_completed = [im for im in single_images if im.get("status") != "pending"]
    single_post_trip = [im for im in single_completed if im.get("start", {}).get("post_trip") or im.get("end", {}).get("post_trip")]
    single_pre_trip = [im for im in single_completed if im not in single_post_trip]

    wk_beam_mask = post_repair & beam
    pressure_wk_stats = {
        key: {
            "min": float(np.min(raw[key][wk_beam_mask])),
            "median": float(np.median(raw[key][wk_beam_mask])),
            "p95": float(np.percentile(raw[key][wk_beam_mask], 95)),
            "max": float(np.max(raw[key][wk_beam_mask])),
        }
        for key in ("waxs_pressure", "maxs_pressure", "saxs_pressure")
    }

    gap_indices = np.flatnonzero(dt > 5.0)
    gaps = [
        {
            "before_sample_id": int(ids[i - 1]),
            "after_sample_id": int(ids[i]),
            "before_local": local(t[i - 1], "%Y-%m-%d %H:%M:%S"),
            "after_local": local(t[i], "%Y-%m-%d %H:%M:%S"),
            "seconds": float(dt[i]),
        }
        for i in gap_indices
    ]

    summary = {
        "timezone": "America/New_York (EDT, UTC-04:00)",
        "specimen": bundle["identity"]["specimen"],
        "samples": len(samples),
        "first_sample_local": local(t[0], "%Y-%m-%d %H:%M:%S"),
        "last_sample_local": local(t[-1], "%Y-%m-%d %H:%M:%S"),
        "wall_span_s": float(t[-1] - t[0]),
        "observed_s": float(totals["observed_s"][-1]),
        "unobserved_s": float(unobserved[-1]),
        "fast_open_s": float(totals["fast_open_s"][-1]),
        "fe_fast_open_s": float(totals["fe_fast_open_s"][-1]),
        "online_beam_s": float(totals["beam_s"][-1]),
        "minor_alarm_correction_s": float(correction.sum()),
        "best_estimate_beam_s": float(corrected[-1]),
        "weekend_added_beam_s": float(totals["beam_s"][-1] - totals["beam_s"][57134]),
        "unknown_beam_s": float(totals["unknown_beam_s"][-1]),
        "unknown_fast_s": float(totals["unknown_fast_s"][-1]),
        "last_beam_on_sample_local": local(t[np.flatnonzero(beam)[-1]], "%Y-%m-%d %H:%M:%S"),
        "bpm3_overall_weighted_mean": flux_mean,
        "bpm3_overall_weighted_sd": flux_sd,
        "bpm3_overall_weighted_cv_percent": float(100.0 * flux_sd / flux_mean),
        "bpm3_overall_integral_signal_s": flux_integral,
        "bpm3_weekend_weighted_mean": flux_wk_mean,
        "bpm3_weekend_weighted_sd": flux_wk_sd,
        "diode_weekend_beam_weighted_mean": diode_mean,
        "diode_weekend_beam_weighted_sd": diode_sd,
        "diode_weekend_steady_median": float(np.median(diode_steady_vals)),
        "diode_weekend_steady_p10": float(np.percentile(diode_steady_vals, 10)),
        "diode_weekend_steady_p90": float(np.percentile(diode_steady_vals, 90)),
        "weekend_beam_on_pressure_torr": pressure_wk_stats,
        "legacy_image_attempts": len(legacy_images),
        "legacy_image_outcomes": dict(Counter(im["status"] for im in legacy_images)),
        "single_run_image_attempts": len(single_images),
        "single_run_image_outcomes": dict(Counter(im["status"] for im in single_images)),
        "single_run_completed_pre_trip": len(single_pre_trip),
        "single_run_completed_post_trip": len(single_post_trip),
        "total_completed_image_sets": sum(1 for im in legacy_images if im.get("run_uid")) + len(single_completed),
        "total_image_attempts": len(image_final),
        "episodes": episodes,
        "gaps_over_5s": gaps,
        "single_run_sessions": session_records,
        "key_events": {
            "oct22_pressure_trip_local": "2026-10-22 22:57:32 (WAXS 0.054 Torr vs 0.050 Torr ceiling)",
            "oct23_vacuum_repair_and_migration_local": "2026-10-23 13:48:29 (0.009 Torr ceiling, SAXS+WAXS+OAV+TetrAMM)",
            "oct24_false_stale_trip_local": "2026-10-24 10:00:45.259 (3.87 s scalar sweep delay; pressures 0.0026/0.0016/0 Torr)",
            "oct24_post_trip_images_count": 8,
            "oct24_rearm_and_resume_local": "2026-10-24 10:45:04.730 (rearmed after pump/valve recovery)",
            "oct25_export_stall_sample_id": 234025,
            "oct25_export_stall_local": "2026-10-25 15:01:55.918 is the SOURCE timestamp of the final recorded export cursor, not the time exporting stopped. SQLite reports 55,765 pending samples at session end; Tiled not independently verified.",
            "oct26_last_completed_image_local": "2026-10-26 06:16:47.535",
            "oct26_pending_image_timeout_local": "2026-10-26 06:21:44.845 image start -> close operation 06:22:18.929 (~34 s later), consistent with a detector timeout but no traceback/RunStop verified; cleanup 06:31:21.028",
            "oct26_chamber_pressure_trip_local": "2026-10-26 08:13:15.218 (WAXS 22.0 Torr, MAXS 0.82 Torr) -> pump/turbo/water shutdown readbacks confirmed 08:13:47.603; cause of pressure rise not established",
            "oct26_monitor_end_local": "2026-10-26 08:14:02.088 (WAXS 200.0 Torr, MAXS 130.0 Torr)",
        },
    }
    return {
        "ids": ids,
        "t": t,
        "raw": raw,
        "ring_mode": ring_mode,
        "totals": totals,
        "unobserved": unobserved,
        "corrected": corrected,
        "correction": correction,
        "corrected_delta": corrected_delta,
        "opened": opened,
        "beam": beam,
        "fe_open": fe_open,
        "enabled": enabled,
        "p_ok": p_ok,
        "inhibited": inhibited,
        "images": image_final,
        "summary": summary,
    }


def figure_header(page, title, subtitle, total=5):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="#FAFCFD")
    fig.text(0.08, 0.955, "SMI  /  COMMISSIONING FINAL REPORT", color=TEAL, fontsize=10, weight="bold")
    fig.text(0.08, 0.916, title, color=NAVY, fontsize=20, weight="bold")
    fig.text(0.08, 0.887, subtitle, color=GRAY, fontsize=9)
    fig.text(0.08, 0.034, "KAPTON AIR HOLDER 01  •  22–26 OCT 2026  •  ALL TIMES EDT", color=GRAY, fontsize=8)
    fig.text(0.92, 0.034, f"{page:02d} / {total:02d}", ha="right", color=GRAY, fontsize=8)
    return fig


def save_page(pdf, fig):
    """Fit figure text and table cells to their actual rendered widths."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def wrap(artist, width):
        lines = []
        for paragraph in artist.get_text().splitlines():
            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}".strip()
                artist.set_text(candidate)
                if line and artist.get_window_extent(renderer).width > width:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        artist.set_text("\n".join(lines))

    for artist in fig.texts:
        x, y = artist.get_position()
        if artist.get_ha() == "right":
            continue
        if y >= .88:  # Keep headings on one line, within the page margins.
            width = (.92 - x) * fig.bbox.width
            while artist.get_window_extent(renderer).width > width:
                artist.set_fontsize(artist.get_fontsize() - .25)
        elif .05 < y < .88 and (artist.get_va() == "top" or y < .30):
            wrap(artist, (.92 - x) * fig.bbox.width)

    for ax in fig.axes:
        for table in ax.tables:
            for cell in table.get_celld().values():
                cell.PAD = .035
                artist = cell.get_text()
                wrap(artist, cell.get_window_extent(renderer).width * .91)
                available = cell.get_window_extent(renderer).height * .9
                while artist.get_window_extent(renderer).height > available:
                    artist.set_fontsize(artist.get_fontsize() - .25)
                    if artist.get_fontsize() < 6:
                        raise ValueError("Table needs more space; refusing unreadably small text")
    fig.canvas.draw()
    # Check complete artist bounds before writing; avoid silently clipping a PDF.
    for artist in fig.texts:
        box = artist.get_window_extent(renderer)
        if box.x0 < 0 or box.x1 > fig.bbox.width or box.y0 < 0 or box.y1 > fig.bbox.height:
            raise ValueError(f"Text outside page: {artist.get_text()[:70]}")
    pdf.savefig(fig)
    plt.close(fig)


def card(fig, x, y, width, value, label, detail):
    fig.add_artist(
        FancyBboxPatch(
            (x, y),
            width,
            0.088,
            boxstyle="round,pad=0.012",
            facecolor="#EAF2F5",
            edgecolor="none",
            transform=fig.transFigure,
        )
    )
    fig.text(x + 0.005, y + 0.056, value, fontsize=15.5, color=NAVY, weight="bold")
    fig.text(x + 0.005, y + 0.032, label, fontsize=8.5, color=TEAL, weight="bold")
    fig.text(x + 0.005, y + 0.011, detail, fontsize=7.3, color=GRAY)


def style(ax, title, ylabel, *, date_fmt="%b %d\n%H:%M", hours=6):
    ax.set_title(title, loc="left", fontsize=10.5, color=NAVY, weight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=8.5, color=GRAY)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C8D3DA")
    ax.grid(axis="y", color="#DCE4E9", lw=0.5)
    ax.tick_params(labelsize=7.5, colors=GRAY)
    ax.set_facecolor("white")
    if date_fmt:
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_fmt, tz=TZ))
    if hours:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=hours, tz=TZ))


def plot_envelope(ax, t, values, *, color, label, seconds=180):
    valid = np.isfinite(values)
    if not np.any(valid):
        return
    tv, vv = t[valid], values[valid]
    bins = np.floor((tv - t[0]) / seconds).astype(int)
    groups = np.unique(bins)
    centers, med, lo, hi = [], [], [], []
    for g in groups:
        if centers and g > previous_group + 1:
            # Preserve beam-off/missing intervals instead of joining distant bins.
            centers.append(t[0] + (previous_group + 1) * seconds)
            med.append(np.nan)
            lo.append(np.nan)
            hi.append(np.nan)
        m = bins == g
        v = vv[m]
        centers.append(np.mean(tv[m]))
        med.append(np.median(v))
        lo.append(np.min(v))
        hi.append(np.max(v))
        previous_group = g
    x = mdates.date2num([datetime.fromtimestamp(ts, TZ) for ts in centers])
    ax.fill_between(x, lo, hi, color=color, alpha=0.18, linewidth=0)
    ax.plot(x, med, color=color, lw=1.2, label=label)


def generate_pdf(data, bundle, output, *, dose=None, weekend_metadata=()):
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
        "axes.labelcolor": GRAY,
        "text.color": NAVY,
    })
    s = data["summary"]
    t, raw, ids = data["t"], data["raw"], data["ids"]
    x = mdates.date2num([datetime.fromtimestamp(ts, TZ) for ts in t])
    cache = ROOT / "logs/image_cache"
    has_images = (cache / "manifest.json").exists() and (ROOT / "movie_scale.json").exists()
    base_pages = 5 if has_images else 4
    total_pages = base_pages + len(weekend_metadata) + (2 if dose else 0)

    img_starts = []
    img_beams = []
    img_post = []
    for im in data["images"].values():
        st = im.get("start", {})
        if st and im.get("status") != "pending" and (im.get("single_run") or im.get("run_uid")):
            w = st["wall"]
            img_starts.append(w)
            idx = min(np.searchsorted(t, w), len(t) - 1)
            img_beams.append(data["corrected"][idx] / 3600.0)
            img_post.append(bool(st.get("post_trip") or im.get("end", {}).get("post_trip")))
    img_starts = np.array(img_starts)
    img_beams = np.array(img_beams)
    img_post = np.array(img_post, dtype=bool)

    with PdfPages(
        output,
        metadata={
            "Title": "Kapton irradiation | Final weekend commissioning report (Oct 22-26, 2026)",
            "Author": "SMI commissioning analysis",
            "Subject": "Multi-day Kapton air holder exposure, pressure guard, and single-run telemetry audit",
        },
    ) as pdf:
        # PAGE 1: Campaign overview
        fig = figure_header(
            1,
            "Four days on the Kapton air holder",
            "22–26 Oct 2026  |  Nominal 6 keV  |  Post-repair ceiling: 0.009 Torr",
            total_pages,
        )
        card(fig, 0.08, 0.77, 0.255, duration(s["best_estimate_beam_s"]), "ESTIMATED BEAM TIME", "Online total + 116 s early correction")
        card(fig, 0.37, 0.77, 0.255, duration(s["weekend_added_beam_s"]), "WEEKEND BEAM ADDED", "Post-repair (Oct 23–26) at 2.6 mTorr")
        card(fig, 0.66, 0.77, 0.26, "211 / 214 sets", "JOURNAL END RECORDS", "149 weekend sets; 8 after isolation")

        ax1 = fig.add_axes([0.10, 0.54, 0.82, 0.17])
        ax1.plot(x[::30], data["corrected"][::30] / 3600.0, color=TEAL, lw=1.8, label="Best estimate beam-on (h)")
        ax1.plot(x[::30], data["totals"]["beam_s"][::30] / 3600.0, color=NAVY, lw=1.0, ls="--", label="Online counter (h)")
        x_img = mdates.date2num([datetime.fromtimestamp(v, TZ) for v in img_starts])
        ax1.scatter(x_img[~img_post], img_beams[~img_post], s=6, color=ORANGE, label="Pre-trip image record (203)", zorder=3)
        if np.any(img_post):
            ax1.scatter(x_img[img_post], img_beams[img_post], s=14, color=RED, marker="x", label="Post-trip dark image set (8)", zorder=4)
        style(ax1, "01  Cumulative beam-on exposure across five delivery episodes", "Beam-on time · h", hours=12)
        ax1.set_xlim(x[0], x[-1])
        ax1.legend(loc="upper left", fontsize=7.5, frameon=False, ncol=2)

        ax2 = fig.add_axes([0.10, 0.30, 0.82, 0.17])
        plot_envelope(ax2, t, raw["incident_flux"], color=TEAL, label="BPM3 SumX · incident flux (left)", seconds=300)
        style(ax2, "02  Storage-ring current and incident X-ray flux (BPM3)", "BPM3 SumX · native", hours=12)
        ax2.set_xlim(x[0], x[-1])
        ax2.set_ylim(-5, 60)
        ax2_r = ax2.twinx()
        plot_envelope(ax2_r, t, raw["ring_current"], color=PURPLE, label="Ring current · mA (right)", seconds=300)
        ax2_r.set_ylabel("Ring current · mA", fontsize=8, color=PURPLE)
        ax2_r.tick_params(axis="y", labelsize=7.5, colors=PURPLE)
        ax2_r.spines["top"].set_visible(False)
        ax2_r.spines["right"].set_color(PURPLE)
        ax2_r.set_ylim(-20, 550)
        l1, lb1 = ax2.get_legend_handles_labels()
        l2, lb2 = ax2_r.get_legend_handles_labels()
        ax2.legend(l1 + l2, lb1 + lb2, loc="upper left", fontsize=7.5, frameon=False, ncol=2)

        fig.text(0.10, 0.225, "EXECUTIVE SUMMARY", fontsize=10, weight="bold", color=TEAL)
        fig.text(
            0.10,
            0.200,
            "• Log coverage: Oct 22 17:01 → Oct 26 08:14 EDT; 295,950 samples across 87 h 13 min.\n"
            "• Post-repair beam-on pressures: WAXS 2.5–2.7 mTorr, MAXS 1.5–1.7 mTorr; SAXS zero denotes below range. No over-ceiling pressure was recorded during weekend beam-on samples.\n"
            "• Saturday's stale-read trip completed staged shutdown; eight post-trip image end records followed. The pressure-reader fix exists on disk but is NOT evidenced in this database.\n"
            "• Monday: last image attempt 06:21:45; first closed-shutter sample 06:21:47. A separate high-pressure trip at 08:13:15 completed shutdown by 08:13:48.\n"
            + ("• Diode-confirmed photon and model-dose estimates use the operator's 40 × 300 µm footprint. Saturday first/last images and the dose derivation follow in this report."
             if dose else "• Beam time is a shutter/BPM proxy, not absorbed dose. Weekend image retrieval and a final material-damage assessment remain unverified."),
            fontsize=8.3,
            linespacing=1.42,
            va="top",
        )
        save_page(pdf, fig)

        # PAGE 2: Weekend vacuum performance, TetrAMM transmission, and episode breakdown
        fig = figure_header(
            2,
            "Post-repair vacuum & diode telemetry",
            "0.009 Torr ceiling  |  Continuous TetrAMM channel 2  |  Five irradiation episodes",
            total_pages,
        )
        wk = ids >= 57136
        ax1 = fig.add_axes([0.10, 0.65, 0.82, 0.17])
        plot_envelope(ax1, t[wk], np.maximum(raw["waxs_pressure"][wk], 1e-4), color=TEAL, label="WAXS pressure", seconds=180)
        plot_envelope(ax1, t[wk], np.maximum(raw["maxs_pressure"][wk], 1e-4), color=NAVY, label="MAXS pressure", seconds=180)
        ax1.set_yscale("log")
        ax1.axhline(0.009, color=RED, ls="--", lw=1.0, label="Ceiling 0.009 Torr")
        style(ax1, "03  Weekend chamber pressures (Oct 23 13:48 → Oct 26 08:14)", "Pressure · Torr (log)", hours=8)
        ax1.set_xlim(x[wk][0], x[wk][-1])
        ax1.legend(loc="upper left", fontsize=7.5, frameon=False, ncol=3)

        ax2 = fig.add_axes([0.10, 0.41, 0.82, 0.16])
        dio_beam = np.where(data["beam"][wk] & (raw["diode"][wk] > 0), raw["diode"][wk], np.nan)
        plot_envelope(ax2, t[wk], dio_beam / 1000.0, color=ORANGE, label="TetrAMM Ch2 (beam-on, µA)", seconds=180)
        style(ax2, "04  Transmitted diode current during beam-on intervals", "Diode current · µA", hours=8)
        ax2.set_xlim(x[wk][0], x[wk][-1])
        ax2.set_ylim(0, 42)
        ax2.legend(loc="upper right", fontsize=7.5, frameon=False)

        ep_rows = [["Episode / Window (EDT)", "Beam Time", "Cumul. Beam", "BPM3 Mean", "Diode (nA)", "WAXS / MAXS"]]
        for i, ep in enumerate(s["episodes"], 1):
            dio_str = f"{ep['diode_steady_median']:,.0f}" if ep["diode_steady_median"] is not None else "n/a (pre-diode)"
            ep_rows.append([
                f"{i}: {ep['start_local'][5:-3]}\n→ {ep['end_local'][5:-3]}",
                duration(ep["corrected_beam_s"]).replace(" h ", ":").replace(" min ", ":").replace(" s", ""),
                duration(ep["cumulative_corrected_beam_s"]).replace(" h ", ":").replace(" min ", ":").replace(" s", ""),
                f"{ep['bpm3_weighted_mean']:.2f}",
                dio_str,
                f"{ep['waxs_pressure_median_torr']*1000:.1f} / {ep['maxs_pressure_median_torr']*1000:.1f} mTorr",
            ])
        ax_t = fig.add_axes([0.08, 0.13, 0.84, 0.22])
        ax_t.axis("off")
        tbl = ax_t.table(
            cellText=ep_rows[1:],
            colLabels=ep_rows[0],
            colWidths=[0.28, 0.14, 0.14, 0.11, 0.15, 0.18],
            cellLoc="left",
            loc="center",
            bbox=[0, 0, 1, 1],
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(7.5)
        for (r, _c), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor(NAVY)
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("#EDF3F6" if r % 2 == 1 else "white")
                cell.set_text_props(color=NAVY)
            cell.set_edgecolor("white")

        fig.text(
            0.08,
            0.095,
            "Times in table: h:mm:ss. Diode medians select fresh beam-on samples >1000 nA; this display filter is not used for dose integration. Gaps are not interpolated. Signal changes alone do not establish Kapton damage or realignment. Episode windows omit a 0.10 s counter increment near Oct 26 02:55; the campaign total includes it.",
            fontsize=8.0,
            color=GRAY,
            linespacing=1.35,
            va="top",
        )
        save_page(pdf, fig)

        # PAGE 3: Incident & Protection Audit (Oct 24 10:00 trip, Oct 26 06:21 timeout, Oct 26 08:13 vent)
        fig = figure_header(
            3,
            "Protection trips & operational anomalies",
            "SQLite evidence  |  Saturday stale-read trip  |  Monday pressure rise and image termination",
            total_pages,
        )

        # Panel A: Oct 24 10:00–10:48
        m_sat = (ids >= 129500) & (ids <= 132300)
        ax1 = fig.add_axes([0.10, 0.64, 0.82, 0.17])
        x_sat = x[m_sat]
        ax1.plot(x_sat, raw["waxs_pressure"][m_sat], color=TEAL, lw=1.3, label="WAXS pressure")
        ax1.plot(x_sat, raw["maxs_pressure"][m_sat], color=NAVY, lw=1.1, label="MAXS pressure")
        ax1.plot(x_sat, np.maximum(raw["saxs_pressure"][m_sat], 1e-4), color=ORANGE, lw=1.0, ls=":", label="SAXS pressure (0→1e-4)")
        ax1.set_yscale("log")
        ax1.axhline(0.009, color=RED, ls="--", lw=0.9, label="0.009 Torr ceiling")
        ax1.axvline(mdates.date2num(datetime.fromtimestamp(1792850445.259, TZ)), color=RED, lw=1.0)
        ax1.axvline(mdates.date2num(datetime.fromtimestamp(1792853104.730, TZ)), color=TEAL, ls="--", lw=1.0)
        style(ax1, "05  Saturday: stale-read trip and recovery excursion", "Pressure · Torr (log)", date_fmt="%H:%M", hours=None)
        ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=5, tz=TZ))
        ax1.legend(loc="upper left", fontsize=7, frameon=False, ncol=2)

        # Panel B: Mon Oct 26 08:12:45–08:14:02
        m_mon = ids >= 295880
        ax2 = fig.add_axes([0.10, 0.39, 0.82, 0.16])
        x_mon = x[m_mon]
        ax2.step(x_mon, np.maximum(raw["waxs_pressure"][m_mon], 1e-4), where="post", color=TEAL, lw=1.4, label="WAXS pressure")
        ax2.step(x_mon, np.maximum(raw["maxs_pressure"][m_mon], 1e-4), where="post", color=NAVY, lw=1.2, label="MAXS pressure")
        ax2.set_yscale("log")
        ax2.axhline(0.009, color=RED, ls="--", lw=0.9, label="0.009 Torr ceiling")
        ax2.axvline(mdates.date2num(datetime.fromtimestamp(1793016795.218, TZ)), color=RED, lw=1.0, label="Trip 08:13:15.2")
        ax2.axvline(mdates.date2num(datetime.fromtimestamp(1793016827.603, TZ)), color=ORANGE, ls="--", lw=1.0, label="Pump/Turbo/Water off 08:13:47.6")
        style(ax2, "06  Monday: high-pressure trip after beam exposure ended", "Pressure · Torr (log)", date_fmt="%H:%M:%S", hours=None)
        ax2.xaxis.set_major_locator(mdates.SecondLocator(interval=10, tz=TZ))
        ax2.legend(loc="upper left", fontsize=7.5, frameon=False, ncol=2)

        fig.text(0.10, 0.315, "CHRONOLOGY OF ANOMALIES & SAFEGUARD ACTIONS", fontsize=10, weight="bold", color=TEAL)
        fig.text(
            0.10,
            0.290,
            "1. Saturday 10:00:45 — Stale-read trip. The notes identify a 3.87 s scalar-sweep delay exceeding the old 3 s freshness window; adjacent pressures were normal. Boundary readbacks confirmed at 10:00:48.526, IV1 at 10:01:19.327, turbo disable at 10:01:19.853, and water closure at 10:01:21.275. Eight post-trip image end records have zero added beam time. After a separate recovery excursion, the guard rearmed at 10:45:04.730.\n\n"
            "2. Export backlog. The final journal reports cursor #234025 versus cutoff #289790: 55,765 pending scalar IDs. Oct 25 15:01:55.918 is the cursor's SOURCE timestamp, not when export stopped. Tiled scan 1185490 reports 101,417 scalar events; the backlog cause is not established.\n\n"
            "3. Monday termination. The 06:21:44.845 image attempt has no end record; a close operation follows 34 s later. Tiled now confirms scan 1185490 failed: 'Image detector completion timed out'. The shutter reads closed at 06:21:47.284. At 08:13:15, WAXS/MAXS jumped to 22/0.82 Torr; shutdown readbacks completed at 08:13:47.603. The pressure-rise cause, including possible intentional venting, requires operator confirmation.\n\n"
            "Valve confirmation uses 'Not Open' status, not an independent closed limit. Turbo OnOff=0 confirms disable, not rotor spin-down.",
            fontsize=8.3,
            linespacing=1.36,
            va="top",
        )
        save_page(pdf, fig)

        # PAGE 4: Complete Statistics & Session Audit Table
        fig = figure_header(
            4,
            "Campaign statistics & session audit",
            "Integrated exposure counters, flux/diode distributions, and Bluesky single-run session records",
            total_pages,
        )
        stat_rows = [
            ["Best-estimate beam time (campaign)", f"{duration(s['best_estimate_beam_s'])} ({s['best_estimate_beam_s']:,.2f} s)"],
            ["Saved online beam counter (beam_s)", f"{duration(s['online_beam_s'])} ({s['online_beam_s']:,.2f} s)"],
            ["Added Oct 22 early photon MINOR-alarm interval", f"{s['minor_alarm_correction_s']:.2f} s"],
            ["Weekend beam time added (post-repair)", f"{duration(s['weekend_added_beam_s'])} ({s['weekend_added_beam_s']:,.2f} s)"],
            ["Total wall-clock campaign span", duration(s['wall_span_s'])],
            ["Observed monitor time / Unobserved restart gaps", f"{duration(s['observed_s'])} / {duration(s['unobserved_s'])}"],
            ["Fast shutter controller-open time (fast_open_s)", f"{duration(s['fast_open_s'])} ({s['fast_open_s']:,.2f} s)"],
            ["FE open + Fast shutter open time (fe_fast_open_s)", f"{duration(s['fe_fast_open_s'])} ({s['fe_fast_open_s']:,.2f} s)"],
            ["BPM3 beam-weighted mean ± SD (overall)", f"{s['bpm3_overall_weighted_mean']:.3f} ± {s['bpm3_overall_weighted_sd']:.3f} native (CV {s['bpm3_overall_weighted_cv_percent']:.2f}%)"],
            ["BPM3 beam-weighted mean ± SD (weekend post-repair)", f"{s['bpm3_weekend_weighted_mean']:.3f} ± {s['bpm3_weekend_weighted_sd']:.3f} native"],
            ["Integrated BPM3 × beam time (overall)", f"{s['bpm3_overall_integral_signal_s']:,.0f} signal·s"],
            ["Filtered diode median (p10 – p90)", f"{s['diode_weekend_steady_median']:,.0f} ({s['diode_weekend_steady_p10']:,.0f} – {s['diode_weekend_steady_p90']:,.0f}) nA"],
            ["Beam-on medians: WAXS / MAXS / SAXS", "0.0026 / 0.0016 / 0 Torr; SAXS below range"],
            ["Image end records / attempts (SQLite)", f"{s['total_completed_image_sets']} / {s['total_image_attempts']} (62/63 legacy + 149/151 single-run)"],
            ["Pre-trip vs. Post-trip single-run image sets", f"{s['single_run_completed_pre_trip']} pre-trip beam sets + {s['single_run_completed_post_trip']} post-trip dark sets"],
            ["Scalar / recovery / isolation records", f"{s['samples']:,} / {len(bundle['recovery'])} / {len(bundle['isolation'])}"],
        ]
        ax_s = fig.add_axes([0.08, 0.45, 0.84, 0.41])
        ax_s.axis("off")
        tbl_s = ax_s.table(cellText=stat_rows, colWidths=[0.52, 0.48], cellLoc="left", bbox=[0, 0, 1, 1])
        tbl_s.auto_set_font_size(False)
        tbl_s.set_fontsize(8.0)
        for (r, _c), cell in tbl_s.get_celld().items():
            cell.set_facecolor("#EDF3F6" if r % 2 == 0 else "white")
            cell.set_edgecolor("white")
            cell.set_text_props(color=NAVY)

        fig.text(0.08, 0.415, "SINGLE-RUN SESSIONS RECORDED IN SQLITE", fontsize=10, weight="bold", color=TEAL)
        sess_rows = [
            ["End (EDT)", "Start ID", "Export ID", "Cutoff ID", "Pending", "Image journal"],
            ["Oct 23\n13:57:19", "57,284", "57,543", "57,666", "123", "Recovery failed; no beam"],
            ["Oct 24\n07:45:47", "120,835", "120,835", "121,460", "625", "No image end records"],
            ["Oct 24\n10:37:29", "121,467", "131,756", "131,758", "2", "27 pre-trip + 8 post-trip"],
            ["Oct 24\n10:46:22", "132,252", "132,289", "132,292", "3", "Attempt #36 pending"],
            ["Oct 24\n10:51:35", "132,459", "132,600", "132,604", "4", "One end record (#37)"],
            ["Oct 26\n06:31:22", "132,608", "234,025", "289,790", "55,765", "113 end records; #151 pending"],
        ]
        ax_sr = fig.add_axes([0.08, 0.20, 0.84, 0.19])
        ax_sr.axis("off")
        tbl_sr = ax_sr.table(
            cellText=sess_rows[1:],
            colLabels=sess_rows[0],
            colWidths=[0.15, 0.13, 0.13, 0.13, 0.12, 0.34],
            cellLoc="left",
            bbox=[0, 0, 1, 1],
        )
        tbl_sr.auto_set_font_size(False)
        tbl_sr.set_fontsize(7.3)
        for (r, _c), cell in tbl_sr.get_celld().items():
            if r == 0:
                cell.set_facecolor(NAVY)
                cell.set_text_props(color="white", weight="bold")
            else:
                cell.set_facecolor("#EDF3F6" if r % 2 == 1 else "white")
                cell.set_text_props(color=NAVY)
            cell.set_edgecolor("white")

        fig.text(
            0.08,
            0.165,
            "EVIDENCE & LIMITS\n"
            "• Friday night delivered 8.88 h of logged beam time without image records in this journal.\n"
            "• The database has no pressure_samples table or pressure_stale_s setting: deployment of Saturday's pressure-reader fix is not established.\n"
            "• All image end records are flagged 'interrupted'; normal shutter cycling can set this flag. Selected first/last SAXS/WAXS/OAV arrays now resolve through Tiled.\n"
            "• Source: checkpointed Oct 26 SQLite snapshot (path and full audit in JSON).\n"
            f"SHA-256: {bundle['digest']}",
            fontsize=7.6,
            color=GRAY,
            linespacing=1.35,
            va="top",
        )
        save_page(pdf, fig)

        # PAGE 5: Initial Oct 22 Before/After Reference Frames (from cache)
        cache = ROOT / "logs/image_cache"
        has_images = (cache / "manifest.json").exists() and (ROOT / "movie_scale.json").exists()
        if has_images:
            from matplotlib.colors import LogNorm
            from tiled_images import yellowhot

            manifest = json.loads((cache / "manifest.json").read_text())
            scale = json.loads((ROOT / "movie_scale.json").read_text())
            fig = figure_header(
                5,
                "Initial optical & WAXS reference frames",
                "Cached Oct 22 frames: scans 1185420 and 1185481  |  Initial five-hour reference",
                total_pages,
            )
            for col, meta in enumerate((manifest[0], manifest[-1])):
                frames = np.load(cache / f"{meta['uid']}.npz")
                x0 = 0.08 + col * 0.46
                fig.text(x0, 0.84, "EPISODE 1 START" if col == 0 else "EPISODE 1 END", color=TEAL, fontsize=11, weight="bold")
                fig.text(x0, 0.815, meta["local_time"] + " EDT (Oct 22)", fontsize=9)
                fig.text(x0, 0.792, "Beam on: " + duration(meta["corrected_beam_s"]), fontsize=9, weight="bold")
                ax = fig.add_axes([x0, 0.465, 0.38, 0.30])
                ax.set_axis_off()
                cmap = yellowhot()
                cmap.set_bad("black")
                im = ax.imshow(
                    np.ma.masked_less_equal(frames["waxs"], 0),
                    cmap=cmap,
                    norm=LogNorm(scale["vmin"], scale["vmax"], clip=True),
                    interpolation="nearest",
                )
                ax.set_title(f"WAXS · scan {meta['scan_id']}", fontsize=10, color=NAVY)
                ax = fig.add_axes([x0, 0.17, 0.38, 0.23])
                ax.set_axis_off()
                ax.imshow(frames["oav"], cmap="gray", interpolation="nearest")
                ax.set_title("On-axis view (OAV)", fontsize=10, color=NAVY)
                frames.close()
            cax = fig.add_axes([0.22, 0.432, 0.56, 0.012])
            cb = fig.colorbar(im, cax=cax, orientation="horizontal")
            cb.set_label("WAXS counts · fixed logarithmic yellow-hot scale", fontsize=8)
            cb.ax.tick_params(labelsize=7)
            fig.text(
                0.08,
                0.105,
                "These are initial-campaign references, not final weekend images. The first frame already includes 2 min 21 s exposure. WAXS uses one fixed log scale with nonpositive pixels masked. The following Saturday comparisons use this exact scale; OAV retains its original RGB values.",
                fontsize=8.3,
                linespacing=1.4,
                va="top",
            )
            save_page(pdf, fig)

        if weekend_metadata:
            from weekend_reference_images import render_pages
            render_pages(pdf, weekend_metadata, base_pages+1, total_pages, figure_header, save_page)
        if dose:
            from kapton_dose import dose_pages
            dose_pages(pdf, data, dose, weekend_metadata, base_pages+len(weekend_metadata)+1,
                       total_pages, figure_header, save_page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=ROOT / "kapton_final_report_2026-10-26.pdf")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--replace-existing", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("fontTools").setLevel(logging.WARNING)

    bundle = load(args.database)
    data = analyze(bundle)
    from weekend_reference_images import load_cached
    from kapton_dose import analyze_dose
    weekend_metadata = load_cached()
    dose = None
    if any(m["scan_id"] == 1185490 for m in weekend_metadata):
        dose, _ = analyze_dose(bundle, data, weekend_metadata)
        data["summary"]["key_events"]["oct26_pending_image_timeout_local"] = (
            "06:21:44.845 final attempt; Tiled scan 1185490 RunStop confirms 'Image detector completion timed out'; "
            "first fast-closed scalar at 06:21:47.284; cleanup at 06:22:18.929 and 06:31:21.028"
        )
        data["summary"]["tiled_verification"] = {
            "verified_date": "2026-10-26", "selected_first_last_arrays": "SAXS, WAXS, OAV for scans 1185487 and 1185490",
            "1185490_primary_events": 113, "1185490_scalar_events": 101417,
            "1185490_in_run_pending_scalar_ids": 55222, "1185490_in_run_cutoff": 289247,
            "1185490_later_sqlite_pending_ids": 55765, "1185490_later_sqlite_cutoff": 289790,
            "note": "Different cutoff times explain the in-run summary versus later local finalization totals.",
        }
    summary = {
        **data["summary"],
        "database_path": str(args.database),
        "database_sha256": bundle["digest"],
        "identity": bundle["identity"],
        "configuration_changes": bundle["config_changes"],
        "recovery": bundle["recovery"],
        "isolation": bundle["isolation"],
        "diode_photons_and_dose": dose,
        "weekend_tiled_metadata": weekend_metadata,
    }
    log.info("%s", json.dumps(data["summary"], indent=2))
    if not args.apply:
        log.info("Preview only. Use --apply to create %s and JSON/CSV sidecars.", args.output)
        return

    outputs = [args.output, args.output.with_suffix(".json"), args.output.with_suffix(".csv")]
    if any(p.exists() for p in outputs) and not args.replace_existing:
        raise FileExistsError("Choose a new output name or pass --replace-existing")

    generate_pdf(data, bundle, args.output, dose=dose, weekend_metadata=weekend_metadata)
    with outputs[1].open("w" if args.replace_existing else "x") as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
    with outputs[2].open("w" if args.replace_existing else "x", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "image_id",
                "mode",
                "status",
                "post_trip",
                "local_start",
                "local_end",
                "run_uid",
                "online_beam_start_s",
                "online_beam_end_s",
                "corrected_beam_start_s",
            ],
        )
        writer.writeheader()
        for image in data["images"].values():
            st = image.get("start", {})
            en = image.get("end", {})
            b_start = st.get("totals", {}).get("beam_s")
            b_end = en.get("totals", {}).get("beam_s")
            corr_start = ""
            if st and "wall" in st:
                offset = np.interp(st["wall"], data["t"], np.cumsum(data["correction"]))
                if b_start is not None:
                    corr_start = f"{b_start + offset:.3f}"
            writer.writerow({
                "image_id": image["image_id"],
                "mode": "single_run" if image.get("single_run") else "legacy",
                "status": image["status"],
                "post_trip": int(bool(st.get("post_trip") or en.get("post_trip"))),
                "local_start": local(st["wall"], "%Y-%m-%d %H:%M:%S") if st else "",
                "local_end": local(en["wall"], "%Y-%m-%d %H:%M:%S") if en else "",
                "run_uid": image.get("run_uid", ""),
                "online_beam_start_s": f"{b_start:.3f}" if b_start is not None else "",
                "online_beam_end_s": f"{b_end:.3f}" if b_end is not None else "",
                "corrected_beam_start_s": corr_start,
            })
    log.info("Created %s, %s, %s", *outputs)


if __name__ == "__main__":
    main()

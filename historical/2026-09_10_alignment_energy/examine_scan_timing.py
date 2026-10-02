"""Read scalar timing data from Tiled and report multi-edge scan throughput.

HISTORICAL AD HOC ANALYSIS — September/October 2026; see this directory's README.
From a configured smi-plans environment:
    pixi run python ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/examine_scan_timing.py

No detector images are loaded. Open/failed/short runs are reported but excluded
from full-run calibration. Run under the same Pixi environment for repeatability.
"""

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from tiled.client import from_profile
from tiled.queries import Key
from zoneinfo import ZoneInfo


def examine(catalog):
    runs = catalog.search(Key("scan_name") == "holder2_multi_edge_grid")
    records, intervals = [], []
    for run in runs.values():
        start = run.metadata["start"]
        # Bound this examination to the known experiment, not future matching plans.
        if not 1170294 <= start["scan_id"] <= 1170400:
            continue
        stop = run.metadata.get("stop") or {}
        grid = start.get("grid", {})
        row = {
            "uid": start["uid"], "scan_id": start["scan_id"],
            "sample_id": start.get("sample_id"),
            "sample": start["sample_name"].split("_{")[0],
            "edge": start.get("edge_label"), "arc": start.get("waxs_arc_target"),
            "start": start["time"], "stop": stop.get("time", np.nan),
            "status": stop.get("exit_status", "open"),
            "expected": grid.get("stop_point_exclusive", 0) - grid.get("first_point", 0),
            "events": 0, "first_delay_s": np.nan, "tail_s": np.nan,
            "interval_median_s": np.nan, "interval_p90_s": np.nan,
        }
        row["duration_s"] = row["stop"] - row["start"]
        # A running dataset can grow during reads; only closed runs are calibrated.
        if stop and "primary" in run:
            ds = run["primary"]["data"].read(
                variables=["time", "energy_set", "grid_point", "piezo_x", "piezo_y"])
            t = np.asarray(ds["time"], dtype=float)
            if len(t) and (t[0] < row["start"] or t[-1] > row["stop"]):
                raise ValueError(f"Invalid event timestamps for scan {row['scan_id']}")
            row["events"] = len(t)
            if len(t):
                row["first_delay_s"] = t[0] - row["start"]
                row["tail_s"] = row["stop"] - t[-1]
            if len(t) > 1:
                dt = np.diff(t)
                row["interval_median_s"] = float(np.median(dt))
                row["interval_p90_s"] = float(np.quantile(dt, .9))
                for i, delta in enumerate(dt):
                    intervals.append({
                        "scan_id": row["scan_id"], "edge": row["edge"], "arc": row["arc"],
                        "dt_s": float(delta),
                        "energy_step_eV": round(float(ds["energy_set"][i + 1] - ds["energy_set"][i]), 3),
                        "x_transition": abs(float(ds["piezo_x"][i + 1] - ds["piezo_x"][i])) > 50,
                    })
        records.append(row)
    frame = pd.DataFrame(records).sort_values("start").reset_index(drop=True)
    frame["full"] = ((frame.status == "success") & (frame.events == frame.expected)
                     & (frame.events.isin([80, 87])))
    frame["gap_before_s"] = frame.start - frame.stop.shift()
    frame["transition"] = np.where(
        frame.sample_id != frame.sample_id.shift(), "sample", np.where(
            frame.arc != frame.arc.shift(), "arc", "edge"))
    frame["start_local"] = [datetime.fromtimestamp(t, ZoneInfo("America/New_York")).isoformat()
                            for t in frame.start]
    intervals = pd.DataFrame(intervals)
    return frame, intervals


def report(frame, intervals):
    full = frame[frame.full]
    good_intervals = intervals[intervals.scan_id.isin(full.scan_id)]
    print("Status/event counts:\n", frame.groupby(["status", "events"]).size().to_string())
    print("\nFull-run timing (seconds):")
    grouped = full.groupby(["arc", "edge"]).agg(
        runs=("scan_id", "count"), median_s=("duration_s", "median"),
        min_s=("duration_s", "min"), max_s=("duration_s", "max"),
        first_s=("first_delay_s", "median"), tail_s=("tail_s", "median"),
        interval_s=("interval_median_s", "median"))
    print(grouped.round(2).to_string())
    print("\nInter-event timing by energy step (seconds):")
    print(good_intervals.groupby(["arc", "energy_step_eV"]).dt_s.agg(
        ["count", "median", "mean", "max"]).round(3).to_string())
    print("\nColumn transitions vs Y steps (seconds):")
    print(good_intervals.groupby(["arc", "x_transition"]).dt_s.agg(
        ["count", "median", "mean"]).round(3).to_string())
    # Only adjacent full runs can contribute to routine transition calibration.
    gaps = frame[frame.full & frame.full.shift(fill_value=False)]
    print("\nInter-run gaps, adjacent full runs (seconds; all gaps shown):")
    print(gaps.groupby("transition").gap_before_s.agg(
        ["count", "median", "min", "max"]).round(2).to_string())
    print("\nGaps over 5 minutes (exclude from routine estimate):")
    print(frame.loc[frame.gap_before_s > 300,
                    ["scan_id", "sample", "gap_before_s"]].round(2).to_string(index=False))
    print("\nComplete sample batches (ten unique full edge/angle runs):")
    sample_minutes = []
    for sample, rows in full.groupby("sample_id"):
        if len(rows) != 10 or len(rows.groupby(["arc", "edge"])) != 10:
            continue
        minutes = (rows.stop.max() - rows.start.min()) / 60
        sample_minutes.append(minutes)
        print(rows.iloc[0]["sample"], f"{minutes:.2f} min")
    # Ten run durations + eight edge gaps + one arc gap within a sample.
    routine_gaps = gaps[gaps.gap_before_s <= 300].groupby("transition").gap_before_s.median()
    estimate_s = grouped.median_s.sum() + 8 * routine_gaps["edge"] + routine_gaps["arc"]
    batch_s = 8 * estimate_s + 7 * routine_gaps["sample"]
    summary = {
        "full_runs": len(full), "full_events": int(full.events.sum()),
        "per_sample_minutes": estimate_s / 60, "eight_samples_hours": batch_s / 3600,
        "observed_complete_sample_minutes": sample_minutes,
        "routine_gap_medians_s": routine_gaps.to_dict(),
        "calibration": "1 s exposure, 2 s energy settle; same five lists and 0/20 arcs",
    }
    print("\nInitial estimate:\n", json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    catalog = from_profile("auto")["smi"]["raw"]
    frame, intervals = examine(catalog)
    summary = report(frame, intervals)
    out = Path(__file__).parent
    frame.to_csv(out / "holder2_timing_runs.csv", index=False)
    intervals.to_csv(out / "holder2_timing_intervals.csv", index=False)
    (out / "holder2_timing_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

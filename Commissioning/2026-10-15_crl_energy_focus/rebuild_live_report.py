"""Rebuild live_crl_focus.html from completed Tiled runs.

Use this if the live panel stalled mid-series (e.g. one sweep's analysis raised in an
older build): it re-reads the finished energy sweeps from Tiled and regenerates the same
self-refreshing page with the hardened analysis. Safe to run while acquisition continues.

    pixi run python .../rebuild_live_report.py                 # most recent 4 fine sweeps
    pixi run python .../rebuild_live_report.py --n 3 --out /tmp/panel.html
"""

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINE_SCAN_NAME = "crl_energy_focus_commissioning"
FIELDS = ["energy_energy_setpoint", "piezo_x", "pil2M_stats1_total"]


def _load_report_module():
    spec = importlib.util.spec_from_file_location(
        "live_focus_report", HERE / "live_focus_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4, help="most recent fine sweeps to include")
    ap.add_argument("--out", default=str(HERE / "live_crl_focus.html"))
    args = ap.parse_args()

    from tiled.client import from_profile
    from tiled.queries import Key

    cat = from_profile("auto")["smi"]["raw"]
    found = cat.search(Key("scan_name") == FINE_SCAN_NAME)
    # Oldest-first so the page lists holders in acquisition order (5 -> 4 -> 2 -> 3).
    items = sorted(found.items(), key=lambda kv: kv[1].metadata["start"]["time"])[-args.n:]
    if not items:
        raise SystemExit(f"no Tiled runs with scan_name={FINE_SCAN_NAME!r} found")

    report = _load_report_module().LiveFocusReport(args.out)
    for uid, run in items:
        start = dict(run.metadata["start"])
        df = run["primary"]["data"].read(variables=FIELDS).to_dataframe()
        rows = list(zip(df["energy_energy_setpoint"], df["piezo_x"], df["pil2M_stats1_total"]))
        report.rebuild_from_rows(start, rows)
        print(f"added holder {start.get('crl_holders')}  ({uid[:8]}, {len(rows)} points)")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

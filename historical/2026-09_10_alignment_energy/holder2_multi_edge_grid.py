"""HISTORICAL AD HOC PLAN — September/October 2026; see this directory's README.

Five K edges at WAXS 0/20, completing each holder2 sample before moving on.

In the configured beamline IPython session:
    %run -i ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/holder2_multi_edge_grid.py
    RE(run_holder2_edges())

S5 recovery (no previous data on S5):
    RE(run_s5_edges())
Continue after the last recorded grid_point=178:
    RE(run_s5_edges(start_point=179))
Uses a top-left grid starting 100 um above stored X, which itself is below
the reported -58164.9 um limit. Y starts at stored Y and increases.

Loading prints a preview only. Stored X is the grid's horizontal center;
stored Y is its minimum Y. All offsets are in micrometers and Y >= 0.
One fresh position per exposure, continuous across all edges and both angles.
Each invocation starts the same grid again; position usage is not persisted.
"""

import math

import bluesky.plan_stubs as bps
import numpy as np
from ophyd import Signal

from smi_plans import ListStore, bar_name_tokens, load_holder, resolve_list, sample_center
from smi_plans._compose import acquire, energy_axis
from smi_plans._core import goto_sample, saxs_waxs_dets

EDGE_LISTS = (
    ("MnK", "Mn K 1ev 87 pts"),
    ("FeK", "Fe K 1ev 87 pts"),
    ("CoK", "Co K 1ev 87 pts"),
    ("NiK", "Ni K 1ev 87 pts"),
    ("ZnK", "Zinc 1ev 80 pts"),
)
ARCS = (0.0, 20.0)
DX, DY = 100.0, 10.0


def top_middle_grid(n):
    """Fit n exposures in the closest-to-square physical footprint, Y fastest.

    For each possible column count use the minimum rows needed, then minimize
    the difference between physical width and height. Break ties by unused cells.
    """
    if n < 1:
        raise ValueError("At least one exposure is required")
    candidates = [(nx, math.ceil(n / nx)) for nx in range(1, n + 1)]
    nx, ny = min(candidates, key=lambda dims: (
        abs((dims[0] - 1) * DX - (dims[1] - 1) * DY),
        dims[0] * dims[1] - n,
    ))
    column, row = np.divmod(np.arange(n), ny)
    xs = column * DX - (nx - 1) * DX / 2
    ys = np.where(column % 2 == 0, row, ny - 1 - row) * DY
    return np.column_stack((xs, ys)), nx, ny


bar = load_holder("holder2")
store = ListStore.from_redis()
edge_scans = []
for edge_label, list_name in EDGE_LISTS:
    values = np.asarray(resolve_list(list_name, kind="energy", store=store), dtype=float)
    if values.ndim != 1 or not values.size or not np.isfinite(values).all():
        raise ValueError(f"{list_name!r} must be a nonempty, finite 1-D energy list")
    edge_scans.append((edge_label, list_name, values.tolist()))

events_per_sample = len(ARCS) * sum(len(values) for _, _, values in edge_scans)
offsets, nx, ny = top_middle_grid(events_per_sample)
centers = {}
for s in bar:
    cx, cy = sample_center(s)
    if cx is None or cy is None or not np.isfinite([cx, cy]).all():
        raise ValueError(f"{s.name!r} needs finite stored piezo_x and piezo_y")
    centers[s.id] = (float(cx), float(cy))


def fresh_energy_axis(values, center, first_point, point_signal, *, grid_offsets=None):
    """Use energy_axis's per-point hook to visit this run's slice of the grid."""
    axis = energy_axis(values, settle=2)
    energy_hook = axis.per_point
    indices = iter(range(first_point, first_point + len(values)))
    cx, cy = center
    grid_offsets = offsets if grid_offsets is None else grid_offsets

    def move_spot():
        if energy_hook is not None:
            yield from energy_hook()
        index = next(indices)
        dx, dy = grid_offsets[index]
        yield from bps.mv(
            piezo.x, cx + float(dx), piezo.y, cy + float(dy),
            point_signal, index,
        )

    axis.per_point = move_spot
    axis.reads.extend([piezo.x, piezo.y, point_signal])
    return axis


def run_holder2_edges(*, sample_names=None, anchor="top_middle", x_shift_um=0.0,
                      start_point=0):
    """One run per sample/angle/edge; sample outermost, continuous fresh XY grid.

    sample_names selects stored names case-insensitively (None means all).
    anchor='top_left' places all X offsets >= 0; Y offsets are always >= 0.
    x_shift_um adds an absolute offset to the grid anchor, not the stored sample.
    start_point skips earlier exposures without resizing/recentering the grid.
    """
    if anchor not in ("top_middle", "top_left"):
        raise ValueError("anchor must be 'top_middle' or 'top_left'")
    if not np.isfinite(x_shift_um):
        raise ValueError("x_shift_um must be finite")
    if not isinstance(start_point, int) or not 0 <= start_point < events_per_sample:
        raise ValueError(f"start_point must be an integer in [0, {events_per_sample - 1}]")
    selected = list(bar)
    if sample_names is not None:
        if isinstance(sample_names, str):
            sample_names = [sample_names]
        wanted = {name.strip().casefold() for name in sample_names}
        selected = [s for s in bar if s.name.strip().casefold() in wanted]
        missing = wanted - {s.name.strip().casefold() for s in selected}
        if missing or not selected:
            raise ValueError(f"No matching samples for {sorted(missing or wanted)}")
    grid_offsets = offsets.copy()
    if anchor == "top_left":
        grid_offsets[:, 0] -= grid_offsets[:, 0].min()
    grid_offsets[:, 0] += x_shift_um

    yield from det_exposure_time(1, 1)
    for s in selected:
        cx, cy = centers[s.id]
        print(f"{s.name}: X [{cx + grid_offsets[:, 0].min():g}, "
              f"{cx + grid_offsets[:, 0].max():g}], "
              f"Y [{cy:g}, {cy + grid_offsets[:, 1].max():g}] um")
        # Restore the other recorded axes, but move XY directly to the first
        # grid point. The stored X itself may be outside the current limits.
        yield from goto_sample(s, skip={piezo.x, piezo.y})
        yield from bps.mv(
            piezo.x, cx + float(grid_offsets[start_point, 0]),
            piezo.y, cy + float(grid_offsets[start_point, 1]),
        )
        first_point = 0
        point_signal = Signal(name="grid_point", value=0)
        for arc in ARCS:
            arc_points = sum(len(values) for _, _, values in edge_scans)
            if first_point + arc_points <= start_point:
                first_point += arc_points
                continue
            yield from bps.mv(waxs.arc, arc)
            dets = saxs_waxs_dets()  # Must select after the arc move.
            for edge_label, list_name, values in edge_scans:
                stop_point = first_point + len(values)
                if stop_point <= start_point:
                    first_point = stop_point
                    continue
                skip = max(0, start_point - first_point)
                values = values[skip:]
                first_point += skip
                print(f"{s.name}: WAXS={arc:g}, {edge_label}, "
                      f"grid points {first_point}–{first_point + len(values) - 1}")
                axis = fresh_energy_axis(
                    values, centers[s.id], first_point, point_signal,
                    grid_offsets=grid_offsets,
                )
                tokens = bar_name_tokens(
                    arc, arc_fmt="wa{:04.1f}", include_energy=True,
                    include_arc=True, include_incidence=False,
                    extra_tokens=[edge_label],
                )
                yield from acquire(
                    s.name, dets, [axis], sample=s,
                    reads=[energy, waxs, xbpm2, xbpm3],
                    geometry="transmission", scan_name="holder2_multi_edge_grid",
                    name_tokens=tokens,
                    md={
                        "sample_id": s.id, "holder_id": s.holder_id,
                        "edge_label": edge_label, "energy_list": list_name,
                        "waxs_arc_target": arc,
                        "grid": {
                            "nx": nx, "ny": ny, "dx_um": DX, "dy_um": DY,
                            "anchor_xy_um": [cx + x_shift_um, cy],
                            "stored_xy_um": list(centers[s.id]),
                            "anchor": anchor + "_minimum_y",
                            "x_shift_um": x_shift_um,
                            "resume_start_point": start_point,
                            "first_point": first_point,
                            "stop_point_exclusive": first_point + len(values),
                            "total_points": events_per_sample,
                        },
                    },
                )
                first_point += len(values)
        assert first_point == events_per_sample


def run_s5_edges(*, start_point=0, fresh_grid=False):
    """Complete S5, optionally skipping earlier events and using a fresh X block.

    Continue after recorded grid_point 178, preserving original XY mapping:
        RE(run_s5_edges(start_point=179))
    Alternatively restart WAXS=0 CoK from the beginning on a fresh block:
        RE(run_s5_edges(start_point=174, fresh_grid=True))
    fresh_grid shifts an additional full grid width plus one X step (1000 um).
    It is a fixed second block, not a persistent fresh-position allocator.
    """
    yield from run_holder2_edges(
        sample_names=["s5"], anchor="top_left",
        x_shift_um=100.0 + (nx * DX if fresh_grid else 0.0),
        start_point=start_point,
    )


print(f"holder2: {len(bar)} samples, {len(edge_scans)} edges, arcs {ARCS}")
print(f"{events_per_sample} exposures/sample; "
      f"{len(bar) * events_per_sample} exposures total; "
      f"{len(bar) * len(ARCS) * len(edge_scans)} runs")
print(f"Grid: {nx} X columns × {ny} Y rows, spacing {DX:g} × {DY:g} um")
print(f"Offsets: X [{offsets[:, 0].min():g}, {offsets[:, 0].max():g}], "
      f"Y [{offsets[:, 1].min():g}, {offsets[:, 1].max():g}] um")
for s in bar:
    cx, cy = centers[s.id]
    print(f"  {s.name}: X [{cx + offsets[:, 0].min():g}, "
          f"{cx + offsets[:, 0].max():g}], "
          f"Y [{cy:g}, {cy + offsets[:, 1].max():g}] um")
print("Run: RE(run_holder2_edges())")
print("S5 only, top-left +100 um X: RE(run_s5_edges())")

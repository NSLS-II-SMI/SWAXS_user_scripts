"""HISTORICAL AD HOC PLAN — September/October 2026; see this directory's README.

holder1 NEXAFS: AGB at energy endpoints, samples on a centered fresh-spot snake.

Load in the configured beamline IPython session with:
    %run -i ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/saxs_nexafs_snake.py
Then acquire with:
    RE(run_plan(mode="waxs0", start_block=1))  # Recovery after the original scan.

For a new, unexposed sample set, acquire both angles with:
    RE(run_plan(mode="both", start_block=0))

Blocks are not tracked persistently. Block 0 is the original centered snake;
each subsequent block is shifted in +X beyond the preceding block's columns.
Keep the same energy list, step sizes, and stored centers when recovering.

Piezo coordinates and step sizes are in micrometers. Each column has 20 Y
moves (21 measurement positions); the next energy starts the adjacent column.
"""

import numpy as np
import bluesky.plan_stubs as bps

from smi_plans import (
    ListStore, apply_name_prefix, bar_name_tokens, load_holder, resolve_list,
    sample_center,
)
from smi_plans._compose import acquire_bar, energy_axis
from smi_plans._core import saxs_waxs_dets


AGB_NAME = "AGB"                 # Exact stored name, case-insensitive.
Y_STEPS = 20                    # 20 moves = 21 positions per column.
DY = 10.0                      # um
DX = 100.0                     # um; advance in +X between columns.

bar = load_holder("holder1")
# Select before applying any filename prefix.
agbs = [s for s in bar if s.name.strip().casefold() == AGB_NAME.casefold()]
samples = [s for s in bar if s not in agbs]
if len(agbs) != 1 or not samples:
    raise ValueError(
        "Expected one AGB and at least one sample; holder names: "
        + repr([s.name for s in bar])
    )

lists = ListStore.from_redis()
energies = np.asarray(resolve_list("Sk_dense", kind="energy", store=lists), dtype=float)
if energies.ndim != 1 or not len(energies) or not np.isfinite(energies).all():
    raise ValueError("Sk_dense must be a nonempty, finite 1-D energy list")
agb_energies = sorted(set([float(energies.min()), float(energies.max())]))

# One XY pair per energy, preserving the energy list's original order.
column, row = np.divmod(np.arange(len(energies)), Y_STEPS + 1)
x_offsets = column.astype(float) * DX
y_offsets = np.where(column % 2 == 0, Y_STEPS - row, row).astype(float) * DY
# Center the visited bounding box, including a partially filled final column.
x_offsets -= (x_offsets.min() + x_offsets.max()) / 2
y_offsets -= (y_offsets.min() + y_offsets.max()) / 2
block_pitch = float(x_offsets.max() - x_offsets.min() + DX)

centers = {}
for s in bar:
    cx, cy = sample_center(s)
    if cx is None or cy is None:
        raise ValueError(f"{s.name!r} needs stored piezo_x and piezo_y coordinates")
    centers[s.id] = (float(cx), float(cy))

name_spec = {
    "include_energy": True, "include_arc": True,
    "include_incidence": False, "arc_fmt": "wa{:04.1f}",
}
for s in bar:
    s.name = apply_name_prefix(s.name, name_spec)

reads = [energy, waxs, xbpm2, xbpm3, piezo.x, piezo.y]


def axes_for(s, block=0):
    cx, cy = centers[s.id]
    cx += block * block_pitch
    axis = energy_axis(energies, settle=2)
    spots = iter(zip(x_offsets, y_offsets))
    energy_hook = axis.per_point

    def move_spot():
        if energy_hook is not None:
            yield from energy_hook()
        dx, dy = next(spots)
        # Absolute targets avoid accumulated offsets and repeat correctly on replay.
        yield from bps.mv(
            piezo.x, cx + float(dx),
            piezo.y, cy + float(dy),
        )

    # Built-in hook runs after energy settles, before each measurement.
    axis.per_point = move_spot
    return [axis]


def run_plan(*, mode="waxs0", start_block=1):
    """Acquire selected angles on explicit, non-overlapping position blocks.

    mode: 'waxs0' (0 degrees), 'simultaneous' (20 degrees), or 'both' (20 then 0).
    start_block: 0 for unused samples; 1 skips the original completed snake.
    Each angle consumes one block. AGB uses a stationary spot shifted by
    block * DX, with only the two endpoint energies at that spot.
    Defaults perform the missing WAXS=0 scan on fresh block 1.
    """
    modes = {"waxs0": (0.0,), "simultaneous": (20.0,), "both": (20.0, 0.0)}
    if mode not in modes:
        raise ValueError("mode must be 'waxs0', 'simultaneous', or 'both'")
    if not isinstance(start_block, int) or start_block < 0:
        raise ValueError("start_block must be a nonnegative integer")

    yield from det_exposure_time(1, 1)
    for block, arc in enumerate(modes[mode], start=start_block):
        print(f"WAXS={arc:g}, block={block}: sample X offsets "
              f"[{x_offsets.min() + block * block_pitch:g}, "
              f"{x_offsets.max() + block * block_pitch:g}] um")
        yield from bps.mv(waxs.arc, arc)
        # Select AFTER the arc move: at zero, SAXS is blocked and is excluded.
        dets = saxs_waxs_dets()
        name_tokens = bar_name_tokens(
            arc, arc_fmt="wa{:04.1f}", include_arc=True,
            include_energy=True, include_incidence=False,
        )
        md = {"position_block": block, "waxs_arc_target": arc,
              "sample_x_shift_um": block * block_pitch}

        def setup_agb(s):
            cx, cy = centers[s.id]
            yield from bps.mv(piezo.x, cx + block * DX, piezo.y, cy)

        # One stationary AGB run per angle, with only low and high energies.
        yield from acquire_bar(
            agbs, dets, lambda s: [energy_axis(agb_energies, settle=2)],
            setup_for=setup_agb, reads=reads, geometry="transmission",
            scan_name="saxs_NEXAFS_AGB", name_tokens=name_tokens,
            md={"position_block": block, "waxs_arc_target": arc,
                "sample_x_shift_um": block * DX},
        )
        yield from acquire_bar(
            samples, dets, lambda s: axes_for(s, block), reads=reads,
            geometry="transmission", scan_name="saxs_NEXAFS",
            name_tokens=name_tokens, md=md,
        )


print("AGB:", [s.name for s in agbs], "at energies", agb_energies)
print("Samples:", [s.name for s in samples])
print(f"{len(energies)} events/sample; "
      f"{len(samples) * len(energies) + len(agb_energies)} events per arc")
print(f"Block 0 offsets (um): X [{x_offsets.min():g}, {x_offsets.max():g}], "
      f"Y [{y_offsets.min():g}, {y_offsets.max():g}]")
print(f"Each fresh block shifts samples +{block_pitch:g} um in X; AGB +{DX:g} um.")
print("Recovery: RE(run_plan(mode='waxs0', start_block=1))")
# RE(run_plan(mode="waxs0", start_block=1))

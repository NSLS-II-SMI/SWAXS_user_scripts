"""
Clean bar-plan examples built on ``smi_plans``.

This file is intentionally small.  The reusable machinery now lives in ``smi_plans``:
holder loading, alignment persistence, position moves, filename-token helpers, scan axes,
acquisition envelopes, and fresh-spot wrappers.

Typical use in the live beamline session::

    %run -i /home/xf12id/SWAXS_user_scripts/bar_plans.py

    preview_name("s1", arc=15, exposure=1.0,
                 name_spec={"include_energy": False,
                            "include_exposure": True,
                            "arc_fmt": "waxs_{:.0f}",
                            "extra_tokens": ["px_{piezo_x:.1f}",
                                             "py_{piezo_y:.1f}",
                                             "pz_{piezo_z:.1f}"]})

    RE(transmission_bar_grid("holder1", "PGao", waxs_arc=(15, 25, 35), nx=1, ny=1,
                             name_spec={"include_energy": False,
                                        "include_exposure": True,
                                        "arc_fmt": "waxs_{:.0f}",
                                        "extra_tokens": ["px_{piezo_x:.1f}",
                                                         "py_{piezo_y:.1f}",
                                                         "pz_{piezo_z:.1f}"]}))

The helper functions ``preview_name``, ``adjust_bar_positions``, and ``sort_bar_by_name`` are
imported directly from ``smi_plans`` and are safe to call at the console without ``RE(...)``.
"""

import numpy as np
import bluesky.plan_stubs as bps

import smi_plans._compose as _compose
import smi_plans._core as _core
from smi_plans import (
    load_holder,
    resolve_list,
    sample_center,
    get_aligned,
    needs_alignment,
    save_aligned,
    bar_name_tokens,
    apply_name_prefix,
    preview_name,
    adjust_bar_positions,
    sort_bar_by_name,
)
from smi_plans._compose import (
    ScanAxis,
    SPEED_MEDIUM,
    acquire,
    incidence_axis,
    move_energy_fb,
    spatial_grid_axes,
)
from smi_plans._core import goto_sample
from smi_plans._preprocessors import fresh_spot_wrapper


__all__ = [
    "preview_name",
    "adjust_bar_positions",
    "sort_bar_by_name",
    "transmission_bar_grid",
    "transmission_bar_energies",
    "giwaxs_bar_energy",
]


ARC_SAXS_BLOCK_DEG = 30


def _dev(name):
    """Return a beamline global injected into ``smi_plans`` or this `%run -i` namespace."""
    if hasattr(_compose, name):
        return getattr(_compose, name)
    obj = globals()[name]
    # Some sessions inject devices into smi_plans at startup; `%run -i` sessions may only have them
    # in the IPython namespace.  Keep smi_plans' global-based helpers usable either way.
    setattr(_compose, name, obj)
    setattr(_core, name, obj)
    return obj


def _run_md(project, md=None):
    out = dict(md or {})
    if project is not None:
        out.setdefault("project_name", project)
    return out


def _dets_at_arc(arc_value, *, use_saxs=True, use_waxs=True, arc_block_deg=ARC_SAXS_BLOCK_DEG):
    dets = []
    if use_waxs:
        dets.append(_dev("pil900KW"))
    if use_saxs and float(arc_value) >= float(arc_block_deg):
        dets.append(_dev("pil2M"))
    return dets


def _grid_offsets(nx, ny, dx, dy):
    xs = (np.arange(nx) - (nx - 1) / 2.0) * dx if nx > 1 else np.array([0.0])
    ys = (np.arange(ny) - (ny - 1) / 2.0) * dy if ny > 1 else np.array([0.0])
    return list(xs), list(ys)


def _grid_axes(cx, cy, ox, oy, *, snake=True):
    piezo = _dev("piezo")
    return spatial_grid_axes(
        x_motor=piezo.x,
        x=[cx + d for d in ox],
        y_motor=piezo.y,
        y=[cy + d for d in oy],
        center=(cx, cy),
        snake=snake,
    )


def _filtered_name_tokens(arc_value, *, grid=False, incidence=False, name_spec=None):
    spec = {k: v for k, v in (name_spec or {}).items()
            if k not in ("grid", "include_incidence")}
    return bar_name_tokens(arc_value, grid=grid, include_incidence=incidence, **spec)


def _record_exposure_if_needed(t, reads, name_spec):
    if not (name_spec or {}).get("include_exposure"):
        return None
    sig = _dev("Signal")(name="exposure_s", value=float(t))
    yield from bps.mv(sig, float(t))
    reads.append(sig)
    return sig


def _energy_axis(energies, *, settle=2.0):
    """Energy axis that relies on the naming preprocessor to record ``{energy_energy}`` once."""
    return ScanAxis(
        "energy",
        list(energies),
        move=lambda value: move_energy_fb(value, settle=settle),
        speed=SPEED_MEDIUM,
    )


def transmission_bar_grid(holder_name, project=None, *, t=1.0, waxs_arc=(0,),
                          nx=3, ny=3, dx=150.0, dy=150.0, name_spec=None,
                          use_saxs=True, use_waxs=True, store=None, md=None,
                          arc_block_deg=ARC_SAXS_BLOCK_DEG):
    """Transmission SAXS/WAXS over a holder, one run per ``(sample, WAXS arc)``.

    This is the clean replacement for the old hand-written grid plan.  Samples are loaded by holder
    name from the ``smi_plans`` store; positions come from each sample's runnable Position; filename
    tokens come from ``smi_plans.bar_name_tokens``.
    """
    bar = load_holder(holder_name, store=store)
    reads = [_dev("xbpm2"), _dev("xbpm3"), _dev("pin_diode"), _dev("piezo")]
    ox, oy = _grid_offsets(nx, ny, dx, dy)
    run_md = _run_md(project, md)

    print("\n=== transmission_bar_grid: holder={!r}, samples={}, arcs={} ===".format(
        holder_name, len(bar), list(waxs_arc)))
    yield from _dev("det_exposure_time")(t, t)
    yield from _record_exposure_if_needed(t, reads, name_spec)

    for arc_value in waxs_arc:
        dets = _dets_at_arc(
            arc_value, use_saxs=use_saxs, use_waxs=use_waxs, arc_block_deg=arc_block_deg)
        print("\n=== WAXS arc = {} deg; dets = {} ===".format(
            arc_value, ", ".join(d.name for d in dets)))
        yield from bps.mv(_dev("waxs").arc, arc_value)
        yield from bps.sleep(1)
        for i, sample in enumerate(bar, 1):
            cx, cy = sample_center(sample)
            if cx is None or cy is None:
                print("  !! skip {}/{} {}: missing piezo_x/piezo_y".format(
                    i, len(bar), sample.name))
                continue
            print("  >>> {}/{} {} @ arc {}".format(i, len(bar), sample.name, arc_value))
            yield from goto_sample(sample)
            axes = _grid_axes(cx, cy, ox, oy) if nx * ny > 1 else []
            yield from acquire(
                apply_name_prefix(sample.name, name_spec),
                dets,
                axes,
                reads=reads,
                geometry="transmission",
                scan_name="transmission_grid",
                sample=sample,
                md=run_md,
                name_tokens=_filtered_name_tokens(
                    arc_value, grid=(nx * ny > 1), name_spec=name_spec),
                check_order=False,
            )


def transmission_bar_energies(holder_name, project=None, *, energies, t=1.0,
                              waxs_arc=(0,), nx=1, ny=1, dx=150.0, dy=150.0,
                              fresh_step=1.0, name_spec=None, use_saxs=True,
                              use_waxs=True, store=None, md=None,
                              arc_block_deg=ARC_SAXS_BLOCK_DEG):
    """Transmission energy scan over a holder, optionally with a small spatial grid.

    ``energies`` may be an explicit list or a stored list name resolved by ``smi_plans.resolve_list``.
    A nonzero ``fresh_step`` walks ``piezo.y`` after each frame when no y-grid is active.
    """
    bar = load_holder(holder_name, store=store)
    energies = resolve_list(energies, kind="energy")
    reads = [_dev("xbpm2"), _dev("xbpm3"), _dev("pin_diode"), _dev("piezo")]
    ox, oy = _grid_offsets(nx, ny, dx, dy)
    do_fresh = bool(fresh_step) and ny <= 1
    run_md = _run_md(project, md)

    print("\n=== transmission_bar_energies: holder={!r}, samples={}, energies={}, arcs={} ===".format(
        holder_name, len(bar), len(energies), list(waxs_arc)))
    yield from _dev("det_exposure_time")(t, t)
    yield from _record_exposure_if_needed(t, reads, name_spec)

    for arc_value in waxs_arc:
        dets = _dets_at_arc(
            arc_value, use_saxs=use_saxs, use_waxs=use_waxs, arc_block_deg=arc_block_deg)
        print("\n=== WAXS arc = {} deg; dets = {} ===".format(
            arc_value, ", ".join(d.name for d in dets)))
        yield from bps.mv(_dev("waxs").arc, arc_value)
        yield from bps.sleep(1)
        for i, sample in enumerate(bar, 1):
            cx, cy = sample_center(sample)
            if cx is None or cy is None:
                print("  !! skip {}/{} {}: missing piezo_x/piezo_y".format(
                    i, len(bar), sample.name))
                continue
            print("  >>> {}/{} {} @ arc {}".format(i, len(bar), sample.name, arc_value))
            yield from goto_sample(sample)
            axes = [_energy_axis(energies, settle=2.0)]
            if nx * ny > 1:
                axes += _grid_axes(cx, cy, ox, oy)
            plan = acquire(
                apply_name_prefix(sample.name, name_spec),
                dets,
                axes,
                reads=reads,
                geometry="transmission",
                scan_name="transmission_energy",
                sample=sample,
                md=run_md,
                name_tokens=_filtered_name_tokens(
                    arc_value, grid=(nx * ny > 1), name_spec=name_spec),
                check_order=False,
            )
            if do_fresh:
                plan = fresh_spot_wrapper(plan, _dev("piezo").y, fresh_step)
            yield from plan


def giwaxs_bar_energy(holder_name, project=None, *, energies,
                      incident_angles=(0.08, 0.12, 0.16), t=1.0,
                      waxs_arc=(0, 20), align_arc=20, align_angle=0.15,
                      realign=False, fresh_step=-100.0, name_spec=None,
                      use_saxs=True, use_waxs=True, store=None, md=None,
                      arc_block_deg=ARC_SAXS_BLOCK_DEG, align=None):
    """GIWAXS energy scan over a holder with cached per-sample alignment.

    Alignment is performed once per sample and persisted via ``smi_plans.save_aligned``.  Energy and
    incidence are composed as scan axes; the fresh-spot walk is handled by ``fresh_spot_wrapper``.
    """
    bar = load_holder(holder_name, store=store)
    energies = resolve_list(energies, kind="energy")
    angles = resolve_list(incident_angles, kind="incidence")
    reads = [_dev("xbpm2"), _dev("xbpm3"), _dev("piezo")]
    run_md = _run_md(project, md)
    piezo = _dev("piezo")
    align = align or _dev("alignment_gisaxs")

    print("\n=== giwaxs_bar_energy: holder={!r}, samples={}, energies={}, angles={} ===".format(
        holder_name, len(bar), len(energies), len(angles)))

    yield from bps.mv(_dev("waxs").arc, align_arc)
    yield from bps.sleep(1)
    for i, sample in enumerate(bar, 1):
        if needs_alignment(sample, force=realign):
            print("  [align {}/{}] {}".format(i, len(bar), sample.name))
            yield from goto_sample(sample)
            yield from align(align_angle)
            yield from save_aligned(bar, sample, piezo.th.position, piezo.y.position)
        else:
            th0, y0 = get_aligned(sample)
            print("  [skip  {}/{}] {} already aligned: th0={:.4f}, y={:.1f}".format(
                i, len(bar), sample.name, th0, y0))

    yield from _dev("det_exposure_time")(t, t)
    yield from _record_exposure_if_needed(t, reads, name_spec)

    for arc_value in waxs_arc:
        dets = _dets_at_arc(
            arc_value, use_saxs=use_saxs, use_waxs=use_waxs, arc_block_deg=arc_block_deg)
        print("\n=== WAXS arc = {} deg; dets = {} ===".format(
            arc_value, ", ".join(d.name for d in dets)))
        yield from bps.mv(_dev("waxs").arc, arc_value)
        yield from bps.sleep(1)
        for i, sample in enumerate(bar, 1):
            th0, y0 = get_aligned(sample)
            print("  >>> {}/{} {} @ arc {}".format(i, len(bar), sample.name, arc_value))
            yield from goto_sample(sample, skip={piezo.y, piezo.th})
            yield from bps.mv(piezo.y, y0)
            plan = acquire(
                apply_name_prefix(sample.name, name_spec),
                dets,
                [_energy_axis(energies, settle=2.0), incidence_axis(piezo.th, th0, angles)],
                reads=reads,
                geometry="reflection",
                scan_name="giwaxs_energy",
                sample=sample,
                md=run_md,
                name_tokens=_filtered_name_tokens(
                    arc_value, incidence=True, name_spec=name_spec),
                check_order=False,
            )
            yield from fresh_spot_wrapper(plan, piezo.x, fresh_step)

"""Review settings, load with %run -i, preview_crl_series(), then RE(crl_focus_series()).

Importing/loading this file does not connect to or move hardware. Live devices are
looked up only when preview_crl_series() / crl_focus_series() are called. Energy
moves use the beamline RunEngine's installed managed-energy-move preprocessor.
"""

import math
import os

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
import numpy as np
from bluesky.utils import FailedStatus
from smi_beamline.devices.attenuator_data import FOIL_LAYOUT, attenuation_factor, foil_description
from smi_beamline.devices.crl_optics import CRLModel
from smi_beamline.plans.harmonic_lock import with_harmonic_lock

# Captured at load (defined under %run -i and importlib) so the optional live-report
# module can be found next to this script without relying on sys.path.
try:
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:  # pragma: no cover - only if run without a file context
    _SCRIPT_DIR = None

# ------------------------ EDIT THESE SETTINGS -------------------------------
# Measured per-holder alignment from beam-position snapshots, all taken (or treated) at
# crl.z = 0. "in_mm" is the holder's lens insertion position; crl_x/crl_y steer the
# focused beam onto the sample knife edge. Holder 3's x/y were snapshotted at z=+200 and
# are only a starting guess at z=0 -- the coarse piezo.x scan is what locates the edge.
HOLDER_ALIGNMENT = {
    2: {"in_mm": -1.1801, "crl_x_mm": -8.5766, "crl_y_mm": -9.75},
    3: {"in_mm": -0.22,   "crl_x_mm": -8.5764, "crl_y_mm": -9.9878},
    4: {"in_mm": -0.8099, "crl_x_mm": -9.447,  "crl_y_mm": -9.77},
    5: {"in_mm": -0.6993, "crl_x_mm": -12.667, "crl_y_mm": -9.82},
}
# Nominal OUT (withdrawn) positions from the CRL device itself (LensHolder.out_mm):
# +10 mm for holders 1–6, −10 mm for 7–12. These are well inside the soft limits.
# (The earlier snapshot readbacks — e.g. lens6 +12.355, lens7/8 ≈ −14.99 — sat at or
# past the limits, so commanding them tripped check_value before any motion.)
OUT_POSITIONS_MM = {i: (10.0 if i <= 6 else -10.0) for i in range(1, 13)}
CRL_Z_MM = 0.0                    # all holders run at z=0 to find the real focus there
HOLDER_SETS = ((5,), (4,), (2,), (3,))  # individual holders, ascending focus energy
ENERGY_LIMITS_EV = (6000.0, 24000.0)
ENERGY_HALF_RANGE_FRACTION = 0.08  # ±8% around model focus, clipped to 6–24 keV
ENERGY_POINTS = 21
# Optional explicit ranges, e.g. {(3,): (16000, 18000)}; keys are holder tuples.
ENERGY_RANGES_EV = {}
EDGE_CENTER_UM = -14705.0         # nominal center of the coarse edge search (starting guess)
COARSE_HALF_RANGE_UM = 400.0      # ±400 µm coarse knife-edge search around EDGE_CENTER_UM
COARSE_POINTS = 81                # 10 µm steps
EDGE_HALF_RANGE_UM = 60.0         # fine window ±60 µm around the found edge (120 µm total)
EDGE_POINTS = 61                 # 2 µm steps
EXPOSURE_S = 0.5
ENERGY_SETTLE_S = 2.0
LENS_SETTLE_S = 2.0
# Attenuation policy: ONE foil per holder, inserted once and left for the whole sweep
# (changing foils mid-scan can disturb the focused beam, and the per-energy selector
# mis-selected a near-opaque stack).  The foil is sized at the BRIGHTEST (highest) energy
# of the window so attenuation stays >= ATTENUATION_MIN_FACTOR across the whole sweep; at
# lower energies the same foil attenuates more (recorded, not corrected).  The varying
# attenuation_factor is read at every point.
#
# 1500x is the calibrated sweet spot (ref scan 1170759: 538x -> ~38M counts): bright-end
# counts stay 0.4-7M (>=6x headroom below the reference plateau) while every window's dim
# end stays measurable (>= ~900 counts).  A single fixed foil swings 100-1000x across a
# window, so raising this much higher (e.g. 1e5) over-attenuates the dim ends to ~0 counts.
ATTENUATION_MIN_FACTOR = 1500.0
# Optional per-holder foil override, e.g. {5: "1_9"} to force a specific foil label.
FOIL_OVERRIDE = {}
# ---------------------------------------------------------------------------


def scan_specs(holder_sets=None):
    """Pure calculation using the current CRL report's 1600 mm / SSA geometry."""
    model = CRLModel()
    if not -300 <= CRL_Z_MM <= 300:
        raise ValueError("CRL_Z_MM must be in the reported -300..300 mm travel")
    specs = []
    for holders in HOLDER_SETS if holder_sets is None else holder_sets:
        holders = tuple(holders)
        focus_eV = 10000 * math.sqrt(
            model.power_per_m(10, holders) / model.geometry.required_power_per_m(CRL_Z_MM))
        low, high = ENERGY_RANGES_EV.get(holders, (
            max(ENERGY_LIMITS_EV[0], 50 * math.floor(focus_eV * (1 - ENERGY_HALF_RANGE_FRACTION) / 50)),
            min(ENERGY_LIMITS_EV[1], 50 * math.ceil(focus_eV * (1 + ENERGY_HALF_RANGE_FRACTION) / 50)),
        ))
        if not 6000 <= low < high <= 24000:
            raise ValueError(f"Invalid energy interval for {holders}: {low}, {high}")
        specs.append({"holders": holders, "focus_eV": focus_eV,
                      "start_eV": low, "stop_eV": high})
    if not specs:
        raise ValueError("Choose at least one holder combination")
    return specs


def _namespace(namespace):
    if namespace is not None:
        return namespace
    from IPython import get_ipython

    shell = get_ipython()
    if shell is None:
        raise RuntimeError("Run in the beamline IPython session or supply namespace=")
    return shell.user_ns


def preview_crl_series(holder_sets=None, *, namespace=None):
    """Print model windows and validate harmonic coverage; no hardware writes."""
    ns = _namespace(namespace)
    specs = scan_specs(holder_sets)
    print(f"CRL Z={CRL_Z_MM:g} mm; coarse ±{COARSE_HALF_RANGE_UM:g} µm ({COARSE_POINTS} pts) "
          f"then {ENERGY_POINTS} energies × {EDGE_POINTS} positions around the found edge; "
          f"{EXPOSURE_S:g} s/frame; single foil >= {ATTENUATION_MIN_FACTOR:g}x across each window")
    for spec in specs:
        h = ns["energy"].harmonic_for_range(spec["start_eV"], spec["stop_eV"])
        spec["harmonic"] = h
        align = HOLDER_ALIGNMENT.get(spec["holders"][0], {})
        foil = _single_foil(spec["start_eV"], spec["stop_eV"], spec["holders"][0])
        lo = attenuation_factor([foil], spec["stop_eV"])   # least attenuation (bright end)
        hi = attenuation_factor([foil], spec["start_eV"])  # most attenuation (dim end)
        print(f"holders {spec['holders']}: model focus {spec['focus_eV']/1000:.3f} keV; "
              f"scan {spec['start_eV']/1000:.3f}–{spec['stop_eV']/1000:.3f} keV; "
              f"harmonic {h}; IN {align.get('in_mm')}; "
              f"crl.x {align.get('crl_x_mm')}; crl.y {align.get('crl_y_mm')}; "
              f"foil att{foil} ({foil_description(foil).split(': ', 1)[-1]}) "
              f"atten {lo:.2g}–{hi:.2g}x")
    frames = len(specs) * (COARSE_POINTS + ENERGY_POINTS * EDGE_POINTS)
    print(f"{frames} frames (coarse + fine); exposure-only {frames*EXPOSURE_S/60:.1f} min; "
          f"about {frames*(588.43/441)/60:.0f} min at scan 1170759's frame cadence, "
          "plus long energy moves, threshold updates, and lens/x/y changes.")
    return specs


def _set_detector_energy(detector, energy_eV):
    """Waited version of the profile's Pilatus energy/half-energy threshold policy."""
    keV = energy_eV / 1000
    gain = 2 if keV < 7 else (1 if keV < 20 else 0)
    yield from bps.mv(detector.cam_energy, keV, detector.threshold, keV / 2,
                      detector.gain, gain)
    # Apply only after all setting writes finish.
    yield from bps.mv(detector.apply, 1)
    yield from bps.mv(detector.cam.energyset, keV)
    # Loading trimbits after ThresholdApply can take ~10 s; poll for up to ~45 s.
    yield from bps.sleep(1.0)
    for _ in range(180):
        actual_e = yield from bps.rd(detector.energy_read)
        actual_t = yield from bps.rd(detector.threshold_read)
        # cam1:GainMenu_RBV is not present on this IOC; read the menu setpoint, which
        # reflects the current selection (an mbbo GET returns the active value).
        actual_g = yield from bps.rd(detector.gain)
        if abs(actual_e - keV) <= 0.05 and abs(actual_t - keV / 2) <= 0.05 and int(actual_g) == gain:
            yield from bps.sleep(0.5)
            return
        yield from bps.sleep(0.25)
    raise RuntimeError(f"Pilatus threshold/gain readbacks did not confirm at {keV:g} keV")


def _edge_center(xs, totals):
    """Locate a knife-edge center from a coarse (piezo.x, stats-total) profile.

    Uses the peak of |d(total)/dx|: only the edge *position* is needed here, so this is
    deliberately polarity-agnostic (unlike the report's signed rising-edge fit, which
    measures width). Raises if the peak sits on a search boundary -- the edge was not
    bracketed and COARSE_HALF_RANGE_UM should be widened.
    """
    x = np.asarray(xs, dtype=float)
    y = np.asarray(totals, dtype=float)
    order = np.argsort(x)
    x, y = x[order], y[order]
    xc = (x[1:] + x[:-1]) / 2
    d = np.abs(np.diff(y) / np.diff(x))
    k = int(np.argmax(d))
    if k == 0 or k == len(d) - 1:
        raise RuntimeError("coarse edge at search boundary; widen COARSE_HALF_RANGE_UM")
    y0, y1, y2 = d[k - 1], d[k], d[k + 1]
    denom = y0 - 2 * y1 + y2
    delta = 0.5 * (y0 - y2) / denom if denom else 0.0  # parabolic sub-step refinement
    return float(xc[k] + delta * (xc[k + 1] - xc[k]))


def _single_foil(start_eV, stop_eV, holder=None):
    """Pick one foil giving >= ATTENUATION_MIN_FACTOR across [start, stop] eV.

    A fixed foil attenuates LEAST at the highest energy, so meeting the minimum at the
    bright end guarantees it across the window. Among qualifying single foils, pick the
    one whose worst-case (lowest-energy) attenuation is smallest -- i.e. the most signal.
    ``FOIL_OVERRIDE[holder]`` forces a specific label.
    """
    if holder is not None and holder in FOIL_OVERRIDE:
        label = FOIL_OVERRIDE[holder]
        if label not in FOIL_LAYOUT:
            raise ValueError(f"FOIL_OVERRIDE[{holder}]={label!r} is not a known foil label")
        return label
    grid = np.linspace(start_eV, stop_eV, ENERGY_POINTS)
    best = None  # (worst-case attenuation over the window, label)
    for label in FOIL_LAYOUT:
        facs = [attenuation_factor([label], e) for e in grid]
        if min(facs) >= ATTENUATION_MIN_FACTOR:
            key = max(facs)
            if best is None or key < best[0]:
                best = (key, label)
    if best is None:
        raise ValueError(
            f"No single foil reaches {ATTENUATION_MIN_FACTOR:g}x across "
            f"{start_eV:g}-{stop_eV:g} eV; lower ATTENUATION_MIN_FACTOR or set FOIL_OVERRIDE")
    return best[1]


def _mv_settle(*args, attempts=6, settle_s=1.5):
    """bps.mv with retries. CRL stage axes sometimes report a settle/following miss
    (FailedStatus: MoveStatus success=False) and need several attempts to settle in.
    A genuine fault still raises after the final attempt."""
    for attempt in range(1, attempts + 1):
        try:
            yield from bps.mv(*args)
            return
        except FailedStatus:
            if attempt == attempts:
                raise
            yield from bps.sleep(settle_s)


def _insert_single_foil(ns, label):
    """Insert exactly foil ``label`` (e.g. '1_5') and retract every other foil."""
    bank, pos = label.split("_")
    want1 = [f"f{pos}"] if bank == "1" else []
    want2 = [f"f{pos}"] if bank == "2" else []
    yield from bps.mv(ns["attenuators1"], want1, ns["attenuators2"], want2)


def _live_report_callback(report_path):
    """Load the optional live-report subscription from the module next to this script.

    ``report_path=True`` writes to ``live_crl_focus.html`` beside the script; a string
    path is used verbatim. Imported lazily so the plain plan stays import-clean/offline.
    """
    import importlib.util

    if _SCRIPT_DIR is None:
        raise RuntimeError("cannot locate live_focus_report.py (no script directory)")
    if report_path is True:
        report_path = os.path.join(_SCRIPT_DIR, "live_crl_focus.html")
    mod_path = os.path.join(_SCRIPT_DIR, "live_focus_report.py")
    spec = importlib.util.spec_from_file_location("live_focus_report", mod_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LiveFocusReport(report_path)


def crl_focus_series(holder_sets=None, *, namespace=None, report_path=None):
    """One grid run per fixed holder set, with a single fixed attenuation foil per holder.

    Keeps current CRL angles, SSA gaps, sample Y/Z, and detector geometry; sets crl.x/y
    per holder. One sized foil is inserted per holder and left for the whole sweep (its
    varying attenuation factor is recorded, not corrected). Returns run UIDs. On
    completion/error, restores exposure settings, leaving optics, energy, detector
    threshold, foils, and edge at their last positions. Does not auto-run on load.

    ``report_path`` (``True`` or a file path) installs a live Bokeh report that rewrites
    one self-refreshing HTML page after each sweep; leave ``None`` to disable.
    """
    ns = _namespace(namespace)
    specs = scan_specs(holder_sets)
    for spec in specs:
        if len(spec["holders"]) != 1:
            raise ValueError("per-holder x/y alignment requires single-holder sets")
    needed = {i for s in specs for i in s["holders"]}
    for i in needed:
        align = HOLDER_ALIGNMENT.get(i)
        if align is None or not all(math.isfinite(align.get(k, float("nan")))
                                    for k in ("in_mm", "crl_x_mm", "crl_y_mm")):
            raise ValueError(f"Fill HOLDER_ALIGNMENT[{i}] with measured in/x/y positions first")
    if (ENERGY_POINTS < 3 or EDGE_POINTS < 5 or COARSE_POINTS < 5 or EXPOSURE_S <= 0
            or EDGE_HALF_RANGE_UM <= 0 or COARSE_HALF_RANGE_UM <= 0 or ATTENUATION_MIN_FACTOR <= 1):
        raise ValueError("Invalid scan sampling/exposure/attenuation settings")
    energy, crl, piezo, detector, attenuation = [
        ns[k] for k in ("energy", "crl", "piezo", "pil2M", "attenuation")]
    # Validate all requested motor targets, harmonics, and foil feasibility before motion.
    crl.z.check_value(CRL_Z_MM)
    for i, position in OUT_POSITIONS_MM.items():
        getattr(crl, f"lens{i}").check_value(position)
    for i in needed:
        getattr(crl, f"lens{i}").check_value(HOLDER_ALIGNMENT[i]["in_mm"])
        crl.x.check_value(HOLDER_ALIGNMENT[i]["crl_x_mm"])
        crl.y.check_value(HOLDER_ALIGNMENT[i]["crl_y_mm"])
    # Cover both the coarse search and any fine window landing near its edge.
    reach = COARSE_HALF_RANGE_UM + EDGE_HALF_RANGE_UM
    for x in (EDGE_CENTER_UM - reach, EDGE_CENTER_UM + reach):
        piezo.x.check_value(x)
    for spec in specs:
        spec["harmonic"] = energy.harmonic_for_range(spec["start_eV"], spec["stop_eV"])
        # One foil for the whole window, sized at its brightest end (raises if none fits).
        spec["foil"] = _single_foil(spec["start_eV"], spec["stop_eV"], spec["holders"][0])
    camera = [detector.cam.acquire_time, detector.cam.acquire_period, detector.cam.num_images]
    previous = []
    for signal in camera:
        previous.append((signal, (yield from bps.rd(signal))))

    def body():
        # Preserve the profile's repeated exposure-setting convention, pil2M only.
        for _ in range(2):
            yield from bps.mv(detector.cam.acquire_time, EXPOSURE_S,
                              detector.cam.acquire_period, EXPOSURE_S + 0.001,
                              detector.cam.num_images, 1)
        uids = []
        for spec in specs:
            holders = spec["holders"]
            (holder,) = holders
            align = HOLDER_ALIGNMENT[holder]
            # Insert the single sized foil FIRST, so the beam is attenuated before any
            # energy move; it stays in for the whole holder (coarse + fine).
            yield from _insert_single_foil(ns, spec["foil"])
            # Withdraw first, then move body Z, align x/y, then insert the selected holder.
            for i, position in OUT_POSITIONS_MM.items():
                yield from _mv_settle(getattr(crl, f"lens{i}"), position)
            yield from _mv_settle(crl.z, CRL_Z_MM)
            yield from _mv_settle(crl.x, align["crl_x_mm"], crl.y, align["crl_y_mm"])
            yield from _mv_settle(getattr(crl, f"lens{holder}"), align["in_mm"])
            yield from bps.sleep(LENS_SETTLE_S)
            # Fixed sensitivity for the whole energy sweep, set from this holder's
            # theoretical central energy (threshold = central energy / 2).
            yield from _set_detector_energy(detector, spec["focus_eV"])
            label = "_".join(map(str, holders))

            # --- Coarse knife-edge scan at the model-focus energy: locate the edge. ---
            yield from bps.mv(energy, spec["focus_eV"])
            yield from bps.sleep(ENERGY_SETTLE_S)
            coarse = []

            def coarse_step(detectors, step, pos_cache):
                yield from bps.move_per_step(step, pos_cache)
                yield from bps.trigger_and_read(list(detectors) + list(step))
                x_rb = yield from bps.rd(piezo.x)
                total = yield from bps.rd(detector.stats1.total)
                coarse.append((float(x_rb), float(total)))

            coarse_md = {
                "sample_name": f"crl_coarse_edge_h{label}_z{CRL_Z_MM:g}",
                "scan_name": "crl_energy_focus_coarse",
                "crl_holders": list(holders), "crl_z_mm": CRL_Z_MM,
                "crl_x_mm": align["crl_x_mm"], "crl_y_mm": align["crl_y_mm"],
                "crl_in_positions_mm": {str(holder): align["in_mm"]},
                "coarse_energy_eV": spec["focus_eV"],
                "coarse_nominal_center_um": EDGE_CENTER_UM,
                "attenuation_foil": spec["foil"],
                "attenuation_min_factor": ATTENUATION_MIN_FACTOR,
                "reference_scan_id": 1170759,
            }
            yield from bp.scan(
                [detector, attenuation], piezo.x,
                EDGE_CENTER_UM - COARSE_HALF_RANGE_UM,
                EDGE_CENTER_UM + COARSE_HALF_RANGE_UM, COARSE_POINTS,
                per_step=coarse_step, md=coarse_md,
            )
            edge_center = _edge_center([c[0] for c in coarse], [c[1] for c in coarse])

            # --- Fine energy × knife-edge grid, centered on the found edge. ---
            last_energy = None

            def per_step(detectors, step, pos_cache):
                nonlocal last_energy
                e = float(step[energy])
                if last_energy != e:
                    # Foil is fixed for the whole sweep; only the energy changes per row.
                    yield from bps.mv(energy, e)
                    pos_cache[energy] = step[energy]
                    yield from bps.sleep(ENERGY_SETTLE_S)
                    last_energy = e
                yield from bps.move_per_step(step, pos_cache)
                yield from bps.trigger_and_read(list(detectors) + list(step))

            md = {
                "sample_name": f"crl_focus_h{label}_z{CRL_Z_MM:g}",
                "scan_name": "crl_energy_focus_commissioning",
                "crl_holders": list(holders), "crl_z_mm": CRL_Z_MM,
                "crl_x_mm": align["crl_x_mm"], "crl_y_mm": align["crl_y_mm"],
                "crl_in_positions_mm": {str(holder): align["in_mm"]},
                "model_focus_eV": spec["focus_eV"],
                "coarse_edge_center_um": edge_center,
                "coarse_edge_nominal_um": EDGE_CENTER_UM,
                "pilatus_sensitivity_energy_eV": spec["focus_eV"],
                "pilatus_sensitivity_policy": "fixed_at_holder_model_focus",
                "model_geometry": "sample 1600 mm at Z=0; SSA 10.5 m upstream",
                "attenuation_foil": spec["foil"],
                "attenuation_min_factor": ATTENUATION_MIN_FACTOR,
                "attenuation_policy": "single_foil_sized_at_window_bright_end",
                "reference_scan_id": 1170759,
            }
            reads = [detector, attenuation, detector.energy_read,
                     detector.threshold_read, detector.gain]
            plan = bp.grid_scan(
                reads, energy, spec["start_eV"], spec["stop_eV"], ENERGY_POINTS,
                piezo.x, edge_center - EDGE_HALF_RANGE_UM,
                edge_center + EDGE_HALF_RANGE_UM, EDGE_POINTS,
                per_step=per_step, md=md,
            )
            uid = yield from with_harmonic_lock(
                plan, spec["start_eV"], spec["stop_eV"], energy=energy,
                harmonic=spec["harmonic"],
            )
            uids.append(uid)
        return uids

    def cleanup():
        for signal, value in previous:
            yield from bps.mv(signal, value)

    inner = body()
    if report_path is not None:
        inner = bpp.subs_wrapper(inner, _live_report_callback(report_path))
    return (yield from bpp.finalize_wrapper(inner, cleanup()))

# Aligam GiSAXS sample
#


def run_saxs_SChan(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and scans a line of y spots, taking images at each (a transmission-geometry
    #   raster across the sample).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that builds
    #   the line of positions for you and records the position + beam into each saved image:
    #
    #     from smi_plans import map_line_run
    #     yield from map_line_run("nPS_97k", axis="y", center=0, size=1000, num=11,
    #                             dets=[pil2M, pil900KW], t=t)   # SAXS + current WAXS detector
    #     # (call it per sample, the way you loop below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your detector list 'dets' has TWO removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (the MAXS detector, removed with no replacement). Also
    #   the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan.
    #   See the ⚠️ notes on those lines below. (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "SC_"
    x_list = [20800, 5800, -7700, -22700]  #
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [-500, 500, 11]  # [2.64, 8.64, 2]
    x_range = [-500, 500, 6]
    samples = ["nPS_97k", "SC1-11_WD", "SC1-12_PS", "SC1-13_CS"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_scan(dets, piezo.y, *y_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [41000, 30000, 20400, 6650, -6750]  #
    y_list = [-2500, -500, -3500, -2000, -1000]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [
        [-4000, 4000, 161],
        [-3500, 3500, 141],
        [-3000, 3000, 121],
        [-3000, 3000, 121],
        [-3000, 3000, 121],
    ]
    x_range = [
        [-4000, 4000, 33],
        [-3500, 3500, 29],
        [-3000, 3000, 25],
        [-3000, 3000, 25],
        [-3000, 3000, 25],
    ]  # [2.64, 8.64, 2]
    samples = [
        "67-N_0p05",
        "76-4core_0p05",
        "76-6core_0p05",
        "76-8core_0p05",
        "76-10core_0p05",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [21450, 6450, -7950, -23950, -39350]  #
    y_list = [-2500, -1500, -3500, -6500, -4000]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [
        [-2500, 2500, 101],
        [-2500, 2500, 101],
        [-2500, 2500, 101],
        [-2500, 2500, 101],
        [-2500, 2500, 67],
    ]
    x_range = [
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
    ]  # [2.64, 8.64, 2]
    samples = [
        "76-8core_0p025_c",
        "76-6core_0p025_c",
        "76-4core_0p025_c",
        "67-N_0p025_c",
        "76-10core_0p15",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [40600, 24200, 10600, -4600, -14200, -25800, -35800]  #
    y_list = [-4000, -3500, -4500, -4500, -3500, -4500, -4500]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [
        [-2500, 2500, 67],
        [-2500, 2500, 67],
        [-2000, 2000, 54],
        [-2000, 2000, 54],
        [-2500, 2500, 51],
        [-2000, 2000, 41],
        [-2000, 2000, 41],
    ]
    x_range = [
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2000, 2000, 17],
        [-2000, 2000, 17],
        [-2500, 2500, 21],
        [-2000, 2000, 17],
        [-2000, 2000, 17],
    ]  # [2.64, 8.64, 2]
    samples = [
        "76-8core_0p15",
        "76-6core_0p15",
        "76-4core_0p15",
        "67-N_0p15",
        "76-10core_0p25",
        "76-8core_0p25",
        "76-6core_0p25",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_4(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [41800, 30500, 17100, 1400, -17300, -38600]  #
    y_list = [3000, 3500, 1500, 1500, 3000, 3000]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [
        [-2500, 2500, 51],
        [-2500, 2500, 51],
        [-2500, 2500, 51],
        [-2500, 2500, 51],
        [-2500, 2500, 51],
        [-2500, 2500, 51],
    ]
    x_range = [
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
        [-2500, 2500, 21],
    ]  # [2.64, 8.64, 2]
    samples = [
        "76-4core_0p25",
        "67-N_0p25",
        "76-10core_0p50",
        "76-8core_0p50",
        "76-6core_0p50",
        "76-4core_0p50",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_5(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [40700, 27900, 8600, -9500, -27400, -42800]  #
    y_list = [4000, 4000, 4000, 5000, 4000, 4000]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [
        [-3500, 3500, 71],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
    ]
    x_range = [
        [-3500, 3500, 29],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
        [-3500, 3500, 11],
    ]  # [2.64, 8.64, 2]
    samples = [
        "67-N_0p5",
        "76-10core_tkp",
        "76-8core_tkp",
        "76-6core_tkp",
        "76-4core_tkp",
        "67-N_tkp",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_RZA(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [800, -17800]  #
    y_list = [-5500, 4500]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [[1000, 2000, 14], [-4500, 4500, 121]]
    x_range = [[-8000, 8000, 65], [-7000, 7000, 57]]  # [2.64, 8.64, 2]
    samples = ["08-12core_Akron_top", "08-12core_Akron_bottom"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_RZA2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [-36400, 32800, 17000]  #
    y_list = [500, -500, -500]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [[-2000, 2000, 4], [-5000, 5000, 81], [-5000, 5000, 21]]
    x_range = [
        [-2000, 2000, 4],
        [-5000, 5000, 41],
        [-5000, 5000, 41],
    ]  # [2.64, 8.64, 2]
    samples = ["2thickKapton", "35-11core_0p0007_dps", "35-11core_0p02_dps"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_micro(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [40370, 19170, 4270, -13630]  #
    y_list = [-3500, -3000, -3000, -4500]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [[-225, 225, 151], [-225, 225, 151], [-225, 225, 151], [-225, 225, 151]]
    x_range = [
        [-750, 750, 41],
        [-750, 750, 41],
        [-750, 750, 41],
        [-750, 750, 41],
    ]  # [2.64, 8.64, 2]
    samples = ["76-10core_0p025", "76-10core_0p05", "76-10core_0p25", "76-6core_0p025"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_kraus_micro2(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping measurement — for each sample it drives to
    #   position and rasters a grid/line of x/y spots, taking images at each (a transmission-
    #   geometry map across the sample).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the position grid for you and records the
    #   position + beam into each saved image (no hand-built grid ranges or file names):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #                             x_num=..., y_num=..., dets=[pil2M, pil900KW], t=t)
    #     # (call it per sample; use map_line_run for a single-line scan.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: your 'dets' list has two removed cameras — 'pil300KW'
    #   (now 'pil900KW') and 'rayonix' (MAXS, removed with no replacement); and the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "AAK"
    x_list = [4270, -30230, -13630]  #
    y_list = [-3000, 2000, -4500]
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): TWO detectors on this line were removed and would error: (1) 'pil300KW' — the current WAXS detector is 'pil900KW' (it's a different camera, so check beam-center/calibration); (2) 'rayonix' (the MAXS detector) was removed with NO current replacement — drop it from this list or ask beamline staff. (pil2M/SAXS is fine.)
    y_range = [[-225, 225, 151], [-225, 225, 151], [-225, 225, 151]]
    x_range = [[-750, 750, 41], [-750, 750, 41], [-750, 750, 41]]  # [2.64, 8.64, 2]
    samples = ["76-10core_0p25", "76-8core_0p25", "76-6core_0p025"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.z, 5000)
    for x, y, sample, x_range, y_range in zip(
        x_list, y_list, samples, x_range, y_range
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.rel_grid_scan(dets, piezo.y, *y_range, piezo.x, *x_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def run_waxsRPI(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a WAXS arc scan — for each sample it drives to position and sweeps the
    #   WAXS detector arc through a range of angles, taking an image at each.
    # 💡 NEWER, EASIER WAY: 'smi_plans' can sweep the WAXS arc as an "axis" and records the
    #   arc angle + beam into each image; the arc-economy GIWAXS helpers handle this too:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("NPS-Cu_1_Shift", [pil900KW],
    #                        [motor_axis("wa", waxs, list(np.linspace(2.85, 44.85, 8)))])
    #   (Your script below still works as-is, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls must be run as a plan. See the ⚠️ notes below.
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    name = "SP"
    x_list = [4000, 4500, 12000, 18000]  #
    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    y_range = [0, 0, 1]
    waxs_arc = [2.85, 44.85, 8]
    samples = [
        "NPS-Cu_1_Shift",
        "NPS-Cu_2_Shift",
        "NPS-Cu_160c_1_Shift",
        "NPS-Cu_160c_2_Shift",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)
        sample_id(user_name=name, sample_name=sample)
        yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def linkam_fast(n=6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick SAXS scan down the sample y while the (Linkam) heating stage is
    #   in use — it retracts the shutter, scans y in n steps, then re-inserts the shutter.
    # 💡 smi_plans: for Linkam temperature work see linkam_heater + temperature_ramp_run /
    #   goto_temperature, which set the temperature and record it into each image for you. The
    #   y scan itself maps to map_line_run. Nothing here is broken (pil2M/stage.y are fine).
    # === end smi_plans note ================================================
    yield from bps.mv(attn_shutter, "Retract")
    yield from bp.scan([pil2M], stage.y, 0.1, 0.9, n)
    yield from bps.mv(attn_shutter, "Insert")

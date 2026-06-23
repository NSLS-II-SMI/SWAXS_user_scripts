def mapping_saxs_Greer(t=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each WAXS-arc angle, visits each sample and raster-scans a small
    #   x/y grid (a 2-D map), taking SAXS+WAXS+fluorescence at every grid point.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a ready
    #   map-runner that does the grid for you and records the WAXS-arc, beam, and detector
    #   distance into the data + file name (no hand-built "{sam}_wa{waxs}deg"). For a single
    #   sample's grid it looks like (per-sample x/y ranges as in your x_range/y_range):
    #
    #     from smi_plans import map_grid_run         # do this once per session
    #     yield from map_grid_run(
    #         "SPYZ_90deg",
    #         piezo.x, 0, -300, 16,                  # x: start, stop, npts (relative to sample)
    #         piezo.y, 0, -60, 31,                   # y: start, stop, npts
    #         t=t, dets=[pil2M, pil900KW, amptek],
    #     )
    #     # ...wrap several of these with smi_plans.map_bar(...) to loop the whole bar + arc.
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT for the
    #    lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses the retired 'pil300KW' WAXS detector (use
    #   'pil900KW'), and the 'det_exposure_time(...)' calls must be run as plans — see the
    #   ⚠️ notes on those lines.  (amptek is fine — it still works.)
    # === end smi_plans note ================================================
    # samples = ['SPYZ_new', 'BOYZ', 'SPXZ', 'BOXZ']

    # x_list = [29000, 9330, -6470, -28870]
    # y_list = [3530, 2190, 3310, 2680]

    # x_range=[[0, 60, 4],[0, 80, 5], [0, 60, 4], [0, 60, 4]]
    # y_range=[[0, -300, 151], [0, -140, 71], [0, -300, 151], [0, -160, 81]]

    samples = ["SPYZ_90deg", "BOYZ_90deg", "SPXZ_90deg", "BOXZ_90deg"]
    name = "JG"
    x_list = [26570, 6780, -11660, -33150]
    y_list = [3250, 2970, 2110, 1960]

    x_range = [[0, -300, 16], [0, -200, 21], [0, -340, 18], [0, -200, 11]]
    y_range = [[0, -60, 31], [0, -60, 31], [0, -60, 31], [0, -60, 31]]

    # Detectors, motors:
    dets = [pil2M, pil300KW, amptek]  # dets = [pil2M,pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' map_grid_run sets it for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from Y coordinates ({len(y_list)})"
    assert len(x_list) == len(
        x_range
    ), f"Number of X coordinates ({len(x_list)}) is different X ranges ({len(x_range)})"
    assert len(x_list) == len(
        y_range
    ), f"Number of X coordinates ({len(x_list)}) is different Y ranges ({len(y_range)})"

    waxs_range = np.linspace(0, 26, 5)

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            name_fmt = "{sam}_wa{waxs}deg"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.rel_grid_scan(
                dets, piezo.x, *x_r, piezo.y, *y_r, 0
            )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def mapping_saxs_test(t=0.1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tiny test version of the map above — one "sample" at the current
    #   position, a 2-point x by 1-point y grid, just to check the plumbing.
    #
    # 💡 NEWER, EASIER WAY: same as the real map — smi_plans' map_grid_run does the grid and
    #   records the context for you. A test-sized call:
    #
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(
    #         "test",
    #         piezo.x, 0, 0, 2,                      # 2 points in x (relative)
    #         piezo.y, 0, 0, 1,                      # 1 point in y
    #         t=t, dets=[pil2M, pil900KW, amptek],
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    samples = ["test"]
    name = "test"
    x_list = [0]
    y_list = [0]

    x_range = [[0, 0, 2]]
    y_range = [[0, 0, 1]]

    # Detectors, motors:
    dets = [pil2M, pil300KW, amptek]  # dets = [pil2M,pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' map_grid_run sets it for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from Y coordinates ({len(y_list)})"
    assert len(x_list) == len(
        x_range
    ), f"Number of X coordinates ({len(x_list)}) is different X ranges ({len(x_range)})"
    assert len(x_list) == len(
        y_range
    ), f"Number of X coordinates ({len(x_list)}) is different Y ranges ({len(y_range)})"

    for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
        yield from bps.mvr(piezo.x, x)
        yield from bps.mvr(piezo.y, y)
        name_fmt = "{sam}"
        sample_name = name_fmt.format(sam=sample)
        sample_id(user_name=name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.rel_grid_scan(
            dets, piezo.x, *x_r, piezo.y, *y_r, 0
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).

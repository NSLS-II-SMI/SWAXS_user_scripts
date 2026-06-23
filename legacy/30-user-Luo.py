def mapping_Luo(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: micro-focus *mapping* — for each sample, and each WAXS arc angle, it
    #   rasters the beam across a little grid of x/y spots (a "rel_grid_scan", i.e. a grid of
    #   relative moves) and takes an image at every spot. (This is a nicely-built script.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a one-call
    #   grid-mapping plan (a "plan" is just a recipe of steps Bluesky runs for you). It records
    #   the x/y position and beam intensity INTO each image and builds the file name for you,
    #   so you don't have to set file paths by hand. Same kind of map as below:
    #
    #     from smi_plans import map_grid_run, spatial_grid_axes   # import once at session start
    #     yield from map_grid_run(
    #         "Yao_6_2",                                # the rest of the file name is added automatically
    #         dets=[pil900KW, pil2M],                   # WAXS is pil900KW now — see ⚠️ below
    #         x=(0, 500, 21), y=(0, 500, 101),         # your x/y ranges (start, stop, npts), unchanged
    #         t=t,                                      # your exposure, unchanged
    #     )
    #     # (loop this over your samples / waxs arc angles, moving piezo.x/y/z to each sample)
    #
    #   (This is just a tidier option to try later — your script below works as-is EXCEPT for
    #    the ⚠️ lines, which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW' (used in the
    #   detector list and in the file-path line below); (2) the 'det_exposure_time(...)' calls
    #   no longer set the exposure unless run as a plan (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================

    names = [
        "Yao_6_2",
        "AB_TMA_2",
        "ABA_TMA_2",
        "ABAB_TMA_2",
        "ABABA_TMA_2",
        "ABABA_IPrMeP_2",
    ]
    xlocs = [21400, 5500, -7200, -11700, -17200, -30700]
    ylocs = [0, 0, 0, 0, 0, 0]
    zlocs = [2700, 2700, 2700, 2700, 2700, 2700]

    x_range = [
        [0, 500, 21],
        [0, 500, 21],
        [0, 500, 21],
        [0, 500, 21],
        [0, 500, 21],
        [0, 500, 21],
    ]
    y_range = [
        [0, 500, 101],
        [0, 500, 101],
        [0, 500, 101],
        [0, 500, 101],
        [0, 500, 101],
        [0, 500, 101],
    ]
    wa_range = [[0, 13, 3], [0, 13, 3], [0, 13, 3], [0, 13, 3], [0, 13, 3], [0, 13, 3]]

    # names = ['CRP_2_275', 'CRP_1_131', 'Yao_6', 'CRP_2_275F', 'CRP_1_275A', 'AB_TMA', 'iPrMeP_stat', 'ABA_TMA', 'ABAB_TMA', 'ABABA_TMA',
    # 'TMA_stat', 'ABABA_IPrMeP' ]
    # xlocs = [30400,        26100,        21400,        16200,         9600,         5500,         -500,        -7200,
    #        -11700,       -17200,       -23700,   -30700]
    # ylocs = [0,            0,            0,            0,            0,            0,            0,            0,
    #             0,            0,            0,        0]
    # zlocs = [2700,         2700,         2700,         2700,         2700,         2700,         2700,         2700,
    #          2700,         2700,         2700,     2700]
    # x_range=[[0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11],
    #  [0, 500, 11], [0, 500, 11], [0, 500, 11], [0, 500, 11]]
    # y_range=[[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],
    # [0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101]]

    # wa_range=[[0, 26, 5],   [0, 13, 3],   [0, 26, 5],   [0, 26, 5],   [0, 26, 5],   [0, 13, 3],   [0, 13, 3],   [0, 13, 3],
    #    [0, 13, 3],   [0, 13, 3],   [0, 13, 3],   [0, 13, 3]]
    user = "AL"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(names)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(ylocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(zlocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(x_range)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(y_range)})"
    assert len(xlocs) == len(
        wa_range
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(wa_range)})"

    # Detectors, motors:
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for num, (x, y, sample, x_r, y_r, wax_ra) in enumerate(
        zip(xlocs, ylocs, names, x_range, y_range, wa_range)
    ):
        if num == 0:
            proposal_id("2121_1", "307948_Luo")
        else:
            proposal_id("2121_1", "307948_Luo2")

        pil2M.cam.file_path.put(
            "/nsls2/xf12id2/data/images/users/2021_1/307948_Luo2/1M/%s" % sample
        )
        pil300KW.cam.file_path.put(
            "/nsls2/xf12id2/data/images/users/2021_1/307948_Luo2/300KW/%s" % sample
        )  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

        for wa in np.linspace(wax_ra[0], wax_ra[1], wax_ra[2]):
            yield from bps.mv(waxs, wa)

            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y + 500)
            name_fmt = "{sam}_4m_16.1keV_wa{waxs}"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.rel_grid_scan(
                dets, piezo.y, *y_r, piezo.x, *x_r, 0
            )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

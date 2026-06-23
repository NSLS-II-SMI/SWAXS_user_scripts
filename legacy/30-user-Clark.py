import numpy as np
from cycler import cycler


def crazy_mapping(x_top, x_range, x_step, y_top, y_range, y_step, angle):
    x_all, y_all = [], []

    for num, y_coord in enumerate(np.linspace(y_top, y_top + y_range, y_step)):
        x_coord = x_top + (y_coord - y_top) * np.tan(np.deg2rad(angle))
        xs = np.linspace(x_coord, x_coord + x_range, x_step)
        ys = np.repeat(y_coord, len(xs))

        x_all = x_all + xs.tolist()
        y_all = y_all + ys.tolist()

    xall = [int(i) for i in x_all]
    yall = [int(i) for i in y_all]

    return xall, yall


def mapping2_waxs_ucol(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: micro-focus mapping — for each sample it sets a custom save folder, moves to
    #   the spot, sweeps the WAXS arc, and runs one coordinated 2D grid scan (y then x), taking an
    #   image at every point of the little raster.
    #
    # 💡 NICE WORK + NEWER, EASIER WAY: collecting each map as ONE 'rel_grid_scan' is the modern,
    #   tidy way — nice! smi_plans has a grid map helper that does this AND records the position/beam
    #   into each image and names the files for you (so you don't need the per-sample 'cam.file_path.put'
    #   or the hand-built 'name_fmt'):
    #
    #     from smi_plans import map_grid_run                 # do this once at the top of your session
    #     yield from map_grid_run(
    #         "GTAC_SMcap_real",                             # the rest of the file name is added automatically
    #         piezo.y, 0, 5000, 251,                         # your y range, unchanged
    #         piezo.x, 0, 0, 1,                              # your x range, unchanged
    #         t=t, dets=[pil2M, pil900KW],
    #     )                                                  # loop the WAXS arc and samples around it as you do now
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    waxs_range = [13, 6.5, 0]
    name = "NC"
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans map runs set exposure for you via t=.)

    # samples = ['GTAC_smcap']
    # x_list = [-30501]
    # y_list = [-2000]
    # x_range=[ [0, 0, 1]]
    # y_range=[ [0, 5000, 251]]

    samples = [
        "GTAC_SMcap_real",
        "cap_bag5",
        "cap_bag4",
        "Bag2_S2.4",
        "bag3_4d",
        "bag3_2d_part1",
        "bag3_2d_part2",
        "bag3_1d",
    ]
    x_list = [-23701, -18501, -10801, -45101, 11300, 30398, 36098, 48800]
    y_list = [-1000, -5700, -6900, -4700, -1900, -3100, -2800, -6900]
    x_range = [
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 4400, 45],
        [0, 2300, 24],
        [0, 2000, 21],
        [0, 2000, 21],
        [0, 5000, 51],
    ]
    y_range = [
        [0, 5000, 251],
        [0, 6000, 201],
        [0, 6000, 201],
        [0, 4000, 41],
        [0, 2800, 29],
        [0, 3300, 34],
        [0, 2600, 27],
        [0, 4500, 46],
    ]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
        pil2M.cam.file_path.put(
            f"/nsls2/xf12id2/data/images/users/2020_2/305363_Clark2/1M/%s" % sample
        )
        pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
            f"/nsls2/xf12id2/data/images/users/2020_2/305363_Clark2/300KW/%s" % sample
        )

        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans map runs set exposure for you via t=.)


def mapping1_waxs_ucol(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: micro-focus mapping (the active part is "Bag1_S3" + a couple of capillaries) —
    #   for each sample it sets a custom save folder, moves to the spot, sweeps the WAXS arc, and runs
    #   one coordinated 2D grid scan (y then x). (The big quoted block above is an older 'scan_nd'
    #   tilted-raster version, kept for reference — it doesn't run.)
    #
    # 💡 NICE WORK + NEWER, EASIER WAY: collecting each map as ONE 'rel_grid_scan' is the modern,
    #   tidy way — nice! smi_plans has a grid map helper that records the position/beam into each
    #   image and names the files for you (so you don't need the per-sample 'cam.file_path.put'):
    #
    #     from smi_plans import map_grid_run                 # do this once at the top of your session
    #     yield from map_grid_run("Bag1_S3_in_topleft",
    #                             piezo.y, 0, 3800, 39, piezo.x, 0, 3500, 36,
    #                             t=t, dets=[pil2M, pil900KW])
    #   (for the tilted/snaked raster the older 'scan_nd' style, build the points with
    #    spatial_grid_axes / build_axes_from_spec and hand them to acquire(...).)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    waxs_range = [13, 6.5, 0]
    name = "NC"
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans map runs set exposure for you via t=.)
    """
    sample = 'Bag1_S2_inner'
    
    pil2M.cam.file_path.put(f"/ramdisk/images/users/2020_2/305363_Clark1/1M/%s"%sample)
    pil300KW.cam.file_path.put(f"/nsls2/xf12id2/data/images/users/2020_2/305363_Clark1/300KW/%s"%sample)

    samples = ['Bag1S2_in_midleft','Bag1S2_in_botleft', 'Bag1S2_in_bot', 'Bag1S2_in_midright',
    'Bag1S2_in_topright', 'Bag1S2_in_top']

    x_list = [10600, 9100, 9100, 10815, 17715, 17915, 14915]
    y_list = [-3300, -1300, 3700, 5300, 3000, 0, -3000]
    x_range= [1000, 1000, 1000, 5600, 1000, 1000, 1000]
    y_range= [2000, 5000, 1600, 1000, 2300, 3000, 3000]
    angles = [-45, 0, 47, 0, -47, 0, 45]

    assert len(x_list) == len(samples), f'Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})'
    for x, y, sample, x_r, y_r, angle in zip(x_list, y_list, samples, x_range, y_range, angles):       
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        x_all, y_all = crazy_mapping(x_top=x, x_range=x_r, x_step=20, y_top=y, y_range=y_r, y_step=20, angle=angle)

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = '{sam}_wa{waxs}'
            sample_name = name_fmt.format(sam=sample, waxs='%2.1f'%wa)
            sample_id(user_name=name, sample_name=sample_name) 
            print(f'\n\t=== Sample: {sample_name} ===\n')
            traj1 = cycler(piezo.y, y_all)
            traj2 = cycler(piezo.x, x_all)
            traj = traj1+traj2
            yield from bp.scan_nd(dets, traj)

    """
    sample = "Bag1_S3"

    pil2M.cam.file_path.put(
        f"/ramdisk/images/users/2020_2/305363_Clark1/1M/%s" % sample
    )
    pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        f"/nsls2/xf12id2/data/images/users/2020_2/305363_Clark1/300KW/%s" % sample
    )

    samples = [
        "Bag1_S3_in_topleft",
        "Bag1_S3_in_midleft",
        "Bag1_S3_in_botleft",
        "Bag1_S3_in_bot",
        "Bag1_S3_in_botright",
        "Bag1_S3_in_midright",
        "Bag1_S3_in_topright",
    ]

    x_list = [10600, 9100, 9100, 10815, 17715, 17915, 14915]
    y_list = [-3300, -1300, 3700, 5300, 3000, 0, -3000]
    x_range = [1000, 1000, 1000, 5600, 1000, 1000, 1000]
    y_range = [2000, 5000, 1600, 1000, 2300, 3000, 3000]
    angles = [-45, 0, 47, 0, -47, 0, 45]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, y, sample, x_r, y_r, angle in zip(
        x_list, y_list, samples, x_range, y_range, angles
    ):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        x_all, y_all = crazy_mapping(
            x_top=x,
            x_range=x_r,
            x_step=15,
            y_top=y,
            y_range=y_r,
            y_step=15,
            angle=angle,
        )

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            traj1 = cycler(piezo.y, y_all)
            traj2 = cycler(piezo.x, x_all)
            traj = traj1 + traj2
            yield from bp.scan_nd(dets, traj)

    samples = ["Bag2_S2.1", "Bag2_S2.3", "Bag1_S2_inner"]
    x_list = [
        38798,
        -15000,
        -42000,
    ]
    y_list = [-2099, 100, -2200]
    x_range = [[0, 3500, 36], [0, 3600, 37], [0, 3500, 15]]
    y_range = [[0, 3800, 39], [0, 3100, 32], [0, 5000, 21]]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
        pil2M.cam.file_path.put(
            f"/ramdisk/images/users/2020_2/305363_Clark1/1M/%s" % sample
        )
        pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
            f"/nsls2/xf12id2/data/images/users/2020_2/305363_Clark1/300KW/%s" % sample
        )

        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans map runs set exposure for you via t=.)


def mapping_waxs_ucol(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: micro-focus mapping — for each sample it moves to the spot, sweeps the
    #   WAXS arc, and runs one coordinated 2D grid scan (y then x), taking an image at every point.
    #
    # 💡 NICE WORK + NEWER, EASIER WAY: collecting each map as ONE 'rel_grid_scan' is the modern,
    #   tidy way — nice! smi_plans has a grid map helper that records the position/beam into each
    #   image and names the files for you:
    #
    #     from smi_plans import map_grid_run                 # do this once at the top of your session
    #     yield from map_grid_run("Bag2_S2.2",
    #                             piezo.y, 0, 3800, 77, piezo.x, 0, 3800, 39,
    #                             t=t, dets=[pil2M, pil900KW])    # loop the WAXS arc and samples around it as you do now
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # samples = ['Bag1_S2_rim', 'Bag1_S2_inner','Bag2_S2.2','Bag1_S3','Bag1_S1']
    # x_list = [  -43900,         -42000,         -16200,     9400,      36800]
    # y_list = [   -3300,          -2200,            0,      -2800,      -2800]
    samples = ["Bag2_S2.2", "Bag1_S1"]
    x_list = [-16200, 36800]
    y_list = [0, -2800]
    name = "NC"

    # x_range=[[0, 7500, 126], [0, 3500, 15], [0, 3800, 39], [0, 9300, 32], [0, 9000, 31]]
    # y_range=[[0, 9000, 151], [0, 5000, 21], [0, 3800, 77], [0, 8400, 29], [0, 9000, 31]]
    x_range = [[0, 3800, 39], [0, 9000, 31]]
    y_range = [[0, 3800, 77], [0, 9000, 31]]

    waxs_range = [13, 6.5, 0]
    # Detectors, motors:
    dets = [pil2M, pil300KW]  # dets = [pil2M,pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans map runs set exposure for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

        #     for yrs in np.linspace(y_r[0], y_r[1], y_r[2]):
        #         yield from bps.mv(piezo.y, y+yrs)
        #         for xrs in np.linspace(x_r[0], x_r[1], x_r[2]):
        #             yield from bps.mv(piezo.x, x+xrs)
        #             name_fmt = '{sam}_x{x}_y{y}'
        #             sample_name = name_fmt.format(sam=sample, x='%6.6d'%(x+xrs), y='%6.6d'%(y+yrs))
        #             sample_id(user_name=name, sample_name=sample_name)
        #             #print(f'\n\t=== Sample: {sample_name} ===\n')
        #             yield from bp.count(dets, num=1)

        # #yield from bp.rel_grid_scan(dets, piezo.x, *x_r, piezo.y, *y_r, 0) #1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans map runs set exposure for you via t=.)


def run_waxs_UCol(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a WAXS line scan — for each sample it steps down a column of y positions
    #   and, at each spot, scans the WAXS arc (taking an image at each arc angle).
    #
    # 💡 NEWER, EASIER WAY: smi_plans builds the WAXS arc as an "axis" and the y positions as a
    #   line axis, then runs them in one acquire call that records the arc/position/beam into each
    #   image and names the files for you:
    #
    #     from smi_plans import acquire, motor_axis           # do this once at the top of your session
    #     yield from acquire("salmonDNA2_air", [pil900KW],
    #                        [motor_axis("y", piezo.y, np.linspace(-40, 200, 49)),
    #                         motor_axis("wa", waxs, [0, 6.5, 13])])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    xlocs = [5500]
    names = ["salmonDNA2_air"]
    user = "GS"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    y0 = -1350
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    y_range = np.linspace(
        -40, 200, 49
    )  # if you start from the bottom, reverse signs: 40, -200, 49
    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_range = [0, 13, 3]
    for sam, x in zip(names, xlocs):
        yield from bps.mv(piezo.x, x)
        for y in y_range:
            yield from bps.mv(piezo.y, y0 + y)
            name_fmt = "{sam}_y{y_pos}um"
            sample_name = name_fmt.format(sam=sam, y_pos="%2.1f" % y)
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def run_waxs_emptyUCol(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes empty/background WAXS-arc scans — for each named spot it moves x and
    #   scans the WAXS arc (an image at each arc angle), for vacuum/background subtraction later.
    #
    # 💡 NEWER, EASIER WAY: build the WAXS arc as an "axis" and run it per sample with smi_plans;
    #   it records the arc/position/beam into each image and names the files for you:
    #
    #     from smi_plans import acquire, motor_axis           # do this once at the top of your session
    #     yield from acquire("sDDnem_vac1_bkg", [pil900KW],
    #                        [motor_axis("wa", waxs, [0, 6.5, 13])])    # loop the x positions around it
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    xlocs = [-34500, -25000, -17050, -3825, 3750, 14050]
    ylocs = [0, 0, 0, 0, 0, 0]
    names = [
        "sDDnem_vac1_bkg",
        "sDDcol_vac_bkg",
        "DDshort_vac1_bkg",
        "DDlong_vac_bkg",
        "GTACshort_vac_bkg",
        "GTAClong_vac_bkg",
    ]
    user = "GS"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_range = [0, 13, 3]
    for sam, x in zip(names, xlocs):
        yield from bps.mv(piezo.x, x)
        name_fmt = "{sam}"
        sample_name = name_fmt.format(sam=sam)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def saxs_waxs_temps_Ucol(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one temperature-stamped SAXS+WAXS reading — records the Lakeshore
    #   temperature and elapsed time into the file name, then scans the WAXS arc once.
    #
    # 💡 NEWER, EASIER WAY: smi_plans records the temperature/time INTO the data and names the
    #   files from those recorded fields for you (no hand-built '{temperature}C_{tim}s'), and the
    #   WAXS arc is an "axis":
    #
    #     from smi_plans import acquire, motor_axis, lakeshore_heater
    #     yield from acquire("W1013ITO", [pil2M, pil900KW],
    #                        [motor_axis("wa", waxs, [0, 6.5, 13])],
    #                        reads=[ls.ch1_read])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) 'rayonix'
    #   (the MAXS detector) was removed with no replacement; (3) the 'det_exposure_time(...)' calls
    #   no longer set the exposure unless run as a plan (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    name = "VM"

    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix, ls.ch1_read]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed → use 'pil900KW' (different camera, check beam-center/calibration); 'rayonix' (the MAXS detector) was removed from the beamline and has no current replacement — remove it from your detector list or ask beamline staff. Both would error.
    y_range = [5.6, 5.6, 1]
    sample = "W1013ITO"
    waxs_range = [0, 13, 3]

    name_fmt = "{sam}_{temperature}C_{tim}s"

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    temp = ls.ch1_read.value
    t1 = time.time()
    time_elapsed = int(t1 - t0)
    sample_name = name_fmt.format(temperature=temp, sam=sample, tim=time_elapsed)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=sample, sample_name=sample_name)
    # yield from bp.count(dets)
    yield from bp.scan(dets, waxs, *waxs_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def run_contRPI(t=1, numb=100, sleep=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a simple time series — takes a SAXS+WAXS image, waits 'sleep' seconds, and
    #   repeats 'numb' times.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-line time-series helper that loops for you, records
    #   the elapsed time INTO each image, and names the files:
    #
    #     from smi_plans import time_series_run               # do this once at the top of your session
    #     yield from time_series_run("RPI", num=numb, delay=sleep, t=t, dets=[pil2M, pil900KW])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans time_series_run sets it for you via t=.)
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # dets = [pil300Kw]
    for i in range(numb):
        yield from bp.count(dets, num=1)
        yield from bps.sleep(sleep)


def instec_insitu_hard_xray(t=0.4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ temperature run on the Instec hot stage — it walks a grid of
    #   spots while the temperature changes, waits for the Lakeshore reading, and at each spot
    #   sweeps the WAXS arc and takes a SAXS+WAXS image (stamping temperature/time into the name).
    #
    # 💡 NEWER, EASIER WAY: an in-situ "hold and watch while T changes" run is the smi_plans
    #   isothermal/kinetics run — it drives/reads the heater, records temperature/time INTO each
    #   image, and names the files from the recorded fields:
    #
    #     from smi_plans import isothermal_kinetics_run, lakeshore_heater   # do this once at the top
    #     yield from isothermal_kinetics_run("DIO_loop3", t=t, dets=[pil2M, pil900KW],
    #                                        heater=lakeshore_heater)        # sweep the WAXS arc / step spots as you do now
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "DIO_loop3"
    temperatures = np.arange(90, 39, -1).tolist()

    waxs_arc = np.linspace(0, 19.5, 4)

    yss = np.linspace(-1.05, -0.85, 21)
    xss = np.linspace(-1.3, -1.5, 21)

    yss, xss = np.meshgrid(yss, xss)

    yss = yss.ravel()
    xss = xss.ravel()

    num = 0
    cur_temp = 400

    t0 = time.time()

    while num < 200 and cur_temp > 313:
        yield from bps.mv(stage.y, yss[num])
        yield from bps.mv(stage.x, xss[num])

        num = num + 1

        t_kelvin = t + 273.15
        cur_temp = ls.input_A.value

        while cur_temp < 100:
            yield from bps.sleep(10)
            cur_temp = ls.input_A.value

        # yield from bps.sleep(60)

        if waxs.arc.position > 10:
            wa_arc = waxs_arc[::-1]
        else:
            wa_arc = waxs_arc

        t1 = time.time()

        for j, wa in enumerate(wa_arc):
            yield from bps.mv(waxs, wa)
            name_fmt = "{sample}_{temperature}C_t{time}_wa{waxs}_sdd1.6m"
            sample_name = name_fmt.format(
                sample=name,
                temperature="%3.1f" % (cur_temp - 273.15),
                time="%3.1f" % (t1 - t0),
                waxs="%2.1f" % wa,
            )
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name="NC", sample_name=sample_name)
            yield from bp.count(dets, num=1)


def instec_insitu_t_step_hard_xray(t=0.4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ temperature-STEP run on the Instec hot stage — for each setpoint
    #   it commands the heater, waits for the Lakeshore reading to reach it, then sweeps the WAXS
    #   arc and takes a SAXS+WAXS image at a new spot (stamping the temperature into the name).
    #
    # 💡 NEWER, EASIER WAY: stepping temperature and measuring at each step is the smi_plans
    #   temperature-ramp run — it commands/waits on the heater, records temperature INTO each
    #   image, and names the files from the recorded fields:
    #
    #     from smi_plans import temperature_ramp_run, lakeshore_heater   # do this once at the top
    #     yield from temperature_ramp_run("RM734_loop1", [86, 84, 82, 80],   # your temperatures
    #                                     t=t, dets=[pil2M, pil900KW], heater=lakeshore_heater)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "RM734_loop1"
    temperatures = np.arange(86, 80, -2).tolist()

    waxs_arc = np.linspace(0, 19.5, 4)

    yss = np.linspace(-1.0, -0.9, 11)
    xss = np.linspace(1.2, 1.1, 11)

    yss, xss = np.meshgrid(yss, xss)

    yss = yss.ravel()
    xss = xss.ravel()

    for num, temper in enumerate(temperatures):
        yield from bps.mv(stage.y, yss[num])
        yield from bps.mv(stage.x, xss[num])

        t_kelvin = temper + 273.15
        yield from ls.output3.mv_temp(t_kelvin - 10)

        cur_temp = ls.input_A.value

        while abs(cur_temp - t_kelvin) > 1.5:
            yield from bps.sleep(10)
            cur_temp = ls.input_A.value

        yield from bps.sleep(60)

        if waxs.arc.position > 10:
            wa_arc = waxs_arc[::-1]
        else:
            wa_arc = waxs_arc

        for j, wa in enumerate(wa_arc):
            yield from bps.mv(waxs, wa)
            name_fmt = "{sample}_{temperature}C_wa{waxs}_sdd1.6m"
            sample_name = name_fmt.format(
                sample=name, temperature="%3.1f" % temper, waxs="%2.1f" % wa
            )
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name="NC", sample_name=sample_name)
            yield from bp.count(dets, num=1)


def instec_insitu_hard_xray_fixT(t=0.4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single fixed-temperature reading — at the current temperature it sweeps
    #   the WAXS arc and takes a SAXS+WAXS image at each arc angle (temperature written into the name).
    #
    # 💡 NEWER, EASIER WAY: build the WAXS arc as an "axis" and run it in one acquire call that
    #   records the arc/temperature into each image and names the files:
    #
    #     from smi_plans import acquire, motor_axis           # do this once at the top of your session
    #     yield from acquire("RM734__edgeglass", [pil2M, pil900KW],
    #                        [motor_axis("wa", waxs, np.linspace(0, 19.5, 4))],
    #                        reads=[ls.ch1_read])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "RM734__edgeglass"

    temp_C = 110
    # temperatures = [120]
    waxs_arc = np.linspace(0, 19.5, 4)

    if waxs.arc.position > 10:
        wa_arc = waxs_arc[::-1]
    else:
        wa_arc = waxs_arc

    for j, wa in enumerate(wa_arc):
        yield from bps.mv(waxs, wa)
        name_fmt = "{sample}_{temperature}C_wa{waxs}_sdd1.6m_11.15keV"
        sample_name = name_fmt.format(
            sample=name, temperature="%3.1f" % temp_C, waxs="%2.1f" % wa
        )
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name="NC", sample_name=sample_name)
        yield from bp.count(dets, num=1)


def hard_xray_greg(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single SAXS+WAXS reading — sweeps the WAXS arc once at the current spot
    #   and takes an image at each arc angle.
    #
    # 💡 NEWER, EASIER WAY: build the WAXS arc as an "axis" and run it in one acquire call that
    #   records the arc/beam into each image and names the files:
    #
    #     from smi_plans import acquire, motor_axis           # do this once at the top of your session
    #     yield from acquire("glass", [pil2M, pil900KW],
    #                        [motor_axis("wa", waxs, np.linspace(0, 13.0, 3))])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "glass"

    # temperatures = [120]
    waxs_arc = np.linspace(0, 13.0, 3)

    if waxs.arc.position > 10:
        wa_arc = waxs_arc[::-1]
    else:
        wa_arc = waxs_arc

    ypos = [-300, 300, 3]
    for j, wa in enumerate(wa_arc):
        yield from bps.mv(waxs, wa)
        name_fmt = "{sample}_wa{waxs}_sdd1.6m"
        sample_name = name_fmt.format(sample=name, waxs="%2.1f" % wa)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name="GS", sample_name=sample_name)
        # yield from bp.rel_scan(dets, piezo.y, *ypos)
        yield from bp.count(dets)


def instec_insitu_hard_xray_2021_3(t=0.4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ temperature run on the Instec hot stage — walks a grid of spots
    #   while the temperature changes, waits for the Lakeshore reading, then sweeps the WAXS arc
    #   and takes a SAXS+WAXS image (stamping temperature/time into the name).
    #
    # 💡 NEWER, EASIER WAY: this "hold and watch while T changes" run is the smi_plans isothermal/
    #   kinetics run — it reads the heater, records temperature/time INTO each image, and names the
    #   files from the recorded fields:
    #
    #     from smi_plans import isothermal_kinetics_run, lakeshore_heater   # do this once at the top
    #     yield from isothermal_kinetics_run("7-N_", t=t, dets=[pil2M, pil900KW],
    #                                        heater=lakeshore_heater)        # sweep the WAXS arc / step spots as you do now
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "7-N_"
    waxs_arc = [0, 20]

    yss = np.linspace(-1.55, -1.4, 26)
    xss = np.linspace(-3.0, -2.8, 15)

    yss, xss = np.meshgrid(yss, xss)

    yss = yss.ravel()
    xss = xss.ravel()

    num = 0
    cur_temp = 400

    t0 = time.time()

    while num < 200 and cur_temp > 300:
        yield from bps.mv(stage.y, yss[num])
        yield from bps.mv(stage.x, xss[num])

        num = num + 1

        t_kelvin = t + 273.15
        cur_temp = ls.input_A.value

        while cur_temp < 100:
            yield from bps.sleep(2)
            cur_temp = ls.input_A.value

        # yield from bps.sleep(60)

        if waxs.arc.position > 10:
            wa_arc = waxs_arc[::-1]
        else:
            wa_arc = waxs_arc
        yield from bps.sleep(2)

        t1 = time.time()

        for j, wa in enumerate(wa_arc):
            yield from bps.mv(waxs, wa)
            name_fmt = "{sample}_{temperature}C_t{time}_wa{waxs}_sdd2.0m_16.1keV"
            sample_name = name_fmt.format(
                sample=name,
                temperature="%3.1f" % (cur_temp - 273.15),
                time="%4.1f" % (3940 + t1 - t0),
                waxs="%2.1f" % wa,
            )
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name="NC", sample_name=sample_name)
            yield from bp.count(dets, num=1)


def instec_oneshot_hard_xray_2021_3(t=0.4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single "one-shot" reading at the current temperature — sweeps the WAXS
    #   arc once and takes a SAXS+WAXS image at each arc angle.
    #
    # 💡 NEWER, EASIER WAY: build the WAXS arc as an "axis" and run it in one acquire call that
    #   records the arc/beam into each image and names the files:
    #
    #     from smi_plans import acquire, motor_axis           # do this once at the top of your session
    #     yield from acquire("7-N_RT_120deg", [pil2M, pil900KW],
    #                        [motor_axis("wa", waxs, [0, 20])])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name = "7-N_RT_120deg"
    waxs_arc = [0, 20]

    if waxs.arc.position > 10:
        wa_arc = waxs_arc[::-1]
    else:
        wa_arc = waxs_arc

    for j, wa in enumerate(wa_arc):
        yield from bps.mv(waxs, wa)
        name_fmt = "{sample}_wa{waxs}_sdd2.0m_16.1keV"
        sample_name = name_fmt.format(sample=name, waxs="%2.1f" % wa)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name="NC", sample_name=sample_name)
        yield from bp.count(dets, num=1)

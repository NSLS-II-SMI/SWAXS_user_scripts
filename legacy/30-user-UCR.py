# Align GiSAXS sample
import numpy as np


def run_mesh_fastUCR(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each WAXS-arc position, raster-scans the sample in x/y and
    #   takes a SAXS/WAXS image at every grid point (a microfocus map / mesh scan).
    #
    # 👍 Nice — you're already using ONE coordinated grid scan per map
    #   (bp.rel_grid_scan), which is exactly the tidy pattern smi_plans is built around
    #   (one "run" per map instead of one file per point). The migration is mostly a
    #   rename to the preset, which also records energy/beam/positions into the data:
    #
    #     from smi_plans import map_grid_run, map_dets
    #     yield from map_grid_run(
    #         "sample1_real_watertest", map_dets(),    # detector set chosen for you
    #         x=piezo.x, x_range=(0, 0, 1),            # your x grid, unchanged
    #         y=piezo.y, y_range=(0, 600, 151),        # your y grid, unchanged
    #         t=t,
    #     )
    #     # (loop the WAXS-arc positions around it, or see map_bar for whole-bar maps.)
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines, which need a small fix.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure
    #   on its own — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    samples = ["sample1_real_watertest_4um_step_"]
    x_list = [-34889]
    y_list = [-7610]

    name = "DK"

    x_range = [[0, 0, 1]]
    y_range = [[0, 600, 151]]

    # Detectors, motors:
    dets = [pil900KW]  # dets = [pil2M,pil300KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' map presets set exposure via t=.)
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    waxs_range = [0, 20]

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
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.
    yield from bps.mv(waxs, 0)


def run_mesh_fastUCI(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: raster-scans each sample in x/y at several WAXS-arc positions,
    #   taking a WAXS image at every grid point — a multi-sample microfocus map.
    #
    # 👍 You're already doing ONE coordinated grid scan per map (bp.rel_grid_scan),
    #   the same tidy "one run per map" shape smi_plans uses. The migration is mostly
    #   swapping in the preset (which also records energy/beam/positions for you):
    #
    #     from smi_plans import map_grid_run, map_dets
    #     # for each sample: map_grid_run(name, map_dets(),
    #     #                                y=piezo.y, y_range=(0, 200, 101),   # your y grid
    #     #                                x=piezo.x, x_range=(0, 125, 6),     # your x grid
    #     #                                t=t)
    #     # see map_bar to drive a whole bar of samples at once.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' no longer sets the exposure on its own — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_range = [0, 6.5, 13, 19.5, 26]
    name = "TW"
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.

    samples = [
        "tooth4_bot",
        "tooth4_cen-tip",
        "Mag-gypsum",
        "Mag-cell",
        "Mag-nocell",
        "tooth0pm",
        "tooth1pm",
        "tooth2pm",
        "tooth3pm",
        "tooth4pm",
        "tooth5pm",
    ]
    x_list = [
        17045,
        17190,
        3220,
        -12740,
        -32520,
        27950,
        28550,
        29000,
        29450,
        29850,
        30250,
    ]
    y_list = [-4110, -4160, 670, -1800, -1160, -1650, -1500, -1650, -1750, -1500, -1000]
    x_range = [
        [0, 125, 6],
        [0, 400, 17],
        [0, 200, 9],
        [0, 200, 9],
        [0, 200, 9],
        [0, 250, 6],
        [0, 300, 7],
        [0, 300, 7],
        [0, 350, 8],
        [0, 400, 9],
        [0, 350, 8],
    ]
    y_range = [
        [0, 200, 101],
        [0, 200, 101],
        [0, 200, 101],
        [0, 200, 101],
        [0, 200, 101],
        [0, 350, 36],
        [0, 400, 41],
        [0, 400, 41],
        [0, 400, 41],
        [0, 450, 46],
        [0, 500, 51],
    ]

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

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def mesh_UCI_2020_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: raster-scans three samples (T1/T2/T3) in x/y at several WAXS-arc
    #   positions, taking a WAXS image at every grid point — a multi-sample map.
    #
    # 👍 Already ONE coordinated grid scan per map (bp.rel_grid_scan) — the same tidy
    #   shape smi_plans uses. Swap in the preset to also record energy/beam/positions:
    #
    #     from smi_plans import map_grid_run, map_dets
    #     # per sample: map_grid_run(name, map_dets(),
    #     #                          y=piezo.y, y_range=(0, 400, 201),   # your y grid
    #     #                          x=piezo.x, x_range=(0, 450, 19),    # your x grid
    #     #                          t=t)   # see map_bar for the whole bar at once.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' no longer sets the exposure on its own — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_range = [0, 6.5, 13, 19.5, 26]
    name = "TW"
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.

    samples = ["T1", "T2", "T3"]
    x_list = [10270, 2715, -3465]
    y_list = [-1440, -1860, -1800]
    x_range = [[0, 450, 19], [0, 375, 17], [0, 375, 16]]
    y_range = [[0, 400, 201], [0, 400, 201], [0, 500, 251]]

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

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def mesh_UCI_2021_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: raster-scans a set of samples in x/y at several WAXS-arc
    #   positions (here recording both WAXS and SAXS at every grid point) — a
    #   multi-sample microfocus map.
    #
    # 👍 Already ONE coordinated grid scan per map (bp.rel_grid_scan). Swap in the
    #   preset to also record energy/beam/positions automatically:
    #
    #     from smi_plans import map_grid_run, map_dets
    #     # per sample: map_grid_run(name, map_dets(),
    #     #                          y=piezo.y, y_range=(0, 300, 31),    # your y grid
    #     #                          x=piezo.x, x_range=(0, 200, 9),     # your x grid
    #     #                          t=t)   # see map_bar for the whole bar at once.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' no longer sets the exposure on its own — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_range = np.linspace(0, 26, 5)

    name = "TW"
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration). (pil2M is fine.)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.

    # Finished at -17300 in X

    # samples = [    'S1_map1', 'S1_map2', 'S2_map1', 'S2_map2', 'S5', 'S7','chiton_art_frontal','chiton_art_lateral',
    # 'chi_ima13-22_t13','chi_ima13-22_t14','chi_ima13-22_t15','chi_ima13-22_t16','chi_ima13-22_t17','chi_ima13-22_t18','chi_ima13-22_t19','chi_ima13-22_t20-22',
    # 'chi_ima0-12_map1','chi_ima0-12_map2','chi_ima0-12_map3','chi_ima0-12_map4', 'wood', 'chitin_edgeon', 'chitin_large']
    # x_list = [     41600,        42800,      29200,     29950,     20900,     12900,      2200,      1250,     -8970,      -9020,     -8970,     -9070,     -9120,     -9470,     -9670,
    #     -9920,    -17520,       -17300,     -17200,    -17250,    -24150,    -33250,    -40250]
    # y_list = [       800,          600,        500,       350,       550,       500,      1150,       950,       100,        350,       900,      1250,      1500,      1750,      1950,
    #      2150,       100,          300,        600,      1500,      1500,      1500,      1500]
    # x_range=[[0, 1200,31], [0,350, 11], [0,700,21],[0,350,11],[0,300,11],[0,700,21],[0,390,14],[0,300,11], [0,200,5], [0,250,6], [0,250,6], [0,200,5], [0,200,5], [0,200,5], [0,200,5],
    # [0,250,11],[0,300,11],   [0,200,9],  [0,200,9],[0,300,11], [0,200,6],   [0,0,1],   [0,0,1]]
    # y_range=[ [0,550,111], [0,300, 61], [0,400,81],[0,250,51],[0,200,21],[0,250,26],[0,250,51],[0,300,61],[0,200,11],[0,200,11],[0,200,11],[0,200,11],[0,200,11],[0,200,11],[0,200,11],
    # [0,300,31],[0,200,21],  [0,300,31], [0,700,71],[0,600,61],[0,200,41],[0,100,10],[0,100,10]]

    samples = [
        "chi_ima0-12_map2",
        "chi_ima0-12_map3",
        "chi_ima0-12_map4",
        "wood",
        "chitin_edgeon",
        "chitin_large",
    ]
    x_list = [-17300, -17200, -17250, -23850, -33050, -40250]
    y_list = [300, 600, 1500, 1400, 1500, 1500]
    x_range = [
        [0, 200, 9],
        [0, 200, 9],
        [0, 300, 11],
        [0, 200, 6],
        [0, 0, 1],
        [0, 0, 1],
    ]
    y_range = [
        [0, 300, 31],
        [0, 700, 71],
        [0, 600, 61],
        [0, 200, 41],
        [0, 100, 10],
        [0, 100, 10],
    ]

    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(y_list)})"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(
        x_range
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(x_range)})"
    assert len(x_list) == len(
        y_range
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(y_range)})"

    for x, y, sample, x_r, y_r in zip(x_list, y_list, samples, x_range, y_range):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}_16.1keV_1.6m"
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def mesh_UCI_2021_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: raster-scans several samples in x/y at two WAXS-arc positions
    #   (recording WAXS + SAXS at every grid point), moving each sample to its own
    #   x/y/z/chi/hexapod position first — a multi-sample microfocus map.
    #
    # 👍 Already ONE coordinated grid scan per map (bp.rel_grid_scan), and you set
    #   proposal_id/sample names per sample — both still work. smi_plans' preset does
    #   the same map while recording energy/beam/positions into the data for you:
    #
    #     from smi_plans import map_grid_run, map_dets
    #     # per sample (after moving x/y/z/chi/hexapod): map_grid_run(name, map_dets(),
    #     #     y=piezo.y, y_range=(0, 1300, 66), x=piezo.x, x_range=(0, 5700, 115), t=t)
    #     # see map_bar to drive the whole bar at once.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines below. Note:
    #    piezo.ch, stage.y, proposal_id and sample_id are all fine — not flagged.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' no longer sets the exposure on its own — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_range = [0, 20]

    name = "WY"
    dets = [pil300KW, pil900KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' (already in this list) — drop pil300KW and keep pil900KW (note: different camera from pil300KW, so check beam-center/calibration). pil900KW and pil2M are fine.
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.

    # these samples are done.
    # samples = ['SS_BPS', 'SS_HSLD', 'SS_FVST',  'SS_TCSS',  'SS_SVSTt', 'SS_SVSTb',   'SS_BOSV','SS_BOFV',  'RS_FVSAMT','RS_SVSAMTt','RS_SVSAMTb', 'RS_FVS']
    # x_list = [   42900,   40580,      41550,       38550,     35700,      34940,         36250,    33000,    21340,       15340,       14890,       10140]
    # y_list = [    -300,   -1500,      3300,         400,       3600,       4600,        -1700,   -1500,       3100,        1100,        2200,       1500]
    # z_list = [   3100,     3100,       3100,        3100,      3100,       3100,          3100,     3100,     3100,        3100,        3100,       3700]
    # hexa_y = [    6,        6,          6,           6,         6,          6,              6,        6,        6,           6,          6,          6]
    # x_range=[[0,300,11], [0,300,11], [0,390,14],  [0,390,14], [0,330,12],[0,900,31], [0,250,11],[0,390,14],[0,390,14],[0,540,19],   [0,600,21], [0,420,15]]
    # y_range=[[0,720,181],[0,600,151],[0,1200,301],[0,400,101],[0,900,226],[0,340,86],[0,300,76],[0,200,51],[0,740,186],[0,1080,271],[0,740,186],[0,1600,401]]

    # these samples are very large areas and 3rd priority (lowest) except for the 1st teeth12.
    samples = ["12teeth_all", "RS_RWS", "RS_R", "FS_FRWSTD", "FS_FPRWS_PL3"]
    x_list = [-27880, -12400, -19000, 2220, -6000]
    y_list = [-6620, 1600, 1900, -4220, -5820]
    z_list = [-100, 5300, 6700, 1900, -700]
    hexa_y = [-7, 6, 6, -6, -6]
    chi_list = [5, 0, 0, 0, 0]
    x_range = [[0, 5700, 115], [0, 900, 31], [0, 900, 31], [0, 720, 25], [0, 720, 25]]
    y_range = [
        [0, 1300, 66],
        [0, 860, 216],
        [0, 900, 226],
        [0, 600, 151],
        [0, 800, 201],
    ]

    # 14 hours -- samples done.
    # samples = ['RS_SVSt',  'RS_SVSb', 'RS_BO',   'TBS_TBOLD',  'TBS_TBOTD','TBS_TS',  'TBS_TRWSLD','TBS_TRWSTD' ]
    # x_list = [   5250,       5600,     -4950,     -25250,      -28900,     -33050,     -38660,     -41740  ]
    # y_list = [   1200,       2250,      1800,       1150,        550,        1900,       -400,       1100 ]
    # z_list = [   3700,       3700,      3700,       3700,       3700,       3700,        6900,      4500 ]
    # hexa_y = [    6,          6,         6,          6,           6,           6,         6,          6   ]
    # x_range=[[0,360,13],  [0,540,19],[0,690,24],  [0,270,10], [0,300,11], [0,450,16],  [0,360,13], [0,330,12] ]
    # y_range=[[0,1300,326],[0,420,106],[0,600,151],[0,500,126],[0,500,126],[0,1200,301],[0,700,176],[0,400,101]]

    # samples done
    # samples = ['FS_FOBTD','FS_FSp2t','FS_FSp2b', 'FS_FSp1',   'FS_FR',  'FS_FRWS',    'BS',     'IT_tooth0','IT_tooth1', 'FS_FPRWS'    ]
    # x_list = [   40750,       36500,     36800,     31880,     26150,     21850,    -15350,     -33300,      -38130,     7240        ]
    # y_list = [   -4400,       -4750,     -4350,     -5250,     -4950,     -4050,     -4400,     -4540,       -4520,     -4920        ]
    # z_list = [   -1500,      -1100,      -1100,     -1100,     -500,       -1100,    -1100,      -1100,      -1100,     -700         ]
    # hexa_y = [    -6,          -6,       -6,         -6,         -6,       -6,         -6,        -6,         -6,        -6            ]
    # x_range=[[0,300,11],  [0,510,18],[0,450,16],  [0,450,16],[0,720,25], [0,720,25], [0,960,33], [0,420,15], [0,510,18], [0,1800,61]       ]
    # y_range=[[0,500,126],[0,400,101],[0,760,191],[0,700,176],[0,700,176],[0,800,201],[0,400,101],[0,459,154],[0,510,171],[0,900,91]     ]

    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(y_list)})"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(
        x_range
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(x_range)})"
    assert len(x_list) == len(
        y_range
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(y_range)})"

    for x, y, z, chi, hy, sample, x_r, y_r in zip(
        x_list, y_list, z_list, chi_list, hexa_y, samples, x_range, y_range
    ):
        # proposal_id('2021_3', 'Wang%s'%num)
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)
        yield from bps.mv(piezo.ch, chi)
        yield from bps.mv(stage.y, hy)

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sam}_wa{waxs}_16.1keV_2m"
            proposal_id("2021_3", "308498_Yang/%s" % sample)
            sample_name = name_fmt.format(sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.

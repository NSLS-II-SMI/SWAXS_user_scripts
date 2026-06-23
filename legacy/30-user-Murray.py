def ex_situ(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks along a bar of capillary samples (moving piezo.x to each one)
    #   and takes a single SAXS image per sample.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that can run a
    #   whole bar of samples for you from a simple list. It records the position, detector
    #   distance, beam intensity, etc. INTO each image and builds the file name automatically,
    #   so you don't have to read piezo.x.position / pil2M_pos.z / RE.md["scan_id"] by hand:
    #
    #     from smi_plans import transmission_bar, SampleList   # import once at session start
    #     samples = SampleList.from_columns(
    #         name=sample_list_E,                              # your sample names, unchanged
    #         x=x_list_E,                                      # your bar x positions, unchanged
    #     )
    #     yield from transmission_bar(samples, dets=[pil2M], t=meas_t)
    #
    #   (This is just a tidier option to try later — your script below works as-is EXCEPT for
    #    the ⚠️ line, which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # x_list = [45300, 38800, 32600, 26100, 19500, 13500, 7000, 600, -5700, -12100, -18400, -25200, -31500, -37500, -43700]
    # sample_list = ['cap1', 'cap2', 'cap3', 'cap4', 'cap5', 'cap6', 'cap7', 'cap8', 'cap9', 'cap10', 'cap11', 'cap12',  'cap13', 'cap14', 'cap15']

    # x_list_A = [-37500, -31200, -25000, -18300, -12000, -6000]
    # sample_list_A = ['hexane', 'toluene', 'PbS15_hexane_50mgmL','PbS16_hexane_25mgmL','PbS17_hexane_100mgmL','PbS22B_hexane_100mgmL']

    # x_list_B = [-43700, -37200, -31000, -24500, -18300, -11800, -5500]
    # sample_list_B = ['Fe3O4-9_14p9mgmL_toluene', 'Fe3O4-11_23p1mgmL_toluene', 'Fe3O4-14_7p4mgmL_toluene','Fe3O4-15_12p6mgmL_toluene','PbS25_100mgmL_hexane','PbS26_29p7mgmL_hexane','PbS27_31.3mgmL_hexane']

    # x_list_C = [38800, 32500, 25900, 19300, 13200, 7000, 500, -5800, -12100, -18450, -24900, -31350]
    # sample_list_C = ['FICO-6A_mgmL_hexane', 'FICO-6B_mgmL_hexane', 'FICO-6C_mgmL_hexane','FICO-6D_mgmL_hexane','FICO-6E_mgmL_hexane','FICO-6F_mgmL_hexane','FICO-7A2_mgmL_hexane','FICO-7A3_mgmL_hexane','FICO-7B2_mgmL_hexane','FICO-7D2_mgmL_hexane','FICO-2AW_mgmL_hexane','FICO-2AP_mgmL_hexane']

    # x_list_D = [38500, 32400, 25900, 19300, 13100, 6800]
    # sample_list_D = ['10mM_SDS_H2O', 'OLD_A_FICO_6E_1pcOA_50mM_SDS', 'OLD_B_FICO_6E_100mM_SDS','OLD_C_Fe3O4-11_PbS22B_1to1p5_1pcOA_10mM_SDS','OLD_D_Fe3O4-11_PbS22B_1to2_1pcOA_10mM_SDS','OLD_E_Fe3O4-11_PbS22B_1to2p5_1pcOA_10mM_SDS']

    x_list_E = [
        38800,
        32400,
        26100,
        19400,
        13400,
        6900,
        600,
        -5700,
        -12100,
        -18400,
        -25200,
        -31500,
        -37500,
        -44100,
    ]
    sample_list_E = [
        "PbS22B_FICO_7A2_2to1_1pcOA_10mM_SDS",
        "PbS22B_FICO_7A2_3to1_1pcOA_10mM_SDS",
        "PbS22B_FICO_7A2_4p5to1_1pcOA_10mM_SDS",
        "PbS25_PbS15_2to1_1pcoA_10mM_SDS",
        "PbS25_PbS15_1to1_1pcOA_10mM_SDS",
        "PbS25_PbS15_1to2_1pcOA_10mM_SDS",
        "PbS16_PbS15_2to1_1pcOA_10mM_SDS",
        "PbS16_PbS15_1to1_1pcOA_10mM_SDS",
        "PbS16_PbS15_1to2_1pcOA_10mM_SDS",
        "PbS22B_Fe3O4-11_1to1_1pcOA_10mM_SDS",
        "PbS22B_Fe3O4-11_2to1_1pcOA_10mM_SDS",
        "PbS22B_Fe3O4-11_13to1_1pcOA_10mM_SDS",
        "PbS22B_Fe3O4-14_1to1_1pcOA_10mM_SDS",
        "PbS22B_Fe3O4-14_1to2_1pcOA_10mM_SDS",
    ]

    # waxs_arc = [0, 13, 3]
    dets = [pil2M]
    # dets = [pil300KW, pil2M]

    for x, sample in zip(x_list_E, sample_list_E):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

        name_fmt = "{sample}_x{x_pos}_y{y_pos}_sax{saxs_z}m_{meas_t}s_{scan_id}"
        sample_name = name_fmt.format(
            sample=sample,
            x_pos=np.round(piezo.x.position, 2),
            y_pos=np.round(piezo.y.position, 2),
            saxs_z=np.round(pil2M_pos.z.position, 2),
            meas_t=meas_t,
            scan_id=RE.md["scan_id"],
        )
        sample_id(user_name="EM", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        # yield from bp.scan(dets, waxs, *waxs_arc)
        yield from bp.count(dets, num=1)


def in_situ(meas_t=1, t0=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a long in-situ *time series* — it loops up to 50000 times, and on each
    #   pass visits a few samples (moving piezo.y to each) and takes an image, stamping the
    #   elapsed time into the file name. It's watching colloidal assembly happen over hours.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built time-series plan (a "plan" is a recipe of steps Bluesky runs for you).
    #   It keeps taking images on a schedule and records the REAL elapsed time, position and
    #   beam intensity INTO each image — so the time ends up in the data itself, not just in
    #   the file name, and you don't manage the counter/clock by hand:
    #
    #     from smi_plans import time_series_run            # import once at session start
    #     yield from time_series_run(
    #         "Kin40_Fe11_PbS22B",                         # the rest of the file name is added automatically
    #         dets=[pil900KW, pil2M],                      # WAXS is pil900KW now — see ⚠️ below
    #         t=meas_t,                                    # your exposure, unchanged
    #         period=None, num=50000,                      # how often / how many frames (tune to taste)
    #     )
    #     # (to revisit several y-spots each pass, loop time_series_run over your y_list/sample_list)
    #
    #   Why this is nicer here: the old "for ii in range(50000)" loop drives the run from plain
    #   Python around bp.count, so the timing drifts and the elapsed time lives only in the file
    #   name; the smi_plans version records the true timestamps as data you can plot directly.
    #
    #   (This is just a suggestion to try later — your script below works as-is EXCEPT for the
    #    ⚠️ lines, which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (⚠️ notes below). (internal: Tier 0 — RE-driven Python loop around bp.count.)
    # === end smi_plans note ================================================
    y_list = [6200, 2150, -2200, -6350]
    # y_list = [-6350]

    sample_list = [
        "Kin40_Fe11_PbS22B_1to2_hextol_noOA_200mM-SDS_70C",
        "Kin39_FICO6C_PbS26_1to3_hextol_noOA_200mM-SDS_70C",
        "Kin38_FICO6C_PbS26_1to3p86_hextol_noOA_200mM-SDS_70C",
        "Kin37_FICO7B2_PbS26_1to6_hextol_noOA_200mM-SDS_70C",
    ]
    # sample_list = ['FICO_72A_70C_200mMSDS_noOA_monocrystal']
    # sample_list = ['xtestgreen32', 'xtestyellow31', 'xtestred30', 'xtestblue29']
    # sample_list = ['green', 'yellow', 'red', 'blue']

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    if t0 < 10:
        t0 = time.time()

    scan_id0 = RE.md["scan_id"] + 1
    yield from bps.sleep(1)
    count = 0

    for ii in range(50000):
        for y, sample in zip(y_list, sample_list):  # loop over samples on bar
            yield from bps.mv(piezo.y, y)
            det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = (
                "{sample}_x{x_pos}_y{y_pos}_sax{saxs_z}m_{meas_t}s_t{t}s_{scan_id}"
            )
            sample_name = name_fmt.format(
                sample=sample,
                x_pos=np.round(piezo.x.position, 2),
                y_pos=np.round(piezo.y.position, 2),
                saxs_z=np.round(pil2M_pos.z.position, 2),
                meas_t=meas_t,
                t=np.round(time.time() - t0, 0),
                scan_id=scan_id0 + count,
            )
            count = count + 1

            # name_fmt = '{sample}_{scan_id}_t{t}s_x{x_pos}_y{y_pos}_sax{saxs_z}m_{meas_t}s'
            # sample_name = name_fmt.format(sample=sample, scan_id=scan_id0+count, t=np.round(time.time()-t0, 0), x_pos=np.round(piezo.x.position,2), y_pos=np.round(piezo.y.position,2), saxs_z=np.round(pil2M_pos.z.position,2), meas_t=meas_t)

            sample_id(user_name="EM_insitu", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bps.sleep(1)
            yield from bp.count(dets, num=1)


def in_situ_wrap(meas_t=1, t0=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a safety wrapper around in_situ() — if the long time-series errors out,
    #   it waits 2 seconds and restarts it, so an overnight run keeps going after a glitch.
    #
    # 💡 NEWER, EASIER WAY: you usually won't need this hand-rolled retry once you migrate.
    #   smi_plans' time_series_run (see the note on in_situ above) is the supported way to do a
    #   long, robust in-situ acquisition. If you do want automatic restart-on-error, ask
    #   beamline staff about the suspender/auto-resume support that the newer plans plug into,
    #   rather than catching every exception with a bare 'except:' (which can also swallow a
    #   real stop request). (This wrapper isn't broken — it's just no longer the easiest path.)
    # === end smi_plans note ================================================
    if t0 < 10:
        t0 = time.time()
    try:
        yield from in_situ(meas_t, t0=t0)
    except:
        print("!!!! ERROR, but proceed in 2 sec!!!!")
        yield from bps.sleep(2)
        yield from in_situ_wrap(meas_t, t0=t0)


#
# Note:
# 2019-12-04 11pm started in-situ with 20ml/min at room temp; RE errors
# 2019-12-05 4pm tube broken, change to thick ones, also lower flow rate to 5 with higher temp
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Murray.py

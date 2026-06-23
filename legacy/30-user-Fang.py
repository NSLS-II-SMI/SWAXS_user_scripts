def ex_situ(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps along a bar of 14 samples (moving piezo.x to each) and takes one
    #   SAXS image per sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a multi-sample "bar" helper — you list the sample
    #   names and x positions once, and it visits each, takes the image, and records the
    #   position / beam / scan id straight INTO the data and the file name, so you don't have
    #   to hand-build "{sample}_x..._{scan_id}" or call sample_id yourself:
    #
    #     from smi_plans import SampleList, transmission_bar    # do this once per session
    #     samples = SampleList.from_columns(name=sample_list_E, x=x_list_E)  # your bar
    #     yield from transmission_bar(samples, dets=[pil2M], t=meas_t)
    #
    #   (Optional — your script below works as-is EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
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
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' transmission_bar sets exposure for you via t=.)

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


sample_id(user_name="Fang", sample_name="test")
sample_list = [
    "Au10_FF",
    "Au10FCC_50",
    "Au10FCC_100",
    "Au10FCC_150",
    "Au10FCC_200",
]
##150 should be 200
##200 should be 500

## Beam center: ( 431, 567 )
## det to sample distance: 5.3 meter
## 16.1 KeV
## beam size: 20 X 200


def movx(dx):
    yield from bps.mvr(piezo.x, dx)


def movy(dy):
    yield from bps.mvr(piezo.y, dy)


def measure_saxs(i, meas_t=1, att="Sn60X4", my=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS image of one sample from 'sample_list' (with a chosen
    #   attenuator), optionally nudging y by 30 first.
    #
    # 💡 NEWER, EASIER WAY: a single recorded SAXS shot is one 'smi_plans' acquire call, which
    #   records position / beam / scan id into the image and file name for you:
    #
    #     from smi_plans import acquire
    #     yield from acquire(sample_list[i], [pil2M], [], t=meas_t)   # one recorded SAXS image
    #
    #   (The attenuators 'att2_*' still work the same way — nothing broken there. Optional —
    #    your code below works as-is EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M]
    if my:
        yield from bps.mvr(piezo.y, 30)
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' acquire/transmission_run sets exposure for you via t=.)
    sample = sample_list[i]
    name_fmt = "{sample}_x{x_pos}_y{y_pos}_sax{saxs_z}m_{meas_t}s_{att}_att_{scan_id}"
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=np.round(piezo.x.position, 2),
        y_pos=np.round(piezo.y.position, 2),
        saxs_z=np.round(pil2M_pos.z.position, 2),
        meas_t=meas_t,
        att=att,
        scan_id=RE.md["scan_id"],
    )
    sample_id(user_name="Fang", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    # yield from bp.scan(dets, waxs, *waxs_arc)
    yield from bp.count(dets, num=1)


def in_situ(meas_t=1, t0=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time series — it loops "forever" (up to 50000 rounds), and on
    #   each round visits a few y positions / samples and takes a WAXS+SAXS image, stamping the
    #   elapsed time since t0 into the file name. (This is a time-resolved / kinetics run.)
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has time-series / kinetics helpers that repeat a
    #   measurement on a schedule and record the real elapsed time, position, and beam into
    #   each image automatically (so you don't compute "t{t}s" by hand or manage the scan_id):
    #
    #     from smi_plans import time_series_run         # do this once per session
    #     # repeat a SAXS/WAXS measurement over time; it timestamps each point for you.
    #     # For a multi-sample version, combine with a SampleList of the y positions/names.
    #
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (Optional — your script below works as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call needs to be run as a plan (see ⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    y_list = [6200, 2150, -2200, -6350]

    sample_list = [
        "Kin40_Fe11_PbS22B_1to2_hextol_noOA_200mM-SDS_70C",
        "Kin39_FICO6C_PbS26_1to3_hextol_noOA_200mM-SDS_70C",
        "Kin38_FICO6C_PbS26_1to3p86_hextol_noOA_200mM-SDS_70C",
        "Kin37_FICO7B2_PbS26_1to6_hextol_noOA_200mM-SDS_70C",
    ]
    # sample_list = ['FICO_72A_70C_200mMSDS_noOA_monocrystal']
    # sample_list = ['xtestgreen32', 'xtestyellow31', 'xtestred30', 'xtestblue29']
    # sample_list = ['green', 'yellow', 'red', 'blue']

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)
    if t0 < 10:
        t0 = time.time()

    scan_id0 = RE.md["scan_id"] + 1
    yield from bps.sleep(1)
    count = 0

    for ii in range(50000):
        for y, sample in zip(y_list, sample_list):  # loop over samples on bar
            yield from bps.mv(piezo.y, y)
            det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' time_series_run sets exposure for you via t=.)

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
    # WHAT THIS DOES: runs in_situ() and, if it errors, waits 2 s and restarts it — a
    #   crash-resistant wrapper so a long overnight in-situ run keeps going.
    #
    # 💡 NEWER, EASIER WAY: see the in_situ note above (time_series_run). smi_plans' time-series
    #   helpers are designed to run unattended, so you generally don't need this retry wrapper.
    #   (Optional — this wrapper still works as-is.)
    # === end smi_plans note ================================================
    if t0 < 10:
        t0 = time.time()
    try:
        yield from in_situ(meas_t, t0=t0)
    except:
        print("!!!! ERROR, but proceed in 2 sec!!!!")
        yield from bps.sleep(2)
        yield from in_situ_wrap(meas_t, t0=t0)


# print(time.strftime('%Y-%m-%dT%H:%M:%S %Z',time.localtime(time.time())))


# proposal_id('2019_3', '305435_Murray')
# purple OnAxis is beam position in air

# ======== To open bluesky: bsui

# --- Close the hutch
#
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Murray.py
#
# --- To take a single measurement:
# sample_id(user_name='EM',sample_name='test') then, on Pilatus1M, enter exposure time and click 'Start'
#
#
# --- Before opening hutch:
# If bluesky is set to running and want to stop just type 'exit'
#
# bsx 1.050000 for saxs_z 8300
# bsx0.350000 for saxs_z 7300
# bsx0.750000 for saxs_z 6300
# bsx1.500000 for saxs_z 5300
#
# --- To move WAXS detector (Pilatus 300K)
#
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Fang.py

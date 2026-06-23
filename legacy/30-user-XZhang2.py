##Collect data:

# SMI: 2021/10/29

# create proposal:  proposal_id('2021_3', '30000_YZhang_XZ')    #create the proposal id and folder
# create proposal:  proposal_id('2021_3', '30000_YZhang_Nov')    #create the proposal id and folder
# create proposal:  proposal_id('2021_3', '307961_Dinca')    #create the proposal id and folder


# Energy: 16.1 keV, 0.77009 A
# SAXS distance 5000
# SAXS in vacuum and WAXS in vacuum


# For WAXS,
# WAXS beam center: [  87, 97   ], there is bad pixel here  could check later,  (BS: X: -20.92 )
# Put Att and move bs to check the BC_WAXS, --> [ 87, 97 ]


# beam center [488, 591]


# Fisrt Run, 1 samples, make hexpod Y = -5
# Pizo_Z, 2100


sample_dict = {
    1: "XZ_S1_1_Chitosan_Cu_Fiber_Wet",
    2: "XZ_S2_2_NaCellulose",
    3: "XZ_S2_7_Crab_Chitasan",
    4: "XZ_S2_9_CuNa_CellusloseNaOH",
    5: "XZ_S2_9_CuNa_Celluslose",
}
pxy_dict = {
    1: (-32800, -1000),
    2: (-27300, -700),
    3: (-16000, -1000),
    4: (-2600, -1000),
    5: (20400, -6000),
}

# manually measure each sampls
# Sam1,
# mov_sam(1)
# RE( measure_waxs( t = 1, waxs_angle=0, att='None', dy=0, user_name='', sample= None )  )
# Change CHI to 6 deg, do measrue_S1,, sid00005868 -->  sid00005871
# Change CHI to 0 deg, do measrue_S1,,
# Sam2-5,
#  For sam5, rot chi to 6, sid00005912  -->    sid00005915
# Then measrue SAXS, looks like no signal in SAXS for all samples


# Second Run, 4 samples + MIT_Sample, make hexpod Y = -5
# make hexpod Y = -6
# Pizo_Z, 2100


sample_dict = {
    1: "XZ_S2_1_Wood",
    2: "XZ_S2_4_CrabTendonChitin",
    3: "YG_Standard_Al2O3",
    4: "XZ_S2_5_SquidChitin",
    5: "XZ_S2_6_CrabTendonChitosan",
    6: "Dinca_Unkown_X1",
    7: "Dinca_Unkown_X2",
    8: "Dinca_Unkown_X3",
    9: "Dinca_PowderA",
    10: "Dinca_PowderB",
}

pxy_dict = {
    1: (31789, -8000),
    2: (25800, -700),
    3: (13800, -1000),
    4: (7600, -6000),
    5: (-4400, -6000),
}


# name_sam( 1 )
# 2, looks nice
# 4, squid, looks find
# 5, looks nice
# sample 3, Al2O3, standard sample

# 6-10, DC samples


def measure_Al2O3():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: maps a standard Al2O3 sample — for each WAXS-arc angle it steps the sample
    #   up/down in z (100 positions) and takes a WAXS measurement at each, calling measure_waxs.
    #
    # 💡 NEWER, EASIER WAY: notice this drives the beamline by calling RE(...) INSIDE a Python for
    #   loop. That works, but it starts a brand-new "run" for every single point, so the z position
    #   isn't recorded as a swept axis. In 'smi_plans' you instead build ONE plan that sweeps z and
    #   the WAXS arc as "axes" and hand it to RE once — the z/arc/beam values then land IN the data:
    #
    #     from smi_plans import acquire, motor_axis
    #     RE(acquire(sample, [pil900KW],
    #         [motor_axis("waxs_arc", waxs.arc, [0,5,7,10,15,20,25,27,30,35,40,45,47,50,55,60]),
    #          motor_axis("z", piezo.z, np.arange(-5000, 5000, 100))], t=1))
    #
    #   (Optional — your loop still works as-is. Note measure_waxs itself uses the retired pil300KW
    #    detector; see the ⚠️ inside measure_waxs.)  (internal: Tier 0.)
    # === end smi_plans note ================================================
    WA = np.array([0, 5, 7, 10, 15, 20, 25, 27, 30, 35, 40, 45, 47, 50, 55, 60])
    sample = RE.md["sample"]
    pz_list = np.arange(-5000, 5000, 100)
    for wa in WA:
        for pz in pz_list:
            RE(bps.mv(piezo.z, pz))
            sami = sample + "_PZ_%.0f" % piezo.z.position
            RE(
                measure_waxs(
                    t=1, waxs_angle=wa, att="None", dy=0, user_name="", sample=sami
                )
            )


def measure_One():
    WA = np.array(
        [
            0,
            5,
            15,
            25,
        ]
    )
    if abs(waxs.arc.user_readback.value - WA.max()) < 2:
        WA = WA[::-1]
    for wa in WA:
        RE(
            measure_waxs(
                t=1, waxs_angle=wa, att="None", dy=0, user_name="", sample=None
            )
        )


def check_sample_loc(sleep=5):
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        time.sleep(sleep)


def measure_XZ_Run2(Index=[1], N=8):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the run-book for "Run 2" — for each sample index it moves to that sample and
    #   does a y-line WAXS scan at arc=0, then repeats the loop doing it at arc=20.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you'd list the samples once (a "bar") and let one plan
    #   visit each and sweep the WAXS arc + y, recording sample/position into the data, instead of
    #   two passes of RE(...)-in-a-loop. See measure_waxs0_XZ_scany below (which has the ⚠️ pil300KW
    #   fix). (Nothing here is broken; this is just the tidier pattern.)  (internal: Tier 0/1.)
    # === end smi_plans note ================================================
    # Index = [1,2,3,6,7]
    for i in Index:
        mov_sam(i)
        measure_waxs0_XZ_scany(N=N)
    for i in Index:
        mov_sam(i)
        measure_waxs20_XZ_scany(N=N)


def measure_waxs0_XZ_scany(N=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a y-line WAXS scan at arc angle 0 — takes a WAXS measurement, steps the
    #   sample up by 500 in y, and repeats N times (a quick "scan along the sample" in y).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' turns the y steps into a recorded axis so the y position is
    #   saved with each frame, in one plan:
    #     from smi_plans import acquire, motor_axis
    #     RE(acquire(RE.md["sample"], [pil900KW],
    #         [motor_axis("y", piezo.y, np.arange(0, N*500, 500))], t=1))
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'dets = [pil900KW, pil300KW]' line uses 'pil300KW', which was
    #   retired — that line would error. Use 'pil900KW' (see the ⚠️ note on it). (The actual frames
    #   here come from measure_waxs, which has the same fix flagged.)  (internal: Tier 0.)
    # === end smi_plans note ================================================
    sample = RE.md["sample"]
    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    for i in range(N):
        RE(
            measure_waxs(
                t=1, waxs_angle=0, att="None", dy=0, user_name="XZ", sample=sample
            )
        )
        RE(bps.mvr(piezo.y, 500))


def measure_waxs20_XZ_scany(N=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same as measure_waxs0_XZ_scany but at WAXS arc angle 20 — a y-line scan that
    #   steps up 500 in y and measures N times (note: it calls measure_wsaxs, the combined run).
    #
    # 💡 NEWER, EASIER WAY: same idea — let 'smi_plans' record the y axis for you in one plan
    #   (acquire + motor_axis("y", piezo.y, ...)). See measure_waxs0_XZ_scany above for the form.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'dets = [pil900KW, pil300KW]' line uses the retired 'pil300KW'
    #   (it would error) — use 'pil900KW'. See the ⚠️ note on that line. (internal: Tier 0.)
    # === end smi_plans note ================================================
    sample = RE.md["sample"]
    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    for i in range(N):
        RE(
            measure_wsaxs(
                t=1, waxs_angle=20, att="None", dy=0, user_name="XZ", sample=sample
            )
        )
        RE(bps.mvr(piezo.y, 500))


##################################################
############ Some convinent functions#################
#########################################################


def movx(dx):
    RE(bps.mvr(piezo.x, dx))


def movy(dy):
    RE(bps.mvr(piezo.y, dy))


def get_posxy():
    return round(piezo.x.user_readback.value, 2), round(piezo.y.user_readback.value, 2)


def move_waxs(waxs_angle=8.0):
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_off(waxs_angle=8.0):
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_on(waxs_angle=0.0):
    RE(bps.mv(waxs, waxs_angle))


def mov_sam(pos):
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px))
    RE(bps.mv(piezo.y, py))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample


def name_sam(pos):
    sample = sample_dict[pos]
    print("Change sample name at pos=%s to:%s" % (pos, sample))
    RE.md["sample"] = sample


def check_saxs_sample_loc(sleep=5):
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        time.sleep(sleep)


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick one-shot WAXS "snapshot" with a test name, for checking the beam.
    # 💡 NEWER, EASIER WAY: a single shot is just an 'acquire' with no axes in smi_plans, e.g.
    #     from smi_plans import acquire
    #     yield from acquire("test", [pil900KW], [], t=t)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on the lines below.
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick one-shot SAXS "snapshot" with a test name (pil2M is the SAXS camera).
    # 💡 NEWER, EASIER WAY: in smi_plans this is  yield from acquire("test", [pil2M], [], t=t).
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan — see the ⚠️ note on that line below.
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_samples_saxs_map1():
    mov_sam(0)
    # xlist = np.linspace( 38000, 41600, 121 )  #[ 38700,   39100,    39500,  39900, 40100   ]
    # ylist = [ ]
    # first try
    xlist = [
        39500,
    ]
    ylist = np.linspace(-6030, -6030 + 2 * 500, 501)  # NO peaks beam damage?
    # second try
    xlist = [39500 - 500]
    ylist = np.linspace(-6030, -6030 + 4 * 200, 201)  # NO peaks, beam damage?
    # Third try
    xlist = [39500 - 1000]
    ylist = np.linspace(-6030, -6030 + 10 * 100, 101)  # Some peaks
    # Forth try
    xlist = [39500 + 200]
    ylist = np.linspace(-6030, -6030 + 10 * 100, 101)  # No Peaks, beam damage already
    # Fifth try
    xlist = [39500 + 1000]
    ylist = np.linspace(-6030, -6030 + 10 * 100, 101)  # #Some peaks
    # six try
    xlist = np.linspace(38000, 38000 + 60 * 50, 51)  #
    ylist = [-5200]

    # 7 try
    xlist = np.linspace(38000, 38000 + 60 * 50, 51)  #
    ylist = [-4500]

    print(xlist, ylist)
    RE(
        measure_saxs_map(
            xlist,
            ylist,
            user_name="HZ",
            sample=None,
            att="None",
        )
    )


def do_one_map(sam_id, xstart, ystart_up, ystart_bot, dia=3):
    mov_sam(sam_id)
    if dia == 3:
        Nx = 18

    xlist = np.linspace(xstart, xstart + 220 * (Nx - 1), Nx)
    ylist = np.linspace(ystart_up, ystart_up + 30 * 50, 51)
    sample = RE.md["sample"] + "Up"
    RE(
        measure_saxs_map(
            xlist,
            ylist,
            t=1,
            user_name="HZ",
            sample=sample,
            att="None",
        )
    )
    ylist = np.linspace(ystart_bot, ystart_bot + 30 * 50, 51)
    sample = RE.md["sample"] + "Bot"
    RE(
        measure_saxs_map(
            xlist,
            ylist,
            t=1,
            user_name="HZ",
            sample=sample,
            att="None",
        )
    )
    mov_sam(sam_id)
    sample = RE.md["sample"] + "ScanY"
    RE(
        measure_saxs_scany(
            N=220,
            t=1,
            user_name="HZ",
            sample=sample,
            att="None",
        )
    )


def measure_samples_saxs_map():

    do_one_map(1, xstart=35600, ystart_up=-7800, ystart_bot=-1900)
    do_one_map(2, xstart=28400, ystart_up=-7300, ystart_bot=-2900)
    do_one_map(3, xstart=20500, ystart_up=-4200, ystart_bot=300)
    do_one_map(4, xstart=35600, ystart_up=-7800, ystart_bot=-3400)
    do_one_map(5, xstart=14000, ystart_up=-5500, ystart_bot=-1000)
    do_one_map(6, xstart=5000, ystart_up=-6600, ystart_bot=-3600)
    do_one_map(7, xstart=-11700, ystart_up=-7200, ystart_bot=-900)


def measure_saxs_map(
    xlist,
    ylist,
    t=1,
    user_name="HZ",
    sample=None,
    att="None",
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 2D SAXS raster map — steps the sample across a grid of x and y positions
    #   and takes a SAXS image at each (the file name records x/y/detector-distance/exposure).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has dedicated mapping plans that build the x/y grid for you
    #   and write the position + beam INTO each image, so you don't hand-format that long name:
    #
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, piezo.x, xlist, piezo.y, ylist, dets=[pil2M], t=t)
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    dets = [pil2M]
    for px in xlist:
        yield from bps.mv(piezo.x, px)
        for py in ylist:
            yield from bps.mv(piezo.y, py)
            name_fmt = "{sample}_x{x_pos}_y{y_pos}_det{saxs_z}m_expt{expt}s_att{att}_sid{scan_id:08d}"
            sample_name = name_fmt.format(
                sample=sample,
                x_pos=np.round(piezo.x.position, 2),
                y_pos=np.round(piezo.y.position, 2),
                saxs_z=np.round(pil2M_pos.z.position, 2),
                expt=t,
                att=att,
                scan_id=RE.md["scan_id"],
            )
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            sample_id(user_name=user_name, sample_name=sample_name)
            yield from bp.count(dets, num=1)


def measure_saxs_scany(
    N,
    t=1,
    user_name="HZ",
    sample=None,
    att="None",
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS y-line scan — takes N SAXS images, nudging the sample by 30 in y each
    #   time (the file name records x/y/detector-distance/exposure).
    # 💡 NEWER, EASIER WAY: let smi_plans record the y axis for you in one plan:
    #     from smi_plans import map_line_run
    #     yield from map_line_run(sample, piezo.y, 0, 30*(N-1), N, dets=[pil2M], t=t)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    dets = [pil2M]
    for i in range(N):
        name_fmt = "{sample}_x{x_pos}_y{y_pos}_det{saxs_z}m_expt{expt}s_att{att}_sid{scan_id:08d}"
        sample_name = name_fmt.format(
            sample=sample,
            x_pos=np.round(piezo.x.position, 2),
            y_pos=np.round(piezo.y.position, 2),
            saxs_z=np.round(pil2M_pos.z.position, 2),
            expt=t,
            att=att,
            scan_id=RE.md["scan_id"],
        )
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        yield from bp.count(dets, num=1)
        yield from bps.mv(piezo.y, 30)


def measure_pindiol_current():
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr


def measure_saxs(t=1, att="None", dy=0, user_name="XZ", sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the reusable "take one SAXS image of the current sample" helper — optionally
    #   nudges y first, then builds a descriptive file name and snaps one pil2M image.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' a single SAXS frame is an 'acquire' with no axes, and it
    #   records x/y/detector-distance/beam INTO the data and fills the file name from those recorded
    #   fields (so you don't read .position into the name by hand):
    #     from smi_plans import acquire
    #     yield from acquire(sample or RE.md["sample"], [pil2M], [], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    dets = [pil2M]
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = (
        "{sample}_x{x_pos}_y{y_pos}_det{saxs_z}m_expt{expt}s_att{att}_sid{scan_id:08d}"
    )
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=np.round(piezo.x.position, 2),
        y_pos=np.round(piezo.y.position, 2),
        saxs_z=np.round(pil2M_pos.z.position, 2),
        expt=t,
        att=att,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")
    # det_exposure_time(0.5)


def measure_waxs(t=1, waxs_angle=0, att="None", dy=0, user_name="XZ", sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the reusable "move the WAXS arc to an angle and take one WAXS image of the
    #   current sample" helper, with a descriptive file name.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' a WAXS shot is an 'acquire' that records arc-angle/x/y/
    #   beam into the data; to sweep several arc angles, hand it a motor_axis instead of looping:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(sample or RE.md["sample"], [pil900KW],
    #                        [motor_axis("waxs_arc", waxs.arc, [waxs_angle])], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        waxs_angle=waxs_angle,
        expt=t,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    # sample_id(user_name='test', sample_name='test')


def measure_wsaxs(t=1, waxs_angle=20, att="None", dy=0, user_name="XZ", sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like measure_waxs but records BOTH detectors at once (WAXS + SAXS): it moves
    #   the WAXS arc, then takes one combined image set of the current sample.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you just list both detectors in one acquire and it saves
    #   WAXS + SAXS together with the recorded angle/position/beam:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(sample or RE.md["sample"], [pil900KW, pil2M],
    #                        [motor_axis("waxs_arc", waxs.arc, [waxs_angle])], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_det{saxs_z}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2M_pos.z.position, 2),
        waxs_angle=waxs_angle,
        expt=t,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    # sample_id(user_name='test', sample_name='test')


def measure_series_saxs(
    t=[1],
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_saxs(t=ti, att="None", dy=dy))


def measure_series_waxs(
    t=[1],
    waxs_angle=20,
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    ks = list(sample_dict.keys())[:8]
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_waxs(t=ti, waxs_angle=waxs_angle, att="None", dy=dy))


def measure_waxs_multi_angles(
    t=1.0,
    att="None",
    dy=0,
    user_name="",
    saxs_on=False,
    waxs_angles=[0.0, 6.5, 13.0],
    inverse_angle=False,
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sweeps the WAXS detector arc through several angles and takes a WAXS image at
    #   each (optionally adding a SAXS image at the largest arc angle). It can also sweep the angles
    #   in reverse so the arc doesn't have to travel all the way back.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the arc angles become a recorded "axis" handed to one
    #   acquire call, which writes the arc angle + position + beam INTO each image:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(RE.md["sample"], [pil900KW],
    #         [motor_axis("waxs_arc", waxs.arc, waxs_angles, reverse_alternate=inverse_angle)], t=t)
    #   (For the multi-sample version, giwaxs_bar_arc_economy sweeps the arc the short way for you.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines below. (internal: Tier 1.)
    # === end smi_plans note ================================================

    # waxs_angles = np.linspace(0, 65, 11)   #the max range
    # waxs_angles =   np.linspace(0, 65, 11),
    # [ 0. ,  6.5, 13. , 19.5]

    waxs_angle_array = np.array(waxs_angles)
    if inverse_angle:
        waxs_angle_array = waxs_angle_array[::-1]
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    max_waxs_angle = np.max(waxs_angle_array)
    for waxs_angle in waxs_angle_array:
        yield from bps.mv(waxs, waxs_angle)
        sample = RE.md["sample"]
        if dy:
            yield from bps.mvr(piezo.y, dy)
        name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
        sample_name = name_fmt.format(
            sample=sample,
            x_pos=piezo.x.position,
            y_pos=piezo.y.position,
            z_pos=piezo.z.position,
            waxs_angle=waxs_angle,
            expt=t,
            scan_id=RE.md["scan_id"],
        )
        print(sample_name)
        if saxs_on:
            if waxs_angle == max_waxs_angle:
                dets = [
                    pil2M,
                    pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
                ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
            else:
                dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        # yield from bp.scan(dets, waxs, *waxs_arc)
        yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick one-shot WAXS snapshot (this copy uses the current pil900KW camera).
    # 💡 NEWER, EASIER WAY: in smi_plans this is  yield from acquire("test", [pil900KW], [], t=t).
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan — see the ⚠️ note on that line below.
    # === end smi_plans note ================================================
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick one-shot SAXS snapshot (pil2M is the SAXS camera).
    # 💡 NEWER, EASIER WAY: in smi_plans this is  yield from acquire("test", [pil2M], [], t=t).
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan — see the ⚠️ note on that line below.
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_pindiol_current():
    # smi_plans: no acquisition here — just opens the fast shutter, reads a diode current, and
    #   closes it (a diagnostic helper, nothing to migrate).
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr

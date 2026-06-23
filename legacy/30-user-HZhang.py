##Collect data:

# SMI: 2021/9/22


# create proposal:  proposal_id('2021_3', '30000_YZhang')    #create the proposal id and folder
# Energy: 16.1 keV, 0.77009 A
# SAXS distance 5000
# SAXS in vacuum and WAXS in air


# low div beam, 220 X 30 um2
# For 8 meter, beamStopX: 0.7 , 1M: X 0.25 , Center [ 490, 588 ]
# For 5 meter, beamstopX: 1.85 , 1M, X  1.13,   Center, [490, 588 ]
# For 3 meter, beamstopX: 1.9, 1M, X, 1.43 Center, [490, 588 ]
### For 2 meter, beamstopX: 1.8, 1M, X, 1.05 Center, [490, 588 ]


#  RE( shopen() )  # to open the beam and feedback
#  RE( shclose())

#  %run -i

# The beam center on SAXS:  [ 485, 566 ]
# Energy: 16.1 keV, 0.77009 A
# SAXS distance 5000
## For pindiol:
#   No filter, it's saturated ( 125257)
#   Sn30 um, X1, still saturated ( 125257 )  #RE(bps.mv(att1_9.open_cmd, 1))
#   Sn30 um, X2, still saturated ( 125256 )  #RE(bps.mv(att1_10.open_cmd, 1))
#   Sn30 um, X3 (X1 + X2) ,  (67713 )
#   Sn30 um, X4,  (27456)
# Sn30 um, X5,  (11334 )
#   Sn30 um, X8,  (722)


# For WAXS,
# WAXS beam center: [  87, 97   ], there is bad pixel here  could check later,  (BS: X: -20.92 )
# Put Att and move bs to check the BC_WAXS, --> [ 87, 97 ]


# beam center [488, 591]


## For 8 meter, beamStopX: 1.04857 , 1M: X 0.24 , Center [ 490, 588 ]
#
########################
# First Run for HZhang, microfocusing,

# sample_dict = {    0: 'HZ_S21_10nmAu_10nmSalt_SiliconOil',     }
# pxy_dict = {   0:  ( 39400, -5300)  }


########################
# Second Run for HZhang, low divergency

# low div beam, 220 X 30 um2
# Hexpond Y changes from 0 to 1
# For 8 meter, beamStopX: 0.7 , 1M: X 0.247 , Center [ 490, 586 ]


# sample_dict = {    1: 'HZ2_S21_PEG2K_Au10_SilOil_10mMNaCl_R1', 2: 'HZ2_S22_PEG2K_Au10_SilOil_500mMNaCl_R1', 3: 'HZ2_S23_20nmAu_10nmSalt_SiliconOil',
# 4: 'HZ2_S24_PEG2K_Au20_SilOil_500mMNaCl_R1', 5: 'HZ2_S25_PEG2K_Au10_SilOil_10mMNaCl_tubingD_356', 6: 'HZ2_S26_PEG2K_Au10_SilOil_10mMNaCl_tubingD_3000',
# 7: 'HZ2_S27_PEG2K_Au10_SilOil_10mMNaCl_tubingD_223'    }
# pxy_dict = {  1:  ( 37400, -8000), 2:  ( 30000, -7500),  3:  ( 22200, -4500  ),  4:  ( 37400, -8000), 5:  ( 15800, -5500), 6:  ( 7200, -7000), 7:  ( -2200, -6000),
# 7:  ( -10200, -7500),   }  #looks like the 4 is not correct,  the 4 just repeat 1, 5 should sample4, 6 should sample5, 7 should be sample 7. Did not measrue Sample 6


########################
# Third Run for HZhang, low divergency, Thursday night, around 11:30 pm

# low div beam, 220 X 30 um2
# Hexpond Y changes from 0 to -2
# For 8 meter, beamStopX: 0.7 , 1M: X 0.247 , Center [ 490, 586 ]


sample_dict = {
    1: "HZ2_S21_PEG2K_Au10_SilOil_10mMNaCl_R1",
    2: "HZ2_S22_PEG2K_Au10_SilOil_500mMNaCl_R1",
    3: "HZ2_S23_20nmAu_10nmSalt_SiliconOil",
    4: "HZ2_S24_PEG2K_Au20_SilOil_500mMNaCl_R1",
    5: "HZ2_S25_PEG2K_Au10_SilOil_10mMNaCl_tubingD_356",
    6: "HZ2_S26_PEG2K_Au10_SilOil_10mMNaCl_tubingD_3000",
    7: "HZ2_S27_PEG2K_Au10_SilOil_10mMNaCl_tubingD_223",
    8: "HZ3_S31_PEG2K_Au10_SilOil_100mMNaCl_100nM",
    9: "HZ3_S32_PEG2K_Au10_SilOil_100mMNaCl_20nM",
    10: "HZ3_S33_PEG2K_Au10_OA_100mMNaCl_20nM",
    11: "HZ3_S34_PEG2K_Au10_BuOH_100mMNaCl_20nM",
    12: "HZ3_S35_PEG2K_Au10_SilOil_10mMNaCl_20nM",
    13: "HZ3_S36_PEG2K_Au10_SilOil_500mMNaCl_20nM",
}
pxy_dict = {
    1: (37400, -8200),
    2: (30000, -7500),
    3: (22200, -4500),
    4: (15800, -4300),
    5: (7200, -7000),
    6: (-2200, -6000),
    7: (-10200, -7500),
    8: (-16900, -3000),
    9: (-22500, -3660),
    10: (-28800, -2460),
    11: (-33100, -2200),
    12: (-37200, -4600),
    13: (-41100, -5300),
}


def measure_samples_saxs_map_923Ngt():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a top-level run-book — for a handful of samples it does a single
    #   y-scan, and for the rest it does full 2-D maps (top and bottom regions) plus a
    #   y-scan, by calling the do_one_yscan / do_one_map helpers below.
    #
    # 💡 NEWER, EASIER WAY: the helpers this calls start a brand-new run with RE(...) for
    #   each step. The 'smi_plans' helper library can run a whole list of samples as ONE
    #   coordinated mapping measurement and record which sample each frame belongs to. See
    #   map_bar / map_grid_run / map_line_run, e.g.:
    #
    #     from smi_plans import map_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     RE(map_bar(samples, ...))     # one coordinated run instead of many
    #
    #   (Just a tidier option to try later — the run-book below still works as-is.)
    # === end smi_plans note ================================================
    for i in [1, 2, 3, 4, 5, 7]:
        do_one_yscan(i)
    do_one_map(6, xstart=-4200, ystart_up=-5600, ystart_bot=-1800)
    do_one_map(8, xstart=-18400, ystart_up=-3000, ystart_bot=1200)
    do_one_map(9, xstart=-24100, ystart_up=-3400, ystart_bot=900)
    do_one_map(10, xstart=-30400, ystart_up=-2460, ystart_bot=1940)
    do_one_map(11, xstart=-34700, ystart_up=-2200, ystart_bot=-700)
    do_one_map(12, xstart=-38500, ystart_up=-4600, ystart_bot=1000)
    do_one_map(13, xstart=-42700, ystart_up=-5200, ystart_bot=-1000)


##################################################
############ Some convinent functions#################
#########################################################


def movx(dx):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortcut to nudge the sample left/right (piezo.x) by dx.
    #
    # 💡 NEWER, EASIER WAY: this calls RE(...) inside a function, which only works when you
    #   type it at the prompt — it can't be used inside a "plan" (a recipe other plans run).
    #   Inside a plan you'd write  yield from bps.mv(piezo.x, new_position). At the prompt,
    #   RE(bps.mvr(piezo.x, dx)) is fine as-is. (Nothing here is broken.)
    # === end smi_plans note ================================================
    RE(bps.mvr(piezo.x, dx))


def movy(dy):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortcut to nudge the sample up/down (piezo.y) by dy.
    #
    # 💡 NEWER, EASIER WAY: same idea as movx — RE(...) inside a function only works at the
    #   prompt, not inside a plan; inside a plan use  yield from bps.mv(piezo.y, ...).
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    RE(bps.mvr(piezo.y, dy))


def get_posxy():
    return round(piezo.x.user_readback.value, 2), round(piezo.y.user_readback.value, 2)


def move_waxs(waxs_angle=8.0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS detector arc to the given angle.
    #
    # 💡 NEWER, EASIER WAY: like the movers above, RE(...) inside a function only works at
    #   the prompt; inside a plan use  yield from bps.mv(waxs, angle). In smi_plans the arc
    #   position is usually handled for you by saxs_waxs_dets / the grazing presets.
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_off(waxs_angle=8.0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS arc (same as move_waxs). 💡 RE(...) inside a function
    #   only works at the prompt; inside a plan use  yield from bps.mv(waxs, angle).
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_on(waxs_angle=0.0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS arc back toward 0. 💡 RE(...) inside a function only
    #   works at the prompt; inside a plan use  yield from bps.mv(waxs, angle).
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    RE(bps.mv(waxs, waxs_angle))


def mov_sam(pos):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to a numbered sample — it looks up that sample's x/y from
    #   pxy_dict, moves piezo.x and piezo.y there, and stashes the sample name in RE.md.
    #
    # 💡 NEWER, EASIER WAY: with the 'smi_plans' helper library you describe your samples
    #   once as a SampleList (name + x/y/z), and the plans move to each sample for you and
    #   record which sample each frame belongs to — so you don't keep parallel dicts or poke
    #   RE.md['sample'] by hand. See SampleList.from_columns(...) and goto_sample. (Note: this
    #   uses RE(...) inside a function, which only works at the prompt; inside a plan you'd
    #   use  yield from bps.mv(...). Nothing here is broken.)
    # === end smi_plans note ================================================
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px))
    RE(bps.mv(piezo.y, py))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample


def check_saxs_sample_loc(sleep=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick visual check — steps through every sample position (via
    #   mov_sam) pausing a few seconds at each so you can confirm the coordinates.
    #
    # 💡 NEWER, EASIER WAY: nothing here is broken. With smi_plans you'd describe the
    #   positions once as a SampleList and could step through them with goto_sample; this
    #   loop is fine as a quick eyeball check.
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        time.sleep(sleep)


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single quick WAXS snapshot (a test image).
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-shot acquire that records the beam readings
    #   into the saved data for you, e.g.  yield from acquire("test", [pil900KW], []).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t)' is now a "plan" (plain call does
    #   nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (Heads up: there is a
    #   SECOND snap_waxs defined later in this file that overrides this one — that later copy
    #   uses the current 'pil900KW'.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' technique runs set it for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single quick SAXS snapshot (a test image).
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-shot acquire that records the beam readings
    #   into the saved data for you, e.g.  yield from acquire("test", [pil2M], []).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(t)' is now a "plan" (plain call does
    #   nothing) — see the ⚠️ note below.
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' technique runs set it for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_samples_saxs_map1():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book that picks an x/y grid (the later xlist/ylist assignments
    #   below win) and then runs a SAXS map over it via measure_saxs_map.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library has ready-made mapping plans that
    #   raster a grid and record the positions + beam readings into the saved data for you:
    #
    #     from smi_plans import map_grid_run, spatial_grid_axes
    #     RE(map_grid_run("HZ", *spatial_grid_axes(piezo.x, xlist, piezo.y, ylist),
    #                     dets=[pil2M]))
    #
    #   (Just a tidier option to try later — your run-book below still works as-is.)
    # === end smi_plans note ================================================
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


def do_one_yscan(sam_id):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to a numbered sample, then runs a 220-point y-scan on it
    #   (via measure_saxs_scany), tagging the name with "ScanY".
    #
    # 💡 NEWER, EASIER WAY: smi_plans' map_line_run does a line scan and records the
    #   positions for you, e.g.  RE(map_line_run(name, piezo.y, y0, y1, 220, dets=[pil2M])).
    #   (This calls RE(...) inside a function, which only works at the prompt. Nothing here
    #   is broken.)
    # === end smi_plans note ================================================
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


def do_one_map(sam_id, xstart, ystart_up, ystart_bot, dia=3):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to a numbered sample and maps it — a 2-D SAXS map over the
    #   "Up" region, another over the "Bot" region, then a y-scan, by calling
    #   measure_saxs_map / measure_saxs_scany.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' map_grid_run rasters a 2-D grid in one coordinated
    #   run and records the positions for you, so you don't start three separate RE(...)
    #   runs per sample:
    #
    #     from smi_plans import map_grid_run, spatial_grid_axes
    #     RE(map_grid_run(sample, *spatial_grid_axes(piezo.x, xlist, piezo.y, ylist),
    #                     dets=[pil2M]))
    #
    #   (Just a tidier option to try later — the run-book below still works as-is.)
    # === end smi_plans note ================================================
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book that maps each of samples 1-7 in turn by calling do_one_map.
    #
    # 💡 NEWER, EASIER WAY: with smi_plans you can describe the samples once as a SampleList
    #   and run the whole bar of maps as one coordinated measurement via map_bar, so each
    #   frame knows which sample it belongs to. (Just a tidier option to try later — this
    #   run-book still works as-is.)
    # === end smi_plans note ================================================
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
    # WHAT THIS DOES: rasters the sample over a 2-D grid (every x in xlist × every y in
    #   ylist) and takes a SAXS image at each point, building the file name from the live
    #   positions and detector distance.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   ready-made grid map. It records the x/y positions, detector distance, beam readings,
    #   etc. straight INTO the saved data and fills the file name from them — so you don't
    #   read piezo.x.position / pil2M_pos.z.position by hand. Also note: right now this takes
    #   a separate "run" per point; map_grid_run does the whole grid as ONE run:
    #
    #     from smi_plans import map_grid_run, spatial_grid_axes
    #     yield from map_grid_run(sample,
    #                             *spatial_grid_axes(piezo.x, xlist, piezo.y, ylist),
    #                             t=t, dets=[pil2M])
    #
    #   (Just a tidier option to try later — your loop below still works as-is, except the
    #    'det_exposure_time' line marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note
    #   on it).
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    dets = [pil2M]
    for px in xlist:
        yield from bps.mv(piezo.x, px)  # move to the absolute position
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
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' map_grid_run sets it for you via t=.)
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
    # WHAT THIS DOES: takes N SAXS images, stepping piezo.y by +30 between each (a y-scan),
    #   building the file name from the live positions and detector distance.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' map_line_run does a line scan as ONE coordinated run
    #   and records the y position (and beam readings) into the saved data and file name for
    #   you — so you don't read piezo.y.position by hand or take a separate run per step:
    #
    #     from smi_plans import map_line_run
    #     y0 = piezo.y.position
    #     yield from map_line_run(sample, piezo.y, y0, y0 + 30*(N-1), N, t=t, dets=[pil2M])
    #
    #   (Just a tidier option to try later — your loop below still works as-is, except the
    #    'det_exposure_time' line marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note
    #   on it).
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
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' map_line_run sets it for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        yield from bp.count(dets, num=1)
        # yield from   bps.mv(piezo.y, 30)  #here is something wrong, should move a relative postion, have to redo this y scan!!!! NOTE at Thursady afternoon (9/23)
        yield from bps.mvr(
            piezo.y, 30
        )  # here is something wrong, should move a relative postion, have to redo this y scan!!!! NOTE at Thursady afternoon (9/23)


def measure_pindiol_current():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the fast shutter, reads the pin-diode current once, closes the
    #   shutter, and returns that current — a quick beam-intensity check.
    #
    # 💡 NEWER, EASIER WAY: nothing here is broken. In smi_plans the pin-diode reading is
    #   recorded INTO the data automatically during a scan (you can put it in the file name
    #   as e.g. "{pin_diode_current2_mean_value}"), so you rarely need to read it by hand
    #   like this. (Heads up: this function is defined twice in this file — the later copy is
    #   identical.)
    # === end smi_plans note ================================================
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr


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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — for every sample, and every y-offset, and every exposure
    #   time, it runs a single SAXS measurement (via the measure_saxs helper).
    #
    # 💡 NEWER, EASIER WAY: with smi_plans you describe the samples once as a SampleList and
    #   run them as one coordinated transmission/SAXS measurement (e.g. transmission_bar),
    #   recording which sample/offset each frame belongs to instead of starting a fresh
    #   RE(...) run each time. (Just a tidier option to try later — this run-book still works.)
    # === end smi_plans note ================================================
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — for the first 8 samples, and every y-offset, and every
    #   exposure time, it runs a single WAXS measurement (via the measure_waxs helper).
    #
    # 💡 NEWER, EASIER WAY: like measure_series_saxs, smi_plans can run the whole sample bar
    #   as one coordinated measurement and record which sample/offset/arc each frame is,
    #   instead of one RE(...) run per point. (Just a tidier option to try later — this
    #   run-book still works as-is.)
    # === end smi_plans note ================================================
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
    # WHAT THIS DOES: steps the WAXS detector arc through several angles and takes an image
    #   at each (optionally adding the SAXS detector at the widest angle), building the file
    #   name from the live x/y/z positions and the arc angle.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that sweeps
    #   the arc as a proper scan axis and records the positions + arc angle + beam readings
    #   into the saved data and file name for you (so you don't read piezo.x/y/z.position by
    #   hand). Roughly:
    #
    #     from smi_plans import acquire, motor_axis, saxs_waxs_dets
    #     yield from acquire(RE.md["sample"], saxs_waxs_dets(),
    #                        [motor_axis("waxs", waxs.arc, [0.0, 6.5, 13.0])])
    #
    #   (Just a tidier option to try later — your loop below still works as-is, except the
    #    ⚠️ lines, which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the 'det_exposure_time(...)' lines are now "plans"
    #   (plain calls do nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (The
    #   'rayonix' / 'pil300KW' text in the comment further down is just a comment, so it's
    #   harmless — but don't bring rayonix back: it was removed with no replacement.)
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
                    pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera; check calibration).
                ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
            else:
                dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera; check calibration).

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        # yield from bp.scan(dets, waxs, *waxs_arc)
        yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single quick WAXS snapshot (a test image). This is the SECOND
    #   snap_waxs in the file, so this is the one that actually runs (it correctly uses the
    #   current WAXS detector 'pil900KW').
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-shot acquire that records the beam readings
    #   into the saved data for you, e.g.  yield from acquire("test", [pil900KW], []).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(t)' is now a "plan" (plain call does
    #   nothing) — see the ⚠️ note below. (The detector here, 'pil900KW', is fine.)
    # === end smi_plans note ================================================
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' technique runs set it for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single quick SAXS snapshot (a test image). This is the SECOND
    #   snap_saxs in the file, so this is the one that actually runs.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-shot acquire that records the beam readings
    #   into the saved data for you, e.g.  yield from acquire("test", [pil2M], []).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(t)' is now a "plan" (plain call does
    #   nothing) — see the ⚠️ note below.
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' technique runs set it for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_pindiol_current():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the fast shutter, reads the pin-diode current once, closes it,
    #   and returns that current. This is the SECOND (identical) copy in the file.
    #
    # 💡 NEWER, EASIER WAY: nothing here is broken. In smi_plans the pin-diode reading is
    #   recorded INTO the data automatically during a scan (put it in the file name as e.g.
    #   "{pin_diode_current2_mean_value}"), so you rarely read it by hand like this.
    # === end smi_plans note ================================================
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr

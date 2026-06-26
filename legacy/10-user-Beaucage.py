# Align GiSAXS sample
import numpy as np

# ============================ SMI GI Alignment ===============================#R
alignbspos = 11
measurebspos = 1.15
GV7 = TwoButtonShutter("XF:12IDC-VA:2{Det:1M-GV:7}", name="GV7")


def alignmentmodeBoc():
    """Move gate valves, attenutators, and beamtop into GI alignment mode"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into grazing-incidence "alignment mode" — parks the
    #   WAXS arc, opens the SAXS gate valve, sets attenuators/foils, and slides the SAXS
    #   beamstop rod out so you can see the direct beam while aligning.
    # 💡 In 'smi_plans' this beamstop/attenuator setup is handled for you by the align step
    #   (align_sample) before a measurement, so you don't usually call it by hand. (Just
    #   context — nothing here is wrong except the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the SAXS beamstop rod 'pil2M_bs_rod' was renamed
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (GV7 / att2_* are fine.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 10)  # move the waxs detector out of the way
    yield from bps.mv(GV7.open_cmd, 1)  # open the SAXS gate valve
    yield from bps.mv(att2_6, "Retract")  # make sure that atten2_6 is out
    # yield from bps.mv(att2_8,"Insert")  # (for 7.5keV) make sure that atten2_8 is out
    yield from SMIBeam().insertFoils(1)  # (for >11keV in vac) 1 = insert
    yield from bps.sleep(1)

    # if bragg.position<8:
    #     yield from bps.mv(att1_5,"Insert")
    #     yield from bps.sleep(1)
    #     yield from bps.mv(att1_7,"Insert")
    #     # yield from SMIBeam().insertFoils(1)   # (for >11keV in vac) 1 = insert
    #     yield from bps.sleep(1)
    # elif bragg.position>8 and bragg.position<9:
    # #for 13.5 keV
    #     yield from bps.mv(att1_12,"Insert")
    #     yield from bps.sleep(1)
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # move beamstop out of the way  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")  # don't overwrite user data
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def measurementmodeBoc():
    """Move gate valves, attenutators, and beamtop into GI measurement mode"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the counterpart to alignmentmodeBoc — puts the beamline back into
    #   "measure mode" (retracts foils, slides the beamstop rod to its measuring spot, closes
    #   the SAXS gate valve) ready to collect data.
    # 💡 In 'smi_plans' the align step restores the beamstop/attenuators for you after aligning,
    #   so this is normally automatic. (Nothing here is wrong except the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the SAXS beamstop rod 'pil2M_bs_rod' was renamed — see the
    #   ⚠️ note below. (GV7 is fine.)
    # === end smi_plans note ================================================
    # yield from bps.mv(att2_8,"Retract") # (for 7.5keV)
    yield from SMIBeam().insertFoils(0)  # (for >11keV)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    # uncomment to close SAXS gate valve during measurements
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(1)


def align_gisaxs_height_Boc(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a height-alignment scan — sweeps sample y, finds the peak/edge, moves y
    #   there. One building block of the alignment routines below.
    # 💡 In 'smi_plans' alignment is done once up front by align_sample, with the result saved
    #   with the data — you don't usually call the height/theta scans by hand. (Nothing broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Boc(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a theta (incident-angle) alignment scan — sweeps piezo.th, finds the
    #   peak, moves there. The other building block of the alignment routines below.
    # 💡 In 'smi_plans' this is handled by align_sample as part of one up-front alignment, with
    #   the result recorded into the data. (Nothing broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def alignBoc(align_height=5000):
    """Do GI alignment"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to alignment
    #   mode, then repeatedly refines sample height and incident angle (coarse then fine,
    #   including a reflectivity step), and switches back to measure mode at the end.
    # 💡 NEWER, EASIER WAY: 'smi_plans' bundles this whole align-the-sample dance into one call,
    #   align_sample, and saves the alignment result with your data. The GIWAXS techniques can
    #   call it per sample via align=, so you usually don't run a hand-written alignment:
    #     from smi_plans import align_sample
    #     yield from align_sample()        # aligns and records the result
    #   (Just a tidier option — this still works as-is except the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below). (internal: Tier 3.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeBoc()
    yield from bps.mv(piezo.y, align_height)
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 883)
    yield from align_gisaxs_height_Boc(600, 16, der=True)
    yield from align_gisaxs_th_Boc(1, 11)
    yield from align_gisaxs_height_Boc(300, 11, der=True)
    yield from align_gisaxs_th_Boc(0.5, 11)
    yield from bps.mv(piezo.th, ps.peak + 0.2)
    yield from bps.mv(
        pil2M.roi1.min_xyz.min_y, 883 - 336
    )  # 336 offset = 0.4*3.14/180*8287/0.172
    yield from align_gisaxs_th_Boc(0.3, 31)
    yield from align_gisaxs_height_Boc(200, 21)
    yield from align_gisaxs_th_Boc(0.1, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeBoc()


def alignBocBulk(align_height=5000):
    """Do GI alignment, but skip reflectivity step"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shorter grazing-incidence alignment (height + theta only, no
    #   reflectivity step) for bulk samples.
    # 💡 NEWER, EASIER WAY: same as alignBoc — 'smi_plans' align_sample does the up-front
    #   alignment and saves it with the data. (Just a tidier option — works as-is except ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below). (internal: Tier 3.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeBoc()
    yield from bps.mv(piezo.y, align_height)
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 883)
    yield from align_gisaxs_height_Boc(600, 16, der=True)
    yield from align_gisaxs_th_Boc(1, 11)
    yield from align_gisaxs_height_Boc(300, 11, der=True)
    yield from align_gisaxs_th_Boc(0.5, 11)
    yield from bps.mv(piezo.th, ps.peak)
    yield from measurementmodeBoc()


# ============================ Custom Run Routines ===============================#


def run_giwaxsBocBoth():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — at each of several energies (two absorption edges), runs the
    #   GIWAXS bar scan run_giwaxsBoc, tagging the file name with the energy.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you'd combine the energy sweep with the GIWAXS bar
    #   in one call (giwaxs_bar with an energy_axis, or the giwaxs+energy combined recipe);
    #   energy_axis handles the energy move + beam feedback and records the energy into each
    #   image. (Nothing broken here — it just orchestrates run_giwaxsBoc; see that function's
    #   ⚠️ notes.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    thresh_map = {}
    thresh_map[13400] = 10
    thresh_map[13473] = 10
    thresh_map[13550] = 10
    thresh_map[15125] = 11
    thresh_map[15199] = 11
    thresh_map[15275] = 11

    for e in [13400, 13473, 13550, 15125, 15199, 15275]:
        yield from bps.mv(energy, e)
        yield from run_giwaxsBoc(t=1.0, tag=f"{e:5d}keV_air")
        # yield from run_giwaxsBocBulk(t=0.5,tag=f'{e:5d}keV_air')


def run_giwaxsBoc(t=0.5, th_step=0.001, x_list_offset=0, tag=""):
    """GIWAXS Run Routine

    Runs a scan along a sample bar allowing for custom waxs_arc and theta_scan
    definitions. Also allows for 'walking' on the sample during measurement to
    avoid beam damage.

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks the sample bar; at each sample it aligns, then for each incident
    #   angle sweeps the WAXS arc, "walking" along x between angles to avoid beam damage.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' giwaxs_bar walks the bar (aligning each sample if you
    #   pass align=align_sample), sweeps incident angle and WAXS arc, and records the angle / x
    #   / WAXS-position / beam into each image and file name (so you can drop the hand-built
    #   "{sample}_{th}deg" name). The "walk x to avoid beam damage" can be a per-point x-offset:
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, motor_axis, align_sample
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     yield from giwaxs_bar(bar, t=t, dets=[pil2M, pil900KW], align=align_sample,
    #                           incident_angles=[0.08, 0.20], arc=motor_axis("waxs", waxs, np.arange(2.83, 22.83, 4)))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 2.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    name = "PB"

    # define x-positions on sample bar
    # x_list = [,,,,,,,,,]

    # define names of samples on sample bar
    # sample_list = ['TP14n','TP27n','TM9n','TM15n','TM18n','TM22n','TM39n','TM39r','TM15r','TP27r']

    # x_list = x_list[::-1]
    # sample_list = sample_list[::-1]

    # shift xlist
    x_list = [x + x_list_offset for x in x_list]

    # sanity check
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # Set up theta and waxs scans
    ## for Nils/Lee VAOI studies
    # th_array = np.arange(0.08,0.280,th_step)
    # waxs_arc = [2.83, 20.83, 4]
    # ## for non VAOI studies
    th_array = np.array([-0.12, 0])
    waxs_arc = [2.83, 22.83, 4]

    # sanity check
    waxs_step = (waxs_arc[1] - waxs_arc[0]) / (waxs_arc[2] - 1)
    assert (
        waxs_step <= 6.00001
    ), f"waxs arc step<6 for proper stitching: waxs_step = {waxs_step}"

    # need to walk around sample to avoid beam_damage
    glob_xoff = 2000
    glob_walk_length = 2000  # microns
    glob_xstep = int(glob_walk_length / th_array.shape[0])

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)  # move to next sample
        yield from bps.mv(piezo.th, 0.05)  # set stage angle to ~0
        yield from alignBoc(6000)  # run alignment routine
        plt.close("all")  # close alignment plots (memory issues)

        th_start = piezo.th.position
        det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' giwaxs_bar sets it for you via t=.)
        for j, th in enumerate(th_start + th_array):  # loop over incident angles
            # uncomment to walk around sample to avoid beam_damage
            yield from bps.mv(piezo.x, (x - glob_xoff + j * glob_xstep))

            # convert angles to "real" angles
            real_th = 0.2 + th_array[j]  # 0.2 = alignment angle for Si
            yield from bps.mv(piezo.th, th)

            sample_name = sample + "_{th:5.4f}deg".format(th=real_th)
            if tag:
                sample_name += "_" + tag
            sample_id(user_name="PB", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.scan(dets, waxs, *waxs_arc)

            # uncomment below for manual snake mode.
            # waxs_arc[1],waxs_arc[0] = waxs_arc[0],waxs_arc[1]

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def run_giwaxsBocBulk(t=1, tag=""):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS bar scan for bulk samples — walks the bar, aligns each (skipping
    #   the reflectivity step), and at each incident angle takes an image (with snake-mode WAXS).
    #
    # 💡 NEWER, EASIER WAY: same 'smi_plans' giwaxs_bar pattern as run_giwaxsBoc (with
    #   align=align_sample); it records angle/position/beam into each image and file name.
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 2.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the detector list uses 'pil300KW' (retired WAXS) and
    #   'rayonix' (the MAXS detector, removed with no replacement) — see the ⚠️ note below;
    #   (2) the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (⚠️ notes below).
    # === end smi_plans note ================================================
    name = "PB"
    # x_list = [] # GI bar 1 - Lee samples
    # x_list = [50000,38000,30000,23500,11500,2500,-5500,-12500,-19500,-26500,-33500] # GI bar 2 - Peter membrane dry samples
    # x_list = [11500,2500] # GI bar 2 - Peter membrane dry samples
    # x_list = [] # GI bar 3 - Lee low priority and Nils samples
    x_list = [38000, 30000, 23500, 11500, 2500]  # GI bar 2 - Peter membrane dry samples

    # sample_list = ['BTBT_noAu','BTBT_noPFBT','BTBT_PFBT','BTBT_Au','BTBT_NoOx','BTBT_Ox','DIF_noAu','DIF_Au','DIF_noPFBT','DIF_PFBT'] # GI bar 1 - Lee samples
    # sample_list = ['mLbL_dry_7500','Dow6bulk_dry_7500','Dow7bulk_dry_7500',
    #               'Dow8bulk_dry_7500','Dow10bulk_dry_7500','SWC4bulk_dry_7500','SWC4iTS_dry_7500',
    #               'Dow6iTS_dry_7500','Dow7iTS_dry_7500','Dow8iTS_dry_7500', 'Dow10iTS_dry_7500'] # GI bar 2 - Peter membrane dry samples
    # sample_list = ['Dow10bulk_dry_7500','SWC4bulk_dry_7500'] # GI bar 2 - Peter membrane dry samples
    sample_list = [
        "Dow6bulk_dry_7500",
        "Dow7bulk_dry_7500",
        "Dow8bulk_dry_7500",
        "Dow10bulk_dry_7500",
        "SWC4bulk_dry_7500",
    ]  # GI bar 2 - Peter membrane dry samples

    # th_list = np.arange(0.08,0.280,0.0005) # for Nils/Lee VAOI studies
    th_array = np.array([0.0, 0.15])
    waxs_arc = [2.83, 2.83, 1]

    # sanity check
    # waxs_step = (waxs_arc[1] - waxs_arc[0])/waxs_arc[2]
    # assert waxs_step<=6.00001,f'waxs arc step<6 for proper stitching: waxs_step = {waxs_step}'

    # need to walk around sample to avoid beam_damage
    glob_xoff = 1000
    glob_xstep = 200

    dets = [pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): both were removed (this line would error). 'pil300KW' (WAXS) is now 'pil900KW' — use that instead (different camera, so check beam-center/calibration). 'rayonix' (the MAXS detector) was removed from the beamline with no current replacement — drop it from the list or ask beamline staff.
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.th, 0.05)
        yield from alignBocBulk()
        plt.close("all")
        # yield from bps.mv(att2_6,"Insert") # add in attenutator to avoid saturation

        th_start = piezo.th.position
        det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' giwaxs_bar sets it for you via t=.)
        for j, th in enumerate(th_start + th_array):
            # uncomment to walk around sample to avoid beam_damage
            # yield from bps.mv(piezo.x, (x-glob_xoff+j*glob_xstep))

            # convert angles??
            real_th = 0.2 + th_array[j]  # from critical angle / alignment angle for Si
            yield from bps.mv(piezo.th, th)

            sample_name = sample + "_{th}deg".format(th=real_th)
            if tag:
                sample_name += "_" + tag
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.scan(dets, waxs, *waxs_arc)

            # uncomment below for manual snake mode.
            waxs_arc[1], waxs_arc[0] = waxs_arc[0], waxs_arc[1]

        # yield from bps.mv(att2_6,"Retract")
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def nexafs_scan(det, energies, incident_angle, ctime):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS energy scan at a fixed incident angle — moves theta, then sweeps
    #   the X-ray energy across an edge taking a WAXS image at each step.
    # 💡 NEWER, EASIER WAY: this is exactly 'smi_plans' nexafs_run / energy_axis; it handles the
    #   energy move + beam feedback and records the energy into each image and file name:
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run(sample, energies, t=ctime, dets=[pil900KW], geometry="reflection")
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #   (Heads-up: this function uses 'sample' in the file name but doesn't define it — looks
    #    like a pre-existing bug; smi_plans templates the name from recorded fields instead.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below).
    # === end smi_plans note ================================================
    sample_name = "{sample}_{th:5.4f}deg_{e:5d}eV_DB".format(
        sample=sample, th=incident_angle, e=int(energies[0])
    )

    # move to theta 0 + value
    yield from bps.mvr(piezo.th, incident_angle)

    # Scan the energies
    det_exposure_time(ctime, ctime)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(ctime, ctime)  — or at the prompt:  RE(det_exposure_time(ctime, ctime)). (smi_plans' nexafs_run sets it for you via t=.)
    yield from bp.scan(
        [pil300KW, pil300kwroi2], energy, energies[0], energies[-1], len(energies)  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). (Its ROI signal 'pil300kwroi2' depends on the same retired detector, so update it too.)
    )


def giwaxsTempSingleWaxsSeries(
    x_list, y_list, th_list, sample_list, waxs_arc, num, t=1, user="BP"
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at each WAXS-arc position, walks the (pre-aligned) bar and takes one
    #   GIWAXS image per sample, baking the Linkam temperature into the file name. Used by the
    #   heating loop below for in-situ temperature kinetics.
    # 💡 NEWER, EASIER WAY: 'smi_plans' giwaxs_bar walks the bar and records the angle / WAXS-
    #   position / temperature / beam into each image and file name; for the in-situ heating it
    #   pairs with a temperature run (isothermal_kinetics_run / temperature_ramp_run). (Just a
    #   tidier option — works as-is EXCEPT the ⚠️ lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (ls/Linkam is fine.)
    # === end smi_plans note ================================================
    print(num)
    for waxspos in waxs_arc:
        for x, y, th, sample in zip(
            x_list, y_list, th_list, sample_list
        ):  # loop over samples on bar
            yield from bps.mv(piezo.x, x)  # move to next sample
            yield from bps.mv(piezo.y, y)  # move to next sample
            yield from bps.mv(piezo.th, th)  # move to next sample
            print(x)
            th_meas = 0.10 + piezo.th.position
            th_real = 0.10

            yield from bps.mv(piezo.th, th_meas)
            yield from bps.mv(
                waxs, waxspos
            )  # move the waxs dectector to the measurement position
            waxs_arc = [waxspos]
            temp = ls.ch1_read.value
            dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
            sample_name = (
                "{sample}_inc{th:5.4f}deg_waxs{waxspos:5.4f}_{temp:5.4f}C_{num}".format(
                    sample=sample, th=th_real, waxspos=waxspos, temp=temp, num=num
                )
            )
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            # yield from bp.scan(dets, waxs, *waxs_arc)# should just be a single point "scan"
            yield from bp.count(dets)


def heatingLoop():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time/heating series — aligns two samples, then repeatedly
    #   walks them in x (forward and back) taking GIWAXS, re-aligning every so often, for a
    #   long count (effectively an open-ended kinetics run you stop with Ctrl-C).
    # 💡 NEWER, EASIER WAY: "keep measuring on a cadence while heating" is the 'smi_plans'
    #   kinetics family (isothermal_kinetics_run / time_series_run), which timestamps each frame
    #   and records temperature into the data. The periodic re-align is align_sample on a
    #   schedule. (Nothing here errors except note the two ⚠️/heads-up below.)
    # 💡 HEADS-UP (not broken now, but fragile): this uses 'counter % quickalignevery is 0',
    #   and 'is' for number comparison is unreliable in Python — '==' is what you want. The
    #   actual data is taken via giwaxsTempSingleWaxsSeries (see its ⚠️ pil300KW note).
    #   (internal: Tier 0/1.)
    # === end smi_plans note ================================================
    # Load 1 xpos = [-11000,2000] #2493 is from -2000 to -11000, 2523 is from 2000 to 11000
    xpos = [-12000, 1000]  # 2493 is from -2500 to -12000, 2523 is from 2000 to 11000
    names = ["DPP_2493", "DPP_2523"]

    xstep = 200
    quickalignevery = 15  # do a quickalign every n exposures
    sleepbetweenexps = 10
    nscans = 2000  # Arbitrary high number; I don't know how the runengine would handle an infinite loop but effectively this.  End the run with ctrl-c + RE.stop()

    ypos = [7100, 7100]
    thpos = [0.06, 0.06]

    for i, x in enumerate(xpos):
        yield from bps.mv(piezo.x, x + 4500)
        yield from alignement_gisaxs(0.08)
        ypos[i] = piezo.y.position
        thpos[i] = piezo.th.position

    # continually measure, every 30 minutes re-align and shift 200 um in x
    counter = 0

    print("Alignment Done:")
    print(str(names))
    print(str(xpos))
    print(str(ypos))
    print(str(thpos))

    xmodfwd = np.arange(0, 9001, xstep)
    xmodbck = np.arange(9001, 0, xstep)

    xmod = np.concatenate((xmodfwd, xmodbck))

    while counter < nscans:
        for xmv in xmod:
            lclxpos = xpos + xmv
            yield from giwaxsTempSingleWaxsSeries(
                lclxpos, ypos, thpos, names, [2.93, 8.93], counter, t=3, user="BP2-1"
            )
            sleep(sleepbetweenexps)
            counter += 1
            yield from giwaxsTempSingleWaxsSeries(
                lclxpos, ypos, thpos, names, [8.93, 2.93], counter, t=3, user="BP2-1"
            )
            sleep(sleepbetweenexps)
            counter += 1
            if counter % quickalignevery is 0 or counter % quickalignevery is 1:
                for i, x in enumerate(xpos):
                    yield from bps.mv(waxs, 8.93)
                    yield from bps.mv(piezo.x, x + 4500)
                    yield from alignement_gisaxs(0.08)
                    ypos[i] = piezo.y.position
                    thpos[i] = piezo.th.position


def afterlunchrun():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines sample lists + energies and hands them to the
    #   resonant GIWAXS energy run (run_giwaxsEnergyBoc). 💡 Just orchestration; the migration
    #   lives in run_giwaxsEnergyBoc (giwaxs_bar + energy_axis). Nothing broken here itself.
    # === end smi_plans note ================================================
    #  xl1 = [-50000,-37500,-25000,-8000,2000,14000,24000]
    #  sl1 = ['TP14n','TP27n','TM9n','TM15n','TM18n','TM22n','TM39n']
    #  ea1 = [13480]
    xl2 = [36500]
    sl2 = ["TM39r"]
    ea2 = [15195, 15200, 15205, 15195]
    xl3 = [41000, 47000]
    sl3 = ["TM15r", "TP27r"]
    ea3 = [15195, 15200, 15205, 15195]
    yield from run_giwaxsEnergyBoc(xl2, sl2, ea2, t=2)
    yield from run_giwaxsEnergyBoc(xl3, sl3, ea3, t=2)


def GIbar2res():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines sample lists + edge energies and runs the resonant
    #   GIWAXS energy scan (run_giwaxsEnergyBoc). 💡 Just orchestration; see that function's note
    #   (giwaxs_bar + energy_axis). Nothing broken here itself.
    # === end smi_plans note ================================================
    # Samples for which energy scans are needed
    xl1 = [-48000, -39000, -29000, -19000]
    sl1 = ["TP14r", "TM9r", "TM18r", "TM22r"]
    # Samples for single energy shot
    xl2 = [-9000, 1000, 9000, 20000, 26000, 38000, 46500]
    sl2 = ["TM9b", "TP27b", "TM39b", "TP14b", "SVPS-10PEO", "SVPS-10P2VP", "SVPS"]
    ea_waxs_Rb = [15195, 15200, 15205, 15195]
    ea_waxs_Br = [13480, 13485, 13490, 13495, 13480]
    # yield from run_giwaxsEnergyBoc(xl1,sl1,ea_waxs_Br,t=2)
    yield from run_giwaxsEnergyBoc(xl1, sl1, ea_waxs_Rb, t=2)


def GIbar2nonres():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines sample lists + incident-angle/WAXS arcs and runs the
    #   GISAXS angle scan (run_gisaxsAngleBoc). 💡 Just orchestration; see that function's note
    #   (giwaxs_bar + incidence_axis). Nothing broken here itself.
    # === end smi_plans note ================================================
    # WAXS and SAXS
    xl1 = [-9000, 1000, 9000, 20000]
    sl1 = ["TM9b", "TP27b", "TM39b", "TP14b"]
    # SAXS only
    xl2 = [26000, 38000, 46500]
    sl2 = ["SVPS-10PEO", "SVPS-10P2VP", "SVPS"]

    xl2 = [38000, 46500]
    sl2 = ["SVPS-10P2VP", "SVPS"]

    waxs_arc_nowaxs = [8.9, 8.9, 1]
    waxs_arc_forwaxs = [2.9, 20.9, 4]

    angle_arc_GISAXS = np.linspace(0.08, 0.25, 18)
    angle_arc_GIWAXS = np.linspace(0.1, 0.2, 2)
    # yield from run_gisaxsAngleBoc(xl1,sl1,angle_arc_GIWAXS,waxs_arc_forwaxs)
    yield from run_gisaxsAngleBoc(xl2, sl2, angle_arc_GISAXS, waxs_arc_nowaxs, t=2)


def earlyeveningtransmissionrun():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines transmission sample lists + NEXAFS/WAXS energies and
    #   runs the SAXS+WAXS energy scan (run_saxswaxsEnergyBoc). 💡 Just orchestration; see that
    #   function's note (transmission_run + nexafs_run/energy_axis). Nothing broken here itself.
    # === end smi_plans note ================================================
    ea_nexafs_Br = np.linspace(13450, 13500, 51)
    ea_nexafs_Rb = np.linspace(15150, 15250, 51)
    ea_waxs_Rb = [15195, 15200, 15205, 15195]
    ea_waxs_Br = [13480, 13485, 13490, 13480]
    # Samples for static runs
    xl1 = [43500, 37000, 30500, 23500, 15500, 8500, 2500]
    sl1 = [
        "Dow6bulk",
        "Dow7bulk",
        "Dow8bulk",
        "Dow10bulk",
        "SWC4bulk",
        "Dow6BAbulk",
        "SWC4BAbulk",
    ]
    ea1 = [13480]

    # Sampls for energy scans
    xl2 = [-4500, -11000, -17000, -22000, -26500]
    sl2 = [
        "Dow6bulkRbBr100",
        "Dow7bulkRbBr100",
        "Dow8bulkRbBr100",
        "Dow10bulkRbBr100",
        "SWC4bulkRbBr100",
    ]

    yield from run_saxswaxsEnergyBoc(xl1, sl1, ea1, ea1, t=0.3)
    yield from run_saxswaxsEnergyBoc(xl2, sl2, ea_waxs_Br, ea_nexafs_Br, t=0.3)
    yield from run_saxswaxsEnergyBoc(xl2, sl2, ea_waxs_Rb, ea_nexafs_Rb, t=0.3)


def tuesdaymorningtransmissionrun():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines transmission samples + energies and runs the SAXS+
    #   WAXS energy scan (run_saxswaxsEnergyBoc). 💡 Just orchestration; see that function's
    #   note. Nothing broken here itself.
    # === end smi_plans note ================================================
    ea_nexafs_Br = np.linspace(13450, 13500, 51)
    ea_nexafs_Rb = np.linspace(15150, 15250, 51)
    ea_waxs_Rb = [15195, 15200, 15205, 15195]
    ea_waxs_Br = [13480, 13485, 13490, 13495, 13480]
    # Samples for static runs
    xl = [30000.2, 24500.2, 19000.2, 9250.2, -1000.2, -6000.2, -11500.2, -17500.2]
    sl = [
        "Dow6bulkRbBr50",
        "Dow7bulkRbBr50",
        "Dow10bulkRbBr50",
        "SWC4bulkRbBr50",
        "Dow6bulkRbBr500",
        "Dow7bulkRbBr500",
        "Dow10bulkRbBr500",
        "SWC4bulkRbBr500",
    ]

    # yield from run_saxswaxsEnergyBoc([4000],['TapeBlank2'],[13480],[13480],t=1)
    # yield from run_saxswaxsEnergyBoc(xl,sl,ea_waxs_Br,ea_nexafs_Br,t=0.3)
    yield from run_saxswaxsEnergyBoc(xl, sl, ea_waxs_Rb, ea_nexafs_Rb, t=0.3)


def tuesdaylunchtransmission():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines sample lists + x/y map ranges and runs the SAXS map
    #   (run_saxsmapBoc). 💡 Just orchestration; see that function's note (map_grid_run).
    #   Nothing broken here itself.
    # === end smi_plans note ================================================
    name1 = [
        "AS1-034",
        "AS1-038A",
        "AS1-038B",
        "AS1-038C",
        "AS1-038D",
        "AS1-038E",
        "AS1-036A",
        "AS1-036B",
        "AS1-036C",
        "AS1-036D",
        "AS1-036E",
    ]
    pos1 = [
        -44000,
        -35000,
        -27000,
        -19000,
        -10000,
        -2000,
        8000,
        16500,
        25000,
        33000,
        41500,
    ]  # centers

    name2 = [
        "PT5E-010A",
        "PT5E-010B",
        "PT5E-010C",
        "AS1-040A",
        "AS1-040B",
        "AS1-040C",
        "AS1-040D",
        "AS1-040E",
    ]
    pos2 = [-35000, -27000, -19000, -10000, -2000, 8000, 16500, 25000]

    x_range = [-500, 500, 4]
    y_range = [-250, 225, 4]

    # yield from run_saxsmapBoc(pos1,name1,x_range=x_range,y_range=y_range,t=1,y_cen=-4500)
    yield from run_saxsmapBoc(
        pos2, name2, x_range=x_range, y_range=y_range, t=1, y_cen=10250
    )


def run_giwaxsEnergyBoc(x_list, sample_list, energy_arc_waxs, t=5, tag=""):
    """GIWAXS Run Routine"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant GIWAXS bar run — for each sample it aligns, then for each
    #   energy near an absorption edge sweeps the WAXS arc, taking images, pausing the beam-
    #   feedback "suspender" around each energy move.
    #
    # 💡 NEWER, EASIER WAY: sweeping energy while collecting GIWAXS is the 'smi_plans' GIWAXS +
    #   energy combination. energy_axis steps the energy AND manages the beam feedback (pauses
    #   it in one bps.mv -- the device manages gap/feedback/harmonic) — so you can drop the manual
    #   remove_suspender/install_suspender + sleep scaffolding. align_sample aligns each sample
    #   and saves it; the energy/angle are recorded into each image and file name:
    #     from smi_plans import giwaxs_bar, SampleList, energy_axis, motor_axis, align_sample
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     yield from giwaxs_bar(bar, t=t, dets=[pil2M, pil900KW], align=align_sample,
    #                           axes=[energy_axis(energy_arc_waxs), motor_axis("waxs", waxs, [2.9, 20.9, 4])])
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 lines are
    #    scaffolding you can delete once you migrate.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    # x_list = [-50000,-37500,-25000,-8000,2000,14000,24000,36000,41000,47000]

    # define names of samples on sample bar
    # sample_list = ['TP14n','TP27n','TM9n','TM15n','TM18n','TM22n','TM39n','TM39r','TM15r','TP27r']

    ct_nexafs = 0.2
    # x_list = x_list[::-1]
    # sample_list = sample_list[::-1]

    # shift xlist
    # x_list = [x+x_list_offset for x in x_list]

    # sanity check
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # Set up theta and waxs scans
    ## for Nils/Lee VAOI studies
    # th_array = np.arange(0.08,0.280,th_step)
    # waxs_arc = [2.83, 20.83, 4]
    # ## for non VAOI studies

    th_array = np.array([0.08, 0.14])
    waxs_arc = [2.9, 20.9, 4]
    # energy_arc_waxs = [13480,13485,13490,13480]

    energy_arc_nexafs_Br = np.linspace(13450, 13500, 51)
    energy_arc_nexafs_Rb = np.linspace(15150, 15250, 51)

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)  # move to next sample

        yield from remove_suspender(susp_xbpm2_sum)
        yield from bps.mv(energy, energy_arc_waxs[0])

        yield from bps.sleep(10)  # 💡 smi_plans: you can drop this settle wait and the manual remove_suspender/install_suspender around it — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
        yield from install_suspender(susp_xbpm2_sum)

        yield from alignement_gisaxs(0.1)  # run alignment routine

        th_meas = np.array([0.10 + piezo.th.position])
        th_real = [0.10]

        # yield from bps.mv(waxs,2.9) #move the waxs dectector to the measurement position
        # det_exposure_time(ct_nexafs, ct_nexafs)
        # yield from nexafs_scan([pil2M], energy_arc_nexafs_Rb, 0.10, ct_nexafs)

        # yield from remove_suspender( susp_xbpm2_sum)
        # yield from bps.mv(energy, 15200)
        # yield from bps.sleep(10)
        # yield from install_suspender( susp_xbpm2_sum)
        #
        # yield from nexafs_scan([pil2M], energy_arc_nexafs_Rb, 0.10, ct_nexafs)

        yield from bps.mv(
            waxs, 2.9
        )  # move the waxs dectector to the measurement position

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
        for i, th in enumerate(th_meas):  # loop over incident angles
            # convert angles to "real" angles
            yield from bps.mv(piezo.th, th)

            for k, e in enumerate(energy_arc_waxs):
                sample_name = "{sample}_{th:5.4f}deg_{e:5d}eV_{num}".format(
                    sample=sample, th=th_real[i], e=e, num=k
                )
                sample_id(user_name="PB", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from remove_suspender(susp_xbpm2_sum)
                yield from bps.mv(energy, e)
                yield from bps.sleep(10)  # 💡 smi_plans: you can drop this settle wait and the manual suspender management — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from install_suspender(susp_xbpm2_sum)

                # yield from bp.scan(dets, energy, e, e, 1)
                yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def run_gisaxsAngleBoc(x_list, sample_list, angle_arc, waxs_arc, t=5, tag=""):
    """GIWAXS Run Routine"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS angle scan over a bar — for each sample it aligns, then sweeps a
    #   set of incident angles at a fixed WAXS-arc position, taking an image at each.
    # 💡 NEWER, EASIER WAY: sweeping incident angle over a bar is 'smi_plans' giwaxs_bar with an
    #   incidence_axis; align_sample aligns each sample and the angle/position are recorded into
    #   each image and file name:
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, motor_axis, align_sample
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     yield from giwaxs_bar(bar, t=t, dets=[pil2M, pil900KW], align=align_sample,
    #                           incident_angles=list(angle_arc), arc=motor_axis("waxs", waxs, [2.9]))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    # x_list = [-50000,-37500,-25000,-8000,2000,14000,24000,36000,41000,47000]

    # define names of samples on sample bar
    # sample_list = ['TP14n','TP27n','TM9n','TM15n','TM18n','TM22n','TM39n','TM39r','TM15r','TP27r']

    ct_nexafs = 0.2
    # x_list = x_list[::-1]
    # sample_list = sample_list[::-1]

    # shift xlist
    # x_list = [x+x_list_offset for x in x_list]

    # sanity check
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # Set up theta and waxs scans
    ## for Nils/Lee VAOI studies
    # th_array = np.arange(0.08,0.280,th_step)
    # waxs_arc = [2.83, 20.83, 4]
    # ## for non VAOI studies

    # th_array  = np.array([0.08,0.14])
    # waxs_arc = [2.9, 20.9, 4]
    # energy_arc_waxs = [13480,13485,13490,13480]

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)  # move to next sample

        yield from alignement_gisaxs(0.1)  # run alignment routine

        th_meas = (
            angle_arc + piezo.th.position
        )  # np.array([0.10 + piezo.th.position, 0.20 + piezo.th.position])
        th_real = angle_arc

        # yield from bps.mv(waxs,2.9) #move the waxs dectector to the measurement position
        # det_exposure_time(ct_nexafs, ct_nexafs)
        # yield from nexafs_scan([pil2M], energy_arc_nexafs_Rb, 0.10, ct_nexafs)

        # yield from remove_suspender( susp_xbpm2_sum)
        # yield from bps.mv(energy, 15200)
        # yield from bps.sleep(10)
        # yield from install_suspender( susp_xbpm2_sum)
        #
        # yield from nexafs_scan([pil2M], energy_arc_nexafs_Rb, 0.10, ct_nexafs)

        yield from bps.mv(
            waxs, 2.9
        )  # move the waxs dectector to the measurement position

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
        for i, th in enumerate(th_meas):  # loop over incident angles
            # convert angles to "real" angles
            yield from bps.mv(piezo.th, th)

            sample_name = "{sample}_{th:5.4f}deg__{num}".format(
                sample=sample, th=th_real[i], num=i
            )
            sample_id(user_name="PB", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # yield from bp.scan(dets, energy, e, e, 1)
            yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def run_saxswaxsEnergyBoc(
    x_list, sample_list, energy_arc_waxs, energy_arc_nexafs, t=5, tag=""
):
    """GIWAXS Run Routine"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS+WAXS energy run on a bar — for each sample it runs a
    #   NEXAFS energy scan (via nexafs_scan), then at each WAXS energy takes an image, pausing
    #   the beam-feedback suspender around each energy move.
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' transmission + energy combination.
    #   transmission_run/transmission_bar collect the SAXS/WAXS, and energy_axis/nexafs_run step
    #   the energy AND manage the beam feedback (so you can drop the manual suspender + sleep
    #   scaffolding), recording the energy into each image and file name:
    #     from smi_plans import transmission_bar, nexafs_run, SampleList, energy_axis
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     # nexafs_run per sample for the edge scan, then transmission_bar with energy_axis for the WAXS energies
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 lines are
    #    scaffolding you can delete.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (Also see nexafs_scan's ⚠️ notes.)
    # === end smi_plans note ================================================
    # x_list = [-50000,-37500,-25000,-8000,2000,14000,24000,36000,41000,47000]

    # define names of samples on sample bar
    # sample_list = ['TP14n','TP27n','TM9n','TM15n','TM18n','TM22n','TM39n','TM39r','TM15r','TP27r']

    ct_nexafs = 0.2
    # x_list = x_list[::-1]
    # sample_list = sample_list[::-1]

    # shift xlist
    # x_list = [x+x_list_offset for x in x_list]

    # sanity check
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # Set up theta and waxs scans
    ## for Nils/Lee VAOI studies
    # th_array = np.arange(0.08,0.280,th_step)
    # waxs_arc = [2.83, 20.83, 4]
    # ## for non VAOI studies

    # th_array  = np.array([0.08,0.14])
    waxs_arc = [2.9, 20.9, 4]
    # energy_arc_waxs = [13480,13485,13490,13480]

    # energy_arc_nexafs_Br = np.linspace(13450, 13500, 51)
    # energy_arc_nexafs_Rb = np.linspace(15150,15250,51)

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)  # move to next sample

        yield from bps.mv(
            waxs, 2.9
        )  # move the waxs dectector to the measurement position
        det_exposure_time(ct_nexafs, ct_nexafs)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(ct_nexafs, ct_nexafs)  — or at the prompt:  RE(det_exposure_time(ct_nexafs, ct_nexafs)). (smi_plans' nexafs_run sets it for you via t=.)
        yield from remove_suspender(susp_xbpm2_sum)
        yield from bps.mv(energy, energy_arc_nexafs[0])
        yield from bps.sleep(10)  # 💡 smi_plans: you can drop this settle wait and the manual suspender management — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
        yield from install_suspender(susp_xbpm2_sum)

        yield from nexafs_scan([pil2M], energy_arc_nexafs, 0.10, ct_nexafs)

        yield from bps.mv(
            waxs, 2.9
        )  # move the waxs dectector to the measurement position

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' transmission_bar sets it for you via t=.)
        for k, e in enumerate(energy_arc_waxs):
            sample_name = "{sample}_{e:5d}eV_{num}".format(sample=sample, e=e, num=k)
            sample_id(user_name="PB", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from remove_suspender(susp_xbpm2_sum)
            yield from bps.mv(energy, e)
            yield from bps.sleep(10)  # 💡 smi_plans: you can drop this settle wait and the manual suspender management — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from install_suspender(susp_xbpm2_sum)

            # yield from bp.scan(dets, energy, e, e, 1)
            yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def mondaynightmaps():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — defines two samples + a large x/y map range and runs the SAXS
    #   map (run_saxsmapBoc). 💡 Just orchestration; see that function's note (map_grid_run).
    #   Nothing broken here itself.
    # === end smi_plans note ================================================
    samples = ["PT5E-015A", "PT5E-015B"]
    positions = [-19000, 21000]  # centers
    x_range = [-17500, 17500, 176]
    y_range = [-10000, 10000, 101]

    yield from run_saxsmapBoc(
        positions, samples, x_range=x_range, y_range=y_range, t=0.2
    )


def run_saxsmapBoc(
    x_list, samples, x_range=[-500, 500, 11], y_range=[-250, 250, 11], t=1, y_cen=0
):
    """Simple SAXS/WAXS transmission measurements

    Runs a scan along a transmission bar where, for each sample center in the
    x_list, measurements are taken in a grid defined by x_range and y_range
    about this center.

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS map — for each sample center it rasters an x/y grid
    #   and takes a SAXS image at each point (WAXS arc parked out of the way).
    # 💡 NEWER, EASIER WAY: this is exactly 'smi_plans' map_grid_run (per sample) or map_bar
    #   over the centers; it records the x/y position into each image and templates the file
    #   name from them:
    #     from smi_plans import map_grid_run, map_dets
    #     for x, sample in zip(x_list, samples):
    #         yield from bps.mv(piezo.x, x)
    #         yield from map_grid_run(sample, map_dets(use_saxs=True),
    #                                 x=tuple(x_range), y=tuple(y_range))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 2.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    name = "PT"

    # Detectors, motors:

    yield from bps.mv(waxs, 8.9)
    dets = [pil2M]  # dets = [pil2M,pil300KW]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' map_grid_run sets it for you via t=.)
    yield from bps.mv(piezo.y, y_cen)
    yield from bps.mv(piezo.th, 0)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)
        sample_id(user_name=name, sample_name=sample)
        # yield from bp.scan(dets, piezo.x, *x_range)  # 1 line scane
        yield from bp.rel_grid_scan(
            dets, piezo.x, *x_range, piezo.y, *y_range, 1
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def run_saxsBoc(x_list, samples, energies, t=1):
    """Simple SAXS/WAXS transmission measurements

    Runs a scan along a transmission bar where, for each sample center in the
    x_list, measurements are taken in a grid defined by x_range and y_range
    about this center.

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS+WAXS map — for each sample center it rasters an x/y
    #   grid and takes a SAXS+WAXS image at each point.
    # 💡 NEWER, EASIER WAY: same 'smi_plans' map_grid_run / transmission map pattern; it records
    #   the x/y position into each image and file name. (Just a tidier option — works as-is
    #   EXCEPT the ⚠️ lines.) (Tier 2.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    name = "PB"

    # Detectors, motors:
    dets = [pil2M, pil300KW]  # dets = [pil2M,pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    x_range = [-500, 500, 11]
    y_range = [-250, 250, 11]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' map_grid_run sets it for you via t=.)
    yield from bps.mv(piezo.y, 0)
    yield from bps.mv(piezo.th, 0)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)
        sample_id(user_name=name, sample_name=sample)
        # yield from bp.scan(dets, piezo.x, *x_range)  # 1 line scane
        yield from bp.rel_grid_scan(
            dets, piezo.x, *x_range, piezo.y, *y_range, 1
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def run_saxsEnergyBoc(t=1, tag=""):
    """Simple SAXS/WAXS transmission measurements

    Runs a scan along a transmission bar where, for each sample center in the
    x_list, measurements are taken in a grid defined by x_range and y_range
    about this center.

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission energy run on a capillary tray — for each sample it steps
    #   the X-ray energy across two edges and does a quick x line scan at each energy.
    # 💡 NEWER, EASIER WAY: stepping energy and measuring transmission is 'smi_plans'
    #   transmission_bar + energy_axis (or nexafs_run for the edge scan). energy_axis steps the
    #   energy and manages the beam feedback, recording it into each image and file name — so
    #   you can drop the manual energy.move + mv(energy) + sleep:
    #     from smi_plans import transmission_bar, SampleList, energy_axis
    #     bar = SampleList.from_columns(name=samples, x=x_list)
    #     yield from transmission_bar(bar, [pil900KW], t=t,
    #                                 axes=[energy_axis([13400, 13473, 13550, 15125, 15199, 15275])])
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 line is
    #    scaffolding you can delete.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    name = "PB"
    x_list = [
        -44000,
        -37500,
        -31500,
        -25000,
        -18500,
        -12000,
        -5500,
        1000,
        7000,
        13000,
        19500,
        26000,
        32500,
        39000,
        45500,
    ]  # tray 1
    # x_list  = [13000,19500,26000,32500,39000,45500] #tray 1
    samples = [
        "cap-H2Oblank",
        "SWC4sol-RbBr20mM",
        "SWC4sol-RbCl20mM",
        "SWC4sol-NaBr20mM",
        "SWC4sol-NaCl20mM",
        "SWC4sol-RbBr100mM",
        "SWC4sol-RbCl100mM",
        "SWC4sol-NaBr100mM",
        "SWC4sol-NaCl100mM",
        "SWC4-THF",
        "SWC4-H2OEXCH",
        "blank-RbBr100mM",
        "blank-RbCl100mM",
        "blank-NaBr100mM",
        "blank-NaCl100mM",
    ]
    # samples = ['SWC4-THF','SWC4-H2OEXCH','blank-RbBr100mM','blank-RbCl100mM','blank-NaBr100mM','blank-NaCl100mM']

    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    x_range = [-500, 500, 11]
    energy_arc = [13400, 13473, 13550, 15125, 15199, 15275]

    # sanity check
    assert len(x_list) == len(samples), f"Sample name/position list is borked"

    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' transmission_bar sets it for you via t=.)
    yield from bps.mv(piezo.y, 8000)  # 8000 for capillaries
    yield from bps.mv(piezo.th, 0)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)

        for k, e in enumerate(energy_arc):

            sample_name = sample + "_{e:5d}eV".format(e=e)
            if tag:
                sample_name += "_" + tag
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            energy.move(e)  # 💡 smi_plans: you can drop this double energy command + sleep — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, e)
            sleep(1)

            yield from bp.rel_scan(dets, piezo.x, *x_range)  # 1 line scan

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


ROIsizey = "XF:12IDC-ES:2{Det:1M}ROI1:SizeY"
ROIMiny = "XF:12IDC-ES:2{Det:1M}ROI1:MinY"
ROIsizex = "XF:12IDC-ES:2{Det:1M}ROI1:SizeX"
ROIMinx = "XF:12IDC-ES:2{Det:1M}ROI1:MinX"

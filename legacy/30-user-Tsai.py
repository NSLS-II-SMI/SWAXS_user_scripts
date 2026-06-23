# 2022-Oct-24, Tsai
# /nsls2/data/smi/legacy/results/data/2022_3/310000_Tsai
# /nsls2/data/smi/legacy/results/analysis/2022_3/310000_Tsai
#
# det3 ctrlX
# setthreshold energy 16100 autog 11000
# RE(shopen()); RE(mv(waxs,0))
#
# PRS -90, HP theta 0.297
# RE(alignment_gisaxs_stage) -- find the rough alignment
'''
sample_id(user_name="test", sample_name="test2")
RE(bp.rel_scan([pil900KW], stage.th, -0.2, 0.2, 11))
'''
# RE(bp.rel_scan([pil900KW], stage.th, -0.2, 0.2, 21)) -- find a good th to measure at
# RE(bp.rel_scan([pil900KW], piezo.x, -2000, 2000, 21)) -- find the range to measure scan
# RE(bp.rel_scan([pil900KW], piezo.z, -2000, 2000, 21))
# PRS 0 -- measure at a different rotational angle, PRS 45 doesn't work because stage.z somehow includes tilt 
# Align and measure one PRS at a time
# Note that beam is very small, sensitive to any stage or sample tilts
#
# Oct 25 9am, vac pipe, find beam, energy (14.4 to 16.1), small beam, align CRL, slits, waxs beamstop, AgBH. 
# Oct 25 12am, 16.1keV, 50um*2um, vac. yield from bps.mv(piezo.y, 3500);
#       Align PRS=-90 and 0 and start with waxs=0: ET 
# Oct 25 9am, waxs=20 (abort since no film signal): ET 
# Oct 25 11am, Realign PRS=-90 and restart with waxs=10: ET2
#       Oct 25 11:41 ET2_Sam5p4_scan_prs-90_waxs10.00_x1500_z-900_1s_id346958_000000_WAXS.tif
#       Oct 25 13:09 ET2_Sam5p4_scan_prs-90_waxs10.00_x-200_z-900_1s_id350214_000000_WAXS.tif
# paused after ET2_Sam5p4_scan_prs-90_waxs10.00_x430_z-900_1s_id351768_000000_WAXS.tif(th=-0.34)
# adjust theta: test_prs-90_th-0.5_x400_y3500_z-720_id351775_000000_WAXS better
# test_prs-90_th-0.64_x-200_y3500_z-720_id351780_000000_WAXS.tif better
# test_prs-90_th-0.2_x2800_y3500_z-720_id351787_000000_WAXS.tif better
# test_prs-90_th-0.32_x1500_y3500_z-720_id351796_000000_WAXS better
#
# test_prs0_th-0.7_x400_y3500_z-720_id351803_000000_WAXS.tif
# test_prs0_th-0.66_x1200_y3500_z-720_id351812_000000_WAXS.tif
# yield from bps.mv(piezo.y, 3530): ET3
# 15:50 ET3_Sam5p4_scan_prs0_waxs10.00_x-200_y3530_z610_th-0.65_1s_id351944_000000_WAXS

import numpy as np


def align_gisaxs_th_stage(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a theta-alignment step — sweeps the rotation stage theta (stage.th) over a
    #   small range, finds the peak, and moves there.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' grazing alignment is done once with align_sample, and the
    #   aligned angle is saved with the data (so you don't re-run these scans by hand). ('stage.th',
    #   'pil2M', 'bp.rel_scan' all still work.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], stage.th, -rang, rang, point)
    ps()
    yield from bps.mv(stage.th, ps.peak)


def alignment_gisaxs_stage(angle=0.15):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence (GISAXS) alignment routine on the rotation stage —
    #   switches to alignment mode, scans theta and height a few times to find the surface, sets the
    #   incidence angle, then returns to measurement mode.
    # 💡 NEWER, EASIER WAY: 'smi_plans' bundles all of this into align_sample, which you run once per
    #   sample and which SAVES the alignment result with the data automatically:
    #     from smi_plans import align_sample
    #     yield from align_sample(angle=angle)      # aligns and records the result
    #   (Then your GISAXS scans can pass align=align_sample so each sample is aligned and logged.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure unless
    #   run as a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height(700, 16, der=True)
    yield from align_gisaxs_th_stage(0.7, 11)
    yield from align_gisaxs_height(300, 11, der=True)
    yield from align_gisaxs_th_stage(0.4, 16)

    # move to theta 0 + value
    yield from bps.mv(stage.th, ps.peak + angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=0.165 / 2 + 0.515 / 2)

    # Scan theta and height
    yield from align_gisaxs_th_stage(0.2, 31)
    yield from align_gisaxs_height(200, 21)
    yield from align_gisaxs_th_stage(0.05, 21)

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    # TODO: Should we return to 0
    yield from bps.mv(stage.th, ps.cen - angle)
    yield from smi.modeMeasurement()

# 2022C3
def run_scan_ET(t=1):  

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS map at a fixed rotation angle — sets the rotation
    #   stage and theta, then rasters the sample x and z taking a WAXS image at each spot.
    #
    # 💡 NEWER, EASIER WAY: a 2D x/z raster that records the positions into the data is 'smi_plans'
    #   map_grid_run; you give it the grid and it fills the file name for you (no hand-built
    #   "_x{x}_z{z}_th{th}" string):
    #
    #     from smi_plans import map_grid_run, spatial_grid_axes, motor_axis
    #     yield from bps.mv(stage.phi, 0)           # 'prs' is now 'stage.phi' — see ⚠️ below
    #     yield from map_grid_run(
    #         "Sam5p4_scan_prs0", dets=[pil900KW], t=t,
    #         axes=spatial_grid_axes(piezo.x, x_list, piezo.z, z_list),
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi' (the 'mv(prs, 0)'
    #   line below would error); (2) 'det_exposure_time(...)' no longer sets the exposure unless run
    #   as a plan (⚠️ notes below). (The big '''...''' block is commented-out and isn't run.)
    # === end smi_plans note ================================================

    waxs_angle_array = np.array([10])
    print('{}'.format(waxs_angle_array))

    dets = [pil900KW]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]

    '''
    sample = "Sam5p4_scan_prs-90"
    yield from bps.mv(prs, -90)
    #x1_list = np.arange(-200, 1500, 30)
    #x2_list = np.arange(1500, 2800+1, 30)
    #x_list = np.concatenate((x2_list, x1_list))
    x_list = np.arange(-200, 2800+1, 30)
    z_list = np.arange(-900, 1300+1, 30)
    #yield from bps.mv(stage.th, -0.27) #2022 Oct 24
    yield from bps.mv(stage.th, -0.32) #-0.34,-0.4 2022 Oct 25

    for waxs_angle in waxs_angle_array:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)

        det_exposure_time(t, t)

        for ii, x in enumerate(x_list):  # loop over samples on bar
            yield from bps.mv(piezo.x, x)  # move to next sample
            for jj, z in enumerate(z_list):  # loop over samples on bar
                yield from bps.mv(piezo.z, z)  # move to next sample
                sample_name = (
                    "{sample}_waxs{waxs_angle:05.2f}_x{x}_z{z}_th{th}_{t}s".format(
                        sample=sample, waxs_angle=waxs_angle, x=x, z=z, th=stage.th, t=t
                    )
                )
                sample_id(user_name="ET2", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    '''
    sample = "Sam5p4_scan_prs0"
    yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    #x_list = np.arange(-200, 1600+1, 30)
    #z_list = np.arange(-3000, 1500+1, 30)
    x_list = np.arange(-200, 1300+1, 30)
    z_list = np.arange(400, 2700+1, 30)
    th = -0.65
    yield from bps.mv(stage.th, th) #-0.47
    y = 3530
    yield from bps.mv(piezo.y, y) #3500

    for waxs_angle in waxs_angle_array:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for ii, x in enumerate(x_list):  # loop over samples on bar
            yield from bps.mv(piezo.x, x)  # move to next sample
            for jj, z in enumerate(z_list):  # loop over samples on bar
                yield from bps.mv(piezo.z, z)  # move to next sample
                sample_name = (
                    "{sample}_waxs{waxs_angle:05.2f}_x{x}_y{y}_z{z}_th{th}_{t}s".format(
                        sample=sample, waxs_angle=waxs_angle, x=x, y=y, z=z, th=th, t=t
                    )
                )
                sample_id(user_name="ET3", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)





    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).



# 2020C1
def run_tomo_ET(t=0.5):  # 2020C1

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tomography-style scan — for each WAXS arc angle it steps the sample x across
    #   the beam and, at each x, rotates the stage (prs) through a set of angles (zig/zag) taking a
    #   WAXS+SAXS image at each rotation.
    #
    # 💡 NEWER, EASIER WAY: rotating the sample while recording the angle is 'smi_plans'
    #   tomography_run (or a motor_axis over the rotation stage); it records the rotation angle into
    #   the data and fills the file name for you:
    #
    #     from smi_plans import tomography_run, motor_axis
    #     for x in x_list:
    #         yield from bps.mv(stage.x, x)
    #         yield from tomography_run(
    #             "Sam5p4_scan", dets=[pil900KW, pil2M], t=t,   # current WAXS detector — see ⚠️
    #             rotation=motor_axis("phi", stage.phi, prs_angles_zig),   # prs is now stage.phi — see ⚠️
    #         )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi' (the two
    #   'bp.scan(dets, prs, ...)' lines below would error); (2) 'pil300KW' was retired — it's now
    #   'pil900KW'; (3) 'det_exposure_time(...)' no longer sets the exposure unless run as a plan
    #   (⚠️ notes below).
    # === end smi_plans note ================================================

    sample = "Sam5p4_scan"
    # x_list = [47200.000,37200.000,23700.000,15700.000]
    x_list = np.arange(-4.158 - 0.5, 3.842 + 0.01 + 0.5, 0.2)

    # assert len(x_list) == len(sample_list), f'Sample name/position list is borked'

    angle_arc = 0.1  # np.array([0.08, 0.1, 0.15, 0.2]) # incident angles
    # waxs_angle_array = np.linspace(0, 19.5, 4) #(0, 18, 4)   # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    ## if 12, 3: up to q=2.199
    ## if 18, 4: up to q=3.04

    waxs_angle_array = np.arange(
        6.5, 75, 6.5
    )  # (0, 18, 4)   # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    prs_angles_zig = [-90, 90.1, 120]
    prs_angles_zag = [90, -90 - 0.1, 120]
    dets = [pil300KW, pil2M]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    # yield from bps.mv(piezo.th, 0)
    # yield from alignement_gisaxs(0.1) #run alignment routine

    ##yield from bps.mv(waxs, 4)
    # try:
    # yield from bps.mv(waxs, 0)
    # except:
    # print('ERROR with WAXS, trying again..')
    # yield from bps.mv(waxs, 0)

    # stage.th.position = 0.382
    th_meas = (
        angle_arc + 0.282
    )  # stage.th.position #np.array([0.10 + piezo.th.position, 0.20 + piezo.th.position])
    th_real = angle_arc

    for waxs_angle in waxs_angle_array:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)

        if waxs_angle == 0:
            det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)).
        else:
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        for ii, x in enumerate(x_list):  # loop over samples on bar
            yield from bps.mv(stage.x, x)  # move to next sample

            sample_name = (
                "{sample}_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x}_{t}s".format(
                    sample=sample, th=th_real, waxs_angle=waxs_angle, x=x, t=t
                )
            )
            sample_id(user_name="ET2", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            if ii % 2 == 0:
                yield from bp.scan(dets, prs, *prs_angles_zig)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
            else:
                yield from bp.scan(dets, prs, *prs_angles_zag)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def run_gisaxsAngle_ET(t=1):  # 2020C1
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS scan — aligns the sample, then steps through several
    #   incident angles (piezo.th) and, at each, shifts x a little and sweeps the WAXS arc, taking
    #   an image at each combination.
    #
    # 💡 NEWER, EASIER WAY: sweeping the incident angle + WAXS arc while recording is the 'smi_plans'
    #   GIWAXS preset; align_sample aligns once and saves the result, and incidence_axis/motor_axis
    #   record the angle/arc into the data:
    #
    #     from smi_plans import giwaxs_run, align_sample, incidence_axis, motor_axis
    #     yield from giwaxs_run(
    #         sample, dets=[pil900KW], t=t,          # current WAXS detector — see ⚠️
    #         incident_angles=[0.08, 0.1, 0.15, 0.2],   # your angles, unchanged
    #         arc_angles=list(np.linspace(0, 19.5, 4)),
    #         align=align_sample,
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan (⚠️ notes below).
    #   (Heads-up for a human: 'x_list' and 'x' aren't defined in this function — pre-existing issues.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar

    sample_list = ["tomosample"]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    angle_arc = np.array([0.08, 0.1, 0.15, 0.2])  # incident angles
    waxs_angle_array = np.linspace(
        0, 19.5, 4
    )  # (0, 18, 4)   # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    # if 12, 3: up to q=2.199
    # if 18, 4: up to q=3.04
    dets = [pil300KW]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    # for x, sample in zip(x_list,sample_list): #loop over samples on bar
    if 1:
        # yield from bps.mv(piezo.x, x) #move to next sample
        yield from bps.mv(piezo.th, 0)
        yield from alignement_gisaxs(0.1)  # run alignment routine

        yield from bps.mv(waxs, 4)
        try:
            yield from bps.mv(waxs, 0)
        except:
            print("ERROR with WAXS, trying again..")
            yield from bps.mv(waxs, 0)

        th_meas = (
            angle_arc + piezo.th.position
        )  # np.array([0.10 + piezo.th.position, 0.20 + piezo.th.position])
        th_real = angle_arc

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        x_meas = x

        # for waxs_angle in waxs_angle_array: # loop through waxs angles
        for i, th in enumerate(th_meas):  # loop over incident angles
            yield from bps.mv(piezo.th, th)

            for jj in [0, 1, 2, 3]:
                if i == 0 and jj == 0:
                    x_meas = x_meas - 50  # shift a bit in x
                else:
                    x_meas = x_meas - 200  # shift a bit in x
                yield from bps.mv(piezo.x, x_meas)

                for waxs_angle in waxs_angle_array:
                    yield from bps.mv(waxs, waxs_angle)

                    sample_name = (
                        "{sample}_{th:5.4f}deg_x{x}_waxs{waxs_angle:05.2f}_{t}s".format(
                            sample=sample,
                            th=th_real[i],
                            x=x_meas,
                            waxs_angle=waxs_angle,
                            t=t,
                        )
                    )
                    sample_id(user_name="AB2", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")

                    # yield from bp.scan(dets, energy, e, e, 1)
                    # yield from bp.scan(dets, waxs, *waxs_arc)
                    yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def piezo_pos():
    for ii in [piezo.x, piezo.y, piezo.z, piezo.th, piezo.ch]:
        print(ii.name, ii.position)


def stage_pos():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: prints the current positions of the hexapod x, theta, and the rotation stage.
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' no longer exists — it's now 'stage.phi' (this line would
    #   error on 'prs'). 'stage.x' and 'stage.th' still work.
    # === end smi_plans note ================================================
    for ii in [stage.x, stage.th, prs]:  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        print(ii.name, ii.position)


####

#
# Modify file (sample name, x pos), Save file
# Check sample stage (SmarAct Y) is aroundre 6500
# xxCheck bsx at 0.7

# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Tsai.py
#
# Data: /GPFS/xf12id1/data/images/users/2020_1/Tsai


"""
phi=prs stage
1st round
prs = 90, stage.th = 0.375
prs = -90, stage.th = 0.385
2nd round
prs = 90, stage.th = 0.3825
prs = -90, stage.th = 0.3775

move piezo.ch to stage.th=0.38
%mov stage.th 
The stage.th is tuned well

tune piezo.th at prs = 0 (the rotation is limied bewtwee -95  and 95deg)

align the stage.th again at prs = 0

================alignment is done==============
================start measurement==============


In [238]: stage.th.position                                                                                           
Out[238]: 0.28200000000000003

aligned position: 0.1deg incident angle

In [263]: for ii in [piezo.x, piezo.y, piezo.z, piezo.th, piezo.ch]: 
     ...:     print(ii.name, ii.position) 
     ...:      
     ...:                                                                                                             
piezo_x -711.0120000000001
piezo_y 6711.778
piezo_z -190.161
piezo_th -0.1095
piezo_ch -0.138699

In [268]: stage_pos()                                                                                                 
stage_x -0.158
stage_th 0.382
prs 90.0







"""

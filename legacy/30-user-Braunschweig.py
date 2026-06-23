# Align GiSAXS sample
import numpy as np


def run_giwaxs(t=1):  # 2020C1
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS run over a bar of 4 samples — for each sample
    #   it aligns, then loops over WAXS detector-arc angles and incident angles, nudging x a
    #   little each shot, and takes a WAXS image.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a multi-sample "bar" helper that walks the bar,
    #   aligns each sample, sweeps the arc and incident angle, and records angle/position/beam
    #   straight into every image and file name — so you don't hand-build the long
    #   "{sample}_..._waxs..._x..." name or call sample_id yourself:
    #
    #     from smi_plans import SampleList, giwaxs_bar, align_sample
    #     samples = SampleList.from_columns(name=sample_list, x=x_list)   # list your bar once
    #     yield from giwaxs_bar(
    #         samples,
    #         incident_angles=[0.08, 0.1, 0.15, 0.2],   # your incident angles, unchanged
    #         arc=list(np.linspace(0, 19.5, 4)),        # your WAXS arc angles, unchanged
    #         t=t,                                       # your exposure time, unchanged
    #         align=align_sample,
    #     )
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (Optional — your script below works as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls need to be run as a plan (see ⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar

    sample_list = [
        "5_1_MeDPP_glassOTS_PhMe_none",
        "5_2_MeDPP_glassOTS_PhMe_60minVSADCM",
        "SC1_8_60minVSADCM",
        "SC1_8_PEDOTPSS",
    ]
    x_list = [47200.000, 37200.000, 23700.000, 15700.000]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    angle_arc = np.array([0.08, 0.1, 0.15, 0.2])  # incident angles
    waxs_angle_array = np.linspace(
        0, 19.5, 4
    )  # (0, 18, 4)   # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    # if 12, 3: up to q=2.199
    # if 18, 4: up to q=3.04
    dets = [pil300KW]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). (Also 'rayonix'/MAXS in the note above was retired with no replacement.)

    for x, sample in zip(x_list, sample_list):  # loop over samples on bar

        yield from bps.mv(piezo.x, x)  # move to next sample
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

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)
        x_meas = x

        for waxs_angle in waxs_angle_array:  # loop through waxs angles
            yield from bps.mv(waxs, waxs_angle)

            for i, th in enumerate(th_meas):  # loop over incident angles
                yield from bps.mv(piezo.th, th)

                # if sample!='OTS':
                x_meas = x_meas - 50  # shift a bit in x

                yield from bps.mv(piezo.x, x_meas)

                sample_name = (
                    "{sample}_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x}_{t}s".format(
                        sample=sample,
                        th=th_real[i],
                        waxs_angle=waxs_angle,
                        x=x_meas,
                        t=t,
                    )
                )
                sample_id(user_name="AB", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # yield from bp.scan(dets, energy, e, e, 1)
                # yield from bp.scan(dets, waxs, *waxs_arc)
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def run_gisaxsAngle_AB2(t=1):  # 2020C1
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same idea as run_giwaxs but over a 7-sample bar and with a different
    #   nesting — for each sample it aligns, then loops incident angle → a few x sub-spots →
    #   WAXS-arc angles, taking a WAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: this is again the 'smi_plans' multi-sample "bar" pattern — list the
    #   bar once and let giwaxs_bar walk it, align each sample, sweep angle/arc, and record
    #   angle/position/beam into every image and file name for you:
    #
    #     from smi_plans import SampleList, giwaxs_bar, align_sample
    #     samples = SampleList.from_columns(name=sample_list, x=x_list)   # list your bar once
    #     yield from giwaxs_bar(
    #         samples,
    #         incident_angles=[0.08, 0.1, 0.15, 0.2],   # your incident angles, unchanged
    #         arc=list(np.linspace(0, 19.5, 4)),        # your WAXS arc angles, unchanged
    #         t=t,                                       # your exposure time, unchanged
    #         align=align_sample,
    #     )
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (Optional — your script below works as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls need to be run as a plan (see ⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar

    sample_list = [
        "1_1_MeDPP_glass_thermal_none",
        "1_2_MeDPP_glass_thermal_0.5minVSADCM",
        "1_3_MeDPP_glass_thermal_1minVSADCM",
        "1_4_MeDPP_glass_thermal_5minVSADCM",
        "1_5_MeDPP_glass_thermal_15minVSADCM",
        "1_6_MeDPP_glass_thermal_60minVSADCM",
        "1_7_MeDPP_glass_thermal_240minVSADCM",
    ]
    x_list = [50000, 36800, 22800, 9800, -2500, -16500, -31000]

    # sample_list = ['2_1_MeDPP_glass_thermal_none', '2_2_MeDPP_SiO2_thermal_0.5minVSADCM', '2_3_MeDPP_SiO2_thermal_1minVSADCM', '2_4_MeDPP_SiO2_thermal_5minVSADCM', '2_5_MeDPP_SiO2_thermal_15minVSADCM', '2_6_MeDPP_SiO2_thermal_60minVSADCM', '2_7_MeDPP_SiO2_thermal_240minVSADCM','3_1_MeDPP_SiO2_PhMe_none','3_2_MeDPP_SiO2_PhMe_60minVSADCM','3_3_MeDPP_SiO2_DCM_none','3_4_MeDPP_SiO2_DCM_60minVSADCM','4_1_MeDPP_SiO2_loosepowder_none','4_2_MeDPP_SiO2_loosepowder_shear','4_3_MeDPP_SiO2_compressedpowder_none','4_4_MeDPP_SiO2_compressedpowder_shear']
    # x_list = [-51400,-44400.000, -37400.000, -31400.000,-24400.000, -17400.000,-10400.000,-4400.000,2600.000,8600.000,15600.000,23600.000,29600.000,36600.000,46600.000]

    # sample_list = ['OTS',
    # sample_list = ['5_1_MeDPP_glassOTS_PhMe_none','5_2_MeDPP_glassOTS_PhMe_60minVSADCM','SC1_8_60minVSADCM','SC1_8_PEDOTPSS']
    # x_list = [50250,
    # x_list = [47200.000,37200.000,23700.000,15700.000]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    angle_arc = np.array([0.08, 0.1, 0.15, 0.2])  # incident angles
    waxs_angle_array = np.linspace(
        0, 19.5, 4
    )  # (0, 18, 4)   # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    # if 12, 3: up to q=2.199
    # if 18, 4: up to q=3.04
    dets = [pil300KW]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). (Also 'rayonix'/MAXS in the note above was retired with no replacement.)

    for x, sample in zip(x_list, sample_list):  # loop over samples on bar

        yield from bps.mv(piezo.x, x)  # move to next sample
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

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)
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


####

# Data: /GPFS/xf12id1/data/images/users/2019_3/306008_Braunschweig/


# NOTE - this x position is close to the edge of the sample AB_2_5_MeDPP_SiO2_thermal_15minVSADCM_0.0800deg_waxs19.50_x-22400.0_0.5s_000001_WAXS.tif, checked egde pos: -22240

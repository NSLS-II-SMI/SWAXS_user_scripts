def sample_bar(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: measures a bar of ~39 printed samples — for each WAXS-arc angle it visits each
    #   sample's x/y position and does a vertical (y) line scan, taking SAXS+WAXS along the way.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a "bar" helper that visits each sample, sweeps the WAXS
    #   arc, and runs the per-sample y scan while recording sample/position/arc INTO each image, in
    #   one call (so you don't hand-format the name or keep parallel x/y/range lists in sync):
    #
    #     from smi_plans import map_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_names, x=x_list, y=y_list)
    #     yield from map_bar(samples, piezo.y, y_range, waxs_arc=[0, 6.5, 13],
    #                        dets=[pil2M, pil900KW], t=meas_t)
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan. See the ⚠️
    #   notes on those lines. (internal: Tier 2.)
    # === end smi_plans note ================================================
    # bar_number = 'bar_A'

    # sample_names=['sample_01', 'sample_02', 'sample_03', 'sample_04', 'sample_05', 'sample_06', 'sample_07', 'sample_08', 'sample_09',
    # 'sample_10', 'sample_11', 'sample_12', 'sample_13', 'sample_14', 'sample_15', 'sample_16', 'sample_17', 'sample_18', 'sample_19',
    # 'sample_20', 'sample_21', 'sample_22', 'sample_23', 'sample_24', 'sample_25', 'sample_26', 'sample_27', 'sample_28', 'sample_29',
    # 'sample_30', 'sample_31', 'sample_32', 'sample_33', 'sample_34', 'sample_35', 'sample_36', 'sample_37', 'sample_38', 'sample_39',
    # 'sample_40']

    # x_list = [-56000, -50100, -44400, -38400, -32100, -26500, -20500, -14400, -8400,
    # -2400, 3600, 9600, 15600, 21600, 27600, 33600, 39600, 45600, 51600,
    # 57600, -56000, -50100, -44400, -38400, -32500, -26500, -20200, -14100, -8400,
    # -2400, 3200, 9600, 15600, 21600, 27600, 33600, 39200, 45600, 51600,
    # 57600,]
    # y_list = [-500, -200, 0, 0, -250, 250, 0, -300, -200,
    # -300, 100, 0, 0, 200, 0, 150, -50, 100, 250,
    # 700, 3750, 4000, 3900, 3900, 3850, 4000, 3500, 3500, 3900,
    # 3600, 3750, 3850, 3750, 3650, 3500, 4150, 4200, 4200,4450,
    # 4000
    # ]

    # y_range = [[0,650,66], [0,650,66], [0,400,41], [0,550,56], [0,400,41],[0,300,31], [0,400,41], [0,900,91],[0,1000,101],
    # [0,1000,101],[0,550,56],[0,550,56],[0,500,51],[0,350,36],[0,350,36],[0,350,36],[0,900,91],[0,900,91],[0,950,96],
    # [0,400,41],[0,500,51],[0,500,51],[0,500,51],[0,450,46],[0,450,46],[0,600,61],[0,700,71],[0,700,71],[0,700,71],
    # [0,650,66],[0,700,71],[0,700,71],[0,700,71],[0,650,66],[0,700,71],[0,700,71],[0,450,46],[0,400,41],[0,400,41],
    # [0,500,51],
    # ]

    # bar_number = 'bar_B'

    # sample_names=['sample_01', 'sample_02', 'sample_03', 'sample_04', 'sample_05', 'sample_06', 'sample_07', 'sample_08', 'sample_09',
    # 'sample_10', 'sample_11', 'sample_12', 'sample_13', 'sample_14', 'sample_15', 'sample_16', 'sample_17', 'sample_18', 'sample_19',
    # 'sample_20', 'sample_21', 'sample_22', 'sample_23', 'sample_24', 'sample_25', 'sample_26', 'sample_27', 'sample_28', 'sample_29',
    # 'sample_30', 'sample_31', 'sample_32', 'sample_33', 'sample_34', 'sample_35', 'sample_36', 'sample_37', 'sample_38', 'sample_39',
    # 'sample_40']

    # x_list = [-56000, -50100, -44400, -38400, -32100, -26200, -20500, -14400, -8400,
    # -2400, 3600, 9600, 15600, 21600, 27600, 33300, 39600, 45600, 51600,
    # 57600, -56000, -50100, -44400, -38400, -32500, -26500, -20200, -14100, -8400,
    # -2700, 3600, 9600, 15400, 21600, 27600, 33600, 39200, 45600, 51600,
    # 57600]
    # y_list = [0, -200, -550, -550, -50, -450, 0, -200, -50,
    # -100, -50, 150, 0, -300, 600, 250, 470, -50, 600,
    # 800, 4400, 4250, 3900, 3950, 3850, 4050, 4300, 3950, 4800,
    # 3650, 3650, 4350, 4500, 4250, 4250, 3850, 4600, 3900, 4150,
    # 4700]

    # y_range = [[0,700,71], [0,500,51], [0,600,61], [0,600,61], [0,700,71],[0,800,81], [0,650,66], [0,800,81],[0,750,76],
    # [0,650,66],[0,700,71],[0,850,86],[0,800,81],[0,900,91],[0,350,36],[0,350,36],[0,300,31],[0,300,31],[0,350,36],
    # [0,300,31],[0,450,56],[0,400,41],[0,350,36],[0,350,36],[0,400,41],[0,400,41],[0,250,26],[0,300,31],[0,300,31],
    # [0,400,41],[0,300,31],[0,350,36],[0,350,36],[0,350,36],[0,400,41],[0,300,31],[0,350,36],[0,350,36],[0,350,36],
    # [0,350,36],
    # ]

    # bar_number = 'bar_C'

    # sample_names=['sample_01', 'sample_02', 'sample_03', 'sample_04', 'sample_05', 'sample_06', 'sample_07', 'sample_08', 'sample_09']
    # x_list = [-57600, -51600, -45600, -39600, -33600, -27600, -21600, -15600, -9600]
    # y_list = [-300, -500, -550, 0, 100, 600, -150, -100, 3500]
    # y_range = [[0,400,41], [0,250,26], [0,350,36], [0,350,36], [0,350,36],[0,250,26], [0,250,26], [0,300,31],[0,400,41]]

    bar_number = "bar_D"

    sample_names = [
        "sample_01",
        "sample_02",
        "sample_03",
        "sample_04",
        "sample_05",
        "sample_06",
        "sample_07",
        "sample_08",
        "sample_09",
        "sample_10",
        "sample_11",
        "sample_12",
        "sample_13",
        "sample_14",
        "sample_15",
        "sample_16",
        "sample_17",
        "sample_18",
        "sample_19",
        "sample_20",
        "sample_21",
        "sample_22",
        "sample_23",
        "sample_24",
        "sample_25",
        "sample_26",
        "sample_27",
        "sample_28",
        "sample_29",
        "sample_30",
        "sample_31",
        "sample_32",
        "sample_33",
        "sample_34",
        "sample_35",
        "sample_36",
        "sample_37",
        "sample_38",
        "sample_39",
    ]

    x_list = [
        -57000,
        -51000,
        -45000,
        -39000,
        -33000,
        -27000,
        -21000,
        -15000,
        -9000,
        -3000,
        3000,
        9000,
        15000,
        21000,
        27000,
        33000,
        39000,
        45000,
        51000,
        57000,
        -57000,
        -51000,
        -45000,
        -39000,
        -33000,
        -27000,
        -21000,
        -15000,
        -9000,
        -3000,
        3000,
        9000,
        15000,
        21000,
        27000,
        33000,
        39000,
        45000,
        51000,
    ]

    y_list = [
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -800,
        -700,
        -700,
        -600,
        -500,
        -500,
        -500,
        -300,
        -300,
        -100,
        3200,
        3200,
        3200,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3500,
        3800,
        3800,
    ]

    y_range = [
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 2000, 101],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
        [0, 1500, 151],
    ]

    waxs_arc = [0, 6.5, 13]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(x_list) == len(
        sample_names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        for x, y, sample, y_r in zip(x_list, y_list, sample_names, y_range):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            name_fmt = "{bar}_{sam}_wa{waxs}_dy_10um_exptime_1_yscan"
            sample_name = name_fmt.format(bar=bar_number, sam=sample, waxs="%2.1f" % wa)
            sample_id(user_name="ED", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_scan(dets, piezo.y, *y_r)


# Do not forget to chang the sample name. Also do not make it too many characters!

names = ["ECD_2.5mms5psi2_h118w13bar23_8"]
# names=['ECD_2.5mms5psi2_69B_h650w0bar11_3']
height = 0.059  # mm shift from the nozzle this is half the filament width, which we call h in the name
# waxs arc angle: 0 for the detector centered and 6 for the detctor at 6 degrees
# Do not enter a value
waxs_arc = 13

# 0 or 6.5 or 13g

# No need to be modify
det = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). This module-level 'det' list is used by data_acquisition()/beam_damage_study() below.

import sys
import time


def track_printer(exp_t=1, meas_t=10, trigger_num=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: in-situ 3D-printing acquisition. It watches the printer's hardware signals
    #   (EPICS PVs) and, each time the printer says "I just fired a layer", triggers an X-ray
    #   measurement — stopping after the requested number of triggers, then moving the beam back to
    #   the nozzle. So the printer drives WHEN you collect, not a fixed timer.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a printer-triggered recipe that does exactly this PV
    #   watching + fire-synchronized acquisition for you, recording the print-event number into each
    #   image (so you don't hand-wire monitor/ready/trigger PVs and a while-loop):
    #
    #     from smi_plans import printer_triggered_run
    #     yield from printer_triggered_run(names[0], n_events=trigger_num, t=exp_t,
    #         dets=[pil2M, pil900KW], height=height, height_axis=stage.y)
    #     # (wait_for_printer_fire / beam_to_filament_middle are also available as building blocks.)
    #
    #   (Just a suggestion — your monitoring loop below still works as-is. Note the WAXS detector it
    #    eventually uses, via data_acquisition/det, is the retired pil300KW — see that ⚠️.)
    #   (internal: Tier 0.)
    # === end smi_plans note ================================================

    # Align the sample
    # yield from sample_alignment()

    if waxs.arc.position < 6 and waxs.x.position > -20:
        sys.exit("You moved waxs arc and not waxs ")

    monitor_pv = EpicsSignal("XF:11ID-CT{M1}bi2", name="monitor_pv")
    ready_for_trigger_pv = EpicsSignal("XF:11ID-CT{M1}bi3", name="ready_for_trigger_pv")
    trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", name="trigger_signal")

    trigger_count = 0
    while monitor_pv.get() == 1:
        if trigger_signal_pv.get() == 1:  # trigger signal to execute
            print('this is "function_triggered"! \nGoing to trigger detector...')

            trigger_count += 1
            experimental_adjustement()

            yield from data_acquisition(exp_t, meas_t)
            # yield from beam_damage_study(exp_t, sleep_time, meas_t)

            print("function_triggered successfully executed...waiting for next call.")

            if trigger_count >= trigger_num:
                yield from bps.mv(trigger_signal_pv, 0)
                break
                print("number of requested triggers reached, stopping monitoring...")
            else:
                pass

        yield from bps.sleep(0.5)
        print("monitoring trigger signal")

    # Post printing WAXS measurment
    # det_exposure_time(1)

    # yield from data_acquisition(1, 1)

    # yield from bps.mv(waxs, 8.8)
    # yield from data_acquisition(1, 1)

    # Come back to the beam on the nozzle
    yield from bps.mvr(stage.y, -height)

    print("Done")


def track_printer_timeRes(exp_t=0.1, meas_t=8, trigger_num=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like track_printer, but after the printer fires it ALSO follows the slow
    #   crystallization for 30 minutes — first a fast burst (the initial dynamics), then a long loop
    #   sweeping the WAXS arc over and over for 1800 s to watch the printed material set.
    #
    # 💡 NEWER, EASIER WAY: this "fire-triggered, then follow the crystallization" pattern is two
    #   smi_plans recipes back-to-back, both of which record elapsed time / event into the data:
    #     from smi_plans import printer_triggered_run, print_crystallization_followup_run
    #     yield from printer_triggered_run(names[0], n_events=1, t=exp_t, dets=[pil2M, pil900KW])
    #     yield from print_crystallization_followup_run(names[0], duration_s=1800,
    #                                                   waxs_arc=(0, 13, 3), t=1)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan. See the ⚠️
    #   notes on those lines. (internal: Tier 0.)
    # === end smi_plans note ================================================

    # Aligne the sample
    # yield from sample_alignment()

    if waxs.arc.position < 6 and waxs.x.position > -20:
        sys.exit("You moved waxs arc and not waxs ")

    monitor_pv = EpicsSignal("XF:11ID-CT{M1}bi2", name="monitor_pv")
    ready_for_trigger_pv = EpicsSignal("XF:11ID-CT{M1}bi3", name="ready_for_trigger_pv")
    trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", name="trigger_signal")

    trigger_count = 0
    while monitor_pv.get() == 1:
        if trigger_signal_pv.get() == 1:  # trigger signal to execute
            print('this is "function_triggered"! \nGoing to trigger detector...')

            trigger_count += 1
            experimental_adjustement()

            # initial dynamics
            yield from data_acquisition(
                exp_t, meas_t
            )  # controlled by input to track_printer_timeRes

            # longtime dynamics
            t0 = time.time()
            t1 = time.time()
            waxs_arc = [0, 13, 3]
            dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
            meas_t = 1
            det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
            loopNum = 0
            while t1 - t0 <= 1800:  # total experimental time after initial dynamics
                # yield from bps.sleep(sleep_time) #sleep_time is 29 s between exposures
                yield from bp.scan(dets, waxs, *waxs_arc)
                t1 = time.time()
                print("total elapsed time and loop number")
                print(t1 - t0)
                loopNum = loopNum + 1
                print(loopNum)
                # timing = timing + exp_t + sleep_time

            # yield from beam_damage_study(exp_t, sleep_time, meas_t)

            print("function_triggered successfully executed...waiting for next call.")

            if trigger_count >= trigger_num:
                yield from bps.mv(trigger_signal_pv, 0)
                break
                print("number of requested triggers reached, stopping monitoring...")
            else:
                pass

        yield from bps.sleep(0.5)
        print("monitoring trigger signal")

    # Post printing WAXS measurment
    # det_exposure_time(1)

    # yield from data_acquisition(1, 1)

    # yield from bps.mv(waxs, 8.8)
    # yield from data_acquisition(1, 1)

    # Come back to the beam on the nozzle
    yield from bps.mvr(stage.y, -height)

    print("Done")


def experimental_adjustement():
    # TODO: What do we want to put in the filename
    name_fmt = "{sample}"

    sample_name = name_fmt.format(sample=names[0])
    sample_id(user_name="ED", sample_name=sample_name)


def sample_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the beam to the substrate/film interface and parks it in the middle of
    #   the printed film (height scan + a small offset), using the legacy SMI_Beamline alignment mode.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the printing recipes take an align step and the
    #   beam-to-film positioning is handled by beam_to_filament_middle, with the result saved next to
    #   the data — so you don't drive smi.modeAlignment()/modeMeasurement() by hand. (Nothing broken.)
    # === end smi_plans note ================================================
    sample_id(user_name="test", sample_name="test")

    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    if waxs.arc.position < 6:
        yield from bps.mv(waxs, 6)

    yield from smi.setDirectBeamROI()

    # move to the substrate interface
    yield from align_height_hexa(0.40, 30, der=True)

    # Move the beam to the middle of the film
    yield from bps.mvr(stage.y, height)

    yield from bps.mv(waxs, waxs_arc)

    yield from smi.modeMeasurement()

    # Relative move of the nozzle
    # yield from bps.mvr(stage.x, x_offset)


def align_height_hexa(rang=0.3, point=31, der=False):
    # smi_plans: a height (stage.y) centering scan used during alignment. In smi_plans this kind of
    #   centering is part of align_sample / the printing recipes' align step (and the result is saved
    #   with the data). The ⚠️ below is the only thing that needs a fix to run today.
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_scan([pil2M], stage.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(stage.y, ps.cen)
    plt.close("all")


def align_x_hexa(rang=0.3, point=31, der=False):
    # smi_plans: an x (stage.x) centering scan used during nozzle alignment — same idea as
    #   align_height_hexa. The ⚠️ below is the only thing that needs a fix to run today.
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_scan([pil2M], stage.x, -rang, rang, point)
    # yield from bps.mv(stage.y, ps.cen)


"""       
def align_theta_hexa(rang = 0.1, point = 20, der=False):   
        det_exposure_time(0.5)
        yield from bp.rel_scan([pil2M], stage.th, 0, rang, point )
        ps(der=der)
        #yield from bps.mv(stage.y, ps.cen)
        #plt.close('all')
"""


def data_acquisition(exp_t, meas_t):
    """
    Meas_t: exposition time in second
    num: number of images
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the shared "set exposure, take one image" leaf that the printer-tracking plans
    #   call. It uses the module-level 'det' list (which currently includes the retired pil300KW).
    # 💡 NEWER, EASIER WAY: in smi_plans a single frame is one acquire, and the printing recipes
    #   (printer_triggered_run, etc.) take the exposure via t=, so you don't need this helper.
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line); also the 'det' list above uses the retired pil300KW.
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, meas_t)  — or at the prompt:  RE(det_exposure_time(exp_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.count(det, num=1)


def nozzle_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # smi_plans: aligns the beam to the printer nozzle (an x-centering scan via the legacy
    #   SMI_Beamline mode). In smi_plans, nozzle/filament positioning is handled by
    #   beam_to_filament_middle and the recipes' align step, with the result saved with the data.
    #   (Nothing here is broken.)
    sample_id(user_name="test", sample_name="test")

    # yield from bps.mv(GV7.open_cmd, 1)
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    if waxs.arc.position < 12:
        yield from bps.mv(waxs, 12)

    yield from smi.setDirectBeamROI()

    # Find the center of the nozzle
    yield from align_x_hexa(1, 45, der=False)

    if waxs.arc.position > 8:
        yield from bps.mv(waxs, waxs_arc)

    yield from smi.modeMeasurement()
    # yield from bps.mv(GV7.close_cmd, 1 )


def beam_damage_study(exp_time, sleep_time, meas_time):
    """
    exp_time: exposure time
    sleep_time: sleeping time
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a timed series of frames (with a sleep between each) to see how fast the
    #   X-ray beam damages the sample.
    # 💡 NEWER, EASIER WAY: a "frames on a timer" series is time_series_run in smi_plans, which
    #   records elapsed time/frame into the data:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("beam_damage", duration=meas_time, period=sleep_time,
    #                                t=exp_time, dets=[pil2M, pil900KW])
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line); also 'det' uses the retired pil300KW. (internal: Tier 0.)
    # === end smi_plans note ================================================
    it = np.int(meas_time / (exp_time + sleep_time))
    det_exposure_time(exp_time, meas_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, meas_time)  — or at the prompt:  RE(det_exposure_time(exp_time, meas_time)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.count(det, num=it, delay=sleep_time)


# TODO: Try this function
def scan_fil_height(exp_time, rang, nb_point):
    # smi_plans: a filament-height (stage.y) line scan. In smi_plans this is map_line_run /
    #   acquire + motor_axis("y", stage.y, ...). The ⚠️ below is the only run-blocking fix.
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_scan(det, stage.y, -rang, rang, point)


def ex_situ(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ map of printed lines — for each WAXS-arc angle it walks two rows of
    #   20 positions across the substrate and does a vertical (y) line scan at each, taking SAXS+WAXS.
    # 💡 NEWER, EASIER WAY: this is a grid/bar map in smi_plans (map_grid_run / map_bar), which builds
    #   the positions and records them into each image; sweep the arc as an axis or via the bar helper.
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 2.)
    # === end smi_plans note ================================================
    x0, y0 = (-54449, 4599)  # Bottom left coordinate
    x20, y20 = (59448.8, 4599)  # Bottom right coordinate
    x1, y1 = (-54449.42, 799.93)  # top left coordinate
    sample = "J"

    y_range = [-700, 700, 36]
    waxs_arc = [0.0, 6.5, 13.0, 19.5, 26.0, 32.5, 39.0]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{po}_wa{waxs}"  # Sample name _ positions
    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        for i, (x, y) in enumerate(
            zip(np.linspace(x0, x20, 20), np.linspace(y0, y20, 20))
        ):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            sample_name = name_fmt.format(
                sample=sample, po="%2.2d" % (1 + i), waxs="%2.1f" % wa
            )
            sample_id(user_name="ED", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_scan(dets, piezo.y, *y_range)
            plt.close("all")

        for j, (x, y) in enumerate(
            zip(np.linspace(x0, x20, 20), np.linspace(y0, y20, 20))
        ):
            yield from bps.mv(piezo.x, x - x0 + x1)
            yield from bps.mv(piezo.y, y - y0 + y1)
            sample_name = name_fmt.format(
                sample=sample, po="%2.2d" % (2 + i + j), waxs="%2.1f" % wa
            )
            sample_id(user_name="ED", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_scan(dets, piezo.y, *y_range)
            plt.close("all")


def ex_situ_temp(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature series on 4 samples — it ramps the Lakeshore heater to each set
    #   point (stepping up gently and soaking), then for each WAXS-arc angle visits the 4 samples and
    #   takes a SAXS+WAXS image, recording the target and actual temperature in the file name.
    # 💡 NEWER, EASIER WAY: temperature ramps are a built-in recipe in smi_plans (temperature_ramp_run
    #   / temperature_bar), which drives the heater, waits for it to settle, and records the real
    #   temperature INTO each image:
    #     from smi_plans import temperature_ramp_run, lakeshore_heater
    #     heater = lakeshore_heater()
    #     yield from temperature_ramp_run("ECD_temp", heater, np.linspace(30, 170, 21),
    #         t=meas_t, dets=[pil2M, pil900KW])    # (compose with a per-temp sample/arc loop)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample = ["3E", "1E", "3I", "1I"]
    pos = [(-12250, -3300), (550, -3300), (13150, -3100), (25850, -3000)]
    temp = np.linspace(30, 170, 21)
    waxs_arc = np.linspace(13, 0, 3)
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_wa{waxs}_{temp}C_{actualTemp}C"

    for target_t in temp:
        for i in np.linspace(1, 7, 7):
            yield from bps.mv(ls.ch1_sp, target_t - 7 + i)
            yield from bps.sleep(10)
        yield from bps.sleep(240)
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            for k, (x, y) in enumerate(pos):
                theTemperature = ls.ch1_read.value
                sample_name = name_fmt.format(
                    sample=sample[k],
                    waxs="%2.1f" % wa,
                    temp=target_t,
                    actualTemp=theTemperature,
                )
                sample_id(user_name="ED", sample_name=sample_name)

                yield from bps.mv(piezo.x, x)
                yield from bps.mv(piezo.y, y)

                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)


def ex_situ_single_sample(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single calibration-style measurement (AgBe) — sweeps a couple of WAXS-arc
    #   angles and takes one SAXS+WAXS image at each.
    # 💡 NEWER, EASIER WAY: in smi_plans this is one acquire with the arc as an axis:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("AgBe", [pil2M, pil900KW],
    #                        [motor_axis("waxs_arc", waxs.arc, [13.0])], t=meas_t)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample = "AgBe"
    waxs_arc = [13.0]
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_wa{waxs}"

    # target_t = '25' # change this?

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        # theTemperature = ls.ch1_read.value
        sample_name = name_fmt.format(sample=sample, waxs="%2.1f" % wa)
        # , temp=target_t, actualTemp = theTemperature)
        sample_id(user_name="ED", sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(dets, num=1)


def ex_situ_printer(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single ex-situ printed-ink measurement — sweeps the WAXS arc and takes
    #   SAXS+WAXS across it.
    # 💡 NEWER, EASIER WAY: in smi_plans this is one acquire with the arc as an axis (acquire +
    #   motor_axis("waxs_arc", waxs.arc, ...)).
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    # x_list = [-32500, -21500, -14500, -3500, 6500, 13500, 21500, 30500, 37500]
    sample_list = ["AK_92_ink_5s_meas_t"]

    # assert len(x_list) == len(sample_list), f'Sample name/position list is borked'

    waxs_arc = [0, 26, 5]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    # for x, sample in zip(x_list,sample_list): #loop over samples on bar
    # yield from bps.mv(piezo.x, x)
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

    name_fmt = "{sample}"
    sample_name = name_fmt.format(sample=sample_list[0])
    sample_id(user_name="ED", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.scan(dets, waxs, *waxs_arc)


def ex_situ_printer_height_profile(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a height-profile scan of a printed line — steps the hexapod height (stage.y)
    #   through a list of positions and at each takes a WAXS-arc sweep (SAXS+WAXS).
    # 💡 NEWER, EASIER WAY: compose a height axis with the arc sweep in one smi_plans acquire:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("height_profile", [pil2M, pil900KW],
    #         [motor_axis("y", stage.y, y_list),
    #          motor_axis("waxs_arc", waxs.arc, [0, 13, 3])], t=meas_t)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    y_list = [-2, -2.1, -2.2, -2.3, -2.4, -2.5, -2.6, -2.7, -2.8, -2.9, -2.10, -2.11]
    sample_list = [
        "11_5_hp01",
        "11_5_hp02",
        "11_5_hp03",
        "11_5_hp04",
        "11_5_hp05",
        "11_5_hp06",
        "11_5_hp07",
        "11_5_hp08",
        "11_5_hp09",
        "11_5_hp10",
        "11_5_hp11",
        "11_5_hp012",
    ]

    # assert len(x_list) == len(sample_list), f'Sample name/position list is borked'

    waxs_arc = [0, 13, 3]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for y, sample in zip(y_list, sample_list):  # loop over samples on bar
        yield from bps.mv(stage.y, y)
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

        name_fmt = "{sample}"
        sample_name = name_fmt.format(sample=sample)
        sample_id(user_name="ED", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_arc)


def bkg_bar(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a background measurement — sweeps the WAXS arc once and takes SAXS+WAXS, for
    #   subtracting the empty-bar/substrate signal.
    # 💡 NEWER, EASIER WAY: in smi_plans this is one acquire with the arc as an axis (acquire +
    #   motor_axis("waxs_arc", waxs.arc, ...)).
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️ notes
    #   on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================

    sample_list = ["bar23_background"]

    waxs_ar = [0, 13, 3]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

    name_fmt = "{sample}"
    sample_name = name_fmt.format(sample=sample_list[0])
    sample_id(user_name="ED", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.scan(dets, waxs, *waxs_ar)
    yield from bps.mv(waxs, waxs_arc)

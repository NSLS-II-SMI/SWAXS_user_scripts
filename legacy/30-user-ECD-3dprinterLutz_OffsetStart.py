# Do not forget to chang the sample name. Also do not make it too many characters!

# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE IS: an in-situ 3D-printing experiment — it watches the printer's trigger
#   wires (PVs) and fires the X-ray detector when the printer says "now", to catch the material
#   as it's extruded, plus some alignment and ex-situ mapping helpers.
#
# 💡 NEWER, EASIER WAY: the beamline now has a printing helper library in 'smi_plans' that does
#   exactly this hand-off with the printer. Instead of writing your own PV-watching loop, use:
#
#     from smi_plans import printer_triggered_run, wait_for_printer_fire   # once per session
#     yield from printer_triggered_run(name=names[0], dets=[pil2M, pil900KW], t=exp_t)
#       # it waits for the printer's fire signal, records the shot (with positions/beam),
#       # and writes a proper dataset — no manual /ramdisk or busy-wait needed.
#
#   (See the per-function notes below. The 💡 big win here is that smi_plans records each shot as
#    real data instead of you triggering the camera by hand.)
#
# ⚠️ NEEDS A FIX TO RUN NOW: this file's default detector list uses 'pil300KW', which was retired
#   (see the ⚠️ note on the 'det = [...]' line just below, and on each 'dets = [...]' line in the
#   functions). (internal: Tier 0/1 — printer-triggered.)
# === end smi_plans note ================================================

names = ["ECD_2.5mms5psi2_h118w13bar23_8"]
# names=['ECD_2.5mms5psi2_69B_h650w0bar11_3']
height = 0.059  # mm shift from the nozzle this is half the filament width, which we call h in the name
# waxs arc angle: 0 for the detector centered and 6 for the detctor at 6 degrees
# Do not enter a value
waxs_arc = 13

# 0 or 6.5 or 13g

# No need to be modify
det = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)

import sys
import time


def track_printer(exp_t=1, meas_t=10, trigger_num=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: waits for the 3D printer to say "go" (it polls a trigger wire/PV), and when
    #   it fires, it takes an X-ray measurement of the freshly-printed material; it can wait for
    #   several such triggers, then nudges back to the nozzle. (This is the printer hand-off plan.)
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a printing helper that does this wait-then-record
    #   hand-off for you, and (importantly) writes each shot as a proper dataset with the
    #   positions/beam recorded — instead of polling the PV in a hand-written loop:
    #
    #     from smi_plans import printer_triggered_run, wait_for_printer_fire   # once per session
    #     yield from printer_triggered_run(
    #         name=names[0], dets=[pil2M, pil900KW], t=exp_t,   # your exposure, unchanged
    #         n_triggers=trigger_num,                            # wait for this many printer fires
    #     )
    #
    #   (Optional — your loop below still works. Just note the detector/exposure ⚠️ fixes that
    #    apply via the helpers it calls.) (internal: Tier 0 — triggers off an external signal.)
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
    # WHAT THIS DOES: like track_printer, but after the printer fires it follows the material over
    #   time — a fast first shot, then it loops WAXS-arc scans for ~30 minutes to watch the
    #   crystallization develop.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a printer-triggered "follow-up over time" preset for
    #   exactly this (wait for the fire, then track the print as it evolves):
    #
    #     from smi_plans import print_crystallization_followup_run, wait_for_printer_fire
    #     yield from print_crystallization_followup_run(
    #         name=names[0], dets=[pil2M, pil900KW], t=exp_t)   # records each time point as data
    #
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (Optional — your loop below works as-is EXCEPT the ⚠️ lines.) (internal: Tier 0/1.)
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
            dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)
            meas_t = 1
            det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' print_crystallization_followup_run sets exposure for you via t=.)
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
    # WHAT THIS DOES: aligns the beam to the substrate/film interface (height scan), then nudges
    #   into the middle of the film and switches to measurement mode. (Alignment routine.)
    #
    # 💡 NEWER, EASIER WAY: in smi_plans, alignment like this is usually 'align_sample', run once
    #   and recorded with your data automatically, then passed as align= to your run. (Nothing
    #   broken here.)
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a height alignment — scans stage.y, finds the peak, and moves there.
    #   (Alignment helper used by sample_alignment.)
    #
    # 💡 NEWER, EASIER WAY: handled by 'align_sample' in smi_plans. Mind the ⚠️ exposure fix below.
    # === end smi_plans note ================================================
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
    yield from bp.rel_scan([pil2M], stage.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(stage.y, ps.cen)
    plt.close("all")


def align_x_hexa(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an x alignment — scans stage.x (e.g. to find the nozzle center).
    #   (Alignment helper.)
    #
    # 💡 NEWER, EASIER WAY: handled by 'align_sample' in smi_plans. Mind the ⚠️ exposure fix below.
    # === end smi_plans note ================================================
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
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
    # WHAT THIS DOES: the low-level "take one image" helper used by the printer plans above (sets
    #   the exposure, then counts the detector once).
    #
    # 💡 NEWER, EASIER WAY: a single recorded shot is one 'smi_plans.acquire' call (which sets the
    #   exposure via t= and records positions/beam into the image):
    #     from smi_plans import acquire
    #     yield from acquire(names[0], det, [], t=exp_t)
    #   (The printer presets call this for you — see the top-of-file note. Mind the ⚠️ fix below.)
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, meas_t)  — or at the prompt:  RE(det_exposure_time(exp_t, meas_t)). (smi_plans' acquire/printer presets set exposure for you via t=.)
    yield from bp.count(det, num=1)


def nozzle_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: finds the printer nozzle center (x scan) and returns to measurement mode.
    #   (Alignment helper specific to the printer nozzle.)
    #
    # 💡 NEWER, EASIER WAY: smi_plans' printing helpers include nozzle/beam alignment around the
    #   filament (see 'beam_to_filament_middle'); for general alignment use 'align_sample'.
    #   (Nothing broken here.)
    # === end smi_plans note ================================================
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
    # WHAT THIS DOES: a beam-damage test — takes a series of images on one spot with a delay
    #   between them, to see how the sample changes under the beam.
    #
    # 💡 NEWER, EASIER WAY: a repeated-on-one-spot time series is 'smi_plans.time_series_run' /
    #   'kinetics_run' (it timestamps each point and records position/beam for you):
    #     from smi_plans import time_series_run
    #   (Optional — this works as-is EXCEPT the ⚠️ exposure line below.)
    # === end smi_plans note ================================================
    it = np.int(meas_time / (exp_time + sleep_time))
    det_exposure_time(exp_time, meas_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, meas_time)  — or at the prompt:  RE(det_exposure_time(exp_time, meas_time)). (smi_plans' time_series_run sets exposure for you via t=.)
    yield from bp.count(det, num=it, delay=sleep_time)


# TODO: Try this function
def scan_fil_height(exp_time, rang, nb_point):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: scans the filament height (stage.y) and takes images, to find the best
    #   beam height on the printed filament.
    #
    # 💡 NEWER, EASIER WAY: a height scan with recording is a 'smi_plans.map_line_run' along
    #   stage.y, or part of 'align_sample'. (Mind the ⚠️ exposure line below.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)).
    yield from bp.rel_scan(det, stage.y, -rang, rang, point)


def ex_situ(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ map of a printed sample — for each WAXS arc it steps a diagonal
    #   line of x/y positions across the sample and does a y-scan at each, twice (two rows).
    #
    # 💡 NEWER, EASIER WAY: rastering positions and recording at each is 'smi_plans' mapping —
    #   'map_grid_run' / 'map_line_run' build the position grid and record position/beam into
    #   every image for you:
    #     from smi_plans import map_grid_run, spatial_grid_axes
    #   (Use 'pil900KW' for the current WAXS detector — see ⚠️ below. Optional otherwise; the
    #    ⚠️ exposure line below needs the plan-style fix.)
    # === end smi_plans note ================================================
    x0, y0 = (-61101, 4509.62)  # Bottom left coordinate
    x20, y20 = (52898, 4509.649)  # Bottom right coordinate

    x1, y1 = (x0, 509.610)  # top left coordinate

    sample = "B"
    y_range = [-700, 700, 36]
    waxs_arc = np.linspace(39, 0, 7)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' map_grid_run sets exposure for you via t=.)
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


def ex_situ_printer(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ WAXS-arc scan of a single printed sample (one spot, several arc
    #   angles).
    #
    # 💡 NEWER, EASIER WAY: a single-sample arc scan is one 'smi_plans.giwaxs_run' (or acquire
    #   with an arc motor_axis), which records arc/position/beam for you. (Use 'pil900KW' — see
    #   ⚠️ below; the ⚠️ exposure line also needs the plan-style fix.)
    # === end smi_plans note ================================================
    # x_list = [-32500, -21500, -14500, -3500, 6500, 13500, 21500, 30500, 37500]
    sample_list = ["AK_92_ink_5s_meas_t"]

    # assert len(x_list) == len(sample_list), f'Sample name/position list is borked'

    waxs_arc = [0, 26, 5]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)

    # for x, sample in zip(x_list,sample_list): #loop over samples on bar
    # yield from bps.mv(piezo.x, x)
    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' giwaxs_run sets exposure for you via t=.)

    name_fmt = "{sample}"
    sample_name = name_fmt.format(sample=sample_list[0])
    sample_id(user_name="ED", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.scan(dets, waxs, *waxs_arc)


def ex_situ_printer_height_profile(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps stage.y down through a series of heights ("samples") and does a
    #   WAXS-arc scan at each — a height profile of the printed structure.
    #
    # 💡 NEWER, EASIER WAY: a height series with recording is a 'smi_plans.map_line_run' along
    #   stage.y (or a SampleList of the heights handed to giwaxs_bar). It records height/arc/beam
    #   for you. (Use 'pil900KW' — see ⚠️ below; the ⚠️ exposure line also needs the fix.)
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
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)

    for y, sample in zip(y_list, sample_list):  # loop over samples on bar
        yield from bps.mv(stage.y, y)
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)

        name_fmt = "{sample}"
        sample_name = name_fmt.format(sample=sample)
        sample_id(user_name="ED", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_arc)


def bkg_bar(meas_t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a background WAXS-arc scan (one spot, several arc angles) and parks
    #   the WAXS arc afterward.
    #
    # 💡 NEWER, EASIER WAY: a single background arc scan is one 'smi_plans.giwaxs_run' / acquire
    #   with an arc axis (records arc/beam for you). (Use 'pil900KW' — see ⚠️ below; the ⚠️
    #   exposure line also needs the plan-style fix.)
    # === end smi_plans note ================================================

    sample_list = ["bar23_background"]

    waxs_ar = [0, 13, 3]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)

    det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (smi_plans' giwaxs_run sets exposure for you via t=.)

    name_fmt = "{sample}"
    sample_name = name_fmt.format(sample=sample_list[0])
    sample_id(user_name="ED", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.scan(dets, waxs, *waxs_ar)
    yield from bps.mv(waxs, waxs_arc)

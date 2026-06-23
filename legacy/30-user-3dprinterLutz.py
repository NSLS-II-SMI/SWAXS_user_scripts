# Do not forget to chang the sample name. Also do not make it too many characters!
names = ["20190425_10mms45psi.5sh0.117w6bar4_5"]
# names=['Kapton_test_25micron_waxs0']
height = 0.117  # mm shift from the nozzle
# waxs arc angle: 0 for the detector centered and 6 for the detctor at 6 degrees
# Do not enter a value
waxs_arc = 6  # 0 or 6 or 12

sleep_time = 0


# No need to be modify
det = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

import sys


def track_printer(exp_t=1, meas_t=1, trigger_num=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns to the printed film, then WATCHES the 3D printer's trigger wires (the
    #   EpicsSignal "...bi3"/"...bi4" PVs) in a busy-loop and, each time the printer says "I just
    #   fired", takes a WAXS snapshot — repeating until it has caught the requested number of fires.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper, 'smi_plans', built for exactly this
    #   "wait for the printer, then shoot" pattern. It waits on the printer fire signal AND records
    #   the data as a proper run (so the printer state / positions / beam are saved with the images,
    #   instead of you hand-naming files):
    #
    #     from smi_plans import printer_triggered_run, wait_for_printer_fire
    #     yield from printer_triggered_run(
    #         names[0],
    #         dets=[pil900KW],                      # current WAXS detector — see ⚠️ on 'det' above
    #         t=meas_t,                             # your exposure, unchanged
    #         n_triggers=trigger_num,               # however many printer fires to catch
    #         align=sample_alignment,               # your existing alignment step
    #     )
    #   (wait_for_printer_fire replaces the hand-rolled 'while monitor_pv.get()==1 ... sleep' loop
    #    below, and the run records everything together.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — the module-level 'det' above must use
    #   'pil900KW'; (2) the 'det_exposure_time(...)' calls (in data_acquisition / others) no longer
    #   set the exposure unless run as a plan (⚠️ notes on those lines).
    # === end smi_plans note ================================================

    if waxs_arc != 0 and waxs_arc != 6 and waxs_arc != 12:
        sys.exit("You entered a wrong value for the waxs arc")

    # Aligne the sample
    yield from sample_alignment()

    monitor_pv = EpicsSignal("XF:11ID-CT{M1}bi2", name="monitor_pv")
    ready_for_trigger_pv = EpicsSignal("XF:11ID-CT{M1}bi3", name="ready_for_trigger_pv")
    trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", name="trigger_signal")

    trigger_count = 0
    while monitor_pv.get() == 1:  # smi_plans: this hand-rolled "watch the printer's trigger wire and shoot when it fires" busy-loop is what wait_for_printer_fire / printer_triggered_run do for you (and they record the result as a proper run). Not broken — just lower-level than the modern helper.
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


def experimental_adjustement():
    # TODO: What do we want to put in the filename
    name_fmt = "{sample}"

    sample_name = name_fmt.format(sample=names[0])
    sample_id(user_name="EH", sample_name=sample_name)


def sample_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the alignment step for printing — opens the gate valve, switches the beamline
    #   into alignment mode, finds the film/substrate height, moves the beam into the film, then
    #   switches back to measurement mode. (Called by track_printer before it starts shooting.)
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you align ONCE up front with align_sample and the result
    #   is saved with the data; for the printer flow you'd hand this routine to printer_triggered_run
    #   as its align=... step. ('GV7', 'stage.y', 'waxs' all still work.)
    # === end smi_plans note ================================================
    sample_id(user_name="test", sample_name="test")

    yield from bps.mv(GV7.open_cmd, 1)
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    if waxs.arc.position < 12:
        yield from bps.mv(waxs, 12)

    yield from smi.setDirectBeamROI()

    # move to the substrate interface
    yield from align_height_hexa(0.40, 30, der=True)

    # Move the beam to the middle of the film
    yield from bps.mvr(stage.y, height)

    if waxs.arc.position > 8:
        yield from bps.mv(waxs, waxs_arc)

    yield from smi.modeMeasurement()
    yield from bps.mv(GV7.close_cmd, 1)

    # Relative move of the nozzle
    # yield from bps.mvr(stage.x, x_offset)


def align_height_hexa(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a height-alignment scan — sweeps the hexapod y over a small range, finds the
    #   peak/center, and moves there (to sit on the film/substrate interface).
    # 💡 NEWER, EASIER WAY: in 'smi_plans' alignment like this is done once with align_sample (for
    #   the printer flow, pass it via printer_triggered_run's align=...), and the result is saved
    #   with the data. ('stage.y', 'pil2M' all still work; 'bp.rel_scan' is fine.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
    yield from bp.rel_scan([pil2M], stage.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(stage.y, ps.cen)
    plt.close("all")


def align_x_hexa(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an x-alignment scan — sweeps the hexapod x over a small range (used to find
    #   the center of the nozzle).
    # 💡 NEWER, EASIER WAY: this kind of find-the-center sweep is part of smi_plans align_sample,
    #   which aligns once and saves the result with the data. ('stage.x', 'pil2M' still work.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on it below).
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
    # WHAT THIS DOES: sets the exposure and takes one WAXS image (the per-fire shot used by
    #   track_printer).
    # 💡 NEWER, EASIER WAY: printer_triggered_run takes each shot for you when the printer fires and
    #   records it as a run (so you don't hand-name files). The exposure is set via its t= argument.
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the module-level 'det' uses retired 'pil300KW' — switch to
    #   'pil900KW' (see ⚠️ on 'det' near the top); (2) 'det_exposure_time(...)' no longer sets the
    #   exposure unless run as a plan (⚠️ note on it below).
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, meas_t)  — or at the prompt:  RE(det_exposure_time(exp_t, meas_t)). (smi_plans' printer_triggered_run sets it for you via t=.)
    yield from bp.count(det, num=1)


def nozzle_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: finds the center of the print nozzle (opens the gate valve, alignment mode,
    #   sweeps x to center on the nozzle, then back to measurement mode).
    # 💡 NEWER, EASIER WAY: this centering sweep is part of smi_plans align_sample, which aligns
    #   once and saves the result with the data. ('GV7', 'waxs', the x sweep all still work.)
    # === end smi_plans note ================================================
    sample_id(user_name="test", sample_name="test")

    yield from bps.mv(GV7.open_cmd, 1)
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    if waxs.arc.position < 12:
        yield from bps.mv(waxs, 12)

    yield from smi.setDirectBeamROI()

    # Find the center of the nozzle
    yield from align_x_hexa(0.8, 40, der=False)

    if waxs.arc.position > 8:
        yield from bps.mv(waxs, waxs_arc)

    yield from smi.modeMeasurement()
    yield from bps.mv(GV7.close_cmd, 1)


def beam_damage_study(exp_time, sleep_time, meas_time):
    """
    exp_time: exposure time
    sleep_time: sleeping time
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a series of WAXS images of one spot with a delay between them, to watch
    #   how the X-ray beam damages the sample over time.
    # 💡 NEWER, EASIER WAY: a repeated-shots-with-delay series is 'smi_plans' time_series_run /
    #   kinetics_run, which records the time of each frame into the data:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("beam_damage", dets=[pil900KW], t=exp_time, num=it, delay=sleep_time)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the module-level 'det' uses retired 'pil300KW' — switch to
    #   'pil900KW' (see ⚠️ near the top); (2) 'det_exposure_time(...)' no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (Heads-up for a human: this function refers to 'exp_t'/
    #   'meas_t' which aren't its arguments, and uses the removed 'np.int' — pre-existing issues.)
    # === end smi_plans note ================================================
    it = np.int(meas_time / (exp_time + sleep_time))
    det_exposure_time(exp_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, meas_t)  — or at the prompt:  RE(det_exposure_time(exp_t, meas_t)). (smi_plans' time_series_run sets it for you via t=.)
    yield from bp.count(det, num=it, delay=sleep_time)


# TODO: Try this function
def scan_fil_height(exp_time, rang, nb_point):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sweeps the hexapod y (filament/film height) over a range and takes an image
    #   at each step — a height map of the printed filament.
    # 💡 NEWER, EASIER WAY: a height sweep like this is a 'smi_plans' line map (map_line_run) or a
    #   motor_axis over stage.y, which records the y position into the data:
    #     from smi_plans import map_line_run, motor_axis
    #     yield from map_line_run("fil_height", dets=[pil900KW], t=exp_time,
    #                             axes=[motor_axis("stage_y", stage.y, np.linspace(-rang, rang, nb_point))])
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the module-level 'det' uses retired 'pil300KW' — switch to
    #   'pil900KW' (see ⚠️ near the top); (2) 'det_exposure_time(...)' no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (Heads-up for a human: 'point' isn't defined here —
    #   it's probably meant to be 'nb_point'; pre-existing issue.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)).
    yield from bp.rel_scan(det, stage.y, -rang, rang, point)

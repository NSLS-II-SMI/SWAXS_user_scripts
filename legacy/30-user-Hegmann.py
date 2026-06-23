names = ["PB219_60psi_v0p5"]

height = 0.1  # mm shift from the nozzle this is half the filament width, which we call h in the name


# waxs arc angle: 0 for the detector centered and 6 for the detctor at 6 degrees
# Do not enter a value
waxs_arc = 8

# pil300KW for waxs, pil2M for saxs
det = [pil2M]

import sys
import time


def saxs_hegmann_gird(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping run — for each printed sample it drives to
    #   position and rasters a grid of x/y spots, taking a SAXS image at each (a map across
    #   the printed structure).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that builds
    #   the position grid for you and records the position + beam into each saved image (no
    #   hand-built grid ranges or "{sam}_1.6m_16.1keV" names):
    #
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run("HP24_vessel", x_center=11200, y_center=-1000,
    #                             x_size=1000, y_size=1000, x_num=42, y_num=251,
    #                             dets=[pil2M], t=t)
    #     # (call it per sample, the way you loop below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================

    # yield from bps.mv(stage.th, 3)
    # yield from bps.mv(stage.y, -12)
    # names = ['HP09']
    # xlocs = [ 30090]
    # ylocs = [ 7490]
    # zlocs = [ -3800]
    # x_range=[ [0, 500, 21]]
    # y_range=[ [0, 400, 126]]

    names = ["HP24_vessel", "HP26_vessel", "HP25_platform"]
    xlocs = [11200, 10700, 22800]
    ylocs = [-1000, -9500, -9600]
    zlocs = [-5000, -5000, -5000]
    stage_y = [0, 0, -7]
    x_range = [[0, 1000, 42], [0, 1000, 42], [0, 0, 1]]
    y_range = [[0, 1000, 251], [0, 1000, 251], [0, 6400, 641]]

    # names = ['HP09_pos2']
    # xlocs = [32284]
    # ylocs = [5560]
    # zlocs = [-3500]
    # x_range=[ [0, 990, 33]]
    # y_range=[ [0, 500, 101]]

    user = "MP"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(names)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(ylocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(zlocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(x_range)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(y_range)})"

    # Detectors, motors:
    dets = [pil2M]

    for x, y, sample, x_r, y_r, sta_y in zip(
        xlocs, ylocs, names, x_range, y_range, stage_y
    ):
        yield from bps.mv(stage.y, sta_y)
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        name_fmt = "{sam}_1.6m_16.1keV"
        sample_name = name_fmt.format(sam=sample)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.rel_grid_scan(
            dets, piezo.y, *y_r, piezo.x, *x_r, 0
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def saxs_hegmann_grid2(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping run — per sample, drives to position and rasters a
    #   grid of x/y spots, taking a SAXS image at each.
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the grid for you and records position + beam
    #   into each image:
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run("HP12_3rd", x_center=23784, y_center=-4500, x_size=800,
    #                             y_size=..., x_num=5, y_num=..., dets=[pil2M], t=t)
    #   (Your script below still works as-is, except the ⚠️ lines.) (internal: Tier 2.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls must be run as a plan
    #   (see the ⚠️ notes below).
    # === end smi_plans note ================================================

    names = ["HP12_3rd", "HP12_2nd", "HP13_3rd", "HP14_2nd", "HP14_3rd"]
    xlocs = [23784, 23584, 23584, 16284, 16284]
    ylocs = [-4500, -900, 1500, -3700, -100]
    zlocs = [2700, 2700, 2700, 2700, 2700]
    x_range = [[0, 800, 5], [0, 800, 5], [0, 800, 5], [0, 800, 5], [0, 800, 5]]
    y_range = [[0, 400, 11], [0, 400, 11], [0, 400, 11], [0, 400, 11], [0, 400, 11]]

    user = "MP"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(names)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(ylocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(zlocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(x_range)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(y_range)})"

    # Detectors, motors:
    dets = [pil2M]

    for x, y, sample, x_r, y_r in zip(xlocs, ylocs, names, x_range, y_range):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        name_fmt = "{sam}_5m_16.1keV"
        sample_name = name_fmt.format(sam=sample)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.rel_grid_scan(
            dets, piezo.y, *y_r, piezo.x, *x_r, 1
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def saxs_hegmann(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping run — per sample, drives to position and rasters a
    #   grid of x/y spots, taking a SAXS image at each.
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the grid for you and records position + beam
    #   into each image:
    #     from smi_plans import map_grid_run
    #     # map_grid_run(sample, x_center=..., y_center=..., x_size=..., y_size=...,
    #     #              x_num=..., y_num=..., dets=[pil2M], t=t)
    #   (Your script below still works as-is, except the ⚠️ lines.) (internal: Tier 2.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls must be run as a plan
    #   (see the ⚠️ notes below).
    # === end smi_plans note ================================================
    # xlocs = [38200, 38400, 32800, 32800, 29400, 27300, 20400, 20400, 8400, 8400, -18500, 24800, -34200, -39550, 43000, 36300]
    # ylocs = [-5500, -4500, -5500, -4500, -4500, -4500, -4900, -4800, -4800, -4700, -4900, -4700, -4700, -5980, 7500, 7900]

    # names = ['PB180_vert_1', 'PB180_vert_2', 'PB181_vert_1','PB181_vert_2','PB182_vert', 'PB187_vert', 'PB180_trans_1',
    # 'PB180_trans_2','PB181_trans_1','PB181_trans_2', 'PB190_vert', 'PB190_trans','PB196_vert','PB196_trans','PB195_vert',
    # 'PB195_trans']

    xlocs = [
        -24800,
    ]
    ylocs = [-4700]

    names = [
        "PB190_trans",
    ]

    user = "MP"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil2M]

    for sam, x, y in zip(names, xlocs, ylocs):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        name_fmt = "16p1keV_micro_sdd3p2_{sam}"
        sample_name = name_fmt.format(sam=sam)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


def track_printer_hegmann(acq_t=1, full_meas_t=10, trigger_num=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ 3D-printing measurement — it watches the printer's trigger
    #   signal (an EPICS PV) and, each time the printer fires, triggers a detector
    #   acquisition on the freshly-printed filament, then returns the beam to the nozzle.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', built for
    #   exactly this printer-synchronised measurement. It waits for the printer's fire signal
    #   and takes the shot for you, recording everything into a proper data run:
    #     from smi_plans import printer_triggered_run, wait_for_printer_fire, beam_to_filament_middle
    #     # printer_triggered_run(...) arms on the trigger and acquires when the printer fires;
    #     # beam_to_filament_middle positions the beam on the new filament for you.
    #
    #   Nothing here is broken (GV7, stage.y, the EPICS trigger PVs all still work). This is
    #   purely a "there's a purpose-built helper now" note. (internal: Tier 0 — this drives
    #   the detector by hand and busy-waits; smi_plans would record the run for you.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)

    if waxs.arc.position < 6 and waxs.x.position > -15:
        sys.exit("You moved waxs arc and not waxs ")

    if waxs.arc.position < 7.5:
        sys.exit("waxs is on the way ")

    monitor_pv = EpicsSignal("XF:11ID-CT{M1}bi2", name="monitor_pv")
    ready_for_trigger_pv = EpicsSignal("XF:11ID-CT{M1}bi3", name="ready_for_trigger_pv")
    trigger_signal_pv = EpicsSignal("XF:11ID-CT{M1}bi4", name="trigger_signal")

    trigger_count = 0
    while monitor_pv.get() == 1:
        if trigger_signal_pv.get() == 1:  # trigger signal to execute
            print('this is "function_triggered"! \nGoing to trigger detector...')

            trigger_count += 1

            # Set the sample name
            experimental_adjustement()

            # define the acquisition time and measurment time
            yield from data_acquisition(acq_t, full_meas_t)

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
    yield from bps.mvr(stage.y, height)

    yield from bps.mv(GV7.close_cmd, 1)
    print("Done")


def height_scan(ran=3 * height, nb_step=50, acq_time=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: scans the beam height (stage.y) across the printed filament in nb_step
    #   steps, taking a SAXS image at each — to find how scattering varies with height.
    # 💡 NEWER, EASIER WAY: a height/line scan like this is map_line_run in 'smi_plans', which
    #   records the height + beam into each image (no hand-built "{sample}_height{}"):
    #     from smi_plans import map_line_run
    #     # map_line_run(names[0], axis="y", center=..., size=ran, num=nb_step, dets=[pil2M])
    #   (Your script below still works as-is; the printer GV7/stage.y are fine.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)
    hei_ini = stage.y.position

    if ran > 4 * height:
        sys.exit("Range is too big ")

    # define the acquisition time and measurment time
    yield from data_acquisition(acq_time, acq_time)

    hei = np.linspace(stage.y.position - ran, stage.y.position, nb_step)

    print(hei)

    for i, he in enumerate(hei):
        yield from bps.mv(stage.y, he)
        name_fmt = "{sample}_height{h:4.3f}"
        sample_name = name_fmt.format(sample=names[0], h=he)
        sample_id(user_name="MP", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=1)

    yield from bps.mv(stage.y, hei_ini)

    yield from bps.mv(GV7.close_cmd, 1)
    print("Done")


def experimental_adjustement():
    # smi_plans: no acquisition here — just sets the file name (sample_id). smi_plans builds
    # the file name from the recorded data instead, so a helper like this isn't needed.
    # TODO: What do we want to put in the filename
    name_fmt = "{sample}"

    sample_name = name_fmt.format(sample=names[0])
    sample_id(user_name="MP", sample_name=sample_name)


def sample_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the beam height to the substrate/film interface, then moves to
    #   the middle of the film, switching the beamline between alignment and measurement modes.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' this kind of alignment is done with align_sample,
    #   which finds the interface AND saves the result with the data (so downstream plans and
    #   the file name can use it) — instead of doing it by hand each run:
    #     from smi_plans import align_sample
    #   Nothing here is broken (GV7, waxs, stage.y all work). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)
    # Prepare SMI for alignement (BS and waxs det movement)
    sample_id(user_name="test", sample_name="test")
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    yield from smi.setDirectBeamROI()
    if waxs.arc.position < 6:
        yield from bps.mv(waxs, 6)

    # move to the substrate interface
    yield from align_height_hexa(0.40, 30, der=True)

    # Move the beam to the middle of the film
    yield from bps.mvr(stage.y, -height)

    # Return to measurment configuration (BS and waxs det movement)
    yield from bps.mv(waxs, waxs_arc)
    yield from smi.modeMeasurement()
    yield from bps.mv(GV7.close_cmd, 1)


def align_height_hexa(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small alignment scan of the sample height (stage.y) to find the peak/
    #   edge, then moves there. Used by the alignment routines above.
    # 💡 smi_plans: this peak/edge find + move is built into align_sample, which also saves
    #   the result with the data. (Your script still works, except the ⚠️ line.) (Tier 1.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan (see
    #   the ⚠️ note below).
    # === end smi_plans note ================================================
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_scan([pil2M], stage.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(stage.y, ps.cen)
    plt.close("all")


def align_x_hexa(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small alignment scan of the sample x (e.g. to find the nozzle center).
    # 💡 smi_plans: alignment scans + move-to-peak are handled by align_sample, which saves
    #   the result with the data. (Your script still works, except the ⚠️ line.) (Tier 1.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan (see
    #   the ⚠️ note below).
    # === end smi_plans note ================================================
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_scan([pil2M], stage.x, -rang, rang, point)
    # yield from bps.mv(stage.y, ps.cen)


def data_acquisition(acq_t, meas_t):
    """
    acq_t: Acquisition time, i.e. the time of acquisition for 1 image
    meas_t: Measurment time, i.e. the total acquisition time of the whole scan
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small acquisition helper used by the printer tracking — it takes a
    #   series of images at one spot for a total of meas_t seconds (acq_t per image).
    # 💡 NEWER, EASIER WAY: repeating shots over a fixed time is the 'smi_plans' time-series
    #   idea, which records elapsed time + beam into each image:
    #     from smi_plans import time_series_run
    #     # time_series_run(name, duration=meas_t, dets=[pil2M], t=acq_t)
    #   (Your script below still works as-is, except the ⚠️ line.) (internal: Tier 0/1.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan
    #   (see the ⚠️ note below).
    # === end smi_plans note ================================================

    det_exposure_time(acq_t, acq_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    nb_scan = np.int((meas_t / acq_t))

    yield from bp.scan(det, piezo.x, 0, 0, nb_scan)


def nozzle_alignment():
    """
    Alignement of the height to the substrate film interface
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the beam to the center of the printer nozzle, switching the
    #   beamline between alignment and measurement modes.
    # 💡 smi_plans: alignment like this is done with align_sample (which saves the result),
    #   and beam_to_filament_middle positions the beam for printing measurements. Nothing here
    #   is broken (waxs, GV7 work). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample_id(user_name="test", sample_name="test")

    # yield from bps.mv(GV7.open_cmd, 1)
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    if waxs.arc.position < 6:
        yield from bps.mv(waxs, 6)

    yield from smi.setDirectBeamROI()

    # Find the center of the nozzle
    yield from align_x_hexa(1, 45, der=False)

    if waxs.arc.position > 5:
        yield from bps.mv(waxs, waxs_arc)

    yield from smi.modeMeasurement()
    # yield from bps.mv(GV7.close_cmd, 1 )


def ex_situ_hegmann(meas_t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ SAXS measurement over a list of sample x positions (printed
    #   structures measured off-line, away from the printer).
    # 💡 NEWER, EASIER WAY: 'smi_plans' has bar/transmission helpers that visit your positions
    #   and record position + beam into each image:
    #     from smi_plans import transmission_bar, SampleList
    #   (Your script below still works as-is, except any ⚠️ lines.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    x_list = [
        26400,
        18200,
        12900,
        3900,
        -6500,
        -7100,
        -16100,
        -23700,
        -24200,
        -31700,
        -32400,
        -37500,
        -36800,
    ]
    sample_list = [
        "PL037",
        "PL038",
        "PL017",
        "PL031",
        "PL009_kapton",
        "PL009",
        "PL032",
        "PL022_kapton",
        "PL022",
        "PL026_kapton",
        "PL026",
        "PL043_kapton",
        "PL043",
    ]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    waxs_arc = [0, 26, 5]
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

        name_fmt = "{sample}"
        sample_name = name_fmt.format(sample=sample)
        sample_id(user_name="EH", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.scan(dets, waxs, *waxs_arc)


def ex_situ_xscan_hegmann(meas_t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ SAXS x-scan — for each sample it scans a range of x positions
    #   and takes images, mapping across the printed structure off-line.
    # 💡 NEWER, EASIER WAY: a line scan in x is map_line_run in 'smi_plans', which records the
    #   position + beam into each image:
    #     from smi_plans import map_line_run
    #   (Your script below still works as-is, except any ⚠️ lines.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    x_list = [
        [-28500, -27680],
        [-23080, -21480],
        [-18180, -16180],
        [-10880, -10180],
        [-6280, -5580],
        [-1080, -380],
        [8620, 9520],
        [12220, 12820],
        [17420, 18120],
        [23520, 24220],
        [27420, 28220],
        [35820, 36820],
        [39920, 40820],
        [45120, 45820],
    ]
    sample_list = [
        "PL131_fromleft",
        "PL075_fromleft",
        "PL12_fromleft",
        "PL11_fromleft",
        "PL10_fromleft",
        "PL9_fromleft",
        "PL8_fromleft",
        "PL7_fromleft",
        "PL6_fromleft",
        "PL5_fromleft",
        "PL4_fromleft",
        "PL3_fromleft",
        "PL2_fromleft",
        "PL1_fromleft",
    ]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    waxs_arc = np.linspace(0, 26, 5)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for waxs_a in waxs_arc:
        yield from bps.mv(waxs, waxs_a)
        for x, sample in zip(x_list, sample_list):  # loop over samples on bar
            print("x", x)
            print("div", abs(x[-1] - x[0]) / 100)
            x_meas = np.linspace(x[0], x[-1], int(abs(x[-1] - x[0]) / 50))
            print("xm", x_meas)
            for x_me in x_meas:

                yield from bps.mv(piezo.x, x_me)
                det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

                name_fmt = "{sample}_x{x:5.0f}_waxs{waxs:3.1f}"
                sample_name = name_fmt.format(sample=sample, x=x_me, waxs=waxs_a)
                sample_id(user_name="EH", sample_name=sample_name)

                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)


def ex_situ_xscan_hegmann1(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ SAXS/WAXS x-scan at a couple of positions while also sweeping
    #   the WAXS detector arc.
    # 💡 NEWER, EASIER WAY: 'smi_plans' can sweep position and WAXS arc as "axes" and record
    #   them into the data (map_line_run for x, motor_axis on waxs for the arc).
    #   (Your script below still works as-is, except any ⚠️ lines.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = "PL076_exsitu_xscan"
    x = [36200, 36800]

    waxs_arc = np.linspace(0, 13, 3)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for waxs_a in waxs_arc:
        yield from bps.mv(waxs, waxs_a)
        for k, xs in enumerate(np.linspace(x[0], x[1], 13)):
            yield from bps.mv(piezo.x, xs)
            name_fmt = "{sample}_spot{sp}_waxs{waxs}"
            sample_name = name_fmt.format(
                sample=sample, sp="%2.2d" % (k + 1), waxs="%3.1f" % waxs_a
            )
            sample_id(user_name="MP", sample_name=sample_name)

            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def saxs_hegmann_grid_2021_2(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS micro-mapping run (2021-2) — per sample, drives to position and
    #   rasters a grid of x/y spots, taking a SAXS image at each.
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the grid for you and records position + beam
    #   into each image:
    #     from smi_plans import map_grid_run
    #   (Your script below still works as-is, except any ⚠️ lines.) (internal: Tier 2.)
    # === end smi_plans note ================================================

    # names = ['alpha_6arms_L_lac_microtomed', 'gama_Br_PEG_doublelayer_microtomed']
    # xlocs = [       -22160,         24540]
    # ylocs = [         6940,          6880]
    # zlocs = [        -1200,         -1200]
    # x_range=[ [0, 600, 21],  [0, 600, 21]]
    # y_range=[[0, 342, 115], [0, 381, 128]]

    # names = ['HP_mod_hori',  'HP_mod_vert',  'HP_mod_faceon']
    # xlocs = [        10400,          9850,             3600]
    # ylocs = [         -747,          -9400,            -5800]
    # zlocs = [        2500,            2500,             2500]
    # x_range=[ [0, 600, 21],  [0, 1350, 46],     [0, 450, 16]]
    # y_range=[[0,  800, 81],  [0,  120, 41],    [0, 700, 141]]

    # names = ['olymp_grid']
    # xlocs = [       35400]
    # ylocs = [        -3600]
    # zlocs = [        2500]
    # x_range=[ [0, 600, 21]]
    # y_range=[[0,  400, 41]]

    names = ["olymp_model_cross_sec"]
    xlocs = [-14500]
    ylocs = [-3220]
    zlocs = [2500]
    x_range = [[0, 600, 21]]
    y_range = [[0, 600, 201]]

    user = "MP"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(names)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(ylocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(zlocs)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(x_range)})"
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(xlocs)}) is different from number of samples ({len(y_range)})"

    # Detectors, motors:
    dets = [pil2M]

    for x, y, sample, x_r, y_r in zip(xlocs, ylocs, names, x_range, y_range):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        name_fmt = "{sam}_1.6m_16.1keV"
        sample_name = name_fmt.format(sam=sample)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.rel_grid_scan(
            dets, piezo.y, *y_r, piezo.x, *x_r, 0
        )  # 1 = snake, 0 = not-snake

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

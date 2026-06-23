from yaml import scan
from epics import caget, caput


def set_nozzle_0():
    # smi_plans: setup/bookkeeping helper (records the printer-nozzle "zero" reference in
    # metadata) — no acquisition here, nothing to migrate.
    RE.md["nozzle 0"] = [printer.y_bed.user_readback.value, stage.y.user_readback.value]


def get_nozzle_height():
    # smi_plans: no acquisition logic here — just computes the nozzle height vs its zero.
    h = printer.y_bed.user_readback.value - RE.md["nozzle 0"][0]
    return h


def set_platform_0():
    # smi_plans: setup/bookkeeping helper (records the print-platform "zero") — nothing to migrate.
    RE.md["platform 0"] = [
        printer.y_bed.user_readback.value,
        stage.y.user_readback.value,
    ]


def get_platform_height():
    # smi_plans: no acquisition logic here — just computes the platform height vs its zero.
    h1 = RE.md["platform 0"][0] - printer.y_bed.user_readback.value
    h2 = RE.md["platform 0"][1] - stage.y.user_readback.value
    h = h1 + h2
    return h


def set_nozzle_height(height):
    # smi_plans: setup helper (drives the printer bed + sample y to a nozzle height) —
    # nothing to migrate; runs the moves with RE(...), so not usable with 'yield from'.
    RE(mv(printer.y_bed, RE.md["nozzle 0"][0] - height))
    RE(mvr(stage.y, height))
    RE.md["nozzle height"] = height


def get_nozzle_height():
    # smi_plans: no acquisition logic here — just reads back the nozzle height.
    return RE.md["nozzle 0"][0] - printer.y_bed.user_readback.value


def set_beam_height(bheight):
    # smi_plans: setup helper (drives sample y so the beam sits at a chosen height on the
    # print) — nothing to migrate; runs the move with RE(...).
    curr_height = get_platform_height()
    RE(mvr(stage.y, curr_height - bheight))
    RE.md["beam height"] = get_platform_height()


def set_beam_position(beam_x):
    """
    beam_x (float): >0 move to the right (upstream)
                    <0 move to the left (downstream)
    """
    # smi_plans: setup helper (drives sample x so the beam hits a chosen spot on the print)
    # — nothing to migrate; runs the move with RE(...).
    curr_position = RE.md["nozzle_x 0"]
    RE(mv(stage.x, beam_x - curr_position))
    RE.md["beam_x"] = beam_x - curr_position


def set_nozzle_position_0():
    # smi_plans: setup/bookkeeping helper (records the nozzle x "zero") — nothing to migrate.
    RE.md["nozzle_x 0"] = stage.x.user_readback.value


def get_nozzle_position():
    # smi_plans: no acquisition logic here — just computes the nozzle x vs its zero.
    return stage.x.user_readback.value - RE.md["nozzle_x 0"]


def set_nozzle_position(nozzle_x):
    # smi_plans: setup helper (drives sample x to a nozzle position) — nothing to migrate;
    # runs the move with RE(...).
    RE(mv(stage.x, -(RE.md["nozzle_x 0"] - nozzle_x)))
    RE.md["nozzle_x"] = get_nozzle_position()


from ophyd import (
    EpicsMotor,
    PVPositioner,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    PVPositionerPC,
)
from ophyd import Component as Cpt, FormattedComponent, DynamicDeviceComponent as DDC


class Printer_3D(Device):
    """6 axes for 1st gen 3D printer"""

    z_bed = Cpt(EpicsMotor, "Z_bed}Mtr")
    x_bed = Cpt(EpicsMotor, "X_bed}Mtr")
    y_bed = Cpt(EpicsMotor, "Y_bed}Mtr")
    x_head1 = Cpt(EpicsMotor, "X_head1}Mtr")
    x_head2 = Cpt(EpicsMotor, "X_head2}Mtr")
    y_head1 = Cpt(EpicsMotor, "Y_head1}Mtr")


printer = Printer_3D("XF:11IDM2-3D{3D:", name="printer")


def start_acq(dt=0.1, t=5, name="test", sleep=0):
    """
    Start taking images after delay

    Args:
        dt (float): exposure per frame in seconds,
        t (float): total exposure time for all frames, in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between start of the script and data
            aquisition.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: after an optional delay, takes a burst of WAXS frames of the print and
    #   names the file from the energy / WAXS-arc angle / scan id.
    #
    # 💡 NEWER, EASIER WAY: in-situ printing has its own 'smi_plans' helper. printer_triggered_run
    #   collects frames in sync with the printer and records the print/energy/WAXS info into
    #   each image and file name for you (so you can drop the hand-built name and the scan-id
    #   bookkeeping):
    #     from smi_plans import printer_triggered_run
    #     yield from printer_triggered_run("test", [pil900KW], dt=dt, t=t)
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(dt, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(dt, t)  — or at the prompt:  RE(det_exposure_time(dt, t)). (smi_plans' printer_triggered_run sets it for you via dt=/t=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)

    scan_id = db[-1].start["scan_id"] + 1
    name_fmt = "{sample}_{energy}keV_wa{wax}_id{scan_id}"
    sample_name = name_fmt.format(
        sample=name, energy="%.1f" % e, wax=wa, scan_id=scan_id
    )

    sample_name = sample_name.translate(
        {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
    )
    sample_id(user_name=user_name, sample_name=sample_name)

    yield from bps.sleep(sleep)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def start_acq_long(dt=0.1, name="test", sleep=0):
    """
    Start taking single images every x seconds

    Press CTRL + C to stop the measurement, then RE.stop() in BlueSky.

    Args:
        dt (float): exposure per frame in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between each image.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one WAXS image every few seconds (up to 500 of them), labeling
    #   each with the elapsed time, so you watch a print evolve over time.
    #
    # 💡 NEWER, EASIER WAY: this "single image on a timer, labeled with elapsed time" loop is
    #   the 'smi_plans' time-series/kinetics pattern; it timestamps each frame into the data
    #   and file name for you:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("test", [pil900KW], t=dt, num=500, period=sleep)
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(dt, dt)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(dt, dt)  — or at the prompt:  RE(det_exposure_time(dt, dt)). (smi_plans' time_series_run sets it for you via t=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)
    t0 = time.time()

    for i in range(500):

        t1 = time.time()
        td = str(np.round(t1 - t0, 1)).zfill(6)
        scan_id = db[-1].start["scan_id"] + 1

        name_fmt = "{sample}_time{td}s_{energy}keV_wa{wax}_id{scan_id}"
        sample_name = name_fmt.format(
            sample=name, td=td, energy="%.1f" % e, wax=wa, scan_id=scan_id
        )
        sample_name = sample_name.translate(
            {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
        )
        sample_id(user_name=user_name, sample_name=sample_name)

        yield from bps.sleep(sleep)
        yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def triggered_series(dt=0.1, t=5, name="test_print", sleep_=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: waits for the 3D printer to "fire" (it polls an EPICS trigger signal in
    #   a loop until it goes high), clears the trigger, then starts a burst of WAXS images.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has exactly this for printing. wait_for_printer_fire
    #   waits for the printer's trigger as a normal plan step, and printer_triggered_run does
    #   the whole "wait for fire, then collect" in one go — recording the print/energy info
    #   into each image and file name for you:
    #     from smi_plans import printer_triggered_run, wait_for_printer_fire
    #     yield from wait_for_printer_fire()          # waits for the printer trigger
    #     yield from printer_triggered_run("test_print", [pil900KW], dt=dt, t=t)
    #
    # 💡 HEADS-UP (not broken): this polls with caget(...) and runs the burst with
    #   RE(start_acq(...)) inside the function, so it can't itself be 'yield from'-ed or run
    #   with RE(...). The smi_plans versions are plans you 'yield from', so the wait + collect
    #   compose into one runnable plan. (Nothing here errors.) (internal: Tier 0.)
    # === end smi_plans note ================================================
    look_for_trigger = True
    print("waiting for trigger signal")
    while look_for_trigger:
        if caget("XF:11ID-CT{M3}bi2") < 1:
            RE(sleep(0.5))
        else:
            look_for_trigger = False
    caput("XF:11ID-CT{M3}bi2", 0)
    RE(start_acq(dt, t, name, sleep_))


"""EXP 1 - W/IN NOZZLE SECTION"""


def through_nozzle_exp():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: maps the flow inside the nozzle — rasters a height x width grid over
    #   the capillary section, then another over the tapered section, taking a WAXS image at
    #   each point.
    #
    # 💡 NEWER, EASIER WAY: a height x width raster is the 'smi_plans' mapping pattern; map_grid_run
    #   sweeps the grid and records the x/y position into each image and file name (so you can
    #   drop the manual nested loops and hand-built names). For printing-in-progress it pairs
    #   with the printer helpers (printer_triggered_run / print_crystallization_followup_run):
    #     from smi_plans import map_grid_run, map_dets
    #     # capillary section:
    #     yield from map_grid_run("capillary", map_dets(use_waxs=True),
    #         y=(start_y, end_y, 13), x=(start_x, end_x, 7))   # your height/width grid
    #     # ...then the tapered section similarly...
    #   (Just a tidier option — your script works as-is; nothing here is broken. Note the data
    #    is taken inside start_acq_through_nozzle, where the ⚠️ exposure issue lives.) (Tier 1.)
    # === end smi_plans note ================================================
    # d_N = 0.222 # "250" um nozzle

    # CAPILLARY SECTION
    radial_resolution = 0.07  # 0.025 for 250um nozzle, 0.07 for 700um nozzle
    height_resolution = 0.10  # 100 um

    height_list = [v * height_resolution for v in range(0, 13)]
    width_list = [v * radial_resolution for v in range(0, 7)]
    exp_time = 0.2  # 0.5 for 250um
    # yield from set_beam_height(0)
    t0 = time.time()
    for h_i in height_list:
        print("moving height to ", h_i, type(h_i))
        yield from bps.mvr(stage.y, -height_resolution)

        for w_j in width_list:
            # - = left, + = right
            x_i = RE.md["nozzle_x 0"] - w_j
            print("moving to x=", x_i)
            yield from bps.mv(stage.x, x_i)
            yield from start_acq_through_nozzle(x_i, h_i, "capillary", exp_time)

    print(f"capillary took {t0 - time.time():.3f} seconds long")

    # TAPERED SECTION
    radial_resolution = 0.1  # 25um
    height_resolution = 0.4  # 100 um

    height_list = [v * height_resolution for v in range(0, 8)]
    width_list = [v * radial_resolution for v in range(0, 13)]

    # yield from set_beam_height(0)
    exp_time = 0.2
    t0 = time.time()
    for h_i in height_list:
        print("moving height to ", h_i, type(h_i))
        yield from bps.mvr(stage.y, -height_resolution)

        for w_j in width_list:
            # - = left, + = right
            x_i = RE.md["nozzle_x 0"] - w_j
            print("moving to x=", x_i)
            yield from bps.mv(stage.x, x_i)
            yield from start_acq_through_nozzle(x_i, h_i, "tapered", exp_time)

    print(f"taper took {t0 - time.time():.3f} seconds long")


def start_acq_through_nozzle(x_i, y_i, section, exp_time):
    """
    Start taking images after delay

    Args:
        dt (float): exposure per frame in seconds,
        t (float): total exposure time for all frames, in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between start of the script and data
            aquisition.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the inner worker for through_nozzle_exp — takes one WAXS image at the
    #   current (x, y) inside the nozzle and names the file from the position/section/scan id.
    # 💡 In 'smi_plans' the x/y position is recorded into each image and templated into the
    #   file name by the mapping run (map_grid_run), so this hand-built name and per-point
    #   call go away. (See through_nozzle_exp's note.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' printer_triggered_run sets it for you via t=/dt=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)

    scan_id = db[-1].start["scan_id"] + 1
    sample_name = f"win_nozzle_wa{wa}_x{x_i:.3f}_y{y_i:.3f}_{section}_id{scan_id}_exp{exp_time:.2f}"

    sample_name = sample_name.translate(
        {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
    )
    sample_id(user_name=user_name, sample_name=sample_name)

    # yield from bps.sleep(0)
    yield from bp.count(dets)

    # ensures no overwrite data
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


"""EXP - TIME RESOLVED UNDER BEAM"""


def start_printing_below_nozzle(H, beam_x, dt=0.2, t=5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sets the nozzle to height H above the substrate, then starts a timed
    #   series of WAXS images watching the deposited material just below the nozzle. (The
    #   trigger-wait part is commented out here.)
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the height move is a normal plan step and the
    #   collection is printer_triggered_run / print_crystallization_followup_run (which
    #   follows the print over time and records the metadata for you):
    #     from smi_plans import printer_triggered_run
    #     # set the nozzle height as you do, then:
    #     yield from printer_triggered_run("below_nozzle", [pil900KW], dt=dt, t=t)
    # 💡 HEADS-UP (not broken): this runs the collection with RE(start_acq_below_nozzle(...))
    #   inside the function, so it can't itself be 'yield from'-ed. (internal: Tier 0.)
    # === end smi_plans note ================================================

    assert H > 0

    # assumes print always starts with nozzle on substrate
    set_nozzle_height(H)
    # set_beam_height(-0.3375)
    # set_beam_position(beam_x)
    # RE(sleep(0.5)) # enough time to start deposition macro

    look_for_trigger = True
    # print('waiting for trigger signal')
    # while look_for_trigger:
    #     if caget('XF:11ID-CT{M3}bi2') <1:
    #         RE(sleep(.5))
    #     else: look_for_trigger=False

    # caput('XF:11ID-CT{M3}bi2',0)
    RE(start_acq_below_nozzle(dt, t))


def start_acq_below_nozzle(exp_time, N_imgs, dwell=0):
    """
    Start taking images after delay

    Args:
        dt (float): exposure per frame in seconds,
        t (float): total exposure time for all frames, in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between start of the script and data
            aquisition.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes N WAXS images of the print just below the nozzle over time,
    #   labeling each with elapsed time, beam height, and nozzle height.
    # 💡 NEWER, EASIER WAY: this time-resolved print follow-up is the 'smi_plans'
    #   print_crystallization_followup_run / printer_triggered_run (or time_series_run for a
    #   plain timed series); they record time/height/beam into each image and file name:
    #     from smi_plans import print_crystallization_followup_run
    #     yield from print_crystallization_followup_run("below_nozzle", [pil900KW],
    #                                                   t=exp_time, num=N_imgs, period=dwell)
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' printer_triggered_run sets it for you via t=/dt=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)
    t0 = time.time()

    for j in range(N_imgs):
        t1 = time.time()
        scan_id = db[-1].start["scan_id"] + 1
        beam_height = RE.md["beam height"]
        nozzle_height = get_nozzle_height()
        beam_x = RE.md["beam_x"]
        td = str(np.round(t1 - t0, 1)).zfill(6)

        print("beam_x", beam_x, type(beam_x))
        # print()
        # sample_name = f'below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_bx{beam_x:3.4f}_nh{get_nozzle_height:3.3f}mm'
        sample_name = f"below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_nh{nozzle_height:3.3f}mm_t{td}"
        print(sample_name)

        sample_name = sample_name.translate(
            {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
        )
        sample_id(user_name=user_name, sample_name=sample_name)

        yield from bps.sleep(dwell)
        yield from bp.count(dets)

    # ensures no overwrite data
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


"""EXP 2 - ACROSS BEAM"""


def start_acq_across_beam(exp_time, N_imgs, dwell=0):
    """
    Start taking images after delay

    Args:
        dt (float): exposure per frame in seconds,
        t (float): total exposure time for all frames, in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between start of the script and data
            aquisition.
    For SAXS data, add pil2M detector to dets
    dets = [pil900KW] if waxs.arc.position < 10 else [pil2M, pil900KW]

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes N WAXS images as the printed material passes across the beam over
    #   time, labeling each with elapsed time and beam/nozzle heights.
    # 💡 NEWER, EASIER WAY: same 'smi_plans' time-resolved print pattern
    #   (print_crystallization_followup_run / printer_triggered_run / time_series_run); it
    #   records time/height/beam into each image and file name. To also collect SAXS when the
    #   WAXS arc is out of the way, pass both detectors (the docstring above shows the idea).
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' printer_triggered_run sets it for you via t=/dt=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)
    t0 = time.time()

    for j in range(N_imgs):
        t1 = time.time()
        scan_id = db[-1].start["scan_id"] + 1
        beam_height = RE.md["beam height"]
        nozzle_height = get_nozzle_height()
        beam_x = RE.md["beam_x"]
        td = str(np.round(t1 - t0, 1)).zfill(6)

        print("beam_x", beam_x, type(beam_x))
        # print()
        # sample_name = f'below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_bx{beam_x:3.4f}_nh{get_nozzle_height:3.3f}mm'
        sample_name = f"acrossBeam_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_nh{nozzle_height:3.3f}mm_t{td}"
        print(sample_name)

        sample_name = sample_name.translate(
            {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
        )
        sample_id(user_name=user_name, sample_name=sample_name)

        yield from bps.sleep(dwell)
        yield from bp.count(dets)

    # ensures no overwrite data
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


"""EXP 3 - DOWNSTREAM OF NOZZLE"""


def start_acq_downstream_nozzle(exp_time, N_imgs, distance=0, dwell=0):
    """
    Start taking images after delay

    Args:
        dt (float): exposure per frame in seconds,
        t (float): total exposure time for all frames, in seconds,
        name (str): sample name,
        sleep (float): delay in seconds between start of the script and data
            aquisition.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes N WAXS images downstream of the nozzle over time, labeling each
    #   with elapsed time and beam/nozzle heights.
    # 💡 NEWER, EASIER WAY: same 'smi_plans' time-resolved print follow-up
    #   (print_crystallization_followup_run / printer_triggered_run / time_series_run); the
    #   time/height/beam are recorded into each image and file name for you. (Just a tidier
    #   option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    dets = [pil900KW]
    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' printer_triggered_run sets it for you via t=/dt=.)
    user_name = "RT"
    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 2)).zfill(5)
    t0 = time.time()

    for j in range(N_imgs):
        t1 = time.time()
        scan_id = db[-1].start["scan_id"] + 1
        beam_height = RE.md["beam height"]
        nozzle_height = get_nozzle_height()
        beam_x = RE.md["beam_x"]
        td = str(np.round(t1 - t0, 1)).zfill(6)

        print("beam_x", beam_x, type(beam_x))
        # print()
        # sample_name = f'below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_bx{beam_x:3.4f}_nh{get_nozzle_height:3.3f}mm'
        sample_name = f"below_nozzle_wa{wa}_id{scan_id}_exp{exp_time:.2f}_bh{beam_height:3.3f}mm_nh{nozzle_height:3.3f}mm_t{td}"
        print(sample_name)

        sample_name = sample_name.translate(
            {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
        )
        sample_id(user_name=user_name, sample_name=sample_name)

        yield from bps.sleep(dwell)
        yield from bp.count(dets)

    # ensures no overwrite data
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

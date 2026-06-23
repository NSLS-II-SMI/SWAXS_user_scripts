def run_saxs_lipids(y=1, t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS+WAXS bar — for each sample it moves to the sample's
    #   x/y spot, sets the exposure, and runs a small WAXS-arc + y scan taking an image at each.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library called 'smi_plans' that runs a
    #   multi-sample "bar" like this for you, and writes the position/beam readings straight INTO
    #   each saved image (so you don't have to pack them into the file name by hand). For example:
    #
    #     from smi_plans import transmission_bar, SampleList   # do this once per session
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     yield from transmission_bar("NIST", samples, t=t, dets=[pil2M, pil900KW])
    #       # add the WAXS arc / y sweep as extra axes if you want them per sample
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t)' line no longer sets the exposure unless run as a plan (see the
    #   ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Parameters:
    x_list = [11.4, 7.5, 1.8, -2.17, -11.1]
    samples = [
        "POPC352_A_full",
        "POPC352_A_half",
        "POPC352_B_full",
        "POPC352_B_half",
        "water352",
    ]
    param = "16.1keV"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil2M, pil300KW, ssacurrent]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = [11, 11, 1]
    stage_y = [y, y + 4, 81]

    for x, sample in zip(x_list, samples):
        yield from bps.mv(stage.x, x)
        yield from bps.mv(stage.y, y)
        det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
        sample_id(user_name=sample, sample_name=param)
        # print(RE.md)
        yield from e_grid_scan(dets, waxs, *waxs_arc, stage.y, *stage_y, 0)

    sample_id(user_name="test", sample_name="test")


def move_pos(pos=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick "go to sample N" helper — looks up sample N's x position in your
    #   lists and drives the stage there, then sets the sample id.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you describe your bar ONCE as a SampleList (names +
    #   positions together), then jump to any sample by name and the position/label travel with
    #   the data automatically:
    #     from smi_plans import SampleList, goto_sample
    #     samples = SampleList.from_columns(name=sample_list, x=posx_list)
    #     yield from goto_sample(samples["F2"])     # (goto_sample is a plan: call it with 'yield from')
    #   (Nothing here is broken — this is just a tidier way to keep names and positions in sync.
    #    Note this helper uses stage.x.move(...) directly rather than as a plan, which is fine at
    #    the prompt but won't compose inside a 'yield from' plan.)
    # === end smi_plans note ================================================
    sam = sample_list[pos - 1]
    posx = posx_list[pos - 1]
    print(
        "Move to sample: %s (sample holder position: %s) with posx at: %s."
        % (sam, pos, posx)
    )
    stage.x.move(posx)
    sample_id(user_name=user_name, sample_name=sam)


def fly_scan(det, motor, cycle=1, cycle_t=10, phi=-0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hand-rolled "fly" exposure — it parks the rotation motor at the start,
    #   manually arms the detector and starts one long exposure, then rocks the motor back and
    #   forth between two angles while that single exposure integrates, and waits for it to finish.
    #
    # ⚠️ HEADS-UP (important, even though Python won't error): this routine pokes the detector
    #   DIRECTLY (det.stage(), det.cam.acquire_time.put(...), det.trigger()) and then busy-waits
    #   with 'while not st.done: pass'. Because the trigger happens OUTSIDE Bluesky's RunEngine
    #   (the thing that normally records a "run"), the frames it takes are NOT written into the
    #   data catalog as a proper dataset — there are no start/stop/event "documents", so the
    #   image, the angles, the beam intensity and the timing are not saved together the way every
    #   other scan here saves them. You'd have to dig the raw file off the detector by hand.
    #   The busy-wait also blocks everything else while it spins.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has real fly/monitor-style runs that do this same "expose
    #   while the stage moves" idea but INSIDE the RunEngine, so the image + the rocking angle +
    #   the beam are recorded together automatically. Depending on what you're after, the modern
    #   path is a proper monitored/time-series acquire (e.g. time_series_run / kinetics_run) or a
    #   rocking acquire built with acquire(...) + a motor_axis on the rotation stage — ask staff
    #   which fits, but the key point is to let the RunEngine drive and record it instead of
    #   triggering the camera by hand. (internal: Tier 0.)
    # === end smi_plans note ================================================
    start = phi + 40
    stop = phi - 40
    acq_time = cycle * cycle_t
    yield from bps.mv(motor, start)
    # yield from bps.mv(attn_shutter, 'Retract')
    det.stage()
    det.cam.acquire_time.put(acq_time)
    print(f"Acquire time before staging: {det.cam.acquire_time.get()}")
    st = det.trigger()
    for i in range(cycle):
        yield from list_scan([], motor, [start, stop])
    while not st.done:
        pass
    det.unstage()
    print(f"We are done after {acq_time}s of waiting")
    # yield from bps.mv(attn_shutter, 'Insert')


def grating_rana(det, motor, name="Water_upRepeat", cycle=1, cycle_t=11, n_cycles=20):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a big nested loop — for each temperature, each sample, and each incident
    #   angle it moves the stage into place, takes one image, then runs many hand-rolled "fly"
    #   sweeps (via fly_scan) while rocking the rotation stage.
    #
    # 💡 NEWER, EASIER WAY: this is a temperature + GIWAXS + rocking combination. In 'smi_plans'
    #   you'd set temperature with a heater helper, sweep incident angle with incidence_axis, and
    #   do the rocking exposure with a real monitored run instead of fly_scan (see the ⚠️ note in
    #   fly_scan). Sketch:
    #     from smi_plans import giwaxs_run, incidence_axis, goto_temperature
    #     # per temperature: goto_temperature(...); then giwaxs_run/acquire over incidence_axis(...)
    #   (records the temperature/angle/beam into each image automatically.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this calls fly_scan, which triggers the detector outside the
    #   RunEngine and does NOT record the data as a normal dataset (see fly_scan's ⚠️ note), and
    #   it uses 'prs', the old rotation-stage name that no longer exists (see the ⚠️ line below).
    #   (internal: Tier 0/1.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [302, 305, 310]

    # Medium cycle:
    samples = ["RogerC12", "C12poly"]
    x = [-8.4, 12]
    y = [1.485, 1.47]
    start_angle = [-0.412, -0.35]
    phi = [-0.693, -0.773]
    chi = [0.2, -0.43]
    # Fastest cycle:
    angles = [0.35, 0.25, 0.2]
    # angle_offset = [0.0, 0.1, 0.15]
    angle_offset = [0.35 - x for x in angles]
    x_offset = [0.0, 0.2, 0.4]

    name_fmt = "{sample}_{temperature}K_{angle}deg"

    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        if i_t > 0:
            yield from bps.sleep(1800)
        for i_s, s in enumerate(samples):
            for i_a, a in enumerate(angles):
                sample_name = name_fmt.format(sample=s, temperature=t, angle=a)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bps.mv(stage.x, x[i_s] + x_offset[i_a])
                yield from bps.mv(stage.ch, chi[i_s])
                yield from bps.mv(stage.y, y[i_s])
                yield from bps.mv(stage.th, start_angle[i_s] + angle_offset[i_a])
                yield from bps.mv(prs, phi[i_s])  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                sample_id(user_name=name, sample_name=sample_name)
                yield from bps.mv(det.cam.acquire_time, cycle * cycle_t)
                yield from bps.mv(attn_shutter, "Retract")
                yield from count([det], num=1)
                sample_id(user_name=name, sample_name=f"{sample_name}_sweep20")
                print(f"\n\t=== Sample: {sample_name}_sweep20 ===\n")
                print("... doing fly_scan here ...")
                for i in range(n_cycles):
                    yield from fly_scan(det, motor, cycle, cycle_t, phi[i_s])
                yield from bps.sleep(1)
                yield from bps.mv(attn_shutter, "Insert")


def run_saxs_caps(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS bar for capillaries — for each sample it drives the
    #   stage to that x position and runs a short y scan, taking a SAXS image.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     yield from transmission_bar("caps", samples, t=t, dets=[pil2M])
    #   (records the position/beam into each image and fills the file name for you.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    x_list = [-15, -12.8, -6.45, -0.25, 6.43, 12.5, 19.05, 25.2]  #
    # Detectors, motors:
    dets = [pil2M]
    y_range = [0, 0, 1]  # beginning, end, num pnts
    samples = [
        "LC-O36-6",
        "LC-O36-7",
        "LC-O36-8",
        "LC-O36-9",
        "LC-O37-6",
        "LC-O37-7",
        "LC-O37-8",
        "LC-O37-9",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(stage.x, x)
        sample_id(user_name=sample, sample_name="")
        yield from escan(dets, stage.y, *y_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1)  — or at the prompt:  RE(det_exposure_time(1)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_caps_temp(name="DB"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature-series SAXS bar — sets the Lakeshore heater to each
    #   temperature (waiting to equilibrate), then for every sample does a y scan and saves an
    #   image, recording the temperature and beam alongside.
    # 💡 NEWER, EASIER WAY: stepping a bar of samples through a list of temperatures is the
    #   'smi_plans' temperature combination — temperature_bar drives the heater, waits to settle,
    #   and records the temperature into each image:
    #     from smi_plans import temperature_bar, SampleList
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     yield from temperature_bar("DB", samples, temperatures=[30, 36, 40, 44, 50], t=t,
    #                                dets=[pil2M])
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [30, 36, 40, 44, 50]
    x_list = [-31.88, -25.56, -19.27, -12.92, -6.57, -0.22, 6.05, 12.42, 18.74, 25.09]
    # Detectors, motors:
    dets = [pil2M, ls.ch1_read, xbpm3.sumY]
    y_range = [-3.4, -7.2, 77]
    samples = ["water", "F3", "F2", "F1", "F0", "E3", "E2", "E0", "D3", "D2"]
    name_fmt = "{sample}_{temperature}C"
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(10)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(10)  — or at the prompt:  RE(det_exposure_time(10)). (The smi_plans technique runs set exposure for you via t=.)
    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        if i_t > 0:
            yield from bps.sleep(2400)

        for x, s in zip(x_list, samples):
            sample_name = name_fmt.format(sample=s, temperature=t)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bps.mv(stage.x, x)
            yield from bps.mv(attn_shutter, "Retract")
            sample_id(user_name=name, sample_name=sample_name)
            yield from bp.scan(dets, stage.y, *y_range)
            yield from bps.mv(attn_shutter, "Insert")
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(ls.ch1_sp, 30)


def run_waxs_multi(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small multi-sample WAXS-arc scan — for each sample it moves x and sweeps
    #   the WAXS arc, taking an image at each arc position.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you describe the WAXS arc as an "axis" and hand it to
    #   one acquire call, which records the arc/position/beam into each image:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("SP_air", [pil2M, pil900KW],
    #                        [motor_axis("wa", waxs, [7, 31, 5])])   # or a giwaxs_* preset
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) 'rayonix'
    #   (the MAXS detector) was removed with no replacement; (3) the 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see ⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    x_range = [-3.4, -7.2, 77]
    x_list = [-0.025, 0, 0.025]
    # y_offset
    # Detectors, motors:
    dets = [pil2M, pil300KW, rayonix]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error) — the current WAXS detector is 'pil900KW' (a different camera, so check beam-center/calibration); and 'rayonix' (the MAXS detector) was removed from the beamline with no current replacement — remove it from your detector list or ask beamline staff.
    waxs_arc = [7, 31, 5]
    samples = ["SP_Air_in_Airmode", "SP_CT_New_Vert", "SP_Kapton_in_Airmode"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(stage.x, x)
        sample_id(user_name=sample, sample_name="")
        yield from escan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def run_ben_giwaxs(t=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS bar — for each sample it moves x/y/chi, then for two incident
    #   angles sweeps the WAXS arc and takes an image, labelling each with the real angle.
    # 💡 NEWER, EASIER WAY: aligning/grazing measurements over a bar are the 'smi_plans' GIWAXS
    #   combination; giwaxs_bar visits each sample, and incidence_axis sweeps the incident angle
    #   while recording it into the data:
    #     from smi_plans import giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=samples, x=x_list, y=y_list)
    #     yield from giwaxs_bar("ben", samples, incident_angles=[0.075, 0.100], t=t,
    #                           dets=[pil900KW])
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI signal 'pil300kwroi2') were retired
    #   — the current WAXS detector is 'pil900KW'; (2) the 'det_exposure_time(...)' calls no
    #   longer set the exposure unless run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Parameters:
    aligned_075 = [-0.190, -0.203, -0.180]
    x_list = [-15, -6, 4]
    y_list = [1.465, 1.253, 1.190]
    chi_list = [-0.2, -0.2, -0.2]
    angle_offset = 0.025
    samples = [
        "Si-wafers",
        "PL1G1A",
        "PL9G1A",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumX]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error) and 'pil300kwroi2' is an ROI of that same retired camera. The current WAXS detector is 'pil900KW' — use it (and its ROI) instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = [7, 25, 4]
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    for x, y, a_off, chi, sample in zip(x_list, y_list, aligned_075, chi_list, samples):
        yield from bps.mv(stage.x, x)
        yield from bps.mv(stage.y, y)
        yield from bps.mv(stage.ch, chi)
        for j, ang in enumerate([a_off, a_off - angle_offset]):
            if j == 0:
                real_ang = 0.075
            else:
                real_ang = 0.075 + angle_offset
            yield from bps.mv(stage.th, ang)
            param = "inc_%s" % (real_ang)
            # print(param)
            sample_id(user_name=sample, sample_name=param)
            # print(RE.md)
            yield from escan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def linkam_fast(n=6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the shutter, does a quick SAXS y scan, then closes the shutter.
    # 💡 NEWER, EASIER WAY: a simple position scan like this maps to a transmission/map run in
    #   'smi_plans' (e.g. transmission_run or map_line_run with a y axis), which also records the
    #   position/beam into each image and handles the shutter for you. Nothing here is broken.
    # === end smi_plans note ================================================
    yield from bps.mv(attn_shutter, "Retract")
    yield from bp.scan([pil2M], stage.y, 0.1, 0.9, n)
    yield from bps.mv(attn_shutter, "Insert")

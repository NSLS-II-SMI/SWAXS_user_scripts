####line scan

# sample_id(user_name='ST',sample_name='Nitra-glass_RT_y-4300')


def run_tsaxs_ST(t=0.1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample on the bar, sweeps the WAXS detector arc through a
    #   few angles (to cover a wider q-range) and takes a SAXS+WAXS image at each,
    #   recording the temperature in the file name.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' library has a one-line WAXS-arc scan that
    #   moves the arc and snaps for you, and records the arc angle, temperature, beam
    #   intensity, etc. straight into each image (so the temperature lands in the data,
    #   not just the file name). A close fit is the GIWAXS preset (it handles the arc):
    #
    #     from smi_plans import giwaxs_run
    #     yield from giwaxs_run(
    #         "sam1",                             # rest of the file name is added automatically
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],             # SAXS + current WAXS detector (see ⚠️ below)
    #         arc=np.linspace(0, 18, 4),          # your WAXS arc angles, unchanged
    #         reads=[ls.ch1_read],                # record the temperature with each frame
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) two retired detectors are in your list — 'pil300KW'
    #   is now 'pil900KW', and 'rayonix' (MAXS) is gone with no replacement (see the ⚠️
    #   notes on the dets lines); (2) the two 'det_exposure_time(...)' calls no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes).
    #   (internal: Tier 1 — one image per point.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar
    # sample_list = ['sb-b_1_1'] #
    sample_list = ["sam1"]
    # x_list = [42000]
    x_list = [-5800]

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # angle_arc = np.array([0.08, 0.1, 0.15, 0.2]) # incident angles
    waxs_angle_array = np.linspace(
        0, 18, 4
    )  # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    # if 12, 3: up to q=2.199
    # if 18, 4: up to q=3.04
    dets = [
        pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        ls.ch1_read,
        rayonix,  # ⚠️ FIXME(smi_plans): 'rayonix' (the MAXS detector) was removed from the beamline and has no current replacement — this line would error. Remove it from your detector list or ask beamline staff.
        pil2M,
    ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]

    for x, sample in zip(x_list, sample_list):  # loop over samples on bar

        yield from bps.mv(piezo.x, x)  # move to next sample
        # yield from alignement_gisaxs(0.1) #run alignment routine

        # th_meas = angle_arc + piezo.th.position #np.array([0.10 + piezo.th.position, 0.20 + piezo.th.position])
        # th_real = angle_arc
        y_array = np.array([-4500, -4000])

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        x_meas = x

        for waxs_angle in waxs_angle_array:  # loop through waxs angles
            yield from bps.mv(waxs, waxs_angle)

            for i, th in enumerate(th_meas):  # loop over incident angles
                # yield from bps.mv(piezo.th, th)

                # x_meas = x_meas - 200   # shift a bit in x
                # yield from bps.mv(piezo.x, x_meas)
                temp = ls.ch1_read.value
                sample_name = (
                    "{sample}_{temp}deg_waxs{waxs_angle:05.2f}_x{x}_{t}s".format(
                        sample=sample, temp=temp, waxs_angle=waxs_angle, x=x_meas, t=t
                    )
                )
                sample_id(user_name="ST", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # yield from bp.scan(dets, energy, e, e, 1)
                # yield from bp.scan(dets, waxs, *waxs_arc)
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def run_harv_temp(tim=1, name="HarvTempRe"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each set-point temperature (25 C, 150 C), heats the Lakeshore,
    #   then visits 10 samples on the bar and a few x-offset spots on each, scanning the
    #   WAXS arc at every spot.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' library can run a whole sample bar at a set
    #   temperature and record the temperature/position into each image automatically.
    #   You'd give it your samples (positions + names) as a SampleList and let it heat,
    #   visit, and scan for you:
    #
    #     from smi_plans import temperature_bar, SampleList
    #     samples = SampleList.from_columns(
    #         name=["S1", "S2", ...],
    #         x=[50000, 40500, ...], y=[8950, 8850, ...],
    #     )
    #     yield from temperature_bar(
    #         name, samples,
    #         temperatures=[25, 150],             # your set-points, unchanged
    #         t=tim,                              # exposure time, unchanged (sets the camera for you)
    #         dets=[pil900KW],                    # current WAXS detector (see ⚠️ below)
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the WAXS detector 'pil300KW' was retired — it's now
    #   'pil900KW' (see the ⚠️ note on the dets line); (2) the two 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see their ⚠️ notes).
    #   (internal: Tier 2 — coordinated arc scan per spot.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [25, 150]
    # x_list  = [-42000, -20400, 200, 20400, 44300]
    x_list = [50000, 40500, 29000, 19000, 7300, -3400, -18000, -26000, -33000, -39000]
    # y_list =  [  5600,   5800, 5920, 5822,  5972]
    y_list = [8950, 8850, 8750, 8850, 8700, 8650, 8800, 7970, 7970, 7670]
    samples = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "SH2", "SH3", "SH4"]
    # samples = ['S29']
    # Detectors, motors:
    # dets = [pil2M, rayonix, pil300KW,ls.ch1_read, xbpm3.sumY] #ALL detectors
    dets = [pil300KW, ls.ch1_read, xbpm3.sumY]  # WAXS detector ALONE  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    x_offset = [0, 200, 400, 600, 800]
    waxs_arc = [0, 30, 6]
    name_fmt = "{sample}_{offset}um_{temperature}C"
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (The smi_plans technique runs set exposure for you via t=.)
    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        if i_t > 0:
            yield from bps.sleep(600)
        for x, y, s in zip(x_list, y_list, samples):
            temp = ls.ch1_read.value
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            yield from bps.mv(piezo.z, 200)
            for i_o, o in enumerate(x_offset):
                sample_name = name_fmt.format(sample=s, offset=o, temperature=temp)
                yield from bps.mv(piezo.x, x + x_offset[i_o])
                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)
                yield from bp.scan(dets, waxs, *waxs_arc)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(ls.ch1_sp, 28)


def run_harv_poly(tim=1, name="HarvPoly"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sets the temperature, then sits on one spot and takes 600 WAXS
    #   shots, 30 s apart, watching the sample change over time at fixed temperature.
    #
    # 💡 NEWER, EASIER WAY: "hold the temperature and watch it over time" is exactly the
    #   'smi_plans' isothermal-kinetics helper; it takes the repeated shots and records
    #   the temperature/time into each image for you:
    #
    #     from smi_plans import isothermal_kinetics_run
    #     yield from isothermal_kinetics_run(
    #         name,                               # rest of the file name is added automatically
    #         temperature=85,                     # your hold temperature, unchanged
    #         num=600, period=30,                 # 600 frames, 30 s apart, unchanged
    #         t=tim,                              # exposure time, unchanged (sets the camera for you)
    #         dets=[pil900KW],                    # current WAXS detector (see ⚠️ below)
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the WAXS detector 'pil300KW' was retired — it's now
    #   'pil900KW' (see the ⚠️ note on the dets line); (2) the two 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see their ⚠️ notes).
    #   (internal: Tier 1 — one image per frame, isothermal time series.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [85]
    x_list = [-1000]
    y_list = [-4740]
    samples = ["S29"]
    # Detectors, motors:
    dets = [pil300KW, ls.ch1_read, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name_fmt = "{sample}_{temperature}C"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (The smi_plans technique runs set exposure for you via t=.)
    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        # yield from bps.sleep(30)
        yield from bps.mv(ls.ch1_sp, 28)
        for x, y, s in zip(x_list, y_list, samples):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            yield from bps.mv(piezo.z, 200)
            for i in range(600):
                temp = ls.ch1_read.value
                sample_name = name_fmt.format(sample=s, temperature=temp)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)
                yield from bp.count(dets, num=1)
                yield from bps.sleep(30)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(ls.ch1_sp, 28)


def run_harv_micro(tim=3, name="HarvMicro_2_25C"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: heats to a set-point, then visits several x-offset spots on the
    #   sample and does a short y-scan at each, recording the temperature in the name.
    #
    # 💡 NEWER, EASIER WAY: smi_plans can run a sample bar at a set temperature and do a
    #   small map at each spot, recording the temperature/position into each image. You'd
    #   hand it your samples as a SampleList and let it heat, visit, and scan:
    #
    #     from smi_plans import temperature_bar, SampleList
    #     samples = SampleList.from_columns(name=["SC10", "SC11", ...],
    #                                       x=[40016, ...], y=[-3880, ...])
    #     yield from temperature_bar(
    #         name, samples,
    #         temperatures=[150],                 # your set-point, unchanged
    #         t=tim,                              # exposure time, unchanged (sets the camera for you)
    #         dets=[pil900KW],                    # current WAXS detector (see ⚠️ below)
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the WAXS detector 'pil300KW' was retired — it's now
    #   'pil900KW' (see the ⚠️ note on the dets line); (2) the two 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see their ⚠️ notes).
    #   (internal: Tier 2 — coordinated y-scan per spot.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [150]
    # x_list  = [-42000, -20400, 200, 20400, 44300]
    x_list = [
        40016,
    ]
    # y_list =  [  5600,   5800, 5920, 5822,  5972]
    y_list = [
        -3880,
    ]
    samples = ["SC10", "SC11", "SC12", "SC13", "SC14", "SC15", "SC16", "SC17"]
    # samples = ['S29']
    # Detectors, motors:
    # dets = [pil2M, rayonix, pil300KW,ls.ch1_read, xbpm3.sumY] #ALL detectors
    dets = [pil300KW, ls.ch1_read, xbpm3.sumY]  # WAXS detector ALONE  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    x_offset = [-704, -352, 0, 352, 704]
    y_range = [20, -20, 3]
    waxs_arc = [0, 30, 6]
    name_fmt = "{sample}_{xoffset}um_{temperature}C"
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (The smi_plans technique runs set exposure for you via t=.)
    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        if i_t > 0:
            yield from bps.sleep(600)
        for x, y, s in zip(x_list, y_list, samples):
            temp = ls.ch1_read.value
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            yield from bps.mv(piezo.z, 2800)
            for i_x, xo in enumerate(x_offset):
                sample_name = name_fmt.format(sample=s, xoffset=xo, temperature=temp)
                yield from bps.mv(piezo.x, x + x_offset[i_x])
                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)
                yield from bp.rel_scan(dets, piezo.y, *y_range)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(ls.ch1_sp, 28)

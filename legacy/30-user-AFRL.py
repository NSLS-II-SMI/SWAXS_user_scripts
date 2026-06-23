def saxsafrl(t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a long time-series — it loops up to 10000 times, reading the
    #   Lakeshore temperature each pass and snapping one SAXS+WAXS image, naming each
    #   shot by its temperature and frame number.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-line "watch it over time" helper that
    #   takes repeated shots and records the temperature, beam intensity, etc. straight
    #   into each image (so the temperature lands in the data, not just the file name):
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run(
    #         "BS_water2",                       # rest of the file name is added automatically
    #         num=10000,                         # number of frames, unchanged
    #         t=t,                               # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],            # SAXS + current WAXS detector (see ⚠️ below)
    #         reads=[ls.ch1_read],               # record the Lakeshore temperature with each frame
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the WAXS detector 'pil300KW' was retired — it's now
    #   'pil900KW' (see the ⚠️ note on the dets line); (2) the two 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see the ⚠️ notes on them).
    #   (internal: Tier 1 — one image per frame.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    name = "BS"
    x_list = -6
    # Detectors, motors:
    dets = [pil2M, pil300KW, ls.ch1_read]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # y_range = [-0.0, 0.0, 1]
    sample = "water2"
    num = 10000

    pil2M.cam.file_path.put(
        f"/ramdisk/images/users/2020_2/305934_Schantz/1M/%s" % sample
    )
    name_fmt = "{i}_{temperature}C"
    #    param   = '20.4'
    # assert len(x_list) == len(samples), f'Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})'
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    for i in range(num):
        temp = ls.ch1_read.value
        # fs.open()
        # yield from bps.sleep(0.25)
        # pin = pin_diode.read()['pin_diode_current2_mean_value']['value']
        # pin = pdcurrent2.value
        # print(pin)
        # yield from bps.sleep(0.25)
        # fs.close()
        # sample_name = name_fmt.format(temperature=temp, pinread = float('%.1f'%pin), i = '%4.4d'%i)
        sample_name = name_fmt.format(temperature=temp, i="%4.4d" % (i))
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=sample, sample_name=sample_name)
        # yield from bp.count(dets)
        # yield from bp.rel_scan(dets, stage.y, *y_range)
        yield from bp.count(dets, num=1)
        yield from bps.sleep(2)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

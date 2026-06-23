def run_continous_Zhang(name='test', t=1, td=10):
    """
    Continous SWAXS measurement

    Args:
        name (str): sample name, please make it unique for each,
        t (float): detector exposure time is seconds,
        td (flaot): time interval between measurements.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a continuous (time-series) SWAXS measurement — it parks the WAXS
    #   arc, then keeps taking SAXS + WAXS images in a loop, roughly every 'td' seconds,
    #   tagging each file with the step number and elapsed time. ("Time series" just means
    #   repeating the same shot over and over to watch something change in time.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   ready-made time-series routine. You give it the interval and how long to run, and
    #   it records the elapsed time, beam intensity, etc. into the saved data for you (so
    #   you don't have to hand-build the "{name}_step{}_time{}s" file name):
    #
    #     from smi_plans import time_series_run        # do this once at the top of your session
    #     yield from time_series_run(
    #         name,                                    # the rest of the file name is filled in for you
    #         period=td,                               # your time interval between shots, unchanged
    #         dets=[pil2M, pil900KW],                  # SAXS + WAXS, unchanged
    #         t=t,                                     # your exposure time, unchanged
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes on those lines below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    user = "FZ"
    wa = 17

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t_initial = time.time()

    yield from bps.mv(waxs, wa)
    dets = [pil900KW] if waxs.arc.position < 14.9 else [pil2M, pil900KW]

    
    for i in range(99999):

        t_measurement = time.time()
        
        # Generate sample name
        step = str(i).zfill(4)
        time_sname = str(np.round(t_measurement - t_initial, 0)).zfill(7)
        sample_name = f'{name}_step{step}_time{time_sname}s{get_scan_md()}'
        sample_id(user_name=user, sample_name=sample_name)
        
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)
    
        # Wait until the total time difference passes
        while (time.time() - t_measurement) < td:
            yield from bps.sleep(0.1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so this plain "reset to 0.5s" call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).



def run_continous_pindiode_Zhang(name='test', t=1, td=10):
    """
    Continous SWAXS measurement

    Args:
        name (str): sample name, please make it unique for each,
        t (float): detector exposure time is seconds,
        td (flaot): time interval between measurements.
    """

    user = "FZ"
    wa = 15

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same continuous (time-series) SWAXS loop as above, but it also
    #   briefly opens the shutter and reads the pin-diode (a small beam-intensity sensor)
    #   before each shot, so the measured intensity goes into the file name.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a ready-made time-series routine that repeats
    #   the shot for you and records elapsed time + pin-diode reading straight into the
    #   saved data (no need to hand-build "{name}_step{}_time{}s_pd{}"):
    #
    #     from smi_plans import time_series_run        # do this once at the top of your session
    #     yield from time_series_run(
    #         name,                                    # the rest of the file name is filled in for you
    #         period=td,                               # your time interval between shots, unchanged
    #         dets=[pil2M, pil900KW, pin_diode],       # SAXS + WAXS + the beam-intensity sensor
    #         t=t,                                     # your exposure time, unchanged
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes on those lines below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t_initial = time.time()

    yield from bps.mv(waxs, wa)
    dets = [pil900KW] if waxs.arc.position < 14.9 else [pil2M, pil900KW]
    dets.append(pdcurrent1)

    
    for i in range(99999):

        # Read pin diode current when the shutter is open
        fs.open()
        yield from bps.sleep(0.3)
        pd_curr = pdcurrent1.value
        fs.close()
        pd = str(int(np.round(pd_curr, 0))).zfill(4)

        t_measurement = time.time()
        
        # Generate sample name
        step = str(i).zfill(4)
        time_sname = str(np.round(t_measurement - t_initial, 0)).zfill(7)
        sample_name = f'{name}_step{step}_time{time_sname}s_pd{pd}{get_scan_md()}'
        sample_id(user_name=user, sample_name=sample_name)
        
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)
    
        # Wait until the total time difference passes
        while (time.time() - t_measurement) < td:
            yield from bps.sleep(0.1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so this plain "reset to 0.5s" call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def run_standard_swaxs_Zhang_2023_3(t=2):
    """
    Standard SWAXS scan
    """
    
    names =   [     'KaptonBlank',  'Air Blank', ]
    piezo_x = [     24000,    -3800 ] 
    piezo_y = [  1200 for n in names ]
    piezo_z = [ 10400 for n in names ]

    assert len(names)   == len(piezo_x), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_y), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_z), f"Wrong list lenghts"

    user = 'FZ'
    waxs_arc = [ 20, 0 ]
    x_off = [-500, 0, 500 ]
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a standard SWAXS scan — for each WAXS arc angle and each sample, it
    #   drives to the sample and takes SAXS + WAXS images at three x-offset spots
    #   (-500, 0, +500), reading the pin-diode (a beam-intensity sensor) when SAXS is live.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that builds
    #   the little line of x-positions for you and records position + beam intensity into
    #   the saved data automatically (no need to hand-build "{name}_loc{}_pd{}"):
    #
    #     from smi_plans import map_line_run           # do this once at the top of your session
    #     yield from map_line_run(
    #         "KaptonBlank",                           # the rest of the file name is filled in for you
    #         axis="x", center=24000, size=1000, num=3,  # your 3 x-offsets: -500, 0, +500
    #         dets=[pil2M, pil900KW, pin_diode],       # SAXS + WAXS + the beam-intensity sensor
    #         t=t,                                     # your exposure time, unchanged
    #     )
    #     # (call it per sample / WAXS arc, the way you loop below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes on those lines below).
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        condition = waxs.arc.position < 15

        dets = [pil900KW] if condition else [pil2M, pil900KW]
            
        for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y,
                              piezo.z, z,
            )
        
            for xx, x_of in enumerate(x_off):
                yield from bps.mv(piezo.x, x + x_of)

                if not condition:
                    fs.open()
                    yield from bps.sleep(0.3)
                    pd_curr = pdcurrent1.value
                    fs.close()
                else:
                    pd_curr = 0

                pd = str(int(np.round(pd_curr, 0))).zfill(4)
                
                sample_name = f'{name}_loc{xx}_pd{pd}{get_scan_md()}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so this plain "reset to 0.5s" call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
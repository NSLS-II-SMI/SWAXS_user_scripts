from bluesky.utils import FailedStatus

def run_cai_temp_scan(name_base='M11-cap3', t=1.2):
    # get starting y position
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps a Linkam hot-stage through a list of temperatures (ramping, then soaking at
    #   each), and at every temperature takes a short WAXS/SAXS line scan across the sample.
    #
    # 💡 NEWER, EASIER WAY: ramping the Linkam heater to each temperature, soaking, then
    #   measuring is the beamline 'smi_plans' helper library's temperature ramp run. It drives
    #   the heater, waits for each setpoint + soak, and records the temperature into the saved
    #   data and file name for you:
    #
    #     from smi_plans import temperature_ramp_run, temperature_axis, linkam_heater
    #     yield from temperature_ramp_run(
    #         name_base,
    #         temperature_axis(LThermal, temperatures_c, rates=ramp_rates_cpm, settle=wait_times_sec),
    #         t=t,
    #     )
    #     # (goto_temperature handles the 'set + wait to reach + soak' that ramp_to_temp does here.)
    #
    # 💡 NICE WORK: this script already templates the file name from recorded fields like
    #   {stage_y} and {pin_diode_current2_mean_value} and records the Linkam temperature into
    #   the data — that's exactly the smi_plans style, so migrating is mostly a simplification.
    #
    #   (The 'sleep' waits here are temperature soak/settle time — NOT broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t,t)' call below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ FIXME note on that line).
    # === end smi_plans note ================================================
    y0 = stage.y.position
    x0 = stage.x.position
    waxs_arc = [0, 20]



    


    names          = ['40','60','80','100','120','140','160','180','25-back']
    temperatures_c = [40,  60,  80,  100,  120,  140,  160,  180,  25 ]
    ramp_rates_cpm = [10  ,10,  10,  10,   10,   10,    10,  10   ,40]
    wait_times_sec = [60 ,300 ,300 ,300 ,300  ,300  ,300   ,300, 900]

 



  
    det_exposure_time(t,t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t,t)  — or at the prompt:  RE(det_exposure_time(t,t)). (The smi_plans technique runs set exposure for you via t=.)

    # define scan run
    project_set('insitu')

    def inner(xs,name): 
        """
        
 
        0       """
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if waxs.arc.position < 15:
                dets = [pil900KW, LThermal.temperature_current,stage.x,stage.y]
                RE.md['sample_name'] = f'{name_base}_{name}_y{{stage_y}}_x{{stage_x}}{get_scan_md()}'
                yield from bps.mvr(stage.y, 0.02)
            else:
                
                dets = [pil2M, pin_diode, pil900KW, LThermal.temperature_current,stage.x, stage.y]
                RE.md['sample_name'] = f'{name_base}_{name}_y{{stage_y}}_x{{stage_x}}_pd{{pin_diode_current2_mean_value}}{get_scan_md()}'
               
            # move stage to the starting x position
            yield from bps.mv(stage.x, xs)
            print(f"\n\n\n\t=== Sample: {RE.md['sample_name']} ===")
            yield from bp.rel_scan(dets, stage.x, 0, 0.20, 5)

    def ramp_to_temp(deg,ramp,name, waitsec):
        yield from bps.mv(LThermal.temperature_setpoint,deg)
        yield from bps.mv(LThermal.temperature_rate_setpoint,ramp)
        yield from bps.mv(LThermal.cmd,1)
        while np.abs(LThermal.temperature()-deg) > 0.5:
            yield from bps.sleep(20)  # wait until the temperature is 80C
            print(f'Waiting for temperature to reach {name}, current temperature: {LThermal.temperature()}C')
        # add equilibration time
        print(f'waiting for {waitsec} seconds to ensure temperature equilibration')
        yield from bps.sleep(waitsec)  
        print(f'temperature equilibration done.  reached {LThermal.temperature()}C')
        yield from bps.sleep(20)
    

    for name, temperature, ramprate, waitsec in zip(names,temperatures_c,ramp_rates_cpm,wait_times_sec):
        yield from bps.mvr(stage.y, 0.05)
        yield from ramp_to_temp(temperature, ramprate, name, waitsec)

        print("\n[info] Waiting for system to settle...")
        yield from bps.sleep(20)

        try:
            yield from inner(x0, name)
        except FailedStatus:
            print(f"[warning]...")
            try:
                yield from bps.sleep(20)
                yield from inner(x0, name)
            except FailedStatus:
                print(f"[warning]...")
                try:
                    yield from bps.sleep(20)
                    yield from inner(x0, name)
                except FailedStatus:
                    print(f"[warning]: dectector move failed...")
        
        RE.clear_suspenders()
        yield from bps.sleep(10)

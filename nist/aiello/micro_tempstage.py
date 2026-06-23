


    # LThermal
    # sample_id(user_name='Chaney', sample_name=f'{name_base}_{LThermal.temperature()}degC_{en}eV')
    #     RE.md['temp'] = LThermal.temperature()

    # #examples

    # LThermal.on() # turn on the heating

    # LThermal.off(self): # turn off the heating

    # LThermal.setTemperature(temperature): # sets the setpoint

    # LThermal.setTemperatureRate(temperature_rate): # sets the rate

    # LThermal.temperature() #reads back the current temperature

    # LThermal.temperatureRate() # reads back the current temperature

def run_nist_temp_micro(name_base='test', t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a micro temperature study on the Linkam stage — at room temp,
    #   then +85 C, then -40 C, it runs a fine line-scan in y (167 points over ±250 µm)
    #   at two WAXS arc positions, recording the stage temperature and beam into the
    #   data. (The nested 'inner(...)' helper is just the per-temperature line-scan it
    #   reuses — it's covered by this note, no separate migration needed.)
    #
    # 👍 Nice — you're already letting the file name fill in from recorded values
    #   (e.g. '{stage_y}', '{pin_diode_current2_mean_value}'), which is exactly the
    #   modern smi_plans style, and you record LThermal.temperature_current as a channel.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has Linkam temperature helpers that drive the
    #   heater, wait for equilibrium, and measure, plus a line-scan map preset — so the
    #   set/equilibrate/scan dance becomes a couple of calls:
    #
    #     from smi_plans import linkam_heater, goto_temperature, map_line_run
    #     # goto_temperature(85, ...) drives + waits; map_line_run scans stage.y and
    #     # records everything. (LThermal, stage.x/y, pin_diode, get_scan_md are all fine.)
    #
    #   (Optional — nothing here is broken; this whole routine runs as-is.)
    # === end smi_plans note ================================================
    # get starting y position
    y0 = stage.y.position
    waxs_arc = [0, 20]

    # define scan run
    def inner(y0,name,add_ref=False):
        """
        Inner function to run a temperature scan at 167 y positions from -250 to 250 microns from y0
 
        0       """
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if waxs.arc.position < 15:
                dets = [pil900KW, LThermal.temperature_current,stage.x]
                sample_id(user_name=name_base, sample_name=f'{name}_epoxyref_y{{stage_y}}_{get_scan_md()}')
                
            else:
                # move stage to the right by 50 microns
                yield from bps.mvr(stage.x,0.05)
                dets = [pil2M, pin_diode, pil900KW, LThermal.temperature_current,stage.x]
                sample_id(user_name=name_base, sample_name=f'{name}_epoxyref_y{{stage_y}}_pd{{pin_diode_current2_mean_value}}_{get_scan_md()}')
                
            if add_ref:
                # take reference at the starting y position
                yield from bps.mv(stage.y, y0 - 0.4)
                print(f"\n\n\n\t=== Sample: {RE.md['sample_name']} ===")
                yield from bp.count(dets)
            # move stage to the starting y position
            yield from bps.mv(stage.y, y0)
            if waxs.arc.position < 15:
                sample_id(user_name=name_base, sample_name=f'{name}_microyscan_y{{stage_y}}_{get_scan_md()}')
            else:
                sample_id(user_name=name_base, sample_name=f'{name}_microyscan_y{{stage_y}}_pd{{pin_diode_current2_mean_value}}_{get_scan_md()}')

            print(f"\n\n\n\t=== Sample: {RE.md['sample_name']} ===")
            yield from bp.rel_scan(dets, stage.y, -0.25, 0.25, 167)

    # run at room temperature
    yield from bps.mv(stage.y, y0 - 0.4)
    sample_id(user_name=name_base, sample_name='epoxy_ref')
    project_set(name_base)
    yield from bp.count([pil2M, pin_diode])
    yield from inner(y0, 'room_temp',add_ref=False)

    # move stage to the right by 50 microns
    yield from bps.mvr(stage.x,0.05)
    # set linkam to 85C, equilabrate, then run the scan

    LThermal.setTemperature(85)
    LThermal.setTemperatureRate(30)
    LThermal.on()
    while LThermal.temperature() < 84:
        yield from bps.sleep(20)  # wait until the temperature is 80C
        print(f'Waiting for temperature to reach 84C, current temperature: {LThermal.temperature()}C')
    # add equilibration time
    print('waiting for 120 seconds to ensure temperature equilibration')
    yield from bps.sleep(120)  # wait for 60 seconds to ensure temperature
    print(f'temperature equilibration done.  reached {LThermal.temperature()}C')
    yield from inner(y0, '85C',add_ref=False)

    # move stage to the right by 50 microns
    yield from bps.mvr(stage.x,0.05)
    # set linkam to -40C, equilabrate, then run the scan
    LThermal.setTemperature(-40)
    LThermal.setTemperatureRate(30)
    LThermal.on()
    while LThermal.temperature() > -39:
        yield from bps.sleep(20)  # wait until the temperature is 80C
        print(f"Waiting for temperature to reach -39C, current temperature: {LThermal.temperature()}C")
    print('waiting for 120 seconds to ensure temperature equilibration')
    yield from bps.sleep(120)  # wait for 60 seconds to ensure temperature
    print(f'temperature equilibration done.  reached {LThermal.temperature()}C')
    yield from inner(y0, '-40C', add_ref=False)
    LThermal.setTemperature(25)  # reset temperature to room temperature



def run_exsitu_hard_2025_2(t=1):
    """
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ hard-X-ray survey of a bar of samples — for each WAXS
    #   arc position and each sample, it takes a few points (a small x/y grid of offsets)
    #   and saves an image at each, with SAXS enabled only when the WAXS arc is out of
    #   the way.
    #
    # 👍 You already let the file name fill in from recorded values via get_scan_md() —
    #   that's the modern smi_plans style.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has map/averaging presets that take a few points
    #   per sample across a whole bar and record energy/beam/positions INTO each file:
    #
    #     from smi_plans import map_grid_run, map_dets, map_bar
    #     # map_grid_run does the little x/y offset grid per sample; map_bar drives the
    #     # whole bar. (pil900KW and pil2M here are both fine.)
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names_1   = [  'vacuum', 'PP_fresh_tr', 'EVA_block', 'EVA_pass', 'POE_block', 'POE_pass']
    piezo_x_1 = [    -29000,        -21000,      -11700,      -4700,        3750,      13250]
    piezo_y_1 = [      2000,          2000,        2000,       2000,        2000,       2000]

    names_2   = [ ]
    piezo_x_2 = [ ]
    piezo_y_2 = [ ]

    

    names   =   names_1 +   names_2
    piezo_x = piezo_x_1 + piezo_x_2
    piezo_y = piezo_y_1 + piezo_y_2
    piezo_z = [ 400 for n in names ]
    
    waxs_arc = [ 0, 20, ]

    # Offsets for taking a few points per sample
    x_off = [-50, 50]
    y_off = [-50, 50]

    user = "AA"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' map presets set exposure via t=.)

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]

        for i, (name, x, y, z,) in enumerate(zip(names, piezo_x, piezo_y, piezo_z)):

            yield from bps.mv(
                piezo.y, y,
                piezo.x, x,
                piezo.z, z,
            )

            for yy, y_of in enumerate(y_off):
                yield from bps.mv(piezo.y, y + y_of)

                for xx, x_of in enumerate(x_off):
                    yield from bps.mv(piezo.x, x + x_of)

                    loc = f'{yy}{xx}'
            

                    sample_name = f'{name}{get_scan_md()}_loc{loc}'
                    sample_id(user_name=user, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {RE.md['sample_name']} ===")
                    yield from bp.count(dets)


    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.
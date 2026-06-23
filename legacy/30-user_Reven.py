

def temp_series(name='temp',temps = np.linspace(32,26,13),exp_time=1, hold_delay=120, dets=[pil2M]):   # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a Linkam temperature series — sets the Linkam stage to each temperature
    #   in turn, waits for it to settle and equilibrate, then takes a SAXS image at that temperature.
    #
    # 💡 NEWER, EASIER WAY: stepping temperature and taking an image at each step is the smi_plans
    #   temperature-ramp run. It drives the Linkam, waits for each setpoint, records the temperature
    #   INTO the data, and builds the file name from the recorded fields — so you can drop the
    #   throwaway 'target_file_name' Signal and the hand-built 'name_fmt':
    #
    #     from smi_plans import temperature_ramp_run, linkam_heater   # do this once at the top
    #     yield from temperature_ramp_run(
    #         "temp",                                    # the rest of the file name is added automatically
    #         np.linspace(32, 26, 13),                   # your temperatures, unchanged
    #         t=exp_time, dets=[pil2M], heater=linkam_heater,
    #         settle=hold_delay,                         # your equilibration wait, unchanged
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================
    
    #temps = np.linspace(45, 30, 16)

    #dets = [pil2M] 
    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (The smi_plans temperature_ramp_run sets it for you via t=.)

    s = Signal(name='target_file_name', value='')
    RE.md["sample_name"] = '{target_file_name}'
    for i, temp in enumerate(temps):
        print(f'setting temperature {temp}')
        LThermal.setTemperature(temp)

        while abs(LThermal.temperature()-temp)>0.2:
            yield from bps.sleep(10)
            print(f'{LThermal.temperature()} is too far from {temp} setpoint, waiting 10s')

        print('Reached setpoint', temp)
        if i==0:
            print(f'Beginning equilibration of {2*hold_delay} seconds')
            yield from bps.sleep(2*hold_delay)
        else:
            print(f'Beginning equilibration of {hold_delay} seconds')
            yield from bps.sleep(hold_delay)


        # Metadata
        sdd = pil2M_pos.z.position / 1000

        # Sample name
        name_fmt = ("{sample}_{energy}eV_sdd{sdd}m_temp{temp}")
        sample_name = name_fmt.format(sample = name,energy = "%.2f" % energy.energy.position , sdd = "%.1f" % sdd, temp = "%.1f" %temp)
        sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})

        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        s.put(sample_name)
        
        yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'



def temp_series_withpos(name='temp',temps = np.linspace(32,26,13),exp_time=1, hold_delay=120, dets=[pil2M], xs=[-12.5], ys=[-2.298]):   # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like temp_series, but for each (x, y) spot on the sample it runs the
    #   whole Linkam temperature series (setpoint -> settle -> SAXS image) at that spot.
    #
    # 💡 NEWER, EASIER WAY: compose a position move with the smi_plans temperature-ramp run —
    #   it drives the Linkam, waits for each setpoint, and records temperature/position INTO the
    #   data (so you can drop the throwaway 'target_file_name' Signal and the hand-built name):
    #
    #     from smi_plans import temperature_ramp_run, linkam_heater, goto_sample
    #     # for each (x, y): yield from goto_sample(...); then
    #     yield from temperature_ramp_run("temp", np.linspace(32, 26, 13),
    #                                     t=exp_time, dets=[pil2M], heater=linkam_heater,
    #                                     settle=hold_delay)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================
    
    #temps = np.linspace(45, 30, 16)

    #dets = [pil2M] 
    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (The smi_plans temperature_ramp_run sets it for you via t=.)

    s = Signal(name='target_file_name', value='')
    RE.md["sample_name"] = '{target_file_name}'
    for j in range(len(xs)):
        yield from mv(stage.x,xs[j])
        yield from mv(stage.y,ys[j])

        for i, temp in enumerate(temps):
            LThermal.setTemperature(temp)

            while abs(LThermal.temperature()-temp)>0.2:
                yield from bps.sleep(10)
                print('waiting for 10s')

            print('Reached temp', temp)
            print('Waiting during equilibration')
            if i==0:
                yield from bps.sleep(2*hold_delay)
            else:
                yield from bps.sleep(hold_delay)



            # Metadata
            sdd = pil2M_pos.z.position / 1000

            # Sample name
            name_fmt = ("{sample}_{energy}eV_sdd{sdd}m_temp{temp}_pos{pos`}")
            sample_name = name_fmt.format(sample = name,energy = "%.2f" % energy.energy.position , sdd = "%.1f" % sdd, temp = "%.1f" %temp, pos=j)
            sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})

            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            s.put(sample_name)
            
            yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'





def temp_series_grid(name='temp',
                     temps = np.linspace(32,26,13),
                     exp_time=1, 
                     hold_delay=120, 
                     dets=[pil2M], 
                     xs=np.linspace(-13,-12,11), 
                     ys=np.linspace(-2.3,-2.8,6)):
       # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like temp_series, but rasters a grid of (x, y) spots and, at each spot,
    #   runs the whole Linkam temperature series (setpoint -> settle -> SAXS image).
    #
    # 💡 NEWER, EASIER WAY: build the x/y grid as spatial axes and the temperatures as a
    #   temperature axis, hand them to one acquire call, or wrap the smi_plans temperature-ramp
    #   run inside a position loop. Either way it records temperature/position INTO the data and
    #   names files from the recorded fields (no throwaway 'target_file_name' Signal needed):
    #
    #     from smi_plans import acquire, temperature_axis, spatial_grid_axes
    #     yield from acquire("temp", [pil2M],
    #                        [*spatial_grid_axes(stage.x, np.linspace(-13, -12, 11),
    #                                            stage.y, np.linspace(-2.3, -2.8, 6)),
    #                         temperature_axis(np.linspace(32, 26, 13), settle=hold_delay)])
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================
    

    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (The smi_plans temperature_ramp_run sets it for you via t=.)

    s = Signal(name='target_file_name', value='')
    RE.md["sample_name"] = '{target_file_name}'
    print(f'starting grid scan of {len(xs)*len(ys)} points')
    for xp in xs:

        yield from mv(stage.x,xp)
        for yp in ys:
            yield from mv(stage.y,yp)
            print(f'beginning measurement at x={xp}, y={yp}')
            for i, temp in enumerate(temps):
                print(f'setting temperature {temp}')
                LThermal.setTemperature(temp)

                while abs(LThermal.temperature()-temp)>0.2:
                    yield from bps.sleep(10)
                    print(f'{LThermal.temperature()} is too far from {temp} setpoint, waiting 10s')

                print('Reached setpoint', temp)
                if i==0:
                    print(f'Beginning equilibration of {2*hold_delay} seconds')
                    yield from bps.sleep(2*hold_delay)
                else:
                    print(f'Beginning equilibration of {hold_delay} seconds')
                    yield from bps.sleep(hold_delay)



                # Metadata
                sdd = pil2M_pos.z.position / 1000

                # Sample name
                name_fmt = ("{sample}_{energy}eV_sdd{sdd}m_temp{temp}_x{x}_y{y}")
                sample_name = name_fmt.format(sample = name,
                                              energy = "%.2f" % energy.energy.position , 
                                              sdd = "%.1f" % sdd, 
                                              temp = "%.1f" %temp, 
                                              x=xp, 
                                              y=yp)
                sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})

                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'
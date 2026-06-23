

def temp_series(name='temp',temps = np.linspace(32,26,13),exp_time=1, hold_delay=120, dets=[pil2M]):   # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the Linkam hot-stage through a list of temperatures, waits
    #   at each one for the stage to reach setpoint and equilibrate, then takes a SAXS
    #   image. Builds the file name by hand from the energy, detector distance, and temp.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does
    #   "go to each temperature, settle, then measure" for you in one call, and records
    #   the actual temperature / energy / beam intensity straight INTO the saved data and
    #   file name (so you can drop the hand-built "{sample}_{energy}eV_sdd..." name and the
    #   throwaway 'target_file_name' Signal). Same run would be roughly:
    #
    #     from smi_plans import temperature_ramp_run
    #     yield from temperature_ramp_run(
    #         "temp", np.linspace(32, 26, 13),      # your name + your temperatures
    #         t=exp_time, dets=[pil2M],             # your exposure + detector
    #         settle=hold_delay)                    # how long to dwell at each setpoint
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets
    #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    #   (The Linkam 'LThermal' and 'stage.x/y' are fine — no change needed.)
    # === end smi_plans note ================================================

    #temps = np.linspace(45, 30, 16)

    #dets = [pil2M] 
    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' temperature_ramp_run sets it for you via t=.)

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
    # WHAT THIS DOES: like temp_series, but first moves to each (x, y) sample spot, then
    #   for that spot steps the Linkam through the temperatures, equilibrating and taking
    #   a SAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' lets you run the temperature ramp at each sample
    #   position with one call per spot, recording the real temperature / energy / beam /
    #   position into the data and file name (so you can drop the hand-built name and the
    #   'target_file_name' Signal):
    #
    #     from smi_plans import temperature_ramp_run
    #     for x, y in zip(xs, ys):
    #         yield from bps.mv(stage.x, x, stage.y, y)   # move to the spot (as you do now)
    #         yield from temperature_ramp_run(
    #             "temp", np.linspace(32, 26, 13),        # your name + temperatures
    #             t=exp_time, dets=[pil2M], settle=hold_delay)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets
    #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================

    #temps = np.linspace(45, 30, 16)

    #dets = [pil2M] 
    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' temperature_ramp_run sets it for you via t=.)

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
    # WHAT THIS DOES: a full x-y grid version — at every (x, y) point on a grid it steps
    #   the Linkam through the temperatures, equilibrating and taking a SAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can do the temperature ramp at each grid point and
    #   record the real temperature / energy / beam / x / y into the data and file name
    #   (so you can drop the hand-built name and the 'target_file_name' Signal). For the
    #   x-y raster part there's also a mapping helper if you want it:
    #
    #     from smi_plans import temperature_ramp_run, spatial_grid_axes
    #     for xp in xs:
    #         for yp in ys:
    #             yield from bps.mv(stage.x, xp, stage.y, yp)   # move to grid point
    #             yield from temperature_ramp_run(
    #                 "temp", np.linspace(32, 26, 13),          # your name + temperatures
    #                 t=exp_time, dets=[pil2M], settle=hold_delay)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets
    #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================

    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' temperature_ramp_run sets it for you via t=.)

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
                                              temp = "%.1f" % temp, 
                                              x= "%.1f" % xp, 
                                              y= "%.1f" % yp)
                sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})

                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'
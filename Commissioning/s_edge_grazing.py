

def angle_dependant_temp_Sedge(t=1):
    dets = [pil900KW,LThermal.temperature_current,LThermal.temperature_setpoint]
    det_exposure_time(t, t)



    # bottom left first
    names = ['Lucas_sample2']             
    x_piezo = [ -8900.0]




    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    
    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2472.5,2473.0,2473.5,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    2480.0,2480.5,2481.0,2481.5,2482.0,2482.5,2483.0,2483.5,2484.0,2484.5,2485.0,2485.5,2486.0,2486.5,2487.0,2487.5,2488.0,2488.5,2489.0,2490.0,2490.5,2491.0,
    2491.5,2492.0,2493,2495.0,2500.0,2510.0,2515.0]

    waxs_arc = [9]
    ai0_all = 0.823
    ai_list = np.linspace(.5,4,15)

    for name, xs in zip(names, x_piezo):
        x_step = 1
        '''
        yield from bps.mv(stage.x, xs_hexa,
                          stage.y, ys_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.7)
        '''
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = ai0_all
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                yield from bps.mv(piezo.x, xs)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}_degC{temp}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs - counter * x_step)
                        counter += 1
                        
                        bpm = xbpm2.sumX.get()
                        temperature = LThermal.temperature_setpoint.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm,temp=temperature)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])


                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs - counter * x_step)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())



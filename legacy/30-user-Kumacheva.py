def equalise_temperature(temperature=25):
    """
    Set and stabilise temperature using Lakeshore controller
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sends the Lakeshore heater to a target temperature and then waits in a
    #   loop until the sample has actually reached it (and holds a bit longer for hotter set
    #   points). 'ls' is the Lakeshore temperature controller. (Nothing here is broken.)
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a one-call helper that goes to a temperature and
    #   waits for it to settle, so you don't have to write the wait-loop yourself:
    #
    #     from smi_plans import goto_temperature, lakeshore_heater   # do this once per session
    #     yield from goto_temperature(lakeshore_heater, 25)          # your target in deg C
    #
    #   (smi_plans also has temperature_ramp_run / isothermal_kinetics_run if you want a whole
    #    measurement-per-temperature in one call. This is optional — your loop below works.)
    # === end smi_plans note ================================================
    t_kelvin = float(temperature) + 273.15
    yield from ls.output1.mv_temp(t_kelvin)

    # Activate heating range in Lakeshore
    #if temperature < 80:
    #   yield from bps.mv(ls.output1.status, 1)
    #else:
    yield from bps.mv(ls.output1.status, 3)

    # Equalise temperature
    print(f"Equalising temperature to {temperature} deg C")
    start = time.time()
    temp = ls.input_A.get()
    while abs(temp - t_kelvin) > 1:
        print("Difference: {:.1f} K".format(abs(temp - t_kelvin)))
        yield from bps.sleep(10)
        temp = ls.input_A.get()

        # Escape the loop if too much time passes
        if time.time() - start > 5400:
            temp = t_kelvin
    print("Time needed to equilibrate: {:.1f} min".format((time.time() - start) / 60))

    # Wait extra time depending on temperature
    if (30 < temperature) and (temperature < 181):
        extra_time = 300
    elif 160 <= temperature:
        extra_time = 420
    else:
        extra_time = 0

    print(f'Equilibrating temperature for extra {extra_time} s\n')
    t_start = time.time()
    while (time.time() - t_start) < extra_time:
        print(f'Pumping time: {(time.time() - t_start):.1f} s')
        yield from bps.sleep(30)


def morozova_giswaxs_temp_2023_2(t=1):
    """
    Grazing incidence measurement using Lakeshore controlled heating bar
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature series of grazing-incidence WAXS/SAXS on a bar of many
    #   samples — for each temperature it visits every sample, aligns it, and takes WAXS (and
    #   SAXS at low arc) images over several WAXS-arc and incident-angle settings.
    #
    # 💡 NEWER, EASIER WAY: this "bar of samples × temperatures × angles" pattern is exactly
    #   what 'smi_plans' multi-sample helpers are for. You list the samples once (positions +
    #   names) and the temperatures, and it walks the bar, aligns each sample, sweeps angle,
    #   and records temperature/angle/beam straight into every image and file name — so you
    #   don't have to build "{name}_{temp}degC_run..." by hand or call sample_id at all.
    #
    #     from smi_plans import SampleList, giwaxs_bar, temperature_axis, align_sample
    #     samples = SampleList.from_columns(                # list your bar once
    #         name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     # then sweep temperature with temperature_axis([26, 40, 55, ...]) and hand the bar
    #     # to giwaxs_bar(..., incident_angles=[0.075, 0.125, 0.175, 0.250], arc=[0, 20],
    #     #               t=t, align=align_sample)
    #
    #   (For a ready-made "GIWAXS while ramping temperature at several spots" recipe, see
    #    smi_plans.recipes_combined.giwaxs_tempramp_energy_5loc. All optional — code below works
    #    as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes on those lines). (internal: Tier 1.)
    # === end smi_plans note ================================================

    names_1   = ['st1-PIL-NO3-10p', 'st2-PIL-NO3-5p', 'st3-PIL-NO3-2.5p', 'st4-PIL-Cl-10p', ]
    piezo_x_1 = [           -40000,           -25000,             -10000,             2600, ]
    piezo_y_1 = [              400,              400,                200,              100, ]         
    piezo_z_1 = [             5700,             5700,               5000,             3900, ]
    hexa_x_1 =  [ 0 for n in names_1]


    names_2   = [ 'st5-PIL-Cl-5p',  'st6-PEO', 'st7-PIL-TFSI-drop', 'st8-PIL-NO3-2.5p-r2', ]
    piezo_x_2 = [           13000,      24000,               37000,                 51000, ]
    piezo_y_2 = [               0,       -100,                -200,                  -400, ] 
    piezo_z_2 = [            4500,       4500,                4500,                  3300, ]
    hexa_x_2 =  [ 0 for n in names_2]

    names   = names_1 + names_2
    piezo_x = piezo_x_1 + piezo_x_2
    hexa_x =  hexa_x_1 + hexa_x_2
    piezo_z = piezo_z_1 + piezo_z_2
    piezo_y = piezo_y_1 + piezo_y_2
    
    lakeshore = True
    temperatures = [26, 40, 55, 70, 85, 100, 115, 130, 145, 100, 85, 60, 30, 85, 30]

    incident_angles = [0.075, 0.125, 0.175, 0.250, ]
    waxs_arc = [0, 20]

    step_across_sample = 200
    user_name = 'SM'
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)

    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_y) == len(piezo_z), msg


    for i, temperature in enumerate(temperatures):
        
        if lakeshore:
            yield from equalise_temperature(temperature)

        for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):

            yield from bps.mv(piezo.x, x + i * step_across_sample,
                              piezo.y, y,
                              piezo.z, z,
                              stage.x, hx)

            # Align the sample
            try:
                yield from alignement_gisaxs()
            except:
                yield from alignement_gisaxs(0.01)

            temp_degC = ls.input_A.get() - 273.15 if lakeshore else temperature

            # Sample flat at ai0
            ai0 = piezo.th.position

            for wa in waxs_arc:
                yield from bps.mv(waxs, wa)
                dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
                
                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)
                    yield from bps.mvr(piezo.x, step_across_sample)

                    temp = str(np.round(float(temp_degC), 1)).zfill(5)
                    sample_name = f'{name}_{temp}degC_run{i}{get_scan_md()}_ai{ai}'
                    sample_name = sample_name.translate(
                        {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
                    )
                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

            waxs_arc = waxs_arc[::-1]

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).

    # Turn off the heating and set temperature to 23 deg C
    t_kelvin = 23 + 273.15
    yield from ls.output1.mv_temp(t_kelvin)
    yield from ls.output1.turn_off()

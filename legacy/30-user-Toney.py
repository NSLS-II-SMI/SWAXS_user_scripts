def zihan_alignment():
    """
    Align sample using hexapod
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the sample on the hexapod (tries a coarse angle, falls back to a finer one).
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment + mode switching as
    #   align_sample, which does the search for you and SAVES the found position with your
    #   data. So a separate start/stop/align helper usually isn't needed:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken — it's just hand-rolled alignment that align_sample packages.)
    # === end smi_plans note ================================================
    #proposal_id('2023_1', '000000_tests')

    try:
        yield from alignement_gisaxs_hex(angle=0.5, rough_y=0.5)
    except:
        yield from alignement_gisaxs_hex(angle=0.1, rough_y=0.5)

    #proposal_id('2023_1', '311645_Zhang')


def zihan_giwaxs_2023_1(t=0.5, name='test', dist='unspecified'):
    """
    GIWAXS measurement on a custom stage mounted on the hexapod
    GU-311645 SAF: 310633

    Manually enter the sample name and the squeeze distance
    """


    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS measurement on a custom hexapod-mounted stage — at two WAXS arcs it
    #   takes WAXS images at a list of incident angles (sample names include the squeeze distance).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    incident_angles = [0.5, 1.5, 4.36,6.2]
    waxs_arc = [0, 20]
    user_name = "ZZ"

    # Sample flat at ai0
    ai0 = stage.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        
        dets = [pil900KW] #if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for ai in incident_angles:
            yield from bps.mv(stage.th, ai0 + ai)

            # Metadata
            e = energy.position.energy / 1000
            sdd = pil2M_pos.z.position / 1000
            wa = waxs.arc.position + 0.001
            wa = str(np.round(float(wa), 1)).zfill(4)

            # Sample name
            name_fmt = "{sample}_{dist}mm_{energy}keV_wa{wax}_sdd{sdd}m_ai{ai}"
            sample_name = name_fmt.format(
                sample=name,
                dist=dist,
                energy="%.2f" % e,
                wax=wa,
                sdd="%.1f" % sdd,
                ai=ai,
            )
            sample_name = sample_name.translate(
                {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =,"}
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    yield from bps.mv(stage.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def turn_off_heating(temp=23):
    """
    Turn off the heating and set temperature to 23 deg C for Lakeshore
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: turns the Lakeshore heater off and sets it back to ~23 deg C.
    # 💡 NEWER, EASIER WAY: the Lakeshore device 'ls' is FINE and still works. In smi_plans you'd
    #   use goto_temperature / lakeshore_heater for setpoints; turning the heater off by hand
    #   like this is fine to keep. (No acquisition happens here.)
    # === end smi_plans note ================================================
    print(f'Setting temp to {temp} deg C and turning off the heater')
    t_kelvin = temp + 273.15
    yield from ls.output1.mv_temp(t_kelvin)
    yield from ls.output1.turn_off()

def align_gisaxs_th_zihan(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment building block — scans the sample tilt (piezo.th) over a small range, finds
    #   the peak, and moves there.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment + mode switching as
    #   align_sample, which does the search for you and SAVES the found position with your
    #   data. So a separate start/stop/align helper usually isn't needed:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken — it's just hand-rolled alignment that align_sample packages.)
    # === end smi_plans note ================================================
    th0 = piezo.th.position
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps(plot=False)
    yield from bps.mv(piezo.th, ps.peak)


def zihan_giwaxs_alignment(angle=0.1, sample_name='test'):
    """
    Quicker alignment
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quicker grazing alignment routine — switches to alignment mode, sets the direct/reflected
    #   beam ROIs, and does height + theta searches to land the sample, then returns to measure mode.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment as align_sample — it does
    #   the height/theta (and direct/reflected ROI) search for you and SAVES the found
    #   position alongside your data, so it isn't lost in a print-out. You typically run it
    #   once per sample or pass align=align_sample to giwaxs_run:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken; det_exposure_time below is the usual exposure caveat — see
    #    its ⚠️ note. The fast shutter / attenuators / beamstop moves still work the same.)
    # === end smi_plans note ================================================
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name=sample_name)
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height(800, 16, der=True)
    yield from align_gisaxs_th_zihan(1.5, 27)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    # Scan theta and height
    yield from align_gisaxs_th_zihan(0.2, 11)
    yield from align_gisaxs_height_rb(150, 16)
    yield from align_gisaxs_th_zihan(0.1, 21) 

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mv(piezo.th, ps.cen - angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def zihan_quick_alignment(angle=0.15):
    """
    Short alignement with only alignement on the reflected beam.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a short grazing alignment that only refines on the reflected beam.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment as align_sample — it does
    #   the height/theta (and direct/reflected ROI) search for you and SAVES the found
    #   position alongside your data, so it isn't lost in a print-out. You typically run it
    #   once per sample or pass align=align_sample to giwaxs_run:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken; det_exposure_time below is the usual exposure caveat — see
    #    its ⚠️ note. The fast shutter / attenuators / beamstop moves still work the same.)
    # === end smi_plans note ================================================
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # move to theta 0 + value
    yield from bps.mvr(piezo.th, angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle)

    # Scan theta and height
    yield from align_gisaxs_height_rb(200, 31)
    yield from align_gisaxs_th_zihan(0.1, 21)

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mv(piezo.th, ps.cen - angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False


def zihan_temperature_giwaxs_2023_1(t=0.5):
    """
    Hard X-ray GIWAXS Lakeshore heating stage.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS run with the Lakeshore heating stage — it ramps to a
    #   list of temperatures, equalises at each, and takes WAXS images at several incident
    #   angles and x offsets per temperature.
    #
    # 💡 NEWER, EASIER WAY: this is GIWAXS combined with a temperature ramp. 'smi_plans' has
    #   both pieces (and the Lakeshore device 'ls' is FINE — no change needed):
    #     from smi_plans import giwaxs_bar, align_sample, lakeshore_heater, temperature_ramp_run
    #   These drive the heater, wait for each setpoint, align each sample, and record the REAL
    #   temperature + incident angle INTO the data and file name (temperature in the data, not
    #   just the file name).
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names =   [ 'CS1', 'CS2', 'CS3', 'CS4', 'CS5', 'CS6', 'CS7', 'CS1S', 'CS2S', 'CS3S', 'CS4S']
    piezo_x = [ 52900,  43950, 32900, 22900, 12900, 2900, -7100, -17100, -28100, -38100, -47100 ]   
    piezo_y = [       -100, -100, -100, -100]
    piezo_z = [4500 for n in names]
    # piezo_z = [4200, 4100, ]

    assert len(names)   == len(piezo_x), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_y), f"Wrong list lenghts"
    assert len(piezo_y) == len(piezo_z), f"Wrong list lenghts"

    user_name = "ZZ"
    temperatures = [#25, 30, 40, 50, 60, 
                    80, 100, 80, 60, 40, 25,
                    40, 60, 80, 100, 120, 140,
                    120, 100, 80, 60, 40, 25] 
    
    waxs_arc = [0, 20]
    incident_angles = [0.50, 1.50, 4.36, 6.20]
    piezo_x_offs = [0, 200, 500]

    ai0 = piezo.th.position

    for p, temperature in enumerate(temperatures):
        t_kelvin = temperature + 273.15
        yield from ls.output1.mv_temp(t_kelvin)

        # Activate heating range in Lakeshore
        if temperature < 50:
            yield from bps.mv(ls.output1.status, 1)
        else:
            yield from bps.mv(ls.output1.status, 3)

        # Equalise temperature
        print(f"Equalising temperature to {temperature:.0f} deg C")
        start = time.time()
        temp = ls.input_A.get()
        while abs(temp - t_kelvin) > 5:
            print("Difference: {:.1f} K".format(abs(temp - t_kelvin)))

            yield from bps.sleep(10)
            temp = ls.input_A.get()
            
            # Escape the loop if too much time passes
            if time.time() - start > 10 * 60:
                temp = t_kelvin
        print(
            "Time needed to equilibrate: {:.1f} min".format((time.time() - start) / 60)
        )

        # Wait extra time depending on temperature
        #if (56 < temperature) and (temperature < 160):
        #    yield from bps.sleep(300)
        #elif 160 <= temperature:
        #    yield from bps.sleep(600)

        # Read T and convert to deg C
        temp_degC = ls.input_A.get() - 273.15

        for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x + p * 200,
                              piezo.y, y,
                              piezo.z, z,
                              piezo.th, ai0)
            # Align sample
            yield from zihan_giwaxs_alignment(0.1)

            # Sample flat at ai0
            ai0 = piezo.th.position

            for wa in waxs_arc:
                yield from bps.mv(waxs, wa)
                dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]
                det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)
                    p=0
                    for i, x_off in enumerate(piezo_x_offs):
                        yield from bps.mv(piezo.x, x + p * 200 + x_off)

                        # Metadata
                        e = energy.position.energy / 1000
                        temp = str(np.round(float(temp_degC), 1)).zfill(5)
                        wa = waxs.arc.position + 0.001
                        wa = str(np.round(float(wa), 1)).zfill(4)
                        sdd = pil2M_pos.z.position / 1000


                        name_fmt = "{sample}_{temp}degC_pos{pos}_{energy}eV_wa{wax}_sdd{sdd}m_ai{ai}"
                        sample_name = name_fmt.format(
                            sample=name,
                            pos = i + 1,
                            energy="%.2f" % e,
                            temp=temp,
                            wax=wa,
                            sdd="%.1f" % sdd,
                            ai = ai,
                        )
                        sample_name = sample_name.translate(
                            {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "}
                        )
                        print(f"\n\n\n\t=== Sample: {sample_name} ===")
                        sample_id(user_name=user_name, sample_name=sample_name)
                        
                        yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

    # Turn off the heating and set temperature to 23 deg C
    yield from turn_off_heating()

def zihan_giwaxs_2023_1(t=0.5):
    """
    Hard X-ray GIWAXS, samples on Lakeshore heating stage but no heating.
    """
   
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS measurement on a custom hexapod-mounted stage — at two WAXS arcs it
    #   takes WAXS images at a list of incident angles (sample names include the squeeze distance).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names =   [  'Si', 'PET']
    piezo_x = [  -41100, -47100 ]   
    piezo_y = [   690, 690]
    piezo_z = [4500 for n in names]
    # piezo_z = [4200, 4100, ]

    assert len(names)   == len(piezo_x), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_y), f"Wrong list lenghts"
    assert len(piezo_y) == len(piezo_z), f"Wrong list lenghts"

    user_name = "ZZ"
    
    waxs_arc = [0, 20]
    incident_angles = [0.5,1.5,4.36,6.2]
    piezo_x_offs = [0]
    temp = 25
    ai0 = piezo.th.position


    for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          piezo.th, ai0)
        # Align sample
        yield from zihan_giwaxs_alignment(0.1)

        # Sample flat at ai0
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)
                
                p=0
                for i, x_off in enumerate(piezo_x_offs):
                    yield from bps.mv(piezo.x, x + p * 200 + x_off)

                    # Metadata
                    e = energy.position.energy / 1000
                    temp = str(np.round(float(temp), 1)).zfill(5)
                    wa = waxs.arc.position + 0.001
                    wa = str(np.round(float(wa), 1)).zfill(4)
                    sdd = pil2M_pos.z.position / 1000


                    name_fmt = "{sample}_{temp}degC_pos{pos}_{energy}eV_wa{wax}_sdd{sdd}m_ai{ai}"
                    sample_name = name_fmt.format(
                        sample=name,
                        pos = i + 1,
                        energy="%.2f" % e,
                        temp=temp,
                        wax=wa,
                        sdd="%.1f" % sdd,
                        ai = ai,
                    )
                    sample_name = sample_name.translate(
                        {ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "}
                    )
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    sample_id(user_name=user_name, sample_name=sample_name)
                    
                    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

def Zihan_wip():
    # smi_plans: work-in-progress scratch loop (just prints temperatures) — no acquisition logic here, nothing to migrate.
    temperatures = [#25, 30, 40, 50, 60, 
            80, 100, 80, 60, 40, 25,
            40, 60, 80, 100, 120, 140,
            120, 100, 80, 60, 40, 25]
    for p, temperature in enumerate(temperatures):
        print(p)
        print(temperature)


def alignment_stage_Zihan_2023_2(angle=1.5, sample_name='test'):
    """
    Alignment for bent samples
    Needs refinement, decided on manual
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a careful manual-style alignment for bent samples — direct then reflected height/theta/x
    #   searches, returning to measurement mode at the end.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment as align_sample — it does
    #   the height/theta (and direct/reflected ROI) search for you and SAVES the found
    #   position alongside your data, so it isn't lost in a print-out. You typically run it
    #   once per sample or pass align=align_sample to giwaxs_run:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken; det_exposure_time below is the usual exposure caveat — see
    #    its ⚠️ note. The fast shutter / attenuators / beamstop moves still work the same.)
    # === end smi_plans note ================================================
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name=sample_name)
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan height direct
    yield from bp.rel_scan([pil2M], stage.y, -0.3, 0.1, 41)
    ps(der=True)
    yield from bps.mv(stage.y, ps.peak)

    # Scan theta direct
    yield from bp.rel_scan([pil2M], stage.th, -3, 3, 31)
    ps()
    yield from bps.mv(stage.th, ps.cen)

    # Scan x direct (sample centre)
    yield from bp.rel_scan([pil2M], stage.x, -2, 2, 21)
    ps()
    yield from bps.mv(stage.th, ps.cen)

    # move to theta 0 + value
    yield from bps.mvr(stage.th, angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    # Scan theta reflected
    yield from bp.rel_scan([pil2M], stage.th, -0.2, 2, 21)
    ps()
    yield from bps.mv(stage.th, ps.peak)

    # Scan height reflected
    yield from bp.rel_scan([pil2M], stage.y, -0.05, 0.05, 21)
    ps(der=True)
    yield from bps.mv(stage.y, ps.peak)

    # Scan theta reflected
    yield from bp.rel_scan([pil2M], stage.th, -0.05, 0.05, 21)
    ps()
    yield from bps.mv(stage.th, ps.peak)

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mvr(stage.th, - angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False


def alignment_start(sample_name='alignment'):
    """
    Attenuators in, beamstop out, ROI1 set to direct beam
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into alignment mode and sets the direct-beam ROI (attenuators in,
    #   beamstop out) — the 'start' half of a manual align.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment + mode switching as
    #   align_sample, which does the search for you and SAVES the found position with your
    #   data. So a separate start/stop/align helper usually isn't needed:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken — it's just hand-rolled alignment that align_sample packages.)
    # === end smi_plans note ================================================
    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    sample_id(user_name='test', sample_name=sample_name)
    #proposal_id('2023_2', '311645_Zhang')


def alignment_start_angle(angle=0.15):
    """
    Attenuators in, beamstop out, ROI1 set to direct beam
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into alignment mode and sets the reflected-beam ROI for a given angle.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment + mode switching as
    #   align_sample, which does the search for you and SAVES the found position with your
    #   data. So a separate start/stop/align helper usually isn't needed:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken — it's just hand-rolled alignment that align_sample packages.)
    # === end smi_plans note ================================================
    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set reflected beam ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")


def alignment_stop():
    """
    Attenuators out, beamstop in,
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline back into measurement mode (attenuators out, beamstop in) — the 'stop'
    #   half of a manual align.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment + mode switching as
    #   align_sample, which does the search for you and SAVES the found position with your
    #   data. So a separate start/stop/align helper usually isn't needed:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken — it's just hand-rolled alignment that align_sample packages.)
    # === end smi_plans note ================================================
    smi = SMI_Beamline()
    yield from smi.modeMeasurement()
    #proposal_id('2023_2', '311645_Zhang_1')


def zihan_giwaxs_2023_2(t=0.5, name='test', dist='unspecified'):
    """
    GIWAXS measurement on a custom stage mounted on the hexapod
    Manually enter the sample name and the squeeze distance
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS measurement — aligns, then takes images at a list of incident angles
    #   across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    incident_angles = [0.5, 1.5, 4.5, 6.5]
    waxs_arc = [0,7,20]
    user_name = "ZZ"

    # Sample flat at ai0
    ai0 = stage.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for ai in incident_angles:
            yield from bps.mv(stage.th, ai0 + ai)

            sample_name = f'{name}_{dist}mm{get_scan_md()}_ai{ai}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    yield from bps.mv(stage.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

    """
    Procedure for manual alignment of bending samples

    get y and x close using cameras

    move z to middle (usuallly z=5)
    
    RE(alignment_start())

    do y scan
    RE(rel_scan([pil2M], stage.y, -0.3, 0.3, 21))
    RE(mv(stage.y, TOPINFLECTION))

    do theta scan
    RE(rel_scan([pil2M], stage.th, -0.5, 0.5, 21)) 
    (larger range for inverted sample)
    RE(mv(stage.th, PEAKCENT))

    do x scan
    RE(mvr(stage.y, 0.05)) 
    (not needed for inverted sample)
    RE(rel_scan([pil2M], stage.x, -1.5, 1.5, 21))
    RE(mv(stage.x, NEGPEAKCENT)) 
    #sometimes there will be two adjacent neg peak, go in the center between them
    RE(mvr(stage.y, -0.05))

    do y scan
    RE(rel_scan([pil2M], stage.y, -0.3, 0.3, 21))
    RE(mv(stage.y, TOPINFLECTION))

    do theta scan
    RE(rel_scan([pil2M], stage.th, -0.2, 0.2, 21))
    RE(mv(stage.th, PEAK))

    optional if you see reflected peak (I think you should):

    # change angle to where you want to align at
    
    RE(alignment_start_angle(angle=0.2))
    RE(mvr(stage.th, 0.2))
    RE(rel_scan([pil2M], stage.th, -0.2, 0.2, 21))
    RE(mv(stage.th, PEAK))
    p

    measure
    RE(alignment_stop())
    RE(zihan_giwaxs_2023_2(...))

    """

def zihan_giwaxs_alignment_2023_2(angle=0.1, sample_name='test'):
    """
    Quicker alignment
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing alignment routine (2023_2 variant) — direct/reflected ROI setup plus height and
    #   theta searches, returning to measurement mode.
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment as align_sample — it does
    #   the height/theta (and direct/reflected ROI) search for you and SAVES the found
    #   position alongside your data, so it isn't lost in a print-out. You typically run it
    #   once per sample or pass align=align_sample to giwaxs_run:
    #     from smi_plans import align_sample
    #     yield from align_sample()             # aligns and records the result
    #   (Nothing here is broken; det_exposure_time below is the usual exposure caveat — see
    #    its ⚠️ note. The fast shutter / attenuators / beamstop moves still work the same.)
    # === end smi_plans note ================================================
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name=sample_name)
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height(2000, 21, der=True)
    yield from align_gisaxs_th_zihan(1.5, 31)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    # Scan theta and height
    yield from align_gisaxs_th_zihan(0.2, 11)
    yield from align_gisaxs_height_rb(150, 16)
    yield from align_gisaxs_th_zihan(0.1, 21) 

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mv(piezo.th, ps.cen - angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False


def zihan_giwaxs_samplebar_2023_2(t=0.5):
    """
    Hard X-ray GIWAXS, samples on regular GI stage
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS run over a bar of samples — aligns each sample, then takes images at
    #   a list of incident angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names =   [   'S8_2' ]
    piezo_x = [  -48000]   
    piezo_y = [   6000]
    piezo_z = [ 4000 for n in names ]
    stage_x = [  -15.5]
    # piezo_z = [4200, 4100, ]

    assert len(names)   == len(piezo_x), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_y), f"Wrong list lenghts"
    assert len(piezo_y) == len(piezo_z), f"Wrong list lenghts"
    assert len(piezo_z) == len(stage_x), f"Wrong list lenghts"

    user_name = "ZZ"
    
    waxs_arc = [0, 15]
    incident_angles = [0.14, 0.16, 0.18, 0.20, 0.21]
    ai0 = piezo.th.position

    unaligned_samples = []


    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, stage_x):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          piezo.th, ai0,
                          stage.x, hx,
        )
        # Align sample

        try:
            yield from zihan_giwaxs_alignment_2023_2(0.1, sample_name=name)
        except:
            unaligned_samples.append(name)
            break
        
        # Sample flat at ai0
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)

                sample_name = f'{name}_{get_scan_md()}_ai{ai}'
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    if unaligned_samples:
        f = RE.md['path'] + '/unaligned_samples.txt'
        with open(f, 'w') as file:
            for row in unaligned_samples:
                s = " ".join(map(str, row))
                file.write(s + '\n')

    yield from bps.mv(piezo.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)



def zihan_giwaxs_2024_1(t=0.5, name='Z1-pvsk_on_ito_2', dist='unspecified'):
    """
    GIWAXS measurement on a custom stage mounted on the hexapod
    Manually enter the sample name and the squeeze distance
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS measurement (2024 perovskite series) — aligns, then takes images at
    #   a list of incident angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    incident_angles = [0.5, 4.5]
    waxs_arc = [0, 20]
    user_name = "ZZ"

    # Sample flat at ai0
    ai0 = stage.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for ai in incident_angles:
            yield from bps.mv(stage.th, ai0 + ai)

            sample_name = f'{name}_{dist}mm{get_scan_md()}_ai{ai}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    yield from bps.mv(stage.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

# Align at each angle and then measure
"""
    Procedure for manual alignment of bending samples

    get y and x close using cameras

    move z to middle (usuallly z=5)
    
    RE(alignment_start())

    do y scan
    RE(rel_scan([pil2M], stage.y, -0.3, 0.3, 21))
    RE(mv(stage.y, TOPINFLECTION))

    do theta scan
    RE(rel_scan([pil2M], stage.th, -0.5, 0.5, 21)) 
    (larger range for inverted sample)
    RE(mv(stage.th, PEAKCENT))

    do x scan
    RE(mvr(stage.y, 0.05)) 
    (not needed for inverted sample)
    RE(rel_scan([pil2M], stage.x, -2, 2, 31))
    RE(mv(stage.x, NEGPEAKCENT)) 
    #sometimes there will be two adjacent neg peak, go in the center between them
    RE(mvr(stage.y, -0.05))

    do y scan
    RE(rel_scan([pil2M], stage.y, -0.3, 0.3, 21))
    RE(mv(stage.y, TOPINFLECTION))

    do theta scan
    RE(rel_scan([pil2M], stage.th, -0.2, 0.2, 31))
    RE(mv(stage.th, PEAK))

    optional if you see reflected peak (I think you should):

    # change angle to where you want to align at
    angle = 0.1

    check for stage.z to move sample back to the beam

    Do the stage.y scan, could be broad
    RE(rel_scan([pil2M], stage.y, -0.3, 0.3, 21))
    RE(mv(stage.y, TOPINFLECTION))
    
    RE(alignment_start_angle(angle=angle))
    RE(mvr(stage.th, angle))
    RE(rel_scan([pil2M], stage.th, -0.2, 0.2, 31)) # could use -1, 1, 31 for larger angles to start with
    RE(mv(stage.th, PEAK))
    RE(mvr(stage.th, -angle))

    measure
    RE(alignment_stop())
    RE(zihan_giwaxs_single_2024_1(...))
"""

def zihan_giwaxs_single_2024_1(t=0.5, name='Z1-pvsk_on_ito_2', dist='unspecified', incident_angles=0.5):
    """
    GIWAXS measurement on a custom stage mounted on the hexapod
    Manually enter the sample name and the squeeze distance
    
    Specify incident angle in the function, angle as aligned
    """


    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single-sample hard-X-ray GIWAXS measurement — aligns, then takes images at the chosen
    #   incident angle(s) across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    waxs_arc = [0, 20]
    user_name = "ZZ"

    # Sample flat at ai0
    ai0 = stage.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for ai in incident_angles:
            yield from bps.mv(stage.th, ai0 + ai)

            sample_name = f'{name}_{dist}mm{get_scan_md()}_ai{ai}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    yield from bps.mv(stage.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def S_edge_measurments_2024_1_Toney(t=4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant sulfur-edge GI-NEXAFS run over Toney's samples — align each, then at the chosen
    #   incident angle(s) and WAXS arc(s) sweep the sulfur-edge energy list (~2445-2550 eV, finely spaced over the edge) up and back.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy (NEXAFS) scan in ONE line and records the energy/beam/incident angle
    #   straight INTO the data and file name (so you can drop the bpm-in-the-name juggling):
    #
    #     from smi_plans import nexafs_run        # do this once at the top of your session
    #     yield from nexafs_run("S_edge_Toney", energies,
    #                           t=t, dets=[pil2M, pil900KW], geometry="transmission")
    #     # (loop over your samples / WAXS arc / incident angle; align_sample aligns each)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are settle
    #    waits you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # names =   ['', '50-blank-redo', '50-teacl-redo', '255-blank-redo', '255-teacl-redo']          
    # x_piezo = [     -31080,          -15080,                 920,           16920,            33920]            
    # x_hexa =  [           0,          0,          0,          0,          0]           
    # y_piezo = [        3250,       3250,       3250,       3250,       3250]
    # z_piezo = [       -10500,     -10500,    -10500,     -10500,      -10500]  

    # names =   ['Si-1', 'Si-2', 'Si-3', 'Si-4', 'Si-5', 'Si-6', 'Si-7', 'Si-8', 'Si-9', 'Si-10', 'Si-11']          
    # x_piezo = [-48870, -36870, -21870, -17370,  -6370,   2630,  12630,  20630,  29630,   38630,   47630]            
    # x_hexa =  [     0,      0,      0,      0,      0,      0,      0,      0,      0,       0,       0]           
    # y_piezo = [  3250,   3250,   3250,   3250,   3250,   3250,   3250,   3250,   3250,    3250,    3250]
    # z_piezo = [-10500, -10500, -10500, -10500, -10500, -10500, -10500, -10500, -10500,  -10500,  -10500]  

    # names =   ['50-blank', '255-blank', '180-blank']          
    # x_piezo = [     -7610,       10390,       34390]            
    # x_hexa =  [         0,           0,           0]           
    # y_piezo = [      3496,        3496,        3496]
    # z_piezo = [     -9000,      -10500,      -12000]  

    # names =   ['Si-1', 'Si-2', 'Si-3', 'Si-4', 'Si-5', 'Si-6', 'Si-7', 'Si-8', 'Si-9', 'Si-10', 'Si-11']          
    # x_piezo = [-48870, -36870, -21870, -17370,  -6370,   2630,  12630,  20630,  29630,   38630,   47630]            
    # x_hexa =  [     0,      0,      0,      0,      0,      0,      0,      0,      0,       0,       0]           
    # y_piezo = [  3250,   3250,   3250,   3250,   3250,   3250,   3250,   3250,   3250,    3250,    3250]
    # z_piezo = [-10500, -10500, -10500, -10500, -10500, -10500, -10500, -10500, -10500,  -10500,  -10500]  

    # names =   ['Si-2', 'Si-3', 'Si-4', 'Si-5', 'Si-6', 'Si-7', 'Si-8', 'Si-9', 'Si-10', 'Si-11']          
    # x_piezo = [-36870, -21870, -17370,  -6370,   2630,  12630,  20630,  29630,   38630,   47630]            
    # x_hexa =  [     0,      0,      0,      0,      0,      0,      0,      0,       0,       0]           
    # y_piezo = [  3250,   3250,   3250,   3250,   3250,   3250,   3250,   3250,    3250,    3250]
    # z_piezo = [-10500, -10500, -10500, -10500, -10500, -10500, -10500, -10500,  -10500,  -10500] 

    # names =   ['Si-4', 'Si-5', 'Si-6', 'Si-7', 'Si-8', 'Si-9', 'Si-10', 'Si-11']          
    # x_piezo = [-17370,  -6370,   2630,  12630,  20630,  29630,   38630,   47630]            
    # x_hexa =  [     0,      0,      0,      0,      0,      0,       0,       0]           
    # y_piezo = [  3250,   3250,   3250,   3250,   3250,   3250,    3250,    3250]
    # z_piezo = [-10500, -10500, -10500, -10500, -10500, -10500,  -10500,  -10500] 

    names =   ['Si-11', 'Si-10', 'Si-9', 'Si-8', 'Si-7', 'Si-6', 'Si-15', 'Si-14', 'Si-13', 'Si-12']          
    x_piezo = [ -33955,  -24956, -15956,  -6956,   1044,  10044,   19043,   28044,   37044,   46044]            
    x_hexa =  [      0,       0,      0,      0,      0,      0,       0,       0,       0,       0]           
    y_piezo = [   9440,    9440,   9440,   9440,   9440,   9440,    9440,    9440,    9440,    9440]
    z_piezo = [ -11500,  -11500, -11500, -11500, -11500, -11500,  -11500,  -11500,  -11500,  -11500]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    # 2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]

    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]

    waxs_arc = [0, 20]
    ai0 = 0
    # ai_list = [0.80]
    ai_list = [1.10]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_doblestack(0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_{t}s_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_{t}s_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)
        

def Cl_edge_measurments_2024_1_Toney(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant chlorine-edge GI-NEXAFS run over Toney's samples — align each, then sweep the
    #   chlorine-edge energy list up and back at the chosen incident angle(s)/WAXS arc(s).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy (NEXAFS) scan in ONE line and records the energy/beam/incident angle
    #   straight INTO the data and file name (so you can drop the bpm-in-the-name juggling):
    #
    #     from smi_plans import nexafs_run        # do this once at the top of your session
    #     yield from nexafs_run("Cl_edge_Toney", energies,
    #                           t=t, dets=[pil2M, pil900KW], geometry="transmission")
    #     # (loop over your samples / WAXS arc / incident angle; align_sample aligns each)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are settle
    #    waits you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names =   ['180-teacl', '50-teacl',  '255-teacl']          
    x_piezo = [-31080,             920,           33920]            
    x_hexa =  [ 0,                0,              0]           
    y_piezo = [3250,              3250,         3250]
                        #-3700,             -3700,               -3700,             -3700,                 -3700,             -3700,               -3700,                 -3700,                  -3700,                   -3700]
    z_piezo = [          -10500,          -10500,      -10500]   #           7000,                7000,                  7000,                   7000,                    7000,                     7000,                     7000,
                         #7000,              7000,                7000,              7000,                  7000,              7000,                       7000,              7000,                  7000,              7000,                7000,                  7000,                   7000,                    7000]

    x_piezo = 2000 + np.asarray(x_piezo)
    
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.asarray([2810.0, 2820.0, 2830.0, 2832.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])
    
    waxs_arc = [0]
    ai0 = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_doblestack(0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)


def waxs_S_edge_chaney_variousprs_2024_1_march(t=8):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant sulfur-edge WAXS scan at various sample-rotation (prs) angles — it parks the
    #   rotation stage at a fixed offset, then for each WAXS arc sweeps the S-edge energies
    #   while stepping y, recording images.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can sweep the energy and the sample rotation as
    #   "axes" in one acquire call (recording both INTO the data + file name), and for a
    #   rocking series there's a dedicated CD-SAXS plan:
    #     from smi_plans import acquire, energy_axis, motor_axis, cdsaxs_rock_run
    #     # e.g. energy_axis(energies) + motor_axis("phi", stage.phi, prs_angles), or
    #     #      cdsaxs_rock_run(name, angles=..., t=t) for a pure rock. Uses stage.phi.
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was removed — it's now
    #   'stage.phi' (set as an offset below); (2) the 'det_exposure_time(...)' calls no
    #   longer set the exposure unless run as a plan (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    prs0 = -1
    yield from bps.mv(prs, prs0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    # names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  35044,   29044,   23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3648,   -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848] 

    # names = ["SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  29044,   23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848]

    # names = ["SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848]

    names = ["SiN-0"]
    x =     [ -31200]
    y =     [  -9948] 
 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]
    
    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs0deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


    yield from bps.mv(prs, prs0+35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    x =     [ -31800,  -25600,  -19700,  -13700,   -7700,   -1700,     4500,    10500,    16700,    22600]
    y =     [  -9948,   -9948,   -9748,  -10148,  -10048,   -9648,    -9748,    -9748,    -9648,    -9748] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())

    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]    

    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs35deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0+55)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    x =     [ -19900,  -14100,   -7900,   -1900,     4100,    10400,    16400,    22300]
    y =     [  -9748,  -10148,  -10048,   -9748,     9748,    -9748,    -9648,    -9748] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
            2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
            2500.0,2510.0,2515.0,2530.0,2550.0]
    
    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs55deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


def S_edge_measurments_2024_1_Toney_shortened(t=4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortened resonant sulfur-edge GI-NEXAFS run over Toney's samples — same idea as the full
    #   version with fewer points/positions.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy (NEXAFS) scan in ONE line and records the energy/beam/incident angle
    #   straight INTO the data and file name (so you can drop the bpm-in-the-name juggling):
    #
    #     from smi_plans import nexafs_run        # do this once at the top of your session
    #     yield from nexafs_run("S_edge_Toney", energies,
    #                           t=t, dets=[pil2M, pil900KW], geometry="transmission")
    #     # (loop over your samples / WAXS arc / incident angle; align_sample aligns each)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are settle
    #    waits you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # names =   ['Si-6', 'Si-7', 'Si-8', 'Si-9', 'Si-10', 'Si-11']          
    # x_piezo = [  2630,  12630,  20630,  29630,   38630,   47630]            
    # x_hexa =  [     0,      0,      0,      0,       0,       0]           
    # y_piezo = [  3250,   3250,   3250,   3250,    3250,    3250]
    # z_piezo = [-10500, -10500, -10500, -10500,  -10500,  -10500]  

    names =   ['Si-16']          
    x_piezo = [ -40956]            
    x_hexa =  [      0]           
    y_piezo = [   9440]
    z_piezo = [ -10500]  

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    # 2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]

    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [1.1]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_doblestack(0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_{t}s_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_{t}s_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)


def waxs_S_edge_chaney_variousprs_2024_1_march_shortened(t=8):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortened resonant sulfur-edge WAXS scan at various sample-rotation (prs) angles — same
    #   idea as the full version with fewer points.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can sweep the energy and the sample rotation as
    #   "axes" in one acquire call (recording both INTO the data + file name), and for a
    #   rocking series there's a dedicated CD-SAXS plan:
    #     from smi_plans import acquire, energy_axis, motor_axis, cdsaxs_rock_run
    #     # e.g. energy_axis(energies) + motor_axis("phi", stage.phi, prs_angles), or
    #     #      cdsaxs_rock_run(name, angles=..., t=t) for a pure rock. Uses stage.phi.
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was removed — it's now
    #   'stage.phi' (set as an offset below); (2) the 'det_exposure_time(...)' calls no
    #   longer set the exposure unless run as a plan (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    prs0 = -1
    yield from bps.mv(prs, prs0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    # names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  35044,   29044,   23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3648,   -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848] 

    # names = ["SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  29044,   23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848]

    # names = ["SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    # y =     [  -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848]

    names = ["SiN-0"]
    x =     [ -31200]
    y =     [  -9948] 
 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]
    
    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs0deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


    yield from bps.mv(prs, prs0+35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    # names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  34544,   28544,   22644,   16643,  10394,     4394,    -1606,    -7855,   -14105,   -19855]
    # y =     [  -3648,   -3648,   -3448,   -3848,  -3848,    -3848,    -3648,    -3848,    -3848,    -3648] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())

    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
                2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
                2500.0,2510.0,2515.0,2530.0,2550.0]    

    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs35deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0+55)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    # names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    # x =     [  33500,   27399,   21549,   15550,    9150,    3149,    -2850,    -9050,   -15300,   -21050]
    # y =     [  -3448,   -3448,   -3248,   -3848,   -3848,   -3848,    -3648,    -3848,    -3848,    -3648] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    energies = [2445.0,2450.0,2455.0,2460.0,2465.0,2470.0,2472.0,2473.0,2474.0,2474.5,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,
            2478.5,2479.0,2479.5,2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,
            2500.0,2510.0,2515.0,2530.0,2550.0]
    
    # waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs55deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


def night_2024_3_25():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book wrapper — it sets the proposal id and runs other plans in
    #   this file in sequence (an S-edge run then a prs-rocking WAXS run).
    # 💡 NEWER, EASIER WAY: nothing to change here itself — once you migrate the plans it
    #   calls (see their own notes), this just chains them. In smi_plans you'd usually build
    #   one sample bar (SampleList) and hand it to a single *_bar plan. proposal_id still
    #   works; the newer plans also fold the proposal/sample info INTO the saved data.
    # === end smi_plans note ================================================
    yield from S_edge_measurments_2024_1_Toney()
    yield from waxs_S_edge_chaney_variousprs_2024_1_march()


def night_2023_1(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book wrapper — it sets the proposal id and runs other plans in
    #   this file in sequence (a Cl-edge night run).
    # 💡 NEWER, EASIER WAY: nothing to change here itself — once you migrate the plans it
    #   calls (see their own notes), this just chains them. In smi_plans you'd usually build
    #   one sample bar (SampleList) and hand it to a single *_bar plan. proposal_id still
    #   works; the newer plans also fold the proposal/sample info INTO the saved data.
    # === end smi_plans note ================================================
    #proposal_id("2023_1", "310999_Richter_2")
    #yield from S_edge_measurments_2023_1_night1(t=1)
    proposal_id("2023_1", "310999_Richter_3")
    #yield from transition_S_Cl_edges()
    yield from Cl_edge_measurments_2023_1_night1(t=1)


def night_2023_3(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book wrapper — it sets the proposal id and runs other plans in
    #   this file in sequence (a Cl-edge run, an edge transition, then an S-edge run).
    # 💡 NEWER, EASIER WAY: nothing to change here itself — once you migrate the plans it
    #   calls (see their own notes), this just chains them. In smi_plans you'd usually build
    #   one sample bar (SampleList) and hand it to a single *_bar plan. proposal_id still
    #   works; the newer plans also fold the proposal/sample info INTO the saved data.
    # === end smi_plans note ================================================
    proposal_id("2023_1", "310999_Richter_9")
    yield from Cl_edge_measurments_2023_1_night3(t=1)
    
    yield from transition_Cl_S_edges()

    proposal_id("2023_1", "310999_Richter_10")
    yield from S_edge_measurments_2023_1_night3(t=1)



def transition_Cl_S_edges():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the energy DOWN from the chlorine edge to the sulfur edge — it just steps the X-ray energy down/up in stages with a short
    #   pause at each, to gently move between edges (no images are taken here).
    # 💡 NEWER, EASIER WAY: 'smi_plans' moves the energy safely for you with move_energy_fb
    #   (it steps in <=50 eV hops, settles, manages the beam feedback, and re-seeks if the
    #   beam dips), so this hand-stepped walk with sleeps isn't needed:
    #     from smi_plans import move_energy_fb
    #     yield from move_energy_fb(2450)      # one call does the whole staged move
    #   (Nothing here is broken; the 💡 lines are settle waits you can simply delete.)
    # === end smi_plans note ================================================
    yield from bps.mv(energy, 2800)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2780)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2760)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2740)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2720)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2700)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2680)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2660)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2640)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2610)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2580)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2550)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2525)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2500)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2475)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2450)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)


def transition_S_Cl_edges():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the energy UP from the sulfur edge to the chlorine edge — it just steps the X-ray energy down/up in stages with a short
    #   pause at each, to gently move between edges (no images are taken here).
    # 💡 NEWER, EASIER WAY: 'smi_plans' moves the energy safely for you with move_energy_fb
    #   (it steps in <=50 eV hops, settles, manages the beam feedback, and re-seeks if the
    #   beam dips), so this hand-stepped walk with sleeps isn't needed:
    #     from smi_plans import move_energy_fb
    #     yield from move_energy_fb(2450)      # one call does the whole staged move
    #   (Nothing here is broken; the 💡 lines are settle waits you can simply delete.)
    # === end smi_plans note ================================================
    yield from bps.mv(energy, 2450)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2475)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2500)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2525)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2550)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2580)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2610)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2640)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2660)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2680)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2700)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2720)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2740)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2760)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2780)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2800)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

def transition_Cl_high_edges():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the energy UP from 2800 to 2880 eV — it just steps the X-ray energy down/up in stages with a short
    #   pause at each, to gently move between edges (no images are taken here).
    # 💡 NEWER, EASIER WAY: 'smi_plans' moves the energy safely for you with move_energy_fb
    #   (it steps in <=50 eV hops, settles, manages the beam feedback, and re-seeks if the
    #   beam dips), so this hand-stepped walk with sleeps isn't needed:
    #     from smi_plans import move_energy_fb
    #     yield from move_energy_fb(2450)      # one call does the whole staged move
    #   (Nothing here is broken; the 💡 lines are settle waits you can simply delete.)
    # === end smi_plans note ================================================
    yield from bps.mv(energy, 2800)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2830)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2850)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2880)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
   
def NEXAFS_P_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a phosphorus-edge NEXAFS scan at WAXS 45 deg — sweeps energies (2130-2180) while tracking
    #   the xbpm3 height, taking a WAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy (NEXAFS) scan in ONE line and records the energy/beam/incident angle
    #   straight INTO the data and file name (so you can drop the bpm-in-the-name juggling):
    #
    #     from smi_plans import nexafs_run        # do this once at the top of your session
    #     yield from nexafs_run("NEXAFS_s3_test_Pedge_nspot1", np.linspace(2130, 2180, 51),
    #                           t=t, dets=[pil900KW], geometry="transmission")
    #     # (loop over your samples / WAXS arc / incident angle; align_sample aligns each)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are settle
    #    waits you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 45)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_s3_test_Pedge_nspot1"

    energies = np.linspace(2130, 2180, 51)
    xbpm3_y = np.linspace(1.42, 1.40, 51)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e, xbpm3_ys in zip(energies, xbpm3_y):
        yield from bps.mv(energy, e)
        yield from bps.mv(xbpm3_pos.y, xbpm3_ys)

        yield from bps.sleep(1)

        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm2.sumX.value
        )
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


def P_edge_measurments_2024_1_Toney(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant phosphorus-edge GI-NEXAFS run — align, then sweep the P-edge energies (2120-2190)
    #   while also tracking xbpm3 height, up the energy list.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy (NEXAFS) scan in ONE line and records the energy/beam/incident angle
    #   straight INTO the data and file name (so you can drop the bpm-in-the-name juggling):
    #
    #     from smi_plans import nexafs_run        # do this once at the top of your session
    #     yield from nexafs_run("P_edge_Toney", np.linspace(2120, 2190, 26),
    #                           t=t, dets=[pil2M, pil900KW], geometry="transmission")
    #     # (loop over your samples / WAXS arc / incident angle; align_sample aligns each)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are settle
    #    waits you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names =   [ '180-tbapf6-th9.24' ]          
    x_piezo = [       -28750 ]            
    x_hexa =  [            0 ]           
    y_piezo = [         3000 ]
    z_piezo = [       -10500]  


    # names =   ['50-tbapf6', '180-tbapf6', '255-tbapf6']          
    # x_piezo = [     -45750,       -28750,        -8750]            
    # x_hexa =  [          0,            0,            0]           
    # y_piezo = [       3000,         3000,         3000]
    # z_piezo = [     -10500,       -10500,       -10500]  

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    
    energies = np.linspace(2120, 2190, 26)#2170 - 1.78, 2150 - 1.79, 
    #2130 - bpmx -0.54 bpmy 2.08
    #2120 -                 2.12
    #2150 -                 2.06
    #2160 -                 2.07
    #2170
    #2180 - 
    #2190 -                 2.04
    xbpm3_y = np.linspace(2.12, 2.04, 26)

    waxs_arc = [0]
    ai0 = 0
    ai_list = [7.24]
    stage_th_0 = 0
    stage_th_offset = 2

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from bps.mv(stage.th,stage_th_0)
        yield from alignement_gisaxs_doblestack(0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                yield from bps.mv(stage.th, stage_th_offset)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                for e, xbpm3_ys in zip(energies, xbpm3_y):
                    yield from bps.mv(energy, e)
                    yield from bps.mv(xbpm3_pos.y, xbpm3_ys)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e, xbpm3_ys in zip(energies[::-1], xbpm3_y[::-1]):
                    yield from bps.mv(energy, e)
                    yield from bps.mv(xbpm3_pos.y, xbpm3_ys)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.mv(xbpm3_pos.y, xbpm3_ys)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs + counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="CD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)
            yield from bps.mv(stage.th, stage_th_0)

def grazing_swaxs_2024_2(t=1):
    """
    standard GI-S/WAXS
    """
    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a standard grazing-incidence SAXS+WAXS run over a couple of samples — aligns each (with a
    #   try/except so a failed align doesn't stop the run), then takes images at a few incident
    #   angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names   = [  'FH02_reanneal_4h',  'FH03_reanneal_4h']
    piezo_x = [ -8500,   47000]
    piezo_y = [   2000 for n in names ]          
    piezo_z = [   3300,   3300   ]
    hexa_x =  [  -7.7,  -8.22]
    
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    waxs_arc = [ 0, 20 ]
    x_off = [0]
    incident_angles = [ 0.5, 2.25, 4.5]
    user_name = 'ZZ'

    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):

        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          stage.x, hx)

        # Align the sample
        try:
            yield from alignement_gisaxs(0.1) #0.1 to 0.15
        except:
            print('\n\n\n\n\n\n\n\n\n\nCould not align, remeasure!!!\n\n\n\n\n\n\n\n\n\n')

        # Sample flat at ai0
        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            yield from bps.mv(waxs.bs_y, -3)

            for xx, x_of in enumerate(x_off):
                yield from bps.mv(piezo.x, x + x_of)
                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)

                    sample_name = f'{name}{get_scan_md()}_loc{xx}_ai{ai}'

                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

def grazing_swaxs_2024_2_bg(t=1):
    """
    standard GI-S/WAXS
    """
    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a background grazing SAXS+WAXS run (empty copper stage spots) — same structure as the
    #   sample run, used to record backgrounds.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names   = [  'Copper_stage_bg1',  'Copper_stage_bg2']
    piezo_x = [ 2000,   38000]
    piezo_y = [   1200 for n in names ]          
    piezo_z = [   3300,   3300   ]
    hexa_x =  [  -8.22,  -8.22]
    
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    waxs_arc = [ 0, 20 ]
    x_off = [0]
    incident_angles = [ 0.5, 2.25, 4.5]
    user_name = 'ZZ'

    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):

        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          stage.x, hx)

        # Align the sample
        try:
            yield from alignement_gisaxs(0.1) #0.1 to 0.15
        except:
            print('\n\n\n\n\n\n\n\n\n\nCould not align, remeasure!!!\n\n\n\n\n\n\n\n\n\n')

        # Sample flat at ai0
        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            yield from bps.mv(waxs.bs_y, -3)

            for xx, x_of in enumerate(x_off):
                yield from bps.mv(piezo.x, x + x_of)
                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)

                    sample_name = f'{name}{get_scan_md()}_loc{xx}_ai{ai}'

                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def zihan_giwaxs_line_samplebar_2024_3(t=0.5):
    """
    Hard X-ray GIWAXS, samples on regular GI stage
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray GIWAXS run on the GI stage — aligns each sample (logging any that fail to a
    #   text file) and takes images at a list of incident angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   grazing-incidence (GIWAXS) measurement for you. It aligns each sample, sweeps the
    #   incident angle (and WAXS arc), and records angle/position/beam INTO the data and
    #   into the file name (so you can drop the by-hand get_scan_md()/name building):
    #
    #     from smi_plans import giwaxs_run, align_sample, giwaxs_bar, SampleList
    #     yield from giwaxs_run(name, incident_angles=incident_angles, waxs_arcs=waxs_arc,
    #                           dets=[pil900KW, pil2M], t=t, align=align_sample)
    #     # (or giwaxs_bar(SampleList.from_columns(...)) to run a whole bar of samples)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    names =   [ 'ZZ_Reannal_1p5h_01']
    piezo_x = [  -43000]  # -43000, -800 , 40500
    piezo_y = [  2600]
    piezo_z = [ 0 for n in names ]
    # stage_x = [  -11, ..., 0, 0, 0, ..., 11]
    stage_x = [0 for n in names ]
    # piezo_z = [4200, 4100, ]

    msg = "Wrong number of coordinates"
    assert len(names)   == len(piezo_x), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_y) == len(piezo_z), msg
    assert len(piezo_z) == len(stage_x), msg

    user_name = "ZZ"
    ai0 = piezo.th.position
    waxs_arc = [0, 7, 20]
    incident_angles = [0.5,1.5,3,4.5]
    # x_off = np.arange(0, 25 * 20 + 1, 25) - 250
    # x_off = [-250, -225, -200, -175, -150, -125, -100,  -75,  -50,  -25,    0,
    #            25,   50,   75,  100,  125,  150,  175,  200,  225,  250]
    # x_off = [-250,   -150,-50,0,50,  150,  250]
    x_off=[0]
    unaligned_samples = []


    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, stage_x):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          piezo.th, ai0,
                          stage.x, hx,
        )
        # Align sample
        try:
            yield from alignement_gisaxs(0.1)
        except:
            unaligned_samples.append(name)
            print('\n\n\n\Could not align, remeasure!!!\n\n\n')
            break
        
        # Sample flat at ai0
        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]

            for xx, x_of in enumerate(x_off):
                yield from bps.mv(piezo.x, x + x_of)

                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)

                    sample_name = f'{name}_{get_scan_md()}_loc{xx}_ai{ai}'
                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

    if unaligned_samples:
        f = RE.md['path'] + '/unaligned_samples.txt'
        with open(f, 'w') as file:
            for row in unaligned_samples:
                s = " ".join(map(str, row))
                file.write(s + '\n')

    yield from bps.mv(piezo.th, ai0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

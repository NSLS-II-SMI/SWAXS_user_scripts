
def Cl_edge_measurments_2025_3_thursdaynight_preset():
    #Sample list for Cl edge measurements on Thursday night 2025-03
    names = ['P3HT_undoped',  'P3HT_magicblue_topdope',  'P3HT_magicblue_overdope',   'P3MEEET_undoped', 'P3MEEET_magicblue_topdope',   'P3MEEET_magicblue_overdope', 'PVC_36nm', ' NaPSS_30nm', 'P3HT_37nm']
    x_piezo = [      -56000,                    -45000,                     -40000,              -25000,                    -10000,                             8000,         23000,      44000,       46000]
    x_hexa = [          -16,                       -10,                          0,                   0,                        -0,                                0,             0,          0,          13]          
    y_hexa = [            0,                         0,                          0,                   0,                         0,                                0,             0,          0,           0]
    y_piezo = [        4250,                      4000,                       4000,                4000,                      4000,                             4000,           4000,      4000,        4000]
    z_piezo = [           0,                         0,                          0,                   0,                         0,                                0,              0,         0,           0]
    energies = -11 + np.asarray([2810.0, 2820.0, 2828.0, 2829.0, 2830.0, 2831.0, 2832.0, 2833.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])

    waxs_arc = [7]
    ai0_all = 0
    ai_list = [1.6, 3.2]
    x_step = 30
    yield Cl_edge_gi_scan_smaract_updownsweep(t=1, names=names, x_piezo=x_piezo, y_piezo=y_piezo, z_piezo=z_piezo, x_hexa=x_hexa, y_hexa=y_hexa, \
                    dets=[pil900KW], energies=energies, waxs_arc=waxs_arc, ai0_all=ai0_all, ai_list=ai_list, x_step=x_step)




def Cl_edge_gi_scan_smaract_updownsweep(t=1, names=['name1'], x_piezo=[0], y_piezo=[0], z_piezo=[0], x_hexa=[0], y_hexa=[0], \
                                        dets=[pil900KW], energies=[2800], waxs_arc=[0], ai0_all=0, ai_list=[1.6], x_step=30,
                                        atts=[att2_9],):
    # General function for Cl edge grazing incidence scans with up and down energy sweeps using the smaract
    # and hexapod stages
    # names: list of sample names
    # x_piezo, y_piezo, z_piezo: lists of piezo coordinates
    # x_hexa, y_hexa: lists of hexapod coordinates
    # dets: list of detectors
    # energies: list of energies to scan at the Cl edge
    # waxs_arc: list of WAXS detector positions
    # ai0_all: incident angle offset for the alignment (usually 0)
    # ai_list: list of incident angles to measure at
    # x_step: step size in x in microns for each energy point to limit beam damage
    # atts: list of attenuators to use

    det_exposure_time(t, t)

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(y_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_hexa)})"

    if pil2M in dets:
        saxsmode=True
    else:
        saxsmode=False

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):

        yield from bps.mv(stage.x, xs_hexa,
                          stage.y, ys_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)

        yield from alignement_gisaxs_doblestack(0.7)

        if not saxsmode:
            print("SAXS detector is not chosen, closing its gate valve")
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
        else:  
            print("SAXS detector is chosen, leaving GV7 open,\n\
                   Be sure reflected beam is not hitting the detector!")


        for att in atts:
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)


        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        incident_angle = Signal(name='incident_angle', value=ai0)
        energy_direction = Signal(name='energy_direction', value='upsweep')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'Cl_edge_gi_scan_smaract_updownsweep', 'sample_name': name, 'geometry': 'reflection'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                yield from bps.mv(piezo.x, xs)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)
                    incident_angle.put(ais)
                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        yield from bps.mv(piezo.x, xs + counter * x_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        energy_direction.put('upsweep')
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle, energy_direction])


                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        yield from bps.mv(piezo.x, xs + counter * x_step)
                        counter += 1

                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        energy_direction.put('downsweep')
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle, energy_direction])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def Cl_edge_gi_scan_hexapod_updownsweep(t=1, names=['name1'], x_hexa=[0], y_hexa=[0], dets=[pil900KW], 
                                        energies=[2800], waxs_arc=[0], ai0_all=0, ai_list=[1.6], x_step=0.03, 
                                        atts=[att2_9],):
    # General function for Cl edge grazing incidence scans with up and down energy sweeps using the hexapod 
    # stage
    # names: list of sample names
    # x_piezo, y_piezo, z_piezo: lists of piezo coordinates
    # x_hexa, y_hexa: lists of hexapod coordinates
    # dets: list of detectors
    # energies: list of energies to scan at the Cl edge
    # waxs_arc: list of WAXS detector positions
    # ai0_all: incident angle offset for the alignment (usually 0)
    # ai_list: list of incident angles to measure at
    # x_step: step size in x in microns for each energy point to limit beam damage
    # atts: list of attenuators to use

    det_exposure_time(t, t)

    assert len(x_hexa) == len(names), f"Number of X coordinates ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(x_hexa) == len(y_hexa), f"Number of X coordinates ({len(x_hexa)}) is different from number of samples ({len(y_hexa)})"

    if pil2M in dets:
        saxsmode=True
    else:
        saxsmode=False

    for name, xs_hexa, ys_hexa in zip(names, x_hexa, y_hexa):

        yield from bps.mv(stage.x, xs_hexa,
                          stage.y, ys_hexa)

        yield from bps.mv(stage.th, ai0_all)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)

        yield from alignement_gisaxs_hex(0.7)

        if not saxsmode:
            print("SAXS detector is not chosen, closing its gate valve")
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
        else:  
            print("SAXS detector is chosen, leaving GV7 open,\n\
                   Be sure reflected beam is not hitting the detector!")


        for att in atts:
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)


        ai0 = stage.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        incident_angle = Signal(name='incident_angle', value=ai0)
        energy_direction = Signal(name='energy_direction', value='upsweep')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'Cl_edge_gi_scan_hexapod_updownsweep', 'sample_name': name, 'geometry': 'reflection'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                yield from bps.mv(stage.x, xs_hexa)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(stage.th, ai0 + ais)
                    incident_angle.put(ais)
                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)

                        yield from bps.mv(stage.x, xs_hexa + counter * x_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        energy_direction.put('upsweep')
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle, energy_direction])


                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)

                        yield from bps.mv(stage.x, xs_hexa + counter * x_step)
                        counter += 1

                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        energy_direction.put('downsweep')
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle, energy_direction])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())


def S_edge_trans_scan_hor_smaract(t=1, names=['name1'], x_piezo=[0], y_piezo=[0], z_piezo=[0], x_hexa=[0], y_hexa=[0], \
                                  dets=[pil900KW], energies=[2400], waxs_arc=[0], ai0_all=0, ai_list=[1.6], x_step=30,
                                  atts=[att2_9],):
    # General function for S edge grazing incidence scans samples horizontal with energy upsweep only
    # names: list of sample names
    # x_piezo, y_piezo, z_piezo: lists of piezo coordinates
    # x_hexa, y_hexa: lists of hexapod coordinates
    # dets: list of detectors
    # energies: list of energies to scan at the S edge
    # waxs_arc: list of WAXS detector positions
    # ai0_all: incident angle offset for the alignment (usually 0)
    # ai_list: list of incident angles to measure at
    # x_step: step size in x in microns for each energy point to limit beam damage
    # atts: list of attenuators to use

    det_exposure_time(t, t)

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(y_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_hexa)})"

    if pil2M in dets:
        saxsmode=True
    else:
        saxsmode=False

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):

        yield from bps.mv(stage.x, xs_hexa,
                          stage.y, ys_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)

        yield from alignement_gisaxs_doblestack(0.7)

        if not saxsmode:
            print("SAXS detector is not chosen, closing its gate valve")
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
        else:  
            print("SAXS detector is chosen, leaving GV7 open,\n\
                   Be sure reflected beam is not hitting the detector!")


        for att in atts:
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        incident_angle = Signal(name='incident_angle', value=ai0)

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'S_edge_gi_scan_horizontal_smaract_upsweep', 'sample_name': name, 'geometry': 'reflection'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                yield from bps.mv(piezo.x, xs)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)
                    incident_angle.put(ais)
                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        yield from bps.mv(piezo.x, xs + counter * x_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle])

                    yield from bps.mv(energy, 2500)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 2480)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 2445)

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def S_edge_trans_scan_ver_smaract(t=1, names=['name1'], x_piezo=[0], y_piezo=[0], z_piezo=[0], x_hexa=[0], 
                                  y_hexa=[0], dets=[pil900KW], energies=[2400], waxs_arc=[0], ai0_all=0,
                                  ai_list=[1.6], y_step=30, atts=[att2_9],):
    # General function for S edge grazing incidence scans samples vertical with energy upsweep only
    # names: list of sample names
    # x_piezo, y_piezo, z_piezo: lists of piezo coordinates
    # x_hexa, y_hexa: lists of hexapod coordinates
    # dets: list of detectors
    # energies: list of energies to scan at the S edge
    # waxs_arc: list of WAXS detector positions
    # ai0_all: incident angle offset for the alignment (usually 0)
    # ai_list: list of incident angles to measure at
    # x_step: step size in x in microns for each energy point to limit beam damage
    # atts: list of attenuators to use

    det_exposure_time(t, t)

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(y_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_hexa)})"

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):

        yield from bps.mv(stage.x, xs_hexa,
                          stage.y, ys_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)

        yield from alignement_xrr_xmotor(0.1)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)


        for att in atts:
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)

        ai0 = prs.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        incident_angle = Signal(name='incident_angle', value=ai0)

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'S_edge_gi_scan_vertical_smaract_upsweep', 'sample_name': name, 'geometry': 'reflection'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                if wa < 17:
                    print("WAXS position is too low, reflexcted beam will hit the detctor")
                    wa = 17
                yield from bps.mv(waxs, wa)
                yield from bps.mv(piezo.x, ys)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(prs, ai0 - ais)
                    incident_angle.put(ais)
                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        yield from bps.mv(piezo.x, ys + counter * y_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + atts + [s, incident_angle])

                    yield from bps.mv(energy, 2500)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 2480)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 2445)

                yield from bps.mv(prs.position, ai0)

        (yield from inner())


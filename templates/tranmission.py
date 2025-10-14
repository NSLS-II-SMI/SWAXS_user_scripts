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

def test_multi_transmission():
    names = ['test1', 'test2']
    x_piezo = [0, 1000]
    y_piezo = [0, 0]
    z_piezo = [0, 0]
    waxs_arc = [0, 20]
    points_x_piezo = 10
    points_y_piezo = 2

    yield from multi_transmission(t=1, names=names, 
                                  piezo_x=x_piezo, 
                                  piezo_y=y_piezo, piezo_z=z_piezo, 
                                  waxs_arc=waxs_arc,
                                  points_x_piezo=points_x_piezo,
                                  points_y_piezo=points_y_piezo)

def multi_transmission(t=1,names=[''],
                       piezo_x=None,
                       piezo_y=None,
                       piezo_z=None,
                       stage_x=None,
                       stage_y=None,
                       stage_z=None,
                       waxs_arc=[0,20], 
                       points_x_stage=1,
                       points_y_stage=5,
                       dy_stage=0.15,
                       dx_stage=0.15,
                       points_x_piezo=1,
                       points_y_piezo=1,
                       dy_piezo=30,
                       dx_piezo=300,
                       direct_beam_x=14.2,
                       direct_beam_y=0):
    """
    TODO:  make stage and piezo optional, only one of them is needed
    Multi sample transmission measurement
    Hard X-ray WAXS and SAXS
    Measure transmission only during the first run
    use hexapod only
    """
    s = Signal(name='target_file_name', value='')
    get_trans=False

    msg = "Wrong number of coordinates"
    # If piezo or stage coordinates are None, populate with current positions
    if stage_x is None:
        stage_x = [stage.x.position] * len(names)
    if stage_y is None:
        stage_y = [stage.y.position] * len(names)
    if stage_z is None:
        stage_z = [stage.z.position] * len(names)
    if piezo_x is None:
        piezo_x = [piezo.x.position] * len(names)
    if piezo_y is None:
        piezo_y = [piezo.y.position] * len(names)
    if piezo_z is None:
        piezo_z = [piezo.z.position] * len(names)

    for arr in [stage_x, stage_y, stage_z, piezo_x, piezo_y, piezo_z]:
        assert len(arr) == len(names), msg

    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW, pin_diode]
        
  # removed getting direct beam transmission on first angle non 0
  # going to direct_beam_x and direct_beam_y
        for name, x, y, z, px, py, pz in zip(names, stage_x, stage_y, stage_z, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(stage.x, x,
                              stage.y, y,
                              stage.z, z,
                              piezo.x, px,
                              piezo.y, py,
                              piezo.z, pz)

            # Scan along the capillary
            @bpp.stage_decorator(dets)
            @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'multi_hexapod_swaxs', 'sample_name': name, 'geometry': 'transmission'})
            def inner():
                expnum = 0
                for i in range(points_y_stage):
                    for j in range(points_x_stage):
                        for k in range(points_y_piezo):
                            for l in range(points_x_piezo):
                                new_y = y + i * dy_stage
                                new_x = x + j * dx_stage
                                new_py = py + k * dy_piezo
                                new_px = px + l * dx_piezo
                                yield from bps.mv(piezo.x, new_px,
                                                  piezo.y, new_py, 
                                                  stage.x, new_x,
                                                  stage.y, new_y)
                                expnum += 1
                                    # if (get_trans and i == 0):
                                    #     # Take transmission measurement
                                    #     yield from atten_move_in()

                                    #     # Sample
                                    #     yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 10)
                                    #     sample_id(user_name='test', sample_name='test')
                                    #     yield from bp.count([pil2M,pin_diode])
                                    #     stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                                    #     # Transmission
                                    #     trans = np.round( stats1_sample / stats1_direct, 5)

                                    #     # Revert configuraton
                                    #     yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                                    #     yield from atten_move_out()
                                    

                                trans = 0
                                    # todo: add transmission measurement here if needed

                                # Take normal scans
                                sample_name = f'{name}{get_scan_md()}_loc{expnum}_trs{trans}'
                                print(f"\n\t=== Sample: {sample_name} ===\n")
                                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, stage, piezo] + [s])
            (yield from inner())
    det_exposure_time(0.5, 0.5)



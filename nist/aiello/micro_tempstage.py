


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



def run_nist_linescans(t=0.5):
    """
    Microfocusing line scans along y axis, set y_range for each sample
    """
    
    # names =   ['PET1000_b','PET1000_c','PET1500_a','PET1500_b',    'PET1500_c','PET2000_a',   'PET2000_b',   'PET2000_c', 'PET3000_a',  'PET3000_b',   'PET3000c',    'PET4000a',    'PET4000b', 'PET4000c',  'PET0redo_a',  'PET0redo_b', 'PET0redo_c','PET4000S_a', 'PET4000S_b', 'PET4000S_c','PET3000S_a',   'PET3000S_b', 'PET3000S_c', 'PET2000S_a',  'PET2000S_b',  'PET2000S_c', 'PET1500S_a',  'PET1500S_b', 'PET1500S_c',  'PET1000S_a','PET1000S_b', 'PET1000S_c',  'PET500S_a', 'PET500S_b', 'PET500S_c',    'PET250S_a',   'PET250S_b', 'PET250S_c']
    # piezo_x = [   26600,    26000,          18000,       15500,         14000,       5750 ,          3250,         1750,        -2650,        -5650,        -8150,       -14650,         -17150,     -18650,        -23850,        -27350,       -30350,      -17350,       -15350,       -13350,       -7850,          -5350,        -2850,        1650,           4150,          7650,        12650,          15150,       17650,         22150,       25150,        28150,        34150,       36150,        38150,         44150,         46150,        48150]
    # piezo_y = [   -7490,    -7470,          -7400,       -7400,         -7400,      -7170,          -7080,        -7010,        -6900,        -6820,        -6760,        -6930,          -6730,      -6640,         -6810,         -6660,        -6570,        6060,         6040,         5940,        5720,           5660,         5660,        5820,           5820,          5680,         5660,          5670,         5650,         5410,         5410,         5380,         5320,        5290,        5240,           5360,          5320,        5320]

    # Bar 4: 1-15
    #                    1                2                3              4               5             6             7                 8               9             10              11            12          13           14         15
    # names =   ['180_100_100_N1_c','210_100_100_N1','240_100_100_N1','180_10_N1','210_30prob10_N1','240_10_N1','180_100_100_N2','210_100_100_N2','240_100_100_N2','180_10_N2','210_30prob10_N2','240_10_N2','180_30_PP','210_30_PP','240_30_PP']
    # piezo_x = [     48150,              42650,          37550,        32450,        26450,          20950,          15450,          9750,           4050,           -1750,          -7850,      -13450,     -18950,     -24450,       -29950]
    # piezo_y = [     -850,               -780,           -655,         -655,         -740,           -445,           -115,          -175,            -165,           -380,           -300,       -160,       260,        330,            520]

    # Bar 3: 13-18       
    #                   13                 14               15             16          17          18
    # names =   ['180_100_100_PP_c','210_100_100_PP','240_100_100_PP','180_10_PP','210_10_PP','240_10_PP']
    # piezo_x = [     -10650,            -15650,          -20650,        -25650,     -31050,     -36450]
    # piezo_y = [       340,               680,             110,           120,        170,        465]
    
    #names =   ['180_100_100_PP_c','210_100_100_PP','240_100_100_PP','180_10_PP','210_10_PP','240_10_PP']
    #piezo_x = [-10650,-15650,-20650,-25650,-31050,-36450]
    #piezo_y = [340,680,110,120,170,465]

    names =   ['AAA0_a',   'AAA0_b',      'AAA250',    'AAA500',    'AAA1000',     'AAA1500',  'AAA2000_a', 'AAA2000_b',  'AAA3000_a',  'AAA3000_b',   'AAA4000_a', 'AAA4000_b',      'PP75C',        'PP0',  'AAA4000s_a', 'AAA4000s_b', 'AAA3000s_a', 'AAA3000s_b',   'AAA2000s',   'AAA1500s',   'AAA1000s',    'AAA500s',    'AAA250s']
    piezo_x = [   47245,      45245,          35245,      24745,        13745,          1945,        -7055,       -9555,           -25555,   -27555,        -35555,      -37555,       -36055,       -26055,        -17055,       -15055,        -6055,        -2055,         6945,        16945,        26945,        36945,        46945]
    piezo_y = [   -7500,      -7500,          -7500,      -7460,        -6840,          -7150,       -6920,       -6860,            -6320,     -6360,        -6320,       -6300,         6400,        6040,           5680,        5680,          5860,         5840,         5940,        5720,          5220,         5260,         5020]
    
    y_ranges = [
        [0, 500, 101], [0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101], [0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],[0, 500, 101],
    ]
        
    msg = "Wrong number of coordinates in lists, check names, piezos, etc"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(y_ranges), msg

    user_name = "AA"
    waxs_arc = [0, 20]

    # Direct beam coordinates
    dbeam_x = 18000
    dbeam_y = -900
    stats1_direct = 1



    # beamstop x position on SAXS
    bs_pos = 2.2
    yield from atten_move_out()
    yield from bps.mv(pil1m_bs_rod.x, bs_pos)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil1M, pil900KW]
        det_exposure_time(t, t)

        condition = ( 19 < waxs.arc.position ) and ( waxs.arc.position < 21 )

        # Take direct beam readout for transmission caluclation
        if condition:
            yield from atten_move_in()
            yield from bps.mv(piezo.x, dbeam_x,
                              piezo.y, dbeam_y,
                              pil1m_bs_rod.x, bs_pos + 5)
            
            sample_name = f'empty-attn-direct'
            sample_id(user_name='test', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count([pil1M])
            stats1_direct = db[-1].table(stream_name='primary')['pil1M_stats1_total'].values[0]

            yield from bps.mv(pil1m_bs_rod.x, bs_pos)
            yield from atten_move_out()
        
        # Measure samples
        for name, x, y, y_r in zip(names, piezo_x, piezo_y, y_ranges):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,)

            # Take transmission data
            if condition:
                yield from atten_move_in()
                yield from bps.mv(piezo.y, y + y_r[1] / 2,
                                  pil1m_bs_rod.x, bs_pos + 5,)

                sample_name = f'{name}-attn-sample'
                sample_id(user_name='test', sample_name=sample_name)
                print(f"\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count([pil1M])
                stats1_sample = db[-1].table(stream_name='primary')['pil1M_stats1_total'].values[0]
                
                # Transmission
                trans = np.round( stats1_sample / stats1_direct, 5)

                # Revert configuraton
                yield from bps.mv(pil1m_bs_rod.x, bs_pos,
                                  piezo.y, y,)
                yield from atten_move_out()
            else:
                trans = 0
            
            # Take sample y scan
            sample_name = f'{name}{get_scan_md()}_trs{trans}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.rel_scan(dets, piezo.y, *y_r)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)

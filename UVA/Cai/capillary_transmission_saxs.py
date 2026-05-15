
def atten_move_in(x4=True, x2=True):
    """
    Move 4x + 2x Sn 60 um attenuators in
    """
    print('Moving attenuators in')

    if x4:
       yield from bps.mv(att1_7, 'in')
    if x2:
       yield from bps.mv(att1_6, 'in')

def atten_move_out():
    """
    Move 4x + 2x Sn 60 um attenuators out
    """
    print('Moving attenuators out')
    yield from bps.mv(att1_7, 'out',att1_6, 'out')


def run_swaxs_Cai_2025_2(t=1):
    """
    Hard X-ray WAXS and SAXS
    Measure transmission only during the first run
    """
    
    #Test 5, run 1
    names =   [ 'BzMA-9.06-G1', 'BzMA-8.07-G1', 'BzMA-7.26-G1',  'BzMA-6.25-G1',  'BzMA-4.72-G1', 'BzMA-2.7-G1',  'BzMA-1.0-G1', 'Empty-G1'] 
    piezo_x = [   42500,           30000,         19000,            3000,           -6500,          -21000,           -34500,        -42000]   
    piezo_y = [   -2550,           -1950,         -2250,            -2250,          -2100,          -2100,            -1800,         -1800]     
    piezo_z = [   7800,            7800,          7800,             7800,           11000,          11000,           11000,         11000]

    
    hexa_x =  [ 0 for n in names]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    user_name = "BH"
    waxs_arc = [20, 0]

    points = 5
    dy = 150
    dbeam_x = -42500
    dbeam_y = -2000

    bs_pos = -227.0

    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW, pin_diode]
        
                

        get_trans = (
            ( 19 < waxs.arc.position )
            and ( waxs.arc.position < 21 )
        )

        if get_trans:
            # get transmission empty
            yield from atten_move_in()
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 10)
            yield from bps.mv(piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_id(user_name='test', sample_name='test')
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
            yield from atten_move_out()

        for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y,
                              piezo.z, z,
                              stage.x, hx)

            # Scan along the capillary
            for i in range(points):

                new_y = y + i * dy

                yield from bps.mv(piezo.y, new_y)

                if (get_trans and i == 0):
                    # Take transmission measurement
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 10)
                    sample_id(user_name='test', sample_name='test')
                    yield from bp.count([pil2M,pin_diode])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                    yield from atten_move_out()
                
                if not get_trans:
                    trans = 0

                # Take normal scans
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)


"""
position of hexapod for Linkam temperature stage:
x = -4.6
y = -1
z = -5
"""


def run_hexa_swaxs_Cai_2025_2(t=1):
    """
    Hard X-ray WAXS and SAXS
    Measure transmission only during the first run
    use hexapod only
    """
    
    #Test 5, run 1
    names =   [ 'NIPAM-2.1-thin',  'NIPAM-3.6-thin',  'NIPAM-4.1-thin','tri-NIPAM'] 
    stage_x = [   16.2,         8,         -1.5,        -18.5]   
    stage_y = [   0,           0,           0,          0.3]     
    stage_z = [   0,             0,             0,            0]

    

    msg = "Wrong number of coordinates"
    assert len(stage_x) == len(names), msg
    assert len(stage_x) == len(stage_y), msg
    assert len(stage_x) == len(stage_z), msg

    user_name = "BH"
    waxs_arc = [20, 0]

    points = 5
    dy = 0.15
    dbeam_x = 14.2
    dbeam_y = 0

    bs_pos = -227.0

    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW, pin_diode]
        
                

        get_trans = (
            ( 19 < waxs.arc.position )
            and ( waxs.arc.position < 21 )
        )

        if get_trans:
            # get transmission empty
            yield from atten_move_in()
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 10)
            yield from bps.mv(stage.x, dbeam_x,
                              stage.y, dbeam_y)

            sample_id(user_name='test', sample_name='test')
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
            yield from atten_move_out()

        for name, x, y, z in zip(names, stage_x, stage_y, stage_z):
            yield from bps.mv(stage.x, x,
                              stage.y, y,
                              stage.z, z,)

            # Scan along the sample
            for i in range(points):

                new_y = y + i * dy

                yield from bps.mv(stage.y, new_y)

                if (get_trans and i == 0):
                    # Take transmission measurement
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 10)
                    sample_id(user_name='test', sample_name='test')
                    yield from bp.count([pil2M,pin_diode])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                    yield from atten_move_out()
                
                if not get_trans:
                    trans = 0

                # Take normal scans
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)




def run_swaxs_Cai_2025_3(t=2):
    """
    Hard X-ray WAXS and SAXS
    Measure transmission only during the first run
    """
    
    #Test 1, run 1
    names =   ['MSU-30', 'MSU-31','MSU-32','MSU-33','MSU-34','MSU-35','MSU-36','MSU-37','MSU-38','MSU-39','MSU-40'] 
    piezo_x = [36800,   28200,    20000,    12000,   3300,    -5400, -13400,   -21400,  -29700,   -37900,   -46300]   
    piezo_y = [ -2750,   -2750,    -2750,    -2000,  -2000,    -1700,  -1550,    -1550,  -1550,    -1400,      -1300]     
    #piezo_z = [    7800,  ]
    piezo_z = [   -36000 for n in names ]

    
    hexa_x =  [ 3 for n in names]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    user_name = "BH"
    waxs_arc = [20, 0]

    points = 4
    dy = 150
    dbeam_x = 32500
    dbeam_y = -3500

    bs_pos = -227.4

    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW, pin_diode]
        
                

        get_trans = (
            ( 19 < waxs.arc.position )
            and ( waxs.arc.position < 21 )
        )

        if get_trans:
            # get transmission empty
            yield from atten_move_in()
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 5)
            yield from bps.mv(piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_id(user_name='test', sample_name='test')
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
            yield from atten_move_out()

        for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y,
                              piezo.z, z,
                              stage.x, hx)

            # Scan along the capillary
            for i in range(points):

                new_y = y + i * dy

                yield from bps.mv(piezo.y, new_y)

                if (get_trans and i == 0):
                    # Take transmission measurement
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 5)
                    sample_id(user_name='test', sample_name='test')
                    yield from bp.count([pil2M,pin_diode])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                    yield from atten_move_out()
                
                if not get_trans:
                    trans = 0

                # Take normal scans
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)



def run_temperature_hard_2026_1(t=0.5):
    """
    """

    names_1   = [ 'SNa0-0.5uL',  'SNa0-1uL',   'SNa0-2uL',     'SNa5-1k']
    piezo_x_1 = [        41400,       36400,        31200,         10900]
    piezo_y_1 = [        -1550,       -1550,        -1550,         -1550]

    names_2   = [   ]
    piezo_x_2 = [   ]
    piezo_y_2 = [   ]

    names_3   = [        'SiN',     'C8-Br-b',    'C8-NTf2-b',     'C8-PF6-b',    'C8-OTf-b']
    piezo_x_3 = [       -41100,        -45100,         -40600,         -35000,        -30600]     
    piezo_y_3 = [        -1750,         -1150,          -5300,          -5480,         -5300]   
    
    names_4   = [     ] 
    piezo_x_4 = [     ]
    piezo_y_4 = [     ]

    names_5   = ['MNa0-ii',  'SNa12-1k-ii',   'SNa10-1k-ii',   'SNa5-1k-ii', 'MNa10-1k-ii',]
    piezo_x_5 = [    26800,          21400,           16800,          11600,          1200,]
    piezo_y_5 = [    -5880,          -5880,           -5880,          -5880,         -5880,]
    

    names   =   names_1 +   names_2 +   names_3 +   names_4 +   names_5
    piezo_x = piezo_x_1 + piezo_x_2 + piezo_x_3 + piezo_x_4 + piezo_x_5
    piezo_y = piezo_y_1 + piezo_y_2 + piezo_y_3 + piezo_y_4 + piezo_y_5
    
    piezo_z = [ 7200 for n in names ]
    
    waxs_arc = [ 0 ]

    temperatures = [30, 50, 70, 90, 70, 50, 30]

    user = "BP"
    det_exposure_time(t, t)

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg

    for i, temperature in enumerate(temperatures):
        
        direction = 'temp_u' if i > temperatures.index(max(temperatures)) else 'temp_d'

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
        while abs(temp - t_kelvin) > 3:
            print("Difference: {:.1f} K".format(abs(temp - t_kelvin)))
            yield from bps.sleep(10)
            temp = ls.input_A.get()
            
            # Escape the loop if too much time passes
            if time.time() - start > 120 * 60:
                temp = t_kelvin
        
        print("Time needed to equilibrate: {:.1f} min".format((time.time() - start) / 60))

        # Wait extra time depending on temperature
        if (25 < temperature) and (temperature <= 150):
            wait_time = 60
            print(f'Sleeping for {wait_time} seconds')
            yield from bps.sleep(wait_time)

        for name, x, y, z, in zip(names, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(
                piezo.y, y + i * 20,
                piezo.x, x,
                piezo.z, z,
            )
            loc = f'00'

            # Shorter exposure for bulk samples
            t = 0.5 if 'C8' in name else 5
            det_exposure_time(t, t)

            # Read T and convert to deg C
            temp_degC = ls.input_A.get() - 273.15
            temp = str(np.round(float(temp_degC), 1)).zfill(5)

            for wa in waxs_arc:
                yield from bps.mv(waxs, wa)
                dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]

                sample_name = f'{name}_{direction}{temp}degC{get_scan_md()}_loc{loc}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    # Cleanup
    t_kelvin = 25 + 273.15
    yield from ls.output1.mv_temp(t_kelvin)
    yield from ls.output1.turn_off()
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)



'''
notes

after pumping down chamber (Auto Evacuate and wait for B1:WAXS to turn green)
open valve 7, then after a few seconds, valve 6
RE(restartWAXS())
wait ~2 minutes until the WAXS detector is restarted




to remove samples:
RE(shclose())
click the Vent WAXS/sample Chamber button and wait for B1:WAXS to get to 7.5E+5



'''




def run_swaxs_Cai_2026_1(t=2):
    """
    Hard X-ray WAXS and SAXS
    Measure transmission only during the first run
    """
    ls.input_A_celsius.kind='hinted'
    ls.kind='hinted'

    names =   [ 'BB40',     'BB39',          'BB38',         'BB37',         'BB36',          'BB35',           'BB34',        'BB33'] 
    piezo_x = [-44950.0,    -31950.0,       -19350.0,       -6600.0,           5800.0,         18600.0,          31600.0,      44300.0]   
    piezo_y = [-8767.9,      -8817.9,       -8917.9,        -8967.9,          -9017.9,         -9167.9,          -9167.9,      -9267.9]         

    piezo_z = [   7000 for n in names ]

    temperatures = [30, 60]

    dbeam_x = 38200.0
    dbeam_y = -9267.9
    user_name = "WZ"



    hexa_x =  [ 0 for n in names]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    waxs_arc = [20, 0]

    points = 4
    dy = 150
    # direct beam position (no sample)


    bs_pos = -228.400000

    det_exposure_time(t, t)
    for i, temperature in enumerate(temperatures):
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
        while abs(temp - t_kelvin) > 1:
            print("Difference: {:.1f} K".format(abs(temp - t_kelvin)))
            yield from bps.sleep(10)
            temp = ls.input_A.get()
            
            # Escape the loop if too much time passes
            if time.time() - start > 240 * 60:
                temp = t_kelvin
        
        print("Time needed to reach temp: {:.1f} min".format((time.time() - start) / 60))
        
        if temperature>50:
            print("Equilibrating for 1 more minutes")
            yield from bps.sleep(1*60)


        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            dets = [pil900KW,ls.input_A_celsius] if waxs.arc.position < 15 else [pil2M, pil900KW, pin_diode,ls.input_A_celsius]
            
                    

            get_trans = (
                ( 19 < waxs.arc.position )
                and ( waxs.arc.position < 21 )
            )

            if get_trans:
                # get transmission empty
                yield from atten_move_in()
                yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 5)
                yield from bps.mv(piezo.x, dbeam_x,
                                piezo.y, dbeam_y)

                sample_id(user_name='test', sample_name='test')
                yield from bp.count([pil2M])
                stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
                yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                yield from atten_move_out()

            for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):
                yield from bps.mv(piezo.x, x,
                                piezo.y, y,
                                piezo.z, z,
                                stage.x, hx)

                # Scan along the sample
                for j in range(points):

                    new_y = y + j * dy

                    yield from bps.mv(piezo.y, new_y)

                    if (get_trans and j == 0):
                        # Take transmission measurement
                        yield from atten_move_in()

                        # Sample
                        yield from bps.mv(pil2M.beamstop.x_pin, bs_pos + 5)
                        sample_id(user_name='test', sample_name='test')
                        yield from bp.count([pil2M,pin_diode])
                        stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                        # Transmission
                        trans = np.round( stats1_sample / stats1_direct, 5)

                        # Revert configuraton
                        yield from bps.mv(pil2M.beamstop.x_pin, bs_pos)
                        yield from atten_move_out()
                    
                    if not get_trans:
                        trans = 0

                    # Take normal scans
                    sample_name = f'{name}{get_scan_md()}_tempC{temperature}_loc{j}_trs{trans}'
                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)
    
    t_kelvin = 25 + 273.15
    yield from ls.output1.mv_temp(t_kelvin)
    yield from ls.output1.turn_off()
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)


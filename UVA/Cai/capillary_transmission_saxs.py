
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

            # Scan along the capillary
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



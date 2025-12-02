def overnight_mapping_Das_2025_1(t=2):
    """
    SAXS is the priority, 300x300, 61(y) x 13(x)

    """

    names =   [   'S1',   'S2',   'S3',   'S4',  'S5',  'S6',  'S7',  'bkg', ]
    piezo_x = [ -39000, -28000,  14000,   2000, 15000, 28000, 41000,  45000, ]
    piezo_y = [    500,    500,    500,    500,   500,   600,   900,    900, ]
    piezo_z = [   3700,   3700,   3700,   3700,  3700,  3700,  3700,   3700, ]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg

    waxs_arc = [ 20 , 0]
    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]
        
        # Get xbpm3
        dets.append(xbpm3.sumX)

        for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
                piezo.z, z,
            )

            sample_name = f'{name}_{get_scan_md()}'
            sample_id(user_name='SD', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            
            if 'bkg' not in name:
                yield from bp.rel_grid_scan(dets, piezo.y, -150, 150, 61,  piezo.x, -150, 150, 13, 0)
            else:
                yield from bp.rel_grid_scan(dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 11, 0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def insitu_mapping_Das_2025_1(t=1, waxs_only=False):
    """
    WAXS or SAXS/WAXS at once, 300x300, 61(y) x 13(x)

    """
    # Sample name and coordinates
    
    name = 'BKG-Air'
    x =    -6300
    y =     2200
    z =     -800

    x_offset = 300
    extra_exposure = 5

    if waxs_only:
        waxs_arc = [ 0 ]
    else:
        waxs_arc = [ 15 ]
    
    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]
        
        # Get xbpm3
        dets.append(xbpm3.sumX)

        yield from bps.mv(
            piezo.x, x,
            piezo.y, y,
            piezo.z, z,
            )

        sample_name = f'{name}_{get_scan_md()}'
        sample_id(user_name='SD', sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
            
        if 'fgk' not in name:
            yield from bp.rel_grid_scan(dets, piezo.y, -2, 2, 3,  piezo.x, -2, 2, 3, 0)
        else:
            yield from bp.rel_grid_scan(dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 11, 0)

        
        # # Do a single WAXS + SAXS scan at the end
        waxs_arc_single = [20, 0]
        for wa in waxs_arc_single:
            det_exposure_time(extra_exposure, extra_exposure)

            yield from bps.mv(waxs, wa)
            yield from bps.mv(piezo.x, x + x_offset)

            dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]
            dets.append(xbpm3.sumX)

            sample_name = f'{name}-single{get_scan_md()}'
            sample_id(user_name='SD', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)
        
        # move back to sample
        yield from bps.mv(
            piezo.x, x,
            piezo.y, y,
            piezo.z, z,
            waxs, waxs_arc[0],
        )

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def create_timestamp():
    """
    store in RE.md and print
    """
    RE.md['tstamp'] = time.time()
    print('\nTime stamp created in RE.md')
    tstamp = RE.md['tstamp']
    print(f'tstamp: {tstamp}')

def insitu_loop_mapping_Das_2025_3(t=1, waxs_only=False):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan

    """

    project_set('Mn3O4-IE-RT')

    # Sample name and coordinates
    
    name = 'sample'
    x =    -2500
    y =     1400
    z =   -35400

    if waxs_only:
        waxs_arc = [ 0 ]
    else:
        waxs_arc = [ 14.5 ]
    
    det_exposure_time(t, t)

    run = 0

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    while True:
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
            
            # Get xbpm3
            dets.append(xbpm3.sumX)

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
                piezo.z, z,
                )
            
            eplased = time.time() - tstamp

            sample_name = f'{name}_run{run}_{get_scan_md()}_t{eplased:.0f}'
            sample_id(user_name='SD', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
                
            if 'bgk' not in name:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -300, 300, 121,  piezo.x, -300, 300, 13, 0
                    )
            else:
                yield from bp.rel_grid_scan(dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 11, 0)
            run += 1
    
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def get_positions():
    """
    Create a string with scan metadata
    """
    
    # Metadata
    x = piezo.x.position
    y = piezo.y.position
    
    x = str(np.round(float(x), 1)).zfill(5)
    y = str(np.round(float(y), 1)).zfill(5)

    return f'x={x}_y={y}'


def single_point_Das_2025_3(t=60, name='test'):
    """
    Do a single WAXS + SAXS scan at the end
    """

    # Get time stamp
    try:
        tstamp = RE.md['tstamp']
    except:
        print('There was no time stamp, restart from 0')
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    waxs_arc_single = [20, 0]
    det_exposure_time(t, t)
    
    for wa in waxs_arc_single:
        
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
        dets.append(xbpm3.sumX)
        
        eplased = time.time() - tstamp
        sample_name = f'{name}-single{get_scan_md()}_t{eplased:.0f}_{get_positions()}'
        sample_id(user_name='SD', sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)
    
    yield from bps.mv(waxs, 14.5)
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def single_grain_POI_Das_2025_3(t=30, name='test'):
    """
    Do a single WAXS + SAXS scan at the end
    """
    names =   [   'grain']
    # relative

    x0 =    -2400.0
    y0 =     1250
    z0 =   -34600

    piezo_x = [ x0 -25.0 ]
    piezo_y = [ y0 - 105.0]

  
    


    # Get time stamp
    try:
        tstamp = RE.md['tstamp']
    except:
        print('There was no time stamp, restart from 0')
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    waxs_arc_single = [20]
    det_exposure_time(t, t)
    
    
    for wa in waxs_arc_single:
        print('Move detector...')
        yield from bps.mv(waxs, wa)
        for name_prefix, x, y in zip(names, piezo_x, piezo_y):

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
            )
            eplased = time.time() - tstamp
            sample_name = f'{name}_{name_prefix}-single{get_scan_md()}_t{eplased:.0f}_{get_positions()}'
            sample_id(user_name='SD', sample_name=sample_name)

            dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
            dets.append(xbpm3.sumX)
            
            

            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)
    

    print('Move detector...')
    yield from bps.mv(waxs, 14.5,
                      piezo.x, x0,
                      piezo.y, y0,
                      piezo.z, z0,)
    
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def grains_POI_Das_2025_3(t=30, name='test'):
    """
    Do a single WAXS + SAXS scan at the end
    """
    names =   [   'P1',   'P2', 'P3', 'P4', 'P5']
    # relative

    project_set('Mn3O4-NOIE-exsitu')

    x0 =    800.0
    y0 =     0.0
    z0 =   -30500.0

    piezo_x = [ x0 -100.0 , x0 + 0.0 , x0 + 100.0, x0 + 100.0, x0 - 100.0]
    piezo_y = [ y0 -100.0, y0 + 0.0 , y0 + 100.0, y0 - 100.0, y0 + 100.0 ]

  
    


    # Get time stamp
    try:
        tstamp = RE.md['tstamp']
    except:
        print('There was no time stamp, restart from 0')
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    waxs_arc_single = [20, 0]
    det_exposure_time(t, t)
    
    
    for wa in waxs_arc_single:
        print('Move detector...')
        yield from bps.mv(waxs, wa)
        for name_prefix, x, y in zip(names, piezo_x, piezo_y):

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
            )
            eplased = time.time() - tstamp
            sample_name = f'{name}_{name_prefix}-single{get_scan_md()}_t{eplased:.0f}_{get_positions()}'
            sample_id(user_name='SD', sample_name=sample_name)

            dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
            dets.append(xbpm3.sumX)
            
            

            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)
    

    print('Move detector...')
    yield from bps.mv(waxs, 14.5,
                      piezo.x, x0,
                      piezo.y, y0,
                      piezo.z, z0,)
    
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def clean_tstamp():
    """
    """
    try:
        RE.md.pop('tstamp')
    except:
        print('No time stamp in RE.md')


def operando_mapping_Das_2025_3(t=1, waxs_only=False, repeats=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('Cu-Yao-exsitu')

    # Sample name and coordinates
    
    name = 'Cu-Yao-exsitu_01'
    x =    -3400.0
    y =     2100.0
    z =   -33600.0

    if waxs_only:
        waxs_arc = [ 0 ]
    else:
        waxs_arc = [ 14.5 ]
    
    det_exposure_time(t, t)

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats+1):
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
            
            # Get xbpm3
            dets.append(xbpm3.sumX)

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
                piezo.z, z,
                )
            
            eplased = time.time() - tstamp

            sample_name = f'{name}_run{r}_{get_scan_md()}_t{eplased:.0f}_{get_positions()}'
            sample_id(user_name='SD', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
                
            if 'bgk' not in name:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -300, 300, 10,  piezo.x, -300, 300, 10, 0
                    # dets, piezo.y, -120, 110, 97,  piezo.x, -125, 100, 10, 0
                    # dets, piezo.y, -300, 300, 121, piezo.x, -300, 300, 25, 0
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 11, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

# RE(pil2M.insert_beamstop('rod')    -> potentially changing beamstops, insert attenuators and check


def exsitu_swaxs_Das_2025_3(t=60, x_off=0, y_off=0):
    """
    Low divergence measurements, 9 points on each sample

    """

    names =   [   'bkg', 'S01',  'S02',  'S03', 'S04', 'S05', 'S06',  'S07',  'S08', 'S09', ]
    piezo_x = [ -42400, -35000, -22000,  -6000,  8000, 26000, 38000, -36000, -22400, -8200, ]
    piezo_y = [  -2000,  -2000,  -2000,  -1500, -1500, -1500, -1500,   2700,   2000,  1800, ]
    #piezo_z = [   7000,   7000,   7000,   7000,  7000,  7000,  7000,   7000,   7000,  7000, ]
    piezo_z = [ 3800 for n in names ]
    stage_y = [    -3,      -3,     -3,     -3,    -3,    -3,    -3,     5,       5,     5, ]

    # Offsets for in vacuum plus y offset to scan different pos
    # delta x = -400 um, delta y = -270 um + 150 um = - 120 um

    piezo_x = np.asarray(piezo_x) - 400 + x_off
    piezo_y = np.asarray(piezo_y) - 270 + y_off


    msg = 'Wrong number of coordinates'
    for arr in [piezo_x, piezo_y, piezo_z, stage_y]:
        assert len(arr) == len(names), msg

    waxs_arc = [ 0, 20 ]
    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]
        
        # Get xbpm3
        dets.append(xbpm3.sumX)

        for name, x, y, z, sy in zip(names, piezo_x, piezo_y, piezo_z, stage_y):

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
                piezo.z, z,
                stage.y, sy,
            )

            sample_name = f'{name}_{get_scan_md()}'
            sample_id(user_name='SD', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            
            yield from bp.rel_grid_scan(dets, piezo.y, -300, 300, 3,  piezo.x, -400, 400, 3, 0)
    

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def run_multiple_exposures_Das():
    """
    Run twice with diffent exposure time and offest in y in between
    """
    project_set('pw-exsitu-vac-5s')
    yield from exsitu_swaxs_Das_2025_3(t=5)
    project_set('pw-exsitu-vac-60s')
    yield from exsitu_swaxs_Das_2025_3(t=60, y_off=150)
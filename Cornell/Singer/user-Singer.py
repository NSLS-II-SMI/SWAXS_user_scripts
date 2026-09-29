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


def exsitu_swaxs_Das_2026_1(t=60, x_off=0, y_off=0):
    """
    Low divergence measurements, 9 points on each sample

    """

    names =   [ 'AgBH',  'S01a1',  'S01a2',  'S01b1',  'S01b2',  'S02a',  'S02b',  'S03',  'vac-bkg', ]
    piezo_x = [ -44000,   -29400,   -29400,   -20400,   -19400,   11000,   16000,  41000,     -14000, ] 
    piezo_y = [  -1200,    -1200,    -2000,    -1200,    -1200,   -1200,   -1200,   -800,      -1200  ]
    piezo_z = [ 200 for n in names ]
    stage_y = [  -10 for n in names ]

    piezo_x = np.asarray(piezo_x) + x_off
    piezo_y = np.asarray(piezo_y) + y_off


    msg = 'Wrong number of coordinates'
    for arr in [piezo_x, piezo_y, piezo_z, stage_y]:
        assert len(arr) == len(names), msg

    waxs_arc = [ 0, 20 ]
    det_exposure_time(t, t)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]

        if wa == 20:
            yield from mv(waxs.bs_x, -130)
        
        # Get xbpm3
        #dets.append(xbpm3.sumX)

        for name, x, y, z, sy in zip(names, piezo_x, piezo_y, piezo_z, stage_y):

            yield from bps.mv(
                piezo.x, x,
                piezo.y, y,
                piezo.z, z,
                stage.y, sy,
            )

            sample_name = f'{name}_{get_scan_md()}'
            sample_id(user_name='PW', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            
            if wa == waxs_arc[0]:
                yield from bp.count([OAV_writing])
            
            yield from bp.rel_grid_scan(dets, piezo.y, -300, 300, 3,  piezo.x, -400, 400, 3, 0)
    

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def run_multiple_exposures_Das_2026_1():
    """
    Run twice with diffent exposure time and offest in y in between
    """
    project_set('pw-exsitu-vac-5s')
    yield from exsitu_swaxs_Das_2026_1(t=5)
    project_set('pw-exsitu-vac-60s')
    yield from exsitu_swaxs_Das_2026_1(t=60, y_off=150)


def get_scan_md(tender=False):
    """
    """

    # Metadata
    e = energy.position.energy / 1000
    #temp = str(np.round(float(temp_degC), 1)).zfill(5)
    wa = waxs.arc.position + 0.001
    wa = str(np.round(float(wa), 1)).zfill(4)
    sdd = pil2m_pos.z.position / 1000

    md_fmt = ("_{energy}keV_wa{wa}_sdd{sdd}m")

    if tender:
        scan_md = md_fmt.format(
            energy = "%.5f" % e ,
            wa = wa,
            sdd = "%.1f" % sdd,
        )
    else:
        scan_md = md_fmt.format(
            energy = "%.2f" % e ,
            wa = wa,
            sdd = "%.1f" % sdd,
        )
    return scan_md

def get_more_md(tender=True, bpm=True):
    """"""

    more_md = f'{get_scan_md(tender=tender)}'

    if bpm:
        xbpm = xbpm2.sumX.get()
        xbpm = str(np.round(float(xbpm), 3)).zfill(5)
        more_md = f'{more_md}_xbpm{xbpm}'

    return more_md

def sample_id(user_name='test',sample_name='test'):

    sample_name = f'{user_name}_{sample_name}'.translate(
                {ord(c): "_" for c in r"!@#$%^&*{}:/<>?\|`~+ =,"})

    RE.md["sample_name"] = sample_name


def calib_scan(t=1):
    project_set('CeO2_01')
    name = 'CeO2_01_calib_01'
    waxs_arc = [ 0, 15, 17.5, 20, 22.5, 25]

    yield from det_exposure_time(t, t)

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
    
    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.3 else [pil900KW, pil2M]
        dets.append(xbpm3.sumX)
        eplased = time.time() - tstamp

        sample_name = f'{name}_{get_scan_md()}_t{eplased:.0f}_{get_positions()}'
        sample_id(user_name='SD', sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")

        yield from bp.count(
                        dets, 20
                    )


        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def operando_mapping_Das_2026_3(t=1, waxs_only=False, repeats=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('BG')

    # Sample name and coordinates
    
    name = 'BG_QAPPT_Kapton_wa18p5_03'
    z =    2500.0
    y =    3500.0
    x =    -1800.0
    
    

    if waxs_only:
        waxs_arc = [ 18.5 ]
    else:
        waxs_arc = [ 0, 18.5 ]
    
    yield from det_exposure_time(t, t)

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                    dets, piezo.y, -500, 500, 5, piezo.x, -500, 500, 3, 0
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 3, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def operando_mapping_time_delay_Das_2026_3(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('PEM_03')

    # Sample name and coordinates
    
    name = 'PEM_03_1V0_02_O2'
    z =    2300.0
    y =    1030.0
    x =    6600.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [ 0, 20 ]
    
    yield from det_exposure_time(t, t)

    def delayed_step(detectors, step, pos_cache):
        yield from bps.one_nd_step(detectors, step, pos_cache)

        if point_delay > 0:
            yield from bps.sleep(point_delay)


    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                yield from bp.rel_scan(
                    dets, piezo.x, -1180, 1180, 60,
                    per_step=delayed_step
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 3, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def operando_mapping_time_delay_shuttclose_Das_2026_3(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('PEM_03')

    # Sample name and coordinates
    
    name = 'PEM_03_0V2_01_O2'
    z =    2300.0
    y =    1000.0
    x =    6600.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [ 0, 20 ]
    
    yield from det_exposure_time(t, t)

    def delayed_step(detectors, step, pos_cache):
        yield from bps.one_nd_step(detectors, step, pos_cache)

        yield from shopen()

        yield from bps.trigger_and_read(
            list(detectors) +list(step.keys())
        )

        yield from shclose()

        if point_delay > 0:
            yield from bps.sleep(point_delay)

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                yield from bp.rel_scan(
                    dets, piezo.x, -1180, 1180, 60,
                    per_step=delayed_step
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 3, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def operando_voltage_dependence_Das_2026(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('PEM_04')

    # Sample name and coordinates
    
    name = 'PEM_04_0V2_N2_down3_cy2'
    z =    1500.0
    y =    2515.0
    x =    550.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [ 0, 20 ]
    
    yield from det_exposure_time(t, t)

    def delayed_step(detectors, step, pos_cache):
        yield from bps.one_nd_step(detectors, step, pos_cache)

        if point_delay > 0:
            yield from bps.sleep(point_delay)


    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                yield from bp.rel_scan(
                    dets, piezo.x, -1180, 1180, 5,
                    per_step=delayed_step
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -100, 100, 11,  piezo.x, -100, 100, 3, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def operando_mapping_time_delay_Das_2026_3(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('CuCO2RR')

    # Sample name and coordinates
    
    name = 'CuCO2RR_exsitu_mapping_01'
    z =    3500.0
    y =    3300.0
    x =    900.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [ 18.5 ]
    
    yield from det_exposure_time(t, t)

    def delayed_step(detectors, step, pos_cache):
        yield from bps.one_nd_step(detectors, step, pos_cache)

        if point_delay > 0:
            yield from bps.sleep(point_delay)


    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                yield from bp.rel_scan(
                    dets, piezo.x, -1180, 1180, 60,
                    per_step=delayed_step
                )
            else:
                yield from bp.rel_grid_scan(
                    dets, piezo.y, -250, 250, 22,  piezo.x, -1000, 1000, 83, 0
                )

        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def single_shot_waxs_sweep(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('CuCO2RR_01')

    # Sample name and coordinates
    
    name = 'CuCO2RR_exsitu_test_06_0.5'
    z =    3500.0
    y =    3500.0
    x =    50.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [0, 15, 20, 25, 30 ]
    
    yield from det_exposure_time(t, t)

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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

            yield from bp.count(dets, 1)
        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def operando_mapping(t=1, waxs_only=False, repeats=0, point_delay=0):
    """
    WAXS or SAXS/WAXS at once, 300x300, 121(y) x 13(x)
    1h scan
    """

    project_set('CuCO2RR_02')

    # Sample name and coordinates
    
    name = 'CuCO2RR_CO2_N2_-2V5_Re'
    z =    3550.0
    y =    4381.0
    x =   -2000.0
    
    

    if waxs_only:
        waxs_arc = [ 20 ]
    else:
        waxs_arc = [ 18.5 ]
    
    yield from det_exposure_time(0.5, t)

    def delayed_step(detectors, step, pos_cache):
        yield from bps.one_nd_step(detectors, step, pos_cache)

        if point_delay > 0:
            yield from bps.sleep(point_delay)


    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for r in range(repeats + 1):
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
                
            yield from bp.rel_grid_scan(
                dets, piezo.y, -250, -125 , 10,  piezo.x, -500, 500, 15, 0
            )

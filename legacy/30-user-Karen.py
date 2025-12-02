def get_positions():
    """
    Create a string with scan metadata
    """
    
    # Metadata
    x = piezo.x.position
    y = piezo.y.position
    z = piezo.z.position
    th = piezo.th.position
    temp = ls.input_A.get() - 273.15

    
    x = str(np.round(float(x), 0)).zfill(5)
    y = str(np.round(float(y), 0)).zfill(5)
    z = str(np.round(float(z), 0)).zfill(5)
    th = str(np.round(float(th), 4)).zfill(0)
    temp = str(np.round(float(temp), 1)).zfill(5)
    # f'_ai{str(np.round(0.02555, 3)).zfill(4)}'
   
    return f'x={x}_y={y}_z={z}_th={th}_temp{temp}degC'


def name_sample(name, tstamp):
    """
    Create sample name with metadata

    Args:
        name (str): sample name
        tstamp (time): referenced start time created separately as
            tstamp = time.time()
    """

    eplased = time.time() - tstamp
    sample_name = f'{name}{get_scan_md()}_t{eplased:.1f}_{get_positions()}'
    sample_id(user_name='YCK', sample_name=sample_name)
    print(f'\n\n\n{sample_name}\n')

def take_data_manually(name, t=2):
    """
    """
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
    name_sample(name, tstamp)

    det_exposure_time(t, t)
    yield from bp.count([pil900KW])


def create_timestamp():
    """
    store in RE.md and print
    """
    RE.md['tstamp'] = time.time()
    print('\nTime stamp created in RE.md')
    tstamp = RE.md['tstamp']
    print(f'tstamp: {tstamp}')


def continous_run(sname='test', t=2, wait=8, frames=2160):
    """
    Take data continously
    
    Create timestamp in BlueSky before running this function as
    create_timestamp()

    Args:
        sname (str): basic sample name,
        t (float): camera exposure time is seconds,
        wait (float): delay between frames,
        frames(int): number of frames to take
    """
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
    
    det_exposure_time(t, t)

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames')

        # update sample name
        name_sample(sname, tstamp)

        # take one fram
        yield from bp.count([pil900KW])

        # wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)

def manual_th_scan(name, t=2, angles=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30], loc=None):
    """
    Take data manually over a few theta angles
    and come back to 0.1 deg incident angle
    
    """
    det_exposure_time(t, t)
    
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    try:
        th0 = RE.md['th0']
    except:
        th0 = -1.30-0.1 # as measured
        RE.md['th0'] = th0

    for ai in angles:
        yield from bps.mv(piezo.th, th0 + ai)

        name_sample(name, tstamp)
        sname = RE.md['sample_name']
        RE.md['sample_name'] += f'ai={ai}'
        if loc is not None:
            RE.md['sample_name'] += f'_loc{loc}'
        yield from bp.count([pil900KW])
        RE.md['sample_name'] = sname

    yield from bps.mv(piezo.th, th0 + 0.1)


def run_x_th_scan(name, t):
    """
    """

    x = piezo.x.position

    x_table = [-100, -50, 0, 50, 100]

    for x_step in x_table:
        yield from bps.mv(piezo.x, x + x_step)

        yield from manual_th_scan(name, t)
    
    yield from bps.mv(piezo.x, x)


def run_swaxs_KCW_2023_3(t=2):
    """
    Hard X-ray WAXS and SAXS
    """

    names =   [ 'calib-kapton', 'calib-celgart-rot0', 'calib-glass-fibre', 'calib-cu-foil', 'calib-celgard-rot90'] 
    piezo_x = [   -15000, -6700, 2300, 12300, 22300 ]   
    piezo_y = [    -4000, -4000, -4000, -4000, -5700 ]          
    piezo_z = [ 3000 for n in names ]
    hexa_x =  [ 0 for n in names]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    user_name = "KCW"
    waxs_arc = [0, 20]

    det_exposure_time(t, t)

    # Make sure cam server engages with the detector
    yield from engage_detectors()

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]

        for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y,
                              piezo.z, z,
                              stage.x, hx)

            # Take normal scans
            sample_name = f'{name}{get_scan_md()}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)


def loop_scans_across_y(sname=f'20231106_opexp_NaCu_a', t=2, wait=1, frames=1):
    """
    Sample alignment
    """

    piezo_x = np.round(piezo.x.position, 2)
    piezo_y = np.round(piezo.y.position, 2)

    x_off = [-100, 0, 100, 250]
    y_off = np.linspace(-20, 20, 41)

    for x in x_off:
        yield from bps.mv(piezo.x, piezo_x + x)

        for y in y_off:
            yield from bps.mv(piezo.y, piezo_y + y)

            yield from continous_run(sname=sname, t=t, wait=wait, frames=frames)

    yield from bps.mv(piezo.x, piezo_x,
                      piezo.y, piezo_y,)

def loop_overnight_scans_(sname=f'20231106_opexp_NaCu_a', t=2, wait=1, frames=1):
    """
    Overnight x vs y vs theta
    move to nominal pozition manually after the scan
    """

    piezo_x = [  12450,  12550,  12650, ]
    piezo_y = [ -1225, -1225, -1225, ]

    y_off = [-2, 0, 2]

    for frame in range(frames):
        print(f'Taking {frame + 1} / {frames} frames')

        for i, (x, y) in enumerate(zip(piezo_x, piezo_y)):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y)

            for j, y_of in enumerate(y_off):
                yield from bps.mv(piezo.y, y + y_of)

                loc = f'{i}{j}'
                yield from manual_th_scan(sname, t=2, angles=[0.05, 0.10, 0.15], loc=loc)

def grazing_Chen_Wiegart_2023_3(t=0.5):
    """
    standard GI-S/WAXS
    """
    #[ 'G1-01-x2.083']
    #[ -52417 ] 
    #[   6775 ]  
    #[   9800 ] 
    #[    -13 ] 
    # names   =  [  'G1-01-x7.083',  'G1-01-x8.750',  'G1-01-x9.167', 'G1-01-x10.000', 'G1-01-x25.000', 'G3-01-x25.000', 'G3-01-x10.000', 'G3-01-x7.083', 'G3-01-x2.083', 'G4-01-x2.083', 'G4-01-x7.083', 'G4-01-x25.000']
    # piezo_x =  [    -47417,          -45750,          -45333,         -44500,          -29500,          7300,             22292,          25211,          30215,           17985,          22989,          40900]
    # piezo_y =  [    6775,              6775,           6775,           6775,           6775,            6775,             5815,           5815,           5815,            5615,           5615,           5415]          
    # piezo_z =  [    9800,              9800,           9800,           9800,           9200,            6600,             5600,           5600,           5600,            5400,           5400,           4200]
    # hexa_x =   [     -13,               -13,            -13,            -13,            -13,            -13,              -13,            -13,            -13,             12,             12,             12]
    # names   =  [  'b44-01_VTiCu_Pristine',  'b44-02_VTiCu_750C30M',  'b45-01_NbAlCu_Pristine', 'b45-02_NbAlCu_500C30M', 'b46-01_MoTiCu_Pristine', 'b46-02_MoTiCu_750C30M', 'b47-01_NbAlSc_Pristine', 'b47-02_NbAlSc_900C30M']
    # piezo_x =  [  -53100,                   -41100,                  -29100,                   -17100,                  -3100,                    8900,                    20900,                    34900                  ]
    # piezo_y =  [    6984,                     6984,                    6784,                     6684,                   6584,                    6484,                     6484,                    6284                   ]          
    # piezo_z =  [    8800,                     7800,                    7300,                     6800,                   6800,                    6300,                     6300,                    4800                   ]
    # hexa_x =   [     -13,                      -13,                     -13,                      -13,                    -13,                     -13,                      -13,                    -13                    ]
    names   =  [  'Cufoil_reflection']
    piezo_x =  [  1900]
    piezo_y =  [  7856]          
    piezo_z =  [  6800]
    hexa_x =   [   -13]


    i = 0
    names   = names[i:]
    piezo_x = piezo_x[i:]
    piezo_y = piezo_y[i:]
    piezo_z = piezo_z[i:]
    hexa_x =  hexa_x[i:]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    waxs_arc = [ 0, 20, ]  # degrees
    x_off = [ 0 ]
    incident_angles = [ 0.10, 0.15, 0.20, 0.25, 0.30, 0.50]
    user_name = 'YCW'

    det_exposure_time(t, t)

    # Make sure cam server engages with the detector
    #yield from engage_detectors()
 
    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):

        #yield from bps.mv(piezo.x, x,
        #                  piezo.y, y,
        #                  piezo.z, z,
        #                  stage.x, hx)

        # Align the sample
        #yield from alignement_gisaxs(0.1) #0.1 to 0.15


        # Sample flat at ai0
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            yield from bps.mv(waxs.bs_y, -3)

            for xx, x_of in enumerate(x_off):
                yield from bps.mv(piezo.x, x + x_of)
            
                for ai in incident_angles:
                    yield from bps.mv(piezo.th, ai0 + ai)

                    sample_name = f'{name}{get_scan_md()}_ai{ai}'

                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def alignment_on(beamstop_x=6.55):
    """
    Alignment mode on
    """
    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")
    yield from smi.setDirectBeamROI(size=[48, 20])
    print(f'Using hardcoded SAXS beamstop position {beamstop_x} mm due to smi.mode not working properly')
    yield from bps.mv(pil2M.beamstop.x_rod, beamstop_x + 5)
    sample_id(user_name='test', sample_name='test')

    det_exposure_time(0.5, 0.5)
    print('\t\tALIGNMENT MODE ON')

def alignment_off(beamstop_x=6.55):
    """
    Alignment mode off
    """
    print('\t\tALIGNMENT MODE OFF and WAXS arc to 0 deg')
    smi = SMI_Beamline()
    yield from smi.modeMeasurement()
    print(f'Using hardcoded SAXS beamstop position {beamstop_x} mm due to smi.mode not working properly')
    yield from bps.mv(pil2M.beamstop.x_rod, beamstop_x)
    yield from bps.mv(waxs, 0)


def atten_move_in():
    """
    Move 4x + 2x Sn 60 um attenuators in
    """
    print('Moving attenuators in')

    while att1_7.status.get() != 'Open':
        yield from bps.mv(att1_7.open_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Open':
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)

def atten_move_out():
    """
    Move 4x + 2x Sn 60 um attenuators out
    """
    print('Moving attenuators out')
    while att1_7.status.get() != 'Not Open':
        yield from bps.mv(att1_7.close_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Not Open':
        yield from bps.mv(att1_6.close_cmd, 1)
        yield from bps.sleep(1)

def alignment_on_stepbystep():
    """
    Aomething wrong with beamline code and attens, making separate routine
    yield from bps.mv(
    RE.md['SAXS_setup']['bs_x']
    """
    smi = SMI_Beamline()
    yield from atten_move_in()
    yield from bps.mv(waxs, 15)
    yield from bps.mvr(pil2M.beamstop.x_rod, 5)
    yield from smi.setDirectBeamROI()
    print('\t\tALIGNMENT MODE ON and WAXS arc at 15 deg')

def alignment_off_stepbystep(bs_x=None):
    """
    Aomething wrong with beamline code and attens, making separate routine
    yield from bps.mv(
    RE.md['SAXS_setup']['bs_x']
    """
    if bs_x is None:
        bs_x = RE.md['SAXS_setup']['bs_x']

    yield from atten_move_out()
    yield from bps.mv(waxs, 0)
    yield from bps.mv(pil2M.beamstop.x_rod, bs_x)

    print('\t\tALIGNMENT MODE OFF and WAXS arc to 0 deg')


def continous_run_change_xpos(sname='20250630_op_a_echem', t=2, wait=100, frames=5000,
        x_off=[-150, -100, -50, 0, 50, 100,150]):

    """
    Take data continously
    
    Create timestamp in BlueSky before running this function as
    create_timestamp()

    Args:
        sname (str): basic sample name,
        t (float): camera exposure time is seconds,
        wait (float): delay between frames,
        frames(int): number of frames to take,
        x_off (list of floats): relative x positions to take data at.
    """
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
    
    det_exposure_time(t, t)

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames for {len(x_off)} x positions')

        x_0 = piezo.x.position
        # this could change because of drift.

        for x_step in x_off:
            yield from bps.mv(piezo.x, x_0 + x_step)
            # update sample name
            name_sample(sname, tstamp)

            # take one frame
            yield from bp.count([pil900KW])
        
        yield from bps.mv(piezo.x, x_0)

        # don't wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)

def take_data_across_x(sname='20241030_op_Na_Cu_bar_b', t=2, x_off=[-500, -400, -300, -250, -200,-150, -100, -50, 0, 50, 
                                                                  100,150, 200, 250, 300, 400, 500]):

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    x_0 = piezo.x.position

    for x_step in x_off:
        yield from bps.mv(piezo.x, x_0 + x_step)
        # update sample name
        name_sample(sname, tstamp)

        # take one frame
        yield from bp.count([pil900KW])
    
    yield from bps.mv(piezo.x, x_0)


def align_across_x():
    """
    Create alignment look up table for different positions

    Need to go manually
    """

    try:
        sample_pos = RE.md['sample_pos0']
        x0 = sample_pos['x0']
    except:
        x0 = piezo.x.position
        y0 = piezo.y.position
        z0 = piezo.z.position
        th0 = piezo.th.position
        ch0 = piezo.ch.position
        RE.md['sample_pos0'] = dict(x0=x0, y0=y0, z0=z0, th0=th0, ch0=ch0)

    piezo_x = np.linspace(-500, 500, 11, dtype=int) + x0

    yield from bps.mv(
        piezo.x, sample_pos['x0'],
        piezo.y, sample_pos['y0'],
        piezo.th, sample_pos['th0'],
    )

    yield from alignment_on()

    RE.md['alignment_LUT'] = dict()

    for i, x in enumerate(piezo_x):
        yield from bps.mv(piezo.x, x)



        # Align step by step
        alignment_LUP = dict()

        yield from rel_scan([pil2M], piezo.y, -100, 100, 26)
        ps(der=True)
        yield from bps.mv(piezo.y, ps.cen)

        yield from rel_scan([pil2M], piezo.th, -1.5, 1.5, 26)
        ps(der=False)
        yield from bps.mv(piezo.th, ps.peak)

        plt.close('all')

        yield from bps.sleep(1)

        dict1 = dict(
            x = piezo.x.position,
            y = piezo.y.position,
            th = piezo.th.position,
        )

        RE.md['alignment_LUT'][i] = dict1

    yield from alignment_off()


def save_alignment_to_md(point='0'):
    """
    Save alignment positon for single point
    """

    dict1 = dict(
        x = np.round(piezo.x.position, 2),
        y = np.round(piezo.y.position, 2),
        z = np.round(piezo.z.position, 2),
        th = np.round(piezo.th.position, 3),
    )

    try:
        RE.md['alignment_LUT'][str(point)] = dict1
    except:
        RE.md['alignment_LUT'] = dict()
        RE.md['alignment_LUT'][str(point)] = dict1

def move_to_sample_pos0(key='sample_pos0'):
    """
    Move to starting position based on RE.md
    """

    try:
        sample_pos = RE.md[key]
    except:
        print(f'There is no starting position {key} saved in RE.md')

    print(f'Moving to sample position\n{sample_pos}')

    yield from bps.mv(
        piezo.x, sample_pos['x0'],
        piezo.y, sample_pos['y0'],
        piezo.z, sample_pos['z0'],
        piezo.th, sample_pos['th0'],
        piezo.ch, sample_pos['ch0']
    )

def save_sample_pos0():
    """
    Save sample start position into metadata after alignment
    """

    x0 = np.round(piezo.x.position, 2)
    y0 = np.round(piezo.y.position, 2)
    z0 = np.round(piezo.z.position, 2)
    th0 = np.round(piezo.th.position, 3)
    ch0 = np.round(piezo.ch.position, 3)

    RE.md['sample_pos0'] = dict(x0=x0, y0=y0, z0=z0, th0=th0, ch0=ch0)


def clear_md():
    """
    Remove time stamp, sample zero, and alignment after changing the cell
    """

    keys = [ 'tstamp', 'alignment_LUT', 'sample_pos0']
    
    for k in keys:
        try:
            RE.md.pop(k)
            print(f'Removed: {k}')
        except:
            print(f'No {k} key')


def continous_run_prealigned_positions_2024_1(sname='20250630_op_a_interval', t=2, wait=0, frames=1):
    """
    WAXS at each prealigned point

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of points is done.
    """

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
                      '0': {'x': 1850, 'y': 7372.68, 'z': 10801.3, 'th': 0.86},
                        '-150': {'x': 1700, 'y': 7375.36, 'z': 10801.3, 'th': 0.78},
                        '150': {'x': 2000, 'y': 7370.991, 'z': 10801.29, 'th': 0.78},
                        
        }
        RE.md['alignment_LUT'] = alignment

    alignment = {int(k) : v for k, v in alignment.items()}

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames for {len(alignment)} x positions')

        for key, value in sorted(alignment.items()):

            yield from bps.mv(
                piezo.x, value['x'],
                piezo.y, value['y'],
                #piezo.z, value['z'],
                #piezo.th, value['th'] + 0.1, # angle set already
                piezo.th, value['th'],
            )

            name_sample(sname, tstamp)
            yield from bp.count([pil900KW])
        
        # wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)

def continous_run_change_xpos_thpos(
        sname='20250709_op_a_pretest',
        t=2, wait=100, frames=5000,
        x_off=[-150, -100, -50, 0, 50, 100, 150],
        ai_off=[0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5],
    ):
    """
    Take data continously
    
    Create timestamp in BlueSky before running this function as
    create_timestamp()

    Args:
        sname (str): basic sample name,
        t (float): camera exposure time is seconds,
        wait (float): delay between frames,
        frames(int): number of frames to take,
        x_off (list of floats): relative x positions to take data at.
    """
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
        print(f'Setting timestampt to {tstamp}')

    try:
        th0 = RE.md['th0']
    except:
        th0 = piezo.th.position
        RE.md['th0'] = th0
        print(f'Setting th0 to current position of {th0} deg')

    det_exposure_time(t, t)
    x_0 = piezo.x.position

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames for {len(x_off)} x positions')
    
        for x_step in x_off:
            yield from bps.mv(piezo.x, x_0 + x_step)

            for ai in ai_off:
                yield from bps.mv(piezo.th, th0 + ai)
                # update sample name
                name_sample(sname, tstamp)

                # take one frame
                yield from bp.count([pil900KW])
        
        yield from bps.mv(piezo.x, x_0,
                          piezo.th, th0)

        # don't wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)


def continous_run_prealigned_positions_2025_2(sname='20251117_op_a_echem_run', t=2, wait=100, frames=5000):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, 0, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -2000, 'y': 7579.694, 'z': -0.423, 'th': -0.5433},
                '0': {'x': -0.405, 'y': 7473.095, 'z': -0.438, 'th': 0.5433},
             '2000': {'x': 2000, 'y': 7353.558, 'z': -0.438, 'th': -0.54327},
                        
        }
        RE.md['alignment_LUT'] = alignment

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames for {len(alignment)} ROIs')

        # Iterate over region of interest
        for key, value in alignment.items():

            # ROI alignment values
            x0 = value['x']
            y0 = value['y']
            z0 = value['z']
            th0 = value['th']

            yield from bps.mv(
                piezo.x, x0,
                piezo.y, y0,
                piezo.z, z0,
                piezo.th, th0,
            )

            print(f'{key}, {value}')
            

            # Fine scan across x
            for x_step in x_off:
                print(f'{type(x_off)}')
                print(f'{type(x_step)}')
                print(f'{x_step}')
                print(f'{type(x0)}')
                #clo= x0+x_step
                yield from bps.mv(piezo.x, x0 + x_step)
                #yield from bps.mv(piezo.x, clo)

                print(f'stag1')

                # Go over incident angles
                for ai in ai_off:
                    yield from bps.mv(piezo.th, th0 + ai)

                    print(f'stag2')

                    name_sample(sname, tstamp)
                    # Add incident angle to sample name
                    ai_md = f'_ai_{ai:.3f}'
                    print(f'Incident angle:\t{ai}')
                    name = RE.md['sample_name']
                    RE.md['sample_name'] = name + ai_md

                    yield from bp.count([pil900KW])
        
        # wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)


def continous_run_prealigned_positions_2025_3_swaxs(
        sname='20251027_Cu_cel2325_glassfiber', t=2, wait=0, frames=1, saxs_frame=1):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles. Each nth frame, take full SAXS WAXS scan.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        x_off (list of floats): offset values in um for x scans,
        ai_off (list of floats): values of incident angles to take scans at,
        saxs_frame (int): frame interval for which to take full SWAXS dataset.

    """
    x_off  = [-100, 0, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30]
    
    # for SAXS / WAXS measurement
    y_off  = [0, 10, 50, 100, ]
    waxs_arc = [0, 20]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -17000, 'y': -595.365, 'z': -18842, 'th': 1.439}          
        }
        RE.md['alignment_LUT'] = alignment

    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    for i in range(frames):
        yield from bps.mv(waxs, 0)
        print(f'Taking {i + 1} / {frames} frames for {len(alignment)} ROIs')

        # Iterate over region of interest
        for key, value in alignment.items():

            # ROI alignment values
            x0 = value['x']
            y0 = value['y']
            z0 = value['z']
            th0 = value['th']

            yield from bps.mv(
                piezo.x, x0,
                piezo.y, y0,
                piezo.z, z0,
                piezo.th, th0,
            )

            print(f'{key}, {value}')
            

            # Fine scan across x
            for x_step in x_off:
                yield from bps.mv(piezo.x, x0 + x_step)

                # Go over incident angles
                for ai in ai_off:
                    yield from bps.mv(piezo.th, th0 + ai)

                    name_sample(sname, tstamp)
                    # Add incident angle to sample name
                    ai_md = f'_ai_{ai:.3f}'
                    print(f'Incident angle:\t{ai}')
                    name = RE.md['sample_name']
                    RE.md['sample_name'] = name + ai_md
                    yield from bp.count([pil900KW])
        
        if i % saxs_frame == 0:

            for wa in waxs_arc:
                yield from bps.mv(waxs, wa)
                dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

                for key, value in alignment.items():

                    yield from bps.mv(
                        piezo.x, value['x'],
                        piezo.y, value['y'],
                        piezo.z, value['z'],
                        piezo.th, value['th'],
                    )

                    # Fine scan across y
                    for y_step in y_off:
                        yield from bps.mv(piezo.y, value['y'] - y_step)
                        sname_saxs = sname + '-SWAXS'
                        name_sample(sname_saxs, tstamp)
                        ai = 0
                        ai_md = f'_ai_{ai:.3f}'
                        name = RE.md['sample_name']
                        RE.md['sample_name'] = name + ai_md
                        yield from bp.count(dets)
                
                yield from bps.mv(waxs, 0)
        else:
            print(f'\nWaiting {wait} s')
            yield from bps.sleep(wait)


# Backup


'''
def continous_run_prealigned_positions_2025_2(sname='20250709_op_d_echem', t=2, wait=100, frames=5000):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, -50, 0, 50, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -2000, 'y': 6883.802, 'z': 2000, 'th': 0.18},
                '0': {'x': -0, 'y': 6861.954, 'z': 2000, 'th': 0.18},
             '2000': {'x':  2000, 'y': 6838.093, 'z': 2000, 'th': 0.18},
                        
        }
        RE.md['alignment_LUT'] = alignment
'''
'''
def continous_run_prealigned_positions_2025_2(sname='20250709_op_c_echem', t=2, wait=100, frames=5000):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, -50, 0, 50, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -2800, 'y': 6971.022, 'z': 2000, 'th': 1.06},
                '0': {'x': -800, 'y': 6946.917, 'z': 2000, 'th': 1.06},
             '2000': {'x':  1200, 'y': 6920.857, 'z': 2000, 'th': 1.02},
                        
'''

'''
def continous_run_prealigned_positions_2025_2(sname='20250709_op_b_echem', t=2, wait=100, frames=5000):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, -50, 0, 50, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -4000, 'y': 6853.836, 'z': 2000, 'th': 0.94},
                '0': {'x': -2000, 'y': 6847.006, 'z': 2000, 'th': 0.8312},
             '2000': {'x':  0,    'y': 6835.918,   'z': 2000, 'th':0.646},
                        
        }
'''
'''
def continous_run_prealigned_positions_2025_2(sname='20250709_op_a_echem', t=2, wait=100, frames=5000):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, -50, 0, 50, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -2500, 'y': 7126, 'z': 2000, 'th': 0.54},
                '0': {'x': -500, 'y': 7111, 'z': 2000, 'th': 0.59},
             '2000': {'x':  1500, 'y': 7094.7,   'z': 2000, 'th': 0.57},
                        
        }
        RE.md['alignment_LUT'] = alignment
'''
'''
def continous_run_prealigned_positions_2025_2(sname='Pristine_Cu_in_cell', t=2, wait=50, frames=1):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        
    """
    # x_off (list of floats): offset values in um for x scans,
    # ai_off (list of floats): values of incident angles to take scans at.
    
    x_off  = [-100, -50, 0, 50, 100]
    ai_off = [0.05, 0.10, 0.15, 0.20, 0.30, 0.4, 0.5]

    try:
        alignment = RE.md['alignment_LUT']
    except:
        alignment =  {
            '-2000': {'x': -4000, 'y': 6826.13, 'z': 2000, 'th': 1.18},
                '0': {'x': -2000, 'y': 6819.9, 'z': 2000, 'th': 1.08},
             '2000': {'x':  0,    'y': 6810,   'z': 2000, 'th': 0.88},
'''
''' {'0': {'x': 3648.04, 'y': -1263.1, 'z': 799.8, 'th': 2.19},
 '-100': {'x': 3547.69, 'y': -1249.21, 'z': 799.82, 'th': 2.19},
 '-200': {'x': 3447.79, 'y': -1249.52, 'z': 799.82, 'th': 2.19},
 '-300': {'x': 3347.77, 'y': -1249.37, 'z': 799.82, 'th': 1.875},
 '-400': {'x': 3247.8, 'y': -1244.76, 'z': 799.81, 'th': 1.875},
 '-500': {'x': 3147.79, 'y': -1244.88, 'z': 799.81, 'th': 1.875},
 '-1000': {'x': 2647.77, 'y': -1239.85, 'z': 799.81, 'th': 1.875},
 '-900': {'x': 2748.02, 'y': -1239.9, 'z': 799.81, 'th': 1.875},
 '-1100': {'x': 2547.76, 'y': -1239.96, 'z': 799.81, 'th': 1.875},
 '-1500': {'x': 2147.76, 'y': -1230.9, 'z': 799.8, 'th': 1.675},
 '-1400': {'x': 2248.09, 'y': -1229.97, 'z': 799.79, 'th': 1.686},
 '-1600': {'x': 2047.73, 'y': -1225.97, 'z': 799.79, 'th': 1.686},
 '100': {'x': 3748.02, 'y': -1255.0, 'z': 799.77, 'th': 2.04},
 '200': {'x': 3848.0, 'y': -1255.05, 'z': 799.77, 'th': 2.04},
 '300': {'x': 3947.96, 'y': -1250.96, 'z': 799.77, 'th': 2.04},
 '400': {'x': 4047.98, 'y': -1251.02, 'z': 799.76, 'th': 2.04},
 '500': {'x': 4148.0, 'y': -1251.18, 'z': 799.74, 'th': 2.04},
 '1000': {'x': 4648.05, 'y': -1256.98, 'z': 799.74, 'th': 2.18},
 '900': {'x': 4547.77, 'y': -1255.99, 'z': 799.74, 'th': 2.18},
 '1100': {'x': 4748.04, 'y': -1257.98, 'z': 799.74, 'th': 2.33},
 '1500': {'x': 5148.08, 'y': -1259.73, 'z': 799.74, 'th': 2.18},
 '1400': {'x': 5047.73, 'y': -1257.99, 'z': 799.74, 'th': 2.32},
 '1600': {'x': 5248.13, 'y': -1259.23, 'z': 799.73, 'th': 2.02}}

 
 {'0': {'x': 3999.71, 'y': -1442.75, 'z': 799.8, 'th': 1.00},
 '-250': {'x': 3749.71, 'y': -1437.84, 'z': 799.82, 'th': 1.00},
 '-500': {'x': 3499.71, 'y': -1437.94, 'z': 799.82, 'th': 1.00},
 '250': {'x': 4249.71, 'y': -1438.07, 'z': 799.82, 'th': 1.00},
 '500': {'x': 4499.71, 'y': -1438.41, 'z': 799.81, 'th': 1.00}


    0': {'x': 3999.71, 'y': -1442.75, 'z': 799.8, 'th': 1.00},
 '-250': {'x': 3749.71, 'y': -1437.84, 'z': 799.82, 'th': 1.00},
 '-500': {'x': 3499.71, 'y': -1437.94, 'z': 799.82, 'th': 1.00},
 '250': {'x': 4249.71, 'y': -1438.07, 'z': 799.82, 'th': 1.00},
 '500': {'x': 4499.71, 'y': -1438.41, 'z': 799.81, 'th': 1.00}

 0': {'x': 3999.71, 'y': -1250.94, 'z': 799.8, 'th': 2.05},
 '-250': {'x': 3749.71, 'y': -1247.7, 'z': 799.82, 'th': 2.05},
 '-500': {'x': 3499.71, 'y': -1243.4, 'z': 799.82, 'th': 2.05},
 '250': {'x': 4249.71, 'y': -1249.9, 'z': 799.82, 'th': 2.05},
 '500': {'x': 4499.71, 'y': -1454.7, 'z': 799.81, 'th': 2.05}
 ,


'''
# Read T and convert to deg C
#temp = ls.input_A.get() - 273.15
#temp = str(np.round(float(temp), 1)).zfill(5)

def grazing_Dean_2025_3(t=0.5):
    """
    standard GI-S/WAXS on hexapod for humidity

    """
    #project_set('ex-situ')

    # Sample set 1
    names_1   = ['20251117_exsitu_sample_a']
    stage_x_1 = [27]
    stage_y_1 = [-0.02]
    #stage_z_1 = []

    # Sample set 2
    names_2   = []
    stage_x_2 = []
    stage_y_2 = []
    #stage_z_2 = []
  

    names   = names_1   + names_2
    stage_x = stage_x_1 + stage_x_2
    stage_y = stage_y_1 + stage_y_2
    #stage_z = stage_z_1 + stage_z_2

    msg = "Wrong number of coordinates"
    for arr in [stage_x, stage_y, ]:
        assert len(arr) == len(names), msg

    waxs_arc = [ 0 ]
    incident_angles = [ 0.05, 0.10, 0.15, 0.20, 0.25 ]
    user_name = 'YCW'

    det_exposure_time(t, t)


    try:
        misaligned_samples = RE.md['misaligned_samples']
    except:
        misaligned_samples = []
        RE.md['misaligned_samples'] = misaligned_samples


    for name, sx, sy, in zip(names, stage_x, stage_y, ):

        yield from bps.mv(
            stage.x, sx,
            stage.y, sy,
        )

        # Align the sample
        try:
            yield from alignement_gisaxs_hex_rough_Dean()
        except:
            misaligned_samples.append(name)
            RE.md['misaligned_samples'] = misaligned_samples

        yield from smi.modeMeasurement()
        yield from atten_move_out()

        # Sample flat at ai0
        ai0 = stage.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            yield from bps.mv(waxs.bs_y, -3)
            yield from smi.modeMeasurement()

            for ai in incident_angles:
                yield from bps.mv(stage.th, ai0 + ai)

                ai_md = f'_ai_{ai:.3f}'
                sample_name = f'{name}{get_scan_md()}' + ai_md

                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)

def prealigned_grazing_Dean_2025_3(t=0.5):
    """
    standard GI-S/WAXS on hexapod for humidity

    """
    #project_set('ex-situ')

    # Sample set 1
    names   = ['20251117_exsitu_sample_a_pos9']
    stage_x = [27.4]
    stage_y = [-0.253]


    msg = "Wrong number of coordinates"
    for arr in [stage_x, stage_y, ]:
        assert len(arr) == len(names), msg

    waxs_arc = [ 0 ]
    incident_angles = [ 0.05,0.1,0.15,0.2,0.25 ]
    user_name = 'YCW'

    det_exposure_time(t, t)

    print('\n\nPrealigned sample - skipping alignment step!!\n\n')

    for name, sx, sy, in zip(names, stage_x, stage_y, ):

        yield from bps.mv(
            stage.x, sx,
            stage.y, sy,
        )

        # Sample flat at ai0
        ai0 = stage.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            yield from bps.mv(waxs.bs_y, -3)
            yield from smi.modeMeasurement()

            for ai in incident_angles:
                yield from bps.mv(stage.th, ai0 + ai)

                ai_md = f'_ai_{ai:.3f}'
                sample_name = f'{name}{get_scan_md()}' + ai_md

                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def alignement_gisaxs_hex_rough_Dean(angle=0.1):
    """
    Adopted from alignement_gisaxs_hex_roughsample(angle=0.1)

    """

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)

    yield from smi.modeAlignment()
    #yield from alignment_on_stepbystep()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height_hex(1, 31, der=True)
    try:
        yield from align_gisaxs_th_hex(1.5, 31)
    except:
        yield from align_gisaxs_th_hex(0.7, 31)
    yield from align_gisaxs_height_hex(0.5, 31, der=True)
    yield from align_gisaxs_th_hex(0.5, 31)
    yield from align_gisaxs_height_hex(0.2, 31, der=True)
    yield from align_gisaxs_th_hex(0.2, 31)


    ######
    # Scan theta and height
    #yield from align_gisaxs_height_hex(0.5, 15, der=True)
    #yield from align_gisaxs_th_hex(0.5, 21)
    #yield from align_gisaxs_height_hex(0.2, 25, der=True)
    #yield from align_gisaxs_th_hex(0.2, 21)
    
    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    #      yield from bps.mvr(stage.th, -angle)
    yield from smi.modeMeasurement()
    #yield from alignment_off_stepbystep()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def atten_move_in():
    """
    Move 4x + 2x Sn 60 um attenuators in
    """
    print('Moving attenuators in')

    while att1_7.status.get() != 'Open':
        yield from bps.mv(att1_7.open_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Open':
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)

def atten_move_out():
    """
    Move 4x + 2x  + 1x Sn 60 um attenuators out
    """
    print('Moving attenuators out')
    while att1_7.status.get() != 'Not Open':
        yield from bps.mv(att1_7.close_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Not Open':
        yield from bps.mv(att1_6.close_cmd, 1)
        yield from bps.sleep(1)
    while att1_5.status.get() != 'Not Open':
        yield from bps.mv(att1_6.close_cmd, 1)
        yield from bps.sleep(1)


def alignment_on_stepbystep():
    """
    Aomething wrong with beamline code and attens, making separate routine
    yield from bps.mv(
    RE.md['SAXS_setup']['bs_x']
    """
    smi = SMI_Beamline()
    yield from atten_move_in()
    yield from bps.mv(waxs, 15)
    yield from bps.mvr(pil2M.beamstop.x_rod, 5)
    #yield from smi.setDirectBeamROI()
    print('\t\tALIGNMENT MODE ON and WAXS arc at 15 deg')

def alignment_off_stepbystep(bs_x=None):
    """
    Aomething wrong with beamline code and attens, making separate routine
    yield from bps.mv(
    RE.md['SAXS_setup']['bs_x']
    """
    if bs_x is None:
        bs_x = RE.md['SAXS_setup']['bs_x']

    yield from atten_move_out()
    yield from bps.mv(waxs, 0)
    yield from bps.mv(pil2M.beamstop.x_rod, bs_x)

    print('\t\tALIGNMENT MODE OFF and WAXS arc to 0 deg')

def run_Millares_hard_2026_1(t=1):
    """
    """
    # %run -i /home/xf12id/SWAXS_user_scripts/SBU/Takeuchi/user-Millares.py
    # RE(run_Millares_hard_2026_1(t=1))

    """
    Focal point z = 6400 on crystal
    Focal on camera = 4800
    from camera, push + 1600 in Z to be in beam focus

    """

    names_1   = ["AP351-16-1", "AP351-16-2", "AP351-16-3", "AP351-16-4", "AP351-16-5"]
    piezo_x_1 = [-45200,        -38800,       -32550,       -26250,       -19850]
    piezo_y_1 = [-5000,         -5000,        -5000,        -5000,        -5000]

    names_2   = ["AP351-16-6", "CH289-152-11", "Empty_capillary", "AP351-16-7", "Empty_quartz_tube"]
    piezo_x_2 = [-13550,        -7400,          -800,              5400,         11800]
    piezo_y_2 = [-5000,         -5000,          -5000,             -5000,        -5000]

    names   =   names_1 +   names_2
    piezo_x = piezo_x_1 + piezo_x_2
    piezo_y = piezo_y_1 + piezo_y_2
    
    piezo_z = [ 7000 for n in names ]
    
    waxs_arc = [ 0, 20 ]

    user = "MM"
    det_exposure_time(t, t)

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 14.9 else [pil900KW, pil2M]
        
        if wa == waxs_arc[0]:
            dets.append(OAV_writing)

        for name, x, y, z, in zip(names, piezo_x, piezo_y, piezo_z):

            yield from bps.mv(
                piezo.y, y,
                piezo.x, x,
                piezo.z, z,
            )
            sample_name = f'{name}_{get_scan_md()}'
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def name_sample(name, tstamp, user_name='MM'):
    """
    Create sample name with metadata

    Args:
        name (str): sample name
        tstamp (time): referenced start time created separately as
            tstamp = time.time()
    """

    eplased = time.time() - tstamp
    sample_name = f'{name}_{get_scan_md()}_t{eplased:.1f}_{get_positions()}'
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f'\n\n\n{sample_name}\n')


def get_positions():
    """
    Create a string with scan metadata
    """
    
    # Metadata
    x = piezo.x.position
    y = piezo.y.position
    z = piezo.z.position

    
    x = str(np.round(float(x), 0)).zfill(5)
    y = str(np.round(float(y), 0)).zfill(5)
    z = str(np.round(float(z), 0)).zfill(5)

    # f'_ai{str(np.round(0.02555, 3)).zfill(4)}'
    return f'x={x}_y={y}_z={z}'


def continous_run_prealigned_positions_2026_1(t=0.5, wait=100):

    """
    At each prealigned region of interest, take a finer scan across x with several
    incident angles.

    Args:
        sname (str): sample name,
        t (float): exposure time,
        wait (float): wait time after one series of scans is done,
        frames (int): number of series of scans to be taken,
        saxs_frame (int): frame interval for which to take full SWAXS dataset.

    """

    names   = ['AP351-17-5', 'AP351-17-4', ]
    piezo_x = [      -42800,        43500, ]
    piezo_y = [       -5400,        -5900, ]
    piezo_z = [        5700,         7200, ]

    msg = 'Wrong number of coordinates'
    for arr in [piezo_x, piezo_y, piezo_z, ]:
        assert len(arr) == len(names), msg
    
    tstamp = time.time()

    det_exposure_time(t, t)
    yield from bps.mv(waxs, 0)

    while True:
        
        print(f'Taking infinite number of frames')

        for name, x, y, z, in zip(names, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(
                piezo.y, y,
                piezo.x, x,
                piezo.z, z,
            )

            name_sample(name, tstamp)
            sample_name = RE.md['sample_name']
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from rel_grid_scan([pil900KW], piezo.x, -600, 600, 5)

        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)

def grazing_Millares_2026_1(t=0.5):
    """
    standard GI-S/WAXS on double stack holder
    """
    
    
    names_1   = ["AP335-173-12"] 
    piezo_x_1 = [-47500]
    piezo_y_1 = [-100]          
    piezo_z_1 = [ 6400]
    hexa_x_1 =  [ -12.5]          
    
    names_2   = [ "AP335-173-16", "AP335-173-17", "AP335-173-18", "AP335-173-19", "AP335-173-20"]
    piezo_x_2 = [ -19800,            -11800,           -4000,         5100,            19100]
    piezo_y_2 = [ 800,                 1100,            1100,         1600,             1600]                
    piezo_z_2 = [ 4900,                6400,            5400,         6400,             4400]
    hexa_x_2 =  [ -12.5,              -12.5,           -12.5,        -12.5,            -12.5]
    
    names_3   = [ "AP335-173-21", "AP335-173-22", "AP335-173-23"]
    piezo_x_3 = [ 28100,              36100,           46100]
    piezo_y_3 = [ 1700,                1900,            2000]                
    piezo_z_3 = [ 4600 for n3 in names_3]
    hexa_x_3 =  [ -12.5,              -12.5,           -12.5]

    names   = names_1   + names_2 + names_3
    piezo_x = piezo_x_1 + piezo_x_2 + piezo_x_3
    piezo_y = piezo_y_1 + piezo_y_2 + piezo_y_3
    piezo_z = piezo_z_1 + piezo_z_2 + piezo_z_3
    hexa_x  = hexa_x_1  + hexa_x_2 + hexa_x_3


    # Starting from ith sample
    i = 0
    names   = names[i:]
    piezo_x = piezo_x[i:]
    piezo_y = piezo_y[i:]
    piezo_z = piezo_z[i:]
    hexa_x =  hexa_x[i:]

    msg = 'Wrong number of coordinates'
    for arr in [piezo_x, piezo_y, piezo_z, hexa_x]:
        assert len(arr) == len(names), msg

    waxs_arc = [ 0, 7, 20 ]
    x_off = [0]
    incident_angles = [ 0.05, 0.10, 0.5 ]
    user_name = 'MM'

    det_exposure_time(t, t)

    bp_pos_x = 6.8


    try:
        misaligned_samples = RE.md['misaligned_samples']
    except:
        misaligned_samples = []
        RE.md['misaligned_samples'] = misaligned_samples


    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):

        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          stage.x, hx)

        # Align the sample
        try:
            #yield from alignement_gisaxs_doblestack(0.1)
            # did not work fully
            yield from alignment_gisaxs_Millares(angle=0.1)
        except:
            misaligned_samples.append(name)
            RE.md['misaligned_samples'] = misaligned_samples

        # Sample flat at ai0
        ai0 = piezo.th.position
        yield from bps.mv(pil2M.beamstop.x_rod, bp_pos_x)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

            # problems with the beamstop
            #yield from bps.mv(waxs.bs_y, -3)

            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)

                sample_name = f'{name}{get_scan_md()}_ai{ai}'

                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


def alignment_gisaxs_Millares(angle=0.1):
    """
    Regular alignment routine for GISAXS and GIWAXS. First, scan the sample height and incident angle on the direct beam.
    Then scan the incident angle, height, and incident angle again on the reflected beam.

    Parameters:
        angle (float): Angle at which the alignment on the reflected beam will be done.
    """
    

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height(800, 21, der=True)
    yield from align_gisaxs_th(2.5, 31)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    # Scan theta and height
    yield from align_gisaxs_th(0.2, 21)
    yield from align_gisaxs_height_rb(150, 16)    
    cb=close_plots()
    yield from bpp.subs_wrapper(align_gisaxs_th(0.1, 31), cb)  

    # Return angle
    yield from bps.mv(piezo.th, piezo.th.position-angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False


def grazing_after_manual_alignment(name='test', t=0.5):
    """
    """

    waxs_arc = [ 0, 7, 20 ]
    incident_angles = [ 0.05, 0.10, 0.5 ]
    user_name = 'MM'

    det_exposure_time(t, t)

    # Sample flat at ai0
    ai0 = piezo.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        # problems with the beamstop
        #yield from bps.mv(waxs.bs_y, -3)

        for ai in incident_angles:
            yield from bps.mv(piezo.th, ai0 + ai)

            sample_name = f'{name}{get_scan_md()}_ai{ai}'

            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    yield from bps.mv(piezo.th, ai0)

    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)
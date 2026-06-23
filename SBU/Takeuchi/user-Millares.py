def run_Millares_hard_2026_1(t=1):
    """
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks through a list of capillary/tube samples (each at its own
    #   piezo x/y/z position) and takes a SAXS+WAXS image of each, repeating the whole list
    #   at two WAXS-arc positions (0 and 20).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that can run
    #   a whole list of samples as ONE coordinated measurement — it moves to each sample for
    #   you and records which sample (and the beam readings) each image belongs to, so you
    #   don't build the name by hand with get_scan_md(). The pattern is a "bar" plan:
    #
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from transmission_bar(samples, t=t)     # loops the samples for you
    #
    #   (For the two-arc looping, see saxs_waxs_dets / the arc motor_axis in smi_plans. This
    #    is just a tidier option to try later — your script below still works as-is, except
    #    the 'det_exposure_time' line marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================
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
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

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
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def name_sample(name, tstamp, user_name='MM'):
    """
    Create sample name with metadata

    Args:
        name (str): sample name
        tstamp (time): referenced start time created separately as
            tstamp = time.time()
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: builds a long file name by hand — it glues your sample name together
    #   with the scan metadata, an elapsed time, and the current x/y/z positions (via the
    #   get_positions helper below), then registers it with sample_id.
    #
    # 💡 NEWER, EASIER WAY: with the 'smi_plans' helper library you usually don't build the
    #   name like this at all. The acquisition plans record the positions, beam intensity,
    #   energy, time, etc. straight INTO the saved data, and you put placeholders like
    #   "{piezo_x}" or "{time}" in the name — smi_plans fills them in from the recorded data
    #   automatically. So get_positions()/get_scan_md() become unnecessary once you migrate.
    #   (Nothing here is broken — this is just a tidier approach to consider.)
    # === end smi_plans note ================================================

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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: repeatedly (forever) revisits a couple of pre-aligned sample spots
    #   and, at each, runs a short 5-point raster across piezo.x, waiting a bit between
    #   passes — a simple kinetic/time-series follow-up.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with
    #   time-series/kinetics helpers that take frames on a schedule and record the elapsed
    #   time + positions + beam readings straight into the saved data (so you don't call
    #   name_sample / get_scan_md by hand). For the little x-raster, map_line_run does a
    #   line scan and stamps the positions in for you. Roughly:
    #
    #     from smi_plans import kinetics_run, map_line_run
    #     # ...loop your prealigned spots, and at each:
    #     yield from map_line_run(name, piezo.x, -600, 600, 5, dets=[pil900KW])
    #
    #   (This is just a tidier option to try later — your loop below still works as-is,
    #    except the 'det_exposure_time' line marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note
    #   on it).
    # === end smi_plans note ================================================

    names   = ['AP351-17-5', 'AP351-17-4', ]
    piezo_x = [      -42800,        43500, ]
    piezo_y = [       -5400,        -5900, ]
    piezo_z = [        5700,         7200, ]

    msg = 'Wrong number of coordinates'
    for arr in [piezo_x, piezo_y, piezo_z, ]:
        assert len(arr) == len(names), msg
    
    tstamp = time.time()

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) run over a whole bar of samples on
    #   the double-stack holder. For each sample it moves into place, auto-aligns it, then
    #   takes SAXS+WAXS images at several incident angles and WAXS-arc positions.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   whole bar of grazing samples in one call — it moves to each sample, aligns it, loops
    #   the incident angles, and records which sample/angle (and the beam readings) each
    #   image belongs to. The pattern is:
    #
    #     from smi_plans import giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y,
    #                                       z=piezo_z, hexa_x=hexa_x)
    #     yield from giwaxs_bar(samples, incident_angles=[0.05, 0.10, 0.5],
    #                           t=t, align=align_sample)
    #
    #   (align_sample is smi_plans' built-in alignment; see also giwaxs_bar_arc_economy if
    #    you want to minimize arc moves. This is just a tidier option to try later — your
    #    script below still works as-is, except the 'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them). NOTE: 'pil2M.beamstop.x_rod' used here is already the correct current name,
    #   so that line is fine.
    # === end smi_plans note ================================================
    
    
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

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def alignment_gisaxs_Millares(angle=0.1):
    """
    Regular alignment routine for GISAXS and GIWAXS. First, scan the sample height and incident angle on the direct beam.
    Then scan the incident angle, height, and incident angle again on the reflected beam.

    Parameters:
        angle (float): Angle at which the alignment on the reflected beam will be done.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the GISAXS/GIWAXS alignment routine — it finds the sample surface by
    #   scanning height and incident angle on the direct beam, then refines on the reflected
    #   beam, leaving the sample sitting flat (incident angle 0).
    #
    # 💡 NEWER, EASIER WAY: with the 'smi_plans' helper library you don't usually call an
    #   alignment routine by hand in each script. Alignment is done once up front via
    #   align_sample (or passed as align=... into the grazing presets like giwaxs_bar), and
    #   the alignment result is recorded with the data automatically, so it's reproducible.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.3, 0.3)' line below (see the ⚠️
    #   note on it).
    # === end smi_plans note ================================================
    

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: assumes you've already aligned the sample flat by hand, then takes
    #   SAXS+WAXS images at several incident angles and WAXS-arc positions on that one
    #   sample.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that loops
    #   incident angles for you and records the angle + beam readings into the saved data
    #   and file name (so you don't build the name with get_scan_md by hand). For a single
    #   pre-aligned sample:
    #
    #     from smi_plans import giwaxs_run
    #     yield from giwaxs_run(name, incident_angles=[0.05, 0.10, 0.5], t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    except the 'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================

    waxs_arc = [ 0, 7, 20 ]
    incident_angles = [ 0.05, 0.10, 0.5 ]
    user_name = 'MM'

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
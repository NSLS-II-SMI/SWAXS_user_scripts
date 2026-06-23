def overnight_mapping_Das_2025_1(t=2):
    """
    SAXS is the priority, 300x300, 61(y) x 13(x)

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight microfocus map of a sample bar — for each WAXS arc
    #   position it visits each sample and rasters a fine y-by-x grid (61x13), recording
    #   the beam-monitor (xbpm3) reading too.
    #
    # 💡 NEWER, EASIER WAY: a fine raster like this is a "map grid" in the 'smi_plans'
    #   library, and running the whole bar is one call. It records the position, beam
    #   intensity, etc. into each frame for you, so the numbers don't have to live only in
    #   the file name:
    #
    #     from smi_plans import map_grid_run, map_bar, SampleList
    #     # one sample:
    #     yield from map_grid_run("S1", piezo.y, -150, 150, 61, piezo.x, -150, 150, 13,
    #                             t=t, dets=[pil2M, pil900KW], reads=[xbpm3.sumX])
    #     # or the whole bar at once:
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from map_bar("overnight_Das_2025_1", samples, t=t, dets=[pil2M, pil900KW])
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 2 — grid_scan per spot.)
    # === end smi_plans note ================================================

    names =   [   'S1',   'S2',   'S3',   'S4',  'S5',  'S6',  'S7',  'bkg', ]
    piezo_x = [ -39000, -28000,  14000,   2000, 15000, 28000, 41000,  45000, ]
    piezo_y = [    500,    500,    500,    500,   500,   600,   900,    900, ]
    piezo_z = [   3700,   3700,   3700,   3700,  3700,  3700,  3700,   3700, ]

    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg

    waxs_arc = [ 20 , 0]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def insitu_mapping_Das_2025_1(t=1, waxs_only=False):
    """
    WAXS or SAXS/WAXS at once, 300x300, 61(y) x 13(x)

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ map of one spot — rasters a small y-by-x grid, then does
    #   a single longer SAXS+WAXS shot at an x-offset (with extra exposure) per WAXS arc.
    #
    # 💡 NEWER, EASIER WAY: the raster is a "map grid" and the single longer shot is a
    #   transmission acquire in the 'smi_plans' library; both record the position/beam into
    #   each frame for you and set the exposure via t=:
    #
    #     from smi_plans import map_grid_run, transmission_run
    #     yield from map_grid_run("BKG-Air", piezo.y, -2, 2, 3, piezo.x, -2, 2, 3,
    #                             t=t, dets=[pil2M, pil900KW], reads=[xbpm3.sumX])
    #     yield from transmission_run("BKG-Air-single", t=extra_exposure,
    #                                 dets=[pil2M, pil900KW])
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the three 'det_exposure_time(...)' calls below no longer
    #   set the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 2.)
    # === end smi_plans note ================================================
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
    
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
            det_exposure_time(extra_exposure, extra_exposure)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(extra_exposure, extra_exposure)  — or at the prompt:  RE(det_exposure_time(extra_exposure, extra_exposure)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: repeats a microfocus map of one spot over and over (an endless
    #   loop), stamping each run with the elapsed time so you can watch it evolve.
    #
    # 💡 NEWER, EASIER WAY: "repeat a measurement over time and record the timing" is the
    #   'smi_plans' kinetics/time-series idea. Instead of an open-ended 'while True', you
    #   give it a number of repeats (or a duration) and it records the time/position/beam
    #   into each frame for you:
    #
    #     from smi_plans import kinetics_run, map_grid_run
    #     # one mapped frame, looped N times with timing recorded:
    #     yield from kinetics_run(
    #         "sample",
    #         lambda: map_grid_run("sample", piezo.y, -300, 300, 121,
    #                              piezo.x, -300, 300, 13, t=t,
    #                              dets=[pil2M, pil900KW], reads=[xbpm3.sumX]),
    #         num=...,                            # how many repeats (instead of forever)
    #     )
    #
    #   (Just a tidier option to try later — your loop below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 0/1 —
    #   endless RE-style loop; consider a bounded kinetics run.)
    # === end smi_plans note ================================================

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
    
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one long SAXS+WAXS shot at each of two WAXS arc positions on
    #   the current spot, stamping the name with elapsed time and position.
    #
    # 💡 NEWER, EASIER WAY: a single longer capture is one call in the 'smi_plans' library;
    #   it records the time/position/beam into the image for you (so you don't need a
    #   separate timestamp in RE.md or get_positions() in the name):
    #
    #     from smi_plans import transmission_run
    #     yield from transmission_run(name, t=t, dets=[pil2M, pil900KW])
    #     # (loop the WAXS arc with a motor_axis, or just call it once per arc position)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================

    # Get time stamp
    try:
        tstamp = RE.md['tstamp']
    except:
        print('There was no time stamp, restart from 0')
        tstamp = time.time()
        RE.md['tstamp'] = tstamp

    waxs_arc_single = [20, 0]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    
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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def single_grain_POI_Das_2025_3(t=30, name='test'):
    """
    Do a single WAXS + SAXS scan at the end
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to one chosen grain position and takes a single long WAXS
    #   shot, stamping the name with elapsed time and position.
    #
    # 💡 NEWER, EASIER WAY: a single capture at a position is one call in the 'smi_plans'
    #   library; it records the position/time/beam into the image for you:
    #
    #     from smi_plans import transmission_run
    #     yield from transmission_run(name, t=t, dets=[pil900KW, pil2M])
    #     # (move to the grain first with bps.mv as you do, or pass it as the sample position)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================
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
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    
    
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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


def grains_POI_Das_2025_3(t=30, name='test'):
    """
    Do a single WAXS + SAXS scan at the end
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: visits five chosen grain positions (P1..P5) and takes a single long
    #   WAXS+SAXS shot at each (for two WAXS arc positions), stamping name with time/position.
    #
    # 💡 NEWER, EASIER WAY: visiting a list of positions and taking one shot at each is a
    #   "map" over a SampleList in the 'smi_plans' library, which records the position/
    #   time/beam into each image for you:
    #
    #     from smi_plans import map_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y)
    #     yield from map_bar(name, samples, t=t, dets=[pil900KW, pil2M])
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================
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
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    
    
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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an operando microfocus map repeated a chosen number of times — for
    #   each repeat and WAXS arc it rasters a y-by-x grid on the sample, stamping each run
    #   with elapsed time and position.
    #
    # 💡 NEWER, EASIER WAY: "repeat a map over time during an operando experiment" maps
    #   onto the 'smi_plans' operando/kinetics helpers; they take a bounded number of
    #   repeats and record the time/position/beam into each frame for you:
    #
    #     from smi_plans import operando_kinetics_run, map_grid_run
    #     yield from operando_kinetics_run(
    #         "Cu-Yao-exsitu_01",
    #         lambda: map_grid_run("Cu-Yao-exsitu_01", piezo.y, -300, 300, 10,
    #                              piezo.x, -300, 300, 10, t=t,
    #                              dets=[pil2M, pil900KW], reads=[xbpm3.sumX]),
    #         repeats=repeats,                    # your repeat count, unchanged
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 2.)
    # === end smi_plans note ================================================

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
    
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

# RE(pil2M.insert_beamstop('rod')    -> potentially changing beamstops, insert attenuators and check


def exsitu_swaxs_Das_2025_3(t=60, x_off=0, y_off=0):
    """
    Low divergence measurements, 9 points on each sample

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ex-situ SAXS+WAXS run over a sample bar — for each WAXS arc
    #   position it visits each sample and rasters a small 3x3 grid (9 points) on it.
    #
    # 💡 NEWER, EASIER WAY: running a bar with a small map at each sample is one call in
    #   the 'smi_plans' library; give it the samples as a SampleList and it visits, maps,
    #   names, and records the position/beam into each frame for you:
    #
    #     from smi_plans import map_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from map_bar("exsitu_Das_2025_3", samples, t=t, dets=[pil2M, pil900KW])
    #     # (the per-sample 3x3 grid and the WAXS-arc loop can be added as extra axes.)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 2.)
    # === end smi_plans note ================================================

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
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

def run_multiple_exposures_Das():
    """
    Run twice with diffent exposure time and offest in y in between
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience wrapper — runs the ex-situ bar twice, once with a
    #   short exposure and once with a long exposure (offset in y in between).
    #
    # 💡 NEWER, EASIER WAY: this is just two calls to the same measurement with different
    #   exposure times, which is fine to keep. Once you move the inner run to a smi_plans
    #   technique (see exsitu_swaxs_Das_2025_3 above), this wrapper stays a thin two-liner
    #   that simply calls it twice with different t= values. (Nothing here is broken.)
    # === end smi_plans note ================================================
    project_set('pw-exsitu-vac-5s')
    yield from exsitu_swaxs_Das_2025_3(t=5)
    project_set('pw-exsitu-vac-60s')
    yield from exsitu_swaxs_Das_2025_3(t=60, y_off=150)


def exsitu_swaxs_Das_2026_1(t=60, x_off=0, y_off=0):
    """
    Low divergence measurements, 9 points on each sample

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the 2026 version of the ex-situ SAXS+WAXS bar — for each WAXS arc
    #   position it visits each sample, optionally moves the WAXS beamstop, snaps an OAV
    #   (camera) picture on the first arc, and rasters a small 3x3 grid on each sample.
    #
    # 💡 NEWER, EASIER WAY: running a bar with a small map per sample is one call in the
    #   'smi_plans' library; hand it the samples as a SampleList and it visits, maps, and
    #   records the position/beam into each frame for you:
    #
    #     from smi_plans import map_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from map_bar("exsitu_Das_2026_1", samples, t=t, dets=[pil2M, pil900KW])
    #     # (the per-sample 3x3 grid, WAXS-arc loop, and beamstop move can be added as
    #     #  extra axes / setup steps.)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 2.)
    # === end smi_plans note ================================================

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
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

def run_multiple_exposures_Das_2026_1():
    """
    Run twice with diffent exposure time and offest in y in between
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience wrapper — runs the 2026 ex-situ bar twice, once short
    #   and once long (with a y offset in between).
    #
    # 💡 NEWER, EASIER WAY: this is just two calls to the same measurement with different
    #   exposure times, which is fine to keep. Once the inner run uses a smi_plans
    #   technique (see exsitu_swaxs_Das_2026_1 above), this wrapper stays a thin two-liner
    #   that calls it twice with different t= values. (Nothing here is broken.)
    # === end smi_plans note ================================================
    project_set('pw-exsitu-vac-5s')
    yield from exsitu_swaxs_Das_2026_1(t=5)
    project_set('pw-exsitu-vac-60s')
    yield from exsitu_swaxs_Das_2026_1(t=60, y_off=150)
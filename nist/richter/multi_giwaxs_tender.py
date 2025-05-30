from bluesky.utils import FailedStatus

def Cl_edge_measurments_2025_2_tiledstyle_guillaume(t=1):
# copied from 30-user-Stingelin.py
# used on 2024-1 to take the 'good' data on Sung0Joo's films
# uses att2_9
# 1 s exposures
# one aoi
# 2 wa angle (wa20 is done ontop of wa0)
# 4 pos: at 30 um a point this will slide a total of 4 mm
#

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

   
    names = [       'PBTTT_pristine',          'PBTTT_AcN',   'PBTTT_FeCl3_0p02',   'PBTTT_FeCl3_0p05',   'PBTTT_FeCl3_0p10',   'PBTTT_FeCl3_0p20',   'PBTTT_FeCl3_0p50',  'PBTTT_FeCl3_1p00',       'PVC',      'NaPSS' ]             
    x_piezo = [              -54000,              -54000,              -44000,              -33000,              -21000,               -9000,                4500,              14000,       30000,        50000]    
    x_hexa = [                  -12,                  -1,                   0,                   0,                   0,                   0,                   0,                  0,           0,            0 ]
    y_piezo = [                2700,                2700,                2700,                2700,                2700,                2700,                2700,               2700,        2700,         2700 ] 
    z_piezo = [                3000,                3000,                3000,                3000,                3000,                3000,                3000,               3000,        3000,         3000 ]
     

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    #FeCl3
    energies = -10 + np.asarray([2810.0, 2820.0, 2828.0, 2829.0, 2830.0, 2831.0, 2832.0, 2833.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])

    waxs_arc = [0, 20]
    ai0_all = -2.7
    ai_list = [1.6]


    s = Signal(name='target_file_name', value='')

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignment_gisaxs(0.7)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        yield from bps.mv(pil2M.beamstop.x_rod,6.7)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        dets = [pil2M, pil900KW]
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner1(counter=0):

            for wa in waxs_arc:
                # move the WAXS to the angle, try a few times if it fails
                trynum = 0
                while trynum < 5 and np.abs(waxs.arc.position - wa)> 0.1:
                    try:
                        yield from bps.mv(waxs, wa)
                    except FailedStatus:
                        print(f"Failed to move WAXS to {wa} degrees. Trying again")
                        trynum += 1
                        pass
                if trynum < 5:
                    print(f"WAXS moved to {wa} degrees successfully after {trynum} attempts.")
                else:
                    raise RuntimeError(f"Failed to move WAXS to {wa} degrees after 5 attempts.")
                
                # Do not take SAXS when WAXS detector in the way
                

                yield from bps.mv(piezo.x, xs)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs - counter * 30)
                        counter += 1
                        
                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])

                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs - counter * 30)
                        counter += 1
                        
                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner1())






from bluesky.utils import FailedStatus

def Cl_edge_measurments_2025_2_tiledstyle(t=1):
# copied from 30-user-Stingelin.py
# used on 2024-1 to take the 'good' data on Sung Joo's films
# uses att2_9
# 1 s exposures
# one aoi
# 2 wa angle (wa20 is done ontop of wa0)
# 4 pos: at 30 um a point this will slide a total of 4 mm
#

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

   
    names = [  'P3MEEET_1mMFeCl3_as_redo',    'P3MEEET_1mMFeCl3_10s',     'P3MEEET_1mMFeCl3_24s',     'P3MEEET_1mMFeCl3_39s',    'P3MEEET_1mMFeCl3_79s',              'P3MEEET_1mMFeCl3_159s',        'P3MEEET_1mMFeCl3_279s',      'P3MEEET_1mMFeCl3_439s', 'P3MEEET_1mMFeCl3_609s',  'P3MEEET_1mMFeCl3_909s',  'P3MEEET_1mMFeCl3_1209s',       'P3MEEET_1mMFeCl3_1809s' ]             
    x_piezo =  4000 + np.asarray([       -54000,                     -54000,                     -47000,                    -35000,                    -23000,                                -11000,                        1000,                         15000,                   26000,                    39000,                     48000,                          49000 ])
    x_hexa = [                  -14,                         -5,                         0,                          0,                         0,                                    0,                             0,                            10,                       0,                        0,                        2,                              14 ]
    y_piezo = [               2700,                        2700,                      2700,                       2700,                      2700,                                 2700,                           2700,                         2700,                    2700,                     2700,                     2700,                           2700 ] 
    z_piezo = [               3000,                        3000,                       3000,                       3000,                      3000,                                 3000,                            3000,                        3000,                    3000,                     3000,                     3000,                           3000 ]
    #y hexa 5
    #th hexa 3
    #z hexa 0
    #th piezo -1.5


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    #FeCl3
    energies = -10 + np.asarray([2810.0, 2820.0, 2828.0, 2829.0, 2830.0, 2831.0, 2832.0, 2833.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])

    waxs_arc = [0, 20]
    ai0_all = -2.7
    ai_list = [1.6]


    s = Signal(name='target_file_name', value='')

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignment_gisaxs(0.7)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        yield from bps.mv(pil2M.beamstop.x_rod,6.7)

        ai0 = piezo.th.position
        det_exposure_time(t, t)



        for wa in waxs_arc:
            # move the WAXS to the angle, try a few times if it fails
            trynum = 0
            while trynum < 5 and np.abs(waxs.arc.position - wa)> 0.1:
                try:
                    yield from bps.mv(waxs, wa)
                except FailedStatus:
                    print(f"Failed to move WAXS to {wa} degrees. Trying again")
                    trynum += 1
                    pass
            if trynum < 5:
                print(f"WAXS moved to {wa} degrees successfully after {trynum} attempts.")
            else:
                raise RuntimeError(f"Failed to move WAXS to {wa} degrees after 5 attempts.")
            
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            
            xs0 = xs


            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner1(xs0=xs0, wa=wa, ais=ais): # Lee edited 11:30 PM to keep counting up
                    counter = 0
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1
                        
                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return
                (yield from inner1(xs0=xs0, wa=wa, ais=ais))
                # Lee commented out to see if would run
                dets = [pil900KW, amptek]
                det_exposure_time(3, 3)
                yield from bps.sleep(5)
                bpm = xbpm2.sumX.get()
                name_fmt = "{sample}_amptek_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%energy.energy.position, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)

                yield from bp.count(dets, num=1)
                yield from bps.sleep(5)

                xs0 = piezo.x.position
                det_exposure_time(t, t)
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner2(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner2(xs0=xs0, wa=wa, ais=ais))
                xs0 = piezo.x.position
                name_fmt = "{sample}_pos3_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner3(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner3(xs0=xs0, wa=wa, ais=ais))
                xs0 = piezo.x.position
                name_fmt = "{sample}_pos4_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner4(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner4(xs0=xs0, wa=wa, ais=ais))
                # name_fmt = "{sample}_pos3_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # @bpp.stage_decorator(dets)
                # @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                # def inner3(counter=counter): # Lee edited 11:30 PM to keep counting up
                #     for e in energies:
                #         yield from bps.mv(energy, e)
                #         yield from bps.sleep(2)
                #         if xbpm2.sumX.get() < 50:
                #             yield from bps.sleep(2)
                #             yield from bps.mv(energy, e)
                #             yield from bps.sleep(2)
                #         yield from bps.mv(piezo.x, xs - counter * 30)
                #         counter += 1
                        
                #         bpm = xbpm2.sumX.get()
                #         sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                #         s.put(sample_name)
                #         print(f"\n\t=== Sample: {sample_name} ===\n")
                #         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                #     return counter
                # counter = (yield from inner3(counter))

                # name_fmt = "{sample}_pos4_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # @bpp.stage_decorator(dets)
                # @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                # def inner4(counter=counter): #Lee edited 11:30 PM to keep counting up
                #     for e in energies[::-1]:
                #         yield from bps.mv(energy, e)
                #         yield from bps.sleep(2)
                #         if xbpm2.sumX.get() < 50:
                #             yield from bps.sleep(2)
                #             yield from bps.mv(energy, e)
                #             yield from bps.sleep(2)
                #         yield from bps.mv(piezo.x, xs - counter * 30)
                #         counter += 1

                #         bpm = xbpm2.sumX.get()
                #         sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                #         s.put(sample_name)
                #         print(f"\n\t=== Sample: {sample_name} ===\n")
                #         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                #     return counter
                # counter = (yield from inner4(counter))

            yield from bps.mv(piezo.th, ai0)


def Cl_edge_measurments_2025_2_tiledstyle_singleWAXS(t=1):
    #best practice end of 2025_2
    # used on 2024-1 to take the 'good' data on Sung Joo's films
    # uses att2_9
    # 1 s exposures
    # one aoi
    # 2 wa angle (wa20 is done ontop of wa0)
    # 4 pos: at 30 um a point this will slide a total of 4 mm
    # select most megative location that wokrs (down in camera)


    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

   
    names = [                        'P3MEEET_1mMFeCl3_24s',        'P3MEEET_1mMFeCl3_39s',    'P3MEEET_1mMFeCl3_79s',              'P3MEEET_1mMFeCl3_159s',         'P3MEEET_1mMFeCl3_279s',      'P3MEEET_1mMFeCl3_439s',     'P3MEEET_1mMFeCl3_609s',  'P3MEEET_1mMFeCl3_909s',  'P3MEEET_1mMFeCl3_1209s',       'P3MEEET_1mMFeCl3_1809s' ]             
    x_piezo =  4000 + np.asarray([                   -47000,                       -35000,                    -23000,                                -11000,                           1000,                        15000,                       27000,                    39000,                     40000,                          49000 ])
    x_hexa = [                                            0,                            0,                         0,                                    0,                               0,                            0,                           0,                        0,                        12,                             14 ]
    y_piezo = [                                        2700,                         2700,                      2700,                                 2700,                            2700,                         2700,                        2700,                     2700,                      2700,                           2700 ] 
    z_piezo = [                                        3000,                         3000,                      3000,                                 3000,                            3000,                         3000,                        3000,                     3000,                      3000,                           3000 ]
    #y hexa 5
    #th hexa 3
    #z hexa 0
    #th piezo -1.5


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    #FeCl3
    energies = -10 + np.asarray([2810.0, 2820.0, 2828.0, 2829.0, 2830.0, 2831.0, 2832.0, 2833.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])

    waxs_arc = [0, 20]
    ai0_all = -2.7
    ai_list = [1.6]


    s = Signal(name='target_file_name', value='')

    for name, xs, ys, zs, xs_hexa in (list(zip(names, x_piezo, y_piezo, z_piezo, x_hexa))[2:]+list(zip(names, x_piezo, y_piezo, z_piezo, x_hexa))[:2]):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignment_gisaxs(0.7)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        yield from bps.mv(pil2M.beamstop.x_rod,6.7)

        ai0 = piezo.th.position
        det_exposure_time(t, t)



        for wa in waxs_arc:
            # move the WAXS to the angle, try a few times if it fails
            trynum = 0
            while trynum < 5 and np.abs(waxs.arc.position - wa)> 0.1:
                try:
                    yield from bps.mv(waxs, wa)
                except FailedStatus:
                    print(f"Failed to move WAXS to {wa} degrees. Trying again")
                    trynum += 1
                    pass
            if trynum < 5:
                print(f"WAXS moved to {wa} degrees successfully after {trynum} attempts.")
            else:
                raise RuntimeError(f"Failed to move WAXS to {wa} degrees after 5 attempts.")
            
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            
            xs0 = xs


            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner1(xs0=xs0, wa=wa, ais=ais): # Lee edited 11:30 PM to keep counting up
                    counter = 0
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1
                        
                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return
                (yield from inner1(xs0=xs0, wa=wa, ais=ais))
                # Lee commented out to see if would run
                dets = [pil900KW, amptek]
                det_exposure_time(3, 3)
                yield from bps.sleep(5)
                bpm = xbpm2.sumX.get()
                name_fmt = "{sample}_amptek_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%energy.energy.position, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)

                yield from bp.count(dets, num=1)
                yield from bps.sleep(5)

                xs0 = piezo.x.position
                det_exposure_time(t, t)
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner2(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner2(xs0=xs0, wa=wa, ais=ais))
                xs0 = piezo.x.position
                name_fmt = "{sample}_pos3_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner3(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner3(xs0=xs0, wa=wa, ais=ais))
                xs0 = piezo.x.position
                name_fmt = "{sample}_pos4_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner4(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        if xbpm2.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                        yield from bps.mv(piezo.x, xs0 - counter * 30)
                        counter += 1

                        bpm = xbpm2.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                    return counter
                (yield from inner4(xs0=xs0, wa=wa, ais=ais))
                # name_fmt = "{sample}_pos3_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # @bpp.stage_decorator(dets)
                # @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                # def inner3(counter=counter): # Lee edited 11:30 PM to keep counting up
                #     for e in energies:
                #         yield from bps.mv(energy, e)
                #         yield from bps.sleep(2)
                #         if xbpm2.sumX.get() < 50:
                #             yield from bps.sleep(2)
                #             yield from bps.mv(energy, e)
                #             yield from bps.sleep(2)
                #         yield from bps.mv(piezo.x, xs - counter * 30)
                #         counter += 1
                        
                #         bpm = xbpm2.sumX.get()
                #         sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                #         s.put(sample_name)
                #         print(f"\n\t=== Sample: {sample_name} ===\n")
                #         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                #     return counter
                # counter = (yield from inner3(counter))

                # name_fmt = "{sample}_pos4_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                # @bpp.stage_decorator(dets)
                # @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                # def inner4(counter=counter): #Lee edited 11:30 PM to keep counting up
                #     for e in energies[::-1]:
                #         yield from bps.mv(energy, e)
                #         yield from bps.sleep(2)
                #         if xbpm2.sumX.get() < 50:
                #             yield from bps.sleep(2)
                #             yield from bps.mv(energy, e)
                #             yield from bps.sleep(2)
                #         yield from bps.mv(piezo.x, xs - counter * 30)
                #         counter += 1

                #         bpm = xbpm2.sumX.get()
                #         sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                #         s.put(sample_name)
                #         print(f"\n\t=== Sample: {sample_name} ===\n")
                #         yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, piezo.th] + [s])
                #     return counter
                # counter = (yield from inner4(counter))

            yield from bps.mv(piezo.th, ai0)
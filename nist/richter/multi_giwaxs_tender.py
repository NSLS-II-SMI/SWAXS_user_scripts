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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant (chlorine/FeCl3-edge) grazing-incidence run over a bar
    #   of films — for each sample it aligns, sets attenuators + the SAXS beamstop, then
    #   at two WAXS arc positions sweeps the energy up and back down, sliding the spot in
    #   x between energies, recording a SAXS+WAXS frame at each energy.
    #
    # 👍 You're already on the modern path: one Bluesky "run" per scan (the
    #   @run_decorator inner), readbacks captured as channels via trigger_and_read, and
    #   the file name templated from a recorded field ('{target_file_name}'). smi_plans
    #   does exactly this — so the throwaway Signal + manual sample_name juggling can go away.
    #
    # 💡 NEWER, EASIER WAY: this is the same shape as the beamline's worked example
    #   (nist/richter/Cl_nexafs.py -> nexafs_run). For grazing-incidence resonant work
    #   smi_plans gives you presets that sweep energy at each aligned spot and record
    #   energy/beam/angle for you:
    #
    #     from smi_plans import giwaxs_bar, energy_axis, align_sample
    #     # giwaxs_bar aligns + measures each sample on the bar; energy_axis(energies)
    #     # is the resonant energy sweep (it manages the beam feedback + settling +
    #     # re-seek for you — that's what the 💡-tagged sleeps below are doing by hand).
    #     # See also xrr_resonant_run for resonant reflectivity.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ det_exposure_time lines;
    #    the 💡-tagged energy sleeps/re-seeks just become unnecessary after migrating.
    #    Good news: 'pil2M.beamstop.x_rod' below is already the CURRENT name — nothing
    #    broken there.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines are now plans — see
    #   the ⚠️ notes on them.
    # === end smi_plans note ================================================

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)

   
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
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)

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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the same resonant grazing-incidence run as above, but taking FOUR
    #   spots per sample (pos1..pos4, each its own run) plus an amptek fluorescence point,
    #   sweeping the energy up/down at each spot and sliding x between energies.
    #
    # 👍 Already modern: one run per spot (@run_decorator inner1..inner4), readbacks as
    #   channels (trigger_and_read), and the name templated from '{target_file_name}'.
    #
    # 💡 NEWER, EASIER WAY: smi_plans collapses the four near-identical inner generators
    #   into one preset call per spot, sweeps the energy for you, and records
    #   energy/beam/angle into each file (so the repeated boilerplate + the Signal go away):
    #
    #     from smi_plans import giwaxs_bar, energy_axis
    #     # energy_axis(energies) is the resonant sweep and manages the beam feedback +
    #     # settling + re-seek (the 💡-tagged sleeps below). The amptek point is just a
    #     # second acquire(...) with dets=[pil900KW, amptek]. (amptek is fine.)
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ det_exposure_time lines; the
    #    💡-tagged energy sleeps/re-seeks become unnecessary after migrating. Note:
    #    'pil2M.beamstop.x_rod' is already the CURRENT name — not broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines are now plans — see
    #   the ⚠️ notes on them.
    # === end smi_plans note ================================================

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)

   
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
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)



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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                det_exposure_time(3, 3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(3, 3)  — or at the prompt:  RE(det_exposure_time(3, 3)). (smi_plans' presets set exposure for you via t=.)
                yield from bps.sleep(5)
                bpm = xbpm2.sumX.get()
                name_fmt = "{sample}_amptek_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%energy.energy.position, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)

                yield from bp.count(dets, num=1)
                yield from bps.sleep(5)

                xs0 = piezo.x.position
                det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner2(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the "best practice" version of the resonant grazing-incidence run
    #   (this one starts the sample list at index 2). For each sample it aligns, then at
    #   each WAXS arc position takes four spots (pos1..pos4, each its own run) plus an
    #   amptek fluorescence point, sweeping energy up/down and sliding x between energies.
    #
    # 👍 This is already the tidy "tiled style": one run per spot, readbacks as channels,
    #   and the file name templated from a recorded field ('{target_file_name}').
    #
    # 💡 NEWER, EASIER WAY: smi_plans turns the four repeated inner generators into a
    #   single preset that sweeps energy at each aligned spot and records
    #   energy/beam/angle for you (so the boilerplate + throwaway Signal disappear):
    #
    #     from smi_plans import giwaxs_bar, energy_axis
    #     # energy_axis(energies) is the resonant sweep; it manages the beam feedback +
    #     # settling + re-seek (exactly what the 💡-tagged sleeps below do by hand).
    #     # See nist/richter/Cl_nexafs.py -> nexafs_run for the matching worked example.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ det_exposure_time lines; the
    #    💡-tagged energy sleeps/re-seeks become unnecessary after migrating. Note:
    #    'pil2M.beamstop.x_rod' is already the CURRENT name — not broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines are now plans — see
    #   the ⚠️ notes on them.
    # === end smi_plans note ================================================


    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)

   
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
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)



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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                det_exposure_time(3, 3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(3, 3)  — or at the prompt:  RE(det_exposure_time(3, 3)). (smi_plans' presets set exposure for you via t=.)
                yield from bps.sleep(5)
                bpm = xbpm2.sumX.get()
                name_fmt = "{sample}_amptek_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%energy.energy.position, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)

                yield from bp.count(dets, num=1)
                yield from bps.sleep(5)

                xs0 = piezo.x.position
                det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' presets set exposure for you via t=.)
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                @bpp.stage_decorator(dets)
                @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
                def inner2(xs0=xs0, wa=wa, ais=ais): # lee edited 11:30 PM top keep counting up
                    counter = 0
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
                        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this energy settle + the beam-loss re-seek just below — energy_axis/move_energy_fb do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
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
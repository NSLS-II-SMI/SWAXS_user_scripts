'''
2024/7/12, Friday Afternoon
#Scan Energy from 11150 to 11400 for Ir edge

setthreshold energy 16100 autog 11000

/nsls2/data/smi/legacy/results/data/2024_2/00003_YZhang


proposal_id('2024_2', '00003_YZhang')
Energy: 11.5 keV,   low divergence, in air
setthreshold energy 11500 autog 7500


sample_id(user_name = 'YZhang', sample_name = 'test' )
RE(bps.mv(waxs, 0))
RE(bp.count([pil2M, amptek, pil900KW ]))





In [1617]: sample_id(user_name = 'WL', sample_name = 'B0500_Ir_Edge' )
In [1618]: RE(bp.count([pil2M, amptek, pil900KW ]))
In [1621]: RE(bps.mv(waxs, 0))
In [1622]: RE(bp.count([pil2M, amptek, pil900KW ]))
In [1623]: RE(bps.mv(waxs, 20))
In [1624]: RE(bp.count([pil2M, amptek, pil900KW ]))

np.arange( 11150,11185, 5)
np.arange( 11185, 11195,  2 )
np.arange( 11195, 11246,  0.2 )
np.arange(  11246, 11260,  0.5 )
np.arange(  11261, 11282,  1 )
np.arange(  11282, 11345, 1.5 )
np.arange(   11345, 11400, 2 )


RUN1: 
B0500_IrE_FB_Bpst2s
Full beam, dets = [pil2M, pil900KW,  amptek ]
Sleep 2S between each energy
Scan E, E_reverse 

RE( Ir_edge_measurments_2024_7_12(t=1, sample = 'B0500_IrE_FB_Bpst2s'  ) ) 


RUN2: 
B0500_IrE_FB
Full beam, dets = [pil2M, pil900KW,  amptek ]
Sleep 0 between each energy
Scan E #, E_reverse 

RE( Ir_edge_measurments_2024_7_12(t=1, sample = 'B0500_IrE_FB_NoBpst', reverse=False, bps_sleep_time=0 ) )



RUN3
B0500_IrE_AB
Attenuated beam (4X) 
remove the beam stop
Sleep 0 between each energy
Scan E , E_reverse 
RE( Ir_edge_measurments_2024_7_12(t=1, sample = 'B0500_IrE_AB_NoBpst', reverse=True, bps_sleep_time=0 ) )



RUN4
Empty_AB
Attenuated beam (4X) 
remove the beam stop
Sleep 0 between each energy
Scan E 
RE( Ir_edge_measurments_2024_7_12(t=1, sample = 'Emp_IrE_AB_NoBpst', reverse=True, bps_sleep_time=0 ) )


sample_id(user_name = 'YZhang', sample_name = 'test' )
RE(bp.count([pil2M, amptek, pil900KW ]))

 





'''

user_name = 'JLi'


sample_dict = {  
                 1: 'Sam_A',  
                 2: 'Sam_B',  
                 3: 'Sam_C',  
                 4: 'Sam_D',
                 5: 'Sam_Empt',  
                 6: 'Sam_E', 
}
pxy_dict = {  
              1:  ( 45182, -2500     ) ,  
              2:   (32282, -2500) ,
              3:  ( 6882, -2500     ) ,
              4:  ( -12168, -2500   ) ,  
              5:  ( -18519, -2400     ) , 
              6:  ( -31219, -2700     ) ,  
          
 
  }

dx =  0
dy = 200 #-2000
ks = np.array(list((sample_dict.keys())))
pxy_dict = {k: [pxy_dict[k][0] + dx, pxy_dict[k][1] + dy] for k in ks}

x_list = np.array(list((pxy_dict.values())))[:, 0]
y_list = np.array(list((pxy_dict.values())))[:, 1]
sample_list = np.array(list((sample_dict.values())))


def run():    
    '''
    
    run()

    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over your list of samples; for each one it moves to the sample
    #   (mov_sam) and runs the sulfur-edge energy scan S_edge_one_sample on it.
    #
    # 💡 NEWER, EASIER WAY: notice this calls RE(...) inside a normal Python 'for' loop.
    #   That starts a brand-new run for every sample, so the samples aren't tied together
    #   in the saved data. The 'smi_plans' helper library can run a whole list of samples
    #   as ONE coordinated measurement, moving to each sample for you and recording which
    #   sample each image belongs to. The pattern is a "bar" plan, e.g.:
    #
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     RE(nexafs_bar(samples, np.arange(2460, 2480.2, .2), t=1, dets=[pil2M]))
    #
    #   (Then you run that ONE line instead of this loop. This is just a tidier option to
    #    try later — your loop below still works as-is.)
    # === end smi_plans note ================================================
    for  k  in ks:             
        mov_sam( k )
        RE(  S_edge_one_sample( sample = RE.md['sample']) )



def S_edge_one_sample(t=1, sample = None, reverse=False, bps_sleep_time=2,  ):
    '''

    RE( S_edge_one_sample(t=1, sample = 'test'  ) ) 
 


    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the X-ray energy across the sulfur edge (2460->2480.2 eV in
    #   0.2 eV steps) and takes a SAXS image at each step; optionally repeats the sweep
    #   backwards (reverse=True). Beam intensity is read from xbpm2 into the file name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy sweep (up, or up+down) in one line and records the energy + beam
    #   intensity straight into the saved data and the file name — so you don't hand-build
    #   "{energy}eV_bpm{xbpm}" or read xbpm2 yourself, and it handles the energy settling
    #   and beam feedback for you. Same scan as below:
    #
    #     from smi_plans import nexafs_run         # do this once at the top of your session
    #     yield from nexafs_run(
    #         sample,                              # the rest of the file name is added automatically
    #         np.arange(2460, 2480.2, .2),         # your energies, unchanged
    #         t=t,                                 # your exposure time, unchanged
    #         dets=[pil2M],
    #         updown=reverse,                      # do the down-sweep too when reverse=True
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the 'det_exposure_time' line marked ⚠️ which needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note
    #   on it). The energy 'sleep' lines still work — they're only flagged 💡 as no longer
    #   needed once you migrate.
    # === end smi_plans note ================================================

    dets = [pil2M ] #, pil900KW,  amptek ]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    Elist = np.arange( 2460, 2480.2, .2) #[:2]

    name_fmt = "{sample}_pos1_{energy}eV_bpm{xbpm}"
    for e in Elist:        
        yield from bps.mv(energy, e)
        if bps_sleep_time !=0:  # 💡 smi_plans: you can drop this settle wait (and the beam-recheck just below) once you migrate — move_energy_fb/energy_axis already wait for the energy to settle, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
            yield from bps.sleep(bps_sleep_time)
        if xbpm2.sumX.get() < 100:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)        
        bpm = xbpm2.sumX.get()
        sample_name = name_fmt.format(sample=sample, energy="%6.2f"%e,  xbpm="%4.3f"%bpm)
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    if reverse:
        name_fmt = "{sample}_pos2_{energy}eV_wa_{wa}_bpm{xbpm}"
        for e in Elist[::-1]:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)  # 💡 smi_plans: same as the up-sweep above — this settle wait and the beam-recheck are handled for you by move_energy_fb/energy_axis once you migrate. (Not broken, just no longer needed.)
            if xbpm2.sumX.get() < 10:
                yield from bps.sleep(2)
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)        
            bpm = xbpm2.sumX.get()
            sample_name = name_fmt.format(sample=sample, energy="%6.2f"%e, wa=20,  xbpm="%4.3f"%bpm)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


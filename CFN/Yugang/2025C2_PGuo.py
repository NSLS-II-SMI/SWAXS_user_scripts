'''
pas =318132
saf: 316677


proposal_swap(318132)



20250706
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air

%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C2_PGuo.py


move_waxs(0)  #the waxs beamstop should go to -54.8
Otherwise, we need to do the following:
1) go to the hutch, manually push the base of the WAXS beamstop to the inboard limit
2) go to the smartAct, channel  to do home - forward
3) open the beam, put att, check the waxs beam stop, and if needed put the beamstop - 54.8

if gap messed up
need to do 
energy.move(16.1) 


we need to make the waxs  to >=16, otherwise, it will block the right side of the 2M

Beamstop:
Rod: [6.8, 289, 10 ]
2M: [0,0]
Beam center:
WAXS: 16 deg 



#enable the WAXS
go the terminal, select WAXS
then enter Ctrl + X  --> to restart IOC for waxs detector, wait ~2 min, will * comes up


mov_sam(1)  #will go to sample 1
dir beam [ 746, 1106 ] 
beam stop [ 6.2, 289 ]


pass-318132 20250630_op_a_continous [572]: pil2M.rod_offset_x_mm.set(6.2)
Out[572]: Status(obj=Signal(name='pil2M_rod_offset_x_mm', parent='pil2M', value=6.2, timestamp=1751912742.8448317), done=True, success=True)

pass-318132 20250630_op_a_continous [573]: RE(pil2M.insert_beamstop( 'rod'))
Out[573]: ()                                                                                                                                                                                   

pass-318132 20250630_op_a_continous [574]: RE(SMI.modeAlignment())
/nsls2/data1/smi/shared/config/bluesky/profile_collection/startup/smiclasses/pilatus.py:586: UserWarning: beamstop will be removed, run restore_beamstop to put it back
  warn('beamstop will be removed, run restore_beamstop to put it back')
Out[574]: ()                                                                                                                                                                                   

pass-318132 20250630_op_a_continous [575]: RE(SMI.modeMeasurement())


'''

# username = 'PGuo'
# user_name = 'PGuo'



username = 'BW'
user_name = 'BW'


#########Change Sample name here
sample_dict = {   1: 'FAPBBR3_G', 2: 'BAIn1_G', 3: 'BAFAIn2_G', 4: 'NPBDF_1' , 5: 'NPBDF_2' , 6: 'NPBDF_3' , 7: 'NPBDF_4' , 8: 'FAPbBr3_S' , 9: 'CuPc_q1'  } 
pxy_dict = {    1:[ 47884, 2100 ] , 2: [ 35884, 2100  ]  , 3: [22884, 2000  ] , 
            4: [10884, 1700  ] , 5: [-116, 1600  ] , 6: [-11116, 1400  ] ,
              7: [-23116, 1300  ] , 8: [-37116, 1800  ] , 9: [-48116, 1800  ]  }





ks = np.array(list((sample_dict.keys())))
x_list = np.array(list((pxy_dict.values()))) [:, 0]
y_list = np.array(list((pxy_dict.values()))) [:, 1] #+ 1400
sample_list = np.array(list((sample_dict.values())))


# pxy_dict = {  k: [ pxy_dict[k][0], 1400   ]  for k in pxy_dict  }
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 4 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 5 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 2600   ]  for k in  [ 10 ]  } ) 
# #pxy_dict.update( {  k: [ pxy_dict[k][0], 2200   ]  for k in  [ 5, 6, 7 ]  } )



# Aligned_Dict = {}
# Aligned_Dict[1] = [ 1.353715, 1544.857]
# Aligned_Dict[2] = [ 1.798748, 1625.162 ]
# Aligned_Dict[3] = [ 0.327192,  1623.413]

# Aligned_Dict = {

#     0: { 'th': 1.353715, 'y': 1544.857},
# 1: { 'th': 1.798748, 'y': 1625.162},
# 2: { 'th': 0.327192, 'y': 1623.413},

# 3: {'th': 0.329494, 'y': 1829.588},
 
#  4: {'th': 0.266078, 'y': 1939.25},
#  5: {'th': -0.062271, 'y': 2063.779},
#  6: {'th': 0.078281, 'y': 2178.608},
#  7: {'th': -0.116335, 'y': 2244.538},
#  8: {'th': 0.013467, 'y': 2347.518},
#  9: {'th': 0.061605, 'y': 2572.846}}




# Aligned_Dict[4] = [ 0.140732 , 1425.0 7]
# Aligned_Dict[5] = [0.18900399999999998, 1070.096 ]
# Aligned_Dict[6] = [-0.142403, 949.092]
# Aligned_Dict[7] = 
# Aligned_Dict[8] = 
# Aligned_Dict[9] = 

#Aligned_Dict=align_gix_loop_samples( ii_start = 2)


#y_list = np.array(list((pxy_dict.values())))[:, 1] 
#print( x_list, y_list )

def align_gix_loop_samples( inc_ang = 0.15, ii_start = -1   ):      
    '''      
    Aligned_Dict =     align_gix_loop_samples(   )  
    #  0.48 -0.384     

     '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment-only pass over the bar — moves to each sample, runs the GISAXS
    #   alignment routine, and stores the found incident angle / y in a dict for the measurement
    #   plans to reuse.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you don't pre-align and carry a dict around. align_sample
    #   aligns each sample right when you measure it and saves the alignment WITH the data, and you
    #   describe the bar once as a SampleList:
    #     from smi_plans import SampleList, align_sample
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     # then pass align=align_sample to giwaxs_bar (see the measurement plans below)
    #   (Nothing here is broken — this is just the tidier, "align-and-record-together" approach.
    #    Note this helper calls RE(...) itself, which only works at the prompt, not inside a plan.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar     
    M, _, _ = get_motor(  ) 
    N = len( x_list )
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'  
    print('here')   
    Aligned_Dict = {}
    for ii, (x, sample) in enumerate(zip(x_list,sample_list)):    #loop over samples on bar
        if ii> ii_start:
            if ii == N-1:
                back_to_measureMode = True
            else:
                back_to_measureMode = False     
            print('Do alignment for sample: %s'%sample )
            RE( bps.mv(M.x, x) ) #move to next sample  
            RE( bps.mv(M.y, y_list[ii]) ) #move to next sample  

            if motor == 'pizeo':             
                RE( alignement_gisaxs(inc_ang  ) ) #run alignment routine          
            else:             
                RE( alignement_gisaxs_hex(inc_ang  ) ) #run alignment routine  
            M, TH, YH = get_motor(  )     
            Aligned_Dict[ii]={}
            Aligned_Dict[ii]['th']  = TH
            Aligned_Dict[ii]['y']  = YH
            print( ii, TH, YH )
    RE( smi.modeMeasurement() ) 
    print('THe alignment is DOne!!!')
    return Aligned_Dict




 
print('here@@@@@@@@@@')
def run_gix_loop_wsaxs(t=1, mode = [ 'waxs' ],  
                       angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                       waxs_angle_array = np.array( [  0, 10,  15      ] ) ,  
                       x_shift_array =  np.array( [ -2000, -1000, 0, 1000, 2000 ]), #np.linspace(-1, 1, 5),                      
                       Aligned_Dict = None ):        
       
    '''      
      #RE( run_gix_loop_wsaxs()) 


      Aligned_Dict=align_gix_loop_samples();RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))



    '''    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS/GIWAXS bar — for each WAXS arc it visits every (pre-aligned)
    #   sample, nudges through a few x positions and incident angles, and takes an image, packing
    #   the angle/position/SDD/arc into the file name by hand.
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a grazing-incidence bar like this and records the
    #   angle/arc/position/beam (and detector distance) straight INTO each image:
    #     from smi_plans import giwaxs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from giwaxs_bar(user_name, samples,
    #                           incident_angles=[0.05, 0.1, 0.15, 0.3, 0.6], t=t,
    #                           dets=[pil2M, pil900KW], align=align_sample)   # arc as extra axis
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    print( 'step--0' )
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'     
    if Aligned_Dict is None:    
        Aligned_Dict = align_gix_loop_samples( inc_ang = 0.15 )  
    print( Aligned_Dict )  
    M, _, _ = get_motor(   )  
    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     
        dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
        det_exposure_time(t,t)                  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t,t)  — or at the prompt:  RE(det_exposure_time(t,t)). (The smi_plans technique runs set exposure for you via t=.)
        for ii, (x, sample) in enumerate(zip(x_list,sample_list)):    #loop over samples on bar                
            yield from bps.mv(M.x, x )             
            TH = Aligned_Dict[ii]['th']  
            YH = Aligned_Dict[ii]['y']  
            yield from bps.mv(M.y, YH)  
            yield from bps.mv(M.th, TH)  
            th_meas = angle_arc + TH #piezo.th.position 
            th_real = angle_arc	         
            x_pos_array = x + x_shift_array   
            for j, x_meas in enumerate( x_pos_array) : # measure at a few x positions
                yield from bps.mv(M.x, x_meas)                 
                for i, th in enumerate(th_meas): #loop over incident angles
                    yield from bps.mv(M.th, th)  
                    name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
                    sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,
                    #scan_id=RE.md["scan_id"],
                )
                    sample_id(user_name=  user_name , sample_name=sample_name)                     
                    print(f'\n\t=== Sample: {sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
                    det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t,t)  — or at the prompt:  RE(det_exposure_time(t,t)). (The smi_plans technique runs set exposure for you via t=.)
            #print( 'HERE#############')
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)

def align_Linkam_sample():   
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the single sample on the Linkam heating stage and stores its
    #   incident angle / y in a dict for the temperature plans to reuse.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' align_sample aligns at measurement time and saves the
    #   result WITH the data, so you pass align=align_sample to the temperature run rather than
    #   stashing the angle/y in a dict.
    #   (Nothing here is broken — just a tidier approach. Note this helper calls RE(...) itself,
    #    which only works at the prompt, not inside another plan.)
    # === end smi_plans note ================================================
    Aligned_Dict= {}                   
    RE( alignement_gisaxs( 0.15  ) ) #run alignment routine          
    M, TH, YH = get_motor(  )   
    ii = 0   
    Aligned_Dict[ii]={}
    Aligned_Dict[ii]['th']  = TH
    Aligned_Dict[ii]['y']  = YH
    print( ii, TH, YH ) 
    RE( smi.modeMeasurement() ) 
    return    Aligned_Dict


def _run( Aligned_Dict, 
         sample_name = 'xxx',
         mode = [ 'waxs' ],  
        angle_arc = np.array([  0.15  ]),
         waxs_angle_array = np.array( [  0     ] ) ,   ):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the inner per-temperature measurement — at the current temperature it
    #   moves the (pre-aligned) sample to a few incident angles and takes an image at each,
    #   recording the Linkam temperature in the file name.
    # 💡 NEWER, EASIER WAY: this is the body the 'smi_plans' temperature runs do for you. With
    #   the Linkam configured as a heater, isothermal_kinetics_run / temperature_ramp_run drive
    #   the temperature AND record it (plus angle/position/beam) into each image automatically:
    #     from smi_plans import isothermal_kinetics_run, incidence_axis
    #     # set the temperature with the heater, then acquire over incidence_axis(...)
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now. Note the
    #    file name here is built from LThermal.temperature() by hand; smi_plans records it for you.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    RE.md['sample_name'] = sample_name
    RE.md['sample'] = sample_name
     
    M, _, _ = get_motor(   )  
    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     
        dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
        #det_exposure_time(t,t)  
        ii = 0    
        TH = Aligned_Dict[ii]['th']  
        YH = Aligned_Dict[ii]['y']  
        yield from bps.mv(M.y, YH)  
        yield from bps.mv(M.th, TH)  
        th_meas = angle_arc + TH #piezo.th.position 
        th_real = angle_arc	 
        for i, th in enumerate(th_meas): #loop over incident angles
            yield from bps.mv(M.th, th)  
            #lt = LThermal.temperature()
            t=1
            name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_T{lt:.2f}c_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
            _sample_name = name_fmt.format(sample=sample_name,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,lt=LThermal.temperature(),saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,)
                    #scan_id=RE.md["scan_id"],                
            sample_id(user_name=  user_name , sample_name=_sample_name)                     
            print(f'\n\t=== Sample: {_sample_name} ===\n') 
            yield from bp.count( dets, num=1)
            det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t,t)  — or at the prompt:  RE(det_exposure_time(t,t)). (The smi_plans technique runs set exposure for you via t=.)
            #print( 'HERE#############')
    RE.md['sample_name'] = 'test'
    RE.md['sample'] = 'tes'

def collect_data_atT(T, Aligned_Dict, sample_name = 'xxx', angle_arc = np.array([  0.15  ]),
         waxs_angle_array = np.array( [  0     ] )  ):
    '''
    
    collect_data_atT( 20, Aligned_Dict, sample_name = 'BAI_n1', angle_arc = np.array([  0.05, 0.1, 0.15, 0.3   ]),
         waxs_angle_array = np.array( [  0,      ] )  )
    
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sets the Linkam heater to a target temperature, waits for it to settle,
    #   then runs the per-temperature measurement (_run) once.
    # 💡 NEWER, EASIER WAY: setting a temperature, waiting, and measuring is exactly what the
    #   'smi_plans' isothermal-kinetics / temperature runs do — they ramp + settle + record the
    #   temperature with the data for you:
    #     from smi_plans import goto_temperature, isothermal_kinetics_run
    #     yield from goto_temperature(T)        # ramps and waits
    #   (Nothing here is broken — just a tidier approach. Note this calls RE(_run(...)) itself,
    #    which only works at the prompt, not inside another plan.)
    # === end smi_plans note ================================================

    #print('step...0 ')
    LThermal.setTemperature(   T   )
    LThermal.on() # turn on 

    while abs( LThermal.temperature() - T )  > .5 :            
        time.sleep( 3 ) 
    RE( _run( Aligned_Dict, sample_name = sample_name,
        mode = [ 'waxs' ], angle_arc = angle_arc, 
        waxs_angle_array = waxs_angle_array,   ) ) 
    




def Temperature_Linkam_Fast_ThreeTs(
                     Aligned_Dict, 
                     sample_name = 'BAI_n1',
                     T1= 300 - 273.15, #200 - 275.15
                     T2= 220 - 273.15, 
                     T3= 300 - 273.15,
                     mode = [ 'waxs' ],  
                     exp_time=1, 
                     angle_arc = np.array([  0.15  ]),
                     waxs_angle_array = np.array( [  0     ] ) ,  
                     sleep_time = 3, 
                     
                     ):
    ''' 
    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C2_PGuo.py

    Aligned_Dict= align_Linkam_sample(); #run this alignment once


    collect_data_atT( 140, Aligned_Dict, sample_name = 'NPB_4', 
    angle_arc = np.array([  0.05, 0.1, 0.15, 0.3   ]),
         waxs_angle_array = np.array( [  0,10    ] )  )
    


    Temperature_Linkam_Fast_ThreeTs(
                     Aligned_Dict, 
                     sample_name = 'NPB_Cont5',
                     T1= 430 - 273.15, #200 - 275.15
                     T2= 443 - 273.15, 
                     T3= 445 - 273.15,
                     mode = [ 'waxs' ],  
                     exp_time=1, 
                     angle_arc = np.array([  0.1  ]),
                     waxs_angle_array = np.array( [  10     ] ) ,  
                     sleep_time = 3,                      
                     )
     
    '''

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a fast 3-temperature Linkam cycle — ramps to T1, then while ramping to T2
    #   (and again to T3) it repeatedly runs the per-temperature measurement (_run), so you get a
    #   time/temperature series; finally it cools to 25 C and turns the heater off.
    # 💡 NEWER, EASIER WAY: measuring repeatedly while the temperature ramps is the 'smi_plans'
    #   temperature-ramp / kinetics combination, which drives the ramp and records the
    #   temperature with each image for you:
    #     from smi_plans import temperature_ramp_run     # or isothermal_kinetics_run per hold
    #   (Nothing here is broken except the exposure call at the end — see the ⚠️ on
    #    'det_exposure_time(0.5)' below. Note this calls RE(_run(...)) itself, prompt-only.)
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    print('step...0 ')
    LThermal.setTemperature(   T1   )
    LThermal.on() # turn on
    while abs( LThermal.temperature() - T1 )  > .5:            
        time.sleep( 3 ) 

    LThermal.setTemperature(   T2    )
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    print('step...1 ')
    while abs( LThermal.temperature() - T2 ) > .5:
        RE( _run( Aligned_Dict,  sample_name = sample_name, 
            mode = [ 'waxs' ], angle_arc = angle_arc, 
            waxs_angle_array = waxs_angle_array,   ) )   
        time.sleep( sleep_time ) 

    LThermal.setTemperature(   T3    )
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    while abs( LThermal.temperature() - T3 ) > .5:
        RE( _run( Aligned_Dict, sample_name = sample_name, 
            mode = [ 'waxs' ], angle_arc = angle_arc, 
            waxs_angle_array = waxs_angle_array,   ) )  
        time.sleep( sleep_time )    


    LThermal.setTemperature(   25    )
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    LThermal.off()
    RE.md["sample_name"] = 'test'











def Temperature_Linkam_Step(
                     Aligned_Dict, 
                     sample_name = 'xxx',
                     TL = 200 - 273.15,
                     TH = 320 - 273.15,  
                     Tnum = 30, 
                     mode = [ 'waxs' ],  
                     exp_time=1, 
                     angle_arc = np.array([  0.05, 0.1, 0.15, 0.3  ]),
                     waxs_angle_array = np.array( [  0, 10     ] ) ,  
                     sleep_time = 3, 
                     
                     ):
    ''' 
    Aligned_Dict= align_Linkam_sample();
    RE( Temperature_Linkam_Step( Aligned_Dict ) 
     
    '''
    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a Linkam temperature step-series — steps the temperature from TH down to TL
    #   (then back up) in Tnum steps, measuring (collect_data_atT) at each; finally cools to 25 C
    #   and turns the heater off.
    # 💡 NEWER, EASIER WAY: stepping through a list of temperatures and measuring at each is the
    #   'smi_plans' temperature combination, which ramps/settles and records the temperature with
    #   each image:
    #     from smi_plans import temperature_ramp_run, goto_temperature
    #     # step a list of setpoints (TH..TL..TH); goto_temperature at each, then acquire
    #   (Nothing here is broken except the exposure call at the end — see the ⚠️ on
    #    'det_exposure_time(0.5)' below.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    Tlist = np.linspace( TH, TL, Tnum ) 
    for T in Tlist:
        collect_data_atT(T, Aligned_Dict, sample_name = sample_name,angle_arc = angle_arc, 
            waxs_angle_array = waxs_angle_array,   ) 
    Tlist = np.linspace( TL, TH, Tnum ) 
    for T in Tlist:
        collect_data_atT(T, Aligned_Dict, sample_name = sample_name, angle_arc = angle_arc, 
            waxs_angle_array = waxs_angle_array,   ) 
 
    LThermal.setTemperature(   25    )
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    LThermal.off()
    RE.md["sample_name"] = 'test'




# def Temperature_Linkam_Fast(
#                      Aligned_Dict, 
#                      name='temp',
#                      TL = 200 - 273.15,
#                      TH = 320 - 273.15,  
#                      mode = [ 'waxs' ],  
#                      exp_time=1, 
#                      angle_arc = np.array([  0.15 ]),
#                      waxs_angle_array = np.array( [  0     ] ) ,  
#                      sleep_time = 3, 
                     
#                      ):
#     ''' 
#     Aligned_Dict= align_Linkam_sample(); 
#     RE( Temperature_Linkam_Fast( Aligned_Dict ) 
     
#     '''

#        # function loop to bring linkam to temp, hold and measure
# # Function will begin at start_temp and take a SAXS measurement at every temperature given 

#     def _do_Tfast():
#         M, _, _ = get_motor(   )  
#         for waxs_angle in waxs_angle_array: # loop through waxs angles        
#             yield from bps.mv(waxs, waxs_angle)     
#             dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
#             #det_exposure_time(t,t)  
#             ii = 0    
#             TH = Aligned_Dict[ii]['th']  
#             YH = Aligned_Dict[ii]['y']  
#             yield from bps.mv(M.y, YH)  
#             yield from bps.mv(M.th, TH)  
#             th_meas = angle_arc + TH #piezo.th.position 
#             th_real = angle_arc	 
#             for i, th in enumerate(th_meas): #loop over incident angles
#                 yield from bps.mv(M.th, th)  
#                 #lt = LThermal.temperature()
#                 name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_T{lt:.2f}c_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
#                 sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,lt=LThermal.temperature(),saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,)
#                         #scan_id=RE.md["scan_id"],                
#                 sample_id(user_name=  user_name , sample_name=sample_name)                     
#                 print(f'\n\t=== Sample: {sample_name} ===\n') 
#                 yield from bp.count( dets, num=1)
#                 det_exposure_time(t,t)    
#                 #print( 'HERE#############')
            
    
#     LThermal.setTemperature(   TL    )
#     # LThermal.setTemperatureRate(ramp)
#     LThermal.on() # turn on 
#     while LThermal.temperature() > TL + 1.0 :
#         do_Tfast()
#         time.sleep( sleep_time ) 


#     LThermal.setTemperature(   TH    )
#     # LThermal.setTemperatureRate(ramp)
#     LThermal.on() # turn on 
#     while LThermal.temperature() < TH - 1.0 :
#         do_Tfast()    
#         time.sleep( sleep_time )    

#     LThermal.setTemperature(   25    )
#     sample_id(user_name='test', sample_name='test')
#     det_exposure_time(0.5)
#     LThermal.off()
#     RE.md["sample_name"] = 'test'




def insitu_tgix_samples(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 5      ):  

    '''

    Aligned_Dict =   align_gix_loop_samples()      
    
    RE( insitu_tgix_samples(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 5      ) ) 
    

    '''


    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time-resolved GISAXS loop — for up to run_time seconds it keeps
    #   cycling over the (pre-aligned) bar, taking SAXS+WAXS images at a few x positions per
    #   sample, sleeping sleep_time between passes.
    # 💡 NEWER, EASIER WAY: repeatedly re-measuring a bar over time is the 'smi_plans' kinetics /
    #   time-series combination, which timestamps and records each pass with the data:
    #     from smi_plans import time_series_run, giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     # loop a giwaxs_bar over time, or use time_series_run with the bar as the inner acquire
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    t=1
    dets = [pil2M, pil900KW]
    incident_angle=[      0.15   ]  
    angle_arc = np.array( incident_angle )
    #x_shift_array = np.array( [ -400, 0, 400 ])
    x_shift_array = np.array( [ -5000, 0, 5000 ]) #25000 #
    y_shift_array = np.array( [  0  ])

    username = user_name
    align= False 
    camera = False #True
    waxs_angle = 20
    #sleep_time = 60  #how frequently we collect the data
    # bps.mv(waxs, 15)   
    CTS = 0   
    M, _, _ = get_motor(   )   

    ks = list( sample_dict.keys() ) 
    t0 = time.time()
    while (time.time() - t0 ) < run_time:
        print('The CTS is %s ************ '%CTS)
         
        for ii, k in enumerate(ks): #loop samples
            x = pxy_dict[k][0]
            sample = sample_dict[k] 

            yield from bps.mv(M.x, x) #move to next sample              
            TH = Aligned_Dict[ii]['th']  
            YH = Aligned_Dict[ii]['y']  
            yield from bps.mv(M.y, YH)  
            yield from bps.mv(M.th, TH)  
        

            th_meas = angle_arc + TH #piezo.th.position 
            th_real = angle_arc	         
            x_pos_array = x + x_shift_array                
            y_pos_array = YH + y_shift_array
            for j, x_meas in enumerate( x_pos_array) : # measure at a few x positions
                yield from bps.mv(M.x, x_meas)                               
                for i, th in enumerate(th_meas): #loop over incident angles
                    yield from bps.mv(M.th, th)  
                    name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
                    sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t )
                    sample_id(user_name=  user_name , sample_name=sample_name)                     
                    print(f'\n\t=== Sample: {sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
                    det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t,t)  — or at the prompt:  RE(det_exposure_time(t,t)). (The smi_plans technique runs set exposure for you via t=.)
                    if camera: 
                        save_ova( sample_name )
                        save_hex( sample_name )     

        CTS +=1
        time.sleep(  sleep_time  )
 



def run_giwaxs_Kim(t=1, username=username):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS/GIWAXS bar — for each sample it moves x and aligns, then for each
    #   WAXS arc (alternating direction), a few x positions, and several incident angles takes an
    #   image (SAXS+WAXS at the largest arc, WAXS-only otherwise), packing the angle/arc/position/
    #   scan-id into the file name by hand.
    # 💡 NEWER, EASIER WAY:  from smi_plans import giwaxs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list)
    #     yield from giwaxs_bar(username, samples,
    #                           incident_angles=[0.05, 0.08, 0.10, 0.15, 0.2, 0.3], t=t,
    #                           dets=[pil900KW, pil2M], align=align_sample)
    #   (giwaxs_bar_arc_economy can alternate the WAXS-arc direction like 'inverse_angle' does;
    #    the angle/arc/position/beam/scan-id are recorded straight into each image.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW' (the WAXS-only
    #   'else' branch still lists it); (2) the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # define names of samples on sample bar
    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"
    angle_arc = np.array([0.05, 0.08, 0.10, 0.15, 0.2, 0.3])  # incident angles
    waxs_angle_array = np.array(
        [7, 27, 47]
    )  # 4*3.14/(12.39842/16.1)*np.sin((7*6.5+3.5)*3.14/360) = 6.760 A-1
    # dets = [pil300KW, pil2M] # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
    max_waxs_angle = np.max(waxs_angle_array)
    x_shift_array = np.linspace(-500, 500, 3)  # measure at a few x positions
    inverse_angle = False
    cts = 0
    for ii, (x, sample) in enumerate(
        zip(x_list, sample_list)
    ):  # loop over samples on bar
        yield from bps.mv(piezo.x, x)  # move to next sample

        # yield from  bps.mv(piezo.y, 4000  ) #move y to 4000

        yield from alignement_gisaxs(0.1)  # run alignment routine
        th_meas = angle_arc + piezo.th.position
        th_real = angle_arc
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        x_pos_array = x + x_shift_array
        if inverse_angle:
            Waxs_angle_array = waxs_angle_array[::-1]
        else:
            Waxs_angle_array = waxs_angle_array
        for waxs_angle in Waxs_angle_array:  # loop through waxs angles
            yield from bps.mv(waxs, waxs_angle)
            if waxs_angle == max_waxs_angle:
                dets = [
                    pil900KW,
                    #pil300KW,
                    pil2M,
                ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
                print("Meausre both saxs and waxs here for w-angle=%s" % waxs_angle)
            else:
                dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

            for x_meas in x_pos_array:  # measure at a few x positions
                yield from bps.mv(piezo.x, x_meas)
                for i, th in enumerate(th_meas):  # loop over incident angles
                    yield from bps.mv(piezo.th, th)
                    if inverse_angle:
                        name_fmt = "{sample}_{th:5.4f}deg_waxsN{waxs_angle:05.2f}_x{x:05.2f}_expt{t}s_sid{scan_id:08d}"
                    else:
                        name_fmt = "{sample}_{th:5.4f}deg_waxsP{waxs_angle:05.2f}_x{x:05.2f}_expt{t}s_sid{scan_id:08d}"
                    sample_name = name_fmt.format(
                        sample=sample,
                        th=th_real[i],
                        waxs_angle=waxs_angle,
                        x=x_meas,
                        t=t,
                        scan_id=RE.md["scan_id"],
                    )
                    sample_id(user_name=username, sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    # yield from bp.scan(dets, energy, e, e, 1)
                    # yield from bp.scan(dets, waxs, *waxs_arc)
                    print(dets)
                    yield from bp.count(dets, num=1)
                    # print( 'HERE#############')
        inverse_angle = not inverse_angle
        cts += 1
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)



#def alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1):



def temp_series_grid(name='temp',
                     temps = np.linspace(32,26,13),
                     exp_time=1, 
                     hold_delay=120, 
                     dets=[pil2M], 
                     xs=np.linspace(-13,-12,11), 
                     ys=np.linspace(-2.3,-2.8,6)):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature x position grid — over an x/y grid it ramps the Linkam heater
    #   through a list of temperatures (waiting/equilibrating at each) and takes a SAXS image,
    #   writing the file name into a Signal so it lands in the saved data.
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' temperature + map combination. The heater
    #   ramp/settle is handled for you, the x/y grid is a map run, and the temperature/SDD/energy
    #   are recorded into each image (no hand-built '{target_file_name}' Signal needed):
    #     from smi_plans import temperature_ramp_run, map_grid_run, goto_temperature
    #     # per temperature (goto_temperature) run a map_grid_run over xs/ys, or compose axes
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 3.)
    # === end smi_plans note ================================================
       # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    

    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (The smi_plans technique runs set exposure for you via t=.)

    s = Signal(name='target_file_name', value='')
    RE.md["sample_name"] = '{target_file_name}'
    print(f'starting grid scan of {len(xs)*len(ys)} points')
    for xp in xs:

        yield from mv(stage.x,xp)
        for yp in ys:
            yield from mv(stage.y,yp)
            print(f'beginning measurement at x={xp}, y={yp}')
            for i, temp in enumerate(temps):
                print(f'setting temperature {temp}')
                LThermal.setTemperature(temp)

                while abs(LThermal.temperature()-temp)>0.2:
                    yield from bps.sleep(10)
                    print(f'{LThermal.temperature()} is too far from {temp} setpoint, waiting 10s')

                print('Reached setpoint', temp)
                if i==0:
                    print(f'Beginning equilibration of {2*hold_delay} seconds')
                    yield from bps.sleep(2*hold_delay)
                else:
                    print(f'Beginning equilibration of {hold_delay} seconds')
                    yield from bps.sleep(hold_delay)



                # Metadata
                sdd = pil2m_pos.z.position / 1000

                # Sample name
                name_fmt = ("{sample}_{energy}eV_sdd{sdd}m_temp{temp}_x{x}_y{y}")
                sample_name = name_fmt.format(sample = name,
                                              energy = "%.2f" % energy.energy.position , 
                                              sdd = "%.1f" % sdd, 
                                              temp = "%.1f" % temp, 
                                              x= "%.1f" % xp, 
                                              y= "%.1f" % yp)
                sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})

                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'







def GIWAXS_TD_run():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature-dependent GIWAXS run on the Linkam stage — aligns each sample
    #   warm, cools (re-checking alignment), then at each target temperature measures WAXS at a
    #   set of incident angles per sample, recording the temperature/angle/beam in the file name.
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' temperature + GIWAXS combination. The heater
    #   ramp/settle is handled by the temperature helpers, align_sample aligns and saves the
    #   result, and giwaxs_bar sweeps the incident angle — all recording the values into the data:
    #     from smi_plans import temperature_ramp_run, giwaxs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_hexa, y=y_piezo, z=z_piezo)
    #     # per temperature: goto_temperature(T); then giwaxs_bar(incident_angles=ai_list, ...)
    #   (Nothing here is broken — this is a tidier, fully-recorded way to do the same run. The
    #    stepped WAXS-arc walk-ins / sleeps are the kind of scaffolding smi_plans handles for you.)
    # === end smi_plans note ================================================
    T_start = 20
    T_array = [-70,-50,25]
    names = ['PS3',       'PS7',     'PS11']
    
    x_hexa = [2.5 ,     -4,           -11]
    y_piezo = [0.2,       0.2,    0.2] ### piezo here is just the name, it is actually moving hexa. don't mess with the piezo
    z_piezo =  [3,3,3]

    assert len(x_hexa) == len(y_piezo), f"Number of X coordinates ({len(x_hexa)}) is different from number of y positions ({len(y_piezo)})"
    assert len(x_hexa) == len(z_piezo), f"Number of X coordinates ({len(x_hexa)}) is different from number of z positions ({len(z_piezo)})"
    assert len(x_hexa) == len(names), f"Number of X coordinates ({len(x_hexa)}) is different from number of z positions ({len(names)})"

    ai0_list = []
    y0_list = []
    ai0_list_cold = []
    y0_list_cold = []
    ai_list = [0.08, 0.1, 0.12, 0.15, 0.2]
    dets = [pil900KW]
    yield from bps.mv(LThermal.lnp_mode_set,'Auto')
    LThermal.setTemperatureRate(20)

    # Move to first temperature
    LThermal.setTemperature(T_start)
    LThermal.on()
    yield from bps.sleep(60*LThermal.ramptime.get()) 
    wait_counter=0
    while(abs(LThermal.temperature()-T_start)>1):
        yield from bps.sleep(10)
        wait_counter+=1
        if wait_counter>5*6:
            raise TimeoutError("Linkam is not getting to temperature!")
        ## 


    ### align the samples first before cooling
    for name, ys, zs, xs_hexa in zip(names, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(waxs, 15)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys)
        yield from bps.mv(stage.z, zs)

        yield from alignement_gisaxs_hex(0.15)
        ai0 = stage.th.position
        ypos = stage.y.position
        ai0_list.append(ai0)
        y0_list.append(ypos)
        print(f'{name} position is th={ai0},y={ypos}')
        print(f'ai0 list is {ai0_list} and y list is {y0_list}')
    
    ### move waxs arc back in for waxs
    yield from bps.mv(waxs, 10)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 6)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 5)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 4)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 3)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 2)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 1)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 0)

    # measure the first temperature waxs
    for name, ys, zs, xs_hexa, ai0 in zip(names, y0_list, z_piezo, x_hexa, ai0_list):
        yield from bps.mv(waxs, 0)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys)
        yield from bps.mv(stage.z, zs)
            
        for k, ais in enumerate(ai_list):
            yield from bps.mv(stage.th, ai0 + ais)

            name_fmt = "{sample}_{temp}C_ai{ai}_wa{wax}_bpm{xbpm}"
        
            bpm = xbpm2.sumX.get()
            sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=0, xbpm="%4.3f"%bpm,temp = "%3.2f"%T_start)
            sample_id(user_name="NS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)    

    # Move to first cold temperature
    # ai0 list is [0.454, 0.428, 0.38] and y list is [0.243, 0.271, 0.31]
    LThermal.setTemperature(T_array[0])
    LThermal.on()
    yield from bps.sleep(60*LThermal.ramptime.get()) 
    wait_counter=0
    while(abs(LThermal.temperature()-T_array[0])>1):
        yield from bps.sleep(10)
        wait_counter+=1
        if wait_counter>5*6:
            raise TimeoutError("Linkam is not getting to temperature!")
        ## 

    # check alignment again at first temperature
    for name, ys, zs, xs_hexa in zip(names, y0_list, z_piezo, x_hexa):
        yield from bps.mv(waxs, 15)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys)
        yield from bps.mv(stage.z, zs)

        yield from alignement_gisaxs_hex(0.15)
        ai0_cold = stage.th.position
        ypos_cold = stage.y.position
        ai0_list_cold.append(ai0_cold)
        y0_list_cold.append(ypos_cold)
        print(f'{name} position is th={ai0_cold},y={ypos_cold}')
        print(f'ai0 list is {ai0_list_cold} and y list is {y0_list_cold}')
    for i, cold_align in enumerate(ai0_list_cold):
        if abs(ai0_list_cold[i] - ai0_list[i]) > 0.015:
            raise ValueError(f'ai0 alignment at cold T ({ai0_list_cold}) was way far off initial alignment ({ai0_list})')
        if abs(y0_list_cold[i] - y0_list[i]) > 0.03:
            raise ValueError(f'y alignment at cold T ({y0_list_cold}) was way far off initial alignment ({y0_list})')

    ### move waxs arc back in for waxs
    yield from bps.mv(waxs, 10)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 6)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 5)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 4)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 3)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 2)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 1)
    yield from bps.sleep(1)
    yield from bps.mv(waxs, 0)
    
    for T in T_array:

        LThermal.setTemperature(T)
        LThermal.on()
        yield from bps.sleep(60*LThermal.ramptime.get()) 
        wait_counter=0
        while(abs(LThermal.temperature()-temperature)>1):
            yield from bps.sleep(10)
            wait_counter+=1
            if wait_counter>5*6:
                raise TimeoutError("Linkam is not getting to temperature!")
            
        ### at a temp, do a quick T hold
        yield from bps.sleep(150)

        ## measure the waxs for each sample 
        for name, ys, zs, xs_hexa, ai0 in zip(names, y0_list, z_piezo, x_hexa, ai0_list):
            yield from bps.mv(waxs, 0)
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(stage.y, ys)
            yield from bps.mv(stage.z, zs)

                
            for k, ais in enumerate(ai_list):
                yield from bps.mv(stage.th, ai0 + ais)

                name_fmt = "{sample}_{temp}C_ai{ai}_wa{wax}_bpm{xbpm}"
            
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=0, xbpm="%4.3f"%bpm, temp = "%3.2f"%T)
                sample_id(user_name="NS", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)    

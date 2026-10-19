'''
pas =318132
saf: 316677


proposal_swap(318132)



20250706
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air

%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C2_Kim.py


move_waxs(0)  #the waxs beamstop should go to -54.8  (-58.4 ????)
Otherwise, we need to do the following:
1) go to the hutch, manually push the base of the WAXS beamstop to the inboard limit
2) go to the smartAct, channel  to do home - forward
3) open the beam, put att, check the waxs beam stop, and if needed put the beamstop - 54.8

if gap messed up
need to do 
energy.move(16.1) 


we need to make the waxs  to >=16, otherwise, it will block the right side of the 2M

Beamstop:
Rod: [6.8, 289, 10 ]   --> new pos 5.5
2M: [0,0]
Beam center:
WAXS: 20 deg 



#enable the WAXS
go the terminal, select WAXS
then enter Ctrl + X  --> to restart IOC for waxs detector, wait ~2 min, will * comes up


mov_sam(1)  #will go to sample 1
dir beam [ 746, 1106 ] 
beam stop [ 5.5, 289 ]
SAXS 6 meters
#for DUAN: pil2M.rod_offset_x_mm.set(6.0)




pass-318132 20250630_op_a_continous [572]: pil2M.rod_offset_x_mm.set(5.5)
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



username = 'Kim'
user_name = 'Kim'

username = 'Duan'
user_name = 'Duan'


#########Change Sample name here
#sample_dict = {   1: 'RTA_400C_2', 2: 'RTA_450C_2', 3: 'RTA_500C_2' } 
#pxy_dict = {    1:[ -39387, 4613 ] , 2: [ -34587, 4613  ]  , 3: [-27987, 4613  ]  }

#sample_dict = {   1: 'Zr25_41_2Pr50' } 
#pxy_dict = {   1: [-19305, 4600  ]  } # 1:[ -10530, 4400 ]   }

sample_dict = {   1: '6nm_RTA_450C', 2: '6nm_RTA_400C', 3: '6nm_RTA_350C', 4: '6nm_RTA_AD' } 
pxy_dict = {   1: [14438, 4796  ], 2: [7738, 4796  ], 3: [-5512, 4796], 4: [-12762, 4796] } 


sample_dict = {   1: 'CsPbBr3_S', 2: 'CsPbBr3_L' , 3: 'Mica' } 
pxy_dict = {   1: [ -13400, 5300  ], 2: [ -6000, 5300], 3:  [ 4600,  5300] } 




sample_dict = {   1:  'Mica' ,  2: 'CsPbBr3_S',} 
pxy_dict = {   1:   [ 4600,  5300] ,  2:  [ -14200, 5295  ] } 


# pxy_dict = {   1: [-14407, 4668 ]  } 

ks = np.array(list((sample_dict.keys())))
x_list = np.array(list((pxy_dict.values()))) [:, 0]
y_list = np.array(list((pxy_dict.values()))) [:, 1] #+ 1400
sample_list = np.array(list((sample_dict.values())))


#Aligned_Dict = {};Aligned_Dict[1] = [ 0.58, 4700 ]
##  RE(SMI.modeAlignment())
# manually change THETA to ~ 0.58 
#RE(alignement_height())


#Aligned_Dict = {};Aligned_Dict[0] = dict( th = 0.6564, y = 4946 ) 
#Aligned_Dict = {};Aligned_Dict[0] =  dict( th = 0.785, y = 4841 )  
#     RE(SMI.modeMeasurement())
#     RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))



#alignment for the long samples
# pass-313483 test [239]: Aligned_Dict
# Out[239]: {0: {'th': 0.52,  'y': 4595 }}




# pxy_dict = {  k: [ pxy_dict[k][0], 1400   ]  for k in pxy_dict  }
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 4 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 5 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 2600   ]  for k in  [ 10 ]  } ) 
# #pxy_dict.update( {  k: [ pxy_dict[k][0], 2200   ]  for k in  [ 5, 6, 7 ]  } )



# Aligned_Dict = {}
# Aligned_Dict[1] = [ 1.353715, 1544.857]
# Aligned_Dict[2] = [ 1.798748, 1625.162 ]
# Aligned_Dict[3] = [ 0.327192,  1623.413]



#Aligned_Dict=align_gix_loop_samples( ii_start = 2)


#y_list = np.array(list((pxy_dict.values())))[:, 1] 
#print( x_list, y_list )



#RE( smi.modeMeasurement() ) 



def align_gix_loop_samples( inc_ang = 0.15, ii_start = -1   ):      
    '''      
    Aligned_Dict =     align_gix_loop_samples(   )  
    #  0.48 -0.384     

     '''
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
    RE(bps.mv( pil2M.beamstop.x_rod, 5.5 ) )

    print('THe alignment is DOne!!!')
    return Aligned_Dict

#bps.mv(self.beamstop.x_pin, self.pd_safe_pos.get())


 
print('here@@@@@@@@@@')
def run_gix_loop_wsaxs(t=1, mode = [ 'waxs' ],  
                       angle_arc = np.array([ 0.01, 0.05, 0.08, 0.1, 0.15, 0.2   ]),
                       waxs_angle_array = np.array( [  0, 20     ] ) ,  
                       #x_shift_array =  np.array( [ -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50 ]), #np.array( [-250, 0, 250]), #np.linspace(-1, 1, 5),                      
                       #x_shift_array =  np.array( [ -50, 0, 50 ]) ,
                       x_shift_array =  np.array( [ -1000, -500,  0, 500, 1000 ]) ,
                       Aligned_Dict = None ):        
       
    '''      
      #RE( run_gix_loop_wsaxs()) 


    Aligned_Dict=align_gix_loop_samples();RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))

     
    RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))

    '''    
    print( 'step--0' )
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'     
    if Aligned_Dict is None:    
        Aligned_Dict = align_gix_loop_samples( inc_ang = 0.15 )  
    print( Aligned_Dict )  
    M, _, _ = get_motor(   )  
    yield from bps.mv( pil2M.beamstop.x_rod, 5.5 ) 


    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     
        dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
        det_exposure_time(t,t)                  
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
                    det_exposure_time(t,t)    
            #print( 'HERE#############')
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)



def align_Linkam_sample():   
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
            det_exposure_time(t,t)    
            #print( 'HERE#############')
    RE.md['sample_name'] = 'test'
    RE.md['sample'] = 'tes'

def collect_data_atT(T, Aligned_Dict, sample_name = 'xxx', angle_arc = np.array([  0.15  ]),
         waxs_angle_array = np.array( [  0     ] )  ):
    '''
    
    collect_data_atT( 20, Aligned_Dict, sample_name = 'BAI_n1', angle_arc = np.array([  0.05, 0.1, 0.15, 0.3   ]),
         waxs_angle_array = np.array( [  0,      ] )  )
    
    '''

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
    det_exposure_time(0.5)
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
    det_exposure_time(0.5)
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
                    det_exposure_time(t,t)    
                    if camera: 
                        save_ova( sample_name )
                        save_hex( sample_name )     

        CTS +=1
        time.sleep(  sleep_time  )
 



def run_giwaxs_Kim(t=1, username=username):
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
        det_exposure_time(t, t)
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
                dets = [pil900KW, pil300KW]

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
    det_exposure_time(0.5)



#def alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1):



def temp_series_grid(name='temp',
                     temps = np.linspace(32,26,13),
                     exp_time=1, 
                     hold_delay=120, 
                     dets=[pil2M], 
                     xs=np.linspace(-13,-12,11), 
                     ys=np.linspace(-2.3,-2.8,6)):
       # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    

    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)

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

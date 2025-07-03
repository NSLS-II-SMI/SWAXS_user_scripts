"""
NOTES:

# load this macro

 
####%run -i /home/xf12id/.ipython/profile_collection/startup/users/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py


# Setup

SAF: post SAXS
start time:   
proposal_id('2023_1', '308052B_YZhang')

Energy: 16.1 keV, 0.77009 A, low divergence

setthreshold energy 16100 autog 11000

setthreshold energy 2450 uhighg 1600

# SAXS distance , 5 meter
# 1M [  -4.09, -61.4, 5000  ]
# beam stop [ 2.2, 288.99,  13  ], a rod
# beam center   [  460,  557    ]
# beamstop_save()

Samples

# for bar gisaxs samples, Y 4700, Z, 6000, 


RE( shopen() )
RE( shclose() )



In [210]: RE(mv(ivugap, 6227))
Out[210]: ()                                                                                                                                  

In [211]: energy.move(16100)
Out[211]: MoveStatus(done=True, pos=energy, elapsed=1.0, success=True, settle_time=0.0)

In [212]: 






WAXS 
# put att  14-18keV, Sn 60 um, 7X, move beamstop  -10
# for waxs=0 --> find the beam center is [220, 308] on albula
# for waxs=1 --> find the beam center is [220, 280] on albula
# for waxs=2 --> find the beam center is [220, 252] on albula
# for waxs=3 --> find the beam center is [220, 223] on albula
# for waxs=4 --> find the beam center is [218, 194] on albula, part block by chip
# for waxs=5 --> find the beam center is [218, 166] on albula
# for waxs=6 --> find the beam center is [218, 138] on albula
# for waxs=7 --> find the beam center is [218, 110] on albula
# for waxs=8 --> find the beam center is [218, 81] on albula
# for waxs=9 --> find the beam center is [218, 53] on albula
# for waxs=10 --> find the beam center is [218, 25] on albula
# for waxs=11 --> find the beam center touch the edge
# for waxs=12 --> find the beam center is out of the detector


user_name
sample_name

"""

# def shopen():
#     yield from bps.mv(ph_shutter.open_cmd, 1)
#     yield from bps.sleep(1)
#     # Disabled because of problems with XBPM3 in microfocus    
#     yield from bps.mv(manual_PID_disable_pitch, "0")
#     yield from bps.mv(manual_PID_disable_roll, "0")


# def shopen():
#     yield from bps.mv(ph_shutter.open_cmd, 1)
#     yield from bps.sleep(1)



from epics import caget, caput
from datetime import datetime
import numpy as np

######################################
'''user example

user_name = "YZhang"
proposal_id('2023_1', '308052B_YZhang')

# for test 
dx, dy = 0, 0

#sample_dict = {k: 'S_%03d'%k for k in range(1,16) }
sample_dict = {  1: 'S_O360', }

ks = np.array(list((sample_dict.keys())))
pxy_dict = {  1:  ( -3800 , 800     )       }
#pxy_dict = {k: [pxy_dict[k][0] + dx, pxy_dict[k][1] + dy] for k in ks}

x_list = np.array(list((pxy_dict.values())))[:, 0]
y_list = np.array(list((pxy_dict.values())))[:, 1]
sample_list = np.array(list((sample_dict.values())))



mov_sam_re  #need to find the code
'''



############################################################################
# Define samle information
############################################################################
#sample_id
# user_name = 'test'
# sample_name = 'test'
# #sample_dict = {k: 'S_%03d'%k for k in range(1,16) }
# sample_dict = {  1: 'S_O360', }
# ks = np.array(list((sample_dict.keys())))
# pxy_dict = {  1:  ( -3800 , 800     )       }
# #pxy_dict = {k: [pxy_dict[k][0] + dx, pxy_dict[k][1] + dy] for k in ks}
# x_list = np.array(list((pxy_dict.values())))[:, 0]
# y_list = np.array(list((pxy_dict.values())))[:, 1]
# sample_list = np.array(list((sample_dict.values())))





###########################################
## Setup the motor
###
motor = 'pizeo'  #'stage'
#motor = 'stage'
user_name = ''
user_name = 'YZ'
###########################################




# ###################################################################
# #Setup path, deal with OVA and stage camera 
# ###################################################################
# def proposal_id(cycle_id, proposal_id, analysis=True, camera=True, hexcam = True  ):
#     RE.md["cycle"] = cycle_id
#     RE.md["proposal_number"] = proposal_id.split("_")[0]
#     RE.md["main_proposer"] = proposal_id.split("_")[1]
#     # RE.md['path'] = "/nsls2/xf12id2/data/images/users/" + str(cycle_id) + "/" + str(proposal_id)

#     RE.md["path"] = ("/nsls2/data/smi/legacy/results/data/" + str(cycle_id) + "/" + str(proposal_id))
#     newDir = ("/nsls2/data/smi/legacy/results/data/"+ str(cycle_id)+ "/"+ str(proposal_id)) + "/1M"
#     if not os.path.exists(newDir):
#         os.makedirs(newDir)
#         os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

#     newDir = ("/nsls2/data/smi/legacy/results/data/"+ str(cycle_id)+ "/"+ str(proposal_id)) + "/900KW"
#     if not os.path.exists(newDir):
#         os.makedirs(newDir)
#         os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

#     # Create folder for the analysis
#     if analysis:
#         #newDir = ("/nsls2/data/smi/legacy/results/analysis/"+ str(cycle_id)+ "/"+ str(proposal_id))
#         newDir = ("/nsls2/data/smi/legacy/results/data/"+ str(cycle_id)+ "/"+ str(proposal_id)) + "/Results"
#         if not os.path.exists(newDir):
#             os.makedirs(newDir)
#             os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)

#     if camera:
#         newDir = ("/nsls2/data/smi/legacy/results/data/"+ str(cycle_id)+ "/"+ str(proposal_id)) + "/OAV"
#         if not os.path.exists(newDir):
#             os.makedirs(newDir)
#             os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
#         caput('XF:12IDC-BI{Cam:SAM}JPEG1:EnableCallbacks', 1)     
#         caput( 'XF:12IDC-BI{Cam:SAM}JPEG1:FilePath', newDir ) 
#         print( 'Will save OAV data in :%s.' %newDir )

#     if hexcam:
#         newDir = ("/nsls2/data/smi/legacy/results/data/"+ str(cycle_id)+ "/"+ str(proposal_id)) + "/HEX"
#         if not os.path.exists(newDir):
#             os.makedirs(newDir)
#             os.chmod(newDir, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
#         #caput('XF:12IDC-BI{Cam:HEX}JPEG1:EnableCallbacks', 1)     
#         #caput( 'XF:12IDC-BI{Cam:HEX}JPEG1:FilePath', newDir )  
#         caput('XF:12IDC-BI{Cam:HEX}TIFF1:EnableCallbacks', 1)     
#         caput( 'XF:12IDC-BI{Cam:HEX}TIFF1:FilePath', newDir )  
#         print( 'Will save hexcam data in :%s.' %newDir )

def save_ova(  sample = 'test' ,   setup= False): 
    caput( 'XF:12IDC-BI{Cam:SAM}JPEG1:FileName', sample  )   
    caput( 'XF:12IDC-BI{Cam:SAM}JPEG1:WriteFile', 1 )  
    print('save ova png file: %s here..'%sample)

def save_hex(  sample = 'test' ,  setup= False  ):     
    #caput( 'XF:12IDC-BI{Cam:HEX}JPEG1:FileName', sample  )   
    #caput( 'XF:12IDC-BI{Cam:HEX}JPEG1:WriteFile', 1 )  
    #print('save hex png file: %s here..'%sample)
    format = 'TIFF' #'JPEG'
    fp = 'XF:12IDC-BI{Cam:HEX}%s1:FileName'%format
    #print(fp)
    caput( fp, sample  )   
    caput( 'XF:12IDC-BI{Cam:HEX}%s1:WriteFile'%format, 1 )  

 
def setup_ova(   ):
    caput('XF:12IDC-BI{Cam:SAM}JPEG1:EnableCallbacks', 1)
    #path= '/nsls2/data/smi/legacy/results/data/2024_3/313650_FLuA/OAV/'
    #path= '/nsls2/data/smi/legacy/results/data/2024_1/313760_FLu/OAV/'
    path= '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/OAV/'
    caput( 'XF:12IDC-BI{Cam:SAM}JPEG1:FilePath', path ) 
    print('the OVA path is: %s'%path )
     
def setup_hex(   ):
    format = 'TIFF'
    #format = 'JPEG'
    caput('XF:12IDC-BI{Cam:HEX}%s1:EnableCallbacks'%format, 1)
    path= '/nsls2/data/smi/legacy/results/data/2024_1/313760_FLu/HEX/'
    caput( 'XF:12IDC-BI{Cam:HEX}%s1:FilePath'%format, path ) 


     

 


###################################################################
#End of Setup path, deal with OVA and stage camera 
###################################################################





##################################################
# for Fang's in-situ measurement
# move pil1M x to -4 mm, create sample_dict, three samples for examples
# align, using  
###   Aligned_Dict = RE(  align_gix_loop_samples(inc_ang = 0.15, motor='stage') ) 
# 


#%s%s_%6.6d_SAXS.tif
#%6.6d_SAXS.tif
#/ramdisk/1M/acq_000379_SAXS.tif



help_dict = { 'align': 
             [ "Align GI samples:   RE(  align_gix_loop_samples(inc_ang = 0.15 ) )    ",
              "loop samples using x_list, sample_list and moter pizeo or stage (hexpod), return a dict, Aligned_Dict { 0: {'th': th, 'y': y } } "  
              ],

              'measure':
              [  'measure_one_gix', 
               
               ],
              'move':
              [],
              'scan':
              [  "example1: rel_scan cslit height, using pil1M --> RE(bp.rel_scan([pil1M],cslit.h,-0.3,0.3,21)) " ,
                 "example2: scan waxs.waxs_arc, using dets -->   yield from bp.scan(dets, waxs, *waxs_arc) ) ",  
                  "example3: nscan, dets, traj, -->   bp.scan_nd(all_detectors, trajectory, md=base_md)",


               ],

}


# RE(bp.rel_scan([pil1M], stage.y, -1,1,11))

############################################################################
#Grzaing Incidence
############################################
def get_motor(  ):
    M = piezo
    if motor != 'pizeo':    
        M = stage    
    TH = M.th.position 
    YH = M.y.position 
    return M, TH, YH

 


def measure_one_gix( t=1,  mode = ['saxs'], waxs_angle=15, incident_angle=[0.1],  
                    user_name = None, sample=None, align=False, inc_ang = 0.15   ): 
    '''     RE( measure_one_gisaxs() )      '''    
    if user_name is None:        
        user_name = RE.md["user_name"]         
    if sample is None:        
        sample = RE.md["sample_name"]  
    sample0 = sample   

    if align:
        if motor == 'pizeo':
            yield from alignement_gisaxs(inc_ang ) #run alignment routine  
        else:
            yield from alignement_hex(inc_ang ) #run alignment routine               
    M, TH, YH = get_motor(   )  
    print( YH, TH)  
    dets = []
    if 'saxs' in mode:
        dets.append( pil1M )
    if 'waxs' in mode:
        yield from bps.mv(waxs, waxs_angle)
        dets.append( pil900KW ) 
    angle_arc = np.array( incident_angle  )
    th_meas = angle_arc + TH
    th_real = angle_arc	 
    det_exposure_time(t,t) 
    for i, th in enumerate(th_meas): #loop over incident angles
        yield from bps.mv(M.th, th)  
        name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
        sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,saxs_z=np.round(pil1m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,
                )  
        sample_id(user_name=  user_name , sample_name=sample_name)                     
        print(f'\n\t=== Sample: {sample_name} ===\n')  
        yield from bp.count( dets, num=1)  #measure SAXS     
    yield from  bps.mv(M.th, TH  )  
    RE.md['sample_name'] = sample0
    RE.md['sample'] = sample0  


    
def measure_one_gisaxs( t=1, incident_angle=[0.1],  user_name = None, sample=None, align=False  ): 
    '''     RE( measure_one_gisaxs() )      '''
    measure_one_gix( t=1, mode = ['saxs'], incident_angle=incident_angle,  user_name = user_name,  sample=sample )
    
def measure_one_giwaxs( t=1,   incident_angle=[0.1], waxs_angle=20,  user_name = None, sample=None, align=False  ): 
    '''     RE( measure_one_gisaxs() )      '''
    measure_one_gix( t=1,  mode = ['waxs'], waxs_angle= waxs_angle, incident_angle=incident_angle, 
     user_name = user_name, sample=sample )
    
def measure_one_giwsaxs( t=1, incident_angle=[0.1],  user_name = None, sample=None, align=False  ): 
    '''     RE( measure_one_gisaxs() )      '''
    measure_one_gix( t=1,  mode = ['saxs', 'waxs'], waxs_angle= waxs_angle,  incident_angle=incident_angle, 
     user_name = user_name,  sample=sample )
    
def get_dets( waxs_angle = 15, mode = ['saxs', 'waxs' ] ):
    dets  = []
    if 'waxs' in mode:
        dets.append( pil900KW )
    if 'saxs' in mode:
        if waxs_angle >10:    
            dets.append( pil1M )
    return dets 
           

def run_gix_loop_waxs(t=1, mode = ['saxs', 'waxs' ],  
                       angle_arc = np.array([0.05, 0.08, 0.10, 0.15, 0.2, 0.3 ]),
                       waxs_angle_array = np.array( [ 0,  20, 40   ] ) ,  
                       x_shift_array = np.linspace(-2500, 2500, 3),                      
                       Aligned_Dict = None ):           
    '''      
      RE(  align_gix_loop_samples(inc_ang = 0.15 ) )
     '''    

    assert len(x_list) == len(sample_list), f'Sample name/position list is borked' 
    if Aligned_Dict is None:    
        Aligned_Dict = align_gix_loop_samples( inc_ang = 0.15 )  
    print( Aligned_Dict )  
    M, _, _ = get_motor(   )  
    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     
        dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
        det_exposure_time(t,t)                  
        for ii, (x, sample) in enumerate(zip(x_list,sample_list)):    #loop over samples on bar
            yield from bps.mv(piezo.x, x) #move to next sample              
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
                    sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,saxs_z=np.round(pil1m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,
                    #scan_id=RE.md["scan_id"],
                )
                    sample_id(user_name=  user_name , sample_name=sample_name)                     
                    print(f'\n\t=== Sample: {sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
                    det_exposure_time(t,t)    
                    RE.md['sample_name'] = sample
                    RE.md['sample'] = sample 
                        
            #print( 'HERE#############')
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)


 

def run_gix_loop_samples(t=1,  angle_arc = np.array([0.05, 0.08, 0.10, 0.15, 0.2, 0.3 ]),                        
                       x_shift_array = np.linspace(-2500, 2500, 3),                      
                       Aligned_Dict = None,  mode = ['saxs', 'waxs' ], 
                       waxs_angle_array = np.array( [ 0,  20, 40   ] ) , 
                         ):      
    '''      

      Aligned_Dict = RE(  RE( align_gix_loop_samples( inc_ang = 0.15  )        )   )  
      RE( run_gis_loop_angles() )  


     '''
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked' 
    if Aligned_Dict is None:    
        Aligned_Dict = align_gix_loop_samples( inc_ang = 0.15 )  
    print( Aligned_Dict ) 
    M, _, _ = get_motor(   )       
    #det_exposure_time(t,t)         
    #dets = get_dets( waxs_angle = waxs_angle, mode = mode )           
    for ii, (x, sample) in enumerate(zip(x_list,sample_list)):    #loop over samples on bar
        yield from bps.mv(M.x, x) #move to next sample              
        TH = Aligned_Dict[ii]['th']  
        YH = Aligned_Dict[ii]['y']  
        yield from bps.mv(M.y, YH)  
        yield from bps.mv(M.th, TH)      
        for waxs_angle in waxs_angle_array: # loop through waxs angles        
            yield from bps.mv(waxs, waxs_angle)     
            dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
            det_exposure_time(t,t)

            th_meas = angle_arc + TH #piezo.th.position 
            th_real = angle_arc	         
            x_pos_array = x + x_shift_array    
            for j, x_meas in enumerate( x_pos_array) : # measure at a few x positions
                yield from bps.mv(M.x, x_meas)                 
                for i, th in enumerate(th_meas): #loop over incident angles
                    yield from bps.mv(M.th, th)  
                    name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
                    sample_name = name_fmt.format(sample=sample,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,saxs_z=np.round(pil1m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,
                    #scan_id=RE.md["scan_id"],
                )
                    sample_id(user_name=  user_name , sample_name=sample_name)                     
                    print(f'\n\t=== Sample: {sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
                    det_exposure_time(t,t)  
                    RE.md['sample_name'] = sample
                    RE.md['sample'] = sample 
            #yield from  bps.mv(piezo.y, YH  )  
            #yield from  bps.mv(piezo.th, TH  )   
            #print( 'HERE#############')
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)

                       
                       


def do_line_trans_scan( sample = 'FF_AuCB', username = 'FLu'  ,   t=1,  scan_range = [ -1000,  1000 ], 
                 scan_step  = 30,  method='V',  take_camera=True, waxs_angle=15,    ):
    
    ''''
 
    RE(   do_line_trans_scan(    )     )
    
    
    '''

    YH = piezo.y.position 
    XH = piezo.x.position 
    #TH = piezo.th.position 
    if waxs_angle > 10:
        dets = [ pil900KW,  pil1M ] #
    else:
        dets = [ pil900KW  ] #
    yield from bps.mv(waxs, waxs_angle)  
    if method == 'V':
        vals =  np.arange( scan_range[0], scan_range[-1]+scan_step, scan_step  ) + YH     
    elif method == 'H':
        vals =  np.arange( scan_range[0], scan_range[-1]+scan_step, scan_step  ) + XH   
    det_exposure_time(t,t) 
    for v in vals:
        if method == 'V':
            yield from bps.mv(piezo.y, v)                  
        elif method == 'H':      
                yield from bps.mv(piezo.x, v)  
        name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
        sample_name = name_fmt.format(
        sample=sample,
        x=np.round(piezo.x.position, 2),
        y=np.round(piezo.y.position, 2),
        z_pos=piezo.z.position,
        saxs_z=np.round(pil1m_pos.z.position, 2),
        waxs_angle=waxs_angle,
        t=t,
        #scan_id=RE.md["scan_id"],
    )
        sample_id(user_name=  username , sample_name=sample_name)                     
        print(f'\n\t=== Sample: {sample_name} ===\n')  
        yield from bp.count( dets, num=1)  
        #yield from bps.sleep(1)       
        if take_camera:
            save_ova( sample=sample_name,   )    
        RE.md['sample_name'] = sample
        RE.md['sample'] = sample        
    #yield from bps.mv(piezo.x, XH)   
    #yield from bps.mv(piezo.y, YH )  
 

       






def do_gix_line_scan( sample ='test',  t=1,  scan_range = [ -100, 100], scan_step  = 50,  method='V',  camera=True,  
 user_name = user_name,  ):
    ##tobecheck                      
                          
    
    ''''
    RE(   do_line_scan(    )     )
    
    
    '''

    YH = piezo.y.position 
    XH = piezo.x.position 
    #waxs_angle_array = np.array( [ 0,  20, 40  ] ) 
    waxs_angle_array = np.array( [ 0, 20, 40  ] ) 
    max_waxs_angle = np.max(  waxs_angle_array )  
    if method == 'V':
        vals =  np.arange( scan_range[0], scan_range[-1]+scan_step, scan_step  ) + YH     
    elif method == 'H':
        vals =  np.arange( scan_range[0], scan_range[-1]+scan_step, scan_step  ) + XH     

    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)            
        if waxs_angle == max_waxs_angle:
            dets = [ pil900KW,  pil1M ] # waxs, maxs, saxs = [pil300KW, rayonix, pil1M] 
        #     print( 'Meausre both saxs and waxs here for w-angle=%s'%waxs_angle )
        else:
                dets = [pil900KW ] 
        det_exposure_time(t,t) 
        for v in vals:
            if method == 'V':
                yield from bps.mv(piezo.y, v)                  
            elif method == 'H':      
                 yield from bps.mv(piezo.x, v)  

            name_fmt = '{sample}_x{x:05.2f}_y{y:05.2f}_expt{t}s' 
            sample_name = name_fmt.format( sample = sample, x= piezo.x.position ,  y= piezo.y.position , t=t )  
            sample_id(user_name=  user_name , sample_name=sample_name)                     
            print(f'\n\t=== Sample: {sample_name} ===\n')  
            # if camera:
            #     #path= '/nsls2/xf12id2/data/images/users/2022_3/308052_YZhang/OAV/'
            #     #caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FilePath', path ) 
            #     caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FileName', sample_name  )
            #     caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:WriteFile', 1 )         
            yield from bp.count( dets, num=1)   
            RE.md['sample_name'] = sample
            RE.md['sample'] = sample                     
    yield from bps.mv(piezo.x, XH)        
    yield from bps.mv(piezo.y, YH )        


    
    
############################################################################
#Transimission  

def measure_transmission_xs(t=1, mode = ['saxs'], waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False):
    """RE( measure_transmission_xs( sample = 'test' ) )"""
    
    if user_name is None:        
        user_name = RE.md["user_name"]         
    if sample is None:        
        sample = RE.md["sample_name"]   
    sample0 = sample  
    if dy:
        yield from bps.mvr(piezo.y, dy)
    if dx:
        yield from bps.mvr(piezo.x, dx)
    dets = []
    if 'saxs' in mode:
        dets.append( pil1M )
    #print( 'xxx'  )  
    if 'waxs' in mode:
        yield from bps.mv(waxs, waxs_angle)
        dets.append( pil900KW )   
    #if '300kw' in mode:        
    #    dets.append( pil300KW )     ???  
    #maybe add sid  
    name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
    sample_name = name_fmt.format(
        sample=sample,
        x=np.round(piezo.x.position, 2),
        y=np.round(piezo.y.position, 2),
        z_pos=piezo.z.position,
        saxs_z=np.round(pil1m_pos.z.position, 2),
        waxs_angle=waxs_angle,
        t=t,
        #scan_id=RE.md["scan_id"],
    )
    det_exposure_time(t, t) 
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    if take_camera:
        save_ova( sample=sample_name,   )
    #sample_id(user_name="test", sample_name="test")  
    # if take_camera:  #need check
    #     #path= '/nsls2/xf12id2/data/images/users/2022_3/308052_YZhang/OAV/'
    #     #caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FilePath', path ) 
    #     caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FileName', sample_name  )
    #     caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:WriteFile', 1 )       
    RE.md['sample_name'] = sample0
    RE.md['sample'] = sample0

            

def measure_saxs(t=1, att="None", dx=0, dy=0, user_name=user_name, sample=None, take_camera = False):
    """RE( measure_saxs( sample = 'AgBH_12keV' ) )"""    
    return measure_transmission_xs(t=t, mode = ['saxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample, take_camera = take_camera)   

def measure_waxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_waxs() )  # take default parameters
    """
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['waxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera) 

def measure_wsaxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_wsaxs() )  # take default parameters
    """
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['saxs', 'waxs' ], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera)     
    
    
def snap_waxs(t=0.1):
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="")
    det_exposure_time(t,t )
    yield from bp.count(dets, num=1)
    
def snap_saxs(t=0.1):
    'test '
    dets = [pil1M]
    sample_id(user_name="test", sample_name="")
    det_exposure_time(t,t )
    yield from bp.count(dets, num=1)

    #/ramdisk/900KW
    
############################################################################
# for Map

def getSamMap(  xlim=[4500, 8500], ylim=[-4390, 610 ],  step_size = [100, 100], rot_angle = 0 ):
    #change x Y position here
    Ps_grid = []
    px = np.arange( xlim[0],xlim[1]+step_size[0]*0, step_size[0])
    py = np.arange( ylim[0],ylim[1]+step_size[1]*0, step_size[1])
    rot_angle = np.deg2rad(rot_angle)
    delta_x = np.cos(rot_angle)
    delta_y = np.sin(rot_angle)
    rot_matrix = np.array(((delta_x, -delta_y),(delta_y, delta_x)))
    for y in   py:
        for x in   px:
            Ps_grid.append(  [ x,y ]   )
    Ps_grid = np.array(Ps_grid)
    Ps_grid_rot = np.dot(rot_matrix,Ps_grid.T).T 
    return Ps_grid_rot




def Measure_Map_Trans(  t = 1, mode=['saxs', 'waxs'], user_name=None, sample=None, take_camera = False , ps=None, pz= 8000, waxs_angle=20,   ):  
    '''
    Ps = getSamMap()
    Measure_Map( sample = 'test',  ps= Ps[:2]   )     
    '''
    RE(bps.mov( piezo.z, pz  ))
    if ps is None:
        ps = getSamMap( )
    for (px,py) in ps:
        print( px, py )
        RE(bps.mov( piezo.x, px  ))
        RE(bps.mov( piezo.y, py  ))
        measure_wsaxs( t=t, waxs_angle=waxs_angle, att="None", dx=0, dy=0, user_name= user_name, sample=sample, take_camera = take_camera) 


def measure_saxs_loop_sample(t=[1],dxs=[0], dys=[0],   take_camera = False ):
    """t0=time.time();RE(measure_series_saxs_PNNL());run_time(t0)"""
    ks = list(sample_dict.keys())  # [:8 ] 
    for k in ks:
        print(k)
        yield from mov_sam_re(k)  #mov_sam_re
        for dx in dxs:
            print(dx)
            for dy in dys:
                print(dy)
                print("here we go ... ")
                for ti in t:
                    yield from measure_saxs( t=ti,  att="None", dx=dx, dy=dy, take_camera = take_camera  )                    
 
        
def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0,  20, 40, 60  ], dxs=[0], dys=[0], saxs_on=True ):
    """    
    t0=time.time();RE(measure_series_multi_angle_wsaxs());run_time(t0)    

    """
    ks = list(sample_dict.keys())   
    maxA = np.max(waxs_angles)
    for waxs_angle in waxs_angles:
        for k in ks:
            print(k)
            yield from mov_sam_re(k)  #mov_sam_re
            for dx in dxs:
                print(dx)
                for dy in dys:
                    print(dy)
                    print("here we go ... ")
                    for ti in t:
                        RE.md["sample_name"] = sample_dict[k]   
                        both = False
                        if saxs_on:    
                            if waxs_angle == maxA: 
                                both = True
                        if both:        
                            yield from measure_wsaxs( t=ti, waxs_angle=waxs_angle, att="None", dx=dx, dy=dy, take_camera = take_camera  )
                        else:
                            yield from measure_waxs( t=ti, waxs_angle=waxs_angle, att="None", dx=dx, dy=dy, take_camera = take_camera  )

                       
            
            
############################################################################


    
############################################################################
#some convient functions
############################################################################
from datetime import datetime
def get_current_time():
    from datetime import datetime
    '''get current time in year, month, date, hour, min, sec'''
    return datetime.today().strftime("%Y-%m-%d-%H-%M-%S")

def run_time(t0):
    dt = (time.time() - t0) / 60
    print("The Running time is: %.2f min." % dt) 

flatten_nestlist = lambda l: [item for sublist in l for item in sublist]
def sort_dict_by_value( dicts ):
    '''Y.G., Dev@CFN Jan 14, 2020 sort dictionary by  value
     
    Parameters
    ----------
        dicts: dictionary
 
    Returns
    -------  
        sorted dict
    '''         
    return   {k:v for (k,v) in sorted( dicts.items(), key =  lambda kv:(kv[1], kv[0])) }


############################################################################
#End of some convient functions
############################################################################







############################################################################
#SMI lakeshore
############################################################################
def setT(T):
    T_kelvin = T + 273.15
    yield from ls.output1.mv_temp(T_kelvin)
    # RE( ls.output1.mv_temp(T_kelvin)    )
    print("Set temperature to %.2f oC." % T)
def getT():
    temp_degC = ls.input_A.get() - 273.15
    print("The current temperature is %.2f oC." % temp_degC)
    return temp_degC
def startT():
    """
    Try using range 3 in channel 1
    """
    yield from bps.mv(ls.output1.status, 3)
    print("Start heating up using output1 using range3.")
def stopT():
    yield from ls.output1.turn_off()
    # RE( ls.output1.turn_off()    )
    print("Stop heating up using output1.")
def gotoT(T, tolerance = 0.2 ):
    yield from setT(T)
    yield from startT()
    temp = getT()
    while abs(temp - T) > tolerance:
        print('The difference between the set and readback temperature is: %.2f'%abs(temp - T))
        yield from bps.sleep(10)
        temp = getT()
############################################################################
#Motions
############################################################################
def movx( dx  ):
    '''    move piezo motor a relative dx (um) in x direction    '''
    M, _, _ = get_motor( )   
    RE(  bps.mvr(M.x, dx) )  

def movy( dy  ):
    '''    move piezo motor a relative dy (um) in y direction    ''' 
    M, _, _ = get_motor( )     
    RE( bps.mvr(M.y, dy) )
    
def get_posxy(  ):
    '''    get piezo motor absolution postion    '''     
    M, _, _ = get_motor( )  
    return  round( M.x.user_readback.value, 2 ),round( M.y.user_readback.value , 2 )

def mov_xy( xy   ):
    '''    move piezo motor a relative dx (um) in x direction    '''
    M, _, _ = get_motor( )   
    x,y = xy 
    RE(  bps.mv(M.x, x) )  
    RE( bps.mv(M.y, y) )

# def mov_sam_dict( pos, motor='pizeo' ):   
#     '''    move sam position   '''   
#     M = piezo
#     if motor != 'pizeo':
#         M = stage          
#     px,py = pxy_dict[ pos ]
#     RE(  bps.mv(M.x, px) )
#     RE(  bps.mv(M.y, py) )
#     sample = sample_dict[pos]  
#     print('Move to pos=%s for sample:%s...'%(pos, sample ))
#     RE.md['sample_name']  = sample 
       
def mov_sam(pos, dx=0, dy=0  ):
    M, _, _ = get_motor( )   
    px, py = pxy_dict[pos]
    RE(bps.mv(M.x, px + dx))
    RE(bps.mv(M.y, py + dy))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))   
    RE.md["sample_name"] = sample
    RE.md["sample"] = sample


def mov_sam_re(pos, dx =0, dy=0   ):
    M, _, _ = get_motor( )  
    px, py = pxy_dict[pos]
    yield from bps.mv(piezo.x, px + dx)
    yield from bps.mv(piezo.y, py + dy)
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))     
    RE.md["sample_name"] = sample 
    RE.md["sample"] = sample 

    
def name_sam(pos):
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))     
    RE.md["sample_name"] = sample    
    RE.md["sample"] = sample    
    



def move_waxs( waxs_angle=10.0):
    '''    move waxs detector with beamstop to waxs_angle in degree   '''        
    RE(  bps.mv(waxs, waxs_angle)    )
       
def move_waxs_off( waxs_angle=15.0 ):
    '''    move waxs detector with beamstop to waxs_angle in degree   '''    
    RE(  bps.mv(waxs, waxs_angle)    )
def move_waxs_on( waxs_angle=0.0 ):
    '''    move waxs detector with beamstop to waxs_angle in degree   '''     
    RE(  bps.mv(waxs, waxs_angle)  )

def measure_pindiol_current():
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr
########################################################################         

########################################################################   
#Grzaing incidence X-ray scattering





# def align_gix_samples( inc_ang = 0.1 ):      
#     '''      
#       Aligned_Dict =     align_gix_linkam()   
#      '''
#     # define names of samples on sample bar         
#     Aligned_Dict = {}
#     sample = sample_list[0] 
#     print('Do alignment for sample: %s'%sample )
#     RE(  alignement_gisaxs_hex(inc_ang ) ) #run alignment routine
#     #RE(  alignement_gisaxs(inc_ang ) ) #run alignment routine
#     #yield from alignement_gisaxs_hex(inc_ang )
#     TH = stage.th.position 
#     YH = stage.y.position 
#     Aligned_Dict['th']  = TH
#     Aligned_Dict['y']  = YH
#     print(  TH, YH )
#     return Aligned_Dict




def align_gix_loop_samples( x_list, sample_list, inc_ang = 0.15,   ):      
    '''      

      RE( align_gix_loop_samples( inc_ang = 0.15  )        )  



     '''
    # define names of samples on sample bar     
    M, _, _ = get_motor(  ) 
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'  
    print('here')   
    Aligned_Dict = {}
    for ii, (x, sample) in enumerate(zip(x_list,sample_list)):    #loop over samples on bar
        print('Do alignment for sample: %s'%sample )
        yield from bps.mv(M.x, x) #move to next sample  
        if motor == 'pizeo':             
            yield from alignement_gisaxs(inc_ang  ) #run alignment routine          
        else:             
            yield from alignement_gisaxs_hex(inc_ang  ) #run alignment routine  
        M, TH, YH = get_motor(  )     
        Aligned_Dict[ii]={}
        Aligned_Dict[ii]['th']  = TH
        Aligned_Dict[ii]['y']  = YH
        print( ii, TH, YH )
    return Aligned_Dict



#Grzaing incidence X-ray scattering
## From 37-Alignement
import datetime 
smi = SMI_Beamline()#
def alignement_gisaxs(angle=0.15):        
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.3, 0.3)        
    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique='gisaxs')        
    # Set direct beam ROI
    yield from smi.setDirectBeamROI()
    # Scan theta and height
    yield from align_gisaxs_height(500, 21, der=True)
    yield from align_gisaxs_th(1.5, 27)
    #yield from align_gisaxs_height(300, 11, der=True)
    #yield from align_gisaxs_th(0.5, 16)        
    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)
    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique='gisaxs')        
    # Scan theta and height
    yield from align_gisaxs_th(0.2, 31)
    yield from align_gisaxs_height(150, 21)
    yield from align_gisaxs_th(0.025, 21)        
    # Close all the matplotlib windows
    plt.close('all')        
    # Return angle
    yield from bps.mv(piezo.th, ps.cen - angle)
    yield from smi.modeMeasurement()



def alignement_gisaxs_hex(angle=0.1, rough_y=0.5):
    """
    Regular alignement routine for gisaxs and giwaxs using the hexapod. First, scan of the sample height
    and incident angle on the direct beam.
    Then scan of teh incident angle, height and incident angle again on the reflected beam.

    Params:
            angle (float): angle at which the alignement on the reflected beam will be done,
            rough_y (float): range in hexapod stage y for rough alignment.

    """

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)
    smi = SMI_Beamline()
    yield from smi.modeAlignment()
    # Set direct beam ROI
    yield from smi.setDirectBeamROI()
    # Scan theta and height
    yield from align_gisaxs_height_hex(rough_y, 21, der=True)
    yield from smi.setReflectedBeamROI(total_angle=0.06, technique="gisaxs")
    yield from align_gisaxs_th_hex(0.5, 21)
    # move to theta 0 + value
    yield from bps.mv(stage.th, ps.peak + angle)
    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
    # Scan theta and height
    yield from align_gisaxs_th_hex(0.3, 31)
    yield from align_gisaxs_height_hex(0.1, 21)
    yield from align_gisaxs_th_hex(0.05, 21)
    # Close all the matplotlib windows
    plt.close("all")
    # Return angle
    yield from bps.mv(stage.th, ps.cen - angle)
    yield from smi.modeMeasurement()
    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def align_gix():
    yield from alignement_gisaxs(0.15)  # run alignment routine
############################################################################






































# The END
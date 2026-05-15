'''
saf=
proposal: 318527



20251109
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air


%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_Tomo.py
proposal_swap(318527)
project_set('Tomo')


sample_id(user_name='test', sample_name=f'hscan_{get_scan_md()}')
RE(bp.rel_scan([pil2M,pin_diode],piezo.x,-1000,1000,51))




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







'''

'''
NOTE: 

For calibration holder
M-Drive 5: X,  3: Z,   # set Z limit as 120 
AgBH: [ 68, 101  ]
YAG: [  52, 101  ]

for reactor, 
M-Drive 5: X,  3: Z, 
[41, 74 ] # set Z limit as 80 


data path:
/nsls2/users/yuzhang/smi_proposals_link/2025-3/pass-318919/assets/pilatus2m-1/2025/11/10
AgBH 
RE(measure_saxs( 1 ))
ff2214d5-b7b0-40da-83ad_000000.tiff



some scatering from the pindiode, need to move the saxs pindiode Y a bit up and down to find the best postion

beamstop_save()




Data Folder:
/nsls2/data/smi/proposals/2026-1/pass-318527/projects/static/user_data/2M


 
'''

 
'''
2026/3/25, Microfocusing, 16.1, 23 * 3 um
Data Folder:
/nsls2/data/smi/proposals/2026-1/pass-318527/projects/Tomo
change to pindiode 
RE(pil2M.insert_beamstop('pd'))
change to rod
RE(pil2M.insert_beamstop('rod'))


9 Meter
change from 9 meter to 5 meter

SAXS det, X, Y  are [0,0] --> 2M
#beam center: [749, 574 ]
saxs rod X --> change from 6.8  to 7.3

How to align the sample
1) put the pin (sample) in the middle of the bar
2) load bar to the piezo stage
3) move px to around 0, and y around 0, z round -9000
3.5) draw a vline as Ref 
4) change the PRS angle from 0 to 90, change pz to the half way
5) change 90 to 0, change px to the half way
6) change 0 to -90, change pz to the half way
7) Repeat several time, in the last few runs, make px and pz step as 2 micrometer
8) until no move of the sample when change PRS from -90 to 90



change from microfocusing to low div
beam center is 
[ 755, 567 ]
beamstop [ 6.55, 288 ]



for j in range( 10 ):    
    for i in range(10):
        RE(measure_saxs( t=1, sample = '240_S',  user_name = 'CL'))
        
    movx( -2600 )
    movy( 260  )

N = 30    
for j in range( N ):  
        RE(measure_waxs( t=1, sample = 'S1', waxs_angle=0,  user_name = 'CWang'))
        RE( bps.movr( stage.y, 0.003  ) )
    RE( bps.movr( stage.y, -0.003 * N   ) )
 
    

20260325 NGT   

RE(run_tomo( -90, 91, 181, sample='FL_S3Cube_2025Q3_LargeBeam' ))
found the beam center is not good, then change to a new center

project_set('Tomo_NewCen')
Sample 1: FL_S3Cube_2025Q3
mov det Y to 10
still 5 meter, 16.1 kev, low divergency
beam center is 
[ 757, 508 ]
beamstop [ 6.55, 288 ]
Sampe with angle PRS @89.3  is good

RE(run_tomo( 91-5, 91+6, 50, sample='FL_S3Cube_2025Q3_LargeBeamNC_Fine' ))
RE(run_tomo( 89.3-2, 89.3+2, 40, sample='FL_S3Cube_2025Q3_LargeBeamNC_Fine2' ))   
RE(run_tomo( 89.3-2-90, 89.3+2-90, 40, sample='FL_S3Cube_2025Q3_LargeBeamNC_Fine3' ))  


Second Sample:
RE(run_tomo( -90, 91, 181, sample='FL_S1NaCl_2026Q1_LargeBeam' ))
RE(run_tomo( -90, 91, 1801, sample='FL_S1NaCl_2026Q1_LargeBeam_Fine' ))



20260327 Friday, 12:40 PM
Third Sample:
RE(run_tomo( -90, 91, 1801, sample='FL_S2CsCl_2026Q1_LargeBeam_Fine' ))
RE(run_tomo( -90, 91, 181, sample='FL_S2CsCl_2026Q1_LargeBeam_Fine' ))


20260327 Friday, 4:30 PM
Fourth Sample:
RE(run_tomo( -90, 91, 181, sample='FL_S2TH_2025Q3_LargeBeam' )) --> not the sample, stop

RE(run_tomo( -90, 91, 181, sample='FL_S2TH_2025Q3_LargeBeamB' ))


20260327 Friday, 6:50 PM
Fifth Sample:
RE(run_tomo( -90, 91, 181, sample='FL_S1TH_2025Q3_LargeBeam' )) 

20260327 Friday, 8:05 PM
Sixth Sample:
RE(run_tomo( -90, 91, 181, sample='FL_S4TH_2025Q3_LargeBeam' )) 


'''

def yline_scan( step_size = 0.003 ):
    N = 10    
    for j in range( -N//2, N//2  ):  
        RE(measure_wsaxs( t=5, sample = 'FL_S3Cube_2025Q3_E', waxs_angle=15,  user_name = 'FL'))
        RE( bps.movr( stage.y, step_size  )  )
    #RE( bps.movr( stage.y, -step_size * N //2  ) )




username = 'CL'
user_name = 'CL' 
sample_dict =  {1: '240_S', 2: '240_S1_' }
ypos = 0
pxy_dict = {   1:  ( -28000, -6500  ) ,  2: (  2800, -5820 ),  }



username = 'DR'
user_name = 'DR' 
sample_dict =  {1: 'Blank1', 2: '5lank15' }
ypos = 0
pxy_dict = {   1:  ( -28000, -6500  ) ,  2: (  -29800, -5700 ),  }



username = 'FL'
user_name = 'FL' 
sample_dict =  {1: 'AgBH' }
ypos = 0
pxy_dict = {   1:  ( -41000 , 7000 )  }






# -29800, + 2600  (H)
# -8000 + 2600


# username = 'OG'
# user_name = 'OG'

# sample_dict =  {1: 'AgBH' }
# ypos = 0
# pxy_dict = {   1:  ( -47400+500, -1600 )  }


'''

Sample1: 
CWang's Sample


Sample2: 
FL_S3Cube_2025Q3_F

Sample 3:
FL_S1NaCl_2026Q1_LargeBeam_Fine

Sample 4:
FL_S2CsCl_2026Q1_LargeBeam




'''



pxy_dict = {  k: [ pxy_dict[k][0],  pxy_dict[k][1] + ypos ]  for k in pxy_dict }


 





motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3


def run_tomo(th_ini=-90, th_fin=90, th_st=30, exp_t=1, sample='test',
              nume=1, det=[pil2M,pil900KW] ) :
    det_exposure_time(exp_t, exp_t*nume)

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)
        name_fmt = "{sample}_5.0m_16.1keV_num{num}_{th}deg_bpm{bpm}"
        sample_name = name_fmt.format(sample=sample, num="%2.2d"%num, th="%2.2f"%theta, bpm="%1.3f"%xbpm3.sumX.get())
        sample_id(sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=1)



def mov_sam(pos, dx = 0, dy=0):
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px + dx ))
    RE(bps.mv(piezo.y, py + dy))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample
    RE.md["sample_name"] = sample


def mov_sam_re(pos, dx =0, dy=0   ):
    #M, _, _ = get_motor( )  
    px, py = pxy_dict[pos]
    yield from bps.mv(piezo.x, px + dx)
    yield from bps.mv(piezo.y , py + dy)
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))     
    RE.md["sample_name"] = sample 
    RE.md["sample"] = sample 



# def mov_sam(pos, dx=0, dy=0  ):
#     M, _, _ = get_motor( )   
#     px, py = pxy_dict[pos]
#     RE(bps.mv( motorX, px + dx))
#     RE(bps.mv( motorZ, py + dy))
#     sample = sample_dict[pos]
#     print("Move to pos=%s for sample:%s" % (pos, sample))   
#     RE.md["sample_name"] = sample
#     RE.md["sample"] = sample


# def mov_sam_re(pos, dx =0, dy=0   ):
#     #M, _, _ = get_motor( )  
#     px, py = pxy_dict[pos]
#     yield from bps.mv(motorX, px + dx)
#     yield from bps.mv(motorZ, py + dy)
#     sample = sample_dict[pos]
#     print("Move to pos=%s for sample:%s" % (pos, sample))     
#     RE.md["sample_name"] = sample 
#     RE.md["sample"] = sample 

    
def name_sam(pos):
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))     
    RE.md["sample_name"] = sample    
    RE.md["sample"] = sample    




############################################################################
#Transimission  

def measure_transmission_xs(t=1, mode = ['saxs'], waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False):
    """RE( measure_transmission_xs( sample = 'test' ) )"""
    
    if user_name is None:   
        try:     
            user_name = RE.md["user_name"]   
        except:
            user_name = 'test'

    if sample is None:    
        try:              
            sample = RE.md["sample_name"]   
        except:
            sample = 'test'
    sample0 = sample  
    if dy:
        yield from bps.mvr(piezo.y, dy)
    if dx:
        yield from bps.mvr(piezo.x, dx)
    dets = []
    if 'saxs' in mode:
        dets.append( pil2M )
    #print( 'xxx'  )  
    if 'waxs' in mode:
        dets.append( pil900KW )   
        yield from bps.mv(waxs, waxs_angle)  
        # if waxs_angle >=15:
        #     yield from bps.mv(waxs.bs_x, -108.0 )
        #     yield from bps.mv(waxs.arc, waxs_angle)
        # elif waxs_angle == 0:
        #     yield from bps.mv(waxs, waxs_angle)
        # else:
        #     yield from bps.mv(waxs, waxs_angle)        
        
        


    name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
    sample_name = name_fmt.format(
        sample=sample,
        x=np.round(piezo.x.position, 2),
        y=np.round(piezo.y.position, 2),
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2m_pos.z.position, 2),
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
   
    RE.md['sample_name'] = sample0
    RE.md['sample'] = sample0

            

def measure_saxs(t=1, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False):
    """RE( measure_saxs( sample = 'AgBH_12keV' ) )"""    
    return measure_transmission_xs(t=t, mode = ['saxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample, take_camera = take_camera)   

def measure_waxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_waxs() )  # take default parameters
    """
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['waxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera) 

def measure_wsaxs( t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_wsaxs() )  # take default parameters
    """
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['saxs', 'waxs' ], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera)     
    


def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20 , 40  ], 
                                   #waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    ks = list(sample_dict.keys())   
    maxA = np.max(waxs_angles)
    take_camera = False
    for waxs_angle in waxs_angles:
        print( f'WAXS angle is: {waxs_angle}....')
        for k in ks:
            print(k)
            yield from mov_sam_re(k)  #mov_sam_re
            for dx in dxs:
                print(dx)
                for dy in dys:
                    print(dy)
                    
                    for ti in t:
                        RE.md["sample_name"] = sample_dict[k]   
                        both = False
                        if saxs_on:    
                            if waxs_angle == maxA: 
                                both = True

                        print("Here we go ... ")
                        if both:        
                            yield from measure_wsaxs( t=ti, waxs_angle=waxs_angle, att="None", 
                                                     user_name= user_name, dx=dx, dy=dy, take_camera = take_camera  )
                        else:
                            yield from measure_waxs( t=ti, waxs_angle=waxs_angle, att="None",
                                                    user_name= user_name,
                                                      dx=dx, dy=dy, take_camera = take_camera  )

                       
            


def measure_multi_saxs_loop_angles(  t= [1],  dxs=[0], dys=[0], user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    ks = list(sample_dict.keys())   
    take_camera = False
    for k in ks:
        print(k)
        yield from mov_sam_re(k)  #mov_sam_re
        for dx in dxs:
            print(dx)
            for dy in dys:
                print(dy)                
                for ti in t:
                    RE.md["sample_name"] = sample_dict[k]                       
                    yield from measure_saxs( t=ti,  att="None",  user_name= user_name,
                                             dx=dx, dy=dy, take_camera = take_camera  )
   
   
 


class NanoSyn( ):
    def __init__(  self, sample='NPs'):
        '''       

        '''
        self.sample_pref = sample
        #self.sample_name = 'test'
        self.sample_name = sample
        self.new_batch_num = 0
        #self.base = '/nsls2/data/smi/legacy/results/data/2024_1/313765_YZhang2/Dropbox_Com/'
        self.base = '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/'


    def measure( self,sample_name=None,  t=1, take_camera = False ):
        waxs_angle = 20 #15 #if need change waxs angle, do     move_waxs(  waxs_angle ),  
        dets = [  pil2M, pil900KW ]
        if sample_name is not None:
            sample = sample_name
        else:        
            sample = self.sample_name
        name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
        sample_name = name_fmt.format(
            sample=sample,
            x=np.round(motorX.position, 2),
            y=np.round(motorZ.position, 2),            
            saxs_z=np.round(pil2m_pos.z.position, 2),
            waxs_angle=waxs_angle,
            t=t,
            #scan_id=RE.md["scan_id"],
        )
      ##################################
        #det_exposure_time(t, t) 
        ###################################
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        print("Collect data here....")
        #yield from bp.count(dets, num=1)
        #RE( bp.count(dets, num=1))
        det_exposure_time(t, t) 
        RE(bp.count(  dets ))
        if take_camera:
            scan_id=RE.md["scan_id"]
            sample_name_ova =  user_name +  '_' + sample_name + 'id_%s'%scan_id
            save_ova( sample= sample_name_ova   )





    def run( self,  sample_name ='X', sleep_time= 5, t=1,  motor='piezo', run_time = 3600*10, extra='', verbosity=3, **md):
        '''
        sam = NanoSyn( sample = 'Au111125_ASP_NoThiol_RT' )
        sam.measure( sample_name = 'Au111125_ASP_NoThiol_RT' )
        sam.run( sample_name = 'Au111125_ASP_NoThiol_RT', sleep_time=1, run_time = 60  )

        sam.run( sample_name = 'Au111125_ASP_Thiol_RT', sleep_time=30, run_time = 3600*6  )
        sam.run( sample_name = 'Au111125_ASP_Thiol_HT', sleep_time=30, run_time = 3600*6  )

        '''
        
        t0 = time.time()        
        print('Starting measurements for %.2f min.'%( run_time/60))
        I = 0
        if motor=='piezo':    
            x0, y0 = piezo.x.position, piezo.y.position
            Dx = np.arange( -40, 41, 20 )
            Dy = np.arange( -40, 41, 20  )
        elif motor == 'mdrive'   :     
            Dx = np.arange( -0.2, .3, .2 )
            Dy = np.arange( -0.2, .3, .2 )
        
        Dxy = []
        for i, dy in enumerate(Dy):
            for dx in Dx:
                if i%2==0:
                    Dxy.append( (dx, dy) )
                else:
                    Dxy.append( (-dx, dy) )
        Dxy = np.array( Dxy )    
        N = len( Dxy )    
        while (time.time() < ( t0 + run_time) ):
            self.measure(sample_name = sample_name, t=t )
            print( I )
            x, y = Dxy[ I%N ]
            print( f'Move by dx={x:.2f}, dy={y:.2f}' ) 


            if motor=='piezo':                
                RE( bps.mv( piezo.x, x0+x ) )
                RE( bps.mv( piezo.y, y0+y ) )   

            elif motor == 'mdrive':
                RE( bps.mvr( motorX, x ) )
                RE( bps.mvr( motorZ, y ) )   

            I+=1
            time.sleep(sleep_time)    

        dt = time.time() - t0
        print(f'This measurement for sample: {sample_name} took {dt:.2f} min.')






'''
saf=
proposal: 318527



20251109
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air


%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_EHu.py
proposal_swap(318527)
project_set('static')


sample_id(user_name='pw', sample_name=f'hscan_{get_scan_md()}')
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
# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: a transmission SAXS/WAXS run-book for a sample bar (this is the sibling of
#   2026C1_FLu.py). You set sample positions in pxy_dict, then call helpers like measure_saxs /
#   measure_waxs / measure_multi_waxs_loop_angles to visit each sample and take images. The two
#   '''...''' blocks above are setup notes, not live code.
#
# 💡 NEWER, EASIER WAY: 'smi_plans' has a "transmission bar" helper for exactly this — list the bar
#   once and it visits each sample and records position/beam INTO the data (no hand-built names):
#
#     from smi_plans import transmission_bar, SampleList
#     samples = SampleList.from_columns(name=list(sample_dict.values()),
#                                       x=[p[0] for p in pxy_dict.values()],
#                                       y=[p[1] for p in pxy_dict.values()])
#     RE(transmission_bar(samples, t=1, dets=[pil2M]))     # add pil900KW for WAXS
#
#   See the per-function notes below (transmission_run, time_series_run, kinetics_run). Your script
#   still works as-is EXCEPT for anything marked ⚠️.  (internal: Tier 1.)
# === end smi_plans note ================================================

 



username = 'BLi'
user_name = 'BLi'


 
sample_dict =  {1: 'S1', 2: 'S2', 3: 'S3', 4: 'S4', 5: 'S5', 6: 'S6', 
                7: 'S7', 8: 'S8', 9: 'S9', 10: 'S10', 11: 'S11', 
                12: 'S12', 13: 'S13', 14: 'S14' }
ypos = 0
pxy_dict = {   1:  ( -49100, -4000+500  ) ,  2: ( -43400, -8000), 3: ( -37000, -8000), 4: ( -30800, -8000), 
            5: ( -24600, -8000 ), 6: ( -17900, -8000), 7: ( -11400, -8000 ), 
            8: (-5400,-8000), 9: (1000, -8000), 10: ( 7300, -8000) , 
            11 : ( 13700, -8000), 12 : ( 20100, -8000),
              13 : ( 26300 + 200, -4000), 14 : ( 33200, -8000)}



username = 'YZhou'
user_name = 'YZhou'


sample_dict =  {1: 'S1', 2: 'S2', 3: 'S3', 4: 'S4', 5: 'S5', 6: 'S6', 
                7: 'S7', 8: 'S8', 9: 'S9', 10: 'S10', 11: 'S11', 
                12: 'S12', 13: 'S13', 14: 'S14' }
ypos = 0
pxy_dict = {   1:  ( -49200, -4000  ) ,  2: ( -43300, -4000), 3: ( -36800, -4000), 4: ( -30800, -8000), 
            5: ( -24200, -4000 ), 6: ( -17600, -4000), 7: ( -11200, -4000 ), 
            8: (-5000,-4000), 9: (1300, -4000), 10: ( 7400, -4000) , 
            11 : ( 14100, -4000), 12 : ( 20400, -4000),
              13 : ( 26600, -4000), 14 : ( 33200, -10700)}


username = ''
user_name = ''


sample_dict =  {1: 'Empty', 2: 'Capilary' }
ypos = 0
pxy_dict = {   1:  ( -49200, -4000  ) ,  2: ( -36600, -4000),}

sample_dict =  {1: 'AgBH' }
ypos = 0
pxy_dict = {   1:  ( -47400, -1600 )  }




pxy_dict = {  k: [ pxy_dict[k][0],  pxy_dict[k][1] + ypos ]  for k in pxy_dict }


 





motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3



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

def measure_transmission_xs(t=1, mode = ['saxs'], waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False):
    """RE( measure_transmission_xs( sample = 'test' ) )"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the core "take one transmission image of the current sample" plan. Depending
    #   on 'mode' it uses the SAXS camera (pil2M), the WAXS camera (pil900KW, after moving the arc),
    #   or both; optionally nudges x/y first and saves a descriptive file name.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' a single transmission shot is transmission_run (or a bare
    #   acquire), which records x/y/detector-distance/beam INTO the data and fills the file name from
    #   those recorded fields (so you don't read .position into the name yourself):
    #     from smi_plans import transmission_run
    #     yield from transmission_run(sample or RE.md["sample_name"], t=t,
    #                                 dets=[pil2M] + ([pil900KW] if 'waxs' in mode else []))
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    
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
        dets.append( pil2M )
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
        saxs_z=np.round(pil2m_pos.z.position, 2),
        waxs_angle=waxs_angle,
        t=t,
        #scan_id=RE.md["scan_id"],
    )
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
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
    


def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over WAXS arc angles, and for each angle visits every sample in the bar
    #   (optionally nudging x/y) and takes a WAXS image — adding a SAXS image too at the largest arc
    #   angle. A full "bar x arc-angle" sweep.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a transmission "bar" helper that visits every sample and
    #   sweeps the WAXS arc, recording sample/position/arc into each image, in one call:
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=list(sample_dict.values()),
    #                                       x=[p[0] for p in pxy_dict.values()],
    #                                       y=[p[1] for p in pxy_dict.values()])
    #     yield from transmission_bar(samples, t=t[0], waxs_arc=waxs_angles, dets=[pil2M, pil900KW])
    #   (Nothing here is broken; the ⚠️ exposure fix is inside measure_transmission_xs, which this
    #    calls.)  (internal: Tier 1.)
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())   
    maxA = np.max(waxs_angles)
    take_camera = False
    for waxs_angle in waxs_angles:
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: visits every sample in the bar (optionally nudging x/y) and takes a SAXS image
    #   of each — a straightforward "measure the whole bar in SAXS" loop.
    # 💡 NEWER, EASIER WAY: this is transmission_bar in 'smi_plans' (SAXS only — pass dets=[pil2M]):
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=list(sample_dict.values()),
    #                                       x=[p[0] for p in pxy_dict.values()],
    #                                       y=[p[1] for p in pxy_dict.values()])
    #     yield from transmission_bar(samples, t=t[0], dets=[pil2M])
    #   (Nothing broken here; the ⚠️ exposure fix lives in measure_transmission_xs.)  (internal: Tier 1.)
    # === end smi_plans note ================================================
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
        # === smi_plans note (REVIEW 2026-06-22) ================================
        # WHAT THIS DOES: takes one SAXS+WAXS image of the nanoparticle sample (used as the per-time
        #   point measurement inside run() below). It drives the beamline with RE(...) directly.
        # 💡 NEWER, EASIER WAY: a single shot is one acquire in 'smi_plans'; and the whole
        #   measure-on-a-timer loop in run() is what time_series_run / kinetics_run are for — see
        #   the note on run(). (Note: the exposure line here is currently commented out, so the
        #   exposure is whatever was last set.)
        # === end smi_plans note ================================================
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
        RE(bp.count(  dets ))
        if take_camera:
            scan_id=RE.md["scan_id"]
            sample_name_ova =  user_name +  '_' + sample_name + 'id_%s'%scan_id
            save_ova( sample= sample_name_ova   )





    def run( self,  sample_name ='X', sleep_time= 5, run_time = 3600*10, extra='', verbosity=3, **md):
        '''
        sam = NanoSyn( sample = 'Au111125_ASP_NoThiol_RT' )
        sam.measure( sample_name = 'Au111125_ASP_NoThiol_RT' )
        sam.run( sample_name = 'Au111125_ASP_NoThiol_RT', sleep_time=1, run_time = 60  )

        sam.run( sample_name = 'Au111125_ASP_Thiol_RT', sleep_time=30, run_time = 3600*6  )
        sam.run( sample_name = 'Au111125_ASP_Thiol_HT', sleep_time=30, run_time = 3600*6  )

        '''
        # === smi_plans note (REVIEW 2026-06-22) ================================
        # WHAT THIS DOES: an in-situ nanoparticle-synthesis kinetics run — for up to run_time
        #   seconds it repeatedly measures the sample, then hops to a fresh spot (to dodge beam
        #   damage) and sleeps, building a time series of how the particles grow/assemble.
        #
        # 💡 NEWER, EASIER WAY: a "measure over and over on a timer" experiment is exactly
        #   time_series_run / kinetics_run in 'smi_plans'. It records the elapsed time + frame number
        #   into each image and can step a dose/position motor between frames, so you don't manage
        #   the while-loop and clock yourself:
        #     from smi_plans import time_series_run
        #     RE(time_series_run(sample_name, duration=run_time, period=sleep_time, t=1,
        #                        dets=[pil2M, pil900KW], dose_motor=piezo.x, dose_step=200))
        #   (Nothing here is broken; this is just the tidier, self-recording pattern.)  (internal: Tier 0.)
        # === end smi_plans note ================================================
        
        t0 = time.time()        
        print('Starting measurements for %.2f min.'%( run_time/60))
        I = 0
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
            self.measure(sample_name = sample_name )
            print( I )
            x, y = Dxy[ I%N ]
            print( f'Move by dx={x:.2f}, dy={y:.2f}' ) 
            RE( bps.mvr( motorX, x ) )
            RE( bps.mvr( motorZ, y ) )               
            I+=1
            time.sleep(sleep_time)    

        dt = time.time() - t0
        print(f'This measurement for sample: {sample_name} took {dt:.2f} min.')






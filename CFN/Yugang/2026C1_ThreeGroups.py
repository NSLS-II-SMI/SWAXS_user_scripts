# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: a transmission SAXS/WAXS "run-book" (Yu Zhang, 2026C1, ThreeGroups) — it
#   defines a sample bar (sample_dict / pxy_dict), simple transmission measurement plans, multi-
#   angle/multi-sample loops, and a NanoSyn class for in-situ nanoparticle-synthesis kinetics.
#
# 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that turns these loops
#   into one-line runs and records position / beam / WAXS-arc straight INTO the data (so you don't
#   hand-build the long "{sample}_x..._y..." file names or stuff values into RE.md). Rough mapping:
#     - measure_saxs / measure_waxs / measure_wsaxs   -> transmission_run (one sample, SAXS/WAXS)
#     - measure_multi_*_loop_angles (a bar)           -> transmission_bar (takes a SampleList)
#     - NanoSyn.run (watch a synthesis over time)     -> time_series_run / kinetics_run
#       from smi_plans import transmission_run, transmission_bar, time_series_run, SampleList
#
# ⚠️ IMPORTANT pattern to know (see the per-function notes): several helpers call the beamline with
#   RE( ... )  INSIDE a Python for/while loop (e.g. mov_sam, NanoSyn.run). Each RE(...) starts a
#   SEPARATE run, so closed-loop / scripted control should sit ABOVE the plan; for a simple
#   sequential measurement, make it ONE plan with 'yield from' (the '*_re' twins already do this) —
#   which is exactly what the smi_plans runs above do for you.
#
# (Your script below still works as-is, EXCEPT for anything marked ⚠️ which needs a fix to run now.)
# === end smi_plans note ================================================
'''
saf=
proposal: 318527



20251109
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air


%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_EHu.py
proposal_swap(318527)
project_set('ThreeGroups')


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

 
'''
Data Folder:
/nsls2/data/smi/proposals/2026-1/pass-318527/projects/OGang

9 Meter
X, Y  are [0,0] --> 2M
saxs rod X --> 6.8 

 
'''


 
username = ''
user_name = '' 
sample_dict =  {1: 'QWang_Cell1_S1', 2: 'QWang_Cell1_S2', 3:  'QWang_Cell1_S3', 4: 'QWang_Cell1_S4', 
                5: 'QWang_Cell2_S1',  6: 'QWang_Cell1_S2', 7: 'QWang_Cell1_S3', 
                 8: 'MZheng_S1', 9: 'MZheng_S2',  }
ypos = 9000
pxy_dict = {   1:  ( -43000, -8000  ) ,  2: ( -36500, -8000), 3: ( -30400, -8000), 4: ( -24300, -8000 ), 
            5:  ( -11300, -8000 ),  6: (-5000,-8000), 7: (1600, -8000), 
            8: ( 7300, -8000) , 9 : ( 14400, -8000)}



username = ''
user_name = '' 
sample_dict =  {1: 'CAT_Unknown_S1', 2: 'CAT_Unknown_S2', 3: 'CAT_Unknown_S3', 4: 'CAT_Unknown_S4',                              

                5: 'AS_Unknown_S1',  6: 'AS_Unknown_S2', 7: 'AS_Unknown_S3',  8: 'AS_Unknown_S4',
                  9:  'AS_Unknown_S5',   10: 'AS_Unknown_S6',    }
ypos = 0
pxy_dict = {   1:  ( 33100, -7700  ) ,  2: ( 27000, -7300 ), 3: ( 19900, -7000), 4: ( 13700, -6540 ), 
            5:  ( 8100, -4100 ),  6: (1700,-4100), 7: (-5200, -4100),  8: ( -11800, -4100) ,             
            9 : ( -17600, -6000) , 10: {  -24000, -54100}  }  




username = ''
user_name = '' 
sample_dict =  {1: 'SY_S10_InP', 2: 'SY_S9_Cu3P', 3: 'SY_S7_Ti3C2THF', 4: 'SY_S6_Ti3C2Br2',  
                5:   'SY_S5_Ti3C2_h_MXene',    6:   'SY_S4_Ti3C2', 7:  'SY_S3_Ti3C2Cl2',   
                  8:  'SY_S2_CSS_Air',     9:  'SY_S1_CSS_Fresh', 
                  10:  'Jules_S1',  11:  'Jules_S2'  , 12:  'Jules_S3' }
ypos = 0
pxy_dict = {   1:  ( -36700, -3900  ) ,  2: ( -30400, -3300 ), 3: ( -23800, -5500), 4: ( -17200, -4000 ), 

            5:  (-11100, -4900 ),   6: (-4300, -4300 ), 7: (1700, -4700),  8: ( 7500,-4900) ,    9 : ( 14000, -4900) , 
             
              10: { 21100, -7100},    11: { 27200, -5900},    12: { 33800, -6200},    }  






# -29800, + 2600  (H)
# -8000 + 2600


# username = 'OG'
# user_name = 'OG'

# sample_dict =  {1: 'AgBH' }
# ypos = 0
# pxy_dict = {   1:  ( -47400+500, -1600 )  }


'''
for j in range( 10 ):    
    for i in range(10):
        RE(measure_saxs( t=1, sample = '240_S',  user_name = 'CL'))
        movx( 260  )
    movx( -2600 )
    movy( 260  )


for j in range( 1 ):    
    for i in range(10):
        RE(measure_saxs( t=.1, sample = '240_S',  user_name = 'CL'))
        movx( 260  )
    movx( -2600 )
    movy( 260  )


for j in range( 20 ):  
    RE(measure_saxs( t=1, sample = 'Unknown_S1',  user_name = 'CAT'))
    movy( 120 )


for j in range( 30 ):  
    RE(measure_saxs( t=1, sample = 'Unknown_S2',  user_name = 'CAT'))
    movy( 120 )


'''

ypos = 0
xpos = 0
username = 'CFN' 
sample_dict = {   1: 'AgBH'  }  #PZ = 8400
pxy_dict = {    1:[ 0, 0  ]   } 



pxy_dict = {  k: [ pxy_dict[k][0],  pxy_dict[k][1] + ypos ]  for k in pxy_dict }


 





#otorX = MDrive.m5 #
#otorZ = MDrive.m3


motorZ= MDrive.m5 #
motorX= MDrive.m3


###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3



def mov_sam(pos, dx = 0, dy=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience "go to sample N" — moves x/y to that sample's bar position and
    #   records the sample name in RE.md.
    # 💡 NOTE: this uses  RE(bps.mv(...))  so it can only be run from the prompt, NOT from inside a
    #   running plan. The 'mov_sam_re' twin uses 'yield from bps.mv(...)' and IS safe inside a plan —
    #   prefer that when composing. In smi_plans, 'goto_sample(samples, "name")' does this for you.
    # === end smi_plans note ================================================
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
    # WHAT THIS DOES: the core transmission measurement — takes a SAXS and/or WAXS image of the
    #   current sample (choosing detectors by 'mode'), building the file name from the current
    #   x/y/z and detector distance. (measure_saxs / measure_waxs / measure_wsaxs all call this.)
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run does this in one line and records the
    #   position / detector distance / beam straight INTO the data and into the file name for you:
    #     from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M, pil900KW])   # pick detectors like 'mode'
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
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
    det_exposure_time(t, t)   # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans transmission_run sets it for you via t=.)
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS-only shortcut that just calls measure_transmission_xs (see its note).
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M])
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, mode = ['saxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample, take_camera = take_camera)   

def measure_waxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_waxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a WAXS-only shortcut that just calls measure_transmission_xs (see its note).
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil900KW])   # set the WAXS arc as you do now
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['waxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera) 

def measure_wsaxs( t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_wsaxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS+WAXS shortcut that just calls measure_transmission_xs (see its note).
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M, pil900KW])   # set the WAXS arc as you do now
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['saxs', 'waxs' ], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera)     
    


def measure_multi_waxs_loop_angles(  t= [1],waxs_angles=[0, 16, 20, 40   ], 
                                   # waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a multi-sample bar at several WAXS arc angles — for each angle it visits every
    #   sample (with optional x/y offsets) and takes SAXS+WAXS (at the widest angle) or WAXS-only.
    #   Built the GOOD way with 'yield from', so it's one plan you launch once.
    # 💡 NEWER, EASIER WAY: this is a transmission bar with a WAXS-arc axis:
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from transmission_bar("loop", samples, t=t[0], dets=[pil2M, pil900KW])  # sweep the arc as an axis
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
    # WHAT THIS DOES: a SAXS bar — visits every sample (with optional x/y offsets) and takes a SAXS
    #   image (one plan, built with 'yield from').
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from transmission_bar("saxs_loop", samples, t=t[0], dets=[pil2M])
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a little controller for watching a nanoparticle synthesis over time — .measure()
    #   takes one SAXS+WAXS image, and .run() repeatedly measures (nudging x/y in a small pattern) for
    #   a set duration.
    # 💡 NEWER, EASIER WAY: an in-situ "watch a reaction over time" measurement is the smi_plans
    #   time-series / kinetics run, which loops and records the elapsed time / position / beam INTO
    #   each image for you:
    #     from smi_plans import time_series_run, kinetics_run
    #     yield from time_series_run("NPs", duration=run_time, delay=sleep_time, t=1, dets=[pil2M, pil900KW])
    #   For a closed-loop "decide-then-measure" controller, keep the decision logic ABOVE the plan and
    #   call one measurement plan with 'yield from' (see the ⚠️ note on .run()).
    # === end smi_plans note ================================================
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
        # WHAT THIS DOES: takes one SAXS+WAXS image of the synthesis cell and (optionally) saves the
        #   OAV camera frame, building the file name from the current motor positions.
        # 💡 NOTE: this runs the beamline with  RE(bp.count(dets))  from inside the method, so it can
        #   only be driven from the prompt (calling RE() inside a running plan errors). To compose it
        #   into a bigger plan, write it as 'yield from bp.count(dets)'. smi_plans' transmission_run
        #   does the same image and records position/beam into the data for you.
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
        # WHAT THIS DOES: an in-situ kinetics loop — for a set duration it repeatedly takes a SAXS+WAXS
        #   image of the synthesis and nudges x/y a little each time (in a small snaked pattern),
        #   sleeping between shots.
        # 💡 NEWER, EASIER WAY: a "watch a reaction over time" run is the smi_plans time-series:
        #     from smi_plans import time_series_run
        #     yield from time_series_run(sample_name, duration=run_time, delay=sleep_time, t=1,
        #                                dets=[pil2M, pil900KW])   # it loops + records time/position for you
        # 💡 ABOUT HOW IT RUNS: the position nudges here use  RE(bps.mvr(...))  INSIDE the while loop,
        #   so each is a SEPARATE run. The time-series helper above is one plan; if you need
        #   decide-then-measure logic, keep that logic ABOVE the plan and call ONE measurement plan
        #   with 'yield from' from inside it.
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






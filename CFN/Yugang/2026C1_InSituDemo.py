'''
saf=
proposal: 318527



20251109
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air


%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_EHu.py
proposal_swap(318527)
project_set('InSitu_Demo')


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




username = 'CL'
user_name = 'CL' 
sample_dict =  {1: '240_S', 2: '240_S1_' }
ypos = 0
pxy_dict = {   1:  ( -28000, -6500  ) ,  2: (  2800, -5820 ),  }



# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE IS: a per-experiment setup (it sets the sample table sample_dict / pxy_dict
#   and which MDrive motors are X/Z) plus a set of transmission measuring plans and a NanoSyn
#   class. Note the config is written several times below (CL, then DR overwrites it) — the
#   LAST one that runs wins.
#
# 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans'. Two ideas it would
#   tidy here: (1) keep the sample table as a SampleList (one object per experiment) instead of
#   loose dicts you overwrite; and (2) for the helpers that call RE() inside a function/loop,
#   prefer plain *plans* you run through the RunEngine — see the per-function notes below.
#   (Nothing at the top here is broken; pil2M / pil900KW / pil2m_pos are the current names.)
# === end smi_plans note ================================================



username = 'DR'
user_name = 'DR' 
sample_dict =  {1: '240_S', 3: 'SC_Control1' }
ypos = 0
pxy_dict = {   1:  ( -28000, -6500  ) ,  2: (  -29800, -5700 ),  }




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

'''



pxy_dict = {  k: [ pxy_dict[k][0],  pxy_dict[k][1] + ypos ]  for k in pxy_dict }


 





motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3



def mov_sam(pos, dx = 0, dy=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: jogs the piezo x/y to sample 'pos' (from pxy_dict) and stashes the name
    #   in RE.md. It calls RE(...) itself, so it's a function you run at the prompt — NOT a plan.
    #   (mov_sam_re just below is the plan version of the same move.)
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the bar lives in a SampleList and you move to a
    #   sample with a real plan that also records where it went:
    #     from smi_plans import goto_sample
    #     RE(goto_sample(bar[pos]))     # bar = SampleList.from_columns(names=..., piezo_x=..., piezo_y=...)
    #   (Nothing here is broken — just a tidier pattern.)
    # === end smi_plans note ================================================
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px + dx ))
    RE(bps.mv(piezo.y, py + dy))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample
    RE.md["sample_name"] = sample


def mov_sam_re(pos, dx =0, dy=0   ):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the *plan* version of mov_sam — moves the piezo x/y to sample 'pos' and
    #   stashes the name in RE.md, so you 'yield from' it inside other plans.
    #
    # 💡 NEWER, EASIER WAY: smi_plans does the same with goto_sample(bar[pos]) (a plan), and it
    #   passes the sample name along via the run's metadata instead of mutating RE.md by hand:
    #     from smi_plans import goto_sample
    #     yield from goto_sample(bar[pos])
    #   (Nothing here is broken — just a tidier pattern.)
    # === end smi_plans note ================================================
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
    # WHAT THIS DOES: takes one transmission frame — SAXS, WAXS, or both (per 'mode') — and
    #   bakes the motor positions + detector distance + WAXS angle into the file name by
    #   reading .position and pasting them in. This is the workhorse the measure_* wrappers and
    #   the loop plans below all call.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans', which records the positions /
    #   distance / angle INTO the data and fills them into the file name from the recorded
    #   values (no .position-into-string), and offers an arc-aware detector helper that drops
    #   SAXS automatically when the WAXS arc is in the way:
    #
    #     from smi_plans import transmission_run, saxs_waxs_dets   # do this once per session
    #     yield from transmission_run(sample, t=t,
    #                                 dets=saxs_waxs_dets(use_waxs=('waxs' in mode)),
    #                                 reads=[pil2m_pos.z, waxs])
    #
    #   (Just a tidier option to try later — your plan still works as-is, EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must run as a plan — see
    #   the ⚠️ note on that line.
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
    det_exposure_time(t, t)   # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
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
    # WHAT THIS DOES: a one-line shortcut — calls measure_transmission_xs in SAXS-only mode.
    # 💡 NEWER, EASIER WAY: the smi_plans equivalent is a SAXS-only transmission run:
    #     from smi_plans import transmission_run, saxs_waxs_dets
    #     yield from transmission_run(sample, t=t, dets=saxs_waxs_dets(use_waxs=False))
    #   (See the fuller note on measure_transmission_xs. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, mode = ['saxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample, take_camera = take_camera)   

def measure_waxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_waxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a one-line shortcut — calls measure_transmission_xs in WAXS-only mode.
    # 💡 NEWER, EASIER WAY: the smi_plans equivalent is a WAXS transmission run:
    #     from smi_plans import transmission_run, saxs_waxs_dets
    #     yield from transmission_run(sample, t=t, dets=saxs_waxs_dets(use_saxs=False), reads=[waxs])
    #   (See the fuller note on measure_transmission_xs. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['waxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera) 

def measure_wsaxs( t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_wsaxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a one-line shortcut — calls measure_transmission_xs in SAXS+WAXS mode.
    # 💡 NEWER, EASIER WAY: the smi_plans equivalent reads both detectors (arc-aware):
    #     from smi_plans import transmission_run, saxs_waxs_dets
    #     yield from transmission_run(sample, t=t, dets=saxs_waxs_dets(), reads=[waxs, pil2m_pos.z])
    #   (See the fuller note on measure_transmission_xs. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['saxs', 'waxs' ], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera)     
    


def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over WAXS angles and over every sample (and optional dx/dy offsets
    #   and exposure times), taking WAXS — and at the largest angle also SAXS — at each. It's a
    #   proper plan (it 'yield from's the moves and measurements).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' with a bar runner that loops the
    #   bar + WAXS arc for you and records the arc/beam/distance into the data + file name. The
    #   "only read SAXS at the largest arc" trick is built into its arc-aware detector helper
    #   saxs_waxs_dets(). Sketch:
    #
    #     from smi_plans import SampleList, transmission_bar
    #     bar = SampleList.from_columns(names=list(sample_dict.values()),
    #                                   piezo_x=[v[0] for v in pxy_dict.values()],
    #                                   piezo_y=[v[1] for v in pxy_dict.values()])
    #     yield from transmission_bar(bar, t=t[0], waxs_arc=tuple(waxs_angles))
    #
    #   (Nothing here is broken — pil2M/pil900KW are current. Just a tidier pattern.)
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
    # WHAT THIS DOES: loops over every sample (and optional dx/dy offsets and exposure times)
    #   taking a SAXS frame at each. It's a proper plan.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' bar runner loops the bar for you and records the beam /
    #   distance into the data + file name:
    #
    #     from smi_plans import SampleList, transmission_bar
    #     bar = SampleList.from_columns(names=list(sample_dict.values()),
    #                                   piezo_x=[v[0] for v in pxy_dict.values()],
    #                                   piezo_y=[v[1] for v in pxy_dict.values()])
    #     yield from transmission_bar(bar, t=t[0], use_waxs=False)
    #
    #   (Nothing here is broken — just a tidier pattern.)
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
        # WHAT THIS DOES: takes one SAXS+WAXS frame (WAXS arc 20 deg) and bakes the motor
        #   positions + detector distance into the file name by reading .position. It runs
        #   RE(bp.count(...)) directly, so this method is NOT itself a plan.
        #
        # 💡 NEWER, EASIER WAY: 'smi_plans' records the positions/distance INTO the data and
        #   fills the file name from the recorded values, and gives you a plain *plan* you run
        #   through the RunEngine (instead of calling RE() inside a method):
        #     from smi_plans import transmission_run
        #     RE(transmission_run(sample, t=t, dets=[pil2M, pil900KW], reads=[pil2m_pos.z]))
        #   (Nothing here is broken — det_exposure_time is already commented out. Tidier pattern.)
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
        # WHAT THIS DOES: repeatedly calls measure() in a Python while-loop until a wall-clock
        #   time runs out, nudging the sample by small dx/dy between frames (it moves via
        #   RE(bps.mvr(...)) inside the loop) — a long in-situ time series with a little raster.
        #
        # 💡 NEWER, EASIER WAY: launching a fresh RE(...) per frame inside a Python loop makes
        #   many tiny separate runs. The beamline now has 'smi_plans' with a time-series runner
        #   that records the whole sequence as ONE run with the timing stamped in, launched once:
        #
        #     from smi_plans import time_series_run      # do this once per session
        #     RE(time_series_run(sample_name, duration=run_time, period=sleep_time, t=1,
        #                        dets=[pil2M, pil900KW]))
        #     # the small dx/dy walk can be a per-frame step composed into the run.
        #
        #   (Nothing here is broken — this is a tidier, better-recorded way to do the same run.)
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






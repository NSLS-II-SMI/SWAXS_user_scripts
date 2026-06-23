# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: a transmission SAXS/WAXS "run-book" (Yu Zhang, 2025C3, XLin) — it defines a
#   sample bar (sample_dict / pxy_dict), simple transmission measurement plans, multi-angle/multi-
#   sample loops, and a NanoSyn class for in-situ nanoparticle-synthesis kinetics.
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
saf=315967///317437
proposal: 317378 //318919



20251109
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air


%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C3_XLin.py
proposal_swap(318919)
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







'''

 



username = 'YZ'
user_name = 'YZ'

username = 'DM'
user_name = 'DM'


username = 'XL'
user_name = 'XL'



username = 'YZ'
user_name = 'YZ'


sample_dict =  {1: 'AgBH'}
ypos = 0
pxy_dict = {   1:  ( 69, 101  ) ,}


sample_dict =  {1: 'S1', 2: 'S2', 3: 'S3', 4: 'S4', 5: 'S5', 6: 'S6', 
                7: 'S7', 8: 'S8', 9: 'S9', 10: 'S10', 11: 'S11' }
ypos = 0
pxy_dict = {   1:  ( 65.8, 102.6  ) ,  2: ( 63.1, 100), 3: ( 56.7, 98.4), 4: ( 51, 97.4), 
            5: ( 45.8, 99 ), 6: ( 39.6, 98.6), 7: ( 33.7 , 97.6  + .4 ), 
            8: (30.1,98.4), 9: (25.7, 99.8), 10: ( 22.1, 98.8) , 11 : ( 17.2, 96.8)}


sample_dict =  {1: 'Au110225A1_Top', 2: 'Au110225A1_Bottom', 3: 'Au1111_25ASP',  4: 'Toluene' }
ypos = 0
pxy_dict = {   1:  ( 94.7, 104.2  ) ,  2: ( 89.3, 104.2), 3: ( 81.3, 104.4 ),  4: ( 73.1, 104.5 )  }

sample_dict =  {1: 'Toluene_in_Reactor' }
ypos = 0
pxy_dict = {   1:  ( 29, 71  )  }

sample_dict =  {1: 'ASP' }
ypos = 0
pxy_dict = {   1:  ( 20.6, 69  )  }


 


'''
Sample UID:
('f6f64805-4c5b-4d25-88af-8cc7a0e3dd93',
 '78b899fe-3faf-4650-828b-17ea922df0ae',
 '54d9f4b5-b55f-4b6b-bd5c-f985ef41fdac',
 'c19c3e9d-8aeb-4b60-b3e8-2118e7f276a9',
 '3ffd6d79-b1e0-4e64-bbdb-fb3945a638e5',
 '63684db1-90c0-42c0-9613-53a3a47524db',
 'bf04afdb-277a-455b-9295-49650de4668f',
 '0ad92fa1-1459-4d78-917e-5623df96e10d',
 '00bf5764-c5e9-4647-b6c0-b04a1e612363',
 '28743275-e569-4b22-a5a2-ae3bbe1ec95c',
 'c730fd72-84e5-43f6-b8e7-245d44f3bc95',
 'ffb3a6d4-e7de-441c-a4ec-0bc0b338f7ca',
 'fb2da089-0d9a-4507-b387-b1eb65baa03e',
 'baafd5f2-64bd-4d28-bf39-fa59fa0169a7',
 'e3aecb5c-4d98-4d93-b0f9-edb154878d4c',
 '2c30be45-2e27-4dd6-a055-bb56dd4c07ab',
 '81fd5e2b-b8f6-48e3-8751-61e8c72eb090',
 '295d9ecc-8ccf-46bc-9559-157a7e44b12d',
 '5de9622b-cf65-4b55-8342-b284b56e4f50',
 'fd2276ce-1eac-496c-b031-727b85b741a4',
 '0dbdd437-7589-4862-9690-8ecff82708b8',
 'd37eb03a-733a-4abe-8b2b-4350209172d5',
 '1fcba1d8-d635-44cc-8aa0-295f100f3ef8',
 '94ab870a-b44f-4beb-9fd7-93d4f5a41a94',
 '4ea97583-28cf-4dbe-acb5-6d44d1d9a013',
 '5fbd3b77-8634-40cd-899d-6230c456b1e6',
 'cded5cb0-7d9f-4642-88cb-71ec5c79697b',
 'd11f7088-1e57-417e-8d89-d20b93e34c8d',
 '811355bd-3032-4f41-bb6e-baee557817a8',
 'b297893f-0b2e-4759-a0ec-b0b1a1a03638',
 'bbdb5713-b12a-41ce-b9d7-b2d427969fd1',
 'af877435-e7ca-40f6-b6ec-83e39ce24f46',
 '2cc3ecc5-5fd0-4071-9007-106941268fac')


SAXS:
('a84d21ea-1781-4045-849b-495c10ac9d5d',
 '857e285a-9168-4887-a6bf-ac2b08f3979f',
 'cf0e6abf-fed4-4dc9-8211-0fafde36197a',
 '7297f8ac-cfad-4c56-8aac-c120a53593b2',
 '82746c75-b5bd-4e2c-aae4-2f52bd89f511',
 '381821d6-a9ce-4222-849e-5d146756c7d0',
 'bc790264-1132-4081-a7bd-150a0a839b28',
 '80a943fa-25bf-493a-917a-216c7eea93d6',
 '7cdf338b-db34-47aa-a130-8d27c95b6a12',
 'cd8573bb-978b-40b7-aa46-7bccfbb9335b',
 '14a34784-13f8-40b5-a844-4c02a3861db9')






'''




motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3





def mov_sam(pos, dx=0, dy=0  ):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience "go to sample N" — moves the holder motors to that sample's bar
    #   position and records the sample name in RE.md.
    # 💡 NOTE: this uses  RE(bps.mv(...))  so it can only be run from the prompt, NOT from inside a
    #   running plan. The 'mov_sam_re' twin uses 'yield from bps.mv(...)' and IS safe inside a plan —
    #   prefer that when composing. In smi_plans, 'goto_sample(samples, "name")' does this for you.
    # === end smi_plans note ================================================
    #M, _, _ = get_motor( )   
    px, py = pxy_dict[pos]
    RE(bps.mv( motorX, px + dx))
    RE(bps.mv( motorZ, py + dy))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))   
    RE.md["sample_name"] = sample
    RE.md["sample"] = sample


def mov_sam_re(pos, dx =0, dy=0   ):
    #M, _, _ = get_motor( )  
    px, py = pxy_dict[pos]
    yield from bps.mv(motorX, px + dx)
    yield from bps.mv(motorZ, py + dy)
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))     
    RE.md["sample_name"] = sample 
    RE.md["sample"] = sample 

    
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
    


def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20  ], 
                                   dxs=[0], dys=[0], saxs_on=True , user_name= user_name  ):
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






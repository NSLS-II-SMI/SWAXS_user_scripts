# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: an in-situ growth run-book — config (sample positions in
#   'pxy_dict', names in 'sample_dict') at the top, then helpers to move to a sample,
#   measure SAXS/WAXS, loop over samples/angles, and a NanoSyn class that re-measures a
#   spot over time while nudging x/y to spread the dose.
#
# 💡 NEWER, EASIER WAY: the 'smi_plans' library (a helper library the beamline now
#   provides) covers these patterns and records the energy, beam intensity, position,
#   detector distance, etc. straight INTO the saved data (so they don't have to be packed
#   into the file name by hand):
#     - one transmission shot  ->  from smi_plans import transmission_run
#     - a whole bar of samples ->  transmission_bar / giwaxs_bar with a SampleList
#     - "watch one spot over time" (the NanoSyn loop) -> time_series_run / kinetics_run
#   A SampleList (smi_plans' way of listing samples) can be built straight from your
#   dicts, e.g. SampleList.from_columns(name=[...], x=[...], y=[...]).
#
#   See the per-function notes below for concrete examples with your own numbers. Your
#   code still works as-is, EXCEPT for the lines marked ⚠️ (the det_exposure_time calls)
#   which genuinely need a fix to run now.
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
project_set('InSitu')


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



username = 'DR'
user_name = 'DR' 
sample_dict =  {1: 'Blank1', 2: '5lank15' }
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




'''



pxy_dict = {  k: [ pxy_dict[k][0],  pxy_dict[k][1] + ypos ]  for k in pxy_dict }


 





motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3



def mov_sam(pos, dx = 0, dy=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: jumps the sample stage to the saved x/y position for sample number
    #   'pos' (from pxy_dict) and records its name in RE.md.
    #
    # 💡 NEWER, EASIER WAY: in the 'smi_plans' library you list your samples once (as a
    #   SampleList) and the run helpers move to each one and record its name into the data
    #   for you — so you don't move-then-stash-the-name by hand:
    #     from smi_plans import SampleList, goto_sample
    #     samples = SampleList.from_columns(name=list(sample_dict.values()),
    #                                       x=[v[0] for v in pxy_dict.values()],
    #                                       y=[v[1] for v in pxy_dict.values()])
    #     yield from goto_sample(samples[pos])     # moves there inside a plan
    #   (Nothing here is broken; this just becomes built-in once you migrate.)
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
    # WHAT THIS DOES: the plan version of mov_sam — moves to sample 'pos' from inside a
    #   plan (so it can be used with 'yield from') and records its name.
    #
    # 💡 NEWER, EASIER WAY: same as mov_sam above — 'smi_plans' moves to each sample and
    #   records its name for you when you list samples as a SampleList and use goto_sample
    #   / the bar run helpers. (Nothing here is broken; just becomes built-in.)
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
    # WHAT THIS DOES: the core single-shot measurement — picks SAXS and/or WAXS detectors,
    #   optionally moves the WAXS arc, builds a long file name from the current positions,
    #   sets the exposure, and takes one image.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' library has a one-line transmission run that
    #   sets the exposure (via t=) and records the positions/detector-distance/beam into
    #   the image for you (so you don't have to read piezo.x / pil2m_pos.z by hand and
    #   stuff them into the name — smi_plans fills tokens like {energy_energy} from the data):
    #
    #     from smi_plans import transmission_run
    #     yield from transmission_run(
    #         sample,                             # rest of the file name is added automatically
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],             # SAXS and/or WAXS, as you choose with 'mode'
    #     )
    #     # (for WAXS, move the arc first or pass it as an axis; smi_plans records the angle)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets
    #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
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
    det_exposure_time(t, t)   # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: a shortcut that takes a single SAXS-only shot (it just calls
    #   measure_transmission_xs with mode=['saxs']).
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M])   # sets exposure + records context
    #   (See the fuller note on measure_transmission_xs above. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, mode = ['saxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample, take_camera = take_camera)   

def measure_waxs( t=1, waxs_angle=15, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_waxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortcut that moves the WAXS arc and takes a single WAXS-only shot
    #   (it just calls measure_transmission_xs with mode=['waxs']).
    # 💡 NEWER, EASIER WAY:  from smi_plans import giwaxs_run
    #     yield from giwaxs_run(sample, t=t, dets=[pil900KW], arc=[waxs_angle])  # records arc + context
    #   (See the fuller note on measure_transmission_xs above. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['waxs'], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera) 

def measure_wsaxs( t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False ):
    """ 
    RE(  measure_wsaxs() )  # take default parameters
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a shortcut that takes a single SAXS+WAXS shot at once (it just calls
    #   measure_transmission_xs with mode=['saxs','waxs']).
    # 💡 NEWER, EASIER WAY:  from smi_plans import giwaxs_run
    #     yield from giwaxs_run(sample, t=t, dets=[pil2M, pil900KW], arc=[waxs_angle])
    #   (See the fuller note on measure_transmission_xs above. Nothing here is broken.)
    # === end smi_plans note ================================================
    return measure_transmission_xs(t=t, waxs_angle = waxs_angle, mode = ['saxs', 'waxs' ], att=att, dx=dx, dy=dy, user_name=user_name, sample=sample,  take_camera = take_camera)     
    


def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over a set of WAXS arc angles and, for each, visits every
    #   sample in sample_dict and a few x/y offsets, taking WAXS (and SAXS at the biggest
    #   angle) at each spot.
    #
    # 💡 NEWER, EASIER WAY: "run a bar of samples and sweep the WAXS arc" is exactly the
    #   'smi_plans' GIWAXS bar helper; give it your samples as a SampleList and it visits,
    #   sweeps the arc, names, and records the arc/position/beam into each image:
    #
    #     from smi_plans import giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=list(sample_dict.values()),
    #                                       x=[v[0] for v in pxy_dict.values()],
    #                                       y=[v[1] for v in pxy_dict.values()])
    #     yield from giwaxs_bar("InSitu", samples, arc=[0, 15, 20, 40], t=t[0],
    #                           dets=[pil2M, pil900KW])
    #
    #   (Just a tidier option to try later — your script below works as-is; nothing here
    #    is broken. (internal: Tier 1.))
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
    # WHAT THIS DOES: visits every sample in sample_dict (and a few x/y offsets) and takes
    #   a SAXS shot at each.
    #
    # 💡 NEWER, EASIER WAY: running a bar of SAXS samples is one call in the 'smi_plans'
    #   library; give it your samples as a SampleList and it visits, names, and records the
    #   position/beam into each image:
    #
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=list(sample_dict.values()),
    #                                       x=[v[0] for v in pxy_dict.values()],
    #                                       y=[v[1] for v in pxy_dict.values()])
    #     yield from transmission_bar("InSitu", samples, t=t[0], dets=[pil2M])
    #
    #   (Just a tidier option to try later — your script below works as-is; nothing here
    #    is broken. (internal: Tier 1.))
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
        # WHAT THIS DOES: takes one SAXS+WAXS image of the current sample, building a long
        #   file name from the current motor positions and detector distance.
        #
        # 💡 NEWER, EASIER WAY: the 'smi_plans' library takes a single shot in one line and
        #   records the positions/detector-distance/beam into the image for you (so you
        #   don't read motorX/pil2m_pos.z by hand and pack them into the name):
        #
        #     from smi_plans import transmission_run
        #     yield from transmission_run(sample, t=t, dets=[pil2M, pil900KW])
        #
        #   (Heads-up: this method calls RE(bp.count(...)) directly. In smi_plans you write
        #    the measurement as a plan and 'yield from' it, which lets the time-loop in
        #    run() below schedule everything cleanly instead of starting a new run each shot.)
        #
        #   (Just a tidier option to try later — your code still works as-is,
        #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
        #
        # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets
        #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 0.)
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
        det_exposure_time(t, t)   # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
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
        # === smi_plans note (REVIEW 2026-06-22) ================================
        # WHAT THIS DOES: watches one growing sample over time — it re-measures every few
        #   seconds for up to many hours, nudging x/y a little each time so the beam
        #   doesn't dwell on one spot, until the run time is up.
        #
        # 💡 NEWER, EASIER WAY: "keep measuring over time" is the 'smi_plans' time-series /
        #   kinetics idea. Instead of a hand-rolled 'while time.time() < ...' loop that
        #   calls RE() each pass, you write the measurement as a plan and let a kinetics run
        #   repeat it for a set number of frames (or a duration), recording the time/position
        #   into each frame:
        #
        #     from smi_plans import time_series_run, kinetics_run
        #     # take a frame every 'sleep_time' seconds for the duration, dose-spread x/y:
        #     yield from kinetics_run(sample_name,
        #                             lambda: transmission_run(sample_name, t=t,
        #                                                      dets=[pil2M, pil900KW]),
        #                             period=sleep_time)
        #
        #   (Just a tidier option to try later — your loop below works as-is; nothing here
        #    is broken. (internal: Tier 0 — RE-in-a-while-loop time series.))
        # === end smi_plans note ================================================
        
        t0 = time.time()        
        print('Starting measurements for %.2f min.'%( run_time/60))
        I = 0
        if motor=='piezo':    
            x0, y0 = piezo.x.position, piezo.y.position
            Dx = np.arange( -400, 410, 20 )
            Dy = np.arange( -400, 410, 20  )
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






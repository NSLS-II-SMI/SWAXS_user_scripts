

# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: a micro-focus thermal "run-book" (OGang / Fang Lu, 2024C2) — it defines a
#   sample bar (sample_dict / pxy_dict / lim_dict), simple SAXS/WAXS measurement plans, x/y maps,
#   and a set of melting / isothermal temperature routines you launch by hand from the prompt (see
#   the DAPHNE / Mingxin command examples in the big quoted blocks below).
#
# 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that turns these loops
#   into one-line runs and records position / temperature / beam straight INTO the data (so you
#   don't hand-build the long "{sample}_x..._y..." file names or stuff values into RE.md). Mapping:
#     - measure_saxs / measure_waxs / measure_wsaxs   -> transmission_run (one sample, SAXS/WAXS)
#     - run_RT_temperature (fresh spot per sample)    -> transmission_bar (takes a SampleList)
#     - run_HT_time_temperature / run_Tm (hold + watch)-> isothermal_kinetics_run
#     - run_melting / run_melting_Tm (ramp + measure) -> temperature_ramp_run
#     - Measure_Map / getSamMap (x/y raster)          -> map_grid_run
#       from smi_plans import transmission_run, transmission_bar, temperature_ramp_run, isothermal_kinetics_run
#
# ⚠️ IMPORTANT pattern to know (see per-function notes): the routines whose names DON'T start with
#   RE_ command the beamline with  RE( ... )  INSIDE Python for/while loops. Each RE(...) starts a
#   SEPARATE run, so a long temperature series becomes hundreds of tiny runs and you can't cleanly
#   pause/resume it. The  RE_*  twins are the fixed style: ONE plan built with 'yield from', launched
#   with a single  RE(RE_run_...())  — prefer those (and that is exactly what the smi_plans runs do).
#
# (Your script below still works as-is, EXCEPT for anything marked ⚠️ which needs a fix to run now.)
# === end smi_plans note ================================================
print('Load Fang Lu micro -- 2024C1...')
from datetime import datetime


 

 
 
 


smi = SMI_Beamline()

#user_name = "FLu"
#user_name = "HKim"
#user_name = "MH"
#user_name = "WLiu"
#username = user_name

 
 

''' NOTE

 # SAXS distance , 5 meter
# 1M [  -2.77, -61., 5000  ]
# beam stop [ 1.8, 288.99,  13  ], a rod
# beam center   [ 471, 559     ]
# beamstop_save()



proposal_id('2024_1', '313760_FLu', analysis=True)
/nsls2/data/smi/legacy/results/data/2024_1/313760_FLu

%run -i  ~/.ipython/profile_collection/startup/users/30-user-Flu_2024C1_TSAXS.py


RE( measure_saxs( sample = 'DirectBeam' ) )
RE(SMI.modeMeasurement())
RE( measure_saxs( sample = 'AgBH_5m' ) )

RE( measure_waxs(   sample = 'AgBH_5m', waxs_angle = 20   ) )


t0=time.time();RE(measure_series_multi_angle_wsaxs(waxs_angles=[0,  20   ]));run_time(t0)





Mingxin's T samples
Y: 470
hexY:L -7 


Fang's sample, X -30900, Y: 900, hexY: -1 
proposal_id('2024_2', '313760_Flu_01', analysis=True)


'''




# Run1, pizo motor (SmarAct) Z= ,  sample to SAXS dector distance 5m
dx, dy = 0, 0

user_name = "DS"
username = user_name

#sample_dict = {k: 'S_%03d'%k for k in range(1,16) }
## Run1, S7 - S1, 
# sample_dict = {  8: '3_38_A',  
#                # 10: '2_87_F1',   
# }
# pxy_dict = {  8:  ( 1200, 0     ) ,  
#             #10:  ( 14100, 200     ) ,
 
#   }

# lim_dict = { 8: [ [ 1000, 1400 + 200 ], [-20, 160 + 30 ]], 
#            #   10: [ [ 14100 - 200, 14100 + 200], [200 - 20, 200 + 160 ]], 
# }


sample_dict = {  
                 2: '2-41_v96_8H_1_1',  
                 3: '2-41_v96_8H_1_2',  
                 4: '2-41_v96_8H_2_1', 
                 5: '2-41_v54_8H_1_1',  
                 6: '2-41_v54_8H_1_2',  
                 7: '2-41_v54_8H_2_1', 
                 8: '2-46_v96_8H_1_1',  
                 9: '2-46_v96_8H_1_2',  
                 10: '2-46_v96_8H_2_1', 
                 11: '2-46_v54_8H_1_1',  
                #  12: '2-41_v54_8H_1_2',  
                 13: '2-46_v54_8H_2_1',
                 14: '1xTAE+12-5mM_Mg_Buffer',  
}
pxy_dict = {  
              2:  ( -37018, 528     ) ,  
              3:  ( -30317, 378     ) , 
              4:  ( -24018, -122     ) ,
              5:  ( -18068, -22     ) ,  
              6:  ( -11468, 27     ) , 
              7:  ( -5268, -372     ) , 
              8:  ( 1582, -372     ) ,  
              9:  ( 7281, 127     ) , 
              10:  ( 13982, 127     ) , 
              11:  ( 20081, 278     ) ,  
            #   12:  ( 26685, 28     ) , 
              13:  ( 33131, 27     ) , 
              14:  ( 39331, 478     ) ,  
  
          
 
  }

lim_dict = { 
            2:  [ [ -37018,-37018  + 200 ], [ 528, 528 + 30 ]], 
            3:  [ [ -30317, -30317 + 200 ], [ 378, 378 + 30 ]],
             4:  [ [ -24018, -24018 + 200 ], [ -122, -122 + 30]],
             5:  [ [ -18068, -18068 + 200 ], [ -22, -22 + 30 ]], 
             6:  [ [ -11468, -11468 + 200 ], [ 27, 27 + 30 ]],
             7:  [ [ -5268, -5268 + 200 ], [ -372, -372  + 30 ]],
             8:  [ [  1582,  1582 + 200 ], [ -372, -372 + 30 ]], 
             9:  [ [  7281,  7281 + 200 ], [ 127, 127 + 30 ]],
             10: [ [ 13982, 13982   + 200 ], [ 127, 127 + 30 ]],
             11: [ [ 20081, 20081   + 200 ], [ 278, 278 + 30 ]],
            #  12: [ [ 26685, 26685   + 200 ], [ 28, 28 + 30 ]],
             13: [ [ 33131, 33131   + 200 ], [ 27, 27 + 30 ]],
             14: [ [ 39331, 39331   + 200 ], [ 478, 478 + 30 ]],

            #  10: [ [ 14100 - 200, 14100 + 200], [200 - 20, 200 + 160 ]], 
}








# t0=time.time();RE(measure_series_multi_angle_wsaxs(waxs_angles=[0,  20   ]));run_time(t0)





# def shopen():
#     yield from bps.mv(ph_shutter.open_cmd, 1)
#     yield from bps.sleep(1)
#     # Disabled because of problems with XBPM3 in microfocus    
#     yield from bps.mv(manual_PID_disable_pitch, "0")
#     yield from bps.mv(manual_PID_disable_roll, "0")

   # #Check if te set-up is in-air or not. If so, open t
   # he GV automatically when opening the shutter
    # if get_chamber_pressure(chamber_pressure.waxs) > 1E-02 and get_chamber_pressure(chamber_pressure.maxs) < 1E-02:
    #    yield from bps.mv(GV7.open_cmd, 1 )
    #    yield from bps.sleep(1)
    #    yield from bps.mv(GV7.open_cmd, 1 )
    #    yield from bps.sleep(1)



#####12/15
#energy 8.33, Dis 5 m 



#   t0=time.time();RE(measure_series_multi_angle_wsaxs());run_time(t0)




######################



dx =  0
dy = 0 #-2000
ks = np.array(list((sample_dict.keys())))
pxy_dict = {k: [pxy_dict[k][0] + dx, pxy_dict[k][1] + dy] for k in ks}

x_list = np.array(list((pxy_dict.values())))[:, 0]
y_list = np.array(list((pxy_dict.values())))[:, 1]
sample_list = np.array(list((sample_dict.values())))
##################################################
############ Some convinent functions#################
#########################################################

def Measure_one():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience driver — builds two grid maps with getSamMap and measures each
    #   with Measure_Map (which calls the beamline with RE() internally).
    # 💡 NEWER, EASIER WAY: smi_plans' map_grid_run does a labelled raster in one line (recording
    #   position/beam into each image), and you launch the whole thing as one plan with RE(...).
    # === end smi_plans note ================================================
    #ps1 = getSamMap( pos = [ -27760, -2930],  step_size = [100, 100], rot_angle = 0, Nx=20 , Ny=30)
    #Measure_Map(  t = 5 ,  sample = 'O139_100umstep',  pz=7980,  ps=ps1,  username = 'FTeng', )
    ps1 = getSamMap( pos = [ -27800, -1975],  step_size = [100, 100], rot_angle = 0, Nx=25 , Ny=4)
    Measure_Map(  t = 5 ,  sample = 'O139_50um_100umstep',  pz=7980,  ps=ps1,  username = 'FTeng', )
    
    ps2 = getSamMap( pos = [ -27810, -1455],  step_size = [100, 100], rot_angle = 0, Nx=25 , Ny=4)
    Measure_Map(  t = 5 ,  sample = 'O139_20um_100umstep',  pz=7980,  ps=ps2,  username = 'FTeng', )


 

'''
DAPHNE:  
#for TEST
i_dict =  run_RT_temperature(   exposure_t = 0.1 , i_dict = None  ) 
run_HT_time_temperature( T = 29, t_interval=3, t_total = 12,exposure_t = 0.1, i_dict = i_dict)

#for Real RUN
i_dict =  run_RT_temperature(  ) 
run_HT_time_temperature(  i_dict = i_dict )


# Mingxin
#for TEST
tt0, i_dict = run_melting_Tm(   TH=29.2,  Tm = 25 , TH_sleep_time = 10  ) 
run_Tm( tt0, i_dict, Tm=29, exposure_t = 0.1, t_total_T40 = 30, t_interval = 3 ) 
run_melting( Trange = [ 29, 29.1 ], dtemp = 0.1, exposure_t = 0.2,  sleep_time_per_dtemp  = 1  ) 


#for REAL
tt0, i_dict = run_melting_Tm(   TH=29.2,  Tm = 25 , TH_sleep_time = 10  ) 
run_Tm( tt0, i_dict, Tm=29, exposure_t = 0.1, t_total_T40 = 30, t_interval = 3 ) 
run_melting( Trange = [ 29, 29.1 ], dtemp = 0.1, exposure_t = 0.2,  sleep_time_per_dtemp  = 1  ) 





'''



def run_HT_time_temperature( T =  45, t_interval=10*60, t_total = 31*60, exposure_t = 0.1 , i_dict = None  ):
    '''      
    
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: goes to temperature T, then for a set duration repeatedly visits every sample
    #   on the bar (a fresh map spot each pass) and takes a SAXS image (stamping temperature/elapsed
    #   time into the name), spacing passes by t_interval, then returns to room temperature.
    #
    # ⚠️ WORTH FIXING (about how it runs): the heater command, moves and measurements use  RE(...)
    #   INSIDE the while/for loops, so each is a SEPARATE run and you can't pause/resume the series.
    #   To make it ONE plan, use 'yield from' instead of 'RE(...)' (the RE_run_HT_time_temperature
    #   twin below already does this) and launch it once.
    #
    # 💡 NEWER, EASIER WAY: holding a temperature and measuring over time is the smi_plans
    #   isothermal_kinetics_run; it holds the temperature and records temperature/time into each image.
    # === end smi_plans note ================================================
    #step one 
    #set Temperature 
    if i_dict is None:
        i_dict = {}
        for  k  in ks:
            i_dict[k] = 0
    RE( gotoT( T ) ) 
    t0 = time.time()
    while (time.time() < ( t0 + t_total ) ):
        t1 = time.time()
        for  k  in ks:             
            mov_sam( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                    N, i_dict[k], sample_dict[k], k ))
            RE(bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ))
            RE(bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ))
            sample = RE.md['sample']
            RE(measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-t0 ) ))
            i_dict[k]+=1
        if   ( t_interval + ( t1 - time.time() ) ) < 0:
            pass
        else:
            time.sleep(  t_interval + ( t1 - time.time() )  )

    Tr = 25 
    print( i_dict )
    RE( setT(Tr)    ) 
    RE( stopT() ) 
    return i_dict
   





def run_RT_temperature(   exposure_t = 0.1 , i_dict = None  ):
    '''  
    
    run_RT_temperature(   exposure_t = 0.1 , i_dict = None  ) ) 


    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at room temperature, visits each sample on the bar (a fresh map spot per sample
    #   from getSamMap) and takes one SAXS image, keeping a per-sample spot counter (i_dict).
    #
    # ⚠️ WORTH FIXING (about how it runs): this moves and measures with  RE(bps.mv(...))  and
    #   RE(measure_saxs(...))  INSIDE the for loop, so each is a SEPARATE run. To make it ONE plan,
    #   use 'yield from' instead of 'RE(...)' (the RE_run_RT_temperature twin below already does this).
    #
    # 💡 NEWER, EASIER WAY: visiting a fresh spot per sample on a bar is the smi_plans transmission_bar
    #   (or map_grid_run per sample):
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from transmission_bar("RT", samples, t=exposure_t, dets=[pil2M])
    # === end smi_plans note ================================================
    #step one 
    #set Temperature 
    if i_dict is None:
        i_dict = {}
        for  k  in ks:
            i_dict[k] = 0
    for  k  in ks:             
        mov_sam( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        RE( bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ))
        RE( bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ) )
        sample = RE.md['sample']
        RE( measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() ) ) 
        #measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-t0 ) )

        i_dict[k]+=1
    print( i_dict )    
    return   i_dict







def run_melting_Tm(   TH=50, exposure_t = 0.2 , Tm = 44 , TH_sleep_time = 1800 ):
    ''' 38 - 48, 0.1 0C/min 
    
    tt0, i_dict = run_melting_Tm(   TH=29.2,  Tm = 25 , TH_sleep_time = 10  ) 


    '''  
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a melting prep — measures each sample at room temperature, heats to a high
    #   temperature (TH), holds, measures each sample again, then sets the melting temperature (Tm)
    #   and starts the heater (returns a timer and the per-sample spot counter for run_Tm).
    #
    # ⚠️ WORTH FIXING (about how it runs): the moves, heater commands and measurements use  RE(...)
    #   INSIDE the for loops, so each is a SEPARATE run. To make it ONE plan, use 'yield from' instead
    #   of 'RE(...)' (the RE_run_melting_Tm twin below already does this).
    #
    # 💡 NEWER, EASIER WAY: a temperature melt/anneal with measurements is the smi_plans temperature
    #   run (temperature_ramp_run / isothermal_kinetics_run with a sample bar).
    # === end smi_plans note ================================================
    i_dict = {}
    for  k  in ks:
        i_dict[k] = 0
    #at RT, measure each sample at the starting point
    for  k  in ks:             
        mov_sam( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        RE( bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ) )
        RE( bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ) )
        sample = RE.md['sample']
        RE( measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() ) )
        i_dict[k]+=1

    #raise temperature to 50C
    RE(gotoT( TH ))
    #wait for 30mins
    time.sleep( TH_sleep_time  )
    #measure each sample again at the end of 50C
    for  k  in ks:             
        mov_sam( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        RE(bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ))
        RE( bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ) )
        sample = RE.md['sample']
        RE( measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() ) ) 
        i_dict[k]+=1
    #set temperature to 40C
    tt0 = time.time() #Tr = 40
    RE(setT(Tm)   )
    RE( startT() )
    return tt0, i_dict
     
#  RE( gotoT( Tm ))

def run_Tm(   tt0, i_dict,  Tm, exposure_t = 0.2 ,t_total_T40 =  30 * 60, t_interval = 5 * 60 ,   ):
    '''
    run_Tm( tt0, i_dict, Tm=29, exposure_t = 0.1, t_total_T40 = 30, t_interval = 3 ) 
    
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the isothermal-kinetics part of a melt — goes to the melting temperature (Tm)
    #   and, for a set duration, repeatedly visits each sample and takes a SAXS image (stamping
    #   temperature/elapsed time into the name), spacing passes by t_interval.
    #
    # ⚠️ WORTH FIXING (about how it runs): the moves, heater commands and measurements use  RE(...)
    #   INSIDE the while/for loops, so each is a SEPARATE run and you can't pause/resume the kinetics
    #   run. To make it ONE plan, use 'yield from' instead of 'RE(...)' (the RE_run_Tm twin below
    #   already does this).
    #
    # 💡 NEWER, EASIER WAY: a hold-at-temperature-and-watch run is exactly smi_plans'
    #   isothermal_kinetics_run; it holds the temperature and records temperature/time into each image.
    # === end smi_plans note ================================================


    RE(  gotoT( Tm ) ) 
    t0 = time.time()    
    while (time.time() < ( t0 + t_total_T40 ) ):
        t1 = time.time()
        for  k  in ks:             
            mov_sam( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                    N, i_dict[k], sample_dict[k], k ))
            RE ( bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ) ) 
            RE(  bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ) ) 
            sample = RE.md['sample']
            RE( measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-tt0 ) )            )
            i_dict[k]+=1

        if  (t_interval + ( t1 - time.time() )) > 0:
            time.sleep(  t_interval + ( t1 - time.time() )  )
    Tr = 25 
    RE( setT(Tr)   )
    RE(  stopT() ) 
    

  


def run_melting( Trange = [ 38, 48 ], dtemp = 0.1, exposure_t = 0.2, sleep_time_per_dtemp  = 60   ):
    ''' 38 - 48, 0.1 0C/min 
    
    run_melting( Trange = [ 29, 29.1 ], dtemp = 0.1, exposure_t = 0.2,  sleep_time_per_dtemp  = 1  ) 

    run_melting( Trange = [ 38, 48 ], dtemp = 0.2, exposure_t = 0.1, sleep_time_per_dtemp  = 60)

    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a slow melting ramp — steps the temperature from T1 to T2 in 'dtemp' increments,
    #   waiting 'sleep_time_per_dtemp' at each step, and measures every sample on the bar at each step.
    #
    # ⚠️ WORTH FIXING (about how it runs): the heater commands, moves and measurements use  RE(...)
    #   INSIDE the for loops, so each is a SEPARATE run. To make it ONE plan, use 'yield from' instead
    #   of 'RE(...)' (the RE_run_melting twin below already does this).
    #
    # 💡 NEWER, EASIER WAY: a fine temperature ramp with a measurement at each step is the smi_plans
    #   temperature_ramp_run (build the temperatures with np.arange and pass a sample bar as an axis).
    # === end smi_plans note ================================================
    #step one 
    #set Temperature
    T1, T2 = Trange
    tlist = np.arange( T1, T2, dtemp )
    i_dict = {}
    for  k  in ks:
        i_dict[k] = 0
    #i = 0 
    t0 = time.time()
    for T in tlist:     
        RE( gotoT( T ) ) 
        time.sleep( sleep_time_per_dtemp )
        for  k  in ks:             
            mov_sam( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                 N, i_dict[k], sample_dict[k], k ))
            RE( bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  ))
            RE( bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  ) ) 
            sample = RE.md['sample']
            RE( measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() ) ) 
            i_dict[k]+=1
    Tr = 25 
    RE (setT(Tr)       )
    RE( stopT()      ) 









def RE_run_melting( Trange = [ 38, 48 ], dtemp = 0.1, exposure_t = 0.2  ):
    ''' 38 - 48, 0.1 0C/min 
    
    RE( run_melting( Trange = [ 29, 29.1 ], dtemp = 0.1, exposure_t = 0.2  ) ) 


    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the same slow melting ramp as run_melting, but written the GOOD way — ONE plan
    #   built with 'yield from', so you launch the whole ramp with a single RE(RE_run_melting()) and
    #   can pause/resume it. Nice — this is the style smi_plans encourages.
    # 💡 HEADS-UP (a tiny thing): the measurement line below reads  measure_saxs( exposure_t, ... )
    #   without 'yield from'. Since measure_saxs is itself a plan, that line builds the recipe but
    #   never runs it, so no image is taken — write  'yield from measure_saxs( exposure_t, ... )'.
    # 💡 NEWER, EASIER WAY: the whole routine is one line with smi_plans' temperature_ramp_run.
    # === end smi_plans note ================================================
    #step one 
    #set Temperature
    T1, T2 = Trange
    tlist = np.arange( T1, T2, dtemp )
    i_dict = {}
    for  k  in ks:
        i_dict[k] = 0
    #i = 0 
    t0 = time.time()
    for T in tlist:     
        yield from gotoT( T )
        for  k  in ks:             
            mov_sam_re( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                 N, i_dict[k], sample_dict[k], k ))
            yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
            yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
            sample = RE.md['sample']
            measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() )
            i_dict[k]+=1
    Tr = 25 
    yield from setT(Tr)       
    yield from stopT()     





def RE_run_Tm(  tt0, i_dict, Tm,  exposure_t = 0.2 ,t_total_T40 =  3 * 60 * 60, t_interval = 5 * 60 ,   ):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the isothermal-kinetics part of a melt, written the GOOD way — ONE plan built
    #   with 'yield from' (launch with a single RE(RE_run_Tm(...)) and you can pause/resume).
    # 💡 HEADS-UP: the  measure_saxs( exposure_t, ... )  line below is missing 'yield from', so as
    #   written no image is taken — write  'yield from measure_saxs( exposure_t, ... )'.
    # 💡 NEWER, EASIER WAY: this hold-at-Tm-and-watch run is exactly smi_plans' isothermal_kinetics_run.
    # === end smi_plans note ================================================
    yield from gotoT( Tm )
    t0 = time.time()    
    while (time.time() < ( t0 + t_total_T40 ) ):
        t1 = time.time()
        for  k  in ks:             
            mov_sam_re( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                    N, i_dict[k], sample_dict[k], k ))
            yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
            yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
            sample = RE.md['sample']
            measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-tt0 ) )            
            i_dict[k]+=1
        time.sleep(  t_interval + ( t1 - time.time() )  )
    Tr = 25 
    yield from setT(Tr)   
    yield from stopT()

def RE_run_melting_Tm(   TH=50, exposure_t = 0.2 , Tm = 44 , TH_sleep_time = 1800 ):
    ''' 38 - 48, 0.1 0C/min 
    
    RE( run_melting_Tm(   TH=50, exposure_t = 0.2 , Tm = 44 , TH_sleep_time = 1800 ) ) 


    '''  
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the melting-prep (RT measure -> heat to TH -> hold -> measure -> set Tm),
    #   written the GOOD way — ONE plan built with 'yield from' (launch once with RE(RE_run_melting_Tm())).
    # 💡 HEADS-UP: the  measure_saxs( exposure_t, ... )  lines below are missing 'yield from', so as
    #   written no image is taken — write  'yield from measure_saxs( exposure_t, ... )'.
    # 💡 NEWER, EASIER WAY: a temperature melt/anneal with measurements is the smi_plans temperature
    #   run (temperature_ramp_run / isothermal_kinetics_run with a sample bar).
    # === end smi_plans note ================================================
    i_dict = {}
    for  k  in ks:
        i_dict[k] = 0
    #at RT, measure each sample at the starting point
    for  k  in ks:             
        mov_sam_re( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
        yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
        sample = RE.md['sample']
        measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() )
        i_dict[k]+=1


    #raise temperature to 50C
    yield from gotoT( TH )
    #wait for 30mins
    time.sleep( TH_sleep_time  )
    #measure each sample again at the end of 50C
    for  k  in ks:             
        mov_sam_re( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
        yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
        sample = RE.md['sample']
        measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() )
        i_dict[k]+=1
    #set temperature to 40C
    tt0 = time #Tr = 40
    yield from setT(Tm)   
    yield from startT()
    return tt0, i_dict


def RE_run_HT_time_temperature( T =  45, t_interval=10*60, t_total = 31*60, exposure_t = 0.1 , i_dict = None  ):
    '''      
    RE(  ) 
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hold-at-temperature time series (go to T, then repeatedly measure the bar for
    #   a set duration), written the GOOD way — ONE plan built with 'yield from' (launch once).
    # 💡 HEADS-UP: the  measure_saxs( exposure_t, ... )  line below is missing 'yield from', so as
    #   written no image is taken — write  'yield from measure_saxs( exposure_t, ... )'.
    # 💡 NEWER, EASIER WAY: holding a temperature and measuring over time is the smi_plans
    #   isothermal_kinetics_run.
    # === end smi_plans note ================================================
    #step one 
    #set Temperature 
    if i_dict is None:
        i_dict = {}
        for  k  in ks:
            i_dict[k] = 0
    yield from gotoT( T )
    t0 = time.time()
    while (time.time() < ( t0 + t_total ) ):
        t1 = time.time()
        for  k  in ks:             
            mov_sam_re( k )
            pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
            N = len( pos_list )
            print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                    N, i_dict[k], sample_dict[k], k ))
            yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
            yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
            sample = RE.md['sample']
            measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-t0 ) )

            
            i_dict[k]+=1
        time.sleep(  t_interval + ( t1 - time.time() )  )

    Tr = 25 
    print( i_dict )
    yield from setT(Tr)   
    yield from stopT()
    return i_dict
   


def RE_run_RT_temperature(   exposure_t = 0.1 , i_dict = None  ):
    '''  
    
    RE(   run_RT_temperature(   exposure_t = 0.1 , i_dict = None  ) ) 


    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the room-temperature bar (a fresh spot per sample), written the GOOD way — ONE
    #   plan built with 'yield from' (launch once with RE(RE_run_RT_temperature())).
    # 💡 HEADS-UP: the  measure_saxs( exposure_t, ... )  line below is missing 'yield from', so as
    #   written no image is taken — write  'yield from measure_saxs( exposure_t, ... )'.
    # 💡 NEWER, EASIER WAY: visiting a fresh spot per sample on a bar is the smi_plans transmission_bar.
    # === end smi_plans note ================================================
    #step one 
    #set Temperature 
    if i_dict is None:
        i_dict = {}
        for  k  in ks:
            i_dict[k] = 0
    for  k  in ks:             
        mov_sam_re( k )
        pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
        N = len( pos_list )
        print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
                N, i_dict[k], sample_dict[k], k ))
        yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
        yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
        sample = RE.md['sample']
        measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() )
        #measure_saxs( exposure_t, sample= sample + '_T_%.2f'%getT() + '_runt_%.0fs'%(time.time()-t0 ) )

        i_dict[k]+=1
    print( i_dict )    
    return   i_dict
   




# def run_one_temperature( T =  [ 'T0', 45, 'T0C' ] ,  exposure_t = 0.1  ):
#     '''  
    
#     RE(  ) 


#     '''
#     #step one 
#     #set Temperature 
#     i_dict = {}
#     for  k  in ks:
#         i_dict[k] = 0
#     #i = 0 
#     T0 =  getT()
#     for   T in Tlist:     
#         if T == 'T0':
#             pass
#         elif T == 'T0C':
#             yield from gotoT( T0 )
#         else:
#             yield from gotoT( T )
#         for  k  in ks:             
#             mov_sam_re( k )
#             pos_list = getSamMap( xlim = lim_dict[k][0], ylim = lim_dict[k][1] )
#             N = len( pos_list )
#             print( 'There are %s points available (Cur: %s-th spot) for this sample at pos=%s: %s'%(
#                  N, i_dict[k], sample_dict[k], k ))
#             yield from bps.mv( piezo.x,  pos_list[i_dict[k]%N][0]  )
#             yield from bps.mv( piezo.y,  pos_list[i_dict[k]%N][1]  )
#             measure_saxs( exposure_t, sample=  RE.md['sample'] )
#             i_dict[k]+=1
#     Tr = 25 
#     yield from setT(Tr)       
#     yield from stopT()     




def Measure_All():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience driver — builds a map with getSamMap and measures it with
    #   Measure_Map (which calls the beamline with RE() internally).
    # 💡 NEWER, EASIER WAY: smi_plans' map_grid_run does a labelled raster in one line (recording
    #   position/beam into each image), and you launch the whole thing as one plan with RE(...).
    # === end smi_plans note ================================================



    ps4 =  getSamMap(  xlim=[-16760,-16760+10], ylim=[3371,  1500 ],  step_size = [100, -50], rot_angle = 0 )
    Measure_Map( sample ='0126TTH_cappilary1',  ps= ps4   ) 



def Check_All():

    ps1 = getSamMap(xlim=[4500, 8500], ylim=[-4390, 610 ] )
    ps2 = getSamMap(xlim=[-14000, -8500], ylim=[ -4520, -1100 ] )
    ps3 = getSamMap(xlim=[-24800,-21100], ylim=[-4630,  -330] )
    N = len(ps1) + len(ps2) + len(ps3)
    print( N, N/3600 )

 




def getSamMap(  xlim=[4500, 8500], ylim=[-4390, 610 ],  step_size = [200, 30], rot_angle = 0 ):
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





def Measure_Map(  t = 1 ,  sample = 'O139',  ps=None, pz= 8000,  username = 'FLu', ):
    '''
    Ps = getSamMap()
    Measure_Map( sample = 'test',  ps= Ps[:2]   ) 
    
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a micro-focus raster — for every (x, y) point in 'ps' it moves there and takes
    #   one SAXS+WAXS image (and optionally writes the live OAV camera frame).
    #
    # ⚠️ WORTH FIXING (about how it runs): this moves and measures with  RE(bps.mov(...))  and
    #   RE(bp.count(...))  INSIDE the for loop, so EVERY point is a SEPARATE run — a big map becomes
    #   thousands of tiny runs and you can't pause/resume the map. The modern way is ONE coordinated
    #   grid scan; smi_plans' map_grid_run does exactly that.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' map_grid_run rasters in one line, records position/beam INTO
    #   each image, and names the files for you (no hand-built '{sample}_x..._y...'):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(sample, piezo.x, x0, x1, nx, piezo.y, y0, y1, ny, t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it). (internal: Tier 0.)
    # === end smi_plans note ================================================

    RE(bps.mov( piezo.z, pz  ))
    if ps is None:
        ps = getSamMap( )
    for (px,py) in ps:
        print( px, py )
        RE(bps.mov( piezo.x, px  ))
        RE(bps.mov( piezo.y, py  ))
        dets = [pil2M, pil900KW]
        name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_expt{t}s"
        sample_name = name_fmt.format(
            sample=sample,
            x=np.round(piezo.x.position, 2),
            y=np.round(piezo.y.position, 2),
            z_pos=piezo.z.position,
            saxs_z=np.round(pil2M_pos.z.position, 2),
            t=t,
            #scan_id=RE.md["scan_id"],
        )
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans map runs set exposure for you via t=.)
        # sample_name='test'
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        print("Collect data here....")
        RE(  bp.count(dets, num=1) ) 
        if camera:
            #path= '/nsls2/xf12id2/data/images/users/2022_3/308052_YZhang/OAV/'
            #caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FilePath', path ) 
            caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FileName', sample_name  )
            caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:WriteFile', 1 )       





from epics import caget, caput

def set_fs5(   ):
    #path= '/nsls2/xf12id2/data/images/users/2022_3/308052_YZhang/OAV/'
    path= '/nsls2/data/smi/legacy/results/data/2024_1/313760_FLu/OAV/'
    caput( 'XF:12IDC-BI{Cam:SAM}TIFF1:FilePath', path ) 




 




def get_current_time():
    return datetime.today().strftime("%Y-%m-%d-%H-%M-%S")



def measure_current_sample(t=1, waxs_angles=[0, 20], sample=None):

    """t0=time.time();RE(measure_one_multi_angle_wsaxs());run_time(t0)"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: measures the current sample at several WAXS arc angles — SAXS+WAXS at the
    #   widest angle, WAXS-only at the others. (Built the GOOD way with 'yield from', so it's one plan.)
    # 💡 NEWER, EASIER WAY: sweeping the WAXS arc is one axis in smi_plans:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(sample, [pil2M, pil900KW], [motor_axis("wa", waxs, [0, 20])])
    # === end smi_plans note ================================================
    maxA = np.max(waxs_angles)
    for waxs_angle in waxs_angles:
        print("here we go ... ")
        if waxs_angle == maxA:
            yield from measure_wsaxs(t=t, waxs_angle=waxs_angle, sample=sample)
        else:
            yield from measure_waxs(t=t, waxs_angle=waxs_angle, sample=sample)


def measure_saxs(t=1, att="None", dx=0, dy=0, user_name=username, sample=None):

    """RE( measure_saxs( sample = 'AgBH_12keV' ) )"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one transmission SAXS image of the current sample, building the file name
    #   from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run does this in one line and records the
    #   position / detector distance / beam straight INTO the data and into the file name for you:
    #     from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M])
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================

    if sample is None:
        # sample = RE.md['sample']
        sample = RE.md["sample_name"]
    dets = [pil2M]
    if dy:
        yield from bps.mvr(piezo.y, dy)
    if dx:
        yield from bps.mvr(piezo.x, dx)
    name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_det{saxs_z:05.2f}m_expt{t}s"


    sample_name = name_fmt.format(
        sample=sample,
        x=np.round(piezo.x.position, 2),
        y=np.round(piezo.y.position, 2),
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2M_pos.z.position, 2),
        t=t,
        #scan_id=RE.md["scan_id"],
    )
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans transmission_run sets it for you via t=.)
    # sample_name='test'
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    #sample_id(user_name="test", sample_name="test")
    #RE.md["sample_name"] = ''
    #RE.md["sample"] = ''


def measure_waxs(
    t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=username, sample=None
):
    """ 
    RE(  measure_waxs() )  # take default parameters

    RE( measure_waxs( t = 1, waxs_angle = 0   ) )


    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS arc to a given angle and takes one WAXS image of the current
    #   sample, building the file name from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run takes the WAXS detector and records the arc
    #   angle / position / beam straight INTO the data and names the files for you:
    #     from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil900KW])   # set the WAXS arc as you do now
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================

    if sample is None:
        sample = RE.md["sample"]
        # sample = RE.md['sample_name']
    yield from bps.mv(waxs, waxs_angle)
    #dets = [pil900KW, pil300KW]
    dets = [pil900KW]

    # att_in( att )
    if dx:
        yield from bps.mvr(piezo.x, dx)
    if dy:
        yield from bps.mvr(piezo.y, dy)
    #name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s"
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_det{saxs_z}_waxs{waxs_angle:05.2f}_expt{expt}s"

    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2M_pos.z.position, 2),
        waxs_angle=waxs_angle,
        expt=t,
        #scan_id=RE.md["scan_id"],
    )
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans transmission_run sets it for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    # sample_id(user_name='test', sample_name='test')

    #RE.md["sample_name"] = ''
    #RE.md["sample"] = ''


def measure_wsaxs(
    t=1, waxs_angle=20, att="None", dx=0, dy=0, user_name=username, sample=None
):
    """RE( measure_wsaxs( sample = 'AgBH_12keV' ) )"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes BOTH a SAXS and a WAXS image of the current sample at a given WAXS arc
    #   angle, building the file name from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run takes both detectors and records the arc /
    #   position / beam straight INTO the data and names the files for you:
    #     from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M, pil900KW])   # set the WAXS arc as you do now
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================

    if sample is None:
        # sample = RE.md['sample']
        sample = RE.md["sample_name"]
    yield from bps.mv(waxs, waxs_angle)
    #dets = [pil900KW, pil300KW, pil2M]
    dets = [pil900KW,   pil2M]

    if dx:
        yield from bps.mvr(piezo.x, dx)
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_det{saxs_z}_waxs{waxs_angle:05.2f}_expt{expt}s"

    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2M_pos.z.position, 2),
        waxs_angle=waxs_angle,
        expt=t,
        #scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans transmission_run sets it for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    # sample_id(user_name='test', sample_name='test')
    #RE.md["sample_name"] = ''
    #RE.md["sample"] = ''


def measure_series_multi_angle_wsaxs(
    t=[1], waxs_angles=[0,  20   ], dys=[0]
):

    """
    
    t0=time.time();RE(measure_series_multi_angle_wsaxs(waxs_angles=[0,  20   ]));run_time(t0)

    

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a multi-sample bar at several WAXS arc angles — for each angle it visits every
    #   sample and takes SAXS+WAXS (at the widest angle) or WAXS-only (at the others). Built the GOOD
    #   way with 'yield from', so it's one plan you launch once.
    # 💡 NEWER, EASIER WAY: this is a transmission bar with a WAXS-arc axis:
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from transmission_bar("series", samples, t=t[0], dets=[pil2M, pil900KW])  # sweep the arc as an axis
    # === end smi_plans note ================================================

    ks = list(sample_dict.keys())  # [:8 ]
    maxA = np.max(waxs_angles)
    for waxs_angle in waxs_angles:
        for k in ks:
            print(k)
            yield from mov_sam_re(k)
            for dy in dys:
                print(dy)
                print("here we go ... ")
                for ti in t:
                    RE.md["sample_name"] = sample_dict[k]
                    if waxs_angle == maxA:
                        yield from measure_wsaxs(
                            t=ti, waxs_angle=waxs_angle, att="None", dy=dy
                        )
                    else:
                        yield from measure_waxs(
                            t=ti, waxs_angle=waxs_angle, att="None", dy=dy
                        )



def measure_series_saxs(t=[1]):

    """
    t0=time.time();RE(measure_series_saxs());run_time(t0)
    
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS bar — visits every sample on the bar and takes a SAXS image (one plan,
    #   built with 'yield from').
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=sample_list, x=x_list, y=y_list)
    #     yield from transmission_bar("saxs", samples, t=t[0], dets=[pil2M])
    # === end smi_plans note ================================================



    ks = list(sample_dict.keys())  # [:8 ]    
    dy = -50
    for k in ks:
        print(k)
        dy=0
        yield from mov_sam_re(k, dy=0)
        for ii, ti in enumerate(t):
            RE.md["sample_name"] = sample_dict[k]
            yield from measure_saxs(t=ti, att="None", dy=dy)



def run_time(t0):
    dt = (time.time() - t0) / 60
    print("The Running time is: %.2f min." % dt)



def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick WAXS snapshot (a "test" image) of whatever is in the beam.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run("test", t=t, dets=[pil900KW]) does this and
    #   sets the exposure for you. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t,t )' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t,t )  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick SAXS snapshot (a "test" image) of whatever is in the beam.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run("test", t=t, dets=[pil2M]) does this and sets
    #   the exposure for you. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t,t )' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    'test '
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t,t )  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def mov_sam(pos, dy=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience "go to sample N" — moves x/y to that sample's bar position and
    #   records the sample name in RE.md.
    # 💡 NOTE: this uses  RE(bps.mv(...))  so it can only be called from the prompt, NOT from inside
    #   another plan (calling RE() inside a running plan errors). The 'mov_sam_re' twin uses
    #   'yield from bps.mv(...)' and IS safe to use inside a plan — prefer that when composing.
    #   In smi_plans, 'goto_sample(samples, "name")' does this move (and records it) for you.
    # === end smi_plans note ================================================
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px))
    RE(bps.mv(piezo.y, py + dy))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample
    RE.md["sample_name"] = sample





def name_sam(pos):
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample
    RE.md["sample_name"] = sample


def check_sample_loc(sleep=1):
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        time.sleep(sleep)


def movx(dx):
    RE(bps.mvr(piezo.x, dx))

def movy(dy):
    RE(bps.mvr(piezo.y, dy))

def get_posxy():
    return round(piezo.x.user_readback.value, 2), round(piezo.y.user_readback.value, 2)

def move_waxs(waxs_angle=8.0):
    RE(bps.mv(waxs, waxs_angle))


def measure_pindiol_current():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the fast shutter briefly, reads the pin-diode current, closes the shutter,
    #   and returns the reading (a quick beam/transmission check).
    # 💡 NEWER, EASIER WAY: smi_plans records the pin-diode reading straight into the data during a
    #   transmission_run, so you usually don't need to read it by hand. (Nothing here is broken.)
    # === end smi_plans note ================================================
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr


def check_sample_name(name):
    """
    Convert special characters to underscore so detectors will not complain
    """
    name = name.translate({ord(c): "_" for c in "=!@#$%^&*{}:/<>?\|`~+"})
    return name


#########End of the functions


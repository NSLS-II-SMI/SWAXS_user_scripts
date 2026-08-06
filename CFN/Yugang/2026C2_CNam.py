'''
pas =319371
saf: 319099


proposal_swap(319371)
project_set('microbeam_Kim')


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

'''
2026C1 3/26
change from air to vaccum
16.1 kev, 5 meter, 



procedures
1) close the beam
    RE(shclose())
2)  RE(vent_waxs())  #####click  "Vent WAXS Sample Chamber" on the CSS screen
3) Open the hutch 
    a) Press SBE Access button
    b) Press Open button
4) Open the chamber when 1:WAXS 2:TCG:9 is about 780-800, 
5) load sample holder on the piezo moter stage
6) close chamber
7) RE(pump_waxs())  #####Click "Auto Evacution" on the CSS screen
8) Search/Close  hutch
    a) press SB1, SB2, SB3 sequentially
    b) press front left button
    c) press close (continuous press)
    d) press SBE Access button
9) find sample pos X and y using camera on the CSS screen
9.5) visually update sample name and X position 
    username = 'TZhu'
    user_name =  'TZhu'
    sample_dict = {   1: 'S1',  2: 'S2',   } 
    pxy_dict = {    1:[  55000, 0 ] ,   2: [ 45000,  0 ]    }
# 10) Open gate valve
#     wait until "B1:WAXS" LED turn green  
#     click "2GV-7 Valve" 


11) restart WAXS detector
    RE(startWAXS())
12) Open the beam 
    RE(shopen())
13) Change beam configure to alignment mode 
    RE(smi.modeAlignment())
14) load macro
    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C2_CNam.py

15) check sample height

   mov_sam(1)     
   sample_id(user_name='test', sample_name=f'test{get_scan_md()}')
   RE(bp.count([ pil2M ]  ,num=1))
   manually change the Piezo Y (or Hexapod Y) --> to determine the H (ypos)   # if the thickness of the samples are similar, then just use the first sample to define ypos

16) Reload this micro (python file)
    save this py file by Ctrl + s
    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_CNam.py

17) do alignment
    Aligned_Dict =     align_gix_loop_samples(   ) 

18) Do measurement
    RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))





'''


#BEAMSTOP_X = 6.55


# username = 'PGuo'
# user_name = 'PGuo'
# username = 'Bowen'
# user_name =  'Bowen'
# #########Change Sample name here
# sample_dict = {   1: 'MAPbBr_RE', 2: 'MAPbI_RE',   } 
# sample_dict = {   1: 'MAPbBr_CON', 2: 'MAPbI_CON',   } 
# pxy_dict = {    1:[ -7000 - 300, 8820 ] , 2: [ 1000 - 300, 8820  ]    }



# username = 'CM'
# user_name =  'CM'
# sample_dict = {   1: '4gF',  2: '4gS', 3: '4CF', 4: '4CS', 5: 'CD131', 6: 'CD101',  } 
# pxy_dict = {      1:[  -47400, 23321] ,   2: [ -34900, 23621  ], 3: [ -19900, 23821  ], 4: [ 10600, 24321  ],
#             5: [ 29100, 25021  ], 6: [ 46100, 25421  ] ,      }


# ypos = 8000#7200 #8000
# xpos = 40000
# username = 'TZhu'
# user_name =  'TZhu'
# sample_dict = {   1: 'S12',  2: 'S13', 3: 'S14',   4: 'S15', 5: 'S16',  6: 'S17', 7: 'S18', 8:  'S19', 9: 'S20', } 
# pxy_dict = {    1:[  53600, 0 ] ,   2: [ 41600,  0 ] , 3: [29800, 0 ],  4: [16600, 0], 5: [800, 0 ], 6: [-9000, 0 ],  
#              7: [ -19000, 0 ], 8: [ -29000, 0 ], 9: [ -41400, 0 ],  }   

# ypos = 8000#7200 #8000
# xpos = 40000
# username = 'CNam'
# user_name =  'CNam'
# sample_dict = {   1: 'S1_1',  2: 'S1_2', 3: 'S1_3',   4: 'S1_4', 5: 'S1_5',  6: 'S1_6', 7: 'S1_7',  } 
# pxy_dict = {    1:[  52400, 0 ] ,   2: [ 36600,  0 ] , 3: [22000, 0 ],  4: [7000, 0], 5: [-8000, 0 ], 6: [-24000, 0 ],  
#              7: [ -41000, 0 ],    } 

# ypos = 8000#7200 #8000
# xpos = 40000
# username = 'CNam'
# user_name =  'CNam'
# sample_dict = {   1: 'S2_1',  2: 'S2_2', 3: 'S2_3',   4: 'S2_4', 5: 'S2_5',  6: 'S2_6', 7: 'S2_7', 8: 'S2_8', 9: 'S2_9', 10: 'S2_10', 11: 'S2_11', 12: 'S2_12',} 
# pxy_dict = {    1:[  56000, 0 ] ,   2: [ 47000,  0 ] , 3: [37000, 0 ],  4: [28000, 0], 5: [19000, 0 ], 6: [11000, 0 ],  
#              7: [ 0, 0 ],  8: [ -9000, 0 ], 9: [ -17500, 0 ], 10: [ -26000, 0 ], 11: [ -34500, 0 ], 12: [ -44000, 0 ],  } 

ypos = 0
xpos = 0
username = 'CNam'
user_name =  'CNam'
sample_dict = {   1: 'AgBH'  }  #PZ = 8400
pxy_dict = {    1:[ -48000, 4380 ]   } 
 

ypos = 1960 # -1900#8000#7200 #8000
xpos = 0
username = 'Kim'
user_name =  'Kim'
# sample_dict = {   1: 'InON_9',  2: 'InON_10', 3: 'InON_11', 4: 'InON_12', 5: "InON_13", 6: "InON_14", 7: "InON_15",
#                8: 'InON_16', 9: 'InON_17', 10: 'InON_18', 11: 'InON_19', 12: 'InON_20', 13: 'InON_21'}  

# pxy_dict = {    1:[  47740, 0 ] ,   2: [ 40700,  0 ] , 3: [33740, 0 ],  4: [26740, 0], 5: [19740, 0 ], 6: [11740, 0 ],  
#              7: [ 2740, 0 ],  8: [ -12759, 0 ], 9: [ -19759, 0 ], 10: [-27259, 0 ], 11: [ -33959, 0 ], 12: [ -41959, 0 ],
#                13: [ -49459, 0]} 

#sample_dict = {   1: 'InON_9',  2: 'InON_10', 3: 'InON_11', 4: 'InON_12', 5: "InON_13", 6: "InON_14", 7: "InON_15",
#               8: 'InON_16', 9: 'InON_17', 10: 'InON_18'}  

#pxy_dict = {    1:[  47740, 0 ] ,   2: [ 40700,  0 ] , 3: [33740, 0 ],  4: [26740, 0], 5: [19740, 0 ], 6: [11740, 0 ],  
#             7: [ 2740, 0 ],  8: [ -12759, 0 ], 9: [ -19759, 0 ], 10: [-27259, 0 ]} 

## InON_22 and 23 is on the top
## InON_8 is on the bottom
## Huber Stage was at X=33
## When working on final 6 InON and Starting EUV samples, had to move Z by more than 5mm, something strange with the stage

#sample_dict = {   1: 'InON_8'}  

#pxy_dict = {    1:[  44500, 0 ]} 

# sample_dict = {   1: 'EUV_14',  2: 'EUV_15', 3: 'EUV_16', 4: 'EUV_17', 5: "EUV_18", 6: "EUV_19", 7: "EUV_20",
#                 8: 'EUV_21', 9: 'EUV_22', 10: 'EUV_23'}

# pxy_dict = {    1:[  36867, 0 ] , 2: [ 28867,  0 ] , 3: [20867, 0 ], 4: [12867, 0], 5: [3867, 0 ], 6: [-14132, 0 ],  
#                 7: [ -22132, 0 ],  8: [ -31132, 0 ], 9: [ -39132, 0 ], 10: [-47132, 0 ]}

# sample_dict = { 1: 'EUV_16', 2: 'EUV_17', 3: "EUV_18", 4: "EUV_19", 5: "EUV_20",
#                 6: 'EUV_21', 7: 'EUV_22', 8: 'EUV_23'}

# pxy_dict = {    1: [20867, 0 ], 2: [12867, 0], 3: [3867, 0 ], 4: [-14132, 0 ],  
#                 5: [ -22132, 0 ],  6: [ -31132, 0 ], 7: [ -39132, 0 ], 8: [-47132, 0 ]}

# sample_dict = { 1: 'InON_24', 2: 'InON_25', 3: "InON_26", 4: "InON_27", 5: "InON_28",
#                 6: 'InON_29'}

# pxy_dict = {    1: [50500, 0 ], 2: [44500, 0], 3: [37500, 0 ], 4: [32500, 0 ],  
#                 5: [ 26000, 0 ],  6: [ 21000, 0 ]}

# sample_dict = { 1: 'EUV_1', 2: 'EUV_2', 3: "EUV_3", 4: "EUV_4", 5: "EUV_5",
#                 6: 'EUV_6', 7: 'EUV_7', 8: 'EUV_8', 9: 'EUV_9', 10: 'EUV_10',
#                 11: 'EUV_11', 12: 'EUV_12', 13: 'EUV_13', 14: 'EUV_14', 15: 'EUV_15'}

# pxy_dict = {    1: [14000, 0 ], 2: [7500, 0], 3: [1500, 0 ], 4: [4000, 0 ],  
#                 5: [-14000, 0 ],  6: [-20000, 0 ], 7: [-27000, 0], 8: [-33500, 0],
#                 9: [-40000, 0 ], 10: [-46000, 0]}

sample_dict = { 1: 'EUV_12', 2: 'EUV_13'
                }

pxy_dict = {    1: [-42660, 0 ], 2: [-48160, 0 ]
                }



ypos = 0
xpos = 0
username = 'CFN' 
sample_dict = {   1: 'AgBH'  }  #PZ = 8400
pxy_dict = {    1:[ 0, 0  ]   } 


 
#sample_dict = {   1: 'EUV_16',  2: 'EUV_17'}
#pxy_dict = {    1:[  20867, 0 ] , 2: [ 28867,  0 ]}

#sample_dict = {   1: 'InON_1', 2: 'InON_2', 3: 'InON_3', 4: 'InON_4', 5: 'InON_5', 6: 'InON_6', 7: 'InON_7'}  
#pxy_dict = {    1: [21250, 0 ], 2: [ 11850, 0 ], 3: [ 1850, 0], 4: [-14150, 0], 
#               5: [-24150, 0], 6: [-34150, 0], 7: [-44650, 0] } 



#sample_dict = {   1: 'HZO_1',  2: 'HZO_2', 3: 'HZO_3',   4: 'HZO_4', 5: 'HZO_5', }  
#pxy_dict = {    1:[  34000, 0 ] ,   2: [ 32400,  0 ] , 3: [30800, 0 ],  4: [29100, 0], 5: [27450, 0 ]} 

#Aligned_Dict = { 0: {'th': -0.333759 , 'y': -1982.675  },
#                 1: {'th': -0.336329  , 'y': -1989.229  },
#                 2: {'th': -0.333759 , 'y': -1982.675  },      
#                3: {'th': -0.333759 , 'y': -1982.675  },  
#                4: {'th': -0.337962 , 'y': -2009.73  },         
#     } #the Device


# Aligned_Dict = { 0: {'th': -0.225  , 'y': -2050.8  },
#                  1: {'th':  -0.281449  , 'y':  -2085.733 },
#                  2: {'th': -0.325903  , 'y': -2254.445  },      
#                 3: {'th': -0.175437   , 'y': -2202.62  },  
#                 4: {'th': -0.277466 , 'y': -2254.289  },                 
#                 5: {'th': -0.24729 , 'y': -2309.596    },
#                 6: {'th': -0.240219 , 'y': -2357.436   }        
#      } #the InON_1st

# Aligned_Dict = { 0: {'th': 0.267272  , 'y': 2058.971  },    
#                 1: {'th': 0.0436229  , 'y': 2070.757 },    
#                 2: {'th': -0.024425  , 'y': 2064.423  },         
#                 3: {'th': -0.035114  , 'y': 2036.304  },     
#                 4: {'th': 0.021637 , 'y': 2011.025  },                    
#                 5: {'th': 0.12433 , 'y': 1985.759    },    
#                 6: {'th': 0.022111 , 'y': 1981.373   },     
#                 7: {'th': -0.00777 , 'y': 1972.089 }
                  
#      } #the InON_2nd

#Aligned_Dict = { 0: {'th': 1.0650 , 'y': 1811.938  },    
#                  1: {'th': 0.05542  , 'y': 1855.338 },    
#                  2: {'th': 0.697309 , 'y': 1783.7  },         
#                  3: {'th': 0.367562 , 'y': 1770.662  },     
#                  4: {'th': 0.529349 , 'y': 1711.598  }
#                }

#Aligned_Dict = { 0: {'th': -0.131053  , 'y': -2441.997  },    #InON_21
#the InON_2nd
#Aligned_Dict = { 0: {'th': 0.092694  , 'y': 2091.569  }, 1: {'th': 0.060312, 'y': 2094.722}}

# sample_dict = {   1:   'InON_7'}  

# pxy_dict = {    1:   [-44650, 0] } 


#print('def sample location here...')

ks = np.array(list((sample_dict.keys())))#  [5:5]
pxy_dict = {  k: [ pxy_dict[k][0] - xpos, pxy_dict[k][1] + ypos    ]  for k in ks  }
#print('def sample location here 2...')
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 4 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 5 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 2600   ]  for k in  [ 10 ]  } ) 
# #pxy_dict.update( {  k: [ pxy_dict[k][0], 2200   ]  for k in  [ 5, 6, 7 ]  } )

x_list = np.array(  [  pxy_dict[k][0] for k in ks   ]     )
y_list = np.array(  [  pxy_dict[k][1] for k in ks   ]     )
#y_list = np.array(list((pxy_dict.values()))) [:, 1]  
sample_list = np.array( [  sample_dict[k] for k in ks ] ) 


#print('def sample location here 2...')

#Aligned_Dict=align_gix_loop_samples( ii_start = 2)


#y_list = np.array(list((pxy_dict.values())))[:, 1] 
#print( x_list, y_list )

def align_gix_loop_samples( inc_ang = 0.1, ii_start = -1   ):      
    '''      
    Aligned_Dict =     align_gix_loop_samples(   )  
    #  0.48 -0.384     

     '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks the sample bar and runs the grazing-incidence alignment on each
    #   one (from a chosen start index), remembering each sample's theta/y, then switches the
    #   beam back to measurement mode and parks the beamstop.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has align_sample, which aligns a sample and saves the
    #   result with the data; the GIWAXS bar helpers (giwaxs_bar) can align each sample as they
    #   go (align=align_sample), so you don't keep a separate alignment dictionary by hand.
    #   (Good news: this file already uses the modern beamstop name 'pil2M.beamstop.x_rod' —
    #   that part is up to date.)
    # 💡 HEADS-UP (not broken): this calls RE(...) inside the loop, so it can't itself be
    #   'yield from'-ed or run with RE(...). In smi_plans the alignment is a plan you
    #   'yield from', so it composes with the rest of your scan. (internal: Tier 0.)
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
    #pil2M.beamstop.x_rod.set( BEAMSTOP_X  )
    print('THe alignment is DOne!!!')
    return Aligned_Dict





 
print('here@@@@@@@@@@')
def run_gix_loop_wsaxs(t=5, mode = [ 'waxs', 'saxs' ],  
                       angle_arc = np.array([ 0.05, 0.1, 0.15, 0.2,  0.3,  ]),
                       waxs_angle_array = np.array( [    0,  20,  40    ] ) ,  
                       #x_shift_array = [0], #np.linspace(-1, 1, 5),  
                       x_shift_array =  np.array( [ -500, 0, 500 ]), #np.linspace(-1, 1, 5),                      
                       Aligned_Dict = None ):        
       
    '''      
      #RE( run_gix_loop_wsaxs()) 


      Aligned_Dict=align_gix_loop_samples();
      RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))



    '''    
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the main GISAXS bar run — for each WAXS-arc angle it picks the right
    #   detectors, then for each sample (at its aligned angles from Aligned_Dict) sweeps a few
    #   x-spots and incident angles, taking an image at each.
    #
    # 💡 NEWER, EASIER WAY: this "for each sample on the aligned bar, sweep incident angle and
    #   WAXS arc" pattern is the 'smi_plans' giwaxs_bar. It walks the bar (aligning each sample
    #   if you pass align=align_sample), sweeps incident angle and WAXS arc, and records the
    #   angle / x / y / WAXS-position / beam into each image and file name (so you can drop the
    #   long hand-built "{sample}_{th}deg_x..." name):
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, motor_axis, align_sample
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     yield from giwaxs_bar(
    #         bar, t=t, dets=[pil2M, pil900KW], align=align_sample,
    #         incident_angles=[0.05, 0.1, 0.15, 0.2, 0.3],     # your angle_arc
    #         arc=motor_axis("waxs", waxs, [0, 20, 40]))       # your waxs_angle_array
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    print( 'step--0' )
    yield from det_exposure_time( t,t  )
    #yield from smi.modeMeasurement() 
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'     
    if Aligned_Dict is None:    
        Aligned_Dict = align_gix_loop_samples( inc_ang = 0.15 )  
    
    print( Aligned_Dict )  
    M, _, _ = get_motor(   )  
    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     
        dets = get_dets( waxs_angle = waxs_angle, mode = mode )                       
        det_exposure_time(t,t)                  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
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
                    det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing (and here it's after the image, so it wouldn't have affected that frame). Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans sets exposure up front via t=.)
            #print( 'HERE#############')
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).



def align_Linkam_sample():   
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the single sample on the Linkam hot-stage, remembers its theta/y,
    #   switches the beam back to measurement mode, and parks the beamstop.
    # 💡 In 'smi_plans' this is align_sample (a plan you 'yield from' that also saves the
    #   alignment with the data). 💡 HEADS-UP: this version uses RE(...), so it can't be
    #   'yield from'-ed. (Already uses the modern 'pil2M.beamstop.x_rod' name — good.) (Tier 0.)
    # === end smi_plans note ================================================
    Aligned_Dict= {}                   
    RE( alignment_gisaxs( 0.15  ) ) #run alignment routine          
    M, TH, YH = get_motor(  )   
    ii = 0   
    Aligned_Dict[ii]={}
    Aligned_Dict[ii]['th']  = TH
    Aligned_Dict[ii]['y']  = YH
    print( ii, TH, YH ) 
    RE( smi.modeMeasurement() ) 
    #pil2M.beamstop.x_rod.set( BEAMSTOP_X )

    return    Aligned_Dict


def _run( Aligned_Dict, 
         sample_name = 'xxx',
         mode = [ 'waxs' ],  
        angle_arc = np.array([  0.15  ]),
         waxs_angle_array = np.array( [  0     ] ) ,   ):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the shared inner worker for the Linkam temperature runs — at the aligned
    #   spot it sweeps WAXS arc and incident angle and takes an image at each, baking the
    #   temperature into the file name.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the temperature, angle, and position are recorded
    #   straight INTO the data and templated into the file name, so this whole hand-built
    #   "{sample}_{th}deg_..._T{lt}c_..." name and the per-point loop become one giwaxs_run /
    #   temperature run. (See Temperature_Linkam_Step's note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
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
            det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing (and here it's after the image). Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans sets exposure up front via t=.)
            #print( 'HERE#############')
    RE.md['sample_name'] = 'test'
    RE.md['sample'] = 'tes'


def collect_data_atT(T, Aligned_Dict, sample_name = 'xxx', angle_arc = np.array([  0.15  ]),
         waxs_angle_array = np.array( [  0     ] )  ):
    '''

        pass-318527 PGuo [6]: Aligned_Dict
        Out[6]: 
        {0: {'th': -0.9841789999999999, 'y': 9010.856},
        1: {'th': -0.9421309999999999, 'y': 9129.465}}

 
    
    collect_data_atT( 20, Aligned_Dict, sample_name = 'BAI_n1', angle_arc = np.array([  0.05, 0.1, 0.15, 0.3   ]),
         waxs_angle_array = np.array( [  0,      ] )  )

    
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: ramps the Linkam to temperature T, waits to reach it, then runs one
    #   measurement pass (_run) at that temperature.
    # 💡 NEWER, EASIER WAY: "go to a temperature, settle, then measure" is the 'smi_plans'
    #   goto_temperature + a giwaxs/transmission run (or temperature_ramp_run for a whole
    #   ramp). The real temperature is recorded into the data for you. 💡 HEADS-UP: this runs
    #   the measurement with RE(_run(...)) inside the function, so it can't be 'yield from'-ed.
    #   (internal: Tier 0.)
    # === end smi_plans note ================================================

    #print('step...0 ')
    LThermal.setTemperature(   T   )
    LThermal.on() # turn on 

    while abs( LThermal.temperature() - T )  > .5 :            
        time.sleep( 3 ) 
    RE( _run( Aligned_Dict, sample_name = sample_name,
        mode = [ 'waxs' ], angle_arc = angle_arc, 
        waxs_angle_array = waxs_angle_array,   ) ) 
    


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
    # WHAT THIS DOES: a Linkam temperature step series — measures the aligned sample at a
    #   ladder of temperatures going down (TH->TL), then back up (TL->TH).
    # 💡 NEWER, EASIER WAY: stepping temperature and measuring at each setpoint is the
    #   'smi_plans' temperature_ramp_run (or a goto_temperature loop); it goes to each setpoint,
    #   settles, measures, and records the real temperature into the data and file name:
    #     from smi_plans import temperature_ramp_run
    #     yield from temperature_ramp_run(sample_name, np.linspace(TH, TL, Tnum),
    #                                     t=exp_time, dets=[pil900KW])
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ line.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
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
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    LThermal.off()
    RE.md["sample_name"] = 'test'




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
    # WHAT THIS DOES: a fast three-temperature Linkam protocol — heats to T1, then while
    #   ramping toward T2 keeps measuring, then while ramping toward T3 keeps measuring (an
    #   in-situ temperature-kinetics run).
    # 💡 NEWER, EASIER WAY: "ramp temperature and keep measuring" is the 'smi_plans'
    #   isothermal_kinetics_run / temperature_ramp_run family; they drive the temperature and
    #   re-measure on a cadence, recording the real temperature/time into the data. 💡 HEADS-UP:
    #   this takes data with RE(_run(...)) inside the loops, so it can't be 'yield from'-ed.
    #   (internal: Tier 0.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
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
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    LThermal.off()
    RE.md["sample_name"] = 'test'




def set_T( T ):
    # smi_plans: setup helper (ramps the Linkam toward T) — nothing to migrate. In smi_plans
    # the temperature is driven by goto_temperature / temperature_ramp_run inside a plan.
    lt = LThermal.temperature()
    LThermal.setTemperature( T )
    LThermal.on()
    print(f'Temperature is changing from {lt:.2f} to {T:.2f}...')
    #LThermal.off()    

def turn_off_T(  ):
    # smi_plans: setup helper (turns the Linkam controller off) — nothing to migrate.
    LThermal.off()   
    print(f'Linkam Temperature controller is off...')
    #    

# angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
#                        waxs_angle_array = np.array( [  0,   15 , 20    ] ) ,  
#                        x_shift_array =  np.array( [ -2000, -1000, 0, 1000, 2000 ]), #np.linspace(-1, 1, 5),                      
#                        Aligned_Dict = None ):       
    



def run_linkam_samples_oneT(  Aligned_Dict,   angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                     waxs_angle_array = np.array( [  0, 15, 20     ] ) ,  
                    x_shift_array = np.array( [ -1500, -1000, 0, 1000, 1500 ]) ,  dets = [pil900KW] , t= 1   ):  

    '''

    Aligned_Dict =   align_gix_loop_samples()      
    
    RE( run_linkam_samples_oneT(  Aligned_Dict  ) ) 
    

    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at the current (held) temperature, walks the bar of samples; for each it
    #   sweeps incident angle and a few x-spots and takes a WAXS image, baking the temperature
    #   into the file name.
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' giwaxs_bar with the temperature recorded
    #   into the data (e.g. inside a temperature run). It records angle / x / temperature /
    #   beam into each image and file name, so the long hand-built name goes away:
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, motor_axis
    #     bar = SampleList.from_columns(name=list(sample_dict.values()), x=...)
    #     yield from giwaxs_bar(bar, t=t, dets=[pil900KW],
    #                           incident_angles=[0.05, 0.1, 0.15, 0.3, 0.6],
    #                           arc=motor_axis("waxs", waxs, [0, 15, 20]))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ line.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
    # === end smi_plans note ================================================
    #set_T(T)
    #time.sleep( 60 )


    y_shift_array = np.array( [  0  ])
    username = user_name
    align= False 
    camera = False #True 
    CTS = 0   
    M, _, _ = get_motor(   )   
    det_exposure_time(t,t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
    ks = list( sample_dict.keys() ) 
    t0 = time.time()
    #RE.md['sample_name'] = sample_name
    #RE.md['sample'] = sample_name
     

    for waxs_angle in waxs_angle_array: # loop through waxs angles        
        yield from bps.mv(waxs, waxs_angle)     

        for ii, k in enumerate(ks): #loop samples
            x = pxy_dict[k][0]
            sample = sample_dict[k] 
            sample_name = sample_dict[k] 
            RE.md['sample_name'] = sample 
            RE.md['sample'] = sample 

            yield from bps.mv(M.x, x) #move to next sample              
            TH = Aligned_Dict[ii]['th']  
            YH = Aligned_Dict[ii]['y']  
            yield from bps.mv(M.y, YH)  
            yield from bps.mv(M.th, TH)  
            th_meas = angle_arc + TH #piezo.th.position 
            th_real = angle_arc	 
            for i, th in enumerate(th_meas): #loop over incident angles
                yield from bps.mv(M.th, th)  
                lt = LThermal.temperature()      
                x_pos_array = x + x_shift_array                
                #y_pos_array = YH + y_shift_array
                for j, x_meas in enumerate( x_pos_array) : # measure at a few x positions
                    yield from bps.mv(M.x, x_meas)    
                    name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_T{lt:.2f}c_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
                    _sample_name = name_fmt.format(sample=sample_name,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,lt=LThermal.temperature(),saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,)
                        #scan_id=RE.md["scan_id"],                
                    sample_id(user_name=  user_name , sample_name=_sample_name)                     
                    print(f'\n\t=== Sample: {_sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
                    #det_exposure_time(t,t)    
                    #print( 'HERE#############')
        RE.md['sample_name'] = 'test'
        RE.md['sample'] = 'tes'


   



def insitu_fix_pos_angle(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ):  
    '''

    Aligned_Dict =   align_gix_loop_samples()          
    RE( insitu_fix_pos_angle(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ) ) 
    

    '''

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time series at fixed positions/angle — for up to run_time
    #   seconds it repeatedly visits each sample (at its aligned angle) and takes a WAXS image,
    #   so you watch each sample evolve over time.
    # 💡 NEWER, EASIER WAY: "keep revisiting these samples and measuring for a while" is the
    #   'smi_plans' kinetics/time-series pattern (giwaxs_bar wrapped in a time loop, or
    #   time_series_run); it timestamps each frame into the data. 💡 HEADS-UP: this loops in
    #   plain Python with time.sleep — smi_plans expresses the timed repeat as one runnable
    #   plan. (Nothing broken here; detectors already use pil900KW.) (internal: Tier 1.)
    # === end smi_plans note ================================================

    t=1
    dets = [pil900KW ]
    incident_angle=[      0.1   ]  
    angle_arc = np.array( incident_angle )
    x_shift_array = np.array( [ 0 ]) #25000 #
    y_shift_array = np.array( [  0  ])

    username = user_name
    align= False 
    camera = False #True
    waxs_angle = 0

    CTS = 0   
    M, _, _ = get_motor(   )   

    ks = list( sample_dict.keys() ) 
    t0 = time.time()
    while (time.time() - t0 ) < run_time:
        print('The CTS is %s ************ '%CTS)
         
        for ii, k in enumerate(ks): #loop samples
            x = pxy_dict[k][0]
            sample = sample_dict[k] 
            sample_name = sample_dict[k] 
            

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
                    lt = LThermal.temperature()      

                    yield from bps.mv(M.x, x_meas)    
                    name_fmt = "{sample}_{th:5.4f}deg_x{x:05.2f}_y{y:05.2f}_z{z_pos:05.2f}_T{lt:.2f}c_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
                    _sample_name = name_fmt.format(sample=sample_name,th=th_real[i],x=np.round(M.x.position, 2),y=np.round(M.y.position, 2), z_pos=M.z.position,lt=LThermal.temperature(),saxs_z=np.round(pil2m_pos.z.position, 2), waxs_angle=waxs_angle,t=t,)
                        #scan_id=RE.md["scan_id"],                
                    sample_id(user_name=  user_name , sample_name=_sample_name)                     
                    print(f'\n\t=== Sample: {_sample_name} ===\n') 
                    yield from bp.count( dets, num=1)
             

        CTS +=1
        time.sleep(  sleep_time  )
 





def insitu_tgix_samples(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ):  

    '''

    Aligned_Dict =   align_gix_loop_samples()      
    
    RE( insitu_tgix_samples(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ) ) 
    

    '''


    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time series on the bar with SAXS+WAXS — for up to run_time
    #   seconds it repeatedly visits each sample, sweeps a few x-spots at the aligned angle,
    #   and takes an image, watching the samples evolve.
    # 💡 NEWER, EASIER WAY: same 'smi_plans' kinetics/time-series pattern as insitu_fix_pos_angle
    #   (giwaxs_bar on a timer, or time_series_run); it timestamps each frame and records the
    #   position into the data and file name. 💡 HEADS-UP: loops in plain Python with time.sleep.
    #   (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
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
                    det_exposure_time(t,t)    # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing (and here it's after the image). Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans sets exposure up front via t=.)
                    if camera: 
                        save_ova( sample_name )
                        save_hex( sample_name )     

        CTS +=1
        time.sleep(  sleep_time  )
 



def run_giwaxs_Kim(t=1, username=username):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks the whole bar; at each sample it aligns, then sweeps WAXS-arc
    #   angle, x-spots, and incident angle, taking a GISAXS/WAXS image at every combination
    #   (alternating the arc direction each sample to save time).
    # 💡 NEWER, EASIER WAY: this "for each sample: align, then sweep incident angle + WAXS arc"
    #   pattern is the 'smi_plans' GIWAXS-bar helper. giwaxs_bar_arc_economy alternates the arc
    #   direction (like the inverse_angle flag here), aligns each sample (align=align_sample),
    #   and records angle / x / WAXS-position / beam into each image and file name:
    #     from smi_plans import giwaxs_bar_arc_economy, SampleList, incidence_axis, motor_axis, align_sample
    #     bar = SampleList.from_columns(name=list(sample_list), x=list(x_list))
    #     yield from giwaxs_bar_arc_economy(
    #         bar, t=t, dets=[pil2M, pil900KW], align=align_sample,
    #         incident_angles=[0.05, 0.08, 0.10, 0.15, 0.2, 0.3], arc=motor_axis("waxs", waxs, [7, 27, 47]))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.) (Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (rayonix only appears in old comments here.)
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

        yield from alignment_gisaxs(0.1)  # run alignment routine
        th_meas = angle_arc + piezo.th.position
        th_real = angle_arc
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
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
                dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). (pil900KW is already in this list.)

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
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).



#def alignment_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1):



def temp_series_grid(name='temp',
                     temps = np.linspace(32,26,13),
                     exp_time=1, 
                     hold_delay=120, 
                     dets=[pil2M], 
                     xs=np.linspace(-13,-12,11), 
                     ys=np.linspace(-2.3,-2.8,6)):
       # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at every (x, y) point on a grid it steps the Linkam through a list of
    #   temperatures, equilibrating and taking a SAXS image at each.
    # 💡 NEWER, EASIER WAY: 'smi_plans' can do the temperature ramp at each grid point and
    #   record the real temperature / energy / x / y into the data and file name (so you can
    #   drop the hand-built name and the 'target_file_name' Signal):
    #     from smi_plans import temperature_ramp_run
    #     for xp in xs:
    #         for yp in ys:
    #             yield from bps.mv(stage.x, xp, stage.y, yp)
    #             yield from temperature_ramp_run("temp", np.linspace(32, 26, 13),
    #                                             t=exp_time, dets=[pil2M], settle=hold_delay)
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ line.) (Tier 3.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
    # NOTE for staff: the sample-name line further down references 'ais', 'bpm', and 'T_start'
    #   which aren't defined in this function, so it looks like it would error — smi_plans
    #   builds the file name from recorded fields, which avoids that.
    # === end smi_plans note ================================================

    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' temperature_ramp_run sets it for you via t=.)

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
                #sample_name = sample_name.translate({ord(c): "_" for c in  "})
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=0, xbpm="%4.3f"%bpm,temp = "%3.2f"%T_start)

                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'







def GIWAXS_TD_run():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature-dependent GIWAXS run on three samples — aligns them warm,
    #   measures WAXS, cools to a series of temperatures (re-checking alignment), and measures
    #   WAXS at each, recording the temperature and beam reading in the file name.
    # 💡 NEWER, EASIER WAY: this combination of "align each sample, ramp the Linkam, and measure
    #   WAXS at each temperature" is what 'smi_plans' composes from temperature_ramp_run +
    #   giwaxs_run with align_sample. align_sample saves the alignment, the temperature run
    #   drives + settles the Linkam, and the temperature / angle / beam are recorded into each
    #   image and file name for you. (See the smi_plans recipes_combined module for ready-made
    #   GIWAXS+temperature recipes.)
    # 💡 HEADS-UP (not broken): this is already fairly modern (one bp.count per point, file
    #   name from recorded fields). Two small things for staff: the cold-temperature loop checks
    #   'temperature' which isn't defined here (looks like it should be 'T'), and the WAXS-arc
    #   "walk back in" is a stack of mv+sleep steps that smi_plans would express as one arc move.
    #   (internal: Tier 2.)
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

        yield from alignment_gisaxs_hex(0.15)
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

        yield from alignment_gisaxs_hex(0.15)
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





###########for Transmission
print( 'load transmission here')
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
    





def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0,  20, 40   ], 
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

                       
            






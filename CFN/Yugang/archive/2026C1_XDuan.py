'''

20260404, Saturday

pas =319679
saf: 318453

[xf12id@xf12id2-ws1 ~]$ sync-experiment -b smi  -p 319679
Username : yuzhang
Password : 

Authenticated as : u:BNL yuzhang
Started experiment pass-319679 by yuzhang.
[xf12id@xf12id2-ws1 ~]$ bsui


proposal_swap(319679)
project_set('XDuan')
project_set('XDuan_LT')

Home Hexpod
on the terminal 
[xf12id@xf12id2-ws1 ~]$ telnet 10.67.90.125 6543
Trying 10.67.90.125...
Connected to 10.67.90.125.
Escape character is '^]'.
HP430 HOMR
stageY OFF -476
Start

--> Y is 135






change from Air to Vacuum
1) close 2:GV-7
2) physically open the vavle
3) remove the window
4) physically close the vavle


SAXS: 2M ,5 meter
16.1 kev, low-divergency, in vaccum
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_XDuan.py

su yuzhang
for run jupyter
[yuzhang@xf12id2-ws1 2026-1]$ ssh -NL 8888:localhost:8888 yuzhang@xf12id2-srv1
#[yuzhang@xf12id2-ws1 2026-1]$ ssh -vvv -NL 8888:localhost:8888 yuzhang@xf12id2-srv1



The data is saved in:
/nsls2/data1/smi/proposals/2026-1/pass-319679/projects/XDuan/user_data

Python Codes in:
/home/xf12id/SWAXS_user_scripts/CFN/Yugang/
Copied here:
cd /nsls2/data1/smi/proposals/2026-1/pass-319679/Script
cp -rp /home/xf12id/SWAXS_user_scripts/CFN/Yugang/ .


## Setup Linkam in Vacuum
Connection
main controler:
1) connect to the small computer upstream of the chamber by a instrumention USB cable (white)
2) connect to the LN controller by a pin cable from instrument (middle one) to any of two ports of LN controller
3) connect the pin data/control cable to a pin connector in the another fitthrough port 
, pass the fitthrough 
4) pass the two LN tubings throught the main port in the fitting pad to the chamber and do clamps (two)
5) connect the tubing from LN controller to another small port in the fitting pad
6) connect the two LN tubings to the Linkam stage (GI can be direct mounted onto the piezo motor)
7) start both the main controller and the LN controller
8) restart the IOC, There is a CSS  XF:12ID-ES{LINKAM}:SysReset, click reboot now


Put the YAG bar in to check the beam
Sum 0.625, 0.625
quadEM: 0.857, 0.857 
put OnAxis Camera, 0.0005, 
VFM: 2.89; 

Data collection:
1) Direct beam, put atten, move beamstop off
1.5) Piezo motor, x,y,z for the AgBH sample on the new cal holder --> [ -30000, -2800, 8100 ]
1.6) the Hexpod is in a wired status, after doing the 
        HP430 HOMR
        stageY OFF -476
        Start
        --> Y = 135.3, and all other are 0 

2) saxs beamstop: X  6.8, Y 10 
3) move det to 5 meter
4) do the direct beam again, 


1) Do saxs/waxs on the AgBH sample--> t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)


RE(smi.modeAlignment())
Aligned_Dict =     align_gix_loop_samples(   )
RE(smi.modeMeasurement())
RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))


RE(smi.modeAlignment());
Aligned_Dict=align_gix_loop_samples();
RE(smi.modeMeasurement());
RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))


# Do LN2
project_set('XDuan_LT')

Add more LN2
put four samples on the stage
BZ1, BZ4, HT1, YL12a






2026C1 3/26
change from air to vaccum
16.1 kev, 5 meter, 



procedures
1) RE(shclose())
2) click Vent WAXS Sample Chamber
3) Open the hutch
4) open the chamber
5) load sample holder on the piezo moter stage
6) close chamber
7) Click Auto Evacution
8) Search/Close  hutch
9) find sample pos X and y
10) wait until B1:WAXS LED turn green from yellow to open 2GV-7 Valve
11) RE(startWAXS())
12) RE(shopen())
13) RE(smi.modeAlignment())
14) sample_id(user_name='test', sample_name=f'test{get_scan_md()}')
15) using the combination of 
   RE(bp.count([ pil2M ]  ,num=1))
   manually change the Piezo Y (or Hexapod Y) --> to determine the H
   manually change the Piezo X --> to determine the sample X   
16) chagne the sample names and follow step 15 to find good x and y
    username = 'CM'
    user_name =  'CM'
    sample_dict = {   1: 'JM_B',  2: 'JM_A',   } 
    pxy_dict = {    1:[  10500, 24197] ,   2: [ -11300, 24197  ]    }

17) Save then Load this micro (python file)
%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C1_PGuo.py
18 do alignment
    Aligned_Dict =     align_gix_loop_samples(   )

    #Aligned_Dict = {0: {'th': -2.366813, 'y': 24150.836}, 1: {'th': -3.209889, 'y': 24072.714}}

19) Do measurement
    RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))

    A) we did  RT measurement for all the 20 samples with arc from 0 to 15, 20, and 40,
      but looks like we did not do gisaxs; we measured 3 locations for each sample
    B) for LT, we did RT, then to 200K, 100K, (some point the LN is used up and vaccum is bad, so 
    it stopped), in the next morning, run RT for all the four samples, with arc from  from 0 to 15, 20, and 40,
    and gisaxs; measure one spot for all

    




'''


BEAMSTOP_X = 6.8 #6.55



# username = 'PGuo'
# user_name = 'PGuo'
# username = 'Bowen'
# user_name =  'Bowen'
# #########Change Sample name here
# sample_dict = {   1: 'MAPbBr_RE', 2: 'MAPbI_RE',   } 
# sample_dict = {   1: 'MAPbBr_CON', 2: 'MAPbI_CON',   } 
# pxy_dict = {    1:[ -7000 - 300, 8820 ] , 2: [ 1000 - 300, 8820  ]    }



username = 'XD'
user_name =  'XD'
sample_dict = {   1: 'AgBH'   } 
pxy_dict = {      1:[ -30000, -2800]       }


username = 'UCLA'
user_name =  'UCLA'

sample_dict = {   1: 'BZ_S1',  2: 'BZ_S2', 3: 'BZ_S3', 4: 'BZ_S4',                
                  5: 'CL_S1',  6: 'CL_S2', 7: 'CL_S3', 8: 'CL_S4', 
                  9: 'HT_S1',  10: 'HT_S2', 11: 'HT_S3',
                  12: 'YL_S12_a',  13: 'YL_S12_b', 14: 'YL_S12_c',
                  15: 'YL_S34_a',  16: 'YL_S34_b', 17: 'YL_S34_c' ,   
                  18: 'YL_S56_a',  19: 'YL_S56_b', 20: 'YL_S56_c' ,  
                    } 

pxy_dict = {      1:[  -53861,  0] ,   2:[ -49568,  0] , 3: [-45568.5, 0  ]  ,
            4: [ -39168.36, 0], 5: [ -32168, 0], 6: [-27568.1, 0], 7: [-22868.0, 0], 8: [-17968.0, 0],
              9: [-12467.9, 0], 10: [-6167.9, 0], 11: [-167.9, 0], 12: [5832.4, 0],
                13: [11832.8, 0], 14: [17832.9, 0], 15: [24033.3, 0], 16: [29733.3, 0], 
                17: [33833.3, 0], 18: [39833.3, 0], 19: [45333.5, 0], 20: [50033.5, 0]}




sample_dict = {   1: 'BZS1',  2: 'BZS4', 3: 'HT1', 4: 'YL12a'    } 

pxy_dict = {      1:[  2300.5,  0] ,   2:[ -2899.8,  0] , 3: [ -8899.9, 0  ]  ,  4: [ -13700, 0],  }




Y0 = 2000

#pxy_dict = {  k: [ pxy_dict[k][0], Y0   ]  for k in pxy_dict  }
#ks = np.array(list((sample_dict.keys())))
#sample_list = np.array(list((sample_dict.values())))

Y0 = 1500

#ks = [ 15, 16, 17, 18, 19,20 ] #[ 9, 10, 11 ] 

ks = np.array(list((sample_dict.keys())))
pxy_dict = {  k: [ pxy_dict[k][0], Y0   ]   for k in ks  } 


x_list = np.array(list((pxy_dict.values()))) [:, 0]
y_list = np.array(list((pxy_dict.values()))) [:, 1] #+ Y0
sample_list = np.array(list((sample_dict.values())))
#sample_list = np.array( ks )

#pxy_dict = {  k: [ pxy_dict[k][0], Y0   ]  for k in pxy_dict  }


# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 4 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 1725   ]  for k in  [ 5 ]  } ) 
# pxy_dict.update( {  k: [ pxy_dict[k][0], 2600   ]  for k in  [ 10 ]  } ) 
# #pxy_dict.update( {  k: [ pxy_dict[k][0], 2200   ]  for k in  [ 5, 6, 7 ]  } )

# Aligned_Dict = {
#     0: {'th': 1.264616, 'y': 1888.29},
#     1: {'th': 1.264623, 'y': 1838.047},
#     2: {'th': 1.313334, 'y': 1792.064},
#     3: {'th': 1.455387, 'y': 1692.106},
#     4: {'th': 1.492821, 'y': 1600.24},
#     5: {'th': 1.235385, 'y': 1513.596},
#     6: {'th': 1.466154, 'y': 1402.821},
#     7: {'th': 1.936404, 'y': 1348.117},
#     8: {'th': 1.292013, 'y': 1252.138},
#     9: {'th': 1.380729, 'y': 1150.187},
#     10: {'th': 1.558165, 'y': 986.936}
# }
# Aligned_Dict = {
#     0: {'th': 1.264616, 'y': 1888.29},
#     1: {'th': 1.264623, 'y': 1838.047},
#     2: {'th': 1.313334, 'y': 1792.064},
#     3: {'th': 1.455387, 'y': 1692.106},
#     4: {'th': 1.492821, 'y': 1600.24},
#     5: {'th': 1.235385, 'y': 1513.596},
#     6: {'th': 1.466154, 'y': 1402.821},
#     7: {'th': 1.936404, 'y': 1348.117},
#     8: {'th': 1.292013, 'y': 1252.138},
#     9: {'th': 1.380729, 'y': 1150.187},
#     10: {'th': 1.558165, 'y': 986.936},
#     11: {'th': 1.558159, 'y': 1027.207},
#     12: {'th': 1.462776, 'y': 951.91},
#     13: {'th': 1.626878, 'y': 872.78},
#     14: {'th': 1.535601, 'y': 787.465},
#     15: {'th': 1.420217, 'y': 693.373},
#     16: {'th': 0.952016, 'y': 646.264},
#     17: {'th': 1.291499, 'y': 561.51},
#     18: {'th': 1.475606, 'y': 417.479},
#     19: {'th': 1.422272, 'y': 430.164}
# }
#                                {0: {'th': 1.2920129999999999, 'y': 1252.138},
#  1: {'th': 1.3807289999999999, 'y': 1150.1870000000001},
#  2: {'th': 1.558165, 'y': 986.936}}

                                                                                
'''
pass-319679 XDuan_LT [271]: Aligned_Dict
Out[271]: 
{0: {'th': 0.570256, 'y': 1608.5230000000001},
 1: {'th': 0.698981, 'y': 1652.526},
 2: {'th': 0.9918049999999999, 'y': 1749.717},
 3: {'th': 0.483604, 'y': 1774.699}}

'''

#Aligned_Dict=align_gix_loop_samples( ii_start = 2)


#y_list = np.array(list((pxy_dict.values())))[:, 1] 
#print( x_list, y_list )

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
                RE( alignment_gisaxs(inc_ang  ) ) #run alignment routine          
            else:             
                RE( alignment_gisaxs_hex(inc_ang  ) ) #run alignment routine  
            M, TH, YH = get_motor(  )     
            Aligned_Dict[ii]={}
            Aligned_Dict[ii]['th']  = TH
            Aligned_Dict[ii]['y']  = YH
            print( ii, TH, YH )
            print('The current dict is: %s'% Aligned_Dict )
    RE( smi.modeMeasurement() ) 
    pil2M.beamstop.x_rod.set( BEAMSTOP_X  )
    print('THe alignment is DOne!!!')
    return Aligned_Dict




 
print('here@@@@@@@@@@')
def run_gix_loop_wsaxs(t=1, mode = [ 'waxs', 'saxs' ],  
                       angle_arc = np.array([ 0.05, 0.1,  0.15,  0.3, 0.6  ]),
                       waxs_angle_array = np.array( [    0 ,  15 , 20,  40    ] ) ,  
                       x_shift_array =  np.array( [ -500, 0, 500 ]), #np.linspace(-1, 1, 5),                      
                       Aligned_Dict = None ):        
       
    '''      
      #RE( run_gix_loop_wsaxs()) 


      Aligned_Dict=align_gix_loop_samples();
      RE(run_gix_loop_wsaxs(Aligned_Dict = Aligned_Dict))

      RE( run_gix_loop_wsaxs(t=1, mode = [ 'waxs'  ],  
                       angle_arc = np.array([   0.15 ]),
                       waxs_angle_array = np.array( [    0     ] ) ,  
                       x_shift_array =  np.array( [   0  ]),                    
                       Aligned_Dict  =  Aligned_Dict  ) ) 




    '''    
    print( 'step--0' )
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
    RE( alignment_gisaxs( 0.15  ) ) #run alignment routine          
    M, TH, YH = get_motor(  )   
    ii = 0   
    Aligned_Dict[ii]={}
    Aligned_Dict[ii]['th']  = TH
    Aligned_Dict[ii]['y']  = YH
    print( ii, TH, YH ) 
    RE( smi.modeMeasurement() ) 
    pil2M.beamstop.x_rod.set( BEAMSTOP_X )

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

        pass-318527 PGuo [6]: Aligned_Dict
        Out[6]: 
        {0: {'th': -0.9841789999999999, 'y': 9010.856},
        1: {'th': -0.9421309999999999, 'y': 9129.465}}

 
    
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




def run_Linkam_Tseries( Aligned_Dict, Ts = [  200, 100, 80, 100, 200, 300, 360    ]):

    '''
    run_Linkam_Tseries( Aligned_Dict )

    RE( run_linkam_samples_oneT(  Aligned_Dict,  
                                 angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                                 waxs_angle_array = np.array( [  0, 15, 20     ] ) ,  
                                x_shift_array = np.array( [     0  ]) , 
                                dets = [pil900KW, pil2M] , t= 1   )  )

    RE( run_linkam_samples_oneT(  Aligned_Dict,  
                                 angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                                 waxs_angle_array = np.array( [ 40   ] ) ,  
                                x_shift_array = np.array( [     0  ]) , 
                                dets = [pil900KW, pil2M] , t= 1   )  )
   
    
    '''


    # RE( run_linkam_samples_oneT(  Aligned_Dict,  
    #                              angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
    #                              waxs_angle_array = np.array( [  0, 15, 20     ] ) ,  
    #                             x_shift_array = np.array( [  -500,  0, 500   ]) , 
    #                             dets = [pil900KW, pil2M] , t= 1   )  )

    for T in Ts:        
        set_T( T )        
        print( f'Sleep 10 min here...')
        time.sleep(  20 * 60 ) #sleep 10 min 
        lt = LThermal.temperature()
        print( f'The current T is: {lt:.2f}')
        print( f'Start measure samples at this T: {lt:.2f}')
        RE( run_linkam_samples_oneT(  Aligned_Dict,  
                                 angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                                 waxs_angle_array = np.array( [  0, 15, 20, 40      ] ) ,  
                                #x_shift_array = np.array( [  -500,  0, 500   ]) , 
                                x_shift_array = np.array( [     0    ]) , 
                                dets = [pil900KW, pil2M] , t= 1   )  )
    
    set_T( 300 )
    turn_off_T()
        

         


def set_T( T ):
    T -=  273.15
    lt = LThermal.temperature()
    LThermal.setTemperature( T )
    LThermal.on()
    print(f'Temperature is changing from {lt:.2f} to {T:.2f}...')
    #LThermal.off()    

def turn_off_T(  ):
    LThermal.off()   
    print(f'Linkam Temperature controller is off...')
    #    

# angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
#                        waxs_angle_array = np.array( [  0,   15 , 20    ] ) ,  
#                        x_shift_array =  np.array( [ -2000, -1000, 0, 1000, 2000 ]), #np.linspace(-1, 1, 5),                      
#                        Aligned_Dict = None ):       
    



def run_linkam_samples_oneT(  Aligned_Dict,   angle_arc = np.array([ 0.05, 0.1, 0.15, 0.3, 0.6  ]),
                     waxs_angle_array = np.array( [  0, 15, 20     ] ) ,  
                    x_shift_array = np.array( [ -1500, -1000, 0, 1000, 1500 ]) , 
                      dets = [pil900KW] , t= 1   ):  

    '''

    Aligned_Dict =   align_gix_loop_samples()      
    
    RE( run_linkam_samples_oneT(  Aligned_Dict  ) ) 
    

    '''
    #set_T(T)
    #time.sleep( 60 )


    y_shift_array = np.array( [  0  ])
    username = user_name
    align= False 
    camera = False #True 
    CTS = 0   
    M, _, _ = get_motor(   )   
    det_exposure_time(t,t)  
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


                    if waxs_angle >15:
                        dets = [pil900KW, pil2M ]
                    else:
                        dets = [ pil900KW  ]

                    yield from bp.count( dets, num=1)
                    #det_exposure_time(t,t)    
                    #print( 'HERE#############')
        RE.md['sample_name'] = 'test'
        RE.md['sample'] = 'tes'


   



############################################################################
#Transimission  

def measure_transmission_xs(t=1, mode = ['saxs'], waxs_angle=20, att="None", dx=0, dy=0, user_name=None, sample=None, take_camera = False):
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
    



def measure_multi_waxs_loop_angles(  t= [1], waxs_angles=[0, 15, 20, 40   ], 
                                   dxs=[0], dys=[0], saxs_on=True ,
                                   user_name= user_name  ):
    """    
    t0=time.time();RE(measure_multi_waxs_loop_angles());run_time(t0)    

    """
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

                       


def insitu_fix_pos_angle(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ):  
    '''

    Aligned_Dict =   align_gix_loop_samples()          
    RE( insitu_fix_pos_angle(  Aligned_Dict,  run_time= 3600 * 1 , sleep_time = 1      ) ) 
    

    '''

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

        yield from alignment_gisaxs(0.1)  # run alignment routine
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
                #sample_name = sample_name.translate({ord(c): "_" for c in  "})
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=0, xbpm="%4.3f"%bpm,temp = "%3.2f"%T_start)

                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bp.count(dets + [s])

    LThermal.off()
    RE.md["sample_name"] = 'test'




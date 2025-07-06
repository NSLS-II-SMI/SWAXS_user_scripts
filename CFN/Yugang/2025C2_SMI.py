
#from YZhang_SMI_Base import *
####################################################################################
####Important:  Run this line first 
#  %run -i  ~/.ipython/profile_collection/startup/users/YZhang_SMI_Base.py
####################################################################################


#move rack to SMI morning, do inspection afternoon,  Fri, 2/24
#start the setup Sat, 2/25
# test macro, 2/25


#  %run -i  /home/xf12id/.ipython/profile_collection/startup/users/30-user-YZhang_SMI_Droplet_2024C1.py


# data folder

# /nsls2/data/smi/legacy/results/data/2024_1/313765_Zhang
#1M  900KW  Dropbox_Com  Dropbox_Com_BK  OAV  OAV_0225  Pipelines  Results  SMI_Beamline_BUSI  UV






# SMI: 2023/2/27
# SAF:    Standard
##  
# Energy: 16.1 keV, 0.77009 A, low divergence


# SAXS distance , 5 meter
# 1M [ 0.9, -61.4, 5000  ]
# beam stop [ 1.9, 288.99,  13  ], a rod
# beam center   [  490,  557    ]





 

#  beamstop_save()
#  setthreshold energy 16100 autog 11000




"""
2024/3/9: 10:30 AM
Change 16.1 kev from 14 kev from OPLS setup to low divergency in air
# Eliot did the alignment
# change the Pitch, Roll, WBS, SSA, QE-BPM2/3, mirror postions based on a previous screenshot
Problem with 1M
1) Power on/off
2) 
Restart camserver for Pilatus 300KW and Pilatus 1M:
For the 300kW: 	On a Terminal window: ssh -X det@xf12id2-det1 (pwd: Pilatus2)
For the 900KW: 	On a Terminal window: ssh -X det@xf12id2-det3 (pwd: Pilatus2)
For the 1M: 	On a Terminal window: ssh -X det@xf12id2-det2 (pwd: Pilatus2)
ssh -X det@xf12id2-det2-ppu
to see the status running do manage-iocs status
if is not running, do sudo manage-iocs start det2-camserver or det3-camserver

on the det@xf12id2-det2    run:   ./connect_camserver



for 1M, X = -4, 5meter, beam center [ 463, 561 ], beamstop  [ 1.7, 289, 13 ]
change X to 0.64 to make beam cetner as [ 490, 561 ]
beamstop_save()


proposal_id('2024_1', '313765_Zhang')  # For  2024/3/10
%run -i /home/xf12id/.ipython/profile_collection/startup/users/YZhang_SMI_Base.py
cd  /nsls2/data/smi/legacy/results/data/2024_1/313765_Zhang

mkdir Dropbox_Com;mkdir Dropbox_Com_BK;mkdir npz;mkdir OAV;mkdir Results;chmod 777 . -R
in the 
~/.ipython/profile_collection/startup/users/YZhang_SMI_Base.py
need to change the path for ova

# collect a data for AgBH
RE(collect_wsaxs( sample ='AgBH', waxs_angle = 15 ))


# for MDrive

Res: 9.75E-5
max speed: 5 mm/sec
speed: 2.5 mm/sec 





#do scan to find the hole location
1) move 1M X -5 mm (from  0.64 to -4.36 )
2) RE(smi.modeAlignment())
3) RE(rel_scan([pil1M], MDrive.m1, -3, 3, 31))  #for the left top hole (  34.3, 36.9  ) --> Cx = 35.6
4) RE(rel_scan([pil1M], MDrive.m3, -3, 3, 31))  #for the left top hole (  -12.6, -10  )  --> Cy = -11.35
#for the glass capillary ( -12.3, -10.2 )

for the top left hole (  35.6, -11.35  )
for the top right hole (  134.1, -14.05  )
for the bottom right hole ( 134.2  , -82.1  )
for the bottom left  hole (  36.1, -78.9 )



#for measurement
0) move 1M X +5 mm (from  -4.36 to 0.64 )
1) RE(smi.modeMeasurement())


"""

"""

20240318 


for 1M, X = -.4, 5meter, beam center [ 463, 561 ], beamstop  [ 1.9, 289, 13 ]

beamstop_save()

"""


"""

20240720

for 1M, X = -4.65120, Y = -58.0175, 5meter, beam center [ 458, 577 ], beamstop  [ 1.95, 289, 13 ]
 

20240721
for 1M, X = -4.84, Y = -58.1871, 5meter, beam center [ 458, 577 ], beamstop  [ 1.95, 289, 13 ]
beamstop_save()


20240722
for 1M, X = -4.84, Y = -58.0163, 5meter, beam center [ 458, 577 ], beamstop  [ 2.15, 289, 13 ]
beamstop_save()




20240728
proposal_id('2024_2', '313765_YZhang2')




202410232
proposal_id('2024_3', '313765_Zhang')

cd  /nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang
%run -i  /home/xf12id/.ipython/profile_collection/startup/users/30-user-YZhang_SMI_Droplet_2024C3.py


# for MDrive

Res: 9.75E-5
max speed: 5 mm/sec
speed: 2.5 mm/sec 


XZ: [ 14, 67 ] the YAG screeen  (x_limit a 10)
XZ: [ 30, 69 ] the AgBH, then set X limit a 30  
XZ: [ 30, 139 ] the tubing adaptor screw   



Kapton tube:  front [155,140] end [50, 138]. 

Reactor Mark position = [143,140]

20241024
for 1M, X = -4.84, Y = -58.0, 5meter, beam center [ 458, 578 ], beamstop  [ 1.8, 289, 13 ]
beamstop_save()
"""

'''
20250703
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air

%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C2_SMI.py


move_waxs(0)  #the waxs beamstop should go to -54.8
Otherwise, we need to do the following:
1) go to the hutch, manually push the base of the WAXS beamstop to the inboard limit
2) go to the smartAct, channel  to do home - forward
3) open the beam, put att, check the waxs beam stop, and if needed put the beamstop - 54.8

if gap messed up
need to do 
energy.move(16.1) 


we need to make the waxs  to >=16, otherwise, it will block the right side of the 2M


'''







user_name = 'YZ'
sample_dict =  {1: 'Cu2_SMI'}
ypos = 0
pxy_dict = {   1:  ( -10,  ypos  ) ,}



motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3


class DropletReactor( ):
    def __init__(  self, sample='Au_NPs'):
        '''

         sample='Autonomous_Cu_batch')


        sample='Cu_20231113_Time2Slow_Recp0' #Recp0: 
        sample='Cu_20231113_Time_Recp0' #Recp0: 
                       CTAC (50 mM), Cu (10 mM), Ph (10 mM), SA (50 mM)
        Recp0 (Vol):   12,              4,            0,       24   (Vt=40 ul) 
        Conc.      :   15,              1,            0,       30   


        sample='New_Cu_manual2'
        sample='Cu_20231113_Time2Slow_Recp0'
        sample='Cu_20231114_Manual_5batch'
        sample='Cu_20231114_Manual_batch'


        '''

        p1, p2, p3, p4 = (np.array(  [ 37.4, 5.2 ]  ), np.array(  [  137.0, 7.4 ]  ), 
                    np.array(  [  38.9,-61.0 ]  ),  np.array(  [   138.6  , -58.9  ]  )) 

        L12, L13, L42, L43 = self.get_dis_p1_p2( p1, p2) , self.get_dis_p1_p2( p1, p3) , self.get_dis_p1_p2( p4, p2) , self.get_dis_p1_p2( p4, p3) 
        self.p1, self.p2, self.p3,self.p4 =   p1, p2, p3, p4
        self.L12, self.L13, self.L42, self.L43 = L12, L13, L42, L43
        self.loc_dict = self.get_hol_location()
        self.sample_pref = sample
        #self.sample_name = 'test'
        self.sample_name = sample
        self.new_batch_num = 0
        #self.base = '/nsls2/data/smi/legacy/results/data/2024_1/313765_YZhang2/Dropbox_Com/'
        self.base = '/nsls2/data/smi/legacy/results/data/2024_3/313765_Zhang/Dropbox_Com/'


       
        self.loc_dict['A1'] = (71.5, 125.3)
        self.loc_dict['A2'] = (79.7, 125.5)
        self.loc_dict['A3'] = (88.0, 125.6)
        self.loc_dict['A4'] = (96.2, 125.7)
        self.loc_dict['A5'] = (104.5, 126.0)
        self.loc_dict['A6'] = (112.7, 126.6)
        self.loc_dict['A7'] = (120.9, 126.6)
        self.loc_dict['A8'] = (129.2, 127.5)
        self.loc_dict['A9'] = (137.4,127.9)

        self.loc_dict['B1'] = (71.5, 112.1)
        self.loc_dict['B2'] = (79.7, 112.3)
        self.loc_dict['B3'] = (87.9, 112.5)
        self.loc_dict['B4'] = (96.2, 112.8)
        self.loc_dict['B5'] = (104.5, 113.0)
        self.loc_dict['B6'] = (112.7, 113.3)
        self.loc_dict['B7'] = (121.0, 113.5)
        self.loc_dict['B8'] = (129.2, 113.8)
        self.loc_dict['B9'] = (137.4, 114.6)

        self.loc_dict['C1'] = ( 71.5, 98.6  )
        self.loc_dict['C2'] = ( 79.7, 98.8  )
        self.loc_dict['C3'] = ( 87.9, 99.1 )
        self.loc_dict['C4'] = ( 96.2, 99.3 )
        self.loc_dict['C5'] = (104.5, 99.5)
        self.loc_dict['C6'] = (112.7, 99.8 )
        self.loc_dict['C7'] = (121.0,  100.0 )
        self.loc_dict['C8'] = (129.2, 100.3 )
        self.loc_dict['C9'] = (137.4, 100.5 )


        self.loc_dict['D1'] = (72.1, 85.1)   
        self.loc_dict['D2'] = (80.3, 85.6)
        self.loc_dict['D3'] = (88.4, 85.8)
        self.loc_dict['D4'] = (96.6, 85.7)
        self.loc_dict['D5'] = (104.7, 86.2)
        self.loc_dict['D6'] = (112.9, 86.4)
        self.loc_dict['D7'] = (121.1, 86.6)
        self.loc_dict['D8'] = (129.2, 86.8)
        self.loc_dict['D9'] = (137.4, 87.0)

        self.loc_dict['E1'] = (72.1, 71.9)   
        self.loc_dict['E2'] = (80.3, 72.2)
        self.loc_dict['E3'] = (88.5, 72.4)
        self.loc_dict['E4'] = (96.7, 72.7)
        self.loc_dict['E5'] = (104.9, 72.6)
        self.loc_dict['E6'] = (113.1, 73.2)
        self.loc_dict['E7'] = (121.3, 73.4)
        self.loc_dict['E8'] = (129.5, 73.7)
        self.loc_dict['E9'] = (137.7, 74.0)

        self.loc_dict['F1'] = (72.4, 58.7)
        self.loc_dict['F2'] = (80.6, 58.9)
        self.loc_dict['F3'] = (88.8, 59.1)
        self.loc_dict['F4'] = (97.0, 59.4)
        self.loc_dict['F5'] = (105.2, 59.6)
        self.loc_dict['F6'] = (113.4, 59.8)
        self.loc_dict['F7'] = (121.6,60.1)
        self.loc_dict['F8'] = (129.8, 60.3)
        self.loc_dict['F9'] = (138, 60.5)
        #### Straight glass tubing for RoomTemperature experiment ####
        self.loc_dict['RT'] = (173.3, 139.4)
        self.loc_dict['Align']=(13.1, 70.5)
        self.loc_dict['cap_15']=(12.6, 73.7)


        self.loc_dict['K1']=(195, 143.8)
        self.loc_dict['K2']=(190, 143.8)
        self.loc_dict['K3']=(185, 143.8)
        self.loc_dict['K4']=(180, 143.8)
        self.loc_dict['K5']=(175, 143.8)
        self.loc_dict['K6']=(170, 143.8)
        self.loc_dict['K7']=(165, 143.8)
        self.loc_dict['K8']=(160, 143.6)
        self.loc_dict['K9']=(155, 143.6)
        self.loc_dict['K10']=(150, 143.6)
        self.loc_dict['K11']=(145, 143.6)
        self.loc_dict['K12']=(140, 143.6)
        self.loc_dict['K13']=(135, 143.4)
        self.loc_dict['K14']=(130, 143.4)
        self.loc_dict['K15']=(125, 143.2)
        self.loc_dict['K16']=(120, 142.8)
        self.loc_dict['K17']=(115, 142.7)
        self.loc_dict['K18']=(110, 142.6)
        self.loc_dict['K19']=(105, 142.3)
        #self.loc_dict['K10']=(107, 140.6)
        self.loc_dict['K20']=(100, 142.1)
        self.loc_dict['K21']=(95, 142.0)
        self.loc_dict['K22']=(90, 141.6)
        self.loc_dict['K23']=(85, 141.4)
        self.loc_dict['K24']=(80, 141.2)
        self.loc_dict['K25']=(75, 141.2)
  
        self.loc_dict['falcon']=(75, 141.2)

        self.holes_time = ['A9', 'A2', 'B5', 'C8', 'D1', 'E5',  'F3',   'F9']
        #


    def get_dis_p1_p2( self,p1, p2 ):
        return np.sqrt(  (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )


    def _getk(self,p1, p2 ):
        return ( p2[1] - p1[1]) / ( p2[0] - p1[0]) 

    def get_points_on_line( self,p1, p2, N=9 ):
        x1,y1 = p1
        x2,y2 = p2
        k = self._getk(p1, p2 )    
        dx = (x2-x1)/N
        x = np.linspace( x1, x2, N )
        y = y1 + k * ( x - x1 )
        pts = np.array( list( zip ( x,y )))
        return pts

    def get_hol_location(self,):
        loc_dict = {}
        pts_p1_p3 = self.get_points_on_line( self.p1, self.p3, N=6 ) #six points
        pts_p2_p4 = self.get_points_on_line( self.p2, self.p4, N=6 )  #six points
        lab = ['A', 'B', 'C', 'D', 'E', 'F']
        for i in range(6):
            pts_row= self.get_points_on_line( pts_p1_p3[i], pts_p2_p4[i], N=9 )
            for j in range(1, 10):
                loc_dict['%s%i'%(lab[i], j)] = pts_row[j-1] 
        #loc_dict['D3'] = [63.865, -33.585]
        
        return loc_dict

    def get_Mxz_pos( self ):
        return (motorX.position, motorZ.position)

    def goto_Pos(  self, pos_des, extra='', dx=0, dy =0   ):
        '''
        name: string, such as 'A1'
        '''
        x,y = self.loc_dict[pos_des]
        
        #x0,y0 = self.loc_dict[pos_des[0]+'1']
        x0, y0 = x, y 
        print( x0, y0 )

        RE(bps.mv( motorX , x0, motorZ, y0 ) )
        
        #time.sleep(3)
        #RE(bps.mv( motorX , x, motorZ, y ) )


        self.sample_name = self.sample_pref + '_loc_%s'%pos_des  + extra 
        return self.sample_name

    def measure_holes_series( self  ):
        for hole in self.holes_time:
            self.goto_Pos( hole )
            self.measure_series()

    def measure_series( self, sample_name=None,  t=1, sleep_time = 3, run_time = 60 * 60  ):
        t0 = time.time()
        while (time.time() < ( t0 + run_time) ):
            self.measure(sample_name = sample_name, t=t )
            time.sleep( sleep_time )
        print( 'Done' )           

        
    def measure( self,sample_name=None,  t=1, take_camera = True ):
        waxs_angle = 16 #15 #if need change waxs angle, do     move_waxs(  waxs_angle ),  
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



    def Run_Cu2O_synthesis( self, rxn_poss = None, sleep_time= 3, 
                                new_batch_num = None, run_time= 60*60*10,
                       extra='Fresh_batch38', verbosity=3, **md):

        '''
        sleep_time: time interval between measurements
        extra: label for samples

        25/07/03
        Cu2O Synthesis experiments

        for falcon tube measurements
        '''
        cts=0
        if new_batch_num is  None:
            new_batch_num = 0# self.new_batch_num #start 0
        

        if rxn_poss == None:
           pass
           #sam_name = self.sample_pref + extra + '_batch_'+ str(self.new_batch_num)
        else:
           rxn_poss = ['falcon']
           self.goto_Pos( rxn_pos, extra = extra + '_batch_'+ str(new_batch_num) )
                        

        t00 = time.time()
        measure = False
        while (time.time() < ( t00 + run_time) ):
            Batch_push = try_load_npz(  self.base + 'Batch_push.npz',  
                                      n_loop=3, sleep_time=0.02)

            if Batch_push is not None:
                try:
                    Batch_push = Batch_push['df'].item()
                except:
                    try:
                        Batch_push = Batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in Batch_push.keys():
                    #Batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            Batch_T_t_dict = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  
                                          n_loop=3, sleep_time=0.02)
            if Batch_T_t_dict is not None:
                try:
                    try:
                        Batch_T_t_dict = Batch_T_t_dict['df'].item()
                    except:
                        Batch_T_t_dict = Batch_T_t_dict['df'][0]
                except:
                    pass

                if new_batch_num+1 in Batch_T_t_dict.keys():  
                    measure = False
                    print('We stop the X-ray measurements for Batch %s.'%(new_batch_num))
                    new_batch_num+=1
                    
            if measure:
                t0 = time.time()
                print('We can start the X-ray measurements for 10 min.')
                tf = get_current_time()
                sam_name = self.sample_pref + extra+ '_batch_'+ str(new_batch_num) + '%s_'%tf
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)


            else:
                time.sleep( 10  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key %s in batch_push dict.'%(cts* sleep_time, self.new_batch_num) )

                cts+=1










    def Run_RT_syn( self, RT_position = 'A8', sleep_time= 5,  
                      pos_run_time = 60*60*1, extra='_CuO_Tjunc_run11', verbosity=3, **md):

        '''
        24/07/28
        
        Cu2O synthesis
            Run2: 20mM CuCl2 / 40mM pH / 20mM Ascorbic acid
        


        '''
        #print('sleep 10 minutes')
        #time.sleep(60*8)
        t0 = time.time()
        sam_name = self.goto_Pos( RT_position, extra = extra + '_'   )
        print('We can start the X-ray measurements at %s position for %.2f min.'%(RT_position, pos_run_time/60))
        while (time.time() < ( t0 + pos_run_time) ):
            self.measure(sample_name = sam_name)
            time.sleep(sleep_time)
        print('Done!!! time_scan measurement at %s position'%RT_position)

    def Run_time_scan_Kapton_vertical_scan( self, z_step= 0.2, rxn_pos = 'K3', sleep_time= 2, 
                      wait_time = 60*0, total_run_time= 60*60, 
                      extra='_time_scan_MasterRecipe_run6', 
                      verbosity=3, **md):
        '''
        23/10/24
        Time_dependent study for one droplet with vertical scan
        '''
        t00 = time.time()
        print('Wait for %s min'%(wait_time/60))
        time.sleep(wait_time)
        
        sam_name = self.goto_Pos( rxn_pos, extra = extra  )
        x0,z0 = self.loc_dict[rxn_pos]

        while (time.time() < ( t00 + total_run_time) ):
            for i in range(15):
                z_pos = z0 -1 + z_step*i
                RE(bps.mv( motorZ, z_pos) )
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)
                print('Done!!! time_scan measurement at %s, %s position'%(rxn_pos, z_pos))
            #time.sleep(30)


    def Run_time_scan_Kapton( self, z_cal = -0.6, rxn_poss = None, sleep_time= 2, 
                      wait_time = 60*20, pos_run_time = 80, #total_run_time= 60*60, 
                      extra='_time_scan_MasterRecipe_run1', 
                      verbosity=3, **md):

        '''
        23/10/24
        Time_dependent study for one recipe
        '''
        t00 = time.time()
        if rxn_poss == None:
            rxn_poss = ['K1','K2','K3','K4','K5','K6','K7','K8','K9','K10',
                    'K11','K12','K13','K14','K15','K16','K17','K18','K19']
        print('Wait for %s min'%(wait_time/60))
        time.sleep(wait_time)
        
        #while (time.time() < ( t00 + total_run_time) ):
        for i in range(len(rxn_poss)):
            rxn_pos = rxn_poss[i]
            sam_name = self.goto_Pos( rxn_pos, extra = extra  )
            x0,z0 = self.loc_dict[rxn_pos]
            RE(bps.mv( motorZ, z0+ z_cal) )
            t0 = time.time()
            print('We can start the X-ray measurements at %s position for %.2f min.'%(rxn_pos, pos_run_time/60))
            while (time.time() < ( t0 + pos_run_time) ):
                print(sam_name)
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)
            print('Done!!! time_scan measurement at %s position'%rxn_pos)


    def Run_Kapton_pos( self, rxn_poss = None, sleep_time= 2,
                      extra='_Kapton_Oil', 
                      verbosity=3, **md):

        '''
        23/10/24
        Time_dependent study for one recipe
        '''
        t00 = time.time()
        if rxn_poss == None:
            rxn_poss = ['K1','K2','K3','K4','K5','K6','K7','K8','K9','K10',
                    'K11','K12','K13','K14','K15','K16','K17','K18','K19','K20',
                    'K21','K22','K23','K24','K25']
        
        #while (time.time() < ( t00 + total_run_time) ):
        for i in range(len(rxn_poss)):
            rxn_pos = rxn_poss[i]
            sam_name = self.goto_Pos( rxn_pos, extra = extra  )
            t0 = time.time()
            print(sam_name)
            self.measure(sample_name = sam_name)
            time.sleep(sleep_time)
            print('Done!!! time_scan measurement at %s position'%rxn_pos)



    def Run_time_scan2( self, rxn_poss = ['D5', 'E7'  ], sleep_time= 5, rxnTemp = 110, 
                      pos_run_time = 60, total_run_time= 60*60, extra='_time_scan_S1_run1', verbosity=3, **md):

        '''
        23/03/12
        Time_dependent study for one recipe
        '''
        t00 = time.time()
        while (time.time() < ( t00 + total_run_time) ):
            for i in range(len(rxn_poss)):
                t0 = time.time()
                rxn_pos = rxn_poss[i]
                sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T'+ str(rxnTemp)   )
                print('We can start the X-ray measurements at %s position for %.2f min.'%(rxn_pos, pos_run_time/60))
                while (time.time() < ( t0 + pos_run_time) ):
                    self.measure(sample_name = sam_name)
                    time.sleep(sleep_time)
                print('Done!!! time_scan measurement at %s position'%rxn_pos)



    def Run_time_scan( self, tube_row = 'D', sleep_time= 5, rxnTemp = 120, 
                      pos_run_time = 60*60, extra='_time_scan_S1_run5', verbosity=3, **md):

        '''
        23/03/12
        Time_dependent study for one recipe
        '''
        t0 = time.time()
        row = ['5']#['1','2','3','4','5','6','7','8','9']#[::-1]
        #row =['1']
        for i in range(len(row)):
            t0 = time.time()
            rxn_pos = tube_row + row[i]
            sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T'+ str(rxnTemp)   )
            print('We can start the X-ray measurements at %s position for %.2f min.'%(rxn_pos, pos_run_time/60))
            while (time.time() < ( t0 + pos_run_time) ):
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)
            print('Done!!! time_scan measurement at %s position'%rxn_pos)


    def Run_time_dependent_scan( self, rxn_poss = None, sleep_time= 2, rxnTemps = [90],
                                new_batch_num = None, run_time= 60*60*10,
                      pos_run_time = 60*2.5, extra='_time_scan_Au_run4', verbosity=3, **md):

        '''
        24/10/25
        Time_dependent study for one recipe
        '''
        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num #start 0
        Batch_T_t_dict ={}
        np.savez(self.base + 'Batch_T_t_dict.npz', df=[Batch_T_t_dict])
        if rxn_poss == None:
            rxn_poss = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2', 'A1',
                        'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
                        'C9', 'C8', 'C7', 'C6', 'C5', 'C4', 'C3', 'C2', 'C1',
                        'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
                        'E9', 'E8', 'E7', 'E6', 'E5', 'E4', 'E3', 'E2', 'E1',
                        'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9']

        t00 = time.time()
        measure = False
        while (time.time() < ( t00 + run_time) ):
            ''' Load "Batch_T_t_dict" suggested from BoTorch'''
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)

            if batch_push is not None:
                try:
                    batch_push = batch_push['df'].item()
                except:
                    try:
                        batch_push = batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in batch_push.keys():
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')
                    
            if measure:
                for i in range(len(rxn_poss)):
                    t0 = time.time()
                    rxn_pos = rxn_poss[i]
                    sam_name = self.goto_Pos( rxn_pos, extra = extra + '_batch_'+ str(new_batch_num)+ '_T'+ str(rxnTemps[new_batch_num])   )
                    print('We can start the X-ray measurements at %s position for %.2f min.'%(rxn_pos, pos_run_time/60))
                    while (time.time() < ( t0 + pos_run_time) ):
                        self.measure(sample_name = sam_name)
                        time.sleep(sleep_time)
                print('Done!!! time_scan measurement at %s position'%rxn_pos)
                measure= False
                Batch_T_t_dict[self.new_batch_num] = 'Done'
                np.savez(self.base + 'Batch_T_t_dict.npz', df=[Batch_T_t_dict])
                new_batch_num += 1
                self.new_batch_num  = new_batch_num


            else:
                time.sleep( 10  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1


    def Run_one_batch( self, new_batch_num = None,  rxnTemp=105, rxnTime=8, tube_row = 'C',
            sleep_time= 5, run_time = 3600*20, extra='_ML_run7', push_flow = 80, verbosity=3, **md):

        '''
        23/03/11
        Batch manual recipes for copper synthesis using centrifuge tube
        '''

        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num
        rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = rxnTime, tube_type= 'glass', tube_row= tube_row,
                                                       push_flow = push_flow)
        sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T'+ str(rxnTemp) + '_t'+ str(rxnTime)+'min'   )
        t0 = time.time()
        measure = False
        while (time.time() < ( t0 + run_time) ):
            ''' Load "Batch_T_t_dict" suggested from BoTorch'''
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            batch_Tt = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)

            if batch_push is not None:
                try:
                    batch_push = batch_push['df'].item()
                except:
                    try:
                        batch_push = batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in batch_push.keys():
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            if batch_Tt is not None:
                try:
                    batch_Tt = batch_Tt['df'].item()
                except:
                    try:
                        batch_Tt = batch_Tt['df'][0]
                    except:
                        pass
                if (1 + new_batch_num)  in batch_Tt.keys():
                    #batch_Tt, a dict, also starting from 1, but this 1 will be same as the 1 in the push one
                    #there is no key=0 in batch_Tt
                    # e.g., { 1: [ batch_1_0,  batch_1_1, batch_1_2, batch_1_3, ]   }                    
                    measure = False
                    print('We are preparing a new batch and will stop the X-ray measurements.')
                    next_temp =   batch_Tt[new_batch_num+1][0] #in deg
                    next_time =  batch_Tt[new_batch_num+1][1] #in min 
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, tube_type= 'glass', push_flow = push_flow)

                    sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num
            if measure:
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)

            else:
                time.sleep( 10  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1

    def Run_manual_batch_v2( self, new_batch_num = None,  rxnTemp = 100,rxnTime=8, tube_row='C',
            sleep_time= 3, run_time = 3600*20, extra='manual_batch_run12', push_flow = 80, verbosity=3, **md):

        '''
        Batch manual recipes for copper
        '''

        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num
        rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = rxnTime, tube_type= 'glass', tube_row= tube_row,
                                                       push_flow = push_flow)
        sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T'+ str(rxnTemp) + '_t'+ str(rxnTime)+'min'   )
        t0 = time.time()
        measure = False
        while (time.time() < ( t0 + run_time) ):
            ''' Load "Batch_T_t_dict" suggested from BoTorch'''
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            batch_Tt = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)

            if batch_push is not None:
                try:
                    batch_push = batch_push['df'].item()
                except:
                    try:
                        batch_push = batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in batch_push.keys():
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            if batch_Tt is not None:
                try:
                    batch_Tt = batch_Tt['df'].item()
                except:
                    try:
                        batch_Tt = batch_Tt['df'][0]
                    except:
                        pass
                if (1 + new_batch_num)  in batch_Tt.keys():
                    #batch_Tt, a dict, also starting from 1, but this 1 will be same as the 1 in the push one
                    #there is no key=0 in batch_Tt
                    # e.g., { 1: [ batch_1_0,  batch_1_1, batch_1_2, batch_1_3, ]   }                    
                    measure = False
                    print('We are preparing a new batch and will stop the X-ray measurements.')
                    next_temp =   batch_Tt[new_batch_num+1][0] #in deg
                    next_time =  batch_Tt[new_batch_num+1][1] #in min 
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = rxnTime, tube_type= 'glass', tube_row= tube_row,
                                                       push_flow = push_flow)
                    sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num
            if measure:
                self.measure(sample_name = sam_name)
                time.sleep(sleep_time)

            else:
                sleep_time2=10
                time.sleep( sleep_time2  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time2) )

                cts+=1

    def Run_manual_batch( self, new_batch_num = None,  init_pos = 'C7',init_T='100', init_t='15',
            sleep_time= 3, run_time = 3600*20, extra='_NaBH_batch2', push_flow = 80, verbosity=3, **md):

        '''
        Batch manual recipes for copper
        '''

        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num

        sam_name = self.goto_Pos( init_pos, extra = extra + '_T'+ init_T + '_t'+ init_t+'min'   )
        t0 = time.time()
        measure = False
        while (time.time() < ( t0 + run_time) ):
            ''' Load "Batch_T_t_dict" suggested from BoTorch'''
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            batch_Tt = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)

            if batch_push is not None:
                try:
                    batch_push = batch_push['df'].item()
                except:
                    try:
                        batch_push = batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in batch_push.keys():
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            if batch_Tt is not None:
                try:
                    batch_Tt = batch_Tt['df'].item()
                except:
                    try:
                        batch_Tt = batch_Tt['df'][0]
                    except:
                        pass
                if (1 + new_batch_num)  in batch_Tt.keys():
                    #batch_Tt, a dict, also starting from 1, but this 1 will be same as the 1 in the push one
                    #there is no key=0 in batch_Tt
                    # e.g., { 1: [ batch_1_0,  batch_1_1, batch_1_2, batch_1_3, ]   }                    
                    measure = False
                    print('We are preparing a new batch and will stop the X-ray measurements.')
                    next_temp =   batch_Tt[new_batch_num+1][0] #in deg
                    next_time =  batch_Tt[new_batch_num+1][1] #in min 
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, tube_type= 'glass', push_flow = push_flow)

                    sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num
            if measure:
                self.measure(sample_name = sam_name)
                time.sleep(5)

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1


    def AutoRun_batch( self, new_batch_num = None,  init_T='100', init_t='15',
            sleep_time= 3, run_time = 3600*20, extra='_1115_Cu_Run7_20recps', push_flow = 80, verbosity=3, **md):

        '''



        new_batch_num = None,  init_T='100', init_t='20',  extra='_1115_Cu_Run5', 

        new_batch_num = None,  init_T='100', init_t='12',
            sleep_time= 3, run_time = 3600*20, extra='_1115_Cu_Run5', push_flow = 80, verbosity=3, **md):

        Batch Autonomous experiment (using 1/sigma (dip-fit)) and using 31 data as a initial batch
        '''

        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num
        init_pos, _,_ = Find_new_pos_fr(Target_time=int(init_t))
        sam_name = self.goto_Pos( init_pos, extra = extra + '_T'+ init_T + '_t'+ init_t+'min'   )
        
        t0 = time.time()
        measure = False
        while (time.time() < ( t0 + run_time) ):
            ''' Load "Batch_T_t_dict" suggested from BoTorch'''
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            batch_Tt = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)

            if batch_push is not None:
                try:
                    batch_push = batch_push['df'].item()
                except:
                    try:
                        batch_push = batch_push['df'][0]
                    except:
                        pass

                if new_batch_num in batch_push.keys():
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            if batch_Tt is not None:
                try:
                    batch_Tt = batch_Tt['df'].item()
                except:
                    try:
                        batch_Tt = batch_Tt['df'][0]
                    except:
                        pass
                if (1 + new_batch_num)  in batch_Tt.keys():
                    #batch_Tt, a dict, also starting from 1, but this 1 will be same as the 1 in the push one
                    #there is no key=0 in batch_Tt
                    # e.g., { 1: [ batch_1_0,  batch_1_1, batch_1_2, batch_1_3, ]   }                    
                    measure = False
                    print('We are preparing a new batch and will stop the X-ray measurements.')
                    next_temp =   batch_Tt[new_batch_num+1][0] #in deg
                    next_time =  batch_Tt[new_batch_num+1][1] #in min 
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, tube_type= 'glass', push_flow = push_flow)

                    sam_name = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num
            if measure:
                self.measure(sample_name = sam_name)
                time.sleep(3)

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1

    def Run_manual_recp( self, init_T='25', init_t='1', wait_time = 60 * 0, 
            sleep_time= 3, run_time = 3600*10, extra='_Ir_WH_capillary', verbosity=3, **md):

        '''

        Run_manual_recp( self, init_T='100', init_t='15',
            sleep_time= 3, run_time = 3600*10, extra='_Cu_20recps_11151912_v2_', verbosity=3, **md):
        Run_manual_recp( self, init_T='25', init_t='1', wait_time = 60 * 0, 
            sleep_time= 3, run_time = 3600*10, extra='_Ir_10recps_11160105_v1_', verbosity=3, **md):

        Batch manual recipes for copper
        '''
        cts=0
        init_pos, _,_ = Find_new_pos_fr(Target_time=int(init_t))
        sam_name = self.goto_Pos( init_pos, extra = extra + '_T'+ init_T + '_t'+ init_t+'min'   )
        t0 = time.time()
        measure = True
        time.sleep( wait_time )
        while (time.time() < ( t0 + run_time) ):
            if measure:
                self.measure(sample_name = sam_name)
                #time.sleep(1)

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1




        


DR = DropletReactor( sample = 'Cu2O_')

# For 1 straight glass tubing
def Find_new_pos_fr(Target_time = 20, tube_type= 'glass', set_point= 'A1', push_flow = 80, flow_start='top', tube_row='C'):
   while Target_time > Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[set_point][1]:
       push_flow -=5
   time_diff =[]
   time_diff_pos =[]
   for ci in ['1', '2', '3','4','5','6','7', '8', '9']:#[ '2', '3','4','5','6','7', '8' ]:
       for ri in  ['A','B','C','D','E','F']:
           time_diff.append(np.abs(Target_time-Reactor_pos_vol(use=tube_type, Flowrate=push_flow)[ri+ci][1]))
           time_diff_pos.append(ri+ci)
   rxn_pos = time_diff_pos[np.argmin(time_diff) ]
   push_flow = Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[rxn_pos][0]/ Target_time
   push_vol = Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[rxn_pos][0]
   #Update tube row
   rxn_pos = tube_row+ rxn_pos[-1:]
   return rxn_pos, push_flow, push_vol

### Old version for 6-turn glass tubing
# def Find_new_pos_fr(Target_time = 20, tube_type= 'glass', set_point= 'F7', push_flow = 80, flow_start='top'):
#    while Target_time > Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[set_point][1]:
#        push_flow -=5
#    time_diff =[]
#    time_diff_pos =[]
#    for ci in [ '3','4','5','6','7']:#[ '2', '3','4','5','6','7', '8' ]:
#        for ri in  ['A','B','C','D','E','F']:
#            time_diff.append(np.abs(Target_time-Reactor_pos_vol(use=tube_type, Flowrate=push_flow)[ri+ci][1]))
#            time_diff_pos.append(ri+ci)
#    rxn_pos = time_diff_pos[np.argmin(time_diff) ]
#    push_flow = Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[rxn_pos][0]/ Target_time
#    push_vol = Reactor_pos_vol(use=tube_type, Flowrate=push_flow, flow_start=flow_start)[rxn_pos][0]
#    return rxn_pos, push_flow, push_vol

def Reactor_pos_vol(use ='glass', Flowrate=80, flow_start='top'):
    Reactor_dict ={}
    if flow_start == 'bottom':
        Row = ['F', 'E', 'D', 'C', 'B', 'A']
        Column = ['9', '8', '7', '6', '5', '4', '3', '2', '1']
    elif flow_start =='top':
        Row = ['A',  'B', 'C',  'D', 'E', 'F'  ]
        Column = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    if use == 'PTFE':
        '''SAME tubing for 6 turns'''
        ID_maintube = 1.5875 #mm
        start_len = 9.5 #mm
        Vol = ID_maintube**2/4 *np.pi *start_len

        step_len= 12.625
        jump_len= 22

        for i in range(len(Row)):
            ri = Row[i]
            if ri in ['F', 'D', 'B']:
                for j in range(len(Column)):
                    ci = Column[j]
                    if j ==0:
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol, Rxn_time]
                    else:
                        Vol+=ID_maintube**2/4 *np.pi *step_len
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]
            else:
                for j in range(len(Column[::-1])):
                    ci = Column[::-1][j]
                    if j ==0:
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    else:
                        Vol+=ID_maintube**2/4 *np.pi *step_len
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]

            Vol +=  ID_maintube**2/4 *np.pi *jump_len

    elif use == 'PTFE2':
        ''' required volumes to locate next beam position'''
        Vols = [    35,  52, 53.7, 54.3, 52.3, 53.2, 55, 46.5, 0,
                    0,  0, 112.5, 56.8, 57.5, 57.2, 55.5, 0, 0,
                    0,  0, 155.5, 55, 54.3, 53.8, 55.2, 0, 0,
                    0,  0, 165.2, 55.7, 55.2, 57.5, 59.8, 57.8, 0,
                    0,  0, 110, 57.3, 53.7, 54.5, 53.3, 0, 0,
                    0,  0, 141.3, 54.5, 52.8, 52, 52.7, 57, 0 ]
        pos = 1
        for i in range(len(Row)):
            ri = Row[i]
            if ri in ['F', 'D', 'B']:
                for j in range(len(Column)):
                    ci = Column[j]
                    Vol = np.sum(Vols[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

            else:
                for j in range(len(Column[::-1])):
                    ci = Column[::-1][j]
                    Vol = np.sum(Vols[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

    elif use == 'Kapton':
        ID_curvetube = 1.5875
        start_len = 8.5
        start_Vol = ID_curvetube**2/4 *np.pi *start_len
        ''' required volumes to locate next beam position'''
        Vols = [start_Vol,  50, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0,
                    0,  133.34, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0,
                    0,  133.34, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0,
                    0,  133.34, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0,
                    0,  133.34, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0,
                    0,  133.34, 66.67, 66.67, 66.67, 66.67, 66.67, 66.67, 0]
        pos = 1
        for i in range(len(Row)):
            ri = Row[i]
            if ri in ['F', 'D', 'B']:
                for j in range(len(Column)):
                    ci = Column[j]
                    Vol = np.sum(Vols[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

            else:
                for j in range(len(Column[::-1])):
                    ci = Column[::-1][j]
                    Vol = np.sum(Vols[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

    elif use == 'Kapton2':
        ID_maintube = 2.667 #mm
        ID_curvetube = 1.5875
        Main_len = [9.5, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625,
                    0, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625,
                    0, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625,
                    0, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625,
                    0, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625,
                    0, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625, 12.625]

        start_len = 9.5
        Vol = ID_maintube**2/4 *np.pi *start_len
        pos = 1
        for i in range(len(Row)):
            ri = Row[i]
            if ri in ['F', 'D', 'B']:
                for j in range(len(Column)):
                    ci = Column[j]
                    Vol = ID_maintube**2/4 *np.pi *np.sum(Main_len[:pos])
                    Vol += ID_curvetube**2/4 *np.pi *np.sum(Curve_len[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

            else:
                for j in range(len(Column[::-1])):
                    ci = Column[::-1][j]
                    Vol = ID_maintube**2/4 *np.pi *np.sum(Main_len[:pos])
                    Vol += ID_curvetube**2/4 *np.pi *np.sum(Curve_len[:pos])
                    Rxn_time = Vol/Flowrate
                    Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    pos+=1

    elif use == 'glass':
        '''SAME tubing for 6 turns'''
        ID_maintube = 2 #mm
        start_len = 9.5 #mm
        Vol = ID_maintube**2/4 *np.pi *start_len

        step_len= 12.625
        jump_len= 22

        for i in range(len(Row)):
            ri = Row[i]
            if ri in ['F', 'D', 'B']:
                for j in range(len(Column)):
                    ci = Column[j]
                    if j ==0:
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol, Rxn_time]
                    else:
                        Vol+=ID_maintube**2/4 *np.pi *step_len
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]
            else:
                for j in range(len(Column[::-1])):
                    ci = Column[::-1][j]
                    if j ==0:
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]
                    else:
                        Vol+=ID_maintube**2/4 *np.pi *step_len
                        Rxn_time = Vol/Flowrate
                        Reactor_dict[ri+ci]=[Vol,Rxn_time]

            Vol +=  ID_maintube**2/4 *np.pi *jump_len

    else:
        pass

    return Reactor_dict



def try_load_npz(  npz_filename, n_loop=3, sleep_time=0.02):
    for i in range(n_loop):
        try:
            npz = np.load(npz_filename, allow_pickle=True)
            return npz
        except:
            time.sleep(sleep_time )
            print('Error: Fail to save %s'%npz_filename)
            return None

# def get_hol_location( pos = [ 0, 0], step_size = [ 12.72, 13.3 ], rot_angle = 0, Nx=9, Ny= 6 ):
#     #change x Y position here
#     Nx = Nx  # 6
#     Ny = Ny # 14
#     #Ps = np.zeros( [Nx, Ny ])
#     # Ps = [] 
#     Ps_grid = []
#     rot_angle = np.deg2rad(rot_angle)
#     delta_x = np.cos(rot_angle)
#     delta_y = np.sin(rot_angle)
#     rot_matrix = np.array(((delta_x, -delta_y),(delta_y, delta_x)))


#     for j in range( Ny ):
#         for i in range(Nx):
#             # Ps.append( [  pos[0] -  i * 0.4,  pos[1] -  j * 0.4] )
#             Ps_grid.append([i*step_size[0], j*step_size[1] ])

#     Ps_grid = np.array(Ps_grid)
#     Ps_grid_rot = np.dot(rot_matrix,Ps_grid.T).T
#     Ps = Ps_grid_rot + np.array(pos)
#     return Ps



'''
6/22/2023, 10:40 pm, finish the setup

proposal_id("2023_2", "310844_Zhang3")  # For AutoSyn
sample_id(user_name="test", sample_name="test_CFN")



1) scan stage.x and y to define the data acq position

RE(smi.modeAlignment())
det_exposure_time(0.3, 0.3)
 RE(count([pil1M])) 
 smi.setDirectBeamROI()
RE(rel_scan([pil1M], stage.x, -2, 2, 40))  #find the X range [-1.3, 1.2 ] --> [-1, +1]
RE(rel_scan([pil1M], stage.y, -2, 2, 40))  #find the y range, [-1.2, 1.5] --> [-0.6, +1.2]




# 1M raw data is saved in folder with time d/m/y
for example, 06-24-2023 data are saved in 
/nsls2/data/smi/legacy/results/raw/1M/2023/06/24
filename would be uid style, such as 
4000 -rw-rw-r--+ 1 softioc softioc 4094258 Jun 24 01:07 693dab29-6c43-4c3d-93f5_000000.tiff


# 900 raw data are saved in
/nsls2/data/smi/legacy/results/raw/900KW/2023/06/24







'''






x_list = np.array(list( ( pxy_dict.values()) ) )[:,0]
y_list = np.array(list( ( pxy_dict.values()) ) )[:,1]
sample_list =  np.array(list( ( sample_dict.values()) ) )
ks =  np.array(list( ( sample_dict.keys()) ) )

##################################################
############ Some convinent functions#################
#########################################################




def setup_run( waxs_angle=15  ):
    setup_ova(   )
    move_waxs(waxs_angle)






def flow_227():
    time.sleep( 0*60 )
    run(  'SMI_AuSyn_TwoRec_0227_RUN0_100C_80ulM' , exposure_time=1, maxTime= 6*3600 + 1, interval=5 )


def flow_302F(cenx=-4):  #cen = -4
    run_name = 'SMI_AuSyn_Manual_0302_RUN19_80C_80ulM'
    run(   run_name , exposure_time=1, maxTime= 1, interval=5 , fid=0, cenx = cenx)  
    print('Sleep 20 min here......')
    time.sleep( 20*60 )
    run(  run_name , exposure_time=1, maxTime= 10*3600 + 1, interval=5, fid=0, cenx = cenx)   


 
def flow_623():
    time.sleep( 0*60 )
    run(  'SMI_AuSyn_3Rec_12min_100C_test' , exposure_time=1, maxTime= 6*3600 + 1, interval=5 )



def flow_623_B():
    time.sleep( 10*60 )
    run(  'SMI_AuSyn_box_P7_100C' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )




def flow_623_C():
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_box2_P7_100C_V2' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )


def flow_623_D():
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_UCB100_P7_100C_RUN1' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )




def flow_624_A():
    sleep_time = 20*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_UCB100_P7_100C_RUN2' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )




def flow_624_B():
    sleep_time = 20*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_UCB100_P7_100C_RUN3' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )




def flow_624_C():
    sleep_time = 20*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_UCB100_P7_100C_RUN4' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )




def flow_625_A():
    sleep_time = 10*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuSyn_UCB100_P3_100C_RUN5' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )





def flow_625_B():  #failed , droplet already passed
    sleep_time = 2*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN6' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_C():  #failed , droplet already passed a little bit
    sleep_time = 2*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN7' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_D():  # saw something in the begging, but becuase releive the back pressure, it's gone 
    sleep_time = 2*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN8' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_E():  #
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN9' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )

def flow_625_F():  #
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN9' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_G():  #
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN10' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_H():  # GOOD
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN11' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )



def flow_625_J():  ## GOOD
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_100C_Time_RUN12' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )


def flow_625_K():  #
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_110C_Time_RUN13' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )


def flow_625_L():  #
    sleep_time = 0*60
    print('sleep %s mins'%(sleep_time/60))
    time.sleep( sleep_time )
    run(  'SMI_AuOneRecp_P5_110C_Time_RUN14' , exposure_time=1, maxTime= 10*60*60 + 1, interval=5 )






#def create_Xray_position_map(  cenx=-2, ceny=10.2, Nx = 2, Ny = 12,  stepx=0.2, stepy=0.03 ):


#def create_Xray_position_map(  cenx=0, ceny=10.2, Nx = 2, Ny = 12,  stepx=0.2, stepy=0.03 ):
#def create_Xray_position_map(  cenx=-1, ceny=10.2, Nx = 2, Ny = 12,  stepx=0.2, stepy=0.03 ):
#def create_Xray_position_map(  cenx=-1, ceny=10.2, Nx = 7, Ny = 12,  stepx=0.2, stepy=0.03 ):
#def create_Xray_position_map(  cenx=0, ceny=0.3, xy_radius=[ 1, 0.9],  stepx=0.2, stepy=0.03 ):  ##For position 7
#def create_Xray_position_map(  cenx=-0.1, ceny=0.04, xy_radius=[ 1, 0.9],  stepx=0.2, stepy=0.03 ):  ##For position 3
def create_Xray_position_map(  cenx=-0.5, ceny=0.0, xy_radius=[ 1, 0.9],  stepx=0.2, stepy=0.03 ):  ##For position 5

    #print('here')
    px = np.arange( cenx - xy_radius[0], cenx + xy_radius[0]+stepx , stepx   )
    py = np.arange( ceny - xy_radius[1], ceny + xy_radius[1] , stepy   )
    py2 = (py.copy())[::-1]
    pxy = []
    i = 0 
    for pxi in px:
        if i%2:
            pY = py2
        else:
            pY = py
        i+=1        
        for pyi in pY:
            pxy.append( [pxi, pyi ])
    pxy = np.array( pxy )
    w = ( (pxy[:,0] - cenx)**2 + (pxy[:,1] - ceny)**2   ) < (min( xy_radius ))**2   
    #print(  len(px), len(py))
    return pxy[w] 



def run(    sample,  exposure_time=1, maxTime=12 * 3600 + 1, interval= 20,  camera=True, fid=0    ):  
    '''    
    run( 'Test_2min', exposure_time=1, maxTime= 120 + 1, interval=5,   ) 
    run(   'Test',  exposure_time=1, maxTime=10, interval= 5,  camera=True, fid=0    )



    ''' 

    dets = [ pil1M, pil900KW  ]
    #dets = [ pil1M   ]
    #waxs_angle = 15    #   move_waxs(15)
    det_exposure_time(exposure_time, exposure_time) 
    t0 = time.time()
    start_time = 0
    trigger_time = np.arange(start_time, maxTime, interval)
    print('There will be %.3f K to be measrued.'%( len(trigger_time)/1000 ) )
    # while self.clock()<maxTime:
    pxy = create_Xray_position_map(  )
    
    pxy1 = np.vstack( [pxy, pxy[::-1]] )
    Npxy = len(pxy1)
    RE(  bps.mv(stage.x, pxy1[ 0 ][0] )     )  
    RE(  bps.mv(stage.y, pxy1[ 0 ][1] )     )    

    for trigger in trigger_time:
        while ( time.time() - t0 ) < trigger:
            time.sleep(.2)
        tf = get_current_time()
        extra =  '%s_'%tf + '%06d_'%fid   
 
        _sample =  extra + sample 
        name_fmt = '{sample}_x{x:.2f}_y{y:.2f}_expt{expt}s' #_sid{scan_id:08d}'          
        sample_name = name_fmt.format(sample=_sample, x=stage.x.position, y=stage.y.position,  expt= exposure_time, ) # scan_id=RE.md['scan_id'])   
        sample_id(user_name=user_name, sample_name=sample_name ) 
        print(f'\n\t=== Sample: {sample_name} ===\n')
        print('Collect data here....')
        if camera:
            sample_name_oav = '%s_%s_id%s_OAV'%( user_name, sample_name,RE.md['scan_id'] )
            save_ova(  sample = sample_name_oav, setup= False )             
        RE(  bp.count(dets, num=1)  )
        fid+=1    
        pos_indx = fid%Npxy         
        RE(  bps.mv(stage.x, pxy1[ pos_indx ][0] )     )  
        RE(  bps.mv(stage.y, pxy1[ pos_indx ][1] )     )    
          
  


def run_nobeam(    sample,  exposure_time=1, maxTime=12 * 3600 + 1, interval= 20,  camera=True, fid=0    ):  
    '''    
    run( 'Test_2min', exposure_time=1, maxTime= 120 + 1, interval=5,   ) 
    run(  'SMI_CuSyn_161Rec_105C_40ulM'  )  #Cu, interval=20,  #20221029 nite, 1:30 am     
    ''' 

    #dets = [ pil1M, pil900KW  ]
    #dets = [ pil1M   ]
    #waxs_angle = 15    #   move_waxs(15)
    det_exposure_time(exposure_time, exposure_time) 
    t0 = time.time()
    start_time = 0
    trigger_time = np.arange(start_time, maxTime, interval)
    print('There will be %.3f K to be measrued.'%( len(trigger_time)/1000 ) )
    # while self.clock()<maxTime:
    for trigger in trigger_time:
        while ( time.time() - t0 ) < trigger:
            time.sleep(.2)
        tf = get_current_time()
        extra =  '%s_'%tf + '%06d_'%fid   
        _sample =  extra + sample 
        name_fmt = '{sample}_expt{expt}s' #_sid{scan_id:08d}'          
        sample_name = name_fmt.format(sample=_sample,  expt= exposure_time, ) # scan_id=RE.md['scan_id'])   
        sample_id(user_name=user_name, sample_name=sample_name ) 
        print(f'\n\t=== Sample: {sample_name} ===\n')
        print('Collect data here....')
        if camera:
            save_ova(  sample = sample_name, setup= False ) 
        #RE(  bp.count(dets, num=1)  )
        fid+=1
  
#def collect_one_data(    sample,  exposure_time=1,   camera=True, fid=0    ):  
def collect_one_data(    sample,  exposure_time=1,   camera=False, fid=0    ):  

    '''   

    collect_one_data(    'Run14_DropX_',  exposure_time=1,   camera=True, fid=0    )
 

    ''' 

    dets = [ pil1M, pil900KW  ]
    det_exposure_time(exposure_time, exposure_time) 
    tf = get_current_time()
    extra =  '%s_'%tf + '%06d_'%fid   
    _sample =  extra + sample 
    name_fmt = '{sample}_expt{expt}s' #_sid{scan_id:08d}'          
    sample_name = name_fmt.format(sample=_sample,  expt= exposure_time, ) # scan_id=RE.md['scan_id'])   
    sample_id(user_name=user_name, sample_name=sample_name ) 
    print(f'\n\t=== Sample: {sample_name} ===\n')
    print('Collect data here....')
    if camera:
        sample_name_oav = '%s_%s_id%s_OAV'%( user_name, sample_name,RE.md['scan_id'] )
        save_ova(  sample = sample_name_oav, setup= False ) 
    RE(  bp.count(dets, num=1)  )
[]   


def collect_wsaxs(  t=1, sample=None, waxs_angle = 20  ):

    yield from bps.mv(waxs, waxs_angle)
    if waxs_angle !=0:
        dets = [ pil900KW,  pil1M ] 
    else:
        dets = [ pil900KW ] 
    name_fmt = "{sample}_x{x:05.2f}_y{y:05.2f}_det{saxs_z:05.2f}m_waxs{waxs_angle:05.2f}_expt{t}s"
    sample_name = name_fmt.format(
        sample=sample,
        x=np.round(stage.x.position, 2),
        y=np.round(stage.y.position, 2),         
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




#WAXS   YZ_2023-02-26-19-17-54_000000_Test_expt1s_id118447_000000_WAXS.tif
#SAXS   YZ_2023-02-26-19-17-54_000000_Test_expt1s_id118447_000000_SAXS.tif
#OAV    YZ_2023-02-26-19-29-40_000000_Test_expt1_id118450_OAV_000.jpg
# get id:   fp.split('_')[-3][2:]
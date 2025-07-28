'''
pass-=316987
saf: 316690


20250706
SAXS: 2M ,5 meter
16.1 kev, low-divergency, in air

%run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2025C2_SZhang.py
proposal_swap(316987)




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
username = 'SZ'
user_name = 'SZ'
sample_dict =  {1: 'SampleX_SMI'}
ypos = 0
pxy_dict = {   1:  ( -10,  ypos  ) ,}


motorX = MDrive.m5 #
motorZ = MDrive.m3

###NOTE
# X (MotorX): 88.4 #motor 5
# Y (MotorZ): 77.6  #motor 3




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





    def run( self,  sample_name ='X', sleep_time= 5, run_time = 60*60*60, extra='', verbosity=3, **md):
        '''
      

        '''
  
        t0 = time.time()        
        print('Starting measurements for %.2f min.'%( run_time/60))
        while (time.time() < ( t0 + run_time) ):
            self.measure(sample_name = sample_name )
            time.sleep(sleep_time)
        dt = time.time() - t0
        print(f'This measurement for sample: {sample_name} took {dt:.2f} min.')






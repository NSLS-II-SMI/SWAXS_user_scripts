
#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4

################################################################################
#  Short-term settings (specific to a particular user/experiment) can
# be placed in this file. You may instead wish to make a copy of this file in
# the user's data directory, and use that as a working copy.
################################################################################

#logbooks_default = ['User Experiments']
#tags_default = ['CFN Soft-Bio']

import pickle
import os
from shutil import copyfile
from ophyd import EpicsSignal
from bluesky.suspenders import SuspendFloor, SuspendCeil
import time
from datetime import datetime
#from Dropbox import CustomDropbox
from utility import *
import numpy as np 

RE.md['experiment_alias_directory'] = '/nsls2/data/cms/legacy/xf11bm/data/2025_1/Yuzhang/'
# ring_current = EpicsSignal('SR:OPS-BI{DCCT:1}I:Real-I')
# sus = SuspendFloor(ring_current, 100, resume_thresh=400, sleep=600)
# RE.install_suspender(sus)

print( 'here'  )

def smaxs_on():
    '''
    2025/4/2
    '''
    detselect( [ pilatus2M, pilatus8002 ] ) 
    WAXSx.move(-220)    
    WAXSy.move(40)
    MAXSx.move( -8  )
    MAXSy.move( -120  )

def maxs_on():   
    # bsin()
    #cms.modeMeasurement()
    detselect(pilatus8002) 
    MAXSx.move(-61)
    MAXSy.move(-138)  #-43



'''
2025/4/2

In [147]: wbs()
bsx = -14.199771
bsy = -8.200139
bsphi = -64.000927


In [206]: wbs()
bsx = -14.400248999999999
bsy = -8.500198
bsphi = -64.000872

direct beam [ 756, 591  ] 



Mdrive 5 ( X)  66.5 
Smpl3_Y ( Y ) 22


'''

### DEFINE YOUR PARENT DATA FOLDER HERE 
# cms.SAXS.setCalibration([759, 1074], 5.03, [-65, -73])  #20201021, 13.5 keV
# cms.SAXS.setCalibration([756-5, 1079+7], 5.0, [-65, -73])   #5m,13.5kev,
cms.SAXS.setCalibration([753, 1680-595  ], 5.8, [-65, -73])


parent_data_folder = '/nsls2/data/cms/legacy/xf11bm/data/2025_1/Yuzhang'

mdx = EpicsMotor("XF:11BM-ES{Mdrive-Ax:5}Mtr", name="mdx")
mdy = EpicsMotor("XF:11BM-ES{Mdrive-Ax:3}Mtr", name="mdy")

smx = EpicsMotor("XF:11BM-ES{Mdrive-Ax:5}Mtr", name="smx")
smy = EpicsMotor("XF:11BM-ES{Mdrive-Ax:3}Mtr", name="smy")

smyBASE = EpicsMotor("XF:11BMB-ES{Chm:Smpl3-Ax:Y}Mtr", name="smyBASE")


def get_current_time( pattern = '%Y_%m_%d_%H_%M_%S' ):
    return datetime.today().strftime( pattern )
#detselect( [ pilatus2M, pilatus8002 ] )
detselect( [ pilatus2M, pilatus8002 ] )


##for Dropbox communication

#DB = CustomDropbox()


#DB.download_file_from_Dropbox( dropbox_file='foo', local_dir = DB.local_dir, dropbox_dir = DB.dropbox_dir )
#DB.upload_file_to_dropbox( 'foo', local_dir = DB.local_dir, dropbox_dir = DB.dropbox_dir, overwrite=True,)










class DropletHolder(PositionalHolder):
    '''This class is for Yugang Zhang's special holder for in situ characterization of nanoparticle synthesis.
       It contains 9(x)x6(y) holes for x-ray probe. The spacing is 12.5mm in both x and y directions
    
    
    '''
    

    # Core methods
    ########################################

    def __init__(self, name='DropletHolder', base=None, **kwargs):
        
        super().__init__(name=name, base=base, **kwargs)
        
        self._positional_axis = ['x','y']
        # self._axes['y'].origin = 1  
        #F9:  [  80, 57  ] #the first input hole (bottom, right along beam travel direction )        
        # self._axes['x'].origin = 80
        # self._axes['y'].origin = 57
        self._axes['x'].origin = 93.67  #72 #71.6
        self._axes['y'].origin = 89.9  #61.6 #61.3        
        self.x_spacing = 12.67 +0.05 # 9mm seperation both in x and yy direction
        self.y_spacing = 13 + 0.3 
        self.getSamples_zigzag()
        self.base = '/nsls2/data/cms/legacy/xf11bm/data/2025_1/Yuzhang/Dropbox_Com/'
        self.new_batch_num = 0 
        self.naming_scheme = ['name', 'extra', 'clock',   'exposure_time']
        self.reactor = Reactor(tubing_type= 'glass', flow_rate=80, flow_start='top')





    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        
        # The _axes_definitions array holds a list of dicts, each defining an axis
        super()._set_axes_definitions()

        self._axes_definitions.append ( {'name': 'y',
                            'motor':  mdy ,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up',
                            } )
        
        self._axes_definitions.append ( {'name': 'x',
                            'motor':  mdx ,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': 'positive moves stage up',
                            } )     
                        



    def slot(self, sample_number):
        '''Moves to the selected slot in the holder.'''
        
        getattr(self, self._positional_axis[0]+'abs')( self.get_slot_position(sample_number) )
        
    
    def get_slot_position(self, slot):
        '''Return the motor position for the requested slot number.'''
        # This method should be over-ridden in sub-classes, so as to properly
        # implement the positioning appropriate for that holder.
        # This is the critical to define the position for the 10 samples. 
        
        position_y = int((slot-1)/9)
        position_x = (slot-1)%9        

        return +position_x*self.x_spacing + self._axes['x'].origin ,  position_y*self.y_spacing + self._axes['y'].origin
        
        
    def addSample(self, sample, sample_number=None):
        '''Add a sample to this holder/bar.'''
        
        if sample_number is None:
            if len(self._samples)==0:
                sample_number = 1
            else:
                ki = [ int(key) for key in self._samples.keys() ]
                sample_number = np.max(ki) + 1
                
                
        if sample_number in self._samples.keys():
            print('Warning: Sample number {} is already defined on holder "{:s}". Use "replaceSample" if you are sure you want to eliminate the existing sample from the holder.'.format(sample_number, self.name) )
            
        else:
            self._samples[sample_number] = sample
            
        self._samples[sample_number] = sample
        
        sample.set_base_stage(self)
        sample.md['holder_sample_number'] = sample_number

        
        
    def addSampleSlot(self, sample, slot):
        '''Adds a sample to the specified "slot" (defined/numbered sample 
        holding spot on this holder).'''
 
       
        self.addSample(sample, sample_number=slot)
        sample.setOrigin( ['x'], [self.get_slot_position(slot)[0]] )
        sample.setOrigin( ['y'], [self.get_slot_position(slot)[1]] )

                
    def listSamplesPositions(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
        
        for sample_number, sample in self._samples.items():
            pos = getattr(sample, self._positional_axis+'pos')(verbosity=0)
            print( '%s: %s (%s = %.3f)' % (str(sample_number), sample.name, self._positional_axis, pos) )


    def listSamples(self):
        '''Print a list of the current samples associated with this holder/
        bar.'''
         
        for sample_number, sample in sorted(self._samples.items()):
            print( '{}: {:s}'.format(sample_number, sample.name) )
            




    def gotoAlignedPosition(self):
        '''Goes to the currently-defined 'aligned' position for this stage. If
        no specific aligned position is defined, then the zero-point for the stage
        is used instead.'''
        
        # TODO: Optional offsets? (Like goto mark?)
        #self.gotoOrigin(axes=self._positional_axis)
        pass
        

        #time.sleep(10)

    def getSample(self, sample_number, verbosity=3):
        '''Return the requested sample object from this holder/bar.
        
        One can provide an integer, in which case the corresponding sample
        (from the holder's inventory) is returned. If a string is provided, 
        the closest-matching sample (by name) is returned.'''
        
        if sample_number not in self._samples:
            if verbosity>=1:
                print('Error: Sample {} not defined.'.format(sample_number))
            return None
        
        sample_match = self._samples[sample_number]

        if verbosity>=3:
            print('{}: {:s}'.format(sample_number, sample_match.name))
        
        return sample_match
    

    def goto_Pos( self, pos_des , name=None, extra = ''  ):
        ''' pos_des: string, e.g., A1,  '''

        sample_number = self.dict_pos_ind[ pos_des ] #
        sample = self.getSample(sample_number, verbosity=0)
        x, y = sample.origin()['x'], sample.origin()['y']
        '''
        2024/02/18
        NEED TO manually re measure it!!
        
        '''
        manual_pos ={}
        ####2024/11/25 Change position manually for 'A1' 
        manual_pos['A1'] = [ 50, 89.7]        #[ 162.44, 138.8]
        manual_pos['A2'] =[  90, 90.0]

        ####
        manual_pos['A3'] =[ 137.44, 138.8]
        manual_pos['A4'] =[ 124.44, 138.6]
        manual_pos['A5'] =[ 112.04, 138.6]
        manual_pos['A6'] =[ 99.24, 138.6]
        manual_pos['A7'] =[ 86.84, 138.6]
        manual_pos['A8'] =[ 73.84, 138.4]
        manual_pos['A9'] =[ 60.84, 138.6]

        manual_pos['B1'] =[ 162.44, 125.8]
        manual_pos['B2'] =[ 150.24, 125.2]
        manual_pos['B3'] =[ 137.84, 125.2]
        manual_pos['B4'] =[ 124.84, 125.2]
        manual_pos['B5'] =[ 112.04, 125.2]
        manual_pos['B6'] =[ 99.24, 125.2]
        manual_pos['B7'] =[ 86.84, 125.2]
        manual_pos['B8'] =[ 73.84, 125.2]
        manual_pos['B9'] =[ 60.44, 125.8]

        manual_pos['C1'] =[ 162.44, 111.8]
        manual_pos['C2'] =[ 150.24, 112.0]
        manual_pos['C3'] =[ 137.64, 112.0]
        manual_pos['C4'] =[ 124.84, 111.8]
        manual_pos['C5'] =[ 112.24, 111.8]
        manual_pos['C6'] =[ 99.44, 111.8]
        manual_pos['C7'] =[ 86.84, 111.8]
        manual_pos['C8'] =[ 74.24, 111.8]
        manual_pos['C9'] =[ 60.44, 111.8]
        
        manual_pos['D1'] =[ 162.44, 98.8]
        manual_pos['D2'] =[ 150.24, 98.6]
        manual_pos['D3'] =[ 137.84, 98.6]
        manual_pos['D4'] =[ 124.84, 98.6]
        manual_pos['D5'] =[ 112.24, 98.6]
        manual_pos['D6'] =[ 99.44, 98.6]
        manual_pos['D7'] =[ 86.84, 98.4]
        manual_pos['D8'] =[ 74.24, 98.4]
        manual_pos['D9'] =[ 60.44, 98.8]

        manual_pos['E1'] =[ 162.44, 85.8]
        manual_pos['E2'] =[ 150.44, 85.2]
        manual_pos['E3'] =[ 137.64, 85.2]
        manual_pos['E4'] =[ 124.84, 85.2]
        manual_pos['E5'] =[ 112.44, 85.2]
        manual_pos['E6'] =[ 99.64, 85.2]
        manual_pos['E7'] =[ 86.84, 85.0]
        manual_pos['E8'] =[ 74.04, 85.0]
        manual_pos['E9'] =[ 60.44, 85.8]

        manual_pos['F1'] =[ 162.44, 71.8]
        manual_pos['F2'] =[ 150.64, 72.0]
        manual_pos['F3'] =[ 138.04, 72.0]
        manual_pos['F4'] =[ 125.24, 71.8]
        manual_pos['F5'] =[ 112.44, 71.8]
        manual_pos['F6'] =[ 99.64, 71.8]
        manual_pos['F7'] =[ 87.04, 71.8]
        manual_pos['F8'] =[ 74.24, 71.6]
        manual_pos['F9'] =[ 60.44, 72.8]

        x, y = manual_pos[pos_des][0], manual_pos[pos_des][1]

        print('Sample: %s -- index-- %s -- motor position: [ %.3f, %.3f]'%(  pos_des, sample_number, x, y )  )
        RE(mov( mdx, x , mdy, y   ))
        sam = self._samples[  sample_number   ]
        if name is  None:
            sam.name = pos_des             
        else:
            sam.name = name 
        sam.name += extra
        return sam 
    

    # def gotoSample(self, sample_number):
        
    #     sample = self.getSample(sample_number, verbosity=0)
    #     #sample.gotoAlignedPosition()
    #     x, y = sample.origin()['x'], sample.origin()['y']
    #     RE(mov( mdx, x , mdy, y   ))
    #     return  self.get_sample_name(  rxn_pos ) 

    # def get_sample_name( self, rxn_pos, T=25):

    #     sample_index = self.dict_pos_ind[ rxn_pos ] #
    #     sam = self._samples[  sample_index   ]
    #     sam.name = rxn_pos + '_T%s'%T
    #     return sam 




    def addSamples(self, name):
        '''Name the samples in the well plate.  
        The format is 'NAME_A05_'
        '''

        #for row_number in range(1, 10):
            #for column in range(1, 7):

        for ii in range(54): #print(column)
            sample_name = '{}_{}'.format(name, ii+1)
            self.addSampleSlot( Sample(sample_name), ii+1)   

    def reset_clock_samples(self):
        for sample in self.getSamples():
            sample.reset_clock()


    def doSamples(self, extra=None, verbosity=3, **md):
        '''Activate the default action (typically measurement) for all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        for sample in self.getSamples_zigzag():
            if verbosity>=3:
                print('Doing sample {}...'.format(sample.name))
            sample.do(verbosity=verbosity, **md, extra=extra)


    def getSamples_zigzag(self, extra=None, verbosity=3, **md):
        '''Activate the default action (typically measurement) for all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        #sam_list = np.array( self.getSamples() )
        # roi_sam_ind = np.array( [ 54, 53, 52, 51, 50, 49, 48, 47, 46,  
        #                          37, 38, 39, 40, 41, 42, 43, 44, 45,
        #                          36, 35, 34, 33, 32, 31, 30, 29, 28, 
        #                          19, 20, 21, 22, 23, 24, 25, 26, 27,
        #                          18, 17, 16, 15, 14, 13, 12, 11, 10,
        #                           9, 8, 7, 6, 5, 4, 3, 2, 1                                 
        #                                                          ] )  # -1      


        self.roi_sam_ind = np.array([54, 53, 52, 51, 50, 49, 48, 47, 46,
                                 45, 44, 43, 42, 41, 40, 39, 38, 37,
                                 36, 35, 34, 33, 32, 31, 30, 29, 28,
                                 27, 26, 25, 24, 23, 22, 21, 20, 19,
                                18, 17, 16, 15, 14, 13, 12, 11, 10,
                                9,  8,  7,  6,  5,  4, 3,  2,  1 ])
        

        self.roi_pos_des = np.array(['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
                                         'B1', 'B2',  'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
         'C1', 'C2', 'C3', 'C4',  'C5', 'C6', 'C7', 'C8', 'C9',
           'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 
           'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8',   'E9',
             'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9'],  dtype='<U2') 
        
        self.roi_pos_des_eff = np.array([ 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                                          'B2',  'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
           'C8', 'C7', 'C6', 'C5', 'C4', 'C3', 'C2',
            'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 
           'E8', 'E7', 'E6', 'E5', 'E4', 'E3', 'E2',
            'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'],  dtype='<U2')        
        
        #self.dict_pos_ind = {  self.roi_pos_des[i]: self.roi_sam_ind[i] for i in range( 0, 54 )  }
        
        self.roi_pos_des = np.array(['A1', 'A2'],  dtype='<U2')     
        self.roi_sam_ind = np.array([ 1 ,2 ] ) 
        self.dict_pos_ind = {  self.roi_pos_des[i]: self.roi_sam_ind[i] for i in range( 0, 2 )  }

        ###return list( sam_list[ roi_sam_ind ]  ) 
        ###return list( sam_list[ np.array([53] ) ]  ) 
        #return self.roi_sam_ind
        #return [ 54, 53, 50 ] 

    def run_manual_0403( self,  exposure_time = 15 , init_sleep_time = 0 * 10,  rxn_pos='A2', 
                        rxn_time='5min', run_time = 60*60*10,   verbosity=3, 
                        sample_name = 'Tube_V38', **md):    
        '''
        2024C3_CMS: 2024/11/25
        For manual batch     
        smx: 85 
        hol.run_manual_1125( sample_name = 'Tube_V4' )

        2025C1_CMS: 2025/04/03         
        hol.run_manual_0403( sample_name = 'Tube_V4' )
        '''

        self.new_batch_num = 0
        #sam = self.goto_Pos( rxn_pos, extra = extra + '_' + rxn_time + '_batch_%s'%(self.new_batch_num)) # + '_'+ ts )
        sam = Sample( sample_name  +  '_batch_%s'%(self.new_batch_num)) 
        sam_name = sam.name 
        t0 = time.time()
        time.sleep( init_sleep_time )
        measure = False
        detselect( [ pilatus2M, pilatus8002 ] ) 
        while (time.time() < ( t0 + run_time) ):
            Batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            if Batch_push is not None:
                try:
                    try:
                        Batch_push = Batch_push['df'].item()
                    except:
                        Batch_push = Batch_push['df'][0]
                except:
                    pass

                if self.new_batch_num  in Batch_push.keys():  
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')

            Batch_T_t_dict = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)
            if Batch_T_t_dict is not None:
                try:
                    try:
                        Batch_T_t_dict = Batch_T_t_dict['df'].item()
                    except:
                        Batch_T_t_dict = Batch_T_t_dict['df'][0]
                except:
                    pass

                if self.new_batch_num+1 in Batch_T_t_dict.keys():  
                    measure = False
                    print('We stop the X-ray measurements for Batch %s.'%(self.new_batch_num))
                    self.new_batch_num+=1
                    #sam = self.goto_Pos( rxn_pos, extra = extra + '_' + rxn_time + '_batch_%s'%(self.new_batch_num))
                    sam = Sample( sample_name  +  '_batch_%s'%(self.new_batch_num)) 
                    sam_name = sam.name 

            if measure: 
                detselect( [ pilatus2M, pilatus8002 ] ) 
                sam.measure(   exposure_time , extra = get_current_time()  )

            else:
                time.sleep( 10  )
                print('Sleep 10 sec to wait for a new key: %s in batch_push dict.'%(self.new_batch_num))


    def run_continue_v2( self,  exposure_time = 15 , init_sleep_time = 0 * 10,  ntemp = 100, ntime= 22,
            sleep_time= 3, run_time = 3600*3,   verbosity=3, extra = '_Cluster_Run2_', **md):    
        
        '''
        For data-driven experiment using cluster (1 batch by 1 batch)        
        '''
        rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = ntime, 
                                                       tube_type= 'Kapton', push_flow = 80)                   
        
        sam = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(ntemp,ntime ) ) # + '_'+ ts )
        sam_name = sam.name 
        
        t0 = time.time()
        time.sleep( init_sleep_time )
        measure = False
        new_batch_num = self.new_batch_num +1
        while (time.time() < ( t0 + run_time) ):
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            
            if batch_push is not None:
                try:
                    try:
                        batch_push = batch_push['df'].item()
                    except:
                        batch_push = batch_push['df'][0]
                except:
                    pass

                if new_batch_num in batch_push.keys():  
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')
            if measure: 
                sam.measure(   exposure_time )
            else:
                time.sleep( 60  )
                print('Sleep 60 sec to wait for a new key in batch_push dict.')



    def run_continue_0217nite( self,  exposure_time = 15 , init_sleep_time = 0 * 10,  init_pos = 'B4',
            sleep_time= 3, run_time = 35*60,    verbosity=3, 
            extra = '_T95_tscan_Run16', **md):    
        
        '''
        manual batch system, but keep measuring (no time to test batch_push...) 
        
        '''
        sam = self.goto_Pos( init_pos, extra = extra   )
        t0 = time.time()
        time.sleep( init_sleep_time )
        # measure = False
        # new_batch_num = self.new_batch_num
        while (time.time() < ( t0 + run_time) ):
            # batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            
            # if batch_push is not None:
            #     try:
            #         try:
            #             batch_push = batch_push['df'].item()
            #         except:
            #             batch_push = batch_push['df'][0]
            #     except:
            #         pass

            #     if new_batch_num in batch_push.keys():  
            #         #batch_push, a dict, starting from 0, 
            #         # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
            #         measure = True
            #         print('We can start the X-ray measurements.')
            measure = True
            if measure: 
                sam.measure(   exposure_time )
                time.sleep(1)
            # else:
            #     time.sleep( 60  )
            #     print('Sleep 60 sec to wait for a new key in batch_push dict.')


    def run_continue( self,  exposure_time = 15 , init_sleep_time = 0 * 10,  init_pos = 'E5',
            sleep_time= 3, run_time = 3600*3,   verbosity=3, extra = '_T100_Identify_Drops_Three', **md):    
        
        '''
        extra = '_T100_Identify_Drops' to identify the droplet, aqu_time = 30 ,  init_pos = 'D7' for reaction time = 15 min 
        extra = '_T100_Identify_Drops_Two' , aqu_time = 15 , init_pos = 'D7' for reaction time = 10 min  
        
        '''
        sam = self.goto_Pos( init_pos, extra = extra   )
        t0 = time.time()
        time.sleep( init_sleep_time )

        measure = False
        new_batch_num = self.new_batch_num
        while (time.time() < ( t0 + run_time) ):
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            
            if batch_push is not None:
                try:
                    try:
                        batch_push = batch_push['df'].item()
                    except:
                        batch_push = batch_push['df'][0]
                except:
                    pass

                if new_batch_num in batch_push.keys():  
                    #batch_push, a dict, starting from 0, 
                    # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
                    measure = True
                    print('We can start the X-ray measurements.')
            if measure: 
                sam.measure(   exposure_time )
            else:
                time.sleep( 60  )
                print('Sleep 60 sec to wait for a new key in batch_push dict.')

    def run_time_scan_0219( self,   exposure_time = 15, init_sleep_time = 60 * 0, 
                verbosity=3,  extra = '_tscan_Run13_Recp1_T' ,**md):
        
        Pos = self.roi_pos_des_eff 
        t0 = time.time()
        Temp_study = 100
        time.sleep(init_sleep_time)
        for p in Pos:
            ts = get_current_time()
            sam = self.goto_Pos( p, extra = extra +str(Temp_study) + '_'+ ts )
            for i in range(16):
                print( '%i times for measuring sample = %s.'%(i+1, sam.name)  )
                sam.measure(   exposure_time )
                time.sleep( 1 )


    def quick_z_measurement(self, exposure_time = 10, label = '0405_8capillary', 
                            pos_x = 171.04, pos_z1 = 92.6, pos_z2= 96, z_step=0.2):
        
        '''
        2025_0405
        capillary
        x1 = 139, 145.5, 151.8, 158.1, 164.5, 171.04
        '''
        zrange = np.arange(pos_z1, pos_z2, z_step)
        for z in zrange:
            RE(mov( mdx, pos_x , mdy, z   ))
            sam = Sample ( label + '_x:' + str(mdx.position) + '_z:' + str(mdy.position) +'_'+ get_current_time())
            sam.measure(exposure_time)



    def run_time_dependent_0221( self,   exposure_time = 15, run_time = 3600*18, 
                                extra = '_tscan_Run13_Recp1_T',
                 Temps=[100,105,95],new_batch_num=0, **md):
        
        #new_batch_num = self.new_batch_num
        Batch_T_t_dict={}
        Pos = self.roi_pos_des_eff[::-1] 
        t0 = time.time()
        measure=False
        while (time.time() < ( t0 + run_time) ):
            batch_push = try_load_npz(  self.base + 'Batch_push.npz')
            if batch_push is not None:
                try:
                    try:
                        batch_push = batch_push['df'].item()
                    except:
                        batch_push = batch_push['df'][0]
                except:
                    pass
                if new_batch_num in batch_push.keys():  
                    measure = True
                    print('We can start the X-ray measurements.')
                if measure:
                    for p in Pos:
                        ts = get_current_time()
                        sam = self.goto_Pos( p, extra = extra +str(Temps[new_batch_num]) + '_'+ ts )
                        for i in range(8):
                            print( '%i times for measuring sample = %s.'%(i+1, sam.name)  )
                            sam.measure(   exposure_time )
                        # time.sleep( .2 )
                    Batch_T_t_dict[new_batch_num] = ['Done']
                    print(Batch_T_t_dict)
                    try_save_npz(  self.base + 'Batch_T_t_dict.npz',  Batch_T_t_dict)
                    new_batch_num+=1
                    measure=False
            else:
                time.sleep( 60  )
                print('Sleep 60 sec to wait for a new key in batch_push dict.')
            # time.sleep( 60  )
            # print('Sleep 60 sec to wait for a new key in batch_push dict.')



    def run_time_scan( self,   exposure_time = 15, init_sleep_time = 60 * 0, 
                verbosity=3, run_time = 3600*18, extra = '_tscan_Run4_Recp1_T', **md):
        new_batch_num = self.new_batch_num
        Batch_T_t_dict={}
        Pos = self.roi_pos_des_eff[::-1] 
        t0 = time.time()
        Temp_study = 80
        measure=False
        while (time.time() < ( t0 + run_time) ):
            batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
            if batch_push is not None:
                try:
                    try:
                        batch_push = batch_push['df'].item()
                    except:
                        batch_push = batch_push['df'][0]
                except:
                    pass
                if new_batch_num in batch_push.keys():  
                    measure = True
                    print('We can start the X-ray measurements.')
                if measure:
                    for p in Pos:
                        ts = get_current_time()
                        sam = self.goto_Pos( p, extra = extra +str(Temp_study) + '_'+ ts )
                        for i in range(8):
                            print( '%i times for measuring sample = %s.'%(i+1, sam.name)  )
                            sam.measure(   exposure_time )
                        # time.sleep( .2 )
                    Batch_T_t_dict[new_batch_num] = ['Done']
                    print(Batch_T_t_dict)
                    try_save_npz(  self.base + 'Batch_T_t_dict.npz',  Batch_T_t_dict)
                    new_batch_num+=1
                    Temp_study -=10
                    measure=False
                else:
                    time.sleep( 60  )
                    print('Sleep 60 sec to wait for a new key in batch_push dict.')

            else:
                time.sleep( 60  )
                print('Sleep 60 sec to wait for a new key in batch_push dict.')




    def run_batch_0220( self, new_batch_num = None, exposure_time = 15, init_pos = 'A3',
                       init_temp = 'T100', init_time='t4min',
            sleep_time= 3, run_time = 3600*20, extra='_PVP_Run12',  verbosity=3, **md): 
        
        '''
        02/19/2024
        extra: Run2 --> manual 7 batch (16 NPs each)
        extra: Run3 --> manual 7 batch (16 NPs each) (change beam position to center)
        '''
        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num       
        sam = self.goto_Pos( init_pos, extra = extra + '_' + init_temp+  '_' + init_time   )
        sam_name = sam.name 
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
                    rxn_pos, push_flow, push_vol = self.reactor.find_new_position(target_time= next_time )                   
                    
                    sam = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    sam_name = sam.name 
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num

            if measure:
                ts = get_current_time()
                sam.name = sam_name  + '_%s'%ts  
                sam.measure(  exposure_time   )

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1




    def run_batch( self, new_batch_num = None, exposure_time = 15, init_pos = 'F3',
            sleep_time= 3, run_time = 3600*20, extra='_Batch_UV2', push_flow = 80, verbosity=3, **md): 
        
        '''
        9/22/2023, run two uv batches, T80t20m 
        hol.run_batch() _Batch_UV1

        9/23/2023
        run two batches for best predicted from GP model 
        _Batch_Best_pred1
        
        '''
        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num                   
        sam = self.goto_Pos( init_pos, extra = extra + '_T80_t5min'   )
        sam_name = sam.name 
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
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, 
                                                                   tube_type= 'Kapton', push_flow = push_flow)                   
                    
                    sam = self.goto_Pos( rxn_pos, extra = extra + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    sam_name = sam.name 
                    new_batch_num += 1
                    self.new_batch_num  = new_batch_num

            if measure:
                ts = get_current_time()
                sam.name = sam_name  + '_%s'%ts  
                sam.measure(  exposure_time   )

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1



    def run( self, new_batch_num = None, exposure_time = 15, #init_pos = 'D2', init_com='',_
            sleep_time= 3, run_time = 3600*24, extra='_Batch_Auto_Run3_', push_flow = 80, verbosity=3, **md): 
        
        '''
        using old data
        '_Batch_Auto_Run1_'
        9/22/2023, start from 7:10 pm
        failed due to the 1+batch_number in the laptop code V7b

        '_Batch_Auto_Run2_', 8:50 pm




        '''
        cts=0
        if new_batch_num is  None:
            new_batch_num = self.new_batch_num                   
        #sam = self.goto_Pos( init_pos, extra = extra +   init_com )
        #sam_name = sam.name 
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
                    rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, tube_type= 'Kapton', push_flow = push_flow)                   
                    
                    sam = self.goto_Pos( rxn_pos, extra = extra  + '_T%s_t%smin'%(next_temp,next_time ) ) # + '_'+ ts )
                    sam_name = sam.name 
                    new_batch_num += 1
                    print( 'move to position=%s - sample_name=%s-batch_num=%s'%( rxn_pos, sam_name, new_batch_num ))                    
                    self.new_batch_num  = new_batch_num
            if measure:
                ts = get_current_time()
                sam.name = sam_name  + '_%s'%ts  
                sam.measure(  exposure_time   )

            else:
                time.sleep( sleep_time  )
                if cts%10 ==0 :
                    print('Sleep %s sec to wait for a new key in batch_push dict.'%(cts* sleep_time) )

                cts+=1






    # def run_need_tested( self, new_batch_num = None, exposure_time = 30, init_pos = 'D7',
    #         sleep_time= 3, run_time = 3600*10, extra='', verbosity=3, **md): 
        
    #     sam = self.goto_Pos( init_pos, extra = extra   )

    #     if new_batch_num is  None:
    #         new_batch_num = self.new_batch_num

    #     t0 = time.time()
    #     measure = False                   
 
    #     while (time.time() < ( t0 + run_time) ):
                          
    #         ''' Load "Batch_T_t_dict" suggested from BoTorch'''
    #         batch_push = try_load_npz(  self.base + 'Batch_push.npz',  n_loop=3, sleep_time=0.02)
    #         batch_Tt = try_load_npz(  self.base + 'Batch_T_t_dict.npz',  n_loop=3, sleep_time=0.02)

    #         if batch_push is not None:
    #             try:
    #                 batch_push = batch_push['df'].item()
    #             except:
    #                 batch_push = batch_push['df'][0]

    #             if new_batch_num in batch_push.keys():  
    #                 #batch_push, a dict, starting from 0, 
    #                 # e.g., { 0: [ batch_init_0,  batch_init_1, batch_init_2, batch_init_3, ]   }
    #                 measure = True
    #                 print('We can start the X-ray measurements.')

    #         if batch_Tt is not None:
    #             try:
    #                 batch_Tt = batch_Tt['df'].item()
    #             except:
    #                 batch_Tt = batch_Tt['df'][0]

    #             if (1 + new_batch_num)  in batch_Tt.keys():
    #                 #batch_Tt, a dict, also starting from 1, but this 1 will be same as the 1 in the push one
    #                 #there is no key=0 in batch_Tt
    #                 # e.g., { 1: [ batch_1_0,  batch_1_1, batch_1_2, batch_1_3, ]   }                    
    #                 measure = False
    #                 print('We are preparing a new batch and will stop the X-ray measurements.') 
    #                 next_temp =   batch_Tt[new_batch_num+1][0] #in deg
    #                 next_time =  batch_Tt[new_batch_num+1][1] #in min 
    #                 rxn_pos, push_flow, push_vol = Find_new_pos_fr(Target_time = next_time, tube_type= 'Kapton', push_flow = 80 )
    #                 self.go_to_pos( rxn_pos )
    #                 sample_index = self.dict_pos_ind[ rxn_pos ] #
    #                 sam = self._samples[  sample_index   ]
    #                 sam.name = rxn_pos + '_T%s'%next_temp 
    #                 new_batch_num += 1
    #                 self.new_batch_num  = new_batch_num

    #         if measure:
    #             sam.measure(  exposure_time   )

    #         else:
    #             time.sleep( sleep_time  )
    #             print('Sleep %s sec to wait for a new key in batch_push dict.'%sleep_time)







 
    
    def doSamples_all( self, extra=None, verbosity=3, **md):
        '''Activate the default action (typically measurement) for all the samples.
        
        If the optional range argument is provided (2-tuple), then only sample
        numbers within that range (inclusive) are run. If range is instead a 
        string, then all samples with names that match are returned.'''
        
        #N = 10 
        N= 5
        
        maxs_on()
        for sample_index in self.getSamples_zigzag()[::-1]:
            sample = hol.gotoSample( sample_index )
            for i in range( N ):                
                sample.measure(**md, extra=extra)

        saxs_on()
        for sample in self.getSamples_zigzag():
            sample = hol.gotoSample( sample_index )
            for i in range( N ):                
                sample.measure(**md, extra=extra)
 
 
 


hol = DropletHolder()
hol.addSamples( 'test' )
#hol.getSamples_zigzag()
#sam = hol.gotoSample( 54 


#cms.SAXS.setCalibration([731, 1680-580], 3.0, [-65, -73])
#cms.SAXS.setCalibration([756-3, 1079+1], 5.0, [-65, -73])   #5m,13.5kev, 
#RE.md['experiment_alias_directory'] = '/nsls2/data/cms/legacy/xf11bm/data/2024_3/YZhang/'


# smx = EpicsMotor('XF:11BM-ES{Mdrive-Ax:X}Mtr', name='smx')
# smy = EpicsMotor('XF:11BM-ES{Mdrive-Ax:Y}Mtr', name='smy')




# if True:
    
#     # cali = CapillaryHolder(base=stg)
#     cali = CapillaryHolderCustom(base=stg)
    
#     cali.addSampleSlot( Sample('FL_screen'), 5.0 )
#     cali.addSampleSlot( Sample('AgBH_cali_5.8m_17kev'), 8.0 )
#     cali.addSampleSlot( Sample('Empty'), 11.0 )
#     cali.addSampleSlot( Sample(''), 15.0 )



'''
#new beamstop setup at 2024C3, Nov

rod bs

In [204]: wbs()
bsx = -16.200314
bsy = 17.000503
bsphi = -182.500528



round bs 


In [179]: wbs()
bsx = -12.800009999999999
bsy = -13.900005
bsphi = -64.0


-->


In [60]: config_update()
In [61]: wbs()
bsx = -18.04
bsy = -10.899688999999999
bsphi = -64.00231699999999
In [62]: config_load()
In [63]: 


 





bottom left hole

In [268]: wsam()
smx = 71.6002625
smy = 61.3003694999999




for MDrive setting
have a trouble to run the mdrive ioc
1) restart the small computer -->  not workking, show purple on css
2) restart the IOC -->  ssh epics@xf11bm-ecat1 , pass: rdg_725
sudo manage-iocs status
sudo manage-iocs stop  mdrive
sudo manage-iocs start  mdrive
#sudo manage-iocs restart  mdrive
--> not working, the css show purple
3) try a different usb, working

4) setup for the MDrive
motor resolution: 9.750000E-5
encode res: 9.750000E-5
speed: max 5 mm/s, 2.5 mm/s for 'normal' speed


'''


'''
202411

calibration

Maxs

555, 363, 
215mm



'''
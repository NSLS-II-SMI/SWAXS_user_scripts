pil2M.stats2.kind = 'hinted'
pil2M.stats2.total.kind = 'hinted'

pil2M.stats3.kind = 'hinted'
pil2M.stats3.total.kind = 'hinted'

# pil2M.beam_offset_y_mm.set(190.404+2*0.172)
pil2M.beam_offset_y_mm.set(190.404+5*0.172)
#RE(smi.setDirectBeamROI())


def run_xrr_bdm_saxs(start_angle, stop_angle, num_steps, det=pil2M, atten=None, bdm_sample_distance=183):
    """
    Perform XRR scan by bouncing down the mirror from start_angle to stop_angle.
    """
    angles = np.linspace(start_angle, stop_angle, num_steps)
    ai0 = bdm.th.get()
    det_exposure_time(1, 1)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=ai0)
    yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from bps.mv(bdm.th, ai0 + angle)
            yield from smi.setReflectedBeamROI(total_angle=-angle, 
                                               technique="gisaxs",
                                               sample_z_offset_mm=bdm_sample_distance)
            sample_name = f'XRR_bounce_down_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle])
        yield from bps.mv(bdm.th, ai0)
    return (yield from inner())


def run_xrr_bdm_waxs(start_angle, stop_angle, num_steps, det=pil900KW, atten=None):
    """
    Perform XRR scan by bouncing down the mirror from start_angle to stop_angle.
    """
    angles = np.linspace(start_angle, stop_angle, num_steps)
    ai0 = bdm.th.get()
    det_exposure_time(1, 1)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=ai0)
    yield from smi.modeAlignment(technique = "giwaxs")
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from bps.mv(bdm.th, ai0 + angle)
            yield from smi.setReflectedBeamROI(total_angle=-angle, 
                                               technique="giwaxs",
                                               roi=pil900KW.roi1,
                                               sample_z_offset_mm=190)
            sample_name = f'XRR_bounce_down_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.trigger_and_read([det] + [s,incident_angle])
        yield from bps.mv(bdm.th, ai0)
    return (yield from inner())

    

def get_bdm_pos():
    """
    Get the current position of the piezo-driven mirror (PDM).
    """
    x = bdm.x.get()
    y = bdm.y.get()
    th = bdm.th.get()
    print(f"PDM Position - X: {x}, Y: {y}, Theta: {th}")
    return x, y, th


def get_piezo_pos():
    """
    Get the current position of the piezo-driven mirror (PDM).
    """
    y = piezo.y.position
    th = piezo.th.position
    print(f"Sample Position - Y: {y}, Theta: {th}")
    return y, th



def check_bdm_refection(angle, bdm_th_origin, det=pil2M, sample_z_offset_mm=183):
    '''check the reflection on the detector at a bdm angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''

    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(bdm.th, bdm_th_origin + angle)
    print(f'current at bdm_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=-angle, technique="gisaxs",sample_z_offset_mm=sample_z_offset_mm)

    yield from count([det]) # count direct beam # exposure time is 0.3s


def move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183):
    y_offset = np.tan(np.deg2rad(2*alpha)) * bdm_sample_distance * 1000  # in um
    new_y = piezo_y_origin - y_offset
    new_th = bdm_th_origin + alpha
    print(f'geometric calculation: for alpha={alpha}deg, y_offset={y_offset}um')
    print(f"Moved sample to Y: {new_y}, Theta: {new_th}")
    yield from bps.mv(bdm.th, new_th, piezo.y, new_y)
    

    saxs_sdd_offset = 183 - bdm_sample_distance # from bdm reflectivity and 185mm is good
    print(f'saxs_sdd_offset: {saxs_sdd_offset}mm')

    print('Setting direct beam from bdm using ROI2')
    yield from smi.setReflectedBeamROI(total_angle=-alpha, 
                                        technique="gisaxs",
                                        sample_z_offset_mm=saxs_sdd_offset+bdm_sample_distance,
                                        roi=pil2M.roi2)

    print('Setting reflected beam from sample using ROI3')
    # yield from smi.setReflectedBeamROI(total_angle=alpha, 
    #                                     technique="bdm_gisaxs",
    #                                     sample_y_offset_mm=-y_offset/1000,
    #                                     roi=pil2M.roi2)

    yield from smi.setReflectedBeamROI(total_angle=alpha, 
                                        technique="gisaxs",
                                        sample_z_offset_mm=-bdm_sample_distance+saxs_sdd_offset,
                                        size=[48, 8*3],
                                        roi=pil2M.roi3)


def scan_knife_edge(rang=200, point=41, der=True, roi = 2):
    """
    Align GISAXS height using a relative scan.

    Parameters:
        rang (float): Range for the scan.
        point (int): Number of points in the scan.
        der (bool): Whether to calculate the derivative.
    """
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    if roi == 1:
        ps(der=der, suffix='_stats1_total', plot=True)
    elif roi == 2:
        ps(der=der, suffix='_stats2_total', plot=True)
    else:
        print('using the default roi')
        ps(der=der, plot=True)
    print(f'The peak center is {ps.cen:.1f}')
    yield from bps.mv(piezo.y, ps.cen)
    return ps.cen


# angles=[0, 0.05, 0.1, 0.16, 0.2, 0.25, 0.3, 0.36, 0.4]
def scan_bdm_angle_sh_knife_edge(angles, piezo_y_origin, bdm_y_origin, bdm_th_origin, bdm_sample_distance=183):
    '''at different bdm angle, scan the sample height using a knife edge'''
    sh_cen_list = []
    for angle in angles:
        if angle == 0:
            yield from mv(bdm.y, bdm_y_origin-2)
        else:
            yield from mv(bdm.y, bdm_y_origin)
        yield from move_bdm_sample(alpha=angle,piezo_y_origin=piezo_y_origin,bdm_th_origin=bdm_th_origin,bdm_sample_distance=bdm_sample_distance)
        _sh_cen = yield from scan_knife_edge()
        sh_cen_list.append(_sh_cen)

    print(f'BDM angle list {angles}')
    print(f'piezo.y center list {sh_cen_list}')



def run_xrr_bdm_xpos(xpos=[2.5, -5.5]):
    '''Move BDM X to specified positions and perform alignment and run XRR scan.'''

    for x in xpos:
        yield from bps.mv(bdm.x, x)
        print(f"Set BDM x to {x}")

        yield from alignment_bdm()
        yield from bps.mvr(bdm.y, -1)
        yield from smi.setDirectBeamROI()
        yield from count([pil2M]) # count direct beam # exposure time is 0.3s
        yield from bps.mvr(bdm.y, 1)
        yield from bps.sleep(1)
        yield from run_xrr_bdm_saxs(0,0.45,181) # expsoure time is 1s




def check_gisaxs_refection_without_bdm(angle, piezo_th_origin, det=pil2M):
    '''check the reflection on the detector at a piezo angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''

    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(piezo.th, piezo_th_origin + angle)
    print(f'current at piezo th_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    yield from count([det]) # count direct beam # exposure time is 0.3s



def check_liquid_refection_with_bdm(bdm_angle, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183, det=pil2M):
    '''check the reflection on the detector at bdm angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''

    yield from move_bdm_sample(alpha=bdm_angle,
                               piezo_y_origin=piezo_y_origin,
                               bdm_th_origin=bdm_th_origin,
                               bdm_sample_distance=bdm_sample_distance)

    
    print(f'current at bdm angle = {bdm_angle} deg')
    yield from bps.sleep(1)

    yield from count([det]) # count direct beam # exposure time is 0.3s

# alpha_list=[0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2]
def scan_y_reflected_beam_from_sample(alpha_list, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183):
    '''Scan reflected beam from sample by varying the BDM angle and adjusting sample position accordingly.'''

    Y_original = []
    Y_peak_cen = []
    
    for alpha in alpha_list:
        yield from move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)
        else:
            det_exposure_time(1, 1)
        # yield from smi.setReflectedBeamROI(0, roi=pil2M.roi3) # use roi3 for direct beam
        yield from count([pil2M]) # exposure time is 0.3s
        Y_original.append(piezo.y.position)
        yield from rel_scan([pil2M], piezo.y, -150, 150, 61) # exposure time is 0.3s
        
        ps(der=False, suffix='_stats3_total', plot=True)
        print(f'The peak center is {ps.cen:.2f}')
        Y_peak_cen.append(ps.cen)

        # yield from rel_scan([pil2M], piezo.th, -0.1, 0.1, 51) # exposure time is 0.3s
    
    # Move back to original position
    yield from move_bdm_sample(0, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
    
    print(f'angle list {alpha_list}')
    print(f'piezo.y original position {Y_original}')
    print(f'piezo.y center list {Y_peak_cen}')
    # return Y_original,Y_peak_cen


# alpha_list=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
def scan_th_reflected_beam_from_sample(alpha_list, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183):
    '''Scan reflected beam from sample by varying the BDM angle and adjusting sample position accordingly.'''

    th_original = []
    th_peak_cen = []
    
    for alpha in alpha_list:
        yield from move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)
        else:
            det_exposure_time(1, 1)
        # yield from smi.setReflectedBeamROI(0, roi=pil2M.roi3) # use roi3 for direct beam
        yield from count([pil2M]) # exposure time is 0.3s
        th_original.append(piezo.th.position)
        yield from rel_scan([pil2M], piezo.th, -0.05, 0.05, 51) # exposure time is 0.3s
        
        ps(der=False, suffix='_stats3_total', plot=True)
        print(f'The peak center is {ps.cen:.2f}')
        th_peak_cen.append(ps.cen)

        # yield from rel_scan([pil2M], piezo.th, -0.1, 0.1, 51) # exposure time is 0.3s
    
    # Move back to original position
    yield from move_bdm_sample(0, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
    
    print(f'angle list {alpha_list}')
    print(f'piezo.y original position {th_original}')
    print(f'piezo.y center list {th_peak_cen}')
    # return Y_original,Y_peak_cen


def xrr_scan_liquid_using_bounced_beam(start_angle,stop_angle,num_steps, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183, det=pil2M):

    """
    Perform XRR scan from a liquid sample using the bounced beam.
    Both liquid sample and BDM need to go to origin before the run
    The data is at ROI3
    """
    angles = np.linspace(start_angle, stop_angle, num_steps)
    det_exposure_time(1, 1)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    # yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from move_bdm_sample(angle, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
            saxs_sdd_offset = 183 - bdm_sample_distance # from bdm reflectivity and 185mm is good
            yield from smi.setReflectedBeamROI(total_angle=angle, 
                                                technique="gisaxs",
                                                size=[48, 8*3],
                                                sample_z_offset_mm=-bdm_sample_distance+saxs_sdd_offset,
                                                roi=pil2M.roi3)

            yield from att_selection_8keV(angle*2)

            sample_name = f'XRR_bounced_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle])

    return (yield from inner())


# alpha_list=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
def scan_reflected_beam_from_sample_without_bdm(alpha_list, piezo_th_origin):
    '''Scan reflected beam from sample by varying the piezo angle'''

    th_original = []
    th_peak_cen = []
    
    for angle in alpha_list:

        # move to theta 0 + value
        yield from bps.mv(piezo.th, piezo_th_origin + angle)
        print(f'current at piezo th_angle = {angle} deg')

        # Set reflected ROI for beam bending down
        yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
        yield from bps.sleep(1)
        if angle <=0.3:
            det_exposure_time(0.3, 0.3)
        else:
            det_exposure_time(1, 1)
        th_original.append(piezo.th.position)
        yield from count([pil2M]) # exposure time is 0.3s
        yield from bps.mv(piezo.th, piezo_th_origin + angle + (angle-0.1)*0.25)
        yield from rel_scan([pil2M], piezo.th, -0.05, 0.05, 51) # exposure time is 0.3s
        
        ps(der=False, suffix='_stats1_total', plot=True)
        print(f'The peak center is {ps.cen:.2f}')
        th_peak_cen.append(ps.cen)
    
    print(f'angle list {alpha_list}')
    print(f'piezo.th original position {th_original}')
    print(f'piezo.th center list {th_peak_cen}')



def run_xrr_solid_substrate_using_direct_beam(start_angle,stop_angle,num_steps, piezo_th_origin,det=pil2M):

    """
    Perform XRR scan from a solid substrate sample using the direct beam without bdm.
    BDM needs to be removed
    The data is at ROI1
    """
    angles = np.linspace(start_angle, stop_angle, num_steps)
    det_exposure_time(1, 1)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    # yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'Si substrate'})
    def inner():
        for angle in angles:
            yield from bps.mv(piezo.th, piezo_th_origin + peizo_th_correction(angle))
            yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", size=[48, 12])
            yield from att_selection_8keV(angle)
            sample_name = f'XRR_directbeam_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle])

    return (yield from inner())



def peizo_th_correction(th_target, slope=1.281629, intercept=0.001648, th_aligned=0.1):
    '''The sample substrate is alinged at peizo_th_for_aligned=0.1
    slope = 1.281629
    intercept = 0.001648
    '''

    actual_motion = (th_target-th_aligned)*slope + intercept + th_aligned

    return actual_motion

    
def check_gisaxs_refection_th_corrected(angle, piezo_th_origin, det=pil2M):
    '''check the reflection on the detector at a piezo angle with motion correction
    TODO: currently only for SAXS; need to adjust for WAXS
    '''

    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(piezo.th, piezo_th_origin + peizo_th_correction(angle))
    print(f'current at piezo th_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    yield from count([det]) # count direct beam # exposure time is 0.3s


def atten_move_in(att_list):
    """
    Move attenuators in
    """
    print('Moving attenuators in')
    for att in att_list:
        while att.status.get() != 'Open':
            yield from bps.mv(att.open_cmd, 1)
            yield from bps.sleep(1)

def atten_move_out(att_list):
    """
    Move attenuators out
    """
    print('Moving attenuators out')
    for att in att_list:
        while att.status.get() != 'Not Open':
            yield from bps.mv(att.close_cmd, 1)
            yield from bps.sleep(1)




def att_selection_8keV(angle):
    """
    Move Mo 20um

    angle,      filter      atten
    0-0.3       x4, x1      att2_3, att2_1
    0.3-0.55    x4          att2_3
    0.55-0.9    x2, x1      att2_2, att2_1
    0.9-1.1     x2          att2_2
    1.1-1.28    x1          att2_1
    1.28-2      NA          NA

    """
    if angle < 0:
        print('angle is nagetive!')
        return
    elif angle < 0.3:
        att_in = [att2_3, att2_1]
        att_out = [att2_2]
    elif angle < 0.55:
        att_in = [att2_3]
        att_out = [att2_1, att2_2]
    elif angle < 0.9:
        att_in = [att2_2, att2_1]
        att_out = [att2_3]
    elif angle < 1.1:
        att_in = [att2_2]
        att_out = [att2_1, att2_3]
    elif angle < 1.28:
        att_in = [att2_1]
        att_out = [att2_2, att2_3]
    elif angle < 2:
        att_in = []
        att_out = [att2_1, att2_2, att2_3]
    else:
        print('angle is too big!')
        return
    if len(att_in)>0:
        yield from atten_move_in(att_in)
    if len(att_out)>0:
        yield from atten_move_out(att_out)



def alignment_gisaxs_using_bdm_bonced_beam(angle=0.1, alpha_bdm=0.05, bdm_sample_distance=185):
    """
    TODO: this function is not done yet...

    Alignment routine for GISAXS using bounced beam from BDM as the direct beam (bdm_alpha=0.05)
    
    First, scan the sample height and incident angle on the direct beam.
    Then scan the incident angle, height, and incident angle again on the reflected beam.

    Parameters:
        angle (float): Angle at which the alignment on the reflected beam will be done.
    """
    

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    # yield from smi.setDirectBeamROI()
    yield from smi.setReflectedBeamROI(total_angle=-alpha_bdm, 
                                    technique="gisaxs",
                                    sample_z_offset_mm=bdm_sample_distance)

    # Scan theta and height
    yield from align_gisaxs_height(800, 21, der=True)
    yield from align_gisaxs_th(1.5, 27)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    # yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
    yield from smi.setReflectedBeamROI(total_angle=angle, 
                                    technique="gisaxs",
                                    sample_z_offset_mm=-bdm_sample_distance,
                                    roi=pil2M.roi1)

    # Scan theta and height
    yield from align_gisaxs_th(0.2, 21)
    yield from align_gisaxs_height_rb(150, 16)
    yield from align_gisaxs_th(0.1, 31)  # was .025, 21 changed to .1 31


    # Scan theta and height finer
    yield from align_gisaxs_height_rb(50, 41)
    yield from align_gisaxs_th(0.05, 31)  # was .025, 21 changed to .1 31


    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mv(piezo.th, piezo.th.position-angle)
    # yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False










# def atten_move_in():
#     """
#     Move 4x + 2x Sn 60 um attenuators in
#     """
#     print('Moving attenuators in')

#     while att1_7.status.get() != 'Open':
#         yield from bps.mv(att1_7.open_cmd, 1)
#         yield from bps.sleep(1)
#     while att1_6.status.get() != 'Open':
#         yield from bps.mv(att1_6.open_cmd, 1)
#         yield from bps.sleep(1)

# def atten_move_out():
#     """
#     Move 4x + 2x Sn 60 um attenuators out
#     """
#     print('Moving attenuators out')
#     while att1_7.status.get() != 'Not Open':
#         yield from bps.mv(att1_7.close_cmd, 1)
#         yield from bps.sleep(1)
#     while att1_6.status.get() != 'Not Open':
#         yield from bps.mv(att1_6.close_cmd, 1)
#         yield from bps.sleep(1)
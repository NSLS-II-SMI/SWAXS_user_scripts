

pil2M.stats2.kind = 'hinted'
pil2M.stats2.total.kind = 'hinted'

pil2M.stats3.kind = 'hinted'
pil2M.stats3.total.kind = 'hinted'

pil2M.beam_offset_y_mm.set(190.404+2*0.172)
#RE(smi.setDirectBeamROI())


def run_xrr_bdm_saxs(start_angle, stop_angle, num_steps, det=pil2M, atten=None, bdm_sample_distance=185):
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

def move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance=185):
    y_offset = np.tan(np.deg2rad(2*alpha)) * bdm_sample_distance * 1000  # in um
    new_y = piezo_y_origin - y_offset
    new_th = bdm_th_origin + alpha
    print(f'geometric calculation: for alpha={alpha}deg, y_offset={y_offset}um')
    print(f"Moved sample to Y: {new_y}, Theta: {new_th}")
    yield from bps.mv(bdm.th, new_th, piezo.y, new_y)
    

    saxs_sdd_offset = 185 - bdm_sample_distance # from bdm reflectivity and 185mm is good
    print(f'saxs_sdd_offset: {saxs_sdd_offset}mm')

    print('Setting direct beam from bdm using ROI2')
    yield from smi.setReflectedBeamROI(total_angle=-alpha, 
                                        technique="gisaxs",
                                        sample_z_offset_mm=saxs_sdd_offset+bdm_sample_distance,
                                        roi=pil2M.roi2)

    print('Setting reflected beam from sample using ROI1')
    # yield from smi.setReflectedBeamROI(total_angle=alpha, 
    #                                     technique="bdm_gisaxs",
    #                                     sample_y_offset_mm=-y_offset/1000,
    #                                     roi=pil2M.roi2)

    yield from smi.setReflectedBeamROI(total_angle=alpha, 
                                        technique="gisaxs",
                                        sample_z_offset_mm=-bdm_sample_distance+saxs_sdd_offset,
                                        roi=pil2M.roi1)

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



def scan_reflected_beam_from_sample(alpha_list=[0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2], bdm_sample_distance=185):
    '''Scan reflected beam from sample by varying the BDM angle and adjusting sample position accordingly.'''

    
    for alpha in alpha_list:
        yield from move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)
        else:
            det_exposure_time(2, 2)
        yield from smi.setReflectedBeamROI(0, roi=pil2M.roi3) # use roi3 for direct beam
        yield from count([pil2M]) # exposure time is 0.3s
        yield from rel_scan([pil2M], piezo.y, -150, 150, 61) # exposure time is 0.3s
        yield from rel_scan([pil2M], piezo.th, -0.1, 0.1, 51) # exposure time is 0.3s
    
    # Move back to original position
    yield from move_bdm_sample(0, piezo_y_origin, bdm_th_origin, bdm_sample_distance)



def scan_reflected_beam_from_sample_without_bdm(alpha_list=[0.04, 0.06, 0.08, 0.1, 0.12, 0.18, 0.2, 0.25, 0.3]):
    '''Scan reflected beam from sample by varying the piezo height and angle'''

    for alpha in alpha_list:
        yield from bps.mv(piezo.th, alpha + piezo_th_origin)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)
        else:
            det_exposure_time(2, 2)
        
        yield from smi.setReflectedBeamROI(alpha) # use roi1 for reflected beam from sample
        yield from smi.setReflectedBeamROI(0, roi=pil2M.roi3) # use roi3 for direct beam
        yield from count([pil2M]) # exposure time is 0.3s
        yield from rel_scan([pil2M], piezo.y, -150, 150, 61) # exposure time is 0.3s
        yield from rel_scan([pil2M], piezo.th, -0.1, 0.1, 51) # exposure time is 0.3s
    
    # Move back to original position
    yield from bps.mv(piezo.th, piezo_th_origin)




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
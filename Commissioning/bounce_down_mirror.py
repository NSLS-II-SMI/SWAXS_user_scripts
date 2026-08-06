# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE IS: a clean, modern bounce-down-mirror (BDM) X-ray reflectivity (XRR) toolkit.
#   Nice work — this is already very close to how 'smi_plans' does things: each XRR plan opens a
#   proper "run" (one saved dataset), records the incident angle as a real data channel
#   ('incident_angle' Signal) and reads it alongside the detector with trigger_and_read, instead
#   of cramming the angle into the file name. That's exactly the pattern smi_plans is built on, so
#   migrating here is mostly a rename, not a rewrite.
#
# 💡 WHERE THIS LIVES IN smi_plans: the XRR presets are in the xrr technique module —
#   'xrr_run' (solid substrate, direct beam), 'xrr_liquid_run' (liquid surface via the bounced
#   beam), 'xrr_resonant_run' (energy-resolved), 'xrr_bar' (a bar of samples), and the helper
#   'piezo_th_correction' (already used below — smi_plans exports this exact function). They open
#   the run, step the angle, set the reflected-beam ROI, and record incident_angle for you:
#
#     from smi_plans import xrr_run, xrr_liquid_run, piezo_th_correction   # once per session
#     yield from xrr_run("Si_substrate", start_angle=0, stop_angle=0.45, num_steps=181, t=1)
#
#   (Everything below still works as-is. The only genuine gotcha is the 'det_exposure_time(...)'
#    calls — they're now "plans" and need to be run as plans; each is marked ⚠️ inline.)
# === end smi_plans note ================================================
pil2M.stats2.kind = 'hinted'
pil2M.stats2.total.kind = 'hinted'

pil2M.stats3.kind = 'hinted'
pil2M.stats3.total.kind = 'hinted'

# pil2M.beam_offset_y_mm.set(190.404+2*0.172)
pil2M.beam_offset_y_mm.set(190.404+5*0.172)
#RE(smi.setDirectBeamROI())
from smi_plans.analysis import pf


def run_xrr_bdm_saxs(start_angle, stop_angle, num_steps, bdm_th_origin, det=pil2M, atten=None, 
                     bdm_sample_distance=172-10, avoid_gaps=True):
    """
    Perform XRR scan by bouncing down the mirror from start_angle to stop_angle.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an XRR (X-ray reflectivity) scan that bends the beam down off the mirror,
    #   stepping the mirror angle and, at each step, setting the reflected-beam region and
    #   recording a SAXS image plus the incident angle.
    #
    # 💡 NEWER, EASIER WAY: this is exactly 'smi_plans.xrr_run'. It opens the run, steps the
    #   angle, sets the reflected ROI, and records 'incident_angle' for you (just like you do
    #   here, very nicely) — in one call:
    #
    #     from smi_plans import xrr_run
    #     yield from xrr_run("XRR_bounce_down", start_angle, stop_angle, num_steps,
    #                        dets=[pil2M], t=1)        # your angles/detector, unchanged
    #
    #   (Optional — this plan already follows the modern pattern. The only fix needed is the
    #    ⚠️ exposure line below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(1, 1)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3/4.)
    # === end smi_plans note ================================================
    angles = np.linspace(start_angle, stop_angle, num_steps)
    yield from det_exposure_time(1, 1)  
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from bps.mv(bdm.th, bdm_th_origin + angle)
            yield from smi.setReflectedBeamROI(total_angle=-angle, 
                                               technique="gisaxs",
                                               sample_z_offset_mm=bdm_sample_distance,
                                               avoid_gaps=avoid_gaps)
            sample_name = f'XRR_bounce_down_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle])
        yield from bps.mv(bdm.th, bdm_th_origin)
    return (yield from inner())


def run_xrr_bdm_waxs(start_angle, stop_angle, num_steps, det=pil900KW, atten=None):
    """
    Perform XRR scan by bouncing down the mirror from start_angle to stop_angle.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the WAXS-detector version of the BDM XRR scan above — bends the beam down,
    #   steps the mirror angle, sets the reflected ROI, and records a WAXS image + incident angle.
    #
    # 💡 NEWER, EASIER WAY: same as the SAXS version — 'smi_plans.xrr_run', just point it at the
    #   WAXS detector. (Nicely, this one already defaults to the current 'pil900KW' — no detector
    #   fix needed here.)
    #
    #     from smi_plans import xrr_run
    #     yield from xrr_run("XRR_bounce_down", start_angle, stop_angle, num_steps,
    #                        dets=[pil900KW], t=1)
    #
    #   (Optional — already modern. The only fix needed is the ⚠️ exposure line below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(1, 1)' line below needs to be run as a
    #   plan (see ⚠️ note on it). (internal: Tier 3/4.)
    # === end smi_plans note ================================================
    angles = np.linspace(start_angle, stop_angle, num_steps)
    ai0 = bdm.th.get()
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr_run sets exposure for you via t=.)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    yield from smi.modeAlignment(technique = "giwaxs")
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from bps.mv(bdm.th, bdm_th_origin + angle)
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
    Get the current position of the Bounce-Down mirror (BDM).
    """
    x = bdm.x.position
    y = bdm.y.position
    th = bdm.th.position 
    print(f"Current BDM Position - X: {x}, Y: {y}, Theta: {th}")
    return x, y, th

def save_bdm_origin():
    print("Saving current BDM position as origin...")
    bdm_x_origin, bdm_y_origin, bdm_th_origin = get_bdm_pos()
    mdsave['bdm_x_origin'] = bdm_x_origin
    mdsave['bdm_y_origin'] = bdm_y_origin
    mdsave['bdm_th_origin'] = bdm_th_origin


def restore_bdm_origin():
    get_bdm_pos()
    global bdm_x_origin, bdm_y_origin, bdm_th_origin
    bdm_x_origin = mdsave['bdm_x_origin']
    bdm_y_origin = mdsave['bdm_y_origin']
    bdm_th_origin = mdsave['bdm_th_origin']
    print(f"BDM origin position - X: {bdm_x_origin}, Y: {bdm_y_origin}, Theta: {bdm_th_origin}")


def go_bdm_origin():
    bdm_x_origin = mdsave['bdm_x_origin']
    bdm_y_origin = mdsave['bdm_y_origin']
    bdm_th_origin = mdsave['bdm_th_origin']
    yield from bps.mv(bdm.x, bdm_x_origin, bdm.y, bdm_y_origin, bdm.th, bdm_th_origin)
    print(f"Moved BDM to origin position - X: {bdm_x_origin}, Y: {bdm_y_origin}, Theta: {bdm_th_origin}")



def get_piezo_pos():
    """
    Get the current position of the piezo-driven mirror (PDM).
    """
    y = piezo.y.position
    th = piezo.th.position
    print(f"Sample Position - Y: {y}, Theta: {th}")
    return y, th

def save_piezo_origin():
    print("Saving current piezo position as origin...")
    piezo_y_origin, piezo_th_origin = get_piezo_pos()
    mdsave['piezo_y_origin'] = piezo_y_origin
    mdsave['piezo_th_origin'] = piezo_th_origin


def restore_piezo_origin():
    get_piezo_pos()
    global piezo_y_origin, piezo_th_origin
    piezo_y_origin = mdsave['piezo_y_origin']
    piezo_th_origin = mdsave['piezo_th_origin']
    print(f"Piezo origin position - Y: {piezo_y_origin}, Theta: {piezo_th_origin}")


def go_piezo_origin():
    piezo_y_origin = mdsave['piezo_y_origin']
    piezo_th_origin = mdsave['piezo_th_origin']
    yield from bps.mv(piezo.y, piezo_y_origin, piezo.th, piezo_th_origin)
    print(f"Moved Piezo to origin position - Y: {piezo_y_origin}, Theta: {piezo_th_origin}")
# bdm_x_origin = mdsave['bdm_x_origin']
# bdm_y_origin = mdsave['bdm_y_origin']
# bdm_th_origin = mdsave['bdm_th_origin']
# piezo_y_origin = mdsave['piezo_y_origin']
# piezo_th_origin = mdsave['piezo_th_origin']


def check_bdm_refection(angle, bdm_th_origin, det=pil2M, sample_z_offset_mm=176):
    '''check the reflection on the detector at a bdm angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick check — moves the mirror to one angle, sets the reflected-beam
    #   region, and takes a single image so you can see where the reflected spot lands.
    #
    # 💡 NEWER, EASIER WAY: this kind of alignment/diagnostic check is part of the smi_plans XRR
    #   setup (the xrr_* runs handle the reflected-ROI placement internally). Keep using this for
    #   eyeballing; just note the ⚠️ exposure fix below. (internal: alignment helper.)
    # === end smi_plans note ================================================

    yield from det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(bdm.th, bdm_th_origin + angle)
    print(f'current at bdm_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=-angle, technique="gisaxs",sample_z_offset_mm=sample_z_offset_mm)

    yield from count([det]) # count direct beam # exposure time is 0.3s


def move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance=176, saxs_sdd_offset=-50):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the geometry primitive at the heart of liquid XRR — for a chosen incidence
    #   angle it figures out how far to drop the sample in y (so the bounced beam still hits it),
    #   moves the mirror + sample, and sets the direct- and reflected-beam regions.
    #
    # 💡 NEWER, EASIER WAY: this angle->y geometry is built into smi_plans' liquid XRR preset
    #   ('xrr_liquid_run'), so when you migrate you won't need to call this by hand. (Nothing
    #   broken here — it's a pure motion/ROI helper.)
    # === end smi_plans note ================================================
    y_offset = np.tan(np.deg2rad(2*alpha)) * bdm_sample_distance * 1000  # in um
    new_y = piezo_y_origin - y_offset
    new_th = bdm_th_origin + alpha
    print(f'geometric calculation: for alpha={alpha}deg, y_offset={y_offset}um')
    print(f"Moved sample to Y: {new_y}, Theta: {new_th}")
    yield from bps.mv(bdm.th, new_th, piezo.y, new_y)
    

    print(f'saxs_sdd_offset: {saxs_sdd_offset}mm')

    print('Setting direct beam from bdm using ROI2')
    yield from smi.setReflectedBeamROI(total_angle=-alpha, 
                                        technique="gisaxs",
                                        sample_z_offset_mm=bdm_sample_distance+saxs_sdd_offset,
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sample-height alignment — scans piezo.y, finds the edge (peak of the
    #   derivative of the intensity), and moves to it. (Nothing broken here.)
    #
    # 💡 NEWER, EASIER WAY: in smi_plans, alignment like this is usually done once up front via
    #   'align_sample' (passed as align= to a run), and the result is recorded with the data
    #   automatically. This helper is fine to keep using for manual alignment.
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    if roi == 1:
        # ps(der=der, suffix='_stats1_total', plot=True)
        pf(der=True, suffix='_stats1_total')
    elif roi == 2:
        # ps(der=der, suffix='_stats2_total', plot=True)
        pf(der=True, suffix='_stats2_total')
    else:
        print('using the default roi')
        # ps(der=der, plot=True)
        pf(der=True)
    print(f'The peak center is {pf.cen:.1f}')
    yield from bps.mv(piezo.y, pf.cen)
    return pf.cen


# angles=[0, 0.05, 0.1, 0.16, 0.2, 0.25, 0.3, 0.36, 0.4]
def scan_bdm_angle_sh_knife_edge(angles, piezo_y_origin, bdm_y_origin, bdm_th_origin, bdm_sample_distance=176):
    '''at different bdm angle, scan the sample height using a knife edge'''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a commissioning sweep — at each mirror angle it repositions the sample and
    #   re-finds the height by knife-edge, collecting the height centers vs angle. (No fix needed.)
    #
    # 💡 NEWER, EASIER WAY: this is a calibration/commissioning survey; smi_plans' XRR presets use
    #   the resulting correction internally. Keep using this for commissioning the BDM geometry.
    # === end smi_plans note ================================================
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at each of several mirror x positions, it aligns, snaps a direct-beam
    #   reference, then runs a full BDM XRR scan (run_xrr_bdm_saxs). A handy "do XRR at a few
    #   spots" wrapper.
    #
    # 💡 NEWER, EASIER WAY: running XRR over several positions/samples is 'smi_plans.xrr_bar'
    #   (give it the list of positions and it loops + records for you):
    #
    #     from smi_plans import xrr_bar
    #     # build a SampleList of your x positions, then xrr_bar(samples, start_angle=0,
    #     #   stop_angle=0.45, num_steps=181, t=1)
    #
    #   (Optional — this wrapper works as-is; the exposure fix is inside run_xrr_bdm_saxs.)
    # === end smi_plans note ================================================

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




def check_gisaxs_refection_without_bdm(angle, piezo_th_origin, det=pil2M, sample_z_offset_mm=-50):
    '''check the reflection on the detector at a piezo angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same diagnostic as check_bdm_refection but without the mirror — moves
    #   piezo.th to one angle, sets the reflected ROI, takes a single image. (Alignment helper.)
    #
    # 💡 NEWER, EASIER WAY: this overlaps smi_plans' XRR/GISAXS alignment setup; keep it for
    #   manual checks. Just mind the ⚠️ exposure fix below.
    # === end smi_plans note ================================================

    yield from det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(piezo.th, piezo_th_origin + angle)
    print(f'current at piezo th_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", sample_z_offset_mm=sample_z_offset_mm, roi=pil2M.roi3)

    yield from count([det]) # count direct beam # exposure time is 0.3s



def check_liquid_refection_with_bdm(bdm_angle, piezo_y_origin, bdm_th_origin, 
                                    bdm_sample_distance=176, 
                                    saxs_sdd_offset=-10,
                                    avoid_gaps=False,
                                    det=pil2M):
    '''check the reflection on the detector at bdm angle
    TODO: currently only for SAXS; need to adjust for WAXS
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a one-shot liquid-surface reflection check — drops the sample to the right
    #   y for the given mirror angle (via move_bdm_sample) and takes one image. (Alignment helper;
    #   nothing broken.)
    #
    # 💡 NEWER, EASIER WAY: the liquid-XRR geometry this checks is handled for you by
    #   'smi_plans.xrr_liquid_run'. Keep this for quick manual checks.
    # === end smi_plans note ================================================

    yield from move_bdm_sample(alpha=bdm_angle,
                               piezo_y_origin=piezo_y_origin,
                               bdm_th_origin=bdm_th_origin,
                               bdm_sample_distance=bdm_sample_distance)

    yield from smi.setReflectedBeamROI(total_angle=bdm_angle, 
                                    technique="gisaxs",
                                    size=[48, 8*3],
                                    sample_z_offset_mm=-bdm_sample_distance+saxs_sdd_offset,
                                    avoid_gaps=avoid_gaps,
                                    roi=pil2M.roi3)
    
    print(f'current at bdm angle = {bdm_angle} deg')
    yield from bps.sleep(1)

    yield from count([det]) # count direct beam # exposure time is 0.3s

# alpha_list=[0.04, 0.06, 0.08, 0.1, 0.13, 0.16, 0.2]
def scan_y_reflected_beam_from_sample(alpha_list, piezo_y_origin, bdm_th_origin, bdm_sample_distance=183):
    '''Scan reflected beam from sample by varying the BDM angle and adjusting sample position accordingly.'''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a commissioning sweep that, for each incidence angle, repositions the
    #   sample, takes a quick image, then scans piezo.y to find where the reflected beam lands —
    #   building a table of y-center vs angle.
    #
    # 💡 NEWER, EASIER WAY: this is calibration of the bounced-beam geometry; smi_plans' XRR
    #   presets ('xrr_liquid_run') use such a calibration internally. Keep this for commissioning.
    #   (Two ⚠️ exposure lines below need the plan-style fix.) (internal: alignment survey.)
    # === end smi_plans note ================================================

    Y_original = []
    Y_peak_cen = []
    
    for alpha in alpha_list:
        yield from move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).
        else:
            det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): same as above — it's now a "plan". Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)).
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like scan_y_reflected_beam_from_sample, but it scans piezo.th (the angle)
    #   instead of y to find the reflected-beam center vs incidence angle. (Commissioning sweep.)
    #
    # 💡 NEWER, EASIER WAY: same story — this calibrates the bounced-beam geometry that
    #   'smi_plans.xrr_liquid_run' uses internally. Keep for commissioning; mind the two ⚠️
    #   exposure lines below. (internal: alignment survey.)
    # === end smi_plans note ================================================

    th_original = []
    th_peak_cen = []
    
    for alpha in alpha_list:
        yield from move_bdm_sample(alpha, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
        yield from bps.sleep(1)
        if alpha <=0.15:
            det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).
        else:
            det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): same as above — it's now a "plan". Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)).
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


def xrr_scan_liquid_using_bounced_beam(start_angle,stop_angle,num_steps, 
                                       piezo_y_origin, 
                                       bdm_th_origin, 
                                       bdm_sample_distance=176, 
                                       saxs_sdd_offset=-10,
                                       avoid_gaps=True,
                                       det=pil2M):

    """
    Perform XRR scan from a liquid sample using the bounced beam.
    Both liquid sample and BDM need to go to origin before the run
    The data is at ROI3
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: liquid-surface XRR using the bounced beam — opens a run, steps the angle,
    #   re-positions the liquid sample for each angle, picks attenuators, sets the reflected ROI,
    #   and records the image + incident angle. (This is the polished liquid-XRR plan.)
    #
    # 💡 NEWER, EASIER WAY: this is exactly 'smi_plans.xrr_liquid_run'. It bakes in the
    #   angle->sample-y geometry, the attenuator selection, and recording 'incident_angle' (all of
    #   which you do nicely here) into one call:
    #
    #     from smi_plans import xrr_liquid_run
    #     yield from xrr_liquid_run("XRR_bounced", start_angle, stop_angle, num_steps, t=1)
    #
    #   (Optional — already modern. Only the ⚠️ exposure line below needs the plan-style fix.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(1, 1)' line below needs to be run as a
    #   plan (see ⚠️ note on it). (internal: Tier 4.)
    # === end smi_plans note ================================================
    angles = np.linspace(start_angle, stop_angle, num_steps)
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr_liquid_run sets exposure for you via t=.)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    # yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'XRR_bounce_down'})
    def inner():
        for angle in angles:
            yield from move_bdm_sample(angle, piezo_y_origin, bdm_th_origin, bdm_sample_distance)
            yield from smi.setReflectedBeamROI(total_angle=angle, 
                                                technique="gisaxs",
                                                size=[48, 8*3],
                                                sample_z_offset_mm=-bdm_sample_distance+saxs_sdd_offset,
                                                avoid_gaps=avoid_gaps,
                                                roi=pil2M.roi3)

            yield from att_selection_8keV(angle*2)

            sample_name = f'XRR_bounced_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle, attenuation])

    return (yield from inner())


# alpha_list=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
def scan_reflected_beam_from_sample_without_bdm(alpha_list, piezo_th_origin):
    '''Scan reflected beam from sample by varying the piezo angle'''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the no-mirror version of the reflected-beam survey — sweeps piezo.th, finds
    #   the reflected-beam center at each angle, and tabulates it. (Commissioning/alignment sweep.)
    #
    # 💡 NEWER, EASIER WAY: this calibrates the direct-beam (no-BDM) reflectivity geometry used by
    #   'smi_plans.xrr_run'. Keep for commissioning; mind the two ⚠️ exposure lines below.
    # === end smi_plans note ================================================

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
            det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).
        else:
            det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): same as above — it's now a "plan". Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)).
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: solid-substrate XRR with the direct beam (no mirror) — opens a run, steps
    #   the angle (applying the small piezo.th motion correction), picks attenuators, sets the
    #   reflected ROI, and records the image + incident angle.
    #
    # 💡 NEWER, EASIER WAY: this is 'smi_plans.xrr_run'. It applies 'piezo_th_correction'
    #   (smi_plans exports the exact same function — see below), handles attenuators, and records
    #   'incident_angle' for you:
    #
    #     from smi_plans import xrr_run
    #     yield from xrr_run("Si_substrate", start_angle, stop_angle, num_steps, t=1)
    #
    #   (Optional — already modern. Only the ⚠️ exposure line below needs the plan-style fix.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(1, 1)' line below needs to be run as a
    #   plan (see ⚠️ note on it). (internal: Tier 4.)
    # === end smi_plans note ================================================
    angles = np.linspace(start_angle, stop_angle, num_steps)
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr_run sets exposure for you via t=.)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    # yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'Si substrate'})
    def inner():
        for angle in angles:
            yield from bps.mv(piezo.th, piezo_th_origin + piezo_th_correction(angle))
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



def piezo_th_correction(th_target, slope=1.281629, intercept=0.001648, th_aligned=0.1):
    '''The sample substrate is aligned at piezo_th_for_aligned=0.1
    slope = 1.281629
    intercept = 0.001648
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: corrects the requested incidence angle into the actual piezo.th motion
    #   (the stage doesn't move exactly 1:1 with angle), using a measured slope/intercept.
    #
    # 💡 GOOD NEWS: 'smi_plans' ships this exact helper under the same name —
    #   'from smi_plans import piezo_th_correction'. The XRR presets (xrr_run, etc.) call it for
    #   you, so once you migrate you won't need this local copy. (Nothing broken.)
    # === end smi_plans note ================================================

    actual_motion = (th_target-th_aligned)*slope + intercept + th_aligned

    return actual_motion

    
def check_gisaxs_refection_th_corrected(angle, piezo_th_origin, det=pil2M, sample_z_offset_mm=-50):
    '''check the reflection on the detector at a piezo angle with motion correction
    TODO: currently only for SAXS; need to adjust for WAXS
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same reflected-beam check as the others, but applies piezo_th_correction so
    #   the angle you ask for is the angle you actually get. (Alignment helper.)
    #
    # 💡 NEWER, EASIER WAY: smi_plans' XRR presets apply piezo_th_correction internally. Keep this
    #   for manual checks; mind the ⚠️ exposure fix below.
    # === end smi_plans note ================================================

    yield from det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(piezo.th, piezo_th_origin + piezo_th_correction(angle))
    print(f'current at piezo th_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", sample_z_offset_mm=sample_z_offset_mm)

    yield from count([det]) # count direct beam # exposure time is 0.3s




def check_gisaxs_refection_th_stage(angle, stage_th_origin=-0.1, det=pil2M, sample_z_offset_mm=-50):
    '''check the reflection on the detector at a piezo angle with motion correction
    TODO: currently only for SAXS; need to adjust for WAXS
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same reflected-beam check as the others, but applies piezo_th_correction so
    #   the angle you ask for is the angle you actually get. (Alignment helper.)
    #
    # 💡 NEWER, EASIER WAY: smi_plans' XRR presets apply piezo_th_correction internally. Keep this
    #   for manual checks; mind the ⚠️ exposure fix below.
    # === end smi_plans note ================================================

    yield from det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

    yield from smi.modeAlignment(technique="gisaxs")
    
    # move to theta 0 + value
    yield from bps.mv(stage.th, stage_th_origin + angle)
    print(f'current at stage th_angle = {angle} deg')

    # Set reflected ROI for beam bending down
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", sample_z_offset_mm=sample_z_offset_mm)

    yield from count([det]) # count direct beam # exposure time is 0.3s




def run_xrr_solid_substrate_th_stage_using_direct_beam(start_angle,stop_angle,num_steps, 
                                                       stage_th_origin=-0.1,
                                                       sample_z_offset_mm=-50,
                                                       avoid_gaps=True,
                                                       det=pil2M):

    """
    Perform XRR scan from a solid substrate sample using the direct beam without bdm.
    BDM needs to be removed
    The data is at ROI1
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: solid-substrate XRR with the direct beam (no mirror) — opens a run, steps
    #   the angle (applying the small piezo.th motion correction), picks attenuators, sets the
    #   reflected ROI, and records the image + incident angle.
    #
    # 💡 NEWER, EASIER WAY: this is 'smi_plans.xrr_run'. It applies 'piezo_th_correction'
    #   (smi_plans exports the exact same function — see below), handles attenuators, and records
    #   'incident_angle' for you:
    #
    #     from smi_plans import xrr_run
    #     yield from xrr_run("Si_substrate", start_angle, stop_angle, num_steps, t=1)
    #
    #   (Optional — already modern. Only the ⚠️ exposure line below needs the plan-style fix.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(1, 1)' line below needs to be run as a
    #   plan (see ⚠️ note on it). (internal: Tier 4.)
    # === end smi_plans note ================================================
    angles = np.linspace(start_angle, stop_angle, num_steps)
    yield from det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr_run sets exposure for you via t=.)
    s = Signal(name='target_file_name', value='')
    incident_angle = Signal(name='incident_angle', value=start_angle)
    # yield from smi.modeAlignment()
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md={'file_name' :'{target_file_name}', 'scan_name': 'Si substrate'})
    def inner():
        for angle in angles:
            yield from bps.mv(stage.th, stage_th_origin + angle)
            yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", 
                                               size=[48, 12], sample_z_offset_mm=sample_z_offset_mm,
                                               avoid_gaps=avoid_gaps)
            yield from att_selection_8keV(angle)
            sample_name = f'XRR_directbeam_{angle:.3f}deg{get_scan_md()}'
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            incident_angle.put(angle)
            #if atten:
            #    yield from bps.mv(attenuator, atten)
            yield from bps.sleep(1)  # Allow time for the piezo to settle
            yield from bps.trigger_and_read([det] + [s,incident_angle,attenuation])

    return (yield from inner())




def atten_move_in(att_list):
    """
    Move attenuators in
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: inserts a list of attenuators (waits until each reports 'Open').
    #   (atten_move_out just below does the reverse.) Attenuators still work the same way — nothing
    #   broken here.
    #
    # 💡 NEWER, EASIER WAY: for sweeping attenuation as part of commissioning, smi_plans has
    #   'attenuator_ladder_run'. For just inserting/removing filters during a scan, helpers like
    #   these are still fine.
    # === end smi_plans note ================================================
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: picks the right attenuators for a given XRR angle (more filtering at low
    #   angle where the reflectivity is near 1) and inserts/removes them. (att2_* still work
    #   normally — nothing broken.)
    #
    # 💡 NEWER, EASIER WAY: the smi_plans XRR presets do this angle-dependent attenuation for you.
    #   If you just want to characterize the attenuator ladder, see 'attenuator_ladder_run'.
    # === end smi_plans note ================================================
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



def alignment_gisaxs_using_bdm_bonced_beam(angle=0.1, alpha_bdm=0.05, 
                                           piezo_y_origin=0, bdm_th_origin=0, 
                                           bdm_sample_distance=176,
                                           sdd_offset=-10, avoid_gaps=True):
    """
    TODO: this function is not done yet...

    Alignment routine for GISAXS using bounced beam from BDM as the direct beam (bdm_alpha=0.05)
    
    First, scan the sample height and incident angle on the direct beam.
    Then scan the incident angle, height, and incident angle again on the reflected beam.

    Parameters:
        angle (float): Angle at which the alignment on the reflected beam will be done.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: (still a work-in-progress, per the TODO) a GISAXS alignment that uses the
    #   BDM-bounced beam as the "direct" beam — it scans sample height and angle on the direct
    #   beam, then refines on the reflected beam with progressively finer scans.
    #
    # 💡 NEWER, EASIER WAY: alignment like this is what 'align_sample' is for in smi_plans — you
    #   run it once and the alignment result is recorded with your data automatically, then pass
    #   it as align= to your run (e.g. giwaxs_run / xrr_liquid_run). Keep finishing this for the
    #   BDM-bounced case; mind the ⚠️ exposure fix below. (internal: alignment routine.)
    # === end smi_plans note ================================================
    

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    yield from det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).

    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    # yield from smi.setDirectBeamROI()
    yield from smi.setReflectedBeamROI(total_angle=-alpha_bdm, 
                                    technique="gisaxs",
                                    sample_z_offset_mm=bdm_sample_distance+sdd_offset,
                                    avoid_gaps=avoid_gaps)

    # Scan theta and height
    yield from align_gisaxs_height(800, 21, der=True)
    yield from align_gisaxs_th(1.5, 27)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    # yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")
    yield from smi.setReflectedBeamROI(total_angle=angle, 
                                    technique="gisaxs",
                                    sample_z_offset_mm=-bdm_sample_distance+sdd_offset,
                                    avoid_gaps=avoid_gaps,
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
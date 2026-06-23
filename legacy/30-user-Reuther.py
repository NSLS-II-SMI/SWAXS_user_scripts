def run_swaxs_reuther_2023_cap(t=1):
    """
    Take WAXS and SAXS at several sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: runs a bar of capillary samples — for each WAXS arc position it
    #   visits each sample and a few x/y offset spots on it, taking a SAXS+WAXS image
    #   (SAXS is skipped automatically when the WAXS arc is in the SAXS beam path).
    #
    # 💡 NEWER, EASIER WAY: running a whole bar of transmission samples is one call in
    #   the 'smi_plans' library; you give it the samples (positions + names) as a
    #   SampleList and it visits, names, and records the energy/arc/detector-distance into
    #   each image for you (so you don't have to read energy.position / pil2M_pos.z by hand):
    #
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y)
    #     yield from transmission_bar(
    #         "reuther_2023_cap", samples,
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],
    #     )
    #     # (offsets per sample and the WAXS-arc loop can be added as extra axes; ask staff
    #     #  for the offset/arc pattern that matches your averaging scheme.)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================

    names =   [ '529.5_9_mg_ml', '529.4_NATIVE', '529.2_NATIVE', '529.3_NATIVE', '538.2_NATIVE', '538.1_NATIVE', 
               '490_NATIVE_10w%', '460.2_NATIVE_10w%', '460.1_4.76_mg_ml', '476.3_NATIVE','476.2_NATIVE', '476.1_NATIVE']
    piezo_x = [  49800,  24300, 18050, 11800, 5550, -1200, -7200, -13950, -19950, 70-26450, -32700, -39200 ]
    piezo_y = [-192 for n in names]
   # piezo_y = [       -792,    -792, -792,  -792    ]
    hexa_y =  [0 for n in names]  #in mm

    x_off = [0]
    y_off = [0, 200, 400, 600]
 
    waxs_arc = [20, 0]

    user = "JR"

    # Check and correct sample names just in case
    names = [n.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "}) for n in names]

    # Check if the length of xlocs, ylocs and names are the same
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        # Detectors, disable SAXS when WAXS in the way
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for name, x, y, hy in zip(names, piezo_x, piezo_y, hexa_y):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)

            for yy, y_of in enumerate(y_off):
                yield from bps.mv(piezo.y, y + y_of)

                for xx, x_of in enumerate(x_off):
                    yield from bps.mv(piezo.x, x + x_of)
                    

                    # Metadata
                    e = energy.position.energy / 1000
                    wa = waxs.arc.position + 0.001
                    wa = str(np.round(float(wa), 1)).zfill(4)
                    sdd = pil2M_pos.z.position / 1000

                    # Sample name
                    name_fmt = ( "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_loc{xx}{yy}")
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%.2f" % e,
                        wax=wa,
                        sdd="%.1f" % sdd,
                        #loc=int(loc),
                        xx = xx,
                        yy = yy,
                    )
                    sample_id(user_name=user, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

# 2023-1 round 2
RE.md['SAF_number'] = 310643

def run_swaxs_reuther_2023_slide(t=1):
    """
    Take WAXS and SAXS at several sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same idea as the capillary bar above, but for samples on a slide —
    #   for each WAXS arc position it visits each sample and a few x/y offset spots,
    #   taking a SAXS+WAXS image (SAXS skipped when the WAXS arc blocks it).
    #
    # 💡 NEWER, EASIER WAY: running a bar of transmission samples is one call in the
    #   'smi_plans' library; hand it the samples (positions + names) as a SampleList and
    #   it visits, names, and records the energy/arc/detector-distance into each image:
    #
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y)
    #     yield from transmission_bar(
    #         "reuther_2023_slide", samples,
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],
    #     )
    #     # (offsets per sample and the WAXS-arc loop can be added as extra axes.)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================

    names =   [ '476.3_KAP', '527.1_KAP', 'BLANK_KAP', 'BLANK_GLASS', '538.1_GLASS']
    piezo_x = [ 47500, 19100, -6399, -25399, -31899]
    piezo_y = [ 5150,  5150,  4150, 3150, 3150]
    hexa_y =  [0 for n in names]  #in mm

    x_off = [0, 500]
    y_off = [0, 500]
    user = "JR"
    waxs_arc = [20, 0]

    # Check and correct sample names just in case
    names = [n.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "}) for n in names]

    # Check if the length of xlocs, ylocs and names are the same
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        # Detectors, disable SAXS when WAXS in the way
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for name, x, y, hy in zip(names, piezo_x, piezo_y, hexa_y):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)

            for yy, y_of in enumerate(y_off):
                yield from bps.mv(piezo.y, y + y_of)

                for xx, x_of in enumerate(x_off):
                    yield from bps.mv(piezo.x, x + x_of)
                    

                    # Metadata
                    e = energy.position.energy / 1000
                    wa = waxs.arc.position + 0.001
                    wa = str(np.round(float(wa), 1)).zfill(4)
                    sdd = pil2M_pos.z.position / 1000

                    # Sample name
                    name_fmt = ( "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_loc{xx}{yy}")
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%.2f" % e,
                        wax=wa,
                        sdd="%.1f" % sdd,
                        #loc=int(loc),
                        xx = xx,
                        yy = yy,
                    )
                    sample_id(user_name=user, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

def align_gisaxs_th_zihan(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small alignment scan — it rocks the sample tilt (theta) over a
    #   range, finds the peak of the reflected/direct beam, moves there, then returns.
    #
    # 💡 NEWER, EASIER WAY: in the 'smi_plans' library, grazing alignment like this is
    #   handled by 'align_sample' (and the GISAXS/GIWAXS runs can align for you up front),
    #   and the alignment result is saved alongside the data automatically. So instead of
    #   calling a hand-rolled theta scan, you'd let the run align once and record it:
    #
    #     from smi_plans import align_sample, giwaxs_run
    #     yield from giwaxs_run(..., align=align_sample)   # aligns, then measures, and saves both
    #
    #   (Nothing here is broken; this just becomes a built-in step once you migrate.)
    # === end smi_plans note ================================================
    th0 = piezo.th.position
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    try:
        ps(plot=False)
        yield from bps.mv(piezo.th, ps.peak)
    except:
        print('\n\n\n\n\Could not aligned well with theta')
    yield from bps.mv(piezo.th, th0)

def zihan_giwaxs_alignment(angle=0.1):
    """
    Quicker alignment
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a full grazing-incidence (GISAXS) alignment routine — it switches
    #   the beamline into alignment mode, finds the direct and reflected beams, scans
    #   tilt (theta) and height to get the sample flat at the right angle, then switches
    #   back to measurement mode.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' library does grazing alignment for you with
    #   'align_sample', and the GISAXS/GIWAXS run helpers can align once up front and save
    #   the alignment with the data, so you don't have to call a separate routine each time:
    #
    #     from smi_plans import align_sample, giwaxs_run
    #     yield from giwaxs_run(
    #         "my_sample", t=t, dets=[pil2M, pil900KW],
    #         incident_angles=[0.1],              # your grazing angle(s)
    #         align=align_sample,                 # aligns, then measures, and records both
    #     )
    #
    #   (Just a tidier path to try later — your routine below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.3, 0.3)' line below no longer
    #   sets the exposure unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================

    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan theta and height
    yield from align_gisaxs_height(800, 16, der=True)
    yield from align_gisaxs_th_zihan(1.5, 27)

    # move to theta 0 + value
    yield from bps.mv(piezo.th, ps.peak + angle)

    # Set reflected ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")

    # Scan theta and height
    yield from align_gisaxs_th_zihan(0.2, 11)
    yield from align_gisaxs_height_rb(150, 16)
    yield from align_gisaxs_th_zihan(0.1, 21) 

    # Close all the matplotlib windows
    plt.close("all")

    # Return angle
    yield from bps.mv(piezo.th, ps.cen - angle)
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def reuter_giwaxs_2023_1(t=0.5):
    """
    Hard X-ray GIWAXS, samples on Lakeshore heating stage but no heating.
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS (GIWAXS) run over a bar of samples — for
    #   each sample it aligns, then for each WAXS arc position and incident angle it takes
    #   a SAXS+WAXS image at a few x-offset spots.
    #
    # 💡 NEWER, EASIER WAY: running a GIWAXS bar (align each sample, sweep incident angle
    #   and WAXS arc) is exactly what the 'smi_plans' GIWAXS helpers do, and they record
    #   the angle/arc/energy/position into each image and align for you:
    #
    #     from smi_plans import giwaxs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from giwaxs_bar(
    #         "reuter_giwaxs_2023_1", samples,
    #         incident_angles=[0.1, 0.5],         # your incident angles, unchanged
    #         arc=[20, 0],                        # your WAXS arc positions, unchanged
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M, pil900KW],
    #         align=align_sample,                 # aligns each sample and saves the result
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================

    names =   [ '523.1', '524.1', '538.1', 'GIWAX_GLASS_BLANK']
    piezo_x = [  58399,   35799,   11799, -4201]   
    piezo_y = [5703 for n in names]
    piezo_z = [  1378, 4178, 1978, 1978]
    #piezo_z = [5100 for n in names]
    stage_x = [13, 13, 13, 13]
    # piezo_z = [4200, 4100, ]

    assert len(names)   == len(piezo_x), f"Wrong list lenghts"
    assert len(piezo_x) == len(piezo_y), f"Wrong list lenghts"
    assert len(piezo_y) == len(piezo_z), f"Wrong list lenghts"

    user = "JR"
    waxs_arc = [20, 0]
    incident_angles = [0.1, 0.5]
    piezo_x_offs = [0, 200, 400]

    ai0 = piezo.th.position

    for name, x, y, z, hexa_x in zip(names, piezo_x, piezo_y, piezo_z, stage_x):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          stage.x, hexa_x,
                          piezo.th, ai0)
        # Align sample
        yield from zihan_giwaxs_alignment(0.1)

        # Sample flat at ai0
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)
                
                p=0
                for i, x_off in enumerate(piezo_x_offs):
                    yield from bps.mv(piezo.x, x + p * 200 + x_off)

                    # Metadata
                    e = energy.position.energy / 1000
                    wa = waxs.arc.position + 0.001
                    wa = str(np.round(float(wa), 1)).zfill(4)
                    sdd = pil2M_pos.z.position / 1000


                    # Sample name
                    name_fmt = ( "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_loc{xx}{yy}_ai{ai}")
                    sample_name = name_fmt.format(
                        sample = name,
                        energy = "%.2f" % e,
                        wax = wa,
                        sdd = "%.1f" % sdd,
                        #loc=int(loc),
                        xx = 0,
                        yy = i,
                        ai = ai,
                    )
                    sample_id(user_name=user, sample_name=sample_name)
                    print(f"\n\n\n\t=== Sample: {sample_name} ===")
                    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

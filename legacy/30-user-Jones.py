# 2023-June-2 Fri
#
# 16.1 keV, 200*30um beam, air
# proposal_id("2023_2", "312283_Jones", analysis=True)
# RE.md['SAF_number'] = 311104
# RE.md['SAXS_setup'] = {'sdd': 9200, 'beam_centre': [450, 554], 'bs': 'rod', 'energy': 16100}
# 
# RE(rel_scan([pil2M], stage.y, -2, 2, 15)); ps()
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# 1. [Search hutch and close]
# 2. RE(shopen())
# 3. [Enter sample name and x-position in this 30-user-Jones.py]
# [Ctrl+s to save this file]
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Jones.py
#
# (Just in case)
# Ctrl+c once/twice; RE.abort()
# bsui
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Jones.py
#
# 4. RE(shclose())
# 5. [To take out sample]
# ---------------------------------------------------------------
# Note: 
# beamstop_save()

def measure_saxs(t=1, user_name="ZC", sample='EmptyKapton', xr_list = [-200, 0]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a SAXS image at a few x offsets on one sample (for averaging).
    #
    # 💡 NEWER, EASIER WAY: taking SAXS/WAXS at several x positions (for averaging) is
    #   the beamline 'smi_plans' helper library's transmission run. It loops the
    #   positions and records each one + the beam into the saved data + file name (so
    #   you can drop the hand-built name strings and sample_id calls):
    #
    #     from smi_plans import transmission_run, motor_axis
    #     yield from transmission_run(sample, [motor_axis('x', piezo.x, x_positions)], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    x0 = piezo.x.position
    y0 = piezo.y.position
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for xr in xr_list:
        x = x0+xr
        yield from bps.mv(piezo.x, x0+xr)

        sample_name = "{sample}_x{x:06.0f}_y{y:06.0f}_{t}s".format(
            sample=sample,
            x=x,
            y=y0,
            t=t,
        )
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(dets, num=1)


def measure_saxs_array(t=1, user_name="SF", sample='Ba4_d', xr_list = [-200, 0]):
    #x0 = piezo.x.position
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps across a row of samples (an x array) and takes a SAXS image at a few x offsets
    #   on each.
    #
    # 💡 NEWER, EASIER WAY: taking SAXS/WAXS at several x positions (for averaging) is
    #   the beamline 'smi_plans' helper library's transmission run. It loops the
    #   positions and records each one + the beam into the saved data + file name (so
    #   you can drop the hand-built name strings and sample_id calls):
    #
    #     from smi_plans import transmission_run, motor_axis
    #     yield from transmission_run(sample, [motor_axis('x', piezo.x, x_positions)], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    x0_list = np.arange(-43550, 40451-12000, 6000)

    for idx, x0 in enumerate(x0_list):
        y0 = piezo.y.position
        dets = [pil2M]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for xr in xr_list:
            x = x0+xr
            yield from bps.mv(piezo.x, x0+xr)

            sample_name = "{sample}{ii}_sdd2200_x{x:06.0f}_y{y:06.0f}_{t}s".format(
                sample=sample,
                ii = idx+1,
                x=x,
                y=y0,
                t=t,
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(dets, num=1)


## RE(measure_waxs(t=0.5, waxs_angle=20, user_name="ZC", sample='Bar1_b1', xr_list = [-200, 0, 200]))
def measure_waxs(t=1, waxs_angle=20, user_name="ZC", sample='test', xr_list = [-200, 0, 200]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS detector into place, then steps across a row of samples and takes a
    #   WAXS image at a few x offsets on each.
    #
    # 💡 NEWER, EASIER WAY: taking SAXS/WAXS at several x positions (for averaging) is
    #   the beamline 'smi_plans' helper library's transmission run. It loops the
    #   positions and records each one + the beam into the saved data + file name (so
    #   you can drop the hand-built name strings and sample_id calls):
    #
    #     from smi_plans import transmission_run, motor_axis
    #     yield from transmission_run(sample, [motor_axis('x', piezo.x, x_positions)], t=t)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, waxs_angle)
    
    #x0 = piezo.x.position
    x0_list = np.arange(-43550, 40451, 6000)

    for x0 in x0_list:
        y0 = piezo.y.position
        dets = [pil900KW]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        for xr in xr_list:
            x = x0+xr
            yield from bps.mv(piezo.x, x0+xr)

            sample_name = "{sample}_x{x:06.0f}_y{y:06.0f}_{t}s".format(
                sample=sample,
                x=x,
                y=y0,
                t=t,
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(dets, num=1)


def test_measure(t=1, waxs_angle=0, user_name="test", sample_name='EmptyKapton', dets = [pil2M, pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick test — sets exposure and takes one SAXS+WAXS image of a sample.
    #
    # 💡 NEWER, EASIER WAY: the beamline 'smi_plans' helper library takes one labelled
    #   image in a single call and records the beam/positions into the data + file name:
    #
    #     from smi_plans import acquire, saxs_waxs_dets
    #     yield from acquire(sample_name, saxs_waxs_dets(), [])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, waxs_angle)
    sample_id(user_name=user_name, sample_name=sample_name)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.count(dets, num=1)

def move_waxs(waxs_angle=20):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a one-line helper that moves the WAXS detector arc to an angle.
    #
    # 💡 smi_plans: nothing to migrate — this is a single motor move, not a measurement.
    #   (The 'waxs' arc is set for you inside the smi_plans GIWAXS runs.) Nothing is broken.
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, waxs_angle)


def alignement_gisaxs(angle=0.15, flag_reflect = 1):
    """
    Regular alignement routine for gisaxs and giwaxs. First, scan of the sample height and incident angle on the direct beam.
    Then scan of teh incident angle, height and incident angle again on the reflected beam.

    param angle: np.float. Angle at which the alignement on the reflected beam will be done

    """

    # Activate the automated derivative calculation
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the standard GISAXS/GIWAXS alignment routine on the piezo stage — finds the sample
    #   height and incident angle on the direct beam, then refines on the reflected beam.
    #
    # 💡 NEWER, EASIER WAY: alignment like this is handled by the beamline 'smi_plans'
    #   helper library's align_sample (used as the 'align=' step of a GIWAXS run), which
    #   aligns each sample once and saves the result WITH the data — so you don't keep a
    #   separate alignment routine by hand.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI(size=[48, 36])

    # Scan theta and height
    yield from align_gisaxs_height(800, 21, der=True)
    yield from align_gisaxs_th(1.5, 31)

    if flag_reflect:
        print('## Align with reflected beam.....')
        # move to theta 0 + value
        yield from bps.mv(piezo.th, ps.peak + angle)

        # Set reflected ROI
        yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs", size=[48, 16])

        # Scan theta and height
        yield from align_gisaxs_th(0.2, 21)
        yield from align_gisaxs_height_rb(150, 16)
        yield from align_gisaxs_th(0.1, 31)  # was .025, 21 changed to .1 31
    else:
        print('## Align with direct beam.....')
        # Scan theta and height
        yield from align_gisaxs_height(200, 16, der=True)
        yield from align_gisaxs_th(0.3, 21)

    # Close all the matplotlib windows
    #plt.close("all")

    # Return angle
    if flag_reflect:
        yield from bps.mv(piezo.th, ps.cen - angle)
    else:
        yield from bps.mv(piezo.th, ps.peak)

    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

    
# 2023-Jun-2 Static, pil2M Y-44.4
# RE(run_giswaxs(t=5, , flag_align=1))
# RE(run_giswaxs(t=5, flag_align=1, flag_reflect=0, piezo_y_init=7700))
def run_giswaxs(t=0.5, flag_align=1, flag_reflect = 1, waxs_angles = [25], piezo_y_init=8000):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GI-S/WAXS run over a bar of samples — for each sample it (optionally) aligns, then
    #   takes WAXS/SAXS at several incident angles and WAXS arc positions.
    #
    # 💡 NEWER, EASIER WAY: aligning each sample then sweeping incident angle / WAXS arc
    #   is the beamline 'smi_plans' helper library's GIWAXS run. align_sample aligns and
    #   saves the result; incidence_axis sweeps the angle while recording it into data:
    #
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, align_sample
    #     samples = SampleList.from_columns(name=sample_list, x=x_list)
    #     yield from giwaxs_bar(samples, incidence_axis(piezo.th, th0, incident_angles),
    #                           t=t, align=align_sample)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    x_rel = [-52200, -44800, -39400, -31400, -25000, -18600, -10400, 4200, 11400]
             #75000, 81000, 88000, 95000,103000]
    offset = 0
    x_list = [x + offset for x in x_rel]
    sample_list = ["Td_chiral_1", "Td_chiral_2", "Td_achiral_1","Td_achiral_2","Td_40_1", "Td_40_2","TBP1","TBP2","TBP3"] 
            
    # "Td_chiral_1", "Td_chiral_2",
                #    "Td_achiral_1","Td_achiral_2","Td_40_1"]
                   
                  #"Td 40 2", "Td chiral DDAOH", "Td achiral DDAOH",
                  #"TBP chiral nonalt 1","TBP chiral nonalt 2","TBP chiral alt 1","TBP chiral alt 2",
                  #"TBP etched 1","TBP etched 2"]

    t0 = time.time()
    assert len(x_list) == len(sample_list), f"Sample name/position list is incorrect"

    data_dir = '/nsls2/data/smi/legacy/results/data/2024_1/312437_Jones/'
    # data_dir = '/nsls2/data/smi/proposals/2025-1/pass-312437/projects/'
    # data_dir = '/nsls2/data/smi/proposals/2025-2/pass-318110/projects/'

    x_shift_array = np.asarray([-200, -0, 200]) 
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar
        # if 's1' in sample or 's4' in sample or 's5' in sample:
        #     x_shift_array = np.asarray([0, -100]) 
        # else:
        #     x_shift_array = np.asarray([0]) 

        yield from bps.mv(piezo.x, x)  # move to next sample
        if flag_align:
            yield from bps.mv(piezo.th, 0) 
            yield from bps.mv(piezo.y, piezo_y_init) 
            yield from alignement_gisaxs(0.1, flag_reflect=flag_reflect)  # run alignment routine
            # yield from saxs_bs.rod_in(x_pos=saxs_bs.x_rod.position - 5)
            yield from saxs_bs.rod_in(x_pos=7.295)
        else:
            yield from saxs_bs.rod_in(x_pos=7.295)
            yield from SMI_Beamline().modeMeasurement()

        print('##### {}, x = {}, aligned at y = {}, theta = {}'.format(sample, piezo.x.position, piezo.y.position, piezo.th.position))
        #aligned_positions.append([sample, piezo.x.position, piezo.y.position, piezo.th.position])
        with open(data_dir+'Align/aligned_positions.txt', 'a') as f:
            note = '{}: x{}, y{}, th{},'.format(sample, piezo.x.position, piezo.y.position, piezo.th.position)
            f.write(note)
            f.write('\n')

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        x_pos_array = x  + x_shift_array

        for waxs_angle in waxs_angles:  # loop through waxs angles
            yield from bps.mv(waxs, waxs_angle)

            if waxs_angle >= 15:
                dets = [pil900KW, pil2M] 
                angle_arc = np.array([0.16])  # incident angles
            else:
                dets = [pil900KW] 
                angle_arc = np.array([0.08, 0.12, 0.16, 0.2])  # incident angles

            th_meas = (
                angle_arc + piezo.th.position
            ) 

            for x_pos in x_pos_array:
                yield from bps.mv(piezo.x, x_pos)  

                for i, th in enumerate(th_meas):  # loop over incident angles
                    yield from bps.mv(piezo.th, th)

                    sample_name = "{sample}_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x}_{t}s".format(
                        sample=sample,
                        th=angle_arc[i],
                        waxs_angle=waxs_angle,
                        x=x_pos,
                        t=t,
                        #scan_id=RE.md["scan_id"],
                    )
                    # name_fmt = '{sample}_16.1keV_8.3m_waxs{waxs_angle:05.2f}_x{x:04.2f}_{t:05.2f}s_{scan_id}'
                    # sample_name = name_fmt.format(sample=sample, waxs_angle=waxs_angle, x=x, t=t, scan_id=RE.md['scan_id'])
                    sample_id(user_name="GI", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")

                    # yield from bp.scan(dets, energy, e, e, 1)
                    # yield from bp.scan(dets, waxs, *waxs_arc)
                    yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    print('Total time = {}min.'.format((time.time()-t0)/60))

# =============== Humidity Chamber ===============
# readHumidity()
# moxa_in.ch1_sp.get()
# moxa_in.ch1_sp.put(0)
#RE(set_humidity_90())
def set_humidity_80(): # Set up but didn't use for 2023-June
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sets the humidity chamber to ~80% by choosing wet/dry gas flows.
    #
    # 💡 NEWER, EASIER WAY: the beamline 'smi_plans' helper library has set_rh(target) to
    #   set humidity directly (and its RH runs record the humidity into the data), so you
    #   don't pick wet/dry flows by hand. (Nothing here is broken.)
    # === end smi_plans note ================================================
    setWetFlow(3.5)
    setDryFlow(1.5)

# RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1))
def alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1):
    """
    Regular alignement routine for gisaxs and giwaxs using the hexapod. First,
    scan of the sample height and incident angle on the direct beam. Then scan
    of teh incident angle, height and incident angle again on the reflected beam.
    param angle: np.float. Angle at which the alignement on the reflected beam will be done

    """

    # Activate the automated derivative calculation
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the standard GISAXS/GIWAXS alignment routine on the hexapod stage — finds the sample
    #   height and incident angle on the direct beam, then refines on the reflected beam.
    #
    # 💡 NEWER, EASIER WAY: alignment like this is handled by the beamline 'smi_plans'
    #   helper library's align_sample (used as the 'align=' step of a GIWAXS run), which
    #   aligns each sample once and saves the result WITH the data — so you don't keep a
    #   separate alignment routine by hand.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI(size=[48, 36])

    # Scan theta and height
    yield from align_gisaxs_height_hex(rough_y, 21, der=True)
    yield from align_gisaxs_th_hex(0.6, 16)
   
    if flag_reflection:
        # move to theta 0 + value
        yield from bps.mv(stage.th, ps.cen + angle)

        # Set reflected ROI
        yield from smi.setReflectedBeamROI(total_angle=angle, technique='gisaxs', size=[48, 16])

        # Scan theta and height
        yield from align_gisaxs_th_hex(0.8, 21)
        yield from align_gisaxs_height_hex(0.1, 15)
        yield from align_gisaxs_th_hex(0.1, 16)
    else:
        # Scan theta and height
        yield from align_gisaxs_height_hex(0.5, 13, der=True)
        yield from align_gisaxs_th_hex(0.5, 16)
        yield from align_gisaxs_height_hex(0.2, 13, der=True)
        yield from align_gisaxs_th_hex(0.2, 16)

    if flag_reflection:
        # Return angle
        yield from bps.mv(stage.th, ps.cen - angle)

    # Close all the matplotlib windows
    #plt.close("all")
    print('### Aligned x={}, y={}, th={}'.format(stage.x.position, stage.y.position, stage.th.position))

    # Return angle
    #      yield from bps.mvr(stage.th, -angle)
    yield from smi.modeMeasurement()
    print('Putting bs back for measurement')
    yield from saxs_bs.rod_in(x_pos=7.295)

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False


# RE(run_gi_humid(t=5, flag_align = 0, Nmax=1000, time_hr = [0.05, 0.1] , time_sleep_sec= [20, 10, 8]))
#2023-June. Hexa with z~3, theta=1.5, x -14/-12 to 18/20, y -20 to 8 still ok
#Maybe better to do each alignment manually with: 
# RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1))
# RE(rel_scan([pil2M], stage.y, -0.2, 0.2, 16))
# RE(rel_scan([pil2M], stage.th, -0.5, 0.5, 11))
# RE(rel_scan([pil2M, pil900KW], stage.y, -0.3, 0.3, 13))
# RE(rel_scan([pil2M, pil900KW], stage.th, -0.5, 0.5, 11))
# 
# RE(run_gi_humid(t=1, flag_align = 0, n0=42, t0 = None, Nmax=15, time_hr = [0.05, 0.1] , time_sleep_sec= [10, 5, 4]))
# RE(run_gi_humid(t=1, flag_align = 0, n0=0, t0 = t0, Nmax=9999, time_hr = [4, 6] , time_sleep_sec= [3600, 1200, 600]))
# RE(run_gi_humid(t=1, flag_align = 0, n0=0, t0 = t0, Nmax=9999, time_hr = [3, 6] , time_sleep_sec= [3600, 600, 900]))
def run_gi_humid(t=5, flag_align = 0, n0=0, t0 = 0, Nmax=9999, time_hr = [4, 8] , time_sleep_sec= [1200, 600, 30]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ humidity GI-S/WAXS run — (optionally) aligns each sample, then loops over
    #   time taking WAXS/SAXS at several incident angles, with the humidity in each name.
    #
    # 💡 NEWER, EASIER WAY: an in-situ humidity (RH) series — aligning samples, then
    #   looping over time while taking GISAXS/GIWAXS — is the beamline 'smi_plans' helper
    #   library's humidity run. set_rh sets the humidity, and the RH series plans loop
    #   over time while recording the humidity/time/positions into the saved data:
    #
    #     from smi_plans import rh_step_series_run, rh_swelling_kinetics_run, set_rh
    #     # set_rh(target); then rh_step_series_run(...) / rh_swelling_kinetics_run(...)
    #     # loop over time and record humidity + elapsed time into the data + file name.
    #
    #   (The inter-frame 'sleep's / time.sleep waits are just spacing — NOT broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    sample_list = [
        "ZC_dynamic16",
        "ZC_dynamic17",
        "ZC_dynamic18",
        "ZC_dynamic19",
        "ZC_dynamic20",
    ]

    waxs_angles = np.array(
        [15]
    )

    if flag_align == 0:
        x_hexa_list = [12.8, 7.5, 2.0, -3.3, -9.0]  
        y_hexa_aligned = [3.401, 3.398, 3.41, 3.4, 3.379]     
        th_hexa_aligned = [2.467, 2.434, 2.456, 2.54, 2.437]
        # x_hexa_list = [-9.0, -3.5 ]  
        # y_hexa_aligned = [-6.54]     
        # th_hexa_aligned = [2.62]    
    else:
        # Intial positions
        x_hexa_list = [2]  
        y_hexa_list = [3.4]     
        th_hexa_list = [0.6]

        ## Align all samples & save positions
        th_hexa_aligned = []
        y_hexa_aligned = []        

        for sample, x_hexa, y_hexa, th_hex in zip(sample_list, x_hexa_list, y_hexa_list, th_hexa_list):  # loop over samples on bar
            yield from bps.mv(stage.th, th_hex)        
            yield from bps.mv(stage.x, x_hexa)
            yield from bps.mv(stage.y, y_hexa)
            yield from alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1)

            th_hexa_aligned = th_hexa_aligned + [stage.th.position]
            y_hexa_aligned = y_hexa_aligned + [stage.y.position]  

    print(y_hexa_aligned)
    print(th_hexa_aligned)

    ## Measure
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    if t0 is None:
        t0 = time.time()
    for nn in range(Nmax):
        for sample, x_hexa, th_hexa, y_hexa in zip(sample_list, x_hexa_list, th_hexa_aligned, y_hexa_aligned):
            xr_list = [0]
            if np.mod(nn, 5)==0:
                xr_list = [0, 0.4]
            if np.mod(nn, 10)==0:
                xr_list = [-0.4, 0, 0.4]

            for xr in xr_list:
                yield from bps.mv(stage.x, x_hexa+xr)
                yield from bps.mv(stage.y, y_hexa)

                incident_angles = [0.08, 0.12, 0.16, 0.2, 0.3, 0.5]
                #incident_angles = [0.5]
                th_real = np.array(incident_angles)  # incident angles
                th_meas = (  ## Stage positions
                    th_real + th_hexa
                )  
                
                for waxs_angle in waxs_angles:  # loop through waxs angles
                    yield from bps.mv(waxs, waxs_angle)
                    if waxs_angle >= 15:
                        dets = [pil900KW, pil2M] 
                    else:
                        dets = [pil900KW] 

                    for i, th in enumerate(th_meas):  # loop over incident angles
                        yield from bps.mv(stage.th, th)

                        humidity = "%3.2f" % readHumidity(verbosity=0)
                        sample_name = "{sample}_n{nn}_t{time:05.0f}s_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x:05.1f}_{t}s".format(
                            sample=sample,
                            nn=nn+n0,
                            time = time.time()-t0,
                            th=th_real[i],
                            waxs_angle=waxs_angle,
                            x=x_hexa+xr,
                            t=t,
                        )
                        sample_id(user_name='Insitu', sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bp.count(dets, num=1)

        if (time.time()-t0) < time_hr[0]*3600:
            print("\nnn={}, time {:.0f}min; Time range 1: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[0]))
            time.sleep(time_sleep_sec[0])

        elif (time.time()-t0) < time_hr[1]*3600:
            print("\nnn={}, time {:.0f}min; Time range 2: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[1]))
            time.sleep(time_sleep_sec[1])

        else:
            print("\nnn={}, time {:.0f}min; Time range 3: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[2]))
            time.sleep(time_sleep_sec[2])


    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)

####
# Put in new bar
# t0 = time.time()
# REhopen())
#
# Move HEX x to new sample alignment spot (substrate only)
# RE(alignRE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1))= 1))ement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flagRE(alignRE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1))= 1))ement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection RE(alignement_gisaxs_hex(angle=0.1, rough_y=0.5, flag_reflection = 1))= 1))_reflection = 1))= 1))
# Note down all the y, th positions
# Note down x (measurement positions), choose option 1 or not
#
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Joneun -i /home/xf12id/.ipythons.py
#
# RE(run_gi_humid_new(t=1, t0=t0, n0=0, time_hr = [3, 5], time_sleep_sec = [600, 20, RE(run_gi_humid_new(t=1, t0=t0, n0=0, time_hr = [3, 5], time_sleep_sec = [600, 20, 1200], Nmax=999))1200], Nmax=999))
# RE(shclose())
#
# ctrl+C, RE.abort()
# (normally not needed) bsuicR
#
# (test only) RE(run_gi_humid_new(t=1, n0=0, time_hr = [0.1, 0.2], time_sleep_sec = [3, 5, 6], Nmax=999))
def run_gi_humid_new(t=0.5, t0=0, user_name='Insitu', time_hr = [2], time_sleep_sec = [3600, 600], xr_list=[0.3], n0=0, Nmax=999):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a newer in-situ humidity GI-S/WAXS run — uses prealigned positions and loops over
    #   time taking WAXS/SAXS at the incident angle(s).
    #
    # 💡 NEWER, EASIER WAY: an in-situ humidity (RH) series — aligning samples, then
    #   looping over time while taking GISAXS/GIWAXS — is the beamline 'smi_plans' helper
    #   library's humidity run. set_rh sets the humidity, and the RH series plans loop
    #   over time while recording the humidity/time/positions into the saved data:
    #
    #     from smi_plans import rh_step_series_run, rh_swelling_kinetics_run, set_rh
    #     # set_rh(target); then rh_step_series_run(...) / rh_swelling_kinetics_run(...)
    #     # loop over time and record humidity + elapsed time into the data + file name.
    #
    #   (The inter-frame 'sleep's / time.sleep waits are just spacing — NOT broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    if t0==None:
        t0 = time.time()
   
    sample_list = ["achiral_DDAOH_realsies", "TBP2_1", "TBP2_2", "TBP3_1", "TBP3_2"]
    
    if 1:     
        x_hexa_list = [-10.92, -5.45, 1.6, 7.65, 13.54] 
        y_hexa_aligned = [-6.359, -6.335, -6.314, -6.302, -6.27]       
        th_hexa_aligned = [2.036, 2.083, 1.956, 2.056, 2.027]  

    yield from saxs_bs.rod_in(x_pos=7.295)
    
    Natt = 5
    for aa in np.arange(0, Natt):
        yield from bps.mv(att1_9.open_cmd, 1)
        yield from bps.sleep(0.5)

    #th_real = np.array([0.12, 0.16, 0.2])  # incident angles
    th_real = np.array([0.16])  # incident angles
     
    print(x_hexa_list)
    print(y_hexa_aligned)
    print(th_hexa_aligned)

    waxs_angles = np.array([25])

    ## Measure
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    for nn in range(Nmax):
        for sample, x_hexa, th_hexa, y_hexa in zip(sample_list, x_hexa_list, th_hexa_aligned, y_hexa_aligned):
           
            flag_option1 = True #False, CHANGE THIS

            # ### OPTION 1
            # if flag_option1:  
            #     xr_list = [-0.75 + np.mod(nn, 6)*0.3]
            #     ypos_list = [y_hexa]
            #     if np.mod(nn, 6)==0:
            #         xr_list.append(0)
            #         ypos_list.append(y_hexa-0.2)
                        
            # ### OPTION 2 
            # else:
                # xr_list = [-0.3 + np.mod(nn, 3)*0.3]
                # ypos_list = [y_hexa - 0.2*np.mod(np.floor(nn/3), 2)]
            #xr_list = [0]
            # ypos_list = [y_hexa]  


            th_meas = (  ## Stage positions
                th_real + th_hexa
            )   
                        
            for xr in xr_list: 
                yield from bps.mv(stage.x, x_hexa+xr)                
                yield from bps.mv(stage.y, y_hexa) 
                    
                for waxs_angle in waxs_angles:  # loop through waxs angles
                    #yield from bps.mv(waxs, waxs_angle)

                    if waxs_angle >= 15:
                        dets = [pil900KW, pil2M] 
                    else:
                        dets = [pil900KW] 

                    for i, th in enumerate(th_meas):  # loop over incident angles
                        yield from bps.mv(stage.th, th)

                        sample_name = "{sample}_n{nn}_t{time:05.0f}s_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x:06.2f}_y{y:06.2f}_{t}s".format(
                            sample=sample,
                            nn=nn+n0,
                            time = time.time()-t0,
                            th=th_real[i],
                            waxs_angle=waxs_angle,
                            x=x_hexa+xr,
                            y=y_hexa,
                            t=t,
                        )
                        sample_id(user_name=user_name, sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bp.count(dets, num=1)

        if (time.time()-t0) < time_hr[0]*3600:
            print("\nnn={}, time {:.0f}min; Time range 1: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[0]))
            #time.sleep(time_sleep_sec[0])
            yield from bps.sleep(time_sleep_sec[0])

        elif (time.time()-t0) < time_hr[1]*3600:
            print("\nnn={}, time {:.0f}min; Time range 2: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[1]))
            yield from bps.sleep(time_sleep_sec[1])

        else:
            print("\nnn={}, time {:.0f}min; Time range 3: sleeping for {}s".format(nn+n0, (time.time()-t0)/60, time_sleep_sec[2]))
            yield from bps.sleep(time_sleep_sec[2])

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


# RE(run_gi_humid_testexp(t_list = [0.5, 1, 2, 3, 5], xr_list=[-0.4], n0=41, Nmax=1, incident_angles = [0.08, 0.5]))
def run_gi_humid_testexp(t_list = [0.5, 1, 2, 3, 5], xr_list=[-0.4], n0=41, Nmax=1, incident_angles = [0.08, 0.5]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an exposure-time test for the humidity GI-S/WAXS run — repeats the measurement at a
    #   list of exposure times.
    #
    # 💡 NEWER, EASIER WAY: an in-situ humidity (RH) series — aligning samples, then
    #   looping over time while taking GISAXS/GIWAXS — is the beamline 'smi_plans' helper
    #   library's humidity run. set_rh sets the humidity, and the RH series plans loop
    #   over time while recording the humidity/time/positions into the saved data:
    #
    #     from smi_plans import rh_step_series_run, rh_swelling_kinetics_run, set_rh
    #     # set_rh(target); then rh_step_series_run(...) / rh_swelling_kinetics_run(...)
    #     # loop over time and record humidity + elapsed time into the data + file name.
    #
    #   (The inter-frame 'sleep's / time.sleep waits are just spacing — NOT broken.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call(s) below no longer
    #   set the exposure unless run as a plan (see the ⚠️ FIXME note(s) on those lines).
    # === end smi_plans note ================================================
    sample_list = [
        "ZC_dynamic2",
    ]

    waxs_angles = np.array(
        [15]
    )

    if 1:
        x_hexa_list = [8.8]  
        y_hexa_aligned = [3.43]     
        th_hexa_aligned = [2.493]

    print(y_hexa_aligned)
    print(th_hexa_aligned)

    ## Measure
    for t in t_list:
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        for sample, x_hexa, th_hexa, y_hexa in zip(sample_list, x_hexa_list, th_hexa_aligned, y_hexa_aligned):
            yield from bps.mv(stage.y, y_hexa)

            for xr in xr_list:
                yield from bps.mv(stage.x, x_hexa+xr)

                th_real = np.array(incident_angles)  # incident angles
                th_meas = (  ## Stage positions
                    th_real + th_hexa
                )  
                
                for waxs_angle in waxs_angles:  # loop through waxs angles

                    yield from bps.mv(waxs, waxs_angle)
                    if waxs_angle >= 15:
                        dets = [pil900KW, pil2M] 
                    else:
                        dets = [pil900KW] 

                    for i, th in enumerate(th_meas):  # loop over incident angles
                        yield from bps.mv(stage.th, th)

                        humidity = "%3.2f" % readHumidity(verbosity=0)
                        sample_name = "{sample}_n{nn}_{th:5.4f}deg_waxs{waxs_angle:05.2f}_x{x:05.1f}_{t}s".format(
                            sample=sample,
                            nn=n0,
                            #time = time.time()-t0,
                            th=th_real[i],
                            waxs_angle=waxs_angle,
                            x=x_hexa+xr,
                            t=t,
                        )
                        sample_id(user_name='Insitu', sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        for nn in range(Nmax):
                            yield from bp.count(dets, num=1)


    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)





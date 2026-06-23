def gisaxsElb(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) run — for each sample it moves there,
    #   then steps through a few incident angles (piezo.th) and, at each, sweeps the WAXS arc in one
    #   coordinated scan, taking SAXS+WAXS images. It also logs the Linkam temperature.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' GIWAXS preset aligns each sample (and saves the
    #   alignment with the data), sweeps incident angle + WAXS arc while recording them, so you don't
    #   rebuild the "_ai{angle}deg_x{x_pos}" name by hand:
    #
    #     from smi_plans import giwaxs_bar, align_sample, SampleList, incidence_axis
    #     samples = SampleList.from_columns(name=curr_names, x=curr_tray)
    #     yield from giwaxs_bar(
    #         samples, dets=[pil2M, pil900KW], t=meas_t,   # current detectors — see ⚠️
    #         incident_angles=[0.10, 0.20, 0.40],          # your real angles
    #         arc_angles=[3.25, 15.25, 3],                 # your WAXS arc, unchanged
    #         align=align_sample,
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) 'rayonix'
    #   (the MAXS detector) was removed with no replacement; (3) 'det_exposure_time(...)' no longer
    #   sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dude = "CM"
    waxs_arc = [3.25, 15.25, 3]
    dets = [pil2M, pil300KW, rayonix, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error) — the current WAXS detector is 'pil900KW' (a different camera, so check beam-center/calibration); and 'rayonix' (the MAXS detector) was removed from the beamline with no current replacement — drop it from this list or ask beamline staff.
    # glob_xoff = 1000
    xlocs1 = [
        45600
    ]  # , 33600, 24600, 14600, 3600, -6400, -16400, -26400, -34400, -44400]

    names1 = [
        "KE_G22G1_50nmDiR_10mg-1"
    ]  # ,'KE_G22G1_50nmDiR_10mg-2','KE_G22G1_50nmDiR_5mg-3','KE_G22G1_50nmDiR_5mg-4','KE_G22G1_15nmDiR_5mg-5','KE_G22G1_15nmDiR_10mg-6','KE_G22G1_15nmDiR_10mg-7','KE_G22G1_15nmDiR_1mg-8','KE_G22G1_35nmDiR_20mg-0', 'KE_G22G1_35nmDiR_1mg-10']

    # what we run now
    curr_tray = xlocs1
    curr_names = names1
    assert len(curr_tray) == len(
        curr_names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, name in zip(curr_tray, curr_names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.th, 0.2)
        # yield from alignCai()
        plt.close("all")
        angle_offset = [0.02, 0.12, 0.32]
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_{angle}deg_x{x_pos}"
        temp = ls.ch1_read.value
        for k in range(0, 3, 1):
            x_meas = x + k * 50
            for j, ang in enumerate(a_off + np.array(angle_offset)):
                yield from bps.mv(piezo.x, x_meas)
                real_ang = 0.08 + angle_offset[j]
                yield from bps.mv(piezo.th, ang)
                sample_name = name_fmt.format(
                    sample=name, angle=real_ang, x_pos=np.round(x_meas, 3)
                )
                sample_id(user_name=dude, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


alignbspos = 11
measurebspos = 1.1
GV7 = TwoButtonShutter("XF:12IDC-VA:2{Det:1M-GV:7}", name="GV7")


def alignmentmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: switches the beamline into alignment mode — inserts the alignment foils, moves
    #   the WAXS arc out of the way, and parks the SAXS beamstop rod for alignment.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' this mode-switching is handled inside align_sample (and
    #   the beamstop rod now has convenience plans). The aligned state is then saved with the data.
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil2M_bs_rod' was renamed — the SAXS beamstop rod is now
    #   'pil2M.beamstop.x_rod' (⚠️ note below); (2) 'det_exposure_time(...)' no longer sets the
    #   exposure unless run as a plan (⚠️ note below).
    # === end smi_plans note ================================================
    # yield from bps.mv(GV7.open_cmd, 1 )
    yield from SMIBeam().insertFoils("Alignement")
    if waxs.arc.position < 8:
        yield from bps.mv(waxs, 8)
    yield from bps.sleep(1)
    yield from bps.mv(pil2M_pos.x, -7)
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def measurementmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: switches the beamline back into measurement mode — moves the SAXS detector and
    #   beamstop rod to the measurement position and inserts the measurement foils.
    # 💡 NEWER, EASIER WAY: 'smi_plans' restores the measurement configuration for you as part of
    #   align_sample (use  yield from pil2M.restore_beamstop()  for the rod).
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — the SAXS beamstop rod is now
    #   'pil2M.beamstop.x_rod' (see ⚠️ note below).
    # === end smi_plans note ================================================
    # yield from bps.mv(GV7.close_cmd, 1 )
    yield from bps.mv(pil2M_pos.x, -7)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from SMIBeam().insertFoils("Measurement")
    yield from bps.sleep(1)


def align_gisaxs_height_Cai(rang=0.3, point=31, der=False):
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Cai(rang=0.3, point=31):
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def align_gisaxsCai():
    align_gisaxs_manualCai(rang=0.2, point=31)
    align_gisaxs_manualCai(rang=0.1, point=21)


def alignCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to alignment mode,
    #   scans height and theta a few times (coarse then fine) to find the surface, sets the
    #   incidence angle, then returns to measurement mode.
    # 💡 NEWER, EASIER WAY: 'smi_plans' bundles all of this into align_sample, which you run once per
    #   sample and which SAVES the alignment result with the data:
    #     from smi_plans import align_sample
    #     yield from align_sample(angle=0.08)       # aligns and records the result
    #   (Then your GISAXS scan can pass align=align_sample so each sample is aligned and logged.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as a
    #   plan (⚠️ note below). (This routine also calls alignmentmodeCai/measurementmodeCai, which use
    #   the renamed beamstop rod — see their ⚠️ notes.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 900)
    yield from align_gisaxs_height_Cai(700, 16, der=True)
    yield from align_gisaxs_th_Cai(1, 11)
    yield from align_gisaxs_height_Cai(300, 11, der=True)
    yield from align_gisaxs_th_Cai(0.5, 16)
    yield from bps.mv(piezo.th, ps.peak + 0.08)
    yield from bps.mv(
        pil2M.roi1.min_xyz.min_y, 900 - 97
    )  # 168 px for 0.1deg at 8.3 m, 330px for 0.25deg at 6.5 m
    yield from align_gisaxs_th_Cai(0.3, 31)
    yield from align_gisaxs_height_Cai(200, 21)
    yield from align_gisaxs_th_Cai(0.05, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()


def alignfine():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a fine (smaller-range) version of the grazing-incidence alignment routine.
    # 💡 NEWER, EASIER WAY: same as alignCai — use 'smi_plans' align_sample once per sample; it does
    #   the coarse+fine theta/height scans and saves the result with the data.
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as a
    #   plan (⚠️ note below). (Calls alignmentmodeCai/measurementmodeCai — see their ⚠️ notes about
    #   the renamed beamstop rod.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 900 - 97)
    yield from align_gisaxs_th_Cai(0.25, 31)
    yield from align_gisaxs_height_Cai(220, 25)
    yield from align_gisaxs_th_Cai(0.1, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()

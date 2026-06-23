# Aligam GiSAXS sample
#


def align_gisaxs_height_subh(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS height (y) alignment — scans y, finds the peak/center with the
    #   peak-stats tool, and moves y there. (A building block used by the alignment routines below.)
    # 💡 NEWER, EASIER WAY: in smi_plans alignment is done once up front with 'align_sample', and
    #   the result is saved with the data automatically — so you don't hand-write the scan + peak
    #   find + move each time. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.5)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (smi_plans' align_sample handles the alignment exposure for you.)
    sample_id(user_name="test", sample_name="test")
    yield from bp.rel_scan([pil2M, pil2Mroi1, pil2Mroi2], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_subh(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS incidence-angle (theta) alignment — scans piezo.th, finds the peak,
    #   and moves theta to it. (A building block used by the alignment routines below.)
    # 💡 NEWER, EASIER WAY: smi_plans aligns the sample once up front with 'align_sample' and saves
    #   the result with the data automatically. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.5)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (smi_plans' align_sample handles the alignment exposure for you.)
    sample_id(user_name="test", sample_name="test")
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


Att_Align1 = att2_6  # att1_12
Att_Align2 = att2_7  # att1_9
GV7 = TwoButtonShutter("XF:12IDC-VA:2{Det:1M-GV:7}", name="GV7")
alignbspossubh = 11.15
measurebspossubh = 1.15


def alignmentmodesubh():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: switches the beamline into "alignment mode" — inserts attenuators, opens the
    #   gate valve, parks the SAXS beamstop rod out of the way, and makes sure the WAXS arc is clear.
    # 💡 NEWER, EASIER WAY: this insert-beamstop / open-valve dance is built into smi_plans'
    #   alignment (align_sample) and beamstop helpers, so you usually don't write it by hand.
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — it's now 'pil2M.beamstop.x_rod'
    #   (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # Att_Align1.set("Insert")
    # yield from bps.sleep(1)
    yield from bps.mv(att1_2, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(att1_3, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(GV7.open_cmd, 1)
    yield from bps.mv(pil2M_bs_rod.x, alignbspossubh)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    if waxs.arc.position < 12:
        yield from bps.mv(waxs, 12)
    sample_id(user_name="test", sample_name="test")


def measurementmodesubh():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: switches the beamline back into "measurement mode" — moves the SAXS beamstop
    #   rod into place, removes the attenuators, and closes the gate valve.
    # 💡 NEWER, EASIER WAY: smi_plans' beamstop helpers (pil2M.insert_beamstop / restore_beamstop)
    #   and the technique runs handle moving the beamstop back for you.
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — it's now 'pil2M.beamstop.x_rod'
    #   (see the ⚠️ note below).
    # === end smi_plans note ================================================
    yield from bps.mv(pil2M_bs_rod.x, measurebspossubh)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    # Att_Align1.set("Retract")
    # yield from bps.sleep(1)
    yield from bps.mv(att1_2, "Retract")
    yield from bps.sleep(1)
    yield from bps.mv(att1_3, "Retract")
    yield from bps.sleep(1)
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(1)
    # mov(waxs,3)


def alignquick():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quicker "alignment mode" — inserts attenuators, opens the gate valve, parks
    #   the SAXS beamstop rod, and moves the WAXS arc clear if it's too low.
    # 💡 NEWER, EASIER WAY: smi_plans' align_sample + beamstop helpers do this setup for you.
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — it's now 'pil2M.beamstop.x_rod'
    #   (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # Att_Align1.set("Insert")
    # yield from bps.sleep(1)
    yield from bps.mv(att1_2, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(att1_3, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(GV7.open_cmd, 1)
    yield from bps.mv(pil2M_bs_rod.x, alignbspossubh)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    if waxs.arc.position < 8:
        yield from bps.mv(waxs, 8)
    sample_id(user_name="test", sample_name="test")


def meas_after_alignquick():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: undoes alignquick — moves the SAXS beamstop rod back into place and removes
    #   the attenuators, ready to measure.
    # 💡 NEWER, EASIER WAY: smi_plans' beamstop helpers (pil2M.insert_beamstop / restore_beamstop)
    #   move the beamstop back for you. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — it's now 'pil2M.beamstop.x_rod'
    #   (see the ⚠️ note below).
    # === end smi_plans note ================================================
    yield from bps.mv(pil2M_bs_rod.x, measurebspossubh)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from bps.mv(att1_2, "Retract")
    yield from bps.sleep(1)
    yield from bps.mv(att1_3, "Retract")
    yield from bps.sleep(1)
    # mov(waxs,3)


def alignsubhgi():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full GISAXS alignment sequence — goes into alignment mode, then does a
    #   coarse-to-fine series of height (y) and incidence-angle (theta) scans, finally setting the
    #   incident angle and returning to measurement mode.
    # 💡 NEWER, EASIER WAY: smi_plans does sample alignment once up front with 'align_sample' (it
    #   handles the coarse/fine scans and the beamstop/attenuator dance) and saves the aligned
    #   position with the data automatically — so the GIWAXS technique runs can call it for you via
    #   align=align_sample. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.5)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (smi_plans' align_sample handles the alignment exposure for you.)
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodesubh()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 863)
    yield from bps.mv(pil2M.roi1.size.y, 100)
    yield from bps.mv(pil2M.roi1.size.x, 100)

    yield from align_gisaxs_height_subh(1000, 16, der=True)
    yield from align_gisaxs_th_subh(1000, 11)
    yield from align_gisaxs_height_subh(500, 11, der=True)
    yield from align_gisaxs_th_subh(500, 11)

    yield from bps.mv(piezo.th, ps.peak - 100)
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 783)
    yield from bps.mv(pil2M.roi1.size.y, 10)
    yield from align_gisaxs_th_subh(300, 31)
    yield from align_gisaxs_height_subh(200, 21)
    yield from align_gisaxs_th_subh(100, 21)
    yield from bps.mv(
        piezo.th, ps.cen + 12
    )  # moves the th to 0.012 degrees positive from aligned 0.1
    yield from measurementmodesubh()


def do_grazingsubh(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GIWAXS) angle scan — aligns the sample, then walks the
    #   incident angle (theta), nudging x along the way, and at each angle scans the WAXS arc.
    #
    # 💡 NEWER, EASIER WAY: aligning then sweeping incident angle + WAXS arc is the smi_plans GIWAXS
    #   run; align_sample aligns and saves the result, incidence_axis sweeps the angle while recording
    #   it into the data, and an arc 'motor_axis' sweeps the WAXS arc:
    #
    #     from smi_plans import giwaxs_run, align_sample, incidence_axis, motor_axis
    #     yield from giwaxs_run("btbtwo3", incident_angles=[0.08, 0.10, 0.20, 0.30],
    #                           t=meas_t, dets=[pil900KW], align=align_sample)
    #
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI 'pil300kwroi2') was retired — it's now
    #   'pil900KW'; (2) the 'det_exposure_time(...)' calls no longer set the exposure unless run as a
    #   plan (see the ⚠️ notes below). (internal: Tier 3.)
    # === end smi_plans note ================================================
    # xlocs = [48403]
    # names = ['BW30-CH-Br-1']
    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    xlocs = [0]
    x_offset = np.linspace(2000, -2000, 41)
    names = ["btbtwo3"]
    prealigned = [0]
    for xloc, name, aligned in zip(xlocs, names, prealigned):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, -1300)
        if aligned == 0:
            yield from alignsubhgi()
            plt.close("all")
        angle_offset = np.linspace(-120, 80, 41)
        # angle_offset = array([-120,-115,-110,-105,-100,-95,-90,-85,-80,-75,-70,-65,-60,-55,-50,-45,-40,-35,-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80])
        e_list = [7060]
        a_off = piezo.th.position
        waxs_arc = [3, 21, 4]
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_run sets it for you via t=.)
        name_fmt = "{sample}_{energ}eV_{angle}deg"
        offset_idx = 0
        # yield from bps.mv(att2_9, 'Insert')
        for i_e, e in enumerate(e_list):
            # yield from bps.mv(energy, e)
            for j, ang in enumerate(a_off - np.array(angle_offset)):
                yield from bps.mv(piezo.x, xloc + x_offset[offset_idx])
                offset_idx += 1
                real_ang = 0.200 + angle_offset[j] / 1000
                yield from bps.mv(piezo.th, ang)
                sample_name = name_fmt.format(sample=name, angle=real_ang, energ=e)
                # print(param)
                sample_id(user_name="NIST", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                # print(RE.md)
                yield from bp.scan(dets, waxs, *waxs_arc)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans giwaxs_run sets it for you via t=.)
        # yield from bps.mv(att2_9, 'Retract')


def align_shortcut():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a short alignment helper — quick align mode, a single height (y) refine, then
    #   back to measurement mode. (Glue used between the grazing grid scans below.)
    # 💡 NEWER, EASIER WAY: smi_plans aligns once up front with 'align_sample' and saves the aligned
    #   position with the data, so you don't re-align by hand between scans. (Nothing here is broken
    #   on its own — the helpers it calls carry the ⚠️ items.)
    # === end smi_plans note ================================================
    yield from alignquick()
    yield from align_gisaxs_height_subh(100, 15)
    yield from meas_after_alignquick()


def do_grazingtemp(meas_t=4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GIWAXS) run at fixed temperature/energy — for each of
    #   eight x ranges it does one coordinated grid scan (x vs WAXS arc), re-aligning the sample
    #   (align_shortcut) between blocks.
    #
    # 💡 NEWER, EASIER WAY: this is a GIWAXS bar — smi_plans' giwaxs_bar takes a sample list, aligns
    #   each with align_sample (saving the result with the data), and runs the arc/x scan, recording
    #   the angle/position/beam into each image and naming the files:
    #
    #     from smi_plans import giwaxs_bar, SampleList, align_sample
    #     samples = SampleList.from_columns(name=[...], x=[...])
    #     yield from giwaxs_bar("P75B2_50C", samples, t=meas_t, dets=[pil900KW], align=align_sample)
    #
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI 'pil300kwroi2') was retired — it's now
    #   'pil900KW'; (2) the many 'det_exposure_time(...)' calls no longer set the exposure unless run
    #   as a plan (see the ⚠️ notes below). (internal: Tier 3.)
    # === end smi_plans note ================================================
    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    e_list = [20300]
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    waxs_arc = [3, 9, 2]

    piezo_x1 = [0, -400, 12]
    piezo_x2 = [-500, -900, 12]
    piezo_x3 = [-1000, -1400, 12]
    piezo_x4 = [-1500, -1900, 12]
    piezo_x5 = [-2000, -2400, 12]
    piezo_x6 = [-2500, -2900, 12]
    piezo_x7 = [-3000, -3400, 12]
    piezo_x8 = [-3500, -3900, 12]

    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV1")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x1, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV2")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x2, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV3")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x3, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV4")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x4, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV5")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x5, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV6")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x6, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV7")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x7, waxs, *waxs_arc, 1)
    yield from align_shortcut()
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV8")
    yield from bp.grid_scan(dets, piezo.x, *piezo_x8, waxs, *waxs_arc, 1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans giwaxs_bar sets it for you via t=.)


def do_singleimage(meas_t=4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single grazing-incidence image set — one coordinated WAXS arc scan
    #   at the current spot (an image at each arc angle).
    # 💡 NEWER, EASIER WAY: smi_plans builds the WAXS arc as an "axis" and runs it in one giwaxs_run
    #   (or acquire) call that records the arc/beam into each image and names the files:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("PVDFWBcool_50C", [pil900KW], [motor_axis("wa", waxs, [3, 5, 7, 9])])
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI 'pil300kwroi2') was retired — it's now
    #   'pil900KW'; (2) the 'det_exposure_time(...)' call no longer sets the exposure unless run as a
    #   plan (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    e_list = [20300]
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_run sets it for you via t=.)
    waxs_arc = [3, 9, 2]
    sample_id(user_name="AK", sample_name="PVDFWBcool_50C_0.088deg_20300eV1")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)


def do_grazing_cool(meas_t=4):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a series of single grazing-incidence WAXS-arc scans, one per named sample
    #   (each does a coordinated WAXS arc scan at the current spot). (Heads up: 'xlocs' is set but
    #   not moved to here, so every block measures the same spot — you may have meant to move x.)
    # 💡 NEWER, EASIER WAY: this is a GIWAXS bar — smi_plans' giwaxs_bar takes a sample list (with
    #   x positions), moves to each, and runs the arc scan, recording the arc/position/beam into each
    #   image and naming the files for you:
    #     from smi_plans import giwaxs_bar, SampleList, align_sample
    #     samples = SampleList.from_columns(name=[...], x=[0, 10000, 20000, ...])
    #     yield from giwaxs_bar("cool_50C", samples, t=meas_t, dets=[pil900KW], align=align_sample)
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI 'pil300kwroi2') was retired — it's now
    #   'pil900KW'; (2) the 'det_exposure_time(...)' call no longer sets the exposure unless run as a
    #   plan (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = [3, 9, 2]
    e_list = [20300]
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans giwaxs_bar sets it for you via t=.)

    xlocs = [0]
    sample_id(user_name="AK", sample_name="PB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [10000]
    sample_id(user_name="AK", sample_name="P50B_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [20000]
    sample_id(user_name="AK", sample_name="PWB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [30000]
    sample_id(user_name="AK", sample_name="P50WB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [40000]
    sample_id(user_name="AK", sample_name="PVDFWB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [50000]
    sample_id(user_name="AK", sample_name="P75WB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [60000]
    sample_id(user_name="AK", sample_name="P75WB_100C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [70000]
    sample_id(user_name="AK", sample_name="P25WB_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [80000]
    sample_id(user_name="AK", sample_name="P25B_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)

    xlocs = [90000]
    sample_id(user_name="AK", sample_name="P75B2_50C_0.088deg_20300eV_cool")
    yield from bp.grid_scan(dets, waxs, *waxs_arc)


#  sample_id(user_name='test', sample_name='test')
#  det_exposure_time(0.5)


def do_grazing1(meas_t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant grazing-incidence (GIWAXS) scan near the sulfur edge — aligns the
    #   sample, then for each energy steps the incident angle (theta) and scans the WAXS arc, taking
    #   an image at each.
    #
    # 💡 NEWER, EASIER WAY: aligning then sweeping energy + incident angle + WAXS arc is the smi_plans
    #   GIWAXS + energy combination — align_sample aligns and saves the result, and energy_axis /
    #   incidence_axis sweep while recording the values into the data and naming the files:
    #
    #     from smi_plans import acquire, align_sample, energy_axis, incidence_axis, motor_axis
    #     yield from acquire("ctrl1_focused", [pil900KW],
    #                        [energy_axis([2460, 2477, 2500]),
    #                         incidence_axis(piezo.th, a_off, [0.40, 0.52, 0.60]),
    #                         motor_axis("wa", waxs, [3, ...])], align=align_sample)
    #
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI 'pil300kwroi2') was retired — it's now
    #   'pil900KW'; (2) the 'det_exposure_time(...)' calls no longer set the exposure unless run as a
    #   plan (see the ⚠️ notes below). (internal: Tier 3.)
    # === end smi_plans note ================================================
    # xlocs = [48403]
    # names = ['BW30-CH-Br-1']
    # Detectors, motors:
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    xlocs = [-37950]
    x_offset = [-200, 0, 200]
    names = ["ctrl1_focused_recheckoldmacro"]
    prealigned = [0]
    for xloc, name, aligned in zip(xlocs, names, prealigned):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, -500)
        if aligned == 0:
            yield from alignYalegi()
            plt.close("all")
        angle_offset = [100, 220, 300]
        e_list = [2460, 2477, 2500]
        a_off = piezo.th.position
        waxs_arc = [3, 87, 15]
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_{energ}eV_{angle}deg"
        for i_e, e in enumerate(e_list):
            yield from bps.mv(energy, e)
            yield from bps.mv(piezo.x, xloc + x_offset[i_e])
            for j, ang in enumerate(a_off - np.array(angle_offset)):
                real_ang = 0.3 + angle_offset[j] / 1000
                yield from bps.mv(piezo.th, ang)
                sample_name = name_fmt.format(sample=name, angle=real_ang, energ=e)
                # print(param)
                sample_id(user_name="FA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                # print(RE.md)
                yield from bp.scan(dets, waxs, *waxs_arc)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)

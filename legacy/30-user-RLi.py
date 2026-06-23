def snapYale(
    t=1,
    dets=[
        pil2M,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick SAXS snapshot with the given exposure time.
    # 💡 NEWER, EASIER WAY:  from smi_plans import acquire
    #     yield from acquire("snap", [pil2M], [], t=t)   # one frame; records beam into the data
    #   (Your line below works as-is EXCEPT the ⚠️ one, which needs a fix now.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.count(dets, num=1)


def ROI_yale():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: briefly inserts an attenuator (att2_11), waits, then retracts it — a
    #   manual beam-attenuation pulse. Nothing here is broken; att2_* attenuators still work
    #   the same way, and smi_plans leaves attenuator handling to you / the technique presets.
    # === end smi_plans note ================================================
    yield from bps.mv(att2_11, "Insert")
    yield from bps.sleep(5)
    yield from bps.mv(att2_11, "Retract")


def do_grazing(meas_t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant grazing-incidence scan near the sulfur edge — for each sample
    #   it aligns, then for each energy and incident angle does a coupled WAXS-arc + x sweep
    #   (an "inner_product_scan", i.e. two motors stepped together) taking images.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans'. Aligning each
    #   sample and sweeping incident angle / energy is the GIWAXS + energy combination, and it
    #   records the angle/energy/beam INTO the data and file name for you. align_sample aligns
    #   and saves the result; energy_axis/incidence_axis sweep while recording:
    #     from smi_plans import giwaxs_run, align_sample, energy_axis, incidence_axis
    #     # for each energy, call giwaxs_run with align=align_sample, sweeping incident angles;
    #     # a coupled two-motor move (waxs.arc + piezo.x together) can be built as paired axes.
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI readout 'pil300kwroi2') was retired
    #   — the current WAXS detector is 'pil900KW'; (2) the 'det_exposure_time(...)' calls no
    #   longer set the exposure unless run as a plan (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]
    dets = [pil2M, pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI readout 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # xlocs = [ 40000,25500,9000,-6000,-22000]
    # names = ['ctrl_glass','ctrl_assq_thin','ctrl_ASSQ_thick','ctrl_PDCBT_ITIC_pt9weight','ctrl_PDCBT_ITIC_ASSQ_1per_pt9weight']

    xlocs = [23800]
    names = ["Sample5-155"]
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of x offset ({len(samples)})"

    for xloc, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, 0.9)  #
        yield from alignCai()
        plt.close("all")

        angle_offset = [0.1, 0.2, 0.3, 0.4]  #
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans technique runs set exposure for you via t=.)

        e_list = [2460, 2477, 2500]
        waxs_arc = [2.8]  # [2.8, 32.8, 6]
        name_fmt = "{sample}_{energ}eV_{angle}deg"

        offset_idx = 0
        for i_e, e in enumerate(e_list):
            yield from bps.mv(energy, e)
            for j, ang in enumerate(a_off - np.array(angle_offset)):
                x_offset = xloc - offset_idx * 1400
                offset_idx += 1
                real_ang = 0.3 + angle_offset[j]
                yield from bps.mv(piezo.th, ang)
                sample_name = name_fmt.format(sample=name, angle=real_ang, energ=e)

                sample_id(user_name="RL", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.inner_product_scan(
                    dets,
                    int(waxs_arc[2]),
                    waxs,
                    float(waxs_arc[0]),
                    float(waxs_arc[1]),
                    piezo.x,
                    x_offset - 600,
                    x_offset + 600,
                )

    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def do_grazing_fine(meas_t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a finer resonant grazing-incidence scan near the sulfur edge — for each
    #   sample it aligns, then for each energy, incident angle, and WAXS-arc position takes an
    #   image (nudging x between frames).
    #
    # 💡 NEWER, EASIER WAY: the GIWAXS + energy combination in 'smi_plans' aligns each sample
    #   and sweeps energy / incident angle / WAXS arc while recording all of them INTO the data
    #   and file name:
    #     from smi_plans import giwaxs_run, align_sample, energy_axis, incidence_axis, motor_axis
    #     # per energy: giwaxs_run(..., align=align_sample) sweeping incident angles + waxs.arc
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI readout 'pil300kwroi2') was retired
    #   — the current WAXS detector is 'pil900KW'; (2) the 'det_exposure_time(...)' calls no
    #   longer set the exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (and its ROI readout 'pil300kwroi2') was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det1 = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    # xlocs = [ 500]
    # names = [ 'Sample5-130_b']
    xlocs = [24000, 500, -29500]
    names = ["Sample5-155_c", "Sample5-130_c", "Sample5-126_c"]
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of x offset ({len(samples)})"

    waxs_arc = np.linspace(2.8, 8.8, 2)  # np.linspace(2.8, 32.8, 6)

    for xloc, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, 0.9)
        yield from alignCai()
        plt.close("all")

        angle_offset = [0.1, 0.5]
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans technique runs set exposure for you via t=.)

        e_list = [2460, 2470, 2474, 2480, 2483, 2500]  # [2460, 2465, 2470, 2475, 2500]
        name_fmt = "{sample}_{energ}eV_{angle}deg_waxs{num}_x{xpos}"

        for i_e, e in enumerate(e_list):
            yield from bps.mv(energy, e)
            for j, ang in enumerate(a_off + np.array(angle_offset)):
                real_ang = 0.3 + angle_offset[j]
                yield from bps.mv(piezo.th, ang)
                for waxs_pos in waxs_arc:
                    yield from bps.mv(waxs, waxs_pos)
                    sample_name = name_fmt.format(
                        sample=name,
                        angle="%04.2f" % real_ang,
                        energ=e,
                        num="%05.2f" % waxs_pos,
                        xpos="%07.1f" % piezo.x.position,
                    )
                    sample_id(user_name="RL", sample_name=sample_name)
                    if waxs_pos < 4:
                        det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
                        yield from bp.count(det1, num=1)
                        yield from bps.mvr(piezo.x, 150)
                    else:
                        det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
                        yield from bp.count(det1, num=1)
                        yield from bps.mvr(piezo.x, 150)

                print(f"\n\t=== Sample: {sample_name} ===\n")

    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


alignbspos = 11
measurebspos = 0.7


def test():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick manual jog of the SAXS-detector x position by 200. Just a test
    #   move — nothing to migrate (pil2M_pos still works the same way).
    # === end smi_plans note ================================================
    yield from bps.mvr(pil2M_pos.x, 200)


def alignmentmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "alignment mode" — opens the fast shutter (GV7),
    #   inserts an attenuator, swings the WAXS arc clear, and parks the SAXS beamstop rod.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' this kind of get-ready-to-align setup is bundled into
    #   the alignment helper (align_sample), so you don't switch modes by hand. There are also
    #   convenience plans to park/restore the SAXS beamstop rod (see ⚠️ below).
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the SAXS beamstop rod 'pil2M_bs_rod' was renamed — it's now
    #   'pil2M.beamstop.x_rod'; (2) the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (⚠️ notes below). (internal: helper.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)
    yield from bps.mv(att2_11, "Insert")

    if waxs.arc.position < 8:
        yield from bps.mv(waxs, 8)
    yield from bps.sleep(1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def measurementmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "measurement mode" — closes the fast shutter
    #   (GV7), re-positions the SAXS detector, moves the SAXS beamstop rod to the measurement
    #   spot, and retracts the attenuator.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the align helper (align_sample) leaves the beamline
    #   ready to measure, and there are convenience plans to restore the SAXS beamstop rod.
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the SAXS beamstop rod 'pil2M_bs_rod' was renamed — it's now
    #   'pil2M.beamstop.x_rod' (⚠️ note below). (internal: helper.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from bps.mv(att2_11, "Retract")
    yield from bps.sleep(1)


def align_gisaxs_height_Cai(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment step — scans sample height (piezo.y) over a small range,
    #   finds the peak/edge, and moves there. A building block of alignCai below.
    # 💡 NEWER, EASIER WAY: smi_plans does grazing alignment with align_sample, which runs the
    #   height + theta search for you and saves the found position with the data. Nothing here
    #   is broken — it's just hand-rolled alignment that align_sample now packages.
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Cai(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment step — scans the sample tilt (piezo.th) over a small range,
    #   finds the peak, and moves there. A building block of alignCai below.
    # 💡 NEWER, EASIER WAY: smi_plans does grazing alignment with align_sample, which runs the
    #   theta search for you and saves the found angle with the data. Nothing here is broken.
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def alignCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to alignment
    #   mode, then does several height + tilt searches (coarse to fine) to land the sample in
    #   the beam, and switches back to measurement mode.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' packages grazing alignment as align_sample — it does the
    #   coarse-to-fine height/theta search for you and SAVES the found position alongside your
    #   data, so it doesn't get lost in a print-out. You typically run it once per sample (or
    #   pass align=align_sample to giwaxs_run) instead of calling a custom routine:
    #     from smi_plans import align_sample
    #     yield from align_sample()                     # aligns and records the result
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: helper.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 910)
    yield from align_gisaxs_height_Cai(700, 16, der=True)
    yield from align_gisaxs_th_Cai(1, 11)
    yield from align_gisaxs_height_Cai(300, 11, der=True)
    yield from align_gisaxs_th_Cai(0.5, 16)
    yield from bps.mv(piezo.th, ps.peak + 0.3)
    yield from bps.mv(
        pil2M.roi1.min_xyz.min_y, 910 - 487
    )  # 168 px for 0.1deg at 8.3 m, 330px for 0.25deg at 6.5 m 97 for 6 m and 0.08
    yield from align_gisaxs_th_Cai(0.3, 31)
    yield from align_gisaxs_height_Cai(200, 21)
    yield from align_gisaxs_th_Cai(0.05, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()


#

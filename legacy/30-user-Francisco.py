# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Francisco.py


def snapYale(
    t=1,
    dets=[
        pil2M,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS snapshot at the current position/energy.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a one-shot transmission grab that also records
    #   the energy/beam into the saved data and file name:
    #     from smi_plans import transmission_run
    #     yield from transmission_run("snap", [pil2M], t=t)   # one image, metadata recorded
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ line which needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)).
    yield from bp.count(dets, num=1)


def ROI_yale():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: briefly inserts an attenuator (to protect/check the beam), waits,
    #   then retracts it. This is a small hand-run helper, not a measurement.
    # 💡 There's no acquisition here to migrate; attenuator moves like this stay the same
    #   under smi_plans (att2_11 is fine — no change needed). Nothing broken here.
    # === end smi_plans note ================================================
    yield from bps.mv(att2_11, "Insert")
    yield from bps.sleep(5)
    yield from bps.mv(att2_11, "Retract")


def do_grazing(meas_t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy (sulfur/tin-edge, ~2460-2500 eV) grazing-incidence
    #   scan — for each sample it aligns, then sweeps energy, incident angle, and WAXS-arc
    #   position, taking a WAXS image (with a small x-offset walk) at each combination.
    #
    # 💡 NEWER, EASIER WAY: aligning each sample and sweeping energy / incident angle / WAXS
    #   arc is the 'smi_plans' GIWAXS + energy combination. align_sample aligns once and
    #   saves the result with the data; energy_axis/incidence_axis sweep while recording the
    #   energy and angle straight into each image (no hand-built name needed):
    #
    #     from smi_plans import giwaxs_run, align_sample, energy_axis, incidence_axis, motor_axis
    #     yield from giwaxs_run(
    #         "ctrl_ASSQ_thick_finescan", [pil900KW],   # WAXS detector (see ⚠️ on pil300KW)
    #         t=meas_t, align=align_sample,
    #         axes=[energy_axis([2460, 2477, 2500]),    # your energies
    #               incidence_axis(piezo.th, piezo.th.position, [0.1, 0.22, 0.3]),  # your angles
    #               motor_axis("waxs", waxs, np.linspace(2.8, 32.8, 6))])           # your arc sweep
    #
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). (Its ROI signal 'pil300kwroi2' depends on that same retired detector, so update it too.)
    # xlocs = [ 40000,25500,9000,-6000,-22000]
    # names = ['ctrl_glass','ctrl_assq_thin','ctrl_ASSQ_thick','ctrl_PDCBT_ITIC_pt9weight','ctrl_PDCBT_ITIC_ASSQ_1per_pt9weight']

    xlocs = [9000]
    names = ["ctrl_ASSQ_thick_finescan"]
    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of x offset ({len(samples)})"

    for xloc, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, 0.9)  # ask misha for the value
        yield from alignCai()
        plt.close("all")

        angle_offset = [0.1, 0.22, 0.3]  # ask misha
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (smi_plans' giwaxs_run sets it for you via t=.)

        e_list = [2460, 2477, 2500]
        waxs_arc = [2.8, 32.8, 6]
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

                sample_id(user_name="FA", sample_name=sample_name)
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

    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def do_grazing_fine(meas_t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a finer tender-energy grazing scan — per sample it aligns, then for
    #   each energy/angle it steps the WAXS arc, picking a short or long exposure depending
    #   on the arc position, and nudges x between shots.
    #
    # 💡 NEWER, EASIER WAY: this is the same 'smi_plans' GIWAXS + energy pattern as
    #   do_grazing. align_sample aligns and saves; energy_axis/incidence_axis and a WAXS-arc
    #   motor_axis sweep while recording energy/angle/WAXS-position into each image:
    #
    #     from smi_plans import giwaxs_run, align_sample, energy_axis, incidence_axis, motor_axis
    #     yield from giwaxs_run(
    #         "P_I_navy2", [pil900KW],                  # WAXS detector (see ⚠️ on pil300KW)
    #         t=meas_t, align=align_sample,
    #         axes=[energy_axis([2470, 2475, 2476, 2477, 2478, 2480, 2482, 2484, 2486]),
    #               incidence_axis(piezo.th, piezo.th.position, [0.22]),
    #               motor_axis("waxs", waxs, np.linspace(2.8, 32.8, 6))])
    #     # (the short-vs-long exposure trick by arc angle is a per-point detail; smi_plans
    #     #  lets you vary t or split the arc into two acquire calls if you still need it.)
    #
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ notes below); (2) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). (Its ROI signal 'pil300kwroi2' depends on that same retired detector, so update it too.)
    det1 = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    # xlocs = [ -51500, -34700, -20500, -5500, 10000, 25000, 40000]
    # names = ['ctrl_ITO_finescan','P_I_A_90perA_finescan', 'P_I_A_50perA_finescan', 'P_I_A_10perA_finescan', 'P_I_A_01perA_finescan', 'P_I_A_00perA_finescan', 'ctrl_ASSQ_thickagain_finescan']

    # xlocs = [ -11500, -33500, -50000]
    # names = ['P_I_00perA_navy_b', 'P_I_A_01perA_teal_b', 'ctrl_ASSQ_thick_magenta_b']

    xlocs = [-45600, -27500, -10500, 6400]
    names = ["P_I_navy2", "P_I_10perA_green", "P_I_50perA_lightblue", "P_I_90perA_pink"]

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of x offset ({len(samples)})"

    waxs_arc = np.linspace(2.8, 32.8, 6)
    # waxs_arc = np.linspace(2.8, 32.8, 2)

    for xloc, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, 0.9)
        yield from alignCai()
        plt.close("all")

        angle_offset = [0.22]
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (smi_plans' giwaxs_run sets it for you via t=.)

        e_list = [
            2470,
            2475,
            2476,
            2477,
            2478,
            2480,
            2482,
            2484,
            2486,
        ]  # , 2465, 2467, 2470, 2473, 2475, 2477, 2500]
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
                        angle=real_ang,
                        energ=e,
                        num="%05.2f" % waxs_pos,
                        xpos="%07.1f" % piezo.x.position,
                    )
                    sample_id(user_name="FA2", sample_name=sample_name)
                    if waxs_pos < 4:
                        det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
                        yield from bp.count(det1, num=1)
                        yield from bps.mvr(piezo.x, 200)
                    else:
                        det_exposure_time(5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(5)  — or at the prompt:  RE(det_exposure_time(5)).
                        yield from bp.count(det1, num=1)
                        yield from bps.mvr(piezo.x, 200)

                print(f"\n\t=== Sample: {sample_name} ===\n")

    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


alignbspos = 11
measurebspos = 0.7


def test():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a scratch one-liner that nudges the SAXS detector x by 200. No
    #   acquisition here — nothing to migrate. (pil2M_pos.x is fine.)
    # === end smi_plans note ================================================
    yield from bps.mvr(pil2M_pos.x, 200)


def alignmentmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "alignment mode" — opens the gate valve,
    #   inserts an attenuator, parks the WAXS arc, and slides the SAXS beamstop rod in so
    #   you can see the direct beam while aligning.
    # 💡 In 'smi_plans' this kind of beamstop/attenuator setup is handled for you by the
    #   align step (e.g. align_sample) before a measurement, so you usually don't call it
    #   by hand. (Just context — nothing here is wrong except the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the SAXS beamstop rod 'pil2M_bs_rod' was renamed
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (GV7 / att2_11 / pil2M_pos.x are fine.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)
    yield from bps.mv(att2_11, "Insert")

    if waxs.arc.position < 8:
        yield from bps.mv(waxs, 8)
    yield from bps.sleep(1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def measurementmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the counterpart to alignmentmodeCai — puts the beamline back into
    #   "measure mode" (closes the gate valve, slides the beamstop rod to its measuring
    #   spot, retracts the attenuator) ready to collect real data.
    # 💡 In 'smi_plans' the align step restores the beamstop/attenuator for you after
    #   aligning, so this is normally automatic. (Nothing here is wrong except the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the SAXS beamstop rod 'pil2M_bs_rod' was renamed — see the
    #   ⚠️ note below. (GV7 / att2_11 / pil2M_pos.x are fine.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from bps.mv(att2_11, "Retract")
    yield from bps.sleep(1)


def align_gisaxs_height_Cai(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a height-alignment scan — sweeps the sample y, finds the peak/edge,
    #   and moves y there. One building block of the alignment routine below.
    # 💡 In 'smi_plans' alignment like this is done once up front by align_sample, and the
    #   result is saved with the data automatically — you don't usually call the individual
    #   height/theta scans by hand. (Nothing broken here.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Cai(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a theta (incident-angle) alignment scan — sweeps piezo.th, finds the
    #   peak, and moves there. The other building block of the alignment routine below.
    # 💡 In 'smi_plans' this is handled by align_sample as part of one up-front alignment,
    #   with the result recorded into the data. (Nothing broken here.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def alignCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to alignment
    #   mode, then repeatedly refines sample height and incident angle (coarse then fine),
    #   and switches back to measure mode at the end.
    # 💡 NEWER, EASIER WAY: 'smi_plans' bundles this whole align-the-sample dance into one
    #   call, align_sample, and saves the alignment result alongside your data. The GIWAXS
    #   techniques (giwaxs_run / giwaxs_bar) can call it for you per sample via align=, so
    #   you usually don't run a hand-written alignment like this anymore:
    #     from smi_plans import align_sample
    #     yield from align_sample()        # aligns and records the result
    #   (Just a tidier option to try later — this still works as-is except the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' line below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 3.)
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).
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

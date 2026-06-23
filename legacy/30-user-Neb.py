# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Francisco.py


def snapYale(
    t=1,
    dets=[
        pil2M,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sets the camera exposure to t seconds and grabs a single
    #   SAXS image (a quick "snapshot" of whatever is in the beam).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans'.
    #   Its 'acquire(...)' takes the shot AND records beam/energy/etc. into the
    #   saved data for you, and it sets the exposure via 't=' so you don't call
    #   det_exposure_time yourself. A one-shot snapshot would look like:
    #
    #     from smi_plans import acquire, saxs_waxs_dets
    #     yield from acquire("snap", saxs_waxs_dets(use_waxs=False), [], reads=None)  # [] = no scan, one image
    #
    #   (Optional tidy-up. Your code still runs — see the ⚠️ note below for the
    #    one line that needs a small change to actually take effect now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(t)' below no longer sets the
    #   exposure on its own (see the ⚠️ note on that line).
    # === end smi_plans note ================================================
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (smi_plans' presets set exposure for you via t=.)
    yield from bp.count(dets, num=1)


def ROI_yale():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: briefly pokes attenuator foil att2_11 in for 5 seconds and
    #   then pulls it back out (a little utility, not a measurement).
    #   The attenuators (att2_*) are unchanged and still work the same way.
    #   There's nothing here to migrate to smi_plans. (Nothing is broken.)
    # === end smi_plans note ================================================
    yield from bps.mv(att2_11, "Insert")
    yield from bps.sleep(5)
    yield from bps.mv(att2_11, "Retract")


def do_grazing(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample along x, aligns the surface to the beam
    #   (alignCai), then sweeps the WAXS arc and a few incident angles, taking a
    #   grazing-incidence image at each — i.e. a multi-sample GIWAXS run.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a GIWAXS preset that does the align +
    #   angle sweep + arc sweep for a whole bar of samples, and records the angle,
    #   energy, beam, etc. into each file automatically (no hand-built name needed):
    #
    #     from smi_plans import giwaxs_bar          # multi-sample grazing-incidence
    #     # describe your samples (names + x positions) and the angles/arc you want,
    #     # and giwaxs_bar aligns each one and measures it; see also giwaxs_run for a
    #     # single sample, and incidence_axis to build the incident-angle list.
    #
    #   (Suggestion for later — your loop below still works EXCEPT for the lines
    #    marked ⚠️, which use detectors that were removed and would error now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' and 'rayonix',
    #   which were both removed from the beamline (see the ⚠️ note on that line),
    #   and 'det_exposure_time(...)' no longer sets the exposure on its own (⚠️ notes).
    # === end smi_plans note ================================================
    dets = [pil2M, pil300KW, rayonix]  # , pil300kwroi2, xbpm3.sumY, xbpm2.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed — the current WAXS detector is 'pil900KW' (a different camera, so check beam-center/calibration); and 'rayonix' (the MAXS detector) was removed with no replacement. Both would error — drop rayonix and swap pil300KW->pil900KW.

    # xlocs = [ -43000, -25000, -7000, 10000, 25000, 40000 ]
    # names = ['bar1_C1a_50nm_sam1', 'bar1_C1a_50nm_sam2',  'bar1_C2B1_50nm_sam1',  'bar1_C2B1_50nm_sam2', 'bar1_Nafion_50nm_sam1', 'bar1_Nafion_50nm_sam2']
    # xlocs = [ -43000, -26000, -9000, 8000, 24000 ]
    # names = ['bar1_C1a_50nm_sam1', 'bar1_C1a_50nm_sam2',  'bar1_C2B1_50nm_sam1',  'bar1_C2B1_50nm_sam2', 'bar1_Nafion_50nm_sam1']
    xlocs = [-46000, -31000, -13000, 3500, 21500, 37000]
    names = [
        "bar2_C1a_250nm_sam1",
        "bar2_C1a_250nm_sam2",
        "bar2_C2B1_250nm_sam1",
        "bar2_C2B1_250nm_sam2",
        "bar2_Nafion_250nm_sam1",
        "bar2_Nafion_250nm_sam2",
    ]

    assert len(xlocs) == len(
        names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of x offset ({len(samples)})"

    for xloc, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, xloc)
        yield from bps.mv(piezo.th, 0.1)
        yield from alignCai()
        plt.close("all")

        angle_offset = [-0.05, -0.02, 0, 0.02, 0.1]
        a_off = piezo.th.position  #  yield from bps.mv(piezo.th, ps.peak + 0.1)
        # det_exposure_time(meas_t)

        waxs_arc = np.linspace(2.8, 32.8 + 18, 6 + 3)
        name_fmt = "{sample}_{energ}eV_{angle}deg_waxs{num}_{exposure}s_x{xpos}"

        # offset_idx = 0
        for j, ang in enumerate(a_off + np.array(angle_offset)):
            # x_offset =  xloc - offset_idx * 1800
            # offset_idx += 1
            real_ang = 0.1 + angle_offset[j]
            yield from bps.mv(piezo.th, ang)
            for waxs_pos in waxs_arc:
                yield from bps.mv(waxs, waxs_pos)
                sample_name = name_fmt.format(
                    sample=name,
                    angle="%04.2f" % real_ang,
                    energ="%07.1f" % energy.position.energy,
                    num="%05.2f" % waxs_pos,
                    xpos="%07.0f" % piezo.x.position,
                    exposure=meas_t,
                )
                sample_id(user_name="ET", sample_name=sample_name)
                det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (smi_plans' giwaxs presets set exposure for you via t=.)
                yield from bp.count(dets, num=1)
                yield from bps.mvr(piezo.x, 200)

                print(f"\n\t=== Sample: {sample_name} ===\n")

    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing when called plain. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.


alignbspos = 11
measurebspos = 0.7


def test():
    yield from bps.mvr(pil2M_pos.x, 200)


def alignmentmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "alignment" mode — opens the shutter,
    #   inserts alignment foils, parks the WAXS arc, and slides the SAXS beamstop
    #   rod to its alignment position.
    #
    # 💡 smi_plans CONTEXT: in smi_plans the GIWAXS presets handle this align-vs-measure
    #   switching for you (see align_sample / giwaxs_run), so you usually don't drive
    #   the beamstop by hand. If you do, the rod has convenience helpers (insert/restore).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed and 'det_exposure_time'
    #   is now a plan — see the ⚠️ notes on those two lines.
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.open_cmd, 1)
    yield from SMIBeam().insertFoils("Alignement")

    if waxs.arc.position < 8:
        yield from bps.mv(waxs, 8)
    yield from bps.sleep(1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.


def measurementmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline back into "measurement" mode — moves the
    #   SAXS detector back, slides the beamstop rod to its measurement position,
    #   and swaps in the measurement foils.
    #   (smi_plans' GIWAXS presets manage this align/measure switch for you.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — see the ⚠️ note on
    #   that line below.
    # === end smi_plans note ================================================
    # yield from bps.mv(GV7.close_cmd, 1 ) #comment out to use pil2M
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from SMIBeam().insertFoils("Measurement")
    yield from bps.sleep(1)


def align_gisaxs_height_Cai(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: one alignment step — scans the sample height (piezo.y) over a
    #   small range, finds the center from the peak, and moves there. A building
    #   block of alignCai. In smi_plans this kind of step lives inside 'align_sample'.
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Cai(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: one alignment step — scans the sample tilt (piezo.th) over a
    #   small range, finds the peak, and moves there. A building block of alignCai.
    #   In smi_plans this is handled inside 'align_sample'. (Nothing here is broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def alignCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to
    #   alignment mode, then walks the sample height (piezo.y) and tilt (piezo.th)
    #   in a few coarse-to-fine scans to find the surface, then returns to
    #   measurement mode. (The align_gisaxs_height_Cai / align_gisaxs_th_Cai helpers
    #   above are just the individual height/tilt scan steps this calls.)
    #
    # 💡 NEWER, EASIER WAY: smi_plans has 'align_sample' (and the 'giwaxs_run' /
    #   'giwaxs_bar' presets call it automatically) which does this surface alignment
    #   for you and, importantly, SAVES the found angle/height alongside your data, so
    #   you don't have to keep it in your head or re-align by hand next time:
    #
    #     from smi_plans import align_sample, giwaxs_run
    #     # giwaxs_run("mysample", ...) aligns first, then measures, recording it all.
    #
    #   (Optional — this routine still works EXCEPT for the ⚠️ line below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(0.5)' below is now a plan and
    #   does nothing called plain — see the ⚠️ note on that line.
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_x, 457)
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 910)
    yield from align_gisaxs_height_Cai(700, 16, der=True)
    yield from align_gisaxs_th_Cai(1, 11)
    yield from align_gisaxs_height_Cai(300, 11, der=True)
    yield from align_gisaxs_th_Cai(0.5, 16)
    yield from bps.mv(piezo.th, ps.peak + 0.1)  # 0.3
    yield from bps.mv(
        pil2M.roi1.min_xyz.min_y, 910 - 168
    )  # 168 px for 0.1deg at 8.3 m, 330px for 0.25deg at 6.5 m 97 for 6 m and 0.08
    yield from align_gisaxs_th_Cai(0.3, 31)
    yield from align_gisaxs_height_Cai(200, 21)
    yield from align_gisaxs_th_Cai(0.05, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()


#

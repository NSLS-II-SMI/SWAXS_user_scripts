def gocko(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample along x, aligns the surface (alignCai), then
    #   sweeps the WAXS arc at a handful of incident angles, recording a WAXS scan
    #   at each — a multi-sample grazing-incidence (GIWAXS) run.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a GIWAXS preset that aligns each sample
    #   and does the angle/arc sweep across a whole bar, writing the angle, energy,
    #   beam intensity, etc. into each file automatically:
    #
    #     from smi_plans import giwaxs_bar        # multi-sample grazing-incidence
    #     # give it your sample names + x positions and the angles/arc you want;
    #     # see giwaxs_run for a single sample and incidence_axis to build angles.
    #
    #   (Optional tidy-up. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' no longer sets the exposure on its own — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    dets = [pil300KW, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). (xbpm3.sumY is fine.)
    xlocs1 = [-48000, -34000, -23000, -12000, 2000, 15000, 30000, 43000]
    names1 = [
        "BWXLE-new-water30min-CsBrsoaked-THF",
        "BWXLE-new-water30min-CsBrsoaked-DCM",
        "BW30-new-water30min-CsBrsoaked-THF",
        "BW30-new-water30min-CsBrsoaked-DCM",
        "BWXLE-new-sonic1min-CsBrsoaked-THF",
        "BWXLE-new-sonic1min-CsBrsoaked-DCM",
        "BW30-new-sonic1min-CsBrsoaked-THF",
        "BW30-new-sonic1min-CsBrsoaked-DCM",
    ]

    # what we run now
    curr_tray = xlocs1
    curr_names = names1
    assert len(curr_tray) == len(
        curr_names
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    waxs_arc = [2.83, 26.83, 5]
    for x, name in zip(curr_tray, curr_names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.th, 0.9)
        yield from alignCai()
        plt.close("all")
        angle_offset = [-0.05, -0.02, 0, 0.02, 0.05]
        a_off = piezo.th.position
        det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(meas_t)  inside a plan, or  RE(det_exposure_time(meas_t))  at the prompt. (smi_plans' giwaxs presets set exposure via t=.)
        name_fmt = "{sample}_{angle}deg"
        for j, ang in enumerate(a_off + np.array(angle_offset)):
            yield from bps.mv(piezo.x, (x + j * 0))
            real_ang = 0.1 + angle_offset[j]
            yield from bps.mv(piezo.th, ang)
            sample_name = name_fmt.format(sample=name, angle=float("%.3f" % real_ang))
            sample_id(user_name="BO_13.47keV", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.


def test():
    yield from bps.mv(att1_9, "Insert")


def gocko_res(meas_t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a RESONANT grazing-incidence run — aligns each sample, then at
    #   a couple of incident angles it steps the X-ray energy (here just 5018 eV) and
    #   takes an image at each energy. (Heads up: the big triple-quoted block in the
    #   middle is an older version parked as a note — it doesn't run.)
    #
    # 💡 NEWER, EASIER WAY: smi_plans pairs a grazing-incidence preset with an energy
    #   axis so it aligns, steps energy, and records energy/angle/beam into every file:
    #
    #     from smi_plans import giwaxs_run, energy_axis
    #     # giwaxs_run handles align + measure for a sample; energy_axis(np.array([5018]))
    #     # provides the resonant energy steps (and it manages the beam feedback for you).
    #     # For a ready-made resonant reflectivity-style scan see also xrr_resonant_run.
    #
    #   (Optional. Your code still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed) and
    #   'det_exposure_time(...)' is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    xlocs1 = [-46000]
    names1 = ["Reso-BWXLE-new-NaClsoaked-water30min-THF"]
    # xlocs1 = [-46000, -35000, -22000, -10000]
    # names1 = ['Reso-BWXLE-new-NaClsoaked-water30min-THF','Reso-BWXLE-new-NaClsoaked-water30min-DCM','Reso-BW30-new-NaClsoaked-water30min-THF','Reso-BW30-new-NaClsoaked-water30min-DCM']
    xoffset = 0
    curr_tray = xlocs1
    curr_names = names1

    # ener = [5008, 5013, 5018, 5023, 5008]
    ener = [5018]

    det2 = [pil300KW, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration). (xbpm3.sumY is fine.)
    waxs_arc = [2.83, 56.83, 10]
    """
        for x, name in zip(curr_tray, curr_names): 
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.th, 0.2)
            yield from alignCai()
            a_off = piezo.th.position
            plt.close('all')
            yield from bps.mv(att2_11, 'Insert')
            angle = [-0.12, 0.08, 0.24]
            det_exposure_time(meas_t) 
            name_fmt = '{sample}_{angle}deg_{energy}eV_{num}'
            for j, ang in enumerate( np.array(angle) ):
                yield from bps.mv(piezo.x, (x-xoffset+j*0))
                yield from bps.mv(piezo.th,  a_off + ang)
                i=0
                for energies in ener:
                    energy.move(energies)
                    sample_name = name_fmt.format(sample=name, angle=float('%.3f'%(ang+0.25)), energy = energies, num =i)
                    sample_id(user_name='BO', sample_name=sample_name)
                    print(f'\n\t=== Sample: {sample_name} ===\n')
                    yield from bp.scan(det2, waxs, *waxs_arc)
                    i += 1
        """
    curr_tray = xlocs1
    curr_names = names1
    det1 = [pil2M]

    xoffset = 200
    for x, name in zip(curr_tray, curr_names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.th, 0.2)
        yield from alignCai()
        a_off = piezo.th.position
        plt.close("all")
        yield from bps.mv(att2_5, "Insert")
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        i = 0
        a_off = piezo.th.position
        angle = [-0.12, 0.08]
        for j, ang in enumerate(angle):
            yield from bps.mv(piezo.x, (x - xoffset + j * 0))
            yield from bps.mv(piezo.th, a_off + ang)
            name_fmt = "{sample}_{angle}deg_{energy}eV_{num}"
            i = 0
            for energies in ener:
                energy.move(energies)
                sample_name = name_fmt.format(
                    sample=name,
                    angle=float("%.3f" % (ang + 0.25)),
                    energy=energies,
                    num=i,
                )
                sample_id(user_name="BO", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(det1, num=1)
                i += 1

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.


alignbspos = 11
measurebspos = 1.2
GV7 = TwoButtonShutter("XF:12IDC-VA:2{Det:1M-GV:7}", name="GV7")


def alignmentmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "alignment" mode — opens the shutter,
    #   inserts alignment foils, parks the WAXS arc, and slides the SAXS beamstop
    #   rod to its alignment position. (smi_plans' GIWAXS presets do this align/measure
    #   switching for you via align_sample / giwaxs_run.)
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
    yield from bps.mv(pil2M_bs_rod.x, alignbspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.


def measurementmodeCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline back into "measurement" mode — closes the
    #   alignment shutter, moves the SAXS detector back, slides the beamstop rod to
    #   its measurement position, and swaps in the measurement foils.
    #   (smi_plans' GIWAXS presets manage this align/measure switch for you.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_rod' was renamed — see the ⚠️ note on
    #   that line below.
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.mv(pil2M_pos.x, -4)
    yield from bps.mv(pil2M_bs_rod.x, measurebspos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
    yield from bps.sleep(1)
    yield from SMIBeam().insertFoils("Measurment")
    yield from bps.sleep(1)


def align_gisaxs_height_Cai(rang=0.3, point=31, der=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: one alignment step — scans the sample height (piezo.y), finds
    #   the center, and moves there. A building block of alignCai; in smi_plans this
    #   lives inside 'align_sample'. (Nothing here is broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.y, -rang, rang, point)
    ps(der=der)
    yield from bps.mv(piezo.y, ps.cen)


def align_gisaxs_th_Cai(rang=0.3, point=31):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: one alignment step — scans the sample tilt (piezo.th), finds
    #   the peak, and moves there. A building block of alignCai; in smi_plans this is
    #   handled inside 'align_sample'. (Nothing here is broken.)
    # === end smi_plans note ================================================
    yield from bp.rel_scan([pil2M], piezo.th, -rang, rang, point)
    ps()
    yield from bps.mv(piezo.th, ps.peak)


def align_gisaxsCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small wrapper that runs a coarse then fine alignment step.
    #   smi_plans bundles this whole align routine into 'align_sample' (called for you
    #   by giwaxs_run / giwaxs_bar). (Nothing here is broken.)
    # === end smi_plans note ================================================
    align_gisaxs_manualCai(rang=0.2, point=31)
    align_gisaxs_manualCai(rang=0.1, point=21)


def alignCai():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the full grazing-incidence alignment routine — switches to
    #   alignment mode, walks the sample height (piezo.y) and tilt (piezo.th) in a few
    #   coarse-to-fine scans to find the surface, then returns to measurement mode.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has 'align_sample' (and giwaxs_run / giwaxs_bar
    #   call it automatically), which does this alignment AND saves the found
    #   angle/height with your data so you don't have to track it by hand:
    #
    #     from smi_plans import align_sample, giwaxs_run
    #     # giwaxs_run("mysample", ...) aligns first, then measures, recording it all.
    #
    #   (Optional — this routine still works EXCEPT for the ⚠️ line below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(0.5)' is now a plan and does
    #   nothing called plain — see the ⚠️ note on that line.
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 900)
    yield from align_gisaxs_height_Cai(700, 16, der=True)
    yield from align_gisaxs_th_Cai(1, 11)
    yield from align_gisaxs_height_Cai(300, 11, der=True)
    yield from align_gisaxs_th_Cai(0.5, 16)
    yield from bps.mv(piezo.th, ps.peak + 0.25)
    yield from bps.mv(
        pil2M.roi1.min_xyz.min_y, 900 - 97
    )  # 168 px for 0.1deg at 8.3 m, 330px for 0.25deg at 6.5 m 97 for 6 m and 0.08
    yield from align_gisaxs_th_Cai(0.3, 31)
    yield from align_gisaxs_height_Cai(200, 21)
    yield from align_gisaxs_th_Cai(0.05, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()


def alignfine():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a finer-grained version of the grazing-incidence alignment —
    #   same idea as alignCai but with tighter tilt/height scans for a precise final
    #   surface alignment. smi_plans' 'align_sample' (used by giwaxs_run/giwaxs_bar)
    #   does this for you and saves the result with your data.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(0.5)' is now a plan and does
    #   nothing called plain — see the ⚠️ note on that line.
    # === end smi_plans note ================================================
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(0.5)  inside a plan, or  RE(det_exposure_time(0.5))  at the prompt.
    sample_id(user_name="test", sample_name="test")
    yield from alignmentmodeCai()
    yield from bps.mv(pil2M.roi1.min_xyz.min_y, 916 - 330)
    yield from align_gisaxs_th_Cai(0.25, 31)
    yield from align_gisaxs_height_Cai(220, 25)
    yield from align_gisaxs_th_Cai(0.1, 21)
    yield from bps.mv(piezo.th, ps.cen)
    yield from measurementmodeCai()

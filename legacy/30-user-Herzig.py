def alignement_herzig_2020_3():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: stores this bar's sample names + positions + measured incidence angles
    #   into module-level globals so the other plans can read them (the active alignment loop
    #   is commented out here). It's bookkeeping/alignment setup, not a measurement.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you don't keep sample tables and aligned angles in
    #   loose globals. You put them in a SampleList (one row per sample, with its position and
    #   measured angle), and grazing-incidence alignment is run by the bar runner up front and
    #   the result is recorded WITH the data automatically:
    #
    #     from smi_plans import SampleList
    #     bar = SampleList.from_columns(
    #         names=["s315h", "s324h", "s325h", "s338h", "s339v", "s339h", "313h"],
    #         piezo_x=[20000, 50000, 36000, 12000, -14000, -40000, -59000],
    #         piezo_y=[8000, -2900, -2900, -2900, -2800, -2700, -2670],
    #     )
    #     # then: yield from giwaxs_bar(bar, align=alignement_gisaxs, ...)  (it aligns each sample)
    #
    #   (Nothing here is broken — it's just setup. This is a tidier pattern to adopt later.)
    # === end smi_plans note ================================================
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa, y_hexa

    names = ["s315h", "s324h", "s325h", "s338h", "s339v", "s339h", "313h"]
    x_piezo = [20000, 50000, 36000, 12000, -14000, -40000, -59000]
    y_piezo = [8000, -2900, -2900, -2900, -2800, -2700, -2670]
    z_piezo = [5000, -500, -500, -500, -500, -500, -500]
    x_hexa = [0, 10, 0, 0, 0, 0, -5]
    y_hexa = [6.5, 0, 0, 0, 0, 0, 0]

    incident_angles = [
        1.11119,
        -0.191966,
        0.598941,
        0.714874,
        0.404448,
        0.569336,
        0.545989,
    ]
    y_piezo_aligned = [
        7934.81,
        -3182.572,
        -3047.423,
        -2976.562,
        -2917.547,
        -2778.959,
        -2602.172,
    ]

    # incident_angles = [ 0.83422 ,  0.168648, -0.315438,  0.538535,  0.5593  ,  0.537955, 0.545215,  0.48137 ]
    # y_piezo_aligned = [ 7919.766,  8172.95 , -3172.044, -3065.634, -2925.553, -2917.084, -2781.573, -2627.836]

    # smi = SMI_Beamline()
    # yield from smi.modeAlignment(technique='gisaxs')

    # for name, xs_piezo, ys_piezo, zs_piezo, xs_hexa, ys_hexa in zip(names[1:], x_piezo[1:], y_piezo[1:], z_piezo[1:], x_hexa[1:], y_hexa[1:]):
    #     yield from bps.mv(piezo.x, xs_piezo)
    #     yield from bps.mv(piezo.y, ys_piezo)
    #     yield from bps.mv(stage.y, ys_hexa)
    #     yield from bps.mv(stage.x, xs_hexa)
    #     yield from bps.mv(piezo.z, zs_piezo)

    #     yield from alignement_gisaxs_multisample(angle = 0.1)

    #     incident_angles = incident_angles + [piezo.th.position]
    #     y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

    # yield from smi.modeMeasurement()

    # print(incident_angles)
    # print(y_piezo_aligned)

    # yield from bps.mv(att1_9, 'Insert')
    # yield from bps.sleep(1)
    # yield from bps.mv(att1_9, 'Insert')
    # yield from bps.sleep(1)

    # yield from bps.mv(stage.x, 0)
    # yield from bps.mv(stage.y, 0)


def run_Herzi_short_2020_3(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) bar at 14 keV — for each sample it
    #   goes to the stored aligned position/angle, takes exposures at a few WAXS-arc angles,
    #   then does a fine incidence-angle scan. (Uses the globals set by alignement_herzig_2020_3.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' with a ready grazing-incidence
    #   bar runner that loops samples, aligns each one, steps the incidence angle, and steps
    #   the WAXS arc — recording the angle/arc/beam into the data + file name for you (no
    #   hand-built "{sample}_14keV_..._wa{wax}"). Roughly:
    #
    #     from smi_plans import SampleList, giwaxs_bar       # do this once per session
    #     bar = SampleList.from_columns(names=names, piezo_x=x_piezo, piezo_y=y_piezo_aligned)
    #     yield from giwaxs_bar(bar, align=alignement_gisaxs, align_angle=0.11,
    #                           waxs_arc=tuple(np.linspace(0, 13, 3)), t=t,
    #                           incident_angles=np.linspace(0.05, 0.20, 16))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_range = np.linspace(0, 13, 3)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for name, xs, zs, aiss, ys, xs_hexa, ys_hexa in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa, y_hexa
    ):
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(stage.x, xs_hexa)

        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss)

        ai0 = piezo.th.position

        # yield from bps.mvr(piezo.th, angl)
        name_fmt = "{sample}_14keV_exppos1_{num}_ai{angle}deg_wa{wax}"
        if waxs.arc.position > 12:
            wa_ran = waxs_range[::-1]
        else:
            wa_ran = waxs_range

        for wa in wa_ran:
            yield from bps.mv(waxs, wa)
            sample_name = name_fmt.format(
                sample=name, num="%1.1d" % i, angle="%3.2f" % 0.11, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

        yield from bps.mv(piezo.th, ai0)
        yield from bps.mv(piezo.x, xs + 1000)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        angl = np.linspace(0.05, 0.20, 16)
        name_fmt = "{sample}_14keV_aiscan_ai{angle}deg_wa{wax}"

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for ang in angl:
                yield from bps.mv(piezo.th, ai0 + ang)
                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % ang, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_hxray_herzig(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience wrapper — runs the alignment setup, then the hard-X-ray
    #   grazing-incidence bar (run_Herzi_short_2020_3).
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the align-then-measure pairing is built into the
    #   bar runner, so a wrapper like this becomes a single call (see the note on
    #   run_Herzi_short_2020_3): yield from giwaxs_bar(bar, align=alignement_gisaxs, ...).
    #   (Nothing here is broken — the ⚠️ fixes live in the called function.)
    # === end smi_plans note ================================================
    alignement_herzig_2020_3()
    yield from run_Herzi_short_2020_3(t=t)


def run_Herzi_2020_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) bar at 14 keV — for each sample it
    #   aligns, takes exposures at a few WAXS-arc angles and x-positions, then does a fine
    #   incidence-angle scan.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a grazing-incidence bar runner that aligns each
    #   sample, steps the incidence angle, and steps the WAXS arc for you, recording the
    #   angle/arc/beam into the data + file name:
    #
    #     from smi_plans import SampleList, giwaxs_bar       # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["sample272", "sample307h", "sample319h"],
    #         piezo_x=[-1000, 27000, 47000],
    #     )
    #     yield from giwaxs_bar(bar, align=alignement_gisaxs, align_angle=0.11,
    #                           waxs_arc=tuple(np.linspace(0, 13, 3)), t=t,
    #                           incident_angles=np.linspace(0.05, 0.20, 16))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    # samples = ['sample251', 'sample269', 'sample272', 'sample307h', 'sample319h']
    # x_list  = [-47000, -23000, -1000, 27000, 47000]

    samples = ["sample272", "sample307h", "sample319h"]
    x_list = [-1000, 27000, 47000]

    waxs_range = np.linspace(0, 13, 3)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for x, name in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)

        yield from alignement_gisaxs(0.1)
        yield from bps.mv(att1_9, "Insert")
        yield from bps.sleep(1)
        yield from bps.mv(att1_9, "Insert")

        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + 0.11)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        yield from bps.mv(piezo.x, x + 500)

        # yield from bps.mvr(piezo.th, angl)
        name_fmt = "{sample}_14keV_exppos1_{num}_ai{angle}deg_wa{wax}"
        for i in range(0, 3, 1):
            if waxs.arc.position > 12:
                wa_ran = waxs_range[::-1]
            else:
                wa_ran = waxs_range

            for wa in wa_ran:
                yield from bps.mv(waxs, wa)
                sample_name = name_fmt.format(
                    sample=name, num="%1.1d" % i, angle="%3.2f" % 0.11, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=20)

        yield from bps.mv(piezo.th, ai0)

        yield from bps.mv(piezo.x, x + 1000)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        angl = np.linspace(0.05, 0.20, 16)
        name_fmt = "{sample}_14keV_aiscan_ai{angle}deg_wa{wax}"

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for ang in angl:
                yield from bps.mv(piezo.th, ai0 + ang)
                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % ang, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0 + 0.11)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        yield from bps.mv(piezo.x, x - 500)

        # yield from bps.mvr(piezo.th, angl)
        name_fmt = "{sample}_14keV_exppos2_{num}_ai{angle}deg_wa{wax}"
        for i in range(0, 3, 1):
            if waxs.arc.position > 12:
                wa_ran = waxs_range[::-1]
            else:
                wa_ran = waxs_range

            for wa in wa_ran:
                yield from bps.mv(waxs, wa)
                sample_name = name_fmt.format(
                    sample=name, num="%1.1d" % i, angle="%3.2f" % 0.11, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=20)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_Herzi_2020_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) bar — for each sample it aligns,
    #   takes exposures at several WAXS-arc angles and x-positions, then a fine incidence-angle
    #   scan.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a grazing-incidence bar runner that aligns each
    #   sample and steps the incidence angle + WAXS arc for you, recording the context into
    #   the data + file name:
    #
    #     from smi_plans import SampleList, giwaxs_bar       # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["HF20-181", "HF20-199", "HF20-218", "HF20-228"],
    #         piezo_x=[-45000, -19000, 8000, 33000],
    #     )
    #     yield from giwaxs_bar(bar, align=alignement_gisaxs, align_angle=0.18,
    #                           waxs_arc=tuple(np.linspace(0, 19.5, 4)), t=t,
    #                           incident_angles=np.linspace(0.05, 0.19, 15))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    # samples = ['Si1', 'P1', 'Y61', 'N41', 'PY61']
    # x_list  = [-46000, -22000, -1000, 23000,  46000]

    samples = ["HF20-181", "HF20-199", "HF20-218", "HF20-228"]
    x_list = [-45000, -19000, 8000, 33000]

    waxs_range = np.linspace(0, 19.5, 4)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for x, name in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)

        # yield from bps.mv(GV7.open_cmd, 1 )
        # yield from bps.sleep(1)
        # yield from bps.mv(GV7.open_cmd, 1 )

        yield from alignement_gisaxs(0.1)

        # yield from bps.mv(GV7.close_cmd, 1 )
        # yield from bps.sleep(1)
        # yield from bps.mv(GV7.close_cmd, 1 )

        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + 0.18)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        yield from bps.mv(piezo.x, x + 500)

        # yield from bps.mvr(piezo.th, angl)
        name_fmt = "{sample}_exppos1_{num}_ai{angle}deg_wa{wax}"
        for i in range(0, 3, 1):
            if waxs.arc.position > 16:
                wa_ran = waxs_range[::-1]
            else:
                wa_ran = waxs_range

            for wa in wa_ran:
                yield from bps.mv(waxs, wa)
                sample_name = name_fmt.format(
                    sample=name, num="%1.1d" % i, angle="%3.2f" % 0.18, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=20)

        yield from bps.mv(piezo.th, ai0)

        yield from bps.mv(piezo.x, x + 1000)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        angl = np.linspace(0.05, 0.19, 15)
        name_fmt = "{sample}_aiscan_ai{angle}deg_wa{wax}"

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for ang in angl:
                yield from bps.mv(piezo.th, ai0 + ang)
                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % ang, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0 + 0.18)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        yield from bps.mv(piezo.x, x - 500)

        # yield from bps.mvr(piezo.th, angl)
        name_fmt = "{sample}_exppos2_{num}_ai{angle}deg_wa{wax}"
        for i in range(0, 3, 1):
            if waxs.arc.position > 16:
                wa_ran = waxs_range[::-1]
            else:
                wa_ran = waxs_range

            for wa in wa_ran:
                yield from bps.mv(waxs, wa)
                sample_name = name_fmt.format(
                    sample=name, num="%1.1d" % i, angle="%3.2f" % 0.18, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=20)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def nexafs_herzig(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample, sweeps the X-ray energy across the sulfur edge at a
    #   grazing incidence angle and takes a WAXS image at each energy (a NEXAFS scan).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy scan like this in one line and records the energy + beam straight into the
    #   data and file name (no hand-built "{energy}eV_..._bpm{xbpm}"). It also drives the
    #   energy move robustly (device-managed feedback/gap/harmonic in one move), so the
    #   bps.sleep after each energy move is no longer needed. Per-sample, roughly:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     yield from nexafs_run(name, energies, t=t, dets=[pil900KW, xbpm2],
    #                           geometry="transmission", updown=False)
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' call must run as a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

    waxs_arc = [45.0]

    for name, xs, zs, aiss, ys in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned
    ):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss + 0.7)

        name_fmt = "nexafs_{sample}_{energy}eV_angle0.8deg_wa{wax}_bpm{xbpm}"

        for wa in waxs_arc:
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2490)
        yield from bps.mv(energy, 2470)
        yield from bps.mv(energy, 2450)


def nexafs_herzig_glass(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sweeps the X-ray energy across the sulfur edge on a glass reference and
    #   takes a WAXS image at each energy (a NEXAFS reference scan).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans', which does a full energy scan in
    #   one line and records the energy + beam straight into the data + file name. It also
    #   drives the energy move robustly, so the bps.sleep after each energy move is no longer
    #   needed. Same scan as below:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     energies = (np.arange(2445, 2470, 5).tolist() + np.arange(2470, 2480, 0.25).tolist()
    #                 + np.arange(2480, 2490, 1).tolist() + np.arange(2490, 2501, 5).tolist())
    #     yield from nexafs_run("nexafs_glass", energies, t=t, dets=[pil900KW, xbpm2],
    #                           geometry="transmission", updown=False)
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' call must run as a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = [45.0]

    # for name, xs, zs, aiss, ys in zip(names, x_piezo, z_piezo, incident_angles, y_piezo_aligned):
    #     yield from bps.mv(piezo.x, xs)
    #     yield from bps.mv(piezo.y, ys)
    #     yield from bps.mv(piezo.z, zs)
    #     yield from bps.mv(piezo.th, aiss + 0.7)

    name_fmt = "nexafs_glass_{energy}eV_angle0.8deg_wa{wax}_bpm{xbpm}"

    for wa in waxs_arc:
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

            bpm = xbpm2.sumX.value

            sample_name = name_fmt.format(
                energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2490)
    yield from bps.mv(energy, 2470)
    yield from bps.mv(energy, 2450)


# [7054.818, 6891.486, 6639.453, 6471.627, 6262.9400000000005]
# [0.847336, 0.782651, 0.765316, 0.9306709999999999, 0.8608429999999999]


def run_sedge_herzig(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience wrapper — runs the grazing alignment, then the sulfur-edge
    #   energy measurements (S_edge_measurments_Herzig).
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the align-then-measure pairing is built into the
    #   grazing-incidence + energy bar runners, so this wrapper becomes one call. See the notes
    #   on alignement_herzig and S_edge_measurments_Herzig. (Nothing here is broken — the ⚠️
    #   fixes live in the called functions.)
    # === end smi_plans note ================================================
    yield from alignement_herzig()
    yield from S_edge_measurments_Herzig(t=t)


def alignement_herzig():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks the bar, runs the grazing-incidence alignment routine on each
    #   sample, and stores the found incidence angles + aligned y-positions into module
    #   globals (it also flips the beamline into/out of "alignment mode" and parks an
    #   attenuator). It's alignment setup, not a measurement.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' alignment isn't stashed in loose globals and the
    #   old SMI_Beamline().modeAlignment()/modeMeasurement() bracketing isn't needed — the bar
    #   runner aligns each sample as it goes and records the result WITH the data. You describe
    #   the bar once as a SampleList and let giwaxs_bar(...) align it:
    #
    #     from smi_plans import SampleList
    #     bar = SampleList.from_columns(names=names, piezo_x=x_piezo, piezo_y=y_piezo)
    #     # then: yield from giwaxs_bar(bar, align=alignement_gisaxs_multisample, ...)
    #
    #   (Nothing here is broken — att2_9 still works. This is a tidier pattern to adopt later.)
    # === end smi_plans note ================================================
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa, y_hexa
    # names = ['s332v', 's329v', 's324v', 's340v', 'glass']
    # names = ['s325h', 's325v', 's324h', 's338v', 's335v']
    # names = ['s315h', 's313h', 's307h', 's339h', 's339v', 's338h']
    # names = ['s318v', 's318h', 's319v', 's306v', 's306h', 's307v', 's319h', 's317h']

    names = ["s334h", "s328h", "s340h", "s335h", "s332h", "s329h", "s272", "s270"]

    x_piezo = [18000, -25000, 50000, 43000, 18000, -9000, -32000, -56000]
    y_piezo = [8000, 8000, -2670, -2670, -2670, -2670, -2670, -2670]
    z_piezo = [-1100, -1100, -1100, -1100, -1100, -1100, -1100, -1100]
    x_hexa = [0, 0, 20, 0, 0, 0, 0, 0]
    y_hexa = [6.5, 6.5, 0, 0, 0, 0, 0, 0]

    incident_angles = []
    y_piezo_aligned = []

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, xs_piezo, ys_piezo, zs_piezo, xs_hexa, ys_hexa in zip(
        names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa
    ):
        yield from bps.mv(piezo.x, xs_piezo)
        yield from bps.mv(piezo.y, ys_piezo)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs_piezo)

        yield from alignement_gisaxs_multisample(angle=0.45)

        incident_angles = incident_angles + [piezo.th.position]
        y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

    yield from smi.modeMeasurement()

    print(incident_angles)
    print(y_piezo_aligned)

    yield from bps.mv(att2_9, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(att2_9, "Insert")
    yield from bps.sleep(1)

    yield from bps.mv(stage.x, 0)
    yield from bps.mv(stage.y, 0)


def S_edge_measurments_Herzig(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each grazing-incidence sample it first does a quick x-scan to check
    #   uniformity, then sweeps the X-ray energy across the sulfur edge at two incidence angles
    #   and several WAXS-arc angles, moving the sample in x as it goes.
    #
    # 💡 NEWER, EASIER WAY: this combines grazing-incidence + an energy sweep — both of which
    #   'smi_plans' has dedicated, composable pieces for (it records the energy/angle/arc/beam
    #   into the data + file name, and drives the energy move robustly so the per-energy
    #   bps.sleep is no longer needed). A single-sample energy scan at a fixed angle looks like:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     yield from nexafs_run(name, energies, t=t, dets=[pil2M, pil900KW, xbpm2],
    #                           geometry="grazing", updown=False)
    #     # for the full grazing bar across angles, compose with smi_plans.giwaxs_run / energy_axis.
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    waxs_arc = np.linspace(0, 19.5, 4)
    ai_list = [0.5, 0.8]

    for name, xs, zs, aiss, ys, xs_hexa, ys_hexa in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa, y_hexa
    ):
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(stage.x, xs_hexa)

        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss)

        ai0 = piezo.th.position

        # pre position measurement to check sample inhomogeneity
        yield from bps.mv(waxs, 0)
        yield from bps.mv(energy, 2450)
        yield from bps.mv(piezo.th, ai0 + 0.8)

        dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        det_exposure_time(0.2, 0.2)  # ⚠️ FIXME(smi_plans): same as above — this "set 0.2 s" only takes effect if run as a plan:  yield from det_exposure_time(0.2, 0.2)  (or  RE(det_exposure_time(0.2, 0.2))).

        xss = np.linspace(xs, xs + 1 * 4500, 26)
        xss1 = np.linspace(xs + 1 * 4500, xs + 2 * 4500, 26)
        xssss = np.concatenate([xss, xss1])
        name_fmt = "{sample}_xscan_{energy}eV_ai{ai}_pos{pos}"
        for i, xxx in enumerate(np.round(xssss, 2)):
            yield from bps.mv(piezo.x, xxx)
            bpm = xbpm2.sumX.value
            sample_name = name_fmt.format(
                sample=name, energy="%6.2f" % 2450.0, ai="%3.2f" % 0.8, pos="%2.2d" % i
            )
            sample_id(user_name="LR", sample_name=sample_name)
            yield from bp.count(dets, num=1)

        energies = [
            2450.0,
            2460.0,
            2470.0,
            2472.0,
            2474.0,
            2474.5,
            2475.0,
            2475.5,
            2476.0,
            2476.5,
            2477.0,
            2477.5,
            2478.0,
            2478.5,
            2479.0,
            2479.5,
            2480.0,
            2481.0,
            2482.0,
            2483.0,
            2484.0,
            2485.0,
            2486.0,
            2487.0,
            2490.0,
            2500.0,
        ]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                yield from bps.mv(piezo.x, xs + k * 4500)

                name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"

                xss = np.linspace(xs + k * 4500, xs + (1 + k) * 4500, 27)
                for e, x_ss in zip(energies, xss):
                    yield from bps.mv(piezo.x, x_ss)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(0.7)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    bpm = xbpm2.sumX.value
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%6.2f" % e,
                        ai="%3.2f" % ais,
                        wax=wa,
                        xbpm="%4.3f" % bpm,
                    )
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2490)
                yield from bps.mv(energy, 2470)
                yield from bps.mv(energy, 2450)

    yield from bps.mv(stage.x, 0)
    yield from bps.mv(stage.y, 0)


def run_Herzi_Sedge_2021_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sulfur-edge grazing-incidence bar — for each sample it aligns, does a
    #   uniformity x-scan at two incidence angles, then sweeps the X-ray energy across the
    #   S edge at several WAXS-arc angles while stepping the sample in x.
    #
    # 💡 NEWER, EASIER WAY: this is grazing-incidence + an energy sweep, which 'smi_plans'
    #   builds from composable pieces and records (energy/angle/arc/beam into the data + file
    #   name; robust energy moves so the per-energy bps.sleep + the "gentle walk-back" sleeps
    #   at the end aren't needed). A single-sample S-edge scan at a fixed angle:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     yield from nexafs_run(name, energies, t=t, dets=[pil2M, pil900KW, xbpm2],
    #                           geometry="grazing", updown=False)
    #     # for the full grazing bar, compose with smi_plans.giwaxs_run / energy_axis.
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    # samples = ['glass', '063an', '044an', '061an',  '043', '060', '008an', '030an',  '007',  '028']
    # x_piezo = [  49000,   24000,   -1000,  -28000, -55000, 49000,   24000,   -2000, -28000, -56000]
    # x_hexa =  [      0,       0,       0,       0,     -3,     0,       0,       0,      0,     -3]
    # y_piezo = [   4500,    4500,    4500,    4500,   4500, -4400,   -4400,   -4400,  -4400,  -4400]

    # samples = ['056an',   '055', '020an',   '019', '050an', '049', '024an',  '023', '063ac', '044ac']
    # x_piezo = [  49000,   26000,       0,  -32000,  -55000, 49000,   23000,      0,  -32000,  -55000]
    # x_hexa =  [      5,       0,       0,       0,       0,     4,       0,      0,       0,      0]
    # y_piezo = [   4500,    4500,    4500,    4500,    4500, -4400,   -4400,  -4400,   -4400,  -4400]

    # samples = ['061ac',  '008ac', '030ac','063oa', '044oa','061oa', '008oa','030oa', '047an',  '045']
    # x_piezo = [  48000,   28000,    1000,  -24000,  -52000, 48000,   28000,   1000,  -24000,  -52000]
    # x_hexa =  [      5,       0,       0,       0,       0,     5,       0,      0,       0,      0]
    # y_piezo = [   4500,    4500,    4500,    4500,    4500, -4400,   -4400,  -4400,   -4400,  -4400]

    # samples = ['017an',   '014',  '059an',  '058', '026an', '025', '053an',  '052', '056ac',  '056oa']
    # x_piezo = [  49000,   24000,   -1500,  -27000,  -54000, 48000,   24000,  -1500,  -27000,  -54000]
    # x_hexa =  [      3,       0,       0,       0,       0,     3,       0,      0,       0,      0]
    # y_piezo = [   4500,    4500,    4500,    4500,    4500, -4400,   -4400,  -4400,   -4400,  -4400]

    samples = [
        "020ac",
        "020oa",
        "050ac",
        "050oa",
        "024ac",
        "024oa",
        "010an",
        "009",
        "048an",
        "057an",
    ]
    x_piezo = [49000, 27000, 0, -27000, -54000, 49000, 27000, 0, -27000, -54000]
    x_hexa = [5, 0, 0, 0, 0, 5, 0, 0, 0, 0]
    y_piezo = [4500, 4500, 4500, 4500, 4500, -4400, -4400, -4400, -4400, -4400]

    assert len(x_piezo) == len(
        samples
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(samples)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        x_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = np.linspace(0, 19.5, 4)
    ai_list = [0.5, 0.8]

    for w, (xs, y, x_hexa, name) in enumerate(zip(x_piezo, y_piezo, x_hexa, samples)):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(stage.x, x_hexa)

        yield from alignement_gisaxs(0.45)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)

        ai0 = piezo.th.position

        # pre position measurement to check sample inhomogeneity
        yield from bps.mv(waxs, 0)
        yield from bps.mv(energy, 2450)

        dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        det_exposure_time(0.2, 0.2)  # ⚠️ FIXME(smi_plans): same as above — this "set 0.2 s" only takes effect if run as a plan:  yield from det_exposure_time(0.2, 0.2)  (or  RE(det_exposure_time(0.2, 0.2))).
        name_fmt = "{sample}_xscan_{energy}eV_ai{ai}_pos{pos}"

        xss = np.linspace(xs, xs + 1 * 4500, 26)
        yield from bps.mv(piezo.th, ai0 + 0.5)

        for i, xxx in enumerate(np.round(xss, 2)):
            yield from bps.mv(piezo.x, xxx)
            bpm = xbpm2.sumX.value
            sample_name = name_fmt.format(
                sample=name, energy="%6.2f" % 2450.0, ai="%3.2f" % 0.5, pos="%2.2d" % i
            )
            sample_id(user_name="LR", sample_name=sample_name)
            yield from bp.count(dets, num=1)

        xss1 = np.linspace(xs + 1 * 4500, xs + 2 * 4500, 26)
        yield from bps.mv(piezo.th, ai0 + 0.8)

        for i, xxx in enumerate(np.round(xss1, 2)):
            yield from bps.mv(piezo.x, xxx)
            bpm = xbpm2.sumX.value
            sample_name = name_fmt.format(
                sample=name, energy="%6.2f" % 2450.0, ai="%3.2f" % 0.8, pos="%2.2d" % i
            )
            sample_id(user_name="LR", sample_name=sample_name)
            yield from bp.count(dets, num=1)

        energies = [
            2450.0,
            2460.0,
            2470.0,
            2472.0,
            2474.0,
            2474.5,
            2475.0,
            2475.5,
            2476.0,
            2476.5,
            2477.0,
            2477.5,
            2478.0,
            2478.5,
            2479.0,
            2479.5,
            2480.0,
            2481.0,
            2482.0,
            2483.0,
            2484.0,
            2485.0,
            2486.0,
            2487.0,
            2490.0,
            2500.0,
        ]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                yield from bps.mv(piezo.x, xs + k * 4500)

                name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"

                xss = np.linspace(xs + k * 4500, xs + (1 + k) * 4500, 27)
                for e, x_ss in zip(energies, xss):
                    yield from bps.mv(energy, e)
                    # yield from bps.sleep(0.4)
                    yield from bps.mv(piezo.x, x_ss)

                    bpm = xbpm2.sumX.value
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%6.2f" % e,
                        ai="%3.2f" % ais,
                        wax=wa,
                        xbpm="%4.3f" % bpm,
                    )
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2490)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop these walk-back sleeps — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 2470)
                yield from bps.sleep(1)  # 💡 smi_plans: same as above — this settle wait is handled for you by move_energy_fb/energy_axis once you switch over.
                yield from bps.mv(energy, 2450)

        yield from bps.mv(piezo.th, ai0)

    yield from bps.mv(stage.x, 0)


def run_Herzi_2021_1(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS/GIWAXS) bar at 14 keV — for each sample it
    #   aligns, takes exposures at a few WAXS-arc angles and x-positions, then a fine
    #   incidence-angle scan.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a grazing-incidence bar runner that aligns each
    #   sample and steps the incidence angle + WAXS arc for you, recording the context into
    #   the data + file name:
    #
    #     from smi_plans import SampleList, giwaxs_bar       # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["056an", "055", "020an", "019", "050an", "049", "024an", "023"],
    #         piezo_x=[55000, 34000, 6000, -24000, -50000, 6000, -24000, -50000],
    #         piezo_y=[4500, 4500, 4500, 4500, 4500, -4400, -4400, -4400],
    #     )
    #     yield from giwaxs_bar(bar, align=alignement_gisaxs, align_angle=0.14,
    #                           waxs_arc=tuple(np.linspace(0, 13, 3)), t=t,
    #                           incident_angles=np.linspace(0.05, 0.20, 16))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    # samples = ['glass', '063an', '044an', '061an',  '043', '060', '008an', '030an',  '007',  '028']
    # x_piezo = [  55000,   37000,   10000,  -17000, -47000, 55000,   38000,   13000, -15000, -43000]
    # x_hexa =  [      7,       0,       0,       0,      0,     7,       0,       0,      0,      0]
    # y_piezo = [   4500,    4500,    4500,    4500,   4500, -4400,   -4400,   -4400,  -4400,  -4400]

    samples = ["056an", "055", "020an", "019", "050an", "049", "024an", "023"]
    x_piezo = [55000, 34000, 6000, -24000, -50000, 6000, -24000, -50000]
    x_hexa = [7, 0, 0, 0, 0, 7, 0, 0]
    y_piezo = [4500, 4500, 4500, 4500, 4500, -4400, -4400, -4400]

    assert len(x_piezo) == len(
        samples
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(samples)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        x_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_range = np.linspace(0, 13, 3)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for x, y, x_hexa, name in zip(x_piezo, y_piezo, x_hexa, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(stage.x, x_hexa)

        yield from alignement_gisaxs(0.1)

        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + 0.14)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

        if waxs.arc.position > 12:
            wa_ran = waxs_range[::-1]
        else:
            wa_ran = waxs_range

        name_fmt = "{sample}_14keV_exp_{pos}_ai{angle}deg_wa{wax}"

        for wa in wa_ran:
            yield from bps.mv(waxs, wa)

            yield from bps.mv(piezo.x, x + 500)
            sample_name = name_fmt.format(
                sample=name, pos="pos1", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 500)
            sample_name = name_fmt.format(
                sample=name, pos="pos2", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 1000)
            sample_name = name_fmt.format(
                sample=name, pos="pos3", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

        yield from bps.mv(piezo.th, ai0)
        yield from bps.mv(piezo.x, x)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        angl = np.linspace(0.05, 0.20, 16)
        name_fmt = "{sample}_14keV_aiscan_ai{angle}deg_wa{wax}"

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for ang in angl:
                yield from bps.mv(piezo.th, ai0 + ang)
                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % ang, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_test_Herzi_2021_1(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a test grazing-incidence (GISAXS/GIWAXS) bar at 14 keV — aligns each
    #   monitor sample, takes exposures at several x-positions and WAXS-arc angles, plus a fine
    #   incidence-angle scan (and repeats at a second incidence angle).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a grazing-incidence bar runner that aligns each
    #   sample and steps the incidence angle + WAXS arc for you, recording the context into
    #   the data + file name:
    #
    #     from smi_plans import SampleList, giwaxs_bar       # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["mono1", "mono2", "mono3", "mono4"],
    #         piezo_x=[55000, 50500, 38500, 27500],
    #         piezo_y=[-4400, -4400, -4400, -4400],
    #     )
    #     yield from giwaxs_bar(bar, align=alignement_gisaxs, align_angle=0.14,
    #                           waxs_arc=tuple(np.linspace(0, 13, 3)), t=t,
    #                           incident_angles=np.linspace(0.05, 0.20, 16))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    # samples = ['glass', '063an', '044an', '061an',  '043', '060', '008an', '030an',  '007',  '028']
    # x_piezo = [  55000,   37000,   10000,  -17000, -47000, 55000,   38000,   13000, -15000, -43000]
    # x_hexa =  [      7,       0,       0,       0,      0,     7,       0,       0,      0,      0]
    # y_piezo = [   4500,    4500,    4500,    4500,   4500, -4400,   -4400,   -4400,  -4400,  -4400]

    samples = ["mono1", "mono2", "mono3", "mono4"]
    x_piezo = [55000, 50500, 38500, 27500]
    x_hexa = [7.5, 0, 0, 0]
    y_piezo = [-4400, -4400, -4400, -4400]

    assert len(x_piezo) == len(
        samples
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(samples)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        x_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_range = np.linspace(0, 13, 3)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    for x, y, x_hexa, name in zip(x_piezo, y_piezo, x_hexa, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(stage.x, x_hexa)

        yield from alignement_gisaxs(0.1)

        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + 0.14)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

        if waxs.arc.position > 12:
            wa_ran = waxs_range[::-1]
        else:
            wa_ran = waxs_range

        name_fmt = "{sample}_14keV_exp_{pos}_ai{angle}deg_wa{wax}"

        for wa in wa_ran:
            yield from bps.mv(waxs, wa)

            yield from bps.mv(piezo.x, x + 1500)
            sample_name = name_fmt.format(
                sample=name, pos="pos1", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x + 1250)
            sample_name = name_fmt.format(
                sample=name, pos="pos2", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x + 1000)
            sample_name = name_fmt.format(
                sample=name, pos="pos3", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x + 750)
            sample_name = name_fmt.format(
                sample=name, pos="pos4", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x + 500)
            sample_name = name_fmt.format(
                sample=name, pos="pos5", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x + 250)
            sample_name = name_fmt.format(
                sample=name, pos="pos6", angle="%3.2f" % 0.14, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

        yield from bps.mv(piezo.th, ai0)
        yield from bps.mv(piezo.x, x)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
        angl = np.linspace(0.05, 0.20, 16)
        name_fmt = "{sample}_14keV_aiscan_ai{angle}deg_wa{wax}"

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for ang in angl:
                yield from bps.mv(piezo.th, ai0 + ang)
                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % ang, wax="%2.1f" % wa
                )
                sample_id(user_name="EH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        sample_id(user_name="test", sample_name="test")
        det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).

        yield from bps.mv(piezo.th, ai0 + 0.30)

        if waxs.arc.position > 12:
            wa_ran = waxs_range[::-1]
        else:
            wa_ran = waxs_range

        name_fmt = "{sample}_14keV_exp_{pos}_ai{angle}deg_wa{wax}"

        for wa in wa_ran:
            yield from bps.mv(waxs, wa)

            yield from bps.mv(piezo.x, x - 250)
            sample_name = name_fmt.format(
                sample=name, pos="pos1", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 500)
            sample_name = name_fmt.format(
                sample=name, pos="pos2", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 750)
            sample_name = name_fmt.format(
                sample=name, pos="pos3", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 1000)
            sample_name = name_fmt.format(
                sample=name, pos="pos4", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 1250)
            sample_name = name_fmt.format(
                sample=name, pos="pos5", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)

            yield from bps.mv(piezo.x, x - 1500)
            sample_name = name_fmt.format(
                sample=name, pos="pos6", angle="%3.2f" % 0.30, wax="%2.1f" % wa
            )
            sample_id(user_name="EH", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=20)


def nigh_test():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight wrapper — runs the test bar then the real 2021_1 bar.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you'd queue these as two giwaxs_bar(...) runs (see
    #   the notes on run_test_Herzi_2021_1 / run_Herzi_2021_1). Nothing here is broken — the
    #   ⚠️ fixes live in the called functions.
    # === end smi_plans note ================================================
    yield from run_test_Herzi_2021_1(t=0.5)
    yield from run_Herzi_2021_1(t=0.5)

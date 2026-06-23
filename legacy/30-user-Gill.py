def gill_giwaxs(exp_time=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS (GIWAXS) measurement — it moves to a sample
    #   spot, aligns the surface, then for each WAXS detector-arc angle and each incident
    #   angle it takes a WAXS image. (GIWAXS = the beam skims the surface at a shallow angle.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   GIWAXS scan like this for you and writes the angle / arc / beam intensity straight INTO
    #   the saved data and the file name, so you don't have to hand-build "{sample}_..._wa{wa}".
    #   'align_sample' does the alignment and saves where it landed. For example:
    #
    #     from smi_plans import giwaxs_run, align_sample   # do this once at the top of a session
    #     yield from giwaxs_run(
    #         "CEll_RT_overnight",                          # rest of the file name added for you
    #         incident_angles=[0.12, 0.22, 0.30, 0.4],      # your angles, unchanged
    #         arc=[0, 20, 40],                              # your WAXS arc positions, unchanged
    #         t=exp_time,                                   # your exposure time, unchanged
    #         align=align_sample,                           # align first and record where it landed
    #     )
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the
    #   ⚠️ notes on those lines). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil900KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil900KW' here is fine.)
    name = "CEll_RT_overnight"
    # initial_angle_zero = -0.72
    inc_angle = [0.12, 0.22, 0.30, 0.4]
    waxs_arc = [0, 20, 40]
    # yield from bps.mv(stage.th, initial_angle_zero)
    x = [-3.1]
    for i, xsss in enumerate(x):
        yield from bps.mv(stage.x, xsss)
        # yield from bps.mv(prs, ph)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_gisaxs_hex(angle=0.2)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)

        ai_0 = stage.th.position
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            for incident_angle in inc_angle:
                name_fmt = "{sample}_pos{pos}_{angle}deg_wa{wa}"
                yield from bps.mv(stage.th, ai_0 + incident_angle)
                sample_name = name_fmt.format(
                    sample=name,
                    pos="%1.1d" % i,
                    angle="%1.2f" % incident_angle,
                    wa="%2.1f" % wa,
                )
                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name="SG", sample_name=sample_name)
                det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' giwaxs_run sets exposure for you via t=.)
                yield from bp.count(dets, num=1)

        yield from bps.mv(stage.th, ai_0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def gill_giwaxs_bkg(exp_time=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes GIWAXS "background" images — for each WAXS arc position it steps
    #   through a row of nearby y spots and takes a WAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you describe the y positions and arc angles as
    #   "axes" (lists of values to step through) and hand them to one call, which records the
    #   y position / arc / beam into every image and the file name automatically:
    #
    #     from smi_plans import giwaxs_run                 # do this once at the top of a session
    #     yield from giwaxs_run(
    #         "CEll_RT_bkg",                               # rest of the file name added for you
    #         arc=[0, 20, 40],                             # your WAXS arc positions, unchanged
    #         t=exp_time,                                  # your exposure time, unchanged
    #         # ...add a y-position axis with motor_axis("y", stage.y, [-3, -3.02, ...])
    #     )
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ note below.)
    #
    #   (Your script below still works as-is, EXCEPT for the lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls below need to be run as a plan. (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil900KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil900KW' here is fine.)
    name = "CEll_RT_bkg"
    # initial_angle_zero = -0.72
    waxs_arc = [0, 20, 40]
    # yield from bps.mv(stage.th, initial_angle_zero)
    y = [-3, -3.02, -3.04, -3.06, -3.08, -3.10, -3.12, -3.14]
    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        for i, ys in enumerate(y):
            yield from bps.mv(stage.y, ys)
            name_fmt = "{sample}_pos{pos}_wa{wa}"
            sample_name = name_fmt.format(sample=name, pos="%1.1d" % i, wa="%2.1f" % wa)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name="SG", sample_name=sample_name)
            det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' giwaxs_run sets exposure for you via t=.)
            yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).

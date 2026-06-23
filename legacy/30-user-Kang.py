def rotation_saxs(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each of 3 samples, takes SAXS+WAXS images while rotating the
    #   sample (the 'prs' rotation stage) from -90 to +90 deg at a few WAXS-arc angles.
    #
    # 💡 NEWER, EASIER WAY: rotating a sample through phi while collecting is the
    #   'smi_plans' rocking/CD-SAXS pattern. You hand it the rotation axis and arc axis
    #   as "axes" and one acquire call records the angle, WAXS position, and beam
    #   intensity straight into each saved image (no hand-built file name needed):
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(
    #         "AGIB3N_1top", [pil2M, pil900KW],         # SAXS + WAXS (see ⚠️ on pil300KW)
    #         [motor_axis("waxs", waxs, np.arange(0, 26, 6.5)),    # your WAXS-arc steps
    #          motor_axis("phi", stage.phi, np.linspace(-90, 90, 91))])  # your rotation (see ⚠️ on 'prs')
    #
    #   (This is just a tidier option to try later — your script below still works
    #    as-is, EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was renamed to 'stage.phi'
    #   (the old name would error) — see the ⚠️ note on the grid_scan line; (2) 'pil300KW'
    #   (WAXS) was retired — it's now 'pil900KW'; (3) the 'det_exposure_time(...)' calls
    #   no longer set the exposure unless run as a plan (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================

    # sample = ['Hopper2_AGIB_AuPd_top', 'Hopper2_AGIB_AuPd_mid', 'Hopper2_AGIB_AuPd_bot'] #Change filename
    sample = ["AGIB3N_1top", "AGIB3N_1mid", "AGIB3N_1cen"]  # Change filename
    # y_list  = [-6.06, -6.04, -6.02] #hexapod is in mm
    # y_list  = [-10320, -10300, -10280]  #SmarAct is um
    y_list = [4760, 4810, 4860]  # , 5210]  #SmarAct is um

    assert len(y_list) == len(
        sample
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    # dets = [pil2M, rayonix, pil300KW]
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    prs_range = [-90, 90, 91]
    waxs_range = [0, 26, 5]  # step of 6.5 degrees
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    # pil_pos_x = [-0.4997, -0.4997 + 4.3, -0.4997 + 4.3, -0.4997]
    # pil_pos_y = [-59.9987, -59.9987, -59.9987 + 4.3, -59.9987]

    # waxs_po = np.linspace(20.95, 2.95, 4)

    for sam, y in zip(sample, y_list):
        # yield from bps.mv(stage.y, y) #hexapod
        yield from bps.mv(piezo.y, y)  # SmarAct
        name_fmt = "{sam}"
        sample_name = name_fmt.format(sam=sam)
        sample_id(user_name="MK", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.grid_scan(dets, prs, *prs_range, waxs, *waxs_range, 1)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'. (Note: 'prs_range' here is just a variable name, not the device, so leave it as-is.)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def rotation_saxs_fast(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same idea as rotation_saxs but stepped by hand — for each of 3
    #   samples it loops over WAXS-arc angles, and within each it rotates the 'prs'
    #   stage from -90 to +90 deg one step at a time, taking SAXS+WAXS at each.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you don't write the nested loops yourself —
    #   you describe the rotation and arc as "axes" and one acquire call sweeps them,
    #   recording the angle / WAXS position / beam intensity into each saved image:
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(
    #         "AGIB3DR_2fast_top", [pil2M, pil900KW],   # SAXS + WAXS (see ⚠️ on pil300KW)
    #         [motor_axis("waxs", waxs, np.linspace(0, 26, 5)),    # your WAXS-arc steps
    #          motor_axis("phi", stage.phi, np.linspace(-90, 90, 91))])  # your rotation (see ⚠️ on 'prs')
    #
    #   (This is just a tidier option to try later — your script below still works
    #    as-is, EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was renamed to 'stage.phi'
    #   (the old name would error) — see the ⚠️ note below; (2) 'pil300KW' (WAXS) was
    #   retired — it's now 'pil900KW'; (3) the 'det_exposure_time(...)' calls no longer
    #   set the exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    sample = [
        "AGIB3DR_2fast_top",
        "AGIB3DR_2fast_mid",
        "AGIB3DR_2fast_cen",
    ]  # Change filename
    y_list = [5150, 5230, 5310]  # SmarAct is um

    assert len(y_list) == len(
        sample
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    prs_range = np.linspace(-90, 90, 91)
    waxs_range = np.linspace(0, 26, 5)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)
    for sam, y in zip(sample, y_list):
        yield from bps.mv(piezo.y, y)
        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            for pr in prs_range:
                yield from bps.mv(prs, pr)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'. ('pr' and 'prs_range' here are just loop variables, leave them as-is.)
                name_fmt = "{sam}_wa{waxs}deg_{prs}deg"
                sample_name = name_fmt.format(
                    sam=sam, waxs="%2.1f" % wa, prs="%3.3d" % pr
                )
                sample_id(user_name="MK", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def rotation_saxs_att(t=1):  # attenuated WAXS, so SAXS recorded separately first

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a two-pass version — first it records SAXS only while rotating the
    #   'prs' stage through -90..+90 deg per sample; then it inserts attenuators and
    #   records WAXS (at a few WAXS-arc/detector positions) over the same rotation.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' lets you describe the rotation as an axis and run
    #   each detector pass with one acquire call; it records the angle / WAXS position /
    #   beam intensity into each image, and you set attenuators with normal moves between
    #   the two passes:
    #
    #     from smi_plans import acquire, motor_axis
    #     # pass 1 (SAXS):
    #     yield from acquire("Hopper1_AGIB_AuPd_top_saxs", [pil2M],
    #                        [motor_axis("phi", stage.phi, np.arange(-90, 91, 1))])  # see ⚠️ on 'prs'
    #     # ...insert attenuators with bps.mv(att1_5, "Insert") etc...
    #     # pass 2 (WAXS at each waxs position):
    #     yield from acquire("Hopper1_AGIB_AuPd_top_waxs", [pil900KW],   # see ⚠️ on pil300KW
    #                        [motor_axis("waxs", waxs, np.linspace(20.95, 2.95, 4)),
    #                         motor_axis("phi", stage.phi, np.arange(-90, 91, 1))])
    #
    #   (This is just a tidier option to try later — your script below still works
    #    as-is, EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was renamed to 'stage.phi'
    #   (the old name would error) — ⚠️ notes below; (2) 'pil300KW' (WAXS) was retired —
    #   it's now 'pil900KW'; (3) the 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    #   (The attenuators att1_5/att1_6 and pil2M_pos.x/.y are fine — no change needed.)
    # === end smi_plans note ================================================

    # sample = ['Disc3_AuPd_top-3', 'Disc3_AuPd_mid-3', 'Disc3_AuPd_bot-3'] #Change filename
    sample = [
        "Hopper1_AGIB_AuPd_top",
        "Hopper1_AGIB_AuPd_mid",
        "Hopper1_AGIB_AuPd_bot",
    ]  # Change filename
    # y_list  = [-6.06, -6.04, -6.02] #hexapod is in mm
    # y_list  = [-10320, -10300, -10280]  #SmarAct is um
    y_list = [-9540, -9520, -9500]  # SmarAct is um

    assert len(y_list) == len(
        sample
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    # dets = [pil2M, rayonix, pil300KW]
    dets0 = [pil2M]
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    pil_pos_x = [-0.4997, -0.4997 + 4.3, -0.4997 + 4.3, -0.4997]
    pil_pos_y = [-59.9987, -59.9987, -59.9987 + 4.3, -59.9987]

    waxs_po = np.linspace(20.95, 2.95, 4)

    for sam, y in zip(sample, y_list):
        # yield from bps.mv(stage.y, y) #hexapod
        yield from bps.mv(piezo.y, y)  # SmarAct
        yield from bps.mv(waxs, 70)
        for angle in range(-90, 91, 1):
            yield from bps.mv(prs, angle)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sam}_phi{angle}deg"
            sample_name = name_fmt.format(sam=sam, angle=angle)
            sample_id(user_name="MK", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets0, num=1)

    yield from bps.mv(att1_5, "Insert")
    yield from bps.sleep(1)
    yield from bps.mv(att1_6, "Insert")
    yield from bps.sleep(1)
    for sam, y in zip(sample, y_list):
        # yield from bps.mv(stage.y, y) #hexapod
        yield from bps.mv(piezo.y, y)  # SmarAct
        for i, waxs_pos in enumerate(waxs_po):
            yield from bps.mv(waxs, waxs_pos)
            yield from bps.mv(pil2M_pos.x, pil_pos_x[i])
            yield from bps.mv(pil2M_pos.y, pil_pos_y[i])

            for angle in range(-90, 91, 1):
                yield from bps.mv(prs, angle)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

                name_fmt = "{sam}_phi{angle}deg_{waxs_pos}deg"
                sample_name = name_fmt.format(sam=sam, angle=angle, waxs_pos=waxs_pos)
                sample_id(user_name="MK", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).

    yield from bps.mv(att1_5, "Retract")
    yield from bps.sleep(1)
    yield from bps.mv(att1_6, "Retract")
    yield from bps.sleep(1)

    yield from bps.mv(pil2M_pos.x, -0.4997)
    yield from bps.mv(pil2M_pos.y, -59.9987)

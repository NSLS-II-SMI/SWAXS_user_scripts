def run_waxs_IC(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS scan near the tin (Sn) edge — for each sample it sets
    #   a rotation (0 or 45 deg), then sweeps energy and the WAXS arc, taking images, with
    #   manual energy walk-backs after the edge.
    #
    # 💡 NEWER, EASIER WAY: sweeping energy while collecting WAXS is the 'smi_plans' GIWAXS +
    #   energy combination. energy_axis steps the energy (handling the move + beam feedback)
    #   and records it into each image, and a WAXS-arc motor_axis sweeps the arc:
    #     from smi_plans import giwaxs_bar, SampleList, energy_axis, motor_axis
    #     bar = SampleList.from_columns(name=names, x=x)
    #     yield from giwaxs_bar(
    #         bar, t=t, dets=[pil2M, pil900KW],         # WAXS detector (see ⚠️ on pil300KW)
    #         axes=[energy_axis([2405, 2465, 2471, 2473, 2475, 2477, 2479, 2481]),
    #               motor_axis("waxs", waxs, np.arange(0, 19.5, 4))])
    #
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 energy
    #    walk-backs become unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ notes below); (2) the rotation stage 'prs' was renamed to 'stage.phi'
    #   (⚠️ notes below); (3) the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    names = [
        "2um_725_7m",
        "2um_725_45d_7m",
        "5um_825_7m",
        "5um_825_45d_7m",
        "10um_825_7m",
        "10um_825_45d_7m",
        "AgBh",
    ]
    x = [34000, 36000, 19500, 13500, 4500, -3000, -25000]

    energies = [2405, 2465, 2471, 2473, 2475, 2477, 2479, 2481]

    waxs_arc = [0, 19.5, 4]

    for xs, name in zip(x, names):
        yield from bps.mv(piezo.x, xs)

        if (
            name == "2um_725_45d_7m"
            or name == "5um_825_45d_7m"
            or name == "10um_825_45d_7m"
        ):
            yield from bps.mv(prs, 45)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        else:
            yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets it for you via t=.)
        name_fmt = "{sample}_{energy}eV"
        for i, e in enumerate(energies):

            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="IC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_arc)
            if e == 2405:
                yield from bps.mv(energy, 2430)
            elif e == 2481:
                yield from bps.mv(energy, 2460)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 2430)
                yield from bps.mv(energy, 2405)
                name_fmt = "{sample}_2405eV_postedge"
                sample_name = name_fmt.format(sample=name)
                sample_id(user_name="IC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.scan(dets, waxs, *waxs_arc)

    names = ["10um_825_45d_7m_nexafs_w20"]
    x = [-5000]
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    yield from bps.mv(waxs, 20)
    yield from bps.mv(energy, 2420)  # 💡 smi_plans: you can drop this stepped energy ramp-up — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2440)
    yield from bps.mv(energy, 2450)
    energies = np.linspace(2450, 2531, 163)
    for xs, name in zip(x, names):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run/energy_axis set it for you via t=.)
        name_fmt = "{sample}_{energy}eV"
        for i, e in enumerate(energies):
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="IC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            if e == 2405:
                yield from bps.mv(energy, 2430)
            elif e > 2530.6:
                yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 2470)
                yield from bps.mv(energy, 2430)
                yield from bps.mv(energy, 2405)
                name_fmt = "{sample}_2405eV_postedge"
                sample_name = name_fmt.format(sample=name)
                sample_id(user_name="IC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def film_Sn_edge2(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tin-edge energy scan on two film spots (sample + background) — at each
    #   x it steps the energy across the Sn edge and takes a WAXS image, with a manual energy
    #   walk-back to a post-edge point at the end.
    #
    # 💡 NEWER, EASIER WAY: stepping the energy across an edge and recording it is exactly
    #   'smi_plans' nexafs_run / energy_axis — it handles the energy move + beam feedback and
    #   writes the energy into each image and file name (so you can drop the hand-built name
    #   and the energy walk-backs):
    #     from smi_plans import nexafs_run
    #     for name, xpos in zip(["...sample...", "...bkg..."], [6700, -5000]):
    #         yield from bps.mv(piezo.x, xpos)
    #         yield from nexafs_run(name, [3850, 3900, 3920, 3925, *range(3930, 3941)],
    #                               t=t, dets=[pil900KW], geometry="reflection")
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 walk-backs
    #    become unnecessary.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    names = [
        "1909_utbVE_40p11cd_ai1p1_2bragg_w3p7",
        "1909_utbVE_40p11cd_ai1p1_2bragg_bkg_w3p7",
    ]
    x = [6700, -5000]

    energies = np.concatenate(
        [np.asarray([3850, 3900, 3920, 3925]), np.arange(3930, 3941, 1)]
    )
    for xs, name in zip(x, names):
        yield from bps.mv(piezo.x, xs)
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run/energy_axis set it for you via t=.)
        name_fmt = "{sample}_{energy}eV"
        for e in energies:
            yield from bps.mv(energy, e)

            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="IC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

            if e == 3850:
                yield from bps.mv(energy, 3875)

            elif e > 3939.5:
                yield from bps.mv(energy, 3920)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 3890)
                yield from bps.mv(energy, 3850)
                name_fmt = "{sample}_3850eV_postedge"
                sample_name = name_fmt.format(sample=name)
                sample_id(user_name="IC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def film_Sn_edge1(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same as film_Sn_edge2 but on a different pair of film spots and a
    #   slightly finer energy grid across the tin edge.
    #
    # 💡 NEWER, EASIER WAY: same 'smi_plans' nexafs_run / energy_axis as film_Sn_edge2 — it
    #   handles the energy move + beam feedback and records the energy into each image and
    #   file name:
    #     from smi_plans import nexafs_run
    #     for name, xpos in zip(["...sample...", "...bkg..."], [-23000, -17000]):
    #         yield from bps.mv(piezo.x, xpos)
    #         yield from nexafs_run(name, energies, t=t, dets=[pil900KW], geometry="reflection")
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 walk-backs
    #    become unnecessary.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    names = [
        "1909_bbVE_40p11cd_ai1p1_2bragg_w3p7",
        "1909_bbVE_40p11cd_ai1p1_2bragg_bkg_w3p7",
    ]
    x = [-23000, -17000]

    energies = np.concatenate(
        [
            np.asarray([3850, 3900, 3920]),
            np.arange(3925, 3935, 0.5),
            np.arange(3935, 3946, 1),
        ]
    )
    for xs, name in zip(x, names):
        yield from bps.mv(piezo.x, xs)
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run/energy_axis set it for you via t=.)
        name_fmt = "{sample}_{energy}eV"
        for e in energies:
            yield from bps.mv(energy, e)

            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="IC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

            if e == 3850:
                yield from bps.mv(energy, 3875)

            elif e > 3944.5:
                yield from bps.mv(energy, 3920)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 3890)
                yield from bps.mv(energy, 3850)
                name_fmt = "{sample}_3850eV_postedge"
                sample_name = name_fmt.format(sample=name)
                sample_id(user_name="IC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def film_Sn_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tin-edge scan on one film — at each energy it sweeps the WAXS arc
    #   (a small rocking range) and takes images, switching to a "postedge" label after the
    #   energy walk-back.
    #
    # 💡 NEWER, EASIER WAY: combine 'smi_plans' energy + WAXS-arc axes in one giwaxs_run; it
    #   handles the energy move + beam feedback and records energy / arc-angle into each image
    #   and file name:
    #     from smi_plans import giwaxs_run, energy_axis, motor_axis
    #     yield from giwaxs_run(
    #         "1909_utbVE_40p11CD_ai0p5deg", [pil900KW], t=t,
    #         axes=[energy_axis([3850, 3900, 3920, 3925, 3930, 3935, 3945]),
    #               motor_axis("waxs", waxs, np.arange(3, 16, 3))])
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 walk-back
    #    becomes unnecessary.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    names = ["1909_utbVE_40p11CD_ai0p5deg"]

    energies = [3850, 3900, 3920, 3925, 3930, 3935, 3945, 3850]
    waxs_arc = [3, 16, 3]
    i = 0
    for name in names:
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_run/energy_axis set it for you via t=.)
        name_fmt = "{sample}_{energy}eV"
        for e in energies:
            yield from bps.mv(energy, e)
            if i == 1:
                name_fmt = "{sample}_{energy}eV_postedge"
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="IC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_arc)

            if e == 3850:
                yield from bps.mv(energy, 3875)

            elif e == 3945:
                yield from bps.mv(energy, 3920)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 3890)
                yield from bps.mv(energy, 3850)
                i = 1


def fly_scan_ai(det, motor, cycle=1, cycle_t=10, phi=-0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a "fly scan" of incident angle — it stages the detector, sets a long
    #   single exposure, triggers it, then sweeps the angle continuously back and forth while
    #   the one long frame integrates (a continuous-motion reflectivity sweep).
    #
    # 💡 NEWER, EASIER WAY: this hand-built fly scan pokes the camera directly
    #   (det.cam.acquire_time.put / det.trigger / busy-wait 'while not st.done: pass') and
    #   doesn't record a normal Bluesky "run" (so the metadata/file-naming you get elsewhere
    #   isn't captured). In smi_plans, continuous sweeps are expressed as a plan with a
    #   motor_axis and the detectors as recorded readables, so you keep the metadata and it
    #   composes with the rest. (Ask beamline staff for the current fly/continuous-sweep
    #   helper if you rely on this.) (Not broken to run, but it's the least-recorded style —
    #   internal: Tier 0.)
    # === end smi_plans note ================================================
    start = phi + 0
    stop = phi + 4.5
    acq_time = cycle * cycle_t
    yield from bps.mv(motor, start)
    # yield from bps.mv(attn_shutter, 'Retract')
    det.stage()
    det.cam.acquire_time.put(acq_time)
    print(f"Acquire time before staging: {det.cam.acquire_time.get()}")
    st = det.trigger()
    for i in range(cycle):
        yield from list_scan([], motor, [start, stop])
    while not st.done:
        pass
    det.unstage()
    print(f"We are done after {acq_time}s of waiting")
    # yield from bps.mv(attn_shutter, 'Insert')


def ai_scan_multilayer(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant X-ray reflectivity (XRR) scan — at each energy it sweeps the
    #   incident angle (theta) up then down over a fine range, taking a WAXS image at each
    #   angle.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has xrr_resonant_run for exactly this (reflectivity at
    #   several energies near an edge). incidence_axis sweeps the incident angle and energy_axis
    #   steps the energy (handling the move + beam feedback), and the angle/energy are recorded
    #   into each image and file name (so you can drop the hand-built name and fwd/rev tags):
    #     from smi_plans import xrr_resonant_run
    #     yield from xrr_resonant_run(
    #         "10nmMLYAHY_noPEB_Exp1", [pil900KW], t=t,
    #         energies=[3900, 3930, 4000],
    #         incident_angles=np.linspace(0.5, 2.5, 101), th0=piezo.th.position, updown=True)
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    name = "10nmMLYAHY_noPEB_Exp1"
    energies = [3900, 3930, 4000]
    waxs_arc = [6.5]
    incident_angle = np.linspace(0.5, 2.5, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr_resonant_run sets it for you via t=.)
    name_fmt = "{sample}_{energy}eV_ai{alpha_i}_wa{waxs}_{num}"

    ai0 = piezo.th.position

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        for e in energies:
            yield from mv_energy(e)
            yield from bps.mvr(piezo.x, 200)
            for i in [0, 1]:
                if i == 0:
                    incident_an = incident_angle
                    met = "fwd"
                else:
                    incident_an = incident_angle[::-1]
                    met = "rev"

                for inc_ang in incident_an:
                    print(inc_ang)
                    yield from bps.mv(piezo.th, ai0 + inc_ang)

                    sample_name = name_fmt.format(
                        sample=name,
                        energy=e,
                        alpha_i="%3.2f" % inc_ang,
                        waxs=wa,
                        num=met,
                    )
                    sample_id(user_name="IC", sample_name=sample_name)

                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


def ai_scan_multilayer_nightscan(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight resonant XRR run — for each sample it aligns (with gate
    #   valve / attenuator handling), then for each energy sweeps the incident angle and takes
    #   a WAXS image at each, with an energy walk-down between samples.
    #
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' xrr_resonant_run with align_sample. It
    #   aligns each sample and saves the result, sweeps incident angle and energy (handling the
    #   energy move + beam feedback), and records angle/energy into each image and file name:
    #     from smi_plans import xrr_resonant_run, align_sample
    #     yield from xrr_resonant_run(
    #         "bare_ML", [pil900KW], t=t, align=align_sample,
    #         energies=np.linspace(3900, 4000, 21),
    #         incident_angles=np.linspace(0.5, 2.5, 101))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines; the 💡 energy
    #    walk-down becomes unnecessary.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (GV7 / att2_* are fine.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    # names = ['10nmSiYAVE_Unexp', '10nmMLYAVE_Unexp', '10nmSiYAHY_Unexp', 'bare_ML']
    names = ["bare_ML"]
    # xs = [-36500, -23000, -1000, 23400]
    xs = [23400]
    energies = np.linspace(3900, 4000, 21)
    waxs_arc = [6.5]
    incident_angle = np.linspace(0.5, 2.5, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr_resonant_run sets it for you via t=.)
    name_fmt = "{sample}_{energy}eV_ai{alpha_i}_wa{waxs}"

    ai0 = 0

    for z, (x, name) in enumerate(zip(xs, names)):

        yield from bps.mv(piezo.x, x)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(10)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.mv(piezo.th, ai0)

        yield from alignement_gisaxs(0.4)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(10)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.mv(att2_10, "Insert")
        ai0 = piezo.th.position
        for i, wa in enumerate(waxs_arc):
            if i == 0:
                incid_angle = incident_angle
            else:
                incid_angle = incident_angle[::-1]
            yield from bps.mv(waxs, wa)
            energiess = energies
            for j, e in enumerate(energiess):
                yield from bps.mv(energy, e)
                if z == 3:
                    yield from bps.mvr(piezo.x, 0)
                else:
                    yield from bps.mvr(piezo.x, 250)

                for inc_ang in incid_angle:
                    yield from bps.mv(piezo.th, ai0 + inc_ang)

                    sample_name = name_fmt.format(
                        sample=name, energy=e, alpha_i="%3.2f" % inc_ang, waxs=wa
                    )
                    sample_id(user_name="IC", sample_name=sample_name)

                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 3960)  # 💡 smi_plans: you can drop this energy walk-down + sleep — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(5)
            yield from bps.mv(energy, 3920)


# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT'S BELOW: the big triple-quoted ("...") block that follows is COMMENTED-OUT scratch
#   code — an old, never-finished 'ai_scan_reflectivity_scan'. It is a string, not running
#   code (and it has unfinished syntax, e.g. missing colons), so it does nothing. We did NOT
#   touch anything inside it. If you want that reflectivity scan, the working, supported way
#   is 'smi_plans' xrr_resonant_run (see the note on ai_scan_multilayer_nightscan above) —
#   not this scratch. Safe to delete this dead block whenever you like.
# === end smi_plans note ================================================
"""
def ai_scan_reflectivity_scan(t=1):
    dets = [pil300KW]
    
    #names = ['10nmSiYAVE_Unexp', '10nmMLYAVE_Unexp', '10nmSiYAHY_Unexp', 'bare_ML']
    names = ['bare_ML']
    #xs = [-36500, -23000, -1000, 23400]
    xs = [23400]
    #energies = np.linspace(3900, 4000, 21)
    energies = [3900,3930,4100]
    incident_angle = np.linspace(0.1, 5, 101)
    
    det_exposure_time(t,t) 
    name_fmt = '{sample}_reflectivity_{energy}eV_{direction}_ai{alpha_i}_'

    ai0 = 0
    
    # Loop over samples, doing alignment first
    for z, (x, name) in enumerate(zip(xs, names)):
        
        # Move to sample position
        yield from bps.mv(piezo.x, x)

        # Move waxs out of the way
        yield from bps.mv(wax, 13.5)

        # Open gate valve for alignment
        yield from bps.mv(GV7.open_cmd, 1 )
        yield from bps.sleep(10)
        # Make sure valve is open?
        yield from bps.mv(GV7.open_cmd, 1 )
        # Move incident angle to guessed zero
        yield from bps.mv(piezo.th, ai0)
        # Align theta and z
        yield from alignement_gisaxs(0.4)
        # Close the gate valve
        yield from bps.mv(GV7.close_cmd, 1 )
        yield from bps.sleep(10)
        yield from bps.mv(GV7.close_cmd, 1 )
        
        # Redefine zerp theta based on alignment
        ai0 = piezo.th.position

        # Move the waxs back
        yield from bps.mv(waxs, 0)

        # Insert all Al filters (subject to change based on flux)
        yield from bps.mv(att2_9, 'Insert')
        yield from bps.mv(att2_10, 'Insert')
        yield from bps.mv(att2_11, 'Insert')
        yield from bps.mv(att2_12, 'Insert')

        # Once aligned, loop over energies
        for j, e in enumerate(energies):
            # step carefully through energy

            # Move in x
            yield from bps.mvr(piezo.x,300)

            for d in ['fwd','rev']
                # Define incident angle direction
                if d == 'fwd'    
                    incid_angle = incident_angle
                elif d == 'rev'
                    incid_angle = incident_angle[::-1]

                for inc_ang in incid_angle:
                    yield from bps.mv(piezo.th, ai0 + inc_ang)

                    sample_name = name_fmt.format(sample=name, energy=e, direction=d, alpha_i='%3.2f'%inc_an)
                    sample_id(user_name='IC', sample_name=sample_name)
                    
                    print(f'\n\t=== Sample: {sample_name} ===\n')
                    yield from bp.count(dets, num=1)
            
            yield from bps.mv(energy, 3960)
            yield from bps.sleep(5)
            yield from bps.mv(energy, 3920)
"""


def reflectivity_night(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: runs the reflectivity scan three times back-to-back (with different
    #   "foil" numbers) — an overnight batch wrapper around test_reflectivity_scan.
    # 💡 In 'smi_plans' the reflectivity run is xrr_resonant_run (see test_reflectivity_scan's
    #   note); you'd just 'yield from' it a few times the same way. (Nothing broken here.)
    # === end smi_plans note ================================================
    yield from test_reflectivity_scan(t=0.5, nu=1)
    yield from test_reflectivity_scan(t=0.5, nu=2)
    yield from test_reflectivity_scan(t=0.5, nu=3)


def test_reflectivity_scan(t=1, nu=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the main resonant X-ray reflectivity run — for each sample it aligns
    #   (gate valve handling), then at each energy steps the incident angle through several
    #   ranges, switching attenuators per range to keep the signal in a good window, and
    #   takes a WAXS image at each angle.
    #
    # 💡 NEWER, EASIER WAY: this whole "align, sweep angle in ranges with the right
    #   attenuation, at several energies" is what 'smi_plans' xrr_resonant_run is for. It
    #   aligns (align_sample), sweeps incident angle (incidence_axis) and energy (energy_axis,
    #   handling the move + beam feedback), and can manage the per-range attenuation, recording
    #   angle/energy into each image and file name (so the hand-built name, the clean_shit/
    #   function_att attenuator juggling, and the mv_energy stepping all become unnecessary):
    #     from smi_plans import xrr_resonant_run, align_sample
    #     bar = ...   # your samples (names + xs + zs) as a SampleList
    #     yield from xrr_resonant_run(bar, [pil900KW], t=t, align=align_sample,
    #                                 energies=[3900, 3930, 4100],
    #                                 incident_angles=np.linspace(0.2, 4.8, 257))
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (GV7 / att2_* / waxs.x are fine.) (Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).
    energy = [3900, 3930, 4100]  #'3900'
    dire = "fwd"
    names = [
        "10nmSiYAHY_Unexp_Ref",
        "10nmMLYAVE_Unexp_Ref",
        "10nmSiYAVE_Unexp_Ref",
        "bare_ML_part2",
        "10nmMLYAHY_noPEB_Exp_Ref",
    ]
    # name = 'bare_ML'
    xs = [-2850, -17850, -36350, 22050, 39050]
    zs = [-2400, -2400, -2400, -2400, -3000]  # 23400
    # x = 22650

    # PUT SAMPLE LOOP HERE
    ai0 = 0

    for x, z, name in zip(xs, zs, names):

        # Move to sample position
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.z, z)

        # Open gate valve for alignment
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(10)
        # Make sure valve is open?
        yield from bps.mv(GV7.open_cmd, 1)
        # Move incident angle to guessed zero
        yield from bps.sleep(5)

        yield from bps.mv(piezo.th, ai0)
        # Align theta and z
        yield from alignement_gisaxs(0.4)
        # Close the gate valve
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(10)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)

        ai0 = piezo.th.position

        # Move the waxs back
        yield from bps.mv(waxs, 0)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr_resonant_run sets it for you via t=.)
        name_fmt = "{sample}_reflectivity_{energy}eV_{direction}_ai{alpha_i}_foil{num}_{number}"

        # Define angular ranges for the scan
        ai_ranges = [
            [0.2, 0.7],
            [0.6, 1.2],
            [0.9, 1.6],
            [1.5, 2.6],
            [2.5, 3.0],
            [2.9, 3.2],
            [3.1, 3.6],
            [3.5, 4.0],
            [3.9, 4.4],
            [4.3, 4.8],
        ]
        ais = [[]] * len(ai_ranges)
        for alphai in np.linspace(0.2, 4.8, 257):
            for i, ai_range in enumerate(ai_ranges):
                if alphai < ai_range[1] and ai_range[0] <= alphai:
                    ais[i] = ais[i] + [alphai]

        # Loop over the energies
        for en in energy:
            # Change energy using slow change defined below
            yield from bps.mvr(piezo.x, 300)

            yield from mv_energy(en)
            for ran_num, aiss in enumerate(ais):
                yield from clean_shit()
                yield from clean_shit()
                yield from function_att(ran_num)
                yield from function_att(ran_num)

                if ran_num < 3.5:
                    yield from bps.mv(waxs.x, 0)
                else:
                    yield from bps.mv(waxs.x, -22.0)

                for ai in aiss:
                    yield from bps.mv(piezo.th, ai0 + ai)

                    sample_name = name_fmt.format(
                        sample=name,
                        energy=en,
                        direction=dire,
                        alpha_i="%4.3f" % ai,
                        num=ran_num,
                        number=nu,
                    )
                    sample_id(user_name="IC", sample_name=sample_name)

                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


def clean_shit(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: retracts all 12 attenuators one by one (clears all attenuation).
    # 💡 Attenuator helper — the att2_* attenuators are fine and still work the same way, so
    #   nothing here is broken. In 'smi_plans' the reflectivity run can set attenuation per
    #   angle range for you, so you usually don't clear/set them by hand. (Nothing to fix.)
    # === end smi_plans note ================================================
    yield from bps.mv(att2_1, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_2, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_3, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_4, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_5, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_6, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_7, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_8, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_9, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_10, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_11, "Retract")
    yield from bps.sleep(t)
    yield from bps.mv(att2_12, "Retract")
    yield from bps.sleep(t)


def clean_sh(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: inserts all 12 attenuators one by one (maximum attenuation) — the
    #   opposite of clean_shit.
    # 💡 Attenuator helper — att2_* still work the same way; nothing broken. In 'smi_plans'
    #   the reflectivity run handles per-range attenuation for you. (Nothing to fix.)
    # === end smi_plans note ================================================
    yield from bps.mv(att2_1, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_2, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_3, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_4, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_5, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_6, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_7, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_8, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_9, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_10, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_11, "Insert")
    yield from bps.sleep(t)
    yield from bps.mv(att2_12, "Insert")
    yield from bps.sleep(t)


def function_att(ran_num, t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an attenuator "ladder" — inserts a specific combination of attenuators
    #   for each incident-angle range (ran_num), so the reflectivity signal stays in a good
    #   range as the angle changes.
    # 💡 Attenuator helper — att2_* still work the same way; nothing broken. In 'smi_plans'
    #   xrr_resonant_run can apply per-range attenuation as part of the run, so you usually
    #   don't call this by hand. (Nothing to fix.)
    # === end smi_plans note ================================================
    if ran_num == 0:
        # 5x +1x
        yield from bps.mv(att2_5, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 1:
        # 4x +1x
        yield from bps.mv(att2_5, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 2:
        # 3x +1x
        yield from bps.mv(att2_5, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_10, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 3:
        # 12x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_10, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 4:
        # 11x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 5:
        # 10x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 6:
        # 8x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_10, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 7:
        # 7x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 8:
        # 6x
        yield from bps.mv(att2_12, "Insert")
        yield from bps.sleep(t)

    elif ran_num == 9:
        # 5x
        yield from bps.mv(att2_11, "Insert")
        yield from bps.sleep(t)
        yield from bps.mv(att2_9, "Insert")
        yield from bps.sleep(t)


# © Luke Long. Venmo is an acceptable form of payment.
def mv_energy(set_point, t=3, step=30):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the X-ray energy to a target carefully — it walks there in 30 eV
    #   steps, sleeping a few seconds after each step, because big energy jumps used to be
    #   flaky.
    # 💡 NEWER, EASIER WAY: the beamline's energy move was fixed, and 'smi_plans' does all of
    #   this for you. move_energy_fb (and energy_axis, used inside the technique runs) steps
    #   the energy in one move (the device manages the feedback),
    #   (re-seek is opt-in) — so you don't need this hand-rolled stepper anymore:
    #     from smi_plans import move_energy_fb
    #     yield from move_energy_fb(set_point)     # safe stepped move + settle, done for you
    #   (This isn't broken — it just becomes unnecessary once you migrate. See the 💡 below.)
    # === end smi_plans note ================================================
    e_diff = set_point - energy.energy.position
    while abs(e_diff) > step:
        print(
            f"LARGE ENERGY DIFFERENCE. TAKING STEP SIZE OF {step}eV. @ GUI: DONT FORGET TO VENMO LUKE"
        )
        yield from bps.mvr(energy, sign(e_diff) * 30)
        yield from bps.sleep(t)  # 💡 smi_plans: you can drop this settle wait (and this whole stepped loop) — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
        e_diff = set_point - energy.energy.position
    yield from bps.mv(energy, set_point)


def fluo_scan(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a fluorescence energy scan — at a fixed incident angle it steps the
    #   energy across the edge and records a WAXS image plus the beam reading at each step.
    #
    # 💡 NEWER, EASIER WAY: stepping the energy across an edge and recording the beam is
    #   'smi_plans' nexafs_run / energy_axis; it handles the energy move + beam feedback and
    #   writes the energy and beam into each image and file name (so you can drop the hand-
    #   built "{sample}_{energy}eV_bpm{bpm}" name):
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run(
    #         "10nmMLYAHY_noPEB_Unexp_fluoscan1_",
    #         np.append(np.linspace(3900, 3990, 181), np.linspace(3990, 4100, 56)),
    #         t=t, dets=[pil900KW, xbpm2])
    #   (Just a tidier option — your script works as-is EXCEPT the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (WAXS) was retired — it's now 'pil900KW'
    #   (⚠️ note below); (2) the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' (WAXS) was removed (this would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration).

    name = "10nmMLYAHY_noPEB_Unexp_fluoscan1_"
    energies = np.append(np.linspace(3900, 3990, 181), np.linspace(3990, 4100, 56))

    waxs_arc = [20]
    incident_angle = 0.6

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run/energy_axis set it for you via t=.)
    name_fmt = "{sample}_{energy}eV_bpm{bpm}"
    yield from bps.mvr(piezo.th, incident_angle)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        for e in energies:
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(
                sample=name, energy=e, bpm="%5.2f" % xbpm2.sumX.value
            )
            sample_id(user_name="IC", sample_name=sample_name)

            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            # print(inc_ang)
            # yield from bps.sleep(1)

    yield from bps.mvr(piezo.th, -incident_angle)

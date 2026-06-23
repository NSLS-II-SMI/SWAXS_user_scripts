def NEXAFS_S_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS sweep across the sulfur edge (2430->2520 eV, 91
    #   points), taking a WAXS image + beam reading at each energy.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library called 'smi_plans' that does a
    #   full energy scan like this in ONE line, and records the energy/beam straight INTO each
    #   image (so you don't have to hand-build the "{energy}eV_xbpm{xbpm}" file name):
    #
    #     from smi_plans import nexafs_run            # do this once per session
    #     yield from nexafs_run("su8_ne", np.linspace(2430, 2520, 91), t=t,
    #                           dets=[pil900KW], geometry="transmission")
    #
    #   (it sets the exposure, manages the energy move + beam feedback, and re-seeks if the beam
    #    dips — so you can drop the per-step sleeps. Use pil900KW for the current WAXS detector.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding you
    #    can simply delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (see the
    #   ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 65)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "su8_ne"

    energies = np.linspace(2430, 2520, 91)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(sample=name, energy=e, xbpm="%3.2f" % bpm)
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


def NEXAFS_Cl_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS sweep across the chlorine edge (2815->2850 eV, 71
    #   points), taking SAXS+WAXS images + a beam reading at each energy.
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run
    #     yield from nexafs_run("ZEP_flood_redo_ai1.5deg", np.linspace(2815, 2850, 71), t=t,
    #                           dets=[pil2M, pil900KW], geometry="transmission")
    #   (sets the exposure, manages the energy move + beam feedback, and records energy/beam into
    #    each image — so you can drop the per-step sleep. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (see the
    #   ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 65)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "ZEP_flood_redo_ai1.5deg"

    energies = np.linspace(2800, 2850, 51)
    energies = np.linspace(2815, 2850, 71)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(sample=name, energy=e, xbpm="%3.2f" % bpm)
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


def NEXAFS_S_edge_fine(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the sample, then runs a tender-energy NEXAFS sweep across the sulfur
    #   edge with a FINE step near the edge, taking a WAXS image + beam reading at each energy.
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run, align_sample
    #     energies = np.r_[np.arange(2440,2470,5), np.arange(2470,2475,1),
    #                      np.arange(2475,2485,0.5), np.arange(2485,2500,1), np.arange(2500,2520,5)]
    #     yield from nexafs_run("ZEP_flood", energies, t=t, dets=[pil900KW],
    #                           geometry="grazing", align=align_sample)   # grazing = your ai=1.5deg
    #   (align_sample aligns and saves the result with the data; nexafs_run sets the exposure,
    #    manages the energy move + beam feedback, and records energy/beam — so you can drop the
    #    per-step sleeps and the stepped walk-back. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 65)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    energies = (
        np.arange(2440, 2470, 5).tolist()
        + np.arange(2470, 2475, 1).tolist()
        + np.arange(2475, 2485, 0.5).tolist()
        + np.arange(2485, 2500, 1).tolist()
        + np.arange(2500, 2520, 5).tolist()
    )
    ai = 1.5

    # names =  [ 'Sn', 'Sb', 'SP', 'Sn_exp', 'Sb_exp', 'SP_exp', 'SnZ', 'SbZ', 'SPZ', 'Sn_exp_Z', 'Sb_exp_Z', 'SP_exp_Z']
    # x_piezo = [48000, 38000, 28000, 20000, 12000, 1000, -8000, -16000, -22000, -30000, -38000, -48000]
    # y_piezo = [ 6500,  6500,  6500,  6500,  6500, 6500,  6900,   6900,  6900,   6900,   6900,   6900]
    # z_piezo = [    0,     0,     0,     0,     0,    0,     0,      0,     0,      0,      0,      0]

    names = ["ZEP_flood"]
    x_piezo = [51000]
    y_piezo = [7500]
    z_piezo = [0]

    ai0 = 1
    for name, x, y in zip(names, x_piezo, y_piezo):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        yield from bps.mv(piezo.th, ai0)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "nexafs_{sample}_{energy}eV_angle{ai}_bpm{xbpm}"

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_gisaxs(angle=0.4)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.close_cmd, 1)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position

        yield from bps.mv(piezo.th, ai0 + 1.5)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "nexafs_2s_{sample}_{energy}eV_angle{ai}_bpm{xbpm}"
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

            bpm = xbpm3.sumX.value

            sample_name = name_fmt.format(
                sample=name, energy=e, ai=1.5, xbpm="%3.2f" % bpm
            )
            sample_id(user_name="SR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
        yield from bps.mv(energy, 2470)
        yield from bps.mv(energy, 2450)


def alignement_Tiwale(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment-only pass — puts the beamline in GISAXS alignment mode, aligns
    #   each sample on the bar, and stashes the found incident angle / aligned y in module-level
    #   lists for the measurement routines below.
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you don't align everything up front and keep the
    #   numbers in globals. align_sample aligns each sample right when you measure it and saves
    #   the alignment WITH the data:
    #     from smi_plans import align_sample, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, z=z_piezo)
    #     # pass align=align_sample to nexafs_bar / giwaxs_bar (see the measurement functions)
    #   (Nothing here is broken — this is just the tidier, "align-and-record-together" approach.)
    # === end smi_plans note ================================================
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, xs_hexa

    names = ["su8_ue", "su8_exp", "uv6_ue", "uv6_exp", "pag_0", "pag_20", "pag_40"]
    x_piezo = [53500, 34900, 25500, 5500, -15500, -38500, -47500]
    y_piezo = [6859.975, 6900, 6900, 6900, 6900, 6900, 6900]
    z_piezo = [0, 0, 0, 0, 0, 0]
    x_hexa = [10, 10, 10, 10, 10, 0]
    incident_angles = []
    y_piezo_aligned = []

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, xs_piezo, zs_piezo, ys_piezo, xs_hexa in zip(
        names, x_piezo, z_piezo, y_piezo, x_hexa
    ):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs_piezo)
        yield from bps.mv(piezo.y, ys_piezo)
        yield from bps.mv(piezo.z, zs_piezo)

        yield from bps.mv(piezo.th, 0)
        yield from alignement_gisaxs_multisample(angle=0.25)

        incident_angles = incident_angles + [piezo.th.position]
        y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

    yield from smi.modeMeasurement()

    print(incident_angles)
    print(y_piezo_aligned)


def NEXAFS_S_edge_fine_multisample(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS bar across the sulfur edge (fine step) — for each pre-aligned
    #   sample it moves into place at its incident angle and sweeps the energy, taking a WAXS
    #   image + beam reading at each, then steps the energy back down.
    # 💡 NEWER, EASIER WAY: running a NEXAFS energy sweep on each sample of a bar is the
    #   'smi_plans' energy-scan + bar combination — nexafs_bar takes a SampleList and runs the
    #   sweep at each sample, recording the energy/position/beam into each image:
    #     from smi_plans import nexafs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, z=z_piezo)
    #     energies = np.r_[np.arange(2440,2470,5), np.arange(2470,2475,1),
    #                      np.arange(2475,2485,0.5), np.arange(2485,2500,1), np.arange(2500,2520,5)]
    #     yield from nexafs_bar("SR", samples, energies=energies, t=t, dets=[pil900KW],
    #                           align=align_sample)
    #   (manages the energy move + beam feedback, so you can drop the per-step and walk-back
    #    sleeps. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (see the
    #   ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, xs_hexa

    names = ["su8_ue", "su8_exp", "uv6_ue", "uv6_exp", "pag_0", "pag_20", "pag_40"]
    x_piezo = [53500, 37900, 25500, 8500, -15500, -38500, -47500]
    y_piezo = [6900, 6900, 6900, 6900, 6900, 6900, 6900]
    z_piezo = [0, 0, 0, 0, 0, 0, 0]
    x_hexa = [10, 10, 10, 10, 10, 10, 0]
    incident_angles = [
        0.2122,
        0.168532,
        -0.113152,
        -0.313694,
        0.233214,
        0.207891,
        0.186071,
    ]
    y_piezo_aligned = [
        6859.975,
        6915.767,
        6901.334,
        6922.385,
        6992.986,
        7033.101,
        7140.869,
    ]

    energies = (
        np.arange(2440, 2470, 5).tolist()
        + np.arange(2470, 2475, 1).tolist()
        + np.arange(2475, 2485, 0.5).tolist()
        + np.arange(2485, 2500, 1).tolist()
        + np.arange(2500, 2520, 5).tolist()
    )

    yield from bps.mv(waxs, 65)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for name, xs_piezo, zs_piezo, ys_piezo, xs_hexa, ais in zip(
        names, x_piezo, z_piezo, y_piezo_aligned, x_hexa, incident_angles
    ):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs_piezo)
        yield from bps.mv(piezo.y, ys_piezo)
        yield from bps.mv(piezo.z, zs_piezo)
        yield from bps.mv(piezo.th, ais + 0.7)

        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

            bpm = xbpm3.sumX.value

            sample_name = name_fmt.format(sample=name, energy=e, xbpm="%3.2f" % bpm)
            sample_id(user_name="SR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2470)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2450)
        yield from bps.sleep(2)


def saxs_prep_multisample(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS bar near the sulfur edge — for each WAXS arc and sample it
    #   walks the energy and (per energy) a fresh x spot and several incident angles, taking a
    #   WAXS image at each and stepping the energy back down between samples.
    # 💡 NEWER, EASIER WAY: build the energies and incident angles as "axes" and hand them to one
    #   acquire call (per sample / arc); smi_plans records energy/angle/position/beam into each
    #   image and manages the energy move + beam feedback:
    #     from smi_plans import acquire, energy_axis, incidence_axis, motor_axis
    #     yield from acquire("pag_40", [pil900KW],
    #                        [motor_axis("wa", waxs, np.linspace(0,39,7)),
    #                         energy_axis([2450, 2475, ..., 2500]),
    #                         incidence_axis(piezo.th, ai0, [0.3, 0.5, 0.7, 1.0, 1.5])])
    #   (so you can drop the per-step sleeps and the walk-back. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    energies = [
        2450,
        2475,
        2476,
        2477,
        2478,
        2479,
        2480,
        2481,
        2482,
        2483,
        2484,
        2490,
        2500,
    ]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_pos{posi}_wa{wa}_xbpm{xbpm}"

    waxs_range = np.linspace(0, 39, 7)

    # names=  [  'pag_0',  'pag_20',  'pag_40']
    # x_piezo = [ -15500,    -38500,    -47500]
    # y_piezo = [   6900,      6900,      6900]
    # z_piezo = [      0,         0,         0]
    # x_hexa =  [      7,         7,         0]
    # incident_angles = [ 0.233214, 0.207891, 0.186071]
    # y_piezo_aligned = [ 6992.986, 7033.101, 7140.869]

    names = ["pag_40"]
    x_piezo = [-47500]
    y_piezo = [6900]
    z_piezo = [0]
    x_hexa = [-4]
    incident_angles = [0.186071]
    y_piezo_aligned = [7140.869]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)

        for name, xs_piezo, zs_piezo, ys_piezo, xs_hexa, ais in zip(
            names, x_piezo, z_piezo, y_piezo_aligned, x_hexa, incident_angles
        ):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.x, xs_piezo)
            yield from bps.mv(piezo.y, ys_piezo)
            yield from bps.mv(piezo.z, zs_piezo)
            yield from bps.mv(piezo.th, ais)

            for k, e in enumerate(energies):
                yield from bps.mv(piezo.x, xs_piezo - k * 300)
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

                name_fmt = "{sample}_saxs_ai{ai}_{energy}eV_xbpm{xbpm}_wa{wa}"

                for j, aiss in enumerate([0.3, 0.5, 0.7, 1.0, 1.5]):
                    yield from bps.mv(piezo.th, ais + aiss)

                    sample_name = name_fmt.format(
                        sample=name,
                        ai="%1.2f" % aiss,
                        energy=e,
                        xbpm="%3.1f" % xbpm3.sumY.value,
                        wa="%2.1f" % wa,
                    )
                    sample_id(user_name="OS", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)  # 💡 smi_plans: you can drop this stepped energy walk-back (and the sleeps after it) — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2450)
            yield from bps.sleep(2)


def SAXS_S_edge_fine(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant-SAXS energy sweep across the sulfur edge (fine step), taking a
    #   SAXS image + beam reading at each energy, then stepping the energy back down.
    # 💡 NEWER, EASIER WAY:  from smi_plans import acquire, energy_axis
    #     energies = np.r_[np.arange(2450,2470,5), np.arange(2470,2475,1),
    #                      np.arange(2475,2485,0.5), np.arange(2485,2500,1), np.arange(2500,2520,5)]
    #     yield from acquire("s3_ai0.9deg_sdd2.5m", [pil2M], [energy_axis(energies)])
    #   (records energy/beam into each image and manages the energy move — so you can drop the
    #    per-step sleep and the stepped walk-back.)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M]
    name = "s3_ai0.9deg_sdd2.5m"
    energies = (
        np.arange(2450, 2470, 5).tolist()
        + np.arange(2470, 2475, 1).tolist()
        + np.arange(2475, 2485, 0.5).tolist()
        + np.arange(2485, 2500, 1).tolist()
        + np.arange(2500, 2520, 5).tolist()
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(sample=name, energy=e, xbpm="%3.2f" % bpm)
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2470)
    yield from bps.mv(energy, 2450)


def fly_scan_ai_nikhil(det, motor, cycle=1, cycle_t=10, phi=-0.6):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hand-rolled "fly" exposure — parks the rotation motor at the start, arms
    #   the detector and starts ONE long exposure by hand, then rocks the motor between two
    #   angles while it integrates, and busy-waits for it to finish.
    #
    # ⚠️ HEADS-UP (important, even though Python won't error): this pokes the detector directly
    #   (det.stage(), det.cam.acquire_time.put(...), det.trigger()) and busy-waits with
    #   'while not st.done: pass'. Because the trigger happens OUTSIDE Bluesky's RunEngine (the
    #   part that records a "run"), the frames are NOT written into the data catalog as a proper
    #   dataset — there are no start/stop/event "documents", so the image, the rocking angle, the
    #   beam intensity and the timing are not saved together the way the other scans here are.
    #   You'd have to fetch the raw file off the detector by hand, and the busy-wait blocks
    #   everything else while it spins.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has real fly/monitor-style runs that do this "expose while
    #   the stage moves" idea INSIDE the RunEngine, so the image + angle + beam are recorded
    #   together automatically. Depending on the goal, use a proper monitored/time-series acquire
    #   (e.g. time_series_run / kinetics_run) or a rocking acquire built with acquire(...) + a
    #   motor_axis on the rotation stage — ask staff which fits, but let the RunEngine drive and
    #   record it rather than triggering the camera by hand. (internal: Tier 0.)
    # === end smi_plans note ================================================
    start = phi - 30
    stop = phi + 30

    acq_time = cycle * cycle_t

    yield from bps.mv(motor, start)
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


def SAXS_S_edge_allprs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a rocking/rotation SAXS scan — at a fixed energy it steps the rotation
    #   stage ('prs') through 1001 angles from -25 to +25 deg and takes a SAXS image at each
    #   (a rocking-curve / tomography-style sweep).
    # 💡 NEWER, EASIER WAY: rotation/tomography sweeps are 'smi_plans' territory. Either use the
    #   tomography preset, or sweep the rotation stage as a "motor axis" in one acquire — both
    #   record the angle/beam straight into each image:
    #     from smi_plans import tomography_run            # rotation about stage.phi
    #     # or: from smi_plans import acquire, motor_axis
    #     #     yield from acquire("s2_ai0.9deg", [pil2M],
    #     #                        [motor_axis("phi", stage.phi, np.linspace(1.275-25, 1.275+25, 1001))])
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' (the old rotation-stage name) no longer exists — it's
    #   now 'stage.phi'; (2) the 'det_exposure_time(...)' call no longer sets the exposure unless
    #   run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M]
    name = "s2_ai0.9deg"

    prs0 = 1.275
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_2450eV_sdd2.5m_prs{prs}_xbpm{xbpm}"

    for prs_pos in np.linspace(-25, 25, 1001):
        yield from bps.mv(prs, prs0 + prs_pos)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        yield from bps.sleep(1)

        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(
            sample=name, prs="%3.2f" % prs_pos, xbpm="%3.2f" % bpm
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


def giwaxs_S_edge_pag_2021_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant GIWAXS scan near the sulfur edge — for each sample it aligns,
    #   then for each WAXS arc walks the energy and (per energy) several incident angles, taking
    #   a WAXS image at each and stepping the energy back down.
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' GIWAXS + energy combination — align_sample
    #   aligns and saves the result, and you compose energy + incidence + arc axes into one
    #   acquire (per sample):
    #     from smi_plans import acquire, align_sample, energy_axis, incidence_axis, motor_axis
    #     yield from acquire(name, [pil900KW],
    #                        [motor_axis("wa", waxs, np.linspace(0,26,5)),
    #                         energy_axis([2450, 2475, ..., 2500]),
    #                         incidence_axis(piezo.th, ai0, [0.3, 0.5, 0.7, 1.5])],
    #                        align=align_sample)
    #   (records energy/angle/arc/position/beam into each image and manages the energy move — so
    #    you can drop the per-step sleeps and the walk-back. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    names = ["pag0_redo", "pag20", "pag40"]
    x = [44000, 28000, 5000]

    energies = [
        2450,
        2475,
        2476,
        2477,
        2478,
        2479,
        2480,
        2481,
        2482,
        2483,
        2484,
        2490,
        2500,
    ]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    name_fmt = "{sample}_{energy}eV_pos{posi}_wa{wa}_xbpm{xbpm}"

    waxs_range = np.linspace(0, 39, 7)
    ai0 = 0

    for name, xs in zip(names, x):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.th, ai0)

        waxs_range = np.linspace(0, 26, 5)

        # yield from bps.mv(GV7.open_cmd, 1 )
        # yield from bps.sleep(1)
        # yield from bps.mv(GV7.open_cmd, 1 )
        # yield from bps.sleep(1)

        yield from alignement_gisaxs(angle=0.4)

        # yield from bps.mv(GV7.close_cmd, 1 )
        # yield from bps.sleep(1)
        # yield from bps.mv(GV7.close_cmd, 1 )
        # yield from bps.sleep(1)

        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            for k, e in enumerate(energies):
                yield from bps.mv(piezo.x, xs - k * 300)
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

                name_fmt = "{sample}_2.8m_ai{ai}_{energy}eV_xbpm{xbpm}_wa{wa}"

                for j, aiss in enumerate([0.3, 0.5, 0.7, 1.5]):
                    yield from bps.mv(piezo.th, ai0 + aiss)

                    sample_name = name_fmt.format(
                        sample=name,
                        ai="%1.2f" % aiss,
                        energy=e,
                        xbpm="%3.1f" % xbpm3.sumY.value,
                        wa="%2.1f" % wa,
                    )
                    sample_id(user_name="OS", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)


def ex_situ_nexafsznedge_2021_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS bar across the zinc edge (~9640->9750 eV, fine near the edge) —
    #   for each sample it aligns, then sweeps the energy taking a WAXS image + beam reading at
    #   each, then steps the energy back down. Gate-valve handling wraps the alignment.
    # 💡 NEWER, EASIER WAY: running a NEXAFS energy sweep on each sample of a bar is the
    #   'smi_plans' energy-scan + bar combination — nexafs_bar takes a SampleList, aligns each
    #   sample, and runs the sweep, recording the energy/position/beam into each image:
    #     from smi_plans import nexafs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     energies = np.r_[np.arange(9640,9660,5), np.arange(9660,9680,0.5),
    #                      np.arange(9680,9700,1), np.arange(9700,9720,2), np.arange(9720,9750,2)]
    #     yield from nexafs_bar("SR", samples, energies=energies, t=t, dets=[pil900KW],
    #                           align=align_sample)
    #   (manages the energy move + beam feedback, so you can drop the per-step and walk-back
    #    sleeps. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(2)
    yield from bps.mv(GV7.close_cmd, 1)

    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_range = [65]

    # energies = np.linspace(9640, 9720, 81)
    energies = (
        np.arange(9640, 9660, 5).tolist()
        + np.arange(9660, 9680, 0.5).tolist()
        + np.arange(9680, 9700, 1).tolist()
        + np.arange(9700, 9720, 2).tolist()
        + np.arange(9720, 9750, 2).tolist()
    )

    samples = [
        "SnZ_redo",
        "SbZ",
        "SPZ",
        "PZ",
        "Sn_exp_Z",
        "Sb_exp_Z",
        "SP_exp_Z",
        "PZ_exp",
    ]
    x_list = [15000, 6000, -3000, -14000, -21000, -28000, -39000, -47000]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        for sam, x in zip(samples, x_list):
            yield from bps.mv(piezo.x, x)

            yield from bps.mv(GV7.open_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(GV7.open_cmd, 1)
            yield from bps.sleep(1)

            yield from alignement_gisaxs(angle=0.4)

            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(GV7.close_cmd, 1)
            yield from bps.sleep(1)

            ai0 = piezo.th.position
            yield from bps.mv(piezo.th, ai0 + 0.2)

            for k, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

                name_fmt = "nexafs_ai0.2deg_{sam}_{energy}eV_wa{waxs}_bpm{bpm}"

                bpm1 = xbpm3.sumX.value
                sample_name = name_fmt.format(
                    sam=sam, energy=e, waxs="%2.1f" % wa, bpm="%1.3f" % bpm1
                )
                sample_id(user_name="SR", sample_name=sample_name)
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 9730)  # 💡 smi_plans: you can drop this stepped energy walk-back (and the sleeps after it) — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 9710)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 9685)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 9660)
            yield from bps.sleep(2)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def ex_situ_saxsnexafsznedge_2021_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS scan near the zinc edge — for one sample it aligns, then
    #   walks the energy while stepping x (a fresh spot per energy), taking SAXS+WAXS images and
    #   stepping the energy back down at the end.
    # 💡 NEWER, EASIER WAY:  from smi_plans import acquire, align_sample, energy_axis, motor_axis
    #     energies = np.r_[np.arange(9640,9660,5), np.arange(9660,9680,0.5),
    #                      np.arange(9680,9700,1), np.arange(9700,9720,2)]
    #     yield from acquire("PZ", [pil2M, pil900KW],
    #                        [energy_axis(energies), motor_axis("x", piezo.x, xss)],
    #                        align=align_sample)
    #   (records energy/position/beam into each image and manages the energy move — so you can
    #    drop the per-step sleep and the walk-back. Use pil900KW for WAXS — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 💡 lines are scaffolding.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Detectors, motors:
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_range = [65]

    energies = (
        np.arange(9640, 9660, 5).tolist()
        + np.arange(9660, 9680, 0.5).tolist()
        + np.arange(9680, 9700, 1).tolist()
        + np.arange(9700, 9720, 2).tolist()
    )

    # samples = [  'M', 'MA', 'MAZ', 'MAZm',    'P',   'PA',  'PAZ', 'PAZm']
    # x_list  = [17500, 6500, -2500, -13500, -21500, -30000, -39000, -48000]

    samples = ["PZ"]
    x_list = [26000]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        for sam, x in zip(samples, x_list):
            yield from bps.mv(piezo.x, x)

            yield from alignement_gisaxs(angle=0.4)

            ai0 = piezo.th.position

            yield from bps.mv(piezo.th, ai0 + 0.18)
            xss = np.linspace(x, x - 3000, 74)

            for k, (e, xs) in enumerate(zip(energies, xss)):
                yield from bps.mv(energy, e)
                yield from bps.mv(piezo.x, xs)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

                name_fmt = "{sam}_ai0.18_sdd5m_{energy}eV_wa{waxs}_bpm{bpm}"

                bpm1 = xbpm3.sumX.value
                sample_name = name_fmt.format(
                    sam=sam, energy=e, waxs="%2.1f" % wa, bpm="%1.3f" % bpm1
                )
                sample_id(user_name="NT", sample_name=sample_name)
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 9710)  # 💡 smi_plans: you can drop this stepped energy walk-back (and the sleeps after it) — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 9685)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 9660)
            yield from bps.sleep(2)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def night_nikhil(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 2D raster — scans piezo.y x piezo.x over a grid (snaking), reading the
    #   detector at each point (e.g. a microfocus map).
    # 💡 NEWER, EASIER WAY: grid/line/spiral maps are 'smi_plans' map runs, which record the
    #   x/y position and beam into each point automatically and fill the file name for you:
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run("nikhil_map", dets=[fd],
    #                             y=(-225, 225, 101), x=(-280, 280, 17), snake=True)
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 2.)
    # === end smi_plans note ================================================

    # yield from ex_situ_saxsnexafsznedge_2021_2(t=t)
    # yield from bps.sleep(5)

    # yield from ex_situ_nexafsznedge_2021_2(t=t)
    # yield from bps.sleep(5)

    x_range = [-280, 280, 17]
    y_range = [-225, 225, 101]
    dets = [fd]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.rel_grid_scan(
        dets, piezo.y, *y_range, piezo.x, *x_range, 1
    )  # 1 = snake, 0 = not-snake

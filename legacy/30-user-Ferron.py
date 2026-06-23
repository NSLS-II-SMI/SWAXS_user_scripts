def xrr_spol_waxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy reflectivity / grazing-incidence angle scan
    #   (s-pol) on a few samples — aligns each, then for each WAXS arc and energy it walks
    #   the incident angle through clusters (changing attenuators between clusters) and
    #   images at each angle.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has reflectivity/grazing presets that build the
    #   incident-angle list, manage attenuators, and record angle/energy/beam INTO each
    #   file. The energy sweep also handles the beam feedback for you:
    #
    #     from smi_plans import xrr_run, incidence_axis, energy_axis
    #     # xrr_run does the angle sweep with attenuator handling; incidence_axis(th0, ais)
    #     # builds the angle list; energy_axis(energies) is the energy sweep.
    #     # For grazing-incidence specifically see giwaxs_run / align_sample.
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    # names =  [ 'ps_ref', 'pss_ref', 'ps_pss_bilayer', 'y6_ref', 'n2200_ref', 'si_ref']
    # x_piezo = [   57000,     43000,            17000,    -8000,      -30000,   -40000]
    # x_hexa = [       12,         0,                0,        0,           0,      -14]
    # y_piezo = [    5500,      5500,             5500,     5500,        5500,     5500]
    # z_piezo = [       0,        0,                 0,        0,           0,        0]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 1).tolist()
        + np.arange(2480, 2490, 2).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    energies1 = (
        np.arange(2447, 2477, 5).tolist()
        + np.arange(2477, 2487, 1).tolist()
        + np.arange(2487, 2497, 2).tolist()
        + np.arange(2497, 2508, 5).tolist()
    )

    names = ["ps_pss_bilayer3", "n2200_pete", "y6"]
    x_piezo = [20000, 0, -15000]
    x_hexa = [0, 0, 0]
    y_piezo = [5500, 5500, 5500]
    z_piezo = [0, 0, 0]
    ener = [energies1, energies, energies]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        x_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(
        ener
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(ener)})"

    dets = [pil900KW]
    waxs_arc = [1]

    # #List of incident angles clustured in subsection for attenuators
    # ai_lists = [[np.linspace(0.03, 1.03, 51).tolist() + np.linspace(1.05,  2.01, 33).tolist()] + [np.linspace(2.01,  2.51, 26).tolist()] +
    # [np.linspace(0.51,  1.5, 34).tolist()] + [np.linspace(1.55, 4, 50).tolist()] + [np.linspace(4, 6, 41).tolist()] + [np.linspace(6, 8, 41).tolist()]]

    # ai_lists = [[np.linspace(0.03, 1.03, 51).tolist() + np.linspace(1.05,  2.01, 33).tolist()] + [np.linspace(2.01,  2.51, 26).tolist()] +
    # [np.linspace(0.87,  1.17, 11).tolist()] + [np.linspace(1.2,  1.5, 11).tolist()] + [np.linspace(1.55, 2.7, 24).tolist()] +
    # [np.linspace(2.75, 4, 26).tolist()] + [np.linspace(4, 6, 41).tolist()] + [np.linspace(6, 8, 41).tolist()]]

    ai_lists = [
        [np.linspace(0.03, 1.035, 68).tolist()]
        + [np.linspace(1.05, 2.01, 49).tolist()]
        + [np.linspace(2.01, 3.01, 51).tolist()]
    ]

    for name, xs, xs_hexa, zs, ys, eners in zip(
        names, x_piezo, x_hexa, z_piezo, y_piezo, ener
    ):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs.arc, wa)

            for energ in eners:
                yield from bps.mv(energy, energ)
                yield from bps.sleep(5)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
                yield from bps.mvr(piezo.x, -300)

                # ai_list should be a list of list. No change of attenuation inside one list
                for k, ai_list in enumerate(ai_lists[0]):
                    ai_list = [round(1000 * x, 4) for x in ai_list]
                    ai_list = np.asarray(ai_list) / 1000
                    print(ai_list)

                    # yield from calc_absorbers(num=k)
                    absorbers, exp_time = yield from calc_absorbers_expt(num=k)

                    # iterate over the angle stored in one list
                    for l, ais in enumerate(ai_list):
                        yield from bps.mv(piezo.th, ai0 + ais)
                        yield from bps.sleep(0.5)

                        det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                        bpm = xbpm3.sumX.get()
                        name_fmt = "{sample}_aiscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                        sample_name = name_fmt.format(
                            sample=name,
                            energy="%4.2f" % energ,
                            angle="%4.3f" % ais,
                            waxs="%2.1f" % wa,
                            absorber=absorbers,
                            bpm="%2.3f" % bpm,
                            time="%1.1f" % exp_time,
                        )

                        sample_id(user_name="TF", sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")  # Duplicate the
                        yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
            yield from bps.mv(energy, 2450)
        yield from bps.mv(piezo.th, ai0)

    yield from bps.mv(waxs, 0)


def xrr_ppol_waxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy reflectivity angle scan (p-pol) — aligns each
    #   sample, then for each energy walks the incident angle (here via the rotation
    #   stage) through attenuator clusters, imaging at each angle.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_run' builds the angle sweep + attenuator
    #   handling and records angle/energy/beam INTO each file; the rotation is just a
    #   recorded axis, and the energy sweep manages the beam feedback for you:
    #
    #     from smi_plans import xrr_run, incidence_axis, motor_axis, energy_axis
    #     # the rotation that used to be 'prs' is now 'stage.phi', e.g.
    #     #   motor_axis("phi", stage.phi, angle_list)   # recorded rotation axis
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses 'prs' (the old rotation stage, now
    #   'stage.phi') and 'det_exposure_time(...)' is now a plan — see the ⚠️ notes on
    #   those lines.
    # === end smi_plans note ================================================
    # names =  ['PSS70_ver', 'Y6_ver']
    # x_piezo = [      -900,     -900]
    # y_piezo = [     -2000,    -7000]
    # y_hexa =  [         0,       -8]
    # z_piezo = [      2000,     2000]
    # ener =    [[2450, 2485], [2450, 2475, 2476.5, 2477, 2477.5, 2478, 2483, 2500]]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 1).tolist()
        + np.arange(2480, 2490, 2).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    energies1 = (
        np.arange(2447, 2477, 5).tolist()
        + np.arange(2477, 2487, 1).tolist()
        + np.arange(2487, 2497, 2).tolist()
        + np.arange(2497, 2508, 5).tolist()
    )
    energies2 = np.arange(2486, 2490, 2).tolist() + np.arange(2490, 2501, 5).tolist()

    # ener =    [energies2, energies, energies]
    # names =  [ 'ps_ver', 'y6_ver', 'n2200_ver']
    # x_piezo = [     500,      500,         500]
    # y_piezo = [   -6000,    -2500,        4000]
    # y_hexa =  [      -3,        0,           0]
    # z_piezo = [    2000,     2000,        2000]

    ener = [energies2]
    names = ["n2200_ver"]
    x_piezo = [500]
    y_piezo = [4000]
    y_hexa = [0]
    z_piezo = [2000]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        y_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_hexa)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(
        ener
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(ener)})"

    dets = [pil900KW]
    waxs_arc = [3]

    ai_lists = [
        [np.linspace(0.03, 1.035, 68).tolist()]
        + [np.linspace(1.05, 2.01, 49).tolist()]
        + [np.linspace(2.01, 3.01, 51).tolist()]
    ]
    ai_lists2 = [
        [np.linspace(0.03, 1.035, 68).tolist()] + [np.linspace(1.05, 2.01, 49).tolist()]
    ]

    ai_list_list = [ai_lists]  # , ai_lists2, ai_lists]

    for name, xs, zs, ys, ys_hexa, eners, ai_li in zip(
        names, x_piezo, z_piezo, y_piezo, y_hexa, ener, ai_list_list
    ):

        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(2)

        yield from alignement_xrr(angle=0.15)
        ai0 = prs.position  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(2)

        for energ in eners:
            yield from bps.mv(energy, energ)
            yield from bps.sleep(5)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
            yield from bps.mvr(piezo.y, -30)

            # ai_list should be a list of list. No change of attenuation inside one list
            for k, ai_list in enumerate(ai_li[0]):
                ai_list = [round(1000 * x, 4) for x in ai_list]
                ai_list = np.asarray(ai_list) / 1000
                print(ai_list)

                absorbers, exp_time = yield from calc_absorbers_expt(num=k)
                if k == 0:
                    yield from bps.mv(waxs.arc, 3)
                elif k == 1:
                    yield from bps.mv(waxs.arc, 5)
                else:
                    yield from bps.mv(waxs.arc, 7)

                # iterate over the angle stored in one list
                for l, ais in enumerate(ai_list):

                    # check if negative is the good direction
                    yield from bps.mv(prs, ai0 - ais)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

                    # How to move waxs => reste / quotien of ais
                    # yield from bps.mv(waxs.arc, waxs_arc[0] + 2*ais)
                    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                    bpm = xbpm3.sumX.get()
                    name_fmt = "{sample}_aiscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%4.2f" % energ,
                        angle="%4.3f" % ais,
                        waxs="%2.1f" % (waxs_arc[0]),  #'%2.1f'%(waxs_arc[0] + 2*ais)
                        absorber=absorbers,
                        bpm="%2.3f" % bpm,
                        time="%1.1f" % exp_time,
                    )

                    sample_id(user_name="TF", sample_name=sample_name)
                    yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2470)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        yield from bps.mv(energy, 2450)
        yield from bps.mv(prs, ai0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


def calc_absorbers_expt(num):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small helper that picks an attenuator combination + exposure
    #   time for cluster number 'num' (used by the XRR angle scans to keep counts on
    #   scale as the reflectivity drops). The attenuators (att2_*) are unchanged.
    #
    # 💡 smi_plans CONTEXT: in smi_plans this kind of "choose attenuators + exposure per
    #   angle cluster" is handled inside the reflectivity presets (xrr_run) and the
    #   attenuator helpers, so you usually don't hand-write a ladder like this.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls here are now plans —
    #   see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    print("num", num)
    if num == 0:
        yield from bps.mv(att2_10.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_11.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_10.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_11.open_cmd, 1)
        yield from bps.sleep(1)

        det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (smi_plans' xrr/nexafs presets set exposure via t=.)

        return "1", 0.5

    if num == 1:
        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "1", 1

    if num == 2:
        # yield from bps.mv(att2_10.open_cmd, 1)
        # yield from bps.sleep(1)
        # yield from bps.mv(att2_11.close_cmd, 1)
        # yield from bps.sleep(1)
        # yield from bps.mv(att2_10.open_cmd, 1)
        # yield from bps.sleep(1)
        # yield from bps.mv(att2_11.close_cmd, 1)
        # yield from bps.sleep(1)
        det_exposure_time(3, 3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(3, 3)  — or at the prompt:  RE(det_exposure_time(3, 3)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "1", 3

    if num == 3:
        det_exposure_time(0.2, 0.2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.2, 0.2)  — or at the prompt:  RE(det_exposure_time(0.2, 0.2)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 0.2

    if num == 4:
        det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 0.5

    if num == 5:
        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 1

    if num == 6:
        det_exposure_time(2, 2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(2, 2)  — or at the prompt:  RE(det_exposure_time(2, 2)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 2

    if num == 7:
        det_exposure_time(5, 5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(5, 5)  — or at the prompt:  RE(det_exposure_time(5, 5)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 5


def nexafs_Ferron(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender NEXAFS at a fixed grazing angle — for each sample it
    #   aligns, sets attenuators, then steps the X-ray energy across the edge and images
    #   at each energy.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'nexafs_run' sweeps energy in one call and records
    #   energy + beam INTO each file, managing the beam feedback + settling (so the
    #   per-step sleep and end step-down become unnecessary):
    #
    #     from smi_plans import nexafs_run, energy_axis
    #     # nexafs_run("nexafs_y6_ref2", energies, t=t, dets=[pil900KW], geometry="reflection")
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    dets = [pil900KW]

    # names =  [ 'ps_ref', 'pss_ref', 'ps_pss_bilayer', 'y6_ref', 'n2200_ref', 'si_ref']
    # x_piezo = -10000 + np.asarray([   57000,     43000,            17000,    -8000,      -30000,   -40000])
    # x_hexa = [       12,         0,                0,        0,           0,      -14]
    # y_piezo = [    5500,      5500,             5500,     5500,        5500,     5500]
    # z_piezo = [       0,        0,                 0,        0,           0,        0]

    names = ["y6_ref2"]
    x_piezo = [-15000]
    x_hexa = [0]
    y_piezo = [5500]
    z_piezo = [0]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    energies1 = (
        np.arange(2447, 2477, 5).tolist()
        + np.arange(2477, 2487, 0.5).tolist()
        + np.arange(2487, 2497, 1).tolist()
        + np.arange(2497, 2508, 5).tolist()
    )
    eners = [energies]

    ai = [1.5]

    for name, x, ener in zip(names, x_piezo, eners):
        yield from bps.mv(piezo.x, x)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        name_fmt = "nexafs_{sample}_wa40_{energy}eV_angle{ai}_bpm{xbpm}"

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

        for ais in ai:
            yield from bps.mv(piezo.th, ai0 + ais)

            for e in ener:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                bpm = xbpm3.sumX.value

                sample_name = name_fmt.format(
                    sample=name,
                    energy="%6.2f" % e,
                    ai="%2.2d" % ais,
                    xbpm="%4.3f" % bpm,
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)

        yield from bps.mv(energy, 2470)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        yield from bps.mv(energy, 2450)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)


def nexafs_Ferron_vertical(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender NEXAFS in the vertical (p-pol) geometry — aligns each
    #   sample using the rotation stage, sets attenuators, then steps the energy across
    #   the edge and images at each energy.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'nexafs_run' sweeps energy in one call and records
    #   energy + beam INTO each file, managing the beam feedback + settling. The rotation
    #   that used to be 'prs' is now 'stage.phi' (a recorded axis):
    #
    #     from smi_plans import nexafs_run, motor_axis
    #     # motor_axis("phi", stage.phi, ...) for the rotation; nexafs_run for the sweep.
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses 'prs' (the old rotation stage, now
    #   'stage.phi') and 'det_exposure_time(...)' is now a plan — see the ⚠️ notes.
    # === end smi_plans note ================================================
    dets = [pil900KW]

    waxs_arc = [40]
    ai = [1.5]
    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 1).tolist()
        + np.arange(2480, 2490, 2).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    energies1 = (
        np.arange(2447, 2477, 5).tolist()
        + np.arange(2477, 2487, 1).tolist()
        + np.arange(2487, 2497, 2).tolist()
        + np.arange(2497, 2508, 5).tolist()
    )

    ener = [energies, energies, energies]

    # names =  [ 'ps_ver', 'y6_ver', 'n2200_ver']
    # x_piezo = [     500,      500,         500]
    # y_piezo = [   -6000,    -2500,        4000]
    # y_hexa =  [      -3,        0,           0]
    # z_piezo = [    2000,     2000,        2000]

    names = ["y6_ver"]
    x_piezo = [500]
    y_piezo = [-2500]
    y_hexa = [0]
    z_piezo = [2000]

    for name, x, y, ys_hexa, ene in zip(names, x_piezo, y_piezo, y_hexa, ener):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(stage.y, ys_hexa)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        name_fmt = "nexafs_{sample}_{energy}eV_angle{ai}_bpm{xbpm}"

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_xrr(angle=0.15)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(2)
        yield from bps.mv(GV7.close_cmd, 1)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = prs.position  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

        for ais in ai:
            yield from bps.mv(prs, ai0 - ais)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            for e in ene:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                bpm = xbpm3.sumX.value

                sample_name = name_fmt.format(
                    sample=name,
                    energy="%6.2f" % e,
                    ai="%2.2d" % ais,
                    xbpm="%4.3f" % bpm,
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(prs, ai0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

        yield from bps.mv(energy, 2470)
        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        yield from bps.mv(energy, 2450)
        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)


def xrr_spol_saxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single-energy reflectivity / grazing-incidence angle scan in
    #   SAXS — sets the angle, then walks the incident angle through attenuator clusters,
    #   imaging at each angle (no energy sweep here).
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_run' builds the incident-angle sweep with
    #   attenuator handling and records angle/energy/beam INTO each file:
    #
    #     from smi_plans import xrr_run, incidence_axis   # incidence_axis(th0, ais) = angles
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    names = ["PS_test9_saxs"]
    x_piezo = [34800]
    y_piezo = [6570]
    z_piezo = [3000]
    ener = 2450.0

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    dets = [pil2M]
    waxs_arc = [13]

    # #List of incident angles clustured in subsection for attenuators
    # ai_lists = [[np.linspace(0.03, 0.3, 10).tolist()] + [np.linspace(0.21, 0.51, 11).tolist()] +
    # [np.linspace(0.42, 0.99, 20).tolist()] + [np.linspace(0.87,  1.5, 22).tolist() + [1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05, 2.1]] +
    # [np.linspace(1.8, 10, 165).tolist()]]
    # #[np.linspace(1.8, 4.2, 49).tolist()] + [np.linspace(4,  10, 121).tolist()]]

    # ai_lists = [[np.linspace(0.03, 0.51, 17).tolist()] + [np.linspace(0.21, 0.99, 27).tolist()] +
    # [np.linspace(0.42, 1.5, 37).tolist()] + [np.linspace(0.87,  1.5, 22).tolist() + np.linspace(1.55,  4, 50).tolist()]
    # + [np.linspace(1.8, 10, 165).tolist()]]

    ai_lists = [[np.linspace(0.03, 0.99, 65).tolist()]]

    for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, -2.085)
        # yield from alignement_gisaxs(angle = 0.5)
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs.arc, wa)

            # ai_list should be a list of list. No change of attenuation inside one list
            for k, ai_list in enumerate(ai_lists[0]):

                # yield from calc_absorbers(num=k)
                absorbers, exp_time = yield from calc_absorbers_expt(num=k)

                # iterate over the angle stored in one list
                for l, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)
                    yield from bps.sleep(0.5)

                    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                    bpm = xbpm3.sumX.value
                    name_fmt = "{sample}_aiscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%4.2f" % ener,
                        angle="%4.3f" % ais,
                        waxs="%2.1f" % wa,
                        absorber=absorbers,
                        bpm="%2.3f" % bpm,
                        time="%1.1f" % exp_time,
                    )

                    sample_id(user_name="TF", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")  # Duplicate the

                    yield from bp.count(dets, num=1)


def refl_ener_scan_spol_waxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant reflectivity energy scan (s-pol) over a bar — aligns
    #   each sample, then at a couple of fixed incident angles steps the energy across
    #   the edge and images at each energy.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_resonant_run' does resonant reflectivity
    #   (energy sweep at fixed angle) and records angle/energy/beam INTO each file,
    #   managing the beam feedback + settling:
    #
    #     from smi_plans import xrr_resonant_run, energy_axis, incidence_axis
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    names = [
        "PM6_ref",
        "PS_50",
        "Bilayer_ref",
        "BCP_MT",
        "BCP_TM",
        "BCP_MS",
        "BCP_SM",
        "homo_T",
        "homo_S",
        "Y6_ref",
    ]
    x_piezo = [54000, 42000, 30500, 22500, 8500, -5500, -17500, -29500, -40500, -48500]
    y_piezo = [6570, 6570, 6570, 6570, 6570, 6570, 6570, 6570, 6570, 6570]
    z_piezo = [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000]

    ener = [
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2480, 10).tolist()
        + np.arange(2483, 2487, 0.5).tolist()
        + np.arange(2487, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2480, 10).tolist()
        + np.arange(2483, 2487, 0.5).tolist()
        + np.arange(2487, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2480, 10).tolist()
        + np.arange(2483, 2487, 0.5).tolist()
        + np.arange(2487, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2472, 2482, 0.5).tolist()
        + np.arange(2482, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist(),
    ]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(
        ener
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(ener)})"

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    waxs_arc = [1]

    ai_list = [0.4, 1]

    for name, xs, zs, ys, eners in zip(names, x_piezo, z_piezo, y_piezo, ener):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs.arc, wa)

            for k, ai in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                yield from bps.sleep(0.5)

                yield from bps.mv(att2_11.open_cmd, 1)
                yield from bps.sleep(1)
                yield from bps.mv(att2_11.open_cmd, 1)
                yield from bps.sleep(1)

                det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                for energ in eners:
                    yield from bps.mv(energy, energ)
                    yield from bps.sleep(1)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                    bpm = xbpm3.sumX.value
                    name_fmt = "{sample}_energyscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%4.2f" % energ,
                        angle="%4.3f" % ais,
                        waxs="%2.1f" % wa,
                        absorber=absorbers,
                        bpm="%2.3f" % bpm,
                        time="%1.1f" % exp_time,
                    )

                    sample_id(user_name="TF", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")  # Duplicate the
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2470)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
                yield from bps.mv(energy, 2450)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        yield from bps.mv(piezo.th, ai0)


def refl_ener_scan_ppol_waxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant reflectivity energy scan (p-pol) — at a couple of
    #   incident angles (set via the rotation stage) it steps the energy across the edge
    #   and images at each energy.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_resonant_run' does the energy sweep at fixed
    #   angle and records angle/energy/beam INTO each file. The rotation that used to be
    #   'prs' is now 'stage.phi' (a recorded axis), and the energy sweep manages feedback:
    #
    #     from smi_plans import xrr_resonant_run, motor_axis, energy_axis
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡-tagged
    #    energy waits/step-downs become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses 'prs' (now 'stage.phi'), the detector list
    #   uses 'pil300KW' (removed), and 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    names = ["PM6_ver"]
    x_piezo = [-900]
    y_piezo = [4000]
    y_hexa = [0]
    z_piezo = [2000]
    ener = [
        np.arange(2445, 2470, 10).tolist()
        + np.arange(2470, 2480, 0.5).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    ]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(
        ener
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(ener)})"

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    waxs_arc = [1]

    ai_list = [0.4, 1]

    for name, xs, zs, ys, ys_hexa, eners in zip(
        names, x_piezo, z_piezo, y_piezo, y_hexa, ener
    ):
        # yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)

        # yield from alignement_gisaxs(angle = 0.15)
        ai0 = prs.position  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

        for k, ais in enumerate(ai_list):
            # check if negative is the good direction
            yield from bps.mv(prs, ai0 - ais)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            # How to move waxs => reste / quotien of ais
            yield from bps.mv(waxs.arc, waxs_arc[0] + 2 * ais)

            yield from bps.mv(att2_11.open_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att2_11.open_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att2_10.close_cmd, 1)
            yield from bps.sleep(1)
            yield from bps.mv(att2_10.close_cmd, 1)
            yield from bps.sleep(1)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' xrr/nexafs presets set exposure via t=.)

            for energ in eners:
                yield from bps.mv(energy, energ)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                bpm = xbpm3.sumX.value
                name_fmt = "{sample}_energyscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                sample_name = name_fmt.format(
                    sample=name,
                    energy="%4.2f" % energ,
                    angle="%4.3f" % ais,
                    waxs="%2.1f" % (waxs_arc[0] + 2 * ais),
                    absorber="2",
                    bpm="%2.3f" % bpm,
                    time="%1.1f" % t,
                )

                sample_id(user_name="TF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
            yield from bps.mv(energy, 2450)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        yield from bps.mv(prs, ai0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


def xrr_spol_waxs_smallstep_pedge(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a fine-step reflectivity angle scan near the phosphorus edge —
    #   aligns each sample, then for each energy (reached by manually stepping in ≤10 eV
    #   hops) walks the incident angle through attenuator clusters, imaging at each.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_run' / 'xrr_resonant_run' build the angle and
    #   energy sweeps with attenuator handling and record angle/energy/beam INTO each
    #   file. Importantly, the hand-rolled "step the energy in ≤10 eV hops" loop is no
    #   longer needed — move_energy_fb/energy_axis already step in ≤50 eV hops with
    #   settling and beam feedback:
    #
    #     from smi_plans import xrr_run, energy_axis, move_energy_fb
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡-tagged
    #    energy-stepping/waits become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names = ["homo_P", "BCP_M9", "BCP_PM1", "homo_M"]
    x_piezo = [-10000, -23000, -38000, -52000]
    y_piezo = [6570, 6570, 6570, 6570]
    z_piezo = [2000, 2000, 2000, 2000]

    ener = [
        [2140, 2152, 2155, 2156, 2190],
        [2140, 2152, 2155, 2156, 2190],
        [2140, 2152, 2155, 2156, 2190],
        [2140, 2152, 2155, 2156, 2190],
    ]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(
        ener
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(ener)})"

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    waxs_arc = [1]

    # #List of incident angles clustured in subsection for attenuators
    ai_lists = [
        [np.linspace(0.03, 1.03, 101).tolist() + np.linspace(1.05, 2.01, 65).tolist()]
        + [np.linspace(2.01, 2.51, 51).tolist()]
        + [np.linspace(0.87, 1.5, 43).tolist()]
        + [np.linspace(1.55, 4, 99).tolist()]
        + [np.linspace(4, 6, 81).tolist()]
        + [np.linspace(6, 7, 41).tolist()]
    ]

    for name, xs, zs, ys, eners in zip(names, x_piezo, z_piezo, y_piezo, ener):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs.arc, wa)

            for energ in eners:
                while abs(energy.energy.position - energ) > 10:
                    if energ > energy.energy.position:
                        yield from bps.mv(energy, energy.energy.position + 10)
                    else:
                        yield from bps.mv(energy, energy.energy.position - 10)
                    yield from bps.sleep(5)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                yield from bps.mv(energy, energ)
                yield from bps.sleep(5)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
                yield from bps.mvr(piezo.x, -200)

                # ai_list should be a list of list. No change of attenuation inside one list
                for k, ai_list in enumerate(ai_lists[0]):
                    ai_list = [round(1000 * x, 4) for x in ai_list]
                    ai_list = np.asarray(ai_list) / 1000
                    print(ai_list)

                    # yield from calc_absorbers(num=k)
                    absorbers, exp_time = yield from calc_absorbers_expt(num=k)

                    # iterate over the angle stored in one list
                    for l, ais in enumerate(ai_list):
                        yield from bps.mv(piezo.th, ai0 + ais)
                        yield from bps.sleep(0.5)

                        det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                        bpm = xbpm3.sumX.value
                        name_fmt = "{sample}_aiscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                        sample_name = name_fmt.format(
                            sample=name,
                            energy="%4.2f" % energ,
                            angle="%4.3f" % ais,
                            waxs="%2.1f" % wa,
                            absorber=absorbers,
                            bpm="%2.3f" % bpm,
                            time="%1.1f" % exp_time,
                        )

                        sample_id(user_name="TF", sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")  # Duplicate the
                        yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)


def xrr_spol_waxs_hardxray(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a hard-X-ray reflectivity angle scan at fixed energy — walks the
    #   incident angle through attenuator clusters (using the hard-X-ray attenuator
    #   helper), imaging at each angle.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'xrr_run' builds the angle sweep with attenuator
    #   handling and records angle/energy/beam INTO each file:
    #
    #     from smi_plans import xrr_run, incidence_axis   # incidence_axis(th0, ais) = angles
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list uses 'pil300KW' (removed), and
    #   'det_exposure_time(...)' is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names = ["BCP_MT_new"]
    x_piezo = [-19000]
    y_piezo = [6902]
    z_piezo = [1000]

    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(
        y_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(
        z_piezo
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (it's a different camera, so check beam-center/calibration).
    waxs_arc = [1]

    # #List of incident angles clustured in subsection for attenuators
    # ai_lists = [[np.linspace(0.03, 1.03, 51).tolist() + np.linspace(1.05,  2.01, 33).tolist()] + [np.linspace(2.01,  2.51, 26).tolist()] +
    # [np.linspace(0.51,  1.5, 34).tolist()] + [np.linspace(1.55, 4, 50).tolist()] + [np.linspace(4, 6, 41).tolist()] + [np.linspace(6, 8, 41).tolist()]]

    ai_lists = [
        [np.linspace(0.03, 0.43, 81).tolist()]
        + [np.linspace(0.2, 0.8, 121).tolist()]
        + [np.linspace(0.6, 1.4, 161).tolist()]
    ]

    for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        # yield from alignement_gisaxs(angle = 0.1)
        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs.arc, wa)

            # ai_list should be a list of list. No change of attenuation inside one list
            for k, ai_list in enumerate(ai_lists[0]):
                ai_list = [round(1000 * x, 4) for x in ai_list]
                ai_list = np.asarray(ai_list) / 1000
                print(ai_list)

                # yield from calc_absorbers(num=k)
                absorbers, exp_time = yield from calc_absorbers_hard(num=k)

                # iterate over the angle stored in one list
                for l, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)
                    yield from bps.sleep(0.5)

                    det_exposure_time(exp_time, exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' xrr/nexafs presets set exposure via t=.)

                    bpm = xbpm3.sumX.value
                    name_fmt = "{sample}_aiscan_{energy}keV_ai{angle}deg_wa{waxs}_abs{absorber}_bpm{bpm}_time{time}"
                    sample_name = name_fmt.format(
                        sample=name,
                        energy="%4.2f" % 16100,
                        angle="%4.3f" % ais,
                        waxs="%2.1f" % wa,
                        absorber=absorbers,
                        bpm="%2.3f" % bpm,
                        time="%1.1f" % exp_time,
                    )

                    sample_id(user_name="TF", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")  # Duplicate the
                    yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)


def calc_absorbers_hard(num):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the hard-X-ray version of the attenuator+exposure helper — picks an
    #   att1_* foil combination + exposure for cluster 'num'. The attenuators are unchanged.
    #   In smi_plans this attenuator/exposure laddering is handled inside xrr_run.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls here are now plans —
    #   see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    print("num", num)
    if num == 0:
        yield from bps.mv(att1_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_7.open_cmd, 1)
        yield from bps.sleep(1)

        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)

        return "1", 1

    if num == 1:
        yield from bps.mv(att1_5.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_5.close_cmd, 1)
        yield from bps.sleep(1)
        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "2", 1

    if num == 2:
        yield from bps.mv(att1_7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)
        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "3", 1

    if num == 3:
        yield from bps.mv(att1_5.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_5.close_cmd, 1)
        yield from bps.sleep(1)
        det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (smi_plans' xrr/nexafs presets set exposure via t=.)
        return "4", 1

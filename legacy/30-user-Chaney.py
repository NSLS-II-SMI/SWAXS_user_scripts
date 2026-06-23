def giwaxs_chaney_2021_3(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence WAXS (GIWAXS) run over a bar of samples — for each sample
    #   it moves there (hexapod + piezo), runs the alignment routine, then for each WAXS arc steps a
    #   couple of incident angles and takes a WAXS image.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' giwaxs_bar loops your samples, aligns each one and SAVES the
    #   alignment with the data, and sweeps the incident angle / WAXS arc while recording them (so
    #   you don't rebuild the "_ai{angl}deg_wa{waxs}" name by hand):
    #
    #     from smi_plans import giwaxs_bar, align_sample, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, z=z_piezo, x_hexa=x_hexa)
    #     yield from giwaxs_bar(
    #         samples, dets=[pil900KW], t=t,            # current WAXS detector — see ⚠️
    #         incident_angles=[0.11, 0.14],             # your angles, unchanged
    #         arc_angles=[10.6],                        # your WAXS arc, unchanged
    #         align=align_sample,                       # replaces the alignement_gisaxs call
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    # names = ['sam01', 'sam02', 'sam03', 'sam04', 'sam05', 'sam06', 'sam07', 'sam08', 'sam09', 'sam10', 'sam11', 'sam12', 'sam13',
    #          'sam14', 'sam15', 'sam17', 'sam18', 'sam19', 'sam20', 'sam21', 'sam22', 'sam23', 'sam24', 'sam25', 'sam26', 'sam27']
    # names = ['sam28', 'sam29', 'sam30', 'sam31', 'sam33', 'sam34', 'sam35', 'sam36', 'sam37', 'sam38', 'sam39', 'sam40', 'sam41',
    #          'sam42', 'sam43', 'sam44', 'sam45', 'sam46', 'sam47', 'sam50', 'sam51', 'sam52', 'sam53', 'sam54', 'sam55', 'sam56']
    # names = ['sam57', 'sam58', 'sam59', 'sam60', 'sam61', 'sam62', 'sam63', 'sam64', 'sam65', 'sam66', 'sam67', 'sam68', 'sam69',
    #          'sam70', 'sam73', 'sam74', 'sam77', 'sam78',    'S1',    'S2',   'S3',    'S4',   'S5']
    # names = [  'S6',    'S7',    'S8',    'S9',    'S10',   'S11',   'S12',   'S13',  'S14',  'S15' ]
    # names = [ 'JH-CGE',  'TT1',  'TT3',  'SC1',   'SC2',   'MO3',   'MO4',   'ZZ1']
    # names = [ '1MEO',   '1FS',  'N2200', '10MEO', '10FS',   '5FS',   '20MEO',  '20FS', '5MEO']

    names = ["T1", "T2", "O", "C2", "C1", "Wenhan1", "Wenhan2"]
    x_piezo = [51000, 48000, 38000, 26000, 14000, -6000, -17000]
    y_piezo = [7000, 7000, 7000, 7000, 7000, 7300, 7300]
    z_piezo = [2300, 2300, 2300, 2300, 2300, 2300, 2300]
    x_hexa = [9, 0, 0, 0, 0, 0, 0]

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
        x_hexa
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [10.6]
    angle = [0.11, 0.14]

    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, 0)

        yield from alignement_gisaxs(angle=0.11)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, an in enumerate(angle):
                yield from bps.mv(piezo.x, xs + 200)
                yield from bps.mv(piezo.th, ai0 + an)
                name_fmt = "{sample}_14keV_ai{angl}deg_wa{waxs}"
                sample_name = name_fmt.format(
                    sample=name, angl="%3.2f" % an, waxs="%2.1f" % wa
                )
                sample_id(user_name="PT", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)






def swaxs_S_edge_2024_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS/WAXS scan over a bar of samples across the sulfur edge — for
    #   each sample and WAXS arc, steps the energy (moving x/y a little each step to spread out beam
    #   damage) and takes a SAXS+WAXS image; also includes an up/down sweep section.
    #
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; it loops your samples
    #   and records the energy/beam into the data and the file name (so you don't rebuild the
    #   "_{energy}eV_wa{wax}_bpm{xbpm}" name), and the energy move was fixed so the per-energy sleeps
    #   and the beam re-seek 'if xbpm2.sumX < 50' blocks aren't needed:
    #
    #     from smi_plans import nexafs_bar, SampleList, energy_axis
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M],
    #                           updown=True)          # energy_axis(reverse_alternate=True) for up+down
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines (per-energy sleeps + beam re-seek) are
    #   scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = [ "Si3N4_membrane",  "To",    "CB", "PM7_10mg_To"]
    x = [                38900, 21600,    -400,        -19400]
    y = [                -8150, -8030,   -7450,         -7100] 

    names = [ "CB", "PM7_10mg_To"]
    x = [     -400,        -19400]
    y = [    -7450,         -7100] 


    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist()+[2530, 2500, 2470, 2445])
    
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys-200, ys + 200, 67)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            # yield from bps.mv(energy, 2500)
            # yield from bps.sleep(2)
            # yield from bps.mv(energy, 2480)
            # yield from bps.sleep(2)
            # yield from bps.mv(energy, 2445)
                

    names = [ "Updownsweep_PM7_10mg_To"]
    x = [       -19400]
    y = [         -7100] 

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    waxs_arc = [0]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys-300, ys + 300, 67)
        xss = np.array([xs + 200])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()


        yss1 = np.linspace(ys-300, ys + 300, 67)
        xss1 = np.array([xs - 200])

        yss1, xss1 = np.meshgrid(yss1, xss1)
        yss1 = yss1.ravel()
        xss1 = xss1.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)


            for e, xsss, ysss in zip(energies[::-1], xss1, yss1):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            # yield from bps.mv(energy, 2500)
            # yield from bps.sleep(2)
            # yield from bps.mv(energy, 2480)
            # yield from bps.sleep(2)
            # yield from bps.mv(energy, 2445)
                






def swaxs_S_edge_2024_liquidcell_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS/WAXS scan across the sulfur edge on liquid-cell samples — for
    #   each sample and WAXS arc, steps the energy and takes a SAXS+WAXS image.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; it loops your samples
    #   and records the energy/beam into the data and the file name (no hand-built name), and the
    #   energy move was fixed so the per-energy sleeps and 'if xbpm2.sumX < 50' re-seek aren't needed:
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = [ "PM7_1mg_CB_1", "PM7_10mg_CB_3", "PM6_10mg_CB_2", "PM7_1mg_CB_1"]
    x = [               36450,           17300,          -3830,         -35000]
    y = [               -7821,           -7700,          -7400,          -6750] 

    names = ["Y6_CB_1", "Y6BO_CB_1"]
    x = [        38000,       20300]
    y = [        -4140,       -4000]

    names = ["Si3N4_membrane"]
    x = [        4900]
    y = [        -3232]


    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist()+[2530, 2500, 2470, 2445])
    
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys-0, ys + 0, 67)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)

    
    names = ["Y6_CB_1", "Y6BO_CB_1"]
    x = [        38000,       20300]
    y = [        -4140,       -4000] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = [2445.0, 2460.0, 2476.5, 2477.0, 2477.5, 2478.0, 2478.5, 2479.0, 2479.5, 2485.0, 2550.0]
    
    det_exposure_time(10, 10)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(10, 10)  — or at the prompt:  RE(det_exposure_time(10, 10)). (The smi_plans technique runs set exposure for you via t=.)

    
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys-0, ys + 0, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)




def waxs_S_edge_chris_2024_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS/SAXS scan across the sulfur edge over two samples — for each
    #   sample and WAXS arc, steps the energy (moving y in step) and takes a WAXS+SAXS image.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; it records the
    #   energy/beam into the data and the file name, and the energy move was fixed so the per-energy
    #   sleeps and the 'if xbpm2.sumX < 50' re-seek aren't needed:
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = ["A1_08", "W2_04"]
    x = [      38500,   32800]
    y = [      -8000,   -7800] 


    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1500, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



def waxs_S_edge_chaney_2024_1(t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS/SAXS scan across the sulfur edge over a bar of transmission
    #   samples — for each sample and WAXS arc, steps the energy (moving y in step) and takes images.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; it records the
    #   energy/beam into the data and the file name, and the energy move was fixed so the per-energy
    #   sleeps and the 'if xbpm2.sumX < 50' re-seek aren't needed:
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = ["Trmsn_14", "Trmsn_17", "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35","Trmsn_01", "Trmsn_03"]
    x = [         43300,      37000,      31400,      25400,      19500,      13900,       7300,        1000,       -5000,     -11000,     -17300,     -23300,    -29500,     -35800]
    y = [          4500,       4600,       4700,       4800,       4700,       4900,       5000,        5100,        5200,       5100,       5000,       5100,      5200,       5300] 


    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



def run_2024_11_13_night(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight run-book — sets the proposal/folder and runs one resonant WAXS
    #   plan.
    # 💡 NEWER, EASIER WAY: once the plan it calls is migrated to 'smi_plans' (see its own note),
    #   this stays a simple wrapper. Nothing here is broken.
    # === end smi_plans note ================================================
    # proposal_id("2024_1", "000000_McNeil_02")
    # yield from waxs_S_edge_chris_2024_1(t=t)

    proposal_id("2024_1", "314903_Chaney_02")
    yield from waxs_S_edge_chaney_2024_1(t=t)


"""
    syringe pump
  



    vol = Cpt(EpicsSignal, "Val:Vol-SP",) 
    rate = Cpt(EpicsSignal, "Val:Rate-SP", )
    go = Cpt(EpicsSignal, "Cmd:Run-Cmd",)
    stop = Cpt(EpicsSignal, "Cmd:Stop-Cmd",)
    dia = Cpt(EpicsSignal, "Val:Dia-RB")
    dir = Cpt(EpicsSignal, "Val:Dir-Sel",) 

    Examples
    yield from bps.mv(syringe_pu.x3, 1)         # start pump
    yield from bps.sleep(2.5)                   # wait 2.5 seconds
    yield from bps.mv(syringe_pu.x4, 1)         # stop pump
    yield from bps.mv(syringe_pu.x1, 200)       # sets the volume to 200

    LThermal
    sample_id(user_name='Chaney', sample_name=f'{name_base}_{LThermal.temperature()}degC_{en}eV')
        RE.md['temp'] = LThermal.temperature()

    #examples

    LThermal.on() # turn on the heating

    LThermal.off(self): # turn off the heating

    LThermal.setTemperature(temperature): # sets the setpoint

    LThermal.setTemperatureRate(temperature_rate): # sets the rate

    LThermal.temperature() #reads back the current temperature

    LThermal.temperatureRate() # reads back the current temperature






"""

# example script from Eliot
# to run, in bluesky, it's RE(temp_snapshot(name_base='something')) for example
def temp_series(name_base='temp',temps = np.linspace(25,40,16),ramp=1, num=10, pump_delay=1,exp_time=1, hold_delay=120, dets=[pil900KW,pil2M]):   # function loop to bring linkam to temp, hold and measure
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature series with flowing liquid — ramps the Linkam stage ('LThermal')
    #   to each temperature, holds, parks the beamstop / inserts foils for alignment, then at each
    #   temperature takes a series of frames while GENTLY OSCILLATING the syringe pump back and forth
    #   (infuse/withdraw) so fresh sample is in the beam for every frame.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' helpers for both pieces:
    #   - the temperature ramp + hold is temperature_ramp_run / isothermal_kinetics_run (it drives
    #     the heater, records the temperature into the data, and waits for the hold for you, instead
    #     of the hand-rolled 'while not int(LThermal.status_code.get()) & 2: sleep' loop);
    #   - the syringe oscillation is syringe_infuse / syringe_withdraw, and a frame series is
    #     time_series_run (records the frame time). Sketch:
    #
    #       from smi_plans import isothermal_kinetics_run, linkam_heater, syringe_infuse, syringe_withdraw
    #       for temp in temps:
    #           yield from isothermal_kinetics_run(
    #               linkam_heater(LThermal), temp, f"{name_base}_{int(temp)}degC",
    #               dets=dets, t=exp_time, num=num,
    #               per_frame=lambda i: (syringe_infuse if i % 2 else syringe_withdraw)(syringe_pu, pump_delay),
    #           )
    #     (records temperature + frame time; the beamstop rod is now pil2M.beamstop.x_rod — see ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil2M_bs_rod' was renamed — the SAXS beamstop rod is now
    #   'pil2M.beamstop.x_rod' (⚠️ notes below); (2) 'det_exposure_time(...)' no longer sets the
    #   exposure unless run as a plan (⚠️ note below). ('LThermal', 'syringe_pu' all still work.)
    # === end smi_plans note ================================================
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    LThermal.setTemperature(temps[0])
    LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time,exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time,exp_time)). (The smi_plans technique runs set exposure for you via t=.)
    for i, temp in enumerate(temps):
        LThermal.setTemperature(temp)

        yield from bps.sleep(hold_delay)

        #Move WAXS detector, wait until finished
        yield from bps.mv(waxs, 20)

        yield from bps.sleep(1) #status code takes a second to change
        while not int(LThermal.status_code.get()) & 2:
            yield from bps.sleep(2) # wait for 2 seconds and try again

        # also to prevent motor from being moved too often
        yield from bps.sleep(hold_delay) #equilibrate capillary to temp

        # Put in attenuators
        yield from SMIBeam().insertFoils("Alignement")

        # Move beamstop
        yield from pil2M_bs_rod.mv_in(x_pos=bsx_pos + 5)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).

        #setimagename
        sample_id(user_name='Chaney', sample_name=f'{name_base}_scanDirect_{int(temp)}degC')
        #take image
        yield from bp.count(dets)

        # Move beamstop
        yield from pil2M_bs_rod.mv_in(x_pos=bsx_pos)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).
        # yield from bps.mv(pil2M_bs_rod.x, bsx_pos) #2 for 4000 mm, 1.2 for 6500

        # Remove attenuators
        yield from SMIBeam().insertFoils("Measurement")

        ### constant infuse over all frames ###
        # #start pump, constant infuse during measurement
        # yield from bps.mv(syringe_pu.dir, 0) #set infuse
        # start_time = time.time()
        # yield from bps.mv(syringe_pu.go, 1) # start pump
        # yield from bps.sleep(pump_delay)

        # #take measurements
        # for exposure in range(num):
        #     sample_id(user_name='Chaney', sample_name=f'{name_base}_scan{exposure}_{int(temp)}degC')
        #     RE.md['temp'] = LThermal.temperature()
        #     # collect data
        #     yield from bp.count(dets)
        # stop_time = time.time()
        # yield from bps.mv(syringe_pu.stop_flow, 1) #stop pump

        # #return pump to original position
        # yield from bps.mv(syringe_pu.dir, 1) #set withdrawal
        # yield from bps.mv(syringe_pu.go, 1) # start pump
        # time_withdrawal = stop_time-start_time
        # yield from bps.sleep(time_withdrawal)
        # yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

        ### oscillation with every frame ###
        # SAXS +20deg WAXS
        for osc in range(num):
            if osc % 2 != 0:
                yield from bps.mv(syringe_pu.dir, 0) #infuse
            else:
                yield from bps.mv(syringe_pu.dir, 1) #withdrawal

            yield from bps.mv(syringe_pu.go, 1) # start pump
            yield from bps.sleep(pump_delay)
            # read the current temperature, and set the sample name
            sample_id(user_name='Chaney', sample_name=f'{name_base}_scan{osc}_wa20_{int(temp)}degC')
            RE.md['temp'] = LThermal.temperature()
            # collect data
            yield from bp.count(dets)
            # wait for some delay and repeat num times
            yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
        
        #Move WAXS detector, wait until finished
        yield from bps.mv(waxs, 0)
        #0 deg WAXS
        for osc in range(num):
            if osc % 2 != 0:
                yield from bps.mv(syringe_pu.dir, 0) #infuse
            else:
                yield from bps.mv(syringe_pu.dir, 1) #withdrawal

            yield from bps.mv(syringe_pu.go, 1) # start pump
            yield from bps.sleep(pump_delay)
            # read the current temperature, and set the sample name
            sample_id(user_name='Chaney', sample_name=f'{name_base}_scan{osc}_wa0_{int(temp)}degC')
            RE.md['temp'] = LThermal.temperature()
            # collect data
            yield from bp.count([pil900KW])
            # wait for some delay and repeat num times
            yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
        #push fresh sample into beam
        yield from bps.mv(syringe_pu.dir, 0) #infuse
        yield from bps.mv(syringe_pu.go, 1) # start pump
        yield from bps.sleep(5)
        yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    LThermal.off()

def snap_series(name_base='series', num=10, temp=25, exp_time=1, dets=[pil900KW,pil2M]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: holds the Linkam stage at one temperature and takes a series of frames (a
    #   simple time series at fixed T), labelling each with the temperature.
    # 💡 NEWER, EASIER WAY: an isothermal frame series is 'smi_plans' isothermal_kinetics_run; it
    #   sets/holds the temperature, records it into the data, and takes the frame series (so you can
    #   drop the 'while not int(LThermal.status_code.get()) & 2: sleep' wait loop):
    #     from smi_plans import isothermal_kinetics_run, linkam_heater
    #     yield from isothermal_kinetics_run(linkam_heater(LThermal), temp, name_base,
    #                                        dets=dets, t=exp_time, num=num)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as a
    #   plan (see the ⚠️ note on it below). ('LThermal' still works.)
    # === end smi_plans note ================================================
    LThermal.setTemperature(temp)
    LThermal.on() # turn on 
    yield from bps.sleep(1) #status code takes a second to change
    while not int(LThermal.status_code.get()) & 2:
        yield from bps.sleep(2) # wait for 2 seconds and try again
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time,exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time,exp_time)). (The smi_plans technique runs set exposure for you via t=.)
    for exposure in range(num):
        sample_id(user_name='Chaney', sample_name=f'{name_base}_scan{exposure}_{int(temp)}degC')
        RE.md['temp'] = LThermal.temperature()
        # collect data
        yield from bp.count(dets)


# by the number of steps and the step size
# during the measurement there will be a gentle oscilatinon of solution
# oscilation volume should be +50ul and -50ul with a rate of 





def temp_snapshop(name_base="temp",num=1,delay=0, exp_time=1,dets=[pil900KW,pil2M],pump_time=2.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: pumps fresh sample into the beam with the syringe pump, then takes a few frames
    #   at the current Linkam temperature with a delay between them.
    # 💡 NEWER, EASIER WAY: pushing sample in then taking a frame series is 'smi_plans' time_series_run
    #   with a syringe step; it records the temperature/frame time for you:
    #     from smi_plans import time_series_run, syringe_infuse
    #     yield from syringe_infuse(syringe_pu, pump_time)
    #     yield from time_series_run(name_base, dets=dets, t=exp_time, num=num, delay=delay)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as a
    #   plan (⚠️ note below). (Heads-up for a human: the sample name uses 'en' which isn't defined in
    #   this function — pre-existing issue. 'syringe_pu', 'LThermal' still work.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_time,exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time,exp_time)). (The smi_plans technique runs set exposure for you via t=.)
    # move sample in
    yield from bps.mv(syringe_pu.x3, 1) # start pump
    yield from bps.sleep(pump_time) # wait 2.5 seconds
    yield from bps.mv(syringe_pu.x4, 1) # stop pump
    for i in range(num):
        # read the current temperature, and set the sample name
        sample_id(user_name='Chaney', sample_name=f'{name_base}_{LThermal.temperature()}degC_{en}eV')
        RE.md['temp'] = LThermal.temperature()
        # collect data
        yield from bp.count(dets)
        # wait for some delay and repeat num times
        yield from bps.sleep(delay)

def set_pump_rate(rate):
    yield from bps.mv(syringe_pu.rate, rate)

def set_pump_vol(vol):
    yield from bps.mv(syringe_pu.vol, vol)




def swaxs_S_edge_2024_liquidcell_chris(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS/WAXS scan across the sulfur edge on liquid-cell samples — for
    #   each sample and WAXS arc, steps the energy and takes a SAXS+WAXS image.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; it records the
    #   energy/beam into the data and the file name, and the energy move was fixed so the per-energy
    #   sleeps and the 'if xbpm2.sumX < 50' re-seek aren't needed:
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = ["L1_01", "L1_02", "L1_03"]
    x = [      35370,   16450,   -3250]
    y = [      -6000,   -6450,   -5950] 

    #reduced energy range
    names = ["L1_02a"]
    x = [      16300]
    y = [      -6450] 

    #reduced energy range
    names = ["L1_02b"]
    x = [      16600]
    y = [      -6450] 

    # names = ["L1_01", "L1_02"]
    # x = [      38150,   20050]
    # y = [      -3830,   -3490] 

    #reduced energy range
    names = ["L1_03a"]
    x = [       19800]
    y = [       -3490] 
    
    #Long energy range
    names = ["L1_03b"]
    x = [       20150]
    y = [       -3490]

    #Long energy range
    names = ["L1_03d"]
    x = [       20150]
    y = [       -3490] 

    #Long energy range
    names = ["L1_01e"]
    x = [       38200]
    y = [       -3530]

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    

    # energies = [2450.0, 2455.0, 2460.0, 2465.0, 2470.0, 2473.0, 2475.0, 2475.5, 2476.0, 2476.5, 2477.0, 2477.5, 2478.0, 2478.5, 2479.0,
    #             2479.5, 2480.0, 2480.5, 2483.0, 2485.0, 2487.5, 2490.0, 2492.5, 2495.0, 2500.0, 2510.0, 2520.0, 2530.0, 2540.0, 2550.0]
    

    energies = [2445.0, 2460.0, 2476.5, 2477.0, 2477.5, 2478.0, 2478.5, 2479.0, 2479.5, 2485.0, 2550.0]
    

    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)
        

        yss = np.linspace(ys-0, ys + 0, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M, pdcurrent2]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)





def swaxs_S_edge_2024_liquidcell1ener_chris(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single-energy SAXS/WAXS scan on a liquid-cell sample — sets one energy, then
    #   for each WAXS arc rasters y a little and takes a SAXS+WAXS image at each spot.
    # 💡 NEWER, EASIER WAY: a single-energy y-raster is a 'smi_plans' acquire with a y motor_axis;
    #   move_energy_fb sets the energy (recording it), and the positions are recorded for you:
    #     from smi_plans import acquire, move_energy_fb, motor_axis
    #     yield from move_energy_fb(2550)          # sets + settles the energy, manages beam feedback
    #     yield from acquire("L1_01d", dets=[pil900KW, pil2M], t=t,
    #                        axes=[motor_axis("waxs_arc", waxs, [0, 20]), motor_axis("piezo_y", piezo.y, yss)])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    #Long energy range
    names = ["L1_01d"]
    x = [       38400]
    y = [       -3830] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energie = 2550
    
    # energies = [2450.0, 2455.0, 2460.0, 2465.0, 2470.0, 2473.0, 2475.0, 2475.5, 2476.0, 2476.5, 2477.0, 2477.5, 2478.0, 2478.5, 2479.0,
    #             2479.5, 2480.0, 2480.5, 2483.0, 2485.0, 2487.5, 2490.0, 2492.5, 2495.0, 2500.0, 2510.0, 2520.0, 2530.0, 2540.0, 2550.0]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)
        

        yss = np.linspace(ys-300, ys + 300, 30)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M, pdcurrent2]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            
            yield from bps.mv(energy, energie)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for xsss, ysss in zip(xss, yss):

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % energie, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)



def waxs_S_edge_chaney_variousprs_2024_1(t=1):
    '''
    setthreshold energy 2450 uhighg 1600
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS scan across the sulfur edge over a bar of transmission samples,
    #   repeated at several sample-rotation angles set via the prs stage (a damage-test variant) —
    #   at each rotation it loops the samples and steps the energy.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; the sample rotation that
    #   used to be 'prs' is now 'stage.phi' (set per rotation or via a motor_axis), and the
    #   energy/beam get recorded for you (so the per-energy sleeps and 'if xbpm2.sumX < 50' re-seek
    #   become unnecessary):
    #     from smi_plans import nexafs_bar, SampleList
    #     yield from bps.mv(stage.phi, prs0 + 35)   # 'prs' is now 'stage.phi' — see ⚠️
    #     samples = SampleList.from_columns(name=names, x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    prs0 = -1
    # yield from bps.mv(prs, prs0)


    # names = ["Trmsn_14", "Trmsn_17", "Trmsn_01", "Trmsn_03",
    #          "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35"]
    # x = [         12300,       5900,      -9600,     -16200,     
    #               31400,      25400,      19500,      13900,       7300,        1000,       -5000,     -11000,     -17300,     -23300]
    # y = [         -7400,      -7600,      -7300,      -7400,      
    #                5000,       5100,       5000,       5100,       5300,        5300,        5400,       5200,       5200,       5200] 

    # assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    # waxs_arc = [0, 20, 40]
    # waxs_arc = [0, 20]

    # for name, xs, ys in zip(names, x, y):
    #     yield from bps.mv(piezo.x, xs,
    #                       piezo.y, ys)

    #     yss = np.linspace(ys, ys + 1200, 63)
    #     xss = np.array([xs])

    #     yss, xss = np.meshgrid(yss, xss)
    #     yss = yss.ravel()
    #     xss = xss.ravel()

    #     for wa in waxs_arc:
    #         yield from bps.mv(waxs, wa)
    #         if wa == 0:
    #             dets = [pil900KW]
    #         else:
    #             dets = [pil900KW, pil2M]

    #         det_exposure_time(t, t)

    #         name_fmt = "{sample}_prs0deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
    #         for e, xsss, ysss in zip(energies, xss, yss):
    #             yield from bps.mv(energy, e)
    #             yield from bps.sleep(2)
    #             if xbpm2.sumX.get() < 50:
    #                 yield from bps.sleep(2)
    #                 yield from bps.mv(energy, e)
    #                 yield from bps.sleep(2)

    #             yield from bps.mv(piezo.y, ysss)
    #             yield from bps.mv(piezo.x, xsss)

    #             bpm = xbpm3.sumX.get()

    #             sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
    #             sample_id(user_name="TC", sample_name=sample_name)
    #             print(f"\n\t=== Sample: {sample_name} ===\n")

    #             yield from bp.count(dets, num=1)

    #         yield from bps.mv(energy, 2500)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2480)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2445)


    # yield from bps.mv(prs, prs0+35)

    # names = ["Trmsn_14", "Trmsn_17", "Trmsn_01", "Trmsn_03",
    #          "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35"]
    # x = [         14300,       7900,      -7800,     -14400,     
    #               33400,      27400,      21500,      15900,       9300,        3000,       -3100,      -9100,     -15500,     -21700]
    # y = [         -7400,      -7600,      -7300,      -7400,      
    #                5000,       5100,       5000,       5100,       5300,        5300,        5400,       5200,       5200,       5200] 

    # assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    # waxs_arc = [0, 20, 40]
    # waxs_arc = [0, 20]

    # for name, xs, ys in zip(names, x, y):
    #     yield from bps.mv(piezo.x, xs,
    #                       piezo.y, ys)

    #     yss = np.linspace(ys, ys + 1200, 63)
    #     xss = np.array([xs])

    #     yss, xss = np.meshgrid(yss, xss)
    #     yss = yss.ravel()
    #     xss = xss.ravel()

    #     for wa in waxs_arc:
    #         yield from bps.mv(waxs, wa)
    #         if wa == 0:
    #             dets = [pil900KW]
    #         else:
    #             dets = [pil900KW, pil2M]

    #         det_exposure_time(t, t)

    #         name_fmt = "{sample}_prs35deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
    #         for e, xsss, ysss in zip(energies, xss, yss):
    #             yield from bps.mv(energy, e)
    #             yield from bps.sleep(2)
    #             if xbpm2.sumX.get() < 50:
    #                 yield from bps.sleep(2)
    #                 yield from bps.mv(energy, e)
    #                 yield from bps.sleep(2)

    #             yield from bps.mv(piezo.y, ysss)
    #             yield from bps.mv(piezo.x, xsss)

    #             bpm = xbpm3.sumX.get()

    #             sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
    #             sample_id(user_name="TC", sample_name=sample_name)
    #             print(f"\n\t=== Sample: {sample_name} ===\n")

    #             yield from bp.count(dets, num=1)

    #         yield from bps.mv(energy, 2500)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2480)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2445)



    # yield from bps.mv(prs, prs0+55)

    # names = ["Trmsn_14", "Trmsn_17", "Trmsn_01", "Trmsn_03",
    #          "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35"]
    # x = [         16600,      10200,      -5700,     -12400,     
    #               36100,      29900,      23900,      18000,      11600,        5000,       -1100,      -7000,     -13600,     -19900]
    # y = [         -7400,      -7600,      -7300,      -7400,      
    #                5000,       5100,       5000,       5100,       5300,        5300,        5400,       5200,       5200,       5200] 

    # assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    # energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
    #             + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    # waxs_arc = [0, 20, 40]
    # waxs_arc = [0, 20]

    # for name, xs, ys in zip(names, x, y):
    #     yield from bps.mv(piezo.x, xs,
    #                       piezo.y, ys)

    #     yss = np.linspace(ys, ys + 1200, 63)
    #     xss = np.array([xs])

    #     yss, xss = np.meshgrid(yss, xss)
    #     yss = yss.ravel()
    #     xss = xss.ravel()

    #     for wa in waxs_arc:
    #         yield from bps.mv(waxs, wa)
    #         if wa == 0:
    #             dets = [pil900KW]
    #         else:
    #             dets = [pil900KW, pil2M]

    #         det_exposure_time(t, t)

    #         name_fmt = "{sample}_prs55deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
    #         for e, xsss, ysss in zip(energies, xss, yss):
    #             yield from bps.mv(energy, e)
    #             yield from bps.sleep(2)
    #             if xbpm2.sumX.get() < 50:
    #                 yield from bps.sleep(2)
    #                 yield from bps.mv(energy, e)
    #                 yield from bps.sleep(2)

    #             yield from bps.mv(piezo.y, ysss)
    #             yield from bps.mv(piezo.x, xsss)

    #             bpm = xbpm3.sumX.get()

    #             sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
    #             sample_id(user_name="TC", sample_name=sample_name)
    #             print(f"\n\t=== Sample: {sample_name} ===\n")

    #             yield from bp.count(dets, num=1)

    #         yield from bps.mv(energy, 2500)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2480)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2445)



    # names = ["Trmsn_14", "Trmsn_17", "Trmsn_01", "Trmsn_03",
    #          "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35"]
    # x = [         14300,       7900,      -7800,     -14400,     
    #               33400,      27400,      21500,      15900,       9300,        3000,       -3100,      -9100,     -15500,     -21700]
    # y = [         -7400,      -7600,      -7300,      -7400,      
    #                5000,       5100,       5000,       5100,       5300,        5300,        5400,       5200,       5200,       5200] 



    yield from bps.mv(prs, prs0+35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["Trmsn_14",
             "Trmsn_22", "Trmsn_23", "Trmsn_26", "Trmsn_34", "Trmsn_35"]
    x = [         14300,     
                  21500,      15900,      9300,     -15500,     -21700]
    y = [         -7400,      
                   5000,       5100,       5300,       5200,       5200] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs35deg_damagetest_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)

def waxs_S_edge_chaney_variousprs_2024_1_march(t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS scan across the sulfur edge over a bar of samples, repeated at
    #   several sample-rotation angles set via the prs stage — at each rotation it loops the samples
    #   and steps the energy.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; the rotation that used
    #   to be 'prs' is now 'stage.phi', and the energy/beam get recorded for you (so the per-energy
    #   sleeps and 'if xbpm2.sumX < 50' re-seek are no longer needed):
    #     from smi_plans import nexafs_bar, SampleList
    #     for ang in (prs0, prs0+35, prs0+55):
    #         yield from bps.mv(stage.phi, ang)     # 'prs' is now 'stage.phi' — see ⚠️
    #         samples = SampleList.from_columns(name=names, x=x, y=y)
    #         yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    prs0 = -1
    yield from bps.mv(prs, prs0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    x =     [  35044,   29044,   23544,   17544,   11044,    5044,    -1255,    -7255,   -13455,   -18956]
    y =     [  -3648,   -3648,   -3648,   -3848,   -4048,   -3848,    -3848,    -3848,    -3848,    -3848] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs0deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


    yield from bps.mv(prs, prs0+35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    x =     [  34544,   28544,   22644,   16643,  10394,     4394,    -1606,    -7855,   -14105,   -19855]
    y =     [  -3648,   -3648,   -3448,   -3848,  -3848,    -3848,    -3648,    -3848,    -3848,    -3648] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs35deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0+55)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", "SiN-7",  "SiN-8",  "SiN-9", "SiN-10", "SiN-11"]
    x =     [  33500,   27399,   21549,   15550,    9150,    3149,    -2850,    -9050,   -15300,   -21050]
    y =     [  -3448,   -3448,   -3248,   -3848,   -3848,   -3848,    -3648,    -3848,    -3848,    -3648] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    waxs_arc = [0, 20, 40]
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1200, 63)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs55deg_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    names = ["Trmsn_14", "Trmsn_17", "Trmsn_01", "Trmsn_03",
             "Trmsn_18", "Trmsn_21", "Trmsn_22", "Trmsn_23", "Trmsn_26",  "Trmsn_29",  "Trmsn_30", "Trmsn_33", "Trmsn_34", "Trmsn_35"]
    x = [         14300,       7900,      -7800,     -14400,     
                  33400,      27400,      21500,      15900,       9300,        3000,       -3100,      -9100,     -15500,     -21700]
    y = [         -7400,      -7600,      -7300,      -7400,      
                   5000,       5100,       5000,       5100,       5300,        5300,        5400,       5200,       5200,       5200]





    
def waxs_S_edge_chaney_2024_3(name, x, y, t=1, pump=False):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS/SAXS scan across the sulfur edge over the sample positions you
    #   pass in — for each spot and WAXS arc, steps the energy and takes an image (optionally running
    #   the syringe pump during each shot).
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar (with an optional syringe
    #   step per frame); it records the energy/beam, and the energy move was fixed so the per-energy
    #   sleeps and 'if xbpm2.sumX < 50' re-seek aren't needed:
    #     from smi_plans import nexafs_bar, SampleList, syringe_infuse
    #     samples = SampleList.from_columns(name=[name]*len(x), x=x, y=y)
    #     yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    # names = ["PM7_TO1"]
    # x = [          0]
    # y = [         -6850]
 
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    waxs_arc = [0, 20]

    # waxs_arc = [20]

    for xs, ys in zip(x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M] 

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                if pump:
                    yield from bps.mv(syringe_pu.go, 1) # start pump
                    yield from bps.sleep(1)
                yield from bp.count(dets, num=1)
                if pump:
                    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)

    sample_id(user_name="test", sample_name='test')
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (The smi_plans technique runs set exposure for you via t=.)

    

def waxs_S_edge_chaney_2024_3_coarse(name, t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a coarse (fewer energies, longer exposure) resonant WAXS/SAXS scan across the
    #   sulfur edge on one spot, running the syringe pump during each shot.
    # 💡 NEWER, EASIER WAY: a single-spot energy scan with a syringe step per frame is a 'smi_plans'
    #   energy run (nexafs_run) with syringe_infuse; it records the energy/beam (so the per-energy
    #   sleeps and 'if xbpm2.sumX < 50' re-seek aren't needed):
    #     from smi_plans import nexafs_run, syringe_infuse
    #     yield from nexafs_run(name, energies, t=t, dets=[pil900KW, pil2M], geometry="transmission")
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). The 💡 lines are scaffolding you can delete once you migrate.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    # names = ["PM7_TO1"]
    x = [          2000]
    y = [         -6458] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"
    
    # less energies for long exposure
    energies = (np.arange(2450, 2470, 10).tolist()+ np.arange(2470, 2480, 1).tolist()
            + np.arange(2480, 2520, 20).tolist())

    waxs_arc = [0, 20]


    # yield from bps.mv(syringe_pu.go, 1) # start pump

    for xs, ys in zip(x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bps.mv(syringe_pu.go, 1) # start pump

                yield from bp.count(dets, num=1)

                yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)
    
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump




def waxs_S_edge_chaney_variousprs_2024_3(t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS/SAXS scan across the sulfur edge over a bar of samples,
    #   repeated at several sample-rotation angles set via the prs stage; ends with some static and
    #   different-proposal sections.
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan is a 'smi_plans' bar; the rotation that used
    #   to be 'prs' is now 'stage.phi' (set per rotation), and the energy/beam get recorded for you
    #   (so the per-energy sleeps and 'if xbpm2.sumX < 50' re-seek aren't needed):
    #     from smi_plans import nexafs_bar, SampleList
    #     for ang in (prs0+35, prs0+55, prs0-35):
    #         yield from bps.mv(stage.phi, ang)     # 'prs' is now 'stage.phi' — see ⚠️
    #         samples = SampleList.from_columns(name=names, x=x, y=y)
    #         yield from nexafs_bar(samples, energies, t=t, dets=[pil900KW, pil2M])
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi'; (2)
    #   'det_exposure_time(...)' no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    prs0 = -1
    yield from bps.mv(prs, prs0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bps.mv(stage.y, -5.8)

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2475, 1).tolist() +np.arange(2475, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    waxs_arc = [7, 27]

    # names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", 
    #          "SiN-5", "SiN-6", "SiN-7", "SiN-8"]
    # x =     [  20300,   14000,    7600,    1200,   -5200,   
    #            14000,    7800,    1500,   -4600]
    # y =     [  -6300,   -6500,   -6450,   -6500,   -6600,   
    #             6300,    6350,    6300,    6250] 

    # assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"



    # for name, xs, ys in zip(names, x, y):
    #     yield from bps.mv(piezo.x, xs,
    #                       piezo.y, ys)

    #     yss = np.linspace(ys, ys + 1300, len(energies))
    #     xss = np.array([xs])

    #     yss, xss = np.meshgrid(yss, xss)
    #     yss = yss.ravel()
    #     xss = xss.ravel()

    #     for wa in waxs_arc:
    #         yield from bps.mv(waxs, wa)
    #         if wa == 7:
    #             dets = [pil900KW]
    #         else:
    #             dets = [pil900KW, pil2M]

    #         det_exposure_time(t, t)

    #         name_fmt = "{sample}_prs0deg_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
    #         for e, xsss, ysss in zip(energies, xss, yss):
    #             yield from bps.mv(energy, e)
    #             yield from bps.sleep(2)
    #             if xbpm2.sumX.get() < 50:
    #                 yield from bps.sleep(2)
    #                 yield from bps.mv(energy, e)
    #                 yield from bps.sleep(2)

    #             yield from bps.mv(piezo.y, ysss,
    #                               piezo.x, xsss)

    #             bpm = xbpm3.sumX.get()

    #             sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
    #             sample_id(user_name="TC", sample_name=sample_name)
    #             print(f"\n\t=== Sample: {sample_name} ===\n")

    #             yield from bp.count(dets, num=1)

    #         yield from bps.mv(energy, 2500)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2480)
    #         yield from bps.sleep(2)
    #         yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0+35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-6", "SiN-7", "SiN-8"]
    x =     [   6300,    200,   -5900]
    y =     [   6250,    6100,    6000] 

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    for name, xs, ys in zip(names, x, y):
        #Offset of -1000 microns with rotation of PRS
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1300, len(energies))
        xss = np.array([ xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs35deg_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss,
                                  piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0+55)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4", 
             "SiN-5", "SiN-6", "SiN-7", "SiN-8"]
    x =     [  17700,   11600,    5400,    -900,   -00,   
               11200,    5300,    -800,   -6700]
    y =     [  -6300,   -6600,   -6600,   -6700,   -6900,   
                6300,    6250,    6100,    6000] 
    
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    for name, xs, ys in zip(names, x, y):
        #Offset of -1500 microns with rotation of PRS
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1300, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prs55deg_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss,
                                  piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)



    yield from bps.mv(prs, prs0-35)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    names = ["SiN-0", "SiN-1", "SiN-2", "SiN-3", "SiN-4"]
    x =     [  21800,   15500,    9100,    2600,   -3900]
    y =     [  -6300,   -6600,   -6600,   -6700,   -6900] 
    
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    for name, xs, ys in zip(names, x, y):
        #Offset of -1500 microns with rotation of PRS
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1300, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prsm35deg_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss,
                                  piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)

    waxs_arc = [0, 20]
    yield from bps.mv(prs, prs0-1)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    
    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())

    det_exposure_time(15, 15)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(15, 15)  — or at the prompt:  RE(det_exposure_time(15, 15)). (The smi_plans technique runs set exposure for you via t=.)
    names = ["Li2S8_static"]
    x =     [ 39400]
    y =     [ -5400] 
    
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    for name, xs, ys in zip(names, x, y):
        #Offset of -1500 microns with rotation of PRS
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 600, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss,
                                  piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)


    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (The smi_plans technique runs set exposure for you via t=.)
    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
            + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    

    proposal_id("2024_3", "316022_McNeill_16")

    names = ["Y2_05", "Y2_06", "Y2_07"]
    x =     [-15000,  -21000,   -27700]
    y =     [  -7300,   -7300,   -7300] 
    
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    for name, xs, ys in zip(names, x, y):
        #Offset of -1500 microns with rotation of PRS
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1000, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_prsm35deg_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss,
                                  piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="CM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2445)







def giwaxs_S_edge_chaney_2024_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant GISAXS scan at the sulfur edge over a bar of samples — for each
    #   sample it moves there, aligns, then for each WAXS arc and incident angle steps the energy
    #   (nudging x in step) and takes a WAXS image.
    # 💡 NEWER, EASIER WAY: aligning + sweeping energy/incidence/arc while recording is the
    #   'smi_plans' GIWAXS + energy combination (align_sample saves the alignment; energy_axis /
    #   incidence_axis record the values, so the per-energy sleeps and re-seek aren't needed):
    #     from smi_plans import giwaxs_bar, align_sample, SampleList, energy_axis
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, x_hexa=x_hexa)
    #     yield from giwaxs_bar(samples, dets=[pil900KW, pil2M], t=t, align=align_sample,
    #                           incident_angles=[1.0], arc_angles=[7, 27])  # compose energy_axis for the edge sweep
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless
    #   run as a plan (⚠️ notes below). (Heads-up for a human: 'xstep' isn't defined in this function
    #   — pre-existing issue.)
    # === end smi_plans note ================================================
 

    names = [  'GI_P25_4']             
    x_piezo = [    -48000]  
    x_hexa = [         -8] 
    y_piezo = [     -2700] 
    
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 27]
    ai0_all = 0
    ai_list = [1.0]

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2475, 1).tolist() +np.arange(2475, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.3)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        
        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            if wa ==7:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            # Do not take SAXS when WAXS detector in the way

            counter = 0
            for k, ais in enumerate(ai_list):
    

                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek (the re-move + sleeps below) — move_energy_fb/energy_axis already pause the beam feedback, settle, and re-seek automatically if the beam drops. (Not broken, just no longer needed once you migrate.)
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="GS", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)
                
                yield from bps.mv(energy, 2500)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 2480)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                yield from bps.mv(energy, 2445)

            yield from bps.mv(piezo.th, ai0)
    # vol = Cpt(EpicsSignal, "Val:Vol-SP",) 
    # rate = Cpt(EpicsSignal, "Val:Rate-SP", )
    # go = Cpt(EpicsSignal, "Cmd:Run-Cmd",)
    # stop_flow = Cpt(EpicsSignal, "Cmd:Stop-Cmd",)
    # dia = Cpt(EpicsSignal, "Val:Dia-RB")
    # dir = Cpt(EpicsSignal, "Val:Dir-Sel",) 

def waxs_S_edge_marks_2025_1_coarse(name, x=[0], y=[-3190], t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant WAXS/SAXS scan across the sulfur edge (~2445->2560 eV) with a
    #   flowing-liquid cell — it starts the syringe pump, then for each WAXS arc steps the energy
    #   (nudging x/y a little each step) and takes an image, recording the beam-monitor reading.
    #
    # 💡 NEWER, EASIER WAY: an energy sweep that also runs a flow is the smi_plans energy + flow
    #   combination. energy_axis sweeps the energy AND manages the beam (so you can drop the manual
    #   sleeps and the beam re-seek), records the energy/beam into each image, and names the files;
    #   syringe_infuse starts the pump:
    #
    #     from smi_plans import nexafs_run, syringe_infuse   # do this once at the top of your session
    #     yield from syringe_infuse(syringe_pu)              # start the flow
    #     yield from nexafs_run(name, energies, t=t, dets=[pil900KW, pil2M],
    #                           geometry="transmission")     # sweep the WAXS arc as an extra loop, as you do now
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for anything marked ⚠️; the 💡 lines are scaffolding you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see the ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    # names = ["PM7_TO1"]
    # x = [          2000] 7500  9500
    # y = [         -6458] -3639 -3588

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    # assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"
    
    # less energies for long exposure
    # energies = (np.arange(2450, 2470, 10).tolist()+ np.arange(2470, 2480, 1).tolist()
    #         + np.arange(2480, 2520, 20).tolist())
    


    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())

    xsss = np.linspace(x[0], x[0]+2000, len(energies))
    ysss = np.linspace(y[0], y[0], len(energies))


    waxs_arc = [0, 20]

    # yield from bps.mv(syringe_pu.go, 1) # start pump


    yield from bps.mv(syringe_pu.go, 1) # start pump

    for xs, ys in zip(x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

            name_fmt = "{sample}_sdd3.0m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xss, yss in zip(energies, xsss, ysss):
                # print(e, xss)
                yield from bps.mv(piezo.x, xss)
                yield from bps.mv(piezo.y, yss)
                yield from bps.mv(energy, e)

                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek — move_energy_fb/energy_axis already re-seek the energy if the beam dips. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="TC", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

                # yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

            yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2445)
    
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (The smi_plans technique runs set exposure for you via t=.)





def nexafs_S_edge_marks_2025_1_coarse(name, x=[0], y=[-3190], t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS sweep across the sulfur edge (~2445->2560 eV) at
    #   WAXS arc 20 — at each energy it nudges x/y a little and takes a WAXS image, recording the
    #   beam-monitor reading.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run     # do this once at the top
    #     yield from nexafs_run("nexafs_" + name, energies, t=t,
    #                           dets=[pil900KW], geometry="transmission")
    #   (it sets the exposure, manages the energy move + beam feedback, and records the
    #    energy/beam into each image — so you can drop the per-step sleeps and the beam re-seek.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for anything marked ⚠️; the 💡 lines are scaffolding you can delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]


    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    
    #y -3613 x = 0
    #y -3600 x = 2000

    # Coarse first to look at the edge
    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())


    xsss = np.linspace(x[0], x[0]+2000, len(energies))
    ysss = np.linspace(y[0], y[0], len(energies))

    waxs_arc = [20]

    for xs, ys in zip(x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW]
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)

            name_fmt = "nexafs_{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xss, yss in zip(energies, xsss, ysss):
                # print(e, xss)
                yield from bps.mv(piezo.x, xss)
                yield from bps.mv(piezo.y, yss)

                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek — move_energy_fb/energy_axis already re-seek the energy if the beam dips. (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="SM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2500)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2445)

    sample_id(user_name="test", sample_name="test")



def temp_snapshop(name_base="temp",num=1,delay=0, exp_time=1,en=2472,dets=[pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: parks the X-ray energy at one value (2472 eV by default), then takes
    #   a series of WAXS snapshots, stamping the current Linkam temperature into each name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that records
    #   the temperature (and beam readings) straight INTO the saved data and into the file
    #   name, so you don't have to read LThermal.temperature() by hand. A simple repeated
    #   measurement at fixed conditions is just:
    #
    #     from smi_plans import time_series_run     # do this once at the top of your session
    #     yield from time_series_run("temp", dets=[pil900KW, ls],
    #                                n=num, delay=delay, t=exp_time)
    #
    #   (Here 'ls' is the Lakeshore; for the Linkam use 'LThermal'. The temperature then
    #    shows up in the file name as a recorded field. This is just a tidier option to try
    #    later — your script below still works as-is.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_time,exp_time)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(exp_time, exp_time)  — or at the prompt:  RE(det_exposure_time(exp_time, exp_time)). (smi_plans' technique runs set it for you via t=.)
    energy.move(en)
    for i in range(num):
        sample_id(user_name='Gorecka', sample_name=f'{name_base}_{LThermal.temperature()}degC_{en}eV')
        RE.md['temp'] = LThermal.temperature()
        yield from bp.count(dets)
        yield from bps.sleep(delay)



def saxs_S_edge_linkam_2024_1(t=1,temps=[30]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the X-ray energy across the sulfur edge at a few WAXS-arc
    #   positions and sample spots, taking a SAXS/WAXS image at each energy. (The arc is
    #   the curved WAXS detector mount; at arc 0 only the WAXS camera is in view, otherwise
    #   both SAXS and WAXS are used.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy sweep in one call and writes the energy + beam intensity straight into
    #   the saved data and the file name (so you don't hand-build "{energy}eV_wa..._bpm..."
    #   or read xbpm3 yourself). It also takes care of the energy-move settling and beam
    #   feedback for you. The energy axis itself is just:
    #
    #     from smi_plans import acquire, energy_axis, saxs_waxs_dets
    #     yield from acquire("D1_06_10sexpo",
    #                        saxs_waxs_dets(),                     # SAXS + WAXS together
    #                        [energy_axis([2472, 2475, 247])],     # your energies, unchanged
    #                        reads=[xbpm2, xbpm3])
    #
    #   (For the per-arc looping you have here, see giwaxs_run / the arc motor_axis in
    #    smi_plans. This is just a tidier option to try later.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note
    #   on it). The energy 'sleep' lines still work — they're only flagged 💡 as no longer
    #   needed once you switch to smi_plans.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    name = "D1_06_10sexpo"

    energies = (2472,2475,247)
    waxs_arc = [20, 0]

    
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

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

        name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
        for e, xsss, ysss in zip(energies, xss, yss):
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this (and the beam-recheck just below) once you migrate — move_energy_fb/energy_axis already wait for the energy to settle, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
            if xbpm2.sumX.get() < 50:
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
        yield from bps.sleep(2)  # 💡 smi_plans: these settle waits after each energy move are handled for you by move_energy_fb/energy_axis once you migrate. (Not broken, just no longer needed.)
        yield from bps.mv(energy, 2480)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2445)
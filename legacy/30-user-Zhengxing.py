def Ru_edge_zhengxing_2024_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS scan across the ruthenium edge
    #   (~2800-2880 eV). For each sample position and each WAXS detector arc angle, it
    #   sweeps the X-ray energy and takes a WAXS (and, when the arc is out of the way,
    #   SAXS) image at each energy. ("Tender" just means these are fairly low X-ray
    #   energies; "NEXAFS" means watching how absorption changes as you cross an
    #   element's edge.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does
    #   a full energy scan like this in one line. It steps the energy safely, waits for it
    #   to settle, manages the beam feedback, and records the energy + beam intensity
    #   straight into the saved data and the file name — so you don't have to hand-build
    #   that long "{sample}_{energy}eV_wa{}_bpm{}" name. Same kind of scan as below:
    #
    #     from smi_plans import nexafs_run             # do this once at the top of your session
    #     yield from nexafs_run(
    #         "P1_120C_1_pos1",                        # the rest of the file name is filled in for you
    #         energies,                                # your same energy list, unchanged
    #         t=t,                                     # your exposure time, unchanged
    #         dets=[pil2M, pil900KW],                  # SAXS + the current WAXS detector
    #         geometry="transmission",
    #     )
    #     # (call it per sample position / WAXS arc, the way you loop below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now. The lines
    #    marked 💡 still work but become unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(t, t)' calls no longer set the
    #   exposure unless run as a plan (see the ⚠️ notes on those lines below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    '''
    names = [   'P2_80C',    'P4_80C']
    x_piezo = [    39200,       26500]
    x_hexa =  [        0,           0]
    y_piezo = [    -3900,       -3600]
    z_piezo = [     6600,        6600]
    '''

    names = ['P1_120C_1', 'P1_120C_2','P1_120C_3','P1_120C_4', 'P1_120C_5','P1_120C_6','P1_120C_7']
    x = [           -2.6,        -2.5,       -2.4,       -2.3,        -2.2,       -2.1,      -2.4]
    y = [           -3.2,        -3.2,       -3.2,       -3.2,        -3.2,       -3.2,      -3.2]

    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"

    energies = np.arange(2800, 2825, 5).tolist() + np.arange(2825, 2830, 0.5).tolist() + np.arange(2830, 2848, 2).tolist()+ np.arange(2838, 2850, 0.5).tolist()+ np.arange(2850, 2881, 5).tolist()

    waxs_arc = [20, 0]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(stage.x, xs)
        yield from bps.mv(stage.y, ys)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        yss = np.linspace(ys, ys + 0.5, 55)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed.)
                if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam-loss re-seek block — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(stage.y, ysss)
                yield from bps.mv(stage.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="ZP", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2860)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this stepped energy walk-back (and its sleeps) — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2840)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2820)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2800)
            yield from bps.sleep(2)

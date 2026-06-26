def Nafion_waxs_S_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample, sweeps the X-ray energy across the sulfur edge
    #   (~2452–2508 eV) while nudging the sample in x/y, and takes a SAXS image at each energy.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy scan like this in one line. It records the energy, beam intensity, etc.
    #   straight into the data and fills them into the file name for you (no hand-built
    #   "{energy}eV_..._bpm{xbpm}"). It also drives the energy move robustly — pausing the
    #   beam feedback, moving the energy in one bps.mv (the device manages gap/feedback/harmonic) — so
    #   the try/except + sleep "energy failed, wait 30 s and retry" dance below is no longer
    #   needed. Same measurement (per-sample) as below:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     energies = 7 + np.asarray(np.arange(2445, 2470, 5).tolist()
    #                               + np.arange(2470, 2480, 0.25).tolist()
    #                               + np.arange(2480, 2490, 1).tolist()
    #                               + np.arange(2490, 2501, 5).tolist())
    #     yield from nexafs_run("70nPA", energies, t=t, dets=[pil2M, xbpm2],
    #                           geometry="transmission", updown=False)
    #     # ...wrap one nexafs_run per sample (or use smi_plans.nexafs_bar with a SampleList).
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT for the
    #    ⚠️ line which needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must run as a plan — see
    #   the ⚠️ note on that line.
    # === end smi_plans note ================================================
    dets = [pil2M]

    energies = 7 + np.asarray(
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = np.linspace(52, 52, 1)

    names = ["70nPA", "50nPA", "30nPA", "10nPA"]
    x = [-23500, -1200, 23000, 44500]
    y = [-9700, -9600, -9500, -9000]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 1000, 15)
        xss = np.linspace(xs, xs + 1000, 4)

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                try:  # 💡 smi_plans: you can drop this whole try/except + sleep retry — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                    yield from bps.mv(energy, e)
                except:
                    print("energy failed to move, sleep for 30 s")
                    yield from bps.sleep(30)
                    print("Slept for 30 s, try move energy again")
                    yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: same as above — this settle wait is handled for you by move_energy_fb/energy_axis once you switch over.

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF_sdd2m", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)

    # yield from bps.mv(stage.y, 0)
    # yield from bps.mv(stage.th, 0)

    # names = ['Nafion_xl']
    # x = [-42800]
    # y = [-2500]

    # for name, xs, ys in zip(names, x, y):
    #     yield from bps.mv(piezo.x, xs)
    #     yield from bps.mv(piezo.y, ys)

    #     yss = np.linspace(ys, ys + 1000, 15)
    #     xss = np.linspace(xs, xs + 1000, 4)

    #     yss, xss = np.meshgrid(yss, xss)
    #     yss = yss.ravel()
    #     xss = xss.ravel()

    #     for wa in waxs_arc:
    #         yield from bps.mv(waxs, wa)

    #         det_exposure_time(t,t)
    #         name_fmt = '{sample}_{energy}eV_wa{wax}_bpm{xbpm}'
    #         for e, xsss, ysss in zip(energies, xss, yss):
    #             yield from bps.mv(energy, e)
    #             yield from bps.sleep(1)

    #             yield from bps.mv(piezo.y, ysss)
    #             yield from bps.mv(piezo.x, xsss)

    #             bpm = xbpm2.sumX.value

    #             sample_name = name_fmt.format(sample=name, energy='%6.2f'%e, wax = wa, xbpm = '%4.3f'%bpm)
    #             sample_id(user_name='GF', sample_name=sample_name)
    #             print(f'\n\t=== Sample: {sample_name} ===\n')
    #             yield from bp.count(dets, num=1)

    #         yield from bps.mv(energy, 2470)
    #         yield from bps.mv(energy, 2450)


def Su_nafion_waxs_hard(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at 16.1 keV, for each WAXS-arc angle visits each sample and takes one
    #   SAXS+WAXS frame (a hard-X-ray WAXS bar), across two sample groups.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' with a ready bar runner that
    #   loops samples + WAXS-arc for you and records the arc angle, beam, and detector distance
    #   into the data + file name (no hand-built "{sample}_16100eV_sdd8.3_wa{wax}"). Same idea:
    #
    #     from smi_plans import SampleList, transmission_bar      # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["30nPA", "50nPA"], piezo_x=[12500, -15500], piezo_y=[-300, -300],
    #     )
    #     yield from transmission_bar(bar, t=t, waxs_arc=tuple(np.linspace(0, 32.5, 6)))
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT for the
    #    lines marked ⚠️ which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    waxs_arc = np.linspace(0, 32.5, 6)

    yield from bps.mv(stage.y, 0)
    yield from bps.mv(stage.th, 0)

    names = ["30nPA", "50nPA"]
    x = [12500, -15500]
    y = [-300, -300]

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        for name, xs, ys in zip(names, x, y):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
            name_fmt = "{sample}_16100eV_sdd8.3_wa{wax}"
            sample_name = name_fmt.format(sample=name, wax=wa)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

    yield from bps.mv(stage.th, 1.5)
    yield from bps.mv(stage.y, -8)

    names = ["70nPA", "Nafion_xl"]
    x = [32000, 1000]
    y = [-9000, -9000]

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        for name, xs, ys in zip(names, x, y):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
            name_fmt = "{sample}_16100eV_sdd8.3_wa{wax}"
            sample_name = name_fmt.format(sample=name, wax=wa)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def sara_nafion_waxs_hard(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at 16.1 keV, for each WAXS-arc angle visits each sample and takes one
    #   SAXS+WAXS frame (a hard-X-ray WAXS bar over the SPES samples).
    #
    # 💡 NEWER, EASIER WAY: same as above — 'smi_plans' transmission_bar loops the bar + arc
    #   and records the context into the data + file name:
    #
    #     from smi_plans import SampleList, transmission_bar      # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["SPES_20", "SPES_40", "SPES_60"],
    #         piezo_x=[26000, 4000, -20000], piezo_y=[0, 0, 0],
    #     )
    #     yield from transmission_bar(bar, t=t, waxs_arc=tuple(np.linspace(0, 32.5, 6)))
    #
    #   (Just a tidier option to try later — EXCEPT the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    waxs_arc = np.linspace(0, 32.5, 6)

    # names = ['10nPA_sol', '30nPA_sol', '50nPA_sol', '60nPA_sol']
    # x = [-37200, -31200, -25100, -12200]
    # y = [1000,     1000,   1000,   1000]

    names = ["SPES_20", "SPES_40", "SPES_60"]
    x = [26000, 4000, -20000]
    y = [0, 0, 0]

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        for name, xs, ys in zip(names, x, y):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
            name_fmt = "{sample}_16100eV_sdd8.3_wa{wax}"
            sample_name = name_fmt.format(sample=name, wax=wa)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

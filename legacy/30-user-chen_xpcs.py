def grid_scan_xpcs():

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: at each energy and each x/y grid spot, fires the SAXS camera
    #   to take a fast burst of XPCS frames (here 0.03 s/frame, ~30 s total) and writes
    #   the images straight to the /ramdisk/ disk by hand.
    #
    # ⚠️ HEADS-UP (important, not a crash): the way this takes data — 'pil2M.cam.acquire.put(1)'
    #   plus the 'while pv.get()==1: sleep' busy-wait below — talks to the camera DIRECTLY and
    #   BYPASSES Bluesky's data recording entirely. That means NO run is created and NO
    #   documents/metadata are saved: the energy, beam intensity, sample name, positions, etc.
    #   are NOT recorded anywhere — only raw .tif files land in /ramdisk/, and you're left
    #   stitching context back together from the folder/file names. It will "work" (you get
    #   images) but you lose all the bookkeeping the beamline normally does for you.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a proper
    #   XPCS burst plan that sets the number of frames (cam.num_images) and uses a staged
    #   trigger-and-read, so the frames AND all the context are recorded together as one run:
    #
    #     from smi_plans import xpcs_burst_run            # do this once at the top of your session
    #     for ener in [2450, 2472, 2476, 2490]:          # your energies, unchanged
    #         yield from move_energy_fb(ener)            # steps + settles the energy, handles beam feedback
    #         for (x, y) in grid_positions:              # your x/y grid spots, unchanged
    #             yield from bps.mv(piezo.x, x, piezo.y, y)
    #             yield from xpcs_burst_run(
    #                 "PSBMA5_200um_grid",               # rest of the file name is filled in from recorded data
    #                 dets=[pil2M],
    #                 t=0.03,                            # your per-frame exposure
    #                 n_frames=1000,                     # however many frames make up your ~30 s burst
    #             )
    #   (configure_burst sets cam.num_images for you; the run records energy/beam/positions so you
    #    never have to hand-build the /ramdisk path or the 'pos%s' name again.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(0.03, 30)' line below no longer sets the
    #   exposure unless run as a plan (see its ⚠️ note).
    # === end smi_plans note ================================================

    folder = "301000_Chen34"
    xs = np.linspace(-9350, -9150, 2)
    ys = np.linspace(1220, 1420, 2)
    names = ["PSBMA5_200um_grid"]

    energies = [2450, 2472, 2476, 2490]

    x_off = [0, 60, 0, 60]
    y_off = [0, 0, 60, 60]

    xxs, yys = np.meshgrid(xs, ys)

    dets = [pil2M]
    for name in names:
        for ener, xof, yof in zip(energies, x_off, y_off):
            yield from bps.mv(energy, ener)
            yield from bps.sleep(10)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            for i, (x, y) in enumerate(zip(xxs.ravel(), yys.ravel())):

                pil2M.cam.file_path.put(
                    f"/ramdisk/images/users/2019_3/%s/1M/%s_pos%s" % (folder, name, i)
                )

                yield from bps.mv(piezo.x, x + xof)
                yield from bps.mv(piezo.y, y + yof)

                name_fmt = "{sample}_{energy}eV_pos{pos}"
                sample_name = name_fmt.format(sample=name, energy=ener, pos="%2.2d" % i)
                sample_id(user_name="Chen", sample_name=sample_name)
                yield from bps.sleep(5)

                det_exposure_time(0.03, 30)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.03, 30)  — or at the prompt:  RE(det_exposure_time(0.03, 30)). (smi_plans' xpcs_burst_run sets it for you via t=.)

                print(f"\n\t=== Sample: {sample_name} ===\n")

                pil2M.cam.acquire.put(1)  # smi_plans: this fires the camera DIRECTLY, outside Bluesky — so this burst is NOT recorded as a run (no energy/beam/positions saved, only raw .tif on /ramdisk). xpcs_burst_run uses a staged trigger so the frames + all that context are saved together. (Not a crash, but you lose the bookkeeping.)
                yield from bps.sleep(5)
                pv = EpicsSignal("XF:12IDC-ES:2{Det:1M}cam1:Acquire", name="pv")

                while pv.get() == 1:  # smi_plans: this hand-rolled "wait until the camera is done" busy-loop is what xpcs_burst_run's staged trigger_and_read does for you (and records the result).
                    yield from bps.sleep(5)

        yield from bps.mv(energy, 2475)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
        yield from bps.mv(energy, 2450)


def NEXAFS_SAXS_S_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant scan near the sulfur edge — for each WAXS arc angle it
    #   steps the X-ray energy (and the sample up a little at each energy) and takes a WAXS image.
    #
    # 💡 NEWER, EASIER WAY: sweeping the energy while recording the energy/beam into the data is
    #   exactly what 'smi_plans' energy_axis does; combine it with the WAXS arc to get this scan:
    #
    #     from smi_plans import nexafs_run, energy_axis, motor_axis
    #     # e.g. one nexafs_run per WAXS arc position, or compose energy_axis + an arc motor_axis:
    #     yield from nexafs_run(
    #         "sample_thick_waxs",                  # rest of the file name added automatically
    #         [2450, 2480, 2483, 2484, 2485, 2486, 2500],   # your energies, unchanged
    #         t=t,                                  # your exposure, unchanged
    #         dets=[pil900KW],                      # current WAXS detector — see ⚠️
    #         geometry="transmission",
    #     )
    #   (records energy/beam and sets the exposure for you, so the per-energy sleeps and the
    #    walk-back at the end become unnecessary.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "sample_thick_waxs"

    energies = [2450, 2480, 2483, 2484, 2485, 2486, 2500]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_wa{wa}"

    waxs_an = np.linspace(0, 26, 5)

    yss = np.linspace(1075, 1575, 5)

    for wax in waxs_an:
        yield from bps.mv(waxs, wax)
        for e, ys in zip(energies, yss):
            yield from bps.mv(energy, e)
            yield from bps.mv(piezo.y, ys)
            sample_name = name_fmt.format(sample=name, energy=e, wa="%3.1f" % wax)
            sample_id(user_name="Chen", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2475)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
        yield from bps.mv(energy, 2450)


def grid_scan_static():

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each spot in a small x/y grid, sweeps the X-ray energy back and forth
    #   across the sulfur edge and takes a SAXS+WAXS image at every energy (a resonant map).
    #
    # 💡 NEWER, EASIER WAY: stepping the energy while recording the energy/beam into the data is
    #   'smi_plans' energy_axis; a few sample spots is a spatial grid. You can compose them, e.g.:
    #
    #     from smi_plans import acquire, energy_axis, spatial_grid_axes
    #     yield from acquire(
    #         "PSBMA30_10um_static",                # rest of the file name added automatically
    #         dets=[pil900KW, pil2M],               # current WAXS detector — see ⚠️
    #         axes=[*spatial_grid_axes(piezo.x, x_off, piezo.y, y_off),
    #               energy_axis(np.linspace(2500, 2450, 51), reverse_alternate=True)],
    #     )
    #   (energy_axis records the energy/beam and settles for you; reverse_alternate gives you the
    #    back-and-forth sweep without the manual energies[::-1].)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    names = ["PSBMA30_10um_static"]

    x_off = -36860 + np.asarray([-200, 200])
    y_off = 1220 + np.asarray([-100, 0, 100])

    energies = np.linspace(2500, 2450, 51)
    xxs, yys = np.meshgrid(x_off, y_off)

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    for name in names:
        for i, (x, y) in enumerate(zip(xxs.ravel(), yys.ravel())):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            energies = energies[::-1]
            yield from bps.sleep(2)

            for ener in energies:
                yield from bps.mv(energy, ener)

                yield from bps.sleep(0.1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                name_fmt = "{sample}_{energy}eV_pos{pos}_xbpm{xbpm}"
                sample_name = name_fmt.format(
                    sample=name,
                    energy=ener,
                    pos="%2.2d" % i,
                    xbpm="%3.1f" % xbpm3.sumY.value,
                )
                sample_id(user_name="Chen", sample_name=sample_name)

                det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)
                yield from bp.count(dets, num=1)


def nexafs_S_edge_chen(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS scan at the sulfur edge — steps the X-ray energy and takes a
    #   WAXS image at each energy (with the WAXS arc parked at 45 deg).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a one-line NEXAFS scan that records the energy/beam
    #   into the data and fills them into the file name for you:
    #
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run(
    #         "nexafs_sampletest1_4",               # rest of the file name added automatically
    #         energies,                             # your energy list, unchanged
    #         t=t,                                  # your exposure, unchanged
    #         dets=[pil900KW],                      # current WAXS detector — see ⚠️
    #         geometry="transmission",
    #     )
    #   (sets the exposure, settles each energy, and records energy/beam — so you can drop the
    #    per-energy sleep and the walk-back at the end.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    #   (Heads-up for a human: 'energies' isn't defined inside this function — it relies on a global,
    #    so it may error on its own; that's a pre-existing issue, not something this note changes.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    waxs_arc = [45.0]

    name_fmt = "nexafs_sampletest1_4_{energy}eV_wa{wax}_bpm{xbpm}"

    for wa in waxs_arc:
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

            bpm = xbpm2.sumX.value

            sample_name = name_fmt.format(
                energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
            )
            sample_id(user_name="WC", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2490)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 2470)
    yield from bps.mv(energy, 2450)


def waxs_S_edge_chen_2020_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample on the bar and each WAXS arc angle, sweeps the X-ray
    #   energy down across the sulfur edge and takes a WAXS+SAXS image at each energy.
    #
    # 💡 NEWER, EASIER WAY: a multi-sample energy scan like this is a 'smi_plans' bar — you give
    #   it the sample names + positions once and it loops, aligns nothing extra, and records the
    #   energy/beam into each file name automatically:
    #
    #     from smi_plans import nexafs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y)   # your bar, unchanged
    #     yield from nexafs_bar(
    #         samples, energies, t=t,               # your energies + exposure, unchanged
    #         dets=[pil900KW, pil2M],               # current WAXS detector — see ⚠️
    #     )
    #   (sets the exposure, settles each energy, records energy/beam — so the per-energy sleeps
    #    and the walk-back at the end are no longer needed.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    names = [
        "sampleA1",
        "sampleB1",
        "sampleB2",
        "sampleB3",
        "sampleC4",
        "sampleC5",
        "sampleE8",
        "sampleD1",
        "sampleD2",
        "sampleD3",
        "sampleD4",
        "sampleD5",
        "sampleC8",
        "sampleF1",
        "sampleF2",
        "sampleE1",
        "sampleE3",
        "sampleE4",
        "sampleE5",
        "sampleD8",
        "sampleF8",
    ]
    x = [
        43800,
        28250,
        20750,
        13350,
        5150,
        -5660,
        -10900,
        -18400,
        -26600,
        -34800,
        -42800,
        42300,
        34400,
        26700,
        18800,
        11200,
        2900,
        -5000,
        -12000,
        -20300,
        -27800,
    ]
    y = [
        -4900,
        -5440,
        -5960,
        -5660,
        -5660,
        -5660,
        -5880,
        -4750,
        -5450,
        -5000,
        -4450,
        6950,
        6950,
        6950,
        7450,
        7200,
        7400,
        8250,
        8250,
        8250,
        7750,
    ]

    energies = [
        2450.0,
        2474.0,
        2475.0,
        2476.0,
        2477.0,
        2478.0,
        2479.0,
        2482.0,
        2483.0,
        2484.0,
        2485.0,
        2486.0,
        2487.0,
        2490.0,
        2500.0,
    ]

    waxs_arc = np.linspace(0, 13, 3)

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys + 30)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            name_fmt = "{sample}_rev_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies[::-1]:
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2480)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            yield from bps.mv(energy, 2460)

def NEXAFS_S_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS scan across the sulfur edge
    #   (2450->2500 eV, 51 points) on a solution sample — it sweeps the X-ray energy and
    #   takes a WAXS image + beam reading at each energy. ("NEXAFS" = watching how the
    #   sample absorbs X-rays as you step across an element's absorption edge.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does
    #   a full energy scan like this in ONE line. It steps the energy safely, waits for it
    #   to settle, manages the beam feedback, and records the energy + beam intensity into
    #   the saved data and file name — so you don't hand-build "{sample}_{energy}eV_xbpm{}":
    #
    #     from smi_plans import nexafs_run             # do this once at the top of your session
    #     yield from nexafs_run(
    #         "17_Phil_pk61_buffer_NEXAFS_3rd",        # the rest of the file name is filled in for you
    #         np.linspace(2450, 2500, 51),             # your energies, unchanged
    #         t=t,                                     # your exposure time, unchanged
    #         dets=[pil900KW],                         # the current WAXS detector
    #         geometry="transmission",
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now. The lines
    #    marked 💡 still work but become unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "17_Phil_pk61_buffer_NEXAFS_3rd"
    # x = [8800]

    energies = np.linspace(2450, 2500, 51)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="ZR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.sleep(2)

    yield from bps.mv(energy, 2470)
    yield from bps.sleep(10)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)


def NEXAFS_Cl_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS scan across the chlorine edge
    #   (2800->2850 eV, 51 points) on a solution sample — sweeps the X-ray energy and
    #   takes a WAXS image + beam reading at each energy.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does a full energy scan like this in ONE line. It
    #   steps the energy safely, waits for it to settle, manages the beam feedback, and
    #   records energy + beam intensity into the saved data and file name:
    #
    #     from smi_plans import nexafs_run             # do this once at the top of your session
    #     yield from nexafs_run(
    #         "7_Le_13_Cl_saxs_solution",              # the rest of the file name is filled in for you
    #         np.linspace(2800, 2850, 51),             # your energies, unchanged
    #         t=t,                                     # your exposure time, unchanged
    #         dets=[pil900KW],                         # the current WAXS detector
    #         geometry="transmission",
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now; the 💡 lines just become
    #    unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "7_Le_13_Cl_saxs_solution"
    # x = [8800]

    energies = np.linspace(2800, 2850, 51)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="ZR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.sleep(2)

    yield from bps.mv(energy, 2800)
    yield from bps.sleep(10)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)


def SAXS_Cl_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS scan near the chlorine edge — for each WAXS arc
    #   angle it steps through a handful of chosen energies and takes SAXS + WAXS images,
    #   then does a final "post-measurement" shot at 2810 eV for each arc.
    #   ("Resonant" just means you pick energies right around an element's edge.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans'. You can
    #   hand it the energies as an "axis" and it steps the energy safely (settling, beam
    #   feedback) while recording energy + beam intensity into each saved image — so you
    #   don't hand-build "{sample}_{energy}eV_xbpm{}_wa{}":
    #
    #     from smi_plans import acquire, energy_axis, motor_axis
    #     yield from acquire(
    #         "7_Le_13_Cl_saxs_solution", [pil2M, pil900KW],   # SAXS + current WAXS detector
    #         [motor_axis("wa", waxs, [0.0, 6.5, 13.0]),
    #          energy_axis([2810, 2820, 2826, 2827, 2829, 2832, 2850])],
    #     )
    #     # (sets exposure via the technique presets; see nexafs_run for the simple sweep case.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "7_Le_13_Cl_saxs_solution"
    energies = [2810, 2820, 2826, 2827, 2829, 2832, 2850]
    # energies = [2470]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_wa{wa}"
    wa = [0.0, 6.5, 13.0]

    # y0 = piezo.y.position
    # ys = np.linspace(y0, y0+750, 6)

    for wax in wa:
        yield from bps.mv(waxs, wax)
        for k, e in enumerate(energies):
            yield from bps.mv(energy, e)
            # yield from bps.mv(piezo.y, yss)

            sample_name = name_fmt.format(
                sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
            )
            sample_id(user_name="OS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2810)

    # yield from bps.mvr(piezo.y, 150)
    for wax in wa:
        yield from bps.mv(waxs, wax)

        name_fmt = "{sample}_2810eV_postmeas_xbpm{xbpm}_wa{wa}"
        sample_name = name_fmt.format(
            sample=name, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
        )
        sample_id(user_name="OS", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def NEXAFS_Br_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS scan across the bromine edge (13450->13500 eV, 51 points)
    #   on a solution sample — sweeps the X-ray energy and takes a WAXS image + beam
    #   reading at each energy.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does a full energy scan like this in ONE line. It
    #   steps the energy safely, waits for it to settle, manages the beam feedback, and
    #   records energy + beam intensity into the saved data and file name:
    #
    #     from smi_plans import nexafs_run             # do this once at the top of your session
    #     yield from nexafs_run(
    #         "1_Le_15_Br_nexafs_solution",            # the rest of the file name is filled in for you
    #         np.linspace(13450, 13500, 51),           # your energies, unchanged
    #         t=t,                                     # your exposure time, unchanged
    #         dets=[pil900KW],                         # the current WAXS detector
    #         geometry="transmission",
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now; the 💡 lines just become
    #    unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)

    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "1_Le_15_Br_nexafs_solution"
    # x = [8800]

    energies = np.linspace(13450, 13500, 51)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="ZR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.sleep(2)

    yield from bps.mv(energy, 13450)
    yield from bps.sleep(10)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)


def SAXS_Br_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS scan near the bromine edge — for each WAXS arc angle
    #   it steps through a handful of chosen energies and takes SAXS + WAXS images, then a
    #   final "post-measurement" shot at 13450 eV for each arc.
    #
    # 💡 NEWER, EASIER WAY: hand 'smi_plans' the energies as an "axis"; it steps the energy
    #   safely (settling, beam feedback) and records energy + beam intensity into each
    #   saved image — so you don't hand-build "{sample}_{energy}eV_xbpm{}_wa{}":
    #
    #     from smi_plans import acquire, energy_axis, motor_axis
    #     yield from acquire(
    #         "5_Le_15_Br_saxs", [pil2M, pil900KW],            # SAXS + current WAXS detector
    #         [motor_axis("wa", waxs, [0.0, 6.5, 13.0]),
    #          energy_axis([13450, 13465, 13469, 13471, 13478, 13500])],
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "5_Le_15_Br_saxs"
    energies = [13450, 13465, 13469, 13471, 13478, 13500]
    # energies = [13450]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_wa{wa}"
    wa = [0.0, 6.5, 13.0]

    # y0 = piezo.y.position
    # ys = np.linspace(y0, y0+750, 6)

    for wax in wa:
        yield from bps.mv(waxs, wax)
        for k, e in enumerate(energies):
            yield from bps.mv(energy, e)
            # yield from bps.mv(piezo.y, yss)

            sample_name = name_fmt.format(
                sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
            )
            sample_id(user_name="OS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 13450)

    # yield from bps.mvr(piezo.y, 150)
    for wax in wa:
        yield from bps.mv(waxs, wax)

        name_fmt = "{sample}_13450eV_postmeas_xbpm{xbpm}_wa{wa}"
        sample_name = name_fmt.format(
            sample=name, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
        )
        sample_id(user_name="OS", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def SAXS_s_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant SAXS scan near the sulfur edge — for each WAXS arc angle
    #   it steps through chosen energies (moving to a fresh y-spot at each energy so each
    #   shot hits clean sample) and takes a SAXS image, plus a post-measurement shot at
    #   2470 eV for each arc.
    #
    # 💡 NEWER, EASIER WAY: hand 'smi_plans' the energies and y-positions as "axes" and it
    #   steps the energy safely (settling, beam feedback) while recording energy/position/
    #   beam into each saved image — so you don't hand-build "{sample}_{energy}eV_xbpm{}_wa{}":
    #
    #     from smi_plans import acquire, energy_axis, motor_axis
    #     yield from acquire(
    #         "17_Phil_pk61_buffer_saxs", [pil2M, pil900KW],   # SAXS + current WAXS detector
    #         [motor_axis("wa", waxs, [0.0, 6.5, 13.0, 19.5]),
    #          energy_axis([2470, 2477, 2480, 2482, 2484, 2500])],
    #     )
    #     # (add a y motor_axis if you want the fresh-spot move recorded too.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "17_Phil_pk61_buffer_saxs"
    energies = [2470, 2477, 2480, 2482, 2484, 2500]
    # energies = [2470]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_wa{wa}"
    wa = [0.0, 6.5, 13.0, 19.5]

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(1)
    yield from bps.mv(GV7.close_cmd, 1)

    y0 = piezo.y.position
    ys = np.linspace(y0, y0 + 750, 6)

    for wax in wa:
        yield from bps.mv(waxs, wax)
        for k, (e, yss) in enumerate(zip(energies, ys)):
            yield from bps.mv(energy, e)
            yield from bps.mv(piezo.y, yss)

            sample_name = name_fmt.format(
                sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
            )
            sample_id(user_name="OS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2470)

    yield from bps.mvr(piezo.y, 150)
    for wax in wa:
        yield from bps.mv(waxs, wax)

        name_fmt = "{sample}_2470eV_postmeas_xbpm{xbpm}_wa{wa}"
        sample_name = name_fmt.format(
            sample=name, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
        )
        sample_id(user_name="OS", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")

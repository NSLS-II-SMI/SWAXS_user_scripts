def NEXAFS_S_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS arc to 60, then steps the X-ray energy across the
    #   sulfur edge (2440->2510 eV, 71 points) taking a WAXS image at each step.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy sweep in one line and writes the energy + beam intensity straight into
    #   the saved data and the file name (so you don't hand-build "{energy}eV_xbpm{xbpm}"
    #   or read xbpm3 yourself), and it handles the energy settling/feedback for you:
    #
    #     from smi_plans import nexafs_run         # do this once at the top of your session
    #     yield from bps.mv(waxs, 60)              # arc position, unchanged
    #     yield from nexafs_run(
    #         "NEXAFS_CdSe-CdS-NR-HT-BA-30s",      # the rest of the name is added automatically
    #         np.linspace(2440, 2510, 71),         # your energies, unchanged
    #         t=t,                                 # your exposure time, unchanged
    #         dets=[pil900KW],                     # current WAXS detector (see ⚠️ below)
    #     )
    #
    #   (Just a tidier option to try later — the script below still works EXCEPT for the
    #    two ⚠️ lines, which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan", so the plain
    #   call does nothing; (2) 'pil300KW' was removed from the beamline. See the ⚠️ notes
    #   on those lines below.
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_CdSe-CdS-NR-HT-BA-30s"

    energies = np.linspace(2440, 2510, 71)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="CB", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2480)
    yield from bps.mv(energy, 2470)
    yield from bps.mv(energy, 2450)


def NEXAFS_Ag_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS arc to 60, then steps the X-ray energy across the
    #   silver L edge (3480->3580 eV, 101 points), taking a WAXS image at each step.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does this energy sweep in one line and records the
    #   energy + beam intensity into the data and file name for you, and handles the energy
    #   settling/feedback (so the extra sleep below isn't needed once you switch):
    #
    #     from smi_plans import nexafs_run         # do this once at the top of your session
    #     yield from bps.mv(waxs, 60)
    #     yield from nexafs_run("NEXAFSAgL2_sleeptime_P3HT_ag1nm",
    #                           np.linspace(3480, 3580, 101), t=t, dets=[pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (The energy
    #   'sleep' is only flagged 💡 — it still works, just no longer needed.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFSAgL2_sleeptime_P3HT_ag1nm"

    energies = np.linspace(3480, 3580, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this settle wait once you migrate — move_energy_fb/energy_axis already wait for the energy to settle, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="CB", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 3580)
    yield from bps.mv(energy, 3560)
    yield from bps.mv(energy, 3530)


def NEXAFS_Cd_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: swings the WAXS arc to 60, then steps the X-ray energy across the
    #   cadmium edge (3500->3600 eV, 51 points), taking a WAXS image at each step.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does this in one line and records the energy + beam
    #   intensity into the data and file name for you (and handles energy settling/feedback):
    #
    #     from smi_plans import nexafs_run         # do this once at the top of your session
    #     yield from bps.mv(waxs, 60)
    #     yield from nexafs_run("NEXAFS_Cd_powder_test",
    #                           np.linspace(3500, 3600, 51), t=t, dets=[pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below.
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_Cd_powder_test"

    energies = np.linspace(3500, 3600, 51)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="CB", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 3580)
    yield from bps.mv(energy, 3560)
    yield from bps.mv(energy, 3530)


def time_resolved_S_edge(t=0.1, t1=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single time-resolved SAXS+WAXS exposure at a fixed energy
    #   (~2490 eV) — here the two det_exposure_time arguments differ (t for SAXS, t1 for
    #   WAXS) to give the slow detector a longer frame.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has time-series helpers that take repeated frames
    #   and record the beam readings + timestamps into the saved data and file name for you.
    #   For a quick one-shot at fixed conditions, time_series_run(..., n=1, t=...) works; for
    #   per-detector exposures, set them with the detector's own exposure plan first.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t1)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below.
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "P3HT-tr10s-UVon2_ai0.6"
    e = "2490.0"

    det_exposure_time(t, t1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t1)  — or at the prompt:  RE(det_exposure_time(t, t1)). (smi_plans technique runs set a single exposure via t=; for split SAXS/WAXS times use the detector exposure plan.)
    name_fmt = "{sample}_{energy}eV_bpm{xbpm}"
    sample_name = name_fmt.format(
        sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
    )
    sample_id(user_name="CB", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.count(dets, num=1)


def fly_scan_prsx(det, motor, t=0.1, t1=30, name="test"):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a "fly scan" — it moves a motor (piezo.x here) continuously from
    #   start to stop while the detectors expose, instead of stopping at fixed points.
    #   It does this by triggering the cameras by hand and busy-waiting until they finish.
    #
    # 💡 NEWER, EASIER WAY: this style triggers detectors and spins in a 'while' loop, which
    #   means no proper run/data documents are written. 'smi_plans' has continuous/kinetic
    #   helpers (e.g. time_series_run / kinetics_run, or a motor sweep via motor_axis) that
    #   coordinate the move and the exposures for you and record everything into the saved
    #   data. Worth migrating when you can; it'll save the metadata you're currently losing.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t1)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (Note: despite the
    #   name, this scans 'piezo.x' — the old 'prs' rotation stage is NOT used here.)
    # === end smi_plans note ================================================
    sample_id(user_name="CB", sample_name=name)

    start = piezo.x.position
    stop = piezo.x.position + 3000

    yield from bps.mv(motor, start)
    pil2M.stage()
    pil300KW.stage()  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    det_exposure_time(t, t1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t1)  — or at the prompt:  RE(det_exposure_time(t, t1)).

    print(f"Acquire time before staging: {t}")
    st = pil2M.trigger()
    st1 = pil300KW.trigger()  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera; check calibration).

    yield from list_scan([], motor, [start, stop])
    while not st.done or not st1.done:
        pass

    pil2M.unstage()
    pil300KW.unstage()  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera; check calibration).
    print(f"We are done after {t1}s of waiting")
    # yield from bps.mv(attn_shutter, 'Insert')


def giwaxs_S_edge_calvin(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence sulfur-edge scan — steps the X-ray energy through
    #   a few values and nudges piezo.x to a fresh spot at each energy (to avoid beam
    #   damage), taking SAXS+WAXS images.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can pair an energy sweep with a moving sample spot
    #   and record the energy + beam intensity into the data and file name for you (and it
    #   handles energy settling/feedback, so the sleep below isn't needed once you switch):
    #
    #     from smi_plans import acquire, energy_axis, motor_axis, saxs_waxs_dets
    #     xs = piezo.x.position
    #     yield from acquire("SAXS_WAXS_CdSe-CdS-NR-HT-BA-30s",
    #                        saxs_waxs_dets(),
    #                        [energy_axis([2460, 2475, 2476, 2490, 2510]),
    #                         motor_axis("x", piezo.x, np.linspace(xs, xs+1200, 5))],
    #                        reads=[xbpm3])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (The energy
    #   'sleep' is only flagged 💡 — still works, just no longer needed.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    name = "SAXS_WAXS_CdSe-CdS-NR-HT-BA-30s"
    energies = [2460, 2475, 2476, 2490, 2510]

    xs = piezo.x.position
    xss = np.linspace(xs, xs + 1200, 5)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)).
    name_fmt = "{sample}_{energy}eV_bpm{xbpm}"
    for e, xsss in zip(energies, xss):
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this settle wait once you migrate — move_energy_fb/energy_axis already wait for the energy to settle, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

        yield from bps.mv(piezo.x, xsss)
        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(
            sample=name, energy="%6.2f" % e, xbpm="%4.3f" % bpm
        )
        sample_id(user_name="CB", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2475)
    yield from bps.mv(energy, 2460)


def giwaxs_Ag_edge_calvin(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence silver-edge scan — steps the X-ray energy through
    #   a few values and nudges piezo.x to a fresh spot at each energy, taking SAXS+WAXS
    #   images.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' pairs an energy sweep with a moving sample spot and
    #   records energy + beam intensity into the data and file name for you (and handles the
    #   energy settling/feedback):
    #
    #     from smi_plans import acquire, energy_axis, motor_axis, saxs_waxs_dets
    #     xs = piezo.x.position
    #     yield from acquire("SAXS_WAXS_P3HT_1nmA_2",
    #                        saxs_waxs_dets(),
    #                        [energy_axis([3350, 3357, 3358, 3365]),
    #                         motor_axis("x", piezo.x, np.linspace(xs, xs+1200, 4))],
    #                        reads=[xbpm3])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below. (The energy
    #   'sleep' is only flagged 💡 — still works, just no longer needed.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    name = "SAXS_WAXS_P3HT_1nmA_2"
    energies = [3350, 3357, 3358, 3365]

    xs = piezo.x.position
    xss = np.linspace(xs, xs + 1200, 4)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)).
    name_fmt = "{sample}_{energy}eV_bpm{xbpm}"
    for e, xsss in zip(energies, xss):
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this settle wait once you migrate — move_energy_fb/energy_axis already wait for the energy to settle, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

        yield from bps.mv(piezo.x, xsss)
        bpm = xbpm3.sumX.value

        sample_name = name_fmt.format(
            sample=name, energy="%6.2f" % e, xbpm="%4.3f" % bpm
        )
        sample_id(user_name="CB", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 3400)
    yield from bps.mv(energy, 3430)
    yield from bps.mv(energy, 3460)
    yield from bps.mv(energy, 3500)
    yield from bps.mv(energy, 3530)


def single_giwaxs(t=1, name="test"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS+WAXS image at the current sample position and
    #   incident angle, under the name you pass in.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a one-shot acquire that records the beam
    #   readings into the saved data and file name for you. A single frame is just:
    #
    #     from smi_plans import acquire, saxs_waxs_dets
    #     yield from acquire(name, saxs_waxs_dets(), [], reads=[xbpm2, xbpm3])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time(t, t)' is now a "plan" (plain call
    #   does nothing); (2) 'pil300KW' was removed. See the ⚠️ notes below.
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)).

    sample_id(user_name="CB", sample_name=name)
    print(f"\n\t=== Sample: {name} ===\n")
    yield from bp.count(dets, num=1)


name_tot = "InP_HT1_1x28s_2x0s"


def night_shift_1():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight run-book: nudge the incident angle, run the GISAXS
    #   alignment routine, move to a fresh spot, then take one SAXS+WAXS image.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' bundles "align the sample, then measure it" into its
    #   grazing presets (e.g. giwaxs_run with align=...), and saves the alignment result
    #   with the data so you don't repeat it by hand each shift. See the giwaxs_run /
    #   align_sample helpers. (No urgent fix needed in this function itself, but the helper
    #   it calls, single_giwaxs, has ⚠️ items — see its own note.)
    # === end smi_plans note ================================================
    name = "GISAXS_" + name_tot + "_UV0s" + "_2450eV"
    yield from bps.mvr(piezo.th, -0.6)

    yield from alignement_gisaxs(0.4)

    yield from bps.mvr(piezo.x, 300)
    yield from bps.mvr(piezo.th, 0.6)

    yield from single_giwaxs(name=name)


def night_shift_2():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight run-book: do one fly scan, then every ~minute for 10
    #   minutes move to a fresh spot and take a SAXS+WAXS image (a simple time series).
    #
    # 💡 NEWER, EASIER WAY: this hand-rolls a timing loop with time.time(); 'smi_plans' has
    #   time-series/kinetics helpers (time_series_run / kinetics_run) that take frames on a
    #   schedule and record the timestamps + beam readings into the saved data for you.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the detector list passed below includes 'pil300KW', which
    #   was removed — see the ⚠️ note on that line. (The helpers it calls, fly_scan_prsx and
    #   single_giwaxs, also have their own ⚠️ items.)
    # === end smi_plans note ================================================
    name = name_tot + "_2450eV"
    yield from bps.mvr(piezo.x, 300)

    t0 = time.time()
    yield from fly_scan_prsx([pil2M, pil300KW], piezo.x, 0.1, 10, name=name)  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — pass that instead (different camera; check calibration).

    t1 = time.time()
    i = 0
    while t1 - t0 < 600:
        if (t1 - t0) // 60 != i:
            yield from bps.mvr(piezo.x, 300)
            i = (t1 - t0) // 60

            name = name_tot + "_2450eV" + "%smin" % i
            yield from single_giwaxs(name=name)

        yield from bps.sleep(1)
        t1 = time.time()


def night_shift_3():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight run-book: move to a fresh spot, then take one SAXS+WAXS
    #   image under a UV-exposure name.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a one-shot acquire (see the single_giwaxs note)
    #   that records the beam readings into the saved data and file name for you. (No urgent
    #   fix in this function itself, but the helper it calls, single_giwaxs, has ⚠️ items.)
    # === end smi_plans note ================================================
    name = "GISAXS_" + name_tot + "_UVexpo" + "_2450eV"

    yield from bps.mvr(piezo.x, 300)
    yield from single_giwaxs(name=name)

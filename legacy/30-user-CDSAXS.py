# pil300KW for waxs, pil2M for saxs
# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: the CD-SAXS / CD-GISAXS run-book — lots of routines that rock the
#   sample rotation stage through a fan of angles (the classic CD-SAXS "rock") while a
#   SAXS image is taken at each angle, plus pitch surveys, roughness ("rugo") scans, a few
#   tender-energy NEXAFS sweeps, and detector y-stitch scans.
#
# ⚠️ HEADS-UP, READ THIS FIRST: many routines here use names that the beamline RETIRED, so
#   they will error until fixed (each offending line is flagged with ⚠️ below):
#     - 'prs'  (the old rotation stage)  -> it's now 'stage.phi'        (rule D2)
#     - 'pil300KW' (old WAXS camera)     -> it's now 'pil900KW'         (rule D3)
#     - 'pil2M_bs_rod' (SAXS beamstop rod) -> it's now 'pil2M.beamstop.x_rod' (rule D5)
#     - bare 'det_exposure_time(...)' no longer sets the exposure unless run as a plan (D1)
#
# 💡 NEWER, EASIER WAY: the 'smi_plans' library (a helper library the beamline now
#   provides) has CD-SAXS building blocks that do the rock for you and record the angle,
#   beam intensity, detector distance, etc. straight INTO the saved data:
#     from smi_plans import cdsaxs_rock_run, cdsaxs_pitch_survey, cdsaxs_ystitch_run, \
#                           cd_gisaxs_rock_run, cdsaxs_bar, cdsaxs_dets, motor_axis
#   The rock is, e.g.:
#     yield from cdsaxs_rock_run("my_sample", th_start=-60, th_stop=60, num=121, t=1)
#   (it rocks 'stage.phi' internally, so you never touch 'prs'). For a whole bar of
#   samples use cdsaxs_bar with a SampleList; for the GISAXS phi/alpha-i variants use
#   cd_gisaxs_rock_run; for the up/down detector stitch use cdsaxs_ystitch_run.
#
#   See the per-function notes below. Your code still works as-is EXCEPT for the ⚠️ lines.
# === end smi_plans note ================================================


def cd_saxs(th_ini, th_fin, th_st, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar — moves to each defectivity-pitch sample, then rocks the
    #   rotation stage from th_ini to th_fin (th_st steps) taking 10 SAXS images at each angle.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' library does the rock for you (and rocks the
    #   correct current stage) and records the angle/beam into each image:
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_bar, SampleList
    #     yield from cdsaxs_rock_run("cdsaxs_ech03_..._pitch128",
    #                                th_start=th_ini, th_stop=th_fin, num=th_st, t=exp_t, n=10)
    #     # or do the whole bar at once:
    #     samples = SampleList.from_columns(name=sample, x=x, y=y)
    #     yield from cdsaxs_bar("cdsaxs", samples, th_start=th_ini, th_stop=th_fin,
    #                           num=th_st, t=exp_t)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan (⚠️ note below); (2) 'prs' was removed — it's now 'stage.phi' (⚠️
    #   note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = ["cdsaxs_ech03_defectivity_pitch128","cdsaxs_ech03_defectivity_pitch127","cdsaxs_ech03_defectivity_pitch124",
              "cdsaxs_ech03_defectivity_pitch121","cdsaxs_ech03_defectivity_pitch118","cdsaxs_ech03_defectivity_pitch115",
              "cdsaxs_ech03_defectivity_pitch112","cdsaxs_ech04_defectivity_pitch128","cdsaxs_ech04_defectivity_pitch127",
              "cdsaxs_ech04_defectivity_pitch124","cdsaxs_ech04_defectivity_pitch121","cdsaxs_ech04_defectivity_pitch118",
              "cdsaxs_ech04_defectivity_pitch115","cdsaxs_ech04_defectivity_pitch112","cdsaxs_ech11b_defectivity_pitch128",
              "cdsaxs_ech11b_defectivity_pitch127","cdsaxs_ech11b_defectivity_pitch124","cdsaxs_ech11b_defectivity_pitch121",
              "cdsaxs_ech11b_defectivity_pitch118","cdsaxs_ech11b_defectivity_pitch115","cdsaxs_ech11b_defectivity_pitch112"]
    x = [-41100,-38550,-34050,-29550,-25050,-20550,-16050,-11150,-9650,-5150,-650,3850,8350,12850,17000,18500,23000,27500,32000,36500, 41000]
    y = [  2000,  2000,  2000,  2000,  2000,  2000,  2000,2000,2000,2000,2000,2000,2000,2000,3900,3900,3900,3900,3900,3900,3900,    ]    
    det = [pil2M]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for xs, ys, sample in zip(x, y, sample):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        for theta in np.linspace(th_ini, th_fin, th_st):
            yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
            name_fmt = "{sample}_{th}deg"

            sample_name = name_fmt.format(sample=sample, th="%2.2d" % theta)
            sample_id(user_name="PG", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(det, num=10)


def cd_saxs_old(sample, x, y, num=1, exp_t=1, step=121):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single-sample CD-SAXS rock — moves to (x, y), then rocks the
    #   rotation stage from -60 to 60 deg (step points), taking 'num' SAXS images per angle.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run(sample, th_start=-60, th_stop=60, num=step, t=exp_t, n=num)
    #   (it rocks 'stage.phi' for you and records the angle/beam into each image.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) 'prs' was removed — it's now 'stage.phi'. (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(piezo.x, x)
    yield from bps.mv(piezo.y, y)

    for i, theta in enumerate(np.linspace(-60, 60, step)):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_{num}_{th}deg"

        sample_name = name_fmt.format(sample=sample, num="%2.2d"%i, th="%2.2d"%theta)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=num)
        yield from bps.sleep(1)


def cdsaxs_all_pitch(sample, x, y, num=1, exp_t=1, step=121):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a pitch survey — steps x across a row of grating pitches (p112..p128)
    #   and does a full CD-SAXS rock (via cd_saxs_new) at each pitch.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_pitch_survey
    #     yield from cdsaxs_pitch_survey(sample, x0=x, dx=1500,
    #                                    pitches=["p112nm", ..., "p128nm"],
    #                                    th_start=-60, th_stop=60, num=step, t=exp_t)
    #   (it steps to each pitch, rocks 'stage.phi', and records pitch/angle into the data.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (The 'prs' rock is inside cd_saxs_new — fix it there.)
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p112nm","p113nm","p114nm","p115nm","p116nm","p117nm","p118nm","p119nm","p120nm","p121nm","p122nm","p123nm","p124nm","p125nm",
               "p126nm","p127nm","p128nm"]
    x_off = [0,1500,3000,4500,6000,7500,9000,10500,12000,13500,15000,16500,18000,19500,21000,22500,24000]
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, pitch in zip(x_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y, num=1, exp_t=exp_t, step=step)


def night_patrice(exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight run-book — moves to a series of sample/background spots
    #   and calls the CD-SAXS pitch/rock/roughness routines on each.
    #
    # 💡 NEWER, EASIER WAY: this is glue that calls the routines below. Once those use the
    #   'smi_plans' CD-SAXS helpers (cdsaxs_rock_run / cdsaxs_pitch_survey / cdsaxs_bar),
    #   this stays a thin sequence of calls. Nothing here is broken on its own — but the
    #   routines it calls have ⚠️ items (see their notes). (internal: Tier 1 — run-book.)
    # === end smi_plans note ================================================
    numero = 6
    det = [pil2M]

    # names = ['champs00', 'bkg_champs00','champs05','bkg_champs05','champs0-4','bkg_champs0-4','champs0-3', 'bkg_champs0-3']
    # xs = [-41100, -41100, 14100, 14100, -36450, -36550, -10250, -10250]
    # ys = [-7500, -8500, -7000, -8000, 5450, 6450, 5500, 6400]
    names = ["champs0-3", "bkg_champs0-3"]

    xs = [2220, 2220]
    ys = [6470, 7470]

    for name, x, y in zip(names, xs, ys):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        numero += 1
        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(sample=name, numb=numero)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from cdsaxs_important_pitch(sample_name, x, y, num=1)
        # numero+=1
        # yield from cdsaxs_important_pitch(sample_name, x, y, num=1)

    names = ["champs00"]
    xs = [-14380]
    ys = [-6200]

    numero += 1
    name_fmt = "{sample}_num{numb}"
    sample_name = name_fmt.format(sample=names[0], numb=numero)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from cdsaxs_important_pitch(sample_name, xs[0], ys[0], num=1)

    numero += 1
    name_fmt = "{sample}_num{numb}"
    sample_name = name_fmt.format(sample=names[0], numb=numero)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from cdsaxs_important_pitch(sample_name, xs[0], ys[0], num=1)

    names = ["champs00", "bkg_champs00"]
    xs = [-14380, -14380]
    ys = [-6200, -7200]

    for name, x, y in zip(names, xs, ys):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        numero += 1

        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(sample=name, numb=numero)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from cdsaxs_all_pitch(sample_name, x, y, num=1, step=61)

    numero += 1
    name_fmt = "{sample}_offset300_num{numb}"
    sample_name = name_fmt.format(sample=name, numb=numero)
    yield from cd_saxs_new(sample_name, xs[0], ys[0] + 300, num=1, exp_t=exp_t)

    numero += 1
    name_fmt = "{sample}_offset-300_num{numb}"
    sample_name = name_fmt.format(sample=name, numb=numero)
    yield from cd_saxs_new(sample_name, xs[0], ys[0] - 300, num=1, exp_t=exp_t)

    numero += 1
    name_fmt = "{sample}_num{numb}"
    sample_name = name_fmt.format(sample=name, numb=numero)
    yield from mesure_rugo(sample_name, xs[0], ys[0], num=200, exp_t=exp_t)

    numero += 1
    name_fmt = "{sample}_num{numb}"
    sample_name = name_fmt.format(sample=name, numb=numero)
    yield from mesure_rugo(sample_name, xs[1], ys[1], num=200, exp_t=exp_t)


def scan_boite_pitch(exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a pitch survey for three samples — at each sample it steps x across a
    #   row of pitches (128->112 nm) and takes 10 SAXS images at each pitch.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_pitch_survey
    #     yield from cdsaxs_pitch_survey(sample, x0=x, dx=1500, pitches=..., t=exp_t)
    #   (it steps to each pitch and records the pitch/position into each image.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = ["Echantillon03_defectivity","Echantillon04_defectivity","Echantillon11b_defectivity"]
    x = [-40050, -11150, 17000]
    y = [2000, 2000, 3900]
    det = [pil2M]

    pitches = np.linspace(128, 112, 17)

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for xs, ys, sample in zip(x, y, sample):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yield from bps.mvr(piezo.x, -1500)
        for i, pitch in enumerate(pitches):
            yield from bps.mvr(piezo.x, 1500)
            name_fmt = "{sample}_{pit}nm"

            sample_name = name_fmt.format(sample=sample, pit="%3.3d" % pitch)
            sample_id(user_name="PG", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(det, num=10)


def macro_dinner():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tiny macro — runs the pitch survey, then a CD-SAXS rock.
    # 💡 NEWER, EASIER WAY: keep it as glue; once scan_boite_pitch / cd_saxs use the
    #   'smi_plans' CD-SAXS helpers, this stays a two-line sequence. (Nothing here is broken
    #   on its own; the called routines have ⚠️ items — see their notes.)
    # === end smi_plans note ================================================
    yield from scan_boite_pitch(1)
    yield from cd_saxs(-60, 60, 121, 2)


def NEXAFS_Ti_edge(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS sweep across the titanium edge (4950->5050 eV,
    #   101 points), taking a WAXS image at each energy, then stepping the energy back down.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run
    #     yield from nexafs_run("NEXAFS_echantillon2_Tiedge_ai1p4",
    #                           np.linspace(4950, 5050, 101), t=t,
    #                           dets=[pil900KW], geometry="transmission")
    #   (it sets the exposure, manages the energy move + beam feedback, and records the
    #    energy/beam into each image. You can drop the manual step-back at the end.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the WAXS detector 'pil300KW' was retired — it's now
    #   'pil900KW'; (2) 'det_exposure_time' no longer sets the exposure unless run as a plan
    #   (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_echantillon2_Tiedge_ai1p4"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis already step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 5010)
    yield from bps.mv(energy, 4990)
    yield from bps.mv(energy, 4970)
    yield from bps.mv(energy, 4950)


def NEXAFS_SAXS_Ti_edge(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS+SAXS sweep across the titanium edge
    #   (4950->5050 eV, 101 points), taking a WAXS+SAXS image at each energy, then stepping
    #   the energy back down.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run
    #     yield from nexafs_run("NEXAFS_SAXS_echantillon13realign_ai1p75_Tiedge",
    #                           np.linspace(4950, 5050, 101), t=t,
    #                           dets=[pil900KW, pil2M], geometry="transmission")
    #   (sets the exposure, manages the energy move + beam feedback, records energy/beam,
    #    and you can drop the manual step-back at the end.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time' no longer sets the exposure unless run as a plan (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_SAXS_echantillon13realign_ai1p75_Tiedge"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis already step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 5010)
    yield from bps.mv(energy, 4990)
    yield from bps.mv(energy, 4970)
    yield from bps.mv(energy, 4950)


def GISAXS_scan_boite(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS line scan — steps x across the sample (81 points) at fixed
    #   incident angle and takes one SAXS image at each position.
    #
    # 💡 NEWER, EASIER WAY: stepping x and snapping is a "map line" in the 'smi_plans'
    #   library, which records the position/beam into each image:
    #     from smi_plans import map_line_run
    #     yield from map_line_run("Echantillon13realign_gisaxs_...", piezo.x, 55900, 31900, 81,
    #                             t=t, dets=[pil2M])
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = "Echantillon13realign_gisaxs_scanpolyperiod_e4950eV_ai1p75"
    x = np.linspace(55900, 31900, 81)

    det = [pil2M]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    for k, xs in enumerate(x):
        yield from bps.mv(piezo.x, xs)

        name_fmt = "{sample}_pos{pos}"
        sample_name = name_fmt.format(sample=sample, pos="%2.2d" % k)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=1)


def fly_scan_ai(det, motor, cycle=1, cycle_t=10, phi=-0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a "fly" rock — it arms the detector with a long exposure, then sweeps
    #   the motor back and forth a few times while one long frame integrates, busy-waiting
    #   until the frame is done.
    #
    # 💡 NEWER, EASIER WAY: this is the old hand-rolled style — it pokes the camera directly
    #   (det.cam.acquire_time.put / det.trigger) and busy-waits, which means Bluesky records
    #   nothing about the scan (no run, no saved angle/beam). The 'smi_plans' CD-SAXS rock
    #   does a proper rocking acquisition for you and saves the angle and beam into the data:
    #     from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run("my_sample", th_start=phi-30, th_stop=phi+30, num=...,
    #                                t=cycle*cycle_t)
    #   (it manages staging/triggering and the rotation stage for you — no busy-wait, and
    #    the result lands in the database like every other scan.)
    #
    #   (Nothing here errors, but it doesn't produce saved documents; switching to
    #    cdsaxs_rock_run is strongly recommended. (internal: Tier 0 — cam.put + busy-wait,
    #    writes nothing to the database.))
    # === end smi_plans note ================================================
    start = phi - 30
    stop = phi + 30
    acq_time = cycle * cycle_t
    yield from bps.mv(motor, start)
    # yield from bps.mv(attn_shutter, 'Retract')
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
    # yield from bps.mv(attn_shutter, 'Insert')


def sample_patrice_2020_3(exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book for several "champs" samples — moves to each, runs the
    #   CD-SAXS pitch/roughness/direct-beam routines, then switches to alignment mode and
    #   measures the direct beam.
    #
    # 💡 NEWER, EASIER WAY: this is glue calling the routines below; once those use the
    #   'smi_plans' CD-SAXS helpers (cdsaxs_pitch_survey / cdsaxs_bar) and align_sample,
    #   this stays a thin sequence. Nothing here is broken on its own — but the routines it
    #   calls have ⚠️ items (see their notes). (internal: Tier 1 — run-book.)
    # === end smi_plans note ================================================
    numero = 1
    det = [pil2M]
    # wafer = 'wafer16'
    # names = ['champs5', 'champs5_bkg', 'champs4', 'champs4_bkg', 'champs3', 'champs3_bkg']
    # names = ['champs-1', 'champs-1_bkg', 'champs-2', 'champs-2_bkg', 'champs-3', 'champs-3_bkg']

    wafer = "wafer25"
    # names = ['champs-1', 'champs-1_bkg', 'champs-2', 'champs-2_bkg', 'champs-3', 'champs-3_bkg']
    names = ["champs1", "champs1_bkg", "champs0", "champs0_bkg"]

    xs = [-3400, -3400, 22650, 22650]
    ys = [6360, 7300, 6410, 7300]
    zs = [1800, 1800, 1470, 1470]

    for name, x, y, z in zip(names, xs, ys, zs):
        yield from bps.mv(piezo.z, z)
        numero += 1
        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(wafer=wafer, sample=name, numb=numero)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        if "bkg" in name:
            yield from cdsaxs_important_pitch(sample_name, x, y, num=1)
        else:
            yield from cdsaxs_important_pitch(sample_name, x, y, num=2)

    names = ["champs2","champs2_bkg","champs1","champs1_bkg","champs0","champs0_bkg"]

    xs = [-29420, -29420, -3400, -3400, 22650, 22650]
    ys = [6460, 7300, 6360, 7300, 6410, 7300]
    zs = [2130, 2130, 1800, 1800, 1470, 1470]

    for name, x, y, z in zip(names, xs, ys, zs):
        yield from bps.mv(piezo.z, z)
        numero += 1
        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(sample=name, numb=numero)

        if "bkg" in name:
            yield from mesure_rugo(sample_name, x, y, num=10, exp_t=exp_t)
        else:
            yield from mesure_rugo(sample_name, x, y, num=100, exp_t=exp_t)

    yield from bps.mvr(pil2M_pos.x, -5)
    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, x, y, z in zip(names, xs, ys, zs):
        numero += 1
        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(sample=name, numb=numero)
        yield from bps.mv(piezo.z, z)
        yield from mesure_db(sample_name, x, y, num=1, exp_t=1)

    yield from smi.modeMeasurement()
    yield from bps.mvr(pil2M_pos.x, 5)


def cdsaxs_important_pitch(sample, x, y, num=1, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: measures two key pitches on a sample — steps to each (x/y offset) and
    #   does a full CD-SAXS rock (via cd_saxs_new) at each.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_pitch_survey
    #     yield from cdsaxs_pitch_survey(sample, x0=x, pitches=["p113nm","p100nm"], t=exp_t)
    #   (steps to each pitch, rocks 'stage.phi', records pitch/angle into the data.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line, which needs a fix now.
    #    The 'prs' rock is inside cd_saxs_new — fix it there.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p113nm", "p100nm"]

    if "bkg" in sample:
        x_off = [0, 0]
        y_off = [0, -13300]
    else:
        x_off = [0, 0]
        y_off = [0, -10500]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y + y_of, num=num, exp_t=exp_t)


def mesure_rugo(sample, x, y, num=200, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a line-edge-roughness ("rugo") scan — parks the rotation stage near 0,
    #   then takes many SAXS images at one spot for the "up" and "down" detector positions.
    #
    # 💡 NEWER, EASIER WAY: the up/down detector-position roughness scan is the 'smi_plans'
    #   y-stitch helper, which moves the SAXS detector and records the position/beam for you:
    #     from smi_plans import cdsaxs_ystitch_run
    #     yield from cdsaxs_ystitch_run(sample, num=num, t=exp_t)
    #   (Note: there is a SECOND function named 'mesure_rugo' lower in this file; in Python
    #    the later one wins, so check which you actually call.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' was removed — it's now 'stage.phi'; (2)
    #   'det_exposure_time' no longer sets the exposure unless run as a plan (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    print(sample)
    pitches = ["p100nm"]

    if "bkg" in sample:
        x_off = [0]
        y_off = [-13300]
    else:
        x_off = [0]
        y_off = [-10500]

    yield from bps.mv(prs, -1)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_rugo_{pit}_up"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        print(sample_name)
        sample_id(user_name="PG", sample_name=sample_name)

        yield from bp.count([pil2M], num=num)

    yield from bps.mvr(pil2M_pos.y, 4.3)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)
        name_fmt = "{sample}_rugo_{pit}_down"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        sample_id(user_name="PG", sample_name=sample_name)
        yield from bp.count([pil2M], num=num)

    yield from bps.mvr(pil2M_pos.y, -4.3)


def mesure_db(sample, x, y, num=1, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a direct-beam measurement — parks the rotation stage near 0 and takes
    #   one attenuated SAXS image (for normalization/flux).
    #
    # 💡 NEWER, EASIER WAY: a single attenuated direct-beam shot is the 'smi_plans'
    #   commissioning helper 'direct_beam_scan_run' (it records the beam/attenuation), or a
    #   one-line transmission_run if you just want one frame.
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' was removed — it's now 'stage.phi'; (2)
    #   'det_exposure_time' no longer sets the exposure unless run as a plan (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p100nm"]
    if "bkg" in sample:
        x_off = [0]
        y_off = [-13300]
    else:
        x_off = [0]
        y_off = [-10500]
    yield from bps.mv(prs, -1)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_db_{pit}_att9x60umSn"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        sample_id(user_name="PG", sample_name=sample_name)

        yield from bp.count([pil2M], num=1)


def NEXAFS_P_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tender-energy NEXAFS sweep across the phosphorus edge (2140->2200 eV,
    #   61 points), taking a WAXS image at each energy, then stepping the energy back down.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import nexafs_run
    #     yield from nexafs_run("nexafs_s4_wa0_0.5deg", np.linspace(2140, 2200, 61), t=t,
    #                           dets=[pil900KW], geometry="transmission")
    #   (sets the exposure, manages the energy move + beam feedback, records energy/beam —
    #    so you can drop the per-step sleeps and the manual step-back at the end.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines; the 💡 lines are
    #    scaffolding you can simply delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2)
    #   'det_exposure_time' no longer sets the exposure unless run as a plan (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 0)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "nexafs_s4_wa0_0.5deg"

    energies = np.linspace(2140, 2200, 61)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)

        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.2f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2190)  # 💡 smi_plans: you can drop this stepped energy walk-back (and its sleeps) — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2180)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2170)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2160)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2150)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2140)
    yield from bps.sleep(2)


def cd_saxs_new2(th_ini, th_fin, th_st, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS rock for one sample and its background — rocks the rotation
    #   stage (with a -4 deg zero offset) from th_ini to th_fin and takes a SAXS image at
    #   each angle, for the sample then the background position.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run("sample-33", th_start=th_ini-4, th_stop=th_fin-4,
    #                                num=th_st, t=exp_t)   # then again for the bkg position
    #   (rocks 'stage.phi', records the angle/beam into each image.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) both 'prs' lines were removed — it's now 'stage.phi' (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = "sample-33"
    det = [pil2M]
    yield from bps.mv(piezo.y, 1000)

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    theta_zer=-4

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta+theta_zer)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_8.3m_16.1keV_num{num}_{th}deg"

        sample_name = name_fmt.format(
            sample=sample, num="%2.2d" % num, th="%2.2d" % theta
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=1)

    sample = "sample-33_bkg"
    yield from bps.mv(piezo.y, -3600)

    theta_zer=-4

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta+theta_zer)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_8.3m_16.1keV_num{num}_{th}deg"

        sample_name = name_fmt.format(
            sample=sample, num="%2.2d" % num, th="%2.2d" % theta
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        
        yield from bps.sleep(2)
        yield from bp.count(det, num=1)


def rugo_contact(exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes 50 SAXS images at one spot (a contact-roughness measurement).
    # 💡 NEWER, EASIER WAY: a simple repeated count is one call in 'smi_plans':
    #     from smi_plans import time_series_run
    #     yield from time_series_run("sample-10_rugo_...", num=50, t=exp_t, dets=[pil2M])
    #   (it sets the exposure and records the beam into each frame.)
    #   (Your script below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = "sample-10_rugo_8.3m_16.1keV_5s"
    det = [pil2M]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name="PG", sample_name=sample)

    yield from bp.count(det, num=50)


def cd_saxs_new(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil2M]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: THE core CD-SAXS rock used throughout this file — rocks the rotation
    #   stage from th_ini to th_fin (th_st steps) and takes 'nume' SAXS images at each angle,
    #   writing the beam-monitor value into the file name.
    #
    # 💡 NEWER, EASIER WAY: this is exactly what the 'smi_plans' rock helper does in one
    #   line, and it records the angle/beam into the data (so it doesn't have to be packed
    #   into the file name, and the correct current rotation stage is used):
    #     from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run(sample, th_start=th_ini, th_stop=th_fin, num=th_st,
    #                                t=exp_t, n=nume)
    #   Switching the callers to cdsaxs_rock_run (or cdsaxs_bar for a whole sample list)
    #   removes the 'prs' problem everywhere at once.
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) 'prs' was removed — it's now 'stage.phi' (⚠️ notes below). Because
    #   nearly every routine here calls cd_saxs_new, fixing the rock here (or moving to
    #   cdsaxs_rock_run) fixes them all. (internal: Tier 1.)
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_9.2m_16.1keV_num{num}_{th}deg_bpm{bpm}"
        sample_name = name_fmt.format(sample=sample, num="%5.2d"%num, th="%2.2d"%theta, bpm="%1.3f"%xbpm3.sumX.get()) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)


def night_1_cdsaxs(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar — moves to each sample (x/y/z/chi/theta and hexapod x),
    #   then does a full CD-SAXS rock (via cd_saxs_new) at each, with more frames on signal
    #   samples than on backgrounds.
    #
    # 💡 NEWER, EASIER WAY: running a CD-SAXS bar is one call in 'smi_plans'; give it your
    #   samples as a SampleList and it visits, rocks 'stage.phi', and records angle/position
    #   into each image:
    #     from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("night_1", samples, th_start=-60, th_stop=60, num=121, t=t)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line; the 'prs' rock is
    #    inside cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names = ['w08_-3-1', 'w08_-3-1_bkg', 'w08_1-1', 'w08_1-1_bkg', 'w08_2-1', 'w08_2-1_bkg', 
             'w08_-1-1', 'w08_-1-1_bkg', 'w08_0-1', 'w08_0-1_bkg', 'w08_3-1', 'w08_3-1_bkg', 'ech_tim_ref', 'ech_tim_ref_bkg']
    x =     [    -32000,         -32000,     -1400,         -1400,     21400,         21400, 
                 -32900,         -32900,     -9800,         -9800,     20700,         20700,         40000,             40000]
    x_hexa =[       0.1,            0.1,       0.3,           0.3,       0.5,           0.5, 
                    0.5,            0.5,       0.5,           0.5,       0.5,           0.5,           0.5,               0.5]
    y=      [      8900,           6500,      8900,          6000,      8000,          5900, 
                  -7000,          -9700,     -7000,         -9700,     -7000,        -10500,         -8000,            -10000]
    z=      [     10800,          10800,      9600,          9600,      8900,          8900, 
                  11000,          11000,      9700,          9700,      8900,          8900,          7900,              7900]
    chi=[           0.3,            0.3,      -0.2,          -0.2,      -0.2,          -0.2, 
                  -0.05,          -0.05,     -0.05,         -0.05,      -0.2,          -0.2,          -0.5,               0.5]
    th =[          -0.4,           -0.4,      -0.4,          -0.4,      -0.4,          -0.4,
                 -0.633,         -0.633,     -0.43,         -0.43,       0.3,           0.3,          -2.7,              -2.7]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)

        if 'bkg' in name:
            num=1
        else:
            num=2

        yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num)



def cdsaxs_echolivier(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (Echantillon Olivier) — moves to each sample and does a
    #   full CD-SAXS rock (via cd_saxs_new), with more frames on a couple of key samples.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("echolivier", samples, th_start=-60, th_stop=60, num=121, t=t)
    #   (visits each sample, rocks 'stage.phi', records angle/position into each image.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # names = ['w03_c0_p113', 'w03_c0_p113_bkg', 'w03_c0_p118', 'w03_c0_p118_bkg', 'w03_c0_p100', 'w03_c0_p100_bkg',
    #          'w03_c1_p113', 'w03_c1_p113_bkg', 'w03_c1_p118', 'w03_c1_p118_bkg', 'w03_c1_p100', 'w03_c1_p100_bkg',
    #          'w03_c2_p113', 'w03_c2_p113_bkg', 'w03_c2_p118', 'w03_c2_p118_bkg', 'w03_c2_p100', 'w03_c2_p100_bkg']

    # x =     [       -34900,            -34900,        -10800,            -10800,        -32900,            -32900, 
    #                  -8900,             -8900,         15200,             15200,         -6900,             -6900, 
    #                  17100,             17100,         41150,             41150,         19100,             19100]
    # x_hexa =[          0.5,               0.5,           0.5,               0.5,           0.5,               0.5, 
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5,
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5]
    # y=      [        -4700,             -5400,         -4700,             -5400,          5300,              7600, 
    #                  -4700,             -5400,         -4800,             -5500,          5300,              7600,
    #                  -4800,             -5500,         -4900,             -5600,          5300,              7600,]
    # z=      [        11000,             11000,         10050,             10050,         11000,             11000, 
    #                  10050,             10050,          9100,              9100,         10050,             10050,
    #                   9100,              9100,          8080,              8080,          9100,              9100,]
    # chi=[                0,                 0,             0,                 0,             0,                 0, 
    #                      0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0]
    # th =[                0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0]

    # names = ['w03_c3_p113', 'w03_c3_p113_bkg', 'w03_c3_p128', 'w03_c3_p128_bkg', 'w03_c3_p100', 'w03_c3_p100_bkg',
    #          'w03_c4_p113', 'w03_c4_p113_bkg', 'w03_c4_p128', 'w03_c4_p128_bkg', 'w03_c4_p100', 'w03_c4_p100_bkg',
    #          'w03_c5_p113', 'w03_c5_p113_bkg', 'w03_c5_p128', 'w03_c5_p128_bkg', 'w03_c5_p100', 'w03_c5_p100_bkg']

    # x =     [       -35150,            -35150,        -12500,            -12500,        -34150,            -34150, 
    #                  -9100,             -9100,         13500,             13500,         -8600,             -8600, 
    #                  16950,             16950,         39100,             39100,         19100,             19100]
    # x_hexa =[          0.5,               0.5,           0.5,               0.5,           0.5,               0.5, 
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5,
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5]
    # y=      [        -4300,             -5100,         -4400,             -5100,          7000,              8100, 
    #                  -4300,             -5100,         -4400,             -5200,          7000,              8100,
    #                  -4400,             -5200,         -4500,             -5200,          7000,              8100]
    # z=      [        10900,             10900,         10050,             10050,         10900,             10900, 
    #                  10050,             10050,          9150,              9150,         10050,             10050,
    #                   9150,              9150,          8080,              8080,          9150,              9150]
    # chi=[                0,                 0,             0,                 0,             0,                 0, 
    #                      0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0]
    # th =[                0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0,
    #                      0,                 0,             0,                 0,             0,                 0]

    # names = ['w03_c-3_p113', 'w03_c-3_p113_bkg', 'w03_c-3_p128', 'w03_c-3_p128_bkg', 'w03_c-3_p100', 'w03_c-3_p100_bkg',
    #          'w03_c-2_p113', 'w03_c-2_p113_bkg', 'w03_c-2_p128', 'w03_c-2_p128_bkg', 'w03_c-2_p100', 'w03_c-2_p100_bkg',
    #          'w03_c-1_p113', 'w03_c-1_p113_bkg', 'w03_c-1_p128', 'w03_c-1_p128_bkg', 'w03_c-1_p100', 'w03_c-1_p100_bkg']

    # x =     [       -35250,            -35250,        -12750,            -12750,        -33750,            -33750, 
    #                  -9300,             -9300,         13500,             13500,         -7800,             -7800, 
    #                  16700,             16700,         39100,             39100,         18200,             18200]
    # x_hexa =[          0.5,               0.5,           0.5,               0.5,           0.5,               0.5, 
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5,
    #                    0.5,               0.5,           0.5,               0.5,           0.5,               0.5]
    # y=      [        -4400,             -5300,         -4500,             -5400,          6200,              7800, 
    #                  -4600,             -5400,         -4700,             -5500,          6200,              7800,
    #                  -4700,             -5500,         -4700,             -5700,          6200,              7800]
    # z=      [        10900,             10900,         10000,             10000,         10900,             10900, 
    #                  10000,             10000,          9100,              9100,         10050,             10050,
    #                   9100,              9100,          8100,              8100,          9100,              9100]
    # chi=[              0.1,               0.1,           0.1,               0.1,           0.1,               0.1, 
    #                    0.1,               0.1,           0.1,               0.1,           0.1,               0.1,
    #                    0.1,               0.1,           0.1,               0.1,           0.1,               0.1]
    # th =[             -0.3,              -0.3,          -0.3,              -0.3,          -0.3,              -0.3,
    #                   -0.3,              -0.3,          -0.3,              -0.3,          -0.3,              -0.3,
    #                   -0.3,              -0.3,          -0.3,              -0.3,          -0.3,              -0.3]

    names = ['w03_c0_p113', 'w03_c0_p113_bkg', 'w03_c1_p113', 'w03_c1_p113_bkg', 'w03_c2_p113', 'w03_c2_p113_bkg']
    x =     [       -35050,            -35050,         -9150,             -9150,         16950,             16950]
    x_hexa =[          0.5,               0.5,           0.5,               0.5,           0.5,               0.5]
    y=      [        -4400,             -5300,         -4400,             -5400,         -4500,             -5400]
    z=      [        10900,             10900,         10000,             10000,          9100,              9100]
    chi=[            -0.05,             -0.05,         -0.05,             -0.05,         -0.05,             -0.05]
    th =[              0.3,               0.3,           0.3,               0.3,           0.3,               0.3]


    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)

        if 'w03_c-3_p113' in name or 'w03_c-1_p113' in name:
            num=10
        else:
            num=2

        yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num)



#sdd=   [8.3, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.6]
#bs_pos=[1.7, 1.7, 1.5, 1.5, 1.9, 2.1, 2.1, 2.1, 2.1]

def rugo(t=1, sdd='8.30', num=10, name='test', ys=[0, 0], th=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a roughness ("rugo") scan at one detector distance — takes 'num' SAXS
    #   images at the sample and at a background y, each for an "up" and "down" SAXS detector
    #   position (a y-stitch), naming by SDD and theta.
    #
    # 💡 NEWER, EASIER WAY: the up/down detector-position stitch is the 'smi_plans' helper
    #   'cdsaxs_ystitch_run', which moves the SAXS detector and records the position/beam
    #   into each image (so you don't hand-build the _up/_down names):
    #     from smi_plans import cdsaxs_ystitch_run
    #     yield from cdsaxs_ystitch_run(name, num=num, t=t)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(piezo.y, ys[0])
    name_fmt = "{name}_rugo_{sdd}m_16.1keV_th{th}deg_dn"
    sample_name = name_fmt.format(name=name, sdd=sdd, th="%1.1f"%th)
    sample_id(user_name="PG", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bps.mv(pil2M_pos.y, -3.7)
    yield from bp.count(det, num=num)


    name_fmt = "{name}_rugo_{sdd}m_16.1keV_th{th}deg_up"
    sample_name = name_fmt.format(name=name, sdd=sdd, th="%1.1f"%th)
    sample_id(user_name="PG", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bps.mv(pil2M_pos.y, -8.0)
    yield from bp.count(det, num=num)


    yield from bps.mv(piezo.y, ys[1])

    name_fmt = "{name}_bkg_rugo_{sdd}m_16.1keV_th{th}deg_up"
    sample_name = name_fmt.format(name=name, sdd=sdd, th="%1.1f"%th)
    sample_id(user_name="PG", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bps.mv(pil2M_pos.y, -8.0)
    yield from bp.count(det, num=num)
    

    name_fmt = "{name}_bkg_rugo_{sdd}m_16.1keV_th{th}deg_dn"
    sample_name = name_fmt.format(name=name, sdd=sdd, th="%1.1f"%th)
    sample_id(user_name="PG", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bps.mv(pil2M_pos.y, -3.7)
    yield from bp.count(det, num=num)



def measure_pitch(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a pitch scan at a fixed rotation angle — parks the rotation stage,
    #   steps x across a row of pitches (112..128), and takes one SAXS image at each.
    #
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_pitch_survey
    #     yield from cdsaxs_pitch_survey("w03_c-2", x0=-10750, dx=1500, pitches=..., t=t)
    #   (steps to each pitch and records pitch/position into each image; uses 'stage.phi'.)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line, which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' was removed — it's now 'stage.phi' (⚠️ note below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    name_fmt = "w03_c-2_p{pitch}_8.3m_16.1keV_0deg"
    pitches = np.linspace(112, 128, 17)
    xs = -10750+1500*np.linspace(0, 16, 17)

    yield from bps.mv(prs, -5.25)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bps.mv(piezo.y, -4500)

    for pitch, x in zip(pitches, xs):
        yield from bps.mv(piezo.x, x)
        yield from bps.sleep(2)

        sample_name = name_fmt.format(pitch="%3.3d"%pitch)
        print(sample_name)
        sample_id(user_name="PG", sample_name=sample_name)
        
        yield from bp.count(det, num=1)


# def run_night2(t=1):
#     # yield from cdsaxs_echolivier(1)
    
#     # proposal_id("2022_3", "311003_Reche1")
#     # yield from bps.mv(prs, -5.25)
#     # yield from bps.mv(piezo.x, -35250)
#     # yield from bps.mv(piezo.z, 10900)

#     # yield from rugo(t=1, sdd='8.30', num=100, name='w03_c-3_p113', ys=[-4400, -5300])
    
#     # yield from bps.mv(piezo.x, 16700)
#     # yield from bps.mv(piezo.z, 9100)
#     # yield from rugo(t=1, sdd='8.30', num=100, name='w03_c-1_p113', ys=[-4700, -5500])

#     # proposal_id("2022_3", "311003_Dubreuil1")
#     # yield from measure_pitch(1)



def run_day2(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book — runs roughness scans at two rotation angles, then loops
    #   the SAXS detector through a list of distances (moving the beamstop rod with it) and
    #   repeats the roughness scan at each distance.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' the roughness/stitch is cdsaxs_ystitch_run, and
    #   the beamstop rod has convenience helpers (you don't move the rod motor by hand):
    #     from smi_plans import cdsaxs_ystitch_run
    #     yield from pil2M.insert_beamstop('rod')      # or pil2M.restore_beamstop()
    #     yield from cdsaxs_ystitch_run(name, num=num, t=t)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) every 'prs' line was removed — it's now 'stage.phi';
    #   (2) 'pil2M_bs_rod' (the SAXS beamstop rod) was renamed — it's now
    #   'pil2M.beamstop.x_rod' (⚠️ notes below). (internal: Tier 1 — run-book.)
    # === end smi_plans note ================================================

    proposal_id("2022_3", "311003_Reche1")

    yield from bps.mv(prs, -5.25)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bps.mv(piezo.x, -35250)
    yield from bps.mv(piezo.z, 10900)
    yield from rugo(t=1, sdd='8.30', num=100, name='w03_c-3_p113', ys=[-4400, -5300], th=0)

    yield from bps.mv(prs, -17.25)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bps.mv(piezo.x, -35250)
    yield from bps.mv(piezo.z, 10900)
    yield from rugo(t=1, sdd='8.30', num=100, name='w03_c-3_p113', ys=[-4400, -5300], th=-12)


    sdds=   [8.3, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.6]
    bs_pos=[1.7, 1.7, 1.5, 1.5, 1.9, 2.1, 2.1, 2.1, 2.1]
    for sdd, bs in zip(sdds, bs_pos):
        yield from bps.mv(pil2M_pos.z, 1000*sdd)
        yield from bps.mv(pil2M_bs_rod.x, bs)  # ⚠️ FIXME(smi_plans): 'pil2M_bs_rod' was renamed (it would error). The SAXS beamstop rod is now 'pil2M.beamstop.x_rod' (or use the helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop()).


        yield from bps.mv(prs, -5.25)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        yield from bps.mv(piezo.x, -35250)
        yield from bps.mv(piezo.z, 10900)
        yield from rugo(t=1, sdd='%1.2f'%sdd, num=10, name='w03_c-3_p113', ys=[-4400, -5300], th=0)

        yield from bps.mv(prs, -17.25)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        yield from bps.mv(piezo.x, -35250)
        yield from bps.mv(piezo.z, 10900)
        yield from rugo(t=1, sdd='%1.2f'%sdd, num=10, name='w03_c-3_p113', ys=[-4400, -5300], th=-12)




def measure_nicolas2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS-style raster — for each WAXS arc position it rasters a grid of
    #   x/y points (following a tilted line in y) and takes a SAXS+WAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: a raster like this is a "map grid" in the 'smi_plans' library
    #   (sweep the WAXS arc as an extra axis), which records the arc/position/beam into each
    #   image:
    #     from smi_plans import map_grid_run, motor_axis
    #     yield from map_grid_run("ech2_14.5keV_...", piezo.x, xstart, xstop, nx,
    #                             piezo.y, ystart, ystop, ny, t=t, dets=[pil2M, pil900KW])
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    
    # name_fmt = "ech1_14.5keV_ai_7.0deg_l{ligne}_c{colone}_wa{wax}deg"
    # xs = 22925+ 200 * np.linspace(0, 39, 40)
    # ys1 = 4460.5-24.3*np.linspace(0, 39, 40)
    # ys2 = 4424.5-24.3*np.linspace(0, 39, 40)

    name_fmt = "ech2_14.5keV_ai_7.0deg_l{ligne}_c{colone}_wa{wax}deg"
    # xs = -6680+ 200 * np.linspace(0, 39, 40)
    # ys1 = 4654.5-24.3*np.linspace(0, 39, 40)
    # ys2 = 4619.5-24.3*np.linspace(0, 39, 40)
    
    xs = -6680+ 200 * np.linspace(20, 39, 20)
    ys1 = 4654.5-24.3*np.linspace(20, 39, 20)
    ys2 = 4619.5-24.3*np.linspace(20, 39, 20)


    # yield from bps.mv(prs, -5.5)
    # yield from bps.mv(piezo.th, 7.243685)
    # yield from bps.mv(piezo.ch, 0.1)
    yield from bps.mv(piezo.z, 9300)
    waxs_arc = [0, 20]

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

        for yy, (y1, y2) in enumerate(zip(ys1, ys2)):
            # y1, y2 = ys1[::-1][xx], ys2[::-1][xx]
            ys = np.linspace(y1, y2, 40)[::-1]

            for xx, x in enumerate(xs[::-1]):
                y=ys[xx]
                yield from bps.mv(piezo.y, y)      
                yield from bps.mv(piezo.x, x)

                sample_name = name_fmt.format(ligne='%2.2d'%xx, colone='%2.2d'%yy, wax='%2.2d'%wa)
                print(sample_name)
                sample_id(user_name="NV", sample_name=sample_name)

                yield from bp.count(dets, num=1)




def measure_nicolas_bkg(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a SAXS+WAXS background image at each of two WAXS arc positions.
    # 💡 NEWER, EASIER WAY:  from smi_plans import giwaxs_run
    #     yield from giwaxs_run("ech1_..._bkg", t=t, dets=[pil2M, pil900KW], arc=[0, 20])
    #   (records the arc/beam into each image and sets the exposure for you.)
    #   (Your script below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    
    name_fmt = "ech1_14.5keV_ai_7.0deg_bkg_wa{wax}deg"
    waxs_arc = [0, 20]

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

        sample_name = name_fmt.format(wax='%2.2d'%wa)
        print(sample_name)
        sample_id(user_name="NV", sample_name=sample_name)

        yield from bp.count(dets, num=1)



# 22950 3512.924     4959.92
# 23145 3512.06      4459.06
# 30760 3477.79      4425.076

#ai 0.27715
#phi -3.24



def cd_gisaxs_phi(phi0, phi_ini, phi_fin, phi_st, ai0, ai, exp_t=1, sample='test', nume=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-GISAXS phi rock — sets the grazing incident angle, then rocks the
    #   in-plane rotation (phi, around phi0) and takes a SAXS image at each phi.
    #
    # 💡 NEWER, EASIER WAY: the grazing-incidence CD rock is the 'smi_plans' helper
    #   'cd_gisaxs_rock_run', which rocks the correct current stage and records phi/incident
    #   angle/beam into each image:
    #     from smi_plans import cd_gisaxs_rock_run
    #     yield from cd_gisaxs_rock_run(sample, phi0=phi0, phi_start=phi_ini, phi_stop=phi_fin,
    #                                   num=phi_st, ai0=ai0, ai=ai, t=exp_t)
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) 'prs' was removed — it's now 'stage.phi' (⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = sample+'phiscan'
    det = [pil2M]
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(stage.th, ai0+ai)

    for num, phi in enumerate(np.linspace(phi_ini, phi_fin, phi_st)):        
        yield from bps.mv(prs, phi0+phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        
        name_fmt = "{sample}_5m_16.1keV_num{num}_phi{phii}deg_ai{aii}deg"
        sample_name = name_fmt.format(sample=sample, num="%2.2d"%num, phii="%1.3f"%phi, aii="%1.2f"%ai)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)

def cd_gisaxs_alphai(ai0, ai_ini, ai_fin, ai_st, phi0, phi, exp_t=1, sample='test', nume=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-GISAXS incident-angle scan — fixes the in-plane rotation (phi),
    #   then steps the grazing incident angle (alpha-i, around ai0) and takes a SAXS image
    #   at each angle.
    #
    # 💡 NEWER, EASIER WAY: this pairs with the GISAXS rock helper; the incident-angle sweep
    #   is an 'incidence_axis' you can hand to acquire, or use cd_gisaxs_rock_run for the
    #   companion phi rock:
    #     from smi_plans import acquire, incidence_axis, cdsaxs_dets
    #     yield from acquire(sample, cdsaxs_dets(),
    #                        [incidence_axis(stage.th, ai0, np.linspace(ai_ini, ai_fin, ai_st))])
    #
    #   (Your script below still works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) 'prs' was removed — it's now 'stage.phi' (⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = sample+'aiscan'
    det = [pil2M]
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(prs, phi0+phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    for num, ai in enumerate(np.linspace(ai_ini, ai_fin, ai_st)):        
        yield from bps.mv(stage.th, ai0+ai)
        
        name_fmt = "{sample}_5m_16.1keV_num{num}_phi{phii}deg_ai{aii}deg"
        sample_name = name_fmt.format(sample=sample, num="%2.2d"%num, phii="%1.2f"%phi, aii="%1.3f"%ai)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)


def nigh_cdgisaxs(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-GISAXS run-book — sets the sample position/tilt, then runs the
    #   incident-angle scans (cd_gisaxs_alphai) at a couple of phi values.
    #
    # 💡 NEWER, EASIER WAY: this is glue calling the GISAXS rock/scan routines; in 'smi_plans'
    #   those become cd_gisaxs_rock_run / acquire with incidence_axis (see their notes). The
    #   alignment positions could be found once with align_sample and saved with the data.
    #   Nothing here is broken on its own — but the routines it calls have ⚠️ items.
    #   (internal: Tier 1 — run-book.)
    # === end smi_plans note ================================================
    #ech c-3 prs -3.33, th -0.504, chi 0.0765, hexa_th 0.29925 stage_y 0.032
    yield from bps.mv(stage.y, -0.022)
    yield from bps.mv(piezo.x, 23000)
    yield from bps.mv(piezo.z, 6300)

    yield from bps.mv(piezo.ch, 0.0765)
    yield from bps.mv(piezo.th, -0.504)

    phi0, ai0 = -3.33, 0.29614
    phi_ini, phi_fin, phi_st = -5, 5, 2001
    sample = 'w03_c-3_p100nm'

    # for ai in [0.35, 0.45]:
    #     yield from cd_gisaxs_phi(phi0, phi_ini, phi_fin, phi_st, ai0, ai, exp_t=t, sample=sample, nume=1)


    ai_ini, ai_fin, ai_st = 0.3, 1, 701

    for phi in [0, -0.5]:
        yield from cd_gisaxs_alphai(ai0, ai_ini, ai_fin, ai_st, phi0, phi, exp_t=t, sample=sample, nume=1)


    #ech c-3 prs -3.342, th -0.504, chi 0.098, hexa_th 0.28768 stage_y 0.032
    
    # yield from bps.mv(stage.y, -0.0157)
    # yield from bps.mv(piezo.x, -30000)
    # yield from bps.mv(piezo.z, 8300)

    # yield from bps.mv(piezo.ch, 0.0985)
    # yield from bps.mv(piezo.th, -0.504)

    # phi0, ai0 = -3.342, 0.28768 
    # phi_ini, phi_fin, phi_st = -5, 5, 2001
    # sample = 'w03_c-1_p100nm'

    # for ai in [0.35, 0.45]:
    #     yield from cd_gisaxs_phi(phi0, phi_ini, phi_fin, phi_st, ai0, ai, exp_t=t, sample=sample, nume=1)


    # ai_ini, ai_fin, ai_st = 0.3, 1, 701

    # for phi in [0, -0.5]:
    #     yield from cd_gisaxs_alphai(ai0, ai_ini, ai_fin, ai_st, phi0, phi, exp_t=t, sample=sample, nume=1)

#0.28507 prs -3.129




def cdsaxs_echPaul_2023_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (Echantillon Paul) — moves to each sample (x/y/z/chi/th
    #   + hexapod x) and does a full CD-SAXS rock (via cd_saxs_new) at each.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("echPaul_2023_2", samples, th_start=-60, th_stop=60, num=121, t=t)
    #   (visits each sample, rocks 'stage.phi', records angle/position into each image.)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names = ['E1_001', 'E1_001_bkg', 'E1_010', 'E1_010-bkg','E1_100', 'E1_100_bkg', 'E2_001', 'E2_001_bkg', 'E2_010', 'E2_010_bkg', 'E2_100', 'E2_100_bkg']
    x =     [  -21300,       -23000,    -8400,        -9950,     700,         -900,    11600,        10100,    23300,        21800,    34700,        33100]
    x_hexa =[    0.15,         0.15,     0.15,         0.15,    0.15,         0.15,     0.15,         0.15,     0.15,         0.15,     0.15,         0.15]
    y=      [   -5200,        -5200,    -5700,        -5700,   -6200,        -6200,    -6400,        -6400,    -6200,        -6200,    -6200,        -6200]
    z=      [    8800,         8800,     8800,         8800,    8800,         8800,     8800,         8800,     8800,         8800,     8800,         8800]
    chi=    [       0,            0,        0,            0,       0,            0,     -1.5,         -1.5,     -1.8,         -1.8,     -1.6,         -1.6]
    th =    [       0,            0,        0,            0,       0,            0,        0,            0,        0,            0,        0,            0]


    names = [ 'bkg']
    x =     [-17500]
    x_hexa =[  0.15]
    y=      [ -9200]
    z=      [  8800]
    chi=    [     0]
    th =    [     0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)

        num=2

        yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num)




def cdsaxs_ocd_2023_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (OCD) — moves to each sample and does a full CD-SAXS
    #   rock (via cd_saxs_new) at each.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("ocd_2023_2", samples, th_start=-60, th_stop=60, num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # names = ['w25_cm4', 'w25_cm4_bkg', 'w25_cm3', 'w25_cm3_bkg', 'w25_cm2', 'w25_cm2_bkg', 'w25_cm1', 'w25_cm1_bkg']
    # x =     [  -27600,         -27600,    -12000,        -12000,     18700,        18700,     38500,         38500]
    # x_hexa =[    0.15,           0.15,      0.15,          0.15,      0.15,          0.15,      0.15,          0.15]
    # y=      [   -7100,          -4800,     -7100,         -4800,     -7100,         -4800,     -7100,         -4800]
    # z=      [    4800,           4800,      4800,          4800,      4800,          4800,      4800,          4800]
    # chi=    [     -0.7,          -0.7,      -0.7,          -0.7,      -0.7,          -0.7,      -0.7,          -0.7]
    # th =    [       0,              0,         0,             0,         0,             0,         0,             0]


    # names = ['w25_c0', 'w25_c0_bkg', 'w25_c1', 'w25_c1_bkg', 'w25_c2', 'w25_c2_bkg']
    # x =     [   -9000,        -9000,    17000,        17000,    36500,        36500]
    # x_hexa =[    0.15,         0.15,     0.15,         0.15,     0.15,         0.15]
    # y=      [   -7100,        -4800,    -7100,        -4800,    -7100,        -4800]
    # z=      [    4800,         4800,     4800,         4800,     4800,         4800]
    # chi=    [     -0.7,        -0.7,     -0.7,         -0.7,     -0.7,         -0.7]
    # th =    [       0,            0,        0,            0,        0,            0]

    names = ['w25_c3', 'w25_c3_bkg', 'w25_c4', 'w25_c4_bkg', 'w25_c5', 'w25_c5_bkg']
    x =     [   -8000,        -8000,    18000,        17000,    37000,        37000]
    x_hexa =[    0.15,         0.15,     0.15,         0.15,     0.15,         0.15]
    y=      [   -7100,        -4500,    -7100,        -4500,    -7100,        -4500]
    z=      [    4800,         4800,     4800,         4800,     4800,         4800]
    chi=    [     -0.4,        -0.4,     -0.4,         -0.4,     -0.4,         -0.4]
    th =    [       0,            0,        0,            0,        0,            0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)

        if 'bkg' not in name:
            for xx in [-4000, 0, 4000]:
                for yy in [-1000, 0, 1000]:
                    yield from bps.mv(piezo.x, xs + xx)
                    yield from bps.mv(piezo.y, ys + yy)
                    num=1
                    yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'xx%.1d_yy%.1d'%(0.001*xx, 0.001*yy), nume=num)

        else:                    
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            num=2
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num)

    

def cdsaxs_ovl_2023_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS overlay ("ovl") bar — moves to each sample and does a full
    #   CD-SAXS rock (via cd_saxs_new) at each.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("ovl_2023_2", samples, th_start=-60, th_stop=60, num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)


    names = ['w09ovl_c00-p112', 'w09ovl_c00_bkg-p112', 'w09ovl_c00-p128', 'w09ovl_c00_bkg-p128', 'w09ovl_-10-p112', 'w09ovl_c-10_bkg-p112', 'w09ovl_-10-p112', 'w09ovl_c-10_bkg-p112']
    x =     [           -21100,                -20400,              2900,                  2100,              4900,                   5900,             28900,                  27900]
    x_hexa =[             0.15,                  0.15,              0.15,                  0.15,              0.15,                   0.15,              0.15,                   0.15]
    y=      [             -900,                  -100,             -1000,                  -200,             -1000,                   -200,             -1200,                   -400]
    z=      [             4800,                  4800,              4800,                  4800,              4800,                   4800,              4800,                   4800]
    chi=    [             -0.6,                  -0.6,              -0.6,                  -0.6,              -0.6,                   -0.6,              -0.6,                   -0.6]
    th =    [                0,                     0,                0,                      0,                 0,                      0,                 0,                      0]

    names = [ 'w09ovl_-10-p118', 'w09ovl_c-10_bkg-p118']
    x =     [             28900,                  27900]
    x_hexa =[              0.15,                   0.15]
    y=      [             -1200,                   -400]
    z=      [              4800,                   4800]
    chi=    [              -0.6,                   -0.6]
    th =    [                 0,                      0]



    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
                  
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        num=2
        if 'bkg' not in name:
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet1', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet2', nume=num)
        else:
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=1)



    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        if 'bkg' not in name:
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
                    
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            num=2
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet3', nume=num)





def cdwaxs_echPaulSophie_2023_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-WAXS bar — moves to each sample, and for each WAXS arc position
    #   does a full rock (via cd_saxs_new, with the WAXS detector) at each.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("echPaulSophie_2023_2", samples, th_start=-60, th_stop=60,
    #                           num=121, t=t, dets=[pil900KW], arc=[0, 20])
    #   (visits each sample, sweeps the WAXS arc, rocks 'stage.phi', records angle/arc into
    #    each image. Note: pil900KW here is already the current WAXS detector — that's fine.)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil900KW]
    waxs_arc =[0, 20]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(stage.y, -9)

    names = ['echsoph_E','echpaul_01','echpaul_02','echpaul_04','echpaul_05','echpaul_06', 'echsoph_F']
    x =     [      41000,       32000,       23000,        3000,       -8000,      -18000,      -33000]
    x_hexa =[       0.15,        0.15,        0.15,        0.15,        0.15,        0.15,        0.15]
    y=      [      -9000,       -9000,       -9000,       -9000,       -9000,       -9000,       -9000]
    z=      [       4550,        4550,        4550,        4550,        4550,        4550,        4550]
    chi=    [       -0.5,        -0.5,        -0.5,        -0.5,        -0.5,        -0.5,        -0.5]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis in zip(names, x, x_hexa, y, z, chi):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)

        num=1

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            name = name+'_wa%sdeg'%wa

            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num, det=det)
    
    
    
    yield from bps.mv(stage.y, 0)

    names = ['E1_01_A4','E1_01_C3','E1_01_D3','E1_10_A4','E1_10_C3','E1_10_D3','E1_100_A4','E1_100_C3','E1_100_D3',
             'E2_01_A4','E2_01_C3','E2_01_D3','E2_10_A4','E2_10_C3','E2_10_D3','E2_100_A4','E2_100_C3','E2_100_D3']
    x =     [     35400,     39300,     41300,     22900,     24900,     26900,       9700,      13700,      15500, 
                   -600,      3300,      5300,    -11700,     -7800,     -5700,     -22100,     -18300,     -16300]
    x_hexa =[      0.15,      0.15,      0.15,      0.15,      0.15,      0.15,       0.15,       0.15,       0.15,
                   0.15,      0.15,      0.15,      0.15,      0.15,      0.15,       0.15,       0.15,       0.15]
    y=      [      5800,      7900,      7900,      5700,      7800,      7900,       9700,       8000,       8000, 
                   5900,      7800,      7800,      6000,      8100,      8100,       5300,       7600,       7500]
    z=      [      4550,      4550,      4550,      4550,      4550,      4550,       4550,       4550,       4550,
                   4550,      4550,      4550,      4550,      4550,      4550,       4550,       4550,       4550]
    chi=    [      -0.5,      -0.5,      -0.5,      -0.5,      -0.5,      -0.5,       -0.5,       -0.5,       -0.5,
                   -0.5,      -0.5,      -0.5,      -0.5,      -0.5,      -0.5,       -0.5,       -0.5,       -0.5]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"


    for name, xs, xs_hexa, ys, zs, chis in zip(names, x, x_hexa, y, z, chi):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)

        num=1

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            name = name+'_wa%sdeg'%wa

            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=num, det=det)



def cdsaxs_ovl_2023_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS overlay bar (2023_3) — moves to each sample and does several
    #   repeated CD-SAXS rocks (via cd_saxs_new), including a finer-step test, switching the
    #   exposure shorter for the fine test and back again.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, cdsaxs_rock_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("ovl_2023_3", samples, th_start=-60, th_stop=60, num=121, t=t)
    #     # for a finer test just call cdsaxs_rock_run(... num=241, t=0.1) — t= sets exposure
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the three 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names = ['ech1_p128', 'ech1_bkg_p128', 'ech2_p128', 'ech2_bkg_p128', 'ech3_p128', 'ech3_bkg_p128', 'ech4_p128', 'ech4_bkg_p128', 'ech5_p128','ech5_bkg_p128']
    x =     [     -44200,          -46100,      -25500,          -26500,       -1300,            1700,       16400,           15400,       36700,          35600]
    x_hexa =[      0.365,           0.365,       0.265,           0.265,       0.265,           0.265,       0.265,           0.265,       0.065,          0.065]
    y=      [      -6300,           -8500,       -7500,           -9600,       -7500,           -9600,       -7500,           -9600,       -8000,         -10000]
    z=      [      13310,           13310,       13410,           13410,       13310,           13310,       13110,           13110,       13210,          13210]
    chi=    [     -1.367,          -1.367,      -0.067,          -0.067,      -0.367,          -0.367,       0.433,           0.433,      -0.167,         -0.167]
    th =    [      -0.15,           -0.15,       -0.15,           -0.15,       -0.15,           -0.15,       -0.15,           -0.15,       -0.15,          -0.15]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"


    proposal_id("2023_3", "311000_Freychet_04")
    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        num=5
        if 'bkg' not in name:
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet1', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet2', nume=num)
        else:
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name, nume=1)

    proposal_id("2023_3", "311000_Freychet_05")
    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names[:1], x[:1], x_hexa[:1], y[:1], z[:1], chi[:1], th[:1]):
        if 'bkg' not in name:
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
                    
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)
            num=20
            yield from cd_saxs_new(-60, 60, 241, exp_t=t, sample=name+'testfinestep', nume=num)
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)


    proposal_id("2023_3", "311000_Freychet_06")

    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        if 'bkg' not in name:
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
                    
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            num=5
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet3', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet4', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet5', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet6', nume=num)
            yield from cd_saxs_new(-60, 60, 121, exp_t=t, sample=name+'repet7', nume=num)




def cdsaxs_ovl_2024_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS overlay bar (2024_1) — moves to each sample and does a full
    #   CD-SAXS rock (via cd_saxs_new) centered on a phi offset of -1.52 deg.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("ovl_2024_1", samples, th_start=-60-1.52, th_stop=60-1.52,
    #                           num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -1.52

    names = ['ech_c1', 'ech_c1_bkg', 'ech_c0', 'ech_c0_bkg', 'ech_cm1', 'ech_cm1_bkg', 'ech_cm3', 'ech_cm3_bkg']
    x =     [   28100,        27100,    10700,        10700,     -8500,         -8500,   -28100,         -28100]
    x_hexa =[    0.20,         0.20,     0.20,         0.20,      0.20,          0.20,     0.20,           0.20]
    y=      [    -700,          500,    -1500,        -1500,     -1600,          -200,    -1900,           -400]
    z=      [    1350,         1350,     1350,         1350,      1300,          1300,     1200,           1200]
    chi=    [   0.853,        0.853,   -0.847,       -0.847,    -2.347,        -2.347,   -1.647,         -1.647]
    th =    [ -0.4229,      -0.4229,  -0.4229,      -0.4229,   -0.4229,       -0.4229,  -0.4229,        -0.4229]

    names = ['ech_c5', 'ech_c5_bkg', 'ech_c3', 'ech_c3_bkg', 'ech_cm5', 'ech_cm5_bkg']
    x =     [   18000,        18000,     1400,         1400,    -17800,        -17800]
    x_hexa =[    0.20,         0.20,     0.20,         0.20,      0.20,          0.20]
    y=      [   -1600,         -100,    -1100,          300,     -1100,           300]
    z=      [    1350,         1350,     1300,         1300,      1250,          1250]
    chi=    [  -0.347,       -0.347,   -0.147,       -0.147,    -0.747,        -0.747]
    th =    [ -0.4229,      -0.4229,  -0.4229,      -0.4229,   -0.4229,       -0.4229]


    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        num=10
        if 'bkg' not in name:
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name, nume=num)
        else:
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name, nume=1)




def cdsaxs_IBM_2024_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (IBM, 2024_1) — moves to each grating spot on three
    #   samples and does a full CD-SAXS rock (via cd_saxs_new) centered on phi offset -1.52.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("IBM_2024_1", samples, th_start=-60-1.52, th_stop=60-1.52,
    #                           num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -1.52

    names = ['sam1_g1', 'sam1_g2', 'sam1_g3', 'sam1_g4',  'sam1_g5',  'sam1_g6']
    x =     [    -5500,     -2000,     2000,       6000,      10000,      14000]
    x_hexa =[     0.20,      0.20,     0.20,       0.20,       0.20,       0.20]
    y=      [    -9000,     -9000,    -9000,      -9000,      -9000,      -9000]
    y_hexa =[     -6.0,      -6.0,     -6.0,       -6.0,       -6.0,       -6.0]
    z=      [     5550,      5550,     5500,       5500,       5500,       5500]
    chi=    [    -1.50,     -1.50,    -1.50,      -1.50,      -1.50,      -1.50]
    th =    [  -0.4229,   -0.4229,  -0.4229,    -0.4229,    -0.4229,    -0.4229]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, ys_hexa, zs, chis, ths in zip(names, x, x_hexa, y, y_hexa, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name)


    names = ['sam2_g1', 'sam2_g2', 'sam2_g3', 'sam2_g4',  'sam2_g5',  'sam2_g6']
    x =     [    -5000,     -1000,     3000,       7000,      11000,      14500]
    x_hexa =[     0.20,      0.20,     0.20,       0.20,       0.20,       0.20]
    y=      [    -8000,     -8000,    -8000,      -8000,      -8000,      -8000]
    y_hexa =[      0.0,       0.0,      0.0,        0.0,        0.0,        0.0]
    z=      [     5550,      5550,     5500,       5500,       5500,       5500]
    chi=    [    -0.70,     -0.70,    -0.70,      -0.70,      -0.70,      -0.70]
    th =    [  -0.4229,   -0.4229,  -0.4229,    -0.4229,    -0.4229,    -0.4229]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, ys_hexa, zs, chis, ths in zip(names, x, x_hexa, y, y_hexa, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name)



    names = ['sam3_g1',  'sam3_g2',  'sam3_g3']
    x =     [     6500,      10500,      14500]
    x_hexa =[     0.20,       0.20,       0.20]
    y=      [     4000,       4000,       4000]
    y_hexa =[      0.0,        0.0,        0.0]
    z=      [     5500,       5500,       5500]
    chi=    [     -2.0,       -2.0,       -2.0]
    th =    [  -0.4229,    -0.4229,    -0.4229]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, ys_hexa, zs, chis, ths in zip(names, x, x_hexa, y, y_hexa, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name)






def cdsaxsG_2024_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (2024_2) — moves to a sample and does several CD-SAXS
    #   rocks (via cd_saxs_new) at different chi offsets and reference angles.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_rock_run, cdsaxs_bar
    #     yield from cdsaxs_rock_run("w07_c00", th_start=-60-2, th_stop=60-2, num=121, t=t)
    #     # vary chi between calls as you do, or use cdsaxs_bar for the full list
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)



    phi_offest = -2

    names = [ 'w07_c00']
    x =     [      -21600]
    x_hexa =[       0.3]
    y=      [      -1650]
    z=      [     6700]
    chi=    [       0.9]
    th =    [       5.0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for i in range(1):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)

            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            #yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            #yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'Ref_measure%s'%(i+1), nume=1)
            #phi_offest=0
            #yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'phioff_measure%s'%(i+1), nume=1)
            #phi_offest=-2
            #yield from bps.mv(piezo.z, zs+50)
            #yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'zoff0pO5_measure%s'%(i+1), nume=1)
            #yield from bps.mv(piezo.z, zs+100)
            #yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'zoff0p1_measure%s'%(i+1), nume=1)
            #yield from bps.mv(piezo.z, zs+200)
            #yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'zoff0p2_measure%s'%(i+1), nume=1)
            #yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis+0.2)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'chioff0p2_measure%s'%(i+1), nume=1)
            yield from bps.mv(piezo.ch, chis+0.5)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'chioff0p5_measure%s'%(i+1), nume=1)
            yield from bps.mv(piezo.ch, chis)
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)




    phi_offest = -2

    names = [ 'w07_c00', 'w07_c00_bkg', 'w07_c10', 'w07_c10_bkg', 'w07_c10', 'w07_c01_bkg']
    x =     [    -21600,        -21600,     -6700,         -6700,     10400,         10400]
    x_hexa =[       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [     -1650,          -250,      -450,           750,      -650,         -1650]
    z=      [      6700,          6700,      6100,          6100,      5600,          5600]
    chi=    [       0.9,           0.9,      -0.6,          -0.6,      -0.2,          -0.2]
    th =    [        5,              5,        5,              5,       5.7,           5.7]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    '''
    for i in range(5):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)

            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=5)
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            else:
                if i ==0:
                    yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=5)
    '''
    for i in range(2):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)

            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(2+i+1), nume=1)


def mesure_rugo(exp_t=1, nume=100):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a roughness bar — parks the rotation stage at a phi offset, then for
    #   each sample takes many SAXS images at the "up" and "down" SAXS detector positions
    #   (a y-stitch). (This is the SECOND function named 'mesure_rugo' in the file; in Python
    #   the later def wins, so this is the one that actually runs when you call mesure_rugo.)
    #
    # 💡 NEWER, EASIER WAY: the up/down detector-position roughness stitch over a bar is the
    #   'smi_plans' helper 'cdsaxs_ystitch_run' (with a SampleList), which moves the SAXS
    #   detector and records the position/beam into each image:
    #     from smi_plans import cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_ystitch_run("rugo", samples, num=nume, t=exp_t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' was removed — it's now 'stage.phi'; (2)
    #   'det_exposure_time' no longer sets the exposure unless run as a plan (⚠️ notes
    #   below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    phi_offest = -2

    '''
    names =  'w07_c00'
    x =           -21600
    x_hexa =       0.3
    y=            -1650
    z=           6700
    chi=           0.9
    th =           5.0
    
    names =  'w07_c00_bkg'
    x =           -21600
    x_hexa =       0.3
    y=            -250
    z=           6700
    chi=           0.9
    th =           5.0
    '''

    '''
    names = [ 'w25_c2', 'w25_c2_bkg', 'w25_c3', 'w25_c3_bkg',  'w25_c4',  'w25_c4_bkg',  'w16_c2',  'w16_c2_bkg',  'w16_c3',  'w16_c3_bkg',  'w16_c4',  'w16_c4_bkg']
    x =     [   -22600,       -22700,     3400,         3400,     29400,         29400,    -26000,        -26000,         0,             0,     26100,         26100]
    x_hexa =[      0.3,          0.3,      0.3,          0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [    -8350,        -7350,    -8450,        -7350,     -8550,         -7550,      6200,          7200,      6200,          7200,      6100,          7100]
    z=      [     6500,         6500,     5600,         5600,      5000,          5000,      6700,          6700,      5900,          5900,      5000,          5000]
    chi=    [     -0.1,         -0.1,     -0.1,         -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1]
    th =    [      5.4,          5.4,      5.4,          5.4,       5.4,           5.4,       5.4,           5.4,       5.4,           5.4,       5.4,           5.4]
    '''
 

    names = [ 'w25_c1', 'w25_c1_bkg', 'w25_c0', 'w25_c0_bkg', 'w25_cm1', 'w25_cm1_bkg', 'w25_cm4', 'w25_cm4_bkg', 'w25_cm3', 'w25_cm3_bkg', 'w25_cm2', 'w25_cm2_bkg']
    x =     [   -23900,       -23900,     3100,         3100,     29100,         29100,    -24500,        -26000,      1500,          1500,     27500,         27500]
    x_hexa =[      0.3,          0.3,      0.3,          0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [    -8350,        -7350,    -8350,        -7350,     -8550,         -7550,      6500,          7500,      6500,          7500,      6500,          7500]
    z=      [     6700,         6700,     5700,         5700,      4700,          4700,      6500,          6500,      5500,          5500,      4900,          4900]
    chi=    [     -0.1,         -0.1,     -0.1,         -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1]
    th =    [      5.4,          5.4,      5.4,          5.4,       5.4,           5.4,       5.6,           5.6,       5.6,           5.6,       5.6,           5.6]


    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        name_fmt = "{sample}_rugo_up_sdd8p30"
        sample_name = name_fmt.format(sample=name)
        print(sample_name)
        sample_id(user_name="PG", sample_name=sample_name)
        yield from bp.count([pil2M], num=nume)

        yield from bps.mvr(pil2M_pos.y, 4.3)
        name_fmt = "{sample}_rugo_down_sdd8p30"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="PG", sample_name=sample_name)
        yield from bp.count([pil2M], num=nume)
        yield from bps.mvr(pil2M_pos.y, -4.3)




def cdsaxsstd_2024_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS standard bar (2024_2) — moves to each sample and does a
    #   reference + full CD-SAXS rock + reference (via cd_saxs_new) centered on phi -2 deg.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("std_2024_2", samples, th_start=-60-2, th_stop=60-2, num=61, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -2
    '''
    Forgot to change the name and position. Position are close enough to work
    names = [ 'w16_c1', 'w16_c1_bkg', 'w16_c0', 'w16_c0_bkg', 'w16_cm1', 'w16_cm1_bkg', 'w16_cm4', 'w16_cm4_bkg', 'w16_cm3', 'w16_cm3_bkg', 'w16_cm2', 'w16_cm2_bkg']
    x =     [   -22700,       -22700,     3400,         3400,     29400,         29400,    -24800,        -24800,      1200,          1200,     27200,         27200]
    x_hexa =[      0.3,          0.3,      0.3,          0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [    -8350,        -7550,    -8350,        -7400,     -8350,         -7450,      6400,          7400,      6400,          7400,      6400,          7400]
    z=      [     6700,         6700,     6100,         6100,      5300,          5300,      6700,          6700,      6000,          6000,      5300,          5300]
    chi=    [      0.1,          0.1,      0.1,          0.1,       0.1,           0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1]
    th =    [      6.0,          6.0,      6.0,          6.0,       6.0,           6.0,       5.4,           5.4,       5.4,           5.4,       5.4,           5.4]
    
    
    names = [ 'w25_c2', 'w25_c2_bkg', 'w25_c3', 'w25_c3_bkg',  'w25_c4',  'w25_c4_bkg',  'w16_c2',  'w16_c2_bkg',  'w16_c3',  'w16_c3_bkg',  'w16_c4',  'w16_c4_bkg']
    x =     [   -22600,       -22700,     3400,         3400,     29400,         29400,    -26000,        -26000,         0,             0,     26100,         26100]
    x_hexa =[      0.3,          0.3,      0.3,          0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [    -8350,        -7350,    -8450,        -7350,     -8550,         -7550,      6200,          7200,      6200,          7200,      6100,          7100]
    z=      [     6500,         6500,     5600,         5600,      5000,          5000,      6700,          6700,      5900,          5900,      5000,          5000]
    chi=    [     -0.1,         -0.1,     -0.1,         -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1]
    th =    [      5.4,          5.4,      5.4,          5.4,       5.4,           5.4,       5.4,           5.4,       5.4,           5.4,       5.4,           5.4]
    '''

    names = [ 'w25_c1_bkg', 'w25_c0', 'w25_c0_bkg', 'w25_cm1', 'w25_cm1_bkg', 'w25_cm4', 'w25_cm4_bkg', 'w25_cm3', 'w25_cm3_bkg', 'w25_cm2', 'w25_cm2_bkg']
    x =     [       -23900,     3100,         3100,     29100,         29100,    -24500,        -26000,      1500,          1500,     27500,         27500]
    x_hexa =[          0.3,      0.3,          0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3,       0.3,           0.3]
    y=      [        -7350,    -8350,        -7350,     -8550,         -7550,      6500,          7500,      6500,          7500,      6500,          7500]
    z=      [         6700,     5700,         5700,      4700,          4700,      6500,          6500,      5500,          5500,      4900,          4900]
    chi=    [         -0.1,     -0.1,         -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1,      -0.1,          -0.1]
    th =    [          5.4,      5.4,          5.4,       5.4,           5.4,       5.6,           5.6,       5.6,           5.6,       5.6,           5.6]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 61, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 61, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

 



def mesure_rugo_2024_16(exp_t=1, nume=100):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a long roughness time-series — repeats 200 times, taking one SAXS image
    #   at the sample and at a background position each pass.
    # 💡 NEWER, EASIER WAY: "repeat a measurement many times" is the 'smi_plans' time-series
    #   helper, which records the timing/beam into each frame:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("w25_c0_rugo_...", num=200, t=exp_t, dets=[pil2M])
    #   (Nothing here is broken — the exposure line is already commented out. (internal: Tier 1.))
    # === end smi_plans note ================================================

    names = [ 'w25_c0', 'w25_c0_bkg']
    x =     [      200,          200]
    y=      [        0,         -700]


    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"

    # det_exposure_time(exp_t, exp_t)
    for i in range(200):
        for name, xs, ys in zip(names, x, y):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            name_fmt = "{sample}_rugo_up_sdd9p20_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(user_name="PG", sample_name=sample_name)
            yield from bp.count([pil2M], num=1)



            # yield from bps.mvr(pil2M_pos.y, 4.3)
            # name_fmt = "{sample}_rugo_down_sdd9p20_16.1keV"
            # sample_name = name_fmt.format(sample=name)
            # sample_id(user_name="PG", sample_name=sample_name)
            # yield from bp.count([pil2M], num=nume)
            # yield from bps.mvr(pil2M_pos.y, -4.3)





def cdsaxsstd_2025_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS standard bar (2025_1) — moves to each sample and does a
    #   reference + full CD-SAXS rock + reference (via cd_saxs_new) centered on phi -2 deg.
    #   (Note: this is the FIRST of TWO functions named 'cdsaxsstd_2025_1'; Python keeps the
    #   LATER one, so this earlier copy is shadowed and won't run as 'cdsaxsstd_2025_1'.)
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("std_2025_1", samples, th_start=-60-2, th_stop=60-2, num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -2

    names = [  'c5',  'c5_bkg',  'c4',  'c4_bkg',  'c3',  'c3_bkg',  'c2',  'c2_bkg',  'c1',  'c1_bkg',  'c0', 'c0_bkg', 
              'cm1', 'cm1_bkg', 'cm2', 'cm2_bkg', 'cm3', 'cm3_bkg', 'cm4', 'cm4_bkg', 'cm5', 'cm5_bkg']
    x =     [-54000,    -54000,-39600,    -39600,-29800,    -29800,-20200,    -20200, -9900,     -9900, -2100,    -2100,
              13100,     13100, 22000,     22000, 29600,     29600, 42200,     42200, 54600,     54600]
    x_hexa =[   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,      0.1,
                0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1]
    y=      [ -5300,     -6800, -7900,     -9400, -7200,     -8700, -7200,     -8700, -7300,     -8800, -7100,   -8600,
              -7100,     -8600, -7300,     -8800, -7600,     -9100, -7600,     -9100, -9000,    -10000]
    z=      [  3540,      3540,  3000,      3000,  2740,      2740,  2700,      2700,  2500,      2500,  2300,    2300, 
               2000,      2000,  1800,      1800,  1600,      1600,  1600,      1600,  1300,      1300]
    chi=    [  1.79,      1.79,  -0.6,      -0.6,  -0.2,      -0.2,  -0.1,      -0.1,  -0.3,      -0.3,   1.4,     1.4,
               -0.8,      -0.8,   0.3,       0.3,   0.3,       0.3,   0.8,       0.8,   1.8,       1.8]
    th =    [   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,     0.0,
                0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=4)
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)



def cdsaxsstd_2025_1_nischal(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS standard bar (2025_1, Nischal) — moves to each slot2 sample
    #   and does a reference + full CD-SAXS rock + reference (via cd_saxs_new), phi offset 1.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("std_2025_1_nischal", samples, th_start=-60+1, th_stop=60+1,
    #                           num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = [  'slot2_s3_pos1', 'slot2_s3_pos2', 'slot2_s2_pos1',  'slot2_s2_pos2', 'slot2_s1_pos1',  'slot2_s1_bkg']
    x =     [           -28300,          -31000,           -5300,            -3000,           20700,           24700]
    y=      [            -6500,           -6500,           -6000,            -6000,           -6000,           -6000]
    z=      [             3050,            3050,            3450,             3450,            4350,            4450]
    chi=    [             -0.5,            -0.5,             1.0,              1.0,             1.0,             1.0]
    th =    [              1.0,             1.0,             1.0,              1.0,             1.0,             1.0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=5)
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)


def cdsaxsstd_2025_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS standard bar (2025_1) — moves to each sample and does a
    #   reference + full CD-SAXS rock + reference (via cd_saxs_new) centered on phi -2 deg.
    #   (Note: there are TWO functions named 'cdsaxsstd_2025_1' in this file; in Python the
    #   later one wins, so THIS is the one that runs when you call cdsaxsstd_2025_1.)
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("std_2025_1", samples, th_start=-60-2, th_stop=60-2, num=121, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ line; the 'prs' rock is inside
    #    cd_saxs_new — fixing it there fixes this too.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time' no longer sets the exposure unless run
    #   as a plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -2

    names = [  'c5',  'c5_bkg',  'c4',  'c4_bkg',  'c3',  'c3_bkg',  'c2',  'c2_bkg',  'c1',  'c1_bkg',  'c0', 'c0_bkg', 
              'cm1', 'cm1_bkg', 'cm2', 'cm2_bkg', 'cm3', 'cm3_bkg', 'cm4', 'cm4_bkg', 'cm5', 'cm5_bkg']
    x =     [-54000,    -54000,-39600,    -39600,-29800,    -29800,-20200,    -20200, -9900,     -9900, -2100,    -2100,
              13100,     13100, 22000,     22000, 29600,     29600, 42200,     42200, 54600,     54600]
    x_hexa =[   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,      0.1,
                0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1,   0.1,       0.1]
    y=      [ -5300,     -6800, -7900,     -9400, -7200,     -8700, -7200,     -8700, -7300,     -8800, -7100,   -8600,
              -7100,     -8600, -7300,     -8800, -7600,     -9100, -7600,     -9100, -9000,    -10000]
    z=      [  3540,      3540,  3000,      3000,  2740,      2740,  2700,      2700,  2500,      2500,  2300,    2300, 
               2000,      2000,  1800,      1800,  1600,      1600,  1600,      1600,  1300,      1300]
    chi=    [  1.79,      1.79,  -0.6,      -0.6,  -0.2,      -0.2,  -0.1,      -0.1,  -0.3,      -0.3,   1.4,     1.4,
               -0.8,      -0.8,   0.3,       0.3,   0.3,       0.3,   0.8,       0.8,   1.8,       1.8]
    th =    [   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,     0.0,
                0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0,   0.0,       0.0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, xs_hexa, ys, zs, chis, ths in zip(names, x, x_hexa, y, z, chi, th):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            # yield from bp
            if 'bkg' not in name:
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=4)
                yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)



def cdsaxsstd_2025_1_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (2025_1, Yager) — for each sample position does a
    #   reference + full CD-SAXS rock + reference (via cd_saxs_new), then a SECOND pass that
    #   does the up/down SAXS-detector y-stitch at each sample.
    # 💡 NEWER, EASIER WAY: the rock is cdsaxs_bar / cdsaxs_rock_run, and the up/down stitch
    #   is cdsaxs_ystitch_run, both in 'smi_plans' (they rock 'stage.phi', move the detector,
    #   and record angle/position into each image):
    #     from smi_plans import cdsaxs_bar, cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("yager_2025_1", samples, th_start=-60+1, th_stop=60+1, num=121, t=t)
    #     yield from cdsaxs_ystitch_run("yager_2025_1", samples, num=2, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the two 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan; (2) the 'prs' line in the y-stitch was removed — it's
    #   now 'stage.phi'; (the rock's 'prs' is inside cd_saxs_new — fix it there). (⚠️ notes
    #   below.) (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = ['samA_pos1', 'samA_pos2', 'samA_pos3', 'samA_sub',    
             'samB_AlOx-2cyc_pos1', 'samB_AlOx-2cyc_pos2', 'samB_AlOx-2cyc_sub',  
             'samC_AlOx-4cyc_pos1', 'samC_AlOx-4cyc_pos2', 'samC_AlOx-4cyc_sub',  
             'samD_InOx-2cyc_pos1', 'samD_InOx-2cyc_pos2', 'samD_InOx-2cyc_sub' ]
    
    ## with on-axis camera
    x =     [   -24800,    -23300,      -21800,     -23300,    #A
                -3800,      -3800,      -3800,  #B
                11670,      11670,      11670,  #C
                29300,      29300,      29300   #D
                    ]
    y=      [  -5600,           -5800,    -5600,     -4300-2400,  #A 
               -4300-200,           -4300-400,       -4300-2400,  #B
                -4000-200,           -4000-400,       -4000-2400,  #C
                -2200-200,           -2200-400,       -2200-2400  #D
                    ]
    
    z=      [    2650,            2650,   2650,    2650,   #A 
                3600,           3600,     3600 ,     #B
                4390,          4390,      4390,   #C  #x=6970
                5170,           5170,       5170  #D  #x=23500
                    ]
    
    ## with scattering pattern
    chi=    [  -0.2,         -0.2,      -0.2,  -0.2,  #A   
               -2.4,           -2.4,     -2.4,     #B 
               0.3,            0.3,      0.3,    #C 
                -3.65,          -3.65,      -3.65   #D 
                 ]
    th =    [     1.0,             1.0,      1.0,    1.0,    
              1.0,             1.0,      1.0,
               1.0,             1.0,      1.0,
                1.0,             1.0,      1.0 
              ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of chi ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of th ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            # yield from bp
            # if 'bkg' not in name:
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            if 'pos3' in name:
                yield from cd_saxs_new(60+phi_offest, -60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")
    print("====== Doing detector y-stitch")
    exp_t = t
    nume = 2
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)

            yield from bps.mvr(pil2M_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)
            yield from bps.mvr(pil2M_pos.y, -4.3)

def cdsaxsstd_2025_1A_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (2025_1, Yager set A) — for the samA_pos4 sample/bkg does
    #   a reference + full CD-SAXS rock + reference (via cd_saxs_new), then an up/down SAXS-
    #   detector y-stitch.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("yager_2025_1A", samples, th_start=-60+1, th_stop=60+1, num=121, t=t)
    #     yield from cdsaxs_ystitch_run("yager_2025_1A", samples, num=2, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the rock's 'prs' is inside
    #    cd_saxs_new — fix it there.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the two 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan; (2) the 'prs' line in the y-stitch was removed — it's
    #   now 'stage.phi' (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = ['samA_pos4', 'samA_pos4bg']
    
    ## with on-axis camera
    x =     [   -23300,    -23300    #A
                                    ]
    y=      [  -6000,           -6200  #A 
                    ]
    
    z=      [    2650,            2650      #A 
                ]
    
    ## with scattering pattern
    chi=    [  -0.2,         -0.2    ]   #A   
                                
    th =    [     1.0,             1.0     ]
              

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of chi ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of th ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            # yield from bp
            # if 'bkg' not in name:
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            if 'pos3' in name:
                yield from cd_saxs_new(60+phi_offest, -60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
            else:
                yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")
    print("====== Doing detector y-stitch")
    exp_t = t
    nume = 2
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)

            yield from bps.mvr(pil2M_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)
            yield from bps.mvr(pil2M_pos.y, -4.3)

def cdsaxsstd_2025_1B_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (2025_1, Yager set B) — for the samB pos3 sample/bkg does
    #   a reference + two-direction CD-SAXS rock + reference (via cd_saxs_new), then an
    #   up/down SAXS-detector y-stitch.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("yager_2025_1B", samples, th_start=-60+1, th_stop=60+1, num=121, t=t)
    #     yield from cdsaxs_ystitch_run("yager_2025_1B", samples, num=2, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the rock's 'prs' is inside
    #    cd_saxs_new — fix it there.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the two 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan; (2) the 'prs' line in the y-stitch was removed — it's
    #   now 'stage.phi' (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = ['samB_AlOx-2cyc_pos3', 'samB_AlOx-2cyc_pos3bg' ]
    
    ## with on-axis camera
    x =     [  
                -3800,      -3800  #B
                    ]
    y=      [  
               -6100,           -6300 #B
                    ]
    
    z=      [   
                3600,           3600     #B
                    ]
    
    ## with scattering pattern
    chi=    [  
               -2.4,           -2.4    #B 
                 ]
    th =    [     1.0,             1.0,     
              ]
              

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of chi ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of th ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            # yield from bp
            # if 'bkg' not in name:
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs_new(60+phi_offest, -60+phi_offest, 121, exp_t=t, sample=name+'measureA%s'%(i+1), nume=1)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureB%s'%(i+1), nume=1)
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")
    print("====== Doing detector y-stitch")
    exp_t = t
    nume = 2
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)

            yield from bps.mvr(pil2M_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)
            yield from bps.mvr(pil2M_pos.y, -4.3)

def cdsaxsstd_2025_1CD_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS bar (2025_1, Yager sets C & D) — for each samC/samD position
    #   does a reference + two-direction CD-SAXS rock + reference (via cd_saxs_new), then an
    #   up/down SAXS-detector y-stitch.
    # 💡 NEWER, EASIER WAY:  from smi_plans import cdsaxs_bar, cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar("yager_2025_1CD", samples, th_start=-60+1, th_stop=60+1, num=121, t=t)
    #     yield from cdsaxs_ystitch_run("yager_2025_1CD", samples, num=2, t=t)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines; the rock's 'prs' is inside
    #    cd_saxs_new — fix it there.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the two 'det_exposure_time(...)' calls no longer set the
    #   exposure unless run as a plan; (2) the 'prs' line in the y-stitch was removed — it's
    #   now 'stage.phi' (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = ['samC_AlOx-4cyc_pos3', 'samC_AlOx-4cyc_pos4', 'samC_AlOx-4cyc_pos5bg','samC_AlOx-4cyc_pos6bg',  
             'samD_InOx-2cyc_pos3', 'samD_InOx-2cyc_pos4', 'samD_InOx-2cyc_pos5bg','samD_InOx-2cyc_pos6bg' ]
    
    ## with on-axis camera'samB_AlOx-2cyc_pos3', 'samB_AlOx-2cyc_pos3bg' ]
    
    x =     [  
                11670,      11670,      11670,  11670,  #C
                29300,      29300,      29300,  29300   #D
                    ]
    y=      [  
               -5300,      -5500,       -5700,  -5900, #C
                -3800,     -4000,       -4200,  -4400  #D
                    ]
    
    z=      [   
                4390,          4390,      4390,  4390,   #C  #x=6970
                5170,           5170,       5170 ,5170 #D  #x=23500
                 
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.3,            0.3,      0.3 ,   0.3,  #C 
                -3.65,          -3.65,   -3.65 ,-3.65  #D 
                 ]
    th =    [    1.0,             1.0,     1.0,   1.0,
                1.0,             1.0,      1.0   ,1.0
              ]
              

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of chi ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of th ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            # yield from bp
            # if 'bkg' not in name:
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs_new(60+phi_offest, -60+phi_offest, 121, exp_t=t, sample=name+'measureA%s'%(i+1), nume=1)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureB%s'%(i+1), nume=1)
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")
    print("====== Doing detector y-stitch")
    exp_t = t
    nume = 2
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)

            yield from bps.mvr(pil2M_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)
            yield from bps.mvr(pil2M_pos.y, -4.3)


def xyscan_wieser(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a rectangle x/y raster — for each sample it scans a grid of x/y points
    #   (xmin..xmax by xinc, ymin..ymax by yinc) and takes one SAXS image at each, writing
    #   the beam-monitor value into the name.
    #
    # 💡 NEWER, EASIER WAY: a rectangle raster is a "map grid" in the 'smi_plans' library,
    #   which records the position and beam into each image (so the beam value lands in the
    #   data, not just the name):
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run("samA_noInf_3", piezo.x, xmin, xmax, nx,
    #                             piezo.y, ymin, ymax, ny, t=t, dets=[pil2M])
    #
    #   (Nothing here is broken — no retired names are used. (internal: Tier 1.))
    # === end smi_plans note ================================================
    #rectangle scan between xmin,xmax,ymin,ymax, with xinc, yinc. everything else stays constant
    names=['samA_noInf_3'   ,    'samB_AlOx-2cyc_3'  ,  'samC_AlOx-4cyc_3'  ,   'samD_InOx-2cyc_pos3_3']

    xmin =[   -23300-500,          -3800-500,          11670-500,              29300-500       ]
    xmax =[   -23300+500,          -3800+500,          11670+500,              29300+500       ]
    xinc =[       200,                 200,               200,                    200          ]
## with on-axis camera
    ymin =[    -6200-100  ,           -6300    ,      -5900             ,        -4400 ]
    ymax =[    -6000+100  ,            -6100   ,       -5300            ,         -3800]
    yinc =[        30     ,              30    ,        30           ,              30 ]

    z=      [    2650,             3600,                  4390,                   5170          ]
    chi=    [  -0.2,                 -2.4,                 0.3,                   -3.65         ]
    th =    [     1.0,              1.0,                   1.0,                   1.0           ]

    assert len(names) == len(xmin), f"len of xmin ({len(xmin)}) is different from number of samples ({len(names)})"
    assert len(names) == len(xmax), f"len of xmax ({len(xmax)}) is different from number of samples ({len(names)})"
    assert len(names) == len(xinc), f"len of xinc ({len(xinc)}) is different from number of samples ({len(names)})"
    assert len(names) == len(ymin), f"len of ymin ({len(ymin)}) is different from number of samples ({len(names)})"
    assert len(names) == len(ymax), f"len of ymax ({len(ymax)}) is different from number of samples ({len(names)})"
    assert len(names) == len(yinc), f"len of yinc ({len(yinc)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z),    f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi),  f"len of chi ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th),   f"len of th ({len(th)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for name, xmins, xmaxs, xincs, ymins, ymaxs, yincs, zs, chis, ths in zip(names, xmin, xmax, xinc, ymin, ymax, yinc, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            xrange=np.arange(xmins,xmaxs+xincs,xincs) #including xmax
            yrange=np.arange(ymins,ymaxs+yincs,yincs) #including ymax
            for xi in xrange: #scanning over xrange
                for yi in yrange: #scanning over yrange
                    yield from bps.mv(piezo.x, xi)
                    yield from bps.mv(piezo.y, yi)
                    
                    name_fmt = "{name}_xyscan_9.2m_16.1keV_x{xi}_y{yi}_bpm{bpm}"
                    sample_name = name_fmt.format(name=name, xi="%5.2d"%xi, yi="%5.2d"%yi, bpm="%1.3f"%xbpm3.sumX.get())
                    #sample_id(user_name="PG", sample_name=sample_name)
                    sample_id(sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count([pil2M], num=1)




def mesure_rugo_2025_1(exp_t=1, nume=100):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a roughness bar (2025_1) — parks the rotation stage at a phi offset,
    #   then for each slot2 sample takes many SAXS images at the "up" and "down" SAXS
    #   detector positions (a y-stitch).
    #
    # 💡 NEWER, EASIER WAY: the up/down detector-position roughness stitch over a bar is the
    #   'smi_plans' helper 'cdsaxs_ystitch_run' (with a SampleList), which moves the SAXS
    #   detector and records the position/beam into each image:
    #     from smi_plans import cdsaxs_ystitch_run, SampleList
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_ystitch_run("rugo_2025_1", samples, num=nume, t=exp_t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'det_exposure_time' no longer sets the exposure unless
    #   run as a plan; (2) 'prs' was removed — it's now 'stage.phi' (⚠️ notes below).
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = [  'slot2_s3_pos1', 'slot2_s3_pos2', 'slot2_s2_pos1',  'slot2_s2_pos2', 'slot2_s1_pos1',  'slot2_s1_bkg']
    x =     [           -28300,          -31000,           -5300,            -3000,           20700,           24700]
    y=      [            -6500,           -6500,           -6000,            -6000,           -6000,           -6000]
    z=      [             3050,            3050,            3450,             3450,            4350,            4450]
    chi=    [             -0.5,            -0.5,             1.0,              1.0,             1.0,             1.0]
    th =    [              1.0,             1.0,             1.0,              1.0,             1.0,             1.0]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

            name_fmt = "{sample}_rugo_up_sdd9p20_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)

            yield from bps.mvr(pil2M_pos.y, 4.3)
            name_fmt = "{sample}_rugo_down_sdd9p20_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil2M], num=nume)
            yield from bps.mvr(pil2M_pos.y, -4.3)
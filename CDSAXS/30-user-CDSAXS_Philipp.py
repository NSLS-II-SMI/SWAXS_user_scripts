# pil300KW for waxs, pil2M for saxs


def cd_saxs(th_ini, th_fin, th_st, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS "rocking" scan — for each sample/pitch it rotates the sample
    #   through a series of tilt angles (th_ini -> th_fin) and takes a SAXS image at each.
    #   The rotation motor this script calls 'prs' is what does the rocking. (CD-SAXS measures
    #   the cross-section/critical-dimension of line gratings by tilting through angles.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   ready-made CD-SAXS rocking routine. It rocks the angle for you and records the angle
    #   + beam into each saved image — so you don't hand-build "{sample}_{th}deg". The
    #   rocking stage 'prs' is now called 'stage.phi':
    #
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     yield from cdsaxs_rock_run(
    #         "cdsaxs_ech03_defectivity_pitch128",   # the rest of the file name is filled in for you
    #         th_start=th_ini, th_end=th_fin, th_num=th_st,   # your same angle range
    #         dets=cdsaxs_dets(),                    # the CD-SAXS detector set (pil2M)
    #         t=exp_t, num=10,
    #     )
    #     # (call it per sample/pitch, the way you loop below.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' (the rocking stage) was removed — it's now
    #   'stage.phi'; (2) the 'det_exposure_time(...)' call no longer sets the exposure unless
    #   run as a plan. See the ⚠️ notes on those lines below. (internal: Tier 1.)
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

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: a CD-SAXS rocking scan at one position — rotates the sample from -60 to
    #   +60 deg (121 steps) and takes a SAXS image at each. 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: use the 'smi_plans' CD-SAXS rocking routine (rocking stage 'prs'
    #   is now 'stage.phi'):
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     yield from cdsaxs_rock_run(sample, th_start=-60, th_end=60, th_num=step,
    #                                dets=cdsaxs_dets(), t=exp_t, num=num)
    #   (Your script below still works, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' -> 'stage.phi'; (2) 'det_exposure_time(...)' must
    #   be run as a plan. See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    det = [pil2M]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: steps across many grating pitches (different x offsets) and runs a
    #   CD-SAXS rocking scan at each (by calling cd_saxs_new).
    # 💡 NEWER, EASIER WAY: 'smi_plans' has cdsaxs_pitch_survey for exactly this "sweep the
    #   pitch positions and rock each" pattern, recording pitch/angle/beam for you:
    #     from smi_plans import cdsaxs_pitch_survey, cdsaxs_dets
    #   (Your script below still works, except the ⚠️ line; cd_saxs_new carries its own notes.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan
    #   (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p112nm","p113nm","p114nm","p115nm","p116nm","p117nm","p118nm","p119nm","p120nm","p121nm","p122nm","p123nm","p124nm","p125nm",
               "p126nm","p127nm","p128nm"]
    x_off = [0,1500,3000,4500,6000,7500,9000,10500,12000,13500,15000,16500,18000,19500,21000,22500,24000]
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, pitch in zip(x_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y, num=1, exp_t=exp_t, step=step)


def night_patrice(exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an overnight CD-SAXS run-book — loops over many fields/backgrounds and
    #   runs rocking scans at each (by calling the rocking helpers above).
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) + rocking
    #   routine (cdsaxs_rock_run) that loop your samples and record angle/position/beam for
    #   you. The rocking stage 'prs' (used by the helpers) is now 'stage.phi'.
    #   (Your script below still works; the helpers carry their own ⚠️ notes.) (internal: Tier 1.)
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
    # WHAT THIS DOES: a CD-SAXS run-book over several "box" samples — drives to each and runs
    #   the all-pitch rocking sweep there.
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS bar + pitch-survey workflow
    #   (cdsaxs_bar / cdsaxs_pitch_survey) that loops samples/pitches and records the data
    #   for you. The rocking stage 'prs' (used in the helpers) is now 'stage.phi'.
    #   (Your script below still works; the rocking helpers carry their own ⚠️ notes.)
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = ["Echantillon03_defectivity","Echantillon04_defectivity","Echantillon11b_defectivity"]
    x = [-40050, -11150, 17000]
    y = [2000, 2000, 3900]
    det = [pil2M]

    pitches = np.linspace(128, 112, 17)

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: a convenience wrapper that runs scan_boite_pitch then a cd_saxs rocking
    #   scan back to back. See those functions' notes for the smi_plans equivalents.
    # 💡 smi_plans: nothing extra to migrate here beyond what the called plans already note.
    # === end smi_plans note ================================================
    yield from scan_boite_pitch(1)
    yield from cd_saxs(-60, 60, 121, 2)


def NEXAFS_Ti_edge(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS scan across the titanium edge (4950->5050 eV, 101 points) —
    #   it sweeps the X-ray energy and takes a WAXS image + beam reading at each step.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does a full energy scan like this in ONE line; it
    #   steps the energy safely (settling + beam feedback) and records energy/beam into the
    #   data and file name (no hand-built "{sample}_{energy}eV_xbpm{}"):
    #
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run("NEXAFS_echantillon2_Tiedge_ai1p4",
    #                           np.linspace(4950, 5050, 101), t=t,
    #                           dets=[pil900KW], geometry="grazing")   # current WAXS detector
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now; the 💡 lines just become
    #    unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan.
    #   See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_echantillon2_Tiedge_ai1p4"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 5010)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4990)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4970)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4950)


def NEXAFS_SAXS_Ti_edge(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a resonant NEXAFS + SAXS scan across the titanium edge (4950->5050 eV)
    #   — it sweeps the energy and takes a WAXS + SAXS image + beam reading at each step.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does a full energy scan in ONE line; it steps the
    #   energy safely (settling + beam feedback) and records energy/beam into the data:
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run("NEXAFS_SAXS_echantillon13realign_ai1p75_Tiedge",
    #                           np.linspace(4950, 5050, 101), t=t,
    #                           dets=[pil2M, pil900KW], geometry="grazing")
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now; the 💡 lines just become
    #    unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan.
    #   See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "NEXAFS_SAXS_echantillon13realign_ai1p75_Tiedge"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 5010)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4990)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4970)  # 💡 smi_plans: you can drop this stepped energy walk-back — move_energy_fb/energy_axis step the energy in safe hops, wait for it to settle, and handle the beam feedback. (Not broken, just no longer needed once you migrate.)
    yield from bps.mv(energy, 4950)


def GISAXS_scan_boite(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GISAXS line scan — it steps the sample x across a range (81 spots)
    #   and takes a SAXS image at each, to scan across a patterned "box".
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the line of positions for you and records
    #   position/beam into each image:
    #     from smi_plans import map_line_run
    #     yield from map_line_run("Echantillon13realign_gisaxs", axis="x",
    #                             center=43900, size=24000, num=81, dets=[pil2M], t=t)
    #   (Your script below still works, except the ⚠️ line.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan
    #   (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    sample = "Echantillon13realign_gisaxs_scanpolyperiod_e4950eV_ai1p75"
    x = np.linspace(55900, 31900, 81)

    det = [pil2M]

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    for k, xs in enumerate(x):
        yield from bps.mv(piezo.x, xs)

        name_fmt = "{sample}_pos{pos}"
        sample_name = name_fmt.format(sample=sample, pos="%2.2d" % k)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=1)


def fly_scan_ai(det, motor, cycle=1, cycle_t=10, phi=-0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a "fly" rocking scan — it opens the detector for one long exposure
    #   while continuously sweeping the angle motor back and forth across +/-30 deg, instead
    #   of stopping at each angle. (It drives the camera directly and busy-waits for it.)
    # 💡 NEWER, EASIER WAY: continuous/triggered acquisition like this is what 'smi_plans'
    #   acquisition + the CD-SAXS routines are built to manage cleanly (staging, triggering,
    #   and saving a proper run/documents instead of poking the camera by hand):
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     # cdsaxs_rock_run(name, th_start=phi-30, th_end=phi+30, ..., dets=cdsaxs_dets())
    #   Nothing here is broken, but note this style writes no data documents — smi_plans
    #   would record the run for you. (internal: Tier 0.)
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
    # WHAT THIS DOES: a CD-SAXS run-book — loops over named fields/backgrounds on a wafer and
    #   runs rocking scans at each (by calling the rocking helpers above).
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) + rocking
    #   routine (cdsaxs_rock_run) that loop your samples and record angle/position/beam for
    #   you. The rocking stage 'prs' (used by the helpers) is now 'stage.phi'.
    #   (Your script below still works; the helpers carry their own ⚠️ notes.) (internal: Tier 1.)
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
    # WHAT THIS DOES: runs CD-SAXS rocking scans at a couple of selected ("important")
    #   pitches (by calling cd_saxs_new).
    # 💡 NEWER, EASIER WAY: see cdsaxs_all_pitch / cdsaxs_pitch_survey in 'smi_plans', which
    #   sweep pitch positions and rock each, recording pitch/angle/beam for you.
    #   (Your script below still works, except the ⚠️ line; cd_saxs_new carries its own notes.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan
    #   (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p113nm", "p100nm"]

    if "bkg" in sample:
        x_off = [0, 0]
        y_off = [0, -13300]
    else:
        x_off = [0, 0]
        y_off = [0, -10500]

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y + y_of, num=num, exp_t=exp_t)


def mesure_rugo(sample, x, y, num=200, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS roughness ("rugosité") measurement — many repeats of a
    #   rocking scan at a single pitch position. 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: use the 'smi_plans' CD-SAXS rocking routine (rocking stage 'prs'
    #   is now 'stage.phi'); repeat it for your statistics:
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     # cdsaxs_rock_run(sample, th_start=..., th_end=..., th_num=..., dets=cdsaxs_dets())
    #   (Your script below still works, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' -> 'stage.phi'; and 'det_exposure_time(...)' must be
    #   run as a plan. See the ⚠️ notes below. (internal: Tier 1.)
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

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: a CD-SAXS direct-beam ("db") measurement at a pitch position, using the
    #   rocking stage 'prs'.
    # 💡 NEWER, EASIER WAY: use the 'smi_plans' CD-SAXS rocking routine (rocking stage 'prs'
    #   is now 'stage.phi'); for a true direct-beam check see direct_beam_scan_run.
    #   (Your script below still works, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' -> 'stage.phi'; and 'det_exposure_time(...)' must be
    #   run as a plan. See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    pitches = ["p100nm"]
    if "bkg" in sample:
        x_off = [0]
        y_off = [-13300]
    else:
        x_off = [0]
        y_off = [-10500]
    yield from bps.mv(prs, -1)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_db_{pit}_att9x60umSn"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        sample_id(user_name="PG", sample_name=sample_name)

        yield from bp.count([pil2M], num=1)


def NEXAFS_P_edge(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a NEXAFS scan across the phosphorus edge (2140->2200 eV, 61 points) —
    #   it sweeps the X-ray energy and takes a WAXS image + beam reading at each step.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' does a full energy scan in ONE line; it steps the
    #   energy safely (settling + beam feedback) and records energy/beam into the data:
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run("nexafs_s4_wa0_0.5deg", np.linspace(2140, 2200, 61), t=t,
    #                           dets=[pil900KW], geometry="grazing")   # current WAXS detector
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now; the 💡 lines just become
    #    unnecessary once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan.
    #   See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, 0)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    name = "nexafs_s4_wa0_0.5deg"

    energies = np.linspace(2140, 2200, 61)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.2f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2190)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
    yield from bps.mv(energy, 2180)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
    yield from bps.mv(energy, 2170)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
    yield from bps.mv(energy, 2160)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
    yield from bps.mv(energy, 2150)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
    yield from bps.mv(energy, 2140)
    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)


def cd_saxs_new2(th_ini, th_fin, th_st, exp_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS rocking scan (sample + background) — it rotates the sample
    #   through a range of tilt angles (with a small angle offset) and takes a SAXS image at
    #   each, then repeats for a background position. The rocking motor this script calls
    #   'prs' is what does the tilting.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS rocking routine that rocks the angle and
    #   records angle + beam into each image for you. The rocking stage 'prs' is now
    #   'stage.phi':
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     yield from cdsaxs_rock_run("sample-33", th_start=th_ini, th_end=th_fin,
    #                                th_num=th_st, dets=cdsaxs_dets(), t=exp_t)
    #     # (call it again for the background position.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' was removed — it's now 'stage.phi'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan.
    #   See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample = "sample-33"
    det = [pil2M]
    yield from bps.mv(piezo.y, 1000)

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

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



# h = db[-1]
# h = db[158]
# pd = h.table()['pin_diode_current2_mean_value'].get(1)

def cd_saxs_new(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil2M, pin_diode]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the core CD-SAXS rocking routine — it rotates the sample through tilt
    #   angles (th_ini -> th_fin) and takes a SAXS image at each, recording position + beam
    #   into a hand-built file name. The rocking motor this script calls 'prs' does the tilt.
    #   (Other functions here call this one per pitch/position.)
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a ready-made CD-SAXS rocking routine that records
    #   the angle/position/beam into each saved image for you (no hand-built
    #   "{sample}_num{}_{th}deg_x{}_y{}_..."). The rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     yield from cdsaxs_rock_run(sample, th_start=th_ini, th_end=th_fin, th_num=th_st,
    #                                dets=cdsaxs_dets(), t=exp_t, num=nume)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' was removed — it's now 'stage.phi'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan.
    #   See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_num{num}_{th}deg_x{x}_y{y}_z{z}_bpm{bpm}{md}"
        sample_name = name_fmt.format(sample=sample, num="%03d"%num, th="%2.2d"%theta, x = "%.2f" % (piezo.x.position), y = "%.2f" % (piezo.y.position), z = "%.2f" % (piezo.z.position), bpm="%1.3f"%xbpm3.sumX.get(), md = get_scan_md()) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)

def cd_saxs_newLigang(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil2M, pin_diode]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS rocking scan where the exposure time is increased at larger
    #   tilt angles (to compensate for the longer path), recording position/beam into the
    #   file name. 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: the 'smi_plans' CD-SAXS rocking routine handles the angle sweep
    #   and per-angle settings for you, recording angle/beam into each image (rocking stage
    #   'prs' is now 'stage.phi'):
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     # cdsaxs_rock_run(sample, th_start=th_ini, th_end=th_fin, th_num=th_st, ...)
    #   (Your script below still works, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' -> 'stage.phi'; and the per-angle 'det_exposure_time'
    #   must be run as a plan. See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        exp_ti=exp_t/abs(np.cos(np.deg2rad(theta)))
        print("*************************************************************************")
        print("new exposure time is : ", exp_ti)
        det_exposure_time(exp_ti, exp_ti)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_num{num}_{th}deg_x{x}_y{y}_z{z}_bpm{bpm}{md}_time{exp_ti}"
        sample_name = name_fmt.format(sample=sample, num="%03d"%num, th="%2.2d"%theta, x = "%.2f" % (piezo.x.position), y = "%.2f" % (piezo.y.position), z = "%.2f" % (piezo.z.position), bpm="%1.3f"%xbpm3.sumX.get(), md = get_scan_md(), exp_ti="%.2f" % exp_ti) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)

def dose(exp_t=1, sample='test', nume=1000, det=[pil2M, pin_diode]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a dose / beam-damage series — takes many SAXS images in a row at one
    #   spot (num=nume) to follow how the sample changes with accumulated X-ray dose.
    # 💡 NEWER, EASIER WAY: repeating shots at one point over time is the 'smi_plans' kinetics
    #   / time-series idea, which records elapsed time + beam into each image:
    #     from smi_plans import time_series_run
    #     yield from time_series_run(sample, num=nume, dets=[pil2M, pin_diode], t=exp_t)
    #   (Your script below still works, except the ⚠️ line.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan
    #   (see the ⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)


    name_fmt = "{sample}_num{num}_{th}deg_x{x}_y{y}_z{z}_bpm{bpm}{md}"
    sample_name = name_fmt.format(sample=sample, num="%03d"%nume, th="%2.2d"%(stage.th.position), x = "%.2f" % (piezo.x.position), y = "%.2f" % (piezo.y.position), z = "%.2f" % (piezo.z.position), bpm="%1.3f"%xbpm3.sumX.get(), md = get_scan_md()) # Philipp change, original: num="%2.2d"%num
    #sample_id(user_name="PG", sample_name=sample_name)
    sample_id(sample_name=sample_name)

    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.count(det, num=nume)




def sample_linqz(phi_min,phi_max,N):
    # smi_plans: no acquisition logic here — this just computes a list of rocking angles
    # spaced evenly in qz (a math helper). Nothing to migrate.
    qz_min = np.tan(np.deg2rad(phi_min))
    qz_max = np.tan(np.deg2rad(phi_max))

    # Linearly spaced qz
    qz = np.linspace(qz_min, qz_max, N)

    # Compute corresponding angles in degrees
    phi = np.rad2deg(np.arctan(qz))

    return phi

def cd_saxs_linqz(th_ini, th_fin, th_num, exp_t=0.1, sample='test', nume=1, det=[pil2M, pin_diode]):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS rocking scan variant — rotates the sample through the angle
    #   range and takes a SAXS image at each, recording position/beam into the file name.
    #   'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: use the 'smi_plans' CD-SAXS rocking routine, which records
    #   angle/beam into each image (rocking stage 'prs' is now 'stage.phi'):
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     # cdsaxs_rock_run(sample, th_start=th_ini, th_end=th_fin, th_num=th_num, ...)
    #   (Your script below still works, except the ⚠️ lines.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' -> 'stage.phi'; and 'det_exposure_time(...)' must be
    #   run as a plan. See the ⚠️ notes below. (internal: Tier 1.)
    # === end smi_plans note ================================================

    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    th_ls=sample_linqz(th_ini,th_fin,th_num)

    for num, theta in enumerate(th_ls):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        name_fmt = "{sample}_num{num}_{th}deg_x{x}_y{y}_z{z}_bpm{bpm}{md}"
        sample_name = name_fmt.format(sample=sample, num="%03d"%num, th="%.2f"%theta, x = "%.2f" % (piezo.x.position), y = "%.2f" % (piezo.y.position), z = "%.2f" % (piezo.z.position), bpm="%1.3f"%xbpm3.sumX.get(), md = get_scan_md()) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)


def cdsaxs_IBM_2024_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

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




def cdsaxsstd_2025_1_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling cd_saxs_new).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow: describe the samples
    #   once (SampleList with positions) and a bar helper visits each and rocks it, recording
    #   angle/position/beam into the data. The rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # or loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, ...)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The cd_saxs_new it calls also
    #    carries its own ⚠️ notes.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below). Also note 'prs' -> 'stage.phi'
    #   inside the rocking helper.
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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

def cdsaxsstd_2025Oct_1_Ligang(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 1

    names = ['S1_right_prsscan']
    
    ## with on-axis camera
    x =     [   7800
                    ]
    y=      [  2092
                    ]
    
    z=      [    -15800
                    ]
    
    ## with scattering pattern
    chi=    [  2.6
                 ]
    th =    [     1.91
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
            yield from cd_saxs_newLigang(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025_1A_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — loops a bar of named gratings, drives to each, and
    #   runs a CD-SAXS rocking scan there (by calling the rocking helper). 'prs' is the
    #   rocking stage.
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) and a
    #   rocking routine cdsaxs_rock_run that record angle/position/beam into the data for you.
    #   The rocking stage 'prs' is now 'stage.phi'.
    #   (Your script below still works, except the ⚠️ line; the rocking helper carries its
    #    own ⚠️ notes.) (internal: Tier 1.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan (see
    #   the ⚠️ note below); and 'prs' -> 'stage.phi' inside the rocking helper.
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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

def cdsaxsstd_2025_IBM_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Sam144H_run2']
    
    ## with on-axis camera
    x =     [  
                -15251 #-14764
                    ]
    y=      [  
               -4316 #-4299
                    ]
    
    z=      [   
                1095 #1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.5
                 ]
    th =    [     0
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
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            yield from bps.mv(piezo.y, ys+100)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureB%s'%(i+1), nume=1)
            
            yield from bps.mv(piezo.y, ys+200)
            for j in range(1):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureC%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+300)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t*0.1, sample=name+'measureD%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+400)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t*0.1, sample=name+'measureE%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

 
    yield from bps.mvr(piezo.y, 100)    
    dose(exp_t=1, sample=name+'measure_dose', nume=900)

#Sam144H_run1_dose_num900_00deg_x-15251.01_y-4415.96_z1795.06_bpm1.158_16.10keV_wa20.0_sdd9.0m_id282_000247_SAXS2M.tif
            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025_IBM_2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Sam36H_run1', 'Sam52H_run1']
    
    ## with on-axis camera
    x =     [  
                -10851,        -10851     #-14764
                    ]
    y=      [  
               1600,            6600    #-4299
                    ]
    
    z=      [   
                2100,            2100     #1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.5,             0.5
                 ]
    th =    [     0,           0
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
            yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            yield from bps.mv(piezo.y, ys+100)
            yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureB%s'%(i+1), nume=1)
            
            yield from bps.mv(piezo.y, ys+200)
            for j in range(1):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measureC%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+300)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t*0.1, sample=name+'measureD%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+400)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 121, exp_t=t*0.1, sample=name+'measureE%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

 
    yield from bps.mvr(piezo.y, 100)    
    dose(exp_t=1, sample=name+'measure_dose', nume=900)

            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025May_Philipp1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Anoinf_80nm']
    
    ## with on-axis camera
    x =     [  
                -17250    #-14764
                    ]
    y=      [  
               6800    #-4299
                    ]
    
    z=      [   
                -4800   #1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.3
                 ]
    th =    [     0
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

            yield from bps.mv(piezo.y, ys+0)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureA%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+100)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureB%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+200)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureC%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+300)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureD%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+400)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureE%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+500)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureF%s'%(j+1), nume=1)
            
            yield from bps.mv(piezo.y, ys+600)
            for j in range(10):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureG%s'%(j+1), nume=1)

            yield from bps.mv(piezo.y, ys+700)
            for j in range(20):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureH%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025May_Philipp2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Anoinf_80nm_run2']
    
    ## with on-axis camera
    x =     [  
                -17250    #-14764
                    ]
    y=      [  
               7150    #-4299
                    ]
    
    z=      [   
                -4800   #1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.3
                 ]
    th =    [     0
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
            
            for j in range(5):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t, sample=name+'measureA%s'%(j+1), nume=1)
                yield from cd_saxs_linqz(60+phi_offest, -60+phi_offest, 61, exp_t=t, sample=name+'measureA%sr'%(j+1), nume=1)
                

            yield from bps.mv(piezo.y, ys+100)
            for j in range(20):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureB%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025May_Philipp3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Anoinf_95nm',    'Anoinf_95nm',       'Anoinf_random',       'Anoinf_SuperC320'  ,  'Anoinf_SuperC240']
    
    ## with on-axis camera
    x =     [  
                -17250   ,         -17250 ,           -21250,           -21250,           -21250  #-14764
                    ]
    y=      [  
               5151       ,           3100 ,         3150,                5150,                7152#-4299
                    ]
    
    z=      [   
                -4500   ,            -4500 ,         -4500,               -4500,               -4500#1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.3,                   0.3,           0.2,                   0.2,                0.2
                 ]
    th =    [     0.5,            0.5,                0.5,                  0.5,                0.5
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
            
            for j in range(5):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t, sample=name+'measureA%s'%(j+1), nume=1)
                #yield from cd_saxs_linqz(60+phi_offest, -60+phi_offest, 61, exp_t=t, sample=name+'measureA%sr'%(j+1), nume=1)
                

            yield from bps.mv(piezo.y, ys+100)
            for j in range(20):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureB%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")


## /home/xf12id/SWAXS_user_scripts/CDSAXS/30-user-CDSAXS_Philipp.py

def cdsaxsstd_2025_10_simplePRS(N=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a simple CD-SAXS rocking scan — it sweeps the rocking stage through
    #   -60 to +60 degrees in one coordinated scan (121 points), N times, recording SAXS +
    #   beam at each angle. The rocking motor this script calls 'prs' is what tilts.
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a ready-made CD-SAXS rocking routine that records
    #   angle + beam into each image for you. The rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_rock_run, cdsaxs_dets
    #     yield from cdsaxs_rock_run("S1", th_start=-60, th_end=60, th_num=121,
    #                                dets=cdsaxs_dets())
    #   (Your script below still works as-is, except for the ⚠️ line.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' was removed — it's now 'stage.phi' (see the ⚠️ note
    #   on the rel_scan line below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    #sample_id(user_name='test', sample_name=f'test_S1_left_prsscan_{get_scan_md()}_xbpm3sumX{xbpm3.sumX.get():.2f}')
    for _ in range(N):
        yield from rel_scan([pil2M, pin_diode,xbpm3],prs , -60, 60, 121)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025_10_simplePRS2(N=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same simple CD-SAXS rocking scan as simplePRS, with a slightly wider
    #   angle range (-60 to +65, 126 points). 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: see cdsaxsstd_2025_10_simplePRS above — use cdsaxs_rock_run with
    #   stage.phi (the new name for 'prs'). (Your script below still works, except the ⚠️ line.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' was removed — it's now 'stage.phi' (see ⚠️ below).
    # === end smi_plans note ================================================
    #sample_id(user_name='test', sample_name=f'test_S1_left_prsscan_{get_scan_md()}_xbpm3sumX{xbpm3.sumX.get():.2f}')
    for _ in range(N):
        yield from rel_scan([pil2M, pin_diode,xbpm3],prs , -60, 65, 126)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025_10_simplePRS3(N=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same simple CD-SAXS rocking scan as simplePRS, coarser sampling
    #   (-60 to +64, 63 points). 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: see cdsaxsstd_2025_10_simplePRS above — use cdsaxs_rock_run with
    #   stage.phi (the new name for 'prs'). (Your script below still works, except the ⚠️ line.)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'prs' was removed — it's now 'stage.phi' (see ⚠️ below).
    # === end smi_plans note ================================================
    #sample_id(user_name='test', sample_name=f'test_S1_left_prsscan_{get_scan_md()}_xbpm3sumX{xbpm3.sumX.get():.2f}')
    for _ in range(N):
        yield from rel_scan([pil2M, pin_diode,xbpm3],prs , -60, 64, 63)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


    print("====== Done with CD-SAXS scan")

def cdsaxsstd_2025_1CD_yager(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book (CD variant) — loops a bar of named gratings, drives
    #   to each, and runs a CD-SAXS rocking scan there. 'prs' is the rocking stage.
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) and a
    #   rocking routine cdsaxs_rock_run that record angle/position/beam into the data for you.
    #   The rocking stage 'prs' is now 'stage.phi'.
    #   (Your script below still works, except the ⚠️ line; the rocking helper carries its
    #    own ⚠️ notes.) (internal: Tier 1.)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must be run as a plan (see
    #   the ⚠️ note below); and 'prs' -> 'stage.phi' inside the rocking helper.
    # === end smi_plans note ================================================
    det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(exp_t, exp_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)
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
    # WHAT THIS DOES: a rectangle (x/y grid) scan over several samples — steps a grid of
    #   positions between xmin..xmax / ymin..ymax and takes an image at each spot.
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds an x/y position grid for you and records the
    #   position/beam into each image:
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run("samA", x_center=-23300, y_center=..., x_size=1000,
    #                             y_size=..., x_num=..., y_num=..., dets=[pil2M], t=t)
    #   (Your script below still works as-is; nothing here is broken.) (internal: Tier 2.)
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


def cdsaxsstd_2025September_Philipp1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — it loops over a bar of named gratings, drives to
    #   each position (x/y/z/chi/th), and runs a CD-SAXS rocking scan there (by calling the
    #   rocking helper). The rocking motor this script calls 'prs' is what tilts the sample.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS "bar" workflow (cdsaxs_bar) plus a
    #   rocking routine (cdsaxs_rock_run) that record the rocking angle, position and beam
    #   into each saved image for you — instead of hand-building the long file name. The
    #   rocking stage 'prs' is now 'stage.phi':
    #     from smi_plans import cdsaxs_bar, cdsaxs_rock_run, cdsaxs_dets, SampleList
    #     # loop your samples and call cdsaxs_rock_run(name, th_start=-60, th_end=60, th_num=121,
    #     #                                            dets=cdsaxs_dets(), t=t)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which needs a fix now. The rocking helper it calls
    #    also carries its own ⚠️ 'prs'->'stage.phi' note.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the
    #   exposure unless run as a plan (see the ⚠️ note below).
    # === end smi_plans note ================================================
    # det = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = 0 #prob -2.3?

    names = ['Anoinf_95nm',    'Anoinf_95nm',       'Anoinf_random',       'Anoinf_SuperC320'  ,  'Anoinf_SuperC240']
    
    ## with on-axis camera
    x =     [  
                -17250   ,         -17250 ,           -21250,           -21250,           -21250  #-14764
                    ]
    
    y=      [  
               5151       ,           3100 ,         3150,                5150,                7152#-4299
                    ]
    
    z=      [   
                -4500   ,            -4500 ,         -4500,               -4500,               -4500#1955
                    ]
    
    ## with scattering pattern
    chi=    [  
               0.3,                   0.3,           0.2,                   0.2,                0.2
                 ]
    th =    [     0.5,            0.5,                0.5,                  0.5,                0.5
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
            
            for j in range(5):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t, sample=name+'measureA%s'%(j+1), nume=1)
                #yield from cd_saxs_linqz(60+phi_offest, -60+phi_offest, 61, exp_t=t, sample=name+'measureA%sr'%(j+1), nume=1)
                

            yield from bps.mv(piezo.y, ys+100)
            for j in range(20):
                yield from cd_saxs_linqz(-60+phi_offest, 60+phi_offest, 61, exp_t=t*0.1, sample=name+'measureB%s'%(j+1), nume=1)
                yield from bps.mvr(piezo.y, 20)

            
            # yield from cd_saxs_new(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
            # else:
            #     yield from cd_saxs_new(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)

    print("====== Done with CD-SAXS scan")
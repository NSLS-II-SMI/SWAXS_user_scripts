def run_simple(exp=0.05, t=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one SAXS+WAXS image of a roll-to-roll-printed sample, stamping the
    #   Lakeshore temperature into the file name. (Roll-to-roll = the film moves past the beam.)
    #
    # 💡 NEWER, EASIER WAY: a single recorded shot is one 'smi_plans.acquire' (or giwaxs_run),
    #   which records the temperature, beam, and positions straight into the data and file name:
    #
    #     from smi_plans import acquire
    #     yield from acquire("recheck_90c_0.1mms", [pil2M, pil900KW], [], t=exp)
    #
    #   ALSO: you can DELETE the two 'cam.file_path.put(...)' lines below. Those used to force
    #   where the .tif files were written; the beamline now uses Tiled to track files, so you no
    #   longer set the write path by hand — it's handled for you. (Leaving them in isn't fatal, but
    #   they point at an old 2019 path and aren't needed.)
    #
    #   (Use 'pil900KW' for the current WAXS detector — see the ⚠️ notes below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW' (a few lines
    #   below reference it); (2) the 'det_exposure_time(...)' calls need to be run as a plan.
    #   (internal: Tier 1 — roll-to-roll printing.)
    # === end smi_plans note ================================================
    name = "JW"
    sample = "recheck_90c_0.1mms"
    pil2M.cam.file_path.put(
        f"/ramdisk/images/users/2019_3/304549_Headrick/1M/%s" % sample
    )
    pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). Also: this 'cam.file_path.put(...)' write-path override is no longer needed — Tiled handles file paths now.
        f"/GPFS/xf12id1/data/images/users/2019_3/304549_Headrick3/300KW/%s" % sample
    )
    name_fmt = "{samp}_{temperature}C"
    temp = ls.ch1_read.value
    det_exposure_time(exp, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp, t)  — or at the prompt:  RE(det_exposure_time(exp, t)). (smi_plans' acquire/giwaxs_run sets exposure for you via t=.)
    sample_name = name_fmt.format(samp=sample, temperature=temp)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bps.mv(waxs, 12)
    yield from bp.count([pil2M, pil300KW], num=1)  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def run_fullgiwaxs(t=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a full GIWAXS scan (sweeping the WAXS arc) of one roll-to-roll sample,
    #   stamping the Lakeshore temperature into the file name.
    #
    # 💡 NEWER, EASIER WAY: a single-sample arc sweep is one 'smi_plans.giwaxs_run', which records
    #   arc / temperature / beam into each image and the file name for you:
    #     from smi_plans import giwaxs_run
    #     yield from giwaxs_run("recheck_90c_0.1mms", arc=[0, 19.5, 4], t=t)
    #   ALSO: you can delete the two 'cam.file_path.put(...)' lines — Tiled handles file paths now,
    #   so write-path overrides are no longer needed. (Use 'pil900KW' — see ⚠️ below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls need to be run as a plan. (internal: Tier 1.)
    # === end smi_plans note ================================================
    name = "JW"
    sample = "recheck_90c_0.1mms"
    pil2M.cam.file_path.put(
        f"/ramdisk/images/users/2019_3/304549_Headrick/1M/%s" % sample
    )
    pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). Also: this 'cam.file_path.put(...)' write-path override is no longer needed — Tiled handles file paths now.
        f"/GPFS/xf12id1/data/images/users/2019_3/304549_Headrick3/300KW/%s" % sample
    )
    waxs_range = [0, 19.5, 4]  # up to 3.2 A-1
    # waxs_range = [0, 13, 3] #up to 2.3 A-1
    name_fmt = "{samp}_{temperature}C"
    temp = ls.ch1_read.value
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_run sets exposure for you via t=.)
    sample_name = name_fmt.format(samp=sample, temperature=temp)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.scan([pil2M, pil300KW], waxs, *waxs_range)  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration). ('pil2M' here is fine.)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def run_BD(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a beam-damage / kinetics series — takes 300 WAXS frames in a row on one
    #   spot (with several ROI channels), stamping temperature into the file name.
    #
    # 💡 NEWER, EASIER WAY: a repeated time series is 'smi_plans.time_series_run' / 'kinetics_run'
    #   (it timestamps each frame and records beam/temperature for you):
    #     from smi_plans import time_series_run
    #   ALSO: delete the 'cam.file_path.put(...)' lines — Tiled handles file paths now.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' (and its ROI channels) were retired — the current
    #   WAXS detector is 'pil900KW'; (2) the 'det_exposure_time(...)' calls need to be run as a
    #   plan. (internal: Tier 1.)
    # === end smi_plans note ================================================
    num = 300
    name = "JW"
    sample = "60c_0.2mms"
    pil2M.cam.file_path.put(
        f"/ramdisk/images/users/2019_3/304549_Headrick/1M/%s" % sample
    )
    pil300KW.cam.file_path.put(  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (different camera, so check beam-center/calibration). Also: this 'cam.file_path.put(...)' write-path override is no longer needed — Tiled handles file paths now.
        f"/GPFS/xf12id1/data/images/users/2019_3/304549_Headrick/300KW/%s" % sample
    )
    name_fmt = "{samp}_{temperature}C"
    temp = ls.ch1_read.value
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' time_series_run sets exposure for you via t=.)
    yield from bps.mv(waxs, 12)
    sample_name = name_fmt.format(samp=sample, temperature=temp)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.count([pil300KW, pil300kwroi2, pil300kwroi3, pil300kwroi4], num=num)  # ⚠️ FIXME(smi_plans): 'pil300KW' and its ROI channels (pil300kwroi2/3/4) were removed (this would error). The current WAXS detector is 'pil900KW' — use it (and its ROIs) instead (different camera, so check beam-center/calibration).
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def giwaxs_insitu_heating(tim=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ GIWAXS heating run — aligns the sample, sets the incident angle,
    #   then takes a WAXS image at each WAXS-arc position.
    #
    # 💡 NEWER, EASIER WAY: a single-sample GIWAXS over arc angles is one 'smi_plans.giwaxs_run'
    #   with align (records arc/angle/beam into each image and file name):
    #     from smi_plans import giwaxs_run, align_sample
    #     yield from giwaxs_run("PHBTBTC10_in_situ_sam2_post1", incident_angles=[0.1],
    #                           arc=[0, 20], t=tim, align=align_sample)
    #   (Optional — works as-is EXCEPT the ⚠️ exposure lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================

    # samples = ['PHBTBTC10_quenched_sam1_run2_cool_down_40C']
    samples = ["PHBTBTC10_in_situ_sam2_post1"]

    x_list = [0]
    incident_angle = 0.1

    name = "RH"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    dets = [pil900KW]

    waxs_arc = [0, 20]
    name_fmt = "{sample}_16.1keV_ai{ai}_wa{waxs}"

    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (smi_plans' giwaxs_run sets exposure for you via t=.)

    for s in samples:
        # yield from bps.mvr(piezo.x, 60)

        # yield from alignement_gisaxs(0.1)
        yield from alignement_gisaxs_hex(angle=incident_angle, rough_y=1)
        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + incident_angle)

        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            sample_name = name_fmt.format(
                sample=s, ai="%1.1f" % incident_angle, waxs="%2.1f" % wa
            )
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name=name, sample_name=sample_name)
            yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def giwaxs_insitu_heating_norealignement(tim=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same as giwaxs_insitu_heating, but skips re-aligning (assumes already
    #   aligned) — sets the incident angle and takes a WAXS image at each WAXS-arc position.
    #
    # 💡 NEWER, EASIER WAY: same as above — 'smi_plans.giwaxs_run' (just omit align= if you don't
    #   want to re-align). It records arc/angle/beam for you. (Optional — works as-is EXCEPT the
    #   ⚠️ exposure lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # samples = ['PHBTBTC10_slow_cool_sam3_heat_up_25C']
    # samples = ['PHBTBTC10_slow_cool_sam3_run2_heat_up_25C']
    # samples = ['PHBTBTC10_quenched_sam1_heat_up_25C']
    samples = ["Chad_sample"]

    x_list = [0]
    incident_angle = 0.1
    # incident_angle = 0.2

    name = "RH"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    dets = [pil900KW]

    waxs_arc = [0, 20]
    name_fmt = "{sample}_16.1keV_ai{ai}_wa{waxs}"

    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (smi_plans' giwaxs_run sets exposure for you via t=.)

    for x, s in zip(x_list, samples):
        # yield from bps.mv(piezo.x, 60)

        ai0 = piezo.th.position
        yield from bps.mv(piezo.th, ai0 + incident_angle)

        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            sample_name = name_fmt.format(
                sample=s, ai="%1.1f" % incident_angle, waxs="%2.1f" % wa
            )
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name=name, sample_name=sample_name)
            yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def alignement_h():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick GISAXS alignment (hexapod) then sets WAXS and nudges theta.
    #   (Alignment helper; nothing broken.)
    #
    # 💡 NEWER, EASIER WAY: alignment like this is 'align_sample' in smi_plans (run once, recorded
    #   with the data).
    # === end smi_plans note ================================================
    yield from alignement_gisaxs_hex(0.1)
    yield from bps.mv(waxs, 10)
    yield from bps.mvr(stage.th, 0.1)


def giwaxs_insitu_roll(t=0.1, tim=180):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ roll-to-roll GIWAXS — a single long, multi-frame WAXS exposure
    #   (single frame time t, total time tim) while the printed film rolls past the beam.
    #
    # 💡 NEWER, EASIER WAY: a roll-to-roll / in-situ time series is 'smi_plans' kinetics or, when
    #   the print is the trigger, the printing presets ('printer_triggered_run',
    #   'print_crystallization_followup_run'). They timestamp each frame and record beam/positions:
    #     from smi_plans import time_series_run    # or printer_triggered_run for printer hand-off
    #     yield from time_series_run("PHBTBTC10_solution_sam3", [pil900KW], t=t, total=tim)
    #   (Optional — works as-is EXCEPT the ⚠️ exposure lines.) (internal: Tier 1 — roll-to-roll.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # pil900KW.unstage()
    samples = "PHBTBTC10_solution_sam3"

    name = "RH"
    dets = [pil900KW]
    name_fmt = "{sample}_16.1keV_ai{ai}_wa{waxs}"

    det_exposure_time(t, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, tim)  — or at the prompt:  RE(det_exposure_time(t, tim)). (smi_plans' time_series_run sets exposure for you via t=.)

    # for s in samples:
    #    yield from bps.mvr(piezo.x, 60)

    sample_name = name_fmt.format(sample=samples, ai="%1.1f" % 0.1, waxs="%2.1f" % 10.0)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def giwaxs_insitu_roll_cooling(t=0.5, tim=600):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same as giwaxs_insitu_roll but for a cooling run — one long multi-frame WAXS
    #   exposure as the sample cools.
    #
    # 💡 NEWER, EASIER WAY: same as giwaxs_insitu_roll — 'smi_plans.time_series_run' (timestamps
    #   each frame). (Optional — works as-is EXCEPT the ⚠️ exposure lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # pil900KW.unstage()
    samples = "PHBTBTC10_solution_sam3_cooling"

    name = "RH"
    dets = [pil900KW]
    name_fmt = "{sample}_16.1keV_ai{ai}_wa{waxs}"

    det_exposure_time(t, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, tim)  — or at the prompt:  RE(det_exposure_time(t, tim)). (smi_plans' time_series_run sets exposure for you via t=.)

    sample_name = name_fmt.format(sample=samples, ai="%1.1f" % 0.1, waxs="%2.1f" % 10.0)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def giwaxs_insitu_single(t=0.5, tim=0.5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single in-situ GIWAXS shot (one long multi-frame exposure) on a
    #   solution-cooled roll-to-roll sample, after a small x move.
    #
    # 💡 NEWER, EASIER WAY: a single recorded shot is one 'smi_plans.acquire' / giwaxs_run; for a
    #   timed series use time_series_run. It records beam/positions for you. (Optional — works
    #   as-is EXCEPT the ⚠️ exposure lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # pil900KW.unstage()
    samples = "PHBTBTC10_solution_cooldown_25C_sam3"

    name = "RH"
    dets = [pil900KW]
    name_fmt = "{sample}_16.1keV_ai{ai}_wa{waxs}"

    det_exposure_time(t, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, tim)  — or at the prompt:  RE(det_exposure_time(t, tim)). (smi_plans' giwaxs_run/time_series_run sets exposure for you via t=.)

    for s in samples:
        yield from bps.mvr(piezo.x, -60)

    sample_name = name_fmt.format(sample=samples, ai="%1.1f" % 0.1, waxs="%2.1f" % 10.0)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def giwaxs_headrick_2022_1(t=0.5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS run over a bar of 6 samples — for each sample it moves there,
    #   aligns, then for each WAXS arc and incident angle takes a WAXS+SAXS image.
    #
    # 💡 NEWER, EASIER WAY: this "bar of samples × arc × angle" is the 'smi_plans' multi-sample
    #   GIWAXS helper. List the bar once and it walks it, aligns each, sweeps arc/angle, and
    #   records angle/arc/beam into every image and file name:
    #     from smi_plans import SampleList, giwaxs_bar, align_sample
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, z=z_piezo)
    #     yield from giwaxs_bar(samples, incident_angles=[0.1], arc=[0, 20], t=t, align=align_sample)
    #   (Optional — works as-is EXCEPT the ⚠️ exposure line.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call below needs to be run as a plan.
    # === end smi_plans note ================================================

    names = [
        "Chad_S1_1",
        "Chad_S1_2",
        "Chad_S2_1",
        "Chad_S2_2",
        "Chad_S3_1",
        "Chad_S3_2",
    ]
    x_piezo = [57000, 45000, 10000, -4000, -39000, -51000]
    y_piezo = [5500, 5500, 5500, 5500, 5500, 5500]
    z_piezo = [1100, 1100, 1100, 1100, 1100, 1100]
    x_hexa = [0, 0, 0, 0, 0, 0]

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

    waxs_arc = [0, 20]
    angle = [0.1]
    # angle = [5]

    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, 0.6)

        yield from alignement_gisaxs(angle=0.1)

        ai0 = piezo.th.position
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, an in enumerate(angle):
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.th, ai0 + an)
                name_fmt = "{sample}_16.1keV_ai{angl}deg_wa{waxs}_5m"
                sample_name = name_fmt.format(
                    sample=name, angl="%3.2f" % an, waxs="%2.1f" % wa
                )
                sample_id(user_name="RH", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)


def giwaxs_headrick_2022_2(t=0.5):
    """
    GIWAXS scans duing 2022_2 cycle, GU-308850
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS bar run (2022_2 cycle) — for each sample it aligns (with an x
    #   offset), then for each WAXS arc and incident angle records a WAXS (and SAXS at low arc)
    #   image, building a rich file name from the recorded energy / SDD / beam.
    #
    # 💡 NEWER, EASIER WAY: same as giwaxs_headrick_2022_1 — 'smi_plans.giwaxs_bar' with a
    #   SampleList walks the bar, aligns, sweeps arc/angle, and records energy/SDD/beam straight
    #   into the data and file name (so you don't build "{sample}_{energy}keV_wa{wax}..." by hand):
    #     from smi_plans import SampleList, giwaxs_bar, align_sample
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo, z=z_piezo)
    #     yield from giwaxs_bar(samples, incident_angles=[0.1], arc=[0, 20], t=t, align=align_sample)
    #   (Optional — works as-is EXCEPT the ⚠️ exposure line.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call below needs to be run as a plan.
    # === end smi_plans note ================================================

    user_name = "AD"

    # names =   [ 'ADS_1', 'ADS_2', 'ADS_3', 'ADS_4', 'ADS_5' ]
    # x_piezo = [   46400, 29500, 9500, -7500, -28500         ]
    # y_piezo = [    4600, 4600, 4600, 4600, 4600             ]
    # z_piezo = [       0, 0, 4000, -1000, 1000               ]
    # x_hexa =  [       0, 0, 0, 0, 0                         ]
    names = ["ADS_3"]
    x_piezo = [14400]
    y_piezo = [4600]
    z_piezo = [1000]
    x_hexa = [0]

    # Check sample names just in case
    names = [n.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "}) for n in names]

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

    # Geometry conditions
    waxs_angles = [0, 20]
    inc_angles = [0.1]
    alignment_offset_x = 100  # microns
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' giwaxs_bar sets exposure for you via t=.)

    # Skip samples
    skip = 0

    for name, xs, zs, ys, xs_hexa in zip(
        names[skip:], x_piezo[skip:], z_piezo[skip:], y_piezo[skip:], x_hexa[skip:]
    ):

        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs - alignment_offset_x)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, -1.5)

        try:
            yield from alignement_gisaxs(0.1)
        except:
            yield from alignement_gisaxs(0.4)

        yield from bps.mv(piezo.x, xs)

        ai0 = piezo.th.position
        for wa in waxs_angles:

            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]

            for ai in inc_angles:
                # yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.th, ai0 + ai)

                # Metadata
                name_fmt = "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_bpm{xbpm}_ai{ai}"
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                sample_name = name_fmt.format(
                    sample=name,
                    energy="%.1f" % e,
                    sdd="%.1f" % sdd,
                    wax=str(wa).zfill(4),
                    xbpm="%4.3f" % bpm,
                    ai="%.1f" % ai,
                )
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)
            yield from bps.mv(piezo.th, ai0)


def alignement_h_2022_2(wa=10, inc_angle=0.1):
    """
    Align sample using hexapod and move to experimental conditions

    Params:
        wa (float): WAXS arc angle in degrees,
        inc_angle (float): angle of incidence for the GIWAXS.

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: aligns the sample (hexapod), then moves to the chosen WAXS arc and incident
    #   angle. (Alignment helper; nothing broken.)
    #
    # 💡 NEWER, EASIER WAY: alignment like this is 'align_sample' in smi_plans (run once, recorded
    #   with the data, then passed as align= to your run).
    # === end smi_plans note ================================================
    yield from alignement_gisaxs_hex(angle=inc_angle, rough_y=1)
    yield from bps.mv(waxs, wa)
    yield from bps.mvr(stage.th, inc_angle)


def giwaxs_insitu_roll_cooling_2022_2(t=0.1, tim=180):
    """
    In situ GIWAXS at WAXS 10 deg and incident angle 0.1 deg

    Remember to change sample name!

    Params:
        t (float): exposure time for a single detector frame,
        tim (float): total exposure time including all frames.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ roll-to-roll GIWAXS cooling run (2022_2) — one long multi-frame
    #   WAXS exposure at fixed arc/angle, with a rich file name from recorded energy/SDD/beam.
    #
    # 💡 NEWER, EASIER WAY: a roll-to-roll in-situ series is 'smi_plans.time_series_run' (or the
    #   printing presets if the printer drives it). It timestamps each frame and records
    #   energy/SDD/beam for you. (Optional — works as-is EXCEPT the ⚠️ exposure lines.)
    #   (internal: Tier 1 — roll-to-roll.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # pil900KW.unstage()
    user_name = "AD"
    sample = "PHBTBTC10_in_situ_quene_sam1"

    ai = 0.1
    dets = [pil900KW]
    det_exposure_time(t, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, tim)  — or at the prompt:  RE(det_exposure_time(t, tim)). (smi_plans' time_series_run sets exposure for you via t=.)

    # Metadata
    name_fmt = "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_bpm{xbpm}_ai{ai}"
    bpm = xbpm3.sumX.get()
    e = energy.energy.position / 1000
    sdd = pil2M_pos.z.position / 1000
    wa = waxs.arc.user_readback.value
    wa = str(np.round(wa, 1)).zfill(4)

    sample_name = name_fmt.format(
        sample=name,
        energy="%.1f" % e,
        sdd="%.1f" % sdd,
        wax=wa,
        xbpm="%4.3f" % bpm,
        ai="%.1f" % ai,
    )
    sample_id(user_name=user_name, sample_name=sample_name)

    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=name, sample_name=sample_name)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


def giwaxs_insitu_roll_2022_2(t=0.1, tim=600):
    """
    In situ GIWAXS at WAXS at 10 deg and incident angle of 0.1 deg cooling 30 deg C / min

    Remember to change sample name!

    Params:
        t (float): exposure time for a single detector frame,
        tim (float): total exposure time including all frames.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: another in-situ roll-to-roll GIWAXS run (2022_2, cooling 30 C/min) — one
    #   long multi-frame WAXS exposure with a rich file name from recorded energy/SDD/beam.
    #
    # 💡 NEWER, EASIER WAY: same as giwaxs_insitu_roll_cooling_2022_2 — 'smi_plans.time_series_run'
    #   (timestamps each frame, records energy/SDD/beam). (Optional — works as-is EXCEPT the ⚠️
    #   exposure lines.) (internal: Tier 1.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below need to be run as a plan.
    # === end smi_plans note ================================================
    # pil900KW.unstage()
    user_name = "AD"
    sample = "PHBTBTC10_in_situ_sam11_post"

    ai = 0.1
    dets = [pil900KW]
    det_exposure_time(t, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, tim)  — or at the prompt:  RE(det_exposure_time(t, tim)). (smi_plans' time_series_run sets exposure for you via t=.)

    # Metadata
    name_fmt = "{sample}_{energy}keV_wa{wax}_sdd{sdd}m_bpm{xbpm}_ai{ai}"
    bpm = xbpm3.sumX.get()
    e = energy.energy.position / 1000
    sdd = pil2M_pos.z.position / 1000
    wa = waxs.arc.user_readback.value
    wa = str(np.round(wa, 1)).zfill(4)

    sample_name = name_fmt.format(
        sample=sample,
        energy="%.1f" % e,
        sdd="%.1f" % sdd,
        wax=wa,
        xbpm="%4.3f" % bpm,
        ai="%.1f" % ai,
    )
    sample_id(user_name=user_name, sample_name=sample_name)

    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=user_name, sample_name=sample)
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).

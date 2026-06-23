def run_caps_fastRPI(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each WAXS-arc angle, steps to each capillary on the bar and takes
    #   one SAXS+WAXS frame (a temperature-jump capillary bar at 16.1 keV).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   whole sample bar for you and records the WAXS-arc angle, beam, and detector distance
    #   into the data + file name. Same scan as below:
    #
    #     from smi_plans import SampleList, transmission_bar       # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["LC-O38-6-100Cto40C", "LC-O37-7-100Cto40C",
    #                "LC-O36-9-100Cto40C", "LC-O35-8-100Cto40C"],
    #         piezo_x=[6908, 13476, 19764, 26055],
    #     )
    #     yield from transmission_bar(bar, t=t, waxs_arc=tuple(np.linspace(0, 45.5, 8)))
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT for the
    #    lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' calls must run as plans — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    x_list = [6908, 13476, 19764, 26055]  #
    # Detectors, motors:
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_range = np.linspace(0, 45.5, 8)
    samples = [
        "LC-O38-6-100Cto40C",
        "LC-O37-7-100Cto40C",
        "LC-O36-9-100Cto40C",
        "LC-O35-8-100Cto40C",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        for sam, x in zip(samples, x_list):
            yield from bps.mv(piezo.x, x)
            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sam, waxs="%2.1f" % wa)
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.5 s" only takes effect if run as a plan:  yield from det_exposure_time(0.5)  (or  RE(det_exposure_time(0.5))).


def run_saxs_linkamRPI(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS run while scanning the hexapod height (stage.y)
    #   over a small range — a Linkam capillary measurement.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans', which can do a SAXS scan along
    #   a motor in one call and record the beam/distance/temperature into the data + file name
    #   (so you don't carry the name by hand). For a height scan like this:
    #
    #     from smi_plans import map_line_run        # do this once per session
    #     yield from map_line_run("S66_JA-B5O2-24w-1-04", stage.y, -4.23, -3.15, 5,
    #                             t=t, dets=[pil2M])
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT the lines
    #    marked ⚠️ which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls must run as plans — see
    #   the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    names = ["S66_JA-B5O2-24w-1-04"]
    user = "SL"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

    y_range = [-4.23, -3.15, 5]

    # Detectors, motors:
    dets = [pil2M]
    # waxs_range = np.linspace(45.5, 0, 8)

    name_fmt = "{sam}"
    sample_name = name_fmt.format(sam=names[0])
    sample_id(user_name=user, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.scan(dets, stage.y, *y_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_saxs_cap_temp_2022_2(t=0.5, temp=25):
    """
    Single SAXS measurement

    Linkam capillary stage driven from a laptop with temperature read from Lakeshore.
    Scripts automatically handles attenuators and pin diode current readout.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: inserts attenuators, opens the fast shutter to read the pin-diode
    #   current, removes them, then takes a single SAXS run (a y-scan) and crams the energy,
    #   temperature, detector distance, scan-id and pin-diode reading into the file name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans'. It records all that context
    #   (energy, temperature, beam, distance) INTO the data and builds the file name from the
    #   recorded values, so you don't hand-assemble that long "{energy}keV_{temp}degC_..."
    #   string. A transmission run that captures the same idea:
    #
    #     from smi_plans import transmission_run     # do this once per session
    #     yield from transmission_run("A16_NaI", t=t, dets=[pil2M],
    #                                 reads=[energy, pin_diode])
    #     # filename tokens like {energy_energy} are filled from the recorded stream for you.
    #
    #   (The attenuator/pin-diode steps and att2_*/pin_diode names below are all fine and
    #    still work. This is just a tidier option to try later — EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls must run as plans — see
    #   the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    y_coord = 1.9
    y_range = [0, 0.6]
    n_points = 1
    name = "A16_NaI"
    user = "HH"
    # name = 'test'
    # user = 'test'

    # Mo 20 um 1x and 2x
    attenuators = [att2_1, att2_2]

    # Insert attenuators, open fast shutter, read pin diode current
    # close fast shutter, remove attenuators
    yield from bps.mv(stage.y, y_coord)

    for att in attenuators:
        yield from bps.mv(att.open_cmd, 1)
        yield from bps.sleep(2)

    fs.open()
    yield from bps.sleep(0.3)
    pd_current = pdcurrent1.get()
    fs.close()

    for att in attenuators:
        yield from bps.mv(att.close_cmd, 1)
        yield from bps.sleep(1)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
    dets = [pil2M, pdcurrent1]

    # Metadata
    e = energy.position.energy / 1000
    wa = waxs.arc.position
    wa = str(np.round(float(wa), 1)).zfill(4)
    # temp = ls.input_A.get() - 273.15
    # temp = 10
    temp = str(np.round(float(temp), 1)).zfill(5)
    sdd = pil2M_pos.z.position / 1000
    scan_id = db[-1].start["scan_id"] + 1
    # bpm = xbpm3.sumX.get()

    # Sample name
    name_fmt = "{sample}_{energy}keV_{temp}degC_wa{wax}_sdd{sdd}m_id{scan_id}_pd{pd}"
    sample_name = name_fmt.format(
        sample=name,
        energy="%.2f" % e,
        temp=temp,
        wax=wa,
        sdd="%.1f" % sdd,
        scan_id=scan_id,
        pd="%.0f" % pd_current,
    )
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=user, sample_name=sample_name)

    yield from bp.rel_scan(dets, stage.y, *y_range, n_points)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_contRPI(t=1, numb=100, sleep=5):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes 'numb' SAXS+WAXS frames in a row, with a pause between each —
    #   a simple continuous/time-series acquisition.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' with a dedicated time-series
    #   runner that takes N frames at a fixed period as ONE recorded run (tidier data than
    #   many separate 1-frame counts), and stamps the timing into the data:
    #
    #     from smi_plans import time_series_run      # do this once per session
    #     yield from time_series_run("kinetics", n_frames=numb, period=sleep, t=t,
    #                                dets=[pil2M, pil900KW])
    #
    #   (Just a tidier option to try later — your script still works as-is, EXCEPT the lines
    #    marked ⚠️ which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: uses the retired 'pil300KW' (use 'pil900KW'), and the
    #   'det_exposure_time(...)' call must run as a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # dets = [pil300Kw]
    for i in range(numb):
        yield from bp.count(dets, num=1)
        yield from bps.sleep(sleep)


def acq_tem(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS run scanning the hexapod height (stage.y) and puts
    #   the Lakeshore temperature into the file name.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can scan along a motor and record the temperature
    #   into the data + file name for you (so it doesn't need to be read with .value and
    #   pasted into the name). For example:
    #
    #     from smi_plans import map_line_run         # do this once per session
    #     yield from map_line_run("0122A-11-lk5.5m-1s", stage.y, 5.3, 5.9, 4,
    #                             t=t, dets=[pil2M], reads=[ls])
    #
    #   (Just a tidier option — 'ls' (Lakeshore) is fine and still works. EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must run as a plan — see
    #   the ⚠️ note on that line.
    # === end smi_plans note ================================================
    sam = "0122A-11-lk5.5m-1s"

    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
    temp = ls.ch1_read.value
    name_fmt = "{sam}_{temp}C"
    sample_name = name_fmt.format(sam=sam, temp="%4.1f" % temp)
    sample_id(user_name="LC", sample_name=sample_name)
    yield from bp.scan(dets, stage.y, 5.3, 5.9, 4)


def acq_bd(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS frame at a fixed angle (a 1-point "scan" of piezo.th)
    #   and stamps the Lakeshore temperature into the file name — a quick beam/direct-beam check.
    #
    # 💡 NEWER, EASIER WAY: for a single recorded frame with the temperature captured into the
    #   data + name, 'smi_plans' offers a transmission run:
    #
    #     from smi_plans import transmission_run     # do this once per session
    #     yield from transmission_run("0122A-10-lk5.5m-0.2s-4", t=t, dets=[pil2M], reads=[ls])
    #
    #   (Just a tidier option — 'ls' (Lakeshore) is fine and still works. EXCEPT the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must run as a plan — see
    #   the ⚠️ note on that line.
    # === end smi_plans note ================================================
    sam = "0122A-10-lk5.5m-0.2s-4"

    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)
    temp = ls.ch1_read.value
    name_fmt = "{sam}_{temp}C"
    sample_name = name_fmt.format(sam=sam, temp="%4.1f" % temp)
    sample_id(user_name="LC", sample_name=sample_name)
    yield from bp.scan(dets, piezo.th, 0, 0, 1)


def run_waxs_linkamRPI_2021_3(t=1):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a single SAXS run scanning the hexapod height (stage.y) over a small
    #   range (an "Air"/background measurement).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' can do a SAXS scan along a motor in one call and build
    #   the file name from recorded data:
    #
    #     from smi_plans import map_line_run         # do this once per session
    #     yield from map_line_run("Air", stage.y, 3.2, 1.9, 6, t=t, dets=[pil2M])
    #
    #   (Just a tidier option to try later — EXCEPT the ⚠️ lines which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls must run as plans — see
    #   the ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    names = ["Air"]
    user = "JA"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

    # Detectors, motors:
    dets = [pil2M]

    name_fmt = "{sam}"
    sample_name = name_fmt.format(sam=names[0])
    sample_id(user_name=user, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    yield from bp.scan(dets, stage.y, 3.2, 1.9, 6)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).


def run_waxs_linkamRPI_2022_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: waits until set elapsed-time checkpoints (0.1, 0.5, 1, 60 min) and at
    #   each one takes SAXS+WAXS at two WAXS-arc angles — a coarse in-situ time series.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has 'smi_plans' with a time-series/kinetics
    #   runner that handles the timing for you and records the elapsed time into the data +
    #   file name (instead of formatting "{time}s" by hand):
    #
    #     from smi_plans import time_series_run      # do this once per session
    #     yield from time_series_run("testtest", n_frames=10, period=60.0, t=t,
    #                                dets=[pil2M, pil900KW])
    #     # (for the two-WAXS-angle variant, compose two runs or see technique_F_kinetics.)
    #
    #   (Just a tidier option to try later — EXCEPT the ⚠️ line which needs a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call must run as a plan — see
    #   the ⚠️ note on that line.
    # === end smi_plans note ================================================
    names = ["testtest"]
    time_rec = [0.1, 0.5, 1, 60]
    waxs_range = [20, 0]

    user = "SL"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans technique runs set it for you via t=.)

    # Detectors, motors:
    dets = [pil2M, pil900KW]

    t0 = time.time()

    for t in time_rec:
        while (time.time() - t0) < (t * 60):
            yield from bps.sleep(10)

        for wa in waxs_range:
            yield from bps.mv(waxs, wa)
            name_fmt = "{sample}_{time}s"
            sample_name = name_fmt.format(
                sample=names[0], time="%.1f" % (time.time() - t0)
            )
            sample_id(user_name=user, sample_name=sample_name)

            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

    sample_id(user_name=user, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")

    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if run as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).

def nexafs_S_edge(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sulfur-edge NEXAFS on a couple of samples — for each sample it
    #   parks the WAXS arc, steps the X-ray energy across the edge, and takes a WAXS
    #   image at each energy.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'nexafs_run' does an energy sweep in one call
    #   and records the energy + beam intensity INTO each file automatically (no
    #   hand-built "{energy}eV_bpm{xbpm}" name, no reading xbpm2 yourself):
    #
    #     from smi_plans import nexafs_run
    #     # per sample: nexafs_run("nexafs_BPI_20nm_LCE", energies, t=t,
    #     #                        dets=[pil900KW], geometry="reflection")
    #     # nexafs_run manages the beam feedback + settling for you (see the 💡 notes).
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below; the 💡 lines
    #    just become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    dets = [pil900KW]
    # prs 0 deg
    names = ["BPI_20nm_LCE", "cholesteric_film_20nm"]
    x = [-6000, -17000]
    y = [-4100, -4900]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = [40]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' nexafs_run sets exposure via t=.)
            name_fmt = "nexafs_{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:

                yield from bps.mv(energy, e)
                yield from bps.sleep(3)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)  # 💡 smi_plans: this gentle step-down to a parking energy (2470→2450) is no longer needed — energy_axis/move_energy_fb step in ≤50 eV hops with settling, so you can move straight to your target after migrating. (Not broken, just no longer needed.)
            yield from bps.mv(energy, 2450)


def S_edge_SAXSWAXS_2021_3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sulfur-edge scan recording both SAXS and WAXS — for each WAXS
    #   arc position it steps the energy and takes a SAXS+WAXS image at each, nudging the
    #   spot (piezo.x/y over a small grid) so the beam doesn't damage one place.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'nexafs_run' sweeps the energy in one call and
    #   records energy + beam INTO each file. For the SAXS+WAXS pairing use the SAXS/WAXS
    #   detector helper; for the per-energy spot move, compose energy_axis with piezo
    #   motor_axes:
    #
    #     from smi_plans import nexafs_run, saxs_waxs_dets
    #     # nexafs_run("cholesteric_film_20nm", energies, t=t, dets=saxs_waxs_dets(),
    #     #            geometry="reflection")  — handles the energy sweep + recording.
    #     # nexafs_run manages the beam feedback + settling (see the 💡 notes).
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below; the 💡 lines
    #    become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    dets = [pil900KW, pil2M]

    names = ["cholesteric_film_20nm"]  #'BPI_20nm_LCE']#
    x = [-15900]  # , -5900]
    y = [-5000]  # , -5600]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 200, 20)
        xss = np.array([xs, xs + 200, xs + 400])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' nexafs_run sets exposure via t=.)

            name_fmt = "{sample}_sdd5m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)  # 💡 smi_plans: this gentle step-down to a parking energy (2470→2450) is no longer needed — energy_axis/move_energy_fb step in ≤50 eV hops with settling, so you can move straight to your target after migrating. (Not broken, just no longer needed.)
            yield from bps.mv(energy, 2450)


def saxs_S_edge_Hoang_2022_2(t=0.5):
    """
    Cycle 2022_2
    Based on Gregory and modified for GU-310422. SAXS ssd 8.3 m.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sulfur-edge SAXS scan over a bar of samples — for each sample,
    #   at two WAXS arc positions, it steps the energy and takes a SAXS (and WAXS when
    #   the arc is out of the way) image at each, sliding the spot in y to avoid damage.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' 'nexafs_run' / 'nexafs_bar' sweep the energy and
    #   record energy, beam, SDD, etc. INTO each file from the recorded values, so you
    #   don't read xbpm3 / pil2M_pos.z and hand-build the long name:
    #
    #     from smi_plans import nexafs_bar, saxs_waxs_dets
    #     # nexafs_bar takes your sample names + positions and sweeps energy at each,
    #     # choosing SAXS/WAXS for you; see nexafs_run for a single sample.
    #     # It manages the beam feedback + settling (see the 💡 notes).
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ line below; the 💡 lines
    #    become unnecessary after migrating. Note: pil2M_pos.z, xbpm3, sample_id are fine.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ note on that line.
    # === end smi_plans note ================================================
    user_name = "JH"

    # x and y are positions on the sample, a and b are different rows
    names_a = [
        "0.7_20OBA",
        "0.6_20OBA",
        "40OBA_main",
        "30OBA_main",
        "20OBA_main",
        "10OBA_main",
        "0OBA_main",
    ]
    x_a = [
        39000,
        29000,
        19000,
        5000,
        -7000,
        -22000,
        -37000,
    ]
    y_a = [
        -6800,
        -6800,
        -6800,
        -6500,
        -6500,
        -6500,
        -6500,
    ]

    names_b = [
        "BPIII",
        "BPII",
        "BPI",
        "BP_Chol",
        "0.9_20OBA",
        "0.8_20OBA",
    ]
    x_b = [
        30750,
        16000,
        1000,
        -10700,
        -21700,
        -37500,
    ]
    y_b = [
        6700,
        6700,
        6700,
        6700,
        6700,
        6200,
    ]

    # Combine sample lists
    names = names_a + names_b
    x = x_a + x_b
    y = y_a + y_b

    # Check and correct sample names just in case
    names = [n.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "}) for n in names]

    assert len(x) == len(
        names
    ), f"Number of x coordinates ({len(x)}) is different from number of samples ({len(names)})"
    assert len(x) == len(
        y
    ), f"Number of x coordinates ({len(x)}) is different number of y coordinates ({len(y)})"
    assert len(y) == len(
        names
    ), f"Number of y coordinates ({len(y)}) is different from number of samples ({len(names)})"

    # Move all x and y values if needed
    # x = (np.array(x) + 0).tolist()
    # y = (np.array(y) + 0).tolist()

    # Energies for sulphur K edge
    energies = np.concatenate(
        (
            np.arange(2445, 2470, 5),
            np.arange(2470, 2480, 0.25),
            np.arange(2480, 2490, 1),
            np.arange(2490, 2501, 5),
        )
    )

    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs, piezo.y, ys)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            yield from bps.mv(piezo.x, xs + i * 200)
            # Do not read SAXS if WAXS is in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' nexafs_run sets exposure via t=.)

            # Cover a range of 1.5 mm in y to avoid damage
            yss = np.linspace(ys, ys + 1500, len(energies))

            name_fmt = "{sample}_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}"
            for e, ysss in zip(energies, yss):
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                # Metadata
                bpm = xbpm3.sumX.get()
                sdd = pil2M_pos.z.position / 1000
                # wa = waxs.arc.user_readback.value
                wa = str(np.round(wa, 1)).zfill(4)

                sample_name = name_fmt.format(
                    sample=name,
                    energy="%6.2f" % e,
                    wax=wa,
                    sdd="%.1f" % sdd,
                    xbpm="%4.3f" % bpm,
                )
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            # Go back gently with energy
            yield from bps.mv(energy, 2480)  # 💡 smi_plans: this gentle step-down to a parking energy (2480→2450) is no longer needed — energy_axis/move_energy_fb step in ≤50 eV hops with settling, so you can move straight to your target after migrating. (Not broken, just no longer needed.)
            yield from bps.mv(energy, 2450)


def saxs_S_edge_temperature_Hoang_2022_2(t=0.5):
    """
    Cycle 2022_2: heating stage temperature cycle SAXS ssd 8.3 m.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature cycle crossed with a sulfur-edge scan — for each
    #   temperature (heater driven, then equilibrated) it loops over a bar of samples,
    #   two WAXS arc positions, and a few energies, taking a SAXS/WAXS image at each.
    #
    # 💡 NEWER, EASIER WAY: smi_plans can pair a temperature series with an energy sweep
    #   and record temperature + energy + beam INTO every file. The building blocks are
    #   the temperature preset (or 'temperature_axis' / 'goto_temperature') plus
    #   'energy_axis'; there is also a ready-made combined recipe in
    #   smi_plans.recipes_combined ('giwaxs_tempramp_energy_5loc'):
    #
    #     from smi_plans import temperature_axis, energy_axis
    #     # build a temperature axis + energy axis and hand both to acquire(...),
    #     # OR use smi_plans.recipes_combined.giwaxs_tempramp_energy_5loc as a preset.
    #     # energy_axis manages the beam feedback + settling (see the 💡 notes).
    #     # (Lakeshore 'ls', pil2M_pos.z, xbpm3 are all fine — not flagged.)
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡 lines
    #    become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================
    user_name = "JH"

    # x and y are positions on the sample, a and b are different rows
    names_a = [
        "0_6OBA_main",
        "10_6OBA_main",
        "20_6OBA_main",
        "30_6OBA_main",
        "40_6OBA_main",
        "0.6_20OBA",
        "0.7_20OBA",
    ]
    x_a = [
        45000,
        39500,
        36500,
        31750,
        26750,
        22250,
        18650,
    ]
    y_a = [
        -5000,
        -5100,
        -5500,
        -5000,
        -4500,
        -5000,
        -5000,
    ]

    names_b = [
        "0.8_20OBA",
        "0.8_20OBA_R",
        "0.9_20OBA",
        "BP_chol",
        "BPI",
        "BPII",
        "BPIII",
    ]
    x_b = [
        13500,
        9750,
        5000,
        -750,
        -5750,
        -11750,
        -17750,
    ]
    y_b = [
        -5000,
        -4000,
        -5200,
        -5200,
        -5200,
        -5200,
        -5200,
    ]

    # Combine sample lists
    names = names_a + names_b
    x = x_a + x_b
    y = y_a + y_b

    # Check and correct sample names just in case
    names = [n.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "}) for n in names]

    assert len(x) == len(
        names
    ), f"Number of x coordinates ({len(x)}) is different from number of samples ({len(names)})"
    assert len(x) == len(
        y
    ), f"Number of x coordinates ({len(x)}) is different number of y coordinates ({len(y)})"
    assert len(y) == len(
        names
    ), f"Number of y coordinates ({len(y)}) is different from number of samples ({len(names)})"

    # Move all x and y values if needed
    # x = (np.array(x) + 0).tolist()
    # y = (np.array(y) + 0).tolist()

    # Energies for sulphur K edge
    # energies = np.concatenate((np.arange(2445, 2470, 5),
    #                            np.arange(2470, 2480, 0.25),
    #                            np.arange(2480, 2490, 1),
    #                            np.arange(2490, 2501, 5),
    #                            ))
    energies = [2452, 2472, 2476, 2478, 2482, 2500]
    temperatures = np.arange(30, 201, 5)  # in C

    waxs_arc = [0, 2]

    for i_t, temperature in enumerate(temperatures):

        t_kelvin = temperature + 273.15
        print(t_kelvin)
        yield from ls.output1.mv_temp(t_kelvin)

        print("Equalising temp")
        temp = ls.input_A.get()
        while abs(temp - t_kelvin) > 1:
            print(abs(temp - t_kelvin))
            yield from bps.sleep(10)
            temp = ls.input_A.get()

        t_celsius = temp - 273.15
        if t_celsius > 34:
            print("Waiting for 300 s...")
            yield from bps.sleep(300)

        for name, xs, ys in zip(names, x, y):
            yield from bps.mv(piezo.x, xs, piezo.y, ys)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # yield from bps.mv(piezo.x, xs + i * 200)
                # Do not read SAXS if WAXS is in the way
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]
                det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' temperature/energy presets set exposure via t=.)

                # Cover a range of 1.5 mm in y to avoid damage
                yss = np.linspace(ys, ys + 180, len(energies))

                name_fmt = "{sample}_temp{temperature}degC_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}"
                for e, ysss in zip(energies, yss):
                    yield from bps.mv(piezo.y, ysss)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                    # Metadata
                    bpm = xbpm3.sumX.get()
                    sdd = pil2M_pos.z.position / 1000
                    wa = str(np.round(float(wa), 1)).zfill(4)

                    sample_name = name_fmt.format(
                        sample=name,
                        temperature="%3.1f" % temperature,
                        energy="%6.2f" % e,
                        wax=wa,
                        sdd="%.1f" % sdd,
                        xbpm="%4.3f" % bpm,
                    )
                    sample_id(user_name=user_name, sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")

                    yield from bp.count(dets, num=1)

                # Go back gently with energy
                yield from bps.mv(energy, 2480)  # 💡 smi_plans: this gentle step-down to a parking energy (2480→2450) is no longer needed — energy_axis/move_energy_fb step in ≤50 eV hops with settling, so you can move straight to your target after migrating. (Not broken, just no longer needed.)
                yield from bps.mv(energy, 2450)

    # End of the scan
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.5, 0.5)  inside a plan, or  RE(det_exposure_time(0.5, 0.5))  at the prompt.
    yield from ls.output1.mv_temp(28 + 273.13)


def tensile_continous_Hoang_2022_2(t=0.5):
    """
    Cycle 2022_2: Tensile stage continous measurements

    Set the energy prior to the measurement
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a continuous (time-series) measurement during a tensile pull —
    #   sets the energy once, then loops "forever" (1000 times), sweeping the WAXS arc
    #   and saving an image at each angle, stamping the elapsed time into each name.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has time-series / kinetics presets that take
    #   repeated frames on a clock and record the elapsed time + energy + beam INTO each
    #   file for you (no time.time() bookkeeping or hand-built "{td}s" name):
    #
    #     from smi_plans import time_series_run, time_axis
    #     # time_series_run(name, dets, ...) takes frames over time; time_axis builds the
    #     # time points. (kinetics_run is the same idea for in-situ kinetics.)
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below. Note: setting
    #    the energy once up top is fine; pil2M_pos.z, xbpm3, sample_id are fine.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' is now a plan — see the
    #   ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    user_name = "test_30deg"

    # Sample name
    name = "test_30deg"

    ene = 2470
    yield from bps.mv(energy, ene)

    t0 = time.time()
    waxs_arc = [0, 2, 16]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' time_series/kinetics presets set exposure via t=.)

    # Check and correct sample names just in case
    name = name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "})

    # Continous measurement
    for i in range(1000):

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            # Do not read SAXS if WAXS is in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]
            t1 = time.time()

            # Metadata
            step = str(i).zfill(3)
            td = str(np.round(t1 - t0, 1)).zfill(6)
            e = energy.position.energy
            wa = str(np.round(float(wa), 1)).zfill(4)
            sdd = pil2M_pos.z.position / 1000
            bpm = xbpm3.sumX.get()

            # Sample name
            name_fmt = (
                "{sample}_step{step}_time{td}s_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}"
            )
            sample_name = name_fmt.format(
                sample=name,
                step=step,
                td=td,
                energy="%6.2f" % e,
                wax=wa,
                sdd="%.1f" % sdd,
                xbpm="%4.3f" % bpm,
            )
            sample_id(user_name=user_name, sample_name=sample_name)

            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets)

    # End of the scan
    sample_id(user_name="test_30deg", sample_name="test_30deg")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.5, 0.5)  inside a plan, or  RE(det_exposure_time(0.5, 0.5))  at the prompt.


def tensile_single_Hoang_2022_2(t0, t=0.5):
    """
    Cycle 2022_2: Tensile stage single measurement

    Scan WAXS over different energies and sample rotations. Make sure to specify
    hexapod stage positions for each sample rotation. Also, make t0 in BlueSky by
    t0 = time.time() at the same time the plan in Linkam software is executed.
    Then start the scan by RE(tensile_single_Hoang_2022_2(t0)). Each file name
    will contain time eplased from t0, so detctor frames can be related to the
    Linkam tensile stage plan.

    Params:
        t0 (float): start time of the tensile plan, from time.time()
        t (float): exposure of the single detector frame and also total acquisition
            time.

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: during a tensile pull, for each sample ROTATION it moves the
    #   rotation + hexapod stage there, then at two WAXS arc positions steps a couple of
    #   energies and saves an image, stamping the time-since-t0 into each file name.
    #
    # 💡 NEWER, EASIER WAY: smi_plans records elapsed time + energy + the rotation INTO
    #   each file for you. Build the rotation as a recorded axis and pair it with energy
    #   + time, e.g. with kinetics_run plus axis builders:
    #
    #     from smi_plans import kinetics_run, motor_axis, energy_axis
    #     rot_axis = motor_axis("phi", stage.phi, [0, 15, 30])   # the rotation, recorded
    #     # energy_axis([2470, 2478]) gives the energy steps (it handles beam feedback),
    #     # and kinetics_run captures frames vs time. (stage.x/y/z and Linkam 'ls' are fine.)
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below; the 💡 lines
    #    become unnecessary after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses 'prs' (the old rotation stage, now
    #   'stage.phi') and 'det_exposure_time(...)' is now a plan — see the ⚠️ notes on
    #   those lines.
    # === end smi_plans note ================================================

    user_name = "JH"

    # Sample name
    name = "BPIII_80strain"

    rotations = [0, 15, 30]
    # rotations = [0]

    # Hexapod sample coordinates for different rotations
    hexa_poistions = {
        0: dict(hexa_x=0.3, hexa_y=0.4, hexa_z=7),
        15: dict(hexa_x=2.25, hexa_y=0.3, hexa_z=7),
        30: dict(hexa_x=4.15, hexa_y=0.5, hexa_z=7),
        # 40 : dict(hexa_x=0, hexa_y=0, hexa_z=7),
    }

    energies = [2470, 2478]
    waxs_arc = [0, 2]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' kinetics presets set exposure via t=.)

    # Check and correct sample names just in case
    name = name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "})

    for rot in rotations:

        # Get hexa position from the position dictionary
        x = hexa_poistions[rot]["hexa_x"]
        y = hexa_poistions[rot]["hexa_y"]
        z = hexa_poistions[rot]["hexa_z"]

        yield from bps.mv(prs, rot, stage.x, x, stage.y, y, stage.z, z)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'. (stage.x/y/z in this line are fine.)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            # Do not read SAXS if WAXS is in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yss = np.linspace(y, y + 0.09, len(energies))  # in mm now

            for e, ysss in zip(energies, yss):
                yield from bps.mv(energy, e)
                yield from bps.mv(stage.y, ysss)
                yield from bps.sleep(2)  # 💡 smi_plans: you can drop this settle wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)

                t1 = time.time()

                # Metadata
                rot = str(rot).zfill(2)
                td = str(np.round(t1 - t0, 1)).zfill(6)
                # e = energy.position.energy
                wa = str(np.round(float(wa), 1)).zfill(4)
                sdd = pil2M_pos.z.position / 1000
                bpm = xbpm3.sumX.get()

                # Sample name
                name_fmt = (
                    "{sample}_rot{rot}deg_{td}s_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}"
                )
                sample_name = name_fmt.format(
                    sample=name,
                    rot=rot,
                    td=td,
                    energy="%6.2f" % e,
                    wax=wa,
                    sdd="%.1f" % sdd,
                    xbpm="%4.3f" % bpm,
                )
                sample_id(user_name=user_name, sample_name=sample_name)

                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets)

            yield from bps.mv(energy, 2475)
            yield from bps.sleep(2)  # 💡 smi_plans: this settle wait after the energy move is no longer needed — move_energy_fb/energy_axis handle the wait + beam feedback for you once you migrate. (Not broken, just no longer needed.)

            # Move energy slowly
            if e == 2500:
                yield from bps.mv(energy, 2490)  # 💡 smi_plans: this gentle step-down (2490→2480→2470) is no longer needed — energy_axis/move_energy_fb step in ≤50 eV hops with settling, so you can move straight to your target after migrating. (Not broken, just no longer needed.)
                yield from bps.mv(energy, 2480)
                yield from bps.mv(energy, 2470)

    # End of the scan
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.5, 0.5)  inside a plan, or  RE(det_exposure_time(0.5, 0.5))  at the prompt.

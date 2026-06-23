def giwaxs_Fernandez(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GIWAXS) scan over a bar of ~13 samples. For each WAXS
    #   detector-arc angle it visits every sample (moving stage/piezo to its saved spot + aligned
    #   incidence angle), then sweeps the incident angle through 15 values, snapping a SAXS+WAXS
    #   image at each. ("Grazing incidence" = the beam skims the surface at a shallow angle.)
    #
    # 💡 NEWER, EASIER WAY: this is the bread-and-butter "GIWAXS bar" workflow in 'smi_plans'. You
    #   list the samples (and their positions/angles) once and it visits each, sweeps the incidence
    #   angle and WAXS arc, and writes angle/position/beam INTO every image — so you don't hand-build
    #   the "{sample}_..._ai{angle}deg_wa{waxs}" name:
    #
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo_aligned, z=z_piezo)
    #     yield from giwaxs_bar(samples, t=t,
    #                           incident_angles=np.linspace(0.04, 0.18, 15),
    #                           waxs_arc=np.linspace(0, 19.5, 4))
    #     # (giwaxs_bar_arc_economy reorders the loops to spend less time moving the WAXS arc.)
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan. See the
    #   ⚠️ notes on those lines below. (internal: Tier 1.)
    # === end smi_plans note ================================================
    # sample alignement
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, xs_hexa
    # names =  ['BKGD',  'A1',  'A2', 'A3',   'A4',   'A5',
    #             'A6',  'A7',  'A8', 'A9',  'A10',  'A11',  'A12']
    # x_piezo = [58000, 41000, 21000, 1000, -17000, -37000,
    #            58000, 41000, 21000, 1000, -17000, -37000, -55500]
    # y_piezo = [ 6900,  6900,  6900, 6900,   6900,   6900,
    #            -2200, -2200, -2200,-2200,  -2200,  -2200,  -2200]
    # z_piezo = [    0,     0,     0,    0,      0,       0,
    #             5000,  5000,  5000, 5000,   5000,    5000,   5000]
    # x_hexa =  [    6,      0,    0,    0,      0,       0,
    #                6,      0,    0,    0,      0,       0,     -4]

    # names =  ['A13',  'A14',  'A15', 'A16',   'A17',   'A18',
    #             'A19',  'A20',  'A21', 'A22',  'A23',  'A24',  'A25']
    # x_piezo = [58000, 41000, 21000, 1000, -19000, -39000,
    #            58000, 41000, 21000, 1000, -19000, -39000, -55500]
    # y_piezo = [ 6900,  6900,  6900, 6900,   6900,   6900,
    #            -2200, -2200, -2200,-2200,  -2200,  -2200,  -2200]
    # z_piezo = [    0,     0,     0,    0,      0,       0,
    #             5000,  5000,  5000, 5000,   5000,    5000,   5000]
    # x_hexa =  [    6,      0,    0,    0,      0,       0,
    #                6,      0,    0,    0,      0,       0,     -4]

    names = [
        "A26",
        "A27",
        "A28",
        "A29",
        "A30",
        "BKGD",
        "A01",
        "A02",
        "A03",
        "A04",
        "A05",
        "A06",
        "A07",
    ]
    x_piezo = [
        55000,
        40000,
        17000,
        -2000,
        -25000,
        -47500,
        55000,
        40000,
        17000,
        -2000,
        -25000,
        -42500,
        -57000,
    ]
    y_piezo = [
        6900,
        6900,
        6900,
        6900,
        6900,
        6900,
        -2200,
        -2200,
        -2200,
        -2200,
        -2200,
        -2200,
        -2200,
    ]
    z_piezo = [0, 0, 0, 0, 0, 0, 5000, 5000, 5000, 5000, 5000, 5000, 5000]
    x_hexa = [6, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, -5]

    # incident_angles = [-0.428311, -0.587565, -0.492445, 0.009011, -0.356074, -0.446316, -0.932245, -0.908126, -0.944155, -1.175827, -1.140861, -1.015834, -0.925797]
    # y_piezo_aligned = [ 6493.112,  6492.969,  6482.293, 6473.455,   6459.49,  6445.813, -2312.519, -2349.623, -2362.358, -2396.463,   -2397.1, -2431.483, -2387.921]
    incident_angles = [
        -0.321218,
        -0.45491,
        -0.440744,
        -0.17595,
        -0.394264,
        -0.443751,
        -1.407557,
        -0.820769,
        -1.09834,
        -1.617552,
        -1.093352,
        -0.984098,
        -0.959991,
    ]
    y_piezo_aligned = [
        6489.362,
        6512.907,
        6528.814,
        6534.525,
        6481.937,
        6480.819,
        -2341.031,
        -2307.083,
        -2356.385,
        -2465.571,
        -2386.802,
        -2381.393,
        -2357.137,
    ]

    # smi = SMI_Beamline()
    # yield from smi.modeAlignment(technique='gisaxs')

    # for name, xs_piezo, zs_piezo, ys_piezo, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
    #     yield from bps.mv(stage.x, xs_hexa)
    #     yield from bps.mv(piezo.x, xs_piezo)
    #     yield from bps.mv(piezo.y, ys_piezo)
    #     yield from bps.mv(piezo.z, zs_piezo)

    #     if ys_piezo>0:
    #         yield from bps.mv(piezo.th, 0)
    #         yield from alignement_gisaxs_multisample(angle = 0.08)
    #     else:
    #         yield from bps.mv(piezo.th, -1)
    #         yield from alignement_gisaxs_multisample_special(angle = 0.08)

    #     incident_angles = incident_angles + [piezo.th.position]
    #     y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

    # yield from smi.modeMeasurement()

    print(incident_angles)
    print(y_piezo_aligned)

    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = np.linspace(0, 19.5, 4)
    angle = np.linspace(0.04, 0.18, 15)

    for wa in waxs_arc[::-1]:
        yield from bps.mv(waxs, wa)

        for name, xs, zs, aiss, ys, xs_hexa in zip(
            names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa
        ):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.th, aiss)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            name_fmt = "{sample}_sdd5m_12keV_ai{angle}deg_wa{waxs}"

            for num, an in enumerate(angle):
                yield from bps.mv(piezo.th, aiss + an)
                # yield from bps.mv(piezo.x, xs - num * 100)

                sample_name = name_fmt.format(
                    sample=name, angle="%3.2f" % an, waxs="%2.1f" % wa
                )
                sample_id(user_name="LF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

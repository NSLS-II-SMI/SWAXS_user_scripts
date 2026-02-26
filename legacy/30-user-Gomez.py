def ex_situ_hardxray(t=1):
    # samples = ['PLA2','PLA1','CON6','CON5', 'CON4','CON3','CON2','CON1',
    # '05_Ca_1', '05_Ca_2', '05_UT_1', '05_UT_2', 'PLA6','PLA4','PLA3',
    # ]

    # samples = ['B5_1','B5_2','B5_3', 'B6_1','B6_2','B6_3','B7_1','B7_2','B7_3','B12_1','B12_2','B12_3']
    # x_list  = [45550, 41200, 35600, 25600, 20900, 15400, -1900, -7900, -14000, -24100, -28200, -32700, ]
    # y_list =  [-9300, -9300, -9300, -9300, -9300, -9300, -9300, -9300, -9300, -9300, -9300, -9300]

    # samples = ['A1_1','A1_2','A1_3', 'A1_4','A2_5','A2_6','A2_7','A2_8','A3_9','A3_10','A3_11','A3_12','A3_13','A3_14','A4_15', 'A4_16', 'A4_17', 'A4_19']
    # x_list  = [45950, 43250, 37250, 31650, 24400, 18850, 12500, 8000, -3400, -7300, -11300, -16800, -20900, -26400, -33000,  -37400, -41900, -45200]
    # y_list =  [3500,  3500,  3500,  3500,  3500,  3500,  3500,  3500,  3500,  3500,  3500,  3500,   3500,   3500,    3500, 3500, 3500, 3500]

    # samples = ['C8_32', 'C8_33', 'C8_34', 'C8_35', 'C9_36', 'C9_37', 'C9_38', 'C9_39', 'C10_40', 'C10_41', 'C10_42', 'C10_43',
    # 'C10_44', 'C10_45', 'C11_46', 'C11_47', 'C11_48', 'C11_49', 'C11_50']
    # x_list  = [43700, 38300, 34000, 27800, 20900, 16200, 12100, 7100, -2700, -6700, -10500, -15700, -20000,
    # -24200, -29300, -32700, -36700, -41000, -45000]
    # y_list =  [3700,  3700,  3700,  3700,  3700,  3700,  3700,  3700, 3700,  3700,  3700,   3700,   3700,
    # 3700,   3700,    3700,   3700,  3700,  3700]

    samples = [
        "D13_51",
        "D13_52",
        "D13_53",
        "D14_54",
        "D14_55",
        "D14_56",
        "D15_57",
        "D15_58",
        "D15_59",
        "D16_60",
        "D16_61",
        "D16_62",
        "D16_63",
        "D16_64",
        "D17_65",
        "D17_66",
        "D17_67",
    ]
    x_list = [
        43700,
        38400,
        34000,
        25200,
        20000,
        15400,
        6700,
        2500,
        -2300,
        -6800,
        -14000,
        -19000,
        -23300,
        -28500,
        -34700,
        -39300,
        -43600,
    ]
    y_list = [
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
        -9880,
    ]

    # Detectors, motors:
    dets = [pil2M, pil300KW]
    waxs_range = np.linspace(13, 0, 3)

    ypos = [0, 400, 3]
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of Y coord ({len(y_list)})"

    det_exposure_time(t, t)

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        for sam, x, y in zip(samples, x_list, y_list):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)

            name_fmt = "{sam}_wa{waxs}"
            sample_name = name_fmt.format(sam=sam, waxs="%2.1f" % wa)
            sample_id(user_name="OS", sample_name=sample_name)
            yield from bp.rel_scan(dets, piezo.y, *ypos)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def NEXAFS_Fe_edge(t=0.5, name="sample1"):
    dets = [pil300KW]
    # name = 'Kapton_NEXAFS_1_gvopen_wa70_'
    # x = [8800]

    energies = np.linspace(7100, 7150, 51)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 7100)
    # name_fmt = '{sample}_2430eV_postmeas_xbpm{xbpm}'
    # sample_name = name_fmt.format(sample=name, xbpm = '%3.1f'%xbpm3.sumY.value)
    # sample_id(user_name='GF', sample_name=sample_name)
    # print(f'\n\t=== Sample: {sample_name} ===\n')
    # yield from bp.count(dets, num=1)


def SAXS_Fe_edge(t=0.5):
    dets = [pil2M]
    names = [
        "Ca10_2_SAXS_sdd5_1s_redo_",
        "Ca2_2_SAXS_sdd5_1s_redo_",
        "Ca2_4_SAXS_sdd5_1s_redo_",
        "PBS_2_SAXS_sdd5_1s_redo_",
    ]
    names1 = [
        "Ca10_2_NEXAFS_wa0_redo_",
        "Ca2_2_NEXAFS_wa0_redo_",
        "Ca2_4_NEXAFS_wa0_redo_",
        "PBS_2_NEXAFS_wa0_redo_",
    ]

    xs = [-36600, -10600, 15400, 41100]
    ys = [-1050, -1050, -1050, -1050]
    energies = [7100, 7110, 7114, 7115, 7118, 7120, 7125, 7140]

    for i, (name, name1, x, y) in enumerate(zip(names, names1, xs, ys)):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        yield from NEXAFS_Fe_edge(t=1, name=name1)
        dets = [pil2M]

        det_exposure_time(t, t)
        xsss = [x + 400, x + 900, x + 1200]
        for j, xss in enumerate(xsss):
            yield from bps.mv(piezo.x, xss)
            for e in energies:
                name_fmt = "{sample}_pos{pos}_{energy}eV_xbpm{xbpm}"

                yield from bps.mv(energy, e)
                sample_name = name_fmt.format(
                    sample=name,
                    pos="%2.2d" % j,
                    energy=e,
                    xbpm="%3.1f" % xbpm3.sumY.value,
                )
                sample_id(user_name="SR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 7100)
            name_fmt = "{sample}_pos{pos}_7100eV_postmeas_xbpm{xbpm}"
            sample_name = name_fmt.format(
                sample=name, pos="%2.2d" % j, xbpm="%3.1f" % xbpm3.sumY.value
            )
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def NEXAFS_Ag_edge(t=0.5):
    dets = [pil300KW]
    name = "N2_redo_GINEXAFS_wa75_"
    # x = [8800]

    energies = np.linspace(3340, 3390, 51)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.sleep(2)

    yield from bps.mv(energy, 3340)
    yield from bps.sleep(10)


def GISAXS_Ca_edge(t=0.5):
    dets = [pil300KW]
    names = [
        "O_9_gisaxs",
        "O_8_gisaxs",
        "O_7_gisaxs",
        "O_6_gisaxs",
        "O_5_gisaxs",
        "O_4_gisaxs",
        "O_3_gisaxs",
        "O_2_gisaxs",
        "O_1_gisaxs",
        "Si_last_gisaxs",
    ]
    xs = [-50000, -38500, -22500, -11500, 500, 15000, 27000, 41000, 50000, 31400]
    zs = [700, 0, -800, 400, 1900, -2000, -1000, 300, -600, -800]

    energies = [4030, 4050, 4055, 4075]
    det_exposure_time(t, t)

    name_fmt = "{sample}_{energy}eV_ai{ai}_xbpm{xbpm}_wa{wa}"
    angles = [0.38, 0.4]
    wax = [0, 6.5, 13]

    th_0 = piezo.th.position
    for x, z, name in zip(xs, zs, names):
        yield from bps.mv(piezo.th, th_0)

        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.z, z)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from alignement_gisaxs(0.3)
        yield from bps.mv(att2_11, "Insert")

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(att2_11, "Insert")

        yield from bps.mv(GV7.close_cmd, 1)

        th_0 = piezo.th.position
        for wa in wax:
            yield from bps.mv(waxs, wa)
            for k, e in enumerate(energies):
                yield from bps.mv(energy, e)
                for alpha_i in angles:
                    yield from bps.mv(piezo.th, th_0 + alpha_i)
                    sample_name = name_fmt.format(
                        sample=name,
                        energy=e,
                        ai="%3.2f" % alpha_i,
                        xbpm="%3.1f" % xbpm3.sumY.value,
                        wa="%2.1f" % wa,
                    )
                    sample_id(user_name="SR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 4050)
            yield from bps.mv(energy, 4030)


def SAXS_Ca_edge_hyd(t=0.5):
    dets = [pil2M]
    name = "hyd_cell_blank"

    energies = [4030, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_sp{sp}"
    x_pos = piezo.x.position
    y_pos = piezo.y.position

    for k, e in enumerate(energies):
        yield from bps.mv(energy, e)
        yield from bps.mv(piezo.x, x_pos + k * 500)

        for i in range(0, 5, 1):
            yield from bps.mv(piezo.y, y_pos + i * 200)

            sample_name = name_fmt.format(
                sample=name, energy=e, sp="%2.2d" % i, xbpm="%3.1f" % xbpm3.sumY.value
            )
            sample_id(user_name="JDM", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.y, y_pos)

    yield from bps.mv(energy, 4050)
    yield from bps.mv(energy, 4030)


def SAXS_Ca_edge_hyd_onespot(t=0.5):
    dets = [pil2M]
    name = "hyd_cell_blank_onespot2"

    energies = [4030, 4040, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_sp{sp}"
    y_pos = piezo.y.position

    for k, e in enumerate(energies):
        yield from bps.mv(energy, e)

        for i in range(0, 5, 1):
            yield from bps.mv(piezo.y, y_pos + i * 200)

            sample_name = name_fmt.format(
                sample=name, energy=e, sp="%2.2d" % i, xbpm="%3.1f" % xbpm3.sumY.value
            )
            sample_id(user_name="JDM", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.y, y_pos)

    yield from bps.mv(energy, 4050)
    yield from bps.mv(energy, 4030)


def SAXS_Ca_edge_dry1(t=1):
    dets = [pil300KW, pil2M]
    name = "hyd_cell_blank2"

    energies = [4030, 4040, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_wa{wa}"
    wa = [0.0, 6.5, 13.0]

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(1)
    yield from bps.mv(GV7.close_cmd, 1)

    for wax in wa:
        yield from bps.mv(waxs, wax)
        for k, e in enumerate(energies):
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(
                sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
            )
            sample_id(user_name="JDM", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 4050)
        yield from bps.mv(energy, 4030)

    for wax in wa[::-1]:
        yield from bps.mv(waxs, wax)

        name_fmt = "{sample}_4030eV_postmeas_xbpm{xbpm}_wa{wa}"
        sample_name = name_fmt.format(
            sample=name, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
        )
        sample_id(user_name="OS", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def SAXS_Ca_edge_dry_special1(t=1):
    dets = [pil300KW]
    names = ["O5_chl_4"]
    x_s = [-44500]
    y_s = [-1200]

    energies = [4030, 4040, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_pos{posi}_wa{wa}_xbpm{xbpm}"
    wa = [0.0, 6.5, 13.0]

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(1)
    yield from bps.mv(GV7.close_cmd, 1)

    for x, y, name in zip(x_s, y_s, names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        ys = np.linspace(y, y + 250, 5)
        xs = np.linspace(x, x - 400, 3)

        yss, xss = np.meshgrid(ys, xs)
        yss = yss.ravel()
        xss = xss.ravel()

        for pos, (xsss, ysss) in enumerate(zip(xss, yss)):
            yield from bps.mv(piezo.x, xsss)
            yield from bps.mv(piezo.y, ysss)
            name_new = name + "pos%2.2d" % pos
            yield from NEXAFS_Ca_edge_special(t=0.5, name=name_new)

        for wax in wa:
            yield from bps.mv(waxs, wax)

            for k, e in enumerate(energies):
                yield from bps.mv(energy, e)

                for pos, (xsss, ysss) in enumerate(zip(xss, yss)):
                    yield from bps.mv(piezo.x, xsss)
                    yield from bps.mv(piezo.y, ysss)

                    sample_name = name_fmt.format(
                        sample=name,
                        energy=e,
                        posi="%2.2d" % pos,
                        wa="%2.1f" % wax,
                        xbpm="%3.1f" % xbpm3.sumY.value,
                    )
                    sample_id(user_name="JDM", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 4050)
                yield from bps.mv(energy, 4030)

        for wax in wa[::-1]:
            yield from bps.mv(waxs, wax)

            for pos, (xsss, ysss) in enumerate(zip(xss, yss)):
                yield from bps.mv(piezo.x, xsss)
                yield from bps.mv(piezo.y, ysss)

                name_fmt = "{sample}_postmeas_4030eV_pos{posi}_wa{wa}_xbpm{xbpm}"
                sample_name = name_fmt.format(
                    sample=name,
                    posi="%2.2d" % pos,
                    wa="%2.1f" % wax,
                    xbpm="%3.1f" % xbpm3.sumY.value,
                )
                sample_id(user_name="JDM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def SAXS_Ca_edge_dry_special2(t=1):
    dets = [pil300KW, pil2M]
    names = [
        "O5_ut_2",
        "O5_ut_3",
        "O5_ut_4",
        "O5_ca_1",
        "O5_ca_2",
        "O5_ca_3",
        "O5_chl_1",
        "O5_chl_2",
        "O5_chl_3",
    ]
    x_s = [31500, 25000, 18000, 5400, 100, -5400, -22600, -30600, -38600]
    y_s = [-2200, -1400, -2000, -2000, -2000, -2000, -800, -2000, -2000]

    energies = [4030, 4040, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_pos{posi}_wa{wa}_xbpm{xbpm}"
    wa = [0.0, 6.5, 13.0]

    yield from bps.mv(GV7.open_cmd, 1)
    yield from bps.sleep(1)
    yield from bps.mv(GV7.open_cmd, 1)

    for x, y, name in zip(x_s, y_s, names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        ys = np.linspace(y, y + 500, 2)
        xs = np.linspace(x, x - 500, 2)

        yss, xss = np.meshgrid(ys, xs)
        yss = yss.ravel()
        xss = xss.ravel()
        yield from NEXAFS_Ca_edge_special(t=0.5, name=name)

        for wax in wa:

            yield from bps.mv(waxs, wax)

            for k, e in enumerate(energies):
                yield from bps.mv(energy, e)

                for pos, (xsss, ysss) in enumerate(zip(xss, yss)):
                    yield from bps.mv(piezo.x, xsss)
                    yield from bps.mv(piezo.y, ysss)

                    sample_name = name_fmt.format(
                        sample=name,
                        energy=e,
                        posi="%1.1d" % pos,
                        wa="%2.1f" % wax,
                        xbpm="%3.1f" % xbpm3.sumY.value,
                    )
                    sample_id(user_name="JDM", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 4050)
                yield from bps.mv(energy, 4030)

        wa = [0.0, 6.5, 13.0]
        for wax in wa[::-1]:
            yield from bps.mv(waxs, wax)

            for pos, (xsss, ysss) in enumerate(zip(xss, yss)):
                yield from bps.mv(piezo.x, xsss)
                yield from bps.mv(piezo.y, ysss)

                name_fmt = "{sample}_postmeas_4030eV_pos{posi}_wa{wa}_xbpm{xbpm}"
                sample_name = name_fmt.format(
                    sample=name,
                    posi="%2.2d" % pos,
                    wa="%2.1f" % wax,
                    xbpm="%3.1f" % xbpm3.sumY.value,
                )
                sample_id(user_name="JDM", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def NEXAFS_Ca_edge_special(t=0.5, name="test"):
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]

    energies = np.linspace(4030, 4100, 71)

    det_exposure_time(t, t)
    name_fmt = "nexafs_{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="JDM", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 4075)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 4050)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 4030)

    sample_id(user_name="test", sample_name="test")


def night_shift_run(t=1):
    yield from SAXS_Ca_edge_dry_special1(t=0.5)
    yield from bps.sleep(10)
    yield from SAXS_Ca_edge_dry_special2(t=0.5)


def run_saxs_nexafs(t=1):
    yield from nexafs_prep_multisample(t=0.5)
    yield from bps.sleep(10)
    yield from saxs_prep_multisample(t=0.5)


def nexafs_prep_multisample(t=1):
    names = [
        "NEXAFS_WT_CH24_1_spot3",
        "NEXAFS_WT_CH24_2_spot3",
        "NEXAFS_WT_CH24_3_spot3",
        "NEXAFS_xxt1xxt2_CH24_Ca_1_spot1",
    ]
    x_s = [27400, 20800, 14700, -13250]
    y_s = [300, 300, 200, -1300]

    for x, y, name in zip(x_s, y_s, names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        yield from NEXAFS_Ca_edge_multi(t=0.5, name=name)

    sample_id(user_name="test", sample_name="test")


def saxs_prep_multisample(t=1):
    dets = [pil300KW, pil2M]
    names = [
        "xxt1xxt2_CH24_Ca_1_spot1",
        "xxt1xxt2_CH24_Ca_1_spot2",
        "xxt1xxt2_CH24_Ca_1_spot3",
        "xxt1xxt2_CH24_Ca_3_spot3",
        "xxt1xxt2_CH24_Ca_3_spot2",
        "xxt1xxt2_CH24_Ca_3_spot1",
    ]
    x_s = [-13250, -13250, -13250, -27550, -27250, -27490]
    y_s = [-1400, -800, 100, 300, -800, -1600]

    energies = [4030, 4040, 4050, 4055, 4075]
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_pos{posi}_wa{wa}_xbpm{xbpm}"
    wa = [0, 6.5, 13.0]  # 19.5

    for x, y, name in zip(x_s, y_s, names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)

        for wax in wa:
            yield from bps.mv(waxs, wax)
            for k, e in enumerate(energies):
                yield from bps.mv(energy, e)
                name_fmt = "{sample}_{energy}eV_xbpm{xbpm}_wa{wa}"

                sample_name = name_fmt.format(
                    sample=name,
                    energy=e,
                    xbpm="%3.1f" % xbpm3.sumY.value,
                    wa="%2.1f" % wax,
                )
                sample_id(user_name="OS", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 4050)
            yield from bps.mv(energy, 4030)

        for wax in wa[::-1]:
            yield from bps.mv(waxs, wax)

            name_fmt = "{sample}_4030eV_postmeas_xbpm{xbpm}_wa{wa}"
            sample_name = name_fmt.format(
                sample=name, xbpm="%3.1f" % xbpm3.sumY.value, wa="%2.1f" % wax
            )
            sample_id(user_name="OS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        sample_id(user_name="test", sample_name="test")


def NEXAFS_Ca_edge_multi(t=0.5, name="test"):
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]

    energies = np.linspace(4030, 4150, 121)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="OS", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 4125)
    yield from bps.mv(energy, 4100)
    yield from bps.mv(energy, 4075)
    yield from bps.mv(energy, 4050)
    yield from bps.mv(energy, 4030)

    sample_id(user_name="test", sample_name="test")


def NEXAFS_Ca_edge(
    t=0.5,
):
    yield from bps.mv(waxs, 60)
    dets = [pil300KW]
    name = "hyd_cell_blank_sp2"
    # x = [8800]

    energies = np.linspace(4030, 4150, 121)

    # for name, x in zip(names, x):
    # bps.mv(piezo.x, x)
    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="JDM", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 4125)
    yield from bps.mv(energy, 4100)
    yield from bps.mv(energy, 4075)
    yield from bps.mv(energy, 4050)
    yield from bps.mv(energy, 4030)
    name_fmt = "{sample}_4030.0eV_postmeas"
    sample_name = name_fmt.format(sample=name)
    sample_id(user_name="OS", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")


def NEXAFS_P_edge(t=0.5):
    yield from bps.mv(waxs, 30)
    dets = [pil300KW]
    name = "NEXAFS_PBS1_Pedge_nspot1"

    energies = np.linspace(2140, 2180, 41)
    energies_back = np.linspace(2180, 2140, 41)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    for e in energies_back:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)


def NEXAFS_S_edge(t=0.5):
    yield from bps.mv(waxs, 30)
    dets = [pil300KW]
    name = "NEXAFS_A12_Sedge"

    energies = np.linspace(2430, 2500, 71)
    energies_back = np.linspace(2500, 2430, 36)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    for e in energies_back:
        yield from bps.mv(energy, e)


def waxs_S_edge(t=1):
    dets = [pil300KW]

    names = ["A41"]
    x = [-28200]
    y = [1600]

    names1 = ["P3HT"]
    x1 = [-38700]
    y1 = [900]

    energies = np.linspace(2456, 2500, 23)
    Ys = np.linspace(900, 2200, 23)
    waxs_arc = [0, 19.5, 4]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        det_exposure_time(t, t)
        name_fmt = "{sample}_{energy}eV"
        for e in energies:
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="SR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_arc)

        yield from bps.mv(energy, 2490)
        yield from bps.mv(energy, 2480)
        yield from bps.mv(energy, 2470)
        yield from bps.mv(energy, 2460)
        yield from bps.mv(energy, 2456)

        name_fmt = "{sample}_2456eV_postmeas"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_arc)


def waxs_S_edge(t=1):
    dets = [pil300KW]

    names1 = ["P3HT"]
    x1 = [-38700]
    y1 = [900]

    energies = [2460, 2465, 2470, 2474, 2475, 2476, 2478, 2480]
    Ys = np.linspace(900, 2200, 8)

    waxs_arc = [0, 39, 7]
    for name, xs, ys in zip(names1, x1, y1):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        det_exposure_time(t, t)
        name_fmt = "{sample}_{energy}eV"
        for e, ys in zip(energies, Ys):
            yield from bps.mv(energy, e)
            yield from bps.mv(piezo.y, ys)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.scan(dets, waxs, *waxs_arc)

        yield from bps.mv(energy, 2470)
        yield from bps.mv(energy, 2460)

        name_fmt = "{sample}_2460eV_postmeas"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_arc)


def gomez_S_edge_new(t=1):
    dets = [pil300KW]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = np.linspace(0, 19.5, 4)

    yield from bps.mv(stage.th, 0)
    yield from bps.mv(stage.y, 0)

    names = [
        "P-1",
        "P-2",
        "Y-1",
        "Y-2",
        "Y-3",
        "A5-1",
        "A05-2",
        "A0-1",
        "A0-2",
        "A2-1",
        "A2-2",
        "A05-1",
        "A5-2",
        "5",
        "2-1",
        "2-2",
        "05",
    ]
    x = [
        43400,
        38100,
        32300,
        26850,
        21700,
        16200,
        11000,
        5600,
        400,
        -4900,
        -10300,
        -15600,
        -21100,
        -26300,
        -31400,
        -36500,
        -42100,
    ]
    y = [
        -3850,
        -3950,
        -3800,
        -400,
        -4100,
        -4150,
        -4150,
        -4150,
        -4100,
        -4100,
        -4050,
        -4200,
        -3750,
        -3800,
        -3700,
        -3650,
        -3800,
    ]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 700, 29)
        xss = np.array([xs, xs + 300])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)

    yield from bps.mv(stage.th, 1)
    yield from bps.mv(stage.y, -8)
    names = ["10", "CN", "CN-2", "CB", "CB-2", "DIO", "AA-1", "AA-2", "AA-3"]
    x = [44300, 39200, 33800, 28500, 23200, 18100, 11700, 6300, 900]
    y = [-8700, -8700, -8550, -8400, -8400, -7800, -8600, -8500, -8400]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 700, 29)
        xss = np.array([xs, xs + 300])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)


def nexafs_gomez_S_edge_new(t=1):
    dets = [pil300KW]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = [52.5]

    yield from bps.mv(stage.th, 0)
    yield from bps.mv(stage.y, 0)

    names = ["A05-1", "A5-2", "5", "2-1", "2-2", "05"]
    x = [-15600, -21100, -26300, -31400, -36500, -42100]
    y = [-4200, -3750, -3800, -3700, -3650, -3800]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            det_exposure_time(t, t)
            name_fmt = "nexafs_{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)

    yield from bps.mv(stage.th, 1)
    yield from bps.mv(stage.y, -8)
    names = ["10", "CN", "CN-2", "CB", "CB-2", "DIO", "AA-1", "AA-2", "AA-3"]
    x = [44300, 39200, 33800, 28500, 23200, 18100, 11700, 6300, 900]
    y = [-8700, -8700, -8550, -8400, -8400, -7800, -8600, -8500, -8400]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "nexafs_{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(1)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)





def nexafs_Caedge_2026_1():
    dets = [pil900KW]

    name='nexafs_native2A_ai0.5deg'
    energies = np.linspace(4030, 4070, 41)

    waxs_arc = [7]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            # yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                bpm = xbpm3.sumX.get()
                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_name = sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ =, "})
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner()) 



def Ca_edge_measurments_2026_1(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = [   'w01',  'w02',  'w03',  'w04',  'w05',  'w06',  'w07',  'w08',  'w09',  'w10',  'w11',  'w12',
                'w13',  'w14',  'w15',  'w16',  'w17',  'w18',  'w19',  'w20',  'w21',  'w22',  'w23',  'w24',
                'w25',  'w26',  'w27',  'w28',  'w29',  'w30']
    
    x_piezo = [-43500, -40500, -37500, -34500, -32000, -28500, -25500, -22000, -19000, -15500, -12500, -9500, 
                -6500,  -3500,  -1500,   1000,   4500,   7500,  10500,  14000,  17000,  19500,  23000, 26000, 
                29000,  32500,  35500,  39000,  42500,  45500]
    

    names = [   'w20',  'w21',  'w22',  'w23',  'w24',
                'w25',  'w26',  'w27',  'w28',  'w29',  'w30']
    
    x_piezo = [ 14000,  17000,  19500,  23000, 26000, 
                29000,  32500,  35500,  39000,  42500,  45500]
    # y_piezo = [  2500,   2500,   2500,   2500,   2500,   2500,   2500,   2500,   2500,   2500,   2500,   2500,
    #              2500,   2500,   2500,   2500,   2500,   2500] 


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    # assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    energies = [4030, 4040, 4045, 4048, 4049, 4050, 4051, 4052, 4053, 4053.5, 4054, 4054.5, 4055, 4055.5, 4056, 
                4057, 4058, 4059, 4060, 4062, 4064, 4067, 4070, 4080, 4090, 4100, 4120, 4140, 4150]
    
    waxs_arc = [7, 15]
    ai_list = [0.5]

    for name, xs in zip(names, x_piezo):

        yield from bps.mv(piezo.x, xs)

        yield from alignement_gisaxs_short(0.1)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)

        print(f"AI0: {piezo.th.position}, Y: {piezo.y.position}")
        ai0 = piezo.th.position

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

                    yield from bps.mv(energy, 4100)
                    yield from bps.sleep(3)
                    yield from bps.mv(energy, 4050)   
                    yield from bps.sleep(3)

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())




def nexafs_Cl_edge_2026_1(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = [ 'bpph_nexafs_att9_2x']
    x_piezo = [-51000]
    y_piezo=[0]
    x_hexa = [     0]
    z_piezo = [ 7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.asarray([2803. , 2813. , 2823. , 2825. , 2827. , 2827.5, 2828. , 2828.5, 2829. , 2829.5, 2830.,
                           2830.5, 2831. , 2831.5, 2832. , 2832.5, 2833. , 2833.5, 2834. , 2834.5, 2838. , 2843.,
                             2848. , 2853. ,2858. , 2863. , 2868. , 2873. , 2883. ])
    waxs_arc = [15]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the wa
            
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd5m"

            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm3.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2870)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2840)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2800)
            yield from bps.sleep(2)




def swaxs_Cl_edge_2026_1(t=1):
    """
    307830_Su June 23, 2024
    """

    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)

    names = [ 'bpph', 'bp66', 'bp50', 'mtph', 'ptph', 'pqph', 'pqph2n', 'bp502n', 'blank']
    x =     [  38000,  21500,   4500, -11500, -29000,  29000,    10000,   -4000,   -16000]
    y =     [  -6500,  -6500,  -6000,  -6000,  -5500,   7000,     7000,    7000,     7000]
    z =     [   1600,   1600,   1600,   1600,   1600,   1600,     1600,    1600,     1600]

    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"
    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(z), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(z)})"


    energies = np.asarray([2803.0, 2813. , 2823. , 2825. , 2827. , 2827.5, 2828. , 2828.5, 2829. , 2829.5, 2830.,
                           2830.5, 2831. , 2831.5, 2832. , 2832.5, 2833. , 2833.5, 2834. , 2834.5, 2838. , 2843.,
                             2848. , 2853. ,2858. , 2863. , 2868. , 2873. , 2883. ])
    
    waxs_arc = [7, 20]

    for name, xs, ys, zs in zip(names, x, y, z):

        # changing ys to allow for more room during dense energy scan
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yss = np.linspace(ys, ys + 1000, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_2.0m_{energy}eV_wa{wax}_bpm{xbpm}"
                for e, xsss, ysss in zip(energies, xss, yss):
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    yield from bps.mv(piezo.y, ysss)
                    yield from bps.mv(piezo.x, xsss)

                    bpm = xbpm3.sumX.get()
                    
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    s.put(sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

                
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2860)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2830)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2803)
                yield from bps.sleep(2)

        (yield from inner())




def saxs_humidity_2026_1(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    # names   = [ 'PT', 'MPT', 'BP50', 'BP66',  'BP']
    # hex_x = [  -15.3, -8.95,   -2.6,   3.75, 10.11]
    # hex_y = [   -0.7,  -0.7,   -0.7,   -0.7,  -0.7]

   # names   = [ 'Blank5', 'Blank4', 'Blank3', 'Blank2',  'Blank1']
   # hex_x = [  -15.3, -8.95,   -2.6,   3.75, 10.11]
   # hex_y = [   -0.7,  -0.7,   -0.7,   -0.7,  -0.7]

    names   = [ 'BP502N_run2', 'PQPh2N_run2', 'BlankMiddle', 'PQPh_run2',  'BP_run3']
    hex_x = [  -15.3, -8.95,   -2.6,   3.75, 10.11]
    hex_y = [   -0.7,  -0.7,   -0.7,   -0.7,  -0.7]

   

    # Offsets for taking a few points per sample
    y_off = [-0.3, 0, 0.3]
    user = "GF"
    waxs_arc = [20, 7]

    # Check if the length of xlocs, ylocs and names are the same
    assert len(hex_x) == len(names), f"Number of X coordinates ({len(hex_x)}) is different from number of samples ({len(names)})"

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        # Detectors, disable SAXS when WAXS in the way
        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            
            for name, x, y in zip(names, hex_x, hex_y):
                yield from bps.mv(stage.x, x)

                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(stage.y, y + y_of)
                    yield from bps.sleep(2)

                    loc = f'{yy}'
                    sample_name = f'{name}{get_scan_md()}_wa{wa}_loc{loc}'
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, xbpm2, xbpm3, stage.x, stage.y] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def saxs_cap_2026_1(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    names   = [ 'BPPhCl_SanityCheck']
    x = [ 8250]
    y = [ -1800]
    z = [-1400]


    # Offsets for taking a few points per sample
    y_off = [-400, 0,400]
    user = "GF"
    waxs_arc = [20, 7]

    # Check if the length of xlocs, ylocs and names are the same
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"
    assert len(y) == len(names), f"Number of X coordinates ({len(y)}) is different from number of samples ({len(names)})"

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        # Detectors, disable SAXS when WAXS in the way
        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            
            for name, xs, ys in zip(names, x, y):
                yield from bps.mv(piezo.x, xs, 
                                  piezo.y, ys)

                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, ys + y_of)
                    yield from bps.sleep(2)

                    loc = f'{yy}'
                    sample_name = f'{name}{get_scan_md()}_wa{wa}_loc{loc}'
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, xbpm2, xbpm3, piezo.x, piezo.y] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

def swaxs_humidity_Cl_edge_2026_1(t=1):
    """
    307830_Su June 23, 2024
    """

    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)

    names   = [ 'TrexsBlank6', 'BP502N_Run2', 'PTPh_run2', 'TrexsBlank2', 'TrexsBlank1']
    x = [  -21.65, -15.3, -2.6, 3.75, 10.11]
    y = [   -0.5,  -0.5,   -0.5, -0.5, -0.5]

    assert len(hex_x) == len(names), f"Number of X coordinates ({len(hex_x)}) is different from number of samples ({len(names)})"
    assert len(hex_x) == len(hex_y), f"Number of X coordinates ({len(hex_x)}) is different from number of samples ({len(hex_y)})"

    energies = np.asarray([2803.0, 2813. , 2823. , 2825. , 2827. , 2827.5, 2828. , 2828.5, 2829. , 2829.5, 2830.,
                           2830.5, 2831. , 2831.5, 2832. , 2832.5, 2833. , 2833.5, 2834. , 2834.5, 2838. , 2843.,
                             2848. , 2853. ,2858. , 2863. , 2868. , 2873. , 2883. ])
    
    waxs_arc = [7, 20]

    for name, xs, ys in zip(names, hex_x, hex_y):

        # changing ys to allow for more room during dense energy scan
        yield from bps.mv(stage.x, xs, 
                          stage.y, ys)

        yss = np.linspace(ys-0.3, ys + 0.3, len(energies))
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_5.0m_{energy}eV_wa{wax}_bpm{xbpm}"
                for e, xsss, ysss in zip(energies, xss, yss):
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    yield from bps.mv(stage.y, ysss, 
                                      stage.x, xsss)

                    bpm = xbpm3.sumX.get()
                    
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    s.put(sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9, stage.x, stage.y] + [s])

                yield from bps.sleep(2)
                yield from bps.mv(energy, 2860)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2830)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2803)
                yield from bps.sleep(2)

        (yield from inner())



def giwaxs_2026_1(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    # names = [   'NR_CB_04',  'FN_GI_01', 'FN_GI_02', 'FN_GI_03', 'FN_GI_04', 'NR_CB_01', 'NR_CB_02', 'NR_CB_03']    
    # x_piezo = [ 50000,         40000, 23000, 3000, -12000, -27000, -42000, -52000]
    # # FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [      7,              0,    0,    0,      0,      0,      0,     -5]    
    # y_piezo = [  3500,           3500, 3500, 3500,  3500,   3500,    3500,   3500]
    

    #Refer to this example
    #names = [   'NR_OX_01', 'NR_0X_02', 'NR_OX_03', 'NR_OX_04', 'NR_OX_05', 'NR_OX_06']
    #x_piezo = [      51000,      42711,      24500,       9000,     -23000,     -43000]
    # FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    #x_hexa = [           7,          0,          0,          0,          0,          0]    
    #y_piezo = [       3500,       3500,       3500,       3500,       3500,       3500]

    # names = [   'AO_126_A_0DEG', 'AO_126_B1_0DEG', 'AO_126_B2_0DEG', 'AO_126_C_0DEG', 'AO_126_D1', 'AO_126_D2']
    # x_piezo = [      46000, 29000, 10500, -10000, -21000, -43000]
    # #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [           0, 0, 0, 0, 0, 0]    
    # y_piezo = [       1145, 1145, 1145, 1145, 1145, 1145]
    # # z hexapod at 4.9 mm

    # names = [   'AO_126_E1_0DEG', 'AO_126_E2_0DEG', 'AO_127_A_0DEG', 'AO_127_B_0DEG', 'AO_127_C_0DEG',
    #         'AO_127_E_0DEG', 'AO_128_A_0DEG', 'AO_128_B_0DEG']
    # x_piezo = [      53860, 45000, 30000, 14000, -3000, -19500, -37500, -47500]
    # #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [           7, 0, 0, 0, 0, 0, 0, -5]    
    # y_piezo = [       900, 900, 900, 900, 900, 900, 900, 900]
    # # z hexapod at 0 mm
    # # th at -0.137

    # names = [   'AO_126_A_90DEG', 'AO_126_B1_90DEG', 'AO_126_B2_90DEG', 'AO_126_C_90DEG', 'AO_126_D1_90DEG', 'AO_126_D2_90DEG']
    # x_piezo = [      41000, 21500, 8500, -10000, -24000, -43000]
    # #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [           0, 0, 0, 0, 0, 0]    
    # y_piezo = [       1145, 1145, 1145, 1145, 1145, 1145]
    # z hexapod at 4.9 mm

    # names = [   'AO_126_E1_90DEG', 'AO_126_E2_90DEG', 'AO_127_A_90DEG', 'AO_127_B_90DEG', 'AO_127_C_90DEG',
    #         'AO_127_E_90DEG', 'AO_128_A_90DEG', 'AO_128_B_90DEG']
    # x_piezo = [      47500, 40250, 24000, 7500, -9000, -25000, -42000, -52500]
    # #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [           7, 0, 0, 0, 0, 0, 0, -5]    
    # y_piezo = [       900, 900, 900, 900, 900, 900, 900, 900]
    # # z hexapod at 0 mm
    # # th at -0.137

    names = ['AO_128_B_90DEG']
    x_piezo = [-52500]
    #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    x_hexa = [-5]    
    y_piezo = [1800]
    # z hexapod at 0 mm
    # th at -0.137

    # don't worry about th_piezo. can just tune theta in SmarAct2coordinates manually if alignment program
        # struggles to find the 0 theta for the sample.
    # th_piezo = [  0,           0, 0, 0,  0,   0,    0,   0]

    # IF ACQUISITION FAILS, RECREATE LIST BELOW STARTING FROM FAILED SAMPLE.

    #example:
    # names = [    'FN_GI_04', 'NR_CB_01', 'NR_CB_02', 'NR_CB_03']    
    # x_piezo = [-12000, -27000, -42000, -52000]
    # x_hexa = [        0,      0,      0,     -5]    
    # y_piezo = [    3500,   3500,    3500,   3500]
    # th_piezo = [ 0,   0,    0,   0]

    # names = [   'AO_126_B1_0DEG', 'AO_126_B2_0DEG', 'AO_126_C_0DEG', 'AO_126_D1', 'AO_126_D2']
    # x_piezo = [      29000, 10500, -10000, -21000, -43000]
    # #FOR X_HEXA, DO NOT EXCEED POSITIVE OR NEGATIVE 10. TO BE SAFE, STAY WITHIN POSITIVE OR NEGATIVE 8.
    # x_hexa = [           0, 0, 0, 0, 0]    
    # y_piezo = [       1145, 1145, 1145, 1145, 1145]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    # assert len(x_piezo) == len(th_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(th_piezo)})"

    waxs_arc = [7, 20]

    ai0_all = -0.6

    # ai_list = [0.065, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    # UNCOMMENT BELOW ai_list FOR AGATHA SAMPLES
    ai_list = [0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.84, 0.95, 1.05, 1.16, 1.26]
    # UNCOMMENT BELOW ai_list FOR LOUIS SAMPLES
    # ai_list = [0.065, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.84, 0.91, 0.98, 1.05, 1.12]
    
    
    #np.linspace(0.07, 0.3, 24)
    # xstep = 200

    dets = [pil2M, pil900KW]
    
    # for name, xs, ys, xs_hexa, ai0_all  in zip(names, x_piezo, y_piezo, x_hexa, th_piezo):
    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                        piezo.x, xs,
                        # piezo.y, ys,
                        piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.1)
        print('alignement done')

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                # counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)
                    yield from bps.sleep(1)

                    name_fmt = "{sample}_16.1keV_9.2m_ai{ai}_wa{wax}"
                    
                    # yield from bps.mv(piezo.x, xs - counter * xstep)
                    # counter += 1

                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())


def changetoGI():
    pil2M.rod_offset_x_mm.set(7.8)
    yield from pil2M.insert_beamstop('rod')
    yield from bps.mv(piezo.z, 0)
    yield from bps.mv(piezo.y, 3500)

    # This will move first the pindiode out
    # Then it will move the rod in. Make sure that the X positon of the SAXS bs is 7.8
    # If not do not take data, the beamstop might be out
    
    #What you can try; in the bluesky tab, do: pil2M.rod_offset_x_mm.set(7.8)
    #And then: RE(smi.modeMeasurement())
    #This is what will be done at the end of the alignement. If the beamstop goes at 7.8 good>
    #If not moving it manually will not save the issue since at the end of any alignement iit will go back to the wrong position

    # If this is not working, shoot me a msg

    # Make sure piezo.y is correct: i.e. on the on axis camera, you should see the surface of your sample

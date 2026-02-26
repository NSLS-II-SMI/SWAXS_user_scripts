def guigui(meas_t=0.3):
    det = [pil2M]
    """
        names = ['Diag_ver_10-50nm', 'DX_10-50nm',
        'Diag_ver_2-8nm', 'DX_2-8nm',
        'CDUp_10-50nm', 'CDUm_10-50nm', 'Mxp_10-50nm', 'Mx-_10-50nm',
        ]
              
        x = [11200, 11200, 11200, 5900, 627, -4873, -4873, -4873]
        y = [-2660, 2450,  7749,  7749, 7749,-2660,  2450,  7749]

        
        names = ['CDUp_2-8nm', 'CDUm_2-8nm', 'Mxp_2-8nm', 'Mx-_2-8nm',
        ]
              
        x = [11550, 7250, 2050, -3350]
        y = [8758, 8758, 8758]

        names = ['Mx-_2-8nm']
              
        x = [-3350]
        y = [8758]
        """
    names = ["Mx-_2-8nm","Mxp_2-8nm","CDUm_2-8nm","CDUp_2-8nm","Mx-_10-50nm","Mxp_10-50nm","CDUm_10-50nm","CDUp_10-50nm","Diag_ver_2-8nm",
             "DX_2-8nm","Diag_ver_10-50nm","DX_10-50nm"]
    x = [11550, 7250, 2050, -3350, 11550, -3350, 11550, -3350, 11550, 7250, 2050, -3350]
    y = [8758, 8758, 8758, 8758, 3458, 3458, 3458, 3458, -1742, -1742, -7041, -7041]

    for a in range(0, 12, 1):
        yield from bps.mv(piezo.x, x[a])
        yield from bps.mv(piezo.y, y[a])
        yield from align_gui()
        plt.close("all")
        det_exposure_time(meas_t)
        name_fmt = "{sample}_{num}"
        sample_name = name_fmt.format(sample=names[a], num=a)
        sample_id(user_name="GF_11.8keV_8.3m_ref", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)


def waxs_S_edge_guil(t=1):
    dets = [pil300KW]

    names = ["sample02","sample03","sample04","sample05","sample06","sample07","sample08","sample09","sample10","sample11","sample12"]
    x = [26500,21500,16000,10500,5000,0,-5500,-10500,16000,-21000,-26500]  # , -34000, -41000]
    y = [600, 600, 800, 700, 700, 600, 600, 600, 600, 900, 900]  # , 700, 800]

    energies = np.linspace(2450, 2500, 26)
    waxs_arc = [0, 6.5, 13]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 1300, 26)

        if int(waxs.arc.position) == 0:
            waxs_arc = [0, 6.5, 13]
        elif int(waxs.arc.position) == 13:
            waxs_arc = [13, 6.5, 0]

        if name == "sample02":
            waxs_arc = [6.5, 0]
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}"
            for e, ysss in zip(energies, yss):
                yield from bps.sleep(1)
                yield from bps.mv(energy, e)
                yield from bps.mv(piezo.y, ysss)
                sample_name = name_fmt.format(sample=name, energy=e, wax=wa)
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)


def gratings_S_edge(t=1):
    dets = [pil300KW]

    names = ["1908_J3030_40p20cd"]
    energies = [2400,2432,2433,2434,2435,2436, 2437,2438,2439,2440,2441,2442,2443,2444,2445,2446,2447,2448,2449,2450]

    for name in names:
        det_exposure_time(t, t)
        name_fmt = "{sample}_{energy}eV"
        for e in energies:
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def gratings_Sn_edge(t=1):
    dets = [pil300KW]

    names = ["1908_YAHY_40p11cd"]

    energies = [3900,3920,3921,3922,3923,3924,3925,3926,3927,3928,3929,3930,3931,3932,3933,3934,3935,3936,3937,3940]

    for name in names:
        det_exposure_time(t, t)
        name_fmt = "{sample}_{energy}eV_ai0.7deg"
        for e in energies:
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=name, energy=e)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def nikhil_Zn_edge(t=1):
    dets = [pil300KW, pil300kwroi2]

    names = ["Zn0_unexposed", "Zn0_exposed"]
    xs = [14000, -8000]

    energies = np.linspace(9620, 9700, 81)

    for x, name in zip(xs, names):
        bps.mv(piezo.x, x)
        det_exposure_time(t, t)
        name_fmt = "{sample}_{energy}eV_ct{xbpm}_ai0.1deg"
        for e in energies:
            yield from bps.mv(energy, e)
            xbpm = xbpm3.sumX.value
            sample_name = name_fmt.format(sample=name, energy=e, xbpm="%3.2f" % xbpm)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            # yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 9680)
        yield from bps.mv(energy, 9660)
        yield from bps.mv(energy, 9640)
        yield from bps.mv(energy, 9620)


def meas_gels(t=1):
    dets = [pil300KW, pil2M]

    names = ["DIwater", "bkg_wat"]
    # names = ['sam48', 'sam49', 'sam50', 'sam51', 'sam52', 'sam53', 'sam54']
    xs = [27000, -15000]

    waxs_arc = [0, 13, 3]

    for x, name in zip(xs, names):
        yield from bps.mv(piezo.x, x)
        det_exposure_time(t, t)
        name_fmt = "{sample}_16p1keV_8p3m_"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.scan(dets, waxs, *waxs_arc)


def sin_generation():
    x = np.linspace(0, 30000, 30000)
    gx = 50000 * np.sin(x / 5)  # 20000, 15000, 6000

    # plt.figure()
    # plt.plot(x, gx)
    # plt.show()

    for gs in gx:
        yield from bps.sleep(0.01)
        trigger_signal = "XF:12IDB-BI:2{EM:BPM3}fast_pidY.VAL"
        yield from bps.mv(trigger_signal, gs)


def run_Liheng(t=1):
    # samples = ['LBBL_0.09_sdd8.3m_16.1keV', 'LBBL_0.32_sdd8.3m_16.1keV']

    # x_list  = [37000, 24000]
    # y_list =  [-200, -200]

    # # Detectors, motors:
    # dets = [pil2M]
    # assert len(x_list) == len(samples), f'Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})'
    # assert len(x_list) == len(y_list), f'Number of X coordinates ({len(x_list)}) is different from number of Y coord ({len(y_list)})'

    # ypos = [0, 200, 2]

    # det_exposure_time(t,t)
    # for x, y, sample in zip(x_list,y_list,samples):
    #     yield from bps.mv(piezo.x, x)
    #     yield from bps.mv(piezo.y, y)
    #     sample_id(user_name='LC', sample_name=sample)
    #     yield from bp.rel_scan(dets, piezo.y, *ypos)
    #     # yield from bp.count(dets, num=3)

    samples = ["LhBBL_1.08", "LhBBL_0.94", "LhBBL_0.84", "glass_only"]

    x_list = [-4500, -20000, -32000, -37000]
    y_list = [-500, -500, -500, -500]

    ypos = [0, 200]

    waxs_range = np.linspace(13, 0, 3)
    det_exposure_time(t, t)
    dets = [pil2M, pil300KW]

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)

        for x, y, sample in zip(x_list, y_list, samples):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)

            for yy, y_of in enumerate(ypos):
                yield from bps.mv(piezo.y, y + y_of)

                name_fmt = "{sam}_wa{waxs}_yloc{yy}"
                sample_name = name_fmt.format(
                    sam=sample, yy="%2.2d" % yy, waxs="%2.1f" % wa
                )
                sample_id(user_name="LC", sample_name=sample_name)

                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def batch_caps(t=1):
    samples = ["0.5RLPF","0.5RLPW","1.0RLPW","W2F2-G6","W2F-GL","W2F4-G6","W2F3-G6", "0.5RLPF_4AC","0.5RLPW_4AC","1.0RLPW_4AC","W2F3-G8",
               "F3Y3-G8","W2F6-G8"]
    # 'S2_CuHHTT_TEBF4_Soaked', 'S3_CuHHTT_KNO2_Soaked', 'S5_CuHHTT_TEBF4_Pos', 'S6_CuHHTT_KNO2_Pos','S7_CuHHTT_CsBr_Pos','S9_CuHHTT_KNO2_Neg','S10_CuHHTT_CsBr_Neg'
    # 'S2_CuHHTT_TEBF4_Bare','S4_CuHHTT_CsBr_Soaked','S8_CuHHTT_TEBF4_Neg','S11',
    
    x_list = [38110,31700,25500,18810,12640,6420,-2000,35600,29260,22920,16400,10230,2370]
    # -6600, -13000, -19800, -26000, -32400, -38500, -44800,
    # -9250, -21950, -28200, -34500,

    y_list = [1100,1100,1100,1100,1100,1100,1100,1100,1100,1100,1100,1100,1100]
    # 2000, 2000, 2000, 2000, 2000, 1000, 2000,
    # 2000, 2000, 2000, 2000,

    z_list = [2600,2600,2600,2600,2600,2600,-1400,11600,11600,11600,11600,11600,11600]
    # 2600, 2600, 2600, 2600, 2600, 2600, 2600,
    # 11600, 11600, 11600, 11600,

    # Detectors, motors:
    dets = [pil2M]
    assert len(x_list) == len(samples), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(y_list), f"Number of X coordinates ({len(x_list)}) is different from number of Y coord ({len(y_list)})"
    assert len(x_list) == len(z_list), f"Number of X coordinates ({len(x_list)}) is different from number of Z coord ({len(z_list)})"
    ypos = [0, 50, 2]

    det_exposure_time(t, t)
    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)
        sample_id(user_name="KK_sdd1.8m", sample_name=sample)
        yield from bp.rel_scan(dets, piezo.y, *ypos)
        # yield from bp.count(dets, num=3)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def batch_caps_yugang(t=1):
    samples = [ # '2', '3', '5', '6',  '7',  '9', '10', #    '1',     '4', '8',  '11',
    "S2_CuHHTT_TEBF4_Soaked", "S3_CuHHTT_KNO2_Soaked","S5_CuHHTT_TEBF4_Pos","S6_CuHHTT_KNO2_Pos","S7_CuHHTT_CsBr_Pos","S9_CuHHTT_KNO2_Neg",
    "S10_CuHHTT_CsBr_Neg","S2_CuHHTT_TEBF4_Bare","S4_CuHHTT_CsBr_Soaked","S8_CuHHTT_TEBF4_Neg","S11"]

    x_list = [# 38110, 31700, 25500, 18810, 12640, 6420, -2000, 35600,        22920, 16400, 10230,
        -6520,-12920,-19680,-25860, -32260,-38440,-44740,-8970,-21650,-27940,-34270]

    y_list = [# 600, 600, 600, 600, 600, 600, 600,600,      600, 600, 600,
    2000,2000,2000,2000,2000,1000,2000,2000,2000,2000,2000]

    z_list = [
        # 2600, 2600, 2600, 2600, 2600, 2600, -1400,
        #         11600, 11600, 11600, 11600, 11600, 11600,
    2600,2600,2600,2600,2600,2600,2600,11600,11600,11600, 11600]

    # Detectors, motors:
    dets = [pil2M]
    assert len(x_list) == len(samples), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(x_list) == len(y_list), f"Number of X coordinates ({len(x_list)}) is different from number of Y coord ({len(y_list)})"
    assert len(x_list) == len(z_list), f"Number of X coordinates ({len(x_list)}) is different from number of Z coord ({len(z_list)})"
    ypos = [0, 50, 2]

    det_exposure_time(t, t)
    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)
        sample_id(user_name="YZ", sample_name=sample)
        yield from bp.rel_scan(dets, piezo.y, *ypos)
        # yield from bp.count(dets, num=3)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def run_night_gui():
    # proposal_id('2020_3', '307283_Zhang3')
    # yield from song_waxs_Sedge_2020_3(1)

    proposal_id("2020_3", "307283_Zhong2")
    yield from waxs_S_edge_wenkai(1)

    proposal_id("2020_3", "305401_Gomez2")
    yield from NEXAFS_S_edge(0.5)
    yield from gomez_S_edge(1)

    proposal_id("2020_3", "000000_Su")
    yield from Su_nafion_waxs_S_edge(1)
    yield from Su_nafion_waxs_S_edge_extra(0.5)


def song_waxs_Sedge_2020_3(t=1):

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(5)
    yield from bps.mv(GV7.close_cmd, 1)

    dets = [pil300KW]
    waxs_arc = np.linspace(0, 19.5, 4)
    energies = np.linspace(2460, 2490, 16)

    yield from bps.mv(stage.th, 0)
    yield from bps.mv(stage.y, 0)

    names = ["G4", "H1", "H2", "H3", "H4", "H5"]
    x = [44250, 38900, 32300, 26300, 20300, 14300]
    y = [-2450, -2450, -2350, -2350, -2350, -2350]
    z = [2700, 2700, 2700, 2700, 2700, 2700]

    for name, xs, ys, zs in zip(names, x, y, z):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yss = np.linspace(ys, ys + 500, 8)
        xss = np.linspace(xs, xs + 250, 2)

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                try:
                    yield from bps.mv(energy, e)
                except:
                    print("energy failed to move, sleep for 30 s")
                    yield from bps.sleep(30)
                    print("Slept for 30 s, try move energy again")
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

            yield from bps.mv(energy, 2475)
            yield from bps.mv(energy, 2460)


def waxs_S_edge_wenkai(t=1):

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(5)
    yield from bps.mv(GV7.close_cmd, 1)

    dets = [pil300KW]

    names = ["Rxbai-P", "Rxbai-C"]
    x = [-9500, -16000]
    y = [-2500, -2500]
    z = [2700, 2700]

    names = ["Rxbai-C"]
    x = [-16000]
    y = [-2500]
    z = [2700]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = np.linspace(19.5, 39, 4)

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 1000, 29)
        xss = np.array([xs, xs + 500])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                try:
                    yield from bps.mv(energy, e)
                except:
                    print("energy failed to move, sleep for 30 s")
                    yield from bps.sleep(30)
                    print("Slept for 30 s, try move energy again")
                    yield from bps.mv(energy, e)

                yield from bps.sleep(1)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm2.sumX.value

                sample_name = name_fmt.format(
                    sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm
                )
                sample_id(user_name="WZ", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2470)
            yield from bps.mv(energy, 2450)


def NEXAFS_S_edge(t=0.5):
    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(5)
    yield from bps.mv(GV7.close_cmd, 1)

    yield from bps.mv(waxs, 52)
    dets = [pil300KW]
    names = ["sample1", "sample2", "sample3"]
    x = [9300, 3900, -2000]
    y = [-2100, -2100, -1900]

    energies = np.linspace(2430, 2500, 71)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        for e in energies:
            try:
                yield from bps.mv(energy, e)
            except:
                print("energy failed to move, sleep for 30 s")
                yield from bps.sleep(30)
                print("Slept for 30 s, try move energy again")
                yield from bps.mv(energy, e)
            yield from bps.sleep(1)

            sample_name = name_fmt.format(
                sample=name, energy="%6.2f" % e, xbpm="%3.1f" % xbpm3.sumY.value
            )
            sample_id(user_name="SR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2470)
        yield from bps.mv(energy, 2450)


def gomez_S_edge(t=1):

    yield from bps.mv(GV7.close_cmd, 1)
    yield from bps.sleep(5)
    yield from bps.mv(GV7.close_cmd, 1)

    dets = [pil300KW]

    energies = [2456, 2464, 2472, 2477, 2478, 2479, 2490, 2492]
    waxs_arc = np.linspace(0, 26, 5)

    yield from bps.mv(stage.th, 0)
    yield from bps.mv(stage.y, 0)

    names = ["sample1", "sample2", "sample3"]
    x = [9100, 3700, -1800]
    y = [-2100, -2100, -1900]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 400, 8)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                try:
                    yield from bps.mv(energy, e)
                except:
                    print("energy failed to move, sleep for 30 s")
                    yield from bps.sleep(30)
                    print("Slept for 30 s, try move energy again")
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


def giwaxs_ashwant_(t=1):

    samples = [
        "sample5.0per",
        "sample7.5per",
        "sample10per",
        "sample15per",
        "sample20per",
    ]
    x_list = [43000, 26000, 7000, -13000, -32000]

    waxs_arc = np.linspace(0, 19.5, 4)
    angle = [0.45, 0.5]

    # Detectors, motors:
    dets = [pil2M, pil300KW]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from alignement_gisaxs(angle=0.3)

        # yield from bps.mv(att2_9, 'Insert')
        # yield from bps.sleep(5)
        # yield from bps.mv(att2_9, 'Insert')

        ai0 = piezo.th.position

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            det_exposure_time(t, t)
            name_fmt = "{sample}_3.33keV_ai{angle}deg_wa{wax}"

            for an in angle:
                yield from bps.mv(piezo.th, ai0 + an)
                sample_name = name_fmt.format(
                    sample=sample, angle="%3.3f" % an, wax="%2.2d" % wa
                )
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


def NEXAFS_Ag_edge(t=0.5):
    yield from bps.mv(waxs, 52)

    dets = [pil300KW]
    energies = np.linspace(3330, 3450, 121)

    name = "nexafs_sample20per"

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        try:
            yield from bps.mv(energy, e)
        except:
            print("energy failed to move, sleep for 30 s")
            yield from bps.sleep(30)
            print("Slept for 30 s, try move energy again")
            yield from bps.mv(energy, e)
        yield from bps.sleep(1)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


def test_pilatus900kw(t=1):

    dets = [pil300KW, pil900KW, pil2M]

    names = ["AgBh_5"]
    x = [-9000]
    y = [107.620]
    z = [6000]

    waxs_arc = [0, 2, 19.5, 21.5, 39, 41]
    for name, xs, ys, zs in zip(names, x, y, z):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_wa{wax}"

            sample_name = name_fmt.format(sample=name, wax=wa)
            sample_id(user_name="WZ", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def flatfield_Sedge(t=1):

    dets = [pil900KW]

    names = ["flatfield1700eV_stronger_2477eV"]
    x = [43000]
    y = [-4000]
    z = [0]

    waxs_arc = np.linspace(27, 49, 23)
    for name, xs, ys, zs in zip(names, x, y, z):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        y_list = np.linspace(ys, ys + 400, 16)

        for (wa, y_li) in zip(waxs_arc, y_list):
            yield from bps.mv(piezo.y, y_li)
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)
            name_fmt = "{sample}_wa{wax}"

            sample_name = name_fmt.format(sample=name, wax="%3.1f" % wa)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)


def Sedge_testflatfield(t=1):
    dets = [pil900KW]

    names = ["Cl2_01"]
    x = [19600]
    y = [-4000]
    z = [0]

    energies = (
        np.arange(2445, 2470, 5).tolist()
        + np.arange(2470, 2480, 0.25).tolist()
        + np.arange(2480, 2490, 1).tolist()
        + np.arange(2490, 2501, 5).tolist()
    )
    waxs_arc = [0, 20, 40]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yss = np.linspace(ys, ys + 1000, 31)
        xss = np.array([xs, xs + 500])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            det_exposure_time(t, t)

            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(3)

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


def test_gi_align():
    # t0 = time.time()
    # yield from bp.rel_scan([pil2M], piezo.y, 0, 0, 5)
    # ps(der=True)
    # print(ps.min)
    # t1 = time.time()
    # print('time for ps is', t1-t0)

    t0 = time.time()
    yield from bp.rel_scan([pil2M], piezo.y, 0, 0, 5)
    t1 = time.time()
    uid = list(bec._peak_stats)[0]
    stats = list(bec._peak_stats[uid])[0]
    print(bec._peak_stats[uid][stats].x[0])
    t2 = time.time()
    print("time for scan is", t1 - t0)
    print("time for new ps is", t2 - t1)


def giwaxs_fleury_2022_3(t=0.5):
    """
    GIWAXS macro for 309504 Gregory
    """
    user_name = "GF"

    # Samples and coordinates
    # first bar: Georgia Tech GIWAXS, PEDOT and DPP samples
    # names = [ 'CFE_7_RT',  'CFE_7_55', 'CFE_7_105']
    # x_piezo = [   -53000,      -45000,      -25000]
    # y_piezo = [      3500,       3500,        3500]
    # z_piezo = [     -1000,         -1000,    -1000]
    # x_hexa =  [       -10,             0,        0]

    names = [ 'sample1','sample2','sample3','sample5','sample6','sample7','sample8']
    x_piezo = [   -9000,     2000,    14000,    26000,    37000,    49000,    52000]
    y_piezo = [    3500,     3500,     3500,     3500,     3500,     3500,     3500]
    z_piezo = [   -1000,    -1000,    -1000,    -1000,    -1000,    -1000,    -1000]
    x_hexa =  [       0,        0,        0,        0,        0,        0,       10]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # Geometry conditions
    waxs_angles = [0, 2, 20, 22]
    inc_angles = [0.1, 0.15]
    det_exposure_time(t, t)

    # Go over samples and thier positions
    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, 0.5)

        # Align sample
        yield from alignement_gisaxs(angle=0.1)

        ai0 = piezo.th.position

        # Go over WAXS detector angles
        for wa in waxs_angles:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]

            # Go over different incident angles
            for i, ai in enumerate(inc_angles):
                yield from bps.mv(piezo.th, ai0 + ai)
                yield from bps.mv(piezo.x, xs-i*500)


                # Metadata
                name_fmt = "{sample}_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}_ai{ai}"
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                sample_name = name_fmt.format(
                    sample=name,
                    energy="%.1f" % e,
                    sdd="%.1f" % sdd,
                    wax=str(wa).zfill(4),
                    xbpm="%4.3f" % bpm,
                    ai="%.2f" % ai,
                )
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # Take data
                yield from bp.count(dets, num=1)
            yield from bps.mv(piezo.th, ai0)




def waxs_fleury_2022_3(t=0.5):
    """
    GIWAXS macro for 309504 Gregory
    """
    user_name = "GF"

    names = [     'DS32',    'DS33',    'DS34',    'DS36',    'DS37',    'DS38',   'ISV44',  'ISV220','ISV220_sol']
    x_piezo = [    39800,     27000,     20800,     14500,      1600,     -4800,    -11000,    -17500,    -23800]
    y_piezo = [    -5000,     -3900,     -3900,     -4600,     -4100,     -4800,     -4500,     -4400,     -4200]
    z_piezo = [      710,       710,       710,       710,       710,       710,       710,       710,       710]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [0, 20]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)

            # Metadata
            name_fmt = "{sample}_RTafterheating_{energy}eV_wa{wax}_sdd{sdd}m"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000
            sdd = pil2M_pos.z.position / 1000

            sample_name = name_fmt.format(
                sample=name,
                energy="%.1f" % e,
                sdd="%.1f" % sdd,
                wax=str(wa).zfill(4),
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)


def nexafs_cl(t=1):
    dets = [pil900KW]


    # energies = (np.arange(2800, 2820, 5).tolist()+ np.arange(2820, 2825, 1).tolist()+ np.arange(2825, 2831, 0.25).tolist() + np.arange(2831, 2840, 1).tolist()+ np.arange(2840, 2865, 5).tolist())

    energies = np.linspace(2800, 2850, 51)
    waxs_arc = [20]

    names = ["test"]

    for name in names:
        det_exposure_time(t, t)
        name_fmt = "nexafs_{sample}_{energy}eV_bpm{xbpm}"

        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(1)

            bpm = xbpm3.sumX.value
            sample_name = name_fmt.format(
                sample=name,
                energy="%6.2f" % e,
                xbpm="%4.3f" % bpm,
            )
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)

        yield from bps.mv(energy, 2825)
        yield from bps.mv(energy, 2800)



def waxs_nieves_2022_3(t=0.5):
    """
    GIWAXS macro for 309504 Gregory
    """
    user_name = "GF"

    names = ['s1_prisine_hspe', 's2_prisine_spe', 's3_latp_powder', 's4_pm_hspe_hd', 's5_pm_hspe_vd']
    x_piezo = [          40000,            32000,            20000,            5000,          -13000]
    y_piezo = [          -4700,            -4700,            -4500,           -4500,           -4500]
    z_piezo = [          11000,            11000,            11000,           11000,           11000]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [40]
    det_exposure_time(t, t)
    ypos = [-500, 500, 3]

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        dets = [pil2M]

        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)

            # Metadata
            name_fmt = "{sample}_countsaxs_{energy}eV_wa{wax}_sdd{sdd}m"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000
            sdd = pil2M_pos.z.position / 1000

            sample_name = name_fmt.format(
                sample=name,
                energy="%.1f" % e,
                sdd="%.1f" % sdd,
                wax=str(wa).zfill(4),
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=50)
            # yield from bp.rel_scan(dets, piezo.y, *ypos)




def waxs_agbh_2022_3(t=0.5):
    """
    GIWAXS macro for 309504 Gregory
    """
    user_name = "GF"

    names = ['AgBeh']
    x_piezo = [          -30500]
    y_piezo = [          -4500]
    z_piezo = [          10000]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [0, 2, 20, 22, 40]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)

            # Metadata
            name_fmt = "{sample}_{energy}eV_wa{wax}"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000

            sample_name = name_fmt.format(
                sample=name,
                energy="%.1f" % e,
                wax=str(wa).zfill(4),
            )
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

# CD GI saxs alignments
            # height with the hexapod
            # change phi, and check reflection is on the same pixel
            # change alpha of the hexapod, compensate for the sample to stay at the same 
            # final alignment with height
            # incident angles 0.05,.1,.15,.2
            # is wobble is a problem, do a step scan with short exposures
            


def fly_scan_cdgisaxs(det, motor, cycle=1, cycle_t=10, phi=-0.6):
    start = phi - 30
    stop = phi + 30
    acq_time = cycle * cycle_t
    yield from bps.mv(motor, start)

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


from bluesky.utils import short_uid
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

def rocking_scan(det, motor, cycle=1, cycle_t=10, phi=-0.6, half_delta=30, md=None):
    md = dict(md) if md is not None else {}
    md.update({'cycles': cycle, 'cycle_t': cycle_t, 'phi': phi, 'half_delta': half_delta})
    acq_time = cycle * cycle_t
    det.cam.acquire_time.put(acq_time)

    start = phi - half_delta
    stop = phi + half_delta

    @bpp.stage_decorator([det])
    @bpp.run_decorator(md=md)
    def inner():
        # name of the group we should wait for
        group=short_uid('reading')
        # trigger the detector
        st = yield from bps.trigger(det, group=group)
        # move the motor back and forth, cycle in the original was back and forth
        # except for the last one, this does N-1 cycles
        for i in range(cycle-1):
            yield from bps.mv(motor, stop)
            yield from bps.mv(motor, start)
        # and the last pass forward
        yield from bps.mv(motor, stop)

        # wait for the detector to really finish
        yield from bps.wait(group=group)
        # put the detector reading in the primary stream
        yield from bps.create(name='primary')
        yield from bps.read(det)
        yield from bps.save()

    yield from bps.mv(motor, start)
    return (yield from inner())





def S_edge_testissue(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['test_newsample_4']
    x_piezo = [42700]
    y_piezo =  [-10700]
    z_piezo = [7000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]

    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2475.0,2478.0,2479.0,2479.5,2480.0,2480.5,2481.0,2481.5,2482.0,2482.5,
    2483.0,2483.5,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0, 2490.0,2488.0,2492.5,2495.0,2500.0,2510.0,2515.0]



    waxs_arc = [20]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            counter = 0
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}"

            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(5)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ys + counter * 20)
                counter += 1
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies[::-1]:
                yield from bps.mv(energy, e)
                yield from bps.sleep(5)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ys + counter * 20)
                counter += 1

                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)





def S_edge_testissue(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    names = ['Mo_sheet_abs_settletime3s_redo']
    x_piezo = [4071]
    y_piezo =  [0]
    z_piezo = [7000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]

    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2475.0,2478.0,2479.0,2479.5,2480.0,2480.5,2481.0,2481.5,2482.0,2482.5,
    2483.0,2483.5,2484.0,2485.0,2486.0,2487.0,2488.0,2489.0, 2490.0,2488.0,2492.5,2495.0,2500.0,2510.0,2515.0]

    energies = np.linspace(2500, 2530, 31)

    waxs_arc = [20]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        # yield from bps.mv(piezo.x, xs)
        # yield from bps.mv(piezo.y, ys)
        # yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            # yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way

            counter = 0
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}"

            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                # yield from bps.mv(piezo.y, ys + counter * 20)
                counter += 1
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)



            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies[::-1]:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                # yield from bps.mv(piezo.y, ys + counter * 20)
                counter += 1

                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)





def Mo_Ledge_absorptiontest(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    names = ['Mo_sheet_abs_bsscan_test']
    x_piezo = [0]
    y_piezo =  [-8000]
    z_piezo = [7000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.linspace(2500, 2530, 31)
    list_ener = energies.tolist() + energies[::-1].tolist()
    yield from bp.list_scan([pil2M, energy], energy, list_ener)


def Sscan_fluotest(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['Sedge_sample1_0.8ai']
    # x_piezo = [0]
    # y_piezo =  [-8000]
    # z_piezo = [7000]

    # assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    # assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    # assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.arange(2450, 2470, 5).tolist()+ np.arange(2470, 2475, 1).tolist()+np.arange(2475, 2480, 0.5).tolist()+ np.arange(2480, 2490, 2).tolist()+ np.arange(2490, 2521, 5).tolist()

    list_ener = energies + energies[::-1]
    x_list = np.linspace(20000, 18109, 62).tolist()

    yield from bp.list_scan([pil900KW, energy, piezo, waxs], energy, list_ener, piezo.x, x_list)



def Mo_Kedge_absorption(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    names = ['Mo_Kedge_sheet_abs_1eVstep_redo3rd']
    x_piezo = [0]
    y_piezo =  [-8000]
    z_piezo = [7000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.linspace(19960, 19980, 21)

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        det_exposure_time(t, t)

        name_fmt = "{sample}_sweepup_{energy}eV_bpm{xbpm}"

        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
            if xbpm2.sumX.get() < 50:
                yield from bps.sleep(2)
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
            
            bpm = xbpm2.sumX.get()
            sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm="%4.3f"%bpm)
            sample_id(user_name="LR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            yield from bps.sleep(2)


        name_fmt = "{sample}_sweepdown_{energy}eV_bpm{xbpm}"
        for ee,e in enumerate(energies[::-1]):
            if ee == 0:
                yield from bps.mv(att1_4.open_cmd, 1)
                yield from bps.sleep(1)
                yield from bps.mv(att1_4.open_cmd, 1)


            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
            if xbpm2.sumX.get() < 50:
                yield from bps.sleep(2)
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)

            bpm = xbpm2.sumX.get()
            sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm="%4.3f"%bpm)
            sample_id(user_name="LR", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            yield from bps.sleep(2)

            if ee == 0:
                yield from bps.mv(att1_4.close_cmd, 1)
                yield from bps.sleep(1)
                yield from bps.mv(att1_4.close_cmd, 1)






def Mo_Kedge_absorptiontest(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    names = ['Mo_Kedge_sheet_abs_bsscan_updown2']
    x_piezo = [0]
    y_piezo =  [-8000]
    z_piezo = [7000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.linspace(19960, 19980, 21)
    list_ener = energies.tolist() + energies[::-1].tolist()
    yield from bp.list_scan([pil2M], energy, list_ener)




def giwaxs_amalie_2023_1(t=0.5):
    """
    GIWAXS macro for 14 keV for Amalie sample
    """
    user_name = "AA"

    names = [ 'LZ_0','LZ_5M','LZ_1H','LZ_3H','LZ_10H','HZ_01','HZ_02','HZ_03','HZ_04','HZ_05','HZ_06','HZ_07']
    x_piezo = [57000,  55000,  45000,  33000,   22000,   9000,      0, -12000, -23000, -35000, -46000, -50000]
    y_piezo = [ 5000,   5000,   5000,   5000,    5000,   5000,   5000,   5000,   5000,   5000,   5000,   5000]
    z_piezo = [ 7000,   7000,   7000,   7000,    7000,   7000,   7000,   7000,   7000,   7000,   7000,   7000]
    x_hexa =  [  15,       4,      0,      0,       0,      0,      0,      0,      0,      0,      0,    -10]

    # names = ['HZ_08','HZ_09','HZ_10','HZ_11', 'HZ_12','HZ_13','HZ_14','HZ_15','HZ_16','HZ_17','HZ_18']
    # x_piezo = [57000,  57000,  44000,  33000,   22000,  11000,  -1000, -15000, -28000, -41000, -50000]
    # y_piezo = [ 5000,   5000,   5000,   5000,    5000,   5000,   5000,   5000,   5000,   5000,   5000]
    # z_piezo = [ 7000,   7000,   7000,   7000,    7000,   7000,   7000,   7000,   7000,   7000,   7000]
    # x_hexa =  [  14,       0,      0,      0,       0,      0,      0,      0,      0,      0,    -10]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_angles = [0, 2, 20, 22]
    inc_angles = [0.15, 0.20]
    det_exposure_time(t, t)

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, 0.5)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        det_exposure_time(t, t)
        for wa in waxs_angles:
            yield from bps.mv(waxs, wa)
            yield from bps.sleep(2)
            if abs(waxs.arc.position - wa)>1:
                yield from bps.sleep(20)
                yield from bps.mv(waxs, wa)

            dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]

            for i, ai in enumerate(inc_angles):
                yield from bps.mv(piezo.x, xs+500*i)
                yield from bps.mv(piezo.th, ai0 + ai)

                name_fmt = "{sample}_redo_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}_ai{ai}"
                
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa, 
                                              xbpm="%4.3f"%bpm, ai="%.2f"%ai)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)



def Cl_edge_amalie_2023_1_night3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [ 'hT_N','mT_N','hTe_N','mTe_N','hB_N', 'mB_N', 'Co_N','hT_25', 'mT_25', 'hTe_25', 'mTe_25', 'hB_25', 'mB_25', 'Co_25_redo' ]
    x_piezo = [57000, 57000,  53000,  42000, 32000,  22000,  11000,   1000,  -10000,   -20000,   -30000,  -41000,  -53000,   -53000]
    x_hexa = [    17,     6,      0,      0,     0,      0,      0,      0,       0,        0,        0,       0,       0,      -10]
    y_piezo = [ 5271,  5271,   5271,   5271,  5271,   5271,   5271,   5271,    5271,     5271,     5271,    5271,    5271,     5271]
    z_piezo = [ 7000,  7000,   7000,   7000,  7000,   7000,   7000,   7000,    7000,     7000,     7000,    7000,    7000,     7000]
    
    # x_piezo = -500 + np.asarray(x_piezo)


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = (np.arange(2800, 2818, 5).tolist()+ np.arange(2818, 2822, 1).tolist()+ np.arange(2822, 2833, 0.5).tolist()+ np.arange(2833, 2840, 1).tolist()+ np.arange(2840, 2860, 10).tolist())

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names[::-1], x_piezo[::-1], y_piezo[::-1], z_piezo[::-1], x_hexa[::-1]):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 40)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2840)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2820)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2800)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)



def S_edge_amalie_2023_1_night3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [ 'hT_N','mT_N','hTe_N','mTe_N','hB_N', 'mB_N', 'Co_N','hT_25', 'mT_25', 'hTe_25', 'mTe_25', 'hB_25', 'mB_25', 'Co_25' ]
    x_piezo = [57000, 57000,  53000,  42000, 32000,  22000,  11000,   1000,  -10000,   -20000,   -30000,  -41000,  -53000,   -53000]
    x_hexa = [    17,     6,      0,      0,     0,      0,      0,      0,       0,        0,        0,       0,       0,      -10]
    y_piezo = [ 5271,  5271,   5271,   5271,  5271,   5271,   5271,   5271,    5271,     5271,     5271,    5271,    5271,     5271]
    z_piezo = [ 7000,  7000,   7000,   7000,  7000,   7000,   7000,   7000,    7000,     7000,     7000,    7000,    7000,     7000]
    
    x_piezo = -1800 + np.asarray(x_piezo)


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(2445, 2470, 5).tolist() + np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()+ np.arange(2490, 2501, 5).tolist()

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 40)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2480)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2450)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2430)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)

def night_amalie_2023_1(t=1):

    proposal_id("2023_1", "000000_Freychet3")
    yield from Cl_edge_amalie_2023_1_night3(t=1)
    
    yield from transition_Cl_S_edges()

    proposal_id("2023_1", "000000_Freychet4")
    yield from S_edge_amalie_2023_1_night3(t=1)



def gisaxs_guillaume_2023_1(t=0.5):
    """
    GISAXS macro for 14 keV for Amalie sample
    """
    user_name = "GF"

    # names = [ 'sample01','sample02','sample03','sample04','sample05','sample06','sample07']
    # x_piezo = [    57000,     49000,     30000,      7000,    -13000,    -33000,    -45000]
    # y_piezo = [     5000,      5000,      5000,      5000,      5000,      5000,      5000]
    # z_piezo = [     7000,      7000,      7000,      7000,      7000,      7000,      7000]
    # x_hexa =  [       12,         0,         0,         0,         0,         0,       -10]


    names = [ 'sample08','sample09','sample10','sample11','sample12']
    x_piezo = [    57000,     47000,     26000,      5000,    -16000]
    y_piezo = [     5000,      5000,      5000,      5000,      5000]
    z_piezo = [     7000,      7000,      7000,      7000,      7000]
    x_hexa =  [       12,         0,         0,         0,         0]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_angles = [20]
    inc_angles = [0.15, 0.20, 0.3, 0.5]

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, -1)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        det_exposure_time(t, t)
        for wa in waxs_angles:
            yield from bps.mv(waxs, wa)

            dets =[pil2M]

            for i, ai in enumerate(inc_angles):
                yield from bps.mv(piezo.x, xs-500*i)
                yield from bps.mv(piezo.th, ai0 + ai)
                yield from bps.sleep(20)

                
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                name_fmt = "{sample}_pos1_redo_{energy}eV_wa{wax}_sdd{sdd}m_ai{ai}"
                sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa, ai="%.2f"%ai)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

                yield from bps.mv(piezo.x, xs-500*i-2000)
                name_fmt = "{sample}_pos2_redo_{energy}eV_wa{wax}_sdd{sdd}m_ai{ai}"
                sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa, ai="%.2f"%ai)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

                yield from bps.mv(piezo.x, xs-500*i-4000)
                name_fmt = "{sample}_pos3_redo_{energy}eV_wa{wax}_sdd{sdd}m_ai{ai}"
                sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa, ai="%.2f"%ai)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)




def giwaxs_guillaume_2023_1(t=0.5):
    """
    GISAXS macro for 14 keV for Amalie sample
    """
    user_name = "GF"

    names = [ 'giwaxssa01','giwaxssa02','giwaxssa03','giwaxssa04','giwaxssa05']
    x_piezo = [      55000,       42000,       25000,        7000,      -10000]
    y_piezo = [       5000,        5000,        5000,        5000,        5000]
    z_piezo = [       7000,        7000,        7000,        7000,        7000]
    x_hexa =  [         10,          10,          10,          10,          10]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_angles = [0, 2, 20, 22]
    inc_angles = [0.15, 0.20, 0.3]

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, -1)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        det_exposure_time(t, t)
        for wa in waxs_angles:
            yield from bps.mv(waxs, wa)

            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            for i, ai in enumerate(inc_angles):
                yield from bps.mv(piezo.x, xs-500*i)
                yield from bps.mv(piezo.th, ai0 + ai)
                yield from bps.sleep(20)

                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                name_fmt = "{sample}_ai{ai}_{energy}eV_wa{wax}_sdd{sdd}m"
                sample_name = name_fmt.format(sample=name, ai="%.2f"%ai, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)



def giwaxs_song_2023_1(t=0.5):
    """
    GISAXS macro for 14 keV for Amalie sample
    """
    user_name = "GF"

    # names = [   'A1_perp_',   'B1_perp',   'C1_perp',   'D1_perp']
    # x_piezo = [     -12500,      -27000,      -37000,      -47000]
    # y_piezo = [       5000,        5000,        5000,        5000]
    # z_piezo = [       7000,        7000,        7000,        7000]
    # x_hexa =  [          0,           0,           0,           0]

    # names = [  'A5_perp_', 'B1_perp', 'B2_perp', 'B3_perp', 'B4_perp', 'B5_perp', 'A1_par_', 'A2_par_', 'A3_par_', 'A4_par_']
    # x_piezo = [     55000,     48000,     46000,     36000,    23000,      10000,     -6000,    -16000,    -32000,    -45500]
    # y_piezo = [      5000,      5000,      5000,      5000,      5000,      5000,      5000,      5000,      5000,      5000]
    # z_piezo = [      7000,      7000,      7000,      7000,      7000,      7000,      7000,      7000,      7000,      7000]
    # x_hexa =  [        12,        12,         0,         0,         0,         0,         0,         0,         0,         0]

    names = [  'A5_par_', 'B1_par', 'B2_par', 'B3_par', 'B4_par', 'B5_par']
    x_piezo = [    55500,    55000,    42000,    25000,    11000,    -3000]
    y_piezo = [     5000,     5000,     5000,     5000,     5000,     5000]
    z_piezo = [     7000,     7000,     7000,     7000,     7000,     7000]
    x_hexa =  [       15,        3,        0,        0,        0,        0]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_angles = [0, 20]
    inc_angles = [0.10, 0.15]

    for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, -1)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        det_exposure_time(t, t)
        for wa in waxs_angles:
            yield from bps.mv(waxs, wa)

            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            for i, ai in enumerate(inc_angles):
                yield from bps.mv(piezo.th, ai0 + ai)
                yield from bps.sleep(20)

                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000

                yield from bps.mv(piezo.x, xs-500*i)
                name_fmt = "{sample}_pos1_ai{ai}_{energy}eV_wa{wax}_sdd{sdd}m"
                sample_name = name_fmt.format(sample=name, ai="%.2f"%ai, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

                yield from bps.mv(piezo.x, xs-500)
                name_fmt = "{sample}_pos2_ai{ai}_{energy}eV_wa{wax}_sdd{sdd}m"
                sample_name = name_fmt.format(sample=name, ai="%.2f"%ai, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

                yield from bps.mv(piezo.x, xs-1000)
                name_fmt = "{sample}_pos3_ai{ai}_{energy}eV_wa{wax}_sdd{sdd}m"
                sample_name = name_fmt.format(sample=name, ai="%.2f"%ai, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f"%wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)


def jour_guillaume_2023_1(t=1):

    proposal_id("2023_1", "311003_Freychet6")
    yield from giwaxs_guillaume_2023_1(t=1)
    
    proposal_id("2023_1", "311003_Freychet7")
    yield from giwaxs_song_2023_1(t=1)



def waxs_fleury_2023_1(t=0.5):
    user_name = "GF"

    names = ['K-140C', 'Tri-140C', 'YM10', 'YM10_heat']
    x_piezo = [ -8100,       4400,  17200,       29900]
    y_piezo = [ -7400,      -7600,  -7400,       -7400]
    z_piezo = [  7000,       7000,   7000,        7000]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [0, 20]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)

            # Metadata
            name_fmt = "{sample}_RTafterheating_pos1_{energy}eV_wa{wax}_sdd{sdd}m"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000
            sdd = pil2M_pos.z.position / 1000
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_140C_pos2_{energy}eV_wa{wax}_sdd{sdd}m"
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name) 
            yield from bps.mv(piezo.y, ys+200)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_140C_pos3_{energy}eV_wa{wax}_sdd{sdd}m"
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            yield from bps.mv(piezo.y, ys+400)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)




def waxs_Amnahir_2023_1(t=0.5):
    user_name = "AP"

    names = [  'sa2', 'sa1', 'sa3', 'sa4', 'sa5', 'sa6', 'sa7', 'sa8', 'sa9']
    x_piezo = [45500, 40000, 32500, 22500, 15500,  7500, -3500,-12500,-23500]
    y_piezo = [-3500, -3500, -3500, -3500, -3500, -3500, -3500, -3500, -3500]
    z_piezo = [ 7000,  7000,  7000,  7000,  7000,  7000,  7000,  7000,  7000]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [0, 20]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)

            # Metadata
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_sdd{sdd}m"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000
            sdd = pil2M_pos.z.position / 1000
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_sdd{sdd}m"
            yield from bps.mv(piezo.y, ys-500)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_pos3_{energy}eV_wa{wax}_sdd{sdd}m"
            yield from bps.mv(piezo.y, ys+500)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

    

def waxs_safelymove_2023_1(t=0.5):
    user_name = "GF"

    # names = ['LI2HSPELi_CD0.75', 'LI2HSPELi_C0.1', 'LISPELi_C0.1', 'LI2HSPELi_CD0.1', 'LISPELi_CD0.1']
    # x_piezo = [           47000,            40000,          32500,             24000,           16000]
    # y_piezo = [           -7000,            -7000,          -7000,             -7000,           -7000]
    # z_piezo = [            9000,             9000,           9000,              9000,            9000]

    # names = ['cellop_0.5_1', 'cellop_0.5_2', 'freshcell']
    # x_piezo = [        2300,         -19400,      -39300]
    # y_piezo = [       -7200,          -6600,       -7400]
    # z_piezo = [        9000,           9000,        9000]

    names = ['freshcell_redo']
    x_piezo = [-39000]
    y_piezo = [ -7300]
    z_piezo = [  9000]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [0, 2, 20, 22]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys-200)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)

            # Metadata
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_sdd{sdd}m"
            bpm = xbpm3.sumX.get()
            e = energy.energy.position / 1000
            sdd = pil2M_pos.z.position / 1000
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            # Take data
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_sdd{sdd}m"
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            yield from bps.mv(piezo.y, ys)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)

            name_fmt = "{sample}_pos3_{energy}eV_wa{wax}_sdd{sdd}m"
            sample_name = name_fmt.format(sample=name, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
            sample_id(user_name=user_name, sample_name=sample_name)
            yield from bps.mv(piezo.y, ys+200)
            yield from bps.sleep(2)
            yield from bp.count(dets, num=1)



def swaxs_Ptedge_2023_1(t=0.5):
    user_name = "PT"

    names = [  'sampleA', 'sampleB', 'capillaries']
    x_piezo = [    24400,      5000,        -20800]
    y_piezo = [    -5000,     -5000,         -5000]
    z_piezo = [     6500,      6500,          6500]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [20, 0]
    det_exposure_time(t, t)

    energies = np.asarray([11320, 11398, 11476, 11504, 11532, 11537, 11542, 11547, 11552, 11555, 11557, 11559,
                           11561, 11563, 11565, 11567, 11569, 11571, 11575, 11580, 11590, 11600, 11650 ])

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if wa < 15 else [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)
            
            name_fmt = "{sample}_pos{pos}_{energy}eV_wa{wax}_sdd{sdd}m_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(5)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000
                sample_name = name_fmt.format(sample=name, pos="%.1d"%1, energy="%.3f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa, xbpm="%4.3f"%bpm)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bps.sleep(5)
                yield from bp.count(dets, num=1)

                sample_name = name_fmt.format(sample=name, pos="%.1d"%2, energy="%.3f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa, xbpm="%4.3f"%bpm)
                sample_id(user_name=user_name, sample_name=sample_name)
                yield from bps.mv(piezo.y, ys+250)
                yield from bps.sleep(5)
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

                sample_name = name_fmt.format(sample=name, pos="%.1d"%3, energy="%.3f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa, xbpm="%4.3f"%bpm)
                sample_id(user_name=user_name, sample_name=sample_name)
                yield from bps.mv(piezo.y, ys+500)
                yield from bps.sleep(5)
                yield from bp.count(dets, num=1)
                yield from bps.sleep(2)

            yield from bps.mv(energy, 11600)
            yield from bps.sleep(5)
            yield from bps.mv(energy, 11500)
            yield from bps.sleep(5)            
            yield from bps.mv(energy, 11400)
            yield from bps.sleep(5)            
            yield from bps.mv(energy, 11320)
            yield from bps.sleep(5)



def swaxs_Ptedge_severalposition_2023_1(t=0.5):
    user_name = "PT"

    names = [  'sampleA', 'sampleB']
    x_piezo = [   -20500,     -1500]
    y_piezo = [    -7100,     -7100]
    z_piezo = [     6500,      6500]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [20]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)


            for k in range(0, 20, 1):
                yield from bps.mv(piezo.y, ys+ k*200)

                # Metadata
                name_fmt = "{sample}severalpos_pos{pos}_{energy}eV_wa{wax}_sdd{sdd}m"
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000
                sample_name = name_fmt.format(sample=name, pos='%.2d'%k, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # Take data
                yield from bps.sleep(2)
                yield from bp.count(dets, num=1)



def swaxs_Ptedge_damagetest_2023_1(t=0.5):
    user_name = "PT"

    names = [  'sampleA', 'sampleB']
    x_piezo = [   -20500,     -1500]
    y_piezo = [    -7100,     -7100]
    z_piezo = [     6500,      6500]

    # Checks
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    # Geometry conditions
    waxs_angles = [20]
    det_exposure_time(t, t)

    # Go over WAXS detector angles
    for wa in waxs_angles:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW, pil2M]
        
        # Go over samples and thier positions
        for name, xs, zs, ys in zip(names, x_piezo, z_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)
            yield from bps.sleep(20)


            for k in range(0, 20, 1):
                yield from bps.mv(piezo.y, ys+ k*200)

                # Metadata
                name_fmt = "{sample}severalpos_pos{pos}_{energy}eV_wa{wax}_sdd{sdd}m"
                bpm = xbpm3.sumX.get()
                e = energy.energy.position / 1000
                sdd = pil2M_pos.z.position / 1000
                sample_name = name_fmt.format(sample=name, pos='%.2d'%k, energy="%.1f"%e, sdd="%.1f"%sdd, wax="%.1f" %wa)
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # Take data
                yield from bps.sleep(2)
                yield from bp.count(dets, num=1)


def Pt_edge_nexafs_2023_1(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = ['nexafsrough_sampleB']
    x_piezo = [-1500]
    y_piezo = [-7100]
    z_piezo = [6500]
    
    energies = np.linspace(11540, 11580, 41)
    waxs_arc = [20]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW]

            name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)



def S_edge_song_2023_1(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    # names = [  'A5_par_', 'B1_par', 'B2_par', 'B3_par', 'B4_par', 'B5_par', 'A1_par_', 'A2_par_', 'A3_par_', 'A4_par_']
    # x_piezo = [    55500,    55000,    42000,    26000,    11000,    -2700,    -19000,    -29000,    -44000,    -50000]
    # y_piezo = [     5000,     5000,     5000,     5000,     5000,     5000,      5000,      5000,      5000,      5000]
    # z_piezo = [     7000,     7000,     7000,     7000,     7000,     7000,      7000,      7000,      7000,      7000]
    # x_hexa =  [       15,        3,        0,        0,        0,        0,         0,         0,         0,        -9]

    names = [  'A5_per', 'B1_per', 'B2_per', 'B3_per', 'B4_per', 'B5_per', 'A1_per', 'A2_per', 'A3_per', 'A4_per']
    x_piezo = [   51000,    54500,    45000,    33000,    20000,     8500,    -9500,   -21000,   -31000,   -47000]
    y_piezo = [    5000,     5000,     5000,     5000,     5000,     5000,     5000,     5000,     5000,     5000]
    z_piezo = [    7000,     7000,     7000,     7000,     7000,     7000,     7000,     7000,     7000,     7000]
    x_hexa =  [      15,        4,        0,        0,        0,        0,        0,        0,        0,        0]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(2450, 2470, 5).tolist()+ np.arange(2470, 2475, 1).tolist()+np.arange(2475, 2480, 0.5).tolist()+ np.arange(2480, 2490, 2).tolist()+ np.arange(2490, 2521, 5).tolist()

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 40)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                yield from bps.mv(energy, 2490)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2460)
                yield from bps.sleep(2)
                yield from bps.mv(energy, 2430)
                yield from bps.sleep(2)

            yield from bps.mv(piezo.th, ai0)



def S_edge_Amnahair_2023_1(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    user_name = "AP"

    names = [  'sa2', 'sa1', 'sa3', 'sa4', 'sa5', 'sa6', 'sa7', 'sa8', 'sa9']
    x_piezo = [45500, 40500, 33000, 21500, 14700,  6300, -3500,-12500,-23500]
    y_piezo = [-3800, -3600, -3900, -4000, -3500, -4000, -4000, -4000, -4000]
    z_piezo = [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000,10000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.arange(2450, 2470, 5).tolist()+ np.arange(2470, 2475, 1).tolist()+np.arange(2475, 2480, 0.5).tolist()+ np.arange(2480, 2490, 2).tolist()+ np.arange(2490, 2521, 5).tolist()

    waxs_arc = [0, 20]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yss = np.linspace(ys, ys + 500, 31)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()


        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2490)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2460)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2430)
            yield from bps.sleep(2)



def Co_edge_nexafs_2023_1(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['nexafs_w01', 'nexafs_w04', 'nexafs_w08']
    x_piezo = [     50000,        30000,        10000]
    y_piezo = [      5072,         5072,         5072]
    z_piezo = [      7000,         7000,         7000]
    
    # energies = np.linspace(7690, 7730, 41)
    energies = (np.arange(7700, 7710, 5).tolist() + np.arange(7710, 7722, 1).tolist() + np.arange(7722, 7727, 0.5).tolist()
    + np.arange(7727, 7740, 1).tolist() + np.arange(7740, 7765, 5).tolist())

    waxs_arc = [20]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, 0)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_gisaxs(angle=0.15)
        ai0 = piezo.th.position

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        yield from bps.mv(piezo.th, ai0+0.8)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW]

            name_fmt = "{sample}_ai0.8deg_{energy}eV_wa{wax}_bpm{xbpm}"
            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)




from bluesky.utils import short_uid
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

def rocking_scan(det, motor, cycle=1, cycle_t=10, phi=-0.6, half_delta=30, md=None):
    md = dict(md) if md is not None else {}
    md.update({'cycles': cycle, 'cycle_t': cycle_t, 'phi': phi, 'half_delta': half_delta})
    acq_time = cycle * cycle_t
    det.cam.acquire_time.put(acq_time)

    start = phi - half_delta
    stop = phi + half_delta

    @bpp.stage_decorator([det])
    @bpp.run_decorator(md=md)
    def inner():
        # name of the group we should wait for
        group=short_uid('reading')
        # trigger the detector
        st = yield from bps.trigger(det, group=group)
        # move the motor back and forth, cycle in the original was back and forth
        # except for the last one, this does N-1 cycles
        for i in range(cycle-1):
            yield from bps.mv(motor, stop)
            yield from bps.mv(motor, start)
        # and the last pass forward
        yield from bps.mv(motor, stop)

        # wait for the detector to really finish
        yield from bps.wait(group=group)
        # put the detector reading in the primary stream
        yield from bps.create(name='primary')
        yield from bps.read(det)
        yield from bps.save()

    yield from bps.mv(motor, start)
    return (yield from inner())


def several_rockingscan():

    ai0 = piezo.th.position
    ais = [0.3, 0.5]
    energies = [7700, 7715, 7723, 7725, 7727, 7740]

    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)

        for ai in ais:
            yield from bps.mv(piezo.th, ai0+ai)
            yield from bps.sleep(2)

            bpm = xbpm2.sumX.get()
            name_fmt = "sample2_cdgisaxs_ai{ai}deg_{energy}eV_bpm{xbpm}_prs-3030_8.3m"
            sample_name = name_fmt.format(sample='GF', ai="%.1f"%ai, energy="%6.2f"%e, xbpm="%4.3f"%bpm)
            sample_id(user_name="GF", sample_name=sample_name)

            for i in range(3):
                yield from rocking_scan(pil2M, motor=prs, cycle=1, cycle_t=10, phi=-4.9790, half_delta=30)
                yield from bps.sleep(10)



def several_count():

    ai0 = piezo.th.position
    ais = [0.2, 0.3, 0.5, 0.7]
    energies = [7700, 7715, 7723, 7725, 7727, 7740]

    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)

        for ai in ais:
            yield from bps.mv(piezo.th, ai0+ai)
            yield from bps.sleep(10)

            bpm = xbpm2.sumX.get()
            name_fmt = "sample2_gisaxs_phi0deg_ai{ai}deg_{energy}eV_bpm{xbpm}_8.3m"
            sample_name = name_fmt.format(sample='GF', ai="%.1f"%ai, energy="%6.2f"%e, xbpm="%4.3f"%bpm)
            sample_id(user_name="GF", sample_name=sample_name)

            yield from bp.count([pil2M], num=3)


def cd_saxs_Coedge(t=5):
    det_exposure_time(t, t)

    energies = [7700, 7715, 7723, 7725, 7727, 7740]

    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)

        for num, prss in enumerate(np.linspace(-50, 50, 51)):
            yield from bps.mv(prs, prss)
            yield from bps.sleep(5)

            bpm = xbpm2.sumX.get()
            name_fmt = "cdsaxs_{num}_phi{phi}deg_{energy}eV_bpm{xbpm}_8.3m"
            sample_name = name_fmt.format(sample='GF', num="%.3d"%num, phi="%.1f"%prss, energy="%6.2f"%e, xbpm="%4.3f"%bpm)
            sample_id(user_name="GF", sample_name=sample_name)

            yield from bp.count([pil2M], num=1)




def polefigure_14keV(t=5):
    det_exposure_time(t, t)

    names = ['recuit1', 'recuit2']
    x_piezo = [  27500,     -6000]


    names = ['recuit2']
    x_piezo = [  -6000]

    waxs_arc = [0, 20]

    for name, xs in zip(names, x_piezo):
        yield from bps.mv(prs, 0)
        yield from bps.mv(piezo.x, xs)


        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_gisaxs_hex(angle=0.15)
        ai0 = stage.th.position
        yield from bps.mv(stage.th, ai0+0.2)


        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            for num, prss in enumerate(np.linspace(-90, 90, 181)):
                yield from bps.mv(prs, prss)
                yield from bps.sleep(5)
                
                name_fmt = "recuit1_{num}_ai0.2deg_phi{phi}deg_{energy}eV_wa{wa}"
                sample_name = name_fmt.format(sample='GF', num="%.3d"%num, phi="%.1f"%prss, energy="%.1f"%14, wa="%.1f"%wa)
                sample_id(user_name="GF", sample_name=sample_name)

                yield from bp.count([pil900KW], num=1)

        yield from bps.mv(stage.th, ai0)



def julie_gisaxs_temperature_scan_2023_2(t=0.5):
    """
    Grazing incidence measurement using Lakeshore controlled heating bar
    """

    proposal_id('2023_2', '311003_Freychet_01', analysis=True)

    temperatures = [185]


    names   = ['cube50','cube28-1','cube28-1']
    piezo_x = [  -15000,     -1400,      8400]
    piezo_y = [    4377,      4200,      3900]
    piezo_z = [    1000,      1000,      1000]


    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_y) == len(piezo_z), msg

    incident_angles = [0.2]
    waxs_range = [20]
    user_name = "JG"
    det_exposure_time(t, t)

    dets = [pil900KW, pil2M]

    #loop for alignement
    piezo_th = [0.766706, 0.265281, 0.26577]
    piezo_y_al = [4377.597, 4066.471, 3805.02]

    print(piezo_th)
    print(piezo_y_al)

    t0 = time.time()
    t1 = time.time()
    
    while t1-t0<15000:
        for name, x, y, z, th in zip(names, piezo_x, piezo_y_al, piezo_z, piezo_th):
            yield from bps.mv(waxs, waxs_range[0])

            yield from bps.mv(piezo.x, x,
                            piezo.y, y,
                            piezo.z, z, 
                            piezo.th, th + incident_angles[0])

            tim='%.5d'%(t1-t0)
            sample_name = f'{name}_{tim}s_185degC{get_scan_md()}'
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)
        
        t1 = time.time()


    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)

    # Turn off the heating and set temperature to 23 deg C
    t_kelvin = 23 + 273.15
    yield from ls.output1.mv_temp(t_kelvin)
    yield from ls.output1.turn_off()



def julie_gisaxs_2023_2(t=0.5):
    """
    Grazing incidence measurement using Lakeshore controlled heating bar
    """

    proposal_id('2023_2', '311003_Freychet_01', analysis=True)

    names   = ['cube50','cube28-1','cube28-1']
    piezo_x = [  -15000,     -1400,      8400]
    piezo_y = [    4431,      4200,      3900]
    piezo_z = [    1000,      1000,      1000]

    incident_angles = [0.2]
    waxs_range = [20]
    user_name = "JG"
    det_exposure_time(t, t)

    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_y) == len(piezo_z), msg

    dets = [pil900KW, pil2M]

    #loop for alignement
    piezo_th = [0.766706, 0.265281, 0.26577]
    piezo_y_al = [4437.597, 4066.471, 3805.02]

    yield from bps.mv(waxs, waxs_range[0])

    for name, x, y, z, th in zip(names, piezo_x, piezo_y_al, piezo_z, piezo_th):
        yield from bps.mv(piezo.x, x,
                        piezo.y, y,
                        piezo.z, z, 
                        piezo.th, th + incident_angles[0])

        sample_name = f'{name}_100C_{get_scan_md()}'
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)
        

# proposal_id('2023_2', '311003_Freychet_02')


def giwaxs_mcneil_2023_2(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    # names = [  'DH01', 'DH02', 'DH03', 'DH04', 'DH05', 'DH06', 'DH07', 'DH08', 'DH09']
    # x_piezo = [ -50000, 45000, -29000, -13000,   2000,  18000,  33000,  50000,  55000]
    # y_piezo = [   5300,  5300,   5300,   5300,   5300,   5300,   5300,   5300,   5300]
    # z_piezo = [   7000,  7000,   7000,   7000,   7000,   7000,   7000,   7000,   7000]
    # x_hexa =  [    -10,     0,      0,      0,      0,      0,      0,      0,     12]

    # names = [   'DH10', 'DH11', 'DH12', 'DH13', 'DH14', 'DH15', 'DH16', 'DH17', 'DH18', 'DH19']
    # x_piezo = [ -50000, -48000, -31000, -16000,      0,  15000,  30000,  45000,  55000,  58000]
    # y_piezo = [   5300,   5300,   5300,   5300,   5300,   5300,   5300,   5300,   5300,   5300]
    # z_piezo = [   7000,   7000,   7000,   7000,   7000,   7000,   7000,   7000,   7000,   7000]
    # x_hexa =  [    -13,      0,      0,      0,      0,      0,      0,      0,      5,     17]

    # names = [   'WZ04_per', 'WZ03_per', 'WZ02_per', 'WZ01_per', 'DH02', 'DH22', 'DH21',  'DH20']
    # x_piezo = [     -50000,     -35000,     -16000,       5000,  21000,  37000,  54000,   54000]
    # y_piezo = [       5300,       5300,       5300,       5300,   5300,   5300,   5300,    5300]
    # z_piezo = [       7000,       7000,       7000,       7000,   7000,   7000,   7000,    7000]
    # x_hexa =  [         -4,          0,          0,          0,      0,      0,      0,      15]

    # names = ['WZ04_par', 'WZ03_par', 'WZ02_par', 'WZ01_par']
    # x_piezo = [  -24000,      -2000,      23000,      47000]
    # y_piezo = [    5300,       5300,       5300,       5300]
    # z_piezo = [    7000,       7000,       7000,       7000]
    # x_hexa =  [       0,          0,          0,          0]

    names = [  'DH02', 'DH06', 'DH12', 'DH13']
    x_piezo = [-50000, -45000, -30000, -14000]
    y_piezo = [  5300,   5300,   5300,   5300]
    z_piezo = [  7000,   7000,   7000,   7000]
    x_hexa =  [   -10,      0,      0,      0]

    names = [  'DH12', 'DH13']
    x_piezo = [ -30000, -14000]
    y_piezo = [    5300,   5300]
    z_piezo = [   7000,   7000]
    x_hexa =  [      0,      0]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 2, 20, 22]
    ai0 = 0
    ai_list = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.15, 0.20]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.12)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for k, ais in enumerate(ai_list):
            yield from bps.mv(piezo.th, ai0 + ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                name_fmt = "{sample}_ai{ai}_wa{wax}"
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=wa)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)


    
def giwaxs_pauldumas_sophieguillemin_2023_2(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = ['echpaul_02', 'echpaul_03', 'echpaul_04', 'echpaul_05', 'echpaul_06', 'echsoph_E', 'echsoph_F', 'echpaul_01']
    x_piezo = [    -45000,       -35000,       -23000,       -14000,        -3000,       13000,       33000,        49000]
    y_piezo = [      4900,         4900,         4900,         4900,         4900,         4900,        4900,        4900]
    z_piezo = [      3000,         3000,         3000,         3000,         3000,         3000,        3000,        3000]
    x_hexa =  [         0,            0,            0,            0,            0,            0,           0,           0]

    names = ['echpaul_03', 'echpaul_04', 'echpaul_05', 'echpaul_06', 'echsoph_E', 'echsoph_F', 'echpaul_01']
    x_piezo = [    -35000,       -23000,       -14000,        -3000,       13000,       33000,        49000]
    y_piezo = [      4900,         4900,         4900,         4900,         4900,        4900,        4900]
    z_piezo = [      3000,         3000,         3000,         3000,         3000,        3000,        3000]
    x_hexa =  [         0,            0,            0,            0,            0,           0,           0]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.2]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_hex(angle=0.15)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)
        yield from bps.mv(stage.th, ai0+ai_list[0])

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            for k, prss in enumerate(np.linspace(-60, 60, 121)):
                yield from bps.mv(prs, prss)

                name_fmt = "{sample}_prs{prs}_wa{wax}"
                sample_name = name_fmt.format(sample=name, prs="%.2d"%prss, wax=wa)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)




def Cl_edge_Fleury_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    # names = ['CTFE4_RT','CTFE7_RT','CTFE8_RT','CTFE10_RT','CTFE7_55-1h','CTFE7_105-1h','CTFE4_100-1h','CTFE8_100-1h','CTFE10_100-1h']
    # x_piezo = [  -50000,    -45000,    -24000,      -3000,        17000,         34000,         47000,         53000,          53000]
    # x_hexa = [      -15,         0,         0,          0,            0,             0,             0,             5,             18]
    # y_piezo = [    5000,      5000,      5000,       5000,         5000,          5000,          5000,          5000,           5000]
    # z_piezo = [    7000,      7000,      7000,       7000,         7000,          7000,          7000,          7000,           7000]
    


    names = ['CTFE7_RT','CTFE8_RT','CTFE10_RT','CTFE7_55-1h','CTFE7_105-1h','CTFE4_100-1h','CTFE8_100-1h','CTFE10_100-1h']
    x_piezo = [  -45000,    -24000,      -3000,        17000,         34000,         47000,         53000,          53000]
    x_hexa = [        0,         0,          0,            0,             0,             0,             5,             18]
    y_piezo = [    5000,      5000,       5000,         5000,          5000,          5000,          5000,           5000]
    z_piezo = [    7000,      7000,       7000,         7000,          7000,          7000,          7000,           7000]
    

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = (np.arange(2800, 2818, 5).tolist()+ np.arange(2818, 2822, 1).tolist()+ np.arange(2822, 2833, 0.5).tolist()+ np.arange(2833, 2840, 1).tolist()+ np.arange(2840, 2860, 10).tolist())

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.8)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_ai{ai}_wa{wax}"
                sample_name = name_fmt.format(sample=name, ai=0.8, wax=wa)
                sample_id(user_name="GF", sample_name=sample_name)

                list_ener = energies + energies[::-1]
                x_list = np.linspace(xs, xs+3000, 78).tolist()

                yield from bp.list_scan(dets+[energy, piezo, waxs, xbpm2, xbpm3], energy, list_ener, piezo.x, x_list)

            yield from bps.mv(piezo.th, ai0)



def giwaxs_Fleury_2023_2(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = ['CTFE7_RT','CTFE8_RT','CTFE10_RT','CTFE7_55-1h','CTFE7_105-1h','CTFE4_100-1h','CTFE8_100-1h','CTFE10_100-1h']
    x_piezo = [  -45000,    -24000,      -3000,        17000,         34000,         47000,         53000,          53000]
    x_hexa = [        0,         0,          0,            0,             0,             0,             5,             18]
    y_piezo = [    5000,      5000,       5000,         5000,          5000,          5000,          5000,           5000]
    z_piezo = [    7000,      7000,       7000,         7000,          7000,          7000,          7000,           7000]
    

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.12]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.12)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_ai{ai}_wa{wax}"
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=wa)
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)




def giwaxs_amalie_2023_2(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = ['sam_0A','sam_0B','sam_1','sam_3','sam_5A','sam_5B','sam_5C','sam_7','sam_10A','sam_10B']
    x_piezo = [ -2000,    6000,  14000,  23000,   33000,   42000,   52000,  57000,  57000,    57000,]
    y_piezo = [  5300,    5300,   5300,   5300,    5300,    5300,    5300,   5300,   5300,     5300,]
    z_piezo = [  7000,    7000,   7000,   7000,    7000,    7000,    7000,   7000,   7000,     7000,]
    x_hexa =  [     0,       0,      0,      0,       0,       0,       0,      5,     13,       21,]

    names = [    '0A',    '0B',   '5A',   '5B',    '5C']
    x_piezo = [-26000,  -16500,  -5500,   5500,   15000]
    y_piezo = [  5100,    5100,   5100,   5100,    5100]
    z_piezo = [  7000,    7000,   7000,   7000,    7000]
    x_hexa =  [     0,       0,      0,      0,       0]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 2, 20, 22]
    ai0 = 0
    ai_list = [0.10, 0.12, 0.15]
    x_off = [-500, 0, 500]


    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.12)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for k, ais in enumerate(ai_list):
            yield from bps.mv(piezo.th, ai0 + ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                for xx, x_of in enumerate(x_off):
                    yield from bps.mv(piezo.x, xs + x_of)

                    name_fmt = "{sample}_ai{ai}_pos{loc}_wa{wax}"
                    sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, loc="%.2d"%xx, wax=wa)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)


def day_1307(t=1):

    proposal_id("2023_1", "311003_Freychet_11")
    yield from giwaxs_mcneil_2023_2(t=2)

    proposal_id("2023_1", "311003_Freychet_12")
    yield from giwaxs_amalie_2023_2(t=1)



def Co_edge_nexafs_2023_3(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['E1_01', 'E1_10', 'E1_100', 'E2_01', 'E2_10', 'E2_100', 'E3_01', 'E3_10', 'E3_100']
    x_piezo = [52500,   40500,    31000,   21000,   10500,    -1000,  -11000,  -21500,   -30500]
    y_piezo = [ 5100,    5100,     5100,    5100,    5100,     5100,    5100,    5100,     5100]
    z_piezo = [ 2190,    2190,     2190,    2190,    2190,     2190,    2190,    2190,     2190]
    z_hexa  = [  0.5,     0.5,      0.5,       1,       1,        1,     1.5,     1.5,      1.5]
    
    # energies = np.linspace(7690, 7730, 41)
    energies = (np.arange(7700, 7710, 5).tolist() + np.arange(7710, 7722, 1).tolist() + np.arange(7722, 7727, 0.5).tolist()
    + np.arange(7727, 7740, 1).tolist() + np.arange(7740, 7765, 5).tolist())

    waxs_arc = [40]

    for name, xs, ys, zs, zhs in zip(names, x_piezo, y_piezo, z_piezo, z_hexa):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(stage.z, zhs)

        yield from bps.mv(stage.th, 0.5)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from alignement_gisaxs_hex(angle=0.15)
        print(name, stage.th.position, stage.y.position)
        ai0 = stage.th.position

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        yield from bps.mv(stage.th, ai0+0.5)

        dets = [pil900KW]

        name_fmt = "nexafs_{sample}_ai0.5_wa40"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="GF", sample_name=sample_name)

        list_ener = energies
        yield from bp.list_scan(dets+[energy, piezo, stage, waxs, xbpm2, xbpm3], energy, list_ener)   
        
        yield from bps.mv(energy, 7750)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 7725)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 7700)
        yield from bps.sleep(2)

        yield from bps.mv(stage.th, ai0)




def benwaddi_waxs_tensile_hard(t=1, name='test'):
    dets = [pil900KW]
    yield from bps.mv(stage.y, 0)

    t0 = time.time()
    for i in range(2000):
        det_exposure_time(t, t)
        name_fmt = "{sample}_9.0keV_{time}s_{i}"
        t1 = time.time()
        sample_name = name_fmt.format(sample=name, time="%1.1f" % (t1 - t0), i="%3.3d" % i)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.mvr(stage.y, 0.005)

        time.sleep(4)



def benwaddi_exsituwaxs_hard(t=1, name='test'):
    dets = [pil900KW]

    names = ['supportfilm_only', 'P3HT', 'supportfilm_P3HT', 'supportfilm_P3DT', 'P3DT']
    x_piezo = [           46000,  36000,               6000,              -2000,  -7000]
    y_piezo = [           -3500,  -3500,              -3500,              -3500,  -3500]
    z_piezo = [            9990,   9990,               9990,               9990,   9990]

    det_exposure_time(t, t)


    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        name_fmt = "{sample}_exsitu_9.0keV"
        sample_name = name_fmt.format(sample=name)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)





def giwaxs_pauldumas_2023_3(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['echpaul_1pulse', 'echpaul_RTA']
    x_piezo = [         23300,        -13000]
    y_piezo = [          7000,          4900]
    z_piezo = [          9270,          9270]
    x_hexa =  [         0.062,         0.062]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.1, 0.2]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(prs, 0)
        # yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        # yield from bps.mv(piezo.y, ys)
        # yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        # yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_hex(angle=0.15)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = stage.th.position
        det_exposure_time(t, t)           
        for ais in ai_list:
            yield from bps.mv(stage.th, ai0+ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                # dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                for k, prss in enumerate(np.linspace(-91, 91, 183)):
                    yield from bps.mv(prs, prss)

                    name_fmt = "{sample}_prs{prs}_wa{wax}"
                    sample_name = name_fmt.format(sample=name, prs="%.2d"%prss, ai="%.2d"%ais, wax=wa)
                    sample_id(user_name="PD", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)



def giwaxs_jonasmuller_2023_3(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    # names = ['ech_s1', 'ech_s2', 'ech_s3']
    # x_piezo = [ 34500,     2800,   -33500]
    # y_piezo = [  7000,     7000,     7000]
    # z_piezo = [  7070,     6670,     8270]
    # x_hexa =  [ 0.465,    0.565,    0.465]

    # names = ['ech_ref1', 'ech_ref2', 'ech_ref3']
    # x_piezo = [   34500,       2800,     -33500]
    # y_piezo = [    7000,       7000,       7000]
    # z_piezo = [    7070,       6670,       8270]
    # x_hexa =  [   0.465,      0.565,      0.465]

    # names = ['ech_ref3']
    # x_piezo = [      -33500]
    # y_piezo = [        7000]
    # z_piezo = [         8270]
    # x_hexa =  [   0.465]

    names = ['ech_s4', 'ech_ref4']
    x_piezo = [ 31400,          0]
    y_piezo = [  7000,       7000]
    z_piezo = [  7370,       6670]
    x_hexa =  [ 0.465,      0.565]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0 = 0
    ai_list = [0.5]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(prs, 0)
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        # yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs_hex(angle=0.15)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = stage.th.position
        det_exposure_time(t, t)           
        for ais in ai_list:
            yield from bps.mv(stage.th, ai0+ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                # dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

                for k, prss in enumerate(np.linspace(-91, 91, 183)):
                    yield from bps.mv(prs, prss)

                    name_fmt = "{sample}_prs{prs}_wa{wax}_ai{ai}"
                    sample_name = name_fmt.format(sample=name, prs="%.2d"%prss, ai="%.2f"%ais, wax=wa)
                    sample_id(user_name="JM", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)



def giwaxs_mcneil_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [  'F_01', 'FB_01', 'C_01', 'CB_01', 'F_02', 'FB_02', 'C_02', 'CB_02']
    x_piezo = [ 50000,  48000,   38000,   25000,   8000,   -8000, -19000,  -32000]
    y_piezo = [  6100,   6100,    6100,    6100,   6100,    6100,   6100,    6100]
    z_piezo = [  7000,   7000,    7000,    7000,   7000,    7000,   7000,    7000]
    x_hexa =  [    10,      0,       0,       0,      0,       0,      0,       0]

    names = [  'FB_01', 'C_01', 'CB_01', 'F_02', 'FB_02', 'C_02', 'CB_02']
    x_piezo = [  48000,  38000,   25000,   8000,   -8000, -19000,  -32000]
    y_piezo = [   6100,   6100,    6100,   6100,    6100,   6100,    6100]
    z_piezo = [   7000,   7000,    7000,   7000,    7000,   7000,    7000]
    x_hexa =  [      0,      0,       0,      0,       0,      0,       0]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [5, 15]
    ai0 = 0
    ai_list = np.linspace(0.04, 0.4, 19)

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.12)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for k, ais in enumerate(ai_list):
            yield from bps.mv(piezo.th, ai0 + ais)
            
            # yield from bps.mv(piezo.x, x + k * 50)


            if waxs.arc.position > 10:
                waxs_arc = [15, 5]
            else:
                waxs_arc = [5, 15]

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                dets = [pil900KW]

                name_fmt = "{sample}_10keV_ai{ai}_wa{wax}"
                sample_name = name_fmt.format(sample=name, ai="%3.2f"%ais, wax=wa)
                sample_id(user_name="LR", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

        yield from bps.mv(piezo.th, ai0)



def S_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [   'Co',  'hT',   'mT',  'hTe', 'mTe',  'mB',  'hB']
    x_piezo = [38000, 32100,  25900,  20100, 13800,  7400,  1500]
    x_hexa = [     0,     0,      0,      0,     0,     0,     0]
    y_piezo = [-3000, -2200,  -2300,  -2900, -2900, -2900, -2800]
    z_piezo = [ 7900,  7900,   7900,   7900,  7900,  7900,  7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(2445, 2470, 5).tolist() + np.arange(2470, 2474, 0.5).tolist() + np.arange(2474, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()+ np.arange(2490, 2511, 5).tolist()

    waxs_arc = [0, 20]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        yss = np.linspace(ys, ys + 700, 52)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2510)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2490)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2450)
            yield from bps.sleep(2)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2490)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2510)
            yield from bps.sleep(2)
            
            yield from bps.mv(waxs, wa)

            yss = np.linspace(ys, ys + 700, 58)
            xss = np.array([xs+300])

            yss, xss = np.meshgrid(yss, xss)
            yss = yss.ravel()
            xss = xss.ravel()

            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies[::-1], xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def Te_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [   'Co',  'hTe', 'mTe',  'mB']
    x_piezo = [38100,  20300, 13900,  7500]
    x_hexa = [     0,      0,     0,     0]
    y_piezo = [-3000,  -2900, -2900, -2900]
    z_piezo = [ 7900,   7900,  7900,  7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(4320, 4345, 5).tolist() + np.arange(4345, 4380, 1).tolist() + np.arange(4380, 4390, 2).tolist() + np.arange(4390, 4421, 5).tolist()

    waxs_arc = [0, 20]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        yss = np.linspace(ys, ys + 700, 52)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2510)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2490)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2450)
            yield from bps.sleep(2)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(energy, 2470)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2490)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2510)
            yield from bps.sleep(2)
            
            yield from bps.mv(waxs, wa)

            yss = np.linspace(ys, ys + 700, 58)
            xss = np.array([xs+300])

            yss, xss = np.meshgrid(yss, xss)
            yss = yss.ravel()
            xss = xss.ravel()

            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies[::-1], xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def giwaxs_S_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [   'Co',  'hT',   'mT',  'hTe', 'hTe',   'mB',   'hB']
    x_piezo = [51000, 47000,  32000,  17000,  4000, -13000, -26000]
    x_hexa = [    10,     0,      0,      0,     0,      0,      0]
    y_piezo = [ 7000,  7000,   7000,   7000,  7000,   7000,   7000]
    z_piezo = [ 7900,  7900,   7900,   7900,  7900,   7900,   7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(2445, 2470, 5).tolist() + np.arange(2470, 2474, 0.5).tolist() + np.arange(2474, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()+ np.arange(2490, 2511, 5).tolist()

    waxs_arc = [0, 20]
    ai0_all = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs(0.5)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)


def giwaxs_Te_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [   'Co',  'hT',   'mT',  'hTe', 'hTe',   'mB',   'hB']
    x_piezo = -4000 + np.asarray([51000, 47000,  32000,  17000,  4000, -13000, -26000])
    x_hexa = [    10,     0,      0,      0,     0,      0,      0]
    y_piezo = [ 7000,  7000,   7000,   7000,  7000,   7000,   7000]
    z_piezo = [ 7900,  7900,   7900,   7900,  7900,   7900,   7900]


    names = [   'hTe', 'mTe',   'mB',   'hB']
    x_piezo = -4000 + np.asarray([ 17000,  4000, -13000, -26000])
    x_hexa = [      0,     0,      0,      0]
    y_piezo = [  7000,  7000,   7000,   7000]
    z_piezo = [  7900,  7900,   7900,   7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(4320, 4345, 5).tolist() + np.arange(4345, 4360, 0.4).tolist() + np.arange(4360, 4380, 2).tolist()+ np.arange(4380, 4401, 5).tolist()

    waxs_arc = [0, 20]
    ai0_all = 0
    ai_list = [0.6]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs(0.1)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_10.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_10.open_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)




def nexafs_Te_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [  'hTe']
    x_piezo = [20300]
    x_hexa = [     0]
    y_piezo = [-2900]
    z_piezo = [ 7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(4320, 4345, 5).tolist() + np.arange(4345, 4380, 1).tolist() + np.arange(4380, 4390, 2).tolist() + np.arange(4390, 4421, 5).tolist()
    energies = np.linspace(4330, 4400, 71)

    waxs_arc = [40]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        yss = np.linspace(ys, ys + 700, 52)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 4380)

def nexafs_Ru_edge_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [  'LDPE_C0_1_redoredo_finerstep_nexafs']
    x_piezo = [41500]
    x_hexa = [     0]
    y_piezo = [-3500]
    z_piezo = [ 7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.linspace(2825, 2850, 51)

    waxs_arc = [40]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        yss = np.linspace(ys, ys + 350, 52)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd5m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
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





def Ru_edge_zhengxing_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = ['LDPE_CO_1','OXO_LDPE_2','LDPE_COH_1','LDPE_1','LDPE_CO_2','OXO_LDPE_2','LDPE_COH_2','LDPE_2']
    x_piezo = [    41600,       30900,       20500,   10200,     -10800,      -21500,      -32000,  -42400]
    x_hexa =  [        0,           0,           0,       0,          0,           0,           0,       0]
    y_piezo = [    -3550,       -3850,       -3600,   -3700,      -3400,       -3500,       -3500,   -3500]
    z_piezo = [     7900,        7900,        7900,    7900,       7900,        7900,        7900,    7900]

    names = ['LDPE_CO_2_real']
    x_piezo = [-500]
    x_hexa =  [     0]
    y_piezo = [ -3900]
    z_piezo = [  7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = np.arange(2800, 2825, 5).tolist() + np.arange(2825, 2830, 0.5).tolist() + np.arange(2830, 2848, 2).tolist()+ np.arange(2838, 2850, 0.5).tolist()+ np.arange(2850, 2881, 5).tolist()

    waxs_arc = [20, 0]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        yss = np.linspace(ys, ys + 500, 55)
        xss = np.array([xs])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2860)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2840)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2820)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2800)
            yield from bps.sleep(2)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(energy, 2820)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2840)
            yield from bps.sleep(2)
            yield from bps.mv(energy, 2860)
            yield from bps.sleep(2)
            
            yield from bps.mv(waxs, wa)

            yss = np.linspace(ys, ys + 700, 58)
            xss = np.array([xs+300])

            yss, xss = np.meshgrid(yss, xss)
            yss = yss.ravel()
            xss = xss.ravel()

            name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}_sdd3m"

            for e, xsss, ysss in zip(energies[::-1], xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)
                
                bpm = xbpm2.sumX.get()
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                sample_id(user_name="AA", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)


def giwaxs_Cl_edge_amalie_2023_3(t=1):
    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)

    names = [  'sa1', 'sa2',  'sa3',  'sa4', 'sa5',  'sa6',  'sa7',  'sa8']
    x_piezo = [45000, 33000,  21000,   9000, -5000, -18000, -31000, -45000]
    x_hexa = [    0,     0,      0,      0,     0,      0,      0,      0]
    y_piezo = [ 7000,  7000,   7000,   7000,  7000,   7000,   7000,   7000]
    z_piezo = [ 7900,  7900,   7900,   7900,  7900,   7900,   7900,   7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = -7 + np.asarray([2810.0, 2820.0, 2830.0, 2832.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])
    
    waxs_arc = [0, 20]
    ai0_all = 0
    ai_list = [0.80]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs(0.5)

        yield from bps.mv(att2_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_9.open_cmd, 1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way
            dets = [pil900KW] if wa < 10 else [pil2M, pil900KW]

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 35)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

            yield from bps.mv(piezo.th, ai0)



def nexafs_Cl_edge_2023_3(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = [  'sa8_nexafs']
    x_piezo = [-51000]
    y_piezo=[0]
    x_hexa = [     0]
    z_piezo = [ 7900]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = -7+np.asarray([2810.0, 2820.0, 2830.0, 2832.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])
    
    waxs_arc = [40]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        # yield from bps.mv(stage.x, xs_hexa)
        # yield from bps.mv(piezo.x, xs)
        # yield from bps.mv(piezo.y, ys)
        # yield from bps.mv(piezo.z, zs)

        det_exposure_time(t, t)

        # yss = np.linspace(ys, ys + 350, 52)
        # xss = np.array([xs])

        # yss, xss = np.meshgrid(yss, xss)
        # yss = yss.ravel()
        # xss = xss.ravel()

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the wa
            
            name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}_sdd5m"

            for e in energies:
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                yield from bps.mvr(piezo.x, 50)
                
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




def gisaxs_saroj_2024_1(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    names = [ 'A_025', 'A_050', 'A_075', 'B_025', 'B_050', 'B_075', 'C_025', 'C_050', 'C_075',
              'D_025', 'D_050', 'D_075', 'E_025', 'E_050', 'E_075', 'F_025', 'F_050', 'F_075']
    x_piezo = [ 55000,   55000,   50000,   42000,   35000,   28000,   20000,   13000,    5000, 
                -3000,  -13000,  -21000,  -28000,  -35000,  -42000,  -49000,  -49000,  -49000]
    z_piezo = [  2300,    2300,    2300,    2300,    2300,    2300,    2300,    2300,    2300,
                 2300,    2300,    2300,    2300,    2300,    2300,    2300,    2300,    2300]
    y_piezo = [  7000,    7000,    7000,    7000,    7000,    7000,    7000,    7000,    7000,
                 7000,    7000,    7000,    7000,    7000,    7000,    7000,    7000,    7000]
    x_hexa =  [    14,       4,       0,       0,       0,       0,       0,       0,       0,
                    0,       0,       0,       0,       0,       0,       0,      -6,     -13]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [20]
    ai0 = 0
    ai_list = [0.12, 0.15, 0.20]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.12)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for k, ais in enumerate(ai_list):
            yield from bps.mv(piezo.th, ai0 + ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # Do not take SAXS when WAXS detector in the way
                dets = [pil2M]

                yield from bps.mv(piezo.x, xs)
                yield from bps.sleep(1)
                
                sample_name = f'{name}{get_scan_md()}__ai{ais}_pos1'
                sample_id(user_name='SU', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.x, xs-1000)
                yield from bps.sleep(1)
                sample_name = f'{name}{get_scan_md()}__ai{ais}_pos2'
                sample_id(user_name='SU', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)


        yield from bps.mv(piezo.th, ai0)



# def big_plan():
#     while True:
#         try:
#             yield from useful_plan()
#         except FailedStatus as e:
#             if e.args[0].device is amptek:
#                 yield from recovery_plan()
#             else:
#                 raise



def NEXAFS_Fe_edge(t=0.5):
    dets = [pil900KW, amptek]
    energies = np.linspace(7100, 7150, 51)

    name = "sampletest_nexafs_Feedge"

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm2.sumX.get() < 5:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
    
        bpm = xbpm3.sumX.get()
        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%0.5, wax=20, xbpm="%4.3f"%bpm)
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)



def Fe_edge_measurments_2024_1(t=1):
    dets = [pil900KW, amptek]
    det_exposure_time(t, t)

    names = ['Pg32T-TT_FeCl3_sa7', 'Pg32T-TT_FeCl3_sa7', 'P3MEEMT_FeCl3_sa15','P3MEEMT_FeCl3_sa16','Pg32T-TT_KCLO4_sa7','Pg32T-TT_KCLO4_sa8',   'Co',   'hT',  'hTe']             
    x_piezo = [             55000,                 46000,               28000,                6000,               -6000,              -25000, -36000, -45000, -45000]
    x_hexa = [                 10,                     0,                   0,                   0,                   0,                   0,      0,     -7,    -15]
    y_piezo = [              6700,                  6700,                6800,                6800,                6900,                6900,   7000,   7100,   7100]
    z_piezo = [             -3000,                 -3000,               -3000,               -3000,               -3000,               -3000,  -3000,  -3000,  -3000]
       
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    energies = [7100, 7105, 7110, 7112, 7114, 7115, 7116, 7117, 7118, 7119, 7121, 7122, 7123, 7124, 7125, 7126, 7127, 7128, 7129, 7130, 
                7131, 7132, 7133, 7134, 7135, 7136, 7137, 7138, 7139, 7140, 7141, 7142, 7143, 7145, 7147, 7150, 7155, 7160, 7165]

    waxs_arc = [20]
    ai0_all = 0
    ai_list = [0.5]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)


        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.5)


        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)


        yield from bps.mv(att2_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_6.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_6.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 5:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 5:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="NS", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


            yield from bps.mv(piezo.th, ai0)




def Fe_edge_measurments_xscanamptek_2024_1(t=1):
    dets = [pil900KW, amptek]
    det_exposure_time(t, t)

    # names = ['Pg32T-TT_FeCl3_sa7', 'Pg32T-TT_FeCl3_sa7', 'P3MEEMT_FeCl3_sa15','P3MEEMT_FeCl3_sa16','Pg32T-TT_KCLO4_sa7','Pg32T-TT_KCLO4_sa8',   'Co',   'hT',  'hTe']             
    # x_piezo = [             55000,                 46000,               28000,                6000,               -6000,              -25000, -36000, -45000, -45000]
    # x_hexa = [                 10,                     0,                   0,                   0,                   0,                   0,      0,     -7,    -15]
    # y_piezo = [              6700,                  6700,                6800,                6800,                6900,                6900,   7000,   7100,   7100]
    # z_piezo = [             -3000,                 -3000,               -3000,               -3000,               -3000,               -3000,  -3000,  -3000,  -3000]
       
    # assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    # assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    # assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    # assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # energies = [7100, 7105, 7110, 7112, 7114, 7115, 7116, 7117, 7118, 7119, 7121, 7122, 7123, 7124, 7125, 7126, 7127, 7128, 7129, 7130, 
    #             7131, 7132, 7133, 7134, 7135, 7136, 7137, 7138, 7139, 7140, 7141, 7142, 7143, 7145, 7147, 7150, 7155, 7160, 7165]

    # waxs_arc = [20]
    # ai0_all = 0
    # ai_list = [0.5]

    for name, xs, ys, zs, xs_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)


        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.open_cmd, 1)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.5)


        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(5)
        yield from bps.mv(GV7.close_cmd, 1)


        yield from bps.mv(att2_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_5.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_6.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att2_6.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Do not take SAXS when WAXS detector in the way

            yield from bps.mv(piezo.x, xs)
            counter = 0

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 5:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 30)
                    counter += 1
                    
                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="LR", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)

                name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 5:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    yield from bps.mv(piezo.x, xs - counter * 30)
                    counter += 1

                    bpm = xbpm2.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    sample_id(user_name="NS", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=1)


            yield from bps.mv(piezo.th, ai0)







def swaxs_S_edge_zaiyu_2024_1(t=1):
    dets = [pil900KW, pil2M]

    names = ['WZY_01', 'WZY_02', 'WZY_03', 'WZY_04', 'WZY_05', 'WZY_06', 'WZY_07', 'WZY_08', 
             'WZY_09', 'WZY_10', 'WZY_11'] 
    x = [       44000,   38200,     32600,    27200,    21300,    13300,     7300,     1300, 
                -3900,   -9700,    -17700]
    y = [       -2600,   -2950,     -2800,    -2700,    -3100,    -3100,    -2600,    -3000,
                -2700,   -2700,     -2900]

    assert len(x) == len(y), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(y)})"
    assert len(x) == len(names), f"Number of X coordinates ({len(x)}) is different from number of samples ({len(names)})"

    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
    
    waxs_arc = [0, 20]

    for name, xs, ys in zip(names, x, y):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)

        yss = np.linspace(ys, ys + 1000, 63)
        xss = np.array([xs-200])

        yss, xss = np.meshgrid(yss, xss)
        yss = yss.ravel()
        xss = xss.ravel()

        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if wa == 0:
                dets = [pil900KW]
            else:
                dets = [pil900KW, pil2M]

            det_exposure_time(t, t)

            name_fmt = "{sample}_sdd1.8m_{energy}eV_wa{wax}_bpm{xbpm}"
            for e, xsss, ysss in zip(energies, xss, yss):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                if xbpm2.sumX.get() < 50:
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.y, ysss)
                yield from bps.mv(piezo.x, xsss)

                bpm = xbpm3.sumX.get()

                sample_name = name_fmt.format(sample=name, energy="%6.2f" % e, wax=wa, xbpm="%4.3f" % bpm)
                sample_id(user_name="GF", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

            yield from bps.mv(energy, 2520)
            yield from bps.sleep(5)
            yield from bps.mv(energy, 2480)
            yield from bps.sleep(5)
            yield from bps.mv(energy, 2445)




def bpmvspindiode_Sedge_2024_2(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    name = 'direct_beam_Sedge'


    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]
    
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm2.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos1_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)



    for e in energies[::-1]:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm2.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos2_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)


def bpmvspindiode_Cledge_2024_2(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    name = 'direct_beam_Cledge_att2_9'


    energies = np.asarray([2810.0, 2820.0, 2830.0, 2832.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])

    
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm2.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos1_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)



    for e in energies[::-1]:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm2.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos2_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="LR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)



def giwaxs_amanda_2025_1(t=0.5, name='test'):
    """
    Grazing incidence measurement with microfoused beam on small capa
    """

    # name   = 'sample2_puce1'
    waxs_range = [0, 2, 20, 22, 40]
    det_exposure_time(t, t)

    dets = [pil900KW]

    for wa in waxs_range:

        yield from bps.mv(waxs, wa)
        sample_name = f'{name}_ai5.0deg_{get_scan_md()}'
        sample_id(user_name='GF', sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)
        
    
    #Retour position alignement
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.3, 0.3)
    yield from bps.mv(waxs, 0)


def giwaxs_amanda_bigsamples_2025_1(t=0.5):
    """
    Grazing incidence measurement with microfoused beam on fullsheet
    """

    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['sample8', 'sample9', 'sample10', 'sample11']
    x_piezo = [ -24906,    -34900,     -44900,     -54000]
    y_piezo = [   4660,      4660,       4660,       4660]
    x_hexa =  [      0,         0,          0,         -3]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 2, 20, 22, 40]
    ai0 = 0
    ai_list = [5.0]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for k, ais in enumerate(ai_list):
            yield from bps.mv(piezo.th, ai0 + ais)

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                yield from bps.mv(piezo.x, xs)
                yield from bps.sleep(1)
                
                sample_name = f'{name}_ai5.0deg_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

        yield from bps.mv(piezo.th, ai0)



def giswaxs_fbarbier_2025_1(t=0.5):
    """
    Grazing incidence measurement for Fred Barbier, sdd = 9.2 m, E = 16.1keV LowDiv
    """

    dets = [pil2M]
    det_exposure_time(t, t)

    # names = [  'sa02', 'sa03', 'sa04_poreux', 'sa04_bord', 'sa05', 'sa06', 'sa07']
    # x_piezo = [ 48000,  24000,          4000,      -12000, -26000, -38000, -50000]
    # y_piezo = [  -300,    -300,          -300,        -300,   -300,   -300,   -300]
    # x_hexa =  [     0,      0,             0,           0,      0,      0,      0]

    names = [  'sa01', 'sa08', 'sa09', 'sa10', 'sa11', 'sa12']
    x_piezo = [ 55000,  43000,  25000,   1000, -19000, -43000]
    y_piezo = [  -300,   -300,   -300,   -300,   -300,   -300]
    x_hexa =  [     2,      0,      0,      0,      0,      0]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [20]
    ai0 = 0
    ai_list = [0.15, 0.20, 0.30, 0.45, 0.77]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yield from bps.mv(piezo.th, ai0)
        yield from alignement_gisaxs(angle=0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            
            for k, ais in enumerate(ai_list):
                if ais == 0.1:
                    yield from bps.mv(att1_5.open_cmd, 1)
                    yield from bps.sleep(1)
                    yield from bps.mv(att1_5.open_cmd, 1)
                elif ais == 0.85:
                    yield from bps.mv(att1_5.close_cmd, 1)
                    yield from bps.sleep(1)
                    yield from bps.mv(att1_5.close_cmd, 1)

                yield from bps.mv(piezo.th, ai0 + ais)


                sample_name = f'{name}_ai{ais}deg_pos1_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.x, xs-1000)
                yield from bps.sleep(1)

                sample_name = f'{name}_ai{ais}deg_pos1_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

        yield from bps.mv(piezo.th, ai0)



def giwaxs_flavien_2025_1(t=0.5, name='test'):
    """
    Grazing incidence measurement with microfoused beam on small capa
    """
    
    x = piezo.x.position
    ai0 = piezo.th.position
    yield from bps.mv(piezo.th, ai0+5.0)
    
    # name   = 'sample2_puce1'
    if waxs.arc.position > 20:
        waxs_range = [0, 2, 20, 22, 40][::-1]
    else:
        waxs_range = [0, 2, 20, 22, 40]

    det_exposure_time(t, t)
    dets = [pil900KW]

    for wa in waxs_range:
        yield from bps.mv(waxs, wa)
        sample_name = f'{name}_ai5.0deg_pos1_{get_scan_md()}'
        sample_id(user_name='GF', sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        yield from bp.count(dets)

        yield from bps.mv(piezo.x, x+2000)
        yield from bps.sleep(1)

        sample_name = f'{name}_ai5.0deg_pos2_{get_scan_md()}'
        sample_id(user_name='GF', sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)
        yield from bps.sleep(1)
        yield from bps.mv(piezo.x, x)

    yield from bps.mv(piezo.th, ai0)

    # #Retour position alignement
    # sample_id(user_name='test', sample_name='test')
    # det_exposure_time(0.3, 0.3)
    # yield from bps.mv(waxs, 0)




def giwaxs_chene_2025_1(t=0.5):
    """
    Grazing incidence measurement with microfoused beam on small capa
    """
    
    det_exposure_time(t, t)
    dets = [pil900KW]

    # names = [  '611_A4_par', '611_A4_per', '611_C2_par', '616_C1_per', '616_A4_par']
    # x_piezo = [      -10000,        -7500,        -4500,         -200,         4000]
    # y_piezo = [        1350,         1300,         1270,         1248,         1200]
    # ais0 =   [        0.087,        0.074,            0,         0.46,         0.36]

    names = [  '611_A4_par_redo', '611_A4_per_redo', '616_A4_per', '616_C2_par', '616_C2_per']
    x_piezo = [           -10000,             -6900,        -4500,         -200,         4000]
    y_piezo = [              350,               300,          270,          250,          220]
    ais0 =   [             0.087,             -0.11,         0.35,        -0.27,        -0.68]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    # ai0 = 0.59
    waxs_range = [0, 2, 20, 22]

    # temperatures = [24, 0, -50, -100, -150, -180, 25, 100, 200]

    temperatures = [-50, -100, -150, -180, 25, 100, 200]
    for temp in temperatures:
        if temp==0:
            names = [  '616_C2_per']
            x_piezo = [        4000]
            y_piezo = [                 220]
            ais0 =   [               -0.5]
        else:
            names = [  '611_A4_par_redo', '611_A4_per_redo', '616_A4_per', '616_C2_par', '616_C2_per']
            x_piezo = [           -10000,             -6900,        -4500,         -200,         4000]
            y_piezo = [              350,               300,          270,          250,          220]
            ais0 =   [             0.087,             -0.11,         0.35,        -0.27,        -0.5]

            LThermal.setTemperature(temp)
            
            while abs(LThermal.temperature() - temp) > 10:
                yield from bps.sleep(60)
                print('temp not at there yet')

            print('At temp equal ', temp)
            print('Wainting for 5 min')

            yield from bps.sleep(300)

        temp_real = LThermal.temperature()
        for name, xs, ys, ai0 in zip(names, x_piezo, y_piezo, ais0):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.th, ai0)

            if name != '611_A4_par_redo':
                yield from alignement_gisaxs_doblestack(angle=0.15)
                ai0 = piezo.th.position

            else:
                ai0=-0.43
                yield from bps.mv(waxs, 0,
                                  piezo.th, ai0 + 4.0,
                                  piezo.y, 256)
                det_exposure_time(0.5, 0.5)

                yield from bp.rel_scan([pil900KW], piezo.y, -300 , 300, 51)
                ps(der=False, plot=False)
                yield from bps.mv(piezo.y, ps.cen)
            
            det_exposure_time(t, t)

            yield from bps.mv(piezo.th, ai0 + 4.0)
            for i, wa in enumerate(waxs_range):
                yield from bps.mv(waxs, wa)
                
                tem = '%.01f'%temp
                tem_real = '%.01f'%temp_real

                sample_name = f'{name}_{tem}_ai4.0deg_pos1_{get_scan_md()}_{tem_real}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.x, xs+200)
                yield from bps.sleep(1)

                sample_name = f'{name}_{temp}_ai4.0deg_pos2_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)
                yield from bps.mv(piezo.x, xs)

            yield from bps.mv(piezo.th, ai0)








import bluesky.preprocessors as bpp
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from ophyd import Signal

def single_scan_test(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):
    '''
    Study the beam damage on 1 film to define the opti;am experimental conitions.

    '''
    if ai_list is None:
        ai_list = []

    # 63 energies
    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
   
    energies = [16100, 16100, 16100]

    ai0 = piezo.th.position
    xs = piezo.x.position
    dets = [pil900KW, pil2M]
    dets = [pil2M]

    s = Signal(name='target_file_name', value='', kind=3)

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for i, wa in enumerate(waxs_arc):
            # yield from bps.mv(waxs, wa)

            counter = 0
            for k, ais in enumerate(ai_list):
                if ais==0.6:
                    det_exposure_time(0.5, 0.5)
                else:
                    det_exposure_time(1, 1)

                # yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)
                    if xbpm2.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    
                    # yield from bps.mv(piezo.x, xs + counter * xstep)
                    counter += 1
                    bpm = yield from bps.rd(xbpm2.sumX)
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    # sample_id(user_name="CM", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
                
                # yield from bps.mv(energy, 2500)
                # yield from bps.sleep(2)
                # yield from bps.mv(energy, 2480)
                # yield from bps.sleep(2)
                # yield from bps.mv(energy, 2445)

            # yield from bps.mv(piezo.th, ai0)
    return (yield from inner())
	


import bluesky.preprocessors as bpp
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from ophyd import Signal

def single_scan_giwaxs(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):
    '''
    Study the beam damage on 1 film to define the opti;am experimental conitions.

    '''
    names = ['sj-ppionzrox-m-post', 'sj-ppionzrox-m-ox', 'sj-ppionzrox-m-pre', 'sj-ppion-m-ox', 
                 'sj-bkg-m-coated',     'sj-bkg-m-bare']
    x_piezo = [              53800,               53900,                48700,           37900,
                             26900,               16400]
    x_hexa = [                  14,                 4.3,                    0,               0,
                                0,                    0]
    y_piezo = [               7300,                7300,                 7300,            7300,
                              7300,                7200]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 20]
    ai0_all = -1
    ai_list = [0.10, 0.12, 0.15, 0.20]
    xstep = 0


    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())
    







def temp_series(name='temp',temps = np.linspace(25,40,16),exp_time=1, hold_delay=120, dets=[pil2M]):   # function loop to bring linkam to temp, hold and measure
# Function will begin at start_temp and take a SAXS measurement at every temperature given 
    
    temps = np.linspace(45, 30, 16)

    dets = [pil2M, pil900KW]
    LThermal.setTemperature(temps[0])
    # LThermal.setTemperatureRate(ramp)
    LThermal.on() # turn on 
    det_exposure_time(exp_time,exp_time)

    s = Signal(name='target_file_name', value='')
    RE.md["sample_name"] = '{target_file_name}'
    for i, temp in enumerate(temps):
        LThermal.setTemperature(temp)

        while abs(LThermal.temperature()-temp)>0.5:
            yield from bps.sleep(10)
            print('waiting for 10s')

        print('Reached tem', temp)
        print('Waiting during equilibration')
        if i==0:
            yield from bps.sleep(2*hold_delay)
        else:
            yield from bps.sleep(hold_delay)



        # Metadata
        sdd = pil2M_pos.z.position / 1000

        # Sample name
        name_fmt = ("{sample}_{energy}eV_sdd{sdd}m_temp{temp}")
        sample_name = name_fmt.format(sample = name,energy = "%.2f" % energy.energy.position , sdd = "%.1f" % sdd, temp = "%.1f" %temp)

        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        s.put(sample_name)
        
        yield from bp.count(dets + [s])

    LThermal.off()





def giwaxs_Gu_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):
    # names = ['sa_01_01', 'sa_01_02', 'sa_01_03', 'sa_01_04', 'sa_01_05', 'sa_01_06', 'sa_01_07',
    #          'sa_02_01', 'sa_02_02', 'sa_02_03', 'sa_02_04', 'sa_02_05']
    # x_piezo = [   53000,      53000,      41000,      29000,      18000,       7000,      -4000,
    #              -22000,     -32000,     -43000,     -53000,     -53000]
    # x_hexa = [       12,          1,          0,          0,          0,          0,          0,
    #                   0,          0,          0,         -1,        -12]    
    # y_piezo = [    6000,       6000,       6000,       6000,       6000,       6000,       6000,
    #                6000,       6000,       6000,       6000,       6000]

    # names = ['sa_01_07_redo','sa_02_01_redo']
    # x_piezo = [        -4000,         -22000]
    # x_hexa = [             0,              0]    
    # y_piezo = [         6000,           6000]

    # names = ['sa_02_06', 'sa_02_07', 'sa_02_08', 'sa_02_09', 'sa_02_10',
    #          'sa_03_01', 'sa_03_02', 'sa_03_03', 'sa_03_04', 'sa_03_05']
    # x_piezo = [   53000,      53000,      43000,      32000,      22000,
    #                7000,      -6000,     -18000,     -31000,     -44000]
    # x_hexa = [       12,          1,          0,          0,          0,
    #                   0,          0,          0,          0,          0]    
    # y_piezo = [    6000,       6000,       6000,       6000,       6000,
    #                6000,       6000,       6000,       6000,       6000]

    # names = ['sa_04_01', 'sa_04_02', 'sa_04_03', 'sa_04_04', 'sa_04_05', 'sa_01_A1', 'sa_01_A2', 
    #          'sa_01_A3', 'sa_01_A4', 'sa_01_A5', 'sa_01_A6', 'sa_01_B1', 'sa_01_B2', 'sa_01_B3', 'sa_01_B4', 'sa_01_B5']
    # x_piezo = [   53000,      53000,      45000,      35000,      25000,      15000,       7000, 
    #                   0,      -8000,     -16000,     -24000,     -32000,     -40000,     -47000,     -53000,     -53000]
    # x_hexa = [       12,          2,          0,          0,          0,          0,          0,
    #                   0,          0,          0,          0,          0,          0,          0,         -2,        -10]    
    # y_piezo = [    6000,       6000,       6000,       6000,       6000,       6000,       6000,
    #                6000,       6000,       6000,       6000,       6000,       6000,       6000,       6000,       6000]

    # names = ['sa_01_B6', 'sa_01_C1', 'sa_01_C2', 'sa_01_C3', 'sa_01_D6', 'sa_02_A1', 'sa_02_A2', 'sa_02_A3',
    #          'sa_02_A4', 'sa_02_A5', 'sa_02_A6', 'sa_02_B1', 'sa_02_B2', 'sa_02_B3', 'sa_02_B4', 'sa_02_B5']
    # x_piezo = [   53000,      53000,      47000,      39000,      29000,      15000,       7000,          0,
    #               -8000,     -16000,     -24000,     -32000,     -40000,     -49000,     -53000,     -53000]
    # x_hexa = [       12,          3,          0,          0,          0,          0,          0,          0,
    #                   0,          0,          0,          0,          0,          0,         -5,        -13]    
    # y_piezo = [    6000,       6000,       6000,       6000,       6000,       6000,       6000,       6000,
    #                6000,       6000,       6000,       6000,       6000,       6000,       6000,       6000]
    
    # names = ['sa_01_B4_redo', 'sa_02_A1_redo', 'sa_02_A5_redo', 'sa_02_B4_redo', 'sa_02_B5_redo', 'sa_02_B6', 'sa_02_10_redo']
    # x_piezo = [        53000,           52000,           43000,           34000,           26000,      17000,            7000]
    # x_hexa = [             9,               0,               0,               0,               0,          0,               0]    
    # y_piezo = [         6000,            6000,            6000,            6000,            6000,       6000,            6000]

    names = ['sa_02_B4_redo']
    x_piezo = [        34000]
    x_hexa = [             0]    
    y_piezo = [         6000]
    
 
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0_all = 0.3
    ai_list = [0.10, 0.12, 0.15, 0.20]
    xstep = 300
    
    dets = [pil2M, pil900KW]


    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def giwaxs_Su_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    names = ['sidney_08','jose_04-80','jose_07-80','jose_10-80','jose_04-50','jose_07-50','jose_10-50', 'jose_AgTNF']    
    x_piezo = [    53000,       53000,       49000,       40000,       32000,       24000,       17000,         7000]
    x_hexa = [        13,           4,           0,          0,            0,           0,           0,            0]    
    y_piezo = [     6000,        6000,        6000,        6000,        6000,        6000,        6000,         6000]
    
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0_all = 0.3
    ai_list = [0.10, 0.12, 0.16, 0.20]
    xstep = 0
    
    dets = [pil2M, pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def giwaxs_Milo_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    names = [   'Si',   'P2',  'P3b',  'P3a']    
    x_piezo = [-6000, -20000, -35000, -48000]
    x_hexa = [     0,      0,      0,      0]    
    y_piezo = [ 5000,   5000,   5000,   5000]
    
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0_all = 0.3
    ai_list = [0.10, 0.16, 0.20]
    xstep = 0
    
    dets = [pil2M, pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())




def giwaxs_NV_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    names = [   'HZo_ech4']    
    x_piezo = [-53000]
    x_hexa = [    -9]    
    y_piezo = [ 6000]
    
    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [0, 20]
    ai0_all = 0.3
    ai_list = [0.50]
    xstep = 0
    
    dets = [pil2M, pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())





def giwaxs_chris_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    # names = ['RT_01r', 'RT_02', 'RT_03r', 'RT_04']    
    # x_piezo = [ -6000,  -21000,   -34000,  -45000]
    # x_hexa = [      0,       0,        0,      -3]    
    # y_piezo = [  6000,    6000,     6000,    6000]
    
    names = ['RT_05r', 'RT_06', 'RT_07r', 'RT_08', 'RT_09r', 'RT_10', 'RT_11r', 'RT_12']    
    x_piezo = [ 53000,   47000,    35000,   18000,     5000,   -8000,   -22000,  -36000]
    x_hexa = [      8,       0,        0,       0,        0,       0,        0,       0]    
    y_piezo = [  6000,    6000,     6000,    6000,     6000,    6000,     6000,    6000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 9, 20]
    ai0_all = 0.3
    ai_list = [0.06, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.20]
    xstep = 200
    
    dets = [pil2M, pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())






def swaxs_Cheng_2025_3(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    waxs_arc = [20, 0]


    names   = ['MEM_HDPE','MEM_382','MEM_393','MEM_401','MEM_439','MEM_453','MEM_455','MEM_458','LDPE']
    piezo_x = [     42500,    38500,    33500,    28500,    23000,    15500,    10500,     5000,  -500]
    piezo_y = [         0,        0,        0,        0,        0,        0,        0,        0,     0]

    # Offsets for taking a few points per sample
    x_off = [-400, 0, 400]
    y_off = [0, 400]

    user = "CW"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)

            for name, x, y in zip(names, piezo_x, piezo_y):
                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

    

def swaxs_Milo_2025_3(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    waxs_arc = [0, 20]


    names   = [   'Si3N4',     'P2',    'P3b','PVDF_01','PVDF_02','PVDF_03','PVDF_04']
    piezo_x = [     -6660,   -12400,   -17900,   -25000,   -30000,   -35000,   -42000]
    piezo_y = [         0,        0,        0,        0,        0,        0,        0]

    # Offsets for taking a few points per sample
    x_off = [-400, 0, 400]
    y_off = [0, 400]

    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)

            for name, x, y in zip(names, piezo_x, piezo_y):
                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)




def swaxs_Fei_2025_3(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """



    waxs_arc = [40, 20, 0]

    # names   = [  'I1',  'I2',  'I3',  'I4',  'I5',  'I6',
    #              'J1',  'J2',  'J3',  'J4',  'J5',  'J6',
    #              'K1',  'K2',  'K3',  'K4',  'K5',  'K6',
    #              'L1',  'L2',  'L3',  'L4',  'L5',  'L6',

    #              'M1',  'M2',  'M3',  'M4',  'M5',  'M6',
    #              'N1',  'N2',  'N3',  'N4',  'N5',  'N6',
    #              'O1',  'O2',  'O3',  'O4',  'O5',  'O6',
    #              'P1',  'P2',  'P3',  'P4',  'P5',  'P6']
    
    # piezo_x = [ 39900, 31000, 22000, 13000,  4600, -4200,
    #             39500, 31000, 21500, 13000,  4500, -4600,
    #             39700, 31000, 21900, 13000,  4000, -4800,
    #             39800, 30500, 22000, 13000,  4500, -4800,
                
    #            -14900,-23900,-32500,-41500,-50200,-51200, 
    #            -14500,-24000,-32500,-41500,-50200,-51500,
    #            -15300,-23800,-32800,-41300,-50000,-51700,
    #            -14800,-24000,-32500,-41700,-50300,-51700]
    
    # piezo_y = [ -5400, -5400, -5400, -5800, -5600, -5600,
    #             -4100, -4100, -4100, -4100, -4100, -4300,
    #              1000,  1000,  1000,  1000,  1000,  1000,
    #              1500,  1200,  1000,  1000,   800,   800,
                  
    #             -5000, -5000, -5000, -5000, -5000, -5700,
    #             -3800, -3800, -3800, -3800, -4000, -4000,
    #              1600,  1200,  1200,  1200,  1200,  1400,
    #              1800,  1800,  1800,  1800,  1800,  1800,]
    
    # hexa_y =  [    -4,    -4,    -4,    -4,     -4,   -4,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 5,     5,     5,     5,      5,    5,

    #                -4,    -4,    -4,    -4,     -4,   -4,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 5,     5,     5,     5,      5,    5,]
    
    # hexa_x =  [     0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,

    #                 0,     0,     0,     0,      0,   -8,
    #                 0,     0,     0,     0,      0,   -8,
    #                 0,     0,     0,     0,      0,   -8,
    #                 0,     0,     0,     0,      0,   -8]



    names   = [  'Q1',  'Q2',  'Q3',  'Q4',  'Q5',  'Q6',
                 'R1',  'R2',  'R3',  'R4',  'R5',  'R6',
                 'S1',  'S2',  'S3',  'S4',  'S5',  'S6',
                 'T1',  'T2',  'T3',  'T4',  'T5',  'T6',

                 'U1',  'U2',  'U3',  'U4',  'U5',  'U6',
                 'V1',  'V2',  'V3',  'V4',  'V5',  'V6',
                 'W1',  'W2']
    
    piezo_x = [ 40200, 31000, 22500, 13500,  4500, -4000,
                40000, 31200, 23000, 13500,  5100, -4300,
                40500, 31100, 22300, 13500,  4700, -4100,
                40200, 31500, 22800, 14200,  4500, -4200,
                
               -15000,-24000,-33300,-41800,-50300,-51700, 
               -15300,-24300,-33000,-41500,-50300,-51700,
               -15000,-24000]
    
    piezo_y = [ -6000, -5500, -5600, -5800, -5800, -5800,
                -4800, -4800, -4600, -4600, -4600, -4600,
                  500,  1000,   800,   600,   600,   600,
                 1000,  1000,   800,   800,   800,   800,
                  
                -5300, -5300, -5100, -5100, -5100, -4700,
                -4000, -4200, -3800, -3500, -3500, -3800,
                 1000,  1000]
    
    hexa_y =  [    -4,    -4,    -4,    -4,     -4,   -4,
                    0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,
                    5,     5,     5,     5,      5,    5,

                   -4,    -4,    -4,    -4,     -4,   -4,
                    0,     0,     0,     0,      0,    0,
                    0,     0]
    
    hexa_x =  [     0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,

                    0,     0,     0,     0,      0,   -8,
                    0,     0,     0,     0,      0,   -8,
                    0,     0]

    # Offsets for taking a few points per sample
    x_off = [-400, 0, 400]
    y_off = [-400, 0, 400]
    # y_off = [0, 400]
    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"
    assert len(piezo_x) == len(hexa_x), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_x)})"
    assert len(piezo_x) == len(hexa_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)

            for name, x, y, hex_x, hex_y in zip(names, piezo_x, piezo_y, hexa_x, hexa_y):
                yield from bps.mv(stage.y, hex_y,
                                  stage.x, hex_x)

                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)




def swaxs_Fei_2025_3_finegrid(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    waxs_arc = [0]


    names   = [  'A1',  'A2',  'A3',  'A4',  'A5',  'A6',  
                 'B1',  'B2',  'B3']
    
    piezo_x = [ 40000, 31000, 22000, 13000,  4500, -4000, 
                40000, 31000, 22500]
    
    piezo_y = [ -6000, -6000, -6000, -6000,  -6000,-6000,
                -4800, -4600, -4800]
    
    hexa_y =  [    -4,    -4,    -4,    -4,     -4,   -4,
                    0,     0,     0]
    
    hexa_x =  [     0,     0,     0,     0,      0,    0,
                    0,     0,     0]

    # Offsets for taking a few points per sample
    x_off = [-400, -200, 0, 200, 400]
    y_off = [-400, -300, -200, -100, 0, 100, 200, 300, 400]

    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"
    assert len(piezo_x) == len(hexa_x), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_x)})"
    assert len(piezo_x) == len(hexa_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)
                
            for name, x, y, hex_x, hex_y in zip(names, piezo_x, piezo_y, hexa_x, hexa_y):
                yield from bps.mv(stage.y, hex_y,
                                  stage.x, hex_x)
                
                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)



def saxs_cap_Fei_2025_3(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    # names   = [  'FY1', 'FY1', 'FY3','HWA1','HWB1','HWC1','HWD1','HWE1','HWF1','HWG1','HWI1', 
    #             'HWA2','HWB2','HWC2','HWD2','HWF2','HWG2','HWH2','HWI2','HWA3','HWB3']
    # piezo_x = [  37700, 31300, 25400, 18600, 12300,  5600,   100, -6000,-12500,-19600,-25400,
    #             -31700,-38700,-44600, 34000, 27900, 22000, 15400,  8900,  2300, -4500]
    # piezo_y = [   -600,  -700,  -700,  -700,  -700,  -100,  -700,  -700,  -700,  -700,  -700,
    #               -700, -1900, -1900, -2500, -1300, -1300, -1300, -1300,  -900,  -900]
    # piezo_z = [   2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,
    #               2000,  2000,  2000, -8200, -8200, -8200, -8200, -8200, -8200, -8200]

    names   = [ 'HWE2','HWD3','HWF3','HWG3','HWH3','HWI3','33B2','33B3','33C2','33C3','34B2', 
                'HW01','HW02','HW03','HW04','HW05','HW06','HW07','HW08','HW09','HW11','HW12']
    piezo_x = [  38300, 32100, 24400, 18900, 12400,  6300,     0, -7200,-13200,-19700,-25900,
                -31500, 40800, 28000, 21900, 15200,  9700,  2600, -4100,-10200,-22500,-28700]
    piezo_y = [  -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1500, -1100,
                 -1900, -1200, -1000,  -500,  -500,  -500,  -500,  -500,  -500,  -500,  -500]
    piezo_z = [   2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,  2000,
                  2000, -8200, -8200, -8200, -8200, -8200, -8200, -8200, -8200, -8200, -8200]
    # Offsets for taking a few points per sample
    y_off = [-400, 0, 400]
    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"
    assert len(piezo_x) == len(piezo_z), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_z)})"

    dets = [pil2M]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        # Detectors, disable SAXS when WAXS in the way
        det_exposure_time(t, t)

        for name, x, y, z in zip(names, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x,
                                piezo.z, z)

            for yy, y_of in enumerate(y_off):
                yield from bps.mv(piezo.y, y + y_of)
                yield from bps.sleep(2)

                loc = f'{yy}'
                sample_name = f'{name}{get_scan_md()}_loc{loc}'
                print(f"\n\t=== Sample: {sample_name} ===\n")
                s.put(sample_name)
                yield from bps.trigger_and_read(dets + [energy, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)






def bpmvspindiode_Sedge_2025_3(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    name = 'direct_beam_Sedge'


    energies = [2450.0,2455.0,2460.0,2465.0,2470.0,2473.0,2475.0,2475.5,2476.0,2476.5,2477.0,2477.5,2478.0,2478.5,2479.0,2479.5,
    2480.0,2480.5,2481.0,2482.0,2483.0,2484.0,2485.0,2486.0, 2487.0,2488.0,2489.0,2490.0,2492.5,2495.0,2500.0,2510.0,2515.0]
    
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm3.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos1_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)

    for e in energies[::-1]:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)
        if xbpm3.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        yield from bps.sleep(2)

        fs.close()

        name_fmt = "{sample}_pos2_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)



def bpmvspindiode_Pedge_2025_3(t=1):
    dets = [pil2M]
    det_exposure_time(t, t)

    name = 'direct_beam_Sedge'


    energies = np.linspace(2130, 2180, 51)

    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(4)
        if xbpm3.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        fs.close()

        name_fmt = "{sample}_pos1_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)

    for e in energies[::-1]:
        yield from bps.mv(energy, e)
        yield from bps.sleep(4)
        if xbpm3.sumX.get() < 50:
            yield from bps.sleep(2)
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)

        fs.open()
        yield from bps.sleep(2)
        bpm2 = xbpm2.sumX.get()
        bpm3 = xbpm3.sumX.get()
        pdc = pdcurrent2.get()
        yield from bps.sleep(2)

        fs.close()

        name_fmt = "{sample}_pos2_{energy}eV_bpm2_{xbpm2}_bpm3_{xbpm3}_pd_{pd}"

        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, xbpm2="%4.3f"%bpm2, xbpm3="%4.3f"%bpm3, pd="%4.3f"%pdc)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count([pil2M], num=1)




def song_saxs_tensile_hard(t=1):
    dets = [pil2M, pil900KW]
    names = "MEM_382_redo"
    # det_exposure_time(t, t)
    t0 = time.time()
    for i in range(5000):
        name_fmt = "{sample}_16100eV_sdd5.0m_wa17_{time}_{i}"
        t1 = time.time()
        sample_name = name_fmt.format(sample=names, time="%1.1f" % (t1 - t0), i="%3.3d" % i)
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)




def giwaxs_perovskite_2025_3(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    # names = ['RT_01r', 'RT_02', 'RT_03r', 'RT_04']    
    # x_piezo = [ -6000,  -21000,   -34000,  -45000]
    # x_hexa = [      0,       0,        0,      -3]    
    # y_piezo = [  6000,    6000,     6000,    6000]
    
    names = ['DUT25_014_cr', 'DUT25_014_perov', 'DUT25_014_cr', 'DUT25_014_perov', 'DUT25_027', 'PVK25_076', 'PVK22_205', 'PVK25_070', 'PVK25_074']    
    x_piezo = [       50000,             50000,          37000,             29000,        7000,      -19000,      -41000,      -44000,      -54000]
    x_hexa = [           12,                 5,              0,                 0,           0,           0,           0,         -16,         -17]    
    y_piezo = [        3000,              3000,           3000,              3000,        6000,        6000,        6000,        6000,        6000]

    names = ['PVK25_070', 'PVK25_074']    
    x_piezo = [   -44000,      -54000]
    x_hexa = [       -16,         -17]    
    y_piezo = [   4000,        4000]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 20]
    ai0_all = 0.3
    ai_list = [0.1, 0.2, 0.5, 1.0]
    
    dets = [pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        
        yield from alignement_gisaxs_short(0.1)
        
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        print('ai0 is', ai0)
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def scan_nexafs_PbL3edge():
    dets = [pil900KW]

    name='nexafs_Feedge_redo'
    energies = np.linspace(13030, 13130, 51)

    energies = [13020, 13030, 13040, 13045, 13050, 13051, 13052, 13053, 13054, 13055, 13056, 13057, 13058, 13059, 13060, 13061,
                13062, 13063, 13064, 13065, 13066, 13067, 13068, 13069, 13070, 13071, 13072, 13073, 13074, 13075, 13077, 13079, 
                13081, 13083, 13085, 13090, 13100, 13120]

    waxs_arc = [7, 20]
    ai0_all = 0.3
    ai_list = [0.1, 0.2, 0.5, 1.0]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                name_fmt = ("{sample}_{energy}eV_wa{wax}_ai1.6deg")
                sample_name = name_fmt.format(sample = name,energy = "%.2f" % e , wax = wa)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner())




def sevralai_giwaxs_Fe_edge_2025_3(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):
    dets = [pil900KW]

    # names = [ 'DUT25_014_perov', 'DUT25_014_perov', 'DUT25_027', 'PVK25_076', 'PVK22_205', 'PVK25_070', 'PVK25_074']    
    # x_piezo = [           50000,             29000,        7000,      -19000,      -41000,      -44000,      -54000]
    # x_hexa = [                5,                 0,           0,           0,           0,         -16,         -17]    
    # y_piezo = [            3000,              3200,        3400,        3600,        3800,        4000,        4000]

    # names = [   'JD23_055', 'PVK25_076_redo']    
    # x_piezo = [     -30000,       -8000]
    # x_hexa = [           0,           0]    
    # y_piezo = [       2800,        3500]

    names = ['PVK25_076_redo']    
    x_piezo = [         -8000]
    x_hexa = [              0]    
    y_piezo = [          2500]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # 63 energies
    energies = [13020, 13030, 13040, 13045, 13050, 13051, 13052, 13053, 13054, 13055, 13056, 13057, 13058, 13059, 13060, 13061,
                13062, 13063, 13064, 13065, 13066, 13067, 13068, 13069, 13070, 13071, 13072, 13073, 13074, 13075, 13077, 13079, 
                13081, 13083, 13085, 13090, 13100, 13120]
    
    waxs_arc = [7, 20]
    ai0_all = 0.3
    ai_list = [0.5, 3.0]
    
    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        if 'PVK25_076' in name:
            ai_list = [0.5, 1.0]

        yield from bps.mv(stage.x, xs_hexa,
                        piezo.x, xs,
                        piezo.y, ys,
                        piezo.th, ai0_all)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        
        yield from alignement_gisaxs_short(0.1)
        
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        print('ai0 is', ai0)
        det_exposure_time(t, t)


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
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.3f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
                    
                    yield from bps.mv(energy, 13070)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 13050)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.th, ai0)
        (yield from inner())





def scan_nexafs_BrKedge():
    dets = [pil900KW]

    name='nexafs_Feedge_redo'
    energies = np.linspace(13450, 13550, 51)

    energies = [13450, 13460, 13470, 13480, 13482, 13484, 13485, 13486, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
                13495, 13496, 13497, 13498, 13499, 13500, 13501, 13502, 13503, 13504, 13505, 13506, 13507, 13508, 13509, 13510, 
                13515, 13520, 13530, 13550, 13570, 13590]

    waxs_arc = [20]
    ai_list = [1.0]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                name_fmt = ("{sample}_{energy}eV_wa{wax}_ai1.6deg")
                sample_name = name_fmt.format(sample = name,energy = "%.2f" % e , wax = wa)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner())




def sevralai_giwaxs_Br_edge_2025_3(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):
    '''

    '''
    dets = [pil900KW]

    # names = [ 'DUT25_014_perov', 'DUT25_014_perov', 'DUT25_027', 'PVK25_076', 'PVK22_205', 'PVK25_070', 'PVK25_074']    
    # x_piezo = [           50000,             29000,        7000,      -19000,      -41000,      -44000,      -54000]
    # x_hexa = [                5,                 0,           0,           0,           0,         -16,         -17]    
    # y_piezo = [            3000,              3200,        3400,        3600,        3800,        4000,        4000]

    # names = [   'JD23_055', 'PVK25_076_redo']    
    # x_piezo = [     -30000,       -8000]
    # x_hexa = [           0,           0]    
    # y_piezo = [       2800,        3500]

    names = [   'A2', 'B1']    
    x_piezo = [13000,30000]
    x_hexa = [     0,    0]    
    y_piezo = [ 3150, 3150]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # 63 energies
    energies = [13450, 13460, 13470, 13480, 13482, 13484, 13485, 13486, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
                13495, 13496, 13497, 13498, 13499, 13500, 13501, 13502, 13503, 13504, 13505, 13506, 13507, 13508, 13509, 13510, 
                13515, 13520, 13530, 13550, 13570, 13590]
    
    waxs_arc = [7, 20]
    ai0_all = 0.3
    ai_list = [0.05, 0.1, 0.5]
    
    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        if 'PVK25_076' in name:
            ai_list = [0.5, 1.0]

        yield from bps.mv(stage.x, xs_hexa,
                        piezo.x, xs,
                        piezo.y, ys,
                        piezo.th, ai0_all)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        
        yield from alignement_gisaxs_doblestack(0.1)
        
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        print('ai0 is', ai0)
        det_exposure_time(t, t)


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
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.3f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
                    
                    yield from bps.mv(energy, 13520)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 13480)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.th, ai0)
        (yield from inner())




def sevralai_giwaxs_Br_edge_2025_3_ver(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):
    '''

    '''
    dets = [pil900KW]

    names = [    'A2', 'B1']    
    x_piezo = [-15000,10000]
    x_hexa = [      0,    0]    
    y_piezo = [  3000, 3000]

    names = [   'B1']    
    x_piezo = [10000]
    x_hexa = [     0]    
    y_piezo = [  3000]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # 63 energies
    energies = [13450, 13460, 13470, 13480, 13482, 13484, 13485, 13486, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
                13495, 13496, 13497, 13498, 13499, 13500, 13501, 13502, 13503, 13504, 13505, 13506, 13507, 13508, 13509, 13510, 
                13515, 13520, 13530, 13550, 13570, 13590]
    
    waxs_arc = [15]
    ai_list = [0.05, 0.1, 0.5]
    
    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        # Setup measurement for sample
        yield from bps.mv(piezo.y, ys, 
                        piezo.x, xs, 
                        stage.x, xs_hexa)

        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)

        yield from alignement_xrr_xmotor(angle=0.1)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)

        ai0 = prs.position
        print('ai is', prs.position)
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):

                    yield from bps.mv(prs, ai0 - ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                    
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
                    
                    yield from bps.mv(energy, 13520)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 13480)
                    yield from bps.sleep(2)

                yield from bps.mv(prs, ai0)
        (yield from inner())







def scan_nexafs_CrKedge():
    dets = [pil900KW]

    name='nexafs_Credge_test'
    energies = np.linspace(13450, 13550, 51)

    # energies = [13450, 13460, 13470, 13480, 13482, 13484, 13485, 13486, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
    #             13495, 13496, 13497, 13498, 13499, 13500, 13501, 13502, 13503, 13504, 13505, 13506, 13507, 13508, 13509, 13510, 
    #             13515, 13520, 13530, 13550, 13570, 13590]
    
    energies = np.linspace(5970, 6020, 51)

    waxs_arc = [20]
    ai_list = [1.0]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                name_fmt = ("{sample}_{energy}eV_wa{wax}_ai1.6deg")
                sample_name = name_fmt.format(sample = name,energy = "%.2f" % e , wax = wa)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner())




def sevralai_giwaxs_Cr_edge_2025_3(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):
    '''

    '''
    dets = [pil900KW]

    # names = [   'PVK25_076', 'DUT25_014', 'DUT25_015', 'JD25_055']    
    # x_piezo = [      -10000,       13000,       39000,      53000]
    # x_hexa = [            0,           0,           0,         12]    
    # y_piezo = [        4500,        4500,        4500,       4500]

    names = [   'JD25_055']    
    x_piezo = [       53000]
    x_hexa = [                12]    
    y_piezo = [           3700]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    # 38 energies
    energies = [5960.0, 5970.0, 5980.0, 5990.0, 5995.0, 5996.0, 5997.0, 5998.0, 5999.0, 6000.0, 6001.0, 6002.0,
                6003.0, 6004.0, 6005.0, 6006.0, 6007.0, 6008.0, 6009.0, 6010.0, 6011.0, 6012.0, 6013.0, 6014.0, 
                6015.0, 6016.0, 6017.0, 6018.0, 6019.0, 6020.0, 6022.0, 6024.0, 6026.0, 6028.0, 6030.0, 6035.0,
                6040.0, 6045.0, 6050.0, 6070.0]
    
    waxs_arc = [7, 20]
    ai_list = [0.2, 2]
    ai0_all = 0
    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):

        yield from bps.mv(stage.x, xs_hexa,
                        piezo.x, xs,
                        piezo.y, ys,
                        piezo.th, ai0_all)
        
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(1)
        
        yield from alignement_gisaxs_rough(0.1)
        yield from alignement_gisaxs_rough(0.1)

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        print('ai0 is', ai0)
        det_exposure_time(t, t)

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
                        yield from bps.sleep(2)
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.3f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        s.put(sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
                    
                    yield from bps.mv(energy, 6020)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 5990)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.th, ai0)
        (yield from inner())



def giwaxs_Milo_2026_1(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):

    names = [   'P2', 'P2_annealed',  'P3',  'P3_annealed']    
    x_piezo = [43000,         27000, 13000,          -3000]
    x_hexa = [     0,             0,     0,              0]    
    y_piezo = [ 3700,          3700,  3700,           3700]
    

    names = [   'P3',  'P3_annealed']    
    x_piezo = [ 13000,          -3000]
    x_hexa = [      0,              0]    
    y_piezo = [  3700,           3700]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 20]
    ai0_all = 0.5
    ai_list = [0.10, 0.16, 0.20]
    xstep = 0
    
    dets = [pil2M, pil900KW]

    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        if name!='P3':
            yield from bps.mv(stage.x, xs_hexa,
                            piezo.x, xs,
                            piezo.y, ys,
                            piezo.th, ai0_all)
            yield from alignement_gisaxs_doblestack(0.15)
            print('alignement done')

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        (yield from inner())



def swaxs_Milo_2026_1(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    waxs_arc = [20]


    names   = [   'HES15per_00min', 'HES15per_10min','HES15per_20min','HES15per_30min']
    piezo_x = [     38000,   21000,   4000,   -23000]
    piezo_y = [     -6100,    -6500,  -6000,   -6000]

    # Offsets for taking a few points per sample
    x_off = [-400, 0, 400]
    y_off = [0, 400]

    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)

            for name, x, y in zip(names, piezo_x, piezo_y):
                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)





def P_edge_measurments_2026_1_MattLandsmann(t=1):
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)

    names = ['blank_50nm', 'phospA1', 'phospB1', 'phospC1', 'phospD1', 'phospE1']             
    x_piezo = [     42230,     36230,    30000,      24000,     18700,     13000]
    y_piezo = [     -3976,     -4376,    -4176,      -4076,     -3876,     -3476]
    z_piezo = [      3100,      3100,     3100,       3100,      3100,      3100]
 

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"

    energies = np.asarray([2130.0, 2135.0, 2140.0, 2145.0, 2146.0, 2147.0, 2148.0, 2148.5, 2149.0, 2149.5, 2150.0, 2150.5, 2151.0, 2151.5, 2152.0,
    2152.5, 2153.0, 2153.5, 2154.0, 2154.5, 2155.0, 2155.5, 2156.0, 2156.5, 2157.0, 2158.0, 2159.0, 2160.0, 2165.0, 2170.0, 2175.0, 2180.0, 2185.0, 
    2190.0, 2195.0, 2200.0, 2210.0])

    waxs_arc = [20, 7]

    for name, xs, ys, zs in zip(names, x_piezo, y_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys,
                          piezo.z, zs)

        if name =='blank_50nm' or name == 'phospE1':
            yss = np.linspace(ys, ys + 0, len(energies))

        else:
            yss = np.linspace(ys, ys + 1000, len(energies))
        
        if name =='blank_50nm':
            waxs_arc = [7]
        else:
            waxs_arc = [20, 7]

        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}"
                for e, y in zip(energies, yss):
                    yield from bps.mv(energy, e)
                    yield from bps.mv(piezo.y, y)
                    
                    yield from bps.sleep(3)
                    if xbpm3.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(1)
                    
                    bpm = xbpm3.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

        (yield from inner())

        yield from bps.mv(energy, 2190)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2170)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2150)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2140)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2130)
        yield from bps.sleep(2)



def P_edge_nexafs_measurments_2026_1_MattLandsmann(t=1):
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)
 
    names = [   'NaH2PO4',   'AMP', 'liyan1', 'liyan2', 'liyan3', 'liyan4', 'liyan5']             
    x_piezo = [    -46500,  -35000,   -21000,    -9000,     4000,    18000,    30000]
    y_piezo = [      4178,    3553,     3753,     3753,     3903,     3903,     4000]

    names = [    'liyan6','terri1', 'terri2', 'terri3', 'terri4', 'terri5', 'terri6']             
    x_piezo = [    -44000,  -31000,   -20000,    -9000,     5000,    16000,    28000]
    y_piezo = [      3650,    3500,     4050,     3800,     3900,     3750,     3820]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    energies = np.asarray([2130.0, 2135.0, 2140.0, 2145.0, 2146.0, 2147.0, 2148.0, 2149.0, 2150.0, 2151.0, 2152.0,
    2153.0, 2153.5, 2154.0, 2154.5, 2155.0, 2155.5, 2156.0, 2156.5, 2157.0, 2157.5, 2158.0, 2158.5, 2159.0, 2159.5, 
    2160.0, 2161.0, 2162.0, 2163.0, 2164.0, 2165.0, 2170.0, 2175.0, 2180.0, 2185.0, 2190.0, 2195.0, 2200.0, 2210.0])

    waxs_arc = [15]

    for name, xs, ys in zip(names, x_piezo, y_piezo):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    
                    yield from bps.sleep(3)
                    if xbpm3.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(1)
                    
                    bpm = xbpm3.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

        (yield from inner())

        yield from bps.mv(energy, 2190)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2170)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2150)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2140)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2130)
        yield from bps.sleep(2)




def nexafs_Pedge_2026_1():
    dets = [pil900KW, pil2M]

    name='nexafs_test'
    energies = np.linspace(2140, 2180, 41)

    waxs_arc = [20]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(3)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                bpm = xbpm3.sumX.get()
                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner())
    yield from bps.mv(energy, 2190)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2170)
    yield from bps.sleep(2)    
    yield from bps.mv(energy, 2150)
    yield from bps.sleep(2)    
    yield from bps.mv(energy, 2140)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 2130)
    yield from bps.sleep(2)



def P_edge_measurments_2026_1_gisaxs_Marie(t=1):
    dets = [pil900KW]
    det_exposure_time(t, t)

    names = ['sampleE', 'sampleF', 'sampleG', 'sampleH', 'sampleI', 'sampleA', 'sampleB']             
    x_piezo = [ -55000,    -45000,    -24000,     -3000,     18000,     38000,     52000]
    x_hexa = [      -9,         0,         0,         0,         0,         0,         7]      
    y_hexa = [       0,         0,         0,         0,         0,         0,         0]
    y_piezo = [   5000,      5000,      5000,      5000,      5000,      5000,      5000]
    z_piezo = [      0,         0,         0,         0,         0,         0,         0]
   
    names = [  'sampleB']             
    x_piezo = [    52000]
    x_hexa = [         7]      
    y_hexa = [         0]
    y_piezo = [     5000]
    z_piezo = [        0]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(z_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(z_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(y_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_hexa)})"

    energies = np.asarray([2130.0, 2135.0, 2140.0, 2145.0, 2146.0, 2146.5, 2147.0, 2147.5, 2148.0, 2148.5, 2149.0, 2149.5, 2150.0, 2150.5, 2151.0,
    2151.5, 2152.0, 2152.5, 2153.0, 2153.5, 2154.0, 2154.5, 2155.0, 2155.5, 2156.0, 2157.0, 2158.0, 2159.0, 2160.0, 2165.0, 2170.0, 2175.0, 2180.0, 2185.0, 
    2190.0, 2195.0, 2200.0, 2210.0])

    waxs_arc = [7]
    ai0_all = 0.75
    ai_list = [4.0]

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):
        x_step = 30

        yield from bps.mv(stage.x, xs_hexa,
                        stage.y, ys_hexa,
                        piezo.x, xs,
                        # piezo.y, ys,
                        piezo.z, zs)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.5)

        ai0 = piezo.th.position
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                yield from bps.mv(piezo.x, xs)
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(3)
                        if xbpm3.sumX.get() < 50:
                            yield from bps.sleep(2)
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(1)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())

        yield from bps.mv(energy, 2190)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2170)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2150)
        yield from bps.sleep(2)    
        yield from bps.mv(energy, 2140)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2130)
        yield from bps.sleep(2)



# Modify list of angles
# Modify attenuators
# ...


def xrr_Pedge_2025_6():
    #List of incident angles clustured in subsection for attenuators
    names = ['sampleE', 'sampleF', 'sampleG', 'sampleH', 'sampleI', 'sampleA', 'sampleB']             
    x_piezo = [ -55000,    -45000,    -24000,     -3000,     18000,     38000,     52000]
    x_hexa = [      -9,         0,         0,         0,         0,         0,         7]      
    y_hexa = [       0,         0,         0,         0,         0,         0,         0]
    y_piezo = [   5000,      5000,      5000,      5000,      5000,      5000,      5000]
    z_piezo = [      0,         0,         0,         0,         0,         0,         0]

    names = ['sampleA', 'sampleB']             
    x_piezo = [  38000,     52000]
    x_hexa = [       0,         7]      
    y_hexa = [       0,         0]
    y_piezo = [   5000,      5000]
    z_piezo = [      0,         0]

    angles =             np.linspace(0.03, 1.05, 69).tolist()
    angles +=            np.linspace(1.05,  2.01, 41).tolist()
    angles +=            np.linspace(2.01,  2.51, 35).tolist()
    angles +=            np.linspace(2.51, 4, 51).tolist()
    angles +=            np.linspace(4, 6, 41).tolist()
    angles +=            np.linspace(6, 8, 41).tolist()
    

    energies = [2130, 2147, 2150, 2180]

    attenuator5 = [att5(angle) for angle in angles]
    attenuator6 = [att6(angle) for angle in angles]
    attenuator7 = [att7(angle) for angle in angles]
    attenuator9 = [att9(angle) for angle in angles]
    attenuator10 = [att10(angle) for angle in angles]
    attenuator11 = [att11(angle) for angle in angles]

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):
        if name!='sampleE':
            yield from bps.mv(stage.x, xs_hexa,
                            stage.y, ys_hexa,
                            piezo.x, xs,
                            piezo.z, zs)

            yield from bps.mv(waxs.arc, 15)

            yield from alignement_gisaxs_doblestack(0.5)
            
            yield from bps.mv(waxs.arc,7)
        th0 = piezo.th.position
        print('Theta aligned', th0)
        angles0 = [th0 + angle for angle in angles]
        for en in energies:
            print('The sample measured is ', name)
            print('The energy is ', en)

            while abs(energy.energy.position-en)>20:
                if energy.energy.position>en:
                    yield from bps.mv(energy, energy.energy.position-10)
                    yield from bps.sleep(3)
                else:
                    yield from bps.mv(energy, energy.energy.position+10)
                    yield from bps.sleep(3)

            yield from bps.mv(energy, en)
            yield from bps.sleep(3)
            name_fmt = "{sample}_{energy}eV"
            sample_name = name_fmt.format(sample=name, energy="%6.2f"%en)
            sample_id(user_name="GF", sample_name=sample_name)

            yield from bp.list_scan([pil900KW],
                                    piezo.th, angles0, 
                                    att2_11, attenuator11,
                                    att2_10, attenuator10, 
                                    att2_9, attenuator9,
                                    att2_7,attenuator7,
                                    att2_6,attenuator6, 
                                    att2_5,attenuator5,)
            
        yield from bps.mv(piezo.th, th0)

def att11(angle):
    if angle < 1.4:
        return 0
    elif angle < 1.7:
        return 1
    else:
        return 0
    
def att10(angle):
    if angle < 1.7:
        return 0
    elif angle < 3.6:
        return 1 
    else:
        return 0
    
def att9(angle):
    if angle < 1.7:
        return 0
    elif angle < 2.1:
        return 1
    elif angle < 3.6:
        return 0
    elif angle < 4.8:
        return 1
    else:
        return 0


def att7(angle):
    if angle < 0.5:
        return 1
    else:
        return 0
        
def att6(angle):
    if angle < 0.5:
        return 0
    elif angle < 1.0:
        return 1
    else:
        return 0
    
def att5(angle):
    if angle < 0.5:
        return 0
    elif angle < 0.7:
        return 1
    elif angle < 1.0:
        return 0
    elif angle < 1.4:
        return 1
    else:
        return 0
    




def Cl_edge_Lucas_2026_1(t=1):
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)
 
    names = [   'SiO2_KCl_att9_1x_down']             
    x_piezo = [       200]
    y_piezo = [     -2500]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    #KCl
    energies = -10 + np.asarray([2810.0, 2820.0, 2828.0, 2829.0, 2830.0, 2831.0, 2832.0, 2833.0, 2834.0, 2834.5, 2835.0, 2835.5, 2836.0, 2836.5, 2837.0, 2837.5, 2838.0, 2838.5, 2839.0,
    2839.5, 2840.0, 2840.5, 2841.0, 2841.5, 2845.0, 2850.0, 2855.0, 2860.0, 2865.0, 2870.0, 2875.0, 2880.0, 2890.0])
 
    waxs_arc = [15]

    for name, xs, ys in zip(names, x_piezo, y_piezo):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    
                    yield from bps.sleep(3)
                    if xbpm3.sumX.get() < 50:
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(1)
                    
                    bpm = xbpm3.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

        (yield from inner())




def K_edge_Lucas_2026_1(t=1):
    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)
 
    names = [   'SiO2_KCl_att9_1x']             
    x_piezo = [       200]
    y_piezo = [     -2500]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    #KCl
    energies = np.asarray(np.arange(3580, 3611, 5).tolist() + 
                          np.arange(3612, 3629, 1).tolist() + 
                          np.arange(3630, 3700, 5).tolist())
    
    waxs_arc = [15]

    for name, xs, ys in zip(names, x_piezo, y_piezo):
        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys)
        det_exposure_time(t, t)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                name_fmt = "{sample}_pos1_{energy}eV_wa{wax}_bpm{xbpm}"
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(3)
                    
                    bpm = xbpm3.sumX.get()
                    sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])

                name_fmt = "{sample}_pos2_{energy}eV_wa{wax}_bpm{xbpm}"
                for e in energies[::-1]:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(3)

                    bpm = xbpm3.sumX.get()
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att2_9] + [s])


        (yield from inner())





def swaxs_Fei_2026_1(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """



    waxs_arc = [40, 20, 0]

    # names   = [  'A1',  'A2',  'A3',  'A4',  'A5',  'A6',
    #              'B1',  'B2',  'B3',  'B4',  'B5',  'b6',
    #              'C1',  'C2',  'C3',  'C4',  'C5',  'C6',
    #              'D1',  'D2',  'D3',  'D4',  'D5',  'D6',

    #              'E1',  'E2',  'E3',  'E4',  'E5',  'E6',
    #              'F1',  'F2',  'F3',  'F4',  'F5',  'F6',
    #              'G1',  'G2',  'G3',  'G4',  'G5',  'G6',
    #              'H1',  'H2',  'H3',  'H4',  'H5',  'H6']
    
    # piezo_x = [-51800,-42000,-33000,-24000,-15500, -7000,
    #            -51000,-42000,-33000,-24500,-15500, -7000,
    #            -51000,-42500,-33700,-24500,-15000, -6500,
    #            -52000,-42500,-33500,-24500,-15500, -6500,
                
    #              5000, 13100, 22200, 31200, 40200, 49200, 
    #              5000, 13500, 22500, 31000, 40000, 49200,
    #              4500, 13800, 22000, 31000, 40500, 49200,
    #              4000, 13200, 22200, 31200, 40200, 49200]
    
    # piezo_y = [ -6500, -6600, -6600, -6600, -6600, -6600,
    #             -6600, -6600, -6600, -6600, -6600, -6600,
    #             -2000, -2000, -1600, -1500, -1600, -1500,
    #              3200,  3000,  3000,  3000,  3000,  3000,
                  
    #             -6500, -6500, -6000, -6000, -6000, -6000,
    #             -6000, -6000, -6000, -6000, -6000, -6000,
    #             -2000, -2000, -2000, -2000, -2000, -2000,
    #              3300,  3500,  3500,  3800,  3800,  3800,]
    
    # hexa_y =  [    -6,    -6,    -6,    -6,     -6,   -6,
    #                -1,    -1,    -1,    -1,     -1,   -1,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,

    #                -6,    -6,    -6,    -6,     -6,   -6,
    #                -1,    -1,    -1,    -1,     -1,   -1,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,]
    
    # hexa_x =  [     0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,

    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,
    #                 0,     0,     0,     0,      0,    0,]


    names   = [  'I1',  'I2',  'I3',  'I4',  'I5',  'I6',
                 'J1',  'J2',  'J3',  'J4',  'J5',  'J6',
                 'K1',  'K2',  'K3',  'K4',  'K5',  'K6',
                 'L1',  'L2',  'L3',  'L4',  'L5',  'L6',

                 'M1',  'M2',  'M3',  'M4',  'M5',  'M6',
                 'N1',  'N2',  'N3',  'N4',  'N5',  'N6',
                 'O1',  'O2',  'O3',  'O4',  'O5',  'O6',
                 'P1',  'P2',  'P3',  'P4',  'P5',  'P6']
    
    piezo_x = [-51800,-43000,-34000,-24000,-15500, -6500,
               -51500,-42500,-33500,-24500,-15500, -6500,
               -51500,-42500,-33500,-24500,-15500, -6500,
               -52000,-42500,-33900,-24500,-15500, -6500,
                
                 4600, 13700, 22900, 31900, 40900, 49900, 
                 5400, 13900, 22900, 31900, 40900, 49900,
                 5400, 13900, 22900, 31900, 40900, 49900,
                 5100, 14400, 22600, 31700, 40900, 49900]
    
    piezo_y = [ -7000, -7000, -7000, -7000, -7000, -7000,
                -6500, -7100, -6100, -6100, -6000, -6600,
                -2300, -2300, -2300, -1900, -1900, -1900,
                 3000,  3000,  3000,  3000,  3000,  3000,
                  
                -7000, -7000, -6400, -6400, -6400, -6400,
                -6000, -6000, -6000, -6000, -6000, -6000,
                -2000, -2000, -2000, -1800, -1800, -1500,
                 3500,  3500,  3500,  3500,  3500,  3500,]
    
    hexa_y =  [  -6.5,    -6,    -6,    -6,     -6,   -6,
                   -1,    -1,    -1,    -1,     -1,   -1,
                    0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,

                   -6,    -6,    -6,    -6,     -6,   -6,
                   -1,    -1,    -1,    -1,     -1,   -1,
                    0,     0,     0,     0,      0,    0,
                    0,     0,     0,     0,      0,    0,]
    
    hexa_x =  [     3,     3,     3,     3,      3,    3,
                    3,     3,     3,     3,      3,    3,
                    3,     3,     3,     3,      3,    3,
                    3,     3,     3,     3,      3,    3,

                    1,     1,     1,     1,      1,    1,
                    1,     1,     1,     1,      1,    1,
                    1,     1,     1,     1,      1,    1,
                    1,     1,     1,     1,      1,    1,]


    # Offsets for taking a few points per sample
    x_off = [-400, 0, 400]
    y_off = [-400, 0, 400]
    # y_off = [0, 400]
    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"
    assert len(piezo_x) == len(hexa_x), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_x)})"
    assert len(piezo_x) == len(hexa_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)

            for name, x, y, hex_x, hex_y in zip(names, piezo_x, piezo_y, hexa_x, hexa_y):
                yield from bps.mv(stage.y, hex_y,
                                  stage.x, hex_x)

                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)




def swaxs_Fei_2026_1_finegrid(t=1):
    """
    Take WAXS and SAXS at nine sample positions for averaging

    Specify central positions on the samples with xlocs and ylocs,
    then offsets from central positions with x_off and y_off. Run
    WAXS arc as the slowest motor. SAXS sdd 4.0 m.
    """

    waxs_arc = [40, 20, 0]


    names   = [  'Q1',  'Q2',  'Q3',  'Q4',   'Q5',   'Q6']
    piezo_x = [ 21200, 12200,  3200, -5900, -14400, -23100]
    piezo_y = [ -4200, -4600, -5000, -5200,  -5100,  -5000]
    hexa_y =  [    -5,    -5,    -5,    -5,     -5,     -5]
    hexa_x =  [     0,     0,     0,     0,      0,      0]

    # Offsets for taking a few points per sample
    x_off = [-400, -200, 0, 200, 400]
    y_off = [-400, -300, -200, -100, 0, 100, 200, 300, 400]

    user = "GF"

    # Check if the length of xlocs, ylocs and names are the same
    assert len(piezo_x) == len(names), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(names)})"
    assert len(piezo_x) == len(piezo_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(piezo_y)})"
    assert len(piezo_x) == len(hexa_x), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_x)})"
    assert len(piezo_x) == len(hexa_y), f"Number of X coordinates ({len(piezo_x)}) is different from number of samples ({len(hexa_y)})"

    dets = [pil2M, pil900KW]

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            # Detectors, disable SAXS when WAXS in the way
            det_exposure_time(t, t)
                
            for name, x, y, hex_x, hex_y in zip(names, piezo_x, piezo_y, hexa_x, hexa_y):
                yield from bps.mv(stage.y, hex_y,
                                  stage.x, hex_x)
                
                for yy, y_of in enumerate(y_off):
                    yield from bps.mv(piezo.y, y + y_of)

                    for xx, x_of in enumerate(x_off):
                        yield from bps.mv(piezo.x, x + x_of)
                        yield from bps.sleep(1)

                        loc = f'{yy}{xx}'
                        sample_name = f'{name}{get_scan_md()}_loc{loc}'
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])

    (yield from inner())

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)


    angles =             np.linspace(0.03, 1.05, 69).tolist()
    angles +=            np.linspace(1.05,  2.01, 41).tolist()
    angles +=            np.linspace(2.01,  2.51, 35).tolist()
    angles +=            np.linspace(2.51, 4, 51).tolist()
    angles +=            np.linspace(4, 6, 41).tolist()
    angles +=            np.linspace(6, 8, 41).tolist()



def xrr_Pedge_2026_1_new(t=1):
    #List of incident angles clustured in subsection for attenuators
    names = ['sampleE', 'sampleF', 'sampleG', 'sampleH', 'sampleI', 'sampleA', 'sampleB']             
    x_piezo = [ -55000,    -45000,    -24000,     -3000,     18000,     38000,     52000]
    x_hexa = [      -9,         0,         0,         0,         0,         0,         7]      
    y_hexa = [       0,         0,         0,         0,         0,         0,         0]
    y_piezo = [   5000,      5000,      5000,      5000,      5000,      5000,      5000]
    z_piezo = [      0,         0,         0,         0,         0,         0,         0]

    names = ['sampleF', 'sampleG', 'sampleH', 'sampleI', 'sampleA', 'sampleB']             
    x_piezo = [ -45000,    -24000,     -3000,     18000,     38000,     52000]
    x_hexa = [       0,         0,         0,         0,         0,         7]      
    y_hexa = [       0,         0,         0,         0,         0,         0]
    y_piezo = [   5000,      5000,      5000,      5000,      5000,      5000]
    z_piezo = [      0,         0,         0,         0,         0,         0]

    names = ['sampleE', 'sampleF', 'sampleG', 'sampleC', 'sampleD']             
    x_piezo = [  51000,     30700,     10000,    -22000,    -47000]
    x_hexa = [       0,         0,         0,         0,         0]      
    y_hexa = [       0,         0,         0,         0,         0]
    y_piezo = [   5500,      5500,      5500,      5500,      5500]
    z_piezo = [      0,         0,         0,         0,         0]


    angles =            np.linspace(2.01,  2.51, 35).tolist()
    angles +=            np.linspace(2.51, 4, 51).tolist()
    angles +=            np.linspace(4, 6, 41).tolist()
    angles +=            np.linspace(6, 12, 121).tolist()
    

    energies = [2130, 2147, 2149, 2180]

    atte9 = np.array([att9(angle) for angle in angles])
    atte10 = np.array([att10(angle) for angle in angles])

    th0_afteralignement = -2

    for name, xs, ys, zs, xs_hexa, ys_hexa in zip(names, x_piezo, y_piezo, z_piezo, x_hexa, y_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                        stage.y, ys_hexa,
                        piezo.x, xs,
                        piezo.z, zs)

        yield from bps.mv(waxs.arc, 15)
        yield from bps.mv(stage.th, 2)
        yield from bps.mv(piezo.th, th0_afteralignement)

        yield from alignement_gisaxs_doblestack(0.5)

        th0_afteralignement = piezo.th.position
        print('Theta aligned', th0_afteralignement)
        yield from bps.mv(waxs.arc,7)

        th_0 = piezo.th.position
        
        angles_sma = np.array([th_0 + angle for angle in angles])
        angleshe = np.array([2]*len(angles))
        idx = np.where(angles_sma>5)
        angles_sma[idx] -= 5 
        angleshe[idx] = 7
        idx2 = np.where(angles_sma<5.1)
        angles_smaract = angles_sma[idx2]
        angleshex = angleshe[idx2]
        
        attenuator9 = atte9[idx2]
        attenuator10 = atte10[idx2]


        det_exposure_time(t, t)
        
        print('Theta smaract', angles_smaract)
        print('Theta hex', angleshex)


        for en in energies:
            print('The sample measured is ', name)
            print('The energy is ', en)

            while abs(energy.energy.position-en)>20:
                if energy.energy.position>en:
                    yield from bps.mv(energy, energy.energy.position-10)
                    yield from bps.sleep(3)
                else:
                    yield from bps.mv(energy, energy.energy.position+10)
                    yield from bps.sleep(3)

            yield from bps.mv(energy, en)
            yield from bps.sleep(3)
            name_fmt = "{sample}_{energy}eV"
            sample_name = name_fmt.format(sample=name, energy="%6.2f"%en)
            sample_id(user_name="GF", sample_name=sample_name)

            yield from bp.list_scan([pil900KW], 
                                    piezo.th, angles_smaract, 
                                    stage.th, angleshex, 
                                    att2_10, attenuator10, 
                                    att2_9, attenuator9)
            
    
def att10(angle):
    if angle < 3.6:
        return 1 
    else:
        return 0
    
def att9(angle):
    if angle < 3.6:
        return 0
    elif angle < 4.8:
        return 1
    else:
        return 0
    






def giwaxs_Br_edge_2026_1(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):

    dets = [pil900KW]

    names = [   'GF_E1_CAN1', 'GF_E1_CAN2', 'GF_E2_CAN1', 'GF_E2_CAN2', 'GF_bkg', 'RL_SNPB_S1']    
    x_piezo = [       -48200,       -37500,       -20000,        -8500,     9500,        18000]
    y_piezo = [       3778.2,         3778,         3778,         3778,     3778,         3778]

    names = [   'GF_bkg', 'RL_SNPB_S1']    
    x_piezo = [     4500,        18000]
    y_piezo = [     3778,         3778]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"

    # 26 energies
    energies_long = [13450, 13470, 13480, 13485, 13488, 13489, 13490, 13491, 13492, 13493, 13494, 13495, 13496, 
                     13497, 13498, 13499, 13500, 13504, 13509, 13510, 13515, 13520, 13530, 13550, 13570, 13590]
    # 10 energies
    energies_short = [13450, 13485, 13490, 13491, 13493, 13494,13499, 13504, 13515, 13590]
    
    # 18 energies
    energies_med = [13450, 13470, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494, 13495, 13496, 13500, 
                    13504, 13509, 13520, 13550, 13590]
    
    waxs_arc = [7]
    ai0_all = 0.2
    ai_list = [0.1, 0.12, 0.3]
    
    for name, xs, ys in zip(names, x_piezo, y_piezo):
        x_space=300
        if name=='RL_SNPB_S1':
            ai_list = [0.05, 0.10, 0.20]
        else:
            ai_list = [0.1, 0.12, 0.30]

        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys,
                          piezo.th, ai0_all)
        
        yield from alignement_gisaxs_doblestack(0.1)

        yield from bps.mv(att1_9.open_cmd, 1)
        yield from bps.sleep(1)
        yield from bps.mv(att1_9.open_cmd, 1)
        yield from bps.sleep(1)

        ai0 = piezo.th.position
        print('ai0 is', ai0)
        det_exposure_time(t, t)


        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():

            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                yield from bps.mv(piezo.x, xs)

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    for energies in [energies_long, energies_med, energies_short]:
                        yield from bps.mvr(piezo.x, x_space)
                        name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                        for e in energies:
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)
                            
                            bpm = xbpm3.sumX.get()
                            sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                            print(f"\n\t=== Sample: {sample_name} ===\n")
                            s.put(sample_name)
                            yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])

                        yield from bps.mvr(piezo.x, x_space)
                        name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                        for e in energies[::-1]:
                            yield from bps.mv(energy, e)
                            yield from bps.sleep(2)

                            bpm = xbpm3.sumX.get()
                            sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                            print(f"\n\t=== Sample: {sample_name} ===\n")
                            s.put(sample_name)
                            yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])

                yield from bps.mv(piezo.th, ai0)

        (yield from inner())            


def nexafs_Bredge_2026_1():
    dets = [pil900KW, pil2M]

    name='nexafs_GF_E1_CAN_att1_9x_ai0.2deg'
    energies = [13450, 13470, 13480, 13485, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
                13495, 13496, 13497, 13498, 13499, 13500, 13504, 13509, 13510, 
                13515, 13520, 13530, 13550, 13570, 13590]

    energies = [13450, 13485, 13490, 13491, 13493, 13494,13499, 13504, 13515, 13590]
    
    energies = [13450, 13470, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494,
                13495, 13496, 13500, 13504, 13509, 13520, 13550, 13590]

    waxs_arc = [7]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                bpm = xbpm3.sumX.get()
                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner())
    
    yield from bps.mv(energy, 13500)
    yield from bps.sleep(2)
    yield from bps.mv(energy, 13450)
    yield from bps.sleep(2)    



def aiscan_giwaxs_S_edge_2026_1(t=1, energies=2450, name="Test", waxs_arc=[18]):
    '''
    Study the beam damage on 1 film to define the opti;am experimental conitions.

    '''
    dets = [pil900KW]
    det_exposure_time(t, t)
    
    yield from bps.mv(energy, energies)
    yield from bps.sleep(2)
    yield from bps.mv(energy, energies)
    yield from bps.sleep(2)

    # waxs_arc = [18]
    ai_list = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]   
    ai0 = piezo.th.position

    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            
            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                name_fmt = "aiscan_{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"

                bpm = xbpm3.sumX.get()
                sample_name = name_fmt.format(sample=name,energy="%6.2f"%energies, ai="%3.3f"%ais, wax=waxs_arc[0], xbpm="%4.3f"%bpm)
                s.put(sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])
                yield from bps.sleep(1)

            yield from bps.mv(piezo.th, ai0)
    (yield from inner())





    # names = [   'GF_E1_CAN1', 'GF_E1_CAN2', 'GF_E2_CAN1', 'GF_E2_CAN2', 'GF_bkg', 'RL_SNPB_S1']    


def giwaxs_Br_edge_2026_1_onesample(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):
    dets = [pil900KW]
    name = 'GF_E2_CAN2_pos7_shortenergysweep_updown'    

    # name = 'GF_E1_CAN1_pos2_medenergy_dnsweep'    

    #sa04
    #th0 = 0.193
    #y = 3961


    # 26 energies
    energies_long = [13450, 13470, 13480, 13485, 13488, 13489, 13490, 13491, 13492, 13493, 13494, 13495, 13496, 
                     13497, 13498, 13499, 13500, 13504, 13509, 13510, 13515, 13520, 13530, 13550, 13570, 13590]

    # 18 energies
    energies_med = [13450, 13470, 13487, 13488, 13489, 13490, 13491, 13492, 13493, 13494, 13495, 13496, 13500, 
                    13504, 13509, 13520, 13550, 13590]
    
    energies_short = [13450, 13485, 13490, 13491, 13493, 13494,13499, 13504, 13515, 13590]

    
    energiess = energies_short

    waxs_arc = [7]
    ai_list = [0.3]
    
    yield from bps.mv(att1_9.open_cmd, 1)
    yield from bps.sleep(1)
    yield from bps.mv(att1_9.open_cmd, 1)
    yield from bps.sleep(1)

    ai0 = piezo.th.position
    print('ai0 is', ai0)
    det_exposure_time(t, t)


    s = Signal(name='target_file_name', value='')
    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():

        for i, wa in enumerate(waxs_arc):
            # yield from bps.mv(waxs, wa)

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ai0 + ais)
                for energies in [energiess]:
                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])
                    
                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies[::-1]:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])

            yield from bps.mv(piezo.th, ai0)

    (yield from inner())            



def nexafs_Ptedge_2026_1():
    dets = [pil900KW]

    name='nexafs_GF_Ptedge'
    energies = np.linspace(11555, 11605, 51)

    waxs_arc = [15]

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)

            for i, e in enumerate(energies):
                yield from bps.mv(energy, e)
                yield from bps.sleep(2)
                
                # Metadata
                wa = str(np.round(float(wa), 1)).zfill(4)

                # Sample name
                bpm = xbpm3.sumX.get()
                name_fmt = "{sample}_{energy}eV_wa{wax}_bpm{xbpm}"
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, wax=wa, xbpm="%4.3f"%bpm)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner()) 


def giswaxs_align_all(t=0.5):
    """
    Grazing incidence measurement for Fred Barbier, sdd = 9.2 m, E = 16.1keV LowDiv
    """

    dets = [pil2M]
    det_exposure_time(t, t)

    # names = [  'sa02', 'sa03', 'sa04_poreux', 'sa04_bord', 'sa05', 'sa06', 'sa07']
    # x_piezo = [ 48000,  24000,          4000,      -12000, -26000, -38000, -50000]
    # y_piezo = [  -300,    -300,          -300,        -300,   -300,   -300,   -300]
    # x_hexa =  [     0,      0,             0,           0,      0,      0,      0]

    names = [ 'PTFE_pristine','END5666_25HP','END5667_40HP','END5668_110HP','END5669_40IR','END5670_110IR',
              'END5671_40MW','END5672_110MW','END5673_25VO','END5674_40VO']
    x_piezo = [ 55000,  52000,  39000,  25000, 11000, -3000, -18000, -32000, -46000, -54000]
    x_hexa =  [     9,      0,      0,      0,      0,     0,     0,      0,      0,     -8]
    ai_all = []
    y_all=[]

    for name, xs, xs_hexa in zip(names, x_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa, 
                          piezo.x, xs)

        yield from alignement_gisaxs_short(angle=0.15)
        ai0 = piezo.th.position
        y0 = piezo.y.position

        print(name, ai0, y0)
        ai_all = ai_all + [ai0]
        y_all = y_all + [y0]
        
        print(ai_all)
        print(y_all)




def giswaxs_vincent_2026_1(t=0.5):
    """
    Grazing incidence measurement for Fred Barbier, sdd = 9.2 m, E = 16.1keV LowDiv
    """

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)


    names = [ 'PTFE_pristine','END5666_25HP','END5667_40HP','END5668_110HP','END5669_40IR','END5670_110IR',
              'END5671_40MW','END5672_110MW','END5673_25VO','END5674_40VO']
    x_piezo = [ 55000,  52000,  39000,  25000, 11000, -3000, -18000, -32000, -46000, -54000]
    x_hexa =  [     9,      0,      0,      0,      0,     0,     0,      0,      0,     -8]
    y_piezo = [  4283.174,   3954.5,   4316.817,  4087.033,  4257.556,  3898.791, 3969.575, 3893.011,  3892.141, 3858.028]
    th_piezo = [-0.953633, 1.354059, -0.0305567, -1.415172, -0.838249, -0.261326, 0.315597,-0.492095, -0.145941, -0.261326]



    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(y_piezo)}) is different from number of samples ({len(x_hexa)})"
    assert len(x_piezo) == len(th_piezo), f"Number of X coordinates ({len(th_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [20, 7]
    ai0 = 0
    ai_list = [0.15, 0.30, 0.5]
    
    det_exposure_time(t, t)


    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)

        for name, xs, ys, xs_hexa, ths in zip(names, x_piezo, y_piezo, x_hexa, th_piezo):
            yield from bps.mv(stage.x, xs_hexa, 
                              piezo.x, xs, 
                              piezo.y, ys, 
                              piezo.th, ths)

            for k, ais in enumerate(ai_list):
                yield from bps.mv(piezo.th, ths + ais)

                sample_name = f'{name}_ai{ais}deg_pos1_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

                yield from bps.mv(piezo.x, xs-1000)
                yield from bps.sleep(1)

                sample_name = f'{name}_ai{ais}deg_pos2_{get_scan_md()}'
                sample_id(user_name='GF', sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(dets, num=1)
                yield from bps.sleep(1)

            yield from bps.mv(piezo.th, ai0)



def swaxs_vincent_2026_1(t=0.5):
    """
    Grazing incidence measurement for Fred Barbier, sdd = 9.2 m, E = 16.1keV LowDiv
    """

    dets = [pil2M, pil900KW]
    det_exposure_time(t, t)


    names = [ 'em[ty', 'END5670_110IR','END5669_40IR','END5668_110HP','END5667_40HP','END5666_25HP', 'PTFE_pristine',
              'END5318_106HP', 'END5675_110VO', 'END5674_40VO','END5673_25VO','END5672_110MW','END5671_40MW']
    x_piezo = [ -42000, -36136,  -19136,  -5000,  11000, 25000, 39000,
                -38000,  -19136,  -5000,  11000, 25000, 40000]
    y_piezo = [  -7000, -7000,   -7000,  -7000,  -7000, -7000, -7000, 
                  5500,    5500,   5500,   5500,  5500,  5500]


    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(y_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [20, 7]
    
    det_exposure_time(t, t)

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)

        for name, xs, ys in zip(names, x_piezo, y_piezo):
            yield from bps.mv(piezo.x, xs, 
                              piezo.y, ys)

            sample_name = f'{name}_pos1_{get_scan_md()}'
            sample_id(user_name='GF', sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            yield from bps.sleep(1)

            yield from bps.mv(piezo.x, xs-1000)
            yield from bps.sleep(1)

            sample_name = f'{name}_pos2_{get_scan_md()}'
            sample_id(user_name='GF', sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            yield from bps.sleep(1)





def nexafs_Inedge_2026_1():
    dets = [pil900KW]

    name='nexafs_Incycle0_ai_0.25'
    energies = np.linspace(3720, 3770, 51)

    waxs_arc = [27]

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
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                s.put(sample_name)
                
                yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3] + [s])

            yield from bps.sleep(2)
    (yield from inner()) 





def giwaxs_In_edge_2026_1(t=1, name="Test", ai_list: list[int] = [], xstep=10, waxs_arc = [0, 20]):

    dets = [pil900KW]
    
    names = ["Incycle0_36V","Incycle0_144V","Incycle0_52V","Incycle8_52V","Incycle8_36V","Incycle8_144V",
             "Incycle4_36V","Incycle4_144V","Incycle4_52V","Incycle2_36V", "Incycle2_52V"]                      
    x_piezo = [   49500,     49500,    44500,    27500,    17500,   3000,
                 -31000,    -36500,   -41500,   -45100,   -55100]
    x_hexa = [        5,         0,        0,        0,        0,      0,
                      0,         0,        0,      -10,      -10]
    y_piezo = [  3214.0,    3263.4,   3278.3,   3473.2,   3473.2, 3656.0,    
                 4037.6,    4037.6,   4037.6,   4407.6,   4407.6]
    th_piezo = [-1.515,     -1.518,   -1.512,     -2.1,     -2.1,  -3.25,  
                -2.273,     -2.273,   -2.273,   -1.697,   -1.697]
    
    names = ["Incycle2_144V"]
    x_piezo = [ -2070]
    x_hexa = [ -10]
    y_piezo = [  3600.0] 
    th_piezo = [-1.515]  

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_hexa)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(th_piezo), f"Number of X coordinates ({len(th_piezo)}) is different from number of samples ({len(y_piezo)})"

    # 26 energies
    energies = [3720.0, 3730.0, 3735.0, 3736.0, 3737.0, 3738.0, 3738.5, 3739.0, 3739.5, 3740.0, 3740.5, 3741.0, 
                3741.5, 3742.0, 3742.5, 3743.0, 3744.0, 3745.0, 3746.0, 3747.0, 3750.0, 3755.0, 3760.0, 3765.0,
                3770.0, 3775.0, 3780.0, 3790.0, 3800.0, 3850.0]

    ai_list = [0.2, 0.4, 1.2]
    
    det_exposure_time(t, t)
    x_step=30
    wa = 26
    waxs_arc=[26]
    for name, xs, ys, xshexa, ths in zip(names, x_piezo, y_piezo, x_hexa, th_piezo):

        yield from bps.mv(piezo.x, xs,
                          piezo.y, ys,
                          stage.x, xshexa,
                          piezo.th, ths)
                
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from bps.sleep(3)  

        yield from alignement_gisaxs_doblestack(0.1)
        th0 = piezo.th.position

        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(3)
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.sleep(3)

        s = Signal(name='target_file_name', value='')
        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, th0 + ais)

                    name_fmt = "{sample}_pos1_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        
                        yield from bps.mv(piezo.x, xs + counter * x_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])
                   
                    yield from bps.mv(energy, 3800)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 3750)
                    yield from bps.sleep(2)
                counter_tot = counter
                counter = 0

                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, th0 + ais)

                    name_fmt = "{sample}_pos2_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                    for e in energies:
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                        
                        yield from bps.mv(piezo.x, xs + (counter_tot - counter) * x_step)
                        counter += 1
                        
                        bpm = xbpm3.sumX.get()
                        sample_name = name_fmt.format(sample=name, energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        s.put(sample_name)
                        yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, att1_9] + [s])
                   
                    yield from bps.mv(energy, 3800)
                    yield from bps.sleep(2)
                    yield from bps.mv(energy, 3750)
                    yield from bps.sleep(2)

                yield from bps.mv(piezo.th, th0)

        (yield from inner())            


def saxs_tensile(t=1):
    dets = [pil2M, pil900KW]
    names = "Rep_LCPE_run01"
    det_exposure_time(t, t)
    t0 = time.time()
    for i in range(5000):
        name_fmt = "{sample}_16100eV_sdd5.0m_wa17deg_{i}_{time}"
        t1 = time.time()
        sample_name = name_fmt.format(sample=names, i="%3.3d" % i, time="%1.1f" % (t1 - t0))
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)




def waxs_tensile(t=1):
    dets = [pil900KW]
    names = "Rep_LCPE_run02"
    det_exposure_time(t, t)
    t0 = time.time()
    for i in range(5000):
        name_fmt = "{sample}_16100eV_wa07deg_{i}_{time}"
        t1 = time.time()
        sample_name = name_fmt.format(sample=names, i="%3.3d" % i, time="%1.1f" % (t1 - t0))
        sample_id(user_name="GF", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)


#setthreshold energy 2450 uhighg 1600










def xrr_Pedge_insitu_2026_1(t=0.5):
    """
    """
    
    det_exposure_time(t, t)
    dets = [pil900KW]

    names = ['sampleA']             
    x_piezo = [  3100]
    y_piezo = [   400]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"


    angles = np.linspace(2.01,  2.51, 35).tolist()
    angles += np.linspace(2.51, 4, 51).tolist()
    angles += np.linspace(4, 6, 41).tolist()
    angles += np.linspace(6, 12, 121).tolist()

    energies = [2130, 2149, 2180]

    atte9 = np.array([att9(angle) for angle in angles])
    atte10 = np.array([att10(angle) for angle in angles])

    th0_afteralignement = -0.5

    # temperatures = [30, 100, 200, 300, 350, 400, 450, 500, 525, 550, 575, 600]
    temperatures = [525, 550, 575, 600]

    for temp in temperatures:
        LThermal.setTemperature(temp)
        
        while abs(LThermal.temperature() - temp) > 10:
            yield from bps.sleep(60)
            print('temp not at there yet')

        print('At temp equal ', temp)
        print('Wainting for 5 min')

        if temp !=525:
            yield from bps.sleep(300)
        temp_real = LThermal.temperature()

        for name, xs, ys in zip(names, x_piezo, y_piezo):
            # yield from bps.mv(piezo.x, xs,
            #                   piezo.y, ys_hexa)

            yield from bps.mv(waxs.arc, 15)
            yield from bps.mv(stage.th, 2)
            yield from bps.mv(piezo.th, th0_afteralignement)

            yield from alignement_gisaxs_doblestack(0.2)

            th0_afteralignement = piezo.th.position
            print('Theta aligned', th0_afteralignement)
            yield from bps.mv(waxs.arc,7)

            th_0 = piezo.th.position
            
            angles_sma = np.array([th_0 + angle for angle in angles])
            angleshe = np.array([2]*len(angles))
            idx = np.where(angles_sma>5)
            angles_sma[idx] -= 5 
            angleshe[idx] = 7
            idx2 = np.where(angles_sma<5.1)
            angles_smaract = angles_sma[idx2]
            angleshex = angleshe[idx2]
            
            attenuator9 = atte9[idx2]
            attenuator10 = atte10[idx2]

            det_exposure_time(t, t)
            
            print('Theta smaract', angles_smaract)
            print('Theta hex', angleshex)

            for en in energies:
                print('The sample measured is ', name)
                print('The energy is ', en)

                while abs(energy.energy.position-en)>20:
                    if energy.energy.position>en:
                        yield from bps.mv(energy, energy.energy.position-10)
                        yield from bps.sleep(3)
                    else:
                        yield from bps.mv(energy, energy.energy.position+10)
                        yield from bps.sleep(3)

                yield from bps.mv(energy, en)
                yield from bps.sleep(3)
                name_fmt = "{sample}_{energy}eV_{temp}C"
                sample_name = name_fmt.format(sample=name, energy="%6.2f"%en, temp="%.3d"%temp)
                sample_id(user_name="GF", sample_name=sample_name)

                yield from bp.list_scan([pil900KW], 
                                        piezo.th, angles_smaract, 
                                        stage.th, angleshex, 
                                        att2_10, attenuator10, 
                                        att2_9, attenuator9)
                
    LThermal.off()

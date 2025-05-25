# pil300KW for waxs, pil1M for saxs


def cd_saxs(th_ini, th_fin, th_st, exp_t=1):
    sample = ["cdsaxs_ech03_defectivity_pitch128","cdsaxs_ech03_defectivity_pitch127","cdsaxs_ech03_defectivity_pitch124",
              "cdsaxs_ech03_defectivity_pitch121","cdsaxs_ech03_defectivity_pitch118","cdsaxs_ech03_defectivity_pitch115",
              "cdsaxs_ech03_defectivity_pitch112","cdsaxs_ech04_defectivity_pitch128","cdsaxs_ech04_defectivity_pitch127",
              "cdsaxs_ech04_defectivity_pitch124","cdsaxs_ech04_defectivity_pitch121","cdsaxs_ech04_defectivity_pitch118",
              "cdsaxs_ech04_defectivity_pitch115","cdsaxs_ech04_defectivity_pitch112","cdsaxs_ech11b_defectivity_pitch128",
              "cdsaxs_ech11b_defectivity_pitch127","cdsaxs_ech11b_defectivity_pitch124","cdsaxs_ech11b_defectivity_pitch121",
              "cdsaxs_ech11b_defectivity_pitch118","cdsaxs_ech11b_defectivity_pitch115","cdsaxs_ech11b_defectivity_pitch112"]
    x = [-41100,-38550,-34050,-29550,-25050,-20550,-16050,-11150,-9650,-5150,-650,3850,8350,12850,17000,18500,23000,27500,32000,36500, 41000]
    y = [  2000,  2000,  2000,  2000,  2000,  2000,  2000,2000,2000,2000,2000,2000,2000,2000,3900,3900,3900,3900,3900,3900,3900,    ]    
    det = [pil1M]

    det_exposure_time(exp_t, exp_t)
    for xs, ys, sample in zip(x, y, sample):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        for theta in np.linspace(th_ini, th_fin, th_st):
            yield from bps.mv(prs, theta)
            name_fmt = "{sample}_{th}deg"

            sample_name = name_fmt.format(sample=sample, th="%2.2d" % theta)
            sample_id(user_name="PG", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(det, num=10)


def cd_saxs_old(sample, x, y, num=1, exp_t=1, step=121):
    det = [pil1M]

    det_exposure_time(exp_t, exp_t)
    yield from bps.mv(piezo.x, x)
    yield from bps.mv(piezo.y, y)

    for i, theta in enumerate(np.linspace(-60, 60, step)):
        yield from bps.mv(prs, theta)
        name_fmt = "{sample}_{num}_{th}deg"

        sample_name = name_fmt.format(sample=sample, num="%2.2d"%i, th="%2.2d"%theta)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=num)
        yield from bps.sleep(1)


def cdsaxs_all_pitch(sample, x, y, num=1, exp_t=1, step=121):
    pitches = ["p112nm","p113nm","p114nm","p115nm","p116nm","p117nm","p118nm","p119nm","p120nm","p121nm","p122nm","p123nm","p124nm","p125nm",
               "p126nm","p127nm","p128nm"]
    x_off = [0,1500,3000,4500,6000,7500,9000,10500,12000,13500,15000,16500,18000,19500,21000,22500,24000]
    det_exposure_time(exp_t, exp_t)
    for x_of, pitch in zip(x_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y, num=1, exp_t=exp_t, step=step)


def night_patrice(exp_t=1):
    numero = 6
    det = [pil1M]

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
    sample = ["Echantillon03_defectivity","Echantillon04_defectivity","Echantillon11b_defectivity"]
    x = [-40050, -11150, 17000]
    y = [2000, 2000, 3900]
    det = [pil1M]

    pitches = np.linspace(128, 112, 17)

    det_exposure_time(exp_t, exp_t)
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
    yield from scan_boite_pitch(1)
    yield from cd_saxs(-60, 60, 121, 2)


def NEXAFS_Ti_edge(t=0.5):

    dets = [pil300KW]
    name = "NEXAFS_echantillon2_Tiedge_ai1p4"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)
    yield from bps.mv(energy, 5010)
    yield from bps.mv(energy, 4990)
    yield from bps.mv(energy, 4970)
    yield from bps.mv(energy, 4950)


def NEXAFS_SAXS_Ti_edge(t=0.5):

    dets = [pil300KW, pil1M]
    name = "NEXAFS_SAXS_echantillon13realign_ai1p75_Tiedge"
    # x = [8800]

    energies = np.linspace(4950, 5050, 101)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"

    for e in energies:
        yield from bps.mv(energy, e)
        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.1f" % xbpm3.sumY.value
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 5030)
    yield from bps.mv(energy, 5010)
    yield from bps.mv(energy, 4990)
    yield from bps.mv(energy, 4970)
    yield from bps.mv(energy, 4950)


def GISAXS_scan_boite(t=1):

    sample = "Echantillon13realign_gisaxs_scanpolyperiod_e4950eV_ai1p75"
    x = np.linspace(55900, 31900, 81)

    det = [pil1M]

    det_exposure_time(t, t)
    for k, xs in enumerate(x):
        yield from bps.mv(piezo.x, xs)

        name_fmt = "{sample}_pos{pos}"
        sample_name = name_fmt.format(sample=sample, pos="%2.2d" % k)
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.count(det, num=1)


def fly_scan_ai(det, motor, cycle=1, cycle_t=10, phi=-0.6):
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
    numero = 1
    det = [pil1M]
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

    yield from bps.mvr(pil1m_pos.x, -5)
    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, x, y, z in zip(names, xs, ys, zs):
        numero += 1
        name_fmt = "{sample}_num{numb}"
        sample_name = name_fmt.format(sample=name, numb=numero)
        yield from bps.mv(piezo.z, z)
        yield from mesure_db(sample_name, x, y, num=1, exp_t=1)

    yield from smi.modeMeasurement()
    yield from bps.mvr(pil1m_pos.x, 5)


def cdsaxs_important_pitch(sample, x, y, num=1, exp_t=1):
    pitches = ["p113nm", "p100nm"]

    if "bkg" in sample:
        x_off = [0, 0]
        y_off = [0, -13300]
    else:
        x_off = [0, 0]
        y_off = [0, -10500]

    det_exposure_time(exp_t, exp_t)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_{pit}"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        yield from cd_saxs_new(sample_name, x + x_of, y + y_of, num=num, exp_t=exp_t)


def mesure_rugo(sample, x, y, num=200, exp_t=1):
    print(sample)
    pitches = ["p100nm"]

    if "bkg" in sample:
        x_off = [0]
        y_off = [-13300]
    else:
        x_off = [0]
        y_off = [-10500]

    yield from bps.mv(prs, -1)

    det_exposure_time(exp_t, exp_t)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_rugo_{pit}_up"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        print(sample_name)
        sample_id(user_name="PG", sample_name=sample_name)

        yield from bp.count([pil1M], num=num)

    yield from bps.mvr(pil1m_pos.y, 4.3)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)
        name_fmt = "{sample}_rugo_{pit}_down"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        sample_id(user_name="PG", sample_name=sample_name)
        yield from bp.count([pil1M], num=num)

    yield from bps.mvr(pil1m_pos.y, -4.3)


def mesure_db(sample, x, y, num=1, exp_t=1):
    pitches = ["p100nm"]
    if "bkg" in sample:
        x_off = [0]
        y_off = [-13300]
    else:
        x_off = [0]
        y_off = [-10500]
    yield from bps.mv(prs, -1)

    det_exposure_time(exp_t, exp_t)
    for x_of, y_of, pitch in zip(x_off, y_off, pitches):
        yield from bps.mv(piezo.x, x + x_of)
        yield from bps.mv(piezo.y, y + y_of)

        name_fmt = "{sample}_db_{pit}_att9x60umSn"
        sample_name = name_fmt.format(sample=sample, pit=pitch)
        sample_id(user_name="PG", sample_name=sample_name)

        yield from bp.count([pil1M], num=1)


def NEXAFS_P_edge(t=0.5):
    yield from bps.mv(waxs, 0)
    dets = [pil300KW]
    name = "nexafs_s4_wa0_0.5deg"

    energies = np.linspace(2140, 2200, 61)

    det_exposure_time(t, t)
    name_fmt = "{sample}_{energy}eV_xbpm{xbpm}"
    for e in energies:
        yield from bps.mv(energy, e)
        yield from bps.sleep(2)

        sample_name = name_fmt.format(
            sample=name, energy=e, xbpm="%3.2f" % xbpm3.sumY.value
        )
        sample_id(user_name="SR", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(dets, num=1)

    yield from bps.mv(energy, 2190)
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
    sample = "sample-33"
    det = [pil1M]
    yield from bps.mv(piezo.y, 1000)

    det_exposure_time(exp_t, exp_t)

    theta_zer=-4

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta+theta_zer)
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
        yield from bps.mv(prs, theta+theta_zer)
        name_fmt = "{sample}_8.3m_16.1keV_num{num}_{th}deg"

        sample_name = name_fmt.format(
            sample=sample, num="%2.2d" % num, th="%2.2d" % theta
        )
        sample_id(user_name="PG", sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        
        yield from bps.sleep(2)
        yield from bp.count(det, num=1)




def cd_saxs_new(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil1M]):

    det_exposure_time(exp_t, exp_t)

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)
        name_fmt = "{sample}_9.2m_16.1keV_num{num}_{th}deg_bpm{bpm}"
        sample_name = name_fmt.format(sample=sample, num="%5.2d"%num, th="%2.2d"%theta, bpm="%1.3f"%xbpm3.sumX.get()) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)


def sample_linqz(phi_min,phi_max,N):
    qz_min = np.tan(np.deg2rad(phi_min))
    qz_max = np.tan(np.deg2rad(phi_max))

    # Linearly spaced qz
    qz = np.linspace(qz_min, qz_max, N)

    # Compute corresponding angles in degrees
    phi = np.rad2deg(np.arctan(qz))

    return phi

def cd_saxs_linqz(th_ini, th_fin, th_num, exp_t=1, sample='test', nume=1, det=[pil1M]):

    det_exposure_time(exp_t, exp_t)

    th_ls=sample_linqz(th_ini,th_fin,th_num)

    for num, theta in enumerate(th_ls):
        yield from bps.mv(prs, theta)
        name_fmt = "{sample}_9.2m_16.1keV_num{num}_{th}deg_bpm{bpm}"
        sample_name = name_fmt.format(sample=sample, num="%5.2d"%num, th="%2.2d"%theta, bpm="%1.3f"%xbpm3.sumX.get()) # Philipp change, original: num="%2.2d"%num
        #sample_id(user_name="PG", sample_name=sample_name)
        sample_id(sample_name=sample_name)

        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=nume)


def cdsaxs_IBM_2024_1(t=1):
    det = [pil1M]
    det_exposure_time(t, t)

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
    det = [pil1M]
    det_exposure_time(t, t)

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
    det_exposure_time(exp_t, exp_t)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)

            yield from bps.mvr(pil1m_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)
            yield from bps.mvr(pil1m_pos.y, -4.3)

def cdsaxsstd_2025_1A_yager(t=1):
    det = [pil1M]
    det_exposure_time(t, t)

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
    det_exposure_time(exp_t, exp_t)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)

            yield from bps.mvr(pil1m_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)
            yield from bps.mvr(pil1m_pos.y, -4.3)

def cdsaxsstd_2025_1B_yager(t=1):
    det = [pil1M]
    det_exposure_time(t, t)

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
    det_exposure_time(exp_t, exp_t)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)

            yield from bps.mvr(pil1m_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)
            yield from bps.mvr(pil1m_pos.y, -4.3)

def cdsaxsstd_2025_1CD_yager(t=1):
    det = [pil1M]
    det_exposure_time(t, t)

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
    det_exposure_time(exp_t, exp_t)
    for i in range(1):
        for name, xs, ys, zs, chis, ths in zip(names, x, y, z, chi, th):
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.ch, chis)
            yield from bps.mv(piezo.th, ths)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)

            yield from bps.mv(prs, phi_offest)

            name_fmt = "{sample}_up_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            print(sample_name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)

            yield from bps.mvr(pil1m_pos.y, 4.3)
            name_fmt = "{sample}_down_sdd9200_16.1keV"
            sample_name = name_fmt.format(sample=name)
            sample_id(sample_name=sample_name)
            yield from bp.count([pil1M], num=nume)
            yield from bps.mvr(pil1m_pos.y, -4.3)


def xyscan_wieser(t=1):
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
                    yield from bp.count([pil1M], num=1)


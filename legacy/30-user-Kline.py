def measure(det=[pil2M], sample='test',  t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick one-shot — sets the exposure, names the file, and takes
    #   a single SAXS image of one sample.
    #
    # 💡 NEWER, EASIER WAY: the beamline's 'smi_plans' helper library can take a single
    #   labelled image in one call, and it records the beam/positions into the data and
    #   builds the file name from them automatically (no hand-built name string needed):
    #
    #     from smi_plans import acquire, saxs_waxs_dets
    #     yield from acquire("test", saxs_waxs_dets(use_waxs=False), [])  # one SAXS frame
    #     # (the exposure is set for you via the technique's t= argument)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see ⚠️ note).
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_name = "{sample}".format(sample=sample)
    sample_id(user_name="JK", sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.count(det, num=1)

def cd_saxs(th_ini, th_fin, th_st, exp_t=1, sample='test', nume=1, det=[pil2M]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the heart of a CD-SAXS measurement — it "rocks" the sample by
    #   stepping the rotation stage from th_ini to th_fin (th_st steps) and takes a
    #   SAXS image at each angle, building a long descriptive file name each time.
    #   (Almost every function in this file calls this one to do the actual rocking.)
    #
    # 💡 NEWER, EASIER WAY: rocking-while-collecting is exactly what the beamline's
    #   'smi_plans' helper library calls a CD-SAXS "rock run". It drives the rock for
    #   you and records the rotation angle, beam, detector distance, and positions
    #   straight INTO the saved data (so you don't have to pack them into that long
    #   "{sample}_sdd_cm_..._sample_phi_deg_{th}_..." name by hand):
    #
    #     from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run(
    #         sample,                                  # base name; the rest is filled in
    #         np.linspace(th_ini, th_fin, th_st),      # your same rocking angles
    #         t=exp_t,                                 # your exposure time
    #     )
    #     # (Under the hood smi_plans rocks the rotation stage 'stage.phi' — see the
    #     #  ⚠️ note on the 'prs' line below, which is the old name for that same stage.)
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' is the OLD name for the rotation stage and
    #   no longer exists — it's now 'stage.phi' (⚠️ note on the 'bps.mv(prs, ...)'
    #   line). (2) 'det_exposure_time(...)' no longer sets the exposure unless run as a
    #   plan (⚠️ note below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(exp_t, exp_t*nume)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(exp_t, exp_t*nume)  — or at the prompt:  RE(det_exposure_time(exp_t, exp_t*nume)). (The smi_plans technique runs set exposure for you via t=.)

    for num, theta in enumerate(np.linspace(th_ini, th_fin, th_st)):
        yield from bps.mv(prs, theta)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        sdd_cm = pil2M.sample_distance_mm.get()/10
        name_fmt = "{sample}_sdd_cm_{sdd_cm}_energy_ev_16100_sample_phi_deg_{th}_exposure_time_s_{et}_bpm_{bpm}_posx_um_{posx}_posy_um_{posy}_poxz_um_{posz}_num_{num}"
        #name_fmt = "{sample}_5.2m_16.1keV_num{num}_{th}deg_bpm{bpm}"
        
        
        sample_name = name_fmt.format(sample=sample, num="%2.2d"%num, th="%2.2d"%theta, bpm="%1.3f"%xbpm3.sumX.get(), et = "%2.2f"%exp_t, sdd_cm = "%6.2f"%sdd_cm, posx = "%7.4f"%piezo.x.position, posy = "%7.4f"%piezo.y.position, posz = "%7.4f"%piezo.z.position)
        # sample_id(user_name="JK", sample_name=sample_name)
        sample_id(sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        yield from bp.count(det, num=1)



def cdsaxs_2024_1(t=1):
    det = [pil2M]
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book for one set of CD-SAXS samples — it holds the sample
    #   names and their x/y/z/chi/theta positions, then for each sample drives there
    #   and calls cd_saxs() to do a -60..+60 deg rock (plus a reference shot before
    #   and after).
    #
    # 💡 NEWER, EASIER WAY: a sample table + "do the same rock on every sample" is a
    #   one-liner with the beamline's 'smi_plans' helper library. A sample table is a
    #   first-class object (SampleList) and a "bar" plan loops over it, recording each
    #   sample's name and coordinates into the data for you:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z, chi=chi, th=th)
    #     yield from cdsaxs_bar(samples, t=t)     # rocks each sample the same way
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the ⚠️ lines, which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' below no longer sets the
    #   exposure unless run as a plan (⚠️ note). Also note the rock itself happens in
    #   cd_saxs(), which still uses the retired 'prs' stage name — see the ⚠️ there.
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    phi_offest = -2

    # names = [ 'C5b-L60p120']
    # x =     [   20800]
    # x_hexa =[     0.3]
    # y=      [    -3400]
    # z=      [    -1200]
    # chi=    [    0.6]
    # th =    [  5.75]

    # names = [ 'H5b-L52p104', 'E4b-L52p104', 'C5-L50p100', 'C5-L52p104', 'C5-L55p110', 'C5-L60p120']
    # x =     [   8550, -24350,       24400, 23500, 22600, 21700]
    # x_hexa =[     0.3, 0.3,         0.3, 0.3, 0.3, 0.3]
    # y=      [    -3250, -4100,      -3400, -3400, -3400, -3400]
    # z=      [    -550, 550,         -1200, -1200, -1200, -1200]
    # chi=    [    -0.5, 0.1,         0.6, 0.6, 0.6, 0.6]
    # th =    [  5.35, 5.85,          5.75, 5.75, 5.75, 5.75]

    names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    x =     [   -350, 550, 1450, 2350, 3250]
    x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    y=      [    3450, 3450, 3450, 3450, 3450]
    z=      [    -4600, -4600, -4600, -4600, -4600]
    chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    # names = [ 'F11-L60P120V', 'F11-L80P160V']
    # x =     [   15200, 16100]
    # x_hexa =[     0.3 , 0.3]
    # y=      [    650, 650]
    # z=      [    -4800, -4800]
    # chi=    [    -0.1, -0.1]
    # th =    [  5.5, 5.5]


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
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=1)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)




def cdsaxs_2025_1(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book — holds a sample table (names + x/y/z/chi/th)
    #   and, for each sample (here only those past index 4), moves there and calls
    #   cd_saxs() to do a -60..+60 deg rock plus before/after reference shots.
    #
    # 💡 NEWER, EASIER WAY: the beamline's 'smi_plans' helper library turns a sample
    #   table + "rock each one" into a single call, recording each sample's name and
    #   coordinates into the saved data automatically:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z, chi=chi, th=th)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Just a tidier option to try later — your script below works as-is. The actual
    #    ⚠️ fixes live in cd_saxs(): the retired 'prs' stage and the det_exposure_time
    #    "plan" issue, both flagged with ⚠️ there.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'intel4',       'W204_F2',    'W204_I9',        'W204_I10',       'W204_H8',     'W204_H11', 'W204_L11', 'W204_M9',  ]
    x =     [     4350,        -22170,      -16860,           -10890,          -5950,         -100,        4600,      10300,   ]
    y=      [    -2100,          8500,        8900,             8650,           8950,         8900,        9000,       9100,   ]
    z=      [     9850,          9060,        9160,             9280,           9420,         9460,        9470,       9600,   ]
    chi=    [      1.3,          -0.9,        -0.2,             -1.0,            1.1,         -0.4,         1.0,          0,   ]
    th =    [    - 0.1,           0.1,         0.1,              0.1,             .1,         0.05,         0.1,          0,   ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for i in range(1):
        for nn, (name, xs, ys, zs, chis, ths) in enumerate(zip(names, x, y, z, chi, th)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            if nn>=4:

                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)

                if 'intel' in name:
                    number = 2
                else:
                    number = 10              
        

                # yield from bp
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)

def cdsaxs_2025_1_Karen(t=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same kind of CD-SAXS run-book — a sample table of resist-grating
    #   samples; for each one (here only the last) it moves there, double-checks the y
    #   motor actually arrived, then calls cd_saxs() for a -60..+60 deg rock.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library does the "loop the sample
    #   table and rock each one" part for you and records names/positions into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z, chi=chi, th=th)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    '45s_30nm_200nm_pitch',       '45s_30nm_300nm_pitch',    '45s_50nm_200nm_pitch',        '45s_50nm_300nm_pitch',       '45s_100nm_300nm_pitch',     '75s_30nm_200nm_pitch', '75s_30nm_300nm_pitch', '75s_50nm_200nm_pitch',  ]
    x =     [          -23040,                         -23038,                   -23020,                         -23020,                         -23020,                         27080,                   27120,               27120,       ]
    y=      [           -3262,                           -750,                     1750,                           4250,                           6750,                           -1450,                   1050,                3560,       ]
    z=      [            6100,                           6110,                     6080,                           6060,                           6040,                           7770,                    7760,                 7680,         ]
    chi=    [               0,                              0,                        0,                                   0,                               0,                            0,                 0,                     0,            ]
    th =    [               0,                              0,                        0,                                 0,                               0,                            0,                     0,                 0,                   ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for i in range(1):
        for nn, (name, xs, ys, zs, chis, ths) in enumerate(zip(names, x, y, z, chi, th)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            if nn>=7:
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)
                
                while abs(piezo.y.position - ys) >= 1:
                    print('y motor error')
                    yield from bps.mv(piezo.y, ys)
                    yield from bps.sleep(5)
                
                number = 1              
        

                # yield from bp
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            
def cdsaxs_2025_2_NSH1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for a single sample (imec_nsh_D08) — move to
    #   its x/y/z, confirm the y motor arrived, then call cd_saxs() for a -60..+60 deg
    #   rock with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: even for one sample, the 'smi_plans' helper library can do
    #   the rock in one call and record the positions/beam into the saved data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'imec_nsh_D08'         ]
    x =     [          -7300                   ]
    y=      [           -1979                   ]
    z=      [            -2435                  ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=7:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        
def cdsaxs_2025_2_1_dupont1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for one DuPont beam-damage sample — move to
    #   its x/y/z, confirm the y motor arrived, then cd_saxs() does a -60..+60 deg rock
    #   with before/after reference shots.
    #
    # 💡 NEWER, EASIER WAY: same as the other CD-SAXS run-books here — the 'smi_plans'
    #   helper library wraps "move to the sample and rock it" in one call and records
    #   positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'dupont_EUVD_1,-1_beamdamage'         ]
    x =     [          -7300                   ]
    y=      [           -1979                   ]
    z=      [            -2435                  ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=7:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
        

def cdsaxs_2025_2_FSH1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for one IMEC sample (imec_fsh_d04b) — move to
    #   its x/y/z, confirm the y motor arrived, then cd_saxs() does a -60..+60 deg rock
    #   with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library does the move + rock in one
    #   call and saves positions/beam into the data automatically:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'imec_fsh_d04b',    ]
    x =     [          -33000,       ]
    y=      [           -1480,       ]
    z=      [            -1400,     ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=7:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)
def cdsaxs_2025_2_FSH2(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for four IMEC samples — for each one, move to
    #   its x/y/z, confirm the y motor arrived, then cd_saxs() does a -60..+60 deg rock
    #   with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'imec_fsh_d05b',  'imec_fsh_d06b','imec_fsh_d11b','imec_fsh_d15a'   ]
    x =     [          -34000,      -7700,      13000,              40100]
    y=      [           2086,       2086,       -3914,              -2300      ]
    z=      [            -1400,     -2600,      -3700,              -4700]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)

def cdsaxs_2025_2_FSH3(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for five IMEC "gate" samples — for each, move
    #   to its x/y/z, confirm the y motor arrived, then cd_saxs() does a -60..+60 deg
    #   rock with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'imec_fsh_d06b_gate',  'imec_fsh_d15a_gate','imec_fsh_d04b_gate','imec_fsh_d11b_gate','imec_fsh_d05b_gate'    ]
    x =     [          -29800,      2800,      28800,              8000,        -24500]
    y=      [           -8100,       -8100,       9800,              9800,      9800      ]
    z=      [            -1500,     -3000,      -3900,              -3000,      -1500]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)

def cdsaxs_2025_2_NSH_KD(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book mixing IMEC and KD grating samples — for each,
    #   move to its x/y/z, confirm the y motor arrived, then cd_saxs() does a -60..+60
    #   deg rock with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'imec_fsh_d13b',  'KD_30nm_200nmpitch','KD_30nm_300nmpitch','KD_50nm_200nmpitch','KD_50nm_300nmpitch'  ,'KD_100nm_300nmpitch' ,'IMEC_nsh_d24b' ,'IMEC_nsh_d19b','IMEC_nsh_d15b']
    x =     [          26459,      -460,                        -2960,              -5327,        -7950,                   -10421,                 -21320,          3240,            26500           ]
    y=      [           5225,       9840,                         9760,              9600,         9540,                     9540,                    -4806,          -6600,          -4500           ]
    z=      [            -2840,     -2640,                         -2520,              -2440,      -2280,                   -2160,                    -1720,          -2900,          -4020          ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)

def cdsaxs_2025_2_KD(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for two KD grating samples (rotated 90 deg) —
    #   for each, move to its x/y/z, confirm the y motor arrived, then cd_saxs() does a
    #   -60..+60 deg rock with reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'KD_100nm_300nmpitch_90deg',  'KD_50nm_300nmpitch_90deg',]
    x =     [          3028,                            3024,                ]
    y=      [           4979,                             7354,               ]
    z=      [            -2680,                         -2760,              ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)

def cdsaxs_2025_2_int4(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for one sample (int4) — move to its x/y/z,
    #   confirm the y motor arrived, then cd_saxs() does a -60..+60 deg rock with
    #   reference shots before and after.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library wraps the move + rock in one
    #   call and saves positions/beam into the data automatically:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'int4',   ]
    x =     [          16200,]
    y=      [           3800,   ]
    z=      [            -3300,  ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-60+phi_offest, 60+phi_offest, 121, exp_t=t, sample=name+'_measure%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'_measure_ref-B%s'%(i+1), nume=1)


def cdsaxs_2025_2_Dupont2(t=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for eight DuPont EUV samples — for each, move
    #   to its x/y/z, confirm the y motor arrived, then cd_saxs() does several rocks
    #   (the first sample gets four rocks; the rest get fewer) with reference shots.
    #
    # ⚠️ HEADS-UP (not a code error, but easy to trip on): there are TWO functions in
    #   this file named 'cdsaxs_2025_2_Dupont2'. In Python the SECOND definition (the
    #   one further down, with the 'dupont_euv_d_pos3-1' samples) quietly REPLACES this
    #   one — so calling cdsaxs_2025_2_Dupont2() actually runs the LOWER one, not this
    #   one. If you want this version, rename one of them (e.g. add '_part1').
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'dupont_euv_a_pos1-6',  'dupont_euv_b_pos1-5','dupont_euv_c_pos1-6','dupont_euv_d_pos1-1', 'dupont_euv_d_pos-1-1', 'dupont_euv_c_pos-1,-6', 'dupont_euv_b_pos-1-5', 'dupont_euv_a_pos-1-6']
    x =     [          -30300,                  -10700,              10100,                  31300,                  28700,                   6900,                       -10900,                   -33400        ]
    y=      [           -2500,                   -3500,              -3500,                  -3500,                  3000,                   4500,                       4500,                       1200    ]
    z=      [          -1600,                   -2500,               -3500,                  -4500,                  -3800,                   -2000,                       -2300,                    -1300       ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
            if nn==0:
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure1%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
                yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure2%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-C%s'%(i+1), nume=1)
                yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure3%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-D%s'%(i+1), nume=1)
                yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure4%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-E%s'%(i+1), nume=1)
            else:
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure1%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
                yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure2%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-C%s'%(i+1), nume=1)
   
def cdsaxs_2025_2_Dupont2(t=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for two DuPont EUV samples — for each, move to
    #   its x/y/z, confirm the y motor arrived, then cd_saxs() does several rocks with
    #   reference shots in between.
    #
    # ⚠️ HEADS-UP (not a code error, but easy to trip on): there are TWO functions in
    #   this file named 'cdsaxs_2025_2_Dupont2'. Because this one comes SECOND, it is
    #   the one Python actually keeps — calling cdsaxs_2025_2_Dupont2() runs THIS
    #   version (the earlier eight-sample one above is shadowed/ignored). If you meant
    #   to keep both, give them different names.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'dupont_euv_d_pos3-1',  'dupont_euv_d_pos-3-1',]
    x =     [          -28900,                   -9400        ]
    y=      [           3500,               4500    ]
    z=      [          -1200,                           -2300,  ]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    
    for i in range(1):
        for nn, (name, xs, ys, zs) in enumerate(zip(names, x, y, z)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            #if nn>=70:
            yield from bps.mv(piezo.z, zs)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            
            while abs(piezo.y.position - ys) >= 1:
                print('y motor error')
                yield from bps.mv(piezo.y, ys)
                yield from bps.sleep(5)
            
            number = 1              
        

            # yield from bp
 
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
            yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure1%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
            yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure2%s'%(i+1), nume=number)
            yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-C%s'%(i+1), nume=1)
     

def cdsaxs_2025_1_Matt(t=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS run-book for ten wafer samples — for each, move to its
    #   x/y/z/chi/th, force the y motor to settle, then cd_saxs() does four rocks with
    #   reference shots in between.
    #
    # 💡 NEWER, EASIER WAY: the 'smi_plans' helper library loops the sample table and
    #   rocks each one for you, recording names/positions/beam into the data:
    #
    #     from smi_plans import SampleList, cdsaxs_bar
    #     samples = SampleList.from_columns(name=names, x=x, y=y, z=z, chi=chi, th=th)
    #     yield from cdsaxs_bar(samples, t=t)
    #
    #   (Optional tidy-up — your script below works as-is. The real ⚠️ fixes are in
    #    cd_saxs(): the retired 'prs' stage and the det_exposure_time "plan" issue.)
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [    'W4_D25',       'W2_D25',    'W2_D22',     'W2_D18',       'W1_D9',      'W1_12',     'W_15',   'W3_14',  'W3_20',  'W3_23',]
    x =     [          40620,        -15680,    -29300,      -35500,         -44500,       -32200,     -20100,     28500,    39200,    44500,]
    y=      [           7500,         7500,       7500,        7500,          -7000,        -7000,      -6000,     -6000,    -8000,    -8000,]
    z=      [            2040,         1040,       640,        740,            940,          1140,       1140,      2240,     2440,     2540,]
    chi=    [               0,          0,          0,            0,              0,          3.9,          6,        -4,      1.5,        0,]
    th =    [               0,          0,          0,            0,              0,            0,          0,         0,        0,        0,]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for i in range(1):
        for nn, (name, xs, ys, zs, chis, ths) in enumerate(zip(names, x, y, z, chi, th)):
            # yield from bps.mv(stage.x, xs_hexa)
            # yield from bps.mv(stage.y, ys_hexa)
            
            if nn>=0:
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)
                
                # force piezo.y to move to the correct position
                while abs(piezo.y.position - ys) >= 1:
                    print('y motor error')
                    yield from bps.mv(piezo.y, ys)
                    yield from bps.sleep(4)
                
                number = 1              
        

                # yield from bp
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure1%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)
                yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure2%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-C%s'%(i+1), nume=1)
                yield from cd_saxs(-46+phi_offest, 44+phi_offest, 46, exp_t=t, sample=name+'measure3%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-D%s'%(i+1), nume=1)
                yield from cd_saxs(-45+phi_offest, 45+phi_offest, 46, exp_t=t, sample=name+'measure4%s'%(i+1), nume=number)
                yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-E%s'%(i+1), nume=1)
            


def cdsaxs_2025_1_scan(t=0.2, scan= [1, 1, 1, 1, 1]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an ALIGNMENT / survey helper for CD-SAXS. For each sample it can
    #   sweep one axis at a time — rotation (phi/PRS), y, z, theta, or chi — taking a
    #   SAXS image at each step, so you can find the best position before measuring.
    #   The 'scan=[1,1,1,1,1]' list turns each of those five sweeps on or off.
    #
    # 💡 NEWER, EASIER WAY: these one-axis "find the sweet spot" sweeps are built-in to
    #   the beamline's 'smi_plans' helper library. You point a single axis builder at a
    #   motor and a range and it records the readings into the data:
    #
    #     from smi_plans import acquire, motor_axis, saxs_waxs_dets
    #     # e.g. a y survey around the current position:
    #     yield from acquire("y_survey", saxs_waxs_dets(use_waxs=False),
    #                        [motor_axis("y", piezo.y, np.arange(-0.3, 0.31, 0.05))])
    #     # the phi (rotation) survey is just cdsaxs_rock_run / motor_axis(stage.phi, ...);
    #     # smi_plans also has cdsaxs_pitch_survey for the CD-SAXS pitch search.
    #
    #   (Optional tidy-up — your script below works as-is, EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the 'prs' rotation stage was retired — it's now
    #   'stage.phi' (⚠️ notes on the several 'bps.mv(prs, ...)' lines below, and the
    #   phi sweep also goes through cd_saxs(), which uses 'prs' too). (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (⚠️ notes below).
    # === end smi_plans note ================================================
    det = [pil2M]
    phi_offest = 0

    # names = [ 'B305-L50p100', 'B305-L52p104', 'B305-L55p110', 'B305-L57p115', 'B305-L60p120']
    # x =     [   -350, 550, 1450, 2350, 3250]
    # # x_hexa =[     0.3,  0.3,    0.3, 0.3,  0.3]
    # y=      [    3450, 3450, 3450, 3450, 3450]
    # z=      [    -4600, -4600, -4600, -4600, -4600]
    # chi=    [    -1.6, -1.6, -1.6, -1.6, -1.6]
    # th =    [  3.5, 3.5, 3.5, 3.5, 3.5]

    names = [     'W204_F2',    'W204_I9',        'W204_I10',       'W204_H8',     'W204_H11', 'W204_L11', 'W204_M9',  ]
    x =     [      -22170,      -16860,           -10890,          -5950,         -100,        4600,      10300,   ]
    y=      [           8500,        8900,             8650,           8950,         8900,        9000,       9100,   ]
    z=      [          9060,        9160,             9280,           9420,         9460,        9470,       9600,   ]
    chi=    [                -0.9,        -0.2,             -1.0,            1.1,         -0.4,         1.0,          0,   ]
    th =    [              0.1,         0.1,              0.1,             .1,         0.05,         0.1,          0,   ]


    # names = [    'test',  ]
    # x =     [      -22170]
    # y=      [           8500]
    # z=      [          9060 ]
    # chi=    [                -0.9  ]
    # th =    [              0.1 ]


    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    # assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
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

            number = 10           
    
            ############# scan phi (PRS)
            if scan[0]:
                print("==== scan PRS")
                # yield from bp
                # yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-A%s'%(i+1), nume=1)
                yield from cd_saxs(-1+phi_offest, 1+phi_offest, 41, exp_t=t, sample=name+'phi-scan%s'%(i+1), nume=number)
                # yield from cd_saxs(phi_offest, phi_offest, 1, exp_t=t, sample=name+'measure_ref-B%s'%(i+1), nume=1)

            ############# scan y
            if scan[1]:
                print("==== scan y")
                phi = phi_offest
                yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)

                det_exposure_time(t, t*number)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t*number)  — or at the prompt:  RE(det_exposure_time(t, t*number)). (The smi_plans technique runs set exposure for you via t=.)

                for ii, yys in enumerate(np.arange(-0.3, 0.3+0.01, 0.05)):
                    ypos = ys + yys
                    yield from bps.mv(piezo.y, ypos)

                    sample=name+'y-scan%s'%(ii+1)
                    name_fmt = "{sample}_5.2m_16.1keV_num{num}_{phi}deg_y{y}_yr{yr}_z{z}_bpm{bpm}"
                    sample_name = name_fmt.format(sample=sample, num="%2.2d"%ii, phi="%2.2d"%phi, y="%5.2d"%ypos, yr="%5.2d"%yys, z="%2.2d"%zs, bpm="%1.3f"%xbpm3.sumX.get())
                    # sample_id(user_name="JK", sample_name=sample_name)
                    sample_id(sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(det, num=1)
                    
                yield from bps.mv(piezo.y, ys)

            ############# scan z
            if scan[2]:
                print("==== scan z")
                number = 1
                det_exposure_time(t, t*number)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t*number)  — or at the prompt:  RE(det_exposure_time(t, t*number)). (The smi_plans technique runs set exposure for you via t=.)

                phi = phi_offest
                yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)

                z_list = [-20000, -10000,  -9000,  -8000,  -7000,  -6000,  -5000,  -4000,  -3000,
            -2000,  -1000,   -500, -400, -300, -200, -100,    0,  100,  200,  300,  400,  500,
                1000,   2000,   3000,   4000,   5000,
            6000,   7000,   8000,   9000, 10000, 20000]
                for ii, zzs in enumerate(z_list):
                    zpos = zs + zzs
                    yield from bps.mv(piezo.z, zpos)

                    sample=name+'z-scan%s'%(ii+1)
                    name_fmt = "{sample}_5.2m_16.1keV_num{num}_{phi}deg_y{y}_z{z}_zr{zr}_bpm{bpm}"
                    sample_name = name_fmt.format(sample=sample, num="%2.2d"%ii, phi="%2.2f"%phi, y="%5.2d"%ys, z="%2.2d"%zpos, zr="%2.2d"%zzs, bpm="%1.3f"%xbpm3.sumX.get())
                    # sample_id(user_name="JK", sample_name=sample_name)
                    sample_id(sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(det, num=1)
                    
                yield from bps.mv(piezo.y, ys)
                yield from bps.mv(piezo.z, zs)
                        
            ############# scan theta
            if scan[3]:
                print("==== scan theta")
                phi = phi_offest
                yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)

                det_exposure_time(t, t*number)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t*number)  — or at the prompt:  RE(det_exposure_time(t, t*number)). (The smi_plans technique runs set exposure for you via t=.)

                for ii, thr in enumerate(np.arange(-1, 1.01, 0.1)):
                    thpos = ths + thr
                    yield from bps.mv(piezo.th, thpos)

                    sample=name+'th-scan%s'%(ii+1)
                    name_fmt = "{sample}_5.2m_16.1keV_num{num}_{phi}deg_th{th}_thr{thr}_z{z}_bpm{bpm}"
                    sample_name = name_fmt.format(sample=sample, num="%2.2d"%ii, phi="%2.2f"%phi, th="%5.2f"%thpos, thr="%5.2f"%thr, z="%2.2d"%zs, bpm="%1.3f"%xbpm3.sumX.get())
                    # sample_id(user_name="JK", sample_name=sample_name)
                    sample_id(sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(det, num=1)
                    

            ############# scan chi
            if scan[4]:

                print("==== scan chi")
                phi = phi_offest
                yield from bps.mv(prs, phi_offest)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                yield from bps.mv(piezo.z, zs)
                yield from bps.mv(piezo.ch, chis)
                yield from bps.mv(piezo.th, ths)
                yield from bps.mv(piezo.x, xs)
                yield from bps.mv(piezo.y, ys)

                det_exposure_time(t, t*number)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t*number)  — or at the prompt:  RE(det_exposure_time(t, t*number)). (The smi_plans technique runs set exposure for you via t=.)

                for ii, chr in enumerate(np.arange(-1, 1.01, 0.1)):
                    chpos = chis + chr
                    yield from bps.mv(piezo.ch, chpos)

                    sample=name+'ch-scan%s'%(ii+1)
                    name_fmt = "{sample}_5.2m_16.1keV_num{num}_{phi}deg_ch{ch}_chr{chr}_z{z}_bpm{bpm}"
                    sample_name = name_fmt.format(sample=sample, num="%2.2d"%ii, phi="%2.2f"%phi, ch="%5.2f"%chpos, chr="%5.2f"%chr, z="%2.2d"%zs, bpm="%1.3f"%xbpm3.sumX.get())
                    # sample_id(user_name="JK", sample_name=sample_name)
                    sample_id(sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(det, num=1)
                            





def cd_gisaxs(t=1):
    prs_offset = -1.854

    det = [pil2M]
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: CD-GISAXS — like CD-SAXS but in grazing-incidence geometry. For
    #   each grating sample it aligns, sets attenuators per incident angle, then for a
    #   few incident angles it rocks the rotation stage (phi) across a fine angle grid,
    #   taking a SAXS image at each phi.
    #
    # 💡 NEWER, EASIER WAY: a grazing CD-SAXS rock is the beamline 'smi_plans' helper
    #   library's CD-GISAXS rock run. It drives the rock and records the phi angle,
    #   incident angle, and beam into the data, and align_sample handles the per-sample
    #   alignment:
    #
    #     from smi_plans import cd_gisaxs_rock_run, align_sample
    #     # rock phi at each incident angle, aligning each sample first:
    #     yield from cd_gisaxs_rock_run(...)        # see the cdsaxs_* presets in smi_plans
    #
    #   Under the hood the rock uses 'stage.phi' (the current name for the old 'prs').
    #
    #   (Optional tidy-up — your script below works as-is, EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the 'prs' rotation stage was retired — it's now
    #   'stage.phi' (⚠️ notes on the 'bps.mv(prs, ...)' lines below). (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan
    #   (⚠️ note below).
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    names = ['sam2_g1',  'sam2_g2',  'sam2_g3',  'sam2_g4', 'sam2_g5', 'sam2_g6']
    x =     [   -29300,     -35300,     -21300,     -17300,     -13300,    -9300]
    x_hexa =[     0.20,       0.20,       0.20,       0.20,       0.20,     0.20]
    y=      [     6900,       6900,       6900,       6900,       6900,     6900]
    y_hexa =[      0.0,        0.0,        0.0,        0.0,        0.0,      0.0]
    z=      [      200,        200,        200,        200,        200,      200]
    chi=    [   -1.055,     -1.055,     -1.055,     -1.055,     -1.055,   -1.055]
    th =    [  -0.7229,    -0.7229,    -0.7229,    -0.7229,    -0.7229,  -0.7229]

    names = ['sam2_g2',  'sam2_g3',  'sam2_g4', 'sam2_g5', 'sam2_g6']
    x =     [   -25300,     -21300,     -17300,     -13300,    -9300]
    x_hexa =[     0.20,       0.20,       0.20,       0.20,     0.20]
    y=      [     6900,       6900,       6900,       6900,     6900]
    y_hexa =[      0.0,        0.0,        0.0,        0.0,      0.0]
    z=      [      200,        200,        200,        200,      200]
    chi=    [   -1.055,     -1.055,     -1.055,     -1.055,   -1.055]
    th =    [  -0.7229,    -0.7229,    -0.7229,    -0.7229,  -0.7229]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, ys_hexa, zs, chis, ths in zip(names, x, x_hexa, y, y_hexa, z, chi, th):
        yield from bps.mv(prs, prs_offset)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yield from alignement_gisaxs_hex(0.1)
        
        ai0=stage.th.position

        for num, ai in enumerate([0.15, 0.20, 0.30, 0.50]):
            if ai == 0.15:
                    yield from bps.mv(att1_5.open_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
                    yield from bps.sleep(2)
                    yield from bps.mv(att1_5.open_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
            else:
                    yield from bps.mv(att1_5.close_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
                    yield from bps.sleep(2)
                    yield from bps.mv(att1_5.close_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)       

            yield from bps.mv(stage.th, ai0+ai)
            
            for num1, phi in enumerate(np.concatenate([np.linspace(-5, -1.02, 200), np.linspace(-1, 1, 401), np.linspace(1.02, 5, 200)])):
                yield from bps.mv(prs, prs_offset+phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

                name_fmt = "{sample}_9.2m_16.1keV_phi{phii}deg_ai{aii}deg"
                sample_name = name_fmt.format(sample=name, num="%2.2d"%num1, phii="%1.3f"%phi, aii="%1.2f"%ai)
                sample_id(user_name="KY_GI", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(det, num=1)



    prs_offset = -3.337
    names = ['sam1_g1',  'sam1_g2',  'sam1_g3',  'sam1_g4', 'sam1_g5', 'sam1_g6']
    x =     [    42700,      38700,      34700,      30700,      26700,    22700]
    x_hexa =[     0.20,       0.20,       0.20,       0.20,       0.20,     0.20]
    y=      [     6900,       6900,       6900,       6900,       6900,     6900]
    y_hexa =[      0.0,        0.0,        0.0,        0.0,        0.0,      0.0]
    z=      [      200,        200,        200,        200,        200,      200]
    chi=    [   -1.055,     -1.055,     -1.055,     -1.055,     -1.055,   -1.055]
    th =    [  -0.7229,    -0.7229,    -0.7229,    -0.7229,    -0.7229,  -0.7229]

    assert len(names) == len(x), f"len of x ({len(x)}) is different from number of samples ({len(names)})"
    assert len(names) == len(y), f"len of y ({len(y)}) is different from number of samples ({len(names)})"
    assert len(names) == len(x_hexa), f"len of x_hexa ({len(x_hexa)}) is different from number of samples ({len(names)})"
    assert len(names) == len(z), f"len of z ({len(z)}) is different from number of samples ({len(names)})"
    assert len(names) == len(chi), f"len of y ({len(chi)}) is different from number of samples ({len(names)})"
    assert len(names) == len(th), f"len of z ({len(th)}) is different from number of samples ({len(names)})"

    for name, xs, xs_hexa, ys, ys_hexa, zs, chis, ths in zip(names, x, x_hexa, y, y_hexa, z, chi, th):
        yield from bps.mv(prs, prs_offset)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(stage.y, ys_hexa)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.ch, chis)
        yield from bps.mv(piezo.th, ths)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)

        yield from alignement_gisaxs_hex(0.1)
        ai0=stage.th.position

        for num, ai in enumerate([0.15, 0.20, 0.30, 0.50]):
            if ai == 0.15:
                    yield from bps.mv(att1_5.open_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
                    yield from bps.sleep(2)
                    yield from bps.mv(att1_5.open_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
            else:
                    yield from bps.mv(att1_5.close_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)
                    yield from bps.sleep(2)
                    yield from bps.mv(att1_5.close_cmd, 1)
                    yield from bps.mv(att1_6.open_cmd, 1)       

            yield from bps.mv(stage.th, ai0+ai)
            
            for num1, phi in enumerate(np.concatenate([np.linspace(-5, -1.02, 200), np.linspace(-1, 1, 401), np.linspace(1.02, 5, 200)])):
                yield from bps.mv(prs, prs_offset+phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

                name_fmt = "{sample}_9.2m_16.1keV_phi{phii}deg_ai{aii}deg"
                sample_name = name_fmt.format(sample=name, num="%2.2d"%num1, phii="%1.3f"%phi, aii="%1.2f"%ai)
                sample_id(user_name="KY_GI", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                yield from bp.count(det, num=1)
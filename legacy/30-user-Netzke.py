# phi scan
def gisaxsnetzke(meas_t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GISAXS) phi-scan over ~10 ferroelectric samples. For
    #   each sample it aligns, then loops over WAXS arc -> incidence angle -> in-plane rotation
    #   (phi) -> energy, snapping a WAXS image at every combination. "phi" is the sample's in-plane
    #   rotation; here it's driven by the motor the script calls 'prs'.
    #
    # 💡 NEWER, EASIER WAY: rotating phi while also sweeping incidence/energy is the CD-GISAXS +
    #   energy combination in 'smi_plans'. cd_gisaxs_rock_run rocks phi and records the angle/beam
    #   into the data; for the full multi-sample/energy matrix you'd compose axes, e.g.:
    #
    #     from smi_plans import acquire, motor_axis, incidence_axis, energy_axis, align_sample
    #     yield from acquire(name, [pil900KW],
    #         [motor_axis("phi", stage.phi, [0, -20, -40, -60]),   # was 'prs'
    #          energy_axis([9540, 9580])],
    #         align=align_sample)   # aligns the sample and records the result with the data
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the rotation
    #   stage 'prs' was removed — it's now 'stage.phi' (the bps.mv(prs, ...) lines would crash);
    #   (3) 'det_exposure_time(...)' no longer sets the exposure unless run as a plan. See the ⚠️
    #   notes on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    waxs_arc = np.linspace(0, 45.5, 8)  # for 9.54 keV
    # waxs_arc = np.linspace(0, 26, 5) #(2th_min 2th_max steps) for 16.1 keV
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    phi = [0, -20, -40, -60]
    phi_aioff = [0, -0.03, -0.025, 0.015]
    xlocs = [  # -41000,
        -33500,
        -26000,
        -19000,
        -11500,
        1000,
        8500,
        16000,
        23500,
        31000,
        38500,
    ]
    # xlocs = [25500]
    names = [  #'SAM16-HZO_2',
        "ALLS61",
        "ALLS56",
        "ALLS63",
        "ALLS65",
        "SAM16-HZO_1",
        "SAM16HfO2_2",
        "ALLS58",
        "ALLS62",
        "ALLS57B",
        "ALLS64",
    ]
    angle = [0.2, 0.29, 0.4, 0.45]  # for 9.54 keV
    # angle = [0.08, 0.12, 0.2] #for 16.1 keV
    energ = [9540, 9580]
    # energ = [6100]
    assert len(xlocs) == len(names), f"Sample name/position list is borked"

    for x, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(GV7.open_cmd, 1)
        yield from alignement_gisaxs(0.2)  # for 9.54 keV
        # yield from alignement_gisaxs(0.08) #for 16.1 keV
        yield from bps.mv(GV7.close_cmd, 1)
        yield from bps.mv(att2_5.open_cmd, 1)
        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_E{ene}eV_ai{angle}deg_phi{phi}deg_wa{waxs}"
        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            for an in angle:
                # yield from bps.mv(stage.th, an)
                for ph, aioff in zip(phi, phi_aioff):
                    yield from bps.mv(prs, ph)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
                    yield from bps.mv(stage.th, an + aioff)
                    for en in energ:
                        yield from bps.mv(energy, en)
                        sample_name = name_fmt.format(
                            sample=name,
                            ene="%2.0f" % en,
                            angle="%3.2f" % an,
                            phi="%2.1f" % ph,
                            waxs="%2.1f" % wa,
                        )
                        sample_id(user_name="SN", sample_name=sample_name)
                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bp.count(dets, num=1)
        yield from bps.mv(stage.th, 0)
        yield from bps.mv(piezo.th, 0)

        yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


def netzkeall(meas_t=0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience wrapper that runs two scans back-to-back (gisaxsnetzke then
    #   gisaxsnetzke3). 'yield from' here just means "run that whole plan, then continue".
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you can keep chaining plans the same way, or build one
    #   bigger "bar" plan that covers all your samples in a single run. See the notes inside
    #   gisaxsnetzke / gisaxsnetzke3 for the per-scan migration. (Nothing here is broken — but the
    #   ⚠️ fixes flagged inside those two plans still apply when you run this.)
    # === end smi_plans note ================================================
    yield from gisaxsnetzke(meas_t=0.6)
    yield from gisaxsnetzke3(meas_t=0.6)


def gisaxsquick(meas_t=0.3):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick single-sample GISAXS check — sweeps WAXS arc, energy, and incidence
    #   angle (as small relative nudges of piezo.th), taking a few WAXS images per spot.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' builds the angle/energy/arc sweeps as "axes" handed to one
    #   acquire call, recording angle/energy/beam into each image:
    #
    #     from smi_plans import acquire, incidence_axis, energy_axis, motor_axis
    #     yield from acquire("RY26n", [pil900KW],
    #         [motor_axis("waxs_arc", waxs.arc, np.linspace(0, 45.5, 8)),
    #          energy_axis([9580]),
    #          incidence_axis(piezo.th, piezo.th.position, [0.2, 0.29, 0.4])], t=meas_t)
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ lines.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the rotation
    #   stage 'prs' was removed — it's now 'stage.phi'; (3) 'det_exposure_time(...)' no longer sets
    #   the exposure unless run as a plan. See the ⚠️ notes on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    waxs_arc = np.linspace(0, 45.5, 8)  # (2th_min 2th_max steps)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    phi = -20
    xlocs = [25500]
    names = ["RY26n"]
    # angle = [0.2, 0.29, 0.4, 0.45]
    angle = [0.2, 0.29, 0.4]
    energ = [9580]
    assert len(xlocs) == len(names), f"Sample name/position list is borked"

    for x, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, x)

        # yield from bps.mv(GV7.open_cmd, 1 )
        # yield from alignement_gisaxs(0.2)
        # yield from bps.mv(GV7.close_cmd, 1 )

        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_E{ene}eV_ai{angle}deg_phi{phi}deg_wa{waxs}"
        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
            for en in energ:
                yield from bps.mv(energy, en)
                # and the fastest cycle is the angle change
                for an in angle:
                    yield from bps.mvr(piezo.th, an)
                    sample_name = name_fmt.format(
                        sample=name,
                        ene="%2.0f" % en,
                        angle="%3.2f" % an,
                        phi=phi,
                        waxs="%2.1f" % wa,
                    )
                    sample_id(user_name="SN", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    yield from bp.count(dets, num=4)
                    yield from bps.mvr(piezo.th, -an)

    yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


"""
#incident angle scan
def gisaxsnetzke1(meas_t=0.3):
    waxs_arc = np.linspace(0, 45.5, 8)
    dets = [pil300KW]
    
    xlocs = [12000]
    names = ['RY5']
    phi = 0
        
    assert len(xlocs) == len(names), f'Sample name/position list is borked' 

    for x, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, x)
        #yield from alignement_gisaxs(angle = 0.15)
        #yield from bps.mvr(piezo.th, angle)
        
        det_exposure_time(meas_t, meas_t) 
        name_fmt = '{sample}_ai{angle}deg_{phi}deg_wa{waxs}'
        
        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
        
            for th in np.linspace(0.2, 0.4, 2):
                yield from bps.mvr(stage.th, th)
            
                sample_name = name_fmt.format(sample=name, angle='%3.2f'%th, phi = phi, waxs='%2.1f'%wa)
                sample_id(user_name='SN', sample_name=sample_name)
            
                print(f'\n\t=== Sample: {sample_name} ===\n')
                yield from bp.count(dets, num=1)
                yield from bps.mvr(stage.th, -th)
 
   
#incident angle scan at different position of the sample
def gisaxsnetzke2(meas_t=1):
    waxs_arc = np.linspace(0, 32.5, 6)
    dets = [pil300KW]
    
    xlocs = [-2000, 1000, 0, 1000, 2000]
    names = ['190919-12_01_aiscan_pos1', '190919-12_01_aiscan_pos2', '190919-12_01_aiscan_pos3', '190919-12_01_aiscan_pos4', '190919-12_01_aiscan_pos5']
    phi = 7
        
    assert len(xlocs) == len(names), f'Sample name/position list is borked' 

    for x, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, x)
        #yield from alignement_gisaxs(angle = 0.15)
        #yield from bps.mvr(piezo.th, angle)
        
        det_exposure_time(meas_t, meas_t) 
        name_fmt = '{sample}_ai{angle}deg_{phi}deg_wa{waxs}'
        
        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
        
            for th in np.linspace(0.05, 0.3, 6):
                yield from bps.mvr(piezo.th, th)
            
                sample_name = name_fmt.format(sample=name, angle='%3.2f'%th, phi = phi, waxs='%2.1f'%wa)
                sample_id(user_name='LC', sample_name=sample_name)
            
                print(f'\n\t=== Sample: {sample_name} ===\n')
                yield from bp.count(dets, num=1)
                yield from bps.mvr(piezo.th, -th)   
                
"""
# DONT USE!!!! realignement of tyhe sampl at each phi
def gisaxsnetzke3(meas_t=0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a phi-scan that RE-ALIGNS the sample at each in-plane rotation (phi). For
    #   each sample and each phi it re-runs the GISAXS alignment, then sweeps WAXS arc -> incidence
    #   angle -> energy, taking WAXS images. (The author's own note above says "DONT USE" — keeping
    #   that as-is; this annotation is just for reference.)
    #
    # 💡 NEWER, EASIER WAY: re-aligning at each phi is exactly what align_sample is for in
    #   'smi_plans' — pass align=align_sample to your acquire/giwaxs run and it re-aligns and saves
    #   the alignment result with the data, so you don't hand-call alignement_gisaxs_* and stash
    #   ref_th_0 yourself. Compose phi/incidence/energy as axes (see gisaxsnetzke above).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the rotation
    #   stage 'prs' was removed — it's now 'stage.phi'; (3) 'det_exposure_time(...)' no longer sets
    #   the exposure unless run as a plan. See the ⚠️ notes on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    waxs_arc = np.linspace(0, 45.5, 8)  # (2th_min 2th_max steps)
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    xlocs = [-44500, -34800, -25700, -15500, -5000, 6900, 15200, 25500, 35500, 46800]
    names = [
        "RY13_phioffset",
        "RY15_phioffset",
        "RY16_phioffset",
        "RY17_phioffset",
        "RY18_phioffset",
        "RY19_phioffset",
        "RY21_phioffset",
        "RY26_phioffset",
        "TiN1_phioffset",
        "TiN2_phioffset",
    ]
    angle_off_from02 = [0, 0.09, 0.2]
    energ = [9540, 9580]
    phis = [-22.5, 22.5]
    assert len(xlocs) == len(names), f"Sample name/position list is borked"
    # num = 0
    for x, name in zip(xlocs, names):
        # if num > 0:
        #    yield from bps.mvr(piezo.th, ref_th_0)
        yield from bps.mv(piezo.x, x)
        # yield from alignement_gisaxs(0.15)
        # ref_th_0 = piezo.th.position

        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_E{ene}eV_ai{angle}deg_phi{phi}deg_wa{waxs}"
        # phi is the slowest cycle:s
        for phi in phis:  # (phi_min phi_max steps)
            yield from bps.mv(prs, phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
            yield from alignement_gisaxs_hex_short(0.2)
            ref_th_0 = stage.th.position
            yield from bps.mvr(stage.th, ref_th_0 + 0.2)

            # waxs arc is scanned for a single phi
            for j, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                # then for a single waxs arc we change angle as relative move offset
                for a, an in enumerate(angle_off_from02):
                    yield from bps.mvr(stage.th, an)
                    # and the fastest cycle is the energy
                    for en in energ:
                        yield from bps.mv(energy, en)
                        real_an = an[a] + 0.2
                        sample_name = name_fmt.format(
                            sample=name,
                            ene="%2.0f" % en,
                            angle="%3.2f" % real_an,
                            phi=phi,
                            waxs="%2.1f" % wa,
                        )
                        sample_id(user_name="SN", sample_name=sample_name)

                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bp.count(dets, num=4)
                yield from bps.mv(stage.th, ref_th_0 + 0.2)

        yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
        # num +=1


"""        
#realignement of tyhe sampl at each phi
def gisaxsnetzke4(meas_t=1):
    waxs_arc = np.linspace(0, 32.5, 6) #(2th_min 2th_max steps)
    dets = [pil300KW]
    
    xlocs = [1010]
    names = ['190919-13_bkgnd3']
    angle = [0.2]
        
    assert len(xlocs) == len(names), f'Sample name/position list is borked' 
    num = 0
    for x, name in zip(xlocs, names):
        if num > 0:
            yield from bps.mvr(piezo.th, ref_th_0)
        yield from bps.mv(piezo.x, x)
        #yield from alignement_gisaxs(0.15)
        ref_th_0 = piezo.th.position
        
        det_exposure_time(meas_t, meas_t) 
        name_fmt = '{sample}_phiAlign2_ai{angle}deg_{phi}_wa{waxs}'
        
        for phi in np.linspace(65, 66, 2): #(phi_min phi_max steps)
            yield from bps.mv(prs, phi)
            yield from alignement_gisaxs_shorter(0.15)
            
            for j, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)
                for an in angle:
                    yield from bps.mvr(piezo.th, an)
                    sample_name = name_fmt.format(sample=name, angle='%3.2f'%an, phi = phi, waxs='%2.1f'%wa)
                    sample_id(user_name='LC', sample_name=sample_name)
               
                    print(f'\n\t=== Sample: {sample_name} ===\n')
                    yield from bp.count(dets, num=1)
                    yield from bps.mvr(piezo.th, -an)
                
        yield from bps.mv(prs, 0)
        num +=1
        
        
#Silicon (100) scan
def gisaxsnetzkeSi(meas_t=1):
    waxs_arc = np.linspace(0, 32.5, 6) #(2th_min 2th_max steps)
    dets = [pil300KW]
    
    #xlocs = [-30600, -14100, 3800, 20400, 38900]
   # xlocs = [-27990, -13700, 800, 16300, 32700, 47400]
    xlocs = [1010]
    names = ['SiScGOOD2']
    angle = [0.2]
        
    assert len(xlocs) == len(names), f'Sample name/position list is borked' 
    
    for x, name in zip(xlocs, names):
        yield from bps.mv(piezo.x, x)
        
        yield from bps.mv(GV7.open_cmd, 1 )
        yield from alignement_gisaxs(0.15)
        yield from bps.mv(GV7.close_cmd, 1 )
        
        
        det_exposure_time(meas_t, meas_t) 
        name_fmt = '{sample}_ai{angle}deg_{phi}deg_wa{waxs}'
        
        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)
      #  NE
            for phi in np.linspace(-90, 90, 181): #(phi_min phi_max steps)
                yield from bps.mv(prs, phi)
                
                for an in angle:
                    yield from bps.mvr(piezo.th, an)
            
                    sample_name = name_fmt.format(sample=name, angle='%3.2f'%an, phi = phi, waxs='%2.1f'%wa)
                    sample_id(user_name='LC', sample_name=sample_name)
                    
                    print(f'\n\t=== Sample: {sample_name} ===\n')
                    #Change from 4 to 1 exposure
                    yield from bp.count(dets, num=2)
                 #   yield from bp.count(dets, num=1)
                    yield from bps.mvr(piezo.th, -an)                    
                
        yield from bps.mv(prs, 0)
"""


def gisaxs_netzke_2020_3(meas_t=0.6):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a multi-sample phi-scan that walks each pre-aligned sample (using saved x/y/z
    #   and incidence angle), then loops WAXS arc -> in-plane rotation (phi) -> incidence offset ->
    #   energy, taking WAXS images. It even flips the WAXS-arc sweep direction depending on where
    #   the arc currently sits, to save travel time.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' covers the phi + incidence + energy matrix with composed
    #   axes, and the "sweep the arc the short way" trick is built into giwaxs_bar_arc_economy:
    #
    #     from smi_plans import acquire, motor_axis, energy_axis
    #     yield from acquire(name, [pil900KW],
    #         [motor_axis("phi", stage.phi, [-40, -20, 0]),    # was 'prs'
    #          energy_axis([9540, 9580])], t=meas_t)
    #
    #   (Just a tidier option — your loops below still work as-is EXCEPT for the ⚠️ lines, and the
    #    💡 sleep you can drop after migrating.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the rotation
    #   stage 'prs' was removed — it's now 'stage.phi'; (3) 'det_exposure_time(...)' no longer sets
    #   the exposure unless run as a plan. See the ⚠️ notes on those lines. (internal: Tier 1.)
    # === end smi_plans note ================================================
    waxs_arc = np.linspace(0, 45.5, 8)
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    # xlocs = [-44500, -34800, -25700, -15500, -5000, 6900, 15200, 25500, 35500, 46800]
    # names = ['RY13_phioffset','RY15_phioffset','RY16_phioffset','RY17_phioffset','RY18_phioffset','RY19_phioffset','RY21_phioffset','RY26_phioffset','TiN1_phioffset','TiN2_phioffset']
    # assert len(xlocs) == len(names), f'Sample name/position list is borked'

    angle_off_from02 = [0.20, 0.29, 0.40]
    energ = [9540, 9580]
    phis = [-40, -20, 0]

    ref_th_0 = stage.th.position

    for name, xs, zs, aiss, ys in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned
    ):
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss)

        det_exposure_time(meas_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t, meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_E{ene}eV_ai{angle}deg_phi{phi}deg_wa{waxs}"

        # phi is the slowest cycle:s
        if waxs.arc.position > 20:
            waxs_arc = np.linspace(0, 45.5, 8)[::-1]
        else:
            waxs_arc = np.linspace(0, 45.5, 8)

        for j, wa in enumerate(waxs_arc):
            yield from bps.mv(waxs, wa)

            for phi in phis:  # (phi_min phi_max steps)
                yield from bps.mv(prs, phi)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.

                # check waxs value and adjust waxs range
                for a, an in enumerate(angle_off_from02):
                    yield from bps.mv(stage.th, ref_th_0 + an)

                    for en in energ:
                        yield from bps.mv(energy, en)
                        yield from bps.sleep(1)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)

                        sample_name = name_fmt.format(
                            sample=name,
                            ene="%2.0f" % en,
                            angle="%3.2f" % an,
                            phi=phi,
                            waxs="%2.1f" % wa,
                        )
                        sample_id(user_name="SN", sample_name=sample_name)

                        print(f"\n\t=== Sample: {sample_name} ===\n")
                        yield from bp.count(dets, num=2)

            yield from bps.mv(stage.th, ref_th_0)
        yield from bps.mv(prs, 0)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.


def alignement_netzke():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an up-front alignment pass — it visits each sample on the bar, runs the
    #   grazing-incidence alignment, and remembers the found incidence angle + aligned y for each
    #   (stored in the global lists incident_angles / y_piezo_aligned that the scans above reuse).
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you don't pre-align into global lists and hope the later
    #   scan reuses them — instead you pass align=align_sample to your acquire/giwaxs run, so each
    #   sample is aligned right before it's measured and the alignment result is SAVED alongside the
    #   data automatically. The old 'SMI_Beamline().modeAlignment()/modeMeasurement()' dance is
    #   handled internally. (Nothing here is broken; this is just the modern, less error-prone flow.)
    # === end smi_plans note ================================================
    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned

    # names = ['ALLS80', 'ALLS87', 'RK3', 'RK14', 'ALLS88', 'ALLS101', 'RK16', 'RK19_800C_1', 'RK19_800C_2', 'RK19_750C', 'S25', 'RK13', 'RK2']
    # x_piezo = [-50800, -42800, -35800, -29800, -22800, -14800, -7800, 200, 7200, 15200, 22200, 29200, 36200]
    # z_piezo = [  1660,   1660,   1460,    960,    560,    160,   160, 160, -240,  -240,  -440,  -740, -1040]

    names = [
        "ALLS82",
        "ALLS102",
        "ALLS112",
        "ALLS68",
        "ALLS77",
        "RK1",
        "ALLS76",
        "ALLS78",
        "ALLS84",
        "ALLS103",
        "ALLS91",
        "ALLS86",
        "RK20",
        "RA3",
        "ALLS81",
    ]
    x_piezo = [
        -50000,
        -44000,
        -37000,
        -30000,
        -23000,
        -16000,
        -9000,
        -2000,
        5000,
        13000,
        20000,
        28000,
        36000,
        43000,
        50000,
    ]
    z_piezo = [
        560,
        560,
        560,
        560,
        360,
        360,
        360,
        160,
        160,
        -40,
        -340,
        -340,
        -540,
        -740,
        -1540,
    ]

    incident_angles = []
    y_piezo_aligned = []

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, xs_piezo, zs_piezo in zip(names, x_piezo, z_piezo):
        yield from bps.mv(piezo.x, xs_piezo)
        # yield from bps.mv(piezo.y, ys_piezo)
        yield from bps.mv(piezo.z, zs_piezo)

        yield from alignement_gisaxs_multisample(angle=0.15)

        incident_angles = incident_angles + [piezo.th.position]
        y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

        print(incident_angles)
        print(y_piezo_aligned)

    yield from smi.modeMeasurement()

    print(incident_angles)
    print(y_piezo_aligned)


# y_piezo_aligned = array([7271.133, 7235.479, 7214.69 , 7177.205, 7144.364, 7151.092, 7063.728, 7081.229, 7058.901, 7029.661, 6874.397, 6958.301, 6971.521])
# incident_angles = [ 0.341887,  0.978769,  0.193741,  0.478084,  0.728999,  0.429933, 0.929884,  0.660595,  0.459128,  0.078492,
#     0.262723,  0.100632, -0.328383]

# incident_angles = array([-1.226571, -0.552806,  0.28984 , -0.419068,  0.103962, -0.162368, 0.42735 , -0.451796,  0.124283, -1.463176, -0.168004,
# -0.62571, -0.23411 , -0.106975, -0.307471])
# y_piezo_aligned =array([7144.954, 7172.772, 7184.785, 7133.138, 7088.943, 7091.481, 7050.918, 7039.402, 7007.882, 6938.484, 6947.378, 6943.667,
# 6901.995, 6796.63 , 6892.514])

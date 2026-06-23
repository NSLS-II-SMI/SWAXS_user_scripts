####line scab


def run_gi_sweden_SAXS(tim=0.5, sample="Test", ti_sl=60):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence SAXS run — aligns the surface, takes a y-scan
    #   image set, then repeatedly nudges piezo.x and takes more y-scans, pausing between
    #   passes (a slow time series across a surface/interface).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that records
    #   the angle, positions, beam intensity and elapsed time straight into the saved data
    #   and the file name (so you don't hand-build "{angle}deg_{ti}sec"). Alignment is done
    #   once via align_sample, and a y line-scan is map_line_run; for the repeated passes use
    #   a kinetics helper. Roughly:
    #
    #     from smi_plans import giwaxs_run, map_line_run, time_series_run
    #     # ...align once with align_sample, then per pass:
    #     yield from map_line_run(sample, piezo.y, -20, 20, 41, dets=[pil2M])
    #
    #   (Just a tidier option to try later — your script below still works as-is, except the
    #    'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================
    # Slowest cycle:
    name = "TP"
    num = 2
    x_interface = [piezo.x.position]

    x_surface = x_interface[0] - 1500
    piezo_y_range = [-20, 20, 41]
    samples = [sample + "_interface"]

    surface_sample = sample + "_surface"
    angle = 0.1

    # Detectors, motors:
    dets = [pil2M, pil2Mroi2]  # WAXS detector ALONE
    x_offset = 10
    t0 = time.time()

    yield from bps.mv(piezo.x, x_surface)
    yield from alignement_gisaxs(angle)
    yield from bps.mvr(piezo.th, angle)

    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (smi_plans' technique runs set it for you via t=.)
    sample_id(user_name=name, sample_name=surface_sample)
    yield from bp.rel_scan(dets, piezo.y, *piezo_y_range)

    name_fmt = "{sample}_{angle}deg_{ti}sec"
    #    param   = '16.1keV'
    assert len(x_interface) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, s in zip(x_interface, samples):
        yield from bps.mv(piezo.x, x)
        # yield from alignement_gisaxs_shorter(angle)
        # yield from bps.mvr(piezo.th, angle)
        for i in range(num):
            yield from bps.mv(piezo.x, x + x_offset * i)
            t1 = time.time()
            t_min = np.round((t1 - t0))
            sample_name = name_fmt.format(sample=s, angle=angle, ti="%5.5d" % t_min)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_scan(dets, piezo.y, *piezo_y_range)

            yield from bps.sleep(ti_sl)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)).


def gisaxs_KTH_2021_1(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a multi-sample grazing-incidence (GISAXS) run — it aligns each sample
    #   in turn (recording its incident angle and aligned height), then revisits each sample
    #   and takes SAXS images while stepping the incident angle and nudging piezo.x.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   whole bar of grazing samples in one call — it moves to each sample, aligns it, loops
    #   the incident angles, and records which sample/angle (and beam readings) each image
    #   belongs to, so you don't keep your own incident_angles/y_piezo_aligned lists or
    #   build "{angle}deg_pos{pos}" by hand. The pattern is:
    #
    #     from smi_plans import giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo,
    #                                       z=z_piezo, hexa_x=x_hexa)
    #     yield from giwaxs_bar(samples, incident_angles=np.linspace(0.08, 0.4, 17),
    #                           t=t, align=align_sample)
    #
    #   (Just a tidier option to try later — your script below still works as-is, except the
    #    'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================

    global names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, xs_hexa

    # names = ['1BL_DI', '3BL_DI', '5BL_DI', '1BL_NaCl', '3BL_NaCl', '5BL_NaCl', 'Si_wafer', 'PVAm', 'PVAm_CNF', 'PVAm_CNF_PAH', 'PEI']

    # x_piezo = [59000, 55000, 43000, 30000, 17000, 4000, -9000, -22000, -33000, -45000, -50000]
    # y_piezo = [ 7400,  7400,  7400,  7400,  7400, 7400,  7400,   7400,   7400,   7400,   7400]
    # z_piezo = [    0,     0,     0,     0,     0,    0,     0,      0,      0,      0,      0]
    # x_hexa =  [    8,     0,     0,     0,     0,    0,     0,      0,      0,      0,     -6]
    # incident_angles = [0.079829, 0.113749, 0.022469, 0.002876, 0.156458, 0.017894, 0.472448, -0.001836, 0.03759, -0.062716, 0.033808]
    # y_piezo_aligned = [7598.066, 7613.373, 7603.519, 7569.923, 7566.072, 7542.689, 7521.385, 7491.759, 7484.312, 7445.632, 7480.081]

    names = ["PEI_CNF", "PEI_CNF_PAH"]

    x_piezo = [18000, 1000]
    y_piezo = [7400, 7400]
    z_piezo = [0, 0]
    x_hexa = [0, 0]
    incident_angles = []
    y_piezo_aligned = []

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

    smi = SMI_Beamline()
    yield from smi.modeAlignment(technique="gisaxs")

    for name, xs_piezo, zs_piezo, ys_piezo, xs_hexa in zip(
        names, x_piezo, z_piezo, y_piezo, x_hexa
    ):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs_piezo)
        yield from bps.mv(piezo.y, ys_piezo)
        yield from bps.mv(piezo.z, zs_piezo)
        yield from bps.mv(piezo.th, 0)

        # if ys_piezo>0:
        yield from alignement_gisaxs_multisample(angle=0.08)
        # else:
        #     yield from bps.mv(piezo.th, -1)
        #     yield from alignement_gisaxs_multisample_special(angle = 0.08)

        incident_angles = incident_angles + [piezo.th.position]
        y_piezo_aligned = y_piezo_aligned + [piezo.y.position]

    yield from smi.modeMeasurement()
    print(incident_angles)
    print(y_piezo_aligned)

    angle = [0.1]
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    for name, xs, zs, aiss, ys, xs_hexa in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa
    ):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss)

        for an in angle:
            for i in range(1, 11, 1):
                yield from bps.mv(piezo.x, xs - i * 200)
                yield from bps.mv(piezo.th, aiss + an)
                name_fmt = "{sample}_sdd6.2m_16.1keV_ai{angl}deg_pos{pos}"
                sample_name = name_fmt.format(
                    sample=name, angl="%3.2f" % an, pos="%2.2d" % i
                )
                sample_id(user_name="PT", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

    angle = np.linspace(0.08, 0.4, 17)
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure but is now a "plan", so the plain call does nothing. Write  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.

    for name, xs, zs, aiss, ys, xs_hexa in zip(
        names, x_piezo, z_piezo, incident_angles, y_piezo_aligned, x_hexa
    ):
        yield from bps.mv(stage.x, xs_hexa)
        yield from bps.mv(piezo.x, xs)
        yield from bps.mv(piezo.y, ys)
        yield from bps.mv(piezo.z, zs)
        yield from bps.mv(piezo.th, aiss)

        for j, an in enumerate(angle):
            yield from bps.mv(piezo.x, xs - 2500 - j * 50)
            yield from bps.mv(piezo.th, aiss + an)
            name_fmt = "{sample}_sdd6.2m_16.1keV_ai{angl}deg"
            sample_name = name_fmt.format(sample=name, angl="%3.2f" % an)
            sample_id(user_name="PT", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)).


def run_gi_sweden_GISAXS(tim=0.5, sample="Test", ti_sl=77):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence run that repeatedly nudges piezo.x and takes a
    #   y-scan image set at each spot, pausing between passes (a slow time series across a
    #   surface/interface). The alignment lines here are commented out.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that records
    #   the angle, positions, beam intensity and elapsed time into the saved data and the
    #   file name (so you don't hand-build "{angle}deg_{ti}sec"). A y line-scan is
    #   map_line_run; for the repeated passes use a kinetics helper. Roughly:
    #
    #     from smi_plans import map_line_run, time_series_run
    #     yield from map_line_run(sample, piezo.y, -20, 20, 41, dets=[pil2M])
    #
    #   (Just a tidier option to try later — your script below still works as-is, except the
    #    'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================
    # Slowest cycle:
    name = "TP"
    num = 1
    x_interface = [piezo.x.position]

    x_surface = x_interface[0] - 500

    piezo_y_range = [-20, 20, 41]
    samples = [sample + "_interface"]

    surface_sample = sample + "_surface"
    angle = 0.1

    # Detectors, motors:
    dets = [pil2M, pil2Mroi2]  # WAXS detector ALONE
    x_offset = 10
    t0 = time.time()

    # yield from bps.mv(piezo.x, x_surface)
    # yield from alignement_gisaxs(angle)
    # yield from bps.mvr(piezo.th, angle)

    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (smi_plans' technique runs set it for you via t=.)
    sample_id(user_name=name, sample_name=surface_sample)
    # yield from bp.rel_scan(dets, piezo.y, *piezo_y_range)

    # yield from bps.mv(piezo.x, x_interface)

    name_fmt = "{sample}_{angle}deg_{ti}sec"
    #    param   = '16.1keV'
    assert len(x_interface) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, s in zip(x_interface, samples):
        yield from bps.mv(piezo.x, x)
        # yield from alignement_gisaxs_shorter(angle)
        # yield from bps.mvr(piezo.th, angle)
        for i in range(num):
            # x_pos = [piezo.x.position]
            # yield from bps.mv(piezo.x, x_pos+x_offset)
            yield from bps.mv(piezo.x, x + x_offset * i)
            t1 = time.time()
            t_min = np.round((t1 - t0))
            sample_name = name_fmt.format(sample=s, angle=angle, ti="%5.5d" % t_min)
            sample_id(user_name=name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.rel_scan(dets, piezo.y, *piezo_y_range)

            yield from bps.sleep(ti_sl)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)).

def alignment_start(sample_name='alignment'):
    """
    Attenuators in, beamstop out, ROI1 set to direct beam
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into "alignment mode" (attenuators in, beamstop out)
    #   and sets the direct-beam region-of-interest, ready for you to align by hand.
    #
    # 💡 NEWER, EASIER WAY: with the 'smi_plans' helper library you don't usually flip into
    #   alignment mode by hand around each measurement. Alignment is done once up front via
    #   align_sample (or align=... inside the grazing presets), which handles mode-switching
    #   and ROIs and records the result with your data. (Nothing here is broken.)
    # === end smi_plans note ================================================

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    sample_id(user_name='test', sample_name=sample_name)
    proposal_id('2023_2', '311564_test')


def alignment_start_angle(angle=0.10):
    """
    Attenuators in, beamstop out, ROI1 set to direct beam
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline into alignment mode and sets the *reflected*-beam
    #   ROI for the given grazing angle, ready for reflected-beam alignment.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' align_sample does the direct- and reflected-beam
    #   alignment for you (including setting these ROIs) and records the result with your
    #   data, so this manual step isn't needed once you migrate. (Nothing here is broken.)
    # === end smi_plans note ================================================

    smi = SMI_Beamline()
    yield from smi.modeAlignment()

    # Set reflected beam ROI
    yield from smi.setReflectedBeamROI(total_angle=angle, technique="gisaxs")


def alignment_stop():
    """
    Attenuators out, beamstop in,
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: puts the beamline back into "measurement mode" (attenuators out,
    #   beamstop in) once alignment is finished.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' align_sample / grazing presets switch back to
    #   measurement mode for you after aligning, so this manual step isn't needed once you
    #   migrate. (Nothing here is broken.)
    # === end smi_plans note ================================================

    smi = SMI_Beamline()
    yield from smi.modeMeasurement()
    proposal_id('2023_2', '311564_Pettersson')


def alignment_org(angle=0.1):
    """
    Align using an original script
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: runs the older multi-sample GISAXS alignment helper and stashes the
    #   resulting flat-sample angle in RE.md['ai_0'] for later use.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' align_sample aligns the sample and records the
    #   aligned angle WITH the data automatically (no need to stash it in RE.md by hand),
    #   and the grazing presets can call it for you via align=... (Nothing here is broken.)
    # === end smi_plans note ================================================
    proposal_id('2023_2', '311564_test')
    yield from alignement_gisaxs_multisample(angle=angle)
    RE.md['ai_0'] = piezo.th.user_setpoint.get()
    proposal_id('2023_2', '311564_Pettersson')

def run_loop_measurement(t=0.5, name='test', loops=4, pump_t=180, total_t=600, jump_x=10):
    """
    RE(run_loop_measurement(t=1, name='1bl_PEI_10mM', loops=7, pump_t=210, total_t=720, jump_x=10))


    Take measurements in the loop

    Sample has to be aligned before starting the script and theta
    angle at 0 deg (flat sample).

    Parameters:
        t (float): detector exposure time of one frame,
        name (str): sample name,
        loops (int): number of loops (measurements taken),
        pump_t (flaot): initial delay to finish pumping,
        total_t (float): total time of one measurement iteration,
        jump_x (foat): relative move in piezo x after each y scan, in um,
            (be careful on the direction, move relative to - jump below).
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time-loop measurement on a pre-aligned sample — each cycle
    #   it waits for a pump step, then takes grazing-incidence y-scans at a couple of
    #   incident angles and WAXS-arc positions, then waits out the rest of the cycle time,
    #   repeating for several loops.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with
    #   time-series/kinetics helpers that schedule the cycles and record the elapsed time +
    #   angle + positions + beam readings into the saved data for you (so you don't manage
    #   time.time() bookkeeping or build "{name}_time..._ai{ai}" by hand). The y-scan is a
    #   map_line_run. Roughly:
    #
    #     from smi_plans import kinetics_run, map_line_run
    #     # ...within each cycle, per (arc, angle):
    #     yield from map_line_run(name, piezo.y, -16, 16, 33, dets=[pil2M, pil900KW])
    #
    #   (Just a tidier option to try later — your loop below still works as-is, except the
    #    'det_exposure_time' lines marked ⚠️.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' lines below (see the ⚠️ notes
    #   on them).
    # === end smi_plans note ================================================

    incident_angles = [0.1, 0.4]
    waxs_arc = [20, 0]
    user = "TP"

    condition = (
        ( -1 < waxs.arc.position )
        and ( waxs.arc.position < 1 )
        and (waxs_arc[0] == 20)
    )

    if condition:
        waxs_arc = waxs_arc[::-1]
    
    ranges = { 0.1 : [-16, 16, 33],
               0.4 : [-25, 25, 51],
    }

    try:
        ai0 = RE.md['ai_0']
    except:
        yield from bp.count([])
        ai0 = db[-1].start['ai_0']
        print('Failed to acces RE.md')
    print(f'\n\nSample flat at theta = {ai0}')
    
    proposal_id('2023_2', '311564_Pettersson')
    #det_exposure_time(t, t)
    
    t_initial = time.time()

    for i in range(loops):
        t_start = time.time()
        print('Cycle number',i+1,'started at', (t_start - t_initial)/60)

        # Wait initial time for pumping to finish
        print(f'Start pumping now, going to wait for {pump_t} s\n')
        while (time.time() - t_start) < pump_t:
            print(f'Pumping time: {(time.time() - t_start):.1f} s')
            yield from bps.sleep(10)

        # Go over SAXS and WAXS
        t_measurement = ( time.time() - t_initial ) / 60
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]

            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)
                yield from bps.mvr(piezo.x, - jump_x)

                t2 = 2 * t if ai == 0.4 else t
                det_exposure_time(t2, t2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t2, t2)  — or at the prompt:  RE(det_exposure_time(t2, t2)). (smi_plans' technique runs set it for you via t=.)

                try:
                    y_range = ranges[ai]
                except:
                    y_range = [-10, 10, 11]
                
                sample_name = f'{name}{get_scan_md()}_time{t_measurement:.1f}_ai{ai}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.rel_scan(dets, piezo.y, *y_range, md=dict(ai=ai))
        
        yield from bps.mv(waxs, waxs_arc[0],
                          piezo.th, ai0)

        # Wait until the total loop time passes
        if i + 1 < loops:
            print(f'Waiting for the loop to last {total_t} s in total\n')
            sleep_count = 0
            while (time.time() - t_start) < total_t:
                sleep_count += 1
                if (sleep_count % 10 == 0):
                    print(f'Total time: {(time.time() - t_start):.1f} s')
                yield from bps.sleep(1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this resets the exposure, but it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).


"""
2023-2
Manual alignment 

# direct beam alignment
RE(alignment_start())

# half cut on direct beam
RE(rel_scan([pil2M], piezo.y, -300, 300, 21))
ps(der=True)
RE(mv(piezo.y, ps.cen)) # or replace ps.cen with a valid piezo y position

# th scan (rocking) on direct beam
RE(rel_scan([pil2M], piezo.th, -1, 1, 21))
ps()
RE(mv(piezo.th, ps.cen)) # or replace ps.cen with a valid th position
RE.md['ai_0'] = piezo.th.user_setpoint.get()

# repeat halfcat on direct beam if move in th was substantial
# RE(rel_scan([pil2M], piezo.y, -100, 100, 21))
# ps(der=True)
# RE(mv(piezo.y, ps.cen)) # or replace ps.cen with a valid piezo y position

# Reflected beam alignment
# remember to change angle for values different than 0.1
RE(alignment_start_angle(angle=0.1))
RE(mvr(piezo.th, 0.1))
# alternatively RE(mv(piezo.th,RE.md['ai_0'] + 0.1))

# th scan reflected
RE(rel_scan([pil2M], piezo.th, -0.2, 0.2, 31))
ps()
RE(mv(piezo.th, ps.cen))
RE.md['ai_0'] = piezo.th.user_setpoint.get() - 0.1

# y scan reflected
RE(rel_scan([pil2M], piezo.y, -50, 50, 21))
ps()
RE(mv(piezo.y, ps.cen))  # or replace ps.cen with a valid piezo y position

# final refinement of th
RE(rel_scan([pil2M], piezo.th, -0.025, 0.025, 21))
ps()
RE(mv(piezo.th, ps.cen))
RE.md['ai_0'] = piezo.th.user_setpoint.get() - 0.1

# if aligned and ready for data
RE(alignment_stop())

# if need to change angle of incident from 0.1 to differnt do it now
to thetha 0

RE(mvr(piezo.th, -0.1))
or
RE(mv(piezo.th, RE.md['ai_0']))
"""

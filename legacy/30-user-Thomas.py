# 2023-May-22 Mon
# 16.1 keV, 25um*5um beam, Transmission Linkam with LN2, vac
# proposal_id("2023_2", "312283_Subramanian", analysis=True)
# RE.md['SAF_number'] = 311336
# RE.md['SAXS_setup'] = {'sdd': 9200, 'beam_centre': [395, 558], 'bs': 'rod', 'energy': 16100}
# 
# RE(rel_scan([pil2M], stage.y, -2, 2, 15)); ps()
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# *Auto Evac (click), wait until in vac, yellow turns green, open valves before and after WAXS chamber, 
# Search hutch and close
# RE(shopen())
# Start det3: ctrl+x twice
# type: setthreshold energy 16100 autog 11000
#
# # Ctrl+s to save this file
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Thomas.py
#
# Ctrl+c once/twice; RE.abort()
# bsui
# %run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Thomas.py
#
# RE(shclose())
# To take out sample: wait for sample to go back to RT
# *Auto Bleed to air (click), open WAXS soft vent, 6.5e2
# ---------------------------------------------------------------
# Note: Linkam Transmission, HEXAPOD around x=-9.3, y=1, z=-7.257
# beamstop_save()

def move_waxs(waxs_angle=20):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS detector arc to a given angle. Just a motor move.
    # 💡 NEWER, EASIER WAY: nothing here is broken — smi_plans moves 'waxs.arc' as a normal motor
    #   inside its plans, so a one-line wrapper like this usually isn't needed. (No acquisition.)
    # === end smi_plans note ================================================
    yield from bps.mv(waxs, waxs_angle)

    
# 2023-May
# Measures at 0, 15 waxs detector angles; Take both SAXS and WAXS
# RE(run_measure1(t=0.5, user_name='VS', sam_name='PS-PDMS_5033_run1'))
def run_measure1(t=0.5, user_name='VS', sam_name='PS-PDMS_5033'):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes SAXS+WAXS at two WAXS arc angles (0 and 15 deg) and stamps the temperature, WAXS
    #   angle and position into the file name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that takes a
    #   SAXS/WAXS measurement for you and records the temperature, WAXS arc, position and
    #   beam intensity straight INTO the data and file name (so you can drop the by-hand
    #   name building that reads ls.input_A_celsius / stage positions):
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("PS-PDMS_5033", [pil900KW, pil2M],
    #                        [motor_axis("waxs", waxs.arc, [0, 15])],
    #                        t=t, reads=[ls])          # records the Lakeshore temperature too
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    t0 = time.time()
    waxs_angles = np.array([0, 15]) ## Takes about 30sec to move

    for waxs_angle in waxs_angles:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)
        if waxs_angle >= 15: # WAXS, SAXS
            dets = [pil900KW, pil2M]
        else:                # WAXS
            dets = [pil900KW]

        x = stage.x.position
        y = stage.y.position
        temp = ls.input_A_celsius.get()  # ls.ch1_read.value

        name_fmt = "{sample}_16.1keV_9.2m_{temperature}C_waxs{waxs_angle:05.2f}_x{x:05.3f}_y{y:05.3f}_{t:05.2f}s"
        sample_name = name_fmt.format(
            sample=sam_name,
            temperature="%1.1f" % temp,
            waxs_angle=waxs_angle,
            x=x,
            y=y,
            t=t,
        )
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=user_name, sample_name=sample_name)
        yield from bp.count(dets, num=1)

    print('Took {}s'.format(time.time()-t0))

# For Isothermal
# RE(run_isothermal(t=0.5, Nmax=1000, user_name='VS', sam_name='PS-PDMS_5033_run1', time_sleep_sec=5, y_step=0.002))
def run_isothermal(t=0.5, Nmax=1000, user_name='VS', sam_name='test', time_sleep_sec=10, y_step=0.002):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an isothermal time series — it loops up to Nmax times, nudging y a touch each pass, takes a
    #   SAXS+WAXS frame, stamps temperature/position into the name, and sleeps between frames.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built in-situ time-series plan. It takes frames on a schedule and records
    #   the REAL elapsed time, temperature, position and beam intensity INTO each frame (so
    #   the time/temperature live in the data, not just the file name), and you don't manage
    #   the counter/clock by hand:
    #
    #     from smi_plans import isothermal_kinetics_run
    #     yield from isothermal_kinetics_run("PS-PDMS_5033", dets=[pil900KW, pil2M], t=t,
    #                       period=time_sleep_sec, num=Nmax, reads=[ls])
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    waxs_angle = 15
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil2M]

    for nn in range(Nmax):
        yield from bps.mvr(stage.y, y_step)
        x = stage.x.position
        y = stage.y.position
        temp = ls.input_A_celsius.get()  # ls.ch1_read.value

        name_fmt = "{sample}_16.1keV_9.2m_{temperature}C_waxs{waxs_angle:05.2f}_x{x:05.3f}_y{y:05.3f}_{t:05.2f}s"
        sample_name = name_fmt.format(
            sample=sam_name,
            temperature="%1.1f" % temp,
            waxs_angle=waxs_angle,
            x=x,
            y=y,
            t=t,
        )
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=user_name, sample_name=sample_name)
        yield from bp.count(dets, num=1)

        print("\nnn={}; Sleeping for {}s".format(nn, time_sleep_sec))
        time.sleep(time_sleep_sec)


# Need to select det & specify WAXs angle
# SAXS: RE(run_test(t=0.5, dets = [pil2M], waxs_angle=15, user_name='test', sam_name='test'))
# WAXS: RE(run_test(t=0.5, dets = [pil900KW], waxs_angle=0, user_name='test', sam_name='test'))
def run_test(t=0.5, dets = [pil2M], waxs_angle=15, user_name='VS', sam_name='test'):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a flexible single shot — you pick the detector and WAXS arc angle, it stamps temperature/
    #   position into the name and takes one frame.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that takes a
    #   SAXS/WAXS measurement for you and records the temperature, WAXS arc, position and
    #   beam intensity straight INTO the data and file name (so you can drop the by-hand
    #   name building that reads ls.input_A_celsius / stage positions):
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("test", [pil900KW, pil2M],
    #                        [motor_axis("waxs", waxs.arc, [0, 15])],
    #                        t=t, reads=[ls])          # records the Lakeshore temperature too
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(waxs, waxs_angle)
    x = stage.x.position
    y = stage.y.position
    temp = ls.input_A_celsius.get()  # ls.ch1_read.value

    name_fmt = "{sample}_16.1keV_9.2m_{temperature}C_waxs{waxs_angle:05.2f}_x{x:05.3f}_y{y:05.3f}_{t:05.2f}s"
    sample_name = name_fmt.format(
        sample=sam_name,
        temperature="%1.1f" % temp,
        waxs_angle=waxs_angle,
        x=x,
        y=y,
        t=t,
    )
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name=user_name, sample_name=sample_name)
    yield from bp.count(dets, num=1)





"""
8.3m
  smi_config_update = smi_config.append(current_config_DF, ignore_index=True)
1.248555 1.248555 -13.000182 0.0 8.649654
"""

# 2021-Jul-11
# RE(run_Thomas_temp2(t=0.5, name='VS', samples=['test'], Nmax=1, time_sleep_sec=0))
# RE(run_Thomas_temp2(t=0.5, name='VS', samples=['PS-PDMS_5033'], Nmax=1, time_sleep_sec=0, time_interval_sec=0))

def run_Thomas_temp2(
    t=0.5,
    name="VS",
    samples=["thermal_test"],
    Nmax=1,
    time_sleep_sec=120,
    time_interval_sec=10,
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature time series — for each sample it cycles over WAXS arcs and repeats up to Nmax
    #   times with sleeps, stamping temperature into the name (used for thermal studies).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built in-situ time-series plan. It takes frames on a schedule and records
    #   the REAL elapsed time, temperature, position and beam intensity INTO each frame (so
    #   the time/temperature live in the data, not just the file name), and you don't manage
    #   the counter/clock by hand:
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run("thermal_test", dets=[pil900KW, pil2M], t=t,
    #                       period=time_sleep_sec, num=Nmax, reads=[ls])
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    #x_list = [-2.6]  # [-3.4] #[-3.5] #HEXAPOD
    #y_list = [2.3]  # [2.3] #[2.25]
    # samples = ['thermal1']

    # 2023-May
    x_list = [-8.6]  
    y_list = [0.81]  #z=-7.257

    # Detectors, motors:
    dets = [pil900KW, pil2M]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t0 = time.time()

    waxs_angles = np.array([0, 15])

    # time.sleep(time_sleep_sec)
    yield from bps.sleep(time_sleep_sec)

    for waxs_angle in waxs_angles:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)
        if waxs_angle >= 15:
            dets = [pil900KW, pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        else:
            dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
        print("Meausre saxs and/or waxs here for w-angle=%s" % waxs_angle)

        for i in range(Nmax):
            t1 = time.time()
            temp = ls.input_A_celsius.get()  # ls.ch1_read.value
            for x, y, names in zip(x_list, y_list, samples):
                yield from bps.mv(stage.x, x)  # HEXAPOD
                yield from bps.mv(stage.y, y)

                #name_fmt = "{sample}_16.1keV_8.3m_{time}s_{temperature}C_waxs{waxs_angle:05.2f}_x{x:04.2f}_y{y:04.2f}_{scan_id}"
                name_fmt = "{sample}_16.1keV_9.2m_{time}s_{temperature}C_waxs{waxs_angle:05.2f}_x{x:04.2f}_y{y:04.2f}_{scan_id}"
                sample_name = name_fmt.format(
                    sample=names,
                    time="%1.1f" % (t1 - t0),
                    temperature="%1.1f" % temp,
                    waxs_angle=waxs_angle,
                    x=x,
                    y=y,
                    scan_id=RE.md["scan_id"],
                )

                # xss = np.linspace(x - 500, x + 500, 3)
                # yss = np.linspace(y - 300, y + 300, 3)
                # yss, xss = np.meshgrid(yss, xss)
                # yss = yss.ravel()
                # xss = xss.ravel()

                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)
                yield from bp.count(dets, num=1)

            yield from bps.sleep(time_interval_sec)

            # time.sleep(time_sleep_sec)

    sample_id(user_name="test", sample_name="test")


# 2023-May-22 Static transmission
# RE(run_tswaxs_single(t=10, user_name='StaticT', sam_name='VS_sam1', waxs_angles = [0]))
def run_tswaxs_single(t=10, user_name='StaticT', sam_name='PS-PDMS', waxs_angles = [0], grid=0, Nmax=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a static-temperature SAXS+WAXS capture on one sample — takes frames at the chosen WAXS arc
    #   angle(s) (optionally over a grid / repeated Nmax times).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that takes a
    #   SAXS/WAXS measurement for you and records the temperature, WAXS arc, position and
    #   beam intensity straight INTO the data and file name (so you can drop the by-hand
    #   name building that reads ls.input_A_celsius / stage positions):
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("PS-PDMS", [pil900KW, pil2M],
    #                        [motor_axis("waxs", waxs.arc, [0, 15])],
    #                        t=t, reads=[ls])          # records the Lakeshore temperature too
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # 59000 (sample1),-44000 (AgBH)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t0 = time.time()
    #waxs_angles = np.array([15, 0])

    for waxs_angle in waxs_angles:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)
        if waxs_angle >= 15:
            dets = [pil900KW, pil2M] #, pil300KW]
        else:
            dets = [pil900KW] #, pil300KW]
        print("Meausre saxs and/or waxs here for w-angle=%s" % waxs_angle)

        for i in range(Nmax):
            x = piezo.x.position
            y = piezo.y.position

            name_fmt = "{sample}_16.1keV_9.2m_waxs{waxs_angle:05.2f}_x{x:04.2f}_y{y:04.2f}_{t:05.2f}s"
            sample_name = name_fmt.format(
                sample=sam_name,
                waxs_angle=waxs_angle,
                x=x,
                y=y,
                t=t,
                #scan_id=RE.md["scan_id"],
            )

            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name=user_name, sample_name=sample_name)

            if grid == 0:
                yield from bp.count(dets, num=1)
            else:
                xss = np.linspace(x - 300, x + 300, 3)
                yss = np.linspace(y - 300, y + 300, 3)
                yss, xss = np.meshgrid(yss, xss)
                yss = yss.ravel()
                xss = xss.ravel()
                yield from bp.list_scan(
                    dets, piezo.x, xss.tolist(), piezo.y, yss.tolist()
                )

    sample_id(user_name="test", sample_name="test")



# RE(run_tswaxs(t=2, name = 'T', waxs_angles = [15]))
def run_tswaxs(t=10, name="T", grid=0, Nmax=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS+WAXS capture — takes frames at the chosen WAXS arc angle(s), optionally over a grid
    #   and repeated Nmax times.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that takes a
    #   SAXS/WAXS measurement for you and records the temperature, WAXS arc, position and
    #   beam intensity straight INTO the data and file name (so you can drop the by-hand
    #   name building that reads ls.input_A_celsius / stage positions):
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("T", [pil900KW, pil2M],
    #                        [motor_axis("waxs", waxs.arc, [0, 15])],
    #                        t=t, reads=[ls])          # records the Lakeshore temperature too
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # 59000 (sample1),-44000 (AgBH)
    
    # x_list = [-31430, -18430, 1570, 9570, 23570, 33570, 37370, 43170]
    # y_list = [-2900, -2900, -2900, -2900, -2900, -2900, -2900, -2800]  
    # samples = ["KL13", "KL12", "KL1", "KL2", "KL3","KL4", "KL5", "Kapton2"]
    x_list = [42120]
    y_list = [-8000]
    samples = ['Kapton3']
    # # HEX: -3.41, y 1.67, z-1.4
    # sam6: x-7830, y -10950, z7500
    # x_list = [-3000, 4000, 10000, 17000, 23000, 32100, 39100]
    # y_list = [-5000, -4500, -5000, -5500, -5500, -5500, -5500]  #-5800
    # samples = ["HE_s1_S2VP_Bulk_Pristine_Trans", "HE_s2_S2VP_Bulk_LiTFSI_Trans", 
    #            "HE_s3_S2VP_Bulk_EIMTFSI_Trans","HE_s4_SnBA_Bulk_66",
    #            "HE_s5_SnBA_Bulk_16", "HE_s6_SnBA_Sphere_66",
    #            "HE_s7_SnBA_Sphere_16"]
    # x_list = [-43000, -43000, -37250, -31260, -24270, -18330]
    # y_list = [-2500, -3300, -2750, -2900, -2900, -2900]  #-5800
    # samples = ["KL7a", "KL7b", "KL8", "KL9", "KL10", "KL11"]  


    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t0 = time.time()
    waxs_angles = np.array([0])

    for waxs_angle in waxs_angles:  # loop through waxs angles
        yield from bps.mv(waxs, waxs_angle)
        if waxs_angle >= 15:
            dets = [pil900KW, pil2M] #, pil300KW]
        else:
            dets = [pil900KW] #, pil300KW]
        print("Meausre saxs and/or waxs here for w-angle=%s" % waxs_angle)

        for i in range(Nmax):
            t1 = time.time()
            # temp = ls.input_A_celsius.get() #ls.ch1_read.value
            for x, y, names in zip(x_list, y_list, samples):
                yield from bps.mv(piezo.x, x)
                yield from bps.mv(piezo.y, y)

                name_fmt = "{sample}_16.1keV_8.3m_waxs{waxs_angle:05.2f}_x{x:04.2f}_y{y:04.2f}_{t:05.2f}s"
                sample_name = name_fmt.format(
                    sample=names,
                    waxs_angle=waxs_angle,
                    x=x,
                    y=y,
                    t=t,
                    #scan_id=RE.md["scan_id"],
                )

                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)

                if grid == 0:
                    yield from bp.count(dets, num=1)
                else:
                    xss = np.linspace(x - 300, x + 300, 3)
                    yss = np.linspace(y - 300, y + 300, 3)
                    yss, xss = np.meshgrid(yss, xss)
                    yss = yss.ravel()
                    xss = xss.ravel()
                    yield from bp.list_scan(
                        dets, piezo.x, xss.tolist(), piezo.y, yss.tolist()
                    )

    sample_id(user_name="test", sample_name="test")




# RE(run_giswaxs(t=0.5))
def run_giswaxs(t=0.5, flag_align=1, flag_reflect=1, piezo_y_init=7200):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence SAXS+WAXS run — optionally aligns (height + reflected beam), then takes
    #   images at incident angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a grazing-incidence (GIWAXS) measurement for you.
    #   It aligns each sample, sweeps the incident angle (and WAXS arc), and records
    #   angle/position/beam INTO the data and file name:
    #     from smi_plans import giwaxs_run, giwaxs_bar, align_sample, SampleList
    #     yield from giwaxs_bar(SampleList.from_columns(name=samples, x=x_list, y=y_list),
    #                           incident_angles=ai_list, dets=[pil900KW, pil2M], t=t,
    #                           align=align_sample)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # x_list = [50000, 40000, 28000, 14000, -4000,    -24000]
    # sample_list = ['WS1', 'WS2', 'WS3', 'WS4','WS5',    'sam17']
    #yield from bps.mv(piezo.y, 1800)

    ### 2023-May-22, 
    # HEXAPOD x=-9, y=0, z=4; bsx 3.65-3.45; (was 2.65)
    #   smi_config_update = smi_config.append(current_config_DF, ignore_index=True)
    # 3.649785 3.649785 13.000338 0.000234 9.799842
    #x_list =  [59000] #, 47000, 39000, 28000, 15000, 3000, -15000]
    #sample_list = ["HE_sam1-1"] #,"HE_sam1-2","HE_sam1-3","HE_sam2-1","HE_sam2-2","HE_sam2-3", "KS_sam1"]
    #x_list = [-48000, -36000, -14000, 7000, 22000, 35000]
    #sample_list = ["HE_s1_Bulk_S2VP_Pristine","HE_s2_Bulk_S2VP_LiTFSI","HE_s3_Bulk_S2VP_EIMTFSI","HE_s4_Film_S2VP_Pristine","HE_s5_Film_S2VP_LiTFSI","HE_s6_Film_S2VP_EIMTFSI"] 
    x_list = [-14000+400]
    sample_list = ["HE_s3_Bulk_S2VP_EIMTFSI"] 
 
    ##### HE_sam1-1, x = 58999.955, aligned at y = 4687.467, theta = 0.126291

    assert len(x_list) == len(sample_list), f"Sample name/position list is borked"

    # angle_arc = np.array([0.1, 0.15, 0.19]) # incident angles
    angle_arc = np.array([0.12, 0.16, 0.2])  # incident angles
    # waxs_angle_array = np.linspace(0, 84, 15)

    waxs_angles = np.array(
        [20]
    )  # q=4*3.14/0.77*np.sin((max angle+3.5)/2*3.14159/180)
    
    data_dir = '/nsls2/data/smi/legacy/results/data/2024_1/312283_Subramanian/'

    # x_shift_array = np.linspace(-500, 500, 3) # measure at a few x positions
    aligned_positions = []
    for x, sample in zip(x_list, sample_list):  # loop over samples on bar

        yield from bps.mv(piezo.x, x)  # move to next sample
        if flag_align:
            yield from bps.mv(piezo.y, piezo_y_init) 
            yield from alignement_gisaxs(0.1, flag_reflect=flag_reflect)  # run alignment routine

        print('##### {}, x = {}, aligned at y = {}, theta = {}'.format(sample, piezo.x.position, piezo.y.position, piezo.th.position))
        aligned_positions.append([sample, piezo.x.position, piezo.y.position, piezo.th.position])
        with open(data_dir+'Align/aligned_positions.txt', 'a') as f:
            note = '{}: x{}, y{}, th{},'.format(sample, piezo.x.position, piezo.y.position, piezo.th.position)
            f.write(note)
            f.write('\n')

        th_meas = (
            angle_arc + piezo.th.position
        )  # np.array([0.10 + piezo.th.position, 0.20 + piezo.th.position])
        th_real = angle_arc

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        x_pos_array = x  # + x_shift_array

        for waxs_angle in waxs_angles:  # loop through waxs angles

            yield from bps.mv(waxs, waxs_angle)
            if waxs_angle >= 15:
                dets = [pil900KW, pil2M] #, pil300KW]
            else:
                dets = [pil900KW] #, pil300KW]

            for i, th in enumerate(th_meas):  # loop over incident angles
                yield from bps.mv(piezo.th, th)

                sample_name = "{sample}_{th:5.4f}deg_waxs{waxs_angle:05.2f}_ssd9200_x{x}_{t}s".format(
                    sample=sample,
                    th=th_real[i],
                    waxs_angle=waxs_angle,
                    x=x,
                    t=t,
                    #scan_id=RE.md["scan_id"],
                )
                # name_fmt = '{sample}_16.1keV_8.3m_waxs{waxs_angle:05.2f}_x{x:04.2f}_{t:05.2f}s_{scan_id}'
                # sample_name = name_fmt.format(sample=sample, waxs_angle=waxs_angle, x=x, t=t, scan_id=RE.md['scan_id'])
                sample_id(user_name="Static", sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                # yield from bp.scan(dets, energy, e, e, 1)
                # yield from bp.scan(dets, waxs, *waxs_arc)
                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


########################################
# 2021
def run_Thomas_temp(t=1, name="HarvPoly"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature study over a couple of samples — cycles WAXS arcs and repeats with sleeps,
    #   stamping temperature into the name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built in-situ time-series plan. It takes frames on a schedule and records
    #   the REAL elapsed time, temperature, position and beam intensity INTO each frame (so
    #   the time/temperature live in the data, not just the file name), and you don't manage
    #   the counter/clock by hand:
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run("HarvPoly", dets=[pil900KW, pil2M], t=t,
    #                       period=time_sleep_sec, num=Nmax, reads=[ls])
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    x_list = [13300, -12100]
    y_list = [-3400, -3400]
    samples = ["thermal1", "thermal2"]

    # Detectors, motors:
    dets = [pil2M]

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    t0 = time.time()
    for i in range(2000):
        t1 = time.time()
        temp = ls.ch1_read.value
        for x, y, names in zip(x_list, y_list, samples):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)

            name_fmt = "{sample}_11.15keV_7.5m_{time}s_{temperature}C_{i}"
            sample_name = name_fmt.format(
                sample=names,
                time="%1.1f" % (t1 - t0),
                temperature="%1.1f" % temp,
                i="%3.3d" % i,
            )

            xss = np.linspace(x - 500, x + 500, 3)
            yss = np.linspace(y - 300, y + 300, 3)
            yss, xss = np.meshgrid(yss, xss)
            yss = yss.ravel()
            xss = xss.ravel()

            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name=name, sample_name=sample_name)
            yield from bp.list_scan(dets, piezo.x, xss.tolist(), piezo.y, yss.tolist())

        time.sleep(1800)

    sample_id(user_name="test", sample_name="test")


def saxs_cryo(t=0.5, tem=25, num_max=100):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a cryo SAXS time series — it loops (nudging y each pass) taking SAXS+WAXS frames across a
    #   few WAXS arc angles, stamping the (cryo) temperature into the name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built in-situ time-series plan. It takes frames on a schedule and records
    #   the REAL elapsed time, temperature, position and beam intensity INTO each frame (so
    #   the time/temperature live in the data, not just the file name), and you don't manage
    #   the counter/clock by hand:
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run("bkg_sdd8.3m", dets=[pil900KW, pil2M], t=t,
    #                       period=time_sleep_sec, num=Nmax, reads=[ls])
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    global num
    # Slowest cycle:
    name = "ET"
    # Detectors, motors:
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    # sample = 'PDMS_sdd8.3m'
    sample = "bkg_sdd8.3m"

    waxs_range = np.linspace(0, 13, 3)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    while num < num_max:
        yield from bps.mvr(stage.y, 0.02)
        num += 1
        if waxs.arc.position > 7:
            waxs_ran = waxs_range[::-1]
        else:
            waxs_ran = waxs_range

        for wa in waxs_ran:
            yield from bps.mv(waxs, wa)
            name_fmt = "num{nu}_{temperature}C_wa{wa}"
            sample_name = name_fmt.format(nu=num, temperature="%4.2f" % tem, wa=wa)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name=sample, sample_name=sample_name)

            yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def gisaxs_Thomas(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence SAXS run over Thomas's samples — aligns each and takes images at a few
    #   incident angles across the WAXS arcs.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a grazing-incidence (GIWAXS) measurement for you.
    #   It aligns each sample, sweeps the incident angle (and WAXS arc), and records
    #   angle/position/beam INTO the data and file name:
    #     from smi_plans import giwaxs_run, giwaxs_bar, align_sample, SampleList
    #     yield from giwaxs_bar(SampleList.from_columns(name=samples, x=x_list, y=y_list),
    #                           incident_angles=ai_list, dets=[pil900KW, pil2M], t=t,
    #                           align=align_sample)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    samples = ["T1_A", "T1_B", "T2_A", "T2_B"]
    x_list = [58500, 49000, 39000, 28000]

    waxs_arc = np.linspace(0, 13, 3)
    angle = [0.12, 0.16, 0.2]

    # Detectors, motors:
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for x, sample in zip(x_list, samples):
        yield from bps.mv(piezo.x, x)

        sample_id(user_name="NT", sample_name=sample)

        yield from alignement_gisaxs(0.08)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_ai{angle}deg_wa{waxs}_pos{pos}"
        for j, wa in enumerate(waxs_arc[::-1]):
            yield from bps.mv(waxs, wa)

            for nu, num in enumerate([0, 1, 2, 3, 4]):
                yield from bps.mv(piezo.x, x - nu * 300)

                for an in angle:
                    yield from bps.mv(piezo.th, ai0 + an)
                    sample_name = name_fmt.format(
                        sample=sample, angle="%3.2f" % an, waxs="%2.1f" % wa, pos=nu
                    )
                    sample_id(user_name="PT", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")

                    yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)


def waxs_Thomas(t=1, x_off=0, user="NT"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a WAXS run over a bar of Thomas's samples — moves to each sample and takes a WAXS image
    #   (with an x offset option).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a whole bar of samples from a list and records
    #   position/beam INTO each image and into the file name:
    #     from smi_plans import transmission_bar, SampleList
    #     yield from transmission_bar(SampleList.from_columns(name=samples, x=x_list,
    #                                                          y=y_list), dets=[pil2M], t=t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' (if used in a detector list) was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    samples = [
        "sample01",
        "sample02",
        "sample03",
        "sample04",
        "sample05",
        "sample06",
        "sample07",
        "sample08",
        "sample09",
        "sample10",
        "sample11",
        "sample12",
        "sample13",
        "sample14",
        "sample15",
        "sample16",
        "sample17",
        "sample18",
        "sample19",
        "sample20",
        "sample21",
        "sample22",
        "sample23",
        "sample24",
        "sample25",
        "sample26",
        "sample27",
        "sample28",
        "sample29",
        "sample30",
        "sample31",
        "sample32",
        "sample33",
        "sample34",
        "sample35",
        "sample36",
        "sample37",
        "sample38",
        "sample39",
        "sample40",
        "sample41",
    ]
    x_list = [
        44700,
        41700,
        37700,
        32000,
        28000,
        21000,
        15000,
        10000,
        5800,
        2500,
        -1500,
        -4500,
        -6900,
        -11900,
        -16500,
        -19800,
        -23800,
        -27800,
        -33800,
        -37800,
        -41800,
        45000,
        41000,
        38000,
        33000,
        31000,
        27000,
        22500,
        20000,
        17500,
        15000,
        11000,
        8000,
        4500,
        1500,
        -1500,
        -4500,
        -9500,
        -13500,
        -17500,
        -21500,
    ]
    y_list = [
        -7800,
        -7800,
        -7800,
        -7800,
        -7800,
        -7700,
        -7700,
        -7600,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        -7400,
        3000,
        3000,
        3000,
        3000,
        3000,
        3000,
        3000,
        3200,
        3200,
        3200,
        3200,
        3200,
        3200,
        3200,
        3700,
        3400,
        3400,
        3400,
        3400,
        3500,
    ]
    z_list = [
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
    ]

    assert len(samples) == len(
        x_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        y_list
    ), f"Number of X coordinates ({len(y_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        z_list
    ), f"Number of X coordinates ({len(z_list)}) is different from number of samples ({len(samples)})"

    waxs_arc = np.linspace(0, 13, 3)

    # Detectors, motors:
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for j, wa in enumerate(waxs_arc[::-1]):
        yield from bps.mv(waxs, wa)

        for x, y, z, sample in zip(x_list, y_list, z_list, samples):
            yield from bps.mv(piezo.x, x + x_off)
            yield from bps.mv(piezo.y, y)
            yield from bps.mv(piezo.z, z)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            name_fmt = "{sample}_wa{waxs}_pos{pos}"

            for nu, num in enumerate([0, 1, 2, 3, 4]):
                yield from bps.mv(piezo.y, y + nu * 50)

                sample_name = name_fmt.format(sample=sample, waxs="%2.1f" % wa, pos=nu)
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)


def run_Thomas(t=1, x_off=0):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a run-book wrapper — it runs waxs_Thomas several times at different x offsets
    #   (pos2..pos4) to measure a few spots per sample.
    # 💡 NEWER, EASIER WAY: nothing to change here itself — once you migrate waxs_Thomas (see its
    #   note), this just chains it. In smi_plans you'd pass several x offsets to one bar/map plan
    #   instead of calling the plan several times by hand.
    # === end smi_plans note ================================================
    yield from waxs_Thomas(t=0.5, x_off=-500, user="NT_pos2_0.5s")
    yield from waxs_Thomas(t=0.5, x_off=-250, user="NT_pos3_0.5s")
    yield from waxs_Thomas(t=0.5, x_off=250, user="NT_pos4_0.5s")


def saxs_cryo_2021_1(t=0.5, tem=25, num_max=100):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 2021 cryo SAXS time series — loops taking SAXS+WAXS frames across WAXS arc angles,
    #   stamping the (cryo) temperature into the name.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   purpose-built in-situ time-series plan. It takes frames on a schedule and records
    #   the REAL elapsed time, temperature, position and beam intensity INTO each frame (so
    #   the time/temperature live in the data, not just the file name), and you don't manage
    #   the counter/clock by hand:
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run("cryo_sdd8.3m", dets=[pil900KW, pil2M], t=t,
    #                       period=time_sleep_sec, num=Nmax, reads=[ls])
    #
    #   (The Lakeshore 'ls' temperature device is FINE — no change needed.)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    global num
    # Slowest cycle:
    name = "ET"

    # Detectors, motors:
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample = "kapton"

    waxs_range = np.linspace(0, 13, 3)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # while num < num_max:
    # yield from bps.mvr(stage.y, 0.02)
    num += 1
    if waxs.arc.position > 7:
        waxs_ran = waxs_range[::-1]
    else:
        waxs_ran = waxs_range

    for wa in waxs_ran:
        yield from bps.mv(waxs, wa)
        name_fmt = "num{nu}_{temperature}C_wa{wa}"
        sample_name = name_fmt.format(nu=num, temperature="%4.2f" % tem, wa=wa)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=sample, sample_name=sample_name)

        yield from bp.count(dets, num=1)

    yield from bps.mvr(stage.y, 0.02)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def saxs_2021_1(t=0.5, tem=25, num_max=100):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 2021 SAXS run over a bar of samples — moves to each and takes a SAXS image.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a whole bar of samples from a list and records
    #   position/beam INTO each image and into the file name:
    #     from smi_plans import transmission_bar, SampleList
    #     yield from transmission_bar(SampleList.from_columns(name=samples, x=x_list,
    #                                                          y=y_list), dets=[pil2M], t=t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    global num
    # Slowest cycle:
    name = "ET"

    # Detectors, motors:
    dets = [pil2M]
    sample = "PS_PDMS_50.33dg_sdd8.3m_loop2"

    waxs_range = np.linspace(0, 13, 3)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(waxs, 13.0)

    t0 = time.time()

    while num < 500:
        t1 = time.time()

        name_fmt = "num{nu}_{temperature}C_{time}s"
        sample_name = name_fmt.format(
            nu=num, temperature="%4.2f" % tem, time=np.round(t1 - t0)
        )
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=sample, sample_name=sample_name)

        yield from bp.count(dets, num=1)
        yield from bps.sleep(30)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def waxs_2021_1(t=0.5, tem=25, num_max=1000):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 2021 WAXS run over a bar of samples — moves to each and takes a WAXS image.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a whole bar of samples from a list and records
    #   position/beam INTO each image and into the file name:
    #     from smi_plans import transmission_bar, SampleList
    #     yield from transmission_bar(SampleList.from_columns(name=samples, x=x_list,
    #                                                          y=y_list), dets=[pil2M], t=t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' (if used in a detector list) was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    global num
    # Slowest cycle:
    name = "ET"

    # Detectors, motors:
    dets = [pil2M, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    sample = "PS_PDMS_50.33dg_sdd8.3m_isotherm"

    waxs_range = np.linspace(0, 13, 3)
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    yield from bps.mv(waxs, 6.5)

    t0 = time.time()

    while num < num_max:
        t1 = time.time()

        name_fmt = "num{nu}_{temperature}C_{time}s"
        sample_name = name_fmt.format(
            nu=num, temperature="%4.2f" % tem, time=np.round(t1 - t0)
        )
        print(f"\n\t=== Sample: {sample_name} ===\n")
        sample_id(user_name=sample, sample_name=sample_name)

        yield from bp.count(dets, num=1)
        yield from bps.sleep(5)
        yield from bps.mvr(stage.y, 0.02)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def saxs_Thomas(t=1, x_off=0, user="NT"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a SAXS run over a bar of Thomas's samples — moves to each sample and takes a SAXS image
    #   (with an x offset option).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' runs a whole bar of samples from a list and records
    #   position/beam INTO each image and into the file name:
    #     from smi_plans import transmission_bar, SampleList
    #     yield from transmission_bar(SampleList.from_columns(name=samples, x=x_list,
    #                                                          y=y_list), dets=[pil2M], t=t)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil300KW' (if used in a detector list) was retired — it's now 'pil900KW'; the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the ⚠️ notes
    #   on those lines below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    samples = [
        "sample01",
        "sample02",
        "sample03",
        "sample04",
        "sample05",
        "sample06",
        "sample07",
        "sample08",
        "sample09",
        "sample10",
        "sample11",
        "sample12",
        "sample13",
        "sample14",
        "sample16",
        "sample17",
        "sample18",
        "sample19",
        "sample20",
        "sample21",
        "sample22",
        "sample23",
        "sample24",
        "sample25",
        "sample26",
        "sample27",
        "sample28",
        "sample29",
        "sample30",
        "sample31",
        "kapton_bkg",
    ]
    x_list = [
        46000,
        42000,
        38500,
        35000,
        31500,
        27500,
        23500,
        21000,
        16000,
        11000,
        5000,
        -500,
        -5000,
        -13000,
        45700,
        43700,
        41000,
        34000,
        29800,
        25800,
        22800,
        19800,
        17200,
        15200,
        12200,
        9000,
        2000,
        -4000,
        -7000,
        -10300,
        -13300,
    ]
    y_list = [
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        -7600,
        5000,
        4500,
        5000,
        5000,
        5000,
        5000,
        5000,
        5000,
        5300,
        5300,
        5300,
        5300,
        4300,
        5400,
        5400,
        3800,
        3800,
    ]
    z_list = [
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
        2700,
    ]

    assert len(samples) == len(
        x_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        y_list
    ), f"Number of X coordinates ({len(y_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        z_list
    ), f"Number of X coordinates ({len(z_list)}) is different from number of samples ({len(samples)})"

    xpos = [-500, 500, 5]

    # Detectors, motors:
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x + x_off)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        name_fmt = "{sample}_8.3m_16.1keV"

        sample_name = name_fmt.format(sample=sample)
        sample_id(user_name=user, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")

        yield from bp.rel_scan(dets, piezo.x, *xpos)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)


def rotscan_Thomas(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a sample-rotation scan — for each sample it rotates the stage (prs) through
    #   131 angles from -65 to +65 deg and at each angle does a small x/y grid scan, taking
    #   images (a CD-SAXS / texture style rocking measurement).
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a CD-SAXS rocking plan that rotates the stage and
    #   records the angle INTO the data and file name, and tomography/texture plans for pure
    #   rotation series:
    #     from smi_plans import cdsaxs_rock_run, tomography_run
    #     yield from cdsaxs_rock_run(sample, angles=np.linspace(-65, 65, 131), t=t, dets=[pil2M])
    #     #   (uses stage.phi — the renamed 'prs' — for you)
    #
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was removed — it's now 'stage.phi';
    #   (2) the 'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (see the ⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    samples = ["sample15_grid"]
    x_list = [-30600]
    y_list = [-9400]
    z_list = [1600]

    assert len(samples) == len(
        x_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        y_list
    ), f"Number of X coordinates ({len(y_list)}) is different from number of samples ({len(samples)})"
    assert len(samples) == len(
        z_list
    ), f"Number of X coordinates ({len(z_list)}) is different from number of samples ({len(samples)})"

    # Detectors, motors:
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)

        for i, prs_pos in enumerate(np.linspace(-65, 65, 131)):
            yield from bps.mv(prs, prs_pos)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
            yield from bps.sleep(2)

            name_fmt = "{sample}_8.3m_16.1keV_num{num}_{prs}deg"

            sample_name = name_fmt.format(
                sample=sample, num="%3.3d" % prs_pos, prs="%3.1f" % prs_pos
            )
            sample_id(user_name="NT", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            y_r = [-200, 200, 3]
            x_r = [-500, 500, 3]
            yield from bp.rel_grid_scan(dets, piezo.y, *y_r, piezo.x, *x_r, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)). (The smi_plans technique runs set exposure for you via t=.)

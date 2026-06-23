# Align GiSAXS sample
import numpy as np

def capillaries_saxs_PPG(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks a bar of capillary/film samples (moving x, y, z to each) and
    #   takes a single SAXS image per sample.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that walks a
    #   bar of samples for you and records the position/beam into each saved image and file
    #   name (so you can drop the hand-set sample names):
    #
    #     from smi_plans import transmission_bar, SampleList
    #     bar = SampleList.from_columns(                  # your bar as a little table
    #         name=["012_film", "181_film", "175_film", "210_film", "215_film"],
    #         x=[39300, 20250, 1150, -17900, -37000],
    #         y=[-7000]*5, z=[5400]*5)
    #     yield from transmission_bar(bar, [pil2M], t=t)  # one SAXS image per sample
    #
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # samples = ['4-1','4-2','4-3','4-4','4-5','4-6','4-7','4-8','4-9','4-10','4-11','4-12','4-13','4-14']

    # x_list = [42700, 36400, 30300, 23800, 17400, 11300, 4700, -1700, -8100, -14200, -21100, -27000, -33300, -39700]
    # y_list = [9000,   9000,  9000,  9000,  9000,  9000, 9000,  9000,  7000,   9000,   9000,   9000,   9000,  9000]
    # z_list = [1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400, 1400]

    samples = ["012_film", "181_film", "175_film", "210_film", "215_film"]

    x_list = [39300, 20250, 1150, -17900, -37000]
    y_list = [-7000, -7000, -7000, -7000, -7000]
    z_list = [5400, 5400, 5400, 5400, 5400]

    # Detectors, motors:
    dets = [pil2M]  # dets = [pil2M,pil300KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)

        sample_id(user_name="CW_8.3m_6.51keV_RT_0.6", sample_name=sample)
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)).


def slide_linkam_PPG(t=0.3):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ kinetics run on the Linkam stage — takes a SAXS image,
    #   nudges the sample up a little, waits ~28 s, and repeats 90 times (so you scan a
    #   strip while the Linkam ramps temperature).
    #
    # 💡 NEWER, EASIER WAY: "take an image, wait, repeat on a timer" is the 'smi_plans'
    #   time-series/kinetics pattern, which timestamps each frame into the data and file
    #   name for you:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("21-DJF-001H", [pil2M], t=t, num=90, period=28)
    #     # (move stage.y between frames as you do now, or pass a y-axis if you prefer.)
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (stage.y and ls/Linkam are fine.)
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    samples = "21-DJF-001H"  # ramps up from 25C
    # samples = ['LTC_ramp']
    # samples = ['LTC_15minwait']
    hexa_y = -0.25

    # Detectors, motors:
    dets = [pil2M]  # dets = [pil2M,pil300KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    # assert len(x_list) == len(samples), f'Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})'
    sample_id(user_name="CW_8.3m_6.51keV", sample_name=samples)
    yield from bps.mv(stage.y, hexa_y)

    for i in range(90):
        yield from bp.count(dets, num=1)
        yield from bps.mvr(stage.y, 0.01)
        yield from bps.sleep(28)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)).


def PPG_temp_2022_1(tim=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature series on a bar — sets the Lakeshore to each
    #   temperature, waits to reach setpoint and equilibrate, then walks a row of samples
    #   in x taking a SAXS image at each, before nudging y for the next temperature.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a temperature helper that goes to each setpoint,
    #   settles, and measures, recording the real temperature / position / beam into each
    #   image and file name (so you can drop the hand-built "{sample}_{temperature}C..." name):
    #     from smi_plans import goto_temperature, transmission_bar, SampleList
    #     bar = SampleList.from_columns(name=names, x=x_piezo)
    #     for T in [28, 40, 50, 60]:                 # your temperatures (degC)
    #         yield from goto_temperature(T, settle=...)   # ramp + wait for you
    #         yield from transmission_bar(bar, [pil2M], t=tim)   # one image per sample
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (ls/Lakeshore is fine.)
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    temperatures = [28, 40, 50, 60]

    names = ["s16", "s17", "s18", "s19", "s20", "s6a", "s7a", "e1", "e3", "e4", "e5", "e10", "e7", "e8", "e9",
    ]
    x_piezo = [ -44200, -37850, -31650, -25200, -18900, -12600, -6100, 300, 6650, 13000, 19350, 25700, 32050, 44750,
    ]
    # y_piezo =  [      7000,       7000,       7000,       7000,       7000,       7000,       7000,       7000]
    # assert len(x_piezo) == len(y_piezo), f'Number of X coordinates ({len(x_piezo)}) is different from number of Y coordinates ({len(y_list)})'
    assert len(x_piezo) == len(
        names
    ), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"

    # Detectors, motors:
    dets = [pil2M]  # ALL detectors

    name_fmt = "{sample}_{temperature}C_6.51keV_8.3m"

    det_exposure_time(tim, tim)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(tim, tim)  — or at the prompt:  RE(det_exposure_time(tim, tim)). (smi_plans' temperature_ramp_run sets it for you via t=.)
    for i_t, t in enumerate(temperatures):

        t_kelvin = t + 273.15
        print(t_kelvin)
        yield from ls.output1.mv_temp(t_kelvin)

        temp = ls.input_A.value
        while abs(temp - t_kelvin) > 1:
            print(abs(temp - t_kelvin))
            yield from bps.sleep(10)
            temp = ls.input_A.get()

        t_celsius = temp - 273.15
        if t_celsius > 30:
            yield from bps.sleep(300)
        for name, xs_piezo in zip(names, x_piezo):
            yield from bps.mv(piezo.x, xs_piezo)
            sample_name = name_fmt.format(sample=name, temperature="%3.1f" % t)

            sample_id(user_name="CW", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")

            yield from bp.count(dets, num=1)
        # move caps in Y by 100 um for every T value
        yield from bps.mvr(piezo.y, -(i_t + 1) * 100)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)).
    yield from ls.output1.mv_temp(28 + 273.13)


def capillaries_saxs_ppg_2022_1(t=0.2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: another capillary/film SAXS bar — moves to each sample's x/y/z and
    #   takes a single SAXS image. (The big block of commented-out lists above are just
    #   older sample holders kept for reference.)
    #
    # 💡 NEWER, EASIER WAY: same 'smi_plans' bar pattern as capillaries_saxs_PPG — describe
    #   the active holder as a SampleList and let transmission_bar walk it, recording the
    #   position/beam into each image and file name:
    #     from smi_plans import transmission_bar, SampleList
    #     bar = SampleList.from_columns(
    #         name=["e4film", "e9film", "e31film", "e32film", "e33film"],
    #         x=[-40000, -15000, 5000, 22000, 35000], y=[6700]*5, z=[2500]*5)
    #     yield from transmission_bar(bar, [pil2M], t=t)
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    # holder 5
    # samples = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'a13', 'a14', 'a3', 'a4',
    #'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11', 'a12']

    # x_list = [-45000, -38500, -31700, -25900, -19400, -13300, -6550,   300,  6150, 12500, 18800, 24900, 31450, 37700,
    #          -41500, -34900, -28700, -21900, -15600,  -9700, -3200,  3100,  9600, 16000, 22400, 28500, 35000, 41200]
    # y_list = [ -2000,  -2000,  -2000,  -2000,  -2000,  -2000, -2000, -2000, -2000, -2000, -2000, -2000, -2000, -2000,
    #           -2000,  -2000,  -2000,  -2000,  -2000,  -2000, -2000, -2000, -2000, -2000, -2000, -2000, -2000, -2000]
    # z_list = [ -2500,  -2500,  -2500,  -2500,  -3500,  -3500, -3500, -3500, -5000, -4500, -6500, -6500, -6500, -6500,
    #            8000,   8000,   7500,   7000,   6000,   6000,  6000,  6000,  6000,  5000,  5000,  4000,  4000,   400]

    # holder 6
    # samples = [ 'a1',  'a2', 'a15', 'a16', 'a17',  'e6', 'e11', 'e12', 'e13', 'e14', 'e15', 'e16', 'e17', 'e18', 'e19', 'e20', 'e21', 'e22', 'e23', 'e24', 'e25', 'e26']

    # x_list = [-43500, -39100, -34000, -28900, -24100, -19800, -14800, -11000, -6700, -1750, 2300, 5900, 9800, 14200, 17800, 22150, 26700, 30550, 33900, 38100, 41300, 44000]
    # y_list = [  2600,   2600,   2600,   3100,   3100,   3100,   3100,   3100,  3100,  3500, 3500, 3500, 3500,  3500,  3500,  3500,  3500,  3500,  3900,  3900,  3900,  3900]
    # z_list = [  1900,   1900,   1900,   1900,   1900,   1900,   1900,   1900,  1900,  1900, 1900, 1900, 1900,  1900,  1900,  1900,   700,   700,   200,   200,  1900,  1900]

    # holder 7
    # samples = ['e27', 'e28', 'e29', 'e30', 'e31', 'e32', 'e33', 'e34', 'e35', 'e36', 'e37', 'e38', 'e39', 'DJFA', 'DJFB', 'DJFC', 'DJFD']

    # x_list = [-42900, -39200, -33300, -29600, -23800, -19950, -14250, -9950, -4550,  -750, 3200, 7750, 11250, 16750, 25250, 31300, 39500]
    # y_list = [  6500,   6500,   6500,   6500,   6500,   6500,   5100,  6500,  6500,  6500, 6500, 6500,  6500,  6500,  6500,  6500,  6500]
    # z_list = [  2100,   2100,   2100,   2100,   2100,   2100,   2100,  2100,  2100,  2100, 2100, 2100,  2100,  2100,  2100,  2100,  2100]

    # holder 8
    # samples = ['DJFE', 'DJFF', 'DJFG', 'DJFH', 'a5a', 'e3film', 'e5film', 'e6film', 'e7film', 'e8film']

    # x_list = [-40600, -32600, -22000, -13500,  -8100,  100, 11100, 20100, 32100, 42100]
    # y_list = [  6200,   6200,   6200,   6200,   6200, 6200,  6200,  6200,  6200,  6200]
    # z_list = [  2500,   2500,   2500,   2500,   2500, 2500,  2500,  2500,  2500,  2500]

    # holder 9   !!! these need kapton subtraction !!!
    # samples = ['e12film', 'e13film', 'e30film', 'e28film', 'e29film']

    # x_list = [-40000, -15000, 5000, 30000, 40000]
    # y_list = [  6700,   6700, 6700,  6700,  6700]
    # z_list = [  2500,   2500, 2500,  2500,  2500]

    # holder 10
    # samples = ['e35a', 'e37a', 'e38a', 'e39a', 'e11a', 'e16a', 'e22a']

    # x_list = [-42600, -33150, -24550, -17250, -10350, -3900, 8300]
    # y_list = [  6700,   6700,   6700,   4900,   6700,  6700, 5500]
    # z_list = [  1500,   1500,   1500,   1500,   1500,  1500, 1500]

    # holder 11
    samples = ["e4film", "e9film", "e31film", "e32film", "e33film"]

    x_list = [-40000, -15000, 5000, 22000, 35000]
    y_list = [6700, 6700, 6700, 6700, 6700]
    z_list = [2500, 2500, 2500, 2500, 2500]

    # Detectors, motors:
    dets = [pil2M]  # dets = [pil2M,pil300KW]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(y_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    assert len(z_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for x, y, z, sample in zip(x_list, y_list, z_list, samples):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        yield from bps.mv(piezo.z, z)

        sample_id(user_name="CW_8.3m_6.51keV", sample_name=sample)
        yield from bp.count(dets, num=1)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.1, 0.1)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.1, 0.1)  — or at the prompt:  RE(det_exposure_time(0.1, 0.1)).


def capillaries_saxs_PPG_2022_3(t=0.3):
    """
    Capillaries SAXS 8.3 m 6.510 keV low div in vacuum
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a capillary SAXS bar where, at each sample, it also steps the sample
    #   up through a few y positions (to scan along the capillary), taking a SAXS image at
    #   each y. Parks the WAXS arc out of the way first.
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you describe the y-scan as an axis and let the
    #   bar helper sweep it per sample, recording the y / energy / WAXS-position / detector
    #   distance into each image and file name (so you can drop the hand-built name):
    #     from smi_plans import transmission_bar, SampleList, motor_axis
    #     bar = SampleList.from_columns(name=samples, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from transmission_bar(
    #         bar, [pil2M], t=t,
    #         per_sample=motor_axis("y", piezo.y, np.linspace(-4500, -5000, 2)))  # your y-steps
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    samples = [ 'DT', 'DU', 'DV', 'DW', 'H33']
    #samples = [ f'{s}-r2' for s in samples]
    piezo_x = [ 46200, 39500, 33400, 27200, 207500]
    #piezo_y = [-8000, -8000, -8000, -8000, -8000, -8000, -8000, -8000, -8000, -10000, -8000, -8000, -8000, -8000, -8000]
    #piezo_z = [ 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600, 6600]

    # y and z positions the same for all samples
    piezo_y = [-4500 for s in samples]
    piezo_z = [ 2100 for s in samples]

    lowest_piezo_y = -5000
    steps = 2

    assert len(samples) == len(piezo_x), f"Lenght of samples list is different than piezo_x)"
    assert len(piezo_x) == len(piezo_x), f"Lenght of piezo_x list is different than piezo_y)"
    assert len(piezo_y) == len(piezo_z), f"Lenght of piezo_y list is different than piezo_z)"

    # Move WAXS out of the way
    if waxs.arc.position < 19.5:
        yield from bps.mv(waxs, 20)
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    for name, x, y, z in zip(samples, piezo_x, piezo_y, piezo_z):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z)

        ys = np.linspace(y, lowest_piezo_y , steps).astype(int)

        for yss in ys:
            yield from bps.mv(piezo.y, yss)

            # Metadata
            e = energy.position.energy / 1000
            wa = waxs.arc.position + 0.001
            wa = str(np.round(float(wa), 1)).zfill(4)
            sdd = pil2M_pos.z.position / 1000

            # Sample name
            name_fmt = '{sample}_posy{pos}_{energy}keV_wa{wax}_sdd{sdd}m'
            sample_name = name_fmt.format(sample=name, pos=yss, energy='%.2f'%e, wax=wa,
                                        sdd='%.1f'%sdd)
            sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "})

            sample_id(user_name="CW", sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def films_PPG_2022_3(t=0.3):
    """
    SAXS 8.3 m 6.510 keV low div in vacuum
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a films bar with WAXS — for each WAXS-arc angle it walks all samples
    #   in x (nudging y per arc step) and takes an image, using SAXS only when the WAXS arc
    #   isn't blocking the SAXS detector.
    #
    # 💡 NEWER, EASIER WAY: sweeping the WAXS arc over a bar of samples is the 'smi_plans'
    #   GIWAXS-bar pattern; it records the WAXS-arc angle / position / energy / beam into each
    #   image and file name, and you give it the detectors per arc as you do now:
    #     from smi_plans import giwaxs_bar, SampleList, motor_axis
    #     bar = SampleList.from_columns(name=samples, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from giwaxs_bar(
    #         bar, t=t, dets=[pil2M, pil900KW],
    #         arc=motor_axis("waxs", waxs, [0, 20, 40, 60]))   # your waxs_arc list
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (pil900KW is the current WAXS
    #   detector — good.) (internal: Tier 1.)
    # === end smi_plans note ================================================

    samples = [ '7G', '24A', '24B', '24C', '7A', '7B', '7C', '7D', '7E', '7F']
    piezo_x = [ 44900, 38900, 26900, 15900, 4900, -5100, -16100, -26100, -34100, -41100]

    # y and z positions the same for all samples
    piezo_y = [-4500 for s in samples]
    piezo_z = [ 2100 for s in samples]

    assert len(samples) == len(piezo_x), f"Lenght of samples list is different than piezo_x)"
    assert len(piezo_x) == len(piezo_x), f"Lenght of piezo_x list is different than piezo_y)"
    assert len(piezo_y) == len(piezo_z), f"Lenght of piezo_y list is different than piezo_z)"

    waxs_arc = [0, 20, 40, 60]
    offset_y = 100  # in um

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)
        # Do not read SAXS if WAXS is in the way
        dets = [pil900KW] if waxs.arc.position < 10 else [pil2M, pil900KW]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

        for name, x, y, z in zip(samples, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y + i * offset_y,
                              piezo.z, z)

            # Metadata
            e = energy.position.energy / 1000
            wa = waxs.arc.position + 0.001
            wa = str(np.round(float(wa), 1)).zfill(4)
            sdd = pil2M_pos.z.position / 1000

            # Sample name
            name_fmt = '{sample}_{energy}keV_wa{wax}_sdd{sdd}m'
            sample_name = name_fmt.format(sample=name, energy='%.2f'%e, wax=wa,
                                        sdd='%.1f'%sdd)
            sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "})

            sample_id(user_name="CW", sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def in_situ_waxs_ppg(t=0.3):
    """
    In situ loop scan for evaporation films
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an in-situ time loop for an evaporating film — up to 999 times it
    #   takes a SAXS image, labels it with a step number and elapsed time, then waits 30 s.
    #
    # 💡 NEWER, EASIER WAY: this "image, label with time, wait, repeat" loop is exactly the
    #   'smi_plans' time-series/kinetics pattern, which records the elapsed time / energy /
    #   WAXS-position / detector distance into each image and file name for you:
    #     from smi_plans import time_series_run
    #     yield from time_series_run("sample01", [pil2M], t=t, num=999, period=30)
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # NOTE for staff: the elapsed-time line below uses 't1' which isn't defined in this
    #   function (only 't0' is), so this loop looks like it would error on the first pass —
    #   smi_plans' time_series_run computes elapsed time for you, which sidesteps that.
    # === end smi_plans note ================================================

    name = "sample01"
    wait_time = 30  # seconds

    t0 = time.time()
    
    # Move WAXS out of the way
    if waxs.arc.position < 19.5:
        yield from bps.mv(waxs, 20)
    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)
    
    for i in range(999):

        # Metadata
        step = str(i).zfill(3)
        td = str(np.round(t1 - t0, 1)).zfill(6)
        e = energy.position.energy / 1000
        wa = waxs.arc.position + 0.001
        wa = str(np.round(float(wa), 1)).zfill(4)
        sdd = pil2M_pos.z.position / 1000

        name_fmt = "{sample}_step{step}_time{td}s_{energy}eV_wa{wax}_sdd{sdd}m"
        sample_name = name_fmt.format(sample=name, step=step, td=td, energy='%.2f'%e, wax=wa,
                                      sdd='%.1f'%sdd)
        sample_name.translate({ord(c): "_" for c in "!@#$%^&*{}:/<>?\|`~+ "})

        sample_id(user_name="CW", sample_name=sample_name)
        print(f"\n\n\n\t=== Sample: {sample_name} ===")
        
        yield from bp.count(dets)
        print(f'Waiting for {wait_time} s...')
        yield from bps.sleep(wait_time)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


####################
### 2023-2 cycle ###

RE.md['SAF_number'] = 311180

def capillaries_PPG_2023_2(t=1):
    """
    SAXS 8.3 m 6.510 keV low div in vacuum
    Exposure increased as the intensity is lower
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a capillary SAXS/WAXS bar — for each WAXS-arc angle it walks all the
    #   samples in x and takes an image, using SAXS only when the WAXS arc isn't in the way.
    #   (The file name is built from a helper, get_scan_md().)
    #
    # 💡 NEWER, EASIER WAY: this is the 'smi_plans' GIWAXS-bar pattern; giwaxs_bar walks the
    #   bar and sweeps the WAXS arc, recording the WAXS-angle / position / energy / beam into
    #   each image and file name automatically (so get_scan_md() and the hand-set names are
    #   no longer needed):
    #     from smi_plans import giwaxs_bar, SampleList, motor_axis
    #     bar = SampleList.from_columns(name=samples, x=piezo_x, y=piezo_y, z=piezo_z)
    #     yield from giwaxs_bar(
    #         bar, t=t, dets=[pil2M, pil900KW],
    #         arc=motor_axis("waxs", waxs, [0, 20, 40, 60]))
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    samples = ['80b','81b','82b','83b','84b']
    piezo_x = [3450,-6050,-18250,-25350,-33350]

    # y and z positions the same for all samples
    piezo_y = [-3500 for s in samples]
    piezo_z = [5600 for s in samples]

    assert len(samples) == len(piezo_x), f"Lenght of samples list is different than piezo_x)"
    assert len(piezo_x) == len(piezo_x), f"Lenght of piezo_x list is different than piezo_y)"
    assert len(piezo_y) == len(piezo_z), f"Lenght of piezo_y list is different than piezo_z)"

    waxs_arc = [0, 20, 40, 60]
    offset_y = 0  # in um

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)
        # Do not read SAXS if WAXS is in the way
        dets = [pil900KW] if waxs.arc.position < 15 else [pil2M, pil900KW]
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

        for name, x, y, z in zip(samples, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y + i * offset_y,
                              piezo.z, z)

            # Sample name
            sample_name = f'{name}{get_scan_md()}'
            sample_id(user_name="CW", sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).


def saxs_only_PPG_2023_2(t=1):
    """
    SAXS 8.3 m 6.510 keV low div in vacuum
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a quick SAXS-only background measurement on a single vacuum sample at
    #   one WAXS-arc position.
    #
    # 💡 NEWER, EASIER WAY: for a one-off (or short bar of) SAXS measurement, 'smi_plans'
    #   records the position / energy / beam into the image and file name for you:
    #     from smi_plans import transmission_bar, SampleList
    #     bar = SampleList.from_columns(name=["bkg-vacuum"], x=[-35800], y=[-6000], z=[11200])
    #     yield from transmission_bar(bar, [pil2M], t=t)
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT
    #    for the ⚠️ lines which need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    samples = [  'bkg-vacuum' ]
    piezo_x = [ -35800]

    # y and z positions the same for all samples
    piezo_y = [ -6000 for s in samples]
    piezo_z = [ 11200 for s in samples]

    assert len(samples) == len(piezo_x), f"Lenght of samples list is different than piezo_x)"
    assert len(piezo_x) == len(piezo_x), f"Lenght of piezo_x list is different than piezo_y)"
    assert len(piezo_y) == len(piezo_z), f"Lenght of piezo_y list is different than piezo_z)"

    waxs_arc = [ 20 ]
    offset_y = 0  # in um

    dets = [ pil2M ]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' technique runs set it for you via t=.)

    for i, wa in enumerate(waxs_arc):
        yield from bps.mv(waxs, wa)
        for name, x, y, z in zip(samples, piezo_x, piezo_y, piezo_z):
            yield from bps.mv(piezo.x, x,
                              piezo.y, y + i * offset_y,
                              piezo.z, z)

            # Sample name
            sample_name = f'{name}{get_scan_md()}'
            sample_id(user_name="CW", sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)).
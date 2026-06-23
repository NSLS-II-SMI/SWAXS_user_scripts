# Bolmatov, 9-Nov-2018


def run_saxs_capsRPI(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a multi-sample WAXS-arc bar — for each sample it moves x and sweeps the
    #   WAXS arc, taking an image at each arc position.
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library called 'smi_plans' that runs a
    #   bar like this and writes the position/beam straight INTO each saved image (so you don't
    #   have to pack them into the file name by hand):
    #     from smi_plans import giwaxs_bar, SampleList   # do this once per session
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     yield from giwaxs_bar("LCF", samples, t=t, dets=[pil900KW])  # arc swept as an axis
    #   (Use pil900KW for the current WAXS detector — see ⚠️ below.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    x_list = [-18.9, -14.16, -8.8, -4.2, 0.08, 6.13, 11.6, 18.4]  #
    # Detectors, motors:
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = [2.94, 8.94, 2]  # [2.64, 8.64, 2]
    samples = [
        "LCF-FILM-1",
        "LCF-FILM-2",
        "LCF-FILM-3",
        "LCF-FILM-4",
        "LCF-FILM-5",
        "LCF-FILM-6",
        "LCF-FILM-7",
        "LCF-FILM-8",
    ]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(stage.x, x)
        sample_id(user_name=sample, sample_name="")
        yield from escan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxsRPI(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a transmission SAXS bar — for each sample it moves x and runs a short y
    #   scan, taking a SAXS image at each y point.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=samples, x=x_list)
    #     yield from transmission_bar("LC", samples, t=t, dets=[pil2M])
    #   (records the position/beam into each image and fills the file name for you.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (see ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    name = "LC"
    x_list = [-18.63, -12.2, -5.85, 0.7, 6.9, 12.95]  #
    # Detectors, motors:
    dets = [pil2M]
    y_range = [-3, -6, 11]
    samples = ["LC-O38-6", "LC-O37-6", "LC-O35-7", "LC-O36-6", "LC-O35-6", "LC-O35-8"]
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    for x, sample in zip(x_list, samples):
        yield from bps.mv(stage.x, x)
        sample_id(user_name=name, sample_name=sample)
        yield from escan(dets, stage.y, *y_range)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)


def run_saxs_caps_temp_Bolm(name="DB"):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a temperature + energy SAXS/WAXS bar — sets the Lakeshore heater to each
    #   temperature (waiting to equilibrate), then for each sample and each X-ray energy sweeps
    #   the WAXS arc + y and takes images, recording temperature/energy/beam.
    # 💡 NEWER, EASIER WAY: this combines three smi_plans concerns (temperature, energy, bar).
    #   There is a ready-made combined recipe, or you can compose axes by hand:
    #     from smi_plans.recipes_combined import giwaxs_tempramp_energy_5loc
    #     # or: from smi_plans import acquire, temperature_axis, energy_axis, motor_axis, SampleList
    #     #     acquire over [temperature_axis(...), energy_axis([13450, 13475, 13520]),
    #     #                   motor_axis("wa", waxs, [...])] per sample
    #   (records temperature/energy/arc/position/beam into each image, and manages the energy
    #    move + beam feedback for you. Use pil900KW for the current WAXS detector — see ⚠️.)
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) 'rayonix'
    #   (the MAXS detector) was removed with no replacement; (3) the 'det_exposure_time(...)'
    #   calls no longer set the exposure unless run as a plan (see ⚠️ notes below).
    #   (internal: Tier 2.)
    # === end smi_plans note ================================================
    # Slowest cycle:
    temperatures = [30, 40, 55]
    x_list = [
        -44280,
        -37950,
        -31595,
        -25200,
        -18800,
        -12550,
        -6100,
        225,
        6580,
        13000,
        19300,
        25700,
        32045,
        38390,
    ]
    e_list = [13450, 13475, 13520]
    # Detectors, motors:
    dets = [pil2M, rayonix, pil300KW, ls.ch1_read, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'rayonix' (the MAXS detector) was removed from the beamline with no current replacement (remove it or ask staff); and 'pil300KW' was removed too — the current WAXS detector is 'pil900KW' (a different camera, so check beam-center/calibration).
    y_range = [-2700, -6000, 30]
    waxs_arc = [3, 17, 2]
    samples = [
        "Br",
        "A0",
        "A1",
        "A2",
        "A3",
        "B0",
        "B1",
        "B2",
        "B3",
        "C0",
        "C1",
        "C2",
        "C3",
        "water",
    ]
    name_fmt = "{sample}_{energ}eV_{temperature}C"
    #    param   = '16.1keV'
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    det_exposure_time(10)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(10)  — or at the prompt:  RE(det_exposure_time(10)). (The smi_plans technique runs set exposure for you via t=.)
    for i_t, t in enumerate(temperatures):
        yield from bps.mv(ls.ch1_sp, t)
        if i_t > 0:
            yield from bps.sleep(2400)
        for x, s in zip(x_list, samples):
            temp = ls.ch1_read.value
            yield from bps.mv(piezo.x, x)
            for i_e, e in enumerate(e_list):
                yield from bps.mv(energy, e)
                sample_name = name_fmt.format(sample=s, temperature=temp, energ=e)
                print(f"\n\t=== Sample: {sample_name} ===\n")
                sample_id(user_name=name, sample_name=sample_name)
                yield from bp.grid_scan(dets, waxs, *waxs_arc, piezo.y, *y_range, 0)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bps.mv(ls.ch1_sp, 28)


def test_en(en):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a tiny helper that just moves the X-ray energy to a value you give it.
    # 💡 NEWER, EASIER WAY: 'smi_plans' has move_energy_fb, which moves the energy the safe way —
    #   it pauses the beam-position feedback, steps in small (<=50 eV) hops, waits to settle,
    #   turns feedback back on, and re-seeks if the beam dips:
    #     from smi_plans import move_energy_fb
    #     yield from move_energy_fb(en)
    #   (Nothing here is broken — this is just the recommended, more robust way to move energy.)
    # === end smi_plans note ================================================
    yield from bps.mv(energy, en)

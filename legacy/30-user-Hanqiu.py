def run_waxs_Hanqiu(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each sample, and each energy near the sulfur edge, it sweeps the
    #   WAXS detector arc through a few angles and takes an image at each (a small
    #   energy + WAXS-arc scan).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that can build
    #   the energies and the WAXS-arc sweep as "axes" and run them in one call, recording the
    #   energy / arc angle / beam intensity INTO each image and naming the file for you:
    #
    #     from smi_plans import acquire, energy_axis, motor_axis   # import once at session start
    #     yield from acquire("Cell48EE_2B", [pil900KW, xbpm3.sumY],   # WAXS is pil900KW now — see ⚠️
    #                        [energy_axis([2470, 2485, 2500]),         # your energies, unchanged
    #                         motor_axis("waxs", waxs.arc, np.linspace(3, 39, 7))],  # your arc sweep
    #                        )                                         # t set via the run's exposure
    #     # (loop this over your samples, moving piezo.x/piezo.y to each one)
    #
    #   (This is just a tidier option to try later — your script below works as-is EXCEPT for
    #    the ⚠️ lines, which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan
    #   (⚠️ notes below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    x_list = [8050, 8400, -11100, -12000, -23400]  #
    y_list = [30, 70, -300, -270, -350]
    # Detectors, motors:
    dets = [pil300KW, xbpm3.sumY]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    e_list = [2470, 2485, 2500]
    waxs_arc = [3, 39, 7]  # [2.64, 8.64, 2]
    samples = ["Cell48EE_2B", "Cell48EE_2B", "Cell48FF_B", "Cell48FF_B", "BrokenFilm_1"]
    name_fmt = "{sample}_{energ}eV_{ycoord}um"
    #
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"
    for x, s, y in zip(x_list, samples, y_list):
        yield from bps.mv(piezo.x, x)
        yield from bps.mv(piezo.y, y)
        for i_e, e in enumerate(e_list):
            yield from bps.mv(energy, e)
            sample_name = name_fmt.format(sample=s, energ=e, ycoord=y)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            sample_id(user_name="HJ", sample_name=sample_name)
            yield from bp.scan(dets, waxs, *waxs_arc)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.2)  — or at the prompt:  RE(det_exposure_time(0.2)). (The smi_plans technique runs set exposure for you via t=.)

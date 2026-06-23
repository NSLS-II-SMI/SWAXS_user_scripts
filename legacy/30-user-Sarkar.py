def run_Sarkar(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each WAXS-arc angle, walks to every sample on the bar and takes
    #   one SAXS+WAXS image (a transmission "bar" scan at 16.1 keV).
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   whole sample bar like this for you and records the WAXS-arc angle, beam intensity,
    #   detector distance, etc. straight into the data (and into the file name), so you don't
    #   hand-format "{sample}_wa{wax}_sdd8.3m_16.1keV". Same idea as below:
    #
    #     from smi_plans import SampleList, transmission_bar   # do this once per session
    #     bar = SampleList.from_columns(
    #         names=["kapton_bkg"],
    #         piezo_x=[-42200],
    #         piezo_y=[-2400],
    #     )
    #     yield from transmission_bar(bar, t=t, waxs_arc=(0, 6.5, 13, 19.5))
    #
    #   (Just a tidier option to try later — your script below still works as-is, EXCEPT for
    #    the two lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: this uses the retired 'pil300KW' WAXS detector (use
    #   'pil900KW'), and the 'det_exposure_time(...)' calls need running as plans — see the
    #   ⚠️ notes on those lines below.
    # === end smi_plans note ================================================
    # run with WAXS
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    waxs_arc = [0, 6.5, 13, 19.5]

    # x_list  = [43000, 37000, 33000, 28000, 22500,  6500, -2500, -8500, -14500, -22500, -29500, -34500, -40500, -44500]
    # y_list =  [-2000, -2000, -2000, -2000, -1600, -2000, -2400, -2000,  -2000,  -2000,  -2000,  -2000,  -2000,  -2000]
    # samples = ['HSL50', 'HSL2', 'HSL1', 'HSLUK', 'HSL2LAM_Ann', 'HSLS2HEX', 'HSL76', 'HSL109', 'AB_220023', 'OH1', 'OH5_9h', 'PO', 'Furan_PO',
    # 'HSL3LAM']

    x_list = [-42200]
    y_list = [-2400]
    samples = ["kapton_bkg"]

    assert len(x_list) == len(
        y_list
    ), f"Number of X coordinates ({len(x_list)}) is different from number of Y coordinates ({len(y_list)})"
    assert len(x_list) == len(
        samples
    ), f"Number of X coordinates ({len(x_list)}) is different from number of samples ({len(samples)})"

    for wa in waxs_arc[::-1]:
        yield from bps.mv(waxs, wa)

        for x, y, s in zip(x_list, y_list, samples):
            yield from bps.mv(piezo.x, x)
            yield from bps.mv(piezo.y, y)
            yield from bps.sleep(2)

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' transmission_bar sets it for you via t=.)
            name_fmt = "{sample}_wa{wax}_sdd8.3m_16.1keV"
            sample_name = name_fmt.format(sample=s, wax="%2.2d" % wa)
            sample_id(user_name="AS", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.count(dets, num=1)
            sample_id(user_name="test", sample_name="test")
            det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this "reset to 0.3 s" only takes effect if you run it as a plan:  yield from det_exposure_time(0.3, 0.3)  (or  RE(det_exposure_time(0.3, 0.3))).

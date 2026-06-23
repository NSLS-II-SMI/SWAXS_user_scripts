def saxs_waxs_Shejla(t=1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each rehydrated-peptide sample, and for each WAXS detector arc
    #   angle, it drives to the sample and rasters a small 3x3 grid of x/y spots, taking
    #   a SAXS + WAXS image at each spot. (A "raster" just means stepping across a little
    #   grid of positions so you sample several points on the sample.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that builds
    #   a position grid for you and records the position, energy, beam intensity, etc.
    #   straight into the saved data — so you don't have to bake "{sample}_16100eV_..._wa{}"
    #   into the file name by hand. A small x/y map at one spot looks like:
    #
    #     from smi_plans import map_grid_run            # do this once at the top of your session
    #     yield from map_grid_run(
    #         "DHH2_rehyd",                             # the rest of the file name is filled in for you
    #         x_center=-33000, y_center=0,              # your sample center, unchanged
    #         x_size=1000, y_size=600, x_num=3, y_num=3,  # a 3x3 grid, +/-500 in x and +/-300 in y
    #         dets=[pil2M, pil900KW],                   # SAXS + the current WAXS detector
    #         t=t,                                      # your exposure time, unchanged
    #     )
    #     # (call it once per sample; to also sweep the WAXS arc, loop the arc outside, or
    #     #  ask staff about the saxs_waxs_dets arc helper.)
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(t, t)' call no longer sets the exposure unless run as a plan
    #   (see the ⚠️ notes on those lines below). (internal: Tier 2.)
    # === end smi_plans note ================================================
    dets = [pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

    waxs_arc = np.linspace(0, 26, 5)

    yield from bps.mv(stage.y, 0)
    yield from bps.mv(stage.th, 0)
    # names = ['DHH1_2', 'DHH2_2', 'DHH3_2', 'HHH1_2', 'HHH2_2']
    # x = [-34500, -15000,  4000, 24000, 43500]
    # y = [ -2000,  -2500, -2500, -1500, -2000]
    # z = [  2700,   2700,  2700,  2700,  2700]

    names = ["DHH2_rehyd", "HHH2_rehyd"]
    x = [-33000, 25500]
    y = [0, -1000]
    z = [2700, 2700]

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        for name, xs, ys, zs in zip(names, x, y, z):
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)

            xss = np.linspace(xs - 500, xs + 500, 3)
            yss = np.linspace(ys - 300, ys + 300, 3)
            yss, xss = np.meshgrid(yss, xss)
            yss = yss.ravel()
            xss = xss.ravel()

            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            name_fmt = "{sample}_16100eV_sdd8.3_wa{wax}"
            sample_name = name_fmt.format(sample=name, wax=wa)
            sample_id(user_name="GF", sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            yield from bp.list_scan(dets, piezo.x, xss.tolist(), piezo.y, yss.tolist())

    # yield from bps.mv(stage.th, 1.5)
    # yield from bps.mv(stage.y, -10)
    # names = ['HHH3_2', 'Blank_water_2', 'Bkg_dry_2', 'DHH-Wet_2', 'HHH-Wet_2']
    # x = [45500, 26000,  6000, -13500, -32500]
    # y = [-9000, -9000, -9000,  -9000,  -9000]
    # z = [15800, 15800, 15800,  15800,  15800]

    # for wa in waxs_arc:
    #     yield from bps.mv(waxs, wa)

    #     for name, xs, ys, zs in zip(names, x, y, z):
    #         yield from bps.mv(piezo.x, xs)
    #         yield from bps.mv(piezo.y, ys)
    #         yield from bps.mv(piezo.z, zs)

    #         xss = np.linspace(xs - 500, xs + 500, 3)
    #         yss = np.linspace(ys - 300, ys + 300, 3)
    #         yss, xss = np.meshgrid(yss, xss)
    #         yss = yss.ravel()
    #         xss = xss.ravel()

    #         det_exposure_time(t,t)
    #         name_fmt = '{sample}_16100eV_sdd8.3_wa{wax}'
    #         sample_name = name_fmt.format(sample=name, wax = wa)
    #         sample_id(user_name='GF', sample_name=sample_name)
    #         print(f'\n\t=== Sample: {sample_name} ===\n')
    #         yield from bp.list_scan(dets, piezo.x, xss.tolist() , piezo.y, yss.tolist())


def AGB_scan():
    """
    this is a scan of the SAXS detector from 1.7m to 9 m at every 0.1 m, with attenuators in"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a silver-behenate (AgBeh) calibration sweep — moves the SAXS
    #   detector back from 1.7 m to 9 m in 0.1 m steps (attenuators in) and snaps an
    #   image at each distance, so you can pin down the beam center and q-scale.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a one-line calibration helper in the
    #   'smi_plans' library that does an AgBeh distance scan like this and records the
    #   detector distance, beam intensity, etc. straight into the data (so the numbers
    #   you need for calibration are saved with each image instead of only in the name):
    #
    #     from smi_plans import agbh_calibration_run     # do this once at the top of your session
    #     yield from agbh_calibration_run(
    #         "AGB_scan",                                # rest of the file name is added automatically
    #         dets=[pil2M],
    #         # sweep the SAXS detector distance from 1.7 m to 9 m in 0.1 m steps:
    #         # (pass your distances the same way you build them below)
    #     )
    #
    #   (This is just a tidier option to try later — your script below works as-is;
    #    nothing here is broken. (internal: Tier 1 — one image per point.))
    # === end smi_plans note ================================================
    yield from bps.mv(att1_7, "in")
    #yield from bps.mv(att1_7.open_cmd, 1)
    for zval in np.linspace(1.7, 9, 74): # every 0.1 m from 1.7m to 9m 
        zmm = zval * 1000
        yield from bps.mv(pil2M.motor.z, zmm)
        sample_name = f"AGB_scan_{get_scan_md()}"
        yield from bp.count([pil2M], num=1, md={"sample_name": sample_name})


def AGB_scan2():
    """
    this is a scan of the SAXS detector using AGB and attenuators to find the beam center and real q range"""
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: another silver-behenate (AgBeh) calibration — raster-scans the
    #   SAXS detector x/y (and steps the detector distance) to nail down the beam
    #   center and the true q range at both 9 m and 1.6 m.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a one-line AgBeh calibration helper that runs
    #   this kind of beam-center / q-range scan and writes the detector position into the
    #   saved data automatically:
    #
    #     from smi_plans import agbh_calibration_run     # do this once at the top of your session
    #     yield from agbh_calibration_run("AGB_scan", dets=[pil2M])
    #
    #   It coordinates the moves and the snaps for you, so you don't have to spell out
    #   each grid_scan by hand. (If you need the staff-style ladder of attenuators or a
    #   straight direct-beam scan, smi_plans also has  attenuator_ladder_run  and
    #   direct_beam_scan_run.)
    #
    #   (Just a suggestion to try later — your script below works as-is; nothing here is
    #    broken. (internal: Tier 2 — coordinated grid_scan per unit.))
    # === end smi_plans note ================================================
    yield from bps.mv(att1_7, "in")
    pil2M.motor.x.kind = 'normal'
    pil2M.motor.y.kind = 'normal'
    pil2M.motor.z.kind = 'normal'
    pil2M.motor.kind = 'normal'
    #yield from bps.mv(att1_7.open_cmd, 1)
    sample_name = f"AGB_scan_x_y_9m"
    yield from grid_scan([pil2M],pil2M.motor.x,0,60,3,pil2M.motor.y,-10,10,3,piezo.z,-10000,10000,11,snake_axes=True,md={"sample_name": sample_name})
    sample_name = f"AGB_scan_z"
    yield from grid_scan([pil2M],pil2M.motor.z,9300,1600,78,piezo.z,-10000,10000,11,md={"sample_name": sample_name})
    sample_name = f"AGB_scan_x_y_1.6m"
    yield from grid_scan([pil2M],pil2M.motor.x,0,60,3,pil2M.motor.y,-10,10,3,piezo.z,-10000,10000,11,snake_axes=True,md={"sample_name": sample_name})
    # for zval in np.linspace(1.6, 9.3, 78): # every 0.1 m from 1.7m to 9m 
    #     zmm = zval * 1000
    #     yield from bps.mv(pil2M.motor.z, zmm)
    #     sample_name = f"AGB_scan_{get_scan_md()}"
    #     yield from bp.count([pil2M], num=1, md={"sample_name": sample_name})


def usaxs_multi():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: visits a list of pre-recorded piezo x/y positions (8 "usaxs"
    #   spots) and takes one SAXS image at each, naming each by its label.
    #
    # 💡 NEWER, EASIER WAY: stepping a motor through a fixed list of positions and
    #   snapping at each is exactly what smi_plans' axis builders + acquire do, and they
    #   record the positions into the data so the labels don't have to live only in the
    #   file name. A close fit:
    #
    #     from smi_plans import acquire, motor_axis
    #     # build one axis that walks piezo.x through your 8 positions, then acquire:
    #     yield from acquire("usaxs", [pil2M], [motor_axis("x", piezo.x, x_piezo)])
    #     # (pair it with a piezo.y axis, or set y per point, the same way you do below)
    #
    #   (Just a tidier option to try later — your script below works as-is; nothing here
    #    is broken. (internal: Tier 1 — one image per point.))
    # === end smi_plans note ================================================
    names = ["usaxs_5_",  "usaxs_6_", "usaxs_7_", "usaxs_8_", "usaxs_9_", "usaxs_10_", "usaxs_11_", "usaxs_12_"]
    x_piezo = [-25100.0, -19100.0,  -13500.0,  -6900.0,  -700.0,     6100.0,     12300.0,   18700.0, ]
    y_piezo = [1825.9,   1825.9,    1725.9,    1825.9,    1825.9,     1825.9,     1925.9,     1725.9]
    for x,y,name in zip(x_piezo,y_piezo,names):
        yield from bps.mv(piezo.x,x,piezo.y,y)
        yield from bp.count([pil2M],md={'sample_name' : name +'10deg_9.3m_8keV'})

    
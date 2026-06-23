####line scan


def aaron_rot(t=8):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a coupled-rotation scan — it sweeps the rotation stage (prs) and, in lockstep,
    #   moves the hexapod x and the sample y together (an inner-product scan), taking a SAXS image
    #   at each step. The several lines just chain different prs ranges back-to-back.
    #
    # 💡 NEWER, EASIER WAY: a rotation scan that records the angle into the data is 'smi_plans'
    #   tomography_run / a motor_axis over the rotation stage; coupled axes are built with motor_axis
    #   per device. For example, one segment becomes:
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(
    #         "octahedron_plate_cut", dets=[pil2M], t=t,
    #         axes=[motor_axis("phi", stage.phi, np.linspace(45, 35, 11)),      # prs is now stage.phi — see ⚠️
    #               motor_axis("stage_x", stage.x, np.linspace(0.3834, 0.318, 11)),
    #               motor_axis("piezo_y", piezo.y, np.linspace(-580, -580, 11))],
    #     )
    #   (records the angle/positions for you. For a full rotation series, tomography_run wraps this.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'prs' no longer exists — it's now 'stage.phi' (every line
    #   below would error on 'prs'); (2) 'det_exposure_time(...)' no longer sets the exposure unless
    #   run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    sample_id(user_name="AM", sample_name="octahedron_plate_cut")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from bp.inner_product_scan(
        [pil2M], 11, prs, 45, 35, stage.x, 0.3834, 0.318, piezo.y, -580, -580  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, 34, 25, stage.x, 0.318, 0.254, piezo.y, -580, -580  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, 24, 15, stage.x, 0.254, 0.195, piezo.y, -580, -579  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, 14, 5, stage.x, 0.195, 0.138, piezo.y, -579, -580  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 5, prs, 4, 0, stage.x, 0.138, 0.118, piezo.y, -580, -577  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, 1, -10, stage.x, 0.118, 0.061, piezo.y, -577, -577  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, -11, -20, stage.x, 0.061, 0.031, piezo.y, -577, -577  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, -21, -30, stage.x, 0.031, 0.002, piezo.y, -577, -575  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, -31, -40, stage.x, 0.002, -0.013, piezo.y, -575, -575  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )
    yield from bp.inner_product_scan(
        [pil2M], 10, prs, -41, -50, stage.x, -0.013, -0.0175, piezo.y, -575, -575  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    )


def custo_scan(username, sample_na, meas_t):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS image and builds the file name by hand from the current
    #   x/y positions and the exposure time.
    # 💡 NEWER, EASIER WAY: 'smi_plans' records x/y INTO the data and fills them into the file name
    #   for you, so a single shot is one acquire:
    #     from smi_plans import one_sample_run
    #     yield from one_sample_run(sample_na, dets=[pil2M], t=meas_t, user_hints={"user": username})
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================
    det_exposure_time(meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(meas_t)  — or at the prompt:  RE(det_exposure_time(meas_t)). (The smi_plans technique runs set exposure for you via t=.)
    name_fmt = "{sample}_x_{x_pos}_y_{y_pos}_{expo}s"
    sample_name = name_fmt.format(
        sample=sample_na,
        x_pos=float("%.3f" % piezo.x.position),
        y_pos=float("%.3f" % piezo.y.position),
        expo=meas_t,
    )
    sample_id(user_name=username, sample_name=sample_name)
    yield from bp.count([pil2M], num=1)

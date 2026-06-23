####line scan


def aaron_rot(t=5):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a CD-SAXS-style "rock" of a tetrahedral sample — it sweeps the rotation
    #   stage while creeping the x position in lock-step, taking a SAXS image at each angle (split
    #   into four angle ranges with different point counts). 'inner_product_scan' is just Bluesky's
    #   way of moving two motors together along a straight line (a *plan*, i.e. a recipe it runs).
    #
    # 💡 NEWER, EASIER WAY: rocking a CD-SAXS sample through phi is a one-call job in 'smi_plans'
    #   with cdsaxs_rock_run, which records the angle + beam + detector-distance into each image:
    #
    #     from smi_plans import cdsaxs_rock_run
    #     yield from cdsaxs_rock_run("tetra2_1741", prs_range=(60, -60, 121), t=t)   # angle start,stop,#pts
    #       # if you also need x to track the angle, compose motor axes yourself:
    #       # from smi_plans import acquire, motor_axis
    #       # yield from acquire("tetra2_1741", [pil2M],
    #       #     [motor_axis("phi", stage.phi, np.linspace(60, 46, 15)),     # was 'prs'
    #       #      motor_axis("x", piezo.x, np.linspace(5550, 5580, 15))])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) the rotation stage 'prs' was removed — it's now 'stage.phi'
    #   (the lines below would crash with "name 'prs' is not defined"); (2) 'det_exposure_time(...)'
    #   no longer sets the exposure unless run as a plan. See the ⚠️ notes on those lines.
    #   (internal: Tier 1.)
    # === end smi_plans note ================================================
    sample_id(user_name="AM", sample_name="tetra2_1741")
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    # yield from bp.inner_product_scan([pil2M], 121, prs, 60, -60, piezo.x, -2667.5, -2605.5)
    # yield from bp.inner_product_scan([pil2M], 121, prs, 60, -60, piezo.x, -2680, -2610)
    yield from bp.inner_product_scan([pil2M], 15, prs, 60, 46, piezo.x, 5550, 5580)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bp.inner_product_scan([pil2M], 45, prs, 45, 0, piezo.x, 5580, 5640)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bp.inner_product_scan([pil2M], 45, prs, 1, -45, piezo.x, 5640, 5641)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    yield from bp.inner_product_scan([pil2M], 15, prs, -46, -60, piezo.x, 5640, 5641)  # ⚠️ FIXME(smi_plans): 'prs' no longer exists (it would error). The same rotation stage is now called 'stage.phi' — replace 'prs' with 'stage.phi'.
    # yield from bp.inner_product_scan([pil2M], 10, prs, 34, 25, stage.x, 0.318, 0.254, piezo.y, -580, -580)
    # yield from bp.inner_product_scan([pil2M], 10, prs, 24, 15, stage.x, 0.254, 0.195, piezo.y, -580, -579)
    # yield from bp.inner_product_scan([pil2M], 10, prs, 14, 5, stage.x, 0.195, 0.138, piezo.y, -579, -580)
    # yield from bp.inner_product_scan([pil2M], 5, prs, 4, 0, stage.x, 0.138, 0.118, piezo.y, -580, -577)
    # yield from bp.inner_product_scan([pil2M], 10, prs, 1, -10, stage.x, 0.118, 0.061, piezo.y, -577, -577)
    # yield from bp.inner_product_scan([pil2M], 10, prs, -11, -20, stage.x, 0.061, 0.031, piezo.y, -577, -577)
    # yield from bp.inner_product_scan([pil2M], 10, prs, -21, -30, stage.x, 0.031, 0.002, piezo.y, -577, -575)
    # yield from bp.inner_product_scan([pil2M], 10, prs, -31, -40, stage.x, 0.002, -0.013, piezo.y, -575, -575)
    # yield from bp.inner_product_scan([pil2M], 10, prs, -41, -50, stage.x, -0.013, -0.0175, piezo.y, -575, -575)
    sample_id(user_name="test", sample_name="test")


def test_scan(start=11800, t=10, step=10):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a small commissioning helper — steps the undulator gap (new_ivu_gap) down
    #   by `step` ten times, pausing 2 s each time. It just moves a device; it doesn't record any
    #   data (no detector is read), so there's nothing to "migrate" for data collection here.
    #
    # 💡 NEWER, EASIER WAY: if you ever want to also RECORD something while stepping a device like
    #   this, 'smi_plans' lets you turn any motor into a swept "axis" and capture readings at each
    #   step in one call — e.g. motor_axis("ivu_gap", new_ivu_gap, [...]) handed to acquire(...).
    #   As a pure move-and-wait test, the loop below is fine as-is.
    # === end smi_plans note ================================================
    for i in range(t):
        new_ivu_gap.set(start - i * step)
        yield from bps.sleep(2)


def waxs_aaron_2021_3(t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for two samples, at two WAXS detector-arc angles, moves the stage/piezo to
    #   each sample, nudges x by a couple of offsets, and takes a SAXS+WAXS image at each spot.
    #   A classic "visit each sample on the bar and snap a picture" multi-sample scan.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a "bar" helper for exactly this — you list your samples
    #   (name + x/y/z) once and it visits each and acquires, writing position/beam INTO each image
    #   so you don't hand-format the "{sample}_..._pos{pos}_wa{waxs}" name:
    #
    #     from smi_plans import giwaxs_bar, SampleList
    #     samples = SampleList.from_columns(name=["Ito_back","Pt-Azo_back"],
    #                                       x=[19499,16260], y=[-840,-840], z=[2300,2300])
    #     yield from giwaxs_bar(samples, t=t, waxs_arc=[20, 0])   # sweeps the WAXS arc per sample
    #
    #   (Just a tidier option — your loop below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    user = "AM"

    names = ["Ito_back", "Pt-Azo_back"]

    x_piezo = [19499, 16260]
    y_piezo = [-840, -840]
    z_piezo = [2300, 2300]
    x_hexa = [0, 0]

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

    waxs_arc = [20, 0]
    offset = [0, 100]

    dets = [pil900KW, pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)

        for name, xs, zs, ys, xs_hexa in zip(names, x_piezo, z_piezo, y_piezo, x_hexa):
            yield from bps.mv(stage.x, xs_hexa)
            yield from bps.mv(piezo.x, xs)
            yield from bps.mv(piezo.y, ys)
            yield from bps.mv(piezo.z, zs)

            for off in offset:
                yield from bps.mv(piezo.x, xs + off)
                name_fmt = "{sample}_16.1keV_pos{pos}_wa{waxs}"
                sample_name = name_fmt.format(
                    sample=name, pos="%1.1d" % off, waxs="%2.1f" % wa
                )
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\t=== Sample: {sample_name} ===\n")

                yield from bp.count(dets, num=1)

import sys
import time


det = [pil2M, pdcurrent, pdcurrent1, pdcurrent2]


def bu(user_name, start_y, end_y, acq_t=2, meas_t=2):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks the sample up in y in 50 um steps; at each spot it briefly
    #   opens the shutter through attenuators to read the pin-diode current (a beam-
    #   intensity check), then takes one SAXS image, naming it with that diode reading.
    #
    # 💡 NEWER, EASIER WAY: a step-along-one-line scan like this is a "map line" in the
    #   'smi_plans' library, and it records the position and beam reading into each image
    #   for you (so the diode value lands in the data, not just the file name):
    #
    #     from smi_plans import map_line_run
    #     yield from map_line_run(
    #         user_name,                          # rest of the file name is added automatically
    #         piezo.y, start_y, end_y, step=50,   # your y line, unchanged
    #         t=acq_t,                            # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M],
    #         reads=[pdcurrent2],                 # record the pin-diode current with each frame
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(acq_t, meas_t)' line below no
    #   longer sets the exposure unless run as a plan (see the ⚠️ note on it).
    #   (internal: Tier 1 — one image per point.)
    # === end smi_plans note ================================================
    for i, y_val in enumerate(range(start_y, end_y + 1, 50)):
        yield from bps.mv(piezo.y, y_val)
        name_fmt = "nb{i}_pd_{pd}"
        det_exposure_time(acq_t, meas_t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(acq_t, meas_t)  — or at the prompt:  RE(det_exposure_time(acq_t, meas_t)). (The smi_plans technique runs set exposure for you via t=.)

        yield from bps.mv(att1_9.open_cmd, 1)
        yield from bps.mv(att1_10.open_cmd, 1)

        fs.open()
        yield from bps.sleep(0.3)
        pd_curr = pdcurrent2.value
        fs.close()

        yield from bps.mv(att1_9.close_cmd, 1)
        yield from bps.mv(att1_10.close_cmd, 1)

        yield from bps.sleep(1)

        sample_name = name_fmt.format(i="%2.2d" % (1 + i), pd="%5.5d" % pd_curr)
        sample_id(user_name=user_name, sample_name=sample_name)

        print(f"\n\t=== Sample:{user_name}_{sample_name} ===\n")

        yield from bp.count(det, num=1)


def run_bu_2022_2(name="test", t=1):
    """
    SAXS grid scan on sample with 9 different positions

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a 3x3 SAXS grid scan over a small patch of the sample (9 spots),
    #   building the file name from the current energy, detector distance, and scan id.
    #
    # 💡 NEWER, EASIER WAY: a grid of spots like this is a "map grid" in the 'smi_plans'
    #   library; it records the energy, detector distance, position, etc. into each image
    #   for you (so you don't have to read 'energy.position' / 'pil2M_pos.z' by hand and
    #   cram them into the name — smi_plans fills tokens like {energy_energy} from the data):
    #
    #     from smi_plans import map_grid_run
    #     yield from map_grid_run(
    #         name,                               # rest of the file name is added automatically
    #         piezo.x, 0, 600, 3,                 # your x range, unchanged
    #         piezo.y, 0, 300, 3,                 # your y range, unchanged
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M],
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer
    #   set the exposure unless run as a plan (see the ⚠️ notes on them).
    #   (internal: Tier 2 — coordinated grid_scan per unit.)
    # === end smi_plans note ================================================
    user = "GVD"

    # Nanopositioners relative ranges in um
    x_range = [0, 600, 3]
    y_range = [0, 300, 3]

    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # Metadata
    e = energy.position.energy / 1000
    sdd = pil2M_pos.z.position / 1000
    scan_id = db[-1].start["scan_id"] + 1

    # Sample filename
    name_fmt = "{sample}_{energy}keV_sdd{sdd}m_id{scan_id}"
    sample_name = name_fmt.format(
        sample=name, energy="%.2f" % e, sdd="%.1f" % sdd, scan_id=scan_id
    )
    sample_id(user_name=user, sample_name=sample_name)

    # Take measurement
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.rel_grid_scan(dets, piezo.x, *x_range, piezo.y, *y_range, 0)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def run_background_bu_2022_2(name="test", t=1):
    """
    SAXS background around the sample

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS background image (no sample in the beam),
    #   naming it from the current energy, detector distance, and scan id.
    #
    # 💡 NEWER, EASIER WAY: a single capture like this is one call in the 'smi_plans'
    #   library, and it records the energy/detector-distance into the image for you (so
    #   you don't have to read 'energy.position' / 'pil2M_pos.z' by hand and pack them
    #   into the name):
    #
    #     from smi_plans import transmission_run
    #     yield from transmission_run(
    #         name + "-bkg",                      # rest of the file name is added automatically
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil2M],
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the lines marked ⚠️ which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer
    #   set the exposure unless run as a plan (see the ⚠️ notes on them).
    #   (internal: Tier 1 — single count.)
    # === end smi_plans note ================================================
    user = "GVD"
    name = name + "-bkg"

    dets = [pil2M]
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    # Metadata
    e = energy.position.energy / 1000
    sdd = pil2M_pos.z.position / 1000
    scan_id = db[-1].start["scan_id"] + 1

    # Sample filename
    name_fmt = "{sample}_{energy}keV_sdd{sdd}m_id{scan_id}"
    sample_name = name_fmt.format(
        sample=name, energy="%.2f" % e, sdd="%.1f" % sdd, scan_id=scan_id
    )
    sample_id(user_name=user, sample_name=sample_name)

    # Take measurement
    print(f"\n\t=== Sample: {sample_name} ===\n")
    yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

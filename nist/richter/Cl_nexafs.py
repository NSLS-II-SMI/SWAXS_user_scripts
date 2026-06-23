
def NEXAFS_Cl_edge(t=2):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the X-ray energy across the chlorine edge (2800->2900 eV,
    #   101 points), then back down again, taking a SAXS image + beam readings at each step.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy scan like this in ONE line. It also records the energy, beam intensity,
    #   etc. straight into the saved data and fills them into the file name for you, so you
    #   don't have to hand-build that long "{energy_energy}eV_pd..." name. Same scan as below:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     yield from nexafs_run(
    #         "CL_calibration",                     # the rest of the file name is added automatically
    #         np.linspace(2800, 2900, 101),         # your energies, unchanged
    #         t=t,                                  # your exposure time, unchanged
    #         dets=[pil2M, pin_diode, xbpm2, xbpm3],
    #         geometry="transmission",
    #         updown=True,                          # do the up sweep AND the down sweep in one go
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note on it).
    # === end smi_plans note ================================================

    dets = [pil2M, pin_diode, xbpm2, xbpm3]
    name = "CL_calibration_{energy_energy}eV_pd{pin_diode_current2_mean_value}_bpm2{xbpm2_sumX}_bpm3{xbpm3_sumX}_"
    energies = np.linspace(2800, 2900, 101)
 
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    yield from bps.mv(pin_diode.averaging_time, t)


    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name':name})
    def inner():
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis already pause after each energy move, manage the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed.)
                
            yield from bps.trigger_and_read(dets + [energy])
        for e in energies[::-1]:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)  # 💡 smi_plans: same as above — this settle wait is handled for you by move_energy_fb/energy_axis once you switch over.
            
            yield from bps.trigger_and_read(dets + [energy])
    return (yield from inner())


def NEXAFS_Cl_edge_61pts(t=2):

    dets = [pil2M, pin_diode, xbpm2, xbpm3]
    name = "LiquidCell_phosphate_buffer_50mM_{energy_energy}eV_pd{pin_diode_current2_mean_value}_bpm2{xbpm2_sumX}_bpm3{xbpm3_sumX}_"
    energies = np.linspace(2820, 2880, 61)
 
    det_exposure_time(t, t)
    yield from bps.mv(pin_diode.averaging_time, t)


    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name':name})
    def inner():
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
                
            yield from bps.trigger_and_read(dets + [energy])
        for e in energies[::-1]:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
            
            yield from bps.trigger_and_read(dets + [energy])
    return (yield from inner())











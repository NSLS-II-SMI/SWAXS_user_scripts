import numpy as np
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from ophyd import Signal



def NEXAFS_P_edge(t=60):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the X-ray energy across the phosphorus edge (2140->2200 eV,
    #   31 points), takes a WAXS + SAXS image plus beam readings at each step, then walks
    #   the energy back down in steps at the end. (This file is a nicely-built example.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that does a
    #   full energy scan like this in ONE line. It also records the energy, beam intensity,
    #   etc. straight into the saved data and fills them into the file name for you, so you
    #   don't have to build the name by hand with a throwaway 'target_file_name' Signal.
    #   Same scan as below:
    #
    #     from smi_plans import nexafs_run          # do this once at the top of your session
    #     yield from nexafs_run(
    #         "lipid_green",                        # the rest of the file name is added automatically
    #         np.linspace(2140, 2200, 31),         # your energies, unchanged
    #         t=t,                                  # your exposure time, unchanged
    #         dets=[pil900KW, pil2M, pin_diode, xbpm2, xbpm3],
    #         geometry="transmission",
    #         updown=True,                          # do the up sweep AND the walk-back in one go
    #     )
    #
    #   (This is just a tidier option to try later — your script below already works well,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below (see the ⚠️ note on
    #   it). (internal: Tier 4 — already a clean one-run-per-sample, templated-name script.)
    # === end smi_plans note ================================================

    dets = [pil900KW, pil2M, pin_diode, xbpm2, xbpm3]
    name = "lipid_green_pd{pin_diode_current2_mean}_"
    energies = np.linspace(2140, 2200, 31)

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly, but after a software update it's now a "plan" (a recipe Bluesky runs), so this plain call silently does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (smi_plans' nexafs_run sets it for you via t=.)
    yield from bps.mv(pin_diode.averaging_time, t)

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
    def inner():
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this wait once you migrate — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed.)
                

            name_fmt = "{sample}_{energy}eV_pd{{pin_diode_current2_mean_value}}"
            
            e=energy.energy.position
            sample_name = name_fmt.format(sample=name,energy="%6.2f"%e )
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            yield from bps.trigger_and_read(dets + [s,energy])
        yield from bps.mv(energy, 2190)
        yield from bps.sleep(2)  # 💡 smi_plans: this whole stepped energy walk-back can go once you migrate — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed.)
        yield from bps.mv(energy, 2180)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2170)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2160)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2150)
        yield from bps.sleep(2)
        yield from bps.mv(energy, 2140)
        yield from bps.sleep(2)

    return (yield from inner())







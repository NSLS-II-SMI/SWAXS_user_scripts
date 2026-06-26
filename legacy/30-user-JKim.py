def run_simple_energy(t=1):
    """
    Take simple e scan
    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: steps the X-ray energy across the copper edge (with a denser set of
    #   points right around the edge) and takes a WAXS (and SAXS, when the arc is low)
    #   image at each energy.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a one-line energy-scan helper in the
    #   'smi_plans' library. It records the energy, beam intensity, etc. straight into the
    #   data and into the file name for you (so you don't have to hand-assemble the name),
    #   and — importantly — it manages the energy move and beam feedback itself, so you can
    #   drop the sleeps and beam-recovery tricks below:
    #
    #     from smi_plans import nexafs_run
    #     import numpy as np
    #     energies = np.concatenate((np.arange(8900, 8975, 5), np.arange(8975, 8990, 2),
    #                                np.arange(8990, 9010, 1), np.arange(9010, 9101, 5)))
    #     yield from nexafs_run(
    #         "CuNPfullcell-noVapp-escan",        # rest of the file name is added automatically
    #         energies,                           # your energies, unchanged
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil900KW, pil2M],
    #         geometry="transmission",
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now. The 💡 lines
    #    are bits you can simply delete once you migrate.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the two 'det_exposure_time(...)' calls below no longer set
    #   the exposure unless run as a plan (see their ⚠️ notes). (internal: Tier 1.)
    # === end smi_plans note ================================================

    name = 'CuNPfullcell-noVapp-escan'

    waxs_arc = [ 40 ]

    #energies = np.arange(8950, 9000 + 1, 1)
    energies = np.arange(8900, 9100 + 1, 5)

    energies =  np.concatenate((
        np.arange(8900, 8975, 5),
        np.arange(8975, 8990, 2),
        np.arange(8990, 9010, 1),
        np.arange(9010, 9101, 5),
        ))

    user = "KR"
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)


    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        for i, nrg in enumerate(energies):
            yield from bps.mv(energy, nrg)
            yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
            if xbpm2.sumX.get() < 20:  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis do this for you: a plain bps.mv(energy, E) -- the energy device itself manages the DCM feedback, the undulator gap and the harmonic, so no manual feedback handling, energy hops, or beam re-seek is needed (pass flux_signal=/flux_threshold= if you want a beam-loss guard). (Not broken, just no longer needed once you migrate.)
                yield from bps.sleep(2)
                yield from bps.mv(energy, nrg)
                yield from bps.sleep(2)

            sample_name = f'{name}{get_more_md()}'
            sample_id(user_name=user, sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)


def name_sample(name, tstamp):
    """
    Create sample name with metadata

    Args:
        name (str): sample name
        tstamp (time): referenced start time created separately as
            tstamp = time.time()
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: builds the current file name by hand — it tacks the elapsed time
    #   (and some metadata) onto the base name and sets it as the active sample name.
    #
    # 💡 NEWER, EASIER WAY: with the 'smi_plans' library you usually don't build the name
    #   by hand at all. You pass a base name to a technique run (like time_series_run /
    #   nexafs_run), and smi_plans fills in the recorded numbers for you — e.g. it
    #   substitutes tokens like {energy_energy} and the timing straight from the saved
    #   data. (Nothing here is broken; this just becomes unnecessary once you migrate.)
    # === end smi_plans note ================================================

    eplased = time.time() - tstamp
    sample_name = f'{name}{get_more_md()}_t{eplased:.1f}'
    sample_id(user_name='KR', sample_name=sample_name)
    print(sample_name)

def create_timestamp():
    """
    store in RE.md and print
    """
    RE.md['tstamp'] = time.time()
    print('\nTime stamp created in RE.md')
    tstamp = RE.md['tstamp']
    print(f'tstamp: {tstamp}')

def continous_run(sname='test', t=2, wait=8, frames=2160):
    """
    Take data continously
    
    Create timestamp in BlueSky before running this function as
    create_timestamp()

    Args:
        sname (str): basic sample name,
        t (float): camera exposure time is seconds,
        wait (float): delay between frames,
        frames(int): number of frames to take
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes data continuously — it snaps a SAXS+WAXS image, waits a few
    #   seconds, and repeats for a couple thousand frames, stamping each with the elapsed
    #   time since you called create_timestamp().
    #
    # 💡 NEWER, EASIER WAY: "keep taking frames over time" is the 'smi_plans' time-series
    #   helper in one line. It records the timing/beam-intensity into each image for you,
    #   so you don't need a separate timestamp in RE.md or a hand-built name:
    #
    #     from smi_plans import time_series_run
    #     yield from time_series_run(
    #         sname,                              # rest of the file name is added automatically
    #         num=frames,                         # number of frames, unchanged
    #         period=wait,                        # delay between frames, unchanged
    #         t=t,                                # exposure time, unchanged (sets the camera for you)
    #         dets=[pil900KW, pil2M],
    #     )
    #
    #   (Just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' line below no longer sets
    #   the exposure unless run as a plan (see the ⚠️ note on it). (internal: Tier 1.)
    # === end smi_plans note ================================================
    try:
        tstamp = RE.md['tstamp']
    except:
        tstamp = time.time()
        RE.md['tstamp'] = tstamp
    
    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

    for i in range(frames):

        print(f'Taking {i + 1} / {frames} frames')

        # update sample name
        name_sample(sname, tstamp)

        # take one fram
        yield from bp.count([pil900KW, pil2M])

        # wait
        print(f'\nWaiting {wait} s')
        yield from bps.sleep(wait)
    
def clear_md():
    """
    Remove time stamp, sample zero, and alignment after changing the cell
    """

    keys = [ 'tstamp', 'alignment_LUT', 'sample_pos0']
    
    for k in keys:
        try:
            RE.md.pop(k)
        except:
            print(f'No {k} key')
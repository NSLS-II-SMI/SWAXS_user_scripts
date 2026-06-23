import bluesky.preprocessors as bpp
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from ophyd import Signal

def single_scan_test(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):
    '''
    Study the beam damage on 1 film to define the opti;am experimental conitions.

    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an energy-scan beam-damage test on one film — sweeps the X-ray energy (and optionally
    #   incident angle / WAXS arc), taking a frame at each energy to find safe conditions.
    #
    # 💡 NEWER, EASIER WAY: sweeping the X-ray energy across an edge and recording the energy
    #   + beam into the data is the beamline 'smi_plans' helper library's energy/NEXAFS run.
    #   (Nice touch in this script: it already saves the file name as a 'target_file_name'
    #   Signal into the data instead of cramming it into a string — that's the smi_plans way.)
    #
    #     from smi_plans import nexafs_run
    #     yield from nexafs_run(name, energies, t=t, dets=[pil2M, xbpm2, xbpm3])
    #
    #   Bonus: smi_plans' energy move already waits for the energy to settle, manages the beam
    #   feedback, and re-seeks if the beam dips — so the sleep + beam re-seek here become
    #   unnecessary (see the 💡 notes).
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls below no longer set the
    #   exposure unless run as a plan (see the ⚠️ FIXME notes on those lines).
    # === end smi_plans note ================================================
    if ai_list is None:
        ai_list = []

    # 63 energies
    energies = (np.arange(2445, 2470, 5).tolist()+ np.arange(2470, 2480, 0.25).tolist()+ np.arange(2480, 2490, 1).tolist()
                + np.arange(2490, 2500, 5).tolist()+ np.arange(2500, 2560, 10).tolist())
   
    energies = [16100, 16100, 16100]

    ai0 = piezo.th.position
    xs = piezo.x.position
    dets = [pil900KW, pil2M]
    dets = [pil2M]

    s = Signal(name='target_file_name', value='', kind=3)

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
    def inner():
        for i, wa in enumerate(waxs_arc):
            # yield from bps.mv(waxs, wa)

            counter = 0
            for k, ais in enumerate(ai_list):
                if ais==0.6:
                    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
                else:
                    det_exposure_time(1, 1)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 1)  — or at the prompt:  RE(det_exposure_time(1, 1)). (The smi_plans technique runs set exposure for you via t=.)

                # yield from bps.mv(piezo.th, ai0 + ais)

                name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}_bpm{xbpm}"
                
                for e in energies:
                    yield from bps.mv(energy, e)
                    yield from bps.sleep(2)  # 💡 smi_plans: you can drop this — move_energy_fb/energy_axis already wait for the energy to settle, handle the beam feedback, and re-seek if the beam dips. (Not broken, just no longer needed once you migrate.)
                    if xbpm2.sumX.get() < 50:  # 💡 smi_plans: you can drop this whole beam re-seek — move_energy_fb/energy_axis already re-seek the beam if it dips after an energy move (and wait for it to settle). (Not broken, just no longer needed once you migrate.)
                        yield from bps.sleep(2)
                        yield from bps.mv(energy, e)
                        yield from bps.sleep(2)
                    
                    # yield from bps.mv(piezo.x, xs + counter * xstep)
                    counter += 1
                    bpm = yield from bps.rd(xbpm2.sumX)
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa, xbpm="%4.3f"%bpm)
                    # sample_id(user_name="CM", sample_name=sample_name)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
                
                # yield from bps.mv(energy, 2500)
                # yield from bps.sleep(2)
                # yield from bps.mv(energy, 2480)
                # yield from bps.sleep(2)
                # yield from bps.mv(energy, 2445)

            # yield from bps.mv(piezo.th, ai0)
    return (yield from inner())
	


import bluesky.preprocessors as bpp
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from ophyd import Signal

def single_scan_giwaxs(t=1, name="Test", ai_list: list[int]|None = None, xstep=10, waxs_arc = (0, 20)):
    '''
    Study the beam damage on 1 film to define the opti;am experimental conitions.

    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a GIWAXS run over a bar of samples — for each sample it aligns, then takes frames at
    #   several incident angles and WAXS arc positions.
    #
    # 💡 NEWER, EASIER WAY: aligning each sample then sweeping incident angle / WAXS arc is
    #   the beamline 'smi_plans' helper library's GIWAXS run. align_sample aligns and saves
    #   the result; incidence_axis sweeps the angle while recording it into the data:
    #
    #     from smi_plans import giwaxs_bar, SampleList, incidence_axis, align_sample
    #     samples = SampleList.from_columns(name=names, x=x_piezo, y=y_piezo)
    #     yield from giwaxs_bar(samples, incidence_axis(piezo.th, ai0, ai_list),
    #                           t=t, align=align_sample)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t, t)' call below no longer sets the
    #   exposure unless run as a plan (see the ⚠️ FIXME note on that line).
    # === end smi_plans note ================================================
    names = ['sj-ppionzrox-m-post', 'sj-ppionzrox-m-ox', 'sj-ppionzrox-m-pre', 'sj-ppion-m-ox', 
                 'sj-bkg-m-coated',     'sj-bkg-m-bare']
    x_piezo = [              53800,               53900,                48700,           37900,
                             26900,               16400]
    x_hexa = [                  14,                 4.3,                    0,               0,
                                0,                    0]
    y_piezo = [               7300,                7300,                 7300,            7300,
                              7300,                7200]

    assert len(x_piezo) == len(names), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(names)})"
    assert len(x_piezo) == len(y_piezo), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(y_piezo)})"
    assert len(x_piezo) == len(x_hexa), f"Number of X coordinates ({len(x_piezo)}) is different from number of samples ({len(x_hexa)})"

    waxs_arc = [7, 20]
    ai0_all = -1
    ai_list = [0.10, 0.12, 0.15, 0.20]
    xstep = 0


    for name, xs, ys, xs_hexa in zip(names, x_piezo, y_piezo, x_hexa):
        yield from bps.mv(stage.x, xs_hexa,
                          piezo.x, xs,
                          piezo.y, ys)

        yield from bps.mv(piezo.th, ai0_all)
        yield from alignement_gisaxs_doblestack(0.15)

        ai0 = piezo.th.position
        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

        s = Signal(name='target_file_name', value='')

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md={'sample_name' :'{target_file_name}'})
        def inner():
            for i, wa in enumerate(waxs_arc):
                yield from bps.mv(waxs, wa)

                counter = 0
                for k, ais in enumerate(ai_list):
                    yield from bps.mv(piezo.th, ai0 + ais)

                    name_fmt = "{sample}_{energy}eV_ai{ai}_wa{wax}"
                    
                    yield from bps.mv(piezo.x, xs - counter * xstep)
                    counter += 1
                    e=energy.energy.position
                    sample_name = name_fmt.format(sample=name,energy="%6.2f"%e, ai="%3.2f"%ais, wax=wa)
                    print(f"\n\t=== Sample: {sample_name} ===\n")
                    s.put(sample_name)
                    yield from bps.trigger_and_read(dets + [energy, waxs, xbpm2, xbpm3, piezo.th, piezo.x] + [s])
            yield from bps.mv(piezo.th, ai0)

        return (yield from inner())
    

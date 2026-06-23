
from bluesky.run_engine import WaitForTimeoutError, FailedStatus





def blade_coating_2025_1(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87, align_th=0.12,th=0.12, dets = [pil2M, pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a blade-coating experiment — it aligns, sets the exposure, dispenses a drop
    #   of solution from the syringe pump (infuse for 2.5 s), moves the blade/stage to the measure
    #   position, and takes a SAXS+WAXS image of the freshly coated film.
    #
    # 💡 NEWER, EASIER WAY: blade-coating with a pump trigger is a built-in recipe in 'smi_plans':
    #   blade_coating_run drives the coat-start/measure positions, fires the syringe, and takes a
    #   time series of frames while the film dries — recording elapsed time/frame into each image:
    #
    #     from smi_plans import blade_coating_run
    #     yield from blade_coating_run(sample_name,
    #         coat_start=coating_start_pos, measure_pos=measurement_pos,
    #         infuse_seconds=2.5, t=1, dets=[pil2M, pil900KW])
    #     # (syringe_infuse / syringe_withdraw are also available if you want manual pump control.)
    #
    #   (Just a tidier option — your script below still works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(2)
    
    # yield from bps.mv(thorlabs_su, thorlabs_su.position)
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(1, 200)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(1, 200)  — or at the prompt:  RE(det_exposure_time(1, 200)). (The smi_plans technique runs set exposure for you via t=.)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='ML', sample_name=sample_name)
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    
    yield from bps.mv(thorlabs_su, measurement_pos)
    dets.append(xbpm3.sumX, xbpm2.sumX)
    yield from bp.count(dets)

    # yield from shclose()





def blade_coating_2025_1_slowexp_withoutmotion(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87,align_th=0.12, th=0.12, dets = [pil2M, pil900KW]):   
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: blade-coat then watch it dry IN PLACE — aligns, dispenses solution (15 s
    #   infuse), moves to the measure spot, and takes a slow time series (120 frames, one every
    #   2.5 s) without moving the stage during measurement.
    #
    # 💡 NEWER, EASIER WAY: this "coat, then take a timed series of frames" is blade_coating_run /
    #   time_series_run in 'smi_plans', which records the elapsed time + frame number into each
    #   image (so you can see drying kinetics) in one call:
    #     from smi_plans import blade_coating_run
    #     yield from blade_coating_run(sample_name, coat_start=coating_start_pos,
    #         measure_pos=measurement_pos, infuse_seconds=15, n_frames=120, period=2.5,
    #         t=0.5, dets=[pil2M, pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='SG', sample_name=sample_name)

    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(15)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    yield from bps.mv(thorlabs_su, measurement_pos)

    yield from bp.count(dets, num=120, delay=2.5)

def hydration_scan(sample_name='bladecoating', coating_start_pos=0, measurement_pos=60, th=0.12, dets = [pil2M, pil900KW]):   
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: watches a film hydrate over time — dispenses solution (15 s infuse), moves to
    #   the measure spot, and takes a slow time series (120 frames, one every 2.5 s).
    #
    # 💡 NEWER, EASIER WAY: a timed series like this is time_series_run (or blade_coating_run) in
    #   'smi_plans', which records elapsed-time/frame into each image:
    #     from smi_plans import time_series_run
    #     yield from time_series_run(sample_name, n_frames=120, period=2.5, t=0.5,
    #                                dets=[pil2M, pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    
    # yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th)

    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='SG', sample_name=sample_name)

    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(15)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    yield from bps.mv(thorlabs_su, measurement_pos)

    yield from bp.count(dets, num=120, delay=2.5)


def blade_coating_2025_1_slowexp_withmotion(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87,align_th=0.12, th=0.12, dets = [pil2M, pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: blade-coat then scan the blade/stage across the film WHILE measuring — aligns,
    #   dispenses solution, then scans thorlabs_su from the measure position over 15 mm in 600 steps,
    #   pausing at each (via the custom one_1d_step_withwait step) to take SAXS+WAXS.
    #
    # 💡 NEWER, EASIER WAY: blade_coating_run handles the coat + translate-while-measuring pattern
    #   and records position/time into the data; pass it your translator motor:
    #     from smi_plans import blade_coating_run
    #     yield from blade_coating_run(sample_name, coat_start=coating_start_pos,
    #         measure_pos=measurement_pos, n_frames=600, t=0.5, translator=thorlabs_su,
    #         dets=[pil2M, pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)
    sample_id(user_name='JC', sample_name=sample_name)
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5)
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump
    
    yield from bps.mv(thorlabs_su, measurement_pos)
    yield from bp.scan([pil2M, pil900KW], thorlabs_su, measurement_pos, measurement_pos-15, num=600, per_step=one_1d_step_withwait)



def alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: the alignment step for blade coating — nudges the blade/stage to the measure
    #   position (retrying a few times in case the move times out), runs the grazing-incidence
    #   alignment, then parks at the coating-start position. (The repeated try/except moves are
    #   just retries for a flaky motor.)
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' you pass align=align_sample to your run (e.g. the
    #   blade_coating_run shown above) and it aligns and SAVES the alignment result with the data,
    #   so you don't keep a separate alignment helper in sync. (Nothing here is broken.)
    # === end smi_plans note ================================================
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    try:
        yield from bps.mv(thorlabs_su, measurement_pos,timeout=10)
    except:
        pass
    yield from alignement_gisaxs_hex(angle=align_th)

    yield from bps.mv(thorlabs_su, coating_start_pos)


def blade_coating_2025_1_slowexp_withmotion_Kelvin(sample_name='bladecoating', coating_start_pos=10, measurement_pos=80,align_th=0.12, th=0.16):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a full blade-coat run at a chosen incident angle — records the WAXS arc + angle
    #   in the file name, aligns, sets the incident angle, dispenses solution at the wafer edge, then
    #   scans the blade/stage across the film (800 steps) taking SAXS+WAXS at each, and restores the
    #   angle at the end.
    #
    # 💡 NEWER, EASIER WAY: blade_coating_run covers coat + translate-while-measuring and records
    #   angle/position/beam into the data (so you don't hand-build the "_wa..deg_ai..deg" name):
    #     from smi_plans import blade_coating_run
    #     yield from blade_coating_run(sample_name, coat_start=0, measure_pos=measurement_pos,
    #         n_frames=800, t=0.5, translator=thorlabs_su, geometry="reflection",
    #         dets=[pil2M, pil900KW])
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    #Add info in the sample name
    waxs_pos = waxs.arc.position
    sample_name = sample_name + '_wa%2.1fdeg_ai%.2fdeg_16.1keV'%(waxs_pos, th)

    #Move to measurement position first for alignment
    yield from bps.mv(thorlabs_su, measurement_pos)

    #Align sample
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)
    
    #ai=0 after alignment
    ai0 = stage.th.position

    # Move to wanted incident angle
    yield from bps.mv(stage.th, ai0+th)

    # Set exposure time and sample name
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name='ML', sample_name=sample_name)
    # det_exposure_time(0.5,300)
    #det_exposure_time(2, 600)

    # Move to the edge of the wafer for coating
    yield from bps.mv(thorlabs_su, 0)

    # Do the syringe pump things
    yield from bps.mv(syringe_pu.dir, 0) # set pump to infuse (push rather than withdraw)
    yield from bps.mv(syringe_pu.go, 1) # start pump 
    yield from bps.sleep(2.5) #pump for 2.5s for 2p5 percent solution, gives 200 uL
    #yield from bps.sleep(1) #pump for 1s for 10percent solution, gives 80 uL
    yield from bps.mv(syringe_pu.stop_flow, 1) # stop pump

    # Move back to measurement position
    yield from bps.mv(thorlabs_su, measurement_pos)

    # Measure
    yield from bp.scan([pil2M, pil900KW], thorlabs_su, measurement_pos, measurement_pos-10, num=800, per_step=one_1d_step_withwait) #600 scans are sufficient in general
    
    yield from bps.mv(stage.th, ai0)

#RE(bp.scan([pil2M, pil900KW], thorlabs_su, 60, 60-10, num=600))

def exsitu_2025_01(sample_name='bladecoating', th=0.12, dets = [pil2M, pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a simple ex-situ measurement — nudges the incident angle by th, takes one
    #   SAXS+WAXS image, then returns the angle.
    # 💡 NEWER, EASIER WAY: a single GIWAXS shot at one incidence offset is one acquire in smi_plans:
    #     from smi_plans import acquire, incidence_axis
    #     yield from acquire(sample_name, [pil2M, pil900KW],
    #                        [incidence_axis(stage.th, stage.th.position, [th])], t=0.5)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.5,0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5,0.5)  — or at the prompt:  RE(det_exposure_time(0.5,0.5)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name='AR', sample_name=sample_name)
    
    yield from bps.mvr(stage.th, th)
    yield from bp.count([pil2M, pil900KW])
    yield from bps.mvr(stage.th, -th)


def one_1d_step_withwait(detectors, motor, step, take_reading=None):
    """
    Inner loop of a 1D step scan

    This is the default function for ``per_step`` param in 1D plans.

    Parameters
    ----------
    detectors : iterable
        devices to read
    motor : Settable
        The motor to move
    step : Any
        Where to move the motor to
    take_reading : plan, optional
        function to do the actual acquisition ::

           def take_reading(dets, name='primary'):
                yield from ...

        Callable[List[OphydObj], Optional[str]] -> Generator[Msg], optional

        Defaults to `trigger_and_read`
    """
    # smi_plans: no acquisition logic of its own here — this is a low-level "per_step" helper that
    #   adds a 1.5 s settle before each reading inside a scan. The smi_plans technique runs (e.g.
    #   blade_coating_run) handle settle/trigger timing internally, so you usually won't need this.
    take_reading = bps.trigger_and_read if take_reading is None else take_reading

    def move():
        grp = bps._short_uid("set")
        yield bps.Msg("checkpoint")
        yield bps.Msg("set", motor, step, group=grp)
        yield bps.Msg("wait", None, group=grp)

    yield from move()
    yield from bps.sleep(1.5)
    return (yield from take_reading(list(detectors) + [motor]))



def su_y_center_align():
    """
    hexapod height scan, finding the center of a hole between y=0 and y=5 and moving there

    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an alignment helper — scans the hexapod height (stage.y) on the direct beam,
    #   finds the center of a hole, and moves there. (bec/ps are live-fit helpers that find the peak
    #   center from the scan.)
    #
    # 💡 NEWER, EASIER WAY: in 'smi_plans' centering scans like this are part of the alignment /
    #   commissioning helpers (e.g. align_sample, direct_beam_scan_run), which record the result
    #   with the data instead of relying on the legacy smi.modeAlignment()/modeMeasurement() dance.
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line). (internal: Tier 2.)
    # === end smi_plans note ================================================
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.3, 0.3)  — or at the prompt:  RE(det_exposure_time(0.3, 0.3)). (The smi_plans technique runs set exposure for you via t=.)

    yield from smi.modeAlignment(technique="gisaxs")

    # Set direct beam ROI
    yield from smi.setDirectBeamROI()

    # Scan height on the DB only
    yield from bp.scan([pil2M], stage.y, 0, 4, 25)
    ps(der=False, plot=True)
    yield from bps.mv(stage.y, ps.cen)

    # Close all the matplotlib windows
    #plt.close("all")

    # Return angle
    yield from smi.modeMeasurement()

    # Deactivate the automated derivative calculation
    bec._calc_derivative_and_stats = False

def exsitu_2025_01(sample_name='bladecoating', dets = [pil2M, pil900KW]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a simple ex-situ measurement (this copy redefines the one above) — sets the
    #   exposure and takes one SAXS+WAXS image of the current sample.
    # 💡 NEWER, EASIER WAY: a single shot is one acquire in smi_plans:
    #     from smi_plans import acquire
    #     yield from acquire(sample_name, [pil2M, pil900KW], [], t=0.5)
    # ⚠️ NEEDS A FIX TO RUN NOW: 'det_exposure_time(...)' no longer sets the exposure unless run as
    #   a plan (see the ⚠️ note on that line). (internal: Tier 1.)
    # === end smi_plans note ================================================
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name='JC', sample_name=sample_name)
    
    #dets.append(xbpm3.sumX, xbpm2.sumX)
    yield from bp.count([pil2M, pil900KW])
    #

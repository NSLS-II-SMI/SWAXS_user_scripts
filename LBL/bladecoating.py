
from bluesky.run_engine import WaitForTimeoutError, FailedStatus





def blade_coating_2025_1(sample_name='bladecoating', coating_start_pos=10, measurement_pos=87, align_th=0.12,th=0.12, dets = [pil2M, pil900KW]):
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(1)
    #yield from shopen()
    #yield from bps.sleep(2)
    
    # yield from bps.mv(thorlabs_su, thorlabs_su.position)
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(1, 200)
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
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)
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
    
    # yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th)

    det_exposure_time(0.5, 0.5)
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
    
    yield from alignment_blade_coating_2025_1(coating_start_pos, measurement_pos,th, align_th)

    det_exposure_time(0.5, 0.5)
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
    det_exposure_time(0.5, 0.5)
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
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.5,0.5)
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
    # Activate the automated derivative calculation
    bec._calc_derivative_and_stats = True

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)

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
    
    #yield from alignement_gisaxs_hex(0.1)
    det_exposure_time(0.5, 0.5)
    sample_id(user_name='JC', sample_name=sample_name)
    
    #dets.append(xbpm3.sumX, xbpm2.sumX)
    yield from bp.count([pil2M, pil900KW])
    #

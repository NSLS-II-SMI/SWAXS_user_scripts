
def NEXAFS_Cl_edge(t=2):

    dets = [pil2M, pin_diode, xbpm2, xbpm3]
    name = "CL_calibration_{energy_energy}eV_pd{pin_diode_current2_mean_value}_bpm2{xbpm2_sumX}_bpm3{xbpm3_sumX}_"
    energies = np.linspace(2800, 2900, 101)
 
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











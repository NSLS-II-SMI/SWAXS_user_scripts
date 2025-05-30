import numpy as np
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from ophyd import Signal



def NEXAFS_P_edge(t=60):

    dets = [pil900KW, pil2M, pin_diode, xbpm2, xbpm3]
    name = "lipid_green_pd{pin_diode_current2_mean}_"
    energies = np.linspace(2140, 2200, 31)

    det_exposure_time(t, t)
    yield from bps.mv(pin_diode.averaging_time, t)

    s = Signal(name='target_file_name', value='')

    @bpp.stage_decorator(dets)
    @bpp.run_decorator(md={'sample_name':'{target_file_name}'})
    def inner():
        for e in energies:
            yield from bps.mv(energy, e)
            yield from bps.sleep(2)
                

            name_fmt = "{sample}_{energy}eV_pd{{pin_diode_current2_mean_value}}"
            
            e=energy.energy.position
            sample_name = name_fmt.format(sample=name,energy="%6.2f"%e )
            #print(f"\n\t=== Sample: {sample_name} ===\n")
            s.put(sample_name)
            yield from bps.trigger_and_read(dets + [s,energy])
        yield from bps.mv(energy, 2190)
        yield from bps.sleep(2)
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







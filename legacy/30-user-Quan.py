# E. Marino (UPenn, Murray)
# ref: Chopra, Clark
#
# ======================================================================
# proposal_id('2024_3', '315975_Gonzalez', analysis=True)
#
### To complie this file
#
#%run -i /home/xf12id/.ipython/profile_collection/startup/users/30-user-Marino.py
### See which filter combination gives good reading (100~500), diode saturates at 125k
# RE(test_pdcurrent(Natt=3, add_att1_9=1, add_att1_10=0, add_att1_11=0, add_att1_12=0))
# RE(test_pdcurrent(Natt=3, add_att1_9=1, add_att1_10=1))
#
### Take one measurement, or click 'Start'
# RE(ct(t = 1))
#
### Start measurement with the good filter combination
# RE(insitu_EM(t=1, name = 'EXsitu_PbS53_0p1pc_run1dilute', wait_time_sec=10, Natt=3, add_att1_9=1, add_att1_10=1, number_start=1))
#
#
#
# if do ctrl+C: RE.abort()
#
# RE(shopen())
# RE(shclose())
#
# Data: /nsls2/xf12id2/data/images/users/2022_1/309930_Murray/
# Analysis: /nsls2/xf12id2/analysis/2022_1/309930_Murray/
#
# ======================================================================

import numpy as np
import sys, time

# det = [pil1M, pdcurrent, pdcurrent1, pdcurrent2]
# dets = [pil300KW, pil1M]
# RE(measure_YQ(t=10, use_saxs=1, use_waxs=1, waxs_angle = 20, use_pdcurrent=0, name='sam4b_ref'))
# RE(measure_YQ(t=10, use_saxs=0, use_waxs=1, waxs_angle = 0, use_pdcurrent=0, name='sam4b_ref'))


# RE(measure_YQ(t=1, use_saxs=1, use_waxs=1, waxs_angle = 20, name='cap'))
def measure_YQ(t=1, use_saxs=1, use_waxs=1, waxs_angle = 20, use_pdcurrent=1, name='sam1'):
    det_exposure_time(t, t)

    if use_waxs:
        yield from bps.mv(waxs, waxs_angle)


    if use_waxs and use_saxs:
        dets = [pil2M, pil900KW]
    elif use_waxs:
        dets = [pil900KW]
    elif use_saxs:
        dets = [pil2M]
    if use_pdcurrent:
        dets.append(pdcurrent1)

    if use_saxs:
        for aa in np.arange(0, 3):
            yield from bps.mv(att1_9.open_cmd, 1)
            yield from bps.sleep(0.2)
            yield from bps.mv(att1_10.open_cmd, 1)
            yield from bps.sleep(0.2)

        fs.open()
        yield from bps.sleep(0.5)
        pd_curr = pdcurrent1.value
        fs.close()
        print("=== {}".format(pd_curr))
        for aa in np.arange(0, 5):
            yield from bps.mv(att1_9.close_cmd, 1)
            yield from bps.mv(att1_10.close_cmd, 1)
    else:
        pd_curr = 0


    #### Define sample name & Measure
    name_fmt = "{sample}_{etime}s_x{x}_y{y}_bpm{bpm}_pd{pd_curr}{md}"
    sample_name = name_fmt.format(
        sample=name,
        etime = "%.1f" % (t),
        x = "%.1f" % (piezo.x.position),
        y = "%.1f" % (piezo.y.position),
        bpm="%1.3f"%xbpm3.sumX.get(),
        # pd_curr = "%.1f" % pdcurrent1.get(),
        pd_curr = "%.1f" % (pd_curr),
        md = get_scan_md()
    )
    print(f"\n\t=== Sample: {sample_name} ===\n")
    sample_id(user_name="YQ", sample_name=sample_name)
    yield from bp.count(dets, num=1)


# RE(bps.mv(waxs, 13))
# sample_id(user_name='test', sample_name='test')

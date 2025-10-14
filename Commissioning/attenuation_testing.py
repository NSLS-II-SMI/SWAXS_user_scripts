# take measurements with different attenuators in with
# att1_1 though att1_12 and att2_1 through att2_12, while keeping att2_6 in all the time
def attenuation_test_no_beamstop():
    dets = [pil2M]
    det_exposure_time(2, 2)
    yield from bps.mv(att1_7, "insert") 
    yield from bps.mv(att1_6, "insert") 
    # put each other attenuator in and take a measurement, then remote it
    for j in range(5, 13):
        if j==8: # skip att2_8 since it's always in
            continue
        # get the correct att from the ipython user name space

        att = get_ipython().user_ns[f'att1_{j}']  # att1_j
        yield from bps.mv(att, "insert")  # put in attenuator
        # set sample name appropriately
        sample_id('direct_beam', f'att1_8_and_att1_{j}_sig{{pil2m_stats1_total}}')
        yield from bp.count(dets, num=1)
        yield from bps.mv(att, "retract")  # remove attenuator

def attenuation_test_on_pindiode():
    det_exposure_time(2, 2)
    dets = [pin_diode,pil2M]
    # put each other attenuator in and take a measurement, then remote it
    from IPython import get_ipython

    for j in range(5, 13):
        att = get_ipython().user_ns[f'att1_{j}']  # att1_j
        yield from bps.mv(att, "insert")  # put in attenuator
        # set sample name appropriately
        sample_id('direct_beam', f'_and_att1_{j}_pd{{pin_diode_current2_mean_value}}')
        yield from bp.count(dets, num=1)
        yield from bps.mv(att, "retract")  # remove attenuator
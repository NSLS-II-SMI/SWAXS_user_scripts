# take measurements with different attenuators in with
# att1_1 though att1_12 and att2_1 through att2_12, while keeping att2_6 in all the time
def attenuation_test_no_beamstop():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks an X-ray attenuator "ladder" — it inserts one extra
    #   attenuator foil at a time (att1_5 through att1_12), keeps a couple in the
    #   whole time, takes one SAXS image at each setting, then pulls that foil back
    #   out. This is the classic commissioning check of how much each foil dims the beam.
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with a
    #   ready-made attenuator-ladder routine. It steps through the foils for you and
    #   records the foil setting + measured signal straight into the saved data (so you
    #   don't have to bake "att1_8_and_att1_{...}_sig{...}" into the file name by hand):
    #
    #     from smi_plans import attenuator_ladder_run   # do this once at the top of your session
    #     yield from attenuator_ladder_run(
    #         "direct_beam",                            # the rest of the file name is filled in for you
    #         dets=[pil2M],                             # your detector(s), unchanged
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #   (The att1_*/att2_* attenuators themselves are unchanged and still work fine.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(2, 2)' line below (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    dets = [pil2M]
    det_exposure_time(2, 2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(2, 2)  — or at the prompt:  RE(det_exposure_time(2, 2)). (smi_plans' attenuator_ladder_run sets the exposure for you.)
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same attenuator-ladder check as above, but it also reads the
    #   pin-diode (a small beam-intensity sensor) at each foil setting, inserting one
    #   foil (att1_5..att1_12) at a time, taking a measurement, then retracting it.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' has a ready-made attenuator-ladder routine that
    #   steps the foils for you and records the foil setting + pin-diode reading into the
    #   saved data automatically (no need to hand-build the "_att1_{...}_pd{...}" name):
    #
    #     from smi_plans import attenuator_ladder_run   # do this once at the top of your session
    #     yield from attenuator_ladder_run(
    #         "direct_beam",                            # the rest of the file name is filled in for you
    #         dets=[pin_diode, pil2M],                  # your detectors, unchanged
    #     )
    #
    #   (This is just a tidier option to try later — your script below still works as-is,
    #    EXCEPT for the one line marked ⚠️ which genuinely needs a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(2, 2)' line below (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    det_exposure_time(2, 2)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan" (a recipe Bluesky runs), so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(2, 2)  — or at the prompt:  RE(det_exposure_time(2, 2)). (smi_plans' attenuator_ladder_run sets the exposure for you.)
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
##Collect data:

# SMI: 2021/9/22
# SAF: 308072  Standard        Beamline 12-ID   proposal:  309075


# create proposal:  proposal_id('2021_3', '309075_SWong')    #create the proposal id and folder
# Energy: 16.1 keV, 0.77009 A
# SAXS distance 3000
# SAXS in  and WAXS in air

# WAXS range [ -4, 56 ]


#  RE( shopen() )  # to open the beam and feedback
#  RE( shclose())

#  %run -i


#  WAXS, 900KW, 0 degree, beam center [ 220, 308 ]


# low div beam, 220 X 30 um2
# For 8 meter, beamStopX: 0.7 , 1M: X 0.25 , Center [ 490, 588 ]
# For 5 meter, beamstopX: 1.85 , 1M, X  1.13,   Center, [490, 588 ]
# For 3 meter, beamstopX: 1.9, 1M, X, 1.43 Center, [490, 588 ]
### For 2 meter, beamstopX: 1.8, 1M, X, 1.05 Center, [490, 588 ]


# The beam center on SAXS:
########################
# #First Run for  ,  SAXS 3 m, WAXS, 0, 20
# sample_dict = {   1: 'DTAB_Wash_0_min',  2: 'DTAB_Wash_5_min', 3: 'DTAB_Wash_15_min', 4: 'DTAB_Wash_30_min', 5: 'DTAB_Wash_45_min',
#  6: 'DTAB_Wash_60_min', 7: 'DTAB_Wash_90_min', 8: 'DTAB_Wash_120_min',  9: 'DTAB_Wash_240_min', 10: 'DTAB_Wash_480_min', 11: 'Ethanol',
#     12: 'CTAB_rxn_90_min',  13: 'CTAB_rxn_105_min', 14: 'CTAB_rxn_45_min',  15: 'CTAB_wash_5_min',           }

# pxy_dict = {  1: (45700, 700),  2: ( 40100-100 , 700 ),  3: ( 33900-200 , 700  ), 4: ( 26400 , 700  ), 5:( 1000 , -6500 ) ,
# 6: ( 14700 -1100 , 700 ),  7: ( 8600-1100 , 700  ), 8: ( 2300-1300 , -9700+2000  ), 9: ( -4000 - 1400 , 700  ),
# 10: ( -10300-1000 , 700 ),  11: ( -18000, 700), 12: ( -22900-1000 , 700  ), 13: ( -29200-1400, 700  ), 14: ( -35500-1400 , 700   ),
# 15: ( -43700 , 700   ),    }

# #  measure_series_saxs(  t= [  1 ] ,  dys = [0, -500, -1000, -1500, -2000,  ]   )
# #  measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500, -1000, -1500, -2000,  ]   ), manually measure waxs=0, 20

# The fifth one might be wrong, should be rerun it 'DTAB_Wash_45_min'

# ########################
# #Second
# sample_dict = {   1: 'CTAB_Wash_150_min',  2: 'CTAB_rxn_75_min', 3: 'CTAB_rxn_180_miin', 4: 'CTAB_rxn_210_min', 5: 'CTAB_rxn_60_min',
#  6: 'CTAB_rxn_240_min', 7: 'CTAB_rxn_300_min', 8: 'KBr_120_min',  9: 'CTAB_Wash_120_min', 10: 'CTAB_Wash_240_min', 11: 'CTAB_Wash_75_min',
#     12: 'CTAB_Wash_1_min',  13: 'CTAB_Wash_180_min', 14: 'CTAB_Wash_210_min',  15: 'CTAB_Wash_60_min',           }

# pxy_dict = {  1: (45700, 700),  2: ( 40100-400 , 700 ),  3: ( 33900-800 , 700  ), 4: ( 26400 , 700  ), 5:  ( 20400 , 700 ),
# 6: ( 14700 -1100 , 700 ),  7: ( 8600-1100 , 700  ), 8: ( 2300-1300+300 , 700  ), 9: ( -4000 - 1400 +400 , 700  ),
# 10: ( -10300-1000 +250, 700 ),  11: ( -18000+250, 700), 12: ( -22900-1000-150 , 700  ),  13: ( -29200-1400+250, 700  ), 14: ( -35500-1400+250 , 700   ),
# 15: ( -43700+450 , 700   ),    }

# Manually measure all one by one,  # e.g, mov_sam(14);    measure_series_wsaxs_one_sample( 14  )
# Then, measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500, -1000, -1500, -2000,  ]   )

########################
# #Third, using the 3D printed holder plus Kapton tap
# sample_dict = {   1: 'KBR_60min',  2: 'CTAB_rxn_10_min', 3: 'CTAB_rxn_15_min', 4: 'CTAB_rxn_5_min', 5: 'CTAB_rxn_30_min',
#  6: 'CTAB_rxn_120_min', 7: 'CTAB_rxn_150_min', 8: 'KBr_30_min',  9: 'NWB_6_h', 10: 'CTAB_Wash_0_min', 11: 'NW_8_h',
#     12: 'CTAB_rxn_1_min',  13: 'NWB_2_h', 14: 'CTAB_rxn_noheat',  15: 'Chloroform_Blank',           }

# pxy_dict = {  1: (43700, 1700),  2: ( 37700 , 2700 ),  3: (33499.9, 1699.87)  , 4: (26999.53, -800.33) , 5: (19999.34, 699.64),
# 6: (13399.02, -800.47),  7: (7499.24, 1699.5)  , 8: (2399.4, 800.01), 9: (-3800.51, 5500.02), 10:  (-10000.65, 199.94),
#  11:  (-14500.82, 4399.98) ,  12:  (-20400.66, 2300.01),   13: (-25500, 0   ),  14: ( -34300, -3000   ),   15: ( -37800, -3000   ),    }


# Fourth Run for  ,  SAXS 3 m, WAXS, 0, 20

# sample_dict = {   1: 'CTAB_Wash_10_min',  2: 'CTAB_Wash_15_min', 3: 'CTAB_Wash_30_min', 4: 'CTAB_Wash_45_min', 5: 'CTAB_Wash_90_min',
#  6: 'CTAB_Wash_105_min', 7: 'CTAB_Wash_300_min', 8: 'CTAB_Wash_480_min',  9: 'DTAB_Wash_45_min', }# 10: 'NWB_4_h'   }

# pxy_dict = {  1: (45700 + 200 , 4000),  2: ( 40100-100 +200 , 4000 ),  3: ( 33900-200 , 4000  ), 4: ( 27300 , 4000  ), 5:( 20400 ,4000 ) ,
# 6: ( 14700 -1100+900 ,4000 ),  7: ( 8000 , 4000  ), 8: ( 1700 ,  4000  ), 9: ( -4000 - 1400 ,4000  ),
#      }

# def run4():
#     ks = list( sample_dict.keys() )
#     #for k in ks:
#     #    measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500, -1000, -1500, -2000,  ]   )
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500, -1000, -1500, -2000,  ]   )


# #Fourth Fifth for  ,  SAXS 3 m, WAXS, 0, 20

# sample_dict = {   1: 'KBr_0_min',  2: 'Pt_NPs', 3: 'CTAB_rxn_0_min', 4: 'NWB_3_h', 5: 'NWB_1_h',
#   }
# pxy_dict = {  1: (44200, 2400),  2: ( 38100 , 200  ),  3: (34300, 3000 )  , 4: ( 31399, 3000 ) , 5: ( 26199, 7000 ),
#      }

# def run5():
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500, -1000, -1500, -2000,  ]   )

#     ks = list( sample_dict.keys() )
#     for k in ks:
#         measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500, -1000, -1500, -2000,  ]   )


# Six for Sunita's sample, 3meter
# user_name='SS'
# sample_dict = {   1: 'SS_H2',  2: 'SS_H1', 3: 'SS_G7', 4: 'SS_C4', 5: 'SS_G6',
#  6: 'SS_G8', 7: 'SS_I6', 8: 'SS_C8',  9: 'SS_C7', 10: 'SS_C5', 11: 'SS_I7',
#      12: 'SS_F1',  13: 'SS_F3', 14: 'SS_G4',  15: 'SS_F2',           }
# pxy_dict = {  1: (45900, 1700),  2: ( 39200 , 1700 ),  3: (33100, 1699.87)  , 4: (26699.53, 1700) , 5: (19999.34+300, 1700),
# 6: (13399.02+300, 1700),  7: (7499.24+100, 1699.5)  , 8: (2399.4-900, 1700), 9: (-3800.51-1300, 1700), 10:  (-10000.65-1300, 1700),
#  11:  (-17800, 1700) ,  12:  (-20400.66-4000+400, 1700),   13: (-30500, 1700   ),  14: ( -34300-1500-1000, 1700   ),   15: ( -43300, 1700   ),    }
# def run6():
#     ks = list( sample_dict.keys() )
#     for k in ks:
#         measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500   ]   )
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500   ]   )


# # 7th for Sunita's sample, 3meter
# user_name='SS'
# sample_dict = {   1: 'SS_G3',  2: 'SS_H4', 3: 'SS_I5', 4: 'SS_G5', 5: 'SS_F7',
#  6: 'SS_H8', 7: 'SS_I3', 8: 'SS_H5',  9: 'SS_H3', 10: 'SS_I1', 11: 'SS_I4',
#      12: 'SS_I2',  13: 'SS_G2', 14: 'SS_H7',  15: 'SS_G1',           }
# pxy_dict = {  1: (45900, 1700),  2: ( 39200 , 1700 ),  3: (33100, 1699.87)  , 4: (26699.53, 1700) , 5: (19999.34+300, 1700),
# 6: (13399.02+300, 1700),  7: (7499.24+100, 1699.5)  , 8: (2399.4-900, 1700), 9: (-3800.51-1300, 1700), 10:  (-10000.65-1300, 1700),
#  11:  (-17800, 1700) ,  12:  (-20400.66-4000+400, 1700),   13: (-30500, 1700   ),  14: ( -34300-1500-1000, 1700   ),   15: ( -43300, 1700   ),    }
# def run7():
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500   ]   )

#     ks = list( sample_dict.keys() )
#     for k in ks:
#         measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500   ]   )


# # 8th for Sunita's sample, 3meter
# user_name='SS'
# sample_dict = {   1: 'SS_C6',  2: 'SS_C1', 3: 'SS_C2', 4: 'SS_F6', 5: 'SS_F5',
#  6: 'SS_C3', 7: 'SS_H6', 8: 'SS_F4',  9: 'SS_F8', 10: 'SS_I8'      }
# pxy_dict = {  1: (45900, 1700),  2: ( 39200 , 1700 ),  3: (33100, 1699.87)  , 4: (26699.53, 1700) , 5: (19999.34+300, 1700),
# 6: (13399.02+300, 1700),  7: (7499.24+100, 1699.5)  , 8: (2399.4-900, 1700), 9: (-3800.51-1300, 1700), 10:  (-10000.65-1300, 1700),
#    }
# def run8():
#     ks = list( sample_dict.keys() )
#     for k in ks:
#         measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500   ]   )
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500   ]   )


# 9th for Empty sample, 3meter
# user_name=''
# sample_dict = {   2: 'Empty_Quartz',  3: 'Empty_Glass',     }
# pxy_dict = {    2: ( 39200 , 1700 ),  3: (33100, 1699.87)     }
# def run9():
#     ks = list( sample_dict.keys() )
#     measure_series_waxs(  t= [  1 ] , waxs_angle=40,  dys = [0, -500   ]   )
#     for k in ks:
#         measure_series_wsaxs_one_sample( sam_pos=k, t= [  1 ] , waxs_angle=20,  dys = [0, -500   ]   )
#     measure_series_waxs(  t= [  1 ] , waxs_angle=0,  dys = [0, -500   ]   )


# 10 th do calibration using AgBH
user_name = ""
sample_dict = {
    8: "AgBH",
}
pxy_dict = {8: (1400, -3600)}
# pizeo_Z = 3200, 0,
def run10():  # 3200  , 3meter
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to the AgBH calibration sample and takes a WAXS image at each of
    #   several WAXS arc angles, then one SAXS image.
    #
    # 💡 NEWER, EASIER WAY (and tidier): notice each line calls 'RE(...)' inside a normal Python
    #   'for' loop. 'RE(...)' is the command that actually starts the beamline running a recipe —
    #   calling it over and over in a loop makes a SEPARATE little run for every angle, which is
    #   slower and scatters your data across many runs. The modern style writes ONE recipe (a
    #   "plan") that sweeps the angle, and you press go ONCE. 'smi_plans' has presets for exactly
    #   this (AgBH calibration sweeps over the WAXS arc):
    #
    #     from smi_plans import agbh_calibration_run
    #     yield from agbh_calibration_run(           # run this whole thing with ONE  RE(run10())
    #         "AgBH",
    #         arc_angles=[0, 7, 20, 27, 40, 47, 55], # your angles, unchanged
    #         t=1,                                   # your exposure, unchanged
    #     )
    #   (Then 'run10' becomes a plan you launch once with RE(run10()), instead of calling RE
    #    inside the loop. Everything still gets recorded, all in one run.)
    # === end smi_plans note ================================================
    mov_sam(8)
    dy = 0
    for waxs_angle in [0, 7, 20, 27, 40, 47, 55]:
        RE(measure_waxs(t=1, waxs_angle=waxs_angle, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run each time. The modern way is one plan that sweeps the arc, launched once (see the note above) — tidier and all in one recorded run.
    RE(measure_saxs(t=1, att="None", dy=dy))


def run11():  # 0  , 3meter
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same as run10 but sweeps the WAXS arc angles in reverse order (no SAXS).
    #
    # 💡 NEWER, EASIER WAY: same idea as run10 — instead of calling 'RE(...)' (the "go" command)
    #   once per angle inside a Python loop, write one plan that sweeps the arc and launch it once:
    #
    #     from smi_plans import agbh_calibration_run
    #     yield from agbh_calibration_run("AgBH", arc_angles=[55, 47, 40, 27, 20, 7, 0], t=1)
    #   (then RE(run11()) once, instead of RE inside the loop — all recorded together.)
    # === end smi_plans note ================================================
    mov_sam(8)
    dy = 0
    for waxs_angle in [0, 7, 20, 27, 40, 47, 55][::-1]:
        RE(measure_waxs(t=1, waxs_angle=waxs_angle, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run each time. The modern way is one plan that sweeps the arc, launched once (see the note above).
    # RE( measure_saxs(  t = 1, att='None',  dy=dy ) )


def measure_series_wsaxs_one_sample(
    sam_pos=1,
    t=[1],
    waxs_angle=20,
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to one sample, then steps it through several y-offsets and exposure
    #   times, taking a combined WAXS+SAXS image at each.
    #
    # 💡 NEWER, EASIER WAY (and tidier): each measurement here is launched with 'RE(...)' (the
    #   "go" command) inside Python 'for' loops, so every point becomes its own separate run. For
    #   a synthesis/time-style series like this, 'smi_plans' lets you write ONE plan that walks the
    #   y positions (and even reads back time), recording everything into one run:
    #
    #     from smi_plans import time_series_run, motor_axis
    #     # e.g. step y while recording, in a single run you launch once:
    #     yield from time_series_run(
    #         sample_name, dets=[pil900KW, pil2M, pil300KW], t=1,   # note pil300KW retired — see ⚠️ in measure_wsaxs
    #         axes=[motor_axis("piezo_y", piezo.y, [y0 + d for d in dys])],
    #     )
    #   (Then you press go ONCE with RE(...) instead of calling RE inside the loops; all the
    #    positions/times are recorded together.)
    # === end smi_plans note ================================================
    mov_sam(sam_pos)
    for dy in dys:
        for ti in t:
            RE(measure_wsaxs(t=ti, waxs_angle=waxs_angle, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run for every point. The modern way is one plan that walks the positions, launched once (see the note above).


def measure_series_waxs(
    t=[1],
    waxs_angle=0,
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over every sample on the bar (from sample_dict) and, at each, steps
    #   through y-offsets and exposure times taking a WAXS image.
    #
    # 💡 NEWER, EASIER WAY: this is a multi-sample "bar" run. Instead of calling 'RE(...)' (the
    #   "go" command) once per point inside Python loops — which makes a separate run each time —
    #   'smi_plans' takes your sample list once and loops for you in a single recipe you launch once:
    #
    #     from smi_plans import multi_sample_run, SampleList, motor_axis
    #     samples = SampleList.from_columns(name=names, x=xs, y=ys)   # your sample_dict/pxy_dict, as columns
    #     yield from multi_sample_run(
    #         samples, dets=[pil900KW, pil300KW], t=1,                # note pil300KW retired — see ⚠️ in measure_waxs
    #         axes=[motor_axis("piezo_y", piezo.y, [d for d in dys])],
    #     )
    #   (Press go ONCE with RE(...); every sample/position is recorded together.)
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_waxs(t=ti, waxs_angle=waxs_angle, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run for every point. The modern way is one bar plan, launched once (see the note above).


def measure_series_wsaxs(
    t=[1],
    waxs_angle=20,
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over every sample on the bar and, at each, steps through y-offsets and
    #   exposure times taking a combined WAXS+SAXS image.
    #
    # 💡 NEWER, EASIER WAY: same as measure_series_waxs — a multi-sample "bar" run. Hand your
    #   sample list to 'smi_plans' once and let it loop in a single recipe launched once, instead
    #   of calling 'RE(...)' per point inside Python loops:
    #
    #     from smi_plans import multi_sample_run, SampleList, motor_axis
    #     samples = SampleList.from_columns(name=names, x=xs, y=ys)
    #     yield from multi_sample_run(samples, dets=[pil900KW, pil300KW, pil2M], t=1,   # pil300KW retired — see ⚠️ in measure_wsaxs
    #                                 axes=[motor_axis("piezo_y", piezo.y, list(dys))])
    #   (Press go ONCE with RE(...); everything recorded together.)
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_wsaxs(t=ti, waxs_angle=waxs_angle, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run for every point. The modern way is one bar plan, launched once (see the note above).


def measure_series_saxs(
    t=[1],
    dys=[
        0,
        -500,
        -1000,
        -1500,
        -2000,
    ],
):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: loops over every sample on the bar and, at each, steps through y-offsets and
    #   exposure times taking a SAXS image.
    #
    # 💡 NEWER, EASIER WAY: same multi-sample "bar" pattern. Let 'smi_plans' loop your sample list
    #   in one recipe you launch once, rather than calling 'RE(...)' per point inside Python loops:
    #
    #     from smi_plans import multi_sample_run, SampleList, motor_axis
    #     samples = SampleList.from_columns(name=names, x=xs, y=ys)
    #     yield from multi_sample_run(samples, dets=[pil2M], t=1,
    #                                 axes=[motor_axis("piezo_y", piezo.y, list(dys))])
    #   (Press go ONCE with RE(...); all samples/positions recorded together.)
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_saxs(t=ti, att="None", dy=dy))  # smi_plans: calling RE() inside a Python loop starts a brand-new run for every point. The modern way is one bar plan, launched once (see the note above).


##################################################
############ Some convinent functions#################
#########################################################


def movx(dx):
    RE(bps.mvr(piezo.x, dx))
    print(get_posxy())


def movy(dy):
    RE(bps.mvr(piezo.y, dy))
    print(get_posxy())


def get_posxy():
    return round(piezo.x.user_readback.value, 2), round(piezo.y.user_readback.value, 2)


def move_waxs(waxs_angle=8.0):
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_off(waxs_angle=8.0):
    RE(bps.mv(waxs, waxs_angle))


def move_waxs_on(waxs_angle=0.0):
    RE(bps.mv(waxs, waxs_angle))


def mov_sam(pos):
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px))
    RE(bps.mv(piezo.y, py))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample


def check_saxs_sample_loc(sleep=5):
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        time.sleep(sleep)


def measure_waxs_loop_sample(
    t=0.5,
    att="None",
    move_y=False,
    user_name="",
    saxs_on=True,
    waxs_angles=[0, 20],
    inverse_angle=False,
):

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for each WAXS arc angle, loops over every sample on the bar and takes a
    #   WAXS (and optionally SAXS) image, building the file name by hand from x/y/z/scan_id.
    #
    # 💡 NEWER, EASIER WAY: this is a multi-sample "bar" run. 'smi_plans' loops your sample list
    #   for you, sweeps the WAXS arc, and (importantly) records x/y/z/scan_id INTO the data and
    #   fills them into the file name automatically, so you don't have to assemble that long
    #   "{x_pos}_{y_pos}_..." string yourself:
    #
    #     from smi_plans import multi_sample_run, SampleList, motor_axis
    #     samples = SampleList.from_columns(name=names, x=xs, y=ys)
    #     yield from multi_sample_run(
    #         samples, dets=[pil2M, pil900KW], t=t,   # current detectors — see ⚠️ about pil300KW
    #         axes=[motor_axis("waxs_arc", waxs, list(waxs_angles))],
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (⚠️ notes
    #   below). (Heads-up for a human: 'waxs_angle_array' and 'k' aren't defined in this function —
    #   pre-existing issues this note does not change.)
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    waxs_angles = np.array(waxs_angles)
    max_waxs_angle = np.max(waxs_angles)
    for waxs_angle in waxs_angle_array:
        yield from bps.mv(waxs, waxs_angle)
        for pos in ks:
            mov_sam(k)
            sample = RE.md["sample"]
            name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
            sample_name = name_fmt.format(
                sample=sample,
                x_pos=piezo.x.position,
                y_pos=piezo.y.position,
                z_pos=piezo.z.position,
                waxs_angle=waxs_angle,
                expt=t,
                scan_id=RE.md["scan_id"],
            )
            print(sample_name)
            if saxs_on:
                if waxs_angle == max_waxs_angle:
                    dets = [
                        pil2M,
                        pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' (already in this list) — drop 'pil300KW'. (Note pil900KW is a different camera, so check beam-center/calibration.)
                        pil900KW,
                    ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
                else:
                    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' (already in this list) — drop 'pil300KW'.
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            # yield from bp.scan(dets, waxs, *waxs_arc)
            yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def measure_saxs(t=1, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes a single SAXS image of the current sample, building the file name by
    #   hand from the x/y positions, detector distance, exposure, and scan id.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' records the positions/detector-distance/scan-id INTO the
    #   data and fills them into the file name for you, so you don't hand-assemble that long
    #   "{x_pos}_{y_pos}_det{saxs_z}..." string. A single SAXS shot is one acquire:
    #
    #     from smi_plans import one_sample_run
    #     yield from one_sample_run(sample, dets=[pil2M], t=t)
    #   (records x/y, SDD, scan id automatically; '{att}' you'd add via the attenuator setup.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    dets = [pil2M]
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = (
        "{sample}_x{x_pos}_y{y_pos}_det{saxs_z}m_expt{expt}s_att{att}_sid{scan_id:08d}"
    )
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=np.round(piezo.x.position, 2),
        y_pos=np.round(piezo.y.position, 2),
        saxs_z=np.round(pil2M_pos.z.position, 2),
        expt=t,
        att=att,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")
    # det_exposure_time(0.5)


def measure_waxs(t=1, waxs_angle=0, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS arc to one angle and takes a single WAXS image of the current
    #   sample, building the file name by hand from the x/y/z positions, angle, exposure, scan id.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' records positions/angle/scan-id INTO the data and fills the
    #   file name for you. A single WAXS shot is one acquire (or one_sample_run):
    #
    #     from smi_plans import one_sample_run
    #     yield from bps.mv(waxs, waxs_angle)
    #     yield from one_sample_run(sample, dets=[pil900KW], t=t)   # see ⚠️ about pil300KW
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' (already in this list) — drop 'pil300KW'. (Note pil900KW is a different camera, so check beam-center/calibration.)
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        waxs_angle=waxs_angle,
        expt=t,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")


def measure_wsaxs(t=1, waxs_angle=20, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS arc to one angle and takes a combined WAXS+SAXS image of the
    #   current sample, building the file name by hand from positions, detector distance, etc.
    #
    # 💡 NEWER, EASIER WAY: 'smi_plans' records positions/SDD/angle/scan-id INTO the data and fills
    #   the file name for you. A single combined shot is one acquire (or one_sample_run):
    #
    #     from smi_plans import one_sample_run
    #     yield from bps.mv(waxs, waxs_angle)
    #     yield from one_sample_run(sample, dets=[pil900KW, pil2M], t=t)   # see ⚠️ about pil300KW
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' (already in this list) — drop 'pil300KW'. (Note pil900KW is a different camera, so check beam-center/calibration.)
    # att_in( att )
    if dy:
        yield from bps.mvr(piezo.y, dy)
    name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_det{saxs_z}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
    sample_name = name_fmt.format(
        sample=sample,
        x_pos=piezo.x.position,
        y_pos=piezo.y.position,
        z_pos=piezo.z.position,
        saxs_z=np.round(pil2M_pos.z.position, 2),
        waxs_angle=waxs_angle,
        expt=t,
        scan_id=RE.md["scan_id"],
    )

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")


def measure_waxs_multi_angles(
    t=1.0,
    att="None",
    dy=0,
    user_name="",
    saxs_on=False,
    waxs_angles=[0.0, 6.5, 13.0],
    inverse_angle=False,
):

    # waxs_angles = np.linspace(0, 65, 11)   #the max range
    # waxs_angles =   np.linspace(0, 65, 11),
    # [ 0. ,  6.5, 13. , 19.5]

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sweeps the WAXS arc through several angles and takes a WAXS (optionally also
    #   SAXS) image of the current sample at each, building the file name by hand each time.
    #
    # 💡 NEWER, EASIER WAY: sweeping the WAXS arc while recording is a 'smi_plans' axis; the
    #   positions/angle/scan-id get recorded into the data and the file name for you:
    #
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(
    #         sample, dets=[pil900KW], t=t,          # current WAXS detector — see ⚠️
    #         axes=[motor_axis("waxs_arc", waxs, list(waxs_angles), reverse_alternate=inverse_angle)],
    #     )
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (⚠️ notes below).
    # === end smi_plans note ================================================

    waxs_angle_array = np.array(waxs_angles)
    if inverse_angle:
        waxs_angle_array = waxs_angle_array[::-1]
    dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
    max_waxs_angle = np.max(waxs_angle_array)
    for waxs_angle in waxs_angle_array:
        yield from bps.mv(waxs, waxs_angle)
        sample = RE.md["sample"]
        if dy:
            yield from bps.mvr(piezo.y, dy)
        name_fmt = "{sample}_x{x_pos:05.2f}_y{y_pos:05.2f}_z{z_pos:05.2f}_waxs{waxs_angle:05.2f}_expt{expt}s_sid{scan_id:08d}"
        sample_name = name_fmt.format(
            sample=sample,
            x_pos=piezo.x.position,
            y_pos=piezo.y.position,
            z_pos=piezo.z.position,
            waxs_angle=waxs_angle,
            expt=t,
            scan_id=RE.md["scan_id"],
        )
        print(sample_name)
        if saxs_on:
            if waxs_angle == max_waxs_angle:
                dets = [
                    pil2M,
                    pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
                ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
            else:
                dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead.

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        # yield from bp.scan(dets, waxs, *waxs_arc)
        yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5)  — or at the prompt:  RE(det_exposure_time(0.5)).


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick test WAXS snapshot (no special bookkeeping).
    # 💡 NEWER, EASIER WAY: a quick snapshot is one acquire in 'smi_plans':
    #     from smi_plans import one_sample_run
    #     yield from one_sample_run("test", dets=[pil900KW], t=t)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick test SAXS snapshot (no special bookkeeping).
    # 💡 NEWER, EASIER WAY: a quick snapshot is one acquire in 'smi_plans':
    #     from smi_plans import one_sample_run
    #     yield from one_sample_run("test", dets=[pil2M], t=t)
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' call no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it below).
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t)  — or at the prompt:  RE(det_exposure_time(t)). (The smi_plans technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_pindiol_current():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the shutter briefly, reads the pin-diode current, closes the shutter,
    #   and returns that current (used to log beam intensity for transmission).
    # 💡 NEWER, EASIER WAY: instead of grabbing the value with '.value' to stuff into a file name,
    #   'smi_plans' records readings like the pin diode straight into the data — just list it in
    #   your detectors (e.g. dets=[pil2M, pin_diode]) and it's saved with each measurement, and
    #   you can pull it into the file name with a token like {pin_diode_current2_mean_value}.
    #   (Nothing here is broken — this still works.)
    # === end smi_plans note ================================================
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr

##Collect data:
# === smi_plans note (REVIEW 2026-06-22) ================================
# WHAT THIS FILE DOES: a transmission SAXS/WAXS "run-book" (S. Wong, 2021) — it defines a sample bar
#   (the many sample_dict / pxy_dict blocks), simple SAXS/WAXS measurement plans, multi-angle helpers,
#   and convenience "run" / "series" functions you launch by hand from the prompt.
#
# 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that turns these loops
#   into one-line runs and records position / beam / WAXS-arc straight INTO the data (so you don't
#   hand-build the long "{sample}_x..._y..." file names or stuff values into RE.md). Rough mapping:
#     - measure_saxs / measure_waxs / measure_wsaxs   -> transmission_run (one sample, SAXS/WAXS)
#     - the measure_series_* loops over the bar       -> transmission_bar (takes a SampleList)
#     - measure_waxs_multi_angles (WAXS arc sweep)    -> acquire(..., [motor_axis("wa", waxs, [...])])
#       from smi_plans import transmission_run, transmission_bar, acquire, motor_axis, SampleList
#
# ⚠️ TWO THINGS RECUR AND NEED A FIX TO RUN NOW (flagged inline below where they appear):
#     (1) 'det_exposure_time(t, t)' is now a "plan" — the plain call does nothing; inside a plan write
#         'yield from det_exposure_time(t, t)' (or run it as 'RE(det_exposure_time(t, t))').
#     (2) 'pil300KW' (the old WAXS camera) was retired — the current WAXS detector is 'pil900KW'
#         (a different camera, so re-check beam-center / calibration).
#   (The 'rayonix' MAXS detector mentioned in the commented "# waxs, maxs, saxs = [...]" notes was
#    also removed with no replacement — but it's only in comments here, so nothing to fix.)
#
# ⚠️ IMPORTANT pattern to know (see per-function notes): the "series"/"run" helpers below call the
#   beamline with  RE(measure_*(...))  INSIDE Python for loops. Each RE(...) starts a SEPARATE run, so
#   a long sequence becomes many tiny runs and you can't cleanly pause/resume it. For a simple
#   sequential measurement, make it ONE plan: replace 'RE(measure_*(...))' with 'yield from
#   measure_*(...)' and launch the function once — which is exactly what the smi_plans bar runs do.
#   (Closed-loop / scripted control belongs ABOVE the plan, not inside it.)
#
# (Your script below still works as-is, EXCEPT for anything marked ⚠️ which needs a fix to run now.)
# === end smi_plans note ================================================

# SMI: 2021/10/30
# SAF: 308072  Standard        Beamline 12-ID   proposal:  309075


# create proposal:  proposal_id('2021_3', '309075_SWong2')    #create the proposal id and folder
# create proposal:  proposal_id('2021_3', '30000_YZhang_Nov')    #create the proposal id and folder

# Energy: 16.1 keV, 0.77009 A
# SAXS distance 1800
# SAXS in  and WAXS in air

# WAXS range [ -4, 56 ]


#  RE( shopen() )  # to open the beam and feedback
#  RE( shclose())

#  %run -i
#  WAXS, 900KW, 0 degree, beam center [ 220, 308 ]


# The beam center on SAXS:

# 3 m, beam stop:  1.9
# 3m, 1M, x=-51, Y = -60
# the correspond beam center is [ 452, 565   ]
# beamstop_save()


# First run,

sample_dict = {
    1: "KBr_1_min",
    2: "KBr_2_min",
    3: "KBr_5_min",
    4: "KBr_15_min",
    5: "KBr_30_min",
    6: "KBr_45_min",
    7: "KBr_90_min",
    8: "KBr_120_min",
    9: "KBr_240_min",
    10: "KBr_480_min",
    11: "Oleylamine",
    12: "CTAB_30s",
    13: "CTAB_1min",
    14: "CTAB_2min",
    15: "CTAB_5min",
}
pxy_dict = {
    1: (42300, -1700),
    2: (39500, -1700),
    3: (33600, 0),
    4: (25400, 0),
    5: (19300, -1176),
    6: (12200, -2400),
    7: (7200, 0),
    8: (500, -3000),
    9: (-4300, 2416),
    10: (-8300, 400),
    11: (-15900, -2600),
    12: (-20500, -6100),
    13: (-27400, -7600),
    14: (-33700, 0),
    15: (-40800, 2000),
}
# measure_series_wsaxs_one_sample(  t= [  1 ] ,  dys = [0, -500, -1000, -1500, -2000,  ]   ), manually measure for each one, define the postion
# measure_series_waxs()


# Second run,
sample_dict = {
    1: "CTAB_10min",
    2: "CTAB_15min",
    3: "CTAB_30min",
    4: "CTAB_45min",
    5: "CTAB_60min",
    6: "CTAB_90min",
    7: "CTAB_120min",
    8: "CTAB_240min",
    9: "CTAB_480min",
    10: "NoCTAB",
    11: "NoPt_acac2",
    12: "NoMoCO6",
    13: "ML_0.09uM",
    14: "ML_0.45uM",
    15: "ML_0.9uM",
}

pxy_dict = {
    1: (42400, -1700),
    2: (37300, 0),
    3: (32100, -1000),
    4: (25900, 2000),
    5: (18600, -1176),
    6: (13600, 1000),
    7: (9100, -2000),
    8: (3200, 0),
    9: (-3200, 0),
    10: (-9100, 2000),
    11: (-14600, -4700),
    12: (-22800, -2500),
    13: (-29600, 2500),
    14: (-35100, -3000),
    15: (-41700, 5000),
}


sample_dict = {13: "ML_0.09uM", 14: "ML_0.45uM", 15: "ML_0.9uM"}
pxy_dict = {
    13: (-29600, 2500),
    14: (-35100, -3000),
    15: (-41700, 5000),
}

sample_dict = {
    1: "CTAB_10min",
    2: "CTAB_15min",
    3: "CTAB_30min",
    4: "CTAB_45min",
    5: "CTAB_60min",
    6: "CTAB_90min",
    7: "CTAB_120min",
    8: "CTAB_240min",
    9: "CTAB_480min",
    10: "NoCTAB",
    11: "NoPt_acac2",
    12: "NoMoCO6",
}
pxy_dict = {
    1: (42400, -1700),
    2: (37300, 0),
    3: (32100, -1000),
    4: (25900, 2000),
    5: (18600, -1176),
    6: (13600, 1000),
    7: (9100, -2000),
    8: (3200, 0),
    9: (-3200, 0),
    10: (-9100, 2000),
    11: (-14600, -4700),
    12: (-22800, -2500),
}


# Third run,
sample_dict = {3: "FL_CuDilute", 4: "FL_CuConc"}
pxy_dict = {
    3: (32400, 1000),
    4: (25400, 500),
}


sample_dict = {1: "FL_CuC_CapDia3mm", 2: "FL_CuC_CapDia2mm", 3: "FL_CuC_CapDia1mm"}
pxy_dict = {
    1: (31789, -8000),
    2: (25800, -700),
    3: (13800, -1000),
    4: (7600, -6000),
    5: (-4400, -6000),
}


# sample_dict = {  1: 'FL_CapDia3mm',   2: 'FL_CuC_CapDia2mm',  3: 'FL_CuC_CapDia1mm'  }
sample_dict = {
    1: "FL_CapDia2mm",
}
# sample_dict = {  1: 'FL_CuC_CapDia2mm',    }

sample_dict = {
    1: "FL_CapDia1mm",
}
# sample_dict = {  1: 'FL_CuC_CapDia1mm',    }

user_name = ""


def measure_waxs_one_sample(pos, t=1, waxs_angle=0, dys=[0]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for one sample (by bar position), takes a WAXS image at each y offset in 'dys'.
    # ⚠️ WORTH FIXING (about how it runs): this calls the beamline with  RE(measure_waxs(...))  INSIDE
    #   the for loop, so each y step is a SEPARATE run. For a simple y series, make it ONE plan:
    #   write 'yield from measure_waxs(...)' and launch this function once with RE(measure_waxs_one_sample(...)).
    # 💡 NEWER, EASIER WAY: a WAXS image down a few y spots is one line scan in smi_plans:
    #     from smi_plans import map_line_run
    #     yield from map_line_run(name, piezo.y, 0, -2000, len(dys), t=t, dets=[pil900KW])
    # === end smi_plans note ================================================
    name_sam(pos)
    for dy in dys:
        RE(measure_waxs(t=t, waxs_angle=waxs_angle, att="None", dy=dy))


def measure_swaxs_one_sample(pos, t=1, dys=[0]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: for one sample, takes a SAXS+WAXS image at each y offset in 'dys'.
    # ⚠️ WORTH FIXING (about how it runs): uses  RE(measure_wsaxs(...))  INSIDE the for loop (each y
    #   step is a SEPARATE run). To make it ONE plan, use 'yield from measure_wsaxs(...)' and launch once.
    # 💡 NEWER, EASIER WAY:  from smi_plans import map_line_run
    #     yield from map_line_run(name, piezo.y, 0, -2000, len(dys), t=t, dets=[pil2M, pil900KW])
    # === end smi_plans note ================================================
    name_sam(pos)
    for dy in dys:
        RE(measure_wsaxs(t=t, waxs_angle=20, att="None", dy=dy))


def measure_series_waxs(waxs_angle=0, dys=[0]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a WAXS bar — visits every sample on the bar and takes a WAXS image at each y
    #   offset in 'dys'.
    # ⚠️ WORTH FIXING (about how it runs): moves and measures with  RE(...)  INSIDE the for loops, so
    #   each step is a SEPARATE run and you can't pause/resume the whole bar. Make it ONE plan with
    #   'yield from' (move via mov_sam_re-style 'yield from bps.mv(...)' and 'yield from measure_waxs(...)').
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_list, y=y_list)
    #     yield from transmission_bar("waxs", samples, t=1, dets=[pil900KW])   # add a y line scan per sample
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            RE(measure_waxs(t=1, waxs_angle=waxs_angle, att="None", dy=dy))


def measure_series_swaxs_one_sample(sam_pos=1, dys=[0]):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves to one sample and takes a SAXS+WAXS image at each y offset in 'dys'.
    # ⚠️ WORTH FIXING (about how it runs): uses  RE(measure_wsaxs(...))  INSIDE the for loop (each y
    #   step is a SEPARATE run). Make it ONE plan with 'yield from measure_wsaxs(...)' and launch once.
    # 💡 NEWER, EASIER WAY:  from smi_plans import map_line_run
    #     yield from map_line_run(name, piezo.y, 0, -2000, len(dys), t=1, dets=[pil2M, pil900KW])
    # === end smi_plans note ================================================
    mov_sam(sam_pos)
    for dy in dys:
        RE(measure_wsaxs(t=1, waxs_angle=20, att="None", dy=dy))


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
    # WHAT THIS DOES: a SAXS bar — visits every sample on the bar and takes a SAXS image at each y
    #   offset in 'dys' (for each exposure time in 't').
    # ⚠️ WORTH FIXING (about how it runs): moves and measures with  RE(...)  INSIDE the for loops, so
    #   each step is a SEPARATE run. Make it ONE plan with 'yield from' and launch once.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_list, y=y_list)
    #     yield from transmission_bar("saxs", samples, t=t[0], dets=[pil2M])   # add a y line scan per sample
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_saxs(t=ti, att="None", dy=dy))


# def measure_series_wsaxs_one_sample( sam_pos=1, t= [  1 ] , waxs_angle=20,  dys = [0, -500, -1000, -1500, -2000,  ]   ):
#     mov_sam( sam_pos )
#     for dy in dys:
#         for ti in t:
#             RE( measure_wsaxs(  t = ti, waxs_angle= waxs_angle, att='None',  dy=dy ) )


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
    # WHAT THIS DOES: a SAXS+WAXS bar — visits every sample on the bar and takes a combined image at
    #   each y offset in 'dys' (for each exposure time in 't').
    # ⚠️ WORTH FIXING (about how it runs): moves and measures with  RE(...)  INSIDE the for loops, so
    #   each step is a SEPARATE run. Make it ONE plan with 'yield from' and launch once.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_list, y=y_list)
    #     yield from transmission_bar("swaxs", samples, t=t[0], dets=[pil2M, pil900KW])  # add a y line scan per sample
    # === end smi_plans note ================================================
    ks = list(sample_dict.keys())
    for k in ks:
        mov_sam(k)
        for dy in dys:
            for ti in t:
                RE(measure_wsaxs(t=ti, waxs_angle=waxs_angle, att="None", dy=dy))


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
# user_name=''
# sample_dict = {   8: 'AgBH',     }
# pxy_dict = {    8: (  1400 ,-3600 )    }
# pizeo_Z = 3200, 0,
def run10():  # 3200  , 3meter
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: an AgBH calibration sweep — moves to the AgBH sample and takes a WAXS image at
    #   each arc angle, then a SAXS image.
    # ⚠️ WORTH FIXING (about how it runs): uses  RE(measure_*(...))  INSIDE the for loop, so each arc
    #   angle is a SEPARATE run. Make it ONE plan with 'yield from measure_waxs(...)' and launch once.
    # 💡 NEWER, EASIER WAY: an AgBH calibration is a smi_plans commissioning run, and sweeping the WAXS
    #   arc is one axis:
    #     from smi_plans import agbh_calibration_run        # or: acquire(..., [motor_axis("wa", waxs, [...])])
    #     yield from agbh_calibration_run(t=1, dets=[pil900KW, pil2M])
    # === end smi_plans note ================================================
    mov_sam(8)
    dy = 0
    for waxs_angle in [0, 7, 20, 27, 40, 47, 55]:
        RE(measure_waxs(t=1, waxs_angle=waxs_angle, att="None", dy=dy))
    RE(measure_saxs(t=1, att="None", dy=dy))


def run11():  # 0  , 3meter
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: like run10 but sweeps the WAXS arc in reverse order (and skips the SAXS shot).
    # ⚠️ WORTH FIXING (about how it runs): uses  RE(measure_waxs(...))  INSIDE the for loop (each arc
    #   angle is a SEPARATE run). Make it ONE plan with 'yield from measure_waxs(...)' and launch once.
    # 💡 NEWER, EASIER WAY: sweeping the WAXS arc is one axis in smi_plans:
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire("AgBH", [pil900KW], [motor_axis("wa", waxs, [55, 47, 40, 27, 20, 7, 0])])
    # === end smi_plans note ================================================
    mov_sam(8)
    dy = 0
    for waxs_angle in [0, 7, 20, 27, 40, 47, 55][::-1]:
        RE(measure_waxs(t=1, waxs_angle=waxs_angle, att="None", dy=dy))
    # RE( measure_saxs(  t = 1, att='None',  dy=dy ) )


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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a convenience "go to sample N" — moves x/y to that sample's bar position and
    #   records the sample name in RE.md.
    # 💡 NOTE: this uses  RE(bps.mv(...))  so it can only be called from the prompt, NOT from inside a
    #   running plan (calling RE() inside a running plan errors). To move from inside a plan, write
    #   'yield from bps.mv(...)'. In smi_plans, 'goto_sample(samples, "name")' does this for you.
    # === end smi_plans note ================================================
    px, py = pxy_dict[pos]
    RE(bps.mv(piezo.x, px))
    RE(bps.mv(piezo.y, py))
    sample = sample_dict[pos]
    print("Move to pos=%s for sample:%s" % (pos, sample))
    RE.md["sample"] = sample


def name_sam(pos):
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
    # WHAT THIS DOES: a multi-angle WAXS bar — for each WAXS arc angle it visits every sample and
    #   takes a WAXS (or SAXS+WAXS at the widest angle) image, building the file name by hand.
    #   (Heads up: as written it loops over 'waxs_angle_array', which isn't defined in this function —
    #    you probably meant 'waxs_angles'; it would stop with a "name is not defined" error.)
    # 💡 NEWER, EASIER WAY: this is a transmission bar with a WAXS-arc axis — smi_plans records the
    #   arc/position/beam into each image and names the files for you:
    #     from smi_plans import transmission_bar, SampleList
    #     samples = SampleList.from_columns(name=names, x=x_list, y=y_list)
    #     yield from transmission_bar("loop", samples, t=t, dets=[pil2M, pil900KW])  # sweep the arc as an axis
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the
    #   ⚠️ notes below). (internal: Tier 1.)
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
                        pil300KW,  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
                        pil900KW,
                    ]  # waxs, maxs, saxs = [pil300KW, rayonix, pil2M]
                else:
                    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
            det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
            sample_id(user_name=user_name, sample_name=sample_name)
            print(f"\n\t=== Sample: {sample_name} ===\n")
            # yield from bp.scan(dets, waxs, *waxs_arc)
            yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)


def measure_saxs(t=1, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one transmission SAXS image of the current sample, building the file name
    #   from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M])   # records position/beam into the data + name
    #   (Your script below works as-is EXCEPT for the ⚠️ line, which needs a fix now. internal: Tier 1.)
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

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")
    # det_exposure_time(0.5)


def measure_waxs(t=1, waxs_angle=0, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: moves the WAXS arc to a given angle and takes one WAXS image of the current
    #   sample, building the file name from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil900KW])   # set the WAXS arc as you do now
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (see the
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
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

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
    sample_id(user_name=user_name, sample_name=sample_name)
    print(f"\n\t=== Sample: {sample_name} ===\n")
    print("Collect data here....")
    yield from bp.count(dets, num=1)
    # att_out( att )
    sample_id(user_name="test", sample_name="test")


def measure_wsaxs(t=1, waxs_angle=20, att="None", dy=0, sample=None):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes BOTH a SAXS and a WAXS image of the current sample at a given WAXS arc
    #   angle, building the file name from the current x/y/z and detector distance.
    # 💡 NEWER, EASIER WAY:  from smi_plans import transmission_run
    #     yield from transmission_run(sample, t=t, dets=[pil2M, pil900KW])   # set the WAXS arc as you do now
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' call no longer sets the exposure unless run as a plan (see the
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================
    if sample is None:
        sample = RE.md["sample"]
    yield from bps.mv(waxs, waxs_angle)
    dets = [pil900KW, pil300KW, pil2M]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).
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

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: sweeps the WAXS arc on the current sample — for each arc angle it takes a WAXS
    #   (or SAXS+WAXS at the widest angle) image, building the file name by hand.
    # 💡 NEWER, EASIER WAY: the WAXS arc is one axis in smi_plans (it records the arc/position/beam
    #   into each image and names the files for you):
    #     from smi_plans import acquire, motor_axis
    #     yield from acquire(name, [pil900KW], [motor_axis("wa", waxs, [0.0, 6.5, 13.0])])
    #   (Your script below works as-is EXCEPT for the ⚠️ lines, which need a fix now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: (1) 'pil300KW' was retired — it's now 'pil900KW'; (2) the
    #   'det_exposure_time(...)' calls no longer set the exposure unless run as a plan (see the
    #   ⚠️ notes below). (internal: Tier 1.)
    # === end smi_plans note ================================================

    # waxs_angles = np.linspace(0, 65, 11)   #the max range
    # waxs_angles =   np.linspace(0, 65, 11),
    # [ 0. ,  6.5, 13. , 19.5]

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
                dets = [pil300KW]  # ⚠️ FIXME(smi_plans): 'pil300KW' was removed (it would error). The current WAXS detector is 'pil900KW' — use that instead (note: it's a different camera, so check beam-center/calibration).

        det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
        sample_id(user_name=user_name, sample_name=sample_name)
        print(f"\n\t=== Sample: {sample_name} ===\n")
        # yield from bp.scan(dets, waxs, *waxs_arc)
        yield from bp.count(dets, num=1)
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)


def snap_waxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick WAXS snapshot (a "test" image) of whatever is in the beam.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run("test", t=t, dets=[pil900KW]) does this and
    #   sets the exposure for you. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    dets = [pil900KW]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def snap_saxs(t=0.1):
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: takes one quick SAXS snapshot (a "test" image) of whatever is in the beam.
    # 💡 NEWER, EASIER WAY: smi_plans' transmission_run("test", t=t, dets=[pil2M]) does this and sets
    #   the exposure for you. (Your script below works as-is EXCEPT for the ⚠️ line.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(t)' line below no longer sets the exposure
    #   unless run as a plan (see the ⚠️ note on it).
    # === end smi_plans note ================================================
    dets = [pil2M]
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(...)  — or at the prompt:  RE(det_exposure_time(...)). (smi_plans' technique runs set exposure for you via t=.)
    yield from (bp.count(dets, num=1))


def measure_pindiol_current():
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: opens the fast shutter briefly, reads the pin-diode current, closes the shutter,
    #   and returns the reading (a quick beam/transmission check).
    # 💡 NEWER, EASIER WAY: smi_plans records the pin-diode reading straight into the data during a
    #   transmission_run, so you usually don't need to read it by hand. (Nothing here is broken.)
    # === end smi_plans note ================================================
    fs.open()
    yield from bps.sleep(0.3)
    pd_curr = pdcurrent1.value
    fs.close()
    print("--------- Current pd_curr {}\n".format(pd_curr))
    return pd_curr

"""
2026C3_TSAXS384.py -- Tue 2026-10-20: room-temperature transmission SAXS/WAXS of the
384-cell holder (3-4 bars), in air, 16.1 keV low divergence, SAXS 2M at 5 m.

The holder spans more than the piezo travel, so each bar is put in the beam with the Huber
stack (sx, sy in mm) and the piezo (x, y in um) steps from cell to cell.  A bar is a
rows x cols grid; its cells come from a 3-point calibration (handles pitch, tilt and axis
directions), so measure the corners rather than trusting nominal pitches.

Run sheet
---------
0) bsui
     proposal_swap(<pass id>); project_set('TSAXS384')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_TSAXS384.py
     preflight()
1) Calibrant: RE(measure_wsaxs('AgBH', t=1, arc=20)); RE(measure_waxs('AgBH', t=1, arc=0))
2) Calibrate each bar (camera, or RE(bp.rel_scan([pil2M, pin_diode], piezo.x, -3000, 3000, 61))
   across cell walls):
     move the Huber so the bar is in the beam  -> here('sx', 'sy')  -> BARS[..]['base']
     center on cell A01                         -> here('x', 'y')    -> 'first'
     center on the last cell of row A           -> here('x', 'y')    -> 'last_in_row'
     center on the first cell of the last row   -> here('x', 'y')    -> 'first_in_last_row'
   Edit BARS, re-run this file; uncalibrated bars are skipped.
3) Sample names: NAMES_CSV (columns cell,sample; cell like B1-A01) or NAMES below.  Unnamed
   cells are not measured -- name the empty-cell / solvent backgrounds explicitly.
4) Check a few cells, then run:
     mov_sam('B1-A01'); RE(snap())
     RE(run_trans(select(SAMPLES, 'B1-A01', 'B1-A02'), **TRANS))
     preview(run_trans(**TRANS))                   # dry run: names + count
     RE(run_trans(**TRANS))                        # all named cells of MEASURE_BARS
     RE(run_trans(bar_samples('B3'), **TRANS))     # one bar

UPenn B001 Au-Ag-Cu array, after the N2 / CO2RR screening (55 spots on carbon paper, red frame,
Huber sy + piezo x/y).  Spot n = red label n on
pyCLEAR/data/Received/2026-10-12_AuAgCu-array/B001_AuAgCu55_AfterScreening_OpticalImage_mark_position.png
= pyCLEAR Sample0000nn (PIPETMAX target-ID order); names Sample0000nn_B001_<composition>_AfterScreening.
U1) Positions: MEASURED55 = spots centered by hand on the on-axis camera; every other spot is mapped
    from its blue dot on the marked image (PIX55) by an affine fit through the measured ones, except
    the faint bottom row (Au-Cu edge), placed one lattice step from its neighbours in the next row
    (printed when this file runs; show_samples(HOLDER55) lists them).
      show_samples(HOLDER55)
U2) Check the spots furthest from the measured ones before the long run (1, 11, 20, 41, 53, 55):
      mov_sam(55, HOLDER55); RE(ova_snap('test'))
    off-center: center it by hand, here('sy', 'x', 'y') -> MEASURED55, re-run this file (refits);
    for a spot at a shifted Huber sx (see U3) here('sy', 'x', 'y', 'sx').
    Once: the sign of Huber sx vs piezo x (SXDIR55), on a spot you can see:
      mov_sam(49, HOLDER55); RE(bps.mvr(stage.x, 0.5, piezo.x, -500))
      spot stays centered: SXDIR55 = 1; it moved ~1 mm: SXDIR55 = -1, re-run this file
      RE(bps.mvr(stage.x, -0.5, piezo.x, 500))
U3) Measure row by row: the Huber heats up (and stops) when it moves a lot, so it moves once per
    row -- the spots of a row share one sy and the piezo y takes the spot-to-spot height.  The piezo
    y only travels -9310..12400 um (LIM55), so each row's sy is raised until its crosses fit below
    12400 (then mov_sam shows a different sy / y split of the same spot than MEASURED55).  The piezo
    x only travels -47000..47000 um: spots whose cross does not fit (the far left 52 .. 55) are
    measured with the Huber sx shifted by whole mm, so a row is split there, each part with all arcs
    (the Huber sx moves a few times only).  Bottom
    row first, S1 -> S55, then S54 -> S2, S3 -> S52, ...; the blank carbon_paper_after_reaction
    (BLANKS55) goes with the row of S5.  Per row all arcs 0, 20, 40 (SAXS at 40); per spot a
    13-point cross (x -900..900 then y -900..900, 300 um steps) and one on-axis camera image:
      preview(run_holder_55after())      # 56 x 13 x 3 = 2184 exposures
      RE(run_holder_55after())
      RE(run_holder_55after(35, 36, 'carbon_paper_after_reaction'))   # a few (red labels / names)
      RE(run_holder_55after(arcs=(40,), ova=False))   # e.g. redo one arc
    The on-axis camera must be acquiring; images -> YZ['ova_dir'], one logbook row each.
    After an error: within a row the arcs are the outer loop (all spots at 0, then 20, then 40), so
    finish the row with the spots / arcs missing, then the next rows, e.g.
      RE(run_holder_55after(55, arcs=(0,)))
      RE(run_holder_55after(rows=(0,), arcs=(20, 40), ova=False))
      RE(run_holder_55after(rows=range(1, 10)))

ORNL (C. Liu) powders, Box 1 (after the 55): a Corning 384-well plate, glass bottom, Kapton over the
wells, rows A (bottom on the photo) .. P, columns 1 .. 24.  Wells and names in CLIU_BOX1 (pyCLEAR
Sample000226-319, B005 Cu-M / B006 / B007), named CL_<sample>_Powder; photo + sheet in
pyCLEAR/data/Received/2026-10-15_CLiu-ORNL.  81 powders: M6-M14 (B006, bad grey powder) are
skipped (CLIU_SKIP), 87 Cu(OH)2 is in M18; blanks: the empty wells A1 and P24 (CLIU_BLANKS).
The Huber y motor overheats: huber_y_mv moves it in <= 5 mm steps and, above 48 C (XF:12ID:m65.VAL),
waits until it is below 45 C.  Row N is the top in reach, so row P comes after pushing the plate down.
C1) Corners A1, A24, N1, N24 centered by hand -> CAL_CLIU (done 10-20); re-running this file prints the
    fitted pitch (4.5 mm) and the plan.  The whole plate at Huber sx = SX_CLIU (-2.5; -3 hit the piezo
    x limit on column 24): the piezo x runs from -56000 (A1) to 47300 (A24) -- check both ends, and a
    well far from the corners:
      mov_sam('A24', PLATE_CLIU)
      mov_sam('A1', PLATE_CLIU)
      mov_sam('G12', PLATE_CLIU); RE(ova_snap('test'))
    A failed end: change SX_CLIU (-0.5 mm moves both ends +500 um) and LIM_CLIU, re-run this file.
C2) Rows M .. A (74 wells): one WAXS arc at a time over all wells, 3 spots per well (CROSS_CLIU: the
    centre, then y -500, 500), SAXS at 40, one camera image per well.  The Huber x moves once (to
    SX_CLIU), the Huber y holds 3 heights (rows M-K-I, G-E-C, A; the piezo y takes the rows within),
    visited from the top down and in reverse at the next arc:
      preview(run_cliu_box1())                 # 74 x 3 x 3 = 666 exposures
      RE(run_cliu_box1())
      RE(run_cliu_box1('M18', 'A1'))           # a few wells;  rows='KM': some rows
      RE(run_cliu_box1(arcs=(20, 40)))         # e.g. after an error during the arc-20 pass
C3) Row P: push the plate down, center P1 and P24 -> CAL_CLIU_P, re-run this file:
      preview(run_cliu_box1_P())               # 9 x 3 x 3 = 81 exposures, the Huber y stays put
      RE(run_cliu_box1_P())

UPenn B001 Au-Ag-Cu array, as prepared (the square piece, untested; after Box 1).  The same 55 spots
and pyCLEAR samples as the piece after screening, named Sample0000nn_B001_<composition>_AsPrepared.
Spot n = red label n on
pyCLEAR/data/Received/2026-10-12_AuAgCu-array/B001_AuAgCu55_asprepared_OpticalImage_mark_position.png
(PIX55B: the circle centres; all 55 are visible, so every spot not measured comes from the photo fit).
B1) Mount; center >= 3 spots far apart on the on-axis camera (1, 10, 55; a 4th, e.g. 33, gives the
    fit residual), here('sy', 'x', 'y') -> MEASURED55B (here('sy', 'x', 'y', 'sx') at another Huber
    sx); a bare carbon-paper spot -> BLANKS55B with the array row it goes with; re-run this file
    (prints the fit and the plan), then check spots far from the measured ones:
      mov_sam(41, HOLDER55B); RE(ova_snap('test'))
    off-center: center it, add it to MEASURED55B, re-run this file (refits).  Spots past the piezo x
    travel get the Huber sx shifted (printed; SXDIR55 as for the piece after screening).
B2) Per spot as the piece after screening (13-point cross, arcs 0, 20, 40, SAXS at 40, one camera
    image), ordered as Box 1: the array rows from the top in a few Huber sy bands (the piezo y takes
    the rows within a band), one WAXS arc at a time over all spots, the bands reversed at the next arc:
      preview(run_holder_55before())             # 55 x 13 x 3 = 2145 exposures, + 39 per blank
      RE(run_holder_55before())
      RE(run_holder_55before(33, 'carbon_paper_as_prepared'))   # a few (red labels / names)
      RE(run_holder_55before(arcs=(20, 40)))     # e.g. after an error during the arc-20 pass

ORNL (C. Liu) suspensions, Box 2: the same plate type as Box 1; the B005 suspensions (81, pyCLEAR
box-2 wells, rows B .. P), named CL_<pyCLEAR name>_Suspension, + AgBH (D24), GL_52C (F23) and
MH_5_61_A (F24) (DNA-assembled nanoparticle superlattices); blanks: the empty wells B24 and P24
(CLIU2_BLANKS -- check they are empty).  Photo:
pyCLEAR/data/Received/2026-10-15_CLiu-ORNL/B005_CuM_81_Box2_solution_OpticalImage_mark_position.jpg
D1) Corners A1, A24, M1, M24 centered by hand -> CAL_CLIU2 (done 10-21); rows N, P (CLIU2_LATER) come
    after pushing the box down.  Re-running this file prints the fit, the Huber sx (SX_CLIU2 = None:
    chosen from the corners) and the plan -- wells out of reach are listed and left out.  Check the
    piezo x ends and a middle well:
      mov_sam('B2', PLATE_CLIU2); mov_sam('F24', PLATE_CLIU2); mov_sam('H12', PLATE_CLIU2)
D2) Rows B .. L as Box 1 (3 spots per well, arcs 0, 20, 40, SAXS at 40, one camera image per well):
      preview(run_cliu_box2())                 # 65 x 3 x 3 = 585 exposures
      RE(run_cliu_box2())
      RE(run_cliu_box2('D24'))                 # e.g. AgBH first
D3) Rows N, P: push the box down, center N1, N24, P1, P24 -> CAL_CLIU2_PUSHED (done 10-21), re-run:
      preview(run_cliu_box2_pushed())          # 21 x 3 x 3 = 189 exposures
      RE(run_cliu_box2_pushed())
D4) Re-run of all of Box 2 after a beam error (10-21): CLIU2_RUN = 'run2' ends every name (and
    run_batch Box2_run2): RE(run_cliu_box2_pushed()) now, then push the box back up, check a corner
    (mov_sam('B2', PLATE_CLIU2); RE(ova_snap('test'))) -- moved: new corners -> CAL_CLIU2, re-run
    this file -- and RE(run_cliu_box2()).

W. Liu Au nanoparticles, Box 3 (solutions, 384-well plate): S6 .. S55 in H8-17, G8-17, F8-17,
E8-17, C8-17, named WL_Au_S6 ..; references WL_SiO2_H7, _F7, _C7, _D11 and WL_Water_G7, _E7.  Photo
and map: pyCLEAR/data/Received/2026_1020_WLiu/WH_Au_55_Box3_solution_OpticalImage_mark_position.*
W1) Center the four corners -> CAL_WLIU, re-run this file (prints the fit and the plan), check:
      mov_sam('H8', PLATE_WLIU); mov_sam('C17', PLATE_WLIU); RE(ova_snap('test'))
W2) As Box 1 (3 spots per well, arcs 0, 20, 40, SAXS at 40, one camera image per well):
      preview(run_wliu_box3())                 # 56 x 3 x 3 = 504 exposures
      RE(run_wliu_box3())
"""

YZ.update(
    user='CFN',                 # EDIT: group tag used as the file-name prefix
    experiment='TSAXS384',
    md={'beam': '16.1 keV, low divergence', 'environment': 'air, RT',
        'holder': '384-cell holder (Huber + piezo)', 'saxs_sdd_m': 5},
    ova_dir='/nsls2/auto-storage/smi/proposals/2026-3/pass-321337/projects/TSAXS384/user_data/OVA/',
)

# EDIT after calibration: Huber position of each bar (mm) and its cell grid on the piezo (um).
# None = not calibrated yet (bar skipped).

'''
notes:
huber limit: y [ -30, 20 ]
pz limit: y [ -20000, 20000 ]



red sharpen red marker: 
huber: x, y, 0. 11
pz: x -7600, y 12300



bottom most visiable sample: (sample 35 , see the image) 
huber: x, y, 0. 7
pz: x -7600, y 12300

second bottom, on top of bottom most visible sample (left one, sample 36 ): 
huber: x, y, 0. 2.4
pz: x -12800, y 12300

second bottom, on top of bottom most visible sample (right one, sample 29): 
huber: x, y, 0. 2.4
pz: x -2300, y 12300



third bottom, on top of bottom most visible sample  (sample 30): 
huber: x, y, 0. -2.2
pz: x -6700, y 12300


fourth bottom, on top of bottom most visible sample (left one, sample 31): 
huber: x, y, 0. -8
pz: x -11100, y 12300

fourth bottom, on top of bottom most visible sample (right one, sample 23): 
huber: x, y, 0. -7
pz: x -1400, y 12300


fifth bottom, on top of bottom most visible sample  (sample 24): 
huber: x, y, 0. -12.6
pz: x -5400, y 12300



sixth bottom, on top of bottom most visible sample (left one, sample 25): 
huber: x, y, 0. -18
pz: x -9300, y 12300

sixth bottom, on top of bottom most visible sample (right one, sample 16): 
huber: x, y, 0. -17.8
pz: x 200, y 12300


seventh bottom, on top of bottom most visible sample (sample 17): 
huber: x, y, 0. -23.2
pz: x -4400, y 12300



eighth bottom, on top of bottom most visible sample (left one, sample 18): 
huber: x, y, 0. -27.4
pz: x -8300, y 12300

eighth bottom, on top of bottom most visible sample (right one, sample 8): 
huber: x, y, 0. -27.4
pz: x 1500, y 12300


ninth bottom, on top of bottom most visible sample (sample 9): 
huber: x, y, 0. -30
pz: x -2500, y 10500

tenth bottom, the last one (top row) sample 10: 
huber: x, y, 0. -30
pz: x -7600, y 4700




CLiu Box
bottom, left (A1)
hub: x, y, -2, 10.8
pz: x, y, -56500, 12300 

bottom, Right (A24)
hub: x, y, -2, 10.8
pz: x, y, 46800, 10800


N24:
hub: x, y, -2, -30
pz: x, y, 45800, -7034

N1:
hub: x, y, -2, -30
pz: x, y, -57303, -5634











'''



BARS = {
    'B1': dict(base={'sx': None, 'sy': None}, rows='ABCD', cols=24,
               first=None, last_in_row=None, first_in_last_row=None),
    'B2': dict(base={'sx': None, 'sy': None}, rows='ABCD', cols=24,
               first=None, last_in_row=None, first_in_last_row=None),
    'B3': dict(base={'sx': None, 'sy': None}, rows='ABCD', cols=24,
               first=None, last_in_row=None, first_in_last_row=None),
    'B4': dict(base={'sx': None, 'sy': None}, rows='ABCD', cols=24,
               first=None, last_in_row=None, first_in_last_row=None),
}
MEASURE_BARS = ['B1', 'B2', 'B3']

# EDIT: cell -> sample name; a CSV (cell,sample) overrides this when NAMES_CSV is set
NAMES = {
    # 'B1-A01': 'Empty', 'B1-A02': 'Water', 'B1-A03': 'PS50k-1wt',
}
NAMES_CSV = None    # e.g. '/nsls2/data/smi/proposals/2026-3/pass-XXXXXX/TSAXS384_names.csv'

TRANS = dict(
    t=1,
    arcs=(0, 20),           # WAXS at 0 and 20 deg; SAXS (2M) with the arc-20 frames
    saxs='max',
    offsets=((0, 0),),      # e.g. ((0, -300), (0, 300)) for two spots per cell (offset_axes x, y)
)


def bar_samples(bar, names=None):
    """Named cells of one calibrated bar ([] if not calibrated)."""
    g = BARS[bar]
    if None in (g['first'], g['last_in_row']) or None in g['base'].values() \
            or (len(g['rows']) > 1 and g['first_in_last_row'] is None):
        print(f'bar {bar} not calibrated -- skipped')
        return []
    if names is None:
        names = read_names_csv(NAMES_CSV) if NAMES_CSV else NAMES
    return grid_cells(g['rows'], g['cols'], first=g['first'], last_in_row=g['last_in_row'],
                      first_in_last_row=g['first_in_last_row'], axes=('x', 'y'),
                      base=g['base'], prefix=bar, names=names)


SAMPLES = [s for bar in MEASURE_BARS for s in bar_samples(bar)]
print(f'{len(SAMPLES)} named cells in bars {MEASURE_BARS}')


###############################################################################################
# UPenn B001 Au-Ag-Cu array (55 spots on carbon paper), the piece after the N2 / CO2RR screening
###############################################################################################
# Spot n (red label n on the marked image) = pyCLEAR Sample0000nn, in PIPETMAX target-ID order:
# PIPETMAX column k = 0..9 (Cu = 2k uL), row r = k..9; target ID = 1 + 14 k + r.
PYCLEAR55 = [
    'Sample000001_B001_Au10', 'Sample000002_B001_Au9Ag1', 'Sample000003_B001_Au8Ag2',
    'Sample000004_B001_Au7Ag3', 'Sample000005_B001_Au6Ag4', 'Sample000006_B001_Au4Ag6',
    'Sample000007_B001_Au3Ag7', 'Sample000008_B001_Au2Ag8', 'Sample000009_B001_Au1Ag9',
    'Sample000010_B001_Ag10', 'Sample000011_B001_Au9Cu1', 'Sample000012_B001_Au8Ag1Cu1',
    'Sample000013_B001_Au7Ag2Cu1', 'Sample000014_B001_Au6Ag3Cu1', 'Sample000015_B001_Au4Ag4Cu2',
    'Sample000016_B001_Au3Ag6Cu1', 'Sample000017_B001_Au2Ag7Cu1', 'Sample000018_B001_Au1Ag8Cu1',
    'Sample000019_B001_Ag9Cu1', 'Sample000020_B001_Au8Cu2', 'Sample000021_B001_Au7Ag1Cu2',
    'Sample000022_B001_Au6Ag2Cu2', 'Sample000023_B001_Au4Ag3Cu3', 'Sample000024_B001_Au3Ag4Cu3',
    'Sample000025_B001_Au2Ag6Cu2', 'Sample000026_B001_Au1Ag7Cu2', 'Sample000027_B001_Ag8Cu2',
    'Sample000028_B001_Au7Cu3', 'Sample000029_B001_Au6Ag1Cu3', 'Sample000030_B001_Au4Ag2Cu4',
    'Sample000031_B001_Au10', 'Sample000032_B001_Au2Ag4Cu4', 'Sample000033_B001_Au1Ag6Cu3',
    'Sample000034_B001_Ag7Cu3', 'Sample000035_B001_Au6Cu4', 'Sample000036_B001_Au4Ag1Cu5',
    'Sample000037_B001_Au3Ag2Cu5', 'Sample000038_B001_Au2Ag3Cu5', 'Sample000039_B001_Au1Ag4Cu5',
    'Sample000040_B001_Ag6Cu4', 'Sample000041_B001_Au4Cu6', 'Sample000042_B001_Au3Ag1Cu6',
    'Sample000043_B001_Au2Ag2Cu6', 'Sample000044_B001_Au1Ag3Cu6', 'Sample000045_B001_Ag4Cu6',
    'Sample000046_B001_Au3Cu7', 'Sample000047_B001_Au2Ag1Cu7', 'Sample000048_B001_Au1Ag2Cu7',
    'Sample000049_B001_Ag3Cu7', 'Sample000050_B001_Au2Cu8', 'Sample000051_B001_Au1Ag1Cu8',
    'Sample000052_B001_Ag2Cu8', 'Sample000053_B001_Au1Cu9', 'Sample000054_B001_Ag1Cu9',
    'Sample000055_B001_Cu10',
]
STATE55 = 'AfterScreening'          # name suffix: this piece (the square one is as prepared)
KR55 = [(k, r) for k in range(10) for r in range(k, 10)]       # (column, row) of spot n = index + 1

# Blue dot (pixel x, y) of each spot on B001_AuAgCu55_AfterScreening_OpticalImage_mark_position.png
# (1536 x 1152).  20 has no dot (the spot is not visible): its pixel is the lattice estimate.
PIX55 = {
    1: (1371, 784), 2: (1317, 721), 3: (1279, 658), 4: (1232, 591), 5: (1169, 520),
    6: (1124, 441), 7: (1075, 364), 8: (1016, 308), 9: (962, 245), 10: (900, 166),
    11: (1242, 766), 12: (1200, 709), 13: (1147, 655), 14: (1095, 579), 15: (1034, 502),
    16: (986, 432), 17: (940, 361), 18: (881, 303), 19: (833, 236), 20: (1121, 771),
    21: (1069, 711), 22: (1019, 627), 23: (965, 575), 24: (919, 502), 25: (866, 421),
    26: (808, 360), 27: (760, 286), 28: (986, 755), 29: (949, 696), 30: (895, 632),
    31: (841, 556), 32: (794, 499), 33: (724, 421), 34: (677, 356), 35: (870, 755),
    36: (811, 694), 37: (751, 612), 38: (698, 545), 39: (650, 492), 40: (594, 408),
    41: (724, 734), 42: (693, 669), 43: (641, 615), 44: (577, 530), 45: (516, 468),
    46: (610, 729), 47: (551, 669), 48: (493, 600), 49: (442, 534), 50: (472, 718),
    51: (432, 654), 52: (373, 574), 53: (328, 700), 54: (293, 636), 55: (223, 707),
}

# EDIT: spots centered by hand on the on-axis camera, spot: (Huber sy mm, piezo x um, piezo y um),
# Huber sx = SX55, or (sy, x, y, sx) at another Huber sx.  Used as they are; all other spots come
# from the affine fit through them.
MEASURED55 = {
    35: (7, -7600, 12300), 36: (2.4, -12800, 12300), 29: (2.4, -2300, 12300),
    30: (-2.2, -6700, 12300), 31: (-8, -11100, 12300), 23: (-7, -1400, 12300),
    24: (-12.6, -5400, 12300), 25: (-18, -9300, 12300), 16: (-17.8, 200, 12300),
    17: (-23.2, -4400, 12300), 18: (-27.4, -8300, 12300), 8: (-27.4, 1500, 12300),
    9: (-30, -2500, 10500), 10: (-30, -7600, 4700),
    # checked with mov_sam(n, HOLDER55) on 10-20: sy corrected, x as it was
    7: (-22.87, 6313, 12300), 49: (-9.15, -41263, 12300), 3: (-1.08, 22734, 12300),
    54: (-0.55, -52269, 12300),
    2: (3.363, 26318, 12300), 28: (8, 1470, 12300),
    1: (8.4, 30576, 12300),     # sy 8.4 given as "S2" (read as S1: S2 + one row step = 8.48); x predicted
}
# EDIT: bare carbon paper as blanks (the paper diffracts), measured with the array row given;
# name: (Huber sy mm, piezo x um, piezo y um, row = 0 bottom (Ag 0) .. 9 top (spot 10))
BLANKS55 = {
    'carbon_paper_after_reaction': (-11.47, 26006, 12300, 4),     # right of spot 5 (row 5, 15 .. 45)
}
SX55 = 0.0                  # Huber sx (mm) for the whole array
PY0 = 12300                 # piezo y (um) while the Huber sy can do the vertical
LIM55 = {'sy': (-30, 20), 'x': (-47000, 47000), 'y': (-9310, 12400)}    # travel (Huber mm, piezo um),
                                                                        # with the motors' own
MARGIN55 = 100              # piezo x, y (um) kept from their travel when choosing the Huber sx, sy
SXDIR55 = 1                 # +1: Huber sx +1 mm moves a spot as piezo x +1000 um (check, U2); -1: opposite

CROSS55 = tuple((d, 0) for d in (-900, -600, -300, 0, 300, 600, 900)) + \
          tuple((0, d) for d in (-900, -600, -300, 300, 600, 900))  # 13 spots (piezo x, y um)

TRANS55 = dict(
    t=1,                    # exposure (s)
    arcs=(0, 20, 40),       # WAXS at every arc; SAXS (2M) with the highest
    saxs='max',
    offsets=CROSS55,
    md={'holder': 'UPenn B001 Au-Ag-Cu array, red frame (Huber + piezo)',
        'batch': 'B001_AuAgCu_55', 'piece': 'after N2 / CO2RR screening'},
)


def holder55_positions(measured=None, pix=None, lattice_bottom=True, label='holder55'):
    """
    {spot: {'x': piezo x um, 'v': height sy + (y - PY0) / 1000 mm, 'source'}}:
      'measured'  as in measured (default MEASURED55)
      'photo'     from its pixel on the marked image (pix, default PIX55), by an affine fit
                  marked-image pixel -> stage through the measured
      'lattice'   (lattice_bottom) bottom row (Ag = 0, the Au-Cu edge): these spots are faint on the
                  photo and their dots are guesses (28's was 1.4 mm off), so one lattice step (fitted
                  through the measured spots) from its neighbours in the next row
    """
    measured = MEASURED55 if measured is None else measured
    pix = PIX55 if pix is None else pix
    keys = sorted(measured)
    S = np.array([_xv55(*measured[n]) for n in keys])
    dots = [i for i, n in enumerate(keys)
            if not lattice_bottom or KR55[n - 1][0] != KR55[n - 1][1]]       # not the bottom row
    A = np.array([[*pix[keys[i]], 1.0] for i in dots])
    sv = np.linalg.svd(A[:, :2] - A[:, :2].mean(axis=0), compute_uv=False)
    if len(dots) < 3 or sv[1] < 0.1 * sv[0]:
        raise ValueError(f'{label}: center >= 3 spots far apart, not in a line '
                         f'(have {[keys[i] for i in dots]})')
    coef = np.linalg.lstsq(A, S[dots], rcond=None)[0]
    res = np.linalg.norm(S[dots] - A @ coef, axis=1)
    step = np.linalg.lstsq(np.array([[*KR55[n - 1], 1.0] for n in keys]), S, rcond=None)[0][:2]
    print(f'{label}: photo fit through {len(dots)} measured spots, residual rms '
          f'{np.sqrt(np.mean(res ** 2)):.2f} mm, max {res.max():.2f} mm (spot {keys[dots[res.argmax()]]}); '
          f'lattice step column {np.linalg.norm(step[0]):.2f} mm, row {np.linalg.norm(step[1]):.2f} mm')
    spot = {kr: i + 1 for i, kr in enumerate(KR55)}
    xv, source = {}, {}
    for n in range(1, 56):
        if n in measured:
            xv[n], source[n] = S[keys.index(n)], 'measured'
        else:
            xv[n], source[n] = np.array([*pix[n], 1.0]) @ coef, 'photo'
    for n in range(1, 56):
        k, r = KR55[n - 1]
        if lattice_bottom and r == k and n not in measured:
            near = [xv[spot[k, k + 1]] - step[1]] if k < 9 else []
            near += [xv[spot[k - 1, k]] + step[0]] if k > 0 else []
            xv[n], source[n] = np.mean(near, axis=0), 'lattice'
    return {n: dict(x=float(X) * 1000, v=float(V), source=source[n]) for n, (X, V) in xv.items()}


def _xv55(sy, x, y, sx=None):
    """(X, V) in mm of a hand-centered position: X = piezo x at Huber sx = SX55, V = height."""
    sx = SX55 if sx is None else sx
    return (x + SXDIR55 * (sx - SX55) * 1000) / 1000, sy + (y - PY0) / 1000


def _X55(s):
    """Piezo x (um) of a HOLDER55 spot as if at Huber sx = SX55 (comparable between spots)."""
    return s['x'] + SXDIR55 * (s['sx'] - SX55) * 1000


def holder55_samples(measured=None, pix=None, blanks=None, state=STATE55, offsets=CROSS55,
                     lattice_bottom=True, label='holder55', bands=False, start_sy=None, sx0=None,
                     lim=None):
    """
    The 55 spots and the blanks (default MEASURED55, PIX55, BLANKS55: the piece after screening), row
    by row of the array (row = Ag level, bottom row first) in a serpentine: S1 -> S55, S54 -> S2,
    S3 -> S52, ...  The spots of a row share one Huber sy and the piezo y takes the spot-to-spot
    height, so the Huber moves once per row.  sy is the row mean, shifted as little as needed to keep
    the piezo y of every cross (offsets) inside its travel.  Spots whose cross does not fit the piezo
    x travel get the Huber sx shifted by whole mm (one shift for all of them on each side) and the
    piezo x shifted back.  bands=True: as the 384-well plates instead (band_order: the rows from the
    top in as few Huber sy bands as the piezo y covers, the first nearest start_sy).  sx0: the Huber
    sx of the piece (default SX55; the blanks are measured there too); lim: travel (default LIM55).
    """
    blanks = BLANKS55 if blanks is None else blanks
    sx0 = SX55 if sx0 is None else sx0
    dX = SXDIR55 * (sx0 - SX55) * 1000          # um: piezo x at Huber sx0 = X - dX
    spots = []
    for n, p in holder55_positions(measured, pix, lattice_bottom, label).items():
        k, r = KR55[n - 1]
        spots.append(dict(key=n, name=clean_name(f'{PYCLEAR55[n - 1]}_{state}'), x=p['x'], v=p['v'],
                          array_row=r - k, sample_id=PYCLEAR55[n - 1].split('_')[0],
                          target_id=1 + 14 * k + r, pipetmax_col=k, pipetmax_row=r,
                          position=p['source']))
    for name, (sy, x, y, row) in blanks.items():
        spots.append(dict(key=name, name=clean_name(name), x=float(x) + dX, v=sy + (y - PY0) / 1000,
                          array_row=row, role='blank', position='measured'))
    for s in spots:
        s['x'] -= dX                            # piezo x at Huber sx0
    x_lo, x_hi = _travel('x', lim)
    dx_lo, dx_hi = min(dx for dx, _ in offsets), max(dx for dx, _ in offsets)
    left = lambda X: X + dx_lo < x_lo + MARGIN55
    right = lambda X: X + dx_hi > x_hi - MARGIN55
    xs = [s['x'] for s in spots]
    shift_l = np.ceil(max(x_lo + MARGIN55 - dx_lo - min(xs), 0) / 1000)     # mm, piezo x + shift
    shift_r = np.ceil(max(max(xs) + dx_hi - x_hi + MARGIN55, 0) / 1000)     # mm, piezo x - shift
    if bands:
        for s in spots:
            X = s['x']
            d = shift_l if left(X) else -shift_r if right(X) else 0
            s.update(sx=float(sx0 - SXDIR55 * d), x=round(X + d * 1000))
        samples = band_order(spots, offsets, lambda s: s['array_row'], _X55, lim, start_sy)
        check_samples(samples)
        return samples
    samples = []
    for row in sorted({s['array_row'] for s in spots}):
        cells = sorted((s for s in spots if s['array_row'] == row), key=lambda s: s['x'],
                       reverse=row % 2 == 0)
        sy = _row_sy([s['v'] for s in cells], offsets)
        for s in cells:
            v, X = s.pop('v'), s['x']
            d = shift_l if left(X) else -shift_r if right(X) else 0
            s.update(sx=float(sx0 - SXDIR55 * d), sy=sy, x=round(X + d * 1000), y=round(PY0 + (v - sy) * 1000))
            samples.append(s)
    check_samples(samples)
    return samples


def _row_sy(vs, offsets=CROSS55):
    """Huber sy (mm) of a row of spots at heights vs (mm): their mean, shifted as little as needed to
    keep the piezo y of every spot + offset inside its travel."""
    y_lo, y_hi = _travel('y')
    sy_lo = max(vs) + (PY0 + max(dy for _, dy in offsets) - y_hi + MARGIN55) / 1000
    sy_hi = min(vs) + (PY0 + min(dy for _, dy in offsets) - y_lo - MARGIN55) / 1000
    return round(min(max(np.mean(vs), sy_lo, _travel('sy')[0]), sy_hi, _travel('sy')[1]), 2)


def _travel(axis, lim=None):
    """(low, high) of an axis: lim (default LIM55) and the motor's own soft limits, where set."""
    lo, hi = (LIM55 if lim is None else lim).get(axis, (-np.inf, np.inf))
    try:
        mlo, mhi = AXES[axis].limits
        if mlo < mhi:
            lo, hi = max(lo, mlo), min(hi, mhi)
    except Exception:
        pass
    return lo, hi


def check_holder55(samples=None, offsets=CROSS55, lim=None):
    """Raise (before anything moves) if a spot of a cross is out of travel (lim, default LIM55)."""
    bad = []
    for s in (HOLDER55 if samples is None else samples):
        for dx, dy in offsets:
            for a, v in (('sx', s['sx']), ('sy', s['sy']), ('x', s['x'] + dx), ('y', s['y'] + dy)):
                lo, hi = _travel(a, lim)
                if not lo <= v <= hi:
                    bad.append(f"{s['key']} {a}={v:g} not in [{lo:g}, {hi:g}]")
    if bad:
        raise ValueError('out of travel: ' + '; '.join(sorted(set(bad))[:10]))


def _ova_first_arc(sample, i_arc):
    if i_arc == 0:
        yield from ova_snap(sample)


def run_holder_55after(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the B001 array after screening (the 55 spots and BLANKS55, or the
    given red labels / names, or the array rows given, 0 = bottom), row by row in the order of
    HOLDER55: the Huber moves once per row (and where the Huber sx changes within it), then every arc
    of TRANS55 over the row -- a 13-point cross (CROSS55) per spot, WAXS at every arc with SAXS at the
    highest, and (ova=True) one on-axis camera image per spot on the first arc.  Each row starts at
    the end, and at the arc, where the previous one stopped.  kw override TRANS55.
    """
    samples = _select55(HOLDER55, which, rows)
    opts = dict(TRANS55, **kw)
    check_arcs(opts['arcs'])
    check_holder55(samples, opts['offsets'])
    return _rows55(samples, ova, opts)


def _select55(holder, which, rows):
    """The spots of holder given by red label / name (which) and array row (rows), or all."""
    samples = select(holder, *which) if which else holder
    if rows is not None:
        samples = [s for s in samples if s['array_row'] in rows]
        if not samples:
            raise ValueError(f'no spots in rows {rows}')
    return samples


def _rows55(samples, ova, opts, label='run_holder_55after', row_key='array_row'):
    """Plan: samples (sx, sy, x, y) row by row (row_key): the Huber moves once per row and part of a
    row (_parts55), then every arc over the part; each part starts at the end, and at the arc, where
    the previous one stopped."""
    arcs = list(opts.pop('arcs'))
    rows = {}
    for s in samples:
        rows.setdefault(s[row_key], []).append(s)
    saxs_arcs = _saxs_arcs(arcs, opts.get('saxs', 'max'))
    n_arcs = sum(1 for a in arcs if _dets(a, saxs_arcs, opts.get('waxs_det', True)))
    n_parts = sum(len(_parts55(row)) for row in rows.values())
    _announce(f'{label}, {len(rows)} rows, {n_parts} Huber positions',
              n_arcs * len(samples) * len(opts['offsets']), opts.get('t', 1))
    last_X = last_arc = None
    for row in rows.values():
        if last_X is not None and abs(_X55(row[-1]) - last_X) < abs(_X55(row[0]) - last_X):
            row = row[::-1]
        for part in _parts55(row):
            if last_arc is not None and abs(arcs[-1] - last_arc) < abs(arcs[0] - last_arc):
                arcs = arcs[::-1]
            yield from _huber_to(part[0])
            piezo_only = [{k: v for k, v in s.items() if k not in ('sx', 'sy')} for s in part]
            yield from run_trans(piezo_only, arcs=arcs, at_sample=_ova_first_arc if ova else None, **opts)
            last_arc = yield from bps.rd(_arc_rb())
        last_X = _X55({'x': (yield from bps.rd(AXES['x'])), 'sx': (yield from bps.rd(AXES['sx']))})


def _parts55(row):
    """The row split where the Huber sx changes."""
    parts = []
    for s in row:
        if parts and parts[-1][-1]['sx'] == s['sx']:
            parts[-1].append(s)
        else:
            parts.append([s])
    return parts


def _holder55_summary(label, H, offsets=CROSS55, sx0=SX55):
    xs = [s['x'] + dx for s in H for dx, _ in offsets]
    ys = [s['y'] + dy for s in H for _, dy in offsets]
    print(f'{label}: {len(H)} spots in {len({s["array_row"] for s in H})} rows, Huber sy per '
          f'row {", ".join(f"{sy:g}" for sy in dict.fromkeys(s["sy"] for s in H))} mm; '
          f'piezo x {min(xs):.0f}..{max(xs):.0f} um, y {min(ys):.0f}..{max(ys):.0f} um (crosses included)')
    for sx in sorted({s['sx'] for s in H} - {sx0}):
        print(f'  Huber sx {sx:g} mm (not {sx0:g}) for spots '
              f'{", ".join(str(s["key"]) for s in H if s["sx"] == sx)} -- SXDIR55 = {SXDIR55} checked?')


HOLDER55 = holder55_samples()
_holder55_summary('HOLDER55', HOLDER55)


###############################################################################################
# ORNL (C. Liu) powders, Box 1: a Corning 384-well plate (glass bottom, Kapton over the wells)
###############################################################################################
PLATE_ROWS = 'ABCDEFGHIJKLMNOP'     # 384-well plate: rows A (bottom on the photo) .. P, columns 1 .. 24
PLATE_PITCH = 4.5                   # mm, well to well (only to check the calibration)

# well -> pyCLEAR sample name (pyCLEAR records: B005 Cu-M library, B006 SO2 study, B007 CeO2), from
# "Sample Information to BNL Oct 2026_CLiu_ORNL.xlsx" with the wells C. Liu confirmed on the Box 1
# photo (87, Cu(OH)2, is in M18, not M16).  Box 2 holds the same samples as suspensions.
CLIU_BOX1 = {
    'A2': 'Sample000226_B005_Cu9Co1', 'A4': 'Sample000227_B005_Cu8Co2',
    'A6': 'Sample000228_B005_Cu7Co3', 'A8': 'Sample000229_B005_Cu6Co4',
    'A10': 'Sample000230_B005_Cu5Co5', 'A12': 'Sample000231_B005_Cu4Co6',
    'A14': 'Sample000232_B005_Cu3Co7', 'A16': 'Sample000233_B005_Cu2Co8',
    'A18': 'Sample000234_B005_Cu1Co9', 'A20': 'Sample000235_B005_Co10',
    'A22': 'Sample000236_B005_Cu9Ni1', 'A24': 'Sample000237_B005_Cu8Ni2',
    'C2': 'Sample000238_B005_Cu7Ni3', 'C4': 'Sample000239_B005_Cu6Ni4',
    'C6': 'Sample000240_B005_Cu5Ni5', 'C8': 'Sample000241_B005_Cu4Ni6',
    'C10': 'Sample000242_B005_Cu3Ni7', 'C12': 'Sample000243_B005_Cu2Ni8',
    'C14': 'Sample000244_B005_Cu1Ni9', 'C16': 'Sample000245_B005_Ni10',
    'C18': 'Sample000246_B005_Cu9Zn1', 'C20': 'Sample000247_B005_Cu8Zn2',
    'C22': 'Sample000248_B005_Cu7Zn3', 'C24': 'Sample000249_B005_Cu6Zn4',
    'E2': 'Sample000250_B005_Cu5Zn5', 'E4': 'Sample000251_B005_Cu4Zn6',
    'E6': 'Sample000252_B005_Cu3Zn7', 'E8': 'Sample000253_B005_Cu2Zn8',
    'E10': 'Sample000254_B005_Cu1Zn9', 'E12': 'Sample000255_B005_Zn10',
    'E14': 'Sample000256_B005_Cu9Fe1', 'E16': 'Sample000257_B005_Cu8Fe2',
    'E18': 'Sample000258_B005_Cu7Fe3', 'E20': 'Sample000262_B005_Cu8Cr2',
    'E22': 'Sample000263_B005_Cu7Cr3', 'E24': 'Sample000264_B005_Cu6Cr4',
    'G2': 'Sample000266_B005_Cu9Mn1', 'G4': 'Sample000267_B005_Cu8Mn2',
    'G6': 'Sample000268_B005_Cu7Mn3', 'G8': 'Sample000269_B005_Cu6Mn4',
    'G10': 'Sample000270_B005_Cu5Mn5', 'G12': 'Sample000271_B005_Cu4Mn6',
    'G14': 'Sample000272_B005_Cu3Mn7', 'G18': 'Sample000273_B005_Cu2Mn8',
    'G20': 'Sample000274_B005_Cu1Mn9', 'G22': 'Sample000275_B005_Mn10',
    'G24': 'Sample000276_B005_Cu9Bi1', 'I2': 'Sample000277_B005_Cu8Bi2',
    'I4': 'Sample000278_B005_Cu7Bi3', 'I6': 'Sample000279_B005_Cu6Bi4',
    'I8': 'Sample000280_B005_Cu5Bi5', 'I10': 'Sample000281_B005_Cu4Bi6',
    'I12': 'Sample000282_B005_Cu3Bi7', 'I14': 'Sample000283_B005_Cu2Bi8',
    'I18': 'Sample000284_B005_Cu1Bi9', 'I20': 'Sample000286_B005_Cu9Sn1',
    'I22': 'Sample000287_B005_Cu8Sn2', 'I24': 'Sample000288_B005_Cu7Sn3',
    'K2': 'Sample000289_B005_Cu6Sn4', 'K4': 'Sample000290_B005_Cu5Sn5',
    'K6': 'Sample000291_B005_Cu4Sn6', 'K8': 'Sample000292_B005_Cu3Sn7',
    'K10': 'Sample000296_B005_Cu9Ag1', 'K12': 'Sample000297_B005_Cu8Ag2',
    'K14': 'Sample000298_B005_Cu7Ag3', 'K16': 'Sample000299_B005_Cu6Ag4',
    'K18': 'Sample000300_B005_Cu5Ag5', 'K20': 'Sample000301_B005_Cu4Ag6',
    'K22': 'Sample000302_B005_Cu3Ag7', 'K24': 'Sample000303_B005_Cu2Ag8',
    'M2': 'Sample000304_B005_Cu1Ag9', 'M4': 'Sample000305_B005_Ag10',
    'M6': 'Sample000306_B006_CuOH2-CP-EC-SO2', 'M8': 'Sample000307_B006_Ag-CuOH2-CP-EC-SO2',
    'M10': 'Sample000308_B006_CuOH2-CP-EC-noSO2', 'M12': 'Sample000309_B006_Ag-CuOH2-CP-EC-noSO2',
    'M14': 'Sample000310_B006_CP', 'M18': 'Sample000311_B006_CuOH2', 'P1': 'Sample000312_B007_CeO2',
    'P3': 'Sample000313_B007_CeO2-N2H4', 'P8': 'Sample000314_B007_CeO2Fe6Ni24',
    'P10': 'Sample000315_B007_CeO2Fe6Ni24-N2H4', 'P12': 'Sample000316_B007_CeO2Fe12Ni12',
    'P14': 'Sample000317_B007_CeO2Fe12Ni12-N2H4', 'P16': 'Sample000318_B007_CeO2Fe18Ni6',
    'P20': 'Sample000319_B007_CeO2Fe18Ni6-N2H4',
}
CLIU_SKIP = ('M6', 'M8', 'M10', 'M12', 'M14')   # B006 "bad sample: grey powder" (C. Liu, 2026-10-20)
CLIU_BLANKS = {'A1': 'EmptyWell_A1', 'P24': 'EmptyWell_P24'}  # glass + Kapton, in rows measured anyway
CLIU_PREFIX = 'CL'                  # sample names CL_<pyCLEAR name>_Powder
CLIU_FORM = 'Powder'                # name suffix: the Box 2 suspensions share the Sample IDs
CLIU_LATER = 'P'                    # rows out of reach (top reachable: N) -> after pushing the plate down

# Wells centered by hand on the on-axis camera, well: (Huber sx mm, Huber sy mm, piezo x um, piezo y um)
# = here('sx', 'sy', 'x', 'y').  Any 3+ wells that span the plate; more refine the fit.
CAL_CLIU = {                        # 2026-10-20 evening, corners (N: the top row in reach)
    'A1': (-2, 10.8, -56500, 12300), 'A24': (-2, 10.8, 46800, 10800),
    'N1': (-2, -30, -57303, -5634), 'N24': (-2, -30, 45800, -7034),
}
# EDIT after pushing the plate down: P1 and P24 centered by hand, here('sx', 'sy', 'x', 'y')
CAL_CLIU_P = {                      # 2026-10-20 night, after pushing the plate down
    'P1': (-2.5, -30, -56323, -4914), 'P24': (-2.5, -30, 46800, -5714),
}

SX_CLIU = -2.5                      # Huber sx (mm) for the whole plate: columns 1 .. 24 on the piezo x
LIM_CLIU = dict(LIM55, x=(-57300, 48500))   # piezo x for the plates (um): -57303 reached (Box 1 N1), 48400
                                            # (Box 2 N24, 10-21); at sx -3 Box 1 column 24 hit the limit
CROSS_CLIU = ((0, 0), (0, -500), (0, 500))  # 3 spots per well (piezo x, y um): centre, then y -500, 500

TRANS_CLIU = dict(
    t=1,                    # exposure (s)
    arcs=(0, 20, 40),       # one arc at a time over all wells; SAXS (2M) with the highest
    saxs='max',
    offsets=CROSS_CLIU,
    md={'holder': 'ORNL Box 1, Corning 384-well plate, glass bottom, Kapton (Huber + piezo)',
        'batch': 'B005_CuM_81, B006_CuAg_6, B007_CeFeNi_8', 'form': 'powder'},
)

# Huber y motor temperature: the Huber y never starts a move above HUBER_T_MAX
HUBER_T_MAX = 48.0          # degC
HUBER_T_OK = 45.0           # degC: when too hot, wait until it is back below this
HUBER_T_WAIT = 60           # s between readings while waiting
HUBER_Y_STEP = 5.0          # mm: longer Huber y moves go in steps, the temperature read before each
if 'huber_y_T' not in globals():
    huber_y_T = EpicsSignalRO('XF:12ID:m65.VAL', name='huber_y_T')


def huber_y_mv(target):
    """
    Plan: Huber sy to target in steps of at most HUBER_Y_STEP mm.  Before every step the motor
    temperature (huber_y_T) is read; above HUBER_T_MAX the Huber waits, reading every HUBER_T_WAIT s,
    until it is below HUBER_T_OK.  (A move is not stopped half way: the RunEngine would abort the run.)
    """
    here = yield from bps.rd(AXES['sy'])
    n = int(np.ceil(abs(target - here) / HUBER_Y_STEP - 1e-9))
    for k in range(1, n + 1):
        T = yield from bps.rd(huber_y_T)
        if T > HUBER_T_MAX:
            print(f'Huber y motor {T:.1f} C > {HUBER_T_MAX:g} C: waiting until below {HUBER_T_OK:g} C')
            while T > HUBER_T_OK and not _LOG.get('preview'):   # a dry run does not wait
                yield from bps.sleep(HUBER_T_WAIT)
                T = yield from bps.rd(huber_y_T)
                print(f'  Huber y motor {T:.1f} C')
        yield from bps.mv(AXES['sy'], target if k == n else here + (target - here) * k / n)
    if n:
        T = yield from bps.rd(huber_y_T)
        print(f'Huber sy -> {target:g} mm (motor {T:.1f} C)')


def _huber_to(s):
    """Plan: Huber sx, sy of a sample (sy through huber_y_mv)."""
    if abs((yield from bps.rd(AXES['sx'])) - s['sx']) > 1e-3:
        yield from bps.mv(AXES['sx'], s['sx'])
    if abs((yield from bps.rd(AXES['sy'])) - s['sy']) > 1e-3:
        yield from huber_y_mv(s['sy'])


def _well(w):
    """'A2' -> (row, column) indices from 0."""
    return PLATE_ROWS.index(w[0].upper()), int(w[1:]) - 1


def plate_positions(wells, cal):
    """
    {well: (X, V) mm} of a 384-well plate on the Huber + piezo (X = piezo x at Huber sx = SX55, V =
    height as in holder55_positions), from the wells centered by hand, cal {well: (sx, sy, x, y)}:
    bilinear in (row, column) through 4+ wells (exact through four corners), affine through 3,
    linear along the row through 2 wells of one row (then only that row).
    """
    keys = list(cal)
    rc = np.array([_well(w) for w in keys], float)
    S = np.array([_xv55(sy, x, y, sx) for sx, sy, x, y in (cal[w] for w in keys)])
    one_row = len({r for r, _ in rc}) == 1
    if one_row and {_well(w)[0] for w in wells} != {rc[0, 0]}:
        raise ValueError(f'calibration {keys} is one row: only its wells can be mapped')

    def design(rc):
        cols = [np.ones(len(rc)), rc[:, 1]] if one_row else [np.ones(len(rc)), rc[:, 0], rc[:, 1]]
        return np.column_stack(cols + [rc[:, 0] * rc[:, 1]] if len(keys) >= 4 and not one_row else cols)

    coef, _, rank, _ = np.linalg.lstsq(design(rc), S, rcond=None)
    if rank < design(rc).shape[1]:
        print(f'plate: wells {keys} do not span the plate -- use corners')
    res = np.linalg.norm(S - design(rc) @ coef, axis=1)
    r0 = rc[0, 0] if one_row else 7.5
    mid = design(np.array([[r0, 11.5]]))
    step_c = ((design(np.array([[r0, 12.5]])) - mid) @ coef)[0]     # mm per column (and per row)
    pitch = [np.linalg.norm(step_c)]
    if not one_row:
        pitch.insert(0, np.linalg.norm(((design(np.array([[8.5, 11.5]])) - mid) @ coef)[0]))
    print(f'plate: fit through {len(keys)} wells (residual max {res.max():.2f} mm); pitch '
          f'{" (row), ".join(f"{p:.2f}" for p in pitch)} (column) mm; rows tilted '
          f'{np.degrees(np.arctan2(step_c[1], abs(step_c[0]))):.2f} deg')
    if max(abs(p - PLATE_PITCH) for p in pitch) > 0.1 * PLATE_PITCH:
        print(f'WARNING: pitch is not {PLATE_PITCH} mm -- check the wells in the calibration')
    return {w: tuple(design(np.array([_well(w)], float))[0] @ coef) for w in wells}


def band_order(cells, offsets, row_of, along, lim=None, start_sy=None):
    """
    cells (dicts with Huber 'sx', piezo 'x' and 'v' = height in mm) with Huber 'sy' and piezo 'y'
    set, in the order for few Huber moves.  Huber y: the rows (row_of, larger = higher), from the top,
    in as few bands as the piezo y travel covers -- one Huber sy per band, the piezo y takes the rows
    within it; each band's sy is the one nearest the previous band's (the first: nearest start_sy,
    default the top row's height).  Huber x: within a band the cells of each Huber sx together, the
    Huber sx groups (left to right) in a serpentine over the bands, so the Huber sx moves once per
    group; within a group row by row, each row (along) in a serpentine.  lim: travel table.
    """
    y_lo, y_hi = _travel('y', lim)
    sy_min, sy_max = _travel('sy', lim)
    dy_lo, dy_hi = min(dy for _, dy in offsets), max(dy for _, dy in offsets)
    y_min, y_max = y_lo + MARGIN55 - dy_lo, y_hi - MARGIN55 - dy_hi        # um, for the cell centers
    # sy window of a band: every piezo y in [y_min, y_max]
    window = lambda vs: (max(max(vs) - (y_max - PY0) / 1000, sy_min), min(min(vs) - (y_min - PY0) / 1000, sy_max))
    rows = sorted({row_of(c) for c in cells}, reverse=True)
    bands = []
    for r in rows:
        vs = [c['v'] for c in cells if row_of(c) in (bands[-1] if bands else []) + [r]]
        lo, hi = window(vs)
        if bands and hi - lo >= 0.02:
            bands[-1].append(r)
        else:
            bands.append([r])
    if start_sy is None:
        start_sy = np.mean([c['v'] for c in cells if row_of(c) == rows[0]])
    groups = sorted({c['sx'] for c in cells}, key=lambda hx: np.mean([_X55(c) for c in cells if c['sx'] == hx]))
    samples, prev = [], start_sy
    for i, band in enumerate(bands):
        lo, hi = window([c['v'] for c in cells if row_of(c) in band])
        sy = float(np.ceil(lo * 100) / 100 if prev < lo else np.floor(hi * 100) / 100 if prev > hi else prev)
        prev = sy
        for j, hx in enumerate(groups if i % 2 == 0 else groups[::-1]):
            for k, r in enumerate(band):
                for c in sorted((c for c in cells if row_of(c) == r and c['sx'] == hx), key=along,
                                reverse=(i + j + k) % 2 == 1):
                    c['sy'], c['y'] = sy, round(PY0 + (c.pop('v') - sy) * 1000)
                    samples.append(c)
    return samples


def plate_samples(names, cal, offsets, extra=None, start_sy=None, sx=None, lim=None, label='plate'):
    """
    The wells names {well: sample name} of a 384-well plate (plate_positions), ordered for few Huber
    moves (band_order).  Huber y: the rows from the top in bands, the first band's sy nearest
    start_sy (default the calibration's sy nearest the top row).  Huber x: the columns in as few
    blocks as the piezo x travel covers, each at one Huber sx (in whole mm from the calibration's
    sx), or all at Huber sx = sx.  Wells out of reach of the Huber sy + piezo y travel are left out
    (printed: push the plate).  extra: {well: metadata}; lim: travel table (default LIM55).
    """
    extra = extra or {}
    pos = plate_positions(list(names), cal)
    x_lo, x_hi = _travel('x', lim)
    y_lo, y_hi = _travel('y', lim)
    sy_min, sy_max = _travel('sy', lim)
    dx_lo, dx_hi = min(dx for dx, _ in offsets), max(dx for dx, _ in offsets)
    dy_lo, dy_hi = min(dy for _, dy in offsets), max(dy for _, dy in offsets)
    x_min, x_max = x_lo + MARGIN55 - dx_lo, x_hi - MARGIN55 - dx_hi      # um, for the well centers
    v_min = sy_min + (y_lo + MARGIN55 - dy_lo - PY0) / 1000               # mm, heights in reach
    v_max = sy_max + (y_hi - MARGIN55 - dy_hi - PY0) / 1000
    out = [w for w in names if not v_min <= pos[w][1] <= v_max]
    if out:
        print(f'{label}: out of reach of the Huber sy + piezo y (height {v_min:.1f} .. {v_max:.1f} mm), '
              f'left out: {", ".join(out)}')
        names = {w: n for w, n in names.items() if w not in out}
    # Huber sx: column blocks
    sx0 = float(np.median([c[0] for c in cal.values()]))
    x0 = {w: pos[w][0] * 1000 - SXDIR55 * (sx0 - SX55) * 1000 for w in names}  # piezo x at sx0
    cols = sorted({_well(w)[1] for w in names})
    col_x = {c: np.mean([x0[w] for w in names if _well(w)[1] == c]) for c in cols}
    span = max(col_x.values()) - min(col_x.values())
    n_blocks = max(1, int(np.ceil(span / (x_max - x_min - 3000))))      # 3 mm for tilt and rounding
    edges = np.linspace(min(col_x.values()), max(col_x.values()), n_blocks + 1)[1:-1]
    block = {w: int(np.searchsorted(edges, col_x[_well(w)[1]])) for w in names}
    hx_of = {}
    for b in set(block.values()):
        x = [x0[w] for w in names if block[w] == b]
        d_lo, d_hi = (max(x) - x_max) / 1000, (min(x) - x_min) / 1000      # mm the piezo x gives back
        hx_of[b] = float(sx0 + SXDIR55 * (np.ceil(d_lo) if d_lo > 0 else np.floor(d_hi) if d_hi < 0 else 0))
    if sx is not None:
        block, hx_of = {w: 0 for w in names}, {0: float(sx)}
    if start_sy is None:
        top_row = max(_well(w)[0] for w in names)
        top = max(cal, key=lambda w: (-abs(_well(w)[0] - top_row), _well(w)[1]))
        start_sy = cal[top][1]
    cells = []
    for w in names:
        X, V = pos[w]
        hx = hx_of[block[w]]
        cells.append(dict(key=w, name=clean_name(names[w]), well=w, plate_row=w[0].upper(),
                          plate_col=_well(w)[1] + 1, sx=hx, x=round(X * 1000 - SXDIR55 * (hx - SX55) * 1000),
                          v=V, **extra.get(w, {})))
    samples = band_order(cells, offsets, lambda s: _well(s['well'])[0], lambda s: s['plate_col'],
                         lim, start_sy)
    check_samples(samples)
    return samples


def _cliu_names(wells):
    """({well: CL_<name>_Powder or blank name}, {well: metadata}) of the Box 1 wells given."""
    names, extra = {}, {}
    for w in wells:
        if w in CLIU_BLANKS:
            names[w] = f'{CLIU_PREFIX}_{CLIU_BLANKS[w]}'
            extra[w] = dict(role='blank', form='empty well', box='box1')
        else:
            n = CLIU_BOX1[w]
            names[w] = f'{CLIU_PREFIX}_{n}_{CLIU_FORM}'
            extra[w] = dict(sample_id=n.split('_')[0], batch=n.split('_')[1], form='powder', box='box1')
    return names, extra


def cliu_box1_samples(cal=None):
    """Box 1 wells (CLIU_BOX1 without CLIU_SKIP, + CLIU_BLANKS) except the CLIU_LATER rows, mapped
    through CAL_CLIU ([] before it is filled)."""
    cal = CAL_CLIU if cal is None else cal
    if len(cal) < 3:
        print('CLiu Box 1: not calibrated yet (CAL_CLIU needs 3+ wells, best the four corners)')
        return []
    wells = [w for w in (*CLIU_BOX1, *CLIU_BLANKS) if w not in CLIU_SKIP and w[0] not in CLIU_LATER]
    names, extra = _cliu_names(wells)
    return plate_samples(names, cal, TRANS_CLIU['offsets'], extra, sx=SX_CLIU, lim=LIM_CLIU)


def cliu_box1_p_samples(cal=None):
    """Box 1 row P (CLIU_LATER) after pushing the plate down, mapped through CAL_CLIU_P (P1, P24)."""
    cal = CAL_CLIU_P if cal is None else cal
    if len(cal) < 2:
        print('CLiu Box 1 row P: not calibrated yet (CAL_CLIU_P: P1 and P24 after the push)')
        return []
    wells = [w for w in (*CLIU_BOX1, *CLIU_BLANKS) if w not in CLIU_SKIP and w[0] in CLIU_LATER]
    names, extra = _cliu_names(wells)
    return plate_samples(names, cal, TRANS_CLIU['offsets'], extra, sx=SX_CLIU, lim=LIM_CLIU)


def _by_arc(samples, ova, opts, label):
    """
    Plan: one WAXS arc at a time over all the samples (the arc moves len(arcs) - 1 times), visiting
    the Huber positions (sx, sy) in the order of samples and, at the next arc, in the reverse order,
    so the Huber does not move between arcs.  Huber y through huber_y_mv.  ova: one on-axis camera
    image per sample on the first arc.
    """
    arcs = list(opts.pop('arcs'))
    saxs_arcs = _saxs_arcs(arcs, opts.pop('saxs', 'max'))
    stops = []
    for s in samples:
        if stops and (stops[-1][0]['sx'], stops[-1][0]['sy']) == (s['sx'], s['sy']):
            stops[-1].append(s)
        else:
            stops.append([s])
    n_arcs = sum(1 for a in arcs if _dets(a, saxs_arcs, opts.get('waxs_det', True)))
    _announce(f'{label}: arcs {arcs} one at a time, {len(stops)} Huber positions per arc',
              n_arcs * len(samples) * len(opts['offsets']), opts.get('t', 1))
    for i, arc in enumerate(arcs):
        for stop in (stops if i % 2 == 0 else [st[::-1] for st in stops[::-1]]):
            yield from _huber_to(stop[0])
            piezo_only = [{k: v for k, v in s.items() if k not in ('sx', 'sy')} for s in stop]
            yield from run_trans(piezo_only, arcs=[arc], saxs='all' if arc in saxs_arcs else False,
                                 at_sample=_ova_first_arc if ova and i == 0 else None, **opts)


def _run_plate(plate, which, rows, ova, kw, label, trans=None):
    """Plan: _by_arc over the wells of plate given (which: wells / names, rows: e.g. 'KM'), with
    trans (default TRANS_CLIU) updated by kw; every spot checked against LIM_CLIU first."""
    samples = select(plate, *which) if which else plate
    if rows is not None:
        samples = [s for s in samples if s['plate_row'] in rows]
        if not samples:
            raise ValueError(f'no wells in rows {rows}')
    opts = dict(TRANS_CLIU if trans is None else trans, **kw)
    check_arcs(opts['arcs'])
    check_holder55(samples, opts['offsets'], LIM_CLIU)
    return _by_arc(samples, ova, opts, label)


def run_cliu_box1(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the ORNL powders in Box 1 (PLATE_CLIU: rows A .. M, or the given
    wells / names, or rows, e.g. rows='KM'): one WAXS arc at a time over all wells (TRANS_CLIU arcs,
    SAXS with the highest), 3 spots per well (CROSS_CLIU), one on-axis camera image per well
    on the first arc; Huber positions in the order of PLATE_CLIU (from the top row), reversed at the
    next arc.  kw override TRANS_CLIU.
    """
    if not PLATE_CLIU:
        raise ValueError('CLiu Box 1 not calibrated: fill CAL_CLIU and re-run this file')
    return _run_plate(PLATE_CLIU, which, rows, ova, kw, 'run_cliu_box1')


def run_cliu_box1_P(*which, ova=True, **kw):
    """Plan: as run_cliu_box1, for row P after pushing the plate down (PLATE_CLIU_P, CAL_CLIU_P)."""
    if not PLATE_CLIU_P:
        raise ValueError('row P not calibrated: fill CAL_CLIU_P (P1, P24) after the push, re-run this file')
    return _run_plate(PLATE_CLIU_P, which, None, ova, kw, 'run_cliu_box1_P')


def _plate_summary(label, plate, off=CROSS_CLIU):
    xs = [s['x'] + dx for s in plate for dx, _ in off]
    ys = [s['y'] + dy for s in plate for _, dy in off]
    stops = list(dict.fromkeys((s['sx'], s['sy']) for s in plate))
    print(f'{label}: {len(plate)} wells in rows {"".join(dict.fromkeys(s["plate_row"] for s in plate))}; '
          f'Huber (sx, sy) {", ".join(f"({a:g}, {b:g})" for a, b in stops)} mm; '
          f'piezo x {min(xs):.0f}..{max(xs):.0f} um, y {min(ys):.0f}..{max(ys):.0f} um (crosses included)')


PLATE_CLIU = cliu_box1_samples()
if PLATE_CLIU:
    _plate_summary('PLATE_CLIU', PLATE_CLIU)
PLATE_CLIU_P = cliu_box1_p_samples()
if PLATE_CLIU_P:
    _plate_summary('PLATE_CLIU_P', PLATE_CLIU_P)


###############################################################################################
# UPenn B001 Au-Ag-Cu array, the as-prepared (untested) piece: the square cutout
###############################################################################################
# The same 55 spots / pyCLEAR samples as the piece after screening (PYCLEAR55, KR55, the runners
# above); every spot is visible on this piece, so all of them are placed from the photo.
STATE55B = 'AsPrepared'             # name suffix: Sample0000nn_B001_<composition>_AsPrepared

# Centre (pixel x, y) of the red circle around each spot on
# B001_AuAgCu55_asprepared_OpticalImage_mark_position.png (1086 x 1448)
PIX55B = {
    1: (1028, 740), 2: (980, 689), 3: (929, 638), 4: (882, 588), 5: (830, 538),
    6: (779, 492), 7: (733, 448), 8: (684, 396), 9: (641, 350), 10: (593, 305),
    11: (929, 746), 12: (880, 691), 13: (827, 640), 14: (779, 589), 15: (729, 541),
    16: (679, 492), 17: (638, 447), 18: (587, 403), 19: (546, 353), 20: (833, 752),
    21: (779, 696), 22: (725, 643), 23: (674, 592), 24: (626, 544), 25: (585, 500),
    26: (537, 450), 27: (494, 403), 28: (728, 753), 29: (674, 698), 30: (623, 647),
    31: (573, 599), 32: (525, 549), 33: (483, 500), 34: (433, 450), 35: (619, 754),
    36: (565, 701), 37: (514, 653), 38: (462, 603), 39: (424, 550), 40: (381, 502),
    41: (502, 753), 42: (457, 702), 43: (408, 655), 44: (361, 603), 45: (323, 549),
    46: (396, 754), 47: (349, 704), 48: (306, 655), 49: (263, 605), 50: (297, 757),
    51: (251, 706), 52: (203, 657), 53: (193, 759), 54: (148, 706), 55: (85, 758),
}

# EDIT: spots centered by hand on the on-axis camera, spot: (Huber sy mm, piezo x um, piezo y um),
# Huber sx = SX55, or (sy, x, y, sx) at another Huber sx.  >= 3 spots far apart and not in a line
# (1, 10, 55; a 4th, e.g. 33, shows the fit residual).  Used as they are; all other spots come from
# the affine fit through them.
MEASURED55B = {                     # 2026-10-20 night, all at Huber sx -2.5
    10: (-30, 1100, -6914, -2.5), 31: (0, -1100, -7114, -2.5), 1: (0, 41800, 4914, -2.5),
    55: (0, -48600, 9500, -2.5),
    # checked with mov_sam(n, HOLDER55B), the Huber as set, piezo re-centered ("40 at -8537" read as 41)
    28: (-1.9, 12619, 7743, -2.5), 41: (-1.9, -8537, 9213, -2.5),
    40: (-23.17, -20364, 6163, -2.5), 5: (-23.17, 23780, 9200, -2.5),
}
# EDIT: bare carbon paper of this piece as the blank, measured with the array row given;
# name: (Huber sy mm, piezo x um, piezo y um, row = 0 bottom (Ag 0) .. 9 top (spot 10))
BLANKS55B = {
    # 'carbon_paper_as_prepared': (sy, x, y, 4),
}

SX55B = None                # Huber sx (mm) for the whole piece; None: that of the spots measured
LIM55B = LIM_CLIU           # travel: the piezo x as reached on the CLiu plate (-57300 .. 47500 um)

TRANS55B = dict(TRANS55, md=dict(TRANS55['md'], holder='UPenn B001 Au-Ag-Cu array (Huber + piezo)',
                                 piece='as prepared (untested)'))


def holder55b_samples():
    """
    The as-prepared piece (MEASURED55B, PIX55B, BLANKS55B) ordered as the 384-well plates: the array
    rows from the top in as few Huber sy bands as the piezo y covers (the first nearest the sy of
    the highest spot measured), the Huber sx shifted only for spots past the piezo x travel; []
    until 3 spots are measured.
    """
    if len(MEASURED55B) < 3:
        print('HOLDER55B (B001 as prepared): not calibrated yet -- center >= 3 spots -> MEASURED55B')
        return []
    top = max(MEASURED55B, key=lambda n: KR55[n - 1][1] - KR55[n - 1][0])
    sx0 = SX55B if SX55B is not None else float(np.median([m[3] if len(m) > 3 else SX55
                                                            for m in MEASURED55B.values()]))
    return holder55_samples(MEASURED55B, PIX55B, BLANKS55B, STATE55B, TRANS55B['offsets'],
                            lattice_bottom=False, label='HOLDER55B', bands=True,
                            start_sy=MEASURED55B[top][0], sx0=sx0, lim=LIM55B)


def run_holder_55before(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the as-prepared B001 piece (HOLDER55B: the 55 spots and
    BLANKS55B, or the given red labels / names, or the array rows given, 0 = bottom) as
    run_cliu_box1: one WAXS arc at a time over all spots, the Huber positions (a few Huber sy bands,
    holder55b_samples) in the order of HOLDER55B and reversed at the next arc; per spot TRANS55B (as
    the piece after screening: a 13-point cross, WAXS at every arc with SAXS at the highest) and
    (ova=True) one on-axis camera image on the first arc.  kw override TRANS55B.
    """
    if not HOLDER55B:
        raise ValueError('B001 as-prepared piece not calibrated: fill MEASURED55B (>= 3 spots), '
                         're-run this file')
    samples = _select55(HOLDER55B, which, rows)
    opts = dict(TRANS55B, **kw)
    check_arcs(opts['arcs'])
    check_holder55(samples, opts['offsets'], LIM55B)
    return _by_arc(samples, ova, opts, 'run_holder_55before')


HOLDER55B = holder55b_samples()
if HOLDER55B:
    _holder55_summary('HOLDER55B', HOLDER55B, TRANS55B['offsets'], HOLDER55B[0]['sx'])


###############################################################################################
# ORNL (C. Liu) suspensions, Box 2: a 384-well plate as Box 1, + three samples added at CFN
###############################################################################################
# well -> pyCLEAR sample name (pyCLEAR records, box-2 wells): the B005 Cu-M library as suspensions
# (B006 / B007 are powders only).  Photo (A bottom, columns 1 .. 24 left to right):
# pyCLEAR/data/Received/2026-10-15_CLiu-ORNL/B005_CuM_81_Box2_solution_OpticalImage_mark_position.jpg
CLIU_BOX2 = {
    'B2': 'Sample000225_B005_Cu10', 'B4': 'Sample000226_B005_Cu9Co1',
    'B6': 'Sample000227_B005_Cu8Co2', 'B8': 'Sample000228_B005_Cu7Co3',
    'B10': 'Sample000229_B005_Cu6Co4', 'B12': 'Sample000230_B005_Cu5Co5',
    'B14': 'Sample000231_B005_Cu4Co6', 'B16': 'Sample000232_B005_Cu3Co7',
    'B18': 'Sample000233_B005_Cu2Co8', 'B20': 'Sample000234_B005_Cu1Co9',
    'B22': 'Sample000235_B005_Co10', 'D2': 'Sample000236_B005_Cu9Ni1',
    'D4': 'Sample000237_B005_Cu8Ni2', 'D6': 'Sample000238_B005_Cu7Ni3',
    'D8': 'Sample000239_B005_Cu6Ni4', 'D10': 'Sample000240_B005_Cu5Ni5',
    'D12': 'Sample000241_B005_Cu4Ni6', 'D14': 'Sample000242_B005_Cu3Ni7',
    'D16': 'Sample000243_B005_Cu2Ni8', 'D18': 'Sample000244_B005_Cu1Ni9',
    'D20': 'Sample000245_B005_Ni10', 'F2': 'Sample000246_B005_Cu9Zn1',
    'F4': 'Sample000247_B005_Cu8Zn2', 'F6': 'Sample000248_B005_Cu7Zn3',
    'F8': 'Sample000249_B005_Cu6Zn4', 'F10': 'Sample000250_B005_Cu5Zn5',
    'F12': 'Sample000251_B005_Cu4Zn6', 'F14': 'Sample000252_B005_Cu3Zn7',
    'F16': 'Sample000253_B005_Cu2Zn8', 'F18': 'Sample000254_B005_Cu1Zn9',
    'F20': 'Sample000255_B005_Zn10', 'H2': 'Sample000256_B005_Cu9Fe1',
    'H4': 'Sample000257_B005_Cu8Fe2', 'H6': 'Sample000258_B005_Cu7Fe3',
    'H8': 'Sample000259_B005_Cu6Fe4', 'H10': 'Sample000260_B005_Cu5Fe5',
    'H12': 'Sample000262_B005_Cu8Cr2', 'H14': 'Sample000263_B005_Cu7Cr3',
    'H16': 'Sample000264_B005_Cu6Cr4', 'H18': 'Sample000261_B005_Cu9Cr1',
    'H20': 'Sample000265_B005_Cu5Cr5', 'J2': 'Sample000266_B005_Cu9Mn1',
    'J4': 'Sample000267_B005_Cu8Mn2', 'J6': 'Sample000268_B005_Cu7Mn3',
    'J8': 'Sample000269_B005_Cu6Mn4', 'J10': 'Sample000270_B005_Cu5Mn5',
    'J12': 'Sample000271_B005_Cu4Mn6', 'J14': 'Sample000272_B005_Cu3Mn7',
    'J16': 'Sample000273_B005_Cu2Mn8', 'J18': 'Sample000274_B005_Cu1Mn9',
    'J20': 'Sample000275_B005_Mn10', 'L2': 'Sample000276_B005_Cu9Bi1',
    'L4': 'Sample000277_B005_Cu8Bi2', 'L6': 'Sample000278_B005_Cu7Bi3',
    'L8': 'Sample000279_B005_Cu6Bi4', 'L10': 'Sample000280_B005_Cu5Bi5',
    'L12': 'Sample000281_B005_Cu4Bi6', 'L14': 'Sample000282_B005_Cu3Bi7',
    'L16': 'Sample000283_B005_Cu2Bi8', 'L18': 'Sample000284_B005_Cu1Bi9',
    'L20': 'Sample000285_B005_Bi10', 'N2': 'Sample000286_B005_Cu9Sn1',
    'N4': 'Sample000287_B005_Cu8Sn2', 'N6': 'Sample000288_B005_Cu7Sn3',
    'N8': 'Sample000289_B005_Cu6Sn4', 'N10': 'Sample000290_B005_Cu5Sn5',
    'N12': 'Sample000291_B005_Cu4Sn6', 'N14': 'Sample000292_B005_Cu3Sn7',
    'N16': 'Sample000293_B005_Cu2Sn8', 'N18': 'Sample000294_B005_Cu1Sn9',
    'N20': 'Sample000295_B005_Sn10', 'P2': 'Sample000296_B005_Cu9Ag1',
    'P4': 'Sample000297_B005_Cu8Ag2', 'P6': 'Sample000298_B005_Cu7Ag3',
    'P8': 'Sample000299_B005_Cu6Ag4', 'P10': 'Sample000300_B005_Cu5Ag5',
    'P12': 'Sample000301_B005_Cu4Ag6', 'P14': 'Sample000302_B005_Cu3Ag7',
    'P16': 'Sample000303_B005_Cu2Ag8', 'P18': 'Sample000304_B005_Cu1Ag9',
    'P20': 'Sample000305_B005_Ag10',
}
CLIU2_FORM = 'Suspension'           # name suffix: CL_<pyCLEAR name>_Suspension
CLIU2_RUN = 'run2'                  # EDIT: run tag at the end of every Box 2 name ('' none): run2 = all
                                    # wells again after a beam error (10-21), N, P first, then B .. L
# added on the plate at CFN (names as given, no CL_ prefix): well: (name, metadata)
CLIU2_ADDED = {
    'D24': ('AgBH', dict(role='calibrant', form='powder')),
    'F23': ('GL_52C', dict(form='DNA-assembled nanoparticle superlattice')),
    'F24': ('MH_5_61_A', dict(form='DNA-assembled nanoparticle superlattice')),
}
CLIU2_BLANKS = {'B24': 'EmptyWell_B24', 'P24': 'EmptyWell_P24'}   # EDIT: empty wells (check), in rows
                                                                   # measured anyway
# EDIT: four corners centered by hand, here('sx', 'sy', 'x', 'y'): A1, A24, P1, P24 (or the top row
# in reach, e.g. N1, N24)
CAL_CLIU2 = {                       # 2026-10-21, corners after pushing the box back up (run2)
    'A1': (-2, 13.2, -55000, 12500), 'A24': (-2, 13.2, 48400, 11300),
    'M1': (-2, -30, -55380, 1900), 'M24': (-2, -30, 47800, 600),
    # first placement (run1): A1 (-1.5, 13.2, -56303, 12300), A24 (-1.5, 13.2, 47020, 11500),
    #                         M1 (-1.5, -30, -56903, 1700), M24 (-1.5, -30, 46400, 800)
}
CLIU2_LATER = 'NP'                  # rows measured after pushing the box down (CAL_CLIU2_PUSHED)
# EDIT after pushing the box down: wells of rows N, P centered by hand, here('sx', 'sy', 'x', 'y'),
# best N1, N24, P1, P24 (2 wells of one row: that row only).  Also takes any well out of reach above.
CAL_CLIU2_PUSHED = {                # 2026-10-21, after pushing the box down
    'N1': (-2, -30, -55208, 4465), 'N24': (-2, -30, 48400, 3065),
    'P1': (-2, -30, -55208, -4735), 'P24': (-2, -30, 48200, -5935),
}
SX_CLIU2 = None             # Huber sx (mm) for the whole plate; None: from CAL_CLIU2, in whole mm (printed)

TRANS_CLIU2 = dict(TRANS_CLIU, md={
    'holder': 'ORNL Box 2, Corning 384-well plate, Kapton over the wells (Huber + piezo)',
    'batch': 'B005_CuM_81', 'form': 'suspension', 'run_batch': f'Box2_{CLIU2_RUN or "run1"}'})


def _cliu2_names(wells):
    """({well: CL_<name>_Suspension, added or blank name, + _<CLIU2_RUN>}, {well: metadata}) of the Box 2
    wells given."""
    names, extra = {}, {}
    for w in wells:
        if w in CLIU2_BLANKS:
            names[w] = f'{CLIU_PREFIX}_{CLIU2_BLANKS[w]}'
            extra[w] = dict(role='blank', form='empty well', box='box2')
        elif w in CLIU2_ADDED:
            names[w], md = CLIU2_ADDED[w]
            extra[w] = dict(md, box='box2')
        else:
            n = CLIU_BOX2[w]
            names[w] = f'{CLIU_PREFIX}_{n}_{CLIU2_FORM}'
            extra[w] = dict(sample_id=n.split('_')[0], batch=n.split('_')[1], form='suspension', box='box2')
        if CLIU2_RUN:
            names[w] = f'{names[w]}_{CLIU2_RUN}'
            extra[w]['run'] = CLIU2_RUN
    return names, extra


def cliu_box2_samples(cal=None):
    """Box 2 wells (CLIU_BOX2, CLIU2_ADDED, CLIU2_BLANKS) except the CLIU2_LATER rows, mapped through
    CAL_CLIU2 and ordered as Box 1 (plate_samples); wells out of reach are left out (printed).  []
    before CAL_CLIU2 is filled."""
    cal = CAL_CLIU2 if cal is None else cal
    if len(cal) < 3:
        print('CLiu Box 2: not calibrated yet (CAL_CLIU2 needs 3+ wells, best the four corners)')
        return []
    names, extra = _cliu2_names([w for w in (*CLIU_BOX2, *CLIU2_ADDED, *CLIU2_BLANKS)
                                 if w[0] not in CLIU2_LATER])
    return plate_samples(names, cal, TRANS_CLIU2['offsets'], extra, sx=SX_CLIU2, lim=LIM_CLIU,
                         label='CLiu Box 2')


def cliu_box2_pushed_samples(cal=None, done=None):
    """The Box 2 wells PLATE_CLIU2 (done) leaves out (the CLIU2_LATER rows, any out of reach), after
    pushing the plate down, mapped through CAL_CLIU2_PUSHED (2 wells of one row: that row only)."""
    cal = CAL_CLIU2_PUSHED if cal is None else cal
    done = PLATE_CLIU2 if done is None else done
    if len(cal) < 2 or not done:
        return []
    have = {s['well'] for s in done}
    wells = [w for w in (*CLIU_BOX2, *CLIU2_ADDED, *CLIU2_BLANKS) if w not in have]
    if len({w[0] for w in cal}) == 1:
        wells = [w for w in wells if w[0] == next(iter(cal))[0]]
    if not wells:
        return []
    names, extra = _cliu2_names(wells)
    return plate_samples(names, cal, TRANS_CLIU2['offsets'], extra, sx=SX_CLIU2, lim=LIM_CLIU,
                         label='CLiu Box 2 pushed')


def run_cliu_box2(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of Box 2 (PLATE_CLIU2: the ORNL suspensions, AgBH, GL_52C and
    MH_5_61_A, or the given wells / names, or rows) as run_cliu_box1: one WAXS arc at a time over all
    wells, 3 spots per well (TRANS_CLIU2), one on-axis camera image per well on the first arc; the
    Huber in a few sy bands from the top, reversed at the next arc.  kw override TRANS_CLIU2.
    """
    if not PLATE_CLIU2:
        raise ValueError('CLiu Box 2 not calibrated: fill CAL_CLIU2 and re-run this file')
    return _run_plate(PLATE_CLIU2, which, rows, ova, kw, 'run_cliu_box2', TRANS_CLIU2)


def run_cliu_box2_pushed(*which, ova=True, **kw):
    """Plan: as run_cliu_box2, for the wells out of reach before, after pushing the plate down
    (PLATE_CLIU2_PUSHED, CAL_CLIU2_PUSHED)."""
    if not PLATE_CLIU2_PUSHED:
        raise ValueError('Box 2 after the push not calibrated: fill CAL_CLIU2_PUSHED, re-run this file')
    return _run_plate(PLATE_CLIU2_PUSHED, which, None, ova, kw, 'run_cliu_box2_pushed', TRANS_CLIU2)


PLATE_CLIU2 = cliu_box2_samples()
if PLATE_CLIU2:
    _plate_summary('PLATE_CLIU2', PLATE_CLIU2, TRANS_CLIU2['offsets'])
PLATE_CLIU2_PUSHED = cliu_box2_pushed_samples()
if PLATE_CLIU2_PUSHED:
    _plate_summary('PLATE_CLIU2_PUSHED', PLATE_CLIU2_PUSHED, TRANS_CLIU2['offsets'])


###############################################################################################
# W. Liu Au nanoparticles, Box 3: solutions in a 384-well plate (Kapton over the wells)
###############################################################################################
# pyCLEAR/data/Received/2026_1020_WLiu/WH_Au_55_Box3_solution_OpticalImage_mark_position.jpg and
# .xlsx (A bottom, columns 1 .. 24 left to right): S6 .. S55 in rows H, G, F, E, C, columns 8 .. 17,
# 10 per row; SiO2 and water references in column 7 and D11.
WLIU_PREFIX = 'WL'                  # sample names WL_Au_S6, WL_SiO2_H7, WL_Water_G7
WLIU_FIRST = {'H': 6, 'G': 16, 'F': 26, 'E': 36, 'C': 46}      # row: its sample in column 8
WLIU_BOX3 = {f'{r}{8 + i}': f'S{n + i}' for r, n in WLIU_FIRST.items() for i in range(10)}
WLIU_REFS = {'H7': 'SiO2', 'G7': 'Water', 'F7': 'SiO2', 'E7': 'Water', 'D11': 'SiO2', 'C7': 'SiO2'}
# EDIT: four corners centered by hand, here('sx', 'sy', 'x', 'y'): e.g. A1, A24, P1, P24
CAL_WLIU = {                        # 2026-10-21, the corners of the wells used (C7 .. H17)
    'C7': (-2, 10.8, -28062, 2900), 'C17': (-2, 10.8, 16637, 2100),
    'H7': (-2, -4, -28862, -4500), 'H17': (-2, -4, 16437, -5500),
}
SX_WLIU = None              # Huber sx (mm); None: from CAL_WLIU, in whole mm (printed)

TRANS_WLIU = dict(TRANS_CLIU, md={
    'holder': 'W. Liu Box 3, 384-well plate, Kapton over the wells (Huber + piezo)',
    'batch': 'WH_Au_55', 'form': 'solution'})


def wliu_box3_samples(cal=None):
    """Box 3 wells (WLIU_BOX3, WLIU_REFS) mapped through CAL_WLIU and ordered as Box 1
    (plate_samples); [] before CAL_WLIU is filled."""
    cal = CAL_WLIU if cal is None else cal
    if len(cal) < 3:
        print('WLiu Box 3: not calibrated yet (CAL_WLIU needs 3+ wells, best the four corners)')
        return []
    names, extra = {}, {}
    for w, n in WLIU_BOX3.items():
        names[w] = f'{WLIU_PREFIX}_Au_{n}'
        extra[w] = dict(sample=n, form='solution', box='box3')
    for w, ref in WLIU_REFS.items():
        names[w] = f'{WLIU_PREFIX}_{ref}_{w}'
        extra[w] = dict(role='blank' if ref == 'Water' else 'reference', form='solution', box='box3')
    return plate_samples(names, cal, TRANS_WLIU['offsets'], extra, sx=SX_WLIU, lim=LIM_CLIU,
                         label='WLiu Box 3')


def run_wliu_box3(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the W. Liu Au nanoparticle solutions (PLATE_WLIU: S6 .. S55 and
    the SiO2 / water references, or the given wells / names, or rows) as run_cliu_box1: one WAXS
    arc at a time over all wells, 3 spots per well (TRANS_WLIU), one on-axis camera image per well on
    the first arc; the Huber in a few sy bands from the top, reversed at the next arc.  kw override
    TRANS_WLIU.
    """
    if not PLATE_WLIU:
        raise ValueError('WLiu Box 3 not calibrated: fill CAL_WLIU and re-run this file')
    return _run_plate(PLATE_WLIU, which, rows, ova, kw, 'run_wliu_box3', TRANS_WLIU)


PLATE_WLIU = wliu_box3_samples()
if PLATE_WLIU:
    _plate_summary('PLATE_WLIU', PLATE_WLIU, TRANS_WLIU['offsets'])

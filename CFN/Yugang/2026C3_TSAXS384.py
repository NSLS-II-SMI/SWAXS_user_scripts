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
    y only travels -15000..12400 um (LIM55), so each row's sy is raised until its crosses fit below
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
    fitted pitch (4.5 mm) and the plan.  The whole plate at Huber sx = SX_CLIU (-3): the piezo x runs
    from -56000 (A1 - 500) to 48300 (A24 + 500) -- check both ends, and a well far from the corners:
      mov_sam('A24', PLATE_CLIU); movx(500); movx(-500)
      mov_sam('A1', PLATE_CLIU); movx(-500); movx(500)
      mov_sam('G12', PLATE_CLIU); RE(ova_snap('test'))
    A failed end: change SX_CLIU (-0.5 mm moves both ends +500 um) and LIM_CLIU, re-run this file.
C2) Rows M .. A (74 wells): one WAXS arc at a time over all wells, 5 spots per well (CROSS_CLIU: x
    -500, 0, 500, then y -500, 500), SAXS at 40, one camera image per well.  The Huber x moves once (to
    SX_CLIU), the Huber y holds 3 heights (rows M-K-I, G-E-C, A; the piezo y takes the rows within),
    visited from the top down and in reverse at the next arc:
      preview(run_cliu_box1())                 # 74 x 5 x 3 = 1110 exposures
      RE(run_cliu_box1())
      RE(run_cliu_box1('M18', 'A1'))           # a few wells;  rows='KM': some rows
      RE(run_cliu_box1(arcs=(20, 40)))         # e.g. after an error during the arc-20 pass
C3) Row P: push the plate down, center P1 and P24 -> CAL_CLIU_P, re-run this file:
      preview(run_cliu_box1_P())               # 9 x 5 x 3 = 135 exposures, the Huber y stays put
      RE(run_cliu_box1_P())
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
LIM55 = {'sy': (-30, 20), 'x': (-47000, 47000), 'y': (-15000, 12400)}   # travel (Huber mm, piezo um),
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


def holder55_positions(measured=None):
    """
    {spot: {'x': piezo x um, 'v': height sy + (y - PY0) / 1000 mm, 'source'}}:
      'measured'  as in MEASURED55
      'photo'     from its blue dot, by an affine fit marked-image pixel -> stage through the measured
      'lattice'   bottom row (Ag = 0, the Au-Cu edge): these spots are faint on the photo and their
                  dots are guesses (28's was 1.4 mm off), so one lattice step (fitted through the
                  measured spots) from its neighbours in the next row
    """
    measured = MEASURED55 if measured is None else measured
    keys = sorted(measured)
    S = np.array([_xv55(*measured[n]) for n in keys])
    dots = [i for i, n in enumerate(keys) if KR55[n - 1][0] != KR55[n - 1][1]]   # not the bottom row
    A = np.array([[*PIX55[keys[i]], 1.0] for i in dots])
    coef = np.linalg.lstsq(A, S[dots], rcond=None)[0]
    res = np.linalg.norm(S[dots] - A @ coef, axis=1)
    step = np.linalg.lstsq(np.array([[*KR55[n - 1], 1.0] for n in keys]), S, rcond=None)[0][:2]
    print(f'holder55: photo fit through {len(dots)} measured spots, residual rms '
          f'{np.sqrt(np.mean(res ** 2)):.2f} mm, max {res.max():.2f} mm (spot {keys[dots[res.argmax()]]}); '
          f'lattice step column {np.linalg.norm(step[0]):.2f} mm, row {np.linalg.norm(step[1]):.2f} mm')
    spot = {kr: i + 1 for i, kr in enumerate(KR55)}
    xv, source = {}, {}
    for n in range(1, 56):
        if n in measured:
            xv[n], source[n] = S[keys.index(n)], 'measured'
        else:
            xv[n], source[n] = np.array([*PIX55[n], 1.0]) @ coef, 'photo'
    for n in range(1, 56):
        k, r = KR55[n - 1]
        if r == k and n not in measured:
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


def holder55_samples():
    """
    The 55 spots and BLANKS55, row by row of the array (row = Ag level, bottom row first) in a
    serpentine: S1 -> S55, S54 -> S2, S3 -> S52, ...  The spots of a row share one Huber sy and the
    piezo y takes the spot-to-spot height, so the Huber moves once per row.  sy is the row mean,
    shifted as little as needed to keep the piezo y of every cross (CROSS55) inside its travel.  Spots
    whose cross does not fit the piezo x travel get the Huber sx shifted by whole mm (one shift for
    all of them on each side) and the piezo x shifted back.
    """
    spots = []
    for n, p in holder55_positions().items():
        k, r = KR55[n - 1]
        spots.append(dict(key=n, name=clean_name(f'{PYCLEAR55[n - 1]}_{STATE55}'), x=p['x'], v=p['v'],
                          array_row=r - k, sample_id=PYCLEAR55[n - 1].split('_')[0],
                          target_id=1 + 14 * k + r, pipetmax_col=k, pipetmax_row=r,
                          position=p['source']))
    for name, (sy, x, y, row) in BLANKS55.items():
        spots.append(dict(key=name, name=clean_name(name), x=float(x), v=sy + (y - PY0) / 1000,
                          array_row=row, role='blank', position='measured'))
    x_lo, x_hi = _travel('x')
    dx_lo, dx_hi = min(dx for dx, _ in CROSS55), max(dx for dx, _ in CROSS55)
    left = lambda X: X + dx_lo < x_lo + MARGIN55
    right = lambda X: X + dx_hi > x_hi - MARGIN55
    xs = [s['x'] for s in spots]
    shift_l = np.ceil(max(x_lo + MARGIN55 - dx_lo - min(xs), 0) / 1000)     # mm, piezo x + shift
    shift_r = np.ceil(max(max(xs) + dx_hi - x_hi + MARGIN55, 0) / 1000)     # mm, piezo x - shift
    samples = []
    for row in sorted({s['array_row'] for s in spots}):
        cells = sorted((s for s in spots if s['array_row'] == row), key=lambda s: s['x'],
                       reverse=row % 2 == 0)
        sy = _row_sy([s['v'] for s in cells])
        for s in cells:
            v, X = s.pop('v'), s['x']
            d = shift_l if left(X) else -shift_r if right(X) else 0
            s.update(sx=float(SX55 - SXDIR55 * d), sy=sy, x=round(X + d * 1000), y=round(PY0 + (v - sy) * 1000))
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
    samples = select(HOLDER55, *which) if which else HOLDER55
    if rows is not None:
        samples = [s for s in samples if s['array_row'] in rows]
        if not samples:
            raise ValueError(f'no spots in rows {rows}')
    opts = dict(TRANS55, **kw)
    check_arcs(opts['arcs'])
    check_holder55(samples, opts['offsets'])
    return _rows55(samples, ova, opts)


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


HOLDER55 = holder55_samples()
_xs, _ys = [s['x'] for s in HOLDER55], [s['y'] for s in HOLDER55]
print(f'HOLDER55: {len(HOLDER55)} spots in {len({s["array_row"] for s in HOLDER55})} rows, Huber sy per '
      f'row {", ".join(f"{sy:g}" for sy in dict.fromkeys(s["sy"] for s in HOLDER55))} mm; '
      f'piezo x {min(_xs) - 900:.0f}..{max(_xs) + 900:.0f} um, y {min(_ys) - 900:.0f}..{max(_ys) + 900:.0f} um')
for _sx in sorted({s['sx'] for s in HOLDER55} - {SX55}):
    print(f'  Huber sx {_sx:g} mm (not {SX55:g}) for spots '
          f'{", ".join(str(s["key"]) for s in HOLDER55 if s["sx"] == _sx)} -- SXDIR55 = {SXDIR55} checked?')


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
CAL_CLIU_P = {
    # 'P1': (sx, sy, x, y), 'P24': (sx, sy, x, y),
}

SX_CLIU = -3.0                      # Huber sx (mm) for the whole plate: columns 1 .. 24 on the piezo x
LIM_CLIU = dict(LIM55, x=(-57300, 48500))   # piezo x for the plate (um): -57303 reached (N1); at sx -3
                                            # column 24 needs up to 48300 (A24 + 500) -- check, C1
CROSS_CLIU = ((-500, 0), (0, 0), (500, 0), (0, -500), (0, 500))   # 5 spots per well (piezo x, y um)

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


def plate_samples(names, cal, offsets, extra=None, start_sy=None, sx=None, lim=None):
    """
    The wells names {well: sample name} of a 384-well plate (plate_positions), ordered for few Huber
    moves.  Huber y: the rows, from the top, in as few bands as the piezo y travel covers -- one Huber
    sy per band, the piezo y takes the rows within it; each band's sy is the one nearest the previous
    band's (the first: nearest start_sy, default the calibration's sy nearest the top row).  Huber x:
    the columns in as few blocks as the piezo x travel covers, each at one Huber sx (in whole mm from
    the calibration's sx), or all at Huber sx = sx.  Order: band by band from the top, the blocks of a
    band in a serpentine (the Huber sx moves once per band), the wells of a block row by row in a
    serpentine.  extra: {well: metadata}; lim: travel table (default LIM55).
    """
    extra = extra or {}
    pos = plate_positions(list(names), cal)
    x_lo, x_hi = _travel('x', lim)
    y_lo, y_hi = _travel('y', lim)
    sy_min, sy_max = _travel('sy', lim)
    dx_lo, dx_hi = min(dx for dx, _ in offsets), max(dx for dx, _ in offsets)
    dy_lo, dy_hi = min(dy for _, dy in offsets), max(dy for _, dy in offsets)
    x_min, x_max = x_lo + MARGIN55 - dx_lo, x_hi - MARGIN55 - dx_hi      # um, for the well centers
    y_min, y_max = y_lo + MARGIN55 - dy_lo, y_hi - MARGIN55 - dy_hi
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
    # Huber sy: row bands from the top; sy window of a band: every piezo y in [y_min, y_max]
    window = lambda vs: (max(max(vs) - (y_max - PY0) / 1000, sy_min), min(min(vs) - (y_min - PY0) / 1000, sy_max))
    rows = sorted({_well(w)[0] for w in names}, reverse=True)
    bands = []
    for r in rows:
        vs = [pos[w][1] for w in names if _well(w)[0] in (bands[-1] if bands else []) + [r]]
        lo, hi = window(vs)
        if bands and hi - lo >= 0.02:
            bands[-1].append(r)
        else:
            bands.append([r])
    if start_sy is None:
        top = max(cal, key=lambda w: (-abs(_well(w)[0] - rows[0]), _well(w)[1]))
        start_sy = cal[top][1]
    samples, prev = [], start_sy
    blocks = sorted(hx_of)
    for i, band in enumerate(bands):
        lo, hi = window([pos[w][1] for w in names if _well(w)[0] in band])
        sy = float(np.ceil(lo * 100) / 100 if prev < lo else np.floor(hi * 100) / 100 if prev > hi else prev)
        prev = sy
        for j, b in enumerate(blocks if i % 2 == 0 else blocks[::-1]):
            hx = hx_of[b]
            for k, r in enumerate(band):
                wells = sorted((w for w in names if _well(w)[0] == r and block[w] == b),
                               key=lambda w: _well(w)[1], reverse=(i + j + k) % 2 == 1)
                for w in wells:
                    X, V = pos[w]
                    samples.append(dict(key=w, name=clean_name(names[w]), well=w, plate_row=PLATE_ROWS[r],
                                        plate_col=_well(w)[1] + 1, sx=hx, sy=sy,
                                        x=round(X * 1000 - SXDIR55 * (hx - SX55) * 1000),
                                        y=round(PY0 + (V - sy) * 1000), **extra.get(w, {})))
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


def _run_plate(plate, which, rows, ova, kw, label):
    samples = select(plate, *which) if which else plate
    if rows is not None:
        samples = [s for s in samples if s['plate_row'] in rows]
        if not samples:
            raise ValueError(f'no wells in rows {rows}')
    opts = dict(TRANS_CLIU, **kw)
    check_arcs(opts['arcs'])
    check_holder55(samples, opts['offsets'], LIM_CLIU)
    return _by_arc(samples, ova, opts, label)


def run_cliu_box1(*which, rows=None, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the ORNL powders in Box 1 (PLATE_CLIU: rows A .. M, or the given
    wells / names, or rows, e.g. rows='KM'): one WAXS arc at a time over all wells (TRANS_CLIU arcs,
    SAXS with the highest), 5 spots per well (CROSS_CLIU), one on-axis camera image per well
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


def _plate_summary(label, plate):
    off = TRANS_CLIU['offsets']
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

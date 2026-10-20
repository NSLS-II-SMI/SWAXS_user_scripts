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
    from its blue dot on the marked image (PIX55) by an affine fit through the measured ones
    (printed when this file runs; spot 20 has no visible spot, its pixel is a lattice estimate).
      show_samples(HOLDER55)
U2) Check the spots furthest from the measured ones before the long run (1, 11, 20, 41, 53, 55):
      mov_sam(55, HOLDER55); RE(ova_snap('test'))
    off-center: center it by hand, here('sy', 'x', 'y') -> MEASURED55, re-run this file (refits).
U3) Measure: per spot a 13-point cross (x -900..900 then y -900..900, 300 um steps), WAXS at
    arcs 0, 20, 40 with SAXS at 40, one on-axis camera image at the center (first arc):
      preview(run_holder_55after())      # 55 x 13 x 3 = 2145 exposures
      RE(run_holder_55after())
      RE(run_holder_55after(35, 36))     # a few spots (red labels)
      RE(run_holder_55after(arcs=(40,), ova=False))   # e.g. redo one arc
    The on-axis camera must be acquiring; images -> YZ['ova_dir'], one logbook row each.
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
# Huber sx = SX55.  Used as they are; all other spots come from the affine fit through them.
MEASURED55 = {
    35: (7, -7600, 12300), 36: (2.4, -12800, 12300), 29: (2.4, -2300, 12300),
    30: (-2.2, -6700, 12300), 31: (-8, -11100, 12300), 23: (-7, -1400, 12300),
    24: (-12.6, -5400, 12300), 25: (-18, -9300, 12300), 16: (-17.8, 200, 12300),
    17: (-23.2, -4400, 12300), 18: (-27.4, -8300, 12300), 8: (-27.4, 1500, 12300),
    9: (-30, -2500, 10500), 10: (-30, -7600, 4700),
}
SX55 = 0.0                  # Huber sx (mm) for the whole array
PY0 = 12300                 # piezo y (um) while the Huber sy can do the vertical
LIM55 = {'sy': (-30, 20), 'y': (-20000, 20000)}    # travel (Huber mm, piezo um), with the motors' own

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
    """{spot: {'sx', 'sy', 'x', 'y', 'source'}}: measured spots as measured, the others from an affine
    fit (marked-image pixel -> horizontal x, vertical sy + (y - PY0)) through the measured ones."""
    measured = MEASURED55 if measured is None else measured
    keys = sorted(measured)
    A = np.array([[*PIX55[n], 1.0] for n in keys])
    S = np.array([[measured[n][1] / 1000, measured[n][0] + (measured[n][2] - PY0) / 1000] for n in keys])
    coef = np.linalg.lstsq(A, S, rcond=None)[0]
    res = np.linalg.norm(S - A @ coef, axis=1)
    print(f'holder55: fit through {len(keys)} measured spots, residual rms {np.sqrt(np.mean(res ** 2)):.2f}'
          f' mm, max {res.max():.2f} mm (spot {keys[res.argmax()]})')
    out = {}
    for n in range(1, 56):
        if n in measured:
            sy, x, y = measured[n]
            source = 'measured'
        else:
            X, V = np.array([*PIX55[n], 1.0]) @ coef
            sy = min(max(V, LIM55['sy'][0]), LIM55['sy'][1])      # the piezo y takes the rest
            x, y = X * 1000, PY0 + (V - sy) * 1000
            source = 'fit'
        out[n] = dict(sx=SX55, sy=round(float(sy), 3), x=round(float(x)), y=round(float(y)), source=source)
    return out


def holder55_samples():
    """The 55 spots, ordered row by row of the array (constant Ag, nearly constant sy) in a serpentine."""
    pos = holder55_positions()

    def order(n):
        k, r = KR55[n - 1]
        return r - k, pos[n]['x'] * (-1) ** (r - k)

    spots = sorted(pos, key=order)
    samples = make_samples({n: f'{PYCLEAR55[n - 1]}_{STATE55}' for n in spots},
                           {n: {a: pos[n][a] for a in ('sx', 'sy', 'x', 'y')} for n in spots})
    for s in samples:
        k, r = KR55[s['key'] - 1]
        s.update(sample_id=PYCLEAR55[s['key'] - 1].split('_')[0], target_id=1 + 14 * k + r,
                 pipetmax_col=k, pipetmax_row=r, position=pos[s['key']]['source'])
    return samples


def _travel(axis):
    """(low, high) of an axis: LIM55 and the motor's own soft limits, where set."""
    lo, hi = LIM55.get(axis, (-np.inf, np.inf))
    try:
        mlo, mhi = AXES[axis].limits
        if mlo < mhi:
            lo, hi = max(lo, mlo), min(hi, mhi)
    except Exception:
        pass
    return lo, hi


def check_holder55(samples=None, offsets=CROSS55):
    """Raise (before anything moves) if a spot of a cross is out of travel."""
    bad = []
    for s in (HOLDER55 if samples is None else samples):
        for dx, dy in offsets:
            for a, v in (('sx', s['sx']), ('sy', s['sy']), ('x', s['x'] + dx), ('y', s['y'] + dy)):
                lo, hi = _travel(a)
                if not lo <= v <= hi:
                    bad.append(f"{s['key']} {a}={v:g} not in [{lo:g}, {hi:g}]")
    if bad:
        raise ValueError('out of travel: ' + '; '.join(sorted(set(bad))[:10]))


def _ova_first_arc(sample, i_arc):
    if i_arc == 0:
        yield from ova_snap(sample)


def run_holder_55after(*which, ova=True, **kw):
    """
    Plan: transmission SAXS/WAXS of the 55 spots of the B001 array after screening (or the given red
    labels / names): a 13-point cross (CROSS55) per spot, WAXS at every arc of TRANS55 with SAXS at the
    highest, and (ova=True) one on-axis camera image per spot at its center on the first arc.
    kw override TRANS55.
    """
    samples = select(HOLDER55, *which) if which else HOLDER55
    opts = dict(TRANS55, **kw)
    check_holder55(samples, opts['offsets'])
    return run_trans(samples, at_sample=_ova_first_arc if ova else None, **opts)


HOLDER55 = holder55_samples()
_xs, _ys = [s['x'] for s in HOLDER55], [s['y'] for s in HOLDER55]
print(f'HOLDER55: {len(HOLDER55)} spots; piezo x {min(_xs) - 900:.0f}..{max(_xs) + 900:.0f} um, '
      f'piezo y {min(_ys) - 900:.0f}..{max(_ys) + 900:.0f} um, '
      f'Huber sy {min(s["sy"] for s in HOLDER55):g}..{max(s["sy"] for s in HOLDER55):g} mm')

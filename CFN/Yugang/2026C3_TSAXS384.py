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
"""

YZ.update(
    user='CFN',                 # EDIT: group tag used as the file-name prefix
    experiment='TSAXS384',
    md={'beam': '16.1 keV, low divergence', 'environment': 'air, RT',
        'holder': '384-cell holder (Huber + piezo)', 'saxs_sdd_m': 5},
)

# EDIT after calibration: Huber position of each bar (mm) and its cell grid on the piezo (um).
# None = not calibrated yet (bar skipped).
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

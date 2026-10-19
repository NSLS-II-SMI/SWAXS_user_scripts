"""
2026C3_JMayer.py -- Wed 2026-10-21: J. Mayer group (Yale), in-situ electrochemistry.

Their EC cell and potentiostat; we take GIWAXS (or transmission SAXS/WAXS) frames while the
potential is applied.  16.1 keV low divergence, SAXS 2M at 5 m, in air.

Synchronisation
---------------
ec_start() marks t = 0 (start their potentiostat sequence at the same moment and note its
clock time).  Every frame name carries _<cycle>_<seconds since ec_start>s and every run's
metadata has user_hints.series_t0 (unix) / series_t0_iso, so frames line up with the
potentiostat file afterwards.  The potential goes into the names as _E..V from, in order:
  a) an analog readback: EC.update(readback=moxa_out.ch2_read, scale=..., offset=...)
     (potentiostat E-monitor output wired to the Moxa analog input; scale = V per V)
  b) the programmed steps: EC['schedule'] = [(0, None), (600, -0.2), (1800, -0.5)]
     (seconds after ec_start, V; None = OCV / no token)
  c) typed values: ec_set_potential(-0.5); during a run Ctrl-C (pause) ->
     ec_set_potential(-0.5) -> RE.resume()

Run sheet
---------
0) bsui
     proposal_swap(<pass id>); project_set('JMayer')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_JMayer.py
     preflight()
1) Mount the cell (piezo; use STAGE = 'huber' if it sits on the Huber), find the electrode
   with the camera, edit NAMES / POS, re-run this file.  Keep cables free over the x range
   of SERIES['spots'].
2) Align on the electrode (saved to json; run_gi / run_ec use the latest saved alignment):
     align_gi_samples(stage=STAGE)
   if the cell geometry defeats the automatic alignment: align by hand,
     mark_aligned('Cell1', stage=STAGE)
3) Pristine reference (before any potential):
     RE(run_gi(stage=STAGE, angles=(0.10, 0.15, 0.20), arcs=(0, 20), t=1))
4) In situ:
     preview(run_ec(**SERIES))           # dry run of 2 cycles
     ec_start('CV 0 to -1 V, 10 mV/s')   # at the same time as their potentiostat
     RE(run_ec(**SERIES))
   Ctrl-C then RE.stop() ends it cleanly; RE(run_ec(...)) again continues the same clock and
   cycle counter until the next ec_start().
   Transmission instead of GI (no alignment needed):  RE(run_ec(**SERIES_TRANS))
"""

YZ.update(
    user='JMayer',
    experiment='JMayer_EC',
    md={'beam': '16.1 keV, low divergence', 'environment': 'air, in-situ EC cell',
        'holder': 'Yale EC cell', 'saxs_sdd_m': 5,
        # EDIT with the group:
        'ec_cell': '', 'electrolyte': '', 'working_electrode': '', 'reference_electrode': '',
        'counter_electrode': '', 'potentiostat': ''},
)

STAGE = 'piezo'          # 'huber' if the cell is aligned with the Huber stack (sx/sy/sth, mm)
# file names carry the positions of the stage that moves (spots differ only there)
YZ['name_xyz'] = ('x', 'y', 'z') if STAGE == 'piezo' else ('sx', 'sy', 'sz')

# EDIT: electrode name(s) and position(s) -- piezo (x, y) in um, or Huber (sx, sy) in mm
NAMES = {1: 'Cell1'}
POS = {1: (0, 0)}

SAMPLES = make_samples(NAMES, POS, axes=('x', 'y') if STAGE == 'piezo' else ('sx', 'sy'))

SERIES = dict(
    stage=STAGE,
    angles=(0.15,),          # incident angle(s); None = transmission
    arc=0,                   # WAXS arc for the time series (900KW)
    t=2,                     # exposure (s)
    interval=30,             # cycle start-to-start (s); 0 = as fast as possible
    duration=2 * 3600,       # s per run_ec call
    spots=(-200, 0, 200) if STAGE == 'piezo' else (-0.2, 0, 0.2),   # um / mm: fresh spot per cycle
    swaxs_every=10,          # every 10th cycle also a 900KW + 2M frame at arc 20 (GISAXS)
)

SERIES_TRANS = dict(SERIES, angles=None, swaxs_every=None)

# EDIT: potential steps (s after ec_start, V) if their protocol is fixed; None = OCV
EC['schedule'] = None

show_samples()

"""
2026C3_HZheng.py -- Mon 2026-10-19 AM: H. Zheng group, GISAXS + GIWAXS at room temperature,
then transmission SAXS/WAXS of the same films.

Standard Al GI bar on the piezo stage, in air; 16.1 keV low-divergence beam; SAXS 2M at 5 m;
~10 samples.  GIWAXS at arc 0 and 20 deg, GISAXS (2M) together with the arc-20 frames.

Run sheet
---------
0) bsui
     proposal_swap(<pass id>); project_set('HZheng')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_HZheng.py
     preflight()            # 16.1 keV, sdd ~5000 mm, 2M beamstop 'rod', log folder
1) Calibrant on the cal holder (after moving the piezo to it):
     RE(measure_wsaxs('AgBH', t=1, arc=20)); RE(measure_waxs('AgBH', t=1, arc=0))
2) Load the bar.  With the sample camera find each sample's piezo x (center of the film) and a
   rough surface height y; edit NAMES / X_POS / Y0 below, re-run this file, show_samples().
     mov_sam(1); RE(snap())          # quick look; 'test' frames are ignored by the analysis
3) Align all samples (~1-2 min each).  The result is saved to json after every sample and
   run_gi uses the latest saved alignment, so a Ctrl-C / RE.resume() or a bsui restart
   loses nothing:
     AD = align_gi_samples()
     align_gi_samples(select(SAMPLES, 3, 7))     # re-align a few, keep the others
     load_alignment(  )                             # show what run_gi will use
     manual fix of one sample:  mov_sam(3); ...align by hand...; mark_aligned(3)
4) Measure (GI below: 10 samples -> ~60 exposures, ~5 min):
     preview(run_gi(**GI))           # dry run: file names + count, nothing moves
     RE(run_gi(**GI))
     one sample first:   RE(run_gi(select(SAMPLES, 1), angles=(0.15,), arcs=(0,)))
     GI: GIWAXS at arcs 0, 20, 40; GISAXS (2M) only with the 40 frames (saxs='max')
     longer GISAXS only: RE(run_gi(angles=(0.15,), arcs=(40,), t=5, waxs_det=False))
5) Transmission SAXS/WAXS.  The GI bar cannot be measured in transmission (the films lie flat),
   so after the GI runs re-mount the films on the transmission bar (beam along the film normal;
   0.5 mm Si passes ~45 % at 16.1 keV).  In vacuum: vent / pump as in README "Vacuum chamber".
   Find each film's center with the camera, edit T_NAMES / T_POS below (add an empty spot and
   a bare substrate as backgrounds), re-run this file.  SAMPLES stays the GI bar, so use
   TSAMPLES / run_trans_samples here:
     show_samples(TSAMPLES); mov_sam(1, TSAMPLES); RE(snap())
     preview(run_trans_samples())    # dry run: file names + count (no _<ai>deg in the names)
     RE(run_trans_samples())         # all of TSAMPLES with TRANS: WAXS at 0, 20, 40, SAXS at 40
     longer SAXS only:   RE(run_trans_samples(arcs=(40,), t=5, waxs_det=False))
     RE(run_trans_samples(1, 'Empty', t=5))         # a few, longer exposure


Data saved:
/nsls2/auto-storage/smi/proposals/2026-3/pass-321337/projects     

project_set('QYu')

     
"""

# YZ.update(
#     user='HZheng',
#     experiment='HZheng_GI_RT',
#     md={'beam': '16.1 keV, low divergence', 'environment': 'air, RT', 'holder': 'Al GI bar',
#         'saxs_sdd_m': 5},
# )

YZ.update(
    user='QYu',
    experiment='QYu_GI_RT',
    md={'beam': '16.1 keV, low divergence', 'environment': 'vacuum, RT', 
        'holder': 'Al GI bar', 'saxs_sdd_m': 5},
)

# EDIT: sample names ([A-Za-z0-9-], use '_' only between fields) and piezo x (um) of each film
NAMES = {1: 'SR_2025S1', 2: 'SR_2025S2', 3: 'SR_2025S3', 4: 'SR_2025S4', 5: 'JL6', 6: 'JL7',
         7: 'JL8', 8: 'JL5', }
X_POS = {1: -55400, 2: -40000, 3: -26000, 4: -14000, 5: -1000,
         6: 15000, 7: 29000, 8: 40000,  }
Y0 = 7000          # piezo y (um) near the film surface; alignment scans +-800 um around it

SAMPLES = make_samples(NAMES, {k: (X_POS[k], Y0) for k in NAMES})

GI = dict(
    angles=(0.10, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6 ),   # incident angles (deg)
    arcs=(0, 20, 40 ),                # GIWAXS (900KW) at every arc
    saxs='max',                  # GISAXS (2M) with the highest arc only (40); 'all': every arc
                                 # >= 16 deg; False: no GISAXS
    t=1,                         # exposure (s)
    x_offsets=(-1000,0, 1000 ),              # e.g. (-1000, 0, 1000) for 3 spots per film
)

# EDIT (step 5): transmission bar -- name and piezo (x, y) in um of each film; only the keys in
# T_POS are measured.  Same names as GI by default; add backgrounds, e.g. 9: 'Empty', 10: 'Si-bare'
T_NAMES = dict(NAMES)
T_POS = {}          # e.g. {1: (-50000, 2000), 2: (-40000, 2000), 9: (30000, 2000)}

TSAMPLES = make_samples({k: T_NAMES[k] for k in T_POS}, T_POS, th=0)   # th 0: beam along the normal

TRANS = dict(
    t=1,                         # exposure (s)
    arcs=(0, 20, 40),            # WAXS (900KW) at every arc
    saxs='max',                  # SAXS (2M) with the highest arc only (40); 'all' / False as in GI
    offsets=((0, 0),),           # e.g. ((-500, 0), (0, 0), (500, 0)) for 3 spots per film (x, y um)
    md={'holder': 'transmission bar'},
)


def run_trans_samples(*which, **kw):
    """Plan: run_trans of TSAMPLES (or the given keys / names of it) with TRANS; kw override TRANS."""
    if not TSAMPLES:
        raise ValueError('no transmission samples: fill T_POS and re-run this file')
    return run_trans(select(TSAMPLES, *which) if which else TSAMPLES, **dict(TRANS, **kw))


show_samples()
if TSAMPLES:
    print('transmission (TSAMPLES):')
    show_samples(TSAMPLES)

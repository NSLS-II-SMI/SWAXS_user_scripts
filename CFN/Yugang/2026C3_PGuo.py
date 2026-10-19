"""
2026C3_PGuo.py -- Mon 2026-10-19 PM: P. Guo group, GIWAXS vs temperature on the Linkam (LN2)
in the vacuum chamber.

Same beam as the morning (16.1 keV low divergence, SAXS 2M at 5 m).  The Linkam GI stage sits
directly on the piezo; only the piezo moves.  GIWAXS at arc 0 and 20 deg; the 2M frame at
arc 20 comes for free (GISAXS).

Run sheet
---------
A) Air -> vacuum and Linkam hookup: README.md "Vacuum chamber" and "Linkam + LN2" (from the
   2026C1 runs).  Restart the Linkam IOC if needed (CSS XF:12ID-ES{LINKAM}:SysReset).
B) bsui
     proposal_swap(<pass id>); project_set('PGuo')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_PGuo.py
     preflight(); linkam_T()
C) Find the sample(s) on the Linkam with the camera; edit NAMES / POS, re-run this file.
     RE(startWAXS()); RE(shopen()); mov_sam(1); RE(snap())
D) Room temperature (alignment saved to json after every sample; run_gi uses the latest):
     align_gi_samples()
     RE(run_gi(**GI))
E) Temperature series: re-aligns at every T starting from the previous alignment (saved per
   T as alignment_PGuo_Linkam_GI_T<T>C_latest.json); the live Linkam T is in every name as _T..C.
     preview(run_gi_temperatures(TEMPS, **TSERIES, **GI))    # dry run
     RE(run_gi_temperatures(TEMPS, **TSERIES, **GI))
   Single temperature:  RE(linkam_goto(-100, lnp='Auto')); align_gi_samples(holder='PGuo_m100C')
                        RE(run_gi(aligned='PGuo_m100C', T=LThermal.temperature_current, **GI))
F) Finish: RE(linkam_goto(25)); RE(linkam_off())

Watch the LN2 dewar: if a temperature is not reached within `timeout` the series warns and
measures anyway (the names carry the real temperature).
"""

YZ.update(
    user='PGuo',
    experiment='PGuo_Linkam_GI',
    md={'beam': '16.1 keV, low divergence', 'environment': 'vacuum, Linkam LN2 stage',
        'holder': 'Linkam GI stage on piezo', 'saxs_sdd_m': 5},
)

# EDIT: names and piezo (x, y) in um of each sample on the Linkam stage
NAMES = {1: 'S1', 2: 'S2'}
POS = {1: (-3000, 0), 2: (3000, 0)}

SAMPLES = make_samples(NAMES, POS)

GI = dict(
    angles=(  0.06,    0.08,   0.10,  0.12,  0.15,  0.20,  ),
    arcs=(0, 20  ),
    t=1,
    x_offsets=(0,),
)

# EDIT with the group: Linkam setpoints in degC (LN2 cooling reaches about -190 C)
TEMPS = [25, -50, -100, -150, -180, 25]

TSERIES = dict(
    realign=True,       # re-align at each T (thermal contraction moves height / angle)
    settle=300,         # soak (s) after reaching T
    tol=1.0,            # degC
    timeout=3600,       # s to reach each T, then warn and continue
    rate=10,            # ramp degC/min
    lnp='Auto',         # LN2 pump in auto for cooling
    end_T=25,
    off_at_end=False,
)

show_samples()

"""
2026C3_PGuo.py -- Mon 2026-10-19 PM: P. Guo group in the vacuum chamber: GIWAXS + GISAXS at room
temperature without the Linkam (LINKAM = False, films on the Al GI bar as for QYu), and GIWAXS vs
temperature on the Linkam (LN2) (LINKAM = True).

Same beam as the morning (16.1 keV low divergence, SAXS 2M at 5 m).  The Al GI bar or the
Linkam GI stage sits directly on the piezo; only the piezo moves.  GIWAXS at every arc of
GI['arcs']; the 2M frame (GISAXS) comes with the highest arc (saxs='max').

Run sheet
---------
A) Air -> vacuum: README.md "Vacuum chamber".  For the Linkam also "Linkam + LN2" (from the
   2026C1 runs); restart the Linkam IOC if needed (CSS XF:12ID-ES{LINKAM}:SysReset).
B) Set LINKAM below, then bsui
     proposal_swap(<pass id>); project_set('PGuo')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_PGuo.py
     preflight()                      # and linkam_T() with LINKAM = True
     RE(startWAXS()); RE(shopen())

Room temperature, Linkam not used (LINKAM = False) -- as QYu in 2026C3_HZheng.py
R1) Load the Al GI bar.  With the camera find each film's piezo x and a rough surface height y;
    edit NAMES / X_POS / Y0 in the LINKAM = False block, re-run this file.
      mov_sam(1); RE(snap())
R2) Align (saved to alignment_PGuo_GI_RT_latest.json after every sample):
      align_gi_samples()
      manual fix of one sample:  mov_sam(3); ...align by hand...; mark_aligned(3)
R3) Measure.  Nothing reads or sets the Linkam; the names carry no _T..C:
      preview(run_gi_rt())            # dry run: file names + count
      RE(run_gi_rt())                 # all samples with GI
      RE(run_gi_rt(1, 3, t=5))        # a few, longer exposure
      RE(run_gi_rt(arcs=(0, 20, 40))) # the GISAXS frame then comes with arc 40

Temperature series on the Linkam (LINKAM = True)
C) Load the one sample on the Linkam GI stage, find it with the camera; edit NAMES / POS in the
   LINKAM = True block, re-run this file.
     linkam_T(); mov_sam(1); RE(snap())
D) Room temperature (alignment saved to json after every sample; run_gi uses the latest):
     align_gi_samples()
     RE(run_gi(**GI))
E) Temperatures set by hand.  Set T on the Linkam controller / CSS, or RE(linkam_goto(-100,
   lnp='Auto')); when it is there, run_gi_at_T reads T (only reads the Linkam), re-aligns starting
   from the last alignment and measures GI with the live T in the names (_T..C).  Each T's
   alignment is saved as alignment_PGuo_Linkam_GI_T<T>C_latest.json and as the latest one, so the
   next T starts from it:
     preview(run_gi_at_T())               # dry run
     RE(run_gi_at_T())                    # read T -> re-align -> GI
     RE(run_gi_at_T(settle=300))          # soak 5 min first
     RE(run_gi_at_T(realign=False, t=5))  # last alignment (e.g. after mark_aligned(1)), longer t
F) Automatic temperature series: re-aligns at every T starting from the previous alignment (saved
   per T as alignment_PGuo_Linkam_GI_T<T>C_latest.json); the live Linkam T is in every name as _T..C.
     preview(run_gi_temperatures(TEMPS, **TSERIES, **GI))    # dry run
     RE(run_gi_temperatures(TEMPS, **TSERIES, **GI))
G) Finish: RE(linkam_goto(25)); RE(linkam_off())

Watch the LN2 dewar: if a temperature is not reached within `timeout` the series warns and
measures anyway (the names carry the real temperature).
"""

LINKAM = False      # False: RT on the Al GI bar, Linkam not used; True: samples on the Linkam

if LINKAM:
    YZ.update(
        user='PGuo',
        experiment='PGuo_Linkam_GI',
        md={'beam': '16.1 keV, low divergence', 'environment': 'vacuum, Linkam LN2 stage',
            'holder': 'Linkam GI stage on piezo', 'saxs_sdd_m': 5},
    )

    # EDIT: name and piezo (x, y) in um of the sample on the Linkam GI stage (one sample)
    NAMES = {1: 'S1'}
    POS = {1: (0, 0)}
else:
    YZ.update(
        user='PGuo',
        experiment='PGuo_GI_RT',
        md={'beam': '16.1 keV, low divergence', 'environment': 'vacuum, RT, Linkam not used',
            'holder': 'Al GI bar', 'saxs_sdd_m': 5},
    )

    # EDIT: sample names ([A-Za-z0-9-], use '_' only between fields) and piezo x (um) of each film
    NAMES = {1: 'S1', 2: 'S2'}
    X_POS = {1: -40000, 2: -20000}
    Y0 = 7000          # piezo y (um) near the film surface; alignment scans +-800 um around it
    POS = {k: (X_POS[k], Y0) for k in NAMES}

SAMPLES = make_samples(NAMES, POS)

GI = dict(
    angles=(  0.06,    0.08,   0.10,  0.12,  0.15,  0.20,  ),
    arcs=(0, 20  ),     # GIWAXS (900KW) at every arc
    saxs='max',         # GISAXS (2M) with the highest arc only; 'all': every arc >= 16 deg; False: none
    t=1,
    x_offsets=(0,),
)


def run_gi_rt(*which, **kw):
    """Plan: GIWAXS + GISAXS at room temperature -- the Linkam is neither read nor set -- of
    SAMPLES (or the given keys / names of it) with GI; kw override GI."""
    return run_gi(select(SAMPLES, *which) if which else SAMPLES, **dict(GI, **kw))


def run_gi_at_T(samples=None, realign=True, settle=0, align_angle=0.15, tol=2.0, **kw):
    """
    Plan: GIWAXS + GISAXS at the Linkam temperature as it is now (set by hand); the Linkam is only
    read, never set.  Soak `settle` s, re-align starting from the latest alignment (realign=False:
    use it as is), save the result per T and as the latest, then run_gi with GI (kw override) and
    the live T in the names (_T..C).  A failed re-alignment keeps the previous values.
    """
    samples = _samples(samples)
    gi = dict(GI, **kw)
    T = yield from bps.rd(LThermal.temperature_current)
    T_set = yield from bps.rd(LThermal.temperature_setpoint)
    print(f'Linkam {T:.1f} C (setpoint {T_set:.1f} C)')
    if abs(T - T_set) > tol:
        print(f'WARNING: Linkam is {T - T_set:+.1f} C from its setpoint -- still ramping?')
    if settle:
        print(f'soaking {settle} s')
        yield from bps.sleep(settle)
        T = yield from bps.rd(LThermal.temperature_current)
    aligned = _saved_alignment()
    if realign or not aligned:
        new = yield from align_gi(samples, angle=align_angle, stage=gi.get('stage', 'piezo'),
                                  holder=f'{_holder()}_T{round(T)}C', start=aligned)
        aligned = _merge_alignment(aligned, new)
        save_alignment(aligned, _holder())
    yield from run_gi(samples, aligned, T=LThermal.temperature_current, **gi)


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

"""
2026C3_Murray.py -- Murray group (proposal 321244): transmission SAXS + WAXS.

A) Linkam (LN2), one sample at a time, about -50 .. 50 C.  First T set by hand and measured
   (measure_T, track_T), then an automatic T list (run_T_list).  Time track as in
   2026C3_JMayer.py when the potential is applied: one clock per sample (series_start()),
   frames named _<frame>_<s since series_start>s_..._T..C, the next spot every frame.
B) Room temperature, the multi-sample transmission holder (~14 slots): run_rt.

SAXS (2M) and WAXS (900KW) in the same exposure at WAXS arc 20.  16.1 keV low divergence, SAXS
2M at 5 m (EDIT YZ md below if the setup changes).

Run sheet
---------
0) bsui
     proposal_swap(321244); project_set('Murray')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_Murray.py
     preflight(); linkam_T()
   after closing the hutch: RE(shopen()); before opening it: RE(shclose())
1) Calibrant: RE(measure_wsaxs('AgBH', t=1, arc=20))

Linkam (A)
2) Mount the Linkam, LN2 (README "Linkam + LN2 in vacuum"; restart the IOC if needed: CSS
   XF:12ID-ES{LINKAM}:SysReset).  In air, purge the Linkam with dry N2 below ~5 C or the
   windows frost.  Center the sample window with the camera, here('x', 'y') -> LINKAM_POS,
   re-run this file.
3) Load a sample:
     new_sample('PbS22B', note='...')    # moves to LINKAM_POS; resets the clock
     RE(measure_wsaxs('test', 1))        # quick look at arc 20 ('test' is skipped by the analysis)
     preview(measure_T()); RE(measure_T())   # RT: SAXS + WAXS at arc 20, names ..._T24.9C_...
4) T by hand: set it on the Linkam CSS screen, or
     set_T(-50)                          # TSERIES rate / LN2 pump / tol; waits until there
     RE(measure_T())                     # one frame per spot at this T; the Linkam is only read
     RE(measure_T(settle=120, t=2))      # soak 2 min first, longer exposure
   time track at this T (as run_insitu in 2026C3_JMayer.py):
     series_start('-50 C')               # t = 0 (else the clock of this sample runs on)
     RE(track_T())                       # a frame every 30 s for 3 min, the next spot each
     RE(track_T(duration=600, interval=60))
   Ctrl-C, RE.stop() ends a track early (Ctrl-C, RE.resume() continues it).
5) Automatic T list (TEMPS, TSERIES, TRACK below):
     series_start('T list')              # t = 0 for the list (else the sample's clock runs on)
     preview(run_T_list())               # dry run: names and count (2 frames per T shown)
     RE(run_T_list())                    # per T: ramp, soak, track; Linkam to end_T at the end
     RE(run_T_list([0, 25, 50], duration=60, settle=0))
     RE(run_T_list(max_cycles=1))        # one frame per T
   after RE.stop(): RE(run_T_list([the remaining temperatures]))
   Watch the LN2 dewar: a T not reached within `timeout` is measured anyway (the names carry
   the T read at each frame).
6) Next sample: set_T(25), unload, back to 3).  At the end: RE(linkam_off())

Room-temperature holder (B)
7) Mount the holder; center each slot with the camera; edit RT_NAMES / RT_X / RT_Y (name the
   empty-slot / solvent backgrounds too), re-run this file:
     show_samples(RT_SAMPLES); mov_sam(1, RT_SAMPLES); RE(measure_wsaxs('test', 1))
8)   preview(run_rt()); RE(run_rt())     # all slots of RT_X: SAXS + WAXS at arc 20
     RE(run_rt(3, 'Empty', t=5))         # a few, longer exposure
     RE(run_rt(arcs=(0, 20)))            # + WAXS at arc 0 (the 2M stays with arc 20)

Ctrl-C to pause; RE.resume() / RE.stop() / RE.abort().
"""

YZ.update(
    user='Murray',
    experiment='Murray',
    md={'beam': '16.1 keV, low divergence', 'saxs_sdd_m': 5},
)

LINKAM_MD = {'experiment': 'Murray_Linkam', 'holder': 'Linkam LN2 stage',
             'environment': 'Linkam, LN2'}           # EDIT: + air / N2 purge / vacuum
RT_MD = {'experiment': 'Murray_RT', 'holder': 'RT transmission holder',
         'environment': 'room temperature'}

# EDIT: piezo x / y (um) of the sample in the Linkam window; th 0 = beam along the normal.
# Add sx=..., sy=... (Huber, mm) to move the Huber there as well.
LINKAM_POS = dict(x=0.0, y=0.0, th=0.0)

# EDIT with the group: Linkam setpoints (degC) of run_T_list, in order
TEMPS = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]

TSERIES = dict(             # how set_T / run_T_list drive the Linkam
    rate=10,                # ramp (degC/min)
    lnp='Auto',             # LN2 pump in auto (cooling)
    tol=1.0,                # degC
    settle=60,              # s soak at each T of run_T_list before its track (0: track on arrival)
    timeout=1800,           # s to reach a T, then warn and measure anyway
    end_T=25,               # run_T_list: Linkam setpoint after the list (not measured); None = stay
    off_at_end=False,
)

TRACK = dict(               # time track: track_T, and at every T of run_T_list
    arc=20, saxs=True,      # 2M + 900KW in every frame
    t=1,
    interval=30,            # frame start-to-start (s); 0 = back-to-back
    duration=180,           # s per track_T call / per T of run_T_list
    spots=(0,),             # offsets (um) on spot_axis, the next one every frame, e.g. (-200, 0, 200)
    spot_axis='x',
)

MEASURE = dict(             # one set of frames at the present T: measure_T
    arcs=(20,), saxs='max', # 2M + 900KW in one exposure at arc 20
    t=1,
    offsets=((0, 0),),      # (x, y) um spots, e.g. ((-200, 0), (0, 0), (200, 0))
)

# EDIT: RT transmission holder -- name and piezo x (um) of each slot; only the slots in RT_X
# are measured.  Evenly spaced: RT_X = {k: X1 + (k - 1) * PITCH for k in RT_NAMES}
RT_NAMES = {1: 'S1', 2: 'S2', 3: 'S3', 4: 'S4', 5: 'S5', 6: 'S6', 7: 'S7',
            8: 'S8', 9: 'S9', 10: 'S10', 11: 'S11', 12: 'S12', 13: 'S13', 14: 'S14'}
RT_X = {}                   # e.g. {1: -42000, 2: -35500, ...}
RT_Y = 0.0                  # piezo y (um) of the slot centers
RT_SAMPLES = make_samples({k: RT_NAMES[k] for k in RT_X}, {k: (RT_X[k], RT_Y) for k in RT_X}, th=0)

TRANS = dict(               # RT holder: run_rt
    arcs=(20,), saxs='max', # 2M + 900KW in one exposure at arc 20
    t=1,
    offsets=((0, 0),),      # (x, y) um spots per slot, e.g. ((0, -500), (0, 0), (0, 500))
)

if globals().get('LK_SAMPLE') is None:      # re-running this file keeps the sample in the Linkam,
    LK_SAMPLE = None                        # at the (edited) LINKAM_POS
else:
    LK_SAMPLE = dict({k: v for k, v in LK_SAMPLE.items() if k not in AXES}, **LINKAM_POS)
SAMPLES = [LK_SAMPLE] if LK_SAMPLE else []


def goto_linkam():
    """Console: move to LINKAM_POS."""
    RE(move_to(LINKAM_POS))
    here(*[a for a in LINKAM_POS if a in AXES])


def new_sample(name, move=True, **info):
    """
    Console: the sample just loaded in the Linkam -> files Murray_<name>_...
    info = metadata of this sample (note=..., solvent=...).  Resets the clock (series_start()
    or the first track starts it again); move=True also does goto_linkam().
    """
    global LK_SAMPLE, SAMPLES
    LK_SAMPLE = dict(make_samples({1: name}, {1: LINKAM_POS})[0], **info)
    SAMPLES = [LK_SAMPLE]
    YZ_SERIES.update(t0=None, cycle=0)
    if move:
        goto_linkam()
    show_samples()


def set_T(T, settle=0, **kw):
    """Console: Linkam to T (degC) with the TSERIES rate / LN2 pump / tol / timeout (kw
    override); waits until it is there, then soaks `settle` s."""
    lk = dict(TSERIES, settle=settle, **kw)
    RE(linkam_goto(T, **{k: lk[k] for k in ('tol', 'settle', 'timeout', 'rate', 'lnp')}))
    print(f'Linkam {linkam_T():.1f} C')


def measure_T(settle=0, **kw):
    """Plan: SAXS + WAXS (MEASURE; kw override) of the Linkam sample at the Linkam T as it is
    now (set by hand or with set_T; the Linkam is only read), after a soak of `settle` s.
    The T read at each frame is in its name (_T..C); no time index."""
    s = _sample()
    yield from _linkam_now(settle)
    yield from run_trans([s], **_linkam_kw(MEASURE, kw))


def track_T(**kw):
    """Plan: time track of the Linkam sample at the present T (TRACK; kw override), as
    run_insitu in 2026C3_JMayer.py: a SAXS + WAXS frame every `interval` s for `duration` s,
    the next spot each frame; names _<frame>_<s since series_start()>s_..._T..C (the clock
    starts at the first frame if it is not running).  The Linkam is only read."""
    s = _sample()
    yield from _linkam_now()
    yield from run_series([s], **_linkam_kw(TRACK, kw))


def run_T_list(temps=None, **kw):
    """
    Plan: automatic T series of the Linkam sample.  For each T of `temps` (default TEMPS):
    Linkam to T (TSERIES: rate, LN2 pump, tol, timeout), soak `settle` s, then the time track
    at that T (TRACK: a frame every `interval` s for `duration` s; max_cycles=N: N frames).
    One clock and frame counter for the whole list -- started here unless it is running -- so
    the names _<frame>_<s since series_start()>s_..._T..C run on across the temperatures.  At the
    end the Linkam goes to end_T (not measured) and, with off_at_end, is switched off.
    kw override TSERIES and TRACK, e.g. run_T_list([0, 25], duration=60, settle=0).
    """
    s = _sample()
    temps = list(TEMPS if temps is None else temps)
    lk = {k: kw.pop(k, v) for k, v in TSERIES.items()}
    track = dict(TRACK, **kw)
    T_now = yield from bps.rd(LThermal.temperature_current)
    path = [T_now] + temps
    ramp = sum(abs(b - a) for a, b in zip(path, path[1:])) / lk['rate'] if lk['rate'] else 0
    per_T = (lk['settle'] + track['duration']) / 60
    print(f'run_T_list: {s["name"]}, {len(temps)} temperatures {temps} C, ~{ramp + len(temps) * per_T:.0f} '
          f'min (ramps ~{ramp:.0f} min + {per_T:.1f} min soak and track per T)')
    if YZ_SERIES['t0'] is None and not _previewing():
        series_start('(auto: run_T_list start)')
    for i, T in enumerate(temps):
        print(f'\n##### {s["name"]}: T {i + 1}/{len(temps)} = {T} C #####')
        yield from linkam_goto(T, tol=lk['tol'], settle=lk['settle'], timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])
        name_T = {'T': T} if _previewing() else {}        # a dry run never sets the Linkam
        yield from run_series([s], **_linkam_kw(track, name_T, T_setpoint_C=T))
    if lk['end_T'] is not None:
        yield from linkam_goto(lk['end_T'], tol=lk['tol'], settle=0, timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])
    if lk['off_at_end']:
        yield from linkam_off()


def run_rt(*which, **kw):
    """Plan: run_trans of RT_SAMPLES (or the given keys / names of it) with TRANS; kw override
    TRANS.  The Linkam is not read."""
    if not RT_SAMPLES:
        raise ValueError('no RT holder positions: fill RT_X and re-run this file')
    trans = dict(TRANS, **kw)
    trans['md'] = dict(RT_MD, **(trans.get('md') or {}))
    return run_trans(select(RT_SAMPLES, *which) if which else RT_SAMPLES, **trans)


def _sample():
    if not LK_SAMPLE:
        raise ValueError("no sample in the Linkam: new_sample('name') first")
    return LK_SAMPLE


def _linkam_kw(defaults, kw, **md):
    """defaults + kw for run_trans / run_series, with the Linkam T read at each frame in the
    name (_T..C), the setpoint recorded and LINKAM_MD (+ md) in the metadata."""
    out = dict(defaults, **kw)
    run_md = dict(LINKAM_MD)
    run_md.update(md)
    run_md.update(out.get('md') or {})
    out['md'] = run_md
    out.setdefault('T', LThermal.temperature_current)
    out['readings'] = list(out.get('readings', ())) + [LThermal.temperature_setpoint]
    return out


def _linkam_now(settle=0):
    """Plan: print the Linkam T and setpoint (warn if it is still ramping), soak `settle` s."""
    T = yield from bps.rd(LThermal.temperature_current)
    T_set = yield from bps.rd(LThermal.temperature_setpoint)
    print(f'Linkam {T:.1f} C (setpoint {T_set:.1f} C)')
    if abs(T - T_set) > TSERIES['tol']:
        print(f'WARNING: Linkam is {T - T_set:+.1f} C from its setpoint -- still ramping? '
              f'(the names carry the T read at each frame)')
    if settle:
        print(f'soaking {settle} s')
        yield from bps.sleep(settle)


print(f'Murray: LINKAM_POS {LINKAM_POS}; '
      + (f'in the Linkam: {LK_SAMPLE["name"]}' if LK_SAMPLE else "new_sample(name) first"))
if RT_SAMPLES:
    print('RT holder (RT_SAMPLES):')
    show_samples(RT_SAMPLES)
else:
    print('RT holder: fill RT_X')

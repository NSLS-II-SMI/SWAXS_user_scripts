"""
1) load sample
2) RE(pump_waxs())    #close the chamber and do pump chamber
2.1) maually open the 2:GV-6
2.5) use Huber Stage coordiates: X and Y to postion your sample
3) RE(restartWAXS())  #start the waxs after doing pump
4) RE(shopen())       #open the beamline photon shutter
5) collect data
6)  RE(shclose())     #close the shutter
7)  RE(vent_waxs())  #vent the chamber

8) new_sample('RR_85_OD2', note='...')    # Huber to LINKAM_POS (None: stays); resets clock + spots
RE(measure_wsaxs('test', 1))        # for quick test

RE(measure_T())   # RT: SAXS + WAXS at arc 20, names ..._T24.9C_...



series_start('T list')              # t = 0 for the list (else the sample's clock runs on)
RE(run_T_list(   [-50, 50, -50, 50, -50, 50,  25] , duration=60, settle=0))

RE(run_T_ramp([-50, 50, -50, 50, -50, 50, 25], interval=5))



new_sample('test', note='')
+
RE(run_T_ramp([ 50 ], interval=30))

new_sample('BR_CIS_ZnS_3_1_1wp', note='')

RE(run_T_list(   [5] , duration=60, settle=0))

NOTES:

huber
X: -3.3
T -12.6
Z: -15

sample_id(user_name='test', sample_name=f'test')
collect_twsaxs('AgBH', t=1, arcs=(0, 20, 40))
data saved in: /nsls2/users/yuzhang/smi_proposals_link/2026-3/pass-321244/projects/Murray/user_data


new_sample('RR_85_OD2', note='...') 
new_sample('RR_85_OD2_TCycling', note='')
series_start('T list')  
RE(run_T_ramp([-50, 50, -50, 50, -50, 50, 25], interval=5))


new_sample('RR_85_OD2_TCycling2', note='')
series_start('T list')  
RE(run_T_ramp([ -50  ], interval=15)) # from 25 to -26, got motor waming up problem,
wait for the motor X cooling down
RE(run_T_ramp([ 50  ], interval=15))

RE(run_T_ramp([ -50  ], interval=15)) # from 25 to -26, got motor waming up problem,
wait for the motor X cooling down
RE(run_T_ramp([ 50  ], interval=15))

RE(run_T_ramp([ -50  ], interval=15)) # from 25 to -26, got motor waming up problem,
wait for the motor X cooling down
RE(run_T_ramp([ 50  ], interval=15))

RE(run_T_ramp([ 15  ], interval=30))




new_sample('BR_CISZnS_TChange', note='')



2026C3_Murray.py -- Murray group (proposal 321244): transmission SAXS + WAXS.

A) Linkam (LN2) on the Huber -- the piezo is not used -- one sample at a time, about
   -50 .. 50 C.  First T set by hand and measured (measure_T, track_T), then an automatic T
   list (run_T_list).  Time track as in 2026C3_JMayer.py when the potential is applied: one
   clock per sample (series_start()), frames named _<frame>_<s since series_start>s_..._T..C.
   Every frame on a fresh spot: the next of POS_XY_LIST (Huber sx/sy grid in snake order), across
   calls and temperatures.  The _x/_y/_z name tokens are the Huber sx/sy/sz (mm).
B) Room temperature, the multi-sample transmission holder (~14 slots) on the piezo: run_rt.

SAXS (2M) and WAXS (900KW) in the same exposure at WAXS arc 20.  16.1 keV low divergence, SAXS
2M at 5 m (EDIT YZ md below if the setup changes).

Run sheet
---------
0) bsui
     proposal_swap(321244); project_set('Murray')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_Murray.py
     preflight(); get_T()                # Linkam T, setpoint, on/off, LN2 pump
   after closing the hutch: RE(shopen()); before opening it: RE(shclose())
1) Calibrant: move it into the beam by hand, then
     collect_twsaxs('AgBH')              # WAXS at arcs 0, 20, 40; SAXS at 40 only; nothing else moves
     collect_twsaxs('AgBH', t=2)

Linkam (A)
2) Mount the Linkam on the Huber, LN2 (README "Linkam + LN2 in vacuum"; restart the IOC if
   needed: CSS XF:12ID-ES{LINKAM}:SysReset).  In air, purge the Linkam with dry N2 below ~5 C
   or the windows frost.  Center the sample window with the camera by moving the Huber (sx, sy;
   keep the LN2 lines free), here('sx', 'sy') -> LINKAM_POS, re-run this file -- or leave
   LINKAM_POS at None: new_sample() then takes the Huber position as it is.
   Spots: POS_XY_LIST = snake_xy(nx, ny, dx, dy) around that center (mm), inside the window,
   steps larger than the beam; check the corners with the camera, re-run this file.
3) Load a sample:
     new_sample('PbS22B', note='...')    # Huber to LINKAM_POS (None: stays); resets clock + spots
     RE(measure_wsaxs('test', 1))        # quick look at arc 20 ('test' is skipped by the analysis)
     preview(measure_T()); RE(measure_T())   # RT: SAXS + WAXS at arc 20, names ..._T24.9C_...
4) T by hand: set it on the Linkam CSS screen, or
     get_T()                             # T now (returned), setpoint, ramp, on/off, LN2 pump
     set_T(-50)                          # TSERIES rate / LN2 pump / tol; waits until there
     RE(measure_T())                     # one frame, on the next spot; the Linkam is only read
     RE(measure_T(settle=120, t=1))      # soak 2 min first, longer exposure
     RE(measure_T(n_spots=3))            # 3 frames on the next 3 spots
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
   after RE.stop(): RE(run_T_list([the remaining temperatures]))   (the spots run on)
   Measured all the way through the ramps instead (no soak, no duration):
     preview(run_T_ramp([-50, 50, -50, 50, -50, 50, 25], interval=5))   # estimate + names
     RE(run_T_ramp([-50, 50, -50, 50, -50, 50, 25], interval=5))
       # Linkam -> -50 at the TSERIES rate, a frame every 5 s from the start; at -50 (within
       # tol) the setpoint goes to 50 at once, frames go on; ... ends when 25 is reached
     RE(run_T_ramp([-50, 50, 25], interval=5, hold=60))   # + 1 min measured at each target
     RE(run_T_ramp([50], interval=15))   # stays at 50 at the end; return_RT=True: then to 25
   Spots: LK_SPOT['next'] = frames taken on this sample so far (the next spot is
   POS_XY_LIST[next % len]); all used -> starts over (warning): use a larger grid.
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

# EDIT: Huber sx / sy (mm) of the sample in the Linkam window -- the Linkam is on the Huber and
# the piezo is never moved for it.  None: the Huber position when new_sample() is called.
LINKAM_POS = dict(sx=None, sy=None, sz=-18)
LINKAM_XYZ = ('sx', 'sy', 'sz')     # Linkam names: _x/_y/_z = Huber sx/sy/sz (mm)


def snake_xy(nx, ny, dx, dy, r_max=None):
    """Huber (sx, sy) offsets (mm) of an nx x ny grid centered on (0, 0), steps dx, dy, in snake
    order: row by row in sy, each row along sx, every other row reversed (sy moves once per row).
    r_max (mm): only the spots within this radius, e.g. inside a round window."""
    xs = [(i - (nx - 1) / 2) * dx for i in range(nx)]
    out = []
    for j in range(ny):
        y = (j - (ny - 1) / 2) * dy
        for x in (xs if j % 2 == 0 else xs[::-1]):
            if r_max is None or np.hypot(x, y) <= r_max + 1e-9:
                out.append((round(x, 4), round(y, 4)))
    return out


# EDIT: spots on the Linkam sample -- Huber (sx, sy) offsets (mm) from its center (LINKAM_POS),
# in the order they are used.  Every frame (measure_T, track_T, run_T_list) takes the next unused
# spot of the sample, also across calls and temperatures, so the dose is spread; when all are
# used it starts over at the first (warning).  Keep the grid inside the window and the steps
# larger than the beam.  Rows along sx: the Huber y motor heats up when it moves a lot.
# Or a list: [(0, 0), (0.2, 0), (0.4, 0), (0.4, 0.1), ...]
POS_XY_LIST = snake_xy(nx=3, ny=3, dx=0.2, dy=0.1)     # 25 spots over 0.8 x 0.4 mm

# EDIT with the group: Linkam setpoints (degC) of run_T_list, in order
#TEMPS = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]
TEMPS = [-50, 40, -50, 40, -50, 25]
TEMPS = [-50, 40, -50, 40, -50, 25]

TSERIES = dict(             # how set_T / run_T_list drive the Linkam
    rate=2,                # ramp (degC/min)
    lnp='Auto',             # LN2 pump in auto (cooling)
    tol=1.0,                # degC
    settle=0,              # s soak at each T of run_T_list before its track (0: track on arrival)
    timeout=1800,           # s to reach a T, then warn and measure anyway
    end_T=25,               # run_T_list (and run_T_ramp with return_RT=True): Linkam setpoint after
                            # the list (not measured); None = stay (run_T_ramp: 25)
    off_at_end=False,
)

TRACK = dict(               # time track: track_T, and at every T of run_T_list
    arc=20, saxs=True,      # 2M + 900KW in every frame
    t=1,
    interval=5,            # frame start-to-start (s); 0 = back-to-back
    duration=180,           # s per track_T call / per T of run_T_list
)                           # every frame on the next spot of POS_XY_LIST

MEASURE = dict(             # one set of frames at the present T: measure_T
    arcs=(20,), saxs='max', # 2M + 900KW in one exposure at arc 20
    t=1,
    n_spots=1,              # frames, each on the next spot of POS_XY_LIST
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
    LK_SAMPLE = None                        # at the edited LINKAM_POS (None: where it was)
else:
    LK_SAMPLE = dict(LK_SAMPLE, **{a: v for a, v in LINKAM_POS.items() if v is not None})
SAMPLES = [LK_SAMPLE] if LK_SAMPLE else []
LK_SPOT = globals().get('LK_SPOT') or dict(next=0)    # frames taken on it = next POS_XY_LIST spot


def new_sample(name, move=True, **info):
    """
    Console: the sample just loaded in the Linkam -> files Murray_<name>_...  Its position is the
    Huber sx / sy of LINKAM_POS (None: the Huber position now); move=True moves the Huber there
    (mov_sam(1) does it later).  info = metadata of this sample (note=..., solvent=...).
    Resets the clock (series_start() or the first track starts it again) and the spots: the
    first frame goes to POS_XY_LIST[0].
    """
    global LK_SAMPLE, SAMPLES
    pos = {a: AXES[a].position if v is None else v for a, v in LINKAM_POS.items()}
    LK_SAMPLE = dict(make_samples({1: name}, {1: pos})[0], **info)
    SAMPLES = [LK_SAMPLE]
    YZ_SERIES.update(t0=None, cycle=0)
    LK_SPOT['next'] = 0
    if move:
        RE(move_to(LK_SAMPLE))
    show_samples()


def set_T(T, settle=0, **kw):
    """Console: Linkam to T (degC) with the TSERIES rate / LN2 pump / tol / timeout (kw
    override); waits until it is there, then soaks `settle` s."""
    lk = dict(TSERIES, settle=settle, **kw)
    RE(linkam_goto(T, **{k: lk[k] for k in ('tol', 'settle', 'timeout', 'rate', 'lnp')}))
    get_T()


def get_T(show=True):
    """Console: the Linkam T now (degC), returned (T = get_T()).  show=True also prints the
    setpoint, ramp rate, heating/cooling on or off and the controller status (at setpoint,
    LN2 pump, error).  Only reads the Linkam; no RE."""
    T = linkam_T()
    if not show:
        return T
    T_set = LThermal.temperature_setpoint.get()
    info = [f'setpoint {T_set:.1f} C ({T - T_set:+.1f})',
            f'ramp {LThermal.temperature_rate_setpoint.get():g} C/min',
            'on' if LThermal.cmd.get() else 'OFF (not heating/cooling)']
    try:
        code = int(LThermal.status_code.get())     # bits: 1 error, 2 at setpoint, 8 pump, 16 pump auto
    except Exception:                               # no status PV / not connected: the T is enough
        code = None
    if code is not None:
        info += ['at setpoint' if code & 2 else 'not at setpoint',
                 'LN2 pump ' + ('on' if code & 8 else 'off') + (' (auto)' if code & 16 else '')]
        if code & 1:
            info.append('CONTROLLER ERROR')
    print(f'Linkam {T:.1f} C: ' + ', '.join(info))
    return T


def measure_T(settle=0, **kw):
    """Plan: SAXS + WAXS (MEASURE; kw override) of the Linkam sample at the Linkam T as it is
    now (set by hand or with set_T; the Linkam is only read), after a soak of `settle` s:
    n_spots frames, each on the next spot of POS_XY_LIST (all arcs of a frame on its spot).
    The T read at each frame is in its name (_T..C); no time index."""
    s = _sample()
    yield from _linkam_now(settle)
    opts = _linkam_kw(MEASURE, kw)
    check_arcs(opts['arcs'])                        # a refused arc uses no spot up
    spots = _spot_counter()
    at = [_next_spot(s, spots) for _ in range(opts.pop('n_spots'))]
    yield from _huber_names(run_trans(at, **opts))


def track_T(**kw):
    """Plan: time track of the Linkam sample at the present T (TRACK; kw override), as
    run_insitu in 2026C3_JMayer.py: a SAXS + WAXS frame every `interval` s for `duration` s
    (max_cycles=N: N frames), each on the next spot of POS_XY_LIST; names
    _<frame>_<s since series_start()>s_..._T..C (the clock starts at the first frame if it is
    not running).  The Linkam is only read."""
    s = _sample()
    yield from _linkam_now()
    yield from _huber_names(_track(s, _spot_counter(), **_linkam_kw(TRACK, kw)))


def run_T_list(temps=None, **kw):
    """
    Plan: automatic T series of the Linkam sample.  For each T of `temps` (default TEMPS):
    Linkam to T (TSERIES: rate, LN2 pump, tol, timeout), soak `settle` s, then the time track
    at that T (TRACK: a frame every `interval` s for `duration` s; max_cycles=N: N frames), each
    frame on the next spot of POS_XY_LIST.  One clock and frame counter for the whole list --
    started here unless it is running -- so the names _<frame>_<s since series_start()>s_..._T..C
    run on across the temperatures, and so do the spots.  At the end the Linkam goes to end_T
    (not measured) and, with off_at_end, is switched off.
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
    spots = _spot_counter()
    for i, T in enumerate(temps):
        print(f'\n##### {s["name"]}: T {i + 1}/{len(temps)} = {T} C #####')
        yield from linkam_goto(T, tol=lk['tol'], settle=lk['settle'], timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])
        name_T = {'T': T} if _previewing() else {}        # a dry run never sets the Linkam
        yield from _huber_names(_track(s, spots, **_linkam_kw(track, name_T, T_setpoint_C=T)))
    if lk['end_T'] is not None:
        yield from linkam_goto(lk['end_T'], tol=lk['tol'], settle=0, timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])
    if lk['off_at_end']:
        yield from linkam_off()


def run_T_ramp(temps=None, hold=0, return_RT=False, **kw):
    """
    Plan: T ramps of the Linkam sample, measured all the way.  The Linkam goes to the first T of
    `temps` (default TEMPS) at the TSERIES rate and the frames start at once: a SAXS + WAXS frame
    every `interval` s (TRACK), each on the next spot of POS_XY_LIST.  As soon as the Linkam is
    within tol of the target (checked after every frame) -- and `hold` s later, still measuring --
    the next T is set; no soak, no duration.  The frames end when the last T is reached; the
    Linkam stays there (return_RT=True: then to end_T, 25 C, not measured).  A T not reached
    within its ramp time + timeout is left with a warning (the next T is set).  One clock and
    frame counter (started here unless it is running): names
    _<frame>_<s since series_start()>s_..._T<T read at the frame>C; the target is T_setpoint_C
    in the metadata.
        RE(run_T_ramp([-50, 50, -50, 50, -50, 50, 25], interval=5))
        RE(run_T_ramp([50], interval=15))                    # to 50, stays at 50
        RE(run_T_ramp([50], interval=15, return_RT=True))    # then back to 25
    kw override TSERIES and TRACK (duration is not used).
    """
    s = _sample()
    temps = list(TEMPS if temps is None else temps)
    if not temps:
        raise ValueError('no temperatures')
    lk = {k: kw.pop(k, v) for k, v in TSERIES.items()}
    track = _linkam_kw(dict(TRACK, **kw), {}, T_ramp_C_per_min=lk['rate'])
    track.update(duration=None, max_cycles=None)
    md = track['md']                                 # T_setpoint_C: the target of each frame
    dry = _previewing()
    T_now = yield from bps.rd(LThermal.temperature_current)
    if lk['rate']:
        path = [T_now] + temps
        minutes = sum(abs(b - a) for a, b in zip(path, path[1:])) / lk['rate'] + len(temps) * hold / 60
        frames = minutes * 60 / max(track['interval'], track['t'] + 3)
        print(f'run_T_ramp: {s["name"]}, {temps} C at {lk["rate"]:g} C/min, a frame every '
              f'{track["interval"]} s all the way: ~{minutes:.0f} min, ~{frames:.0f} frames '
              f'(~{frames / len(POS_XY_LIST or [0]):.0f} on each spot of POS_XY_LIST)')
    if YZ_SERIES['t0'] is None and not dry:
        series_start('(auto: run_T_ramp start)')
    at = dict(i=-1)                                  # target index, set time, reached time, frames

    def next_T():
        at['i'] += 1
        if at['i'] == len(temps):
            return True
        T = temps[at['i']]
        T_from = yield from bps.rd(LThermal.temperature_current)
        late = abs(T - T_from) / lk['rate'] * 60 if lk['rate'] else 0
        at.update(T=T, since=time.time(), late=late + lk['timeout'], reached=None, n=0)
        md['T_setpoint_C'] = T
        print(f'\n##### {s["name"]}: Linkam -> {T} C ({at["i"] + 1}/{len(temps)}), from {T_from:.1f} C; '
              f'measuring on the way #####')
        yield from _put(LThermal.temperature_setpoint, round(float(T), 1))
        return False

    def step():
        """Plan, after every frame: on to the next T once this one is reached (+ hold)."""
        at['n'] += 1
        T_now = yield from bps.rd(LThermal.temperature_current)
        if at['reached'] is None:
            if at['n'] >= 2 if dry else abs(T_now - at['T']) <= lk['tol']:   # a dry run: 2 frames per T
                print(f'Linkam at {at["T"]} C ({T_now:.1f} C) after {time.time() - at["since"]:.0f} s')
                at['reached'] = time.time()
            elif time.time() - at['since'] > at['late']:
                print(f'WARNING: Linkam did not reach {at["T"]} C in {at["late"]:.0f} s (now {T_now:.1f} C); '
                      f'going on (the names carry the T read at each frame)')
                at['reached'] = time.time() - hold
        if at['reached'] is not None and (dry or time.time() - at['reached'] >= hold):
            return (yield from next_T())
        return False

    track['after'] = step
    if lk['rate'] is not None:
        yield from _put(LThermal.temperature_rate_setpoint, lk['rate'])
    if lk['lnp'] is not None:
        yield from _put(LThermal.lnp_mode_set, lk['lnp'])
    yield from next_T()
    yield from _put(LThermal.cmd, 1)
    yield from _huber_names(_track(s, _spot_counter(), **track))
    if return_RT:
        T_RT = 25 if lk['end_T'] is None else lk['end_T']
        print(f'return_RT: Linkam -> {T_RT} C (not measured)')
        yield from linkam_goto(T_RT, tol=lk['tol'], settle=0, timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])
    #if lk['off_at_end']:
    #    yield from linkam_off()


def run_rt(*which, **kw):
    """Plan: run_trans of RT_SAMPLES (or the given keys / names of it) with TRANS; kw override
    TRANS.  The Linkam is not read."""
    if not RT_SAMPLES:
        raise ValueError('no RT holder positions: fill RT_X and re-run this file')
    trans = dict(TRANS, **kw)
    trans['md'] = dict(RT_MD, **(trans.get('md') or {}))
    return run_trans(select(RT_SAMPLES, *which) if which else RT_SAMPLES, **trans)


def collect_twsaxs(sample_name, t=1, arcs=(0, 20, 40)):
    """Console: transmission WAXS at every arc of `arcs` and SAXS (2M) with the highest only, of
    the sample now in the beam (moved there by hand, e.g. the AgBH calibrant).  Only the WAXS
    arc moves; names Murray_<sample_name>_x.._y.._z.._expt<t>s."""
    RE(run_trans([{'name': clean_name(sample_name)}], t=t, arcs=arcs, saxs='max'))


def _sample():
    if not LK_SAMPLE:
        raise ValueError("no sample in the Linkam: new_sample('name') first")
    return LK_SAMPLE


def _spot_counter():
    """LK_SPOT; a dry run gets a copy, so it uses no spots up."""
    return dict(LK_SPOT) if _previewing() else LK_SPOT


def _next_spot(s, spots):
    """The sample dict s at its next spot of POS_XY_LIST (Huber sx, sy = center + offset; the
    index is in the metadata as 'spot').  After the last spot it starts over at the first."""
    if not POS_XY_LIST:
        raise ValueError('POS_XY_LIST is empty: at least [(0, 0)]')
    i = spots['next'] % len(POS_XY_LIST)
    if i == 0 and spots['next']:
        print(f'WARNING: all {len(POS_XY_LIST)} spots of POS_XY_LIST used; starting again at '
              f'spot 0 (exposed before)')
    spots['next'] += 1
    dx, dy = POS_XY_LIST[i]
    print(f'spot {i} of {len(POS_XY_LIST)}: sx {dx:+.3f}, sy {dy:+.3f} mm from the center')
    return dict(s, sx=s['sx'] + dx, sy=s['sy'] + dy, spot=i)


def _track(s, spots, arc=20, saxs=True, waxs_det=True, t=1, interval=30, duration=180,
           max_cycles=None, T=None, readings=(), extra=None, md=None, after=None):
    """Plan: run_series of the one sample s in transmission (same clock, frame counter and
    names), but every frame on the next spot of POS_XY_LIST (Huber sx and sy).  duration=None:
    no time limit.  after: plan factory run after every frame; it returns True to end the track
    (a dry run then ends only through it)."""
    check_arcs([arc])
    dets = [pil900KW] if waxs_det else []
    if saxs and arc >= YZ['saxs_min_arc']:
        dets.append(pil2M)
    if not dets:
        raise ValueError('no detector: waxs_det=False and the 2M is shadowed at this arc')
    ser = dict(YZ_SERIES) if _previewing() else YZ_SERIES   # a dry run leaves clock and counter
    if ser['t0'] is None:
        if ser is YZ_SERIES:
            series_start('(auto: track start)')
        else:
            ser['t0'] = time.time()
    if _previewing() and after is None:
        max_cycles = min(max_cycles or 2, 2)
        print('(preview) showing 2 frames')
    print(f'track: {s["name"]}, a frame every {interval or "back-to-back"} s'
          + (f' for {duration} s' if duration is not None else '')
          + f', each on the next spot; t0 = {_iso(ser["t0"])}')
    yield from bps.mv(waxs, arc)
    t_start = time.time()
    n = 0
    while ((duration is None or time.time() - t_start < duration)
           and (max_cycles is None or n < max_cycles)):
        t_frame = time.time()
        at = _next_spot(s, spots)
        yield from move_to(at)
        yield from expose(at, dets, t, idx=ser['cycle'], elapsed=time.time() - ser['t0'],
                          T=T, readings=readings, extra=extra, md=md)
        ser['cycle'] += 1
        n += 1
        if max_cycles is not None and n >= max_cycles:
            break                                    # no wait after the last frame
        if after is not None and (yield from after()):
            break
        wait = interval - (time.time() - t_frame)
        if wait > 0:
            if duration is not None and time.time() - t_start + wait >= duration:
                break                                # the next frame would start after the end
            print(f'frame {ser["cycle"] - 1} done, next in {wait:.0f} s')
            yield from bps.sleep(wait)


def _huber_names(plan):
    """Plan: `plan` with the Huber sx/sy/sz (mm) as the _x/_y/_z name tokens (LINKAM_XYZ); the
    piezo tokens come back afterwards, also after RE.stop() / RE.abort()."""
    keep = YZ['name_xyz']
    YZ['name_xyz'] = LINKAM_XYZ
    try:
        return (yield from plan)
    finally:
        YZ['name_xyz'] = keep


def _linkam_kw(defaults, kw, **md):
    """defaults + kw for run_trans / _track, with the Linkam T read at each frame in the
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


print(f'Murray: Linkam on the Huber, LINKAM_POS {LINKAM_POS}; '
      + (f'in the Linkam: {LK_SAMPLE["name"]}' if LK_SAMPLE else "new_sample(name) first"))
_dxy = np.array(POS_XY_LIST or [(0, 0)])
print(f'POS_XY_LIST: {len(POS_XY_LIST)} spots, sx {_dxy[:, 0].min():+.2f} .. {_dxy[:, 0].max():+.2f}, '
      f'sy {_dxy[:, 1].min():+.2f} .. {_dxy[:, 1].max():+.2f} mm; '
      f'{LK_SPOT["next"]} frames taken on this sample')
if RT_SAMPLES:
    print('RT holder (RT_SAMPLES):')
    show_samples(RT_SAMPLES)
else:
    print('RT holder: fill RT_X')

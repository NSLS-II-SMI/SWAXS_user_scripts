"""
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
     RE(measure_T(settle=120, t=2))      # soak 2 min first, longer exposure
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
LINKAM_POS = dict(sx=None, sy=None)
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
POS_XY_LIST = snake_xy(nx=5, ny=5, dx=0.2, dy=0.1)     # 25 spots over 0.8 x 0.4 mm

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
           max_cycles=None, T=None, readings=(), extra=None, md=None):
    """Plan: run_series of the one sample s in transmission (same clock, frame counter and
    names), but every frame on the next spot of POS_XY_LIST (Huber sx and sy)."""
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
    if _previewing():
        max_cycles = min(max_cycles or 2, 2)
        print('(preview) showing 2 frames')
    print(f'track: {s["name"]}, a frame every {interval or "back-to-back"} s for {duration} s, '
          f'each on the next spot; t0 = {_iso(ser["t0"])}')
    yield from bps.mv(waxs, arc)
    t_start = time.time()
    n = 0
    while time.time() - t_start < duration and (max_cycles is None or n < max_cycles):
        t_frame = time.time()
        at = _next_spot(s, spots)
        yield from move_to(at)
        yield from expose(at, dets, t, idx=ser['cycle'], elapsed=time.time() - ser['t0'],
                          T=T, readings=readings, extra=extra, md=md)
        ser['cycle'] += 1
        n += 1
        if max_cycles is not None and n >= max_cycles:
            break                                    # no wait after the last frame
        wait = interval - (time.time() - t_frame)
        if wait > 0:
            if time.time() - t_start + wait >= duration:
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

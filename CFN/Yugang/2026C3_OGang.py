"""
2026C3_OGang.py -- O. Gang group: transmission SAXS (2M only, no WAXS) on the Linkam.

Self-assembly kinetics of DNA-origami-assembled nanoparticle superlattices while cooling from the
melt: 49 -> 41.5 C in 0.1 C steps, 3 min at each T (TEMPS, TSTEPS).  One 1 mm capillary in the
Linkam at a time.

The sample is beam sensitive (a spot survives ~0.1-0.2 s of beam): every frame goes to a fresh spot
of a large map (SPOT_MAP: down a column in Y, then the next column in X, snake), exposure 0.1 s,
one frame every `interval` s (60 s or more: fewer motor moves, less motor heating).  Beam 200 um (H)
x 30 um (V): X step 0.2 mm, Y step 0.05 mm.  The _x/_y/_z name tokens are the stage the spots move
(STAGE: Huber sx/sy/sz in mm, or the piezo x/y/z in um).

SAXS (2M) at 5 m, WAXS arc at TSTEPS['arc'] (>= 16 so the 900KW does not shadow the 2M; the 900KW is
not read).  16.1 keV low divergence (EDIT YZ md below if the setup changes).

Run sheet
---------
0) bsui
     proposal_swap(<pass id>); project_set('OGang')          # EDIT the pass id
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_OGang.py
     preflight(); get_T()
   after closing the hutch: RE(shopen()); before opening it: RE(shclose())
1) Calibrant (moved into the beam by hand):
     collect_saxs('AgBH')                # 2M at the arc of TSTEPS; nothing else moves
     collect_saxs('AgBH', t=2, ova=True)
2) Mount the Linkam with the capillary on STAGE (below).  Center it with the camera: on the
   capillary axis, in the middle of the filled length; here('sx', 'sy') -> LINKAM_POS, re-run this
   file -- or leave LINKAM_POS empty: new_sample() takes the position as it is.
   Spots: SPOT_MAP = spot_map(nx, ny, dx, dy) around that center: Y within the thick middle of the
   1 mm capillary, enough spots for the whole program (run_T_steps prints how many it needs).
   Check the corners with the camera: mov_sam(1) then movx / movy, or RE(ova_snap('test')).
3) Load a sample:
     new_sample('NPSL1', note='...')     # STAGE to LINKAM_POS; resets clock and spots; prints the map
     RE(measure_T())                     # one 0.1 s 2M frame on the next spot, T as it is (test)
     RE(measure_T(n=3, t=0.2))
     set_T(49); get_T()                  # by hand (TSTEPS / LINKAM rate, tol); measure_T does not set T
4) T program:
     preview(run_T_steps())              # names (first 2 steps), frames, spots needed / left, time
     RE(run_T_steps())                   # Linkam -> 49 C (waits, pre_soak), then 49.0 .. 41.5 C,
                                         # 180 s per step, a frame every 60 s (30, 90, 150 s in each)
     RE(run_T_steps(interval=90))        # fewer frames, fewer moves
     RE(run_T_steps(per_spot=2))         # each spot twice (frames 60 s apart), half the spots
     RE(run_T_steps(t_steps(45, 41.5, 0.1), dwell=300))
     RE(run_T_steps([41.5], dwell=3600)) # hold 1 h at 41.5 C, a frame every interval
     RE(run_T_steps(ova=10))             # + an on-axis camera image before every 10th frame
   The clock and frame numbers run on over calls of the same sample (series_start(): t = 0 again);
   so do the spots (SPOT['i']: the last spot used; every call starts on a fresh one).  After RE.stop(): run_T_steps(the remaining T).
   Names: OGang_<sample>_<frame>_<s since series start>s_x.._y.._z.._T<T read>C_expt0.1s; the
   target T, step, spot and spot use are in the metadata.
5) Next sample: unload, back to 3).  At the end: RE(linkam_off())

Ctrl-C to pause; RE.resume() / RE.stop() / RE.abort().  A pause shifts the rest of the program.
"""

YZ.update(
    user='OGang',
    experiment='OGang',
    md={'beam': '16.1 keV, low divergence', 'saxs_sdd_m': 5},
    ova_dir=(f"/nsls2/auto-storage/smi/proposals/{RE.md.get('cycle')}/{RE.md.get('data_session')}"
             f"/projects/{RE.md.get('project_name') or 'OGang'}/user_data/OVA/"),   # after proposal_swap
)

LINKAM_MD = {'experiment': 'OGang_Linkam', 'holder': 'Linkam, 1 mm capillary',
             'environment': 'Linkam', 'sample_type': 'DNA-origami NP superlattice'}   # EDIT

# EDIT: the stage the Linkam sits on and the spots move: 'huber' (sx, sy in mm) or 'piezo' (x, y
# in um; no motor heating).  SPOT_MAP is in mm either way.
STAGE = 'huber'

# EDIT: center of the spot map on STAGE, e.g. {'sx': -3.3, 'sy': -12.6, 'sz': -18} (piezo: {'x': ..,
# 'y': ..}); a spot axis left out: its position when new_sample() is called.
LINKAM_POS = {}


def spot_map(nx, ny, dx, dy):
    """(dx, dy) offsets (mm) of an nx x ny grid centered on (0, 0), Y first: along y down the first
    x column, back up the next one (snake), ... -- one short move between consecutive spots."""
    xs = [(i - (nx - 1) / 2) * dx for i in range(nx)]
    ys = [(j - (ny - 1) / 2) * dy for j in range(ny)]
    return [(round(x, 4), round(y, 4)) for i, x in enumerate(xs) for y in (ys if i % 2 == 0 else ys[::-1])]


def t_steps(start, stop, step=0.1):
    """Temperatures start, start -/+ step, ..., stop (C), e.g. t_steps(49, 41.5, 0.1): 76 T.  The
    Linkam setpoint takes 0.1 C."""
    n = int(round(abs(stop - start) / step))
    sign = 1 if stop >= start else -1
    return [round(start + sign * k * step, 1) for k in range(n + 1)]


# EDIT: spots -- beam 200 um (H) x 30 um (V): X step 0.2 mm, Y step 0.05 mm.  Capillary along X:
# Y across its 1 mm, keep |y| <= ~0.3 mm (thick middle); X along the filled length.  (Capillary
# along Y: swap, e.g. spot_map(3, 80, 0.2, 0.05).)  At least as many spots as frames.
SPOT_MAP = spot_map(nx=20, ny=13, dx=0.2, dy=0.05)     # 260 spots over 3.8 x 0.6 mm

# EDIT with the group: the T program of run_T_steps, in order (C)
TEMPS = t_steps(49.0, 41.5, 0.1)                        # 76 steps, cooling from the melt

TSTEPS = dict(              # run_T_steps (and measure_T: t, per_spot, arc)
    dwell=180,              # s per T step, setpoint to setpoint
    interval=60,            # s between frames, start to start (60+: fewer moves, cooler motors)
    offset=30,              # s from a step to the first frame after it (T settled), < dwell
    t=0.1,                  # exposure (s): a spot survives ~0.1-0.2 s
    per_spot=1,             # frames on one spot before the next: 1, or 2
    pre_soak=0,             # s at the first T (melt) before the program starts, not measured
    arc=20,                 # WAXS arc (deg, >= 16: 2M not shadowed); only the 2M is read
)

LINKAM = dict(              # how run_T_steps / set_T drive the Linkam
    rate=1.0,               # degC/min: a 0.1 C step takes 6 s
    lnp=None,               # LN2 pump mode: None = leave as is ('Auto' if it cannot hold T)
    tol=0.2,                # degC: reaching the first T (and set_T)
    timeout=1800,           # s to reach the first T, then warn and go on
    end_T=None,             # setpoint after the program (not measured); None = stay at the last T
)

# EDIT: on-axis camera (OVA) images -- the default of the ova= option: True = before every frame,
# N = before every N-th frame (frame index), False = none.  The camera must be acquiring;
# images -> YZ['ova_dir'] as OGang_<sample>[_<frame>_<s>s]_T..C_x.._y.._sx.._sy.._OVA_NNN.jpg
OVA = False

# Motor temperatures: a spot move of an axis listed here waits while its motor is above MOTOR_T_MAX,
# until it is below MOTOR_T_OK (as huber_y_mv in 2026C3_TSAXS384.py).
MOTOR_T_MAX = 48.0          # degC
MOTOR_T_OK = 45.0           # degC
MOTOR_T_WAIT = 60           # s between readings while waiting
if 'huber_y_T' not in globals():
    huber_y_T = EpicsSignalRO('XF:12ID:m65.VAL', name='huber_y_T')
MOTOR_T = {'sy': huber_y_T}  # EDIT: + 'sx': EpicsSignalRO('<PV>', name='huber_x_T') once known

if globals().get('LK_SAMPLE') is None:      # re-running this file keeps the sample and its spots
    LK_SAMPLE = None
else:
    LK_SAMPLE = dict(LK_SAMPLE, **{a: v for a, v in LINKAM_POS.items() if v is not None})
SAMPLES = [LK_SAMPLE] if LK_SAMPLE else []
SPOT = globals().get('SPOT') or dict(i=0, used=0)   # next spot of SPOT_MAP, frames taken on it


def new_sample(name, move=True, **info):
    """
    Console: the capillary just loaded in the Linkam -> files OGang_<name>_...  Its position is
    LINKAM_POS on STAGE (axes left out: where they are now); move=True moves there.  info =
    metadata (note=..., solvent=...).  Resets the clock and the spots (SPOT_MAP from its start).
    """
    global LK_SAMPLE, SAMPLES
    ax, ay = _stage()[:2]
    pos = {a: AXES[a].position for a in (ax, ay)}
    pos.update({a: v for a, v in LINKAM_POS.items() if v is not None})
    LK_SAMPLE = dict(make_samples({1: name}, {1: pos})[0], **info)
    SAMPLES = [LK_SAMPLE]
    YZ_SERIES.update(t0=None, cycle=0)
    SPOT.update(i=0, used=0)
    if move:
        RE(move_to(LK_SAMPLE))
    show_samples()
    show_spots()


def show_spots(per_spot=None):
    """Console: SPOT_MAP extent, and how many frames are left before spots are re-used."""
    ax, ay, _, k = _stage()
    dxy = np.array(SPOT_MAP or [(0, 0)])
    unit = 'mm' if k == 1 else 'um'
    print(f'SPOT_MAP: {len(SPOT_MAP)} spots on {ax}/{ay}, x {dxy[:, 0].min():+.3f} .. {dxy[:, 0].max():+.3f}, '
          f'y {dxy[:, 1].min():+.3f} .. {dxy[:, 1].max():+.3f} mm from the center ({unit} on the stage); '
          f'next spot {SPOT["i"] + (1 if SPOT["used"] else 0)}, {_frames_left(SPOT, per_spot)} '
          f'frames before re-use')


def set_T(T, settle=0, **kw):
    """Console: Linkam to T (degC) with the LINKAM rate / LN2 pump / tol / timeout (kw override);
    waits until it is there, then soaks `settle` s."""
    lk = dict(LINKAM, settle=settle, **kw)
    RE(linkam_goto(T, **{k: lk[k] for k in ('tol', 'settle', 'timeout', 'rate', 'lnp')}))
    get_T()


def get_T(show=True):
    """Console: the Linkam T now (degC), returned (T = get_T()).  show=True also prints the
    setpoint, ramp rate, heating/cooling on or off and the controller status.  Only reads."""
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


def measure_T(n=1, t=None, per_spot=None, settle=0, ova=None):
    """Plan: n SAXS frames (2M only, t s; default TSTEPS) of the Linkam sample at the T as it is now
    (the Linkam is only read), each on the next spot of SPOT_MAP, after a soak of `settle` s.  No
    time index.  ova (None: OVA): an on-axis camera image before each frame."""
    s = _sample()
    t = TSTEPS['t'] if t is None else t
    per_spot = TSTEPS['per_spot'] if per_spot is None else per_spot
    yield from _saxs_ready(TSTEPS['arc'])
    if settle:
        print(f'soaking {settle} s')
        yield from bps.sleep(settle)
    spots = _spot_counter()
    for _ in range(n):
        yield from _names(_frame(s, spots, per_spot, t, None, dict(LINKAM_MD), _ova_opt(ova)))


def run_T_steps(temps=None, ova=None, **kw):
    """
    Plan: T staircase of the Linkam sample with SAXS kinetics.  The Linkam goes to temps[0]
    (default TEMPS) and waits until it is there (LINKAM: rate, LN2 pump, tol, timeout), soaks
    `pre_soak` s (not measured); then the program runs on one clock: the next T every `dwell` s,
    and a 2M frame of `t` s every `interval` s, the first `offset` s after the start (TSTEPS),
    each on the next spot of SPOT_MAP (per_spot consecutive frames per spot; every call starts on
    a fresh spot).  The steps keep to the clock; a pause or a hot-motor wait shifts the rest of
    the program.  Afterwards the Linkam stays at the
    last T (end_T: goes there, not measured).  Frame names _<frame>_<s since series_start()>s_
    ..._T<T read at the frame>C (the clock starts here unless it is running); the target T, step
    and spot are in the metadata.  ova (None: OVA): True = an on-axis camera image before every
    frame, N = before every N-th.  kw override TSTEPS and LINKAM, e.g.
        run_T_steps(interval=90), run_T_steps([41.5], dwell=3600), run_T_steps(per_spot=2)
    """
    s = _sample()
    temps = list(TEMPS if temps is None else temps)
    if not temps:
        raise ValueError('no temperatures')
    lk = {k: kw.pop(k, v) for k, v in LINKAM.items()}
    opts = dict(TSTEPS, **kw)
    dwell, interval, offset = opts['dwell'], opts['interval'], opts['offset']
    if interval <= 0 or not 0 <= offset < dwell:
        raise ValueError(f'need interval > 0 and 0 <= offset < dwell (interval={interval}, '
                         f'offset={offset}, dwell={dwell})')
    total = len(temps) * dwell
    n_frames = int(np.ceil((total - offset) / interval))
    events = sorted([(i * dwell, 0, i) for i in range(len(temps))]          # a T step before a
                    + [(offset + m * interval, 1, m) for m in range(n_frames)])  # frame at the same time
    dry = _previewing()
    spots = _spot_counter()
    left = _frames_left(spots, opts['per_spot'])
    print(f'run_T_steps: {s["name"]}, {len(temps)} T {temps[0]} -> {temps[-1]} C, {dwell:g} s each: '
          f'~{(opts["pre_soak"] + total) / 60:.0f} min; a {opts["t"]:g} s 2M frame every {interval:g} s: '
          f'{n_frames} frames, {opts["per_spot"]} per spot; {left} frames left on SPOT_MAP')
    if n_frames > left:
        print(f'WARNING: SPOT_MAP runs out after {left} of {n_frames} frames: then spots are exposed '
              f'again (beam damage) -- a larger SPOT_MAP, a longer interval or per_spot=2')
    yield from _saxs_ready(opts['arc'])
    yield from linkam_goto(temps[0], tol=lk['tol'], settle=opts['pre_soak'], timeout=lk['timeout'],
                           rate=lk['rate'], lnp=lk['lnp'])
    ser = dict(YZ_SERIES) if dry else YZ_SERIES     # a dry run leaves clock and counter
    if ser['t0'] is None:
        if ser is YZ_SERIES:
            series_start('(auto: run_T_steps start)')
        else:
            ser['t0'] = time.time()
    md = dict(LINKAM_MD, dwell_s=dwell, interval_s=interval, T_ramp_C_per_min=lk['rate'])
    slack = max(10.0, 0.5 * min(interval, dwell))   # behind the clock by more: shift the rest
    start = time.time()
    for tau, kind, k in events:
        if dry and tau >= 2 * dwell:
            print(f'(preview) the first 2 of {len(temps)} steps shown')
            break
        late = time.time() - (start + tau)
        if late > slack:
            print(f'{late:.0f} s behind the clock (pause, hot motor, ...): the rest of the program '
                  f'{late:.0f} s later')
            start += late
        elif late < 0:
            if -late > 5 and not dry:
                print(f'next {"T step" if kind == 0 else "frame"} in {-late:.0f} s')
            yield from bps.sleep(-late)
        if kind == 0:
            T = temps[k]
            md.update(T_setpoint_C=T, T_step=k)
            T_now = yield from bps.rd(LThermal.temperature_current)
            print(f'\n##### {s["name"]}: step {k + 1}/{len(temps)}: Linkam -> {T} C (now {T_now:.1f} C) #####')
            yield from _put(LThermal.temperature_setpoint, round(float(T), 1))
        else:
            T_name = md['T_setpoint_C'] if dry else None   # a dry run never sets the Linkam
            yield from _names(_frame(s, spots, opts['per_spot'], opts['t'], ser, md, _ova_opt(ova), T_name))
    if lk['end_T'] is not None:
        yield from linkam_goto(lk['end_T'], tol=lk['tol'], settle=0, timeout=lk['timeout'],
                               rate=lk['rate'], lnp=lk['lnp'])


def collect_saxs(sample_name, t=1, ova=None):
    """Console: SAXS (2M only) of the sample now in the beam (moved there by hand, e.g. the AgBH
    calibrant) at the WAXS arc of TSTEPS; only the arc moves.  Names OGang_<name>_x.._y.._z.._expt<t>s
    (piezo x/y/z).  ova (None: OVA): an on-axis camera image first."""
    RE(run_trans([{'name': clean_name(sample_name)}], t=t, arcs=(TSTEPS['arc'],), saxs='max',
                 waxs_det=False, at_sample=_ova_first_arc() if _ova_opt(ova) else None))


def _stage():
    """(x axis, y axis, name axes, axis units per mm of SPOT_MAP) of STAGE."""
    return {'huber': ('sx', 'sy', ('sx', 'sy', 'sz'), 1.0),
            'piezo': ('x', 'y', ('x', 'y', 'z'), 1000.0)}[STAGE]


def _sample():
    if not LK_SAMPLE:
        raise ValueError("no sample in the Linkam: new_sample('name') first")
    return LK_SAMPLE


def _spot_counter():
    """SPOT, moved on to a fresh spot (a spot is never shared by two calls); a dry run gets a
    copy, so it uses no spots up."""
    spots = dict(SPOT) if _previewing() else SPOT
    if spots['used']:
        spots.update(i=spots['i'] + 1, used=0)
    return spots


def _frames_left(spots, per_spot=None):
    """Frames a call can take before spots are re-used (it starts on a fresh spot)."""
    per_spot = TSTEPS['per_spot'] if per_spot is None else per_spot
    return max((len(SPOT_MAP) - spots['i'] - (1 if spots['used'] else 0)) * per_spot, 0)


def _next_spot(s, spots, per_spot):
    """The sample dict s at its next spot of SPOT_MAP (per_spot frames on each; index and use in
    the metadata as 'spot', 'spot_use').  After the last spot it starts over (warning)."""
    if not SPOT_MAP:
        raise ValueError('SPOT_MAP is empty: at least [(0, 0)]')
    if spots['used'] >= per_spot:
        spots['i'] += 1
        spots['used'] = 0
    j = spots['i'] % len(SPOT_MAP)
    if spots['i'] >= len(SPOT_MAP) and j == 0 and spots['used'] == 0:
        print(f'WARNING: all {len(SPOT_MAP)} spots of SPOT_MAP used; starting again at spot 0 '
              f'(exposed before: beam damage)')
    spots['used'] += 1
    ax, ay, _, k = _stage()
    dx, dy = SPOT_MAP[j]
    use = spots['used'] + spots['i'] // len(SPOT_MAP) * per_spot
    return dict(s, **{ax: s[ax] + dx * k, ay: s[ay] + dy * k}, spot=j, spot_use=use)


def _frame(s, spots, per_spot, t, ser, md, ova, T_name=None):
    """Plan: one 2M frame of s on its next spot (ser: the series clock / counter, None: no time
    index); T read now (T_name: this number instead, dry runs)."""
    at = _next_spot(s, spots, per_spot)
    yield from _go(at)
    T = LThermal.temperature_current if T_name is None else T_name
    idx = None if ser is None else ser['cycle']
    if ova and (idx is None or idx % int(ova) == 0):
        yield from _ova(at, idx, None if ser is None else time.time() - ser['t0'], T)
    yield from expose(at, [pil2M], t, idx=idx, elapsed=None if ser is None else time.time() - ser['t0'],
                      T=T, readings=[LThermal.temperature_setpoint], md=md)
    if ser is not None:
        ser['cycle'] += 1


def _go(at):
    """Plan: move only the axes of `at` that are not there yet (fewer moves: less motor heating);
    an axis of MOTOR_T first waits while its motor is too hot."""
    args = []
    for a, v in at.items():
        if a not in AXES or v is None:
            continue
        now = yield from bps.rd(AXES[a])
        if abs(now - v) <= (0.5 if a in ('x', 'y', 'z') else 2e-3):     # piezo um, Huber mm
            continue
        if a in MOTOR_T:
            yield from _motor_cool(a)
        args += [AXES[a], v]
    if args:
        yield from bps.mv(*args)


def _motor_cool(a):
    """Plan: wait while the motor of axis `a` (MOTOR_T) is above MOTOR_T_MAX, until below MOTOR_T_OK."""
    T = yield from bps.rd(MOTOR_T[a])
    if T > MOTOR_T_MAX:
        print(f'{a} motor {T:.1f} C > {MOTOR_T_MAX:g} C: waiting until below {MOTOR_T_OK:g} C')
        while T > MOTOR_T_OK and not _previewing():          # a dry run does not wait
            yield from bps.sleep(MOTOR_T_WAIT)
            T = yield from bps.rd(MOTOR_T[a])
            print(f'  {a} motor {T:.1f} C')


def _saxs_ready(arc):
    """Plan: WAXS arc to `arc`, where the 900KW does not shadow the 2M."""
    if arc < YZ['saxs_min_arc']:
        raise ValueError(f'arc {arc} < {YZ["saxs_min_arc"]}: the WAXS detector shadows the 2M')
    check_arcs([arc])
    yield from bps.mv(waxs, arc)


def _names(plan):
    """Plan: `plan` with the STAGE axes as the _x/_y/_z name tokens; the piezo tokens come back
    afterwards, also after RE.stop() / RE.abort()."""
    keep = YZ['name_xyz']
    YZ['name_xyz'] = _stage()[2]
    try:
        return (yield from plan)
    finally:
        YZ['name_xyz'] = keep


def _ova_opt(ova):
    """The ova= option of a plan: None -> the OVA default."""
    return OVA if ova is None else ova


def _ova(sample, idx=None, elapsed=None, T=None):
    """Plan: ova_snap of `sample` here, its name + _<frame>_<s>s and _T..C like its SAXS frame."""
    name = sample['name']
    if idx is not None:
        name += f'_{int(idx):04d}_{max(float(elapsed or 0), 0.0):.1f}s'
    T_val = yield from _value(T, [])
    if T_val is not None and np.isfinite(T_val):
        name += f'_T{T_val:.1f}C'
    yield from ova_snap(dict(sample, name=name))


def _ova_first_arc(T=None):
    """at_sample for run_trans: an OVA image of each sample on the first arc."""
    def snap(sample, i_arc):
        if i_arc == 0:
            yield from _ova(sample, T=T)
    return snap


print(f'OGang: Linkam on {STAGE}, LINKAM_POS {LINKAM_POS}; '
      + (f'in the Linkam: {LK_SAMPLE["name"]}' if LK_SAMPLE else 'new_sample(name) first'))
_n = int(np.ceil((len(TEMPS) * TSTEPS['dwell'] - TSTEPS['offset']) / TSTEPS['interval']))
print(f'TEMPS: {len(TEMPS)} T {TEMPS[0]} -> {TEMPS[-1]} C, {TSTEPS["dwell"]:g} s each, a frame every '
      f'{TSTEPS["interval"]:g} s: {_n} frames ({TSTEPS["t"]:g} s, {TSTEPS["per_spot"]} per spot)')
show_spots()

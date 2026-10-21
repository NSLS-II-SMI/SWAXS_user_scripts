"""
2026C3_JMayer.py -- Wed 2026-10-21: J. Mayer group (Yale), in-situ electrochemistry, GISAXS.

Their EC cell, one sample at a time, on the piezo (Huber parked at CELL).  GISAXS on the 2M with
GIWAXS on the 900KW at WAXS arc 20 only -- both detectors in the same exposure.  16.1 keV low
divergence, SAXS 2M at 5 m, in air.  Per sample: ex situ (dry cell) -> electrolyte -> in situ.

The potential is set by hand on their potentiostat (the SMI profile has no potentiostat
control).  ec_start() marks t = 0 (start their sequence at the same moment), ec_set_potential(V)
records the value now applied; in-situ names carry _<cycle>_<s since ec_start>s and _E..V, and
every run has user_hints.series_t0 so frames line up with the potentiostat file.  If their
E-monitor output is wired to the Moxa analog input, the readback is used instead of the typed
value: EC.update(readback=moxa_out.ch2_read, scale=..., offset=...)  (scale = V per V).

Run sheet
---------
0) bsui
     proposal_swap(321177); project_set('JMayer')
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
     %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_JMayer.py
     preflight()
1) Sample in the dry cell (ex situ):
     new_sample('S1', electrode='...')   # Huber + piezo to CELL; files JMayer_S1_exsitu_...
     snap_swaxs()                        # quick look (see Quick tests)
     align_cell()                        # automatic GI alignment (piezo y/th), saved to json
     sample on PEEK/rubber -- reflected beam only: move py and pth by hand until the reflected
     beam is on the 2M at about 0.15 deg incidence, then
       align_cell_ref(reflect=0.15)      # th scan, y scan, fine th scan on the reflection;
                                         # saves th0 = th - 0.15 and y
       align_cell_ref(th_scan=False)     # y scan on the reflection only, th as set
     theta by hand at incident angle 0, height on the direct beam: align_height()
     all by hand: mark_aligned(1) saves the current th (incident angle 0) and y
     preview(run_cell()); RE(run_cell()) # GI angles 0.10/0.15/0.20 at arc 20
2) Electrolyte in (in situ, open circuit):
     add_electrolyte(electrolyte='...')  # same sample, files JMayer_S1_insitu_...
     align_cell()                        # starts from the ex-situ alignment (or align_cell_ref())
     RE(run_cell())                      # OCV reference, no _E token
3) Potential (by hand on the potentiostat):
     ec_start('CA -0.5 V')               # when their sequence starts: t = 0
     ec_set_potential(-0.5)              # the value now applied (also when it changes)
     preview(run_insitu()); RE(run_insitu())
   new potential: Ctrl-C, RE.stop(), ec_set_potential(-0.8), RE(run_insitu())
     (the clock and the cycle counter continue until the next ec_start / new_sample)
   all GI angles at the present potential: Ctrl-C, RE.stop(), RE(run_cell())
4) Next sample: back to 1) (new_sample resets the EC clock and the potential).

Quick tests at the current position (nothing moves; 'test' names are skipped by the analysis):
     snap_saxs()                 # 2M only, 1 s
     snap_waxs()                 # 900KW only, at the current WAXS arc; snap_waxs(arc=20) moves it
     snap_swaxs('S1_check', t=2) # 2M + 900KW, saved under that name
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

# Cell position, 2026-10-21: Huber sx/sy (mm), piezo x/y/z (um); y is the alignment start
CELL = dict(sx=-2.4, sy=8.0, x=0.0, y=2000.0, z=-6100.0)

GI = dict(
    angles=(0.10, 0.15, 0.20),   # incident angles (deg) above the aligned th
    arcs=(20,),                  # 2M (GISAXS) + 900KW (GIWAXS) in one exposure
    t=1,
    x_offsets=(0,),              # extra piezo x spots (um)
    stage='piezo',
)

SERIES = dict(
    angles=(0.15,),              # incident angle(s) per cycle
    arc=20, saxs=True,           # 2M + 900KW in every frame
    t=1,
    interval=30,                 # cycle start-to-start (s); 0 = as fast as possible
    duration=4 * 3600,           # s per run_insitu call; Ctrl-C, RE.stop() ends it earlier
    spots=(-200, 0, 200),        # piezo x offsets (um): a fresh spot every cycle
    stage='piezo',
)

if globals().get('CELL_SAMPLE') is None:     # re-running this file keeps the sample in the cell
    CELL_SAMPLE = None
SAMPLES = [CELL_SAMPLE] if CELL_SAMPLE else []


def goto_cell():
    """Console: Huber sx/sy and piezo x/y/z to CELL (th is left to the alignment)."""
    RE(bps.mv(*[v for a in CELL for v in (AXES[a], CELL[a])]))
    here('sx', 'sy', 'x', 'y', 'z')


def new_sample(name, move=True, **info):
    """
    Console: the sample just loaded into the dry cell -> ex situ, files JMayer_<name>_exsitu_...
    info = metadata of this sample (electrode=..., note=...).  Resets the EC clock and the
    potential; move=True also does goto_cell().
    """
    global CELL_SAMPLE, SAMPLES
    base = clean_name(name)
    s = make_samples({1: f'{base}_exsitu'}, {1: (CELL['x'], CELL['y'])}, z=CELL['z'])[0]
    CELL_SAMPLE = dict(s, base=base, state='exsitu', **info)
    SAMPLES = [CELL_SAMPLE]
    YZ_SERIES.update(t0=None, cycle=0)
    EC['potential'] = None
    ec_potential_setpoint.put(float('nan'))
    if move:
        goto_cell()
    show_samples()


def add_electrolyte(**info):
    """Console: electrolyte is in -> in situ, same sample, files JMayer_<name>_insitu_...; open
    circuit (no _E token) until ec_set_potential(V).  info = metadata (electrolyte=...)."""
    global CELL_SAMPLE, SAMPLES
    s = _cell()
    CELL_SAMPLE = dict(s, name=f'{s["base"]}_insitu', state='insitu', **info)
    SAMPLES = [CELL_SAMPLE]
    EC['potential'] = None
    ec_potential_setpoint.put(float('nan'))
    show_samples()


def align_cell(angle=0.15):
    """Console: GI alignment (piezo y/th) of the sample in the cell, starting from its latest
    alignment, in situ else from the ex-situ one; saved like align_gi_samples()."""
    global ALIGNED
    s = _cell()
    ALIGNED = _saved_alignment()
    prev = ALIGNED.get(s['name'])
    if not (prev and prev['ok']):
        prev = ALIGNED.get(f'{s["base"]}_exsitu')
    start = {s['name']: prev} if prev and prev['ok'] else None
    RE(align_gi(SAMPLES, angle=angle, stage='piezo', result=ALIGNED, holder=_holder(), start=start))
    show_alignment({s['name']: ALIGNED[s['name']]})
    return ALIGNED


def align_cell_ref(reflect=0.15, th=None, th_scan=True):
    """
    Console: GI alignment of the sample in the cell on the REFLECTED beam only (no direct-beam
    scan).  First set piezo y and th by hand so the reflected beam is on the 2M, near incident
    angle `reflect` (th ~ th0 + reflect, within ~0.2 deg); th=0.67 moves th there first.  Then
    the second half of alignment_gisaxs: reflected-beam ROI at 2 x reflect, th scan +-0.2 deg
    to the reflection, y scan +-150 um on it, fine th scan +-0.1 deg (th_scan=False: the y scan
    only, th taken as set).  Saves th0 = th - reflect and y, used by run_cell / run_insitu.
    A failed scan puts y and th back and saves nothing.
    """
    def scans(th_start):
        yield from smi.setReflectedBeamROI(total_angle=reflect, technique='gisaxs')
        if th_scan:
            yield from align_gisaxs_th(0.2, 21)
        yield from align_gisaxs_height_rb(150, 16)
        if th_scan:
            yield from align_gisaxs_th(0.1, 31)
        th_ref = yield from bps.rd(piezo.th)
        return th_ref - reflect

    return _align_by(scans, th, f'reflected beam at {reflect} deg', reflect)


def align_height(th=None, rang=800, point=21):
    """
    Console: height-only GI alignment of the sample in the cell, with theta aligned by hand
    (th = surface parallel to the beam, incident angle 0; th=None: the piezo th as it is).
    Scans piezo y +-rang um around its current value on the DIRECT beam and goes to the half
    cut (the first scan of alignment_gisaxs).  Theta is never scanned.  Saves th and the new y,
    used by run_cell / run_insitu.  A failed scan puts y back and saves nothing.
    """
    def scans(th_start):
        yield from smi.setDirectBeamROI()
        yield from align_gisaxs_height(rang, point, der=True)
        return th_start

    return _align_by(scans, th, 'height only, th by hand', None)


def _align_by(scans, th, method, angle):
    """Console: run the alignment plan scans(th_start) -> th0 (incident angle 0) on the sample in
    the cell, from the y and th set by hand, and save th0 and y like align_gi_samples()."""
    global ALIGNED
    s = _cell()
    ALIGNED = _saved_alignment()
    RE(_align_plan(s, ALIGNED, scans, th, method, angle))
    if s['name'] in ALIGNED:
        show_alignment({s['name']: ALIGNED[s['name']]})
    return ALIGNED


def _align_plan(s, result, scans, th, method, angle):
    yield from move_to(s, skip=('y', 'th'))             # x, z of the cell; y and th as set by hand
    if th is not None:
        yield from bps.mv(piezo.th, th)
    th_start = yield from bps.rd(piezo.th)
    y_start = yield from bps.rd(piezo.y)
    print(f'\n##### aligning {s["name"]} ({method}) from th = {th_start:.4f}, y = {y_start:.3f} #####')
    try:
        bec._calc_derivative_and_stats = True
        yield from det_exposure_time(0.3, 0.3)
        yield from smi.modeAlignment(technique='gisaxs')
        th0 = yield from scans(th_start)
        yield from smi.modeMeasurement()
        bec._calc_derivative_and_stats = False
    except (RequestAbort, RequestStop):
        print('alignment interrupted: restoring the measurement mode, y and th')
        yield from _restore_measurement_mode()
        yield from bps.mv(piezo.y, y_start, piezo.th, th_start)
        raise
    except Exception as ex:
        print(f'!!! alignment FAILED for {s["name"]}: {type(ex).__name__}: {ex}; y and th back to '
              f'{y_start:.3f}, {th_start:.4f}, saved alignment unchanged')
        yield from _restore_measurement_mode()
        yield from bps.mv(piezo.y, y_start, piezo.th, th_start)
        return
    yield from bps.mv(piezo.th, th0)
    y0 = yield from bps.rd(piezo.y)
    result[s['name']] = dict(th=float(th0), y=float(y0), ok=True, stage='piezo', angle=angle,
                             time=_iso(), error='', method=method, holder=_holder())
    print(f'{s["name"]}: th0={th0:.4f}  y={y0:.3f}  (started at th {th_start:.4f}, y {y_start:.3f})')
    save_alignment(result, _holder())


def run_cell(**kw):
    """Plan: GISAXS + GIWAXS of the sample in the cell at the GI angles (GI; kw override), from
    its latest saved alignment; in situ with the potential (_E..V) once it is known."""
    s = _cell()
    yield from _at_cell()
    gi = dict(GI, **kw)
    if s['state'] == 'insitu':
        E, readings = _ec_E()
        gi.setdefault('E', E)
        gi.setdefault('readings', readings)
    yield from run_gi(SAMPLES, **gi)


def run_insitu(**kw):
    """Plan: in-situ time series of the sample in the cell (SERIES; kw override): every
    `interval` s one 2M + 900KW frame per angle at the next x spot, names
    _<cycle>_<s since ec_start>s ... _E..V."""
    s = _cell()
    if s['state'] != 'insitu':
        raise ValueError('ex situ: add_electrolyte() first (or run_cell() for the dry cell)')
    yield from _at_cell()
    yield from run_ec(SAMPLES, **dict(SERIES, **kw))


def snap_saxs(name='test', t=1):
    """Console: one 2M exposure at the current position; nothing moves."""
    RE(_snap(name, [pil2M], t))


def snap_waxs(name='test', t=1, arc=None):
    """Console: one 900KW exposure at the current position; arc=None: at the current WAXS arc."""
    RE(_snap(name, [pil900KW], t, arc))


def snap_swaxs(name='test', t=1, arc=None):
    """Console: one 2M + 900KW exposure at the current position; arc=None: the current arc."""
    RE(_snap(name, [pil900KW, pil2M], t, arc))


def _snap(name, dets, t, arc=None):
    if arc is not None:
        check_arcs([arc])
        yield from bps.mv(waxs, arc)
    now = yield from bps.rd(_arc_rb())
    if pil2M in dets and now < YZ['saxs_min_arc']:
        print(f'WARNING: WAXS arc {now:.1f} deg shadows part of the 2M')
    yield from expose(name, dets, t)


def _cell():
    if not CELL_SAMPLE:
        raise ValueError("no sample in the cell: new_sample('name') first")
    return CELL_SAMPLE


def _at_cell(tol=0.05):
    """Plan: refuse to measure unless the Huber is at CELL."""
    for a in ('sx', 'sy'):
        v = yield from bps.rd(AXES[a])
        if abs(v - CELL[a]) > tol:
            raise RuntimeError(f'Huber {a} is at {v:.3f} mm, the cell at {CELL[a]} mm: '
                               f'goto_cell() first (or update CELL)')


def _ec_E():
    """E for run_gi names and the signals to record: the analog readback if wired, else the
    typed ec_set_potential() value (no _E token while it is unset)."""
    if EC['readback'] is not None:
        return ({'signal': EC['readback'], 'scale': EC['scale'], 'offset': EC['offset']},
                [ec_potential_setpoint, EC['readback']])
    return ec_potential_setpoint, [ec_potential_setpoint]


print(f'JMayer: CELL {CELL}; one sample at a time -- new_sample(name) first'
      if not CELL_SAMPLE else f'JMayer: in the cell {CELL_SAMPLE["name"]} ({CELL_SAMPLE["state"]})')

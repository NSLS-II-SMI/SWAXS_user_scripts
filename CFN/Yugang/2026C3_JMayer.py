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
     align_cell()                        # GI alignment (piezo y/th), saved to json
       if it fails: align by hand, then mark_aligned(1)
     preview(run_cell()); RE(run_cell()) # GI angles 0.10/0.15/0.20 at arc 20
2) Electrolyte in (in situ, open circuit):
     add_electrolyte(electrolyte='...')  # same sample, files JMayer_S1_insitu_...
     align_cell()                        # starts from the ex-situ alignment
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

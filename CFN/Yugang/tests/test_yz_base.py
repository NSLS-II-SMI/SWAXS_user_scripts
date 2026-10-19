"""
Offline tests of YZhang_SMI_Base.py with simulated devices (tests/sim_beamline.py).

    cd CFN/Yugang && python -m pytest -q tests
"""
import csv
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_beamline import events, make_namespace, starts  # noqa: E402

# Parsers of the CFN analysis tools, copied verbatim (pySAXSAI codes/smi_waxs.py, reducers.py,
# insitu series; pyScattViz org/cms.py)
PYSAXSAI = dict(
    waxs=re.compile(r"_(?:waxs|wa)_?(-?\d+(?:\.\d+)?)", re.I),
    x=re.compile(r"_(?:p)?x_?(-?\d+(?:\.\d+)?)", re.I),
    T=re.compile(r"_T(-?\d+\.?\d*)c_", re.I),
    expt=re.compile(r"_expt(-?\d+\.?\d*)s"),
    deg=re.compile(r"(-?\d+\.?\d*)deg"),
    th=re.compile(r"_th([+-]?\d+\.?\d*)"),
    series=re.compile(r"^(.*?)_(\d+)_\d+(?:\.\d+)?s_(?=[A-Za-z])"),
)
PYSCATTVIZ_INDEXED = re.compile(r"^(.*?)_(\d+)_(\d+(?:\.\d+)?)s_x")
BEAMLINE_SUFFIX = '_16100.00eV_wa20.0_sdd5000.0mm_id123456_000000_WAXS.tif'


@pytest.fixture
def ns(tmp_path):
    return make_namespace(tmp_path)


def three_samples(ns):
    return ns['make_samples']({1: 'S1', 2: 'S2', 3: 'S3'},
                              {1: (-10000, 500), 2: (0, 500), 3: (10000, 500)}, z=8000)


def test_clean_name_removes_parser_traps(ns):
    clean = ns['clean_name']
    assert clean('PS_xylene') == 'PS-xylene'
    assert clean('film_th5nm') == 'film-th5nm'
    assert clean('Cu EC #1') == 'Cu-EC-1'
    assert clean('S1+2') == 'S1-2'
    assert clean('a_T25C_b') == 'a-T25C_b'
    assert clean('P3HT_1.5mM') == 'P3HT_1p5mM'
    assert clean('B_10deg') == 'B_10dg'
    assert clean('run_12_30s') == 'run-12_30s'
    assert clean('run_12_3.5s') == 'run_12_3p5s'      # no longer a series token
    assert clean('ok_name-1') == 'ok_name-1'


def test_names_parse_with_analysis_tools(ns):
    fn = ns['file_name']
    trans = fn('PS50k_B1-A01', 1, (-1234.5, 10, 8000)) + BEAMLINE_SUFFIX
    gi = fn('S1', 0.5, (100, 2, 3), ai=0.15, T=-50.04) + BEAMLINE_SUFFIX
    insitu = fn('CuEC-1', 2, (5, 6, 7), ai=0.15, idx=12, elapsed=360.04, E=-0.5) + BEAMLINE_SUFFIX

    assert trans.startswith('YZ_PS50k_B1-A01_x-1234.50_')
    assert trans.split('_x', 1)[0] == 'YZ_PS50k_B1-A01'          # pyScatt SAXS grouping cut
    assert float(PYSAXSAI['x'].search(trans).group(1)) == -1234.5
    assert float(PYSAXSAI['waxs'].search(trans).group(1)) == 20.0
    assert PYSAXSAI['deg'].search(trans) is None                  # transmission: no 'deg'
    assert PYSAXSAI['th'].search(trans) is None

    assert float(PYSAXSAI['deg'].search(gi).group(1)) == 0.15
    assert float(PYSAXSAI['T'].search(gi).group(1)) == -50.0
    assert float(PYSAXSAI['expt'].search(gi).group(1)) == 0.5

    m = PYSAXSAI['series'].search(insitu)
    assert m.group(1) == 'YZ_CuEC-1_0.1500deg' and int(m.group(2)) == 12
    m = PYSCATTVIZ_INDEXED.search(insitu)
    assert int(m.group(2)) == 12 and float(m.group(3)) == 360.0
    assert '_E-0.500V_' in insitu and '+' not in insitu


def test_run_trans_arcs_detectors_offsets_and_logbook(ns, tmp_path):
    samples = three_samples(ns)
    ns['RE'](ns['run_trans'](samples, t=2, arcs=(0, 20), offsets=((0, -100), (0, 100))))
    st = starts(ns)
    assert len(st) == 3 * 2 * 2
    # arc 0: WAXS only; arc 20: WAXS + SAXS; serpentine sample order on the second arc
    assert [s['user_hints']['detectors'] for s in st[:6]] == [['pil900KW']] * 6
    assert [s['user_hints']['detectors'] for s in st[6:]] == [['pil900KW', 'pil2M']] * 6
    assert [s['sample'] for s in st[::2]] == ['S1', 'S2', 'S3', 'S3', 'S2', 'S1']
    # offsets are relative to each sample's own y (no drift)
    assert [s['user_hints']['positions']['y'] for s in st[:4]] == [400, 600, 400, 600]
    assert st[0]['sample_name'] == 'YZ_S1_x-10000.00_y400.00_z8000.00_expt2s'
    assert st[0]['geometry'] == 'transmission'
    assert set(ns['_sim'].exposures) == {2}
    with open(tmp_path / 'logbook_YZ.csv') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 12 and rows[-1]['sample'] == 'S1'


def test_disallowed_arc_fails_before_any_run(ns):
    with pytest.raises(ValueError, match='not allowed'):
        ns['RE'](ns['run_trans'](three_samples(ns), arcs=(0, 7)))
    assert starts(ns) == []


def test_beamstop_guard(ns):
    ns['pil2M'].active_beamstop.put('rod_removed')       # alignment mode: no detector at all
    with pytest.raises(RuntimeError, match='modeMeasurement'):
        ns['RE'](ns['measure_wsaxs']('S1', t=1, arc=20))
    with pytest.raises(RuntimeError, match='modeMeasurement'):
        ns['RE'](ns['measure_waxs']('S1', t=1, arc=0))
    ns['pil2M'].active_beamstop.put('none')              # no 2M beamstop: WAXS only is fine
    with pytest.raises(RuntimeError, match='insert_beamstop'):
        ns['RE'](ns['measure_saxs']('S1', t=1))
    ns['RE'](ns['measure_waxs']('S1', t=1, arc=0))
    assert len(starts(ns)) == 1


def test_run_trans_center_offset_moves_back(ns):
    samples = three_samples(ns)[:1]
    ns['RE'](ns['run_trans'](samples, arcs=(0,), offsets=((0, -200), (0, 0), (0, 200))))
    assert [s['user_hints']['positions']['y'] for s in starts(ns)] == [300, 500, 700]


def test_gi_alignment_failure_recovery_and_run(ns, tmp_path):
    samples = three_samples(ns)
    ns['_sim'].fail_x.add(0.0)                           # S2 alignment fails
    ns['RE'](ns['bps'].mv(ns['piezo'].th, 0.05))
    aligned = ns['align_gi_samples'](samples, holder='bar1')
    assert [aligned[n]['ok'] for n in ('S1', 'S2', 'S3')] == [True, False, True]
    assert ns['pil2M'].active_beamstop.get() == 'rod'    # restored after the failure
    assert ns['attenuation'].get() == 1
    s1_th = aligned['S1']['th']                          # S2's scan started at S1's th ...
    assert aligned['S2']['th'] == pytest.approx(s1_th)   # ... and th went back there (not +4.5)
    assert aligned['S3']['th'] == pytest.approx(0.3 + 10000e-5)
    saved = json.load(open(tmp_path / 'alignment_bar1_latest.json'))
    assert saved == ns['load_alignment']('bar1')

    ns['_docs'].clear()
    ns['RE'](ns['run_gi'](samples, aligned, angles=(0.1, 0.2), arcs=(0, 20), x_offsets=(0, 500)))
    st = starts(ns)
    assert len(st) == 2 * 2 * 2 * 2                      # S2 skipped
    assert {s['sample'] for s in st} == {'S1', 'S3'}
    s1 = [s for s in st if s['sample'] == 'S1']
    th0 = aligned['S1']['th']
    assert {round(s['user_hints']['positions']['th'] - th0, 6) for s in s1} == {0.1, 0.2}
    assert {s['user_hints']['positions']['x'] for s in s1} == {-10000, -9500}
    assert st[0]['geometry'] == 'reflection'
    assert '_0.1000deg_x' in st[0]['sample_name']


def test_abort_during_alignment_restores_measurement_mode(ns):
    from bluesky.utils import RunEngineInterrupted
    ns['_sim'].pause_in_align = True
    with pytest.raises(RunEngineInterrupted):            # Ctrl-C
        ns['RE'](ns['align_gi'](three_samples(ns)[:1]))
    assert ns['pil2M'].active_beamstop.get() == 'rod_removed'
    try:
        ns['RE'].abort('test')
    except Exception:
        pass
    assert ns['RE'].state == 'idle'
    assert ns['pil2M'].active_beamstop.get() == 'rod' and ns['attenuation'].get() == 1


def test_latest_alignment_survives_partial_realign_and_manual_mark(ns, tmp_path):
    samples = three_samples(ns)
    ns['SAMPLES'] = samples
    ns['align_gi_samples']()
    ns['_sim'].fail_x.add(0.0)
    ns['align_gi_samples'](ns['select'](samples, 2))     # re-align S2 only (fails)
    al = ns['load_alignment']()
    assert [al[n]['ok'] for n in ('S1', 'S2', 'S3')] == [True, False, True]
    ns['RE'](ns['bps'].mv(ns['piezo'].th, 0.42, ns['piezo'].y, 77.0))
    ns['mark_aligned'](2)                                # by key, after aligning by hand
    al = ns['load_alignment']()
    assert al['S2']['ok'] and (al['S2']['th'], al['S2']['y']) == (0.42, 77.0)
    ns['_docs'].clear()
    ns['RE'](ns['run_gi'](angles=(0.1,), arcs=(0,)))     # aligned=None: the saved file
    assert [s['sample'] for s in starts(ns)] == ['S1', 'S2', 'S3']
    with pytest.raises(ValueError, match='no alignment'):
        ns['YZ']['experiment'] = 'other'
        ns['ALIGNED'].clear()
        ns['RE'](ns['run_gi'](angles=(0.1,), arcs=(0,)))


def test_gi_series_skips_failed_alignment(ns):
    samples = three_samples(ns)
    ns['_sim'].fail_x.add(0.0)
    aligned = ns['align_gi_samples'](samples)
    ns['_docs'].clear()
    ns['RE'](ns['run_series'](samples, aligned, angles=(0.15,), max_cycles=1, duration=60))
    assert [s['sample'] for s in starts(ns)] == ['S1', 'S3']


def test_series_stops_instead_of_an_off_schedule_cycle(ns):
    sample = ns['make_samples'](['A'], [(0, 0)])
    ns['series_start']()
    ns['RE'](ns['run_series'](sample, duration=0.5, interval=0.4))
    # cycles at 0 and 0.4 s; the next would be due at 0.8 s > duration -> stop (the old loop
    # skipped the sleep and started a 3rd cycle at once)
    assert len(starts(ns)) == 2


def test_gi_huber_stage(ns):
    samples = ns['make_samples'](['A', 'B'], [(-5.0, 1.0), (5.0, 1.0)], axes=('sx', 'sy'))
    ns['RE'](ns['run_gi'](samples, align=True, stage='huber', angles=(0.12,), arcs=(0,),
                          x_offsets=(0, 0.3)))
    st = starts(ns)
    assert len(st) == 4
    assert {round(s['user_hints']['positions']['sx'], 3) for s in st} == {-5.0, -4.7, 5.0, 5.3}


def test_linkam_temperature_series(ns):
    samples = three_samples(ns)[:2]
    ns['RE'](ns['run_gi_temperatures']([25, -50.04], samples, settle=0, angles=(0.15,),
                                       arcs=(0,), lnp='Auto', end_T=25, off_at_end=True))
    st = starts(ns)
    names = [s['sample_name'] for s in st if 'user_hints' in s]
    assert any('_T25.0C_' in n for n in names) and any('_T-50.0C_' in n for n in names)
    assert ns['_sim'].align_calls == 4                   # re-aligned at each temperature
    assert ns['LThermal'].lnp_mode_set.get() == 'Auto'
    assert ns['LThermal'].cmd.get() == 0
    assert ns['LThermal'].temperature_setpoint.get() == 25
    ev = events(ns)
    assert 'LinkamThermal_temperature_current' in ev[-1]['data']


def test_linkam_timeout(ns):
    ns['LThermal'].lag.put(10.0)
    ns['RE'](ns['linkam_goto'](-100, timeout=0.2, poll=0.05, settle=0))     # warns, continues
    with pytest.raises(TimeoutError):
        ns['RE'](ns['linkam_goto'](-100, timeout=0.2, poll=0.05, settle=0, on_timeout='raise'))


def test_ec_series_schedule_and_readback(ns):
    sample = ns['make_samples'](['CuEC'], [(0, 0)])
    ns['ec_start']('test cell')
    ns['EC']['schedule'] = [(0, 0.0), (1e6, -0.5)]
    ns['RE'](ns['run_ec'](sample, max_cycles=3, duration=60, spots=(-100, 0, 100), t=0.5))
    st = starts(ns)
    assert len(st) == 3
    assert [s['user_hints']['frame_index'] for s in st] == [0, 1, 2]
    assert [s['user_hints']['positions']['x'] for s in st] == [-100, 0, 100]
    assert all('_E0.000V_' in s['sample_name'] for s in st)
    assert all(re.search(r'_000\d_\d+\.\ds_x', s['sample_name']) for s in st)
    assert 'ec_potential_setpoint' in events(ns)[0]['data']
    assert st[0]['user_hints']['series_t0'] == ns['YZ_SERIES']['t0']

    # analog readback wins over the schedule; continues the cycle counter
    ns['EC'].update(readback=ns['moxa_ch2'], scale=-2.0, offset=0.0)
    ns['RE'](ns['run_ec'](sample, max_cycles=1, duration=60, t=0.5))
    last = starts(ns)[-1]
    assert '_E-0.500V_' in last['sample_name'] and last['user_hints']['frame_index'] == 3
    assert 'moxa_out_ch2_read' in events(ns)[-1]['data']


def test_ec_typed_potential_is_read_every_frame(ns):
    sample = ns['make_samples'](['Cell1'], [(0, 0)])
    ns['ec_start']()
    ns['RE'](ns['run_ec'](sample, max_cycles=1, duration=60, t=0.5))     # OCV: no potential yet
    ns['ec_set_potential'](-0.25)                                       # e.g. during a pause
    ns['RE'](ns['run_ec'](sample, max_cycles=1, duration=60, t=0.5))
    n0, n1 = [s['sample_name'] for s in starts(ns)]
    assert '_E' not in n0 and '_E-0.250V_' in n1


def test_gi_series_with_swaxs_every(ns):
    samples = three_samples(ns)[:1]
    aligned = ns['align_gi_samples'](samples)
    ns['_docs'].clear()
    ns['series_start']()
    ns['RE'](ns['run_series'](samples, aligned, angles=(0.15,), max_cycles=2, duration=60,
                              swaxs_every=2))
    st = starts(ns)
    assert [s['user_hints']['detectors'] for s in st] == [['pil900KW'], ['pil900KW', 'pil2M'], ['pil900KW']]
    assert ns['waxs'].arc.position == 0


def test_grid_cells(ns):
    cells = ns['grid_cells']('ABCD', 24, first=(-50000, 1000), last_in_row=(53500, 1000),
                             first_in_last_row=(-50000, 14500), base={'sx': 12.5},
                             prefix='B1', names={'b1-a1': 'Water', 'B1-D24': 'PS 50k', 'B1-B03': 'x'})
    assert [c['name'] for c in cells] == ['Water_B1-A01', 'x_B1-B03', 'PS-50k_B1-D24']
    d24 = cells[-1]
    assert (d24['x'], d24['y'], d24['sx']) == (53500, 14500, 12.5)
    b03 = cells[1]
    assert (b03['x'], b03['y']) == (-50000 + 2 * 4500, 1000 + 4500)
    allc = ns['grid_cells'](2, 3, first=(0, 0), pitch=(1, 2), keep_empty=True)
    assert [c['name'] for c in allc] == ['A01', 'A02', 'A03', 'B01', 'B02', 'B03']
    with pytest.raises(ValueError):
        ns['grid_cells'](2, 3, first=(0, 0), keep_empty=True)


def test_make_samples_rejects_bad_input(ns):
    with pytest.raises(ValueError, match='duplicate'):
        ns['make_samples'](['a', 'a'], [(0, 0), (1, 1)])
    with pytest.raises(TypeError):
        ns['make_samples']({1: 'a'}, {1: {21100, -7100}})      # set literal (old ThreeGroups bug)
    with pytest.raises(ValueError, match='no position'):
        ns['make_samples']({1: 'a', 2: 'b'}, {1: (0, 0)})


# ---------------------------------------------------------------- experiment scripts (sim)
from sim_beamline import load  # noqa: E402


def test_scripts_load_without_side_effects(ns):
    for script in ('2026C3_HZheng.py', '2026C3_PGuo.py', '2026C3_TSAXS384.py', '2026C3_JMayer.py'):
        load(ns, script)
    assert starts(ns) == []                       # loading never takes data or moves motors


def test_hzheng_flow(ns):
    load(ns, '2026C3_HZheng.py')
    ns['align_gi_samples']()
    ns['RE'](ns['run_gi'](**ns['GI']))                 # latest saved alignment
    st = starts(ns)
    data = [s for s in st if 'user_hints' in s]
    gi = ns['GI']                                      # edited at the beamline: count from the script
    per_arc = len(ns['SAMPLES']) * len(gi['angles']) * len(gi['x_offsets'])
    assert len(data) == per_arc * len(gi['arcs'])
    assert all(s['sample_name'].startswith(ns['YZ']['user'] + '_') for s in data)
    assert sum('pil2M' in s['user_hints']['detectors'] for s in data) == per_arc


def test_hzheng_trans_flow(ns):
    load(ns, '2026C3_HZheng.py')
    ns['TSAMPLES'] = []
    with pytest.raises(ValueError, match='T_POS'):
        ns['run_trans_samples']()
    pos = {1: (-50000, 2000), 2: (-40000, 2000), 9: (30000, 2000)}
    names = {**ns['T_NAMES'], 9: 'Empty'}
    ns['TSAMPLES'] = ns['make_samples']({k: names[k] for k in pos}, pos, th=0)
    ns['RE'](ns['bps'].mv(ns['piezo'].th, 0.4))        # left at an aligned th by the GI runs
    ns['RE'](ns['run_trans_samples']())
    data = starts(ns)
    trans = ns['TRANS']
    assert len(data) == 3 * len(trans['arcs']) * len(trans['offsets'])
    assert all('deg' not in s['sample_name'] and s['geometry'] == 'transmission' for s in data)
    assert all(s['holder'] == 'transmission bar' for s in data)
    assert all(s['user_hints']['positions']['th'] == 0 for s in data)
    ns['RE'](ns['run_trans_samples']('Empty', t=5))
    new = starts(ns)[len(data):]
    assert {s['user_hints']['sample'] for s in new} == {'Empty'}
    assert all(s['sample_name'].endswith('_expt5s') for s in new)


def test_pguo_flow(ns):
    load(ns, '2026C3_PGuo.py')
    ns['align_gi_samples']()
    tseries = dict(ns['TSERIES'], settle=0)
    ns['RE'](ns['run_gi_temperatures']([25, -150], **tseries, **ns['GI']))
    names = [s['sample_name'] for s in starts(ns) if 'user_hints' in s]
    assert len(names) == 2 * 2 * 3 * 2
    assert sum('_T-150.0C_' in n for n in names) == 12
    assert ns['LThermal'].temperature_setpoint.get() == 25          # end_T


def test_tsaxs384_flow(ns, tmp_path):
    load(ns, '2026C3_TSAXS384.py')
    assert ns['SAMPLES'] == []                                        # nothing calibrated yet
    ns['BARS']['B2'].update(base={'sx': -20.0, 'sy': 5.0}, first=(-51750, -6750),
                            last_in_row=(51750, -6750), first_in_last_row=(-51750, 6750))
    csv_path = tmp_path / 'names.csv'
    csv_path.write_text('\ufeffcell,sample\nb2-a1,Empty\nB2-A02,Water\nB2-D24,PS 50k\nB1-A01,other bar\n',
                        encoding='utf-8')                  # Excel CSV with a BOM
    ns['NAMES_CSV'] = str(csv_path)
    cells = ns['bar_samples']('B2')
    assert [c['name'] for c in cells] == ['Empty_B2-A01', 'Water_B2-A02', 'PS-50k_B2-D24']
    ns['RE'](ns['run_trans'](cells, **ns['TRANS']))
    data = starts(ns)
    assert len(data) == 3 * 2
    last = data[-1]['user_hints']['positions']
    assert (last['sx'], last['sy'], last['x'], last['y']) == (-20.0, 5.0, -51750, -6750)


def test_jmayer_flow(ns):
    load(ns, '2026C3_JMayer.py')
    ns['align_gi_samples'](stage=ns['STAGE'])
    ns['EC']['schedule'] = [(0, None), (0.05, -0.2)]
    ns['ec_start']('sim')
    series = dict(ns['SERIES'], interval=0, max_cycles=3, duration=60)
    ns['RE'](ns['run_ec'](**series))
    names = [s['sample_name'] for s in starts(ns) if 'user_hints' in s]
    assert len(names) == 3 + 1                                       # + one SWAXS frame (cycle 0)
    assert names[0].startswith('JMayer_Cell1_0.1500deg_0000_')
    assert '_E' not in names[0] and '_E-0.200V_' in names[-1]
    ns['RE'](ns['run_ec'](**dict(ns['SERIES_TRANS'], interval=0, max_cycles=1, duration=60)))
    assert 'deg' not in starts(ns)[-1]['sample_name']


def test_preview_is_a_dry_run(ns, tmp_path):
    load(ns, '2026C3_PGuo.py')
    x_before = ns['piezo'].x.position
    n = ns['preview'](ns['run_gi_temperatures']([25, -150], realign=True, **ns['GI']))
    assert n == 2 * 2 * 3 * 2                                      # same exposures as the real run
    assert starts(ns) == [] and ns['piezo'].x.position == x_before   # nothing ran or moved
    assert ns['LThermal'].temperature_setpoint.get() == 25.0
    assert ns['_sim'].align_calls == 0
    assert not list(tmp_path.glob('logbook_*')) and not list(tmp_path.glob('alignment_*'))
    load(ns, '2026C3_JMayer.py')
    ns['ec_start']()
    assert ns['preview'](ns['run_ec'](aligned={'Cell1': dict(th=0.3, y=1.0, ok=True)},
                                      **ns['SERIES'])) == 2 + 1    # 2 cycles + SWAXS frame
    with pytest.raises(ValueError, match='not allowed'):
        ns['preview'](ns['run_trans'](arcs=(0, 10)))

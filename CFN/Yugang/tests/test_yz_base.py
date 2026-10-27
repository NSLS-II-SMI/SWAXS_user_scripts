"""
Offline tests of YZhang_SMI_Base.py with simulated devices (tests/sim_beamline.py).

    cd CFN/Yugang && python -m pytest -q tests
"""
import csv
import json
import os
import re
import sys
import time

import numpy as np
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


def test_series_no_wait_after_the_last_cycle(ns):
    sample = ns['make_samples'](['A'], [(0, 0)])
    t0 = time.time()
    ns['RE'](ns['run_series'](sample, interval=5, max_cycles=1, duration=60))
    assert len(starts(ns)) == 1 and time.time() - t0 < 2


def test_run_trans_with_linkam_T(ns):
    lk = ns['LThermal']
    lk.temperature_setpoint.put(-20.0)
    ns['RE'](ns['run_trans'](three_samples(ns)[:2], arcs=(20,), T=lk.temperature_current))
    st = starts(ns)
    assert len(st) == 2
    assert all('_z8000.00_T-20.0C_expt1s' in s['sample_name'] for s in st)
    assert all(s['user_hints']['temperature_C'] == -20.0 for s in st)
    assert 'LinkamThermal_temperature_current' in events(ns)[-1]['data']


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
    for script in ('2026C3_HZheng.py', '2026C3_PGuo.py', '2026C3_TSAXS384.py', '2026C3_JMayer.py',
                   '2026C3_Murray.py'):
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
    assert_saxs_at_top_arc(data, gi['arcs'])


def assert_saxs_at_top_arc(data, arcs):
    """saxs='max': 900KW at every arc, the 2M only with the highest arc."""
    for s in data:
        h = s['user_hints']
        assert 'pil900KW' in h['detectors']
        assert ('pil2M' in h['detectors']) == (h['waxs_arc_deg'] == max(arcs))
    assert {s['user_hints']['waxs_arc_deg'] for s in data} == set(arcs)


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
    assert_saxs_at_top_arc(data, trans['arcs'])
    ns['RE'](ns['run_trans_samples']('Empty', t=5))
    new = starts(ns)[len(data):]
    assert {s['user_hints']['sample'] for s in new} == {'Empty'}
    assert all(s['sample_name'].endswith('_expt5s') for s in new)


def load_pguo(ns, linkam):
    """load() of 2026C3_PGuo.py with its LINKAM switch set."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '2026C3_PGuo.py')
    with open(path) as f:
        src, n = re.subn(r'^LINKAM = \w+', f'LINKAM = {linkam}', f.read(), count=1, flags=re.M)
    assert n == 1
    exec(compile(src, path, 'exec'), ns)


def pguo_per_T(ns):
    gi = ns['GI']                                      # edited at the beamline: count from the script
    return len(ns['SAMPLES']) * len(gi['angles']) * len(gi['arcs']) * len(gi['x_offsets'])


def test_pguo_flow(ns):
    load_pguo(ns, True)
    assert ns['YZ']['experiment'] == 'PGuo_Linkam_GI'
    ns['align_gi_samples']()
    tseries = dict(ns['TSERIES'], settle=0)
    ns['RE'](ns['run_gi_temperatures']([25, -150], **tseries, **ns['GI']))
    data = [s for s in starts(ns) if 'user_hints' in s]
    names = [s['sample_name'] for s in data]
    assert len(names) == 2 * pguo_per_T(ns)
    assert sum('_T-150.0C_' in n for n in names) == pguo_per_T(ns)
    assert_saxs_at_top_arc(data, ns['GI']['arcs'])
    assert ns['LThermal'].temperature_setpoint.get() == 25          # end_T


def test_pguo_rt_flow(ns, tmp_path):
    load_pguo(ns, False)
    assert ns['YZ']['experiment'] == 'PGuo_GI_RT'
    ns['LThermal'] = None                              # any Linkam access would raise
    ns['align_gi_samples']()
    assert (tmp_path / 'alignment_PGuo_GI_RT_latest.json').exists()
    ns['RE'](ns['run_gi_rt']())
    data = [s for s in starts(ns) if 'user_hints' in s]
    assert len(data) == pguo_per_T(ns)
    assert all(s['sample_name'].startswith('PGuo_') and '_T' not in s['sample_name'] for s in data)
    assert all(s['holder'] == 'Al GI bar' and 'temperature_C' not in s['user_hints'] for s in data)
    assert_saxs_at_top_arc(data, ns['GI']['arcs'])
    ns['RE'](ns['run_gi_rt'](ns['SAMPLES'][0]['key'], arcs=(0, 20, 40), t=5))
    new = [s for s in starts(ns) if 'user_hints' in s][len(data):]
    assert {s['user_hints']['sample'] for s in new} == {ns['SAMPLES'][0]['name']}
    assert all(s['sample_name'].endswith('_expt5s') for s in new)
    assert_saxs_at_top_arc(new, (0, 20, 40))


def test_pguo_manual_T(ns, tmp_path):
    load_pguo(ns, True)
    lk, sim = ns['LThermal'], ns['_sim']
    ns['align_gi_samples']()                                         # RT
    lk.temperature_setpoint.put(-100.0)                              # set by hand on the controller
    lk.lag.put(0.3)
    n_align = sim.align_calls
    assert ns['preview'](ns['run_gi_at_T']()) == pguo_per_T(ns)      # dry run
    assert sim.align_calls == n_align                                # nothing aligned
    assert not any('user_hints' in s for s in starts(ns))            # nothing measured
    ns['RE'](ns['run_gi_at_T']())
    assert sim.align_calls == n_align + len(ns['SAMPLES'])           # re-aligned at the new T
    per_T = tmp_path / 'alignment_PGuo_Linkam_GI_T-100C_latest.json'
    latest = tmp_path / 'alignment_PGuo_Linkam_GI_latest.json'
    assert json.loads(per_T.read_text()) == json.loads(latest.read_text())   # next T starts here
    data = [s for s in starts(ns) if 'user_hints' in s]
    assert len(data) == pguo_per_T(ns)
    assert all('_T-99.7C_' in s['sample_name'] for s in data)
    assert_saxs_at_top_arc(data, ns['GI']['arcs'])
    assert lk.temperature_setpoint.get() == -100.0 and lk.cmd.get() == 0    # Linkam only read
    ns['RE'](ns['run_gi_at_T'](realign=False, t=5))
    assert sim.align_calls == n_align + len(ns['SAMPLES'])
    new = [s for s in starts(ns) if 'user_hints' in s][len(data):]
    assert len(new) == pguo_per_T(ns) and all(s['sample_name'].endswith('_expt5s') for s in new)


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


def test_tsaxs384_holder55(ns):
    load(ns, '2026C3_TSAXS384.py')
    H, ova, PY0 = ns['HOLDER55'], ns['ova_cam'], ns['PY0']
    blank = 'carbon_paper_after_reaction'
    assert len(H) == 56 and len({s['name'] for s in H}) == 56
    height = lambda sy, y: sy + (y - PY0) / 1000                   # Huber sy + piezo y, mm
    for n, (sy, x, y) in ns['MEASURED55'].items():                 # measured spots stay where measured
        s = ns['select'](H, n)[0]
        assert ns['_X55'](s) == x and s['position'] == 'measured'
        assert abs(height(s['sy'], s['y']) - height(sy, y)) < 1e-3
    rows = {}
    for s in H:
        rows.setdefault(s['array_row'], []).append(s)
    assert all(len({s['sy'] for s in r}) == 1 for r in rows.values())   # one Huber sy per row
    assert [s['key'] for s in rows[0]] == [1, 11, 20, 28, 35, 41, 46, 50, 53, 55]
    assert [s['key'] for s in rows[1]] == [54, 51, 47, 42, 36, 29, 21, 12, 2]
    assert (rows[2][0]['key'], rows[2][-1]['key']) == (3, 52)
    assert [s['key'] for s in rows[4]][:2] == [blank, 5]
    assert all(ns['LIM55']['sy'][0] <= s['sy'] <= ns['LIM55']['sy'][1] for s in H)
    y_lo, y_hi = ns['LIM55']['y']
    assert all(y_lo <= s['y'] - 900 and s['y'] + 900 <= y_hi for s in H)   # crosses in piezo y travel
    x_lo, x_hi = ns['LIM55']['x']
    assert all(x_lo <= s['x'] - 900 and s['x'] + 900 <= x_hi for s in H)   # and piezo x travel
    shifted = [s['key'] for s in H if s['sx'] != ns['SX55']]
    assert shifted == [53, 55, 54, 52]                             # far left: Huber sx shifted
    assert rows[0][0]['sy'] > max(ns['MEASURED55'][n][0] for n in (1, 28))   # Huber up, piezo y down
    assert ns['preview'](ns['run_holder_55after']()) == 56 * 13 * 3
    assert ns['preview'](ns['run_holder_55after'](rows=range(1, 10))) == (56 - 10) * 13 * 3
    assert ova.written == [] and starts(ns) == []                  # the dry run wrote nothing

    msgs = []
    ns['RE'].msg_hook = msgs.append
    ns['RE'](ns['run_holder_55after'](1, 11, 54, 2, blank))       # rows 0, 1 and 4
    huber = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].y]
    row_sy = [rows[0][0]['sy'], rows[1][0]['sy'], rows[4][0]['sy']]
    assert [h for h in huber if h in row_sy] == row_sy                    # once per row
    assert all(abs(b - a) <= ns['HUBER_Y_STEP'] + 1e-9 for a, b in zip([0.0] + huber, huber))   # steps
    huber_x = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].x]
    assert huber_x == [ns['select'](H, 54)[0]['sx'], ns['SX55']]   # for 54, back for the blank
    data = starts(ns)
    assert len(data) == 5 * 13 * 3
    order = list(dict.fromkeys(s['user_hints']['sample_info']['key'] for s in data))
    assert order == [1, 11, 2, 54, blank]                          # row 1 starts nearest row 0's end
    arcs = [s['user_hints']['waxs_arc_deg'] for s in data]
    assert [arcs[i * 13 * 3] for i in (0, 2, 3, 4)] == [0, 40, 0, 40]   # arcs alternate per Huber position
    assert len(ova.written) == 5 and blank in ova.written[-1]
    assert all(w.startswith(ns['YZ']['ova_dir']) and w.endswith('_OVA') for w in ova.written)
    assert_saxs_at_top_arc(data, (0, 20, 40))
    s11 = ns['select'](H, 11)[0]
    cross = [(s['user_hints']['positions']['x'] - s11['x'], s['user_hints']['positions']['y'] - s11['y'])
             for s in data if s['user_hints']['sample_info']['key'] == 11
             and s['user_hints']['waxs_arc_deg'] == 0]
    assert cross == list(ns['CROSS55'])
    del ns['_docs'][:]
    ns['RE'](ns['run_holder_55after'](arcs=(40,), offsets=((0, 0),), ova=False))   # whole array, fast
    order = [s['user_hints']['sample_info']['key'] for s in starts(ns)]
    assert order == [s['key'] for s in H]                          # S1 -> S55, S54 -> S2, S3 -> S52, ...
    assert order[9:11] == [55, 54] and order[18:20] == [2, 3]
    ns['LIM55']['y'] = (-20000, s11['y'] + 800)                    # 11's cross reaches y + 900
    with pytest.raises(ValueError, match='out of travel'):
        ns['run_holder_55after'](11)


def test_tsaxs384_holder55_before(ns):
    load(ns, '2026C3_TSAXS384.py')
    H, PY0 = ns['HOLDER55B'], ns['PY0']                            # as centered on 10-20: 10, 31, 1, 55
    assert len(H) == 55 and {s['sx'] for s in H} == {-2.5}         # the Huber x stays where measured
    assert len({s['sy'] for s in H}) == 3 and H[0]['key'] == 10    # 3 Huber y, from the top
    assert min(s['y'] for s in H) - 900 >= ns['LIM55']['y'][0] == -9310   # piezo y floor (10-20)
    for n, (sy, x, y, sx) in ns['MEASURED55B'].items():
        s = ns['select'](H, n)[0]
        assert s['x'] == x and abs(s['sy'] + (s['y'] - PY0) / 1000 - (sy + (y - PY0) / 1000)) < 1e-3
    ns['check_holder55'](H, ns['CROSS55'], ns['LIM55B'])
    assert ns['preview'](ns['run_holder_55before']()) == 55 * 13 * 3

    ns['MEASURED55B'].clear()
    ns['HOLDER55B'] = ns['holder55b_samples']()
    assert ns['HOLDER55B'] == []                                   # nothing measured
    with pytest.raises(ValueError, match='not calibrated'):
        ns['run_holder_55before']()
    PIX = ns['PIX55B']
    c, s_ = np.cos(np.radians(1)), np.sin(np.radians(1))
    stage = lambda px, py: (0.0875 * (c * (px - 600) - s_ * (py - 600)),   # pixel -> (X, V) mm
                            0.0875 * (s_ * (px - 600) + c * (py - 600)))

    def stage_pos(n):                                              # centered by hand: (sy, x, y)
        X, V = stage(*PIX[n])
        return (round(V - 2, 3), X * 1000, PY0 + 2000)
    ns['MEASURED55B'].update({n: stage_pos(n) for n in (1, 10)})
    assert ns['holder55b_samples']() == []                         # 2 spots: not yet
    ns['MEASURED55B'][5] = stage_pos(5)                            # 1, 5, 10: one PIPETMAX column
    with pytest.raises(ValueError, match='>= 3 spots far apart'):
        ns['holder55b_samples']()
    ns['MEASURED55B'].clear()
    ns['MEASURED55B'].update({n: stage_pos(n) for n in (1, 10, 55, 33)})
    ns['BLANKS55B']['carbon_paper_as_prepared'] = (-5, 0, PY0, 4)
    H = ns['HOLDER55B'] = ns['holder55b_samples']()
    assert len(H) == 56 and len({s['name'] for s in H}) == 56
    assert ns['select'](H, 33)[0]['name'] == 'Sample000033_B001_Au1Ag6Cu3_AsPrepared'
    for s in H:
        if s['key'] in PIX:                                        # every spot from the photo
            X, V = stage(*PIX[s['key']])
            assert abs(ns['_X55'](s) - X * 1000) < 1 and abs(s['sy'] + (s['y'] - PY0) / 1000 - V) < 1e-3
            assert s['position'] == ('measured' if s['key'] in ns['MEASURED55B'] else 'photo')
    bands = list(dict.fromkeys(s['sy'] for s in H))
    assert len(bands) == 2                                         # 2 Huber sy for 10 rows (as Box 1)
    assert [s['array_row'] for s in H] == sorted((s['array_row'] for s in H), reverse=True)  # from the top
    assert H[0]['key'] == 10 and {s['sx'] for s in H} == {ns['SX55']}
    ns['check_holder55'](H)                                        # crosses within travel
    assert ns['preview'](ns['run_holder_55before']()) == 56 * 13 * 3

    msgs = []
    ns['RE'].msg_hook = msgs.append
    ns['RE'](ns['run_holder_55before'](1, 10, 55))                 # rows 9 (10) and 0 (1, 55)
    data = starts(ns)
    arcs = [d['user_hints']['waxs_arc_deg'] for d in data]
    assert arcs == sorted(arcs) and len(data) == 3 * 13 * 3        # one arc at a time
    keys = [d['user_hints']['sample_info']['key'] for d in data]
    order = [s['key'] for s in H if s['key'] in (1, 10, 55)]
    assert order[0] == 10 and list(dict.fromkeys(keys[:39])) == order
    assert list(dict.fromkeys(keys[39:78])) == order[::-1]         # next arc: reversed
    assert len(ns['ova_cam'].written) == 3                         # camera on the first arc only
    assert_saxs_at_top_arc(data, (0, 20, 40))
    huber_y = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].y]
    b10, b1 = (ns['select'](H, n)[0]['sy'] for n in (10, 1))      # top and bottom band
    assert [h for h in huber_y if h in bands] == [b10, b1, b10, b1]


def test_tsaxs384_cliu_plate(ns):
    load(ns, '2026C3_TSAXS384.py')
    P, cal = ns['PLATE_CLIU'], ns['CAL_CLIU']                      # the corners measured 10-20
    wells = [s['well'] for s in P]
    assert len(P) == 73 + 1 and len(set(wells)) == len(P)          # rows A .. M + the A1 blank
    assert not set(ns['CLIU_SKIP']) & set(wells) and not [w for w in wells if w[0] == 'P']
    assert all(s['name'].startswith('CL_') for s in P)
    assert ns['select'](P, 'M18')[0]['name'] == 'CL_Sample000311_B006_CuOH2_Powder'
    a1 = ns['select'](P, 'A1')[0]                                  # a corner stays where measured
    sx, sy, x, y = cal['A1']
    assert abs(ns['_X55'](a1) - (x + sx * 1000)) < 1 and abs(a1['sy'] + (a1['y'] - 12300) / 1000 - sy) < 1e-3
    x_lo, x_hi = ns['LIM_CLIU']['x']
    y_lo, y_hi = ns['LIM_CLIU']['y']
    assert ns['CROSS_CLIU'] == ((0, 0), (0, -500), (0, 500))           # centre, then y -500, 500
    assert all(x_lo <= s['x'] <= x_hi for s in P)
    assert all(y_lo <= s['y'] - 500 and s['y'] + 500 <= y_hi for s in P)
    stops = list(dict.fromkeys((s['sx'], s['sy']) for s in P))
    assert len(stops) == 3 and {a for a, _ in stops} == {-2.5}      # 3 Huber y bands, one Huber x
    assert ns['select'](P, 'A1')[0]['x'] == -56000 and ns['select'](P, 'A24')[0]['x'] == 47300
    assert P[0]['plate_row'] == 'M' and P[-1]['plate_row'] == 'A'  # from the top (N) down
    assert all(ns['LIM55']['sy'][0] <= b <= ns['LIM55']['sy'][1] for _, b in stops)
    assert ns['preview'](ns['run_cliu_box1']()) == 74 * 3 * 3

    msgs = []
    ns['RE'].msg_hook = msgs.append
    ns['RE'](ns['run_cliu_box1']('M2', 'K14', 'C2', 'A24'))       # one well at 4 Huber positions
    data = starts(ns)
    arcs = [d['user_hints']['waxs_arc_deg'] for d in data]
    assert arcs == sorted(arcs) and len(data) == 4 * 3 * 3         # one arc at a time over all wells
    keys = [d['user_hints']['sample_info']['key'] for d in data]
    assert list(dict.fromkeys(keys[:12])) == ['M2', 'K14', 'C2', 'A24']
    assert list(dict.fromkeys(keys[12:24])) == ['A24', 'C2', 'K14', 'M2']   # next arc: reversed
    huber_x = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].x]
    assert huber_x == [-2.5]                                       # the Huber x moves once
    assert len(ns['ova_cam'].written) == 4                         # camera on the first arc only
    assert_saxs_at_top_arc(data, (0, 20, 40))
    huber_y = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].y]
    band = [s['sy'] for s in ns['select'](P, 'M2', 'C2', 'A24')]
    assert [h for h in huber_y if h in band] == [band[0], band[1], band[2], band[1], band[0], band[1], band[2]]
    assert all(abs(b - a) <= ns['HUBER_Y_STEP'] + 1e-9 for a, b in zip([0.0] + huber_y, huber_y))

    PP = ns['PLATE_CLIU_P']                                        # row P, after pushing the plate down
    assert [s['well'] for s in PP] == ['P1', 'P3', 'P8', 'P10', 'P12', 'P14', 'P16', 'P20', 'P24']
    assert {s['sy'] for s in PP} == {-30} and {s['sx'] for s in PP} == {-2.5}   # the Huber stays put
    for w, (sx, sy, x, y) in ns['CAL_CLIU_P'].items():             # the centered wells as measured
        assert ns['select'](PP, w)[0]['x'] == x and ns['select'](PP, w)[0]['y'] == y
    assert PP[0]['name'].startswith('CL_')
    assert all(x_lo <= s['x'] <= x_hi for s in PP)
    assert ns['preview'](ns['run_cliu_box1_P']()) == 9 * 3 * 3



def test_tsaxs384_cliu_box2(ns):
    load(ns, '2026C3_TSAXS384.py')
    P = ns['PLATE_CLIU2']                                          # corners A1, A24, M1, M24 (10-21, run2)
    wells = [s['well'] for s in P]
    assert len(ns['CLIU_BOX2']) == 81 and len(P) == 86 - 21 and len(set(wells)) == len(P)
    assert not [w for w in wells if w[0] in 'NP']                  # rows N, P: after the push
    name = {s['well']: s['name'] for s in P}
    assert name['B2'] == 'CL_Sample000225_B005_Cu10_Suspension_run2' and name['B24'] == 'CL_EmptyWell_B24_run2'
    assert (name['D24'], name['F23'], name['F24']) == ('AgBH_run2', 'GL_52C_run2', 'MH_5_61_A_run2')
    assert ns['TRANS_CLIU2']['md']['run_batch'] == 'Box2_run2'      # re-run after a beam error (10-21)
    assert ns['select'](P, 'D24')[0]['role'] == 'calibrant'
    for w, (sx, sy, x, y) in ns['CAL_CLIU2'].items():              # a corner stays where measured
        if w in name:
            s = ns['select'](P, w)[0]
            assert abs(s['x'] - x) <= 1 and abs(s['sy'] + (s['y'] - 12300) / 1000 - (sy + (y - 12300) / 1000)) < 1e-3
    stops = list(dict.fromkeys((s['sx'], s['sy']) for s in P))
    assert {a for a, _ in stops} == {-2} and len(stops) == 2       # Huber x as measured, 2 Huber y
    assert P[0]['plate_row'] == 'L' and P[-1]['plate_row'] == 'B'  # from the top
    ns['check_holder55'](P, ns['CROSS_CLIU'], ns['LIM_CLIU'])
    assert ns['preview'](ns['run_cliu_box2']()) == 65 * 3 * 3
    PP = ns['PLATE_CLIU2_PUSHED']                                  # rows N, P after the push (10-21)
    assert sorted(s['well'] for s in PP) == sorted([f'{r}{c}' for r in 'NP' for c in range(2, 21, 2)] + ['P24'])
    assert {(s['sx'], s['sy']) for s in PP} == {(-2, -30)}         # one Huber position
    assert ns['select'](PP, 'P24')[0]['x'] == 48200                # the blank, where centered
    ns['check_holder55'](PP, ns['CROSS_CLIU'], ns['LIM_CLIU'])
    assert ns['preview'](ns['run_cliu_box2_pushed']()) == 21 * 3 * 3


def test_tsaxs384_wliu_box3(ns):
    load(ns, '2026C3_TSAXS384.py')
    P = ns['PLATE_WLIU']                                           # corners C7, C17, H7, H17 (10-21)
    for w, (sx, sy, x, y) in ns['CAL_WLIU'].items():               # the corners stay where measured
        s = ns['select'](P, w)[0]
        assert abs(s['x'] - x) <= 1 and abs(s['sy'] + (s['y'] - 12300) / 1000 - (sy + (y - 12300) / 1000)) < 1e-3
    assert {s['sx'] for s in P} == {-2} and P[0]['plate_row'] == 'H'
    ns['check_holder55'](P, ns['CROSS_CLIU'], ns['LIM_CLIU'])
    name = {s['well']: s['name'] for s in P}
    assert len(P) == 50 + 6 and len(set(name.values())) == 56
    assert (name['H8'], name['H17'], name['G8'], name['E17'], name['C17']) == \
        ('WL_Au_S6', 'WL_Au_S15', 'WL_Au_S16', 'WL_Au_S45', 'WL_Au_S55')
    assert name['D11'] == 'WL_SiO2_D11' and ns['select'](P, 'G7')[0]['role'] == 'blank'
    assert len({(s['sx'], s['sy']) for s in P}) == 2               # rows C .. H: 2 Huber y, one x
    assert ns['preview'](ns['run_wliu_box3']()) == 56 * 3 * 3
    ns['RE'](ns['run_wliu_box3']('H8', 'C17', arcs=(20,)))
    assert [d['user_hints']['sample_info']['key'] for d in starts(ns)][::3] == ['H8', 'C17']

def test_huber_y_waits_while_hot(ns):
    load(ns, '2026C3_TSAXS384.py')
    readings = iter([50.0, 47.0, 44.0] + [40.0] * 50)              # hot, then cooling

    class Thermo(ns['Signal']):
        def get(self, **kw):
            return next(readings)
    ns['huber_y_T'] = Thermo(name='huber_y_T')
    ns['HUBER_T_WAIT'] = 0.01
    msgs = []
    ns['RE'].msg_hook = msgs.append
    ns['RE'](ns['huber_y_mv'](-12.0))                              # from 0: 3 steps of 4 mm
    sets = [m.args[0] for m in msgs if m.command == 'set' and m.obj is ns['stage'].y]
    assert sets == [-4.0, -8.0, -12.0]
    first_set = next(i for i, m in enumerate(msgs) if m.command == 'set')
    assert sum(m.command == 'sleep' for m in msgs[:first_set]) == 2    # waited 50 -> 47 -> 44 C
    ns['huber_y_T'] = ns['Signal'](value=60.0, name='huber_y_T')  # hot: a dry run must not wait
    assert ns['preview'](ns['huber_y_mv'](0.0)) == 0


def test_jmayer_flow(ns):
    load(ns, '2026C3_JMayer.py')
    RE, data = ns['RE'], lambda: [s for s in starts(ns) if 'user_hints' in s]
    with pytest.raises(ValueError, match='new_sample'):
        RE(ns['run_cell']())
    ns['new_sample']('NiOx 1', electrode='NiOx')                  # dry cell, moves to CELL
    cell = ns['CELL']
    assert [ns['AXES'][a].position for a in cell] == list(cell.values())
    ns['align_cell']()
    RE(ns['run_cell']())                                          # ex situ: 3 angles at arc 20
    st = data()
    assert [s['user_hints']['incident_angle_deg'] for s in st] == list(ns['GI']['angles'])
    assert all(s['user_hints']['detectors'] == ['pil900KW', 'pil2M'] for s in st)
    assert st[0]['sample_name'].startswith(f"JMayer_NiOx-1_exsitu_{ns['GI']['angles'][0]:.4f}deg_x0.00_")
    assert all('_E' not in s['sample_name'] for s in st)
    assert st[0]['user_hints']['sample_info']['electrode'] == 'NiOx'
    with pytest.raises(ValueError, match='add_electrolyte'):
        RE(ns['run_insitu']())
    th, y, sim = ns['piezo'].th, ns['piezo'].y, ns['_sim']
    al = ns['align_height'](th=0.52)                              # theta by hand: only y is scanned
    assert (al['NiOx-1_exsitu']['th'], al['NiOx-1_exsitu']['y']) == (0.52, 150.0)
    assert sim.scans == [('y direct', 0.52)] and th.position == 0.52
    assert ns['pil2M'].active_beamstop.get() == 'rod' and ns['attenuation'].get() == 1
    sim.fail_x.add(0.0)
    RE(ns['bps'].mv(y, 140.0))
    ns['align_height']()                                          # fails: y back, alignment kept
    assert y.position == 140.0 and ns['pil2M'].active_beamstop.get() == 'rod'
    assert ns['load_alignment']()['NiOx-1_exsitu']['y'] == 150.0
    sim.fail_x.clear()

    sim.scans.clear()                                             # reflected beam only
    RE(ns['bps'].mv(th, 0.58, y, 145.0))                          # reflection found by hand
    al = ns['align_cell_ref'](reflect=0.15)
    assert sim.scans == [('th', 0.58), ('y reflected', 0.65), ('th', 0.65)]   # no direct beam
    assert sim.roi_angle == 0.15
    a = al['NiOx-1_exsitu']
    assert (round(a['th'], 4), a['y'], a['angle']) == (0.5, 150.5, 0.15)      # th0 = th - 0.15
    assert round(th.position, 4) == 0.5 and ns['attenuation'].get() == 1
    sim.scans.clear()
    RE(ns['bps'].mv(th, 0.9, y, 145.0))                           # reflection not in the th scan
    ns['align_cell_ref']()
    assert (th.position, y.position) == (0.9, 145.0)              # back where it was set by hand
    assert ns['pil2M'].active_beamstop.get() == 'rod'
    assert round(ns['load_alignment']()['NiOx-1_exsitu']['th'], 4) == 0.5
    sim.scans.clear()
    ns['align_cell_ref'](th=0.66, th_scan=False)                  # y on the reflection, th as set
    assert sim.scans == [('y reflected', 0.66)]
    assert round(ns['load_alignment']()['NiOx-1_exsitu']['th'], 4) == 0.51
    sim.scans.clear(), sim.modes.clear()                          # the manual procedure in one call
    RE(ns['bps'].mv(th, 0.0, y, 145.0))                           # th 0.65 from the reflection
    al = ns['do_align_using_ref_beam'](ref=0.15, th_range=1, point=51)
    assert sim.scans == [('y direct', 0.0), ('th search', 0.0, 1, 51), ('th', 0.65),
                         ('y reflected', 0.65), ('th', 0.65)]
    assert sim.modes == ['alignment', 'measurement']              # one alignment mode, not two
    a = al['NiOx-1_exsitu']
    assert (round(a['th'], 4), a['y'], round(th.position, 4)) == (0.5, 150.5, 0.5)
    sim.scans.clear(), sim.modes.clear()
    RE(ns['bps'].mv(th, 2.0, y, 145.0))                           # reflection outside +-1 deg
    ns['do_align_using_ref_beam'](height=False)
    assert sim.scans == [('th search', 2.0, 1, 51)] and (th.position, y.position) == (2.0, 145.0)
    assert sim.modes == ['alignment', 'measurement'] and ns['attenuation'].get() == 1
    ns['align_cell_ref'](th=0.6)
    ns['_docs'].clear()
    RE(ns['run_cell'](angles=(0.1,)))                             # measures at th0 + 0.1
    pos = data()[0]['user_hints']['positions']
    assert (round(pos['th'], 4), pos['y']) == (0.6, 150.5)

    ns['add_electrolyte'](electrolyte='KOH')
    al = ns['align_cell']()                                       # in situ: its own alignment
    assert {'NiOx-1_exsitu', 'NiOx-1_insitu'} <= set(al)
    ns['_docs'].clear()
    RE(ns['run_cell'](angles=(0.15,)))                            # OCV: no _E
    assert data()[0]['sample_name'].startswith('JMayer_NiOx-1_insitu_0.1500deg_x')
    assert '_E' not in data()[0]['sample_name']
    ns['ec_start']('sim')
    ns['ec_set_potential'](-0.5)
    assert ns['preview'](ns['run_insitu']()) == 2                 # 2 cycles, counter untouched
    ns['_docs'].clear()
    RE(ns['run_insitu'](interval=0, max_cycles=3))
    st = data()
    assert [s['user_hints']['frame_index'] for s in st] == [0, 1, 2]
    assert [s['user_hints']['positions']['x'] for s in st] == [-200, 0, 200]
    assert all(s['user_hints']['detectors'] == ['pil900KW', 'pil2M'] for s in st)
    assert all(re.search(r'_insitu_0\.1500deg_000\d_\d+\.\ds_x.*_E-0\.500V_expt1s$', s['sample_name'])
               for s in st)
    ns['_docs'].clear()
    RE(ns['run_cell'](angles=(0.15,)))                            # all angles at the potential
    assert '_E-0.500V_' in data()[0]['sample_name']

    RE(ns['bps'].mv(ns['stage'].y, 0.0))                          # Huber off the cell: refuse
    with pytest.raises(RuntimeError, match='goto_cell'):
        RE(ns['run_insitu'](max_cycles=1))
    ns['_docs'].clear()
    ns['new_sample']('S2')                                        # resets clock and potential
    assert ns['YZ_SERIES']['t0'] is None and ns['EC']['potential'] is None
    ns['snap_saxs']()
    ns['snap_waxs']('S2 check', arc=0)
    ns['snap_swaxs'](t=2, arc=20)
    st = data()
    assert [s['user_hints']['detectors'] for s in st] == [['pil2M'], ['pil900KW'], ['pil900KW', 'pil2M']]
    assert [s['user_hints']['waxs_arc_deg'] for s in st] == [20, 0, 20]
    assert st[1]['sample_name'].startswith(f"JMayer_S2-check_x0.00_y{cell['y']:.2f}_z{cell['z']:.2f}_")
    ns['add_electrolyte']()
    assert ns['preview'](ns['run_insitu'](aligned={'S2_insitu': dict(th=0.3, y=1.0, ok=True)})) == 2
    assert (ns['YZ_SERIES']['t0'], ns['YZ_SERIES']['cycle']) == (None, 0)   # dry run: no clock
    load(ns, '2026C3_JMayer.py')                                  # re-running keeps the sample
    assert ns['SAMPLES'][0]['name'] == 'S2_insitu'


def test_preview_is_a_dry_run(ns, tmp_path):
    load_pguo(ns, True)
    x_before = ns['piezo'].x.position
    n = ns['preview'](ns['run_gi_temperatures']([25, -150], realign=True, **ns['GI']))
    assert n == 2 * pguo_per_T(ns)                                 # same exposures as the real run
    assert starts(ns) == [] and ns['piezo'].x.position == x_before   # nothing ran or moved
    assert ns['LThermal'].temperature_setpoint.get() == 25.0
    assert ns['_sim'].align_calls == 0
    assert not list(tmp_path.glob('logbook_*')) and not list(tmp_path.glob('alignment_*'))
    load(ns, '2026C3_JMayer.py')
    ns['new_sample']('Cell1', move=False)
    ns['ec_start']()
    assert ns['preview'](ns['run_ec'](aligned={'Cell1_exsitu': dict(th=0.3, y=1.0, ok=True)},
                                      **ns['SERIES'])) == 2        # 2 cycles
    with pytest.raises(ValueError, match='not allowed'):
        ns['preview'](ns['run_trans'](arcs=(0, 10)))


def test_murray_linkam_flow(ns, capsys, monkeypatch):
    load(ns, '2026C3_Murray.py')
    RE, lk = ns['RE'], ns['LThermal']
    data = lambda: [s for s in starts(ns) if 'user_hints' in s]      # noqa: E731
    with pytest.raises(ValueError, match='new_sample'):
        RE(ns['measure_T']())
    piezo, huber = ns['piezo'], ns['stage']
    RE(ns['bps'].mv(piezo.x, 100.0, piezo.th, 0.4))
    moved = []                                                    # every motor any plan commands
    RE.msg_hook = lambda msg: moved.append(msg.obj.name) if msg.command == 'set' else None
    ns['LINKAM_POS'].update(sx=12.5, sy=3.0)                      # as edited at the beamline
    ns['POS_XY_LIST'] = ns['snake_xy'](3, 2, 0.2, 0.1)            # 6 spots
    ns['LK_SPOT']['next'] = 4                                     # left over from another sample
    ns['new_sample']('PbS 22B', note='film')                      # Huber there, resets clock + spots
    assert [huber.x.position, huber.y.position] == [12.5, 3.0]
    assert ns['LK_SPOT']['next'] == 0

    def at_spots(st, idx):                                        # frames on these POS_XY_LIST spots
        dxy = [ns['POS_XY_LIST'][i] for i in idx]
        assert [s['user_hints']['sample_info']['spot'] for s in st] == idx
        assert [s['user_hints']['positions']['sx'] for s in st] == pytest.approx([12.5 + x for x, _ in dxy])
        assert [s['user_hints']['positions']['sy'] for s in st] == pytest.approx([3.0 + y for _, y in dxy])
        assert all(huber_tokens(s) in s['sample_name'] for s in st)
        return True

    RE(ns['measure_T']())                                         # RT; the Linkam is only read
    st, meas = data(), ns['MEASURE']
    assert len(st) == meas['n_spots'] * len(meas['arcs']) and at_spots(st, [0])
    assert all(s['sample_name'].startswith('Murray_PbS-22B_x') for s in st)
    assert all(huber_tokens(s) in s['sample_name'] for s in st)  # _x/_y/_z = Huber sx/sy/sz
    assert all(s['sample_name'].endswith(f"_T25.0C_expt{meas['t']:g}s") for s in st)
    assert_saxs_at_top_arc(st, meas['arcs'])
    assert all(s['experiment'] == 'Murray_Linkam' and s['holder'] == 'Linkam LN2 stage' for s in st)
    assert st[0]['user_hints']['sample_info']['note'] == 'film'
    assert {'LinkamThermal_temperature_current', 'LinkamThermal_temperature_setpoint'} \
        <= set(events(ns)[-1]['data'])
    assert (lk.temperature_setpoint.get(), lk.cmd.get()) == (25.0, 0)

    capsys.readouterr()
    assert ns['get_T']() == 25.0                                  # read only
    assert 'Linkam 25.0 C: setpoint 25.0 C (+0.0), ramp 10 C/min, OFF' in capsys.readouterr().out
    ns['set_T'](-50)                                              # T by hand: waits until there
    assert (lk.temperature_setpoint.get(), lk.cmd.get(), lk.lnp_mode_set.get()) == (-50.0, 1, 'Auto')
    assert f"Linkam -50.0 C: setpoint -50.0 C (+0.0), ramp {ns['TSERIES']['rate']:g} C/min, on" in capsys.readouterr().out
    lk.lag.put(3.0)                                               # still ramping: warns, measures
    lk.status_code.put(8 | 16)
    assert ns['get_T'](show=False) == -47.0 and not capsys.readouterr().out
    ns['get_T']()
    assert f"Linkam -47.0 C: setpoint -50.0 C (+3.0), ramp {ns['TSERIES']['rate']:g} C/min, on, not at setpoint, " \
        'LN2 pump on (auto)' in capsys.readouterr().out
    def not_connected(**kw):
        raise TimeoutError('STATUS not connected')
    monkeypatch.setattr(lk.status_code, 'get', not_connected)
    assert ns['get_T']() == -47.0                                 # status PV not connected: T still read
    assert 'on\n' in capsys.readouterr().out
    ns['_docs'].clear()
    RE(ns['measure_T'](t=2))
    assert data() and all('_T-47.0C_expt2s' in s['sample_name'] for s in data())
    assert at_spots(data(), [1])
    lk.lag.put(0.0)

    ns['series_start']('-50 C')                                   # time track at -50 C
    ns['_docs'].clear()
    RE(ns['track_T'](interval=0, max_cycles=3))
    st = data()
    assert [s['user_hints']['frame_index'] for s in st] == [0, 1, 2]
    assert at_spots(st, [2, 3, 4])                                # the snake: +x row, then up, back
    assert '_x12.70_y2.95_z' in st[0]['sample_name']
    assert all(s['user_hints']['detectors'] == ['pil900KW', 'pil2M'] for s in st)
    assert all(re.search(rf"^Murray_PbS-22B_000\d_\d+\.\ds_x.*_T-50\.0C_expt{ns['TRACK']['t']:g}s$",
                         s['sample_name']) for s in st)
    m = PYSCATTVIZ_INDEXED.search(st[2]['sample_name'] + BEAMLINE_SUFFIX)
    assert m.group(1) == 'Murray_PbS-22B' and int(m.group(2)) == 2

    capsys.readouterr()
    assert ns['preview'](ns['run_T_list']([-50, 0, 50])) == 3 * 2   # dry run: 2 frames per T
    shown = re.findall(r'^ +\d+  (\S+)$', capsys.readouterr().out, re.M)
    assert [re.search(r'_T(-?\d+\.\d)C_', n).group(1) for n in shown] == \
        ['-50.0', '-50.0', '0.0', '0.0', '50.0', '50.0']          # the target T, not the live one
    assert lk.temperature_setpoint.get() == -50.0 and ns['YZ_SERIES']['cycle'] == 3
    assert ns['LK_SPOT']['next'] == 5                             # a dry run uses no spots up
    ns['_docs'].clear()
    RE(ns['run_T_list']([-50, 0, 50], interval=0, max_cycles=2, settle=0))
    st = data()
    assert [s['user_hints']['frame_index'] for s in st] == [3, 4, 5, 6, 7, 8]   # the clock runs on
    assert at_spots(st, [5, 0, 1, 2, 3, 4])                       # the spots too; all used: again
    assert 'WARNING: all 6 spots of POS_XY_LIST used' in capsys.readouterr().out
    assert [s['T_setpoint_C'] for s in st] == [-50, -50, 0, 0, 50, 50]
    assert [re.search(r'_T(-?\d+\.\d)C_', s['sample_name']).group(1) for s in st] == \
        ['-50.0', '-50.0', '0.0', '0.0', '50.0', '50.0']
    elapsed = [s['user_hints']['elapsed_s'] for s in st]
    assert elapsed == sorted(elapsed)
    assert all(huber_tokens(s) in s['sample_name'] for s in st)
    assert lk.temperature_setpoint.get() == ns['TSERIES']['end_T']           # end_T, not measured
    with pytest.raises(ValueError, match='not allowed'):
        RE(ns['measure_T'](arcs=(7,)))
    assert ns['LK_SPOT']['next'] == 11                            # a refused arc uses no spot up
    assert ns['YZ']['name_xyz'] == ('x', 'y', 'z')                # piezo tokens back, also after errors
    assert moved and not [m for m in moved if m.startswith('piezo')]          # the piezo never moved
    assert (piezo.x.position, piezo.th.position) == (100.0, 0.4)
    RE.msg_hook = None

    load(ns, '2026C3_Murray.py')                                  # re-running keeps the sample
    s = ns['SAMPLES'][0]                                          # (file LINKAM_POS None: where it was)
    assert (s['name'], s['note'], s['sx'], s['sy']) == ('PbS-22B', 'film', 12.5, 3.0)
    assert ns['LK_SPOT']['next'] == 11                            # and its spots
    ns['LINKAM_POS'].update(sx=None, sy=None)
    RE(ns['bps'].mv(huber.x, 7.0, huber.y, 1.0))                  # centered by hand
    ns['new_sample']('S2')                                        # takes the Huber position
    assert (ns['SAMPLES'][0]['sx'], ns['SAMPLES'][0]['sy']) == (7.0, 1.0)
    assert (ns['YZ_SERIES']['t0'], ns['YZ_SERIES']['cycle']) == (None, 0)     # clock reset
    assert ns['LK_SPOT']['next'] == 0


def test_murray_T_ramp(ns, capsys, monkeypatch):
    load(ns, '2026C3_Murray.py')
    RE, lk = ns['RE'], ns['LThermal']
    data = lambda: [s for s in starts(ns) if 'user_hints' in s]      # noqa: E731
    T_name = lambda s: float(re.search(r'_T(-?\d+\.\d)C_', s['sample_name']).group(1))   # noqa: E731
    ramp = dict(T=25.0, step=10.0)                                # the Linkam: 10 C per frame
    monkeypatch.setattr(lk.temperature_current, 'get', lambda **kw: ramp['T'])

    def linkam_moves(msg):                                        # toward the setpoint, at each frame's end
        if msg.command == 'close_run':
            d = lk.temperature_setpoint.get() - ramp['T']
            ramp['T'] += max(-ramp['step'], min(ramp['step'], d))
    RE.msg_hook = linkam_moves
    ns['new_sample']('PbS 22B')

    capsys.readouterr()
    assert ns['preview'](ns['run_T_ramp']([-50, 50, 25], interval=0)) == 3 * 2   # dry run: 2 frames per T
    assert '~' in capsys.readouterr().out                         # the time / frame estimate
    assert (lk.temperature_setpoint.get(), lk.cmd.get()) == (25.0, 0)          # nothing set
    assert (ns['LK_SPOT']['next'], ns['YZ_SERIES']['t0']) == (0, None)

    RE(ns['run_T_ramp']([-50, 50, 25], interval=0))
    st = data()                                                   # frames from the start, all the way
    assert [T_name(s) for s in st] == [25, 15, 5, -5, -15, -25, -35, -45,             # -> -50
                                       -50, -40, -30, -20, -10, 0, 10, 20, 30, 40,   # reached: -> 50
                                       50, 40, 30]                                    # -> 25, ends there
    assert [s['T_setpoint_C'] for s in st] == [-50] * 8 + [50] * 10 + [25] * 3
    assert [s['user_hints']['frame_index'] for s in st] == list(range(21))
    n = len(ns['POS_XY_LIST'])
    assert [s['user_hints']['sample_info']['spot'] for s in st] == [i % n for i in range(21)]
    assert all(s['T_ramp_C_per_min'] == ns['TSERIES']['rate'] for s in st)
    assert all(huber_tokens(s) in s['sample_name'] for s in st)
    assert (lk.temperature_setpoint.get(), lk.cmd.get(), lk.lnp_mode_set.get(),
            lk.temperature_rate_setpoint.get()) == (25.0, 1, 'Auto', ns['TSERIES']['rate'])
    out = capsys.readouterr().out
    assert 'Linkam at -50 C' in out and 'Linkam at 50 C' in out and 'did not reach' not in out
    assert ns['YZ']['name_xyz'] == ('x', 'y', 'z')

    ramp['step'] = 0.0                                            # stuck (LN2 dewar empty)
    ns['_docs'].clear()
    RE(ns['run_T_ramp']([-50, 25], interval=0, rate=None, timeout=0))
    assert [(T_name(s), s['T_setpoint_C']) for s in data()] == [(25, -50), (25, 25)]   # gives up, goes on
    assert 'did not reach -50 C' in capsys.readouterr().out

    ns['_docs'].clear()
    RE(ns['run_T_ramp']([25], interval=0, hold=0.3))              # measured 0.3 s more at the target
    assert len(data()) >= 2 and all(s['T_setpoint_C'] == 25 for s in data())

    monkeypatch.undo()                                            # the sim Linkam: at its setpoint at once
    ns['_docs'].clear()
    RE(ns['run_T_ramp']([50], interval=0))
    assert [s['T_setpoint_C'] for s in data()] == [50]
    assert lk.temperature_setpoint.get() == 50.0                  # stays at the last T
    RE(ns['run_T_ramp']([50], interval=0, return_RT=True))
    assert lk.temperature_setpoint.get() == ns['TSERIES']['end_T'] == 25    # back to RT, not measured
    assert len(data()) == 2
    RE.msg_hook = None


def test_murray_snake_xy(ns):
    load(ns, '2026C3_Murray.py')
    snake = ns['snake_xy']
    assert snake(3, 2, 0.2, 0.1) == [(-0.2, -0.05), (0.0, -0.05), (0.2, -0.05),
                                     (0.2, 0.05), (0.0, 0.05), (-0.2, 0.05)]
    grid = snake(5, 5, 0.1, 0.1)
    assert len(grid) == 25 and grid[12] == (0.0, 0.0) and len(set(grid)) == 25
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == pytest.approx(0.1) for a, b in zip(grid, grid[1:]))
    assert all(x * x + y * y <= 0.2 ** 2 + 1e-9 for x, y in snake(5, 5, 0.1, 0.1, r_max=0.2))
    assert len(snake(5, 5, 0.1, 0.1, r_max=0.2)) == 13
    assert snake(1, 1, 0.2, 0.2) == [(0.0, 0.0)]


def huber_tokens(start):
    """_x.._y.._z.. of a run as the Huber sx/sy/sz (mm) it was taken at."""
    p = start['user_hints']['positions']
    return f"_x{p['sx']:.2f}_y{p['sy']:.2f}_z{p['sz']:.2f}_"


def test_murray_rt_flow(ns):
    load(ns, '2026C3_Murray.py')
    ns['LThermal'] = None                                         # any Linkam access would raise
    ns['RT_SAMPLES'] = []
    with pytest.raises(ValueError, match='RT_X'):
        ns['run_rt']()
    pos = {1: (-42000, 500), 2: (-35500, 500), 14: (42000, 500)}
    names = {**ns['RT_NAMES'], 14: 'Empty'}
    ns['RT_SAMPLES'] = ns['make_samples']({k: names[k] for k in pos}, pos, th=0)
    ns['RE'](ns['bps'].mv(ns['piezo'].th, 0.4))
    ns['RE'](ns['run_rt']())
    data, trans = starts(ns), ns['TRANS']
    assert len(data) == 3 * len(trans['offsets']) * len(trans['arcs'])
    assert all(s['sample_name'].startswith('Murray_') and '_T' not in s['sample_name'] for s in data)
    assert all(s['experiment'] == 'Murray_RT' and s['holder'] == 'RT transmission holder' for s in data)
    assert all('temperature_C' not in s['user_hints'] for s in data)
    assert all(s['user_hints']['positions']['th'] == 0 for s in data)
    assert_saxs_at_top_arc(data, trans['arcs'])
    ns['RE'](ns['run_rt']('Empty', t=5))
    new = starts(ns)[len(data):]
    assert {s['user_hints']['sample'] for s in new} == {'Empty'}
    assert all(s['sample_name'].endswith('_expt5s') for s in new)


def test_murray_collect_twsaxs(ns):
    load(ns, '2026C3_Murray.py')
    piezo, bps = ns['piezo'], ns['bps']
    ns['RE'](bps.mv(piezo.x, 1234.0, piezo.y, -56.0, piezo.th, 0.3))   # moved there by hand
    ns['collect_twsaxs']('AgBH')
    st = starts(ns)
    assert [s['user_hints']['waxs_arc_deg'] for s in st] == [0, 20, 40]
    assert [s['user_hints']['detectors'] for s in st] == [['pil900KW'], ['pil900KW'], ['pil900KW', 'pil2M']]
    assert all(s['sample_name'] == 'Murray_AgBH_x1234.00_y-56.00_z0.00_expt1s' for s in st)
    assert (piezo.x.position, piezo.y.position, piezo.th.position) == (1234.0, -56.0, 0.3)

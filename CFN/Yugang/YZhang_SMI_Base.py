"""
YZhang_SMI_Base.py -- CFN (Yugang Zhang) acquisition toolkit for SMI (12-ID), 2026 profile.

Load it in bsui, then the experiment script that uses it:

    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/YZhang_SMI_Base.py
    %run -i /home/xf12id/SWAXS_user_scripts/CFN/Yugang/2026C3_HZheng.py

README.md in this folder has the workflow, the file-name convention and the run sheets;
yz_help() prints a short reference at the console.

Conventions
-----------
* Axis names follow the console magics:  x y z th ch = SmarAct piezo (um, deg);
  sx sy sz sth sch sph = Huber stack under the piezo (mm, deg).
* A sample is a dict {'name': ..., <axis>: position, <any other field>: metadata}; make_samples()
  builds the list from the old sample_dict / pxy_dict style.
* Everything that takes data is a plan: RE(run_gi(...)), RE(run_trans(...)), RE(snap()).
  Helpers that only move or print (mov_sam, movx, here, preflight, align_gi_samples) call RE
  themselves.
* One exposure = one run, named for the CFN analysis tools (pySAXSAI / pyScattViz /
  pyDataOrg read only the file name):
      <user>_<sample>[_<ai>deg][_<idx>_<elapsed>s]_x.._y.._z..[_T..C][_E..V]_expt..s
  and the beamline appends _<energy>eV_wa<arc>_sdd<mm>mm_id<scan>_<frame>_<det>.tif.
  The same values are stored in each run's metadata under 'user_hints', and a CSV logbook
  is written next to the data (see log_dir()).
"""

import csv
import datetime
import json
import os
import re
import time
import uuid

import numpy as np
import bluesky.plans as bp
import bluesky.plan_stubs as bps
from bluesky.utils import RequestAbort, RequestStop
from ophyd import Component as Cpt, Device, EpicsSignal, EpicsSignalRO, Signal
from ophyd.status import Status


###############################################################################################
# Configuration -- experiment scripts change these with YZ.update(...)
###############################################################################################
YZ = dict(
    user='YZ',                  # file-name prefix (group tag); data files start with '<user>_'
    experiment='',              # short tag stored in every run's metadata
    md={},                      # extra metadata stored in every run (beam, environment, cell, ...)
    name_xyz=('x', 'y', 'z'),   # axes written as the _x/_y/_z file-name tokens
    saxs_min_arc=16.0,          # the 2M is shadowed by the WAXS detector below this arc (deg)
    arc_check=True,             # WAXS arc only 0 or >= 14.5 deg while the WAXS beamstop X is unplugged
    beamstop_guard=True,        # refuse to expose in alignment mode (2M beamstop removed)
    energy_keV=16.1,            # expected energy, checked by preflight()
    log_dir=None,               # alignment json + logbook csv; None = proposal folder or ~/yz_smi_logs
    ova_dir=None,               # on-axis camera JPEGs; None = <proposal>/projects/<project>/user_data/OVA
)

AXES = {
    # SmarAct piezo (um, deg): sample bars, GI alignment, fine positioning
    'x': piezo.x, 'y': piezo.y, 'z': piezo.z, 'th': piezo.th, 'ch': piezo.ch,
    # Huber stack under the piezo (mm, deg): large travel
    'sx': stage.x, 'sy': stage.y, 'sz': stage.z, 'sth': stage.th, 'sch': stage.ch, 'sph': stage.ph,
}

# Which axes a GI alignment moves, per stage: piezo -> alignment_gisaxs, huber -> alignement_gisaxs_hex
GI_STAGES = {
    'piezo': dict(x='x', y='y', th='th'),
    'huber': dict(x='sx', y='sy', th='sth'),
}


###############################################################################################
# Samples
###############################################################################################
def make_samples(names, positions=None, axes=('x', 'y'), **common):
    """
    Build the sample list that the run_*() plans loop over.

    names      {key: name} (old sample_dict) or [name, ...]
    positions  {key: (x, y)} (old pxy_dict), {key: {'x': .., 'sy': ..}}, or a list in name order
    axes       axis names for tuple positions; default ('x', 'y') = piezo um
    common     axis values / fields shared by every sample, e.g. y=1500, z=8000, holder='bar1'

    Returns [{'key': 1, 'name': 'S1', 'x': ..., 'y': ...}, ...] in the given order.
    """
    if isinstance(names, dict):
        keys = list(names)
        name_list = [names[k] for k in keys]
    else:
        name_list = list(names)
        keys = list(range(1, len(name_list) + 1))

    if positions is None:
        pos_list = [{} for _ in keys]
    elif isinstance(positions, dict):
        missing = [k for k in keys if k not in positions]
        if missing:
            raise ValueError(f'no position for sample key(s) {missing}')
        pos_list = [positions[k] for k in keys]
    else:
        pos_list = list(positions)
        if len(pos_list) != len(keys):
            raise ValueError(f'{len(keys)} names but {len(pos_list)} positions')

    samples = []
    for key, name, pos in zip(keys, name_list, pos_list):
        if isinstance(pos, dict):
            pos = {a: float(v) for a, v in pos.items()}
        elif isinstance(pos, (list, tuple, np.ndarray)):
            if len(pos) > len(axes):
                raise ValueError(f'sample {key}: {len(pos)} coordinates but axes={axes}')
            pos = {a: float(v) for a, v in zip(axes, pos)}
        else:
            raise TypeError(f'sample {key}: position {pos!r} must be a tuple/list or dict')
        sample = {'key': key, 'name': clean_name(name)}
        sample.update(common)
        sample.update(pos)
        samples.append(sample)
    check_samples(samples)
    return samples


def check_samples(samples):
    """Raise on duplicate names; warn about names the analysis filters would drop."""
    names = [s['name'] for s in samples]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        raise ValueError(f'duplicate sample names: {dup}')
    for n in names:
        if re.search(r'test|trash|dir', n, re.I):
            print(f'NOTE: "{n}" contains test/trash/dir -- default analysis filters skip such names')
        if len(n) > 60:
            print(f'NOTE: "{n}" is long ({len(n)} chars); keep sample names short')


def select(samples=None, *which):
    """Subset of samples by key or name, e.g. select(SAMPLES, 1, 4, 'S7')."""
    samples = _samples(samples)
    out = [s for s in samples if s['key'] in which or s['name'] in which]
    if len(out) != len(which):
        found = {s['key'] for s in out} | {s['name'] for s in out}
        raise KeyError(f'not found: {[w for w in which if w not in found]}')
    return out


def show_samples(samples=None):
    for s in _samples(samples):
        pos = ', '.join(f'{a}={s[a]:g}' for a in AXES if a in s)
        print(f"{s['key']!s:>4}  {s['name']:<32} {pos}")


def _samples(samples):
    if samples is None:
        samples = globals().get('SAMPLES')
        if samples is None:
            raise ValueError('no samples given and no SAMPLES defined by the experiment script')
    if isinstance(samples, dict) and 'name' in samples:
        samples = [samples]
    return list(samples)


def _positions(axes):
    """Plan: {axis: current position}."""
    out = {}
    for a in axes:
        out[a] = float((yield from bps.rd(AXES[a])))
    return out


def move_to(sample, skip=()):
    """Plan: move every axis that the sample dict defines (all in parallel)."""
    args = []
    for a, v in sample.items():
        if a in AXES and a not in skip and v is not None:
            args += [AXES[a], v]
    if args:
        yield from bps.mv(*args)


###############################################################################################
# Names
###############################################################################################
# '_' + something the analysis parsers would read as a token (sample grouping cuts at '_x',
# GI angle is '<n>deg', temperature '_T<n>C_', series '_<idx>_<t>s_', ...)
_TOKEN_TRAP = re.compile(
    r'_(?=x'                               # '_x' anywhere (SAXS grouping cut)
    r'|p?[yz]_?-?\d'                       # _y1 _z-2 _py3
    r'|th-?\d|det-?\d|expt-?\d|(?:waxs|wa)_?-?\d|id\d|pos\d|rh-?\d|linkam-?\d'
    r'|t-?\d+(?:\.\d+)?c(?:_|$)'           # _T25C_
    r'|t\d+(?:\.\d+)?s(?:_|$)'             # _t30s
    r'|e-?\d+(?:\.\d+)?v(?:_|$)'           # _E-0.5V
    r'|\d+_\d+(?:\.\d+)?s(?:_|$))',        # _12_30.5s_
    re.I)


def clean_name(name):
    """Make a sample name safe for the file name and the analysis parsers ([A-Za-z0-9-] + '_')."""
    s = str(name).strip()
    s = re.sub(r'(?<=\d)\.(?=\d)', 'p', s)           # 1.5mM -> 1p5mM
    s = re.sub(r'[^A-Za-z0-9_\-]', '-', s)
    s = re.sub(r'(?<=\d)deg', 'dg', s, flags=re.I)   # '10deg' would read as an incident angle
    for _ in range(3):                               # traps can overlap; repeat until stable
        s = _TOKEN_TRAP.sub('-', s)
    s = re.sub(r'-{2,}', '-', s)
    s = re.sub(r'_{2,}', '_', s).strip('_-')
    if not s:
        raise ValueError(f'sample name {name!r} is empty after cleaning')
    if s != str(name):
        print(f'sample name "{name}" -> "{s}"')
    return s


def file_name(sample, t, xyz, ai=None, idx=None, elapsed=None, T=None, E=None, extra=None):
    """<user>_<sample>[_<ai>deg][_<idx>_<elapsed>s]_x_y_z[_T..C][_E..V][_extra]_expt<t>s"""
    parts = [YZ['user'], sample] if YZ['user'] else [sample]
    if ai is not None:
        parts.append(f'{ai:.4f}deg')
    if idx is not None:
        parts.append(f'{int(idx):04d}_{max(float(elapsed or 0), 0.0):.1f}s')
    parts += [f'x{xyz[0]:.2f}', f'y{xyz[1]:.2f}', f'z{xyz[2]:.2f}']
    if T is not None and np.isfinite(T):
        parts.append(f'T{T:.1f}C')
    if E is not None and np.isfinite(E):
        parts.append(f'E{E:.3f}V')
    if extra:
        parts.append(clean_name(extra))
    parts.append(f'expt{t:g}s')
    return '_'.join(str(p) for p in parts).replace('+', '')


###############################################################################################
# One exposure
###############################################################################################
def expose(sample, dets, t=1, *, ai=None, idx=None, elapsed=None, T=None, E=None,
           extra=None, readings=(), md=None):
    """
    Plan: one exposure of `sample` at the current position = one Bluesky run.

    sample    sample dict or name
    dets      e.g. [pil900KW] or [pil900KW, pil2M]
    ai        incident angle (deg) for GI, written as <ai>deg
    idx, elapsed   in-situ frame index / seconds since the series start
    T, E      number, a readable signal (read now and recorded), or
              {'signal': sig, 'scale': a, 'offset': b} -> a*reading + b
    readings  extra signals recorded with the detectors (primary stream)
    Returns the run uid.
    """
    s = sample if isinstance(sample, dict) else {'name': clean_name(sample)}
    dets = list(dets)
    if not dets:
        raise ValueError('no detector selected')
    yield from _beamstop_guard(dets)

    recorded = [r for r in readings if r is not None]
    T_val = yield from _value(T, recorded)
    E_val = yield from _value(E, recorded)
    pos = {}
    for a, m in AXES.items():
        pos[a] = float((yield from bps.rd(m)))
    arc = float((yield from bps.rd(_arc_rb())))
    xyz = [pos[a] for a in YZ['name_xyz']]

    name = file_name(s['name'], t, xyz, ai=ai, idx=idx, elapsed=elapsed, T=T_val, E=E_val, extra=extra)
    hints = dict(
        sample=s['name'], exposure_s=t, waxs_arc_deg=round(arc, 3),
        detectors=[d.name for d in dets], positions={a: round(v, 4) for a, v in pos.items()},
        sample_info={k: v for k, v in s.items() if k not in AXES and k != 'name'},
    )
    for k, v in (('incident_angle_deg', ai), ('frame_index', idx), ('elapsed_s', elapsed),
                 ('temperature_C', T_val), ('potential_V', E_val)):
        if v is not None and np.isfinite(v):         # no NaN in metadata (not valid JSON)
            hints[k] = v
    if idx is not None and YZ_SERIES.get('t0'):
        hints['series_t0'] = YZ_SERIES['t0']
        hints['series_t0_iso'] = _iso(YZ_SERIES['t0'])
    run_md = {'sample': s['name'], 'user_group': YZ['user'], 'experiment': YZ['experiment'],
              'geometry': 'reflection' if ai is not None else 'transmission'}
    run_md.update(YZ['md'])
    run_md.update(md or {})
    run_md['user_hints'] = hints
    run_md['sample_name'] = name

    yield from det_exposure_time(t, t)
    print(f'\n\t=== {name} ===\n')
    uid = yield from bp.count(dets + [r for r in recorded if r not in dets], md=run_md)
    _logbook(name, hints, uid)
    return uid


def _value(v, recorded):
    """Plan: None / number / signal / {'signal','scale','offset'} -> float (signals get recorded)."""
    if v is None:
        return None
    if isinstance(v, dict):
        raw = yield from _value(v['signal'], recorded)
        return v.get('scale', 1.0) * raw + v.get('offset', 0.0)
    if hasattr(v, 'read'):
        if v not in recorded:
            recorded.append(v)
        val = yield from bps.rd(v)
        return float(val)
    return float(v)


def _beamstop_guard(dets):
    """Refuse to expose in alignment mode (2M beamstop removed, attenuators in; any detector)
    or with no 2M beamstop selected (2M frames)."""
    if not YZ['beamstop_guard']:
        return
    state = str((yield from bps.rd(pil2M.active_beamstop, default_value='rod')))
    if state.endswith('_removed'):
        fix = 'still in alignment mode: RE(smi.modeMeasurement())'
    elif state == 'none' and pil2M in dets:
        fix = "no 2M beamstop selected: RE(pil2M.insert_beamstop('rod'))"
    else:
        return
    raise RuntimeError(f'pil2M beamstop is "{state}", {fix} before measuring '
                       f'(or YZ["beamstop_guard"] = False if this is intended)')


###############################################################################################
# Detectors / WAXS arc
###############################################################################################
def _arc_rb():
    """WAXS arc readback signal.  The profile sets its kind to 'normal', which leaves the arc
    motor without a hinted field, so bps.rd(waxs.arc) raises; read the readback instead."""
    return waxs.arc.user_readback


def check_arcs(arcs):
    """WAXS arc 0 or >= 14.5 deg only while the WAXS beamstop X motor is unplugged (2026-06)."""
    if not YZ['arc_check']:
        return
    bad = [a for a in arcs if not (abs(a) <= 0.1 or a >= 14.5)]
    if bad:
        raise ValueError(f'WAXS arc {bad} not allowed now (only 0 or >= 14.5 deg); '
                         f'set YZ["arc_check"] = False once the WAXS beamstop motor is fixed')


def _saxs_arcs(arcs, saxs):
    """Arcs at which the 2M is read: saxs='max' (largest clear arc), 'all', or False."""
    clear = [a for a in arcs if a >= YZ['saxs_min_arc']]
    if not saxs or not clear:
        if saxs:
            print(f'NOTE: no arc >= {YZ["saxs_min_arc"]} deg in {list(arcs)} -> no SAXS (2M) data')
        return []
    return clear if saxs == 'all' else [max(clear)]


def _dets(arc, saxs_arcs, waxs_det):
    dets = [pil900KW] if waxs_det else []
    if arc in saxs_arcs:
        dets.append(pil2M)
    return dets


def _announce(what, n_exp, t, overhead=3.0):
    minutes = n_exp * (t + overhead) / 60
    print(f'\n{what}: {n_exp} exposures, ~{minutes:.0f} min (t={t:g} s + ~{overhead:g} s overhead)\n')


###############################################################################################
# Transmission SAXS/WAXS
###############################################################################################
def run_trans(samples=None, t=1, arcs=(0, 20), saxs='max', waxs_det=True,
              offsets=((0, 0),), offset_axes=('x', 'y'), extra=None, md=None, at_sample=None,
              T=None, E=None, readings=()):
    """
    Plan: transmission SAXS/WAXS of every sample.

    arcs      WAXS arc positions (outermost loop, each moved once)
    saxs      'max': read the 2M only at the largest arc >= YZ['saxs_min_arc'];
              'all': at every clear arc; False: never
    offsets   relative spots per sample on offset_axes, e.g. ((0, -200), (0, 0), (0, 200))
    at_sample plan factory at_sample(sample, i_arc), run at each sample's center before its
              spots, e.g. an on-axis camera image on the first arc (i_arc == 0)
    T, E      temperature / potential for names and metadata (number or signal), e.g.
              T=LThermal.temperature_current
    Samples are visited in serpentine order (reversed on every other arc).
    """
    samples = _samples(samples)
    check_arcs(arcs)
    saxs_arcs = _saxs_arcs(arcs, saxs)
    n_arcs = sum(1 for a in arcs if _dets(a, saxs_arcs, waxs_det))
    _announce('run_trans', n_arcs * len(samples) * len(offsets), t)
    ref = yield from _positions(offset_axes)
    for i_arc, arc in enumerate(arcs):
        dets = _dets(arc, saxs_arcs, waxs_det)
        if not dets:
            continue
        yield from bps.mv(waxs, arc)
        for s in (samples if i_arc % 2 == 0 else samples[::-1]):
            yield from move_to(s)
            if at_sample:
                yield from at_sample(s, i_arc)
            base = {a: s.get(a, ref[a]) for a in offset_axes}
            for off in offsets:
                if len(offsets) > 1 or any(off):     # (0, 0) after another spot must move back
                    yield from bps.mv(*[v for a, d in zip(offset_axes, off) for v in (AXES[a], base[a] + d)])
                yield from expose(s, dets, t, T=T, E=E, readings=readings, extra=extra, md=md)


def measure_saxs(sample='test', t=1):
    """Plan: one 2M exposure at the current position (WAXS arc must already be >= saxs_min_arc)."""
    arc = yield from bps.rd(_arc_rb())
    if arc < YZ['saxs_min_arc']:
        print(f'WARNING: WAXS arc {arc:.1f} deg shadows part of the 2M')
    yield from expose(sample, [pil2M], t)


def measure_waxs(sample='test', t=1, arc=0):
    """Plan: one 900KW exposure at the current position and WAXS arc `arc`."""
    check_arcs([arc])
    yield from bps.mv(waxs, arc)
    yield from expose(sample, [pil900KW], t)


def measure_wsaxs(sample='test', t=1, arc=20):
    """Plan: simultaneous 900KW + 2M exposure at WAXS arc `arc` (>= saxs_min_arc)."""
    check_arcs([arc])
    yield from bps.mv(waxs, arc)
    yield from expose(sample, [pil900KW, pil2M], t)


def snap(t=0.5, dets=None, name='test'):
    """Plan: quick look exposure ('test' names are skipped by the analysis filters)."""
    dets = dets or [pil900KW, pil2M]
    yield from expose(name, dets, t)


###############################################################################################
# On-axis camera (OVA) images: the JPEG plugin of the SAM camera, as the old save_ova / setup_ova
###############################################################################################
class _OVACam(Device):
    enable = Cpt(EpicsSignal, 'EnableCallbacks')
    file_path = Cpt(EpicsSignal, 'FilePath', string=True)
    file_name = Cpt(EpicsSignal, 'FileName', string=True)
    write_file = Cpt(EpicsSignal, 'WriteFile', put_complete=True)
    path_exists = Cpt(EpicsSignalRO, 'FilePathExists_RBV')


if 'ova_cam' not in globals():                  # the simulation tests bring their own
    ova_cam = _OVACam('XF:12IDC-BI{Cam:SAM}JPEG1:', name='ova_cam')


def ova_dir():
    """Folder of the on-axis camera JPEGs: YZ['ova_dir'], else <proposal>/projects/<project>/user_data/OVA."""
    d = YZ['ova_dir']
    if not d:
        md = RE.md
        d = (f'/nsls2/data/smi/proposals/{md.get("cycle")}/{md.get("data_session")}/projects/'
             f'{md.get("project_name") or "default"}/user_data/OVA')
    return d.rstrip('/') + '/'


def ova_snap(sample='test', settle=1.0):
    """
    Plan: save the on-axis camera image of `sample` at the current position as
    <ova_dir()><user>_<sample>_x.._y.._sx.._sy.._OVA_NNN.jpg, with a logbook row (detectors 'OVA').
    The camera must be acquiring: the plugin saves its latest frame, so wait `settle` s after a move.
    """
    s = sample if isinstance(sample, dict) else {'name': clean_name(sample)}
    pos = {}
    for a, m in AXES.items():
        pos[a] = float((yield from bps.rd(m)))
    name = '_'.join(([YZ['user']] if YZ['user'] else []) + [
        s['name'], f'x{pos["x"]:.2f}', f'y{pos["y"]:.2f}', f'sx{pos["sx"]:.3f}', f'sy{pos["sy"]:.3f}',
        'OVA'])
    path = ova_dir()
    if settle:
        yield from bps.sleep(settle)
    yield from _put(ova_cam.enable, 1)
    yield from _put(ova_cam.file_path, path)
    if not (yield from bps.rd(ova_cam.path_exists)):
        print(f'WARNING: the camera IOC does not see {path} -- set YZ["ova_dir"]')
    yield from _put(ova_cam.file_name, name)
    yield from _put(ova_cam.write_file, 1, timeout=30)
    print(f'OVA image -> {path}{name}_NNN.jpg')
    _logbook(name, dict(sample=s['name'], detectors=['OVA'], positions=pos), uid='')


###############################################################################################
# Grazing incidence
###############################################################################################
def _gi_align_plan(stage_name, angle):
    if stage_name == 'piezo':
        return alignment_gisaxs(angle)
    if stage_name == 'huber':
        return alignement_gisaxs_hex(angle)
    raise ValueError(f'stage must be one of {list(GI_STAGES)}')


def _restore_measurement_mode():
    """Plan: after a failed alignment, put the beamstop back and retract the alignment foils."""
    bec._calc_derivative_and_stats = False
    state = str((yield from bps.rd(pil2M.active_beamstop, default_value='')))
    if state.endswith('_removed'):
        yield from smi.modeMeasurement()
    else:
        yield from bps.mv(attenuation, 1)


def align_gi(samples=None, angle=0.15, stage='piezo', result=None, holder=None, start=None):
    """
    Plan: beamline GI alignment (alignment_gisaxs / alignement_gisaxs_hex) on every sample.

    Fills `result` = {sample name: {'th', 'y', 'ok', ...}} and saves it to json after every
    sample (load_alignment() recovers it).  The beamline scans are relative to the current
    th/y; start = a previous alignment dict makes each sample start from its aligned th/y.
    A failed sample is flagged ok=False, th/y go back to where its scan started (a failed fit
    can leave th at a scan edge) and the loop continues.  Abort/stop (Ctrl-C, RE.abort())
    restores the measurement mode (beamstop in, attenuators out) before ending.
    """
    samples = _samples(samples)
    gi = GI_STAGES[stage]
    th_m, y_m = AXES[gi['th']], AXES[gi['y']]
    result = {} if result is None else result
    holder = _holder(holder)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    for s in samples:
        print(f'\n##### aligning {s["name"]} ({stage}, {angle} deg) #####')
        yield from move_to(s)
        prev = (start or {}).get(s['name'])
        if prev and prev.get('ok'):
            yield from bps.mv(y_m, prev['y'], th_m, prev['th'])
        th_start = yield from bps.rd(th_m)
        y_start = yield from bps.rd(y_m)
        ok, err = True, ''
        try:
            if not _previewing():
                yield from _gi_align_plan(stage, angle)
        except (RequestAbort, RequestStop):
            print('alignment interrupted: restoring the measurement mode')
            yield from _restore_measurement_mode()
            raise
        except Exception as ex:
            ok, err = False, f'{type(ex).__name__}: {ex}'
            print(f'!!! alignment FAILED for {s["name"]}: {err}')
            yield from _restore_measurement_mode()
            yield from bps.mv(y_m, y_start, th_m, th_start)
        th0 = yield from bps.rd(th_m)
        y0 = yield from bps.rd(y_m)
        result[s['name']] = dict(th=float(th0), y=float(y0), ok=ok, stage=stage, angle=angle,
                                 time=_iso(), error=err, holder=holder)
        print(f'{s["name"]}: th={th0:.4f}  y={y0:.3f}  ok={ok}')
        save_alignment(result, holder, stamp)
    return result


ALIGNED = {}


def align_gi_samples(samples=None, angle=0.15, stage='piezo', holder=None, merge=True):
    """
    Console: run align_gi; the result is saved to json after every sample, so run_gi(**GI)
    (aligned=None) finds it even after a Ctrl-C / RE.resume().  merge=True keeps the saved
    alignment of samples not in `samples` (re-align a few without losing the rest).
    """
    global ALIGNED
    holder = _holder(holder)
    ALIGNED = _saved_alignment(holder) if merge else {}
    RE(align_gi(samples, angle=angle, stage=stage, result=ALIGNED, holder=holder))
    show_alignment(ALIGNED)
    return ALIGNED


def mark_aligned(sample, aligned=None, stage='piezo', holder=None):
    """Console: store the CURRENT th/y as the alignment of `sample` (after a manual alignment)
    in `aligned` (default: the saved alignment of `holder` = this experiment) and save it."""
    gi = GI_STAGES[stage]
    name = sample['name'] if isinstance(sample, dict) else _sample_name(sample)
    if aligned is None:
        holder = _holder(holder)
        aligned = _saved_alignment(holder)
    else:
        holder = holder or next((a['holder'] for a in aligned.values() if a.get('holder')), None)
        holder = _holder(holder)
    aligned[name] = dict(th=float(AXES[gi['th']].position), y=float(AXES[gi['y']].position),
                         ok=True, stage=stage, angle=None, time=_iso(), error='manual',
                         holder=holder)
    save_alignment(aligned, holder)
    print(f'{name}: th={aligned[name]["th"]:.4f}  y={aligned[name]["y"]:.3f} (manual, {holder})')
    return aligned


def show_alignment(aligned):
    for name, a in aligned.items():
        flag = '' if a['ok'] else f'   FAILED: {a.get("error", "")}'
        print(f'{name:<32} th={a["th"]:9.4f}  y={a["y"]:10.3f}{flag}')


def save_alignment(aligned, holder, stamp=None):
    if _previewing():
        return
    try:
        d = log_dir()
        stamp = stamp or datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        tag = _tag(holder)
        for fn in (f'alignment_{tag}_{stamp}.json', f'alignment_{tag}_latest.json'):
            with open(os.path.join(d, fn), 'w') as f:
                json.dump(aligned, f, indent=1)
    except OSError as ex:
        print(f'WARNING: could not save alignment ({ex})')


def load_alignment(holder=None):
    """Load the latest saved alignment of `holder` (default: this experiment), or a json path."""
    path = _alignment_path(holder)
    with open(path) as f:
        aligned = json.load(f)
    print(f'loaded {path}')
    show_alignment(aligned)
    return aligned


def _holder(holder=None):
    return holder or YZ['experiment'] or YZ['user']


def _alignment_path(holder=None):
    if holder and os.path.isfile(str(holder)):
        return holder
    return os.path.join(log_dir(), f'alignment_{_tag(_holder(holder))}_latest.json')


def _saved_alignment(holder=None):
    """The latest saved alignment of `holder`, or {} if there is none."""
    try:
        with open(_alignment_path(holder)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _sample_name(which):
    """Name of the SAMPLES entry with key or name `which` (else `which` itself)."""
    for s in globals().get('SAMPLES') or []:
        if which in (s['key'], s['name']):
            return s['name']
    return str(which)


def _alignment(aligned):
    """aligned: dict, holder name / json path, or None = the latest saved alignment of this
    experiment (falls back to ALIGNED of this session if the log folder is not readable)."""
    if isinstance(aligned, str):
        return load_alignment(aligned)
    if aligned is not None:
        return aligned
    try:
        return load_alignment()
    except (OSError, ValueError) as ex:
        if ALIGNED:
            print(f'WARNING: no saved alignment ({ex}); using ALIGNED of this session')
            return ALIGNED
    raise ValueError('no alignment: align_gi_samples() first, pass aligned=..., or align=True')


def _aligned_samples(samples, aligned, skip_failed=True):
    """The samples that have a (successful, if skip_failed) alignment."""
    todo = []
    for s in samples:
        a = aligned.get(s['name'])
        if a is None:
            print(f'SKIP {s["name"]}: not aligned')
        elif not a['ok'] and skip_failed:
            print(f'SKIP {s["name"]}: alignment failed')
        else:
            todo.append(s)
    return todo


def run_gi(samples=None, aligned=None, angles=(0.10, 0.15, 0.20), arcs=(0, 20), t=1,
           saxs='max', waxs_det=True, x_offsets=(0,), stage='piezo', align=False, align_angle=0.15,
           skip_failed=True, T=None, E=None, readings=(), extra=None, md=None):
    """
    Plan: GIWAXS (+ GISAXS on the 2M at the largest clear arc) of every aligned sample.

    aligned    None = the latest saved alignment of this experiment (align_gi_samples() saves
               it after every sample); or a dict, a holder name or a json path
    align      True: align all samples first, inside this plan
    angles     incident angles (deg) relative to the aligned th
    arcs       WAXS arc positions (outermost loop, each moved once)
    x_offsets  extra spots along the sample (stage x units: um piezo, mm huber)
    T, E       temperature / potential for names and metadata (number or signal), e.g.
               T=LThermal.temperature_current
    """
    samples = _samples(samples)
    check_arcs(arcs)
    gi = GI_STAGES[stage]
    if align:
        aligned = yield from align_gi(samples, angle=align_angle, stage=stage,
                                      result=_saved_alignment())
    aligned = _alignment(aligned)
    todo = _aligned_samples(samples, aligned, skip_failed)
    saxs_arcs = _saxs_arcs(arcs, saxs)
    n_arcs = sum(1 for a in arcs if _dets(a, saxs_arcs, waxs_det))
    _announce('run_gi', n_arcs * len(todo) * len(x_offsets) * len(angles), t)
    ref = yield from _positions([gi['x']])
    for i_arc, arc in enumerate(arcs):
        dets = _dets(arc, saxs_arcs, waxs_det)
        if not dets:
            continue
        yield from bps.mv(waxs, arc)
        for s in (todo if i_arc % 2 == 0 else todo[::-1]):
            a = aligned[s['name']]
            yield from move_to(s, skip=(gi['y'], gi['th']))
            yield from bps.mv(AXES[gi['y']], a['y'], AXES[gi['th']], a['th'])
            x0 = s.get(gi['x'], ref[gi['x']])
            for dx in x_offsets:
                yield from bps.mv(AXES[gi['x']], x0 + dx)
                for ai in angles:
                    yield from bps.mv(AXES[gi['th']], a['th'] + ai)
                    yield from expose(s, dets, t, ai=ai, T=T, E=E, readings=readings,
                                      extra=extra, md=md)
            yield from bps.mv(AXES[gi['th']], a['th'])


###############################################################################################
# Linkam (LThermal, degC)
###############################################################################################
def _put(sig, value, timeout=10):
    """Plan: set a signal without hanging if the IOC rounds or never echoes the value."""
    group = f'yz_put_{uuid.uuid4().hex[:8]}'       # a timed-out status must not block later puts
    yield from bps.abs_set(sig, value, group=group)
    yield from bps.wait(group=group, timeout=timeout, error_on_timeout=False)


def linkam_T():
    """Console: current Linkam temperature (degC)."""
    return LThermal.temperature_current.get()


def linkam_goto(T, tol=1.0, settle=60, timeout=3600, rate=None, lnp=None, poll=5,
                on_timeout='continue'):
    """
    Plan: set the Linkam to T (degC), wait until |T_now - T| <= tol, then soak `settle` s.

    rate        ramp rate (degC/min), None = leave as is
    lnp         LN2 pump mode, e.g. 'Auto' for cooling; None = leave as is
    on_timeout  'continue' (warn and go on; names carry the real T) or 'raise'
    """
    if rate is not None:
        yield from _put(LThermal.temperature_rate_setpoint, rate)
    if lnp is not None:
        yield from _put(LThermal.lnp_mode_set, lnp)
    yield from _put(LThermal.temperature_setpoint, round(float(T), 1))
    yield from _put(LThermal.cmd, 1)
    if _previewing():
        print(f'(preview) Linkam -> {T} C, soak {settle} s')
        return
    waited = 0.0                     # polling time only: a pause / beam-dump suspension does not count
    n = 0
    while True:
        now = yield from bps.rd(LThermal.temperature_current)
        if abs(now - T) <= tol:
            break
        if waited > timeout:
            msg = f'Linkam did not reach {T} C in {timeout} s (now {now:.1f} C)'
            if on_timeout == 'raise':
                raise TimeoutError(msg)
            print(f'WARNING: {msg}; continuing')
            break
        if n % 12 == 0:
            print(f'Linkam {now:.1f} C -> {T:.1f} C  ({waited:.0f} s)')
        n += 1
        yield from bps.sleep(poll)
        waited += poll
    if settle:
        print(f'Linkam at {T} C, soaking {settle} s')
        yield from bps.sleep(settle)


def linkam_off():
    """Plan: stop Linkam heating/cooling."""
    yield from _put(LThermal.cmd, 0)


def run_gi_temperatures(temps, samples=None, aligned=None, realign=True, align_angle=0.15,
                        tol=1.0, settle=120, timeout=3600, rate=None, lnp=None,
                        end_T=None, off_at_end=False, **gi_kw):
    """
    Plan: for each T in `temps` (degC): Linkam to T -> (re)align -> run_gi with the live Linkam
    temperature in the names (_T..C) and in the primary stream.

    aligned    start values (None = the latest saved alignment of this experiment, if any)
    realign    re-align at every T (thermal drift), starting from the previous values; failed
               re-alignments keep the previous values
    gi_kw      passed to run_gi (angles, arcs, t, x_offsets, stage, saxs, ...)
    """
    samples = _samples(samples)
    stage = gi_kw.get('stage', 'piezo')
    if aligned is None:
        aligned = _saved_alignment()                 # e.g. the RT alignment, as a start
        if aligned:
            print(f'starting from the saved alignment of {_holder()}')
    else:
        aligned = dict(_alignment(aligned))
    for T in temps:
        yield from linkam_goto(T, tol=tol, settle=settle, timeout=timeout, rate=rate, lnp=lnp)
        if realign or not aligned:
            tag = f'{_holder()}_T{T:g}C'
            new = yield from align_gi(samples, angle=align_angle, stage=stage, holder=tag,
                                      start=aligned)
            aligned = _merge_alignment(aligned, new)
        yield from run_gi(samples, aligned, T=LThermal.temperature_current, **gi_kw)
    if end_T is not None:
        yield from linkam_goto(end_T, tol=tol, settle=0, timeout=timeout)
    if off_at_end:
        yield from linkam_off()


def _merge_alignment(old, new):
    if not old:
        return dict(new)
    merged = dict(old)
    for name, a in new.items():
        if a['ok']:
            if name in old:
                print(f'{name}: dth={a["th"] - old[name]["th"]:+.4f} deg  dy={a["y"] - old[name]["y"]:+.3f}')
            merged[name] = a
        else:
            print(f'{name}: re-alignment failed, keeping previous values')
    return merged


###############################################################################################
# In-situ time series (incl. electrochemistry)
###############################################################################################
YZ_SERIES = dict(t0=None, cycle=0)


def series_start(note=''):
    """Console: t = 0 of an in-situ series (file names carry the seconds since now)."""
    YZ_SERIES['t0'] = time.time()
    YZ_SERIES['cycle'] = 0
    YZ_SERIES['note'] = note
    print(f'series t0 = {_iso(YZ_SERIES["t0"])}  (unix {YZ_SERIES["t0"]:.3f})  {note}')


def run_series(samples=None, aligned=None, duration=600, interval=0, max_cycles=None,
               angles=None, arc=0, t=1, saxs=False, waxs_det=True, spots=(0,), spot_axis=None,
               stage='piezo', T=None, E=None, readings=(), swaxs_every=None, swaxs_arc=20,
               skip_failed=True, extra=None, md=None):
    """
    Plan: repeat cycles over the samples for `duration` s (or `max_cycles`).

    GI if `angles` is given (aligned=None: the latest saved alignment; samples whose
    alignment failed are skipped unless skip_failed=False), transmission otherwise.  Each cycle uses the
    next entry of `spots` (relative offsets on spot_axis) -> fresh spots spread the dose.
    Names carry _<cycle>_<seconds since series_start()>s.  interval = cycle start-to-start
    period (s); 0 = back-to-back.  swaxs_every=N adds a WAXS+SAXS frame at swaxs_arc every
    N cycles.  E may also be a function of the elapsed seconds (a potential schedule); its
    value is then written to ec_potential_setpoint as well.
    """
    samples = _samples(samples)
    gi = GI_STAGES[stage]
    spot_axis = spot_axis or gi['x']
    check_arcs([arc] + ([swaxs_arc] if swaxs_every else []))
    if angles is not None:
        aligned = _alignment(aligned)
        samples = _aligned_samples(samples, aligned, skip_failed)
        if not samples:
            raise ValueError('no aligned sample to measure')
    ser = dict(YZ_SERIES) if _previewing() else YZ_SERIES   # a dry run leaves clock and counter
    if ser['t0'] is None:
        if ser is YZ_SERIES:
            series_start('(auto: run_series start)')
        else:
            ser['t0'] = time.time()
    dets = [pil900KW] if waxs_det else []
    if saxs and arc >= YZ['saxs_min_arc']:
        dets.append(pil2M)
    if not dets:
        raise ValueError('no detector: waxs_det=False and the 2M is shadowed at this arc')
    n_ang = len(angles) if angles is not None else 1
    print(f'run_series: {len(samples)} samples x {n_ang} angles per cycle, every '
          f'{interval or "back-to-back"} s for {duration} s; t0 = {_iso(ser["t0"])}')

    def one_pass(dets_now, spot, angle_list):
        for s in samples:
            if angles is not None:
                a = aligned[s['name']]
                yield from move_to(s, skip=(gi['y'], gi['th']))
                yield from bps.mv(AXES[gi['y']], a['y'])
            else:
                yield from move_to(s)
            yield from bps.mv(AXES[spot_axis], s.get(spot_axis, ref[spot_axis]) + spot)
            for ai in angle_list:
                if ai is not None:
                    yield from bps.mv(AXES[gi['th']], a['th'] + ai)
                elapsed = time.time() - ser['t0']
                E_now = E
                if callable(E):                      # potential schedule f(elapsed) -> V
                    E_now = float(E(elapsed))
                    yield from bps.mv(ec_potential_setpoint, E_now)
                yield from expose(s, dets_now, t, ai=ai, idx=ser['cycle'], elapsed=elapsed,
                                  T=T, E=E_now, readings=readings, extra=extra, md=md)

    angle_list = list(angles) if angles is not None else [None]
    if _previewing():
        max_cycles = min(max_cycles or 2, 2)
        print('(preview) showing 2 cycles')
    ref = yield from _positions([spot_axis])
    t_start = time.time()
    n = 0
    yield from bps.mv(waxs, arc)
    while time.time() - t_start < duration and (max_cycles is None or n < max_cycles):
        t_cycle = time.time()
        spot = spots[ser['cycle'] % len(spots)]
        yield from one_pass(dets, spot, angle_list)
        if swaxs_every and ser['cycle'] % swaxs_every == 0:
            yield from bps.mv(waxs, swaxs_arc)
            yield from one_pass([pil900KW, pil2M], spot, angle_list[:1])
            yield from bps.mv(waxs, arc)
        ser['cycle'] += 1
        n += 1
        if max_cycles is not None and n >= max_cycles:
            break                                    # no wait after the last cycle
        wait = interval - (time.time() - t_cycle)
        if wait > 0:
            if time.time() - t_start + wait >= duration:
                break                                # the next cycle would start after the end
            print(f'cycle {ser["cycle"] - 1} done, next in {wait:.0f} s')
            yield from bps.sleep(wait)


# Electrochemistry: the potentiostat is the users' own; we keep a common clock (ec_start) and
# record the applied potential typed in with ec_set_potential() and/or an analog readback.
EC = dict(potential=None, schedule=None, readback=None, scale=1.0, offset=0.0)


class _SoftValue(Signal):
    """Soft signal whose set() completes at once (a plain Signal waits for readback == value,
    which never happens for NaN = 'no potential')."""
    def set(self, value, **kwargs):
        self.put(value)
        st = Status(self)
        st.set_finished()
        return st


ec_potential_setpoint = _SoftValue(name='ec_potential_setpoint', value=float('nan'))


def ec_start(note=''):
    """Console: call when the potentiostat sequence starts (t = 0 for all frame names)."""
    series_start(note or 'EC start')


def ec_set_potential(V):
    """Console: record the potential (V) now applied by the potentiostat (None = unknown / OCV).
    During a running plan: Ctrl-C (pause), ec_set_potential(V), RE.resume()."""
    EC['potential'] = V
    ec_potential_setpoint.put(float('nan') if V is None else float(V))
    elapsed = time.time() - YZ_SERIES['t0'] if YZ_SERIES['t0'] else float('nan')
    print(f'EC potential = {V} V at {_iso()} (t = {elapsed:.1f} s)')


def ec_schedule_value(elapsed):
    """Potential (V) of EC['schedule'] = [(t_start_s, V), ...] at `elapsed` s after ec_start()."""
    value = None
    for t_on, V in sorted(EC['schedule']):
        if elapsed >= t_on:
            value = V
    return float('nan') if value is None else value


def ec_E():
    """What run_ec writes as _E..V, in priority order: analog readback (EC['readback'] *
    scale + offset), the programmed EC['schedule'], else the potential typed with
    ec_set_potential() (read at every frame; no _E token while it is unset)."""
    if EC['readback'] is not None:
        return {'signal': EC['readback'], 'scale': EC['scale'], 'offset': EC['offset']}
    if EC['schedule']:
        return ec_schedule_value
    return ec_potential_setpoint


def run_ec(samples=None, aligned=None, readings=(), **series_kw):
    """Plan: run_series (same keywords) with the EC potential in the names (_E..V) and in the
    primary stream (ec_potential_setpoint, plus EC['readback'] if set); see ec_E()."""
    E = ec_E()
    readings = list(readings) + [ec_potential_setpoint]
    if EC['readback'] is not None:
        readings.append(EC['readback'])
    yield from run_series(samples, aligned, E=E, readings=readings, **series_kw)


###############################################################################################
# Multi-cell holders (well plates, cell bars)
###############################################################################################
def norm_cell(label):
    """'a1' -> 'A01', 'B2-c12' -> 'B2-C12'."""
    m = re.fullmatch(r'\s*(?:(.+?)-)?([A-Za-z])0*(\d{1,3})\s*', str(label))
    if not m:
        raise ValueError(f'bad cell label {label!r}')
    pre = f'{m.group(1).upper()}-' if m.group(1) else ''
    return f'{pre}{m.group(2).upper()}{int(m.group(3)):02d}'


def grid_cells(rows, cols, first, last_in_row=None, first_in_last_row=None, pitch=None,
               axes=('x', 'y'), base=None, prefix='', names=None, keep_empty=False):
    """
    Samples for a rows x cols grid of cells (well plate, multi-cell bar).

    rows       number of rows or row letters, e.g. 16 or 'ABCD'
    first      position of cell A01 on `axes`
    last_in_row, first_in_last_row   positions of A<cols> and <last row>01 (3-point calibration:
               handles pitch, rotation and axis direction); or give pitch=(d_col, d_row)
    base       axis values shared by the grid, e.g. the Huber position {'sx': 12.5, 'sy': -3}
    prefix     label prefix, e.g. 'B1' -> cells 'B1-A01' ...
    names      {cell label: sample name}; cells without a name are skipped unless keep_empty
    """
    labels = list(rows) if isinstance(rows, str) else [chr(ord('A') + i) for i in range(rows)]
    first = np.asarray(first, float)
    if pitch is not None:
        u = np.array([pitch[0], 0.0])
        v = np.array([0.0, pitch[1]])
    else:
        u = (np.asarray(last_in_row, float) - first) / max(cols - 1, 1) if last_in_row is not None \
            else np.zeros(2)
        v = (np.asarray(first_in_last_row, float) - first) / max(len(labels) - 1, 1) \
            if first_in_last_row is not None else np.zeros(2)
    if (cols > 1 and not np.any(u)) or (len(labels) > 1 and not np.any(v)):
        raise ValueError('give last_in_row / first_in_last_row (or pitch) for a grid larger than 1 cell')
    names = {norm_cell(k): v_ for k, v_ in (names or {}).items()}
    samples = []
    for r, row in enumerate(labels):
        for c in range(cols):
            cell = f'{prefix}-{row}{c + 1:02d}' if prefix else f'{row}{c + 1:02d}'
            label = names.get(norm_cell(cell))
            if label is None and not keep_empty:
                continue
            p = first + c * u + r * v
            s = {'key': cell, 'name': clean_name(f'{label}_{cell}' if label else cell), 'cell': cell}
            s.update(base or {})
            s.update({a: round(float(val), 4) for a, val in zip(axes, p)})
            samples.append(s)
    check_samples(samples)
    return samples


def read_names_csv(path, key='cell', value='sample'):
    """{cell label: sample name} from a CSV with columns `key` (e.g. B1-A01) and `value`."""
    out = {}
    with open(path, newline='', encoding='utf-8-sig') as f:     # utf-8-sig: Excel's BOM
        for row in csv.DictReader(f):
            if row.get(value, '').strip():
                out[norm_cell(row[key])] = row[value].strip()
    print(f'{len(out)} named cells from {path}')
    return out


###############################################################################################
# Console helpers
###############################################################################################
def here(*axes):
    """Console: current positions, e.g. here() -> piezo x/y/z/th, here('sx', 'sy') -> Huber."""
    axes = axes or ('x', 'y', 'z', 'th')
    pos = tuple(round(float(AXES[a].position), 3) for a in axes)
    print(dict(zip(axes, pos)))
    return pos


def mov_sam(which, samples=None):
    """Console: move to a sample (key or name) of SAMPLES."""
    s = select(samples, which)[0]
    RE(move_to(s))
    print(f'at {s["key"]}: {s["name"]}')


def movx(dx):
    """Console: relative piezo x move (um)."""
    RE(bps.mvr(piezo.x, dx))


def movy(dy):
    """Console: relative piezo y move (um)."""
    RE(bps.mvr(piezo.y, dy))


def preflight():
    """Console: print the things that are easy to get wrong before a run."""
    md = RE.md
    print(f'proposal {md.get("data_session")}   cycle {md.get("cycle")}   project {md.get("project_name")}')
    print(f'user prefix "{YZ["user"]}"   experiment "{YZ["experiment"]}"')
    try:
        e_keV = energy.energy.position / 1000
        flag = '' if abs(e_keV - YZ['energy_keV']) < 0.01 else f'   <-- expected {YZ["energy_keV"]} keV'
        print(f'energy {e_keV:.3f} keV{flag}')
    except Exception as ex:
        print(f'energy: {ex}')
    print(f'SAXS sdd {pil2m_pos.z.position:.0f} mm   WAXS arc {waxs.arc.position:.2f} deg   '
          f'2M beamstop {pil2M.active_beamstop.get()}')
    print(f'logs -> {log_dir()}')
    if 'SAMPLES' in globals():
        print(f'{len(SAMPLES)} samples in SAMPLES')


def preview(plan, moves=False):
    """
    Console: dry-run a plan -- prints the file name of every exposure it would take (before the
    beamline's _eV_wa_sdd suffix; moves too with moves=True) without moving or taking data.  Alignments are skipped
    (current positions stand in), Linkam waits are skipped, series show 2 cycles, and no
    logbook / alignment files are written.  Errors (bad arc, missing alignment, beamstop
    out, ...) show up exactly as in the real run.

        preview(run_gi(**GI))
    """
    state = {}

    def value(obj):
        if obj in state:
            return state[obj]
        for get in (lambda: obj.position, lambda: obj.get()):
            try:
                return get()
            except Exception:
                pass
        return 0.0

    _LOG['preview'] = True
    n_runs, ret = 0, None
    try:
        while True:
            msg = plan.send(ret)
            ret = None
            obj = msg.obj
            if msg.command == 'set':
                state[obj] = msg.args[0]
                if obj is waxs:
                    state[_arc_rb()] = msg.args[0]
                if moves:
                    print(f'        {obj.name} -> {msg.args[0]}')
            elif msg.command == 'locate':
                v = value(obj)
                ret = {'readback': v, 'setpoint': v}
            elif msg.command == 'read' and (obj in state or hasattr(obj, 'position')
                                            or not hasattr(obj, 'component_names')):
                v = value(obj)                       # motors / signals; detectors get None
                keys = [obj.name] + list(getattr(obj, 'hints', {}).get('fields', []))
                ret = {k: {'value': v, 'timestamp': time.time()} for k in keys}
            elif msg.command == 'open_run':
                n_runs += 1
                print(f'{n_runs:5d}  {msg.kwargs.get("sample_name")}')
    except StopIteration:
        pass
    finally:
        _LOG['preview'] = False
    print(f'\npreview: {n_runs} runs')
    return n_runs


def _previewing():
    return bool(_LOG.get('preview'))


def yz_help():
    print(__doc__)
    print('Plans (use RE(...)):  run_trans, run_gi, run_gi_temperatures, run_series, run_ec,\n'
          '   align_gi, linkam_goto, linkam_off, measure_saxs/waxs/wsaxs, snap, ova_snap, expose\n'
          'Console:  preview(plan) = dry run;  make_samples, show_samples, select,\n'
          '   align_gi_samples, load_alignment,\n'
          '   mark_aligned, mov_sam, movx, movy, here, preflight, series_start, ec_start,\n'
          '   ec_set_potential, grid_cells, read_names_csv, linkam_T')


###############################################################################################
# Logs
###############################################################################################
_LOG = {}
_LOG_FIELDS = ['time', 'scan_id', 'uid', 'sample_name', 'sample', 'detectors', 'exposure_s',
               'incident_angle_deg', 'waxs_arc_deg', 'temperature_C', 'potential_V', 'frame_index',
               'elapsed_s'] + list(AXES)


def _tag(text):
    """File-name-safe tag for log / alignment files."""
    return re.sub(r'[^A-Za-z0-9_\-.]', '-', str(text))


def _iso(ts=None):
    return datetime.datetime.fromtimestamp(ts or time.time()).isoformat(timespec='seconds')


def log_dir():
    """Folder for alignment json + logbook: YZ['log_dir'], else <proposal>/projects/<project>/yz_logs,
    else ~/yz_smi_logs/<proposal>_<project>."""
    md = RE.md
    key = (YZ['log_dir'], md.get('cycle'), md.get('data_session'), md.get('project_name'))
    if _LOG.get('key') == key:
        return _LOG['dir']
    _, cycle, session, project = key
    if YZ['log_dir']:
        cands = [YZ['log_dir']]
    else:
        cands = []
        if cycle and session:
            cands.append(f'/nsls2/data/smi/proposals/{cycle}/{session}/projects/{project or "default"}/yz_logs')
        cands.append(os.path.expanduser(f'~/yz_smi_logs/{session}_{project}'))
    for d in cands:
        try:
            os.makedirs(d, exist_ok=True)
            if os.access(d, os.W_OK):
                _LOG.update(key=key, dir=d)
                print(f'yz logs -> {d}')
                return d
        except OSError:
            pass
    raise OSError(f'no writable log folder in {cands}')


def _logbook(name, hints, uid):
    if _previewing():
        return
    try:
        path = os.path.join(log_dir(), f'logbook_{_tag(YZ["user"] or "YZ")}.csv')
        row = {k: hints.get(k) for k in _LOG_FIELDS}
        row.update(hints['positions'])
        row.update(time=_iso(), scan_id=RE.md.get('scan_id'), uid=uid, sample_name=name,
                   detectors='+'.join(hints['detectors']))
        new = not os.path.exists(path)
        with open(path, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=_LOG_FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)
    except Exception as ex:
        if not _LOG.get('warned'):
            print(f'WARNING: logbook not written ({ex}); data collection continues')
            _LOG['warned'] = True


print('YZhang_SMI_Base loaded -- yz_help() for a summary, README.md for the run sheets')

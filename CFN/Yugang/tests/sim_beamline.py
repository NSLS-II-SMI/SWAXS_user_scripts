"""
Simulated SMI namespace for offline tests of the CFN/Yugang scripts (no EPICS, no beam).

The devices only mimic what YZhang_SMI_Base.py touches: piezo / stage (Huber) axes,
pil2M / pil900KW with the 2M beamstop state, the WAXS arc with its temporary 0-or->=14.5 deg
restriction, a Linkam whose temperature follows the setpoint (plus an adjustable lag), the GI
alignment plans (which can be told to fail at chosen piezo x positions), smi.modeMeasurement and
the on-axis camera's JPEG plugin (it records the files it would write).
"""
import os
import types

import numpy as np
import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky import RunEngine
from ophyd import Component as Cpt, Device, Signal
from ophyd.status import Status
from ophyd.sim import SynAxis, SynSignal

YUGANG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Piezo(Device):
    x = Cpt(SynAxis)
    y = Cpt(SynAxis)
    z = Cpt(SynAxis)
    th = Cpt(SynAxis)
    ch = Cpt(SynAxis)


class Huber(Device):
    x = Cpt(SynAxis)
    y = Cpt(SynAxis)
    z = Cpt(SynAxis)
    th = Cpt(SynAxis)
    ch = Cpt(SynAxis)
    ph = Cpt(SynAxis)


class Det(Device):
    image = Cpt(SynSignal, func=lambda: 1.0, kind='hinted')
    active_beamstop = Cpt(Signal, value='rod', kind='config')


class ArcMotor(Device):
    """Like the profile's arc EpicsMotor: user_readback is kind='normal' (instances/pilatus.py),
    so the motor has two read fields and no hint and bps.rd(waxs.arc) raises."""
    user_readback = Cpt(Signal, value=0.0, kind='normal')
    user_setpoint = Cpt(Signal, value=0.0, kind='normal')

    @property
    def position(self):
        return self.user_readback.get()

    def set(self, value):
        self.user_setpoint.put(value)
        self.user_readback.put(value)
        st = Status(self)
        st.set_finished()
        return st


class WAXS(Device):
    arc = Cpt(ArcMotor)

    def set(self, value):
        if not (abs(value) <= 0.1 or value >= 14.5):
            raise ValueError(f'The waxs detector cannot be moved to {value} deg')
        return self.arc.set(value)


class FollowSignal(Signal):
    """Linkam TEMP: setpoint + lag."""
    def get(self, **kwargs):
        p = self.parent
        return float(p.temperature_setpoint.get()) + float(p.lag.get())


class Linkam(Device):
    cmd = Cpt(Signal, value=0)
    temperature_setpoint = Cpt(Signal, value=25.0)
    temperature_rate_setpoint = Cpt(Signal, value=10.0)
    lnp_mode_set = Cpt(Signal, value='Manual')
    lag = Cpt(Signal, value=0.0, kind='omitted')
    temperature_current = Cpt(FollowSignal, value=25.0)


class WriteFileSignal(Signal):
    """JPEG1:WriteFile: writing 1 'saves' <FilePath><FileName> into the camera's `written` list."""
    def put(self, value, **kwargs):
        super().put(value, **kwargs)
        if value:
            p = self.parent
            p.written.append(p.file_path.get() + p.file_name.get())


class OVACam(Device):
    enable = Cpt(Signal, value=0)
    file_path = Cpt(Signal, value='')
    file_name = Cpt(Signal, value='')
    write_file = Cpt(WriteFileSignal, value=0)
    path_exists = Cpt(Signal, value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.written = []


class Energy(Device):
    energy = Cpt(SynAxis, value=16100.0)


class DetPos(Device):
    z = Cpt(SynAxis, value=5000.0)


def make_namespace(log_dir):
    """Fresh simulated session namespace with YZhang_SMI_Base.py loaded."""
    piezo = Piezo(name='piezo')
    stage = Huber(name='stage')
    pil2M = Det(name='pil2M')
    pil900KW = Det(name='pil900KW')
    waxs = WAXS(name='waxs')
    LThermal = Linkam(name='LinkamThermal')
    attenuation = Signal(name='attenuation', value=1)
    moxa_ch2 = Signal(name='moxa_out_ch2_read', value=0.25)

    sim = types.SimpleNamespace(fail_x=set(), exposures=[], align_calls=0, pause_in_align=False,
                                scans=[], th0=0.5, roi_angle=0.16, modes=[])

    def det_exposure_time(exp_t, meas_t=1, period_delay=0.001):
        sim.exposures.append(exp_t)
        yield from bps.null()

    def _fake_align(x_axis, y_axis, th_axis):
        sim.align_calls += 1
        yield from bps.mv(attenuation, 1e6)
        yield from bps.mv(pil2M.active_beamstop, 'rod_removed')
        if sim.pause_in_align:                         # like Ctrl-C during the scans
            yield from bps.checkpoint()
            yield from bps.pause()
        x = yield from bps.rd(x_axis)
        if round(x, 3) in sim.fail_x:
            th = yield from bps.rd(th_axis)
            yield from bps.mv(th_axis, th + 4.5)       # a failed fit can leave th at a scan edge
            raise RuntimeError('fit failed (sim)')
        yield from bps.mv(th_axis, 0.3 + x * 1e-5, y_axis, 100.0 + x * 1e-3)
        yield from bps.mv(pil2M.active_beamstop, 'rod', attenuation, 1)

    def alignment_gisaxs(angle=0.15):
        yield from _fake_align(piezo.x, piezo.y, piezo.th)

    def alignement_gisaxs_hex(angle=0.1, rough_y=0.5):
        yield from _fake_align(stage.x, stage.y, stage.th)

    def modeMeasurement():
        sim.modes.append('measurement')
        yield from bps.mv(pil2M.active_beamstop, 'rod', attenuation, 1)

    def modeAlignment(technique='gisaxs'):
        sim.modes.append('alignment')
        yield from bps.mv(attenuation, 1e6, pil2M.active_beamstop, 'rod_removed')

    def set_roi(*args, **kwargs):
        yield from bps.null()

    def set_reflected_roi(total_angle=0.16, technique='gisaxs', **kwargs):
        sim.roi_angle = total_angle
        yield from bps.null()

    # sample surface: half cut y = 150 + x/1000 on the direct beam (fails at sim.fail_x), and
    # 0.5 more on the reflected beam; th0 = sim.th0, the reflection peaks at th0 + ROI angle
    def align_gisaxs_height(rang=0.3, point=31, der=False):
        x = yield from bps.rd(piezo.x)
        th = yield from bps.rd(piezo.th)
        sim.scans.append(('y direct', round(th, 4)))
        if round(x, 3) in sim.fail_x:
            yield from bps.mv(piezo.y, 1e4)              # a failed fit can leave y anywhere
            raise RuntimeError('fit failed (sim)')
        yield from bps.mv(piezo.y, 150.0 + x * 1e-3)

    def align_gisaxs_height_rb(rang=0.3, point=31, der=False):
        x = yield from bps.rd(piezo.x)
        th = yield from bps.rd(piezo.th)
        sim.scans.append(('y reflected', round(th, 4)))
        yield from bps.mv(piezo.y, 150.5 + x * 1e-3)

    def align_gisaxs_th(rang=0.3, point=31, max_retries=3):
        th = yield from bps.rd(piezo.th)
        sim.scans.append(('th', round(th, 4)) if rang <= 0.2 else ('th search', round(th, 4), rang, point))
        peak = sim.th0 + sim.roi_angle
        if abs(th - peak) > rang:                        # the reflection is outside the scan
            yield from bps.mv(piezo.th, th + rang)
            raise RuntimeError('no peak in the scan (sim)')
        yield from bps.mv(piezo.th, peak)

    RE = RunEngine({})
    RE.md.update(cycle='2026-3', data_session='pass-000000', project_name='sim')
    docs = []
    RE.subscribe(lambda name, doc: docs.append((name, doc)))

    ns = dict(
        np=np, bp=bp, bps=bps, Signal=Signal, RE=RE,
        piezo=piezo, stage=stage, pil2M=pil2M, pil900KW=pil900KW, waxs=waxs,
        pil2m_pos=DetPos(name='pil2M_motor'), energy=Energy(name='energy'),
        LThermal=LThermal, attenuation=attenuation, moxa_ch2=moxa_ch2,
        ova_cam=OVACam(name='ova_cam'),
        huber_y_T=Signal(value=30.0, name='huber_y_T'),     # Huber y motor temperature (degC)
        det_exposure_time=det_exposure_time, alignment_gisaxs=alignment_gisaxs,
        alignement_gisaxs_hex=alignement_gisaxs_hex,
        align_gisaxs_height=align_gisaxs_height, align_gisaxs_height_rb=align_gisaxs_height_rb,
        align_gisaxs_th=align_gisaxs_th,
        smi=types.SimpleNamespace(modeMeasurement=modeMeasurement, modeAlignment=modeAlignment,
                                  setDirectBeamROI=set_roi, setReflectedBeamROI=set_reflected_roi),
        bec=types.SimpleNamespace(_calc_derivative_and_stats=False),
        _sim=sim, _docs=docs,
    )
    load(ns, 'YZhang_SMI_Base.py')
    ns['YZ']['log_dir'] = str(log_dir)
    return ns


def load(ns, script):
    """%run -i equivalent: execute a script of this folder in the namespace."""
    path = os.path.join(YUGANG, script)
    with open(path) as f:
        exec(compile(f.read(), path, 'exec'), ns)
    return ns


def starts(ns):
    return [d for n, d in ns['_docs'] if n == 'start']


def events(ns):
    return [d for n, d in ns['_docs'] if n == 'event']

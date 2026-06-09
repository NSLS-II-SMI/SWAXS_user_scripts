"""
technique_N_xpcs
================

Archetype N -- XPCS / coherent speckle bursts.

Speckle time-series for g2 intensity-correlation: a coherent beam on a single resonant spot,
captured as a **high-frame-rate burst** of many short exposures, then correlated offline into
g2(q, tau).  The defining constraint is *throughput* (hundreds--thousands of frames at a few ms
each) -- which is exactly where the legacy code left the document model.

THE ANTI-PATTERN TO FIX (``legacy/30-user-chen_xpcs.py::grid_scan_xpcs``)
------------------------------------------------------------------------
``grid_scan_xpcs`` does, per spot::

    pil2M.cam.file_path.put("/ramdisk/images/.../%s_pos%s" % ...)   # write-path override
    det_exposure_time(0.03, 30)                                     # 0.03 s x 30 s window
    pil2M.cam.acquire.put(1)                                        # raw PV trigger
    pv = EpicsSignal("XF:12IDC-ES:2{Det:1M}cam1:Acquire", ...)
    while pv.get() == 1:                                            # busy-wait on raw Acquire
        yield from bps.sleep(5)

i.e. it triggers the detector **outside the RunEngine** and busy-waits on the raw ``Acquire``
PV, writing frames to ``/ramdisk/``.  **No documents are recorded at all** -- the burst exists
only as loose files, with no run, no stream, no metadata, nothing in Tiled.  This is the single
highest-priority Tier-0 anti-pattern (Best-Practices Tenet 7 / open question #7).

THE SANCTIONED HIGH-FRAME-RATE CAPTURE (still records documents)
----------------------------------------------------------------
Configure the **frame count as a detector parameter** and let the area detector burst N frames
*internally* into **one recorded datum**, emitted by a single staged ``trigger_and_read``:

* set ``pil2M.cam.num_images`` = N and the per-frame time via ``det_exposure_time(frame, period)``
  -- the legacy ``pil2M.cam.num_images.set(2)`` idiom (``legacy/30-user-Cai.py``) generalized to
  a true burst;
* stage the detector (``one_sample_run`` does this) and ``yield from bps.trigger_and_read([pil2M, ...])``
  **once** -- the detector acquires all N frames and the HDF5/Tiled handler stores them as a
  single multi-frame array datum, with a real start/descriptor/event/stop and full metadata.

  .. warning::
      Do **NOT** use ``cam.acquire.put(1)`` + busy-wait + ``/ramdisk/``.  Use configured frames
      (``cam.num_images``) + a *staged* ``trigger_and_read`` so documents are emitted and the
      data is Tiled-backed.  Never override ``cam.file_path`` to ``/ramdisk/``; let the
      facility writer place frames.

Energy / I0 / temperature are recorded as context.  A **resonant** variant sets the energy near
an edge before the burst (the chen S-edge ~2473 eV motivation).  :func:`xpcs_bar` runs a
:class:`SampleList`.

Monitor / fly alternatives
--------------------------
For *continuous* streaming beyond a single multi-frame datum (very long g2, or decoupling
frame cadence from an environment probe), use ``bp.fly`` with an area-detector flyer, or
``bp.monitor`` / ``bluesky.preprocessors.monitor_during_wrapper`` on a fast Signal -- all still
inside the RunEngine.  The configured-frames burst below is the simplest sanctioned form and the
direct replacement for ``grid_scan_xpcs``; see :func:`xpcs_burst_run`'s notes.

Gold / reference: ``legacy/30-user-chen_xpcs.py::grid_scan_xpcs`` (what NOT to do),
``LBL/30-user-Su.py::xpcs_2025_1``, Cornell/Singer (coherence).

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``Signal``, ``piezo``, ``waxs``, ``energy``,
    ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``, ``det_exposure_time``, and
    (resonant variant) the DCM ``energy``.  An environment temperature device (e.g.
    ``ls.input_A``) is optional and passed in.
"""

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, fname, merge_md)
from ._preprocessors import (ensure_in_wrapper, cleanup_wrapper, baseline_wrapper,
                             beam_loss_reseek_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bpp = None


__all__ = [
    "configure_burst", "xpcs_burst_run", "xpcs_resonant_burst_run", "xpcs_bar", "example",
    "example_resonant",
]


# ---------------------------------------------------------------------------
# Configure the camera for an internal N-frame burst (the heart of the fix)
# ---------------------------------------------------------------------------
def configure_burst(det, frame_time, n_frames, *, period=None):
    """Configure ``det`` to acquire an internal burst of ``n_frames`` x ``frame_time`` seconds.

    This is the sanctioned replacement for ``cam.acquire.put(1)`` + busy-wait: instead of
    triggering outside the RunEngine, we set the *number of images* on the camera so a single
    staged trigger acquires the whole burst and the detector reports one multi-frame datum.

    Parameters
    ----------
    det : area detector (e.g. ``pil2M``)
        Must expose ``det.cam.num_images``.
    frame_time : float
        Per-frame exposure (s), e.g. ``0.003``--``0.05`` for speckle.
    n_frames : int
        Number of frames in the burst (e.g. 1000).  The g2 series length.
    period : float, optional
        Frame period (s); defaults to ``frame_time`` (back-to-back).  Use a larger value for a
        slower cadence.

    Notes
    -----
    Uses ``det_exposure_time(frame, period)`` (the SMI helper) for exposure + period, then sets
    ``num_images`` via the *device* (``bps.mv``), never a raw ``cam.acquire.put``.  ``num_images``
    is also recorded in the baseline by :func:`xpcs_burst_run` so the burst length is provenance.
    """
    per = period if period is not None else frame_time
    det_exposure_time(frame_time, per)                          # noqa: F821
    yield from bps.mv(det.cam.num_images, int(n_frames))


# ---------------------------------------------------------------------------
# One run = one speckle burst on a single spot
# ---------------------------------------------------------------------------
def xpcs_burst_run(name, *, frame_time=0.01, n_frames=1000, period=None, dets=None,
                   burst_det=None, reads=None, temperature=None, geometry="transmission",
                   flux_signal=None, flux_threshold=None, atten_in=None, baseline=None,
                   md=None, name_tokens=("xpcs", "{frame_time_s}sx{n_frames}",
                                         "bpm{xbpm2_sumX}")):
    """ONE run: a high-frame-rate speckle burst on a single (pre-positioned) spot.

    The burst is captured as configured internal frames on ``burst_det`` (default ``pil2M``):
    ``num_images = n_frames`` is set, the detector is staged (by :func:`_core.one_sample_run`),
    and a **single** ``trigger_and_read`` acquires all ``n_frames`` into one recorded
    multi-frame datum -- with a real run, descriptor, event and stop, and full metadata in
    Tiled.  This is the document-preserving replacement for ``grid_scan_xpcs``.

    Energy, I0 (xbpm), optional temperature, the per-frame time and the frame count are recorded
    (frame_time / n_frames as Signals -> filename tokens; SDD + num_images in baseline) so the
    burst is fully self-describing.

    Parameters
    ----------
    name : str
        Human sample / spot label (start of the templated filename).
    frame_time : float
        Per-frame exposure (s).  Speckle bursts are typically a few ms to tens of ms.
    n_frames : int
        Frames in the burst (the correlation series length).
    period : float, optional
        Frame period (s); defaults to ``frame_time``.
    dets : list, optional
        Detectors to STAGE for the run.  Default ``[burst_det, xbpm2, xbpm3]``.  ``xbpm`` are
        cheap I0 monitors recorded alongside the burst.
    burst_det : area detector, optional
        The detector that bursts frames.  Default ``pil2M`` (in-vacuum SAXS, the XPCS detector).
    reads : list, optional
        Extra readables recorded with the burst event.  Default ``[energy, xbpm2, xbpm3]``
        (+ ``temperature`` if given).
    temperature : ophyd readable, optional
        e.g. ``ls.input_A`` -- recorded each event if provided (record the temperature, don't
        bake it into the name).
    geometry : str
        ``"transmission"`` or ``"reflection"``.
    flux_signal, flux_threshold : optional
        If both given, re-seek when I0 drops below threshold *before* the burst (so the burst is
        taken with beam).  Uses the beam-loss preprocessor.
    atten_in : callable () -> plan, optional
        Measurement-configuration guard (e.g. ensure the right attenuator) run once at run open.
    baseline : list, optional
        Constants recorded once.  SDD (``pil2M_pos.z``) and ``num_images`` are appended.
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens; default references recorded ``{frame_time_s}``, ``{n_frames}`` and
        ``{xbpm2_sumX}``.

    Notes
    -----
    *One burst = one run* (one logical XPCS measurement).  For a grid of spots, call this per
    spot (e.g. via :func:`xpcs_bar`) -- NOT a nested run-per-point loop.  For continuous
    streaming longer than one datum, see the monitor/fly note in the module docstring.
    """
    bdet = burst_det if burst_det is not None else pil2M        # noqa: F821
    if dets is None:
        dets = [bdet, xbpm2, xbpm3]                             # noqa: F821
    if reads is None:
        reads = [energy, xbpm2, xbpm3]                          # noqa: F821
    reads = list(reads)
    if temperature is not None and temperature not in reads:
        reads = reads + [temperature]

    # Burst parameters as recorded Signals -> {frame_time_s} / {n_frames} filename tokens.
    frame_time_s = Signal(name="frame_time_s", value=float(frame_time))  # noqa: F821
    n_frames_sig = Signal(name="n_frames", value=int(n_frames))          # noqa: F821
    reads = reads + [frame_time_s, n_frames_sig]

    base = list(baseline) if baseline else []
    base = base + [bdet.cam.num_images]                         # burst length is provenance
    try:
        base = base + [pil2M_pos.z]                            # noqa: F821 (SDD)
    except Exception:
        pass

    sample_name = fname(name, *name_tokens)

    def _measure():
        # Configure the internal burst, then a SINGLE staged trigger_and_read records it.
        yield from configure_burst(bdet, frame_time, n_frames, period=period)
        # The detector acquires all n_frames internally; one event, one multi-frame datum.
        yield from bps.trigger_and_read(list(dets) + list(reads))

    plan = one_sample_run(_measure, dets, sample_name=sample_name,
                          scan_name="xpcs_burst", geometry=geometry,
                          md=md, baseline=base)

    # Re-seek the beam right before the burst if I0 is low (so the burst lands on beam).
    if flux_signal is not None and flux_threshold is not None:
        def _reseek():
            yield from bps.mv(energy, energy.position)         # noqa: F821 (gentle re-command)
            yield from bps.sleep(2)
        plan = beam_loss_reseek_wrapper(plan, flux_signal, flux_threshold, _reseek)
    if atten_in is not None:
        plan = ensure_in_wrapper(plan, atten_in)

    # Always restore num_images=1 so a stray later count is not a giant burst.
    def _restore():
        yield from bps.mv(bdet.cam.num_images, 1)
    plan = cleanup_wrapper(plan, _restore)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Resonant variant: set the energy near an edge before the burst
# ---------------------------------------------------------------------------
def xpcs_resonant_burst_run(name, edge_energy, *, settle=10.0, **kwargs):
    """ONE run: set the DCM energy to ``edge_energy`` (resonant), settle, then a speckle burst.

    Resonant XPCS enhances contrast for a chosen element by sitting on/near its absorption edge
    (the chen S-edge ~2473 eV case).  This is :func:`xpcs_burst_run` with an energy move +
    settle prepended *inside the run* (so the energy is recorded), and ``energy`` is in the read
    list so ``{energy_energy}`` resolves.

    Parameters
    ----------
    name : str
        Human sample / spot label.
    edge_energy : float
        DCM energy (eV) to set before the burst (e.g. ``2473`` near the S K-edge).
    settle : float
        Sleep (s) after the energy move (DCM + beam settle) before the burst.
    **kwargs :
        Forwarded to :func:`xpcs_burst_run` (``frame_time``, ``n_frames``, ``dets``, ...).  An
        ``{energy_energy}`` token is added to ``name_tokens`` if the caller did not set it.
    """
    kwargs.setdefault("name_tokens", ("xpcs", "{energy_energy}eV",
                                      "{frame_time_s}sx{n_frames}", "bpm{xbpm2_sumX}"))
    # Ensure energy is recorded for the {energy_energy} token.
    reads = kwargs.get("reads")
    if reads is None:
        reads = [energy, xbpm2, xbpm3]                          # noqa: F821
        kwargs["reads"] = reads

    # Wrap the burst's measurement by setting energy first via an apply-like closure: simplest
    # is to set energy before delegating (it is recorded because energy is in reads).
    def _set_energy():
        yield from bps.mv(energy, edge_energy)                  # noqa: F821
        yield from bps.sleep(settle)

    # Prepend the energy move as a measurement-config step that runs once at run open.
    existing_atten = kwargs.pop("atten_in", None)

    def _setup():
        yield from _set_energy()
        if existing_atten is not None:
            yield from existing_atten()

    return (yield from xpcs_burst_run(name, atten_in=_setup,
                                      md=merge_md({"resonant_edge_eV": float(edge_energy)},
                                                  kwargs.pop("md", None)),
                                      **kwargs))


# ---------------------------------------------------------------------------
# Multi-spot / multi-sample bar (one run per spot)
# ---------------------------------------------------------------------------
def xpcs_bar(samples, *, frame_time=0.01, n_frames=1000, period=None, dets=None,
             burst_det=None, temperature=None, geometry="transmission", edge_energy=None,
             flux_signal=None, flux_threshold=None, atten_in=None, md=None):
    """Run an XPCS burst on each spot of the bar (ONE run per spot).

    ``samples`` is a :class:`SampleList`; each is coarse-positioned (piezo/hexapod) then a single
    burst is taken.  XPCS is single-spot per measurement, so this is the natural orchestration
    (each spot = one logical g2 measurement = one run).  If ``edge_energy`` is given, each spot
    uses :func:`xpcs_resonant_burst_run` (resonant); otherwise :func:`xpcs_burst_run`.

    Each spot is a *fresh* spot by construction (different sample coordinates), which is the
    XPCS analogue of dose management -- no per-frame nudge (that would smear g2); use distinct
    spots instead.
    """
    for s in samples:
        yield from goto_sample(s)
        if edge_energy is not None:
            yield from xpcs_resonant_burst_run(
                s.name, edge_energy, frame_time=frame_time, n_frames=n_frames, period=period,
                dets=dets, burst_det=burst_det, temperature=temperature, geometry=geometry,
                flux_signal=flux_signal, flux_threshold=flux_threshold, atten_in=atten_in,
                md=merge_md(md, s.md))
        else:
            yield from xpcs_burst_run(
                s.name, frame_time=frame_time, n_frames=n_frames, period=period, dets=dets,
                burst_det=burst_det, temperature=temperature, geometry=geometry,
                flux_signal=flux_signal, flux_threshold=flux_threshold, atten_in=atten_in,
                md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """A 1000-frame, 10 ms speckle burst on each of 3 spots, transmission, with I0 re-seek.

    The document-preserving replacement for ``grid_scan_xpcs``: each spot is ONE run capturing
    a configured 1000-frame burst (Tiled-backed), with energy / xbpm recorded.  Run with::

        RE(technique_N_xpcs.example())
    """
    bar = SampleList.from_columns(
        names=["PSBMA_spot1", "PSBMA_spot2", "PSBMA_spot3"],
        piezo_x=[-9350, -9290, -9230],
        piezo_y=[1220, 1220, 1220],
        md={"project_name": "301000_Demo", "technique": "xpcs"},
    )

    def _atten_in():
        # XPCS usually runs with NO extra attenuation (coherent flux is precious); shown as the
        # hook where you would set a measurement attenuator if your sample needs it.
        yield from bps.null()                                   # noqa: F821 (placeholder)

    yield from xpcs_bar(
        bar, frame_time=0.01, n_frames=1000, geometry="transmission",
        flux_signal=xbpm2.sumX, flux_threshold=50,             # noqa: F821
        atten_in=_atten_in,
        md={"detector": "pil2M", "coherent": True},
    )


def example_resonant():
    """Resonant XPCS: a 2000-frame, 5 ms burst at the S K-edge (~2473 eV) on one spot.

    Run with::

        RE(technique_N_xpcs.example_resonant())
    """
    yield from xpcs_resonant_burst_run(
        "PSBMA_Sedge_spot1", edge_energy=2473.0, settle=10.0,
        frame_time=0.005, n_frames=2000, geometry="transmission",
        flux_signal=xbpm2.sumX, flux_threshold=50,             # noqa: F821
        md={"project_name": "301000_Demo", "edge": "S_K", "coherent": True},
    )

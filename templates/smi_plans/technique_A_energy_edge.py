"""
technique_A_energy_edge
=======================

Archetype A -- Tender-energy resonant scattering & NEXAFS (TReXS / edge scanning).

Sweep the DCM energy across an absorption edge while collecting scattering (SAXS/WAXS) and/or
transmitted flux, in transmission or grazing geometry.  This is the most common SMI mode.

**This file is a PRESET RECIPE built on the composition layer (``_compose``).**  "Energy
sweep" is just one scan axis (:func:`_compose.energy_axis`); this file pre-assembles it with a
sensible energy grid + I0 re-seek + fresh-spot for the common NEXAFS case.  To *combine* an
energy sweep with other concerns (temperature, incidence, spatial, manual steps), compose the
axes directly with :func:`_compose.acquire` -- see ``recipes_combined.py`` and the README.

Gold reference: ``nist/richter/Cl_nexafs.py`` -- the cleanest Tier-4 file.  Every NEXAFS sweep
below is ONE run whose filename is templated from *recorded* fields (``{energy_energy}``,
``{xbpm2_sumX}``, ...), not ``.get()`` strings.

What this file gives you
------------------------
* :func:`energy_grid` -- build a fine-near-edge / coarse-wings energy array.
* :func:`nexafs_run` -- ONE run: up (and optional down) energy sweep on a single sample,
  assembled from an :func:`_compose.energy_axis`.
* :func:`nexafs_bar` -- loop :func:`nexafs_run` over a :class:`SampleList` (one run/sample).
* :func:`example` -- a runnable, fully-specified example.

Idioms preserved: beam-loss re-seek (in the energy axis), fresh-spot dose walking, ensure
attenuators in, baseline capture, up/down reversibility passes.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``Signal``, ``energy``, ``pil2M``, ``pil900KW``,
    ``xbpm2``, ``xbpm3``, ``pin_diode``, ``pil2M_pos``, ``att2_9``, ``waxs``, ``det_exposure_time``.
"""

from ._samples import SampleList
from ._core import goto_sample, merge_md
from ._compose import acquire, energy_axis, ScanAxis, SPEED_MEDIUM
from ._preprocessors import fresh_spot_wrapper, ensure_in_wrapper

try:
    import bluesky.plan_stubs as bps
except Exception:  # pragma: no cover
    bps = None


__all__ = ["energy_grid", "nexafs_run", "nexafs_bar", "example"]


# ---------------------------------------------------------------------------
# Energy grids
# ---------------------------------------------------------------------------
def energy_grid(edge, pre=(-30, -2, 5.0), near=(-2, 2, 0.25), post=(2, 60, 5.0)):
    """Build a 1-D energy array: coarse pre-edge, fine near-edge, coarse post-edge.

    Each of ``pre``/``near``/``post`` is ``(start_offset, stop_offset, step)`` in eV relative
    to ``edge``.  Mirrors the hand-built ``np.concatenate((np.arange(...), ...))`` grids that
    pervade the corpus (e.g. McNeil's 63-point S-edge grid).

    Returns
    -------
    np.ndarray of absolute energies (eV), de-duplicated and sorted.
    """
    segs = []
    for (a, b, s) in (pre, near, post):
        if s <= 0:
            continue
        segs.append(np.arange(edge + a, edge + b, s))          # noqa: F821 (np global)
    grid = np.unique(np.concatenate(segs)) if segs else np.array([edge])  # noqa: F821
    return grid


# ---------------------------------------------------------------------------
# One run = one sample, up (+down) energy sweep  -- assembled from energy_axis
# ---------------------------------------------------------------------------
def nexafs_run(name, energies, *, t=2.0, dets=None, reads=None, geometry="transmission",
               updown=True, settle=2.0, dose_motor=None, dose_step=None,
               flux_signal=None, flux_threshold=None, atten_in=None, baseline=None,
               md=None, name_tokens=("{energy_energy}eV", "bpm{xbpm2_sumX}")):
    """ONE run: NEXAFS / resonant energy sweep on a single sample.

    Recipe: a single :func:`_compose.energy_axis` (optionally up+down) inside
    :func:`_compose.acquire`.  All the knobs below map onto that axis / the run envelope.

    Parameters
    ----------
    name : str
        Human sample label (start of the templated filename).
    energies : sequence
        Energies (eV); e.g. from :func:`energy_grid`.
    t : float
        Exposure / averaging time (s).  Applied to detectors and ``pin_diode``.
    dets : list, optional
        Default ``[pil2M, pin_diode, xbpm2, xbpm3]`` (SAXS + I0 + transmission).
    reads : list, optional
        Extra readables recorded each event.  Default ``[energy]`` (so ``{energy_energy}``
        resolves).
    geometry : str
        ``"transmission"`` or ``"reflection"``.
    updown : bool
        If True, follow the up-sweep with a reversed down-sweep in the SAME run; an
        ``energy_direction`` Signal is recorded so frames are distinguishable.
    settle : float
        Sleep after each energy move.
    dose_motor, dose_step : optional
        Walk ``dose_motor`` by ``dose_step`` after every frame (fresh spot).
    flux_signal, flux_threshold : optional
        Re-seek the energy when I0 drops below threshold (handled inside the energy axis).
    atten_in : callable () -> plan, optional
        Put attenuators/beamstop in the measurement config after any prior alignment (runs once
        at run open via :func:`_compose.acquire`'s ``setup``).
    baseline : list, optional
        Constants (default adds SDD ``pil2M_pos.z`` if available).
    md : dict, optional
        Caller intent merged into the run md.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename.
    """
    if dets is None:
        dets = [pil2M, pin_diode, xbpm2, xbpm3]                 # noqa: F821
    if reads is None:
        reads = [energy]                                       # noqa: F821

    if baseline is None:
        try:
            baseline = [pil2M_pos.z]                            # noqa: F821 (SDD)
        except Exception:
            baseline = []

    det_exposure_time(t, t)                                     # noqa: F821

    # energy_direction Signal distinguishes up vs down frames within the single run.
    energy_direction = Signal(name="energy_direction", value="up")  # noqa: F821
    all_reads = list(reads) + [energy_direction]

    # Concatenate the up pass (and a reversed down pass) into ONE energy axis so both live in
    # ONE run; a per-point hook tags each frame's direction and re-seeks the beam.
    values = list(energies)
    if updown:
        values = values + list(energies)[::-1]
    n_up = len(energies)
    idx = {"i": 0}

    def _per_point():
        energy_direction.put("up" if idx["i"] < n_up else "down")
        idx["i"] += 1
        if flux_signal is not None and flux_threshold is not None:
            tries = 0
            while flux_signal.get() < flux_threshold and tries < 3:
                yield from bps.mv(energy, energy.position)      # noqa: F821 (re-seek)
                yield from bps.sleep(settle)
                tries += 1
        else:
            yield from bps.null()

    e_axis = ScanAxis("energy", values, device=energy,          # noqa: F821
                      settle=settle, per_point=_per_point,
                      reads=[energy], speed=SPEED_MEDIUM)         # gives {energy_energy}

    def _setup():
        yield from bps.mv(pin_diode.averaging_time, t)         # noqa: F821
        if atten_in is not None:
            yield from atten_in()
        energy_direction.put("up")

    plan = acquire(name, dets, [e_axis], reads=all_reads, setup=_setup,
                   geometry=geometry, scan_name="nexafs_energy_sweep",
                   md=md, baseline=baseline, name_tokens=list(name_tokens),
                   check_order=False)

    if dose_motor is not None and dose_step is not None:
        plan = fresh_spot_wrapper(plan, dose_motor, dose_step)
    return (yield from plan)


# ---------------------------------------------------------------------------
# Multi-sample bar (one run per sample)
# ---------------------------------------------------------------------------
def nexafs_bar(samples, energies, *, t=2.0, dets=None, reads=None, geometry="transmission",
               updown=True, settle=2.0, dose_step=None, flux_signal=None,
               flux_threshold=None, atten_in=None, md=None):
    """Run :func:`nexafs_run` for each sample on the bar (ONE run per sample).

    ``samples`` is a :class:`SampleList`.  Each sample is coarse-positioned (piezo/hexapod)
    then swept.  For grazing NEXAFS, compose an incidence axis too (see ``recipes_combined``).
    """
    for s in samples:
        yield from goto_sample(s)
        ds_motor = piezo.x if dose_step else None              # noqa: F821
        yield from nexafs_run(
            s.name, energies, t=t, dets=dets, reads=reads, geometry=geometry,
            updown=updown, settle=settle, dose_motor=ds_motor, dose_step=dose_step,
            flux_signal=flux_signal, flux_threshold=flux_threshold,
            atten_in=atten_in, md=merge_md(md, s.md))


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------
def example():
    """Cl K-edge NEXAFS on a 3-sample bar, transmission, up+down, with I0 re-seek.

    Run with::

        RE(technique_A_energy_edge.example())
    """
    bar = SampleList.from_columns(
        names=["P3HT_undoped", "P3HT_topdope", "PVC_36nm"],
        piezo_x=[-56000, -45000, 23000],
        piezo_y=[4000, 4000, 4000],
        md={"project_name": "311234_Demo"},
    )
    energies = energy_grid(2822, pre=(-12, -2, 2.0), near=(-2, 2, 0.5), post=(2, 70, 5.0))

    def _atten_in():
        yield from bps.mv(att2_9.close_cmd, 1)                  # noqa: F821
        yield from bps.sleep(1)

    yield from nexafs_bar(
        bar, energies, t=1.0, geometry="transmission", updown=True,
        dose_step=30,                          # fresh spot in piezo.x each frame
        flux_signal=xbpm2.sumX, flux_threshold=50,             # noqa: F821
        atten_in=_atten_in,
        md={"edge": "Cl_K"},
    )

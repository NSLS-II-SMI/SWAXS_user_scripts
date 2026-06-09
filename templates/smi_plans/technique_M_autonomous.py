"""
technique_M_autonomous
======================

Archetype M -- Autonomous / closed-loop / ML- or agent-driven acquisition.

The frontier of SMI operation: an *optimizer* (BoTorch / Gaussian-process) or an
*LLM/VLM agent* picks the next measurement, the beamline executes a plan, and the result is
read back and fed into the next decision.  Two in-repo references anchor this file:

* **CFN ``DropletReactor``** (``CFN/Yugang/2024C3_Drop.py``, ``2025C2_SMI.py``) -- autonomous
  droplet nanoparticle synthesis.  A BoTorch loop running in a *separate* process hands the
  next batch in via ``Batch_push.npz`` / ``Batch_T_t_dict.npz`` files; the beamline polls those
  npz files and measures.  (Its acquisition is legacy -- ``RE(bp.count(...))`` *inside* a
  ``while``; this file shows the corrected shape.)
* **CDSAXS auto-alignment** (``CDSAXS/Auto_alignment_CD-SAXS/slope_chase_alignment.py`` and
  ``CDSAXS/local_ranking/at_beamline.py::auto()``) -- a vision-LLM levels chi/theta or finds the
  rotation center: scan once (a single ``rel_grid_scan`` / ``count`` run), pull the images back
  from **Tiled**, decide a correction, ``bps.mv`` to it, repeat until converged.

THE KEY ARCHITECTURE (get this right and the rest follows)
----------------------------------------------------------
The **decision loop lives in plain Python** -- that is appropriate and sanctioned for
closed-loop optimization (you cannot express "ask BoTorch / ask an LLM" as a Bluesky message).
But **all acquisition goes through proper single-run plans**, and **results are read back via
the data broker** (``db``/Tiled, e.g. ``db[-1]``), *never* by triggering detectors outside the
RunEngine.  Concretely:

* a measurement plan :func:`measure_for_agent` -> **ONE run** (uses
  :func:`_core.one_sample_run`) that records the agent's chosen parameters as Signals so they
  land in the data and the filename;
* an orchestration **function** :func:`autonomous_loop` (NOT a plan) that calls
  ``suggest() -> params``, runs ``RE(measure_for_agent(params))``, reads the result back from
  the broker, calls ``analyze() -> feedback``, and repeats.

  .. warning::
      :func:`autonomous_loop` is the **one sanctioned place** ``RE(...)`` is called from Python
      -- the closed-loop controller, which sits **outside / above** the plans.  This is the
      *opposite* of the Tenet-7 anti-pattern (``RE()`` *inside* a plan / ``for`` loop, e.g.
      ``DropletReactor.measure`` doing ``RE(bp.count(dets))`` within a ``while``).  The plans
      stay pure generators; only the controller drives the RunEngine.

* a closed-loop **alignment** example :func:`align_loop` mirroring ``slope_chase``: measure (a
  single ``rel_grid_scan`` run) -> ``analyze(uid) -> correction`` (you inject the image
  analysis) -> ``RE(bps.mv(...))`` -> repeat until converged.

A simple BoTorch-style **ask/tell** stub (:func:`ask_tell_loop`, :class:`GridAskTell`) shows the
suggest/analyze contract with *no hard ML dependency* -- inject your own ``suggest``/``analyze``.

Develop against the digital twin first
--------------------------------------
``CDSAXS/DummyBluSky`` is a faithful **digital twin** (KDTree image replay from real frames,
lab-frame ``PseudoPositioner`` rotation math, a caproto IOC, and a Tiled-like ``db``) with the
same device/PV names as production.  Point ``re``/``broker`` at the twin to develop and
benchmark a controller **without beam time**, then run it unchanged on the real beamline.

.. important::
    Beamline globals required at runtime (injected by the SMI profile collection; not
    importable standalone): ``np``, ``bps``, ``Signal``, ``piezo``, ``prs``, ``waxs``,
    ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2``, ``xbpm3``, ``pil2M_pos``,
    ``det_exposure_time``, and the live ``RE`` (RunEngine) + ``db`` (databroker / Tiled).
    Unlike the pure plan files, the *orchestration functions* here legitimately take ``re`` and
    ``broker`` arguments (defaulting to those globals) because they ARE the controller.  The
    optimizer / agent (``suggest``/``analyze``) is supplied by the caller -- there is no hard
    BoTorch or LLM dependency in this module.
"""

import time

from ._samples import SampleList
from ._core import (one_sample_run, goto_sample, fname, merge_md)
from ._preprocessors import (ensure_in_wrapper, cleanup_wrapper, baseline_wrapper)

try:
    import bluesky.plan_stubs as bps
    import bluesky.plans as bp
    import bluesky.preprocessors as bpp
except Exception:  # pragma: no cover
    bps = None
    bp = None
    bpp = None


__all__ = [
    "measure_for_agent",
    "read_back_result",
    "autonomous_loop",
    "align_loop",
    "GridAskTell",
    "ask_tell_loop",
    "example",
    "example_alignment",
]


# ---------------------------------------------------------------------------
# 1. The measurement PLAN the agent drives -- ONE run, params recorded as Signals
# ---------------------------------------------------------------------------
def measure_for_agent(params, *, dets=None, reads=None, apply_params=None, t=1.0,
                      geometry="transmission", baseline=None, md=None,
                      scan_name="autonomous_measure", name_base="auto",
                      name_tokens=("it{agent_iter}", "bpm{xbpm2_sumX}")):
    """ONE run that realizes an agent's chosen ``params`` and records them in the data.

    This is the *only* acquisition primitive the controller calls.  It is a normal pure
    generator (no ``RE()`` inside) wrapped in :func:`_core.one_sample_run`: the agent's
    parameter vector is stamped into per-parameter ``Signal`` objects that are read in the
    primary stream, so every autonomous point is **self-describing** -- you can later recover
    "what did the optimizer ask for here?" from the broker, not from a side-channel npz file.

    Parameters
    ----------
    params : dict
        The agent's suggestion, e.g. ``{"temperature": 105, "flow": 80, "agent_iter": 7}``.
        Each key becomes a recorded ``Signal`` named exactly that key, so ``{<key>}`` is a
        filename token (numbers and strings both work).
    dets : list, optional
        Detectors.  Default ``[pil2M, pil900KW, xbpm2, xbpm3]`` (SAXS + WAXS + I0).
    reads : list, optional
        Extra readables recorded each event.  Default ``[energy, xbpm2, xbpm3]``.
    apply_params : callable(params) -> plan, optional
        Plan that physically realizes ``params`` (move a stage to a reaction position, set a
        temperature / flow on the rig, set the energy, ...).  You provide it; it runs *inside*
        the run so its moves are recorded.  If ``None``, nothing is actuated (the controller is
        assumed to have set the world up before calling -- e.g. the DropletReactor npz hand-off
        where a separate process already prepared the batch).
    t : float
        Exposure time (s).
    geometry : str
        ``"transmission"`` (droplet/solution synthesis) or ``"reflection"``.
    baseline : list, optional
        Constants recorded once (SDD ``pil2M_pos.z`` added if available).
    md : dict, optional
        Caller / agent intent merged into the run md (``project_name``, the full ``params``
        dict under ``agent_params``, the optimizer name, ...).
    scan_name : str
        Run purpose tag.
    name_base : str
        Human label that starts the templated filename.
    name_tokens : tuple of str
        ``{field}`` tokens appended to the filename; default references the recorded
        ``{agent_iter}`` and ``{xbpm2_sumX}``.

    Returns
    -------
    The plan; ``yield from`` it (the controller does ``RE(measure_for_agent(params))``).
    """
    if dets is None:
        dets = [pil2M, pil900KW, xbpm2, xbpm3]                  # noqa: F821
    if reads is None:
        reads = [energy, xbpm2, xbpm3]                          # noqa: F821

    # Each parameter becomes a recorded Signal -> available as a {key} filename token and as a
    # searchable stream field.  This is how the optimizer's intent gets INTO the data.
    param_sigs = []
    for key, val in params.items():
        sig = Signal(name=str(key), value=val)                 # noqa: F821
        param_sigs.append(sig)

    base = list(baseline) if baseline else []
    try:
        base = base + [pil2M_pos.z]                            # noqa: F821 (SDD)
    except Exception:
        pass

    # Record the whole suggestion (and that this was agent-driven) as intent metadata too.
    run_md = merge_md({"agent_params": dict(params), "driver": "autonomous"}, md)

    det_exposure_time(t, t)                                    # noqa: F821
    sample_name = fname(name_base, *name_tokens)

    def _measure():
        if apply_params is not None:
            yield from apply_params(params)                    # realize params inside the run
        yield from bps.trigger_and_read(list(dets) + list(reads) + param_sigs)

    return (yield from one_sample_run(
        _measure, dets, sample_name=sample_name, scan_name=scan_name,
        geometry=geometry, md=run_md, baseline=base))


# ---------------------------------------------------------------------------
# 2. Read the just-finished run back from the broker (NOT by re-triggering detectors)
# ---------------------------------------------------------------------------
def read_back_result(broker=None, *, uid=None, fields=None):
    """Return the recorded data of a finished run from the data broker.

    This is the **sanctioned** way to get a measurement back into Python for the optimizer:
    pull it from ``db``/Tiled *after* the run closed, exactly as ``slope_chase`` does
    (``db.v2[-1].primary.read()['pil2M_image']``) and ``at_beamline.auto()`` does
    (``db.v2[scan_id]['primary']['data'][...]``).  Never re-read the live PV / re-trigger the
    detector to obtain the result.

    Parameters
    ----------
    broker : databroker / Tiled handle, optional
        Defaults to the global ``db``.
    uid : str or int, optional
        The run to read.  Default ``-1`` (the most recent run, i.e. the one
        :func:`autonomous_loop` just executed).
    fields : list of str, optional
        If given, return only these stream fields (e.g. ``["pil2M_stats1_total"]``); otherwise
        return the whole primary table / dataset.

    Returns
    -------
    The primary-stream data (a table / xarray, broker-version dependent).  The caller's
    ``analyze`` turns this into a scalar objective.

    Notes
    -----
    Implementation is intentionally defensive about databroker v1 vs v2 / Tiled APIs since SMI
    spans several; adapt the one ``getattr`` chain below to your deployment if needed.
    """
    b = broker if broker is not None else db                   # noqa: F821
    key = -1 if uid is None else uid

    run = b[key]
    # v2 / Tiled: run['primary']['data'][field].read(); v1: run.table()
    try:
        primary = run["primary"]["data"]
        if fields:
            return {f: primary[f].read() for f in fields}
        return primary.read()
    except Exception:
        tbl = run.table()
        if fields:
            return tbl[fields]
        return tbl


# ---------------------------------------------------------------------------
# 3. THE closed-loop controller -- the ONE sanctioned RE() caller (a FUNCTION, not a plan)
# ---------------------------------------------------------------------------
def autonomous_loop(suggest, analyze, *, max_iter=20, stop=None, re=None, broker=None,
                    measure=None, on_step=None, settle=0.0, **measure_kwargs):
    """Run an autonomous experiment: suggest -> measure (RE) -> read back -> analyze -> repeat.

    **This is a plain Python function, NOT a Bluesky plan.**  It is the closed-loop controller
    and the single sanctioned place ``RE(...)`` is invoked from Python.  It sits *above* the
    plans: every acquisition is a proper single run (:func:`measure_for_agent`), and every
    result comes back through the broker (:func:`read_back_result`) -- so the loop never breaks
    the document model the way ``DropletReactor.AutoRun_batch`` (RE-in-while) does.

    The optimizer / agent is fully injected:

    * ``suggest(history) -> params`` -- ask the optimizer / LLM for the next parameter dict
      (BoTorch ``acqf`` argmax, an LLM tool call, a grid walk, ...).  ``history`` is the list of
      ``(params, feedback)`` tuples so far.
    * ``analyze(result, params) -> feedback`` -- turn the broker read-back into a scalar /
      structured objective the optimizer can ``tell`` (e.g. peak intensity, 1/sigma of a fit,
      an LLM quality score).

    Parameters
    ----------
    suggest : callable(history) -> dict
        Proposes the next ``params``.  Return ``None`` to stop early.
    analyze : callable(result, params) -> Any
        Computes feedback from the just-finished run's data.
    max_iter : int
        Hard cap on iterations (always have one for autonomous runs).
    stop : callable(history) -> bool, optional
        Optional convergence test evaluated after each analyze; truthy ends the loop.
    re : RunEngine, optional
        Defaults to the global ``RE``.  **This** is what executes the measurement plan.
    broker : databroker/Tiled, optional
        Defaults to the global ``db``; used to read results back.
    measure : callable(params, **kw) -> plan, optional
        The measurement plan factory.  Defaults to :func:`measure_for_agent`.  Must return a
        *plan* (generator); the loop wraps it in ``re(...)``.
    on_step : callable(i, params, result, feedback) -> None, optional
        Side-effect hook (log a row, write a trajectory file, update a live plot).
    settle : float
        Wall-clock seconds to pause between iterations (controller-level, outside any run).
    **measure_kwargs :
        Forwarded to ``measure`` (e.g. ``apply_params=``, ``t=``, ``md=``).

    Returns
    -------
    history : list of (params, feedback)
        The full record of the campaign (also what you would persist / hand to the optimizer).

    Example
    -------
    >>> # (run at the IPython prompt, NOT inside a plan)
    >>> hist = autonomous_loop(opt.suggest, opt.analyze, max_iter=30,
    ...                        apply_params=set_reaction_conditions, t=1.0)
    """
    runengine = re if re is not None else RE                   # noqa: F821
    _measure = measure if measure is not None else measure_for_agent

    history = []
    for i in range(int(max_iter)):
        params = suggest(history)
        if params is None:
            print("autonomous_loop: suggest() returned None; stopping at iter {}.".format(i))
            break

        # --- THE sanctioned RE() call: execute ONE proper run for this suggestion ----------
        runengine(_measure(params, **measure_kwargs))
        # ----------------------------------------------------------------------------------

        # Read the result back from the broker (never re-trigger the detector for it).
        result = read_back_result(broker)
        feedback = analyze(result, params)
        history.append((params, feedback))

        if on_step is not None:
            on_step(i, params, result, feedback)
        print("autonomous_loop: iter {} params={} feedback={}".format(i, params, feedback))

        if stop is not None and stop(history):
            print("autonomous_loop: stop() satisfied at iter {}.".format(i))
            break
        if settle:
            time.sleep(settle)

    return history


# ---------------------------------------------------------------------------
# 4. Closed-loop ALIGNMENT (the slope_chase / at_beamline.auto shape)
# ---------------------------------------------------------------------------
def align_loop(analyze, *, motors, scan=None, re=None, broker=None, max_iter=15,
               tol=None, snap=None, on_step=None):
    """Closed-loop alignment: scan -> analyze image -> correct -> repeat until converged.

    Mirrors ``CDSAXS/.../slope_chase_alignment.py`` (level chi/theta so diffraction peaks are
    horizontal) and ``CDSAXS/local_ranking/at_beamline.py::auto()`` (rotation-center search):
    each iteration runs ONE proper scan run, reads it back from the broker, asks an injected
    ``analyze`` for a correction, and ``RE(bps.mv(...))`` applies it.  The decision loop is
    Python; the acquisition stays a single run.

    Parameters
    ----------
    analyze : callable(uid, broker) -> dict
        Given the just-finished run's ``uid`` (and the broker), return a dict mapping each
        motor (or its name) to a *correction* to apply, plus optionally ``"converged": True``.
        E.g. ``{"piezo_ch": -0.3}`` or ``{piezo.ch: -0.3, "converged": abs(slope) < 0.002}``.
        This is where your OpenCV / VLM image analysis lives (the LLM-discovered
        ``measure_peak_slope`` / ``find_needle_tip``).
    motors : dict
        Mapping of name -> ophyd positioner for every axis ``analyze`` may correct
        (e.g. ``{"piezo_ch": piezo.ch, "piezo_th": piezo.th}``).
    scan : callable() -> plan, optional
        The per-iteration measurement.  Default: a single
        ``bp.count([pil2M], num=1)`` (the slope-chase primitive).  For the rotation-center
        search pass a ``rel_grid_scan`` closure (see :func:`example_alignment`).
    re : RunEngine, optional
        Defaults to global ``RE``.
    broker : databroker/Tiled, optional
        Defaults to global ``db``.
    max_iter : int
        Iteration cap.
    tol : float, optional
        If given, also stop when the largest absolute correction is below ``tol`` (a generic
        convergence test in addition to ``analyze``'s own ``"converged"`` flag).
    snap : callable(name, value) -> value, optional
        Optional quantizer for setpoints (e.g. snap chi to a 0.1 deg grid in [-4, 4], as the
        verified beamline scripts do with ``snap_chi``).
    on_step : callable(i, uid, corrections) -> None, optional
        Side-effect hook (log, copy a trajectory PNG).

    Returns
    -------
    bool : whether convergence was reached.

    Notes
    -----
    Like :func:`autonomous_loop`, this is a **Python function that calls RE()**, not a plan.
    Keep it outside / above your plans.
    """
    runengine = re if re is not None else RE                   # noqa: F821
    b = broker if broker is not None else db                   # noqa: F821
    _scan = scan if scan is not None else (lambda: bp.count([pil2M], num=1))  # noqa: F821

    def _resolve(target):
        # analyze may key by name or by the motor object itself.
        if target in motors:
            return motors[target]
        return target  # assume it's already a positioner

    for i in range(int(max_iter)):
        # --- ONE proper scan run, then read it back via the broker ------------------------
        runengine(_scan())
        uid = b[-1].start["uid"] if hasattr(b[-1], "start") else -1
        corrections = analyze(uid, b)
        # ----------------------------------------------------------------------------------

        converged = bool(corrections.pop("converged", False))
        max_corr = 0.0
        mv_args = []
        for target, delta in corrections.items():
            motor = _resolve(target)
            new_val = motor.position + float(delta)
            if snap is not None:
                new_val = snap(target, new_val)
            mv_args += [motor, new_val]
            max_corr = max(max_corr, abs(float(delta)))

        if on_step is not None:
            on_step(i, uid, corrections)
        print("align_loop: iter {} corrections={} (max |Δ|={:.4f})".format(i, corrections, max_corr))

        if mv_args:
            # --- the second sanctioned RE() call: apply the correction --------------------
            runengine(bps.mv(*mv_args))

        if converged or (tol is not None and max_corr < tol):
            print("align_loop: converged at iter {}.".format(i))
            return True

    print("align_loop: reached max_iter={} without convergence.".format(max_iter))
    return False


# ---------------------------------------------------------------------------
# 5. A simple BoTorch-style ask/tell stub (no hard ML dependency)
# ---------------------------------------------------------------------------
class GridAskTell:
    """A trivial ``ask``/``tell`` optimizer over a discrete grid (BoTorch-shaped, no deps).

    Stands in for a real BoTorch / GP optimizer so the loop can be developed and tested
    (against ``DummyBluSky`` or a unit test) without an ML install.  It exposes the same two
    methods a real optimizer would, so you can swap in BoTorch later by keeping the interface:

    * :meth:`suggest` (``ask``) -> the next ``params`` dict (here: next untried grid point, or
      the best-so-far neighbourhood once the grid is exhausted);
    * :meth:`analyze` (``tell`` helper) -> records the objective for the params just measured.

    Parameters
    ----------
    space : dict of str -> sequence
        The search grid, e.g. ``{"temperature": [90, 100, 110], "flow": [60, 80, 100]}``.
    objective : callable(result, params) -> float
        Maps a broker read-back to a scalar to **maximize** (e.g. peak intensity, 1/sigma).
    iter_key : str
        Name of the auto-incremented iteration counter added to each suggestion (so the run
        records ``{agent_iter}``).  Default ``"agent_iter"``.
    """

    def __init__(self, space, objective, *, iter_key="agent_iter"):
        self.space = {k: list(v) for k, v in space.items()}
        self.objective = objective
        self.iter_key = iter_key
        self._grid = self._product(self.space)
        self._i = 0
        self.best = None  # (params, value)

    @staticmethod
    def _product(space):
        keys = list(space.keys())
        combos = [{}]
        for k in keys:
            combos = [dict(c, **{k: v}) for c in combos for v in space[k]]
        return combos

    def suggest(self, history):
        """``ask``: return the next params dict, or ``None`` when the grid is exhausted."""
        if self._i >= len(self._grid):
            return None
        params = dict(self._grid[self._i])
        params[self.iter_key] = self._i
        self._i += 1
        return params

    def analyze(self, result, params):
        """``tell`` helper: score this run and remember the best (maximization)."""
        value = float(self.objective(result, params))
        if self.best is None or value > self.best[1]:
            self.best = (dict(params), value)
        return value


def ask_tell_loop(optimizer, *, max_iter=20, stop=None, re=None, broker=None, **measure_kwargs):
    """Convenience wrapper: drive :func:`autonomous_loop` from an ``ask``/``tell`` optimizer.

    Pass anything exposing ``suggest(history)`` and ``analyze(result, params)`` (e.g.
    :class:`GridAskTell`, or your BoTorch wrapper).  Returns the history.  This is still a
    Python function (it calls :func:`autonomous_loop`, which calls ``RE``).
    """
    return autonomous_loop(optimizer.suggest, optimizer.analyze, max_iter=max_iter,
                           stop=stop, re=re, broker=broker, **measure_kwargs)


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
def example():
    """Autonomous synthesis loop over a (temperature x flow) grid, maximizing SAXS intensity.

    Demonstrates the *whole* sanctioned shape: a discrete ask/tell optimizer drives
    :func:`measure_for_agent` (ONE run per suggestion, params recorded as Signals), reading the
    peak intensity back from the broker.  Replace :class:`GridAskTell` with BoTorch and
    ``_set_conditions`` with your droplet-reactor command to get the real CFN workflow.

    **Run this at the IPython prompt (it is a controller function, NOT a plan):**

        >>> hist = technique_M_autonomous.example()

    (NOT ``RE(...)`` -- there is no plan to run here; the function calls ``RE`` internally.)
    """
    # Rig command that realizes a suggestion (stand-in: replace with the reactor's set T/flow +
    # goto reaction position).  It IS a plan (runs inside the measurement run).
    def _set_conditions(params):
        # e.g. yield from go_to_temp(params["temperature"]); yield from set_flow(params["flow"])
        yield from bps.null()                                   # noqa: F821 (placeholder)

    # Objective: maximize a SAXS ROI total read back from the broker.
    def _peak_intensity(result, params):
        try:
            return float(result["pil2M_stats1_total"].mean())
        except Exception:
            return 0.0

    opt = GridAskTell(
        space={"temperature": [90, 100, 110], "flow": [60, 80, 100]},
        objective=_peak_intensity,
    )

    hist = ask_tell_loop(
        opt, max_iter=9,
        apply_params=_set_conditions, t=1.0, geometry="transmission",
        name_base="AuNP_autosyn",
        md={"project_name": "311234_Demo", "optimizer": "grid_stub"},
    )
    print("example: best = {}".format(opt.best))
    return hist


def example_alignment():
    """Closed-loop rotation-center alignment (the ``at_beamline.auto`` shape), schematically.

    Each iteration runs ONE ``rel_grid_scan`` over a small (x, z) window x a few PRS angles,
    reads the on-axis camera stack back from Tiled, and asks an injected ``_analyze`` for the
    (x, z) correction; :func:`align_loop` applies it and repeats until ``_analyze`` reports
    convergence.  The image analysis itself (CLAHE superposition + VLM ranking, or the
    paraboloid tip-spread fit) is exactly what you drop into ``_analyze``.

    **Run at the IPython prompt** (controller function, not a plan):

        >>> technique_M_autonomous.example_alignment()
    """
    step = 200  # microns

    # One small raster per iteration: prs outermost (slow), then x, z (the at_beamline shape).
    def _scan():
        return bp.rel_grid_scan(                                # noqa: F821
            [OAV_writing, piezo, prs],                         # noqa: F821
            prs, -60, 60, 5,                                   # noqa: F821 (slow axis outermost)
            piezo.x, -step, step, 3,                           # noqa: F821
            piezo.z, -step, step, 3,                           # noqa: F821
            snake_axes=True)

    # Your image analysis: pull OAV_writing_image from the broker for `uid`, build the
    # superimposed/enhanced images, rank or fit, and return the (x, z) move toward the best.
    def _analyze(uid, broker):
        # imgs = broker[uid]['primary']['data']['OAV_writing_image'].read()
        # ... CLAHE superpose + VLM rank (local_ranking) or paraboloid tip-spread fit ...
        dx, dz = 0.0, 0.0          # <- replace with the computed correction (microns)
        converged = True           # <- replace with your convergence test (best repeats 3x)
        return {"piezo_x": dx, "piezo_z": dz, "converged": converged}

    return align_loop(
        _analyze,
        motors={"piezo_x": piezo.x, "piezo_z": piezo.z},      # noqa: F821
        scan=_scan, max_iter=15)

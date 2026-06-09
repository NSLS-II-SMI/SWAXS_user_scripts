"""
smi_plans
=========

Modern, modular, GUI-ready Bluesky data-acquisition templates for the NSLS-II SMI-SWAXS
beamline.

This package is the *target* style for SMI user scripts.  It is organized so that the
reusable parts (sample model, preprocessors, run-shaping primitives) are separate from the
per-technique plan files, and so that a GUI could eventually import the same building blocks.

Layout
------
* ``_samples``       -- :class:`Sample` / :class:`SampleList` (pure Python; GUI-safe).
* ``_preprocessors`` -- opt-in plan-mutating decorators (fresh-spot, ensure-in, beam-loss
  re-seek, baseline, cleanup, extra-dets).
* ``_core``          -- run-shaping primitives (one-sample run, multi-open-run interleave,
  sample positioning, detector selection, filename tokens).
* ``technique_*``    -- one file per use-case archetype (A-O); each provides clean, composable
  plan functions plus a runnable example.

Authoring rules (the short version)
-----------------------------------
1. ONE run per logical sample (or interleaved runs via :func:`_core.multi_sample_run`).
2. Record context as devices/Signals in the stream (or baseline if constant); never bake it
   into the filename with ``.get()``.
3. Build the filename from recorded fields with :func:`_core.fname` (``{device_field}``).
4. Pass intent via ``md={}``; never use ``sample_id``/``RE.md`` mutation.
5. Plans are generators end-to-end; never call ``RE()`` inside a plan, never ``cam.put`` to
   trigger.
6. Keep the physics idioms via the ``_preprocessors`` wrappers.
7. Keep sample tables out of plan bodies -- use :class:`SampleList`.

.. important::
    The technique files and ``_core``/``_preprocessors`` reference beamline globals injected
    by the SMI profile collection at runtime (``bps``, ``bpp``, ``Signal``, ``np``, ``piezo``,
    ``stage``, ``waxs``, ``prs``, ``energy``, ``pil2M``, ``pil900KW``, ``xbpm2/3``,
    ``det_exposure_time``, alignment routines ...).  They are meant to be ``%run`` / imported
    inside the live beamline IPython session.  ``_samples`` is pure Python and importable
    anywhere.
"""

from ._samples import Sample, SampleList  # noqa: F401  (pure python, always safe)

# The device-dependent modules import bluesky lazily; importing the package outside the
# beamline env should still expose the sample model without exploding.
try:  # pragma: no cover
    from . import _preprocessors, _core, _compose  # noqa: F401
except Exception:  # pragma: no cover
    _preprocessors = None
    _core = None
    _compose = None

__all__ = ["Sample", "SampleList", "_preprocessors", "_core", "_compose"]

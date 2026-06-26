"""
holder_bar.py -- COMPATIBILITY SHIM (the implementation now lives in the smi_plans backend).

The holder-bar loader, alignment persistence, and Position-aware movement that used to live here
have been promoted into ``smi_plans`` (``_holder.py`` + ``_core.goto_sample``).  This file remains
only so existing ``from holder_bar import ...`` lines keep working; new code should import from
``smi_plans`` directly:

    from smi_plans import (load_holder, get_aligned, is_aligned, needs_alignment,
                           save_aligned, clear_aligned, sample_center)
    from smi_plans._core import goto_sample, position_moves

Name changes (old -> new):
    load_holder_bar  -> load_holder
    goto_runnable    -> goto_sample        (reads the runnable nominal/refined Position)
    position_moves(pos)  -> position_moves(pos, piezo_dev, stage_dev)   (explicit devices)

Requires a CURRENT ``smi_plans`` install (the one that provides ``load_holder``); deploy the updated
smi-plans into the beamline env before using this.
"""

from smi_plans import (  # noqa: F401
    HolderBar,
    load_holder,
    get_aligned,
    is_aligned,
    needs_alignment,
    save_aligned,
    clear_aligned,
    sample_center,
)
from smi_plans._core import goto_sample, position_moves  # noqa: F401


# -- back-compat aliases for the old names --------------------------------------------------
load_holder_bar = load_holder    #: deprecated name for :func:`smi_plans.load_holder`
goto_runnable = goto_sample      #: deprecated name for :func:`smi_plans._core.goto_sample`


__all__ = [
    "HolderBar",
    "load_holder", "load_holder_bar",
    "get_aligned", "is_aligned", "needs_alignment",
    "save_aligned", "clear_aligned",
    "sample_center",
    "goto_sample", "goto_runnable",
    "position_moves",
]

"""HISTORICAL AD HOC RESTART — specific to scan 1170553 and its recorded holder state.

Load the continuation in Bluesky, then run after stage motion is recovered:

    %run -i ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/tender_resume_1170553.py
    RE(run_tender_resume_1170553())

Reloads the common plan in an isolated namespace with the live profile objects.
No acquisition occurs merely by loading this file.
"""

import runpy
from pathlib import Path

_plans = runpy.run_path(
    str(Path(__file__).with_name("hard_grazing_damage_check.py")),
    init_globals=globals().copy(),
)
run_tender_resume_1170553 = _plans["run_tender_resume_1170553"]
print("Continuation: In2O3_c8x → In2O3_c8x_2 → BlankSi_3p7keV → In2O3_sparse_leftc4x")
print("Fresh alignment for each; angles 0.3/0.4/0.5/0.6; harmonic 3; attenuation factor 1")
print("Run after stage motion is recovered: RE(run_tender_resume_1170553())")

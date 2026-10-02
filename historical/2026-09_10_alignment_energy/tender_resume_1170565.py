"""HISTORICAL AD HOC RESTART — specific to scan 1170565 and its recorded holder state.

Continue the three remaining Tender positions after the alignment interruption.

After loading the corrected alignment routine into the Bluesky session:
    %run -i ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/tender_resume_1170565.py
    RE(run_tender_resume_1170565())

Loading does not move hardware or start acquisition.
"""

import runpy
from pathlib import Path

_plans = runpy.run_path(
    str(Path(__file__).with_name("hard_grazing_damage_check.py")),
    init_globals=globals().copy(),
)
run_tender_resume_1170565 = _plans["run_tender_resume_1170565"]
print("Continuation: In2O3_c8x_2 → BlankSi_3p7keV → In2O3_sparse_leftc4x")
print("Fresh alignment; angles 0.3/0.4/0.5/0.6; harmonic 3; attenuation factor 1")
print("Run: RE(run_tender_resume_1170565())")

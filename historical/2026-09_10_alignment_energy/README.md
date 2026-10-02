# Historical ad hoc alignment and energy plans — September/October 2026

**Status: historical beamtime recipes, not generic plans or maintained templates.**
These files were moved from the `smi-plans` working tree on 2026-10-02. They were
previously untracked scripts in `docs/`; the reusable behavior extracted from them
is now documented in [smi-plans grazing workflows](https://github.com/EliotGann/smi-plans/blob/master/docs/GRAZING_WORKFLOWS.md).

The plans preserve beamtime-specific holder names, sample IDs, scan IDs, positions,
alignment helpers, harmonic/foil settings and restart defaults. Numbered recovery
scripts refer to the original runs, not the latest scan. Some scripts read live
holders/lists on loading; list-creation scripts write shared Redis scan inputs.
Review/adapt the original setup assumptions before using any as a new experiment.

## Contents

- `hard_grazing_damage_check.py`: Hard/Tender alignment, incidence/energy acquisition,
  before/after checks, sample selections and recorded continuation.
- `holder2_multi_edge_grid.py`: five K edges, WAXS 0/20, fresh-spot grid and S5 restart.
- `saxs_nexafs_snake.py`: holder1 endpoint AGB measurements and fresh-spot NEXAFS.
- `tender_resume_1170553.py`, `tender_resume_1170565.py`: specific historical restarts.
- `prepare_hard_resume.py`, `hard_resume_1170456.json`: preparation and recorded snapshot
  for the original Hard continuation; keep the JSON beside the plan.
- `add_l3_energy_lists.py`, `add_transition_metal_energy_lists.py`: beamtime list setup.
- `examine_scan_timing.py`, `HOLDER2_TIMING_EXAMINATION.md`, `holder2_timing_*`:
  historical throughput analysis and its CSV/JSON outputs. Regeneration queries
  Tiled and overwrites the adjacent reports.
- `voltage_calibration.svg`: preserved loose calibration plot from the same working
  tree. No generating script or calibration provenance was recorded with it.
- `tests/`: the script-specific simulation tests moved with their subjects.

## Simulation tests

Install/use the `smi-plans` Pixi environment. A source checkout is required for its
shared simulated-beamline fixture. The default is sibling `~/smi-plans`; override
with `SMI_PLANS_CHECKOUT` when the repositories are elsewhere. From that checkout:

```bash
pixi run python -m pytest -q ../SWAXS_user_scripts/historical/2026-09_10_alignment_energy/tests
```

The tests mock holder/list stores and use simulated devices. The optional
harmonic-lock integration cases skip if the local profile collection's wrapper is
absent. Scripts with live setup side effects are not executed by test collection.

## Future scripts

Create new user-requested ad hoc plans in this repository's appropriate user-group,
date/purpose directory, not in `smi-plans/docs/` and not in this historical archive.
Use public library APIs where possible. See the root README and `AGENTS.md`.

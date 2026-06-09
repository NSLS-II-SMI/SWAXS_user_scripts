# smi-plans has moved

The `smi_plans` composable-acquisition package that used to live here
(`templates/smi_plans/`) has been promoted to its own standalone, pip-installable
repository:

    ~/get/smi/smi-plans/        (package at src/smi_plans/, `pip install -e .`)

Why: it outgrew "a templates folder" — it is a reusable library (composition layer,
preset recipes, a simulated-device test suite, and skills) that other code and an
eventual GUI should `import smi_plans` properly rather than via `sys.path` into this
repo.

## What stayed in SWAXS_user_scripts

The **survey and design rationale** remain here, because they are an analysis of *this*
repo's ~230 legacy scripts and will back a future pass that annotates each legacy
function with its `smi_plans` equivalent:

- `templates/_analysis/USE_CASE_TAXONOMY.md`
- `templates/_analysis/BEST_PRACTICES_DRAFT.md`
- `templates/_analysis/legacy_batch_*.md`, `folder_*.md`

The same legacy-pattern knowledge is mirrored in the new repo at
`~/get/smi/smi-plans/skills/legacy-swaxs-patterns.md` (the mapping legacy pattern →
smi-plans), so the annotation work can be driven from there.

## Using it

```python
# once, off-beamline or in the env:
#   cd ~/get/smi/smi-plans && pip install -e .
import smi_plans
from smi_plans._compose import acquire, energy_axis, temperature_axis, incidence_axis, motor_axis
```

See the new repo's `README.md`, `docs/PACKAGE_OVERVIEW.md`, and `skills/`.

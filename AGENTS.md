# User-script repository

- Create user-requested ad hoc experiment, beamtime, setup and recovery scripts
  here, rather than in `smi-plans/docs/` or the profile collection.
- Follow the README's user-group folders and date/purpose naming. Put related
  script tests, recovery snapshots and generated reports alongside the scripts.
- Use the installed `smi_plans` APIs for reusable behavior; develop shared library
  functionality and its tests in the sibling `smi-plans` repository.
- `historical/` contains archived beamtime-specific recipes. Label historical
  scripts and document their original assumptions; do not treat numbered restart
  scripts, stored positions or sample IDs as current generic defaults.
- `templates/` is for maintained common-measurement examples.
- The dated archive README documents how to run its simulation tests. Do not
  execute beamline/setup scripts merely to test their imports: some access live
  holders or write shared scan-input lists.

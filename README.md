# SWAXS_user_scripts 
This is the home of all custom user scripts for the NSLS-II SMI-SWAXS beamline.  Historical naming conventions were to have files with the form `30-lastname.py`.  
We have moved all of these old files to the `legacy/` directory. 

Now that this is a separate repo from the profile collection, we encourage each user group to create a folder of the form 

```PIlastname-Institusion/```

for example "Doe-NSA". 
Within this directory, you are free to use whatever naming scheme you choose, although a suggestion of the date and purpose of the scripts within are encouraged, i.e. `grazing_2025-2.py`.

within "templates" the beamline staff will keep up to date example scripts for common measurements.

## Script ownership

New ad hoc plans requested by users (including agent-generated scripts), beamtime
setup scripts and numbered recovery scripts belong here. Use the user-group and
date/purpose conventions above; keep script-specific tests and artifacts together.
Reusable APIs and their documentation belong in
[smi-plans](https://github.com/EliotGann/smi-plans), rather than copying library code.

`historical/` holds explicitly archived beamtime recipes. The
[September/October 2026 alignment/energy archive](historical/2026-09_10_alignment_energy/README.md)
was relocated from the smi-plans working tree on 2026-10-02, including its restart
snapshots, timing outputs and simulation tests. It is historical material, not a
maintained template or a statement of current beamline setup.

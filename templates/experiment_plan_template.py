# Template for separating input selection from main experiment plan

def get_experiment_inputs():
    """
    Collect or define all necessary inputs for the experiment here.
    Replace the example values with your actual input logic or defaults.
    """
    names = ["Sample1", "Sample2"]
    x_piezo = [1000, 2000]
    y_piezo = [3000, 4000]
    z_piezo = [0, 0]
    waxs_arc = [7]
    ai0_all = 0
    ai_list = [1.6, 3.2]
    x_step = 30
    # Add other parameters as needed
    return names, x_piezo, y_piezo, z_piezo, waxs_arc, ai0_all, ai_list, x_step


def main_experiment_plan(names, x_piezo, y_piezo, z_piezo, waxs_arc, ai0_all, ai_list, x_step):
    """
    Main experiment plan logic goes here. This function should use the inputs provided.
    Replace the example logic with your actual experiment steps.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: this is a skeleton/template — right now it just prints the inputs.
    #   The inputs it expects (a list of sample names + piezo x/y/z, a WAXS-arc list, a
    #   starting incidence angle 'ai0_all', a list of incidence angles 'ai_list', and an
    #   x-step) are the classic ingredients of a grazing-incidence (GISAXS/GIWAXS) bar scan.
    #
    # 💡 NEWER, EASIER WAY: instead of hand-writing the loops that move to each sample,
    #   align it, step the incidence angle, and step the WAXS arc, the beamline now has a
    #   helper library 'smi_plans' with a ready-made grazing-incidence bar runner. It also
    #   records angle/energy/beam readings INTO the data and builds the file names for you.
    #   A complete starting point that mirrors these same inputs:
    #
    #     from smi_plans import SampleList, giwaxs_bar   # do this once at the top of your session
    #     bar = SampleList.from_columns(                 # your sample table, by column
    #         names=names, piezo_x=x_piezo, piezo_y=y_piezo, piezo_z=z_piezo,
    #     )
    #     yield from giwaxs_bar(
    #         bar,
    #         align=alignement_gisaxs,        # your existing alignment routine
    #         align_angle=0.1,
    #         waxs_arc=tuple(waxs_arc),       # e.g. (7,)
    #         t=1.0,                          # exposure time
    #         incident_angles=ai_list,        # e.g. [1.6, 3.2]
    #     )
    #     # (If you'd rather drive one sample at a time, use giwaxs_run(name, th0=..., incident_angles=...).)
    #
    #   (This is just a tidier template to start from — nothing here is broken, since the
    #    body is only example prints.)
    # === end smi_plans note ================================================
    # ...existing main plan logic...
    print("Running experiment with:")
    print(f"Names: {names}")
    print(f"X Piezo: {x_piezo}")
    print(f"Y Piezo: {y_piezo}")
    print(f"Z Piezo: {z_piezo}")
    print(f"WAXS Arc: {waxs_arc}")
    print(f"ai0_all: {ai0_all}")
    print(f"ai_list: {ai_list}")
    print(f"x_step: {x_step}")
    # ...
    # Insert your experiment logic here
    pass


if __name__ == "__main__":
    inputs = get_experiment_inputs()
    main_experiment_plan(*inputs)

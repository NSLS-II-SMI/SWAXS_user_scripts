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

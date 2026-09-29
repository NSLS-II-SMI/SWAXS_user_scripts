

'''
for acquisition

Bluesky call: stepped voltage program
RE(P_sorensen_voltage_program_run(
    "sample1_voltage_program",                        # name of the bluesky scan type
    voltages=  [0.8, 1.0, 1.2, 1.385, 1.2, 1.0, 0.8], # Imput voltages in Volts - change as needed
    hold_times=[4  ,   4,   4,    20,   4,   4,   4], # seconds  - should be the same length as voltages
    frame_period=2.0,                                 # how often to take images (seconds)
    exposure_time=1.0,                                # exposure time (seconds)
    detector="saxs",                                  # or "waxs" / "saxs_waxs"
    baseline_image=True,                              # take a baseline image before starting the voltage program (with supply off)
    md={"experiment": "voltage_response"},            # add some metadata for searching and organizing your data
))








for analysis settings that work for AGB are:

reduce_smi_combined(uid='1430d096-e580-4216-a439-e2dc46e4933f', tiled_uri='https://tiled.nsls2.bnl.gov', catalog='smi/migration', solid_angle_correction=True, geometry='transmission', saxs_mask_path='/home/xf12id/saxs9p3m.json', waxs_mask_path=None, cache_geometry=False, image_cache_path='/tmp/smi_browser_cache/1430d096-e580-4216-a439-e2dc46e4933f.h5', n_q=3000, saxs_beam_delta_px=(2.647765810145157, 0.532973293850348), waxs_beam_delta_px=(0.5506777818757322, -3.2518613652412176), saxs_distance_delta_mm=-73.75086283003458, waxs_beam_col_per_arc_deg=-0.16, pixel_splitting=3)


'''
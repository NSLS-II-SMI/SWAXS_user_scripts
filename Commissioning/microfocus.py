def microfocus_scan(x0=0, y0=0):
    '''
    move to the top and side edge, do a transmission scan with the nanopositioner using the saxs detector and return the x and y size
    '''
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: (this one is just a stub — the idea is to find a sample's beam
    #   edges by scanning the tiny nanopositioner across the beam in transmission and
    #   reading the SAXS detector, to measure the focused beam/sample size in x and y.)
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', with
    #   ready-made "mapping" scans that raster a motor (like piezo.x / piezo.y) and take
    #   a measurement at each point, writing the positions and beam readings straight into
    #   the saved data. A line scan in x, then one in y, would look like:
    #
    #     from smi_plans import map_line_run        # do this once at the top of your session
    #     yield from map_line_run("microfocus_x", piezo.x, -1500, 1500, 61,
    #                             dets=[pil2M, pin_diode])   # horizontal cut
    #     yield from map_line_run("microfocus_y", piezo.y, -1500, 1500, 61,
    #                             dets=[pil2M, pin_diode])   # vertical cut
    #
    #   (For a full 2-D raster instead, see map_grid_run. This is just a suggestion —
    #    there's no acquisition code here yet to break.)
    # === end smi_plans note ================================================
    
def atten_move_in():
    """
    Move 4x + 2x Sn 60 um attenuators in
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: pushes two attenuator foils (att1_7, att1_6) into the beam,
    #   waiting until each reports "Open", to cut the beam down for a transmission
    #   measurement. The attenuators are unchanged and still work this way.
    #   In smi_plans, transmission measurements (transmission_run / transmission_bar)
    #   handle the attenuator dance for you. (Nothing here is broken.)
    # === end smi_plans note ================================================
    print('Moving attenuators in')

    while att1_7.status.get() != 'Open':
        yield from bps.mv(att1_7.open_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Open':
        yield from bps.mv(att1_6.open_cmd, 1)
        yield from bps.sleep(1)

def atten_move_out():
    """
    Move 4x + 2x Sn 60 um attenuators out
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: pulls those same two attenuator foils back out of the beam.
    #   Unchanged behavior; smi_plans' transmission presets manage this for you.
    #   (Nothing here is broken.)
    # === end smi_plans note ================================================
    print('Moving attenuators out')
    while att1_7.status.get() != 'Not Open':
        yield from bps.mv(att1_7.close_cmd, 1)
        yield from bps.sleep(1)
    while att1_6.status.get() != 'Not Open':
        yield from bps.mv(att1_6.close_cmd, 1)
        yield from bps.sleep(1)


def run_swaxs_Liu_2023_2(t=2):
    """
    Take WAXS and SAXS as linescans across capillaries
    Take transmission using attenuators

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: walks across a row of capillaries (a few y points each), takes
    #   WAXS + SAXS at each, and once per WAXS angle measures the beam TRANSMISSION by
    #   inserting attenuators + the beamstop and comparing counts to an empty/direct shot.
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a transmission preset that does the
    #   direct-beam reference, attenuator insert/remove, and per-sample transmission for
    #   a whole bar of capillaries, recording the transmission ratio INTO the data (so
    #   you don't compute it from db[-1] and stuff it into the file name by hand):
    #
    #     from smi_plans import transmission_bar, transmission_dets
    #     # describe your samples (names + piezo_x) and let transmission_bar handle the
    #     # direct-beam + attenuator + beamstop sequence; see transmission_run for one sample.
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_pd' (the beamstop stage) was renamed, and
    #   'det_exposure_time(...)' is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names =   [ 'n-1',' n-6',   'B-A',  'B-B',   'B-C',  'B-D',  'B-E',  'B-F',  'B-L',  'z-42-2',]
    piezo_x = [  48950, 42850,  36300,  30150,   23800,  17350,  11200,   4450,  -1700,  -8000,]
    piezo_y = [  -3600, -3600,  -3600,  -3600,   -3600,  -3600,  -3600,  -3600,  -3600,  -3600, ]
    #hexa_y =  [      0,     0,      0,      0,      0,      0,      0,      0,      0,      0, ]  #in mm
    #points =  [      3,     3,      3,      3,      3,      3,      3,      3,      3,      3,       3,      3,      3,     3,     3,]
    hexa_y =  [ 0 for n in names]
    points =  [ 3 for n in names]

    dy = 100
    waxs_arc = [20, 0]

    beamstop = pil2M_bs_pd  # ⚠️ FIXME(smi_plans): 'pil2M_bs_pd' (the SAXS beamstop stage) was renamed (it would error). The beamstop now lives under 'pil2M.beamstop' — e.g. its rod is 'pil2M.beamstop.x_rod', and there are helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop(). Point 'beamstop' at the new pil2M.beamstop axis.
    bs_pos_x = -202.5
    transmission_exposure = 1.0
    dx = 1500
    user = "TB"

    dbeam_x = 46000
    dbeam_y = -4000
    stats1_direct = 1


    # Check if the length of xlocs, ylocs and names are the same
    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        condition = ( 19 < waxs.arc.position ) and ( waxs.arc.position < 21 )

        if condition:
            yield from atten_move_in()
            yield from bps.mv(beamstop.x, bs_pos_x + 5,
                              piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_name = f'empty_-attn-direct'
            sample_id(user_name='test', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(beamstop.x, bs_pos_x)
            yield from atten_move_out()

        for name, x, y, hy, pts in zip(names, piezo_x, piezo_y, hexa_y, points):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)
            
            # Take sample camera image
            if wa == waxs_arc[0]:
                sample_name = f'{name}{get_scan_md()}_loc0'
                yield from bp.count([OAV_writing])
            
            for i, pt in enumerate(range(pts)):

                yield from bps.mv(piezo.y, y + i * dy)

                if ( condition and i == 0 ):

                    # Take transmission
                    det_exposure_time(transmission_exposure, transmission_exposure)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(transmission_exposure, transmission_exposure)  inside a plan, or  RE(...) at the prompt. (smi_plans' transmission presets set exposure via t=.)
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(beamstop.x, bs_pos_x + 5)
                    sample_name = f'{name}-attn-sample'
                    sample_id(user_name='test', sample_name=sample_name)
                    yield from bp.count([pil2M])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): same issue — this is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt.
                    yield from bps.mv(beamstop.x, bs_pos_x)
                    yield from atten_move_out()
                else:
                    trans = 0

                # Take normal scans
                yield from bps.mv(piezo.x, x)
                sample_name = f'{name}{get_scan_md()}_loc{pt}_trs{trans}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def run_swaxs_Liu_2023_3(t=2):
    """
    Take WAXS and SAXS as linescans across capillaries
    Take transmission using attenuators

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same idea as run_swaxs_Liu_2023_2 — line-scans a row of
    #   capillaries in WAXS + SAXS and measures beam transmission once per WAXS angle
    #   using attenuators + the beamstop, comparing to a direct-beam shot.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' transmission preset does the direct-beam
    #   reference + attenuator/beamstop sequence + per-sample transmission for a whole
    #   bar, and records the transmission ratio INTO the data for you:
    #
    #     from smi_plans import transmission_bar, transmission_dets
    #     # see transmission_run for a single sample.
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_pd' was renamed, and 'det_exposure_time(...)'
    #   is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names =   [  'Z48',  'Z49',  'Z50',  ]
    piezo_x = [ -43150, -36600, -30100,  ] 
    
    piezo_y = [ 0 for n in names]
    hexa_y =  [ 0 for n in names]
    points =  [ 3 for n in names]

    dy = 100
    waxs_arc = [20, 0]

    beamstop = pil2M_bs_pd  # ⚠️ FIXME(smi_plans): 'pil2M_bs_pd' (the SAXS beamstop stage) was renamed (it would error). The beamstop now lives under 'pil2M.beamstop' — its rod is 'pil2M.beamstop.x_rod', with helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop(). Point 'beamstop' at the new pil2M.beamstop axis.
    bs_pos_x = -201.5
    user = 'PW'

    dbeam_x = -41400
    dbeam_y = 400
    stats1_direct = 1

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' transmission presets set exposure via t=.)


    # Check if the length of xlocs, ylocs and names are the same
    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        condition = ( 19 < waxs.arc.position ) and ( waxs.arc.position < 21 )

        if condition:
            yield from atten_move_in()
            yield from bps.mv(beamstop.x, bs_pos_x + 5,
                              piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_name = f'empty_-attn-direct'
            sample_id(user_name='test', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(beamstop.x, bs_pos_x)
            yield from atten_move_out()


        for name, x, y, hy, pts in zip(names, piezo_x, piezo_y, hexa_y, points):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)
            
            # Take sample camera image
            if wa == waxs_arc[0]:
                sample_name = f'{name}{get_scan_md()}_loc0'
                sample_id(user_name=user, sample_name=sample_name)
                yield from bp.count([OAV_writing])
            
            for i in range(pts):

                yield from bps.mv(piezo.y, y + i * dy)

                if ( condition and i == 0 ):

                    # Take transmission
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(beamstop.x, bs_pos_x + 5)
                    sample_name = f'{name}-attn-sample'
                    sample_id(user_name='test', sample_name=sample_name)
                    yield from bp.count([pil2M])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(beamstop.x, bs_pos_x)
                    yield from atten_move_out()
                
                if not condition:
                    trans = 0

                # Take normal scans
                yield from bps.mv(piezo.x, x)
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def run_swaxs_Liu_2024_1(t=2):
    """
    Take WAXS and SAXS as linescans across capillaries
    Take transmission using attenuators

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same transmission line-scan as the 2023 versions — for a row of
    #   capillaries, takes WAXS + SAXS at a few y points and measures beam transmission
    #   once per WAXS angle with attenuators + the beamstop vs a direct-beam shot.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' transmission preset handles the direct-beam
    #   reference, attenuator/beamstop sequence, and per-sample transmission across a
    #   whole bar, recording the transmission ratio INTO the data:
    #
    #     from smi_plans import transmission_bar, transmission_dets   # transmission_run = one sample
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_pd' was renamed, and 'det_exposure_time(...)'
    #   is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    names =   [  'M03',  'J35',  'J34',  'J33',  'J30',  'J31',  'J29',  'J28',  'J27', ]#  'J09',  'J10',  'J11',  'M01',  'JM02', ]
    piezo_x = [ -44700, -38500, -32100, -25800, -19700, -12900,  -6300,   -500,   6100, ]# 12500,  19000,  25100,  31300,  37900, ] 
    
    piezo_y = [ 2500 for n in names]
    hexa_y =  [ 0 for n in names]
    points =  [ 3 for n in names]

    dy = 100
    waxs_arc = [20, 0]

    beamstop = pil2M_bs_pd  # ⚠️ FIXME(smi_plans): 'pil2M_bs_pd' (the SAXS beamstop stage) was renamed (it would error). The beamstop now lives under 'pil2M.beamstop' — its rod is 'pil2M.beamstop.x_rod', with helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop(). Point 'beamstop' at the new pil2M.beamstop axis.
    bs_pos_x = -201.5
    user = 'PW'

    dbeam_x = -41400
    dbeam_y = 2500
    stats1_direct = 1

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' transmission presets set exposure via t=.)


    # Check if the length of xlocs, ylocs and names are the same
    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        condition = ( 19 < waxs.arc.position ) and ( waxs.arc.position < 21 )

        if condition:
            yield from atten_move_in()
            yield from bps.mv(beamstop.x, bs_pos_x + 5,
                              piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_name = f'empty-attn-direct'
            sample_id(user_name='test', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(beamstop.x, bs_pos_x)
            yield from atten_move_out()


        for name, x, y, hy, pts in zip(names, piezo_x, piezo_y, hexa_y, points):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)
            
            # Take sample camera image
            if wa == waxs_arc[0]:
                sample_name = f'{name}{get_scan_md()}_loc0'
                sample_id(user_name=user, sample_name=sample_name)
                yield from bp.count([OAV_writing])
            
            for i in range(pts):

                yield from bps.mv(piezo.y, y + i * dy)

                if ( condition and i == 0 ):

                    # Take transmission
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(beamstop.x, bs_pos_x + 5)
                    sample_name = f'{name}-attn-sample'
                    sample_id(user_name='test', sample_name=sample_name)
                    yield from bp.count([pil2M])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(beamstop.x, bs_pos_x)
                    yield from atten_move_out()
                
                if not condition:
                    trans = 0

                # Take normal scans
                yield from bps.mv(piezo.x, x)
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    yield from bps.mv(waxs, waxs_arc[0],
                      piezo.y, piezo_y[0],
                      piezo.x, piezo_x[0],
                      )
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.


def run_swaxs_Liu_2024_2(t=2):
    """
    Take WAXS and SAXS as linescans across capillaries
    Take transmission using attenuators

    """

    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: same transmission line-scan pattern again (here an AgBh
    #   calibrant + a vacuum background) — WAXS + SAXS across a few y points with a
    #   per-WAXS-angle transmission measurement using attenuators + the beamstop.
    #
    # 💡 NEWER, EASIER WAY: smi_plans' transmission preset does the direct-beam +
    #   attenuator/beamstop sequence and per-sample transmission for a whole bar,
    #   recording the transmission ratio INTO the data. (AgBh calibration also has a
    #   dedicated helper, agbh_calibration_run, if you want to formalize that step.)
    #
    #     from smi_plans import transmission_bar, transmission_dets   # transmission_run = one sample
    #
    #   (Optional. Your loop still works EXCEPT for the ⚠️ lines below.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: 'pil2M_bs_pd' was renamed, and 'det_exposure_time(...)'
    #   is now a plan — see the ⚠️ notes on those lines.
    # === end smi_plans note ================================================

    #names =   [  'J15',  'J14',  'J13',  'J12',  'J11',  'J10',  'J09',  'J08A',  'J07',  'J06',  'J05',  'J04',  'J03',  'J02',  'J01', ]
    #piezo_x = [ -43400, -37000, -30400, -24400, -17800, -11800,  -5100,   1100,   7500,  13800,  20000,  26500,  32700,  39000,  45500, ] 

    names =   [  'AgBh', 'vac-bkg',]
    piezo_x = [  -43600,    -19600,]

    piezo_y = [ 5500 for n in names]
    hexa_y =  [ 0 for n in names]
    points =  [ 3 for n in names]

    dy = 100
    waxs_arc = [20, 0]

    beamstop = pil2M_bs_pd  # ⚠️ FIXME(smi_plans): 'pil2M_bs_pd' (the SAXS beamstop stage) was renamed (it would error). The beamstop now lives under 'pil2M.beamstop' — its rod is 'pil2M.beamstop.x_rod', with helpers  yield from pil2M.insert_beamstop('rod')  /  yield from pil2M.restore_beamstop(). Point 'beamstop' at the new pil2M.beamstop axis.
    bs_pos_x = -200.8
    user = 'PW'

    dbeam_x = -19000
    dbeam_y = 5500
    stats1_direct = 1

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Use  yield from det_exposure_time(t, t)  inside a plan, or  RE(det_exposure_time(t, t))  at the prompt. (smi_plans' transmission presets set exposure via t=.)


    msg = "Wrong number of coordinates, check names, piezos, and hexas"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(hexa_y), msg

    for wa in waxs_arc:
        yield from bps.mv(waxs, wa)
        dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]

        condition = ( 19 < waxs.arc.position ) and ( waxs.arc.position < 21 )

        if condition:
            yield from atten_move_in()
            yield from bps.mv(beamstop.x, bs_pos_x + 5,
                              piezo.x, dbeam_x,
                              piezo.y, dbeam_y)

            sample_name = f'empty-attn-direct'
            sample_id(user_name='test', sample_name=sample_name)
            print(f"\n\n\n\t=== Sample: {sample_name} ===")
            yield from bp.count([pil2M])
            stats1_direct = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]
            yield from bps.mv(beamstop.x, bs_pos_x)
            yield from atten_move_out()


        for name, x, y, hy, pts in zip(names, piezo_x, piezo_y, hexa_y, points):
            yield from bps.mv(piezo.y, y,
                              piezo.x, x,
                              stage.y, hy)
            
            # Take sample camera image
            if wa == waxs_arc[0]:
                sample_name = f'{name}{get_scan_md()}_loc0'
                sample_id(user_name=user, sample_name=sample_name)
                yield from bp.count([OAV_writing])
            
            for i in range(pts):

                yield from bps.mv(piezo.y, y + i * dy)

                if ( condition and i == 0 ):

                    # Take transmission
                    yield from atten_move_in()

                    # Sample
                    yield from bps.mv(beamstop.x, bs_pos_x + 5)
                    sample_name = f'{name}-attn-sample'
                    sample_id(user_name='test', sample_name=sample_name)
                    yield from bp.count([pil2M])
                    stats1_sample = db[-1].table(stream_name='primary')['pil2M_stats1_total'].values[0]

                    # Transmission
                    trans = np.round( stats1_sample / stats1_direct, 5)

                    # Revert configuraton
                    yield from bps.mv(beamstop.x, bs_pos_x)
                    yield from atten_move_out()
                
                if not condition:
                    trans = 0

                # Take normal scans
                yield from bps.mv(piezo.x, x)
                sample_name = f'{name}{get_scan_md()}_loc{i}_trs{trans}'
                sample_id(user_name=user, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)

    yield from bps.mv(waxs, waxs_arc[0],
                      piezo.y, piezo_y[0],
                      piezo.x, piezo_x[0],
                      )
    sample_id(user_name="test", sample_name="test")
    det_exposure_time(0.3, 0.3)  # ⚠️ FIXME(smi_plans): same as above — this exposure reset is now a "plan" and does nothing called plain. Use  yield from det_exposure_time(0.3, 0.3)  inside a plan, or  RE(det_exposure_time(0.3, 0.3))  at the prompt.
# Refactored experiment plan template for Fakhraai grazing experiment

def get_fakhraai_inputs():
    """
    Returns a test set of data for the experiment.
    Replace these with real input selection logic as needed.
    """
    names = ['20240620-245nm-O-Tcom15-minus9C-b1134-85C', '20240620-245nm-O-Tcom15-minus9C-b1104-160C']
    piezo_x = [-54000, -43000]
    piezo_y = [-1500, -1500]
    piezo_z = [6300, 6300]
    hexa_x = [-12, -12]
    waxs_arc = [0, 2, 7]
    incident_angles = [0.10, 0.25]
    user_name = 'PL'
    t = 0.5
    return names, piezo_x, piezo_y, piezo_z, hexa_x, waxs_arc, incident_angles, user_name, t


def grazing_fakhraai_plan(names, piezo_x, piezo_y, piezo_z, hexa_x, waxs_arc, incident_angles, user_name, t):
    """
    Main experiment logic from the highlighted function.
    """
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    det_exposure_time(t, t)

    try:
        misaligned_samples = RE.md['misaligned_samples']
    except:
        misaligned_samples = []
        RE.md['misaligned_samples'] = misaligned_samples

    for name, x, y, z, hx in zip(names, piezo_x, piezo_y, piezo_z, hexa_x):
        yield from bps.mv(piezo.x, x,
                          piezo.y, y,
                          piezo.z, z,
                          stage.x, hx)
        # Align the sample
        try:
            yield from alignement_gisaxs_doblestack(0.1)
        except:
            misaligned_samples.append(name)
            RE.md['misaligned_samples'] = misaligned_samples
        # Sample flat at ai0
        ai0 = piezo.th.position
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            dets = [pil900KW] if waxs.arc.position < 15 else [pil900KW, pil2M]
            yield from bps.mv(waxs.bs_y, -3)
            for ai in incident_angles:
                yield from bps.mv(piezo.th, ai0 + ai)
                sample_name = f'{name}{get_scan_md()}_ai{ai}'
                sample_id(user_name=user_name, sample_name=sample_name)
                print(f"\n\n\n\t=== Sample: {sample_name} ===")
                yield from bp.count(dets)
        yield from bps.mv(piezo.th, ai0)
    sample_id(user_name='test', sample_name='test')
    det_exposure_time(0.5, 0.5)


if __name__ == "__main__":
    inputs = get_fakhraai_inputs()
    grazing_fakhraai_plan(*inputs)

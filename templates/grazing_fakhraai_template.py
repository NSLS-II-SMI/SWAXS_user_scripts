# Experimental plan rfactored from a template that was developed and refined for Fakhraai group by Patryk

def get_fakhraai_inputs():
    """
    Returns a test set of data for the experiment.
    Replace these with real input selection logic as needed.
    """
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: just hands back the sample list and settings (names, positions, angles,
    #   exposure) for the experiment — no beam motion happens here. Keeping the "what to
    #   measure" data separate from the "how to measure it" plan is exactly the right idea, and
    #   it's how the newer 'smi_plans' library likes to work too. Nice template!
    #
    # 💡 NEWER, EASIER WAY: smi_plans has a small data type, 'SampleList', built for this — it
    #   holds your samples + positions and can also be loaded from a CSV spreadsheet, so the
    #   bar plan just iterates it for you (and records each sample's info INTO the data):
    #
    #     from smi_plans import SampleList               # import once at session start
    #     samples = SampleList.from_columns(
    #         name=names, x=piezo_x, y=piezo_y, z=piezo_z, stage_x=hexa_x,
    #     )                                              # or: SampleList.from_csv("my_bar.csv")
    #
    #   (Nothing here is broken — this is just showing where your nicely-separated inputs would
    #    plug into the newer bar plans; see the note on grazing_fakhraai_plan below.)
    # === end smi_plans note ================================================
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
    # === smi_plans note (REVIEW 2026-06-22) ================================
    # WHAT THIS DOES: a grazing-incidence (GIWAXS) bar run — for each sample it moves into
    #   place, aligns, then for each WAXS arc angle and each incident angle takes an image;
    #   it also keeps a list of any samples that failed to align. Well structured!
    #
    # 💡 NEWER, EASIER WAY: the beamline now has a helper library, 'smi_plans', that runs a
    #   whole grazing bar from a sample list in one call. It aligns each sample, sweeps the
    #   incident angle and WAXS arc, and records the angle / position / beam intensity INTO the
    #   data and into the file name for you (so you can drop the get_scan_md() name-building):
    #
    #     from smi_plans import giwaxs_bar, SampleList    # import once at session start
    #     samples = SampleList.from_columns(name=names, x=piezo_x, y=piezo_y,
    #                                       z=piezo_z, stage_x=hexa_x)
    #     yield from giwaxs_bar(
    #         samples,
    #         incident_angles=incident_angles,           # your angles, unchanged
    #         waxs_arcs=waxs_arc,                         # your WAXS arc angles, unchanged
    #         dets=[pil900KW, pil2M], t=t,               # your detectors + exposure, unchanged
    #     )                                              # alignment is done per-sample for you
    #
    #   (This is just a tidier option to try later — your script below works as-is EXCEPT for
    #    the ⚠️ lines, which genuinely need a fix to run now.)
    #
    # ⚠️ NEEDS A FIX TO RUN NOW: the 'det_exposure_time(...)' calls no longer set the exposure
    #   unless run as a plan (⚠️ notes below). (internal: Tier 3 — inputs nicely separated.)
    # === end smi_plans note ================================================
    msg = "Wrong number of coordinates"
    assert len(piezo_x) == len(names), msg
    assert len(piezo_x) == len(piezo_y), msg
    assert len(piezo_x) == len(piezo_z), msg
    assert len(piezo_x) == len(hexa_x), msg

    det_exposure_time(t, t)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(t, t)  — or at the prompt:  RE(det_exposure_time(t, t)). (The smi_plans technique runs set exposure for you via t=.)

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
    det_exposure_time(0.5, 0.5)  # ⚠️ FIXME(smi_plans): this used to set the exposure directly; it's now a "plan", so the plain call does nothing. Inside a plan write:  yield from det_exposure_time(0.5, 0.5)  — or at the prompt:  RE(det_exposure_time(0.5, 0.5)). (The smi_plans technique runs set exposure for you via t=.)


if __name__ == "__main__":
    inputs = get_fakhraai_inputs()
    grazing_fakhraai_plan(*inputs)

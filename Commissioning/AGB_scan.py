
def AGB_scan():
    """
    this is a scan of the SAXS detector from 1.7m to 9 m at every 0.1 m, with attenuators in"""

    for zval in np.linspace(1.7, 9, 74): # every 0.1 m from 1.7m to 9m 
        zmm = zval * 1000
        yield from bp.mv(pil2M.motor.z, zmm)
        sample_name = f"AGB_scan_{get_scan_md()}"
        yield from bp.count([pil2M], num=1, md={"sample_name": sample_name})
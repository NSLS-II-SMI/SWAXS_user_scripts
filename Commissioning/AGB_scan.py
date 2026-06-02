
def AGB_scan():
    """
    this is a scan of the SAXS detector from 1.7m to 9 m at every 0.1 m, with attenuators in"""
    yield from bps.mv(att1_7, "in")
    #yield from bps.mv(att1_7.open_cmd, 1)
    for zval in np.linspace(1.7, 9, 74): # every 0.1 m from 1.7m to 9m 
        zmm = zval * 1000
        yield from bps.mv(pil2M.motor.z, zmm)
        sample_name = f"AGB_scan_{get_scan_md()}"
        yield from bp.count([pil2M], num=1, md={"sample_name": sample_name})


def AGB_scan2():
    """
    this is a scan of the SAXS detector using AGB and attenuators to find the beam center and real q range"""
    yield from bps.mv(att1_7, "in")
    pil2M.motor.x.kind = 'normal'
    pil2M.motor.y.kind = 'normal'
    pil2M.motor.z.kind = 'normal'
    pil2M.motor.kind = 'normal'
    #yield from bps.mv(att1_7.open_cmd, 1)
    sample_name = f"AGB_scan_x_y_9m"
    yield from grid_scan([pil2M],pil2M.motor.x,0,60,3,pil2M.motor.y,-10,10,3,piezo.z,-10000,10000,11,snake_axes=True,md={"sample_name": sample_name})
    sample_name = f"AGB_scan_z"
    yield from grid_scan([pil2M],pil2M.motor.z,9300,1600,78,piezo.z,-10000,10000,11,md={"sample_name": sample_name})
    sample_name = f"AGB_scan_x_y_1.6m"
    yield from grid_scan([pil2M],pil2M.motor.x,0,60,3,pil2M.motor.y,-10,10,3,piezo.z,-10000,10000,11,snake_axes=True,md={"sample_name": sample_name})
    # for zval in np.linspace(1.6, 9.3, 78): # every 0.1 m from 1.7m to 9m 
    #     zmm = zval * 1000
    #     yield from bps.mv(pil2M.motor.z, zmm)
    #     sample_name = f"AGB_scan_{get_scan_md()}"
    #     yield from bp.count([pil2M], num=1, md={"sample_name": sample_name})


def usaxs_multi():
    names = ["usaxs_5_",  "usaxs_6_", "usaxs_7_", "usaxs_8_", "usaxs_9_", "usaxs_10_", "usaxs_11_", "usaxs_12_"]
    x_piezo = [-25100.0, -19100.0,  -13500.0,  -6900.0,  -700.0,     6100.0,     12300.0,   18700.0, ]
    y_piezo = [1825.9,   1825.9,    1725.9,    1825.9,    1825.9,     1825.9,     1925.9,     1725.9]
    for x,y,name in zip(x_piezo,y_piezo,names):
        yield from bps.mv(piezo.x,x,piezo.y,y)
        yield from bp.count([pil2M],md={'sample_name' : name +'10deg_9.3m_8keV'})

    
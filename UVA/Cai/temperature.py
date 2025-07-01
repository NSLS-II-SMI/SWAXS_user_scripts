
def run_cai_temp_scan(name_base='test', t=1):
    # get starting y position
    y0 = stage.y.position
    x0 = stage.x.position
    waxs_arc = [0, 20]



    names          = ['-60','-40','-20','0','20','40','60','80','25-10','25-30']
    temperatures_c = [-60   ,-40  ,-20  ,0  ,20  ,40  ,60  ,80  ,25     ,25     ]
    ramp_rates_cpm = [25    ,10   ,10   ,10 ,10  ,10  ,10  ,10  ,25     ,5      ]
    wait_times_sec = [600   ,600  ,600  ,600,600 ,600 ,120 ,120 ,600    ,1200   ]

  

 



    det_exposure_time(t,t)
    det_exposure_time(t,t)
    # define scan run
    project_set(name_base)

    def inner(xs,name): 
        """
        Inner function to run a temperature scan at 167 y positions from -250 to 250 microns from y0
 
        0       """
        for wa in waxs_arc:
            yield from bps.mv(waxs, wa)
            if waxs.arc.position < 15:
                dets = [pil900KW, LThermal.temperature_current,stage.x,stage.y]
                RE.md['sample_name'] = f'{name_base}_{name}_y{{stage_y}}_x{{stage_x}}{get_scan_md()}'
                yield from bps.mvr(stage.y, 0.05)
            else:
                
                dets = [pil2M, pin_diode, pil900KW, LThermal.temperature_current,stage.x, stage.y]
                RE.md['sample_name'] = f'{name_base}_{name}_y{{stage_y}}_x{{stage_x}}_pd{{pin_diode_current2_mean_value}}{get_scan_md()}'
               
            # move stage to the starting x position
            yield from bps.mv(stage.x, xs)
            print(f"\n\n\n\t=== Sample: {RE.md['sample_name']} ===")
            yield from bp.rel_scan(dets, stage.x, 0, 0.40, 5)

    def ramp_to_temp(deg,ramp,name, waitsec):
        yield from bps.mv(LThermal.temperature_setpoint,deg)
        yield from bps.mv(LThermal.temperature_rate_setpoint,ramp)
        yield from bps.mv(LThermal.cmd,1)
        while np.abs(LThermal.temperature()-deg) > 0.1:
            yield from bps.sleep(20)  # wait until the temperature is 80C
            print(f'Waiting for temperature to reach {name}, current temperature: {LThermal.temperature()}C')
        # add equilibration time
        print(f'waiting for {waitsec} seconds to ensure temperature equilibration')
        yield from bps.sleep(waitsec)  
        print(f'temperature equilibration done.  reached {LThermal.temperature()}C')
    

    for name, temperature, ramprate, waitsec in zip(names,temperatures_c,ramp_rates_cpm,wait_times_sec):
        yield from bps.mvr(stage.y, 0.05)
        yield from ramp_to_temp(temperature, ramprate, name, waitsec)
        yield from inner(x0, name)

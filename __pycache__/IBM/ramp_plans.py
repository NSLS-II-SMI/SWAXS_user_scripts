# what you are doing:

def flyscan_for_resonantSAXS_2026C2(sample_name = "2026C2_52H_gisaxs",
                                    user_name = "JA",
                                    exposure_sec = 30,
                                    phi_min = -12.0,
                                    phi_max=12.0,
                                    energy_eV_list = [3700,],
                                    atten=100,
                                    ai_deg=0.5

):

    # ADD ALIGNMENT
    # 1. alignment_gisaxs() at phi = 0 deg
    # 2. set = ai
    # 3. rotate phi to 90 deg 
    # 4. alginment_gisaxs_90deg()
    # 5. set = phi 
    # 6. go back to phi = 0.0

    #alignment_gisaxs() 
    #yield from bps.mv(stage.phi,90)
    #alginment_gisaxs_90deg()
    #yield from bps.mv(stage.phi,0)
    
    yield from bps.mv(stage.th,ai_deg)


    pily0 = 0
    pily1 = 4
    for det_pos in [pily0,pily1]:
        yield from bps.mv(pil2M.motor.y,det_pos)
        
        # sample name convention: samplename_flyscan_energy0000eV_ai00deg_halfphirange00deg_
        for energy in energy_eV_list:

            name = user_name+"_"+f'{sample_name}_flyscan_pilpos{det_pos}_energy{energy}eV_ai{ai_deg}deg_halfphirange{phi_max}deg_{get_scan_md()}'
            
            yield from bps.mv(attenuation,atten)
            yield from ramp_count([pil2M],stage.phi,phi_min,phi_max,exposure=exposure_sec,period=exposure_sec, num=1,md={"sample_name":name})
    yield from bps.mv(pil2M.motor.y,pily0)
# what happened - scan_ids etc

import math

def singleshot_for_resonantSAXS_2026C2(sample_name = "2026C2_52H_gisaxs",
                                       user_name = "JA",
                                       exposure_sec = 30,
                                       ai_ref_deg = 0.5,
                                       phi_ref_deg = 2.0,
                                       energy_ref_eV = 3730,  
                                       energy_eV_list = [3700,],
                                       atten=100,
                                       phi_offset=0,
):
    """
    This function collects the single shots over the given energy 
    so ewald sphere stick to fixed (qz,qy).
    
    Set ai = ai_ref and phi = phi_ref at energy_ref

    """

    

    # # just for notes, be sure to do ALIGNMENT (this takes a LONG time (~40 minutes))
    # yield from alignment_gisaxs() 
    # yield from bps.mv(stage.phi,90)
    # yield from alginment_gisaxs_90deg()
    # yield from bps.mv(stage.phi,0)
    yield from det_exposure_time(exposure_sec,exposure_sec)

    pily0 = 0
    pily1 = 4

    for det_pos in [pily0,pily1]:
        yield from bps.mv(pil2M.motor.y,det_pos)
        for energy_eV in energy_eV_list:

            ai_deg = math.degrees(math.asin(energy_ref_eV/energy_eV *   math.sin(math.radians(ai_ref_deg)  )))

            phi_deg = math.degrees(math.asin(energy_ref_eV/energy_eV* math.cos(math.radians(ai_ref_deg))
                                / math.cos(math.radians(ai_deg)) * math.sin(math.radians(phi_ref_deg)) 
                                ))

            name = user_name+"_"+f'{sample_name}_singleshot_pilpos{det_pos}_energy{energy_eV}eV_ai{ai_deg}deg_phi{phi_deg}deg_{get_scan_md()}'

            yield from bps.mv(attenuation,atten)
            yield from bps.mv(energy,energy_eV)
            yield from bps.mv(stage.th,ai_deg,stage.phi,phi_deg+phi_offset)
            yield from bp.count([pil2M],md={'sample_name':name})
    yield from bps.mv(pil2M.motor.y,pily0)

# what happened - scan_ids etc


import math
from ophyd import Signal

from smi_plans._compose import ScanAxis, acquire, motor_axis, move_energy_fb, SPEED_SLOW


def resonant_saxs_geometry_axis(
    energy_eV_list,
    *,
    energy_ref_eV=3730,
    ai_ref_deg=0.5,
    phi_ref_deg=2.0,
    phi_offset=0,
):
    ai_sig = Signal(name="incident_angle", value=0.0)
    phi_sig = Signal(name="phi_resonant", value=0.0)
    energy_sig = Signal(name="energy_set", value=0.0)

    def _move(energy_eV):
        ai_deg = math.degrees(
            math.asin(
                energy_ref_eV / energy_eV
                * math.sin(math.radians(ai_ref_deg))
            )
        )

        phi_deg = math.degrees(
            math.asin(
                energy_ref_eV / energy_eV
                * math.cos(math.radians(ai_ref_deg))
                / math.cos(math.radians(ai_deg))
                * math.sin(math.radians(phi_ref_deg))
            )
        )

        yield from move_energy_simple(energy_eV)
        yield from bps.mv(
            stage.th, ai_deg,
            stage.phi, phi_deg + phi_offset,
            ai_sig, ai_deg,
            phi_sig, phi_deg,
            energy_sig, energy_eV,
        )

    return ScanAxis(
        "energy",
        list(energy_eV_list),
        move=_move,
        record=energy_sig,
        reads=[energy, ai_sig, phi_sig],
    )


def singleshot_for_resonantSAXS_2026C2_plan(
    sample_name="2026C2_52H_gisaxs",
    user_name="JA",
    exposure_sec=2,
    ai_ref_deg=0.45,
    phi_ref_deg=4.0,
    energy_ref_eV=3730,
    energy_eV_list=(3700,),
    atten=100,
    phi_offset=2.36,
):
    yield from det_exposure_time(exposure_sec, exposure_sec)

    atten_sig = Signal(name="attenuation_set", value=float(atten))

    def _setup():
        yield from bps.mv(
            attenuation, atten,
            atten_sig, float(atten),
        )


    axes = [
        motor_axis(
            "pil_y",
            pil2M.motor.y,
            [0, 4],
            record=True,
            speed=SPEED_SLOW,
        ),
        resonant_saxs_geometry_axis(
            energy_eV_list,
            energy_ref_eV=energy_ref_eV,
            ai_ref_deg=ai_ref_deg,
            phi_ref_deg=phi_ref_deg,
            phi_offset=phi_offset,
        ),
    ]

    yield from acquire(
        f"{user_name}_{sample_name}_singleshot",
        [pil2M],
        axes,
        reads=[energy, xbpm3, atten_sig],
        setup=_setup,
        geometry="reflection",
        scan_name="singleshot_resonant_saxs",
        name_tokens=[
            "pilpos{pil2M_motor_y}",
            "energy{energy_set}eV",
            "ai{incident_angle}deg",
            "phi{phi_resonant}deg",
            "att{attenuation_set}",
            "izero{xbpm3_sumX}",
        ],
        md={
            "sample_name_base": sample_name,
            "user_name": user_name,
            "energy_ref_eV": energy_ref_eV,
            "ai_ref_deg": ai_ref_deg,
            "phi_ref_deg": phi_ref_deg,
            "attenuation": atten,
            "phi_offset": phi_offset,
        },
    )

    yield from bps.mv(pil2M.motor.y, 0)



from smi_plans._core import ramp_count
from smi_plans._compose import move_energy_fb

def move_energy_simple(target_eV, settle=2.0):
    yield from bps.mv(energy, float(target_eV))
    if settle:
        yield from bps.sleep(settle)


def flyscan_for_resonantSAXS_2026C2_plan(
    sample_name="2026C2_52H_gisaxs",
    user_name="JA",
    exposure_sec=12,
    phi_min=-6.0,
    phi_max=6.0,
    energy_eV_list=(3700,),
    atten=100,
    ai_deg=0.5,
    phi_offset=2.36
):
    atten_sig = Signal(name="attenuation_set", value=float(atten))

    def _body():
        yield from bps.mv(stage.th, ai_deg)

        for det_pos in [0, 4]:
            yield from bps.mv(pil2M.motor.y, det_pos)

            for energy_eV in energy_eV_list:
                name = (
                    f"{user_name}_{sample_name}_flyscan_"
                    f"pilpos{det_pos}_"
                    f"energy{energy_eV}eV_"
                    f"ai{ai_deg}deg_"
                    f"phimax{phi_max}deg_"
                    f"att{atten}_"
                    f"izero{{xbpm3_sumX}}_"
                    f"exp{exposure_sec}sec_"
                    f"{get_scan_md()}"
                )

                yield from bps.mv(
                    attenuation, atten,
                    atten_sig, float(atten),
                )
                yield from move_energy_simple(energy_eV)

                yield from ramp_count(
                    [pil2M],
                    stage.phi,
                    phi_min+phi_offset,
                    phi_max+phi_offset,
                    exposure=exposure_sec,
                    period=exposure_sec,
                    num=1,
                    reads=[energy, xbpm3, atten_sig],
                    md={
                        "sample_name": name,
                        "sample_name_base": sample_name,
                        "user_name": user_name,
                        "energy_eV": energy_eV,
                        "incident_angle_deg": ai_deg,
                        "phi_min": phi_min,
                        "phi_max": phi_max,
                        "attenuation": atten,
                    },
                )

    def _cleanup():
        yield from bps.mv(pil2M.motor.y, 0)

    yield from bpp.finalize_wrapper(_body(), _cleanup())


def flyscan_for_resonantSAXS_2026C2_plan2(
    sample_name="2026C2_52H_cycle0_gisaxs",
    user_name="JA",
    exposure_sec=12,
    phi_min=-6.0,
    phi_max=6.0,
    energy_eV_list=(3700,),
    atten=100,
    ai_deg=0.45,
    phi_offset=0.34
):
    atten_sig = Signal(name="attenuation_set", value=float(atten))

    def _body():
        yield from bps.mv(stage.th, ai_deg)

        for det_pos in [4]:
            yield from bps.mv(pil2M.motor.y, det_pos)

            for energy_eV in energy_eV_list:
                name = (
                    f"{user_name}_{sample_name}_flyscan_"
                    f"pilpos{det_pos}_"
                    f"energy{energy_eV}eV_"
                    f"ai{ai_deg}deg_"
                    f"phimax{phi_max}deg_"
                    f"att{atten}_"
                    f"izero{{xbpm3_sumX}}_"
                    f"exp{exposure_sec}sec_"
                    f"{get_scan_md()}"
                )

                yield from bps.mv(
                    attenuation, atten,
                    atten_sig, float(atten),
                )
                yield from move_energy_simple(energy_eV)

                yield from ramp_count(
                    [pil2M],
                    stage.phi,
                    phi_min+phi_offset,
                    phi_max+phi_offset,
                    exposure=exposure_sec,
                    period=exposure_sec,
                    num=1,
                    reads=[energy, xbpm3, atten_sig],
                    md={
                        "sample_name": name,
                        "sample_name_base": sample_name,
                        "user_name": user_name,
                        "energy_eV": energy_eV,
                        "incident_angle_deg": ai_deg,
                        "phi_min": phi_min,
                        "phi_max": phi_max,
                        "attenuation": atten,
                    },
                )

    def _cleanup():
        yield from bps.mv(pil2M.motor.y, 0)

    yield from bpp.finalize_wrapper(_body(), _cleanup())

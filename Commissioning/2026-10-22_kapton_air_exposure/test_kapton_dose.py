"""Independent dimensional and conservation checks of the dose calculation.
SPDX-License-Identifier: BSD-3-Clause
"""
import unittest

import numpy as np

from kapton_dose import E_CHARGE, MASS_KG, MU, MU_EN, T_AL, T_KAPTON, analyze_dose, charge_to_dose


class DosePhysicsTests(unittest.TestCase):
    def test_one_fully_collected_photon(self):
        # One 6 keV photon creates 6000/3.6 electron-hole pairs in ideal silicon.
        q = E_CHARGE * 6000 / 3.6
        result = charge_to_dose(q)
        self.assertAlmostEqual(result["photons_at_diode_min"], 1)
        self.assertAlmostEqual(result["photons_after_kapton_before_Al_min"] * T_AL, 1)
        self.assertAlmostEqual(result["photons_incident_on_kapton_min"] * T_KAPTON * T_AL, 1)

    def test_mass_and_energy_conservation(self):
        # 40x300 um2 times 254 um, times 1420 kg/m3.
        self.assertAlmostEqual(MASS_KG, 40e-6 * 300e-6 * 254e-6 * 1420, places=18)
        result = charge_to_dose(.1)
        mean = (result["upstream_sheet_mean_dose_Gy"] + result["downstream_sheet_mean_dose_Gy"])/2
        self.assertAlmostEqual(mean / result["two_sheet_mean_dose_Gy"], 1)
        expected = result["photons_incident_on_kapton_min"] * 6000 * E_CHARGE * (MU_EN/MU) * (1-T_KAPTON)
        self.assertAlmostEqual(result["absorbed_energy_two_sheets_J"], expected)
        self.assertLess(result["downstream_sheet_mean_dose_Gy"],result["upstream_sheet_mean_dose_Gy"])
        self.assertLess(result["exit_plane_area_mean_dose_Gy"],result["downstream_sheet_mean_dose_Gy"])

    def test_zero_and_invalid_charge(self):
        self.assertEqual(charge_to_dose(0)["two_sheet_mean_dose_Gy"],0)
        for bad in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError): charge_to_dose(bad)

    def test_finite_beam_pulse_and_duplicate_read(self):
        # Constant 1000 nA beam pulse in a 1 nA dark baseline, with a repeated
        # IOC timestamp during the pulse. Only six settled 1 s intervals remain.
        samples=[]
        beam=np.array([10 <= i <= 20 for i in range(30)])
        current=np.where(beam,1000.,1.)
        for i in range(30):
            stamp=(i if i!=17 else 16)-.1
            samples.append({"diode_fresh":True,"readings":{"diode":{"value":current[i],"timestamp":stamp,"severity":0}},
                            "states":{"fast":bool(beam[i])}})
        data={"t":np.arange(30,dtype=float),"raw":{"diode":current},"beam":beam,
              "totals":{"beam_s":np.cumsum(beam.astype(float))}}
        result,_=analyze_dose({"samples":samples},data,[])
        segment=result["segments"][0]
        self.assertEqual(segment["accepted_intervals"],6)
        self.assertAlmostEqual(segment["charge_C"],6*999e-9,places=14)


if __name__ == "__main__":
    unittest.main()

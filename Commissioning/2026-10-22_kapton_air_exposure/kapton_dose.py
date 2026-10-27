"""Diode-confirmed, conservative sampled photon and Kapton dose estimate.

No hardware or network access. Units, geometry and assumptions are explicit.
SPDX-License-Identifier: BSD-3-Clause
"""

import math

import numpy as np

E_CHARGE = 1.602176634e-19
ENERGY_EV = 6000.0
PAIR_EV = 3.6  # Si, X-ray Data Booklet section 4.5; no avalanche gain
AREA_MM2 = .040 * .300  # Operator microscopy: outer rectangular footprint
SHEET_CM = .005 * 2.54  # Exactly 5 thou = 127 um per sheet
RHO_KAPTON = 1.42  # NIST ESTAR composition table
RHO_AL = 2.699  # g/cm3, NIST material density
AL_CM = 110e-4
CURRENT_SCALE = 1e9  # IOC reads nA; operator confirms unchanged over weekend
# NIST X-ray mass coefficient tables, exact 6.00000E-03 MeV row.
# element: (weight fraction, mu/rho, mu_en/rho); cm2/g.
ELEMENTS = {
    "H": (.026362, .4042, .01996),
    "C": (.691133, 10.95, 10.54),
    "N": (.073270, 18.09, 17.59),
    "O": (.209235, 27.70, 27.08),
}
AL_MU = 115.3
MU = sum(w * mu for w, mu, _ in ELEMENTS.values())
MU_EN = sum(w * en for w, _, en in ELEMENTS.values())
T_AL = math.exp(-AL_MU * RHO_AL * AL_CM)
T_SHEET = math.exp(-MU * RHO_KAPTON * SHEET_CM)
T_KAPTON = T_SHEET**2
MASS_KG = RHO_KAPTON * (AREA_MM2 / 100) * (2 * SHEET_CM) / 1000
SOURCES = {
    "kapton_density_composition": "https://physics.nist.gov/cgi-bin/Star/compos.pl?matno=179",
    "H": "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z01.html",
    "C": "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z06.html",
    "N": "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z07.html",
    "O": "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z08.html",
    "Al": "https://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z13.html",
    "Si_pair_energy": "https://xdb.lbl.gov/Section4/Sec_4-5.pdf",
    "current_scale": "https://github.com/epics-modules/quadEM/blob/master/docs/source/databases.rst",
}


def charge_to_dose(charge_c):
    """Unity absorption/collection gives minimum photon count for a passive Si PIN.

    Model dose uses primary-beam attenuation and mass energy-absorption, not
    total attenuation as deposited energy. Charged-particle equilibrium/local
    deposition is assumed; no secondary-transport or dose-profile simulation.
    """
    if not math.isfinite(charge_c) or charge_c < 0:
        raise ValueError("Charge must be finite and nonnegative")
    n_diode = charge_c / E_CHARGE * PAIR_EV / ENERGY_EV
    n_transmitted = n_diode / T_AL
    n_incident = n_transmitted / T_KAPTON
    incident_j = n_incident * ENERGY_EV * E_CHARGE
    first_j = incident_j * (MU_EN / MU) * (1 - T_SHEET)
    second_j = first_j * T_SHEET
    return {
        "charge_C": charge_c,
        "photons_at_diode_min": n_diode,
        "photons_after_kapton_before_Al_min": n_transmitted,
        "photons_incident_on_kapton_min": n_incident,
        "absorbed_energy_two_sheets_J": first_j + second_j,
        "two_sheet_mean_dose_Gy": (first_j + second_j) / MASS_KG,
        "upstream_sheet_mean_dose_Gy": first_j / (MASS_KG / 2),
        "downstream_sheet_mean_dose_Gy": second_j / (MASS_KG / 2),
        "exit_plane_area_mean_dose_Gy": n_transmitted * ENERGY_EV * E_CHARGE * MU_EN / (AREA_MM2 / 100) * 1000,
    }


def analyze_dose(bundle, data, run_metadata):
    samples = bundle["samples"]
    t, raw = data["t"], data["raw"]
    n = len(t)
    dt = np.diff(t, prepend=t[0])
    diode = raw["diode"]
    stamps = np.array([s["readings"].get("diode", {}).get("timestamp", np.nan) for s in samples])
    fresh = np.array([bool(s.get("diode_fresh")) for s in samples])
    valid = fresh & np.isfinite(diode) & np.isfinite(stamps)
    valid &= np.array([s["readings"].get("diode", {}).get("severity", -1) == 0 for s in samples])
    age = t - stamps
    valid &= (age >= -0.1) & (age < 3)

    # Establish an intentionally high empirical background: largest fresh value
    # after >=5 seconds continuously confirmed fast-closed. Never add the
    # negative dark median back to the signal, nor undo the IOC's own offset.
    closed_since = None
    dark = []
    for i, s in enumerate(samples):
        if s["states"].get("fast") is False:
            if closed_since is None or dt[i] > 2:
                closed_since = t[i]
            if t[i] - closed_since >= 5 and valid[i]:
                dark.append(float(diode[i]))
        else:
            closed_since = None
    if not dark:
        raise ValueError("No settled, valid dark readings")
    background = max(0.0, math.ceil(max(dark) * 10) / 10)

    # Conservative sampled rectangular rule. Require both endpoints to confirm
    # beam and fresh diode, discard >2 s gaps and the first 3 s of each beam-on
    # stretch (one-second diode averaging), and take the smaller endpoint current.
    settled = np.zeros(n, dtype=bool)
    since = None
    for i in range(n):
        if data["beam"][i] and valid[i]:
            if since is None or dt[i] > 2:
                since = t[i]
            settled[i] = t[i] - since >= 3
        else:
            since = None
    dsource = np.diff(stamps, prepend=stamps[0])
    mask = settled & np.r_[False, settled[:-1]] & (dt > 0) & (dt <= 2)
    mask &= (dsource > 0) & (dsource <= 2)
    dbeam = np.diff(data["totals"]["beam_s"], prepend=data["totals"]["beam_s"][0])
    weights = np.where(mask, np.minimum(np.minimum(dt, dsource), dbeam), 0)
    current = np.maximum(0, np.minimum(diode, np.r_[np.nan, diode[:-1]]) - background)
    charge = np.where(mask, np.nan_to_num(current) * weights / CURRENT_SCALE, 0)
    # Conventional comparator only; not used for headline minimum estimate.
    conventional = np.where(valid, np.maximum(0, np.nan_to_num(diode) - background) * dbeam / CURRENT_SCALE, 0)
    cumulative = np.cumsum(charge)

    def segment(name, lo, hi, interpretation):
        use = (t >= lo) & (t <= hi)
        # No interval crossing the stated segment boundary is included.
        use &= np.r_[False, t[:-1] >= lo]
        q = float(charge[use].sum())
        secs = float(weights[use].sum())
        result = {"name": name, "start_epoch": lo, "end_epoch": hi,
                  "interpretation": interpretation, "accepted_intervals": int(np.count_nonzero(mask & use)),
                  "credited_integration_s": secs, "online_beam_increment_s": float(dbeam[use & np.isfinite(diode)].sum()),
                  "conventional_charge_C": float(conventional[use].sum()), **charge_to_dose(q)}
        result["mean_diode_current_A"] = q / secs if secs else 0
        result["mean_photons_at_diode_per_s"] = result["photons_at_diode_min"] / secs if secs else 0
        return result

    meta = {m["scan_id"]: m for m in run_metadata}
    segments = [segment("all_recorded_diode_exposure", float(t[0]), float(t[-1]),
                        "Photon total across positions; dose is equivalent single-footprint dose, NOT a confirmed dose to one moved spot.")]
    if 1185487 in meta:
        m = meta[1185487]
        segments.append(segment("saturday_first_good_vacuum_run_1185487", m["start"]["time"], m["stop"]["time"],
                                "Only beam recorded within scan 1185487; prior overnight irradiation excluded."))
    if 1185490 in meta:
        m = meta[1185490]
        segments.append(segment("saturday_long_run_1185490", m["start"]["time"], m["stop"]["time"],
                                "Conservative post-restart dose; excludes all earlier exposure and any overlap with earlier positions."))
        first, last = m["frames"]
        segments.append(segment("between_1185490_reference_images", first["kapton_trigger_wall"], last["kapton_trigger_wall"],
                                "Exposure between first and last displayed images, excluding exposure during/after final image."))
    return {
        "inputs": {"energy_eV": ENERGY_EV, "Si_pair_energy_eV": PAIR_EV, "current_scale_units_per_A": CURRENT_SCALE,
                   "area_mm2": AREA_MM2, "area_um": [40, 300], "kapton_sheets": 2, "sheet_thickness_um": 127,
                   "Al_thickness_um": 110, "density_kapton_g_cm3": RHO_KAPTON, "density_Al_g_cm3": RHO_AL,
                   "geometry": "Kapton -> Kapton -> Al -> passive Si PIN diode; operator confirmed",
                   "units_confirmation": "IOC CurrentScale2=1e9 read on Oct 26; operator confirmed unchanged during weekend",
                   "diode_efficiency_assumed": 1.0, "elemental_coefficients": ELEMENTS},
        "model": {"mu_kapton_cm2_g": MU, "mu_en_kapton_cm2_g": MU_EN, "mu_Al_cm2_g": AL_MU,
                  "transmission_Al": T_AL, "transmission_single_sheet": T_SHEET, "transmission_two_sheets": T_KAPTON,
                  "illuminated_two_sheet_mass_kg": MASS_KG, "background_subtracted_nA": background,
                  "settled_dark_max_nA": max(dark), "settled_dark_median_nA": float(np.median(dark)),
                  "settled_dark_samples": len(dark)},
        "method": "Smaller adjacent fresh diode current minus upper observed settled-dark level; weight by minimum of wall, source-timestamp and online-beam increments; discard >2 s gaps and first 3 s after beam-on. No missing-time, early-photon-alarm or pre-diode extrapolation.",
        "limits": "A conservative sampled, model-based lower estimate, not a statistical confidence bound or a strict pointwise minimum. Assumes 6 keV, passive Si/no gain, verified nA scale, stated foil thickness/density, full footprint within 40x300 um, and local energy deposition. Uncorrected diode inefficiency/other downstream losses increase inferred photons. Averaging cannot prove sub-sample minima; electron escape and footprint uncertainties are not quantified.",
        "segments": segments, "sources": SOURCES,
    }, cumulative


def dose_pages(pdf, data, dose, run_metadata, page_start, total_pages, figure_header, save_page):
    """Add readable model and result pages to the existing report."""
    model = dose["model"]
    fig = figure_header(page_start, "Diode photons & Kapton dose", "6 keV | 110 µm Al downstream | Two 127 µm Kapton sheets | 40 × 300 µm bounding area", total_pages)
    rows = []
    names = {"all_recorded_diode_exposure": "All diode exposure*", "saturday_first_good_vacuum_run_1185487": "Sat morning 1185487",
             "saturday_long_run_1185490": "Sat–Mon 1185490", "between_1185490_reference_images": "Between 1185490 images"}
    for s in dose["segments"]:
        rows.append([names[s["name"]], f'{s["charge_C"]:.4f}', f'{s["photons_after_kapton_before_Al_min"]:.3e}',
                     f'{s["two_sheet_mean_dose_Gy"]:.3e}', f'{s["downstream_sheet_mean_dose_Gy"]:.3e}'])
    ax = fig.add_axes([.08, .59, .84, .24]); ax.axis("off")
    table = ax.table(cellText=rows, colLabels=["Selected exposure", "Charge (C)", "Transmitted photons", "Two-sheet mean (Gy)", "Rear-sheet mean (Gy)"],
                     colWidths=[.26,.12,.22,.20,.20],cellLoc="left",bbox=[0,0,1,1])
    table.auto_set_font_size(False); table.set_fontsize(9)
    for (r,c), cell in table.get_celld().items():
        cell.set_facecolor("#12334B" if r==0 else ("#EDF3F6" if r%2 else "white"));cell.set_edgecolor("white")
        cell.get_text().set_color("white" if r==0 else "#12334B")
    text = (
        "* All-diode photons may be summed, but the all-exposure dose is an equivalent single-footprint value across moved positions. Use the Sat–Mon run for a conservative post-restart spot dose. Prior exposure is not assigned to that spot.\n\n"
        f"Al transmission = {T_AL:.5f} ({100*T_AL:.2f}%); two-sheet Kapton transmission = {T_KAPTON:.5f} ({100*T_KAPTON:.2f}%). Illuminated mass = {MASS_KG*1e9:.4f} µg. The rear sheet receives less energy than the front; both are averaged over the full bounding rectangle.\n\n"
        f"Logged units: nA (CurrentScale2=10^9, operator-confirmed). Subtract {model['background_subtracted_nA']:.1f} nA, the upper settled-dark envelope, rather than adding back the negative dark median. Integrate only fresh, confirmed-beam samples; use the smaller endpoint current and reject transitions/gaps.\n\n"
        "Unity Si absorption/collection and 3.6 eV per electron–hole pair give the minimum photon count for a passive PIN diode. No correction for incomplete diode absorption, collection losses or extra downstream attenuation is applied.\n\n"
        "These are conservative sampled model estimates under the stated geometry and local-deposition assumption, not a statistical confidence limit or a minimum at every point. The measured outer footprint lowers the area-average estimate; the beam core can receive more."
    )
    fig.text(.08,.55,text, fontsize=10, va="top",linespacing=1.45,color="#12334B")
    save_page(pdf,fig)

    fig = figure_header(page_start+1,"Dose calculation & traceability","Primary-beam transport with separate total and energy-absorption coefficients",total_pages)
    equations = [
        "I[A] = (logged_current[nA] − dark_upper[nA]) × 10⁻⁹",
        "Q = Σ I_lower × Δt_accepted",
        "N_diode ≥ (Q/e) × (3.6 eV / 6000 eV)",
        "N_after_Kapton ≥ N_diode / T_Al",
        "N_incident ≥ N_after_Kapton / T_Kapton",
        "E_abs = N_incident × E_photon × (μ_en/μ) × (1 − T_Kapton)",
        "D_two_sheets [Gy] = E_abs [J] / (ρ × A × 2t) [kg]",
    ]
    fig.text(.08,.83,"\n\n".join(equations),fontsize=11,va="top",linespacing=1.3)
    coeff = f"NIST at exactly 6 keV: Al μ/ρ = {AL_MU:.3f} cm²/g; Kapton mixture μ/ρ = {MU:.6f}, μ_en/ρ = {MU_EN:.6f} cm²/g. Kapton density 1.42 g/cm³; Al 2.699 g/cm³. Weight fractions: H 0.026362, C 0.691133, N 0.073270, O 0.209235."
    fig.text(.08,.46,coeff,fontsize=10,va="top",linespacing=1.45)
    selected = next(s for s in dose["segments"] if s["name"]=="saturday_long_run_1185490")
    fig.text(.08,.34,f"Scan 1185490: {selected['credited_integration_s']/3600:.4f} h retained by the conservative integration, from {selected['online_beam_increment_s']/3600:.4f} h online beam time. Q = {selected['charge_C']:.6f} C; diode photons ≥ {selected['photons_at_diode_min']:.4e}; upstream incident photons ≥ {selected['photons_incident_on_kapton_min']:.4e}; deposited energy in both sheets ≈ {selected['absorbed_energy_two_sheets_J']:.4f} J. Front-sheet mean {selected['upstream_sheet_mean_dose_Gy']:.4e} Gy, rear-sheet mean {selected['downstream_sheet_mean_dose_Gy']:.4e} Gy. Exit-plane area mean {selected['exit_plane_area_mean_dose_Gy']:.4e} Gy (model depth-minimum, not a lateral pointwise minimum).",fontsize=10,va="top",linespacing=1.45)
    fig.text(.08,.17,"Sources: NIST X-ray mass coefficient tables (H, C, N, O, Al); NIST Kapton composition; LBNL X-ray Data Booklet §4.5; EPICS quadEM current-scale documentation. Full URLs, constants, charge totals and selection method are stored in the JSON. No flux is inferred for Oct 22 before diode logging or for restart gaps. Dose scales inversely with assumed illuminated area.",fontsize=9,va="top",linespacing=1.4)
    save_page(pdf,fig)

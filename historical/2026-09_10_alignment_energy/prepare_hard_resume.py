"""Snapshot recorded coverage and aligned position for the 2026-09-30 continuation.

HISTORICAL AD HOC RECOVERY PREPARATION — specific to scan 1170456.
From a configured smi-plans environment:
pixi run python ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/prepare_hard_resume.py
Reads scalar Tiled data only; performs no beamline motion.
"""
import json
from pathlib import Path

import numpy as np
from tiled.client import from_profile

UID = "efc05487-d3e3-4a05-97f6-a09f151aa1c2"
BEFORE = "08c41d98-7c80-4725-b47d-1b10411b3993"
COMPLETED = ["751b8436-97d4-4744-9fa2-0adcd161bc7b",
             "a7d66d21-ea72-48b6-8703-df488ef791be",
             "73943230-2c7c-4dc2-baf9-ebda8f77fae4"]


def main():
    catalog = from_profile("auto")["smi"]["raw"]
    for uid, count in zip(COMPLETED, [5, 540, 5]):
        run = catalog[uid]
        assert run.metadata["stop"]["num_events"]["primary"] == count
    run = catalog[UID]
    assert run.metadata.get("stop"), "Source run must be closed"
    start = run.metadata["start"]
    ds = run["primary"]["data"].read(variables=[
        "energy_set", "incident_angle", "stage_theta", "attenuation_inserted",
    ])
    assert len(ds.energy_set) == 388
    zero = start["aligned_theta_zero"]
    flags = []
    for uid in [BEFORE, UID]:
        r = catalog[uid]
        d = r["primary"]["data"].read(variables=["energy_set", "incident_angle", "stage_theta"])
        for i, (e, ai, th) in enumerate(zip(d.energy_set.values, d.incident_angle.values, d.stage_theta.values)):
            error = float(th - zero - ai)
            if abs(error) > .002:
                flags.append({"uid": uid, "seq_num": i + 1, "energy_eV": float(e),
                              "incidence_deg": float(ai), "theta_error_deg": error})
    position = {}
    baseline = run["baseline"]["data"]
    for field in ("stage_x", "stage_y", "stage_z", "stage_chi", "stage_phi"):
        position[field] = float(baseline[field + "_setpoint"].read()[0])
    for field in ("piezo_x", "piezo_y", "piezo_z", "piezo_th"):
        position[field] = float(baseline[field + "_user_setpoint"].read()[0])
    # Theta is set directly to the first pending angle, not the old run's last angle.
    assert len(set(ds.attenuation_inserted.values)) == 1
    result = {
        "source_uid": UID, "before_uid": BEFORE, "completed_uids": COMPLETED,
        "sample_id": start["sample_id"], "sample_name": "Au_c4x",
        "remaining_sample_ids": ["1b33f0f6ee3844b7b9df096ab0ba7354", "b90e5346131c4f26a461d970b67233fc"],
        "theta_zero": zero, "position": position,
        "harmonic": start["harmonic_lock"]["harmonic"],
        "attenuation_factor": start["attenuation_factor_requested"],
        "attenuation_inserted": str(ds.attenuation_inserted.values[0]),
        "group_id": start["damage_check_group"],
        "energies": np.concatenate([np.arange(11860,11900,3), np.arange(11900,11960),
                                    np.arange(11960,12060,3)]).astype(float).tolist(),
        "angles": [.05, .1, .15, .2, .25],
        "recorded_pairs": [[float(e), float(ai)] for e, ai in zip(ds.energy_set.values, ds.incident_angle.values)],
        "flagged_events_not_repeated": flags,
    }
    path = Path(__file__).with_name("hard_resume_1170456.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Saved {path}: 388 recorded pairs, 152 pending; {len(flags)} flagged events")
    for ai in result["angles"]:
        measured = {e for e, angle in result["recorded_pairs"] if angle == ai}
        pending = [e for e in result["energies"] if e not in measured]
        print(f"ai={ai}: {len(pending)} remaining, {pending[0]}–{pending[-1]} eV")


if __name__ == "__main__":
    main()

"""Create Mn/Fe/Co/Ni K-edge lists in the shared scan-input database.

HISTORICAL AD HOC SETUP — September/October 2026; see this directory's README.
From a configured smi-plans environment:
pixi run python ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/add_transition_metal_energy_lists.py
Uses the Zinc template's placement and GUI boundary/step spec format.
"""

import numpy as np

from smi_plans import ListStore, NamedList, resolve_list

EDGE_EV = {"Mn": 6539, "Fe": 7112, "Co": 7709, "Ni": 8333}
ZN_EDGE_EV = 9659
SOURCE = "https://xdb.lbl.gov/Section1/Table_1-1a.htm"
TEMPLATE = "Zinc 1ev 80 pts"


def main():
    store = ListStore.from_redis()
    template = store.get_list(TEMPLATE, "energy")
    template_values = template.resolved_values()
    # Verify the template whose placement this recipe is intended to preserve.
    assert list(template.spec["boundaries"]) == [9600, 9650, 9700, 9800]
    assert list(template.spec["steps"]) == [5, 1, 5]
    assert template_values == list(np.concatenate([
        np.arange(9600, 9650, 5), np.arange(9650, 9700, 1),
        np.arange(9700, 9800, 5),
    ]))
    start_offset = float(template.spec["boundaries"][0]) - ZN_EDGE_EV
    offsets = [start_offset + 50 * i for i in range(5)]
    steps = [5.0, 1.0, 3.0, 5.0]
    pending = []
    for element, edge in EDGE_EV.items():
        boundaries = [edge + off for off in offsets]
        segments = [np.arange(a, b, step).tolist()
                    for a, b, step in zip(boundaries, boundaries[1:], steps)]
        values = [value for segment in segments for value in segment]
        assert [len(segment) for segment in segments] == [10, 50, 17, 10]
        assert len(values) == 87 and np.all(np.diff(values) > 0)
        assert edge in values
        nl = NamedList(
            name=f"{element} K 1ev 87 pts", kind="energy", units="eV", values=values,
            spec={"boundaries": boundaries, "steps": steps, "updown": False},
            md={
                "element": element, "edge": "K", "edge_energy_eV": edge,
                "edge_source_url": SOURCE,
                "edge_source": "G. P. Williams, X-Ray Data Booklet, Section 1.1, Table 1-1",
                "edge_reference": "J. A. Bearden and A. F. Burr, Rev. Mod. Phys. 39, 125 (1967)",
                "template_name": TEMPLATE, "template_id": template.id,
                "template_edge_energy_eV": ZN_EDGE_EV,
                "boundary_offsets_eV": offsets,
                "segment_points": [10, 50, 17, 10],
                "endpoint_convention": "Each segment includes start and excludes stop",
                "notes": "Nominal elemental edges; preserve Zinc template placement. "
                         "The 3 eV segment ends 2 eV before the next boundary.",
            },
        )
        existing = store.find_list(nl.name, nl.kind)
        if existing is not None:
            if existing.resolved_values() != values or existing.units != "eV":
                raise ValueError(f"A different list already exists: {nl.name}")
            print(f"Already present: {nl.name}")
        else:
            pending.append(nl)

    for nl in pending:
        store.put_list(nl)

    # Reconnect and resolve by the same name-based API used by acquisition plans.
    check_store = ListStore.from_redis()
    for element, edge in EDGE_EV.items():
        name = f"{element} K 1ev 87 pts"
        expected = [float(e) for a, b, step in zip(offsets, offsets[1:], steps)
                    for e in np.arange(edge + a, edge + b, step)]
        actual = resolve_list(name, kind="energy", store=check_store)
        assert actual == expected
        print(f"Verified {name}: edge={edge} eV; {len(actual)} points; "
              f"{actual[0]:g} to {actual[-1]:g} eV")
    assert check_store.get_list(TEMPLATE, "energy").resolved_values() == template_values


if __name__ == "__main__":
    main()

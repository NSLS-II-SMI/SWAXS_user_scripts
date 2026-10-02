"""Create Au/In L3 scans by shifting the exact Zinc 80-point template.

HISTORICAL AD HOC SETUP — September/October 2026; see this directory's README.
From a configured smi-plans environment:
pixi run python ~/SWAXS_user_scripts/historical/2026-09_10_alignment_energy/add_l3_energy_lists.py
"""

import numpy as np

from smi_plans import ListStore, NamedList, resolve_list

TEMPLATE = "Zinc 1ev 80 pts"
ZN_EDGE_EV = 9659.0
EDGES = (
    ("Au", 11919.0, "https://xdb.lbl.gov/Section1/Table_1-1c.htm"),
    ("In", 3730.0, "https://xdb.lbl.gov/Section1/Table_1-1b.htm"),
)


def main():
    store = ListStore.from_redis()
    template = store.get_list(TEMPLATE, "energy")
    values = template.resolved_values()
    boundaries = list(template.spec["boundaries"])
    steps = list(template.spec["steps"])
    assert template.units == "eV"
    assert boundaries == [9600, 9650, 9700, 9800]
    assert steps == [5, 1, 5]
    assert values == np.concatenate([
        np.arange(a, b, step) for a, b, step in zip(boundaries, boundaries[1:], steps)
    ]).tolist()
    assert len(values) == 80
    lists = []
    for element, edge, source in EDGES:
        shift = edge - ZN_EDGE_EV
        shifted = [v + shift for v in values]
        assert edge in shifted and np.all(np.diff(shifted) > 0)
        nl = NamedList(
            name=f"{element} L3 1ev 80 pts", kind="energy", units="eV",
            values=shifted,
            spec={"boundaries": [b + shift for b in boundaries],
                  "steps": steps, "updown": False},
            md={
                "element": element, "edge": "L3", "edge_energy_eV": edge,
                "edge_source_url": source,
                "edge_source": "G. P. Williams, X-Ray Data Booklet, Section 1.1, Table 1-1",
                "edge_reference": "J. A. Bearden and A. F. Burr, Rev. Mod. Phys. 39, 125 (1967)",
                "template_name": TEMPLATE, "template_id": template.id,
                "template_edge_energy_eV": ZN_EDGE_EV,
                "boundary_offsets_eV": [b - ZN_EDGE_EV for b in boundaries],
                "segment_points": [10, 50, 20],
                "endpoint_convention": "Each segment includes start and excludes stop",
            },
        )
        existing = store.find_list(nl.name, nl.kind)
        if existing is not None:
            if existing.resolved_values() != shifted or existing.units != "eV":
                raise ValueError(f"A different list already exists: {nl.name}")
            print(f"Already present: {nl.name}")
        else:
            lists.append(nl)
    for nl in lists:
        store.put_list(nl)

    check = ListStore.from_redis()
    for element, edge, _ in EDGES:
        name = f"{element} L3 1ev 80 pts"
        actual = resolve_list(name, kind="energy", store=check)
        assert actual == [v + edge - ZN_EDGE_EV for v in values]
        print(f"Verified {name}: {len(actual)} points; edge={edge:g} eV; "
              f"range={actual[0]:g}–{actual[-1]:g} eV")
    assert check.get_list(TEMPLATE, "energy").resolved_values() == values


if __name__ == "__main__":
    main()

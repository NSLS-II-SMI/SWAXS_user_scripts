"""
smi_plans._samples
==================

A small, typed, **GUI-serializable** sample data model for SMI-SWAXS experiments.

Why
---
The legacy corpus represents a sample bar as a set of parallel lists guarded by asserts::

    names   = ['s1', 's2', 's3']
    x_piezo = [55000, 42000, 25000]
    y_piezo = [5000,  5000,  5000]
    ...
    assert len(x_piezo) == len(names)

This is error-prone (easy to misalign columns), not type-safe, and awkward to drive from a
GUI.  Here a sample is a :class:`Sample` dataclass and a bar is a :class:`SampleList`.  The
parallel-list form is still supported as a *constructor* (:meth:`SampleList.from_columns`) so
existing tables paste straight in, but everything downstream is structured.

Coordinate convention (SMI)
---------------------------
* ``piezo_x/y/z`` -- SmarAct fine stage (microns), ``piezo_th`` incident angle (deg).
* ``hexa_x/y/z``  -- hexapod coarse stage (mm), ``hexa_th`` incident angle (deg).
* ``incident_angles`` -- list of grazing angles (deg) to measure, *relative to aligned 0*.
* ``md`` -- free-form per-sample metadata merged into the run's ``md={}`` (e.g.
  ``{'project_name': ..., 'temperature_set': 35, 'thickness_nm': 40}``).  This is where
  "the user told me X" context lives until it is also recorded as a Signal at acquisition.

Nothing here imports bluesky/ophyd; this module is pure Python and safe to import anywhere
(including a GUI process).
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence


__all__ = ["Sample", "SampleList"]


def _coerce_optional_float(v):
    return None if v is None else float(v)


@dataclass
class Sample:
    """One physical sample / position on the bar.

    Only ``name`` is required.  Coordinates are optional so the same model works for piezo,
    hexapod, or "use current position" workflows -- ``None`` means "do not move this axis".
    """

    name: str

    # SmarAct fine stage
    piezo_x: Optional[float] = None
    piezo_y: Optional[float] = None
    piezo_z: Optional[float] = None
    piezo_th: Optional[float] = None

    # Hexapod coarse stage
    hexa_x: Optional[float] = None
    hexa_y: Optional[float] = None
    hexa_z: Optional[float] = None
    hexa_th: Optional[float] = None

    # Measurement parameters (per sample; technique plans read what they need)
    incident_angles: List[float] = field(default_factory=list)

    # Free-form metadata merged into md={} for this sample's run(s)
    md: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for attr in ("piezo_x", "piezo_y", "piezo_z", "piezo_th",
                     "hexa_x", "hexa_y", "hexa_z", "hexa_th"):
            setattr(self, attr, _coerce_optional_float(getattr(self, attr)))
        self.incident_angles = [float(a) for a in self.incident_angles]
        if not self.name or not str(self.name).strip():
            raise ValueError("Sample.name must be a non-empty string")

    # -- convenience views ---------------------------------------------------
    def piezo_moves(self):
        """Return a dict ``{axis_name: value}`` of the piezo axes that are set (not None).

        Intended to be expanded into ``bps.mv`` pairs by a technique plan, e.g.::

            for axis, val in sample.piezo_moves().items():
                ...  # map 'x'->piezo.x etc.
        """
        out = {}
        for short, attr in (("x", "piezo_x"), ("y", "piezo_y"),
                            ("z", "piezo_z"), ("th", "piezo_th")):
            v = getattr(self, attr)
            if v is not None:
                out[short] = v
        return out

    def hexa_moves(self):
        """Return a dict ``{axis_name: value}`` of the hexapod axes that are set."""
        out = {}
        for short, attr in (("x", "hexa_x"), ("y", "hexa_y"),
                            ("z", "hexa_z"), ("th", "hexa_th")):
            v = getattr(self, attr)
            if v is not None:
                out[short] = v
        return out

    def base_md(self):
        """Metadata describing this sample, for merging into a run's ``md={}``."""
        out = {"sample_name": self.name}
        out.update(self.md)
        return out

    def to_dict(self):
        """JSON-serializable dict (for GUIs / persistence)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class SampleList:
    """An ordered collection of :class:`Sample` with construction & validation helpers."""

    def __init__(self, samples: Sequence[Sample] = ()):
        self.samples: List[Sample] = list(samples)
        self.validate()

    # -- container protocol --------------------------------------------------
    def __iter__(self):
        return iter(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        return self.samples[i]

    def __repr__(self):
        return "SampleList({} samples: {})".format(
            len(self), ", ".join(s.name for s in self.samples))

    # -- validation ----------------------------------------------------------
    def validate(self):
        """Raise if names are duplicated or empty.  Returns self for chaining."""
        names = [s.name for s in self.samples]
        if len(set(names)) != len(names):
            dupes = sorted({n for n in names if names.count(n) > 1})
            raise ValueError("Duplicate sample names: {}".format(dupes))
        return self

    # -- constructors --------------------------------------------------------
    @classmethod
    def from_columns(cls, names, *,
                     piezo_x=None, piezo_y=None, piezo_z=None, piezo_th=None,
                     hexa_x=None, hexa_y=None, hexa_z=None, hexa_th=None,
                     incident_angles=None, md=None):
        """Build from the legacy parallel-list convention with length checks.

        Any column left ``None`` is treated as all-``None`` (axis not used).  ``md`` may be
        a single dict (applied to all) or a per-sample list of dicts.  ``incident_angles``
        may be a single list (shared) or a per-sample list-of-lists.

        Example
        -------
        >>> bar = SampleList.from_columns(
        ...     names   = ['s1', 's2', 's3'],
        ...     piezo_x = [55000, 42000, 25000],
        ...     piezo_y = [5000, 5000, 5000],
        ...     incident_angles = [0.1, 0.2],          # shared by all
        ... )
        """
        n = len(names)

        def _col(col, label):
            if col is None:
                return [None] * n
            if len(col) != n:
                raise ValueError(
                    "Column '{}' has length {} but there are {} samples"
                    .format(label, len(col), n))
            return list(col)

        px, py, pz, pth = (_col(piezo_x, "piezo_x"), _col(piezo_y, "piezo_y"),
                           _col(piezo_z, "piezo_z"), _col(piezo_th, "piezo_th"))
        hx, hy, hz, hth = (_col(hexa_x, "hexa_x"), _col(hexa_y, "hexa_y"),
                           _col(hexa_z, "hexa_z"), _col(hexa_th, "hexa_th"))

        # incident_angles: shared list, per-sample list-of-lists, or None
        if incident_angles is None:
            ia = [[] for _ in range(n)]
        elif len(incident_angles) and isinstance(incident_angles[0], (list, tuple)):
            ia = _col(incident_angles, "incident_angles")
        else:
            ia = [list(incident_angles) for _ in range(n)]

        # md: shared dict or per-sample list
        if md is None:
            mds = [dict() for _ in range(n)]
        elif isinstance(md, dict):
            mds = [dict(md) for _ in range(n)]
        else:
            mds = _col(md, "md")

        samples = [
            Sample(name=names[i],
                   piezo_x=px[i], piezo_y=py[i], piezo_z=pz[i], piezo_th=pth[i],
                   hexa_x=hx[i], hexa_y=hy[i], hexa_z=hz[i], hexa_th=hth[i],
                   incident_angles=list(ia[i]), md=dict(mds[i]))
            for i in range(n)
        ]
        return cls(samples)

    @classmethod
    def from_dicts(cls, dicts):
        """Build from a list of dicts (e.g. a GUI table or JSON)."""
        return cls([Sample.from_dict(d) for d in dicts])

    @classmethod
    def from_csv(cls, path):
        """Build from a CSV whose header columns match :class:`Sample` fields.

        ``incident_angles`` may be a space- or semicolon-separated string in the cell.
        Unknown columns are folded into ``md``.  Blank cells become ``None``.
        """
        import csv

        known = {"name", "piezo_x", "piezo_y", "piezo_z", "piezo_th",
                 "hexa_x", "hexa_y", "hexa_z", "hexa_th", "incident_angles"}
        out = []
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                kwargs = {}
                md = {}
                for k, v in row.items():
                    if k is None:
                        continue
                    key = k.strip()
                    val = (v or "").strip()
                    if key == "name":
                        kwargs["name"] = val
                    elif key == "incident_angles":
                        kwargs["incident_angles"] = [
                            float(x) for x in val.replace(";", " ").split()] if val else []
                    elif key in known:
                        kwargs[key] = (float(val) if val != "" else None)
                    elif key:
                        md[key] = val
                kwargs["md"] = md
                out.append(Sample(**kwargs))
        return cls(out)

    def to_dicts(self):
        return [s.to_dict() for s in self.samples]

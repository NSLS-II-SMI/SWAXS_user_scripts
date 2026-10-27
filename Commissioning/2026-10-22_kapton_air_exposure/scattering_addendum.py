"""Kapton SAXS/WAXS exposure-series addendum; read-only data access, Pixi execution.

Preview by default. --apply --download caches missing Tiled frames/metadata;
--apply --reduce integrates cached frames; --apply --report renders offline.
SPDX-License-Identifier: BSD-3-Clause
"""

import argparse
import contextlib
import csv
import hashlib
import io
import json
import logging
import sqlite3
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import Normalize

from final_weekend_report import DEFAULT_DB, local, save_page

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "logs/scattering_cache"
PREFIX = ROOT / "kapton_scattering_addendum_2026-10-26"
LOG = logging.getLogger(__name__)
FIELDS = {"saxs": "pil2M_image", "waxs": "pil900KW_image"}
BASE_FIELDS = (
    "time", "energy_energy", "pil2M_beam_center_x_px", "pil2M_beam_center_y_px",
    "pil2M_active_beamstop", "pil2M_motor_x", "pil2M_motor_y", "pil2M_motor_z",
    "saxs_beamstop_x_pin", "saxs_beamstop_y_pin", "saxs_beamstop_x_rod",
    "saxs_beamstop_y_rod", "waxs_arc", "waxs_bsx", "piezo_x", "piezo_y",
    "piezo_z", "stage_x", "stage_y", "stage_z", "xbpm3_sumX",
)
PRIMARY_FIELDS = (
    "time", "waxs_arc", "waxs_bsx", "pil2M_motor_x", "pil2M_motor_y",
    "pil2M_motor_z", "kapton_trigger_wall", "kapton_beam_s", "kapton_online_beam_s",
    "kapton_beam_end_s", "kapton_post_trip", "kapton_image_id",
    "pil2M_attenuation_factor_used", "pil900KW_attenuation_factor_used",
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def request(call):
    """Three attempts, 3 s total backoff, and pacing after every request."""
    for attempt in range(3):
        try:
            result = call()
            time.sleep(.15)
            return result
        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == 2:
                raise
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 429 and exc.response.status_code < 500:
                raise
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def journal():
    """Only the completed immutable snapshot; no live monitor or EPICS imports."""
    with sqlite3.connect(DEFAULT_DB.resolve().as_uri() + "?mode=ro&immutable=1", uri=True) as db:
        images = {}
        for (payload,) in db.execute("SELECT payload FROM images ORDER BY id"):
            value = json.loads(payload)
            if "image_id" in value:
                images[value["image_id"]] = value
    return images


def read_scalars(node, wanted):
    keys = [k for k in wanted if k in node]
    ds = request(lambda: node.read(variables=keys))
    return {k: np.asarray(ds[k]).tolist() for k in keys}


def download():
    from tiled.client import from_uri
    from tiled.queries import Key

    CACHE.mkdir(parents=True, exist_ok=True)
    legacy = {m["scan_id"]: m for m in json.loads((ROOT / "logs/image_cache/manifest.json").read_text())}
    audit = journal()
    client = from_uri("https://tiled.nsls2.bnl.gov", timeout=httpx.Timeout(60, connect=5), max_connections=2)
    try:
        catalog = client["smi"]["raw"]
        inventory_path = CACHE / "inventory.json"
        if inventory_path.exists():
            inventory = json.loads(inventory_path.read_text())
        else:
            selected = catalog.search(Key("scan_id") >= 1185419).search(Key("scan_id") <= 1185490)
            inventory = []
            for uid, run in selected.items():
                start = dict(run.metadata["start"])
                stop = dict(run.metadata.get("stop") or {})
                inventory.append({"uid": uid, "scan_id": start["scan_id"],
                                  "start": start, "stop": stop})
                time.sleep(.15)
            inventory.sort(key=lambda m: m["scan_id"])
            write_json(inventory_path, inventory)
        for item in inventory:
            scan, uid = item["scan_id"], item["uid"]
            start, stop = item["start"], item["stop"]
            if start.get("beam_down_test") or "kapton_air_holder_01" not in start.get("sample_name", ""):
                continue
            if not stop.get("num_events", {}).get("primary", 0):
                continue
            target = CACHE / f"{scan}.json"
            run = None
            if target.exists():
                meta = json.loads(target.read_text())
            else:
                run = request(lambda: catalog[uid])
                primary = run["primary"]["data"]
                scalars = read_scalars(primary, PRIMARY_FIELDS)
                baseline = read_scalars(run["baseline"]["data"], BASE_FIELDS)
                desc = list(run["primary"].metadata["descriptors"])
                if len(desc) != 1:
                    raise ValueError(f"Scan {scan}: changing configuration requires segmented reduction")
                config = {k: v["data"] for k, v in desc[0]["configuration"].items() if k in ("pil2M", "pil900KW")}
                detectors = [k for k, field in FIELDS.items() if field in primary]
                n = stop["num_events"]["primary"]
                frames = []
                for index in range(n):
                    if scan in legacy:
                        old = legacy[scan]
                        im = next(x for x in audit.values() if x.get("run_uid") == uid)
                        wall, beam = old["wall"], old["corrected_beam_s"]
                        source = f"logs/image_cache/{uid}.npz"
                    else:
                        image_id = scalars["kapton_image_id"][index]
                        im = audit[image_id]
                        wall = scalars["kapton_trigger_wall"][index]
                        beam = scalars["kapton_beam_s"][index]
                        reference = ROOT / f"logs/weekend_image_cache/{scan}_{index}.npz"
                        source = str(reference.relative_to(ROOT)) if reference.exists() else f"logs/scattering_cache/{scan}_{index}.npz"
                    st = im["start"]
                    post = bool(st.get("post_trip") or im.get("end", {}).get("post_trip"))
                    flux = float(st["values"]["incident_flux"])
                    included = not post and bool(st["states"].get("beam")) and flux > 1 and st.get("incident_flux_fresh", False)
                    frames.append({"index": index, "event": index + 1, "image_id": im["image_id"],
                                   "wall": wall, "local_time": local(wall), "campaign_beam_s": beam,
                                   "bpm3": flux, "included": included, "post_trip": post,
                                   "exclusion": "post-trip" if post else ("" if included else "beam/flux not confirmed"),
                                   "file": source})
                meta = {**item, "catalog": "smi/raw", "baseline": baseline, "primary": scalars,
                        "configuration": config, "detectors": detectors, "frames": frames}
                write_json(target, meta)
            for frame in meta["frames"]:
                path = ROOT / frame["file"]
                if path.exists():
                    continue
                if run is None:
                    run = request(lambda: catalog[uid])
                arrays = {}
                for detector in meta["detectors"]:
                    node = run["primary"]["data"][FIELDS[detector]]
                    shape = node.structure().shape
                    if np.prod(shape[1:]) > 3_000_000:
                        raise ValueError(f"Unexpected frame size: {shape}")
                    i = frame["index"]
                    arrays[detector] = np.squeeze(np.asarray(request(lambda: node[i:i + 1])))
                np.savez_compressed(path, **arrays)
                LOG.info("Cached scan %s event %s/%s", scan, frame["event"], len(meta["frames"]))
            LOG.info("Scan %s: %s; %s image sets", scan, "+".join(meta["detectors"]), len(meta["frames"]))
    finally:
        client.context.close()


def cached_runs():
    return [json.loads(p.read_text()) for p in sorted(CACHE.glob("[0-9]*.json")) if p.stem.isdigit()]


class LocalNode(dict):
    """Minimal offline run adapter for the package's geometry resolvers."""

    def __init__(self, *args, metadata=None, dataset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = metadata or {}
        self.dataset = dataset

    def read(self):
        return self.dataset


def geometry(meta):
    from smi_tiled import resolve_saxs_geometry, resolve_waxs_geometry
    base = xr.Dataset({k: ("snapshot", v) for k, v in meta["baseline"].items()})
    primary = LocalNode(data={k: np.array(v) for k, v in meta["primary"].items()},
                        metadata={"configuration": {k: {"data": v} for k, v in meta["configuration"].items()}})
    run = LocalNode(baseline=LocalNode(dataset=base), primary=primary,
                    metadata={"start": meta["start"]})
    waxs = resolve_waxs_geometry(run)
    saxs = resolve_saxs_geometry(run) if "saxs" in meta["detectors"] else None
    if saxs is not None and not meta["baseline"].get("pil2M_active_beamstop"):
        raise ValueError("Missing active beamstop provenance")
    return saxs, waxs


def reduce_all():
    from smi_tiled import integrate_saxs, integrate_waxs, make_saxs_mask_from_spec, WAXSCalibration
    from smi_tiled.defaults import resolve_mask_path
    from smi_tiled.integrator import make_waxs_mask_callable

    for meta in cached_runs():
        scan = meta["scan_id"]
        target = CACHE / f"{scan}_iq.npz"
        geopath = CACHE / f"{scan}_geometry.json"
        if target.exists() and geopath.exists() and json.loads(geopath.read_text()).get("reduction_schema") == 2:
            continue
        saxgeo, waxgeo = geometry(meta)
        n = len(meta["frames"])
        arc = np.asarray(meta["primary"]["waxs_arc"])
        bsx = np.asarray(meta["primary"]["waxs_bsx"])
        cal = WAXSCalibration(energy_kev=waxgeo.energy_ev / 1000, beam_center_row=waxgeo.beam_center_row_px,
                              beam_center_col=waxgeo.beam_center_col_px, beam_col_per_arc_deg=.08)
        if np.max(np.abs(arc - 15)) > .01 or np.ptp(bsx) > .01:
            raise ValueError("This campaign's fixed WAXS mask needs reassessment for moving geometry")
        # The recorded bsx is an overflow sentinel (-2147.483648 mm). The visible
        # shadow coincides with the bundled unshifted raw polygon, verified on
        # first/last frames. Do not infer a fictitious -416 px shift from arc.
        wmask = make_waxs_mask_callable(resolve_mask_path(None, "waxs"),
                                        waxs_bsx_ref=float(bsx[0]), beamstop_max_abs_arc_deg=None)
        smask = None
        if saxgeo:
            smask = make_saxs_mask_from_spec((1679, 1475), mask_path=resolve_mask_path(None, "saxs"),
                                            active_beamstop=saxgeo.active_beamstop,
                                            beamstop_pos_mm=saxgeo.beamstop_pos_mm,
                                            beam_center_px=(saxgeo.beam_center_row_px, saxgeo.beam_center_col_px))
        output = {}
        for detector in meta["detectors"]:
            profiles, counts = [], []
            q_reference = None
            for first in range(0, n, 8):
                last = min(first + 8, n)
                images = []
                for frame in meta["frames"][first:last]:
                    with np.load(ROOT / frame["file"], allow_pickle=False) as source:
                        im = source[detector].astype(float)
                    # Negative Pilatus sentinels are invalid; real zero counts are retained.
                    im[im < 0] = np.nan
                    images.append(im)
                data = xr.DataArray(np.stack(images), dims=("waxs_arc", "row", "col"),
                                    coords={"waxs_arc": arc[first:last]})
                options = dict(n_q=700 if detector == "saxs" else 1000, n_chi=180,
                               solid_angle_correction=True, pixel_splitting=2,
                               build_detector_ds=False, build_frame_qchi=False, dezinger_threshold=3000.)
                with contextlib.redirect_stdout(io.StringIO()):
                    if detector == "saxs":
                        data.attrs.update(dist=saxgeo.dist_m, poni1=saxgeo.poni1_m, poni2=saxgeo.poni2_m,
                                          pixel1=saxgeo.pixel1_m, pixel2=saxgeo.pixel2_m,
                                          wavelength=saxgeo.wavelength_m * 1e10)
                        result = integrate_saxs(data, mask=smask, waxs_arc=arc[first:last], **options)
                    else:
                        data.attrs.update(smi_energy_per_frame_ev=[waxgeo.energy_ev] * (last - first),
                                          smi_waxs_bsx_per_frame=bsx[first:last])
                        result = integrate_waxs(data, mask_fn=wmask, cal=cal, **options)
                ds = result["iq_frames"]
                q = np.asarray(ds.q) / 10  # package q is nm^-1; report uses Angstrom^-1.
                if q_reference is None:
                    q_reference = q
                profiles.append(np.array([np.interp(q_reference, q, row, left=np.nan, right=np.nan)
                                          for row in np.asarray(ds["I"])]))
                counts.append(np.array([np.interp(q_reference, q, row, left=0, right=0)
                                        for row in np.asarray(ds.counts)]))
                LOG.info("Reduced scan %s %s frames %s-%s/%s", scan, detector, first + 1, last, n)
            exposure = meta["configuration"]["pil2M" if detector == "saxs" else "pil900KW"][
                ("pil2M" if detector == "saxs" else "pil900KW") + "_cam_acquire_time"]
            intensity = np.concatenate(profiles) / exposure
            output[f"{detector}_q"] = q_reference
            output[f"{detector}_intensity"] = intensity
            output[f"{detector}_counts"] = np.concatenate(counts)
            output[f"{detector}_normalized"] = intensity * (50. / np.array([f["bpm3"] for f in meta["frames"]]))[:, None]
        np.savez_compressed(target, **output)
        write_json(geopath, {
            "reduction_schema": 2,
            "saxs": asdict(saxgeo) if saxgeo else None, "waxs": asdict(waxgeo),
            "waxs_calibration": asdict(cal), "solid_angle_correction": True,
            "pixel_splitting": 2, "dezinger_threshold": 3000., "q_unit": "angstrom^-1",
            "intensity_unit": "counts / s / sr", "normalization": "multiply by 50 / pre-trigger BPM3",
            "waxs_beamstop": "fixed unshifted bundled polygon; bsx overflow sentinel, image-verified shadow",
            "mask_sha256": {d: digest(resolve_mask_path(None, d)) for d in meta["detectors"]},
        })


GROUPS = (("early", "Oct 22 · WAXS-only", range(1185420, 1185482)),
          ("1185487", "Oct 24 · morning session", [1185487]),
          ("1185489", "Oct 24 · restart check", [1185489]),
          ("1185490", "Oct 24–26 · long session", [1185490]))
COLORS = {"early": "#008C95", "1185487": "#DA8731", "1185489": "#777777", "1185490": "#5C4B8B"}
BANDS = {"waxs": [(0.4, .8), (1., 1.8)], "saxs": [(.002, .008), (.01, .025), (.03, .06)]}


def collect():
    """Regrid only within each detector; leave unobserved q bins as NaN."""
    groups, audit = {}, []
    runs = cached_runs()
    for key, label, scans in GROUPS:
        selected = [m for m in runs if m["scan_id"] in scans]
        group = {"key": key, "label": label, "meta": selected, "frames": [], "detectors": {}}
        for meta in selected:
            for f in meta["frames"]:
                record = {**f, "scan_id": meta["scan_id"], "uid": meta["uid"], "group": key,
                          "detectors": "+".join(meta["detectors"])}
                with np.load(ROOT / f["file"], allow_pickle=False) as raw:
                    w = raw["waxs"]
                    nonnegative = w[w >= 0]
                    record["waxs_total_nonnegative_counts"] = int(np.sum(nonnegative, dtype=np.int64))
                    record["waxs_median_nonnegative_counts"] = float(np.median(nonnegative))
                # Beam readbacks are sampled before triggering, so they cannot
                # establish that photons arrived during the detector's gate.
                dark = record["waxs_median_nonnegative_counts"] == 0 and record["waxs_total_nonnegative_counts"] < 10_000
                record["detector_dark"] = dark
                if dark and record["included"]:
                    record.update(included=False, exclusion="detector-dark: median=0 and total<10000 counts")
                audit.append(record)
                if record["included"]:
                    group["frames"].append(record)
        if not group["frames"]:
            continue
        group["hours"] = np.array([f["campaign_beam_s"] / 3600 for f in group["frames"]])
        accepted_ids = {f["image_id"] for f in group["frames"]}
        if np.any(np.diff(group["hours"]) <= 0):
            raise ValueError(f"Non-increasing included-frame exposure for {key}")
        for detector in ("waxs", "saxs"):
            raw, normalized, weights, qref = [], [], [], None
            for meta in selected:
                if detector not in meta["detectors"]:
                    continue
                with np.load(CACHE / f"{meta['scan_id']}_iq.npz", allow_pickle=False) as z:
                    q = z[f"{detector}_q"]
                    if qref is None:
                        qref = q.copy()
                    for f in meta["frames"]:
                        if f["image_id"] not in accepted_ids:
                            continue
                        index = f["index"]
                        counts = z[f"{detector}_counts"][index]
                        valid = counts >= 20
                        for dest, suffix in ((raw, "intensity"), (normalized, "normalized")):
                            y = np.where(valid, z[f"{detector}_{suffix}"][index], np.nan)
                            dest.append(np.interp(qref, q, y, left=np.nan, right=np.nan))
                        weights.append(np.interp(qref, q, counts, left=0, right=0))
            if raw:
                group["detectors"][detector] = {"q": qref, "raw": np.array(raw),
                                                "I": np.array(normalized), "counts": np.array(weights)}
        groups[key] = group
    return groups, audit


def band_values(detector, band, field="I"):
    q, values = detector["q"], detector[field]
    use = (q >= band[0]) & (q <= band[1]) & np.all(np.isfinite(values), axis=0)
    if np.count_nonzero(use) < 8:
        raise ValueError(f"Insufficient common coverage for q band {band}")
    return np.trapezoid(values[:, use], q[use], axis=1) / (q[use][-1] - q[use][0])


def statistics(groups):
    out = {}
    for key, g in groups.items():
        metrics = []
        for name, d in g["detectors"].items():
            for band in BANDS[name]:
                y = band_values(d, band)
                raw = band_values(d, band, "raw")
                nref = min(3, len(y))
                first, last = float(np.mean(y[:nref])), float(np.mean(y[-nref:]))
                metrics.append({"detector": name, "q_band_A_inv": band, "first_mean": first,
                                "last_mean": last, "endpoint_change_percent": 100 * (last / first - 1),
                                "single_endpoint_change_percent": float(100 * (y[-1] / y[0] - 1)),
                                "raw_endpoint_change_percent": 100 * (np.mean(raw[-nref:]) / np.mean(raw[:nref]) - 1),
                                "first_cv_percent": 100 * float(np.std(y[:nref])) / first,
                                "last_cv_percent": 100 * float(np.std(y[-nref:])) / last,
                                "endpoint_frames_averaged": nref,
                                "maximum_excursion_percent": float(np.max(np.abs(100 * (y / first - 1))))})
        out[key] = {"label": g["label"], "frames": len(g["frames"]),
                    "first_campaign_h": float(g["hours"][0]), "last_campaign_h": float(g["hours"][-1]),
                    "between_images_beam_h": float(np.ptp(g["hours"])), "metrics": metrics}
    return out


def validate_dataset(groups, audit):
    inventory = json.loads((CACHE / "inventory.json").read_text())
    expected = {m["scan_id"]: m["stop"]["num_events"]["primary"] for m in inventory
                if "kapton_air_holder_01" in m["start"].get("sample_name", "")
                and not m["start"].get("beam_down_test")
                and m["stop"].get("num_events", {}).get("primary", 0)}
    observed = dict(Counter(row["scan_id"] for row in audit))
    if expected != observed:
        raise ValueError(f"Incomplete acquisition coverage: expected {expected}, observed {observed}")
    if len({(row["uid"], row["event"]) for row in audit}) != len(audit):
        raise ValueError("Duplicate detector events")
    for group in groups.values():
        for name, detector in group["detectors"].items():
            assert detector["I"].shape == (len(group["frames"]), len(detector["q"]))
            assert np.all(np.diff(detector["q"]) > 0)
            expected_scale = (50 / np.array([f["bpm3"] for f in group["frames"]]))[:, None]
            np.testing.assert_allclose(detector["I"], detector["raw"] * expected_scale, rtol=1e-12, equal_nan=True)
    return {"acquired_runs": len(expected), "acquired_image_sets": len(audit),
            "complete_runstop_event_coverage": True, "unique_frame_identifiers": True,
            "monotonic_q_and_exposure": True, "normalization_verified": True}


def page(number, title, subtitle, total=9):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(.08, .955, "SMI  /  KAPTON SCATTERING ADDENDUM", fontsize=10, color="#008C95", weight="bold")
    fig.text(.08, .919, title, fontsize=20, color="#12334B", weight="bold")
    fig.text(.08, .89, subtitle, fontsize=9, color="#657584")
    fig.text(.08, .03, "22–26 OCT 2026  •  6 keV  •  TIME ZONE: EDT", fontsize=8, color="#657584")
    fig.text(.92, .03, f"{number:02d} / {total:02d}", ha="right", fontsize=8, color="#657584")
    return fig


def note(fig, y, text, size=9):
    fig.text(.08, y, text, va="top", fontsize=size, color="#334D5F", linespacing=1.4)


def axis_style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=.18)


def selected_indices(hours, count=18):
    if len(hours) <= count:
        return np.arange(len(hours))
    return np.unique([int(np.argmin(np.abs(hours - v))) for v in np.linspace(hours[0], hours[-1], count)])


def waterfall_page(pdf, number, group, detector):
    d = group["detectors"][detector]
    q, values, hours = d["q"], d["I"], group["hours"]
    used = np.all(np.isfinite(values) & (values > 0), axis=0)
    if detector == "saxs":
        used &= (q >= .002) & (q <= .065)
    else:
        used &= (q >= .25) & (q <= 2.25)
    # Preserve masked holes instead of connecting across gaps in q coverage.
    data = np.where(used[None, :], values, np.nan)
    fig = page(number, f"{detector.upper()} · exposure waterfall", group["label"] +
               f"  |  {len(hours)} accepted patterns  |  {np.ptp(hours):.3f} h beam-on between endpoints")
    ax = fig.add_axes([.01, .445, .95, .425], projection="3d")
    colors = plt.get_cmap("viridis")
    norm = Normalize(hours[0], hours[-1])
    indices = selected_indices(hours)
    x = np.log10(q) if detector == "saxs" else q
    for i in indices:
        ax.plot(x, np.full_like(q, hours[i]), np.log10(data[i]), color=colors(norm(hours[i])), lw=.9)
    ax.set_xlabel("q (Å⁻¹)" + (" · log scale" if detector == "saxs" else ""), labelpad=9, fontsize=9)
    ax.set_ylabel("Campaign beam-on (h)", labelpad=9, fontsize=9)
    ax.set_zlabel("log₁₀ I (counts s⁻¹ sr⁻¹)", labelpad=7, fontsize=8)
    ax.tick_params(labelsize=7, pad=1)
    ax.view_init(elev=25, azim=-62)
    ax.set_box_aspect((1.55, 1.15, .7))
    if detector == "saxs":
        ticks = np.array([.002, .005, .01, .02, .05])
        ax.set_xticks(np.log10(ticks), [f"{v:g}" for v in ticks])
        ax.set_xlim(np.log10(.002), np.log10(.065))
    else:
        ax.set_xlim(.25, 2.25)
    cbax = fig.add_axes([.88, .50, .018, .28])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=colors), cax=cbax)
    cb.set_label("Campaign exposure (h)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    fig.text(.08, .455, f"{len(indices)} curves displayed, selected at approximately equal beam-time intervals.", fontsize=8)
    ax2 = fig.add_axes([.12, .205, .71, .20])
    n_reference = np.isfinite(data[:3]).sum(axis=0)
    reference = np.divide(np.nansum(data[:3], axis=0), n_reference,
                          out=np.full(q.shape, np.nan), where=n_reference > 0)
    delta = 100 * (data / reference - 1)
    finite = delta[np.isfinite(delta)]
    limit = max(3., float(np.percentile(np.abs(finite), 98)))
    xe = np.r_[q[0] - (q[1] - q[0]) / 2, (q[:-1] + q[1:]) / 2, q[-1] + (q[-1] - q[-2]) / 2]
    ye = np.r_[hours[0] - (hours[1] - hours[0]) / 2, (hours[:-1] + hours[1:]) / 2,
               hours[-1] + (hours[-1] - hours[-2]) / 2]
    mesh = ax2.pcolormesh(xe, ye, delta, shading="flat", cmap="RdBu_r", vmin=-limit, vmax=limit, rasterized=True)
    ax2.set_title("All patterns: change relative to mean of first three", loc="left", fontsize=10, pad=10)
    ax2.set_ylabel("Campaign beam-on (h)", fontsize=9)
    ax2.set_xlabel("q (Å⁻¹)", fontsize=9)
    ax2.tick_params(labelsize=8)
    if detector == "saxs":
        ax2.set_xscale("log")
        ax2.set_xlim(.002, .065)
    else:
        ax2.set_xlim(.25, 2.25)
    cb = fig.colorbar(mesh, cax=fig.add_axes([.86, .205, .022, .20]), extend="both")
    cb.set_label("ΔI / I₀ (%)", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    note(fig, .14,
         "Intensity is divided by the detector exposure and pixel solid angle, then scaled to BPM3 = 50. "
         "Waterfall heights retain intensity differences; no per-curve area scaling is used. "
         "White q bins lack sufficient shared acceptance (at least 20 weighted pixels/bin). "
         "Heatmap rows use beam-time midpoints, not wall time; gaps in delivery add no exposure. "
         "The campaign counter includes earlier positions and is not a spot-specific dose.", 8.5)
    save_page(pdf, fig)


def render_report():
    import smi_tiled
    import smi_tiled.integrator
    import smi_tiled.loader
    groups, audit = collect()
    checks = validate_dataset(groups, audit)
    summary = statistics(groups)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42})
    provenance = {"source_database": str(DEFAULT_DB), "database_sha256": digest(DEFAULT_DB),
                  "smi_tiled_version": smi_tiled.__version__,
                  "package_source_sha256": {"integrator.py": digest(Path(smi_tiled.integrator.__file__)),
                                             "loader.py": digest(Path(smi_tiled.loader.__file__))},
                  "source_catalog": "https://tiled.nsls2.bnl.gov/api/v1/metadata/smi/raw",
                  "reduction_script_sha256": digest(Path(__file__)), "groups": summary,
                  "validation": checks,
                  "patterns_reduced": dict(Counter(d for row in audit for d in row["detectors"].split("+"))),
                  "patterns_included": dict(Counter(d for row in audit if row["included"] for d in row["detectors"].split("+"))),
                  "excluded_frames": [f for f in audit if not f["included"]],
                  "run_metadata_sha256": {p.name: digest(p) for p in CACHE.glob("*.json")}}
    write_json(PREFIX.with_suffix(".json"), provenance)
    fields = ["scan_id", "uid", "event", "image_id", "group", "detectors", "included", "exclusion",
              "local_time", "wall", "campaign_beam_s", "bpm3", "detector_dark",
              "waxs_total_nonnegative_counts", "waxs_median_nonnegative_counts", "file"]
    with PREFIX.with_suffix(".csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(audit)
    # Long-format export retains every accepted q bin and both normalization choices.
    with (ROOT / (PREFIX.name + "_iq.csv")).open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["scan_id", "event", "campaign_beam_h", "detector", "q_A_inv",
                         "I_counts_s_sr", "I_BPM3_50_counts_s_sr"])
        for g in groups.values():
            for name, d in g["detectors"].items():
                for i, frame in enumerate(g["frames"]):
                    for j in np.flatnonzero(np.isfinite(d["I"][i])):
                        writer.writerow([frame["scan_id"], frame["event"], f"{g['hours'][i]:.7f}", name,
                                         f"{d['q'][j]:.8g}", f"{d['raw'][i,j]:.8g}", f"{d['I'][i,j]:.8g}"])
    with PdfPages(PREFIX.with_suffix(".pdf"), metadata={"Title": "Kapton weekend scattering vs exposure — addendum",
                  "Author": "SMI commissioning analysis", "Subject": "SAXS and WAXS per-frame reductions, October 22–26, 2026"}) as pdf:
        fig = page(1, "Scattering versus accumulated exposure", "Addendum to kapton_final_report_2026-10-26.pdf")
        note(fig, .845, "DATA RECOVERED AND REDUCED", 11)
        totals = provenance["patterns_included"]
        note(fig, .81, f"{len(audit)} recorded image sets: {provenance['patterns_reduced']['waxs']} WAXS and "
             f"{provenance['patterns_reduced']['saxs']} SAXS patterns reduced. "
             f"Exposure-series figures use {totals['waxs']} WAXS and {totals['saxs']} SAXS beam-confirmed patterns.")
        ax = fig.add_axes([.08, .57, .84, .17]); ax.axis("off")
        rows = [["1185420–1185481", "Oct 22", "WAXS", str(summary['early']['frames']),
                 f"{summary['early']['first_campaign_h']:.3f}–{summary['early']['last_campaign_h']:.3f}"],
                *[[k, "Oct 24–26" if k == "1185490" else "Oct 24", "SAXS + WAXS",
                   str(sum(f['included'] for f in audit if f['group'] == k)),
                   (f"{summary[k]['first_campaign_h']:.3f}–{summary[k]['last_campaign_h']:.3f}" if k in summary else "Dark only")]
                  for k in ("1185487", "1185489", "1185490")]]
        table = ax.table(cellText=rows, colLabels=["Scan ID(s)", "Acquired", "Detectors", "Accepted", "Campaign h"],
                         cellLoc="left", bbox=[0, 0, 1, 1], colWidths=[.25, .18, .23, .14, .20])
        table.auto_set_font_size(False); table.set_fontsize(8)
        note(fig, .52, "HOW TO READ THIS ADDENDUM", 11)
        dark_frames = [f for f in audit if f["detector_dark"] and not f["post_trip"]]
        dark_labels = ", ".join(f"{f['scan_id']} event {f['event']}" for f in dark_frames)
        note(fig, .485,
             "Pages 2–6 show exposure-colored waterfalls and all-frame change maps. Page 7 quantifies "
             "within-session changes without vertical offsets. Page 8 checks masks and geometry; page 9 records methods and scan IDs.\n\n"
             "The exposure coordinate is the campaign beam-on counter, including the documented +116.029 s early correction. "
             "Each session is compared to its own initial patterns. The first saved image already follows irradiation; it is not virgin Kapton. "
             "Friday’s approximately 8.88 h image-free irradiation interval cannot be reconstructed from scattering images.\n\n"
             "Eight post-trip frames in scan 1185487 are reduced for audit but excluded from exposure trends. "
             f"Also excluded: {len(dark_frames)} detector-dark sets ({dark_labels}), despite pre-trigger beam-on readings. "
             "Scans 1185419, 1185486 and 1185488 contain no primary images. Scans 1185482–1185485 are beam-down acceptance tests. "
             "The final incomplete attempt in 1185490 has no primary image and is omitted.")
        long = summary["1185490"]["metrics"]
        findings = "; ".join(f"{m['detector'].upper()} {m['q_band_A_inv'][0]:g}–{m['q_band_A_inv'][1]:g} Å⁻¹: "
                              f"{m['endpoint_change_percent']:+.1f}%" for m in long)
        broad_waxs = next(m for m in long if m["detector"] == "waxs" and m["q_band_A_inv"][0] == 1.)
        note(fig, .20, "LONG-SESSION ENDPOINT COMPARISON", 11)
        note(fig, .165, findings + ". Mean of last three versus first three, BPM3-normalized. "
             "Evolution is non-monotonic, with major steps across overnight beam gaps. "
             f"The last three broad-WAXS values have {broad_waxs['last_cv_percent']:.1f}% CV; "
             f"a single first/last pair instead gives {broad_waxs['single_endpoint_change_percent']:+.2f}%. "
             "These are observed scattering changes, not an isolated material-damage measurement; sample/beam drift and transmission changes may contribute.", 8.8)
        save_page(pdf, fig)
        for number, (key, detector) in enumerate((("early", "waxs"), ("1185487", "waxs"), ("1185487", "saxs"),
                                                 ("1185490", "waxs"), ("1185490", "saxs")), 2):
            waterfall_page(pdf, number, groups[key], detector)
        comparison_page(pdf, groups, summary)
        mask_page(pdf, groups)
        methods_page(pdf, groups, provenance)
    LOG.info("Wrote %s.pdf and supporting CSV/JSON", PREFIX)


def comparison_page(pdf, groups, summary):
    fig = page(7, "Quantifying the scattering change", "No waterfall offsets  |  Relative to each session’s first three accepted patterns")
    axes = [fig.add_axes([.12, .64, .79, .19]), fig.add_axes([.12, .365, .79, .19])]
    for ax, detector in zip(axes, ("waxs", "saxs")):
        for key, g in groups.items():
            if key == "1185489" or detector not in g["detectors"]:
                continue
            d = g["detectors"][detector]
            for j, band in enumerate(BANDS[detector]):
                y = band_values(d, band)
                ax.plot(g["hours"], 100 * (y / np.mean(y[:3]) - 1), color=COLORS[key],
                        ls=["-", "--", ":"][j], lw=1.2, label=f"{key if key != 'early' else 'Oct 22'}: {band[0]:g}–{band[1]:g} Å⁻¹")
        ax.axhline(0, color="#AAAAAA", lw=.6)
        ax.set_title(detector.upper() + " · q-band mean intensity change", loc="left", fontsize=11)
        ax.set_ylabel("ΔI / I₀ (%)", fontsize=9)
        ax.set_xlabel("Campaign beam-on exposure (h)", fontsize=9)
        axis_style(ax)
        ax.legend(loc="best", fontsize=6.7, ncol=2, framealpha=.85)
    ax = fig.add_axes([.08, .145, .84, .145]); ax.axis("off")
    rows = []
    for m in summary["1185490"]["metrics"]:
        rows.append([m["detector"].upper(), f"{m['q_band_A_inv'][0]:g}–{m['q_band_A_inv'][1]:g}",
                     f"{m['endpoint_change_percent']:+.2f}%", f"{m['raw_endpoint_change_percent']:+.2f}%",
                     f"{m['first_cv_percent']:.2f}% / {m['last_cv_percent']:.2f}%"])
    table = ax.table(cellText=rows, colLabels=["1185490", "q (Å⁻¹)", "BPM3 norm.", "Time norm. only", "CV first / last"],
                     cellLoc="left", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False); table.set_fontsize(7.3)
    note(fig, .11, "Large steps bracket overnight beam gaps (1185490 events 19→20 and 104→105). "
         "Endpoints average three frames each. CV is within-window scatter, not total measurement uncertainty. "
         "Curves are joined only within a session; q-band means use bins valid in every included frame. "
         "No background, transmission, polarization, or absolute-intensity calibration is applied.", 8)
    save_page(pdf, fig)


def mask_page(pdf, groups):
    from matplotlib.colors import LogNorm
    from smi_tiled import make_saxs_mask_from_spec
    from smi_tiled.defaults import resolve_mask_path
    from smi_tiled.integrator import make_waxs_mask_callable, rotate_image_and_mask
    g = groups["1185490"]
    meta = g["meta"][0]
    saxgeo, _ = geometry(meta)
    fig = page(8, "Detector and mask checks", "Scan 1185490  |  First / last accepted frames  |  Fixed scale within each detector")
    smask = make_saxs_mask_from_spec((1679, 1475), mask_path=resolve_mask_path(None, "saxs"),
                                    active_beamstop=saxgeo.active_beamstop, beamstop_pos_mm=saxgeo.beamstop_pos_mm,
                                    beam_center_px=(saxgeo.beam_center_row_px, saxgeo.beam_center_col_px))
    bsx = meta["primary"]["waxs_bsx"][0]
    wmask = make_waxs_mask_callable(resolve_mask_path(None, "waxs"), waxs_bsx_ref=bsx, beamstop_max_abs_arc_deg=None)
    for col, frame in enumerate((g["frames"][0], g["frames"][-1])):
        with np.load(ROOT / frame["file"], allow_pickle=False) as z:
            for row, detector in enumerate(("saxs", "waxs")):
                im = z[detector]
                if detector == "waxs":
                    mask = wmask(im.shape, 15, bsx)
                    im = rotate_image_and_mask(im, k=3)[0]
                else:
                    mask = smask
                ax = fig.add_axes([.08 + .45 * col, .54 - row * .31, .39, .27])
                artist = ax.imshow(np.ma.masked_where((im < 1) | ~mask, im), cmap="inferno",
                                   norm=LogNorm(1 if row == 0 else 400, 1e4 if row == 0 else 2e4), interpolation="nearest")
                ax.contour(mask, [.5], colors="#00CFD0", linewidths=.35)
                ax.set_title(f"{detector.upper()} · event {frame['event']} · {frame['campaign_beam_s']/3600:.2f} h", fontsize=9)
                ax.set_xticks([]); ax.set_yticks([])
                cb = fig.colorbar(artist, ax=ax, fraction=.035, pad=.025)
                cb.set_label("counts / 1 s", fontsize=7); cb.ax.tick_params(labelsize=7)
    note(fig, .18,
         f"SAXS: recorded pin beamstop, beam center (row, col) = ({saxgeo.beam_center_row_px:.2f}, {saxgeo.beam_center_col_px:.2f}) px; "
         f"corrected SDD = {saxgeo.dist_m:.4f} m. Cyan outlines show excluded pixels. Negative Pilatus sentinels are rejected; zero counts remain valid for integration.\n"
         "WAXS: 3-panel arc, 273 mm calibrated distance, arc approximately 15°. The saved bsx value is an overflow sentinel "
         "(−2147.483648 mm). The visible stationary shadow matches the unshifted bundled polygon; that fixed mask is used "
         "instead of applying a false motor-derived shift. The detector’s bundled bad-module and gap masks are retained.\n"
         "Post-trip events 28–35 of 1185487 retain substantial WAXS signal while SAXS is nearly dark. "
         "They are excluded by acquisition phase and are not used as dark-background references.", 8.5)
    save_page(pdf, fig)


def methods_page(pdf, groups, provenance):
    fig = page(9, "Methods, provenance and scan index", "Reproducible reduction  |  All data access is read-only  |  Full frame/UID mapping in the CSV")
    note(fig, .845, "REDUCTION", 11)
    note(fig, .81,
         "smi-tiled transmission integration: recorded 5999.9995 eV; flat Pilatus 2M SAXS geometry and folded 3-panel "
         "Pilatus 900KW WAXS geometry. SAXS uses recorded beam center and 9 m motor distance plus the package’s calibration corrections; "
         "WAXS uses the package calibration, including −4.5 px column delta and +0.08 px/degree arc term. "
         "2 × 2 pixel splitting; 700 SAXS / 1000 WAXS q bins; 180 azimuth bins; hot-pixel rejection threshold 3000, kernel 5. "
         "I(q) is a pixel-acceptance-weighted mean over the available azimuth, not a full-azimuth reconstruction. "
         "Package q values (nm⁻¹) are divided by 10 for Å⁻¹.\n\n"
         "Normalize by recorded detector acquisition time (1 s), pixel solid angle and pre-trigger incident BPM3 (multiply by 50/BPM3). "
         "Do not normalize by the downstream diode because that would absorb sample-transmission changes into the scaling. "
         "Detector efficiencies are not cross-calibrated, so SAXS and WAXS are displayed independently. "
         "Small arc-readback variations are regridded linearly within each detector; missing coverage remains blank.\n\n"
         "Comparisons are within sessions. Baseline sample-stage positions differ between October 22 and Saturday, and "
         "start/end piezo values vary during the long session. Per-frame sample positions were not recorded in primary. "
         "A scattering change therefore cannot be attributed uniquely to radiation chemistry or assigned a local dose from this record alone. "
         "Detector-dark rejection requires median WAXS = 0 and total nonnegative counts <10,000; raw totals and every exclusion are preserved in the audit CSV.", 8.6)
    note(fig, .46, "EXACT SCAN INDEX", 11)
    ids = [str(i) for i in range(1185420, 1185482)]
    note(fig, .43, "WAXS-only, one image each:\n" + "\n".join(", ".join(ids[i:i + 8]) for i in range(0, len(ids), 8)), 8.1)
    run_index = {m["scan_id"]: m for m in cached_runs()}
    note(fig, .28, "SAXS + WAXS (1185489 is detector-dark):\n" + "\n".join(
        f"{k}: {run_index[int(k)]['uid']}" for k in ("1185487", "1185489", "1185490")), 8.2)
    note(fig, .195, "REPRODUCTION AND FILES", 11)
    note(fig, .165,
         "From /home/xf12id/smi-tiled:\n"
         "pixi run python ../SWAXS_user_scripts/Commissioning/2026-10-22_kapton_air_exposure/scattering_addendum.py "
         "--apply --download --reduce --report\n"
         "Omit --download for offline reproduction. The addendum CSV identifies every acquired frame and its exposure; "
         "_iq.csv exports accepted profiles; logs/scattering_cache contains raw arrays, per-run reductions and geometry/mask hashes. "
         "The JSON records quantitative metrics and the immutable source database SHA-256. "
         "Analysis prepared with OpenCode (GPT-6 Astra).", 8.1)
    save_page(pdf, fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--reduce", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("fontTools").setLevel(logging.WARNING)
    if not args.apply:
        LOG.info("Preview: cache Kapton scans 1185420-1185490 in %s; reduce per-frame SAXS/WAXS and write %s.pdf", CACHE, PREFIX)
        return
    if args.download:
        download()
    if args.reduce:
        reduce_all()
    if args.report:
        render_report()


if __name__ == "__main__":
    main()

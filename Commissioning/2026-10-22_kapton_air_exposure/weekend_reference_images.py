"""Cache bounded first/last beam-on frames and scalar provenance from Tiled.

Preview by default; --apply writes only missing cache entries. No EPICS access.
SPDX-License-Identifier: BSD-3-Clause
"""

import argparse
import json
import logging
import time
from pathlib import Path

import httpx
import numpy as np
from tiled.client import from_uri

from tiled_images import retry

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "logs/weekend_image_cache"
RUNS = (
    (1185487, "fca35755-e42b-4d04-9d0b-8d2c57e96702"),
    (1185490, "3b958206-68d7-4659-9dac-164624aa3911"),
)


def read(node):
    result = retry(node.read)
    time.sleep(.15)
    return np.asarray(result)


def download():
    CACHE.mkdir(exist_ok=True)
    client = from_uri("https://tiled.nsls2.bnl.gov", timeout=httpx.Timeout(30, connect=5), max_connections=2)
    raw = client["smi"]["raw"]
    for scan_id, uid in RUNS:
        target = CACHE / f"{scan_id}.json"
        if target.exists():
            logging.info("Cached scan %s", scan_id)
            continue
        run = retry(lambda: raw[uid])
        start, stop = dict(run.metadata["start"]), dict(run.metadata.get("stop") or {})
        data = run["primary"]["data"]
        fields = ("kapton_image_id", "kapton_trigger_wall", "kapton_beam_s", "kapton_online_beam_s",
                  "kapton_beam_end_s", "kapton_post_trip", "waxs_arc")
        scalars = {key: read(data[key]).tolist() for key in fields}
        eligible = np.flatnonzero(np.asarray(scalars["kapton_post_trip"]) == 0)
        indices = [int(eligible[0]), int(eligible[-1])]
        selected = []
        for index in indices:
            file = CACHE / f"{scan_id}_{index}.npz"
            if not file.exists():
                arrays = {}
                for name, key in (("waxs", "pil900KW_image"), ("saxs", "pil2M_image"), ("oav", "OAV_writing_image")):
                    node = data[key]
                    shape = node.structure().shape
                    if np.prod(shape[1:]) > 30_000_000:
                        raise ValueError(f"Frame too large: {key} {shape}")
                    arrays[name] = np.squeeze(np.asarray(retry(lambda: node[index:index+1])))
                    logging.info("Scan %s frame %s %s %s", scan_id, index+1, name, arrays[name].shape)
                    time.sleep(.2)
                np.savez_compressed(file, **arrays)
            selected.append({"index": index, "event_number": index+1, "file": file.name,
                             **{k: v[index] for k, v in scalars.items()}})
        baseline = run["baseline"]["data"]
        names = ("time", "piezo_x", "piezo_y", "piezo_z", "energy_energy", "waxs_arc",
                 "stage_x", "stage_y", "stage_z", "saxs_beamstop_x_pin", "saxs_beamstop_y_pin")
        base = {key: read(baseline[key]).tolist() for key in names if key in baseline}
        descriptors = list(run["primary"].metadata["descriptors"])
        # Detector configuration is small metadata, not image data.
        configuration = [d.get("configuration", {}) for d in descriptors]
        summary = run["session_summary"]["data"]
        session = {key: read(summary[key]).tolist() for key in summary}
        scalar_desc = list(run["scalars"].metadata["descriptors"])
        diode_description = [d.get("data_keys", {}).get("diode", {}) for d in scalar_desc]
        meta = {"scan_id": scan_id, "uid": uid, "start": start, "stop": stop,
                "frames": selected, "baseline": base, "configuration": configuration,
                "session_summary": session, "diode_description": diode_description}
        target.write_text(json.dumps(meta, indent=2))
        logging.info("Saved scan %s: %s", scan_id, selected)


def load_cached():
    """Return metadata only when both frame files are present for a run."""
    result = []
    for scan_id, _ in RUNS:
        path = CACHE / f"{scan_id}.json"
        if path.exists():
            meta = json.loads(path.read_text())
            if all((CACHE / f["file"]).exists() for f in meta["frames"]):
                result.append(meta)
    return result


def render_pages(pdf, metadata, page_start, total_pages, figure_header, save_page):
    from matplotlib.colors import LogNorm
    from matplotlib import pyplot as plt
    from tiled_images import yellowhot
    from overnight_report import local, duration

    scale = json.loads((ROOT / "movie_scale.json").read_text())
    for page_index, meta in enumerate(metadata):
        scan = meta["scan_id"]
        title = "Saturday: first low-pressure run" if scan == 1185487 else "Saturday–Monday: second long session"
        fig = figure_header(page_start+page_index,title,
                            f"Scan {scan} | First / last pre-trip images | Same WAXS count scale and original OAV RGB",total_pages)
        for col, frame in enumerate(meta["frames"]):
            x = .08 + .46*col
            fig.text(x,.84,"BEFORE" if col==0 else "AFTER",fontsize=12,weight="bold",color="#008C95")
            fig.text(x,.81,local(frame["kapton_trigger_wall"])+" EDT",fontsize=10)
            fig.text(x,.785,f"Event {frame['event_number']} | Campaign counter:",fontsize=9)
            fig.text(x,.763,duration(frame["kapton_beam_s"]),fontsize=10,weight="bold")
            with np.load(CACHE/frame["file"],allow_pickle=False) as arrays:
                ax=fig.add_axes([x,.52,.38,.19]);ax.set_axis_off()
                cmap=yellowhot();cmap.set_bad("black")
                image=ax.imshow(np.ma.masked_less_equal(arrays["waxs"],0),cmap=cmap,
                                norm=LogNorm(scale["vmin"],scale["vmax"],clip=True),interpolation="nearest")
                ax.set_title("WAXS | 1 s | arc 15°",fontsize=10)
                ax=fig.add_axes([x,.235,.38,.24]);ax.set_axis_off()
                ax.imshow(arrays["oav"],interpolation="nearest")
                ax.set_title("On-axis view | original RGB",fontsize=10)
        cax=fig.add_axes([.22,.535,.56,.012])
        cb=fig.colorbar(image,cax=cax,orientation="horizontal")
        cb.set_label(f"Fixed log counts: {scale['vmin']:,.0f}–{scale['vmax']:,.1f} (same as October 22)",fontsize=8)
        cb.ax.tick_params(labelsize=7)
        first,last=meta["frames"]
        additional=last["kapton_beam_s"]-first["kapton_beam_s"]
        explanation=(f"Beam-counter increment between displayed frames: {duration(additional)}. Both exposures resolve through Tiled. "
                     "'Before' is the first image in this run, not virgin Kapton. Counter labels are campaign-wide and do not imply all prior exposure reached this position. "
                     "No per-frame intensity normalization, color rescaling or image registration is applied. "
                     "Nonpositive WAXS pixels are masked; bright values above the fixed scale saturate visually.")
        if scan==1185487:
            explanation += " Last pre-trip event 27 is used; events 28–35 were taken after boundary isolation."
        else:
            explanation += " Event 113 is the final completed set; the later 06:21 attempt timed out and is excluded."
        fig.text(.08,.19,explanation,fontsize=9,va="top",linespacing=1.4)
        fig.text(.08,.085,f"Tiled UID: {meta['uid']}",fontsize=8,color="#657584")
        save_page(pdf,fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    if args.apply:
        download()
    else:
        logging.info("Would cache first/last pre-trip SAXS, WAXS, OAV for %s in %s", RUNS, CACHE)

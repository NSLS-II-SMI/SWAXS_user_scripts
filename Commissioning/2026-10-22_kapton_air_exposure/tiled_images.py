"""Download one WAXS/OAV frame per returned run from Tiled; render compact movies.

Uses public Tiled APIs only. --apply downloads/writes; --render uses cached frames.
SPDX-License-Identifier: BSD-3-Clause
"""

import argparse
import json
import logging
import subprocess
import sys
import time

import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.animation import FFMpegWriter
from tiled.client import from_uri

from overnight_report import DATABASE, ROOT, analyze, duration, load, local

log = logging.getLogger(__name__)
CACHE = ROOT / "logs/image_cache"


def retry(call):
    for attempt in range(3):
        try:
            return call()
        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == 2:
                raise
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 429 and exc.response.status_code < 500:
                raise
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def download(client):
    samples, images, _, _, _ = load(DATABASE)
    data = analyze(samples, images)
    runs = data["saved"]
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, image in enumerate(runs):
        uid = image["run_uid"]
        path = CACHE / f"{uid}.npz"
        mdpath = CACHE / f"{uid}.json"
        if path.exists() and mdpath.exists():
            manifest.append(json.loads(mdpath.read_text()))
            continue
        run = retry(lambda uid=uid: client["smi"]["raw"][uid])
        start = dict(run.metadata["start"])
        stop = dict(run.metadata.get("stop", {}))
        stream = run["primary"]["data"]
        keys = list(stream)
        arrays = {}
        for detector, prefix in (("waxs", "pil900KW"), ("oav", "OAV_writing")):
            candidates = [key for key in keys if key.startswith(prefix) and "image" in key.lower()]
            if len(candidates) != 1:
                raise ValueError(f"{uid}: image field for {detector} ambiguous: {candidates}; keys={keys}")
            node = stream[candidates[0]]
            shape = tuple(node.structure().shape)
            log.info("%s %s shape=%s", uid[:8], candidates[0], shape)
            if np.prod(shape) > 30_000_000:
                raise ValueError(f"Unexpected large image array {shape}; inspect before downloading")
            arrays[detector] = np.squeeze(np.asarray(retry(node.read)))
            time.sleep(.15)
        stamp = image["start"]["wall"]
        correction = float(np.interp(stamp, data["t"], np.cumsum(data["correction"])))
        meta = {"uid": uid, "scan_id": start.get("scan_id"), "wall": stamp,
                "local_time": local(stamp), "online_beam_s": image["start"]["totals"]["beam_s"],
                "corrected_beam_s": image["start"]["totals"]["beam_s"] + correction,
                "exit_status": stop.get("exit_status"), "sample_name": start.get("sample_name"),
                "image_audit_status": image["status"], "keys": keys}
        np.savez_compressed(path, **arrays)
        mdpath.write_text(json.dumps(meta, indent=2))
        manifest.append(meta)
        log.info("Cached %d/%d: scan %s at %s", i+1, len(runs), meta["scan_id"], meta["local_time"])
        time.sleep(.2)
    (CACHE / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def yellowhot():
    return colors.LinearSegmentedColormap.from_list("yellowhot", ["#000000", "#7D1D00", "#D94D00", "#FFB900", "#FFFF40", "#FFFFFF"])


def render():
    manifest = json.loads((CACHE / "manifest.json").read_text())
    # Fixed global 99.8th percentile of positive pixels, sampled across every frame.
    pixels = []
    for row in manifest:
        with np.load(CACHE / f"{row['uid']}.npz") as frames:
            w = frames["waxs"]
            sample = w.ravel()[::25]
            pixels.append(sample[np.isfinite(sample) & (sample > 0)])
    distribution = np.concatenate(pixels)
    vmin = max(1, float(np.percentile(distribution, 1)))
    vmax = max(vmin * 2, float(np.percentile(distribution, 99.8)))
    norm = colors.LogNorm(vmin=vmin, vmax=vmax, clip=True)
    scale = {"cmap": "yellowhot (black-red-orange-yellow-white)", "normalization": "log",
             "vmin": vmin, "vmax": vmax, "method": "global sampled positive-pixel 1st / 99.8th percentiles",
             "fps": 5, "frames": len(manifest)}
    (ROOT / "movie_scale.json").write_text(json.dumps(scale, indent=2))
    for detector in ("waxs", "oav"):
        output = ROOT / f"kapton_{detector}_2026-10-22.mp4"
        # Render explicitly regenerates derived movies from immutable cached arrays.
        fig, ax = plt.subplots(figsize=(9.6, 7.2), facecolor="#0C1722")
        fig.subplots_adjust(left=.04, right=.92, bottom=.08, top=.84)
        ax.set_facecolor("black")
        ax.set_axis_off()
        fig.text(.045, .945, f"KAPTON  /  {'WAXS • LOG YELLOW-HOT' if detector == 'waxs' else 'ON-AXIS VIEW'}",
                         color="#51CED1", fontsize=14, weight="bold")
        label = fig.text(.045, .887, "", color="white", fontsize=13)
        footer = fig.text(.045, .035, "", color="#BDCAD5", fontsize=10)
        with np.load(CACHE / f"{manifest[0]['uid']}.npz") as frames:
            first = frames[detector]
        artist = ax.imshow(np.ma.masked_less_equal(first, 0) if detector == "waxs" else first,
                           cmap=yellowhot() if detector == "waxs" else "gray",
                           norm=norm if detector == "waxs" else None, interpolation="nearest")
        if detector == "waxs":
            bar = fig.colorbar(artist, ax=ax, fraction=.04, pad=.025)
            bar.set_label("counts · fixed log scale", color="white")
            bar.ax.tick_params(colors="white")
        matplotlib.rcParams["animation.ffmpeg_path"] = sys.prefix + "/bin/ffmpeg"
        writer = FFMpegWriter(fps=5, codec="libx264", extra_args=["-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
        with writer.saving(fig, str(output), dpi=100):
            for i, row in enumerate(manifest):
                with np.load(CACHE / f"{row['uid']}.npz") as frames:
                    image = frames[detector]
                artist.set_data(np.ma.masked_less_equal(image, 0) if detector == "waxs" else image)
                label.set_text(f"{row['local_time']} EDT   |   Beam on: {duration(row['corrected_beam_s'])}")
                gap = row["wall"]-manifest[i-1]["wall"] if i else 0
                footer.set_text(f"Scan {row['scan_id']}   •   Frame {i+1}/{len(manifest)}   •   "
                                + (f"{gap/60:.1f} min since prior frame" if i else "First saved frame")
                                + "\nBeam total includes 116.03 s early photon-alarm correction; not real-time playback")
                writer.grab_frame()
                if i in (0, len(manifest)-1):
                    fig.savefig(ROOT / f"{detector}_{'before' if i == 0 else 'after'}.png", dpi=130, facecolor=fig.get_facecolor())
        plt.close(fig)
        probe = subprocess.run([sys.prefix + "/bin/ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                                "-of", "json", str(output)], check=True, capture_output=True, text=True)
        log.info("%s: %s", output, probe.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--login", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("fontTools").setLevel(logging.WARNING)
    if not args.apply:
        log.info("Preview: download 62 returned WAXS/OAV runs to %s; --apply to proceed", CACHE)
        return
    if not args.render:
        client = from_uri("https://tiled.nsls2.bnl.gov", timeout=httpx.Timeout(30, connect=5))
        download(client)
    render()


if __name__ == "__main__":
    main()

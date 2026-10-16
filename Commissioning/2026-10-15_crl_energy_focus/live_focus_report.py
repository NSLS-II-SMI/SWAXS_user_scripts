"""Live cross-holder focus report for crl_focus_series.

A bluesky subscription that, as each fine energy sweep finishes, characterises that
holder (derivative-FWHM vs energy, same convention as analyze_1170759.py) and rewrites
ONE self-refreshing HTML file. Keep a single browser tab open on that file:// path; it
reloads itself every ``refresh_s`` seconds, so no new page is opened per sweep.

This module is NOT imported by crl_focus_series at load time (that keeps the plan script
import-clean and offline-testable). crl_focus_series imports it lazily only when a
``report_path`` is requested. Bokeh/smi_plans.analysis are imported inside the handlers.

The document handlers never raise into the RunEngine: a plotting/analysis error logs a
warning and leaves acquisition untouched.
"""

import os

import numpy as np
from bluesky.callbacks.core import CallbackBase

FINE_SCAN_NAME = "crl_energy_focus_commissioning"
_COLORS = ["#105C78", "#769E2D", "#B24700", "#5B2C83", "#A6093D", "#00704A"]


class LiveFocusReport(CallbackBase):
    """Overwrite ``path`` with a live FWHM-vs-energy report after each fine sweep."""

    def __init__(self, path, *, refresh_s=15):
        self.path = os.fspath(path)
        self.refresh_s = int(refresh_s)
        self._active = False
        self._md = {}
        self._rows = []        # buffered (energy_setpoint_eV, piezo_x_um, stats1_total)
        self._holders = []     # accumulated per-holder characterisations

    # --- document handlers (must never raise into the RunEngine) ---------------
    def start(self, doc):
        self._active = doc.get("scan_name") == FINE_SCAN_NAME
        if self._active:
            self._md = dict(doc)
            self._rows = []

    def event(self, doc):
        if not self._active:
            return
        d = doc.get("data", {})
        self._rows.append((d.get("energy_energy_setpoint"),
                           d.get("piezo_x"), d.get("pil2M_stats1_total")))

    def stop(self, doc):
        if not self._active:
            return
        self._active = False
        try:
            self._holders.append(self._characterize(self._md, self._rows))
            self._write_html()
            print("live focus report updated: {}".format(self.path))
        except Exception as exc:  # noqa: BLE001 - a plotting error must not abort acquisition
            print("live focus report skipped this sweep: {}: {}".format(
                type(exc).__name__, exc))

    def rebuild_from_rows(self, md, rows):
        """Append one sweep from (md, rows) and rewrite the page; rows are (e_eV, x, total).

        Used by rebuild_live_report.py to regenerate the page from completed Tiled runs.
        """
        self._holders.append(self._characterize(md, rows))
        self._write_html()

    @staticmethod
    def _fwhm_for_energy(x, y):
        """Derivative FWHM at one energy (analyze_1170759 convention), or nan if unusable."""
        from smi_plans.analysis import analyze_xy

        if len(x) < 5:
            return float("nan")
        dx = np.diff(x)
        if not np.all(dx > 0):
            return float("nan")
        res = analyze_xy((x[1:] + x[:-1]) / 2, np.diff(y) / dx,
                         yerr=np.sqrt(np.maximum(y[1:], 1) + np.maximum(y[:-1], 1)) / dx,
                         model="none", profile="peak", x_sigma=0,
                         motor="piezo_x (µm)", detector="d(counts)/dx")
        res.derivative = True
        half = res.baseline + (max(res.y) - res.baseline) / 2
        complete = res.y[0] < half and res.y[-1] < half and np.isfinite(res.fwhm)
        return float(res.fwhm) if complete else float("nan")

    # --- analysis (same derivative-FWHM convention as analyze_1170759.py) -------
    def _characterize(self, md, rows_raw):
        rows = [r for r in rows_raw if all(v is not None for v in r)]
        arr = np.asarray(rows, dtype=float)
        if arr.size == 0:
            raise ValueError("no complete (energy, piezo_x, total) rows in sweep")
        energies, xs, ys = arr[:, 0], arr[:, 1], arr[:, 2]
        energy_keV, fwhm_um = [], []
        for e in np.unique(energies):
            sel = energies == e
            order = np.argsort(xs[sel])
            x, y = xs[sel][order], ys[sel][order]
            try:
                w = self._fwhm_for_energy(x, y)
            except Exception:  # noqa: BLE001 - one bad energy must not drop the whole sweep
                w = float("nan")
            energy_keV.append(float(e) / 1000)
            fwhm_um.append(w)
        fwhm = np.asarray(fwhm_um)
        ekeV = np.asarray(energy_keV)
        best = {"energy_keV": float("nan"), "fwhm_um": float("nan")}
        if np.isfinite(fwhm).any():
            k = int(np.nanargmin(fwhm))
            best = {"energy_keV": float(ekeV[k]), "fwhm_um": float(fwhm[k])}
        mf = md.get("model_focus_eV")
        label = "+".join(str(i) for i in md.get("crl_holders", [])) or "?"
        return {"label": "holder {}".format(label),
                "energy_keV": energy_keV, "fwhm_um": fwhm_um,
                "model_focus_keV": (float(mf) / 1000) if mf else float("nan"),
                "edge_um": md.get("coarse_edge_center_um"),
                "best": best}

    # --- rendering -------------------------------------------------------------
    def _write_html(self):
        from bokeh.embed import file_html
        from bokeh.layouts import column
        from bokeh.models import ColumnDataSource, Div, HoverTool
        from bokeh.plotting import figure
        from bokeh.resources import INLINE

        p = figure(width=660, height=430, title="CRL focus vs energy (live)",
                   x_axis_label="Energy (keV)", y_axis_label="Derivative FWHM (µm)",
                   tools="pan,wheel_zoom,box_zoom,reset,save",
                   background_fill_color="#F2F5F7")
        rows_html = []
        for i, h in enumerate(self._holders):
            color = _COLORS[i % len(_COLORS)]
            src = ColumnDataSource(dict(energy_keV=h["energy_keV"], fwhm_um=h["fwhm_um"]))
            p.line("energy_keV", "fwhm_um", source=src, color=color, line_width=2,
                   legend_label=h["label"])
            dots = p.scatter("energy_keV", "fwhm_um", source=src, color=color, size=7,
                             legend_label=h["label"])
            p.add_tools(HoverTool(renderers=[dots], tooltips=[
                ("holder", h["label"]), ("energy", "@energy_keV{0.000} keV"),
                ("FWHM", "@fwhm_um{0.00} µm")]))
            b = h["best"]
            edge = "" if h["edge_um"] is None else "{:.1f}".format(h["edge_um"])
            rows_html.append(
                "<tr><td>{}</td><td>{:.3f}</td><td>{:.3f}</td><td>{:.2f}</td><td>{}</td></tr>"
                .format(h["label"], h["model_focus_keV"], b["energy_keV"], b["fwhm_um"], edge))
        if self._holders:
            p.legend.location = "top_center"
            p.legend.click_policy = "hide"
        table = ("<table border='1' cellpadding='4' style='border-collapse:collapse'>"
                 "<tr><th>holder</th><th>model focus (keV)</th><th>best energy (keV)</th>"
                 "<th>best FWHM (µm)</th><th>edge (µm)</th></tr>"
                 + "".join(rows_html) + "</table>")
        header = Div(text=(
            "<h2>CRL energy-focus commissioning &mdash; live</h2>"
            "<p>{} sweep(s) complete. Page refreshes every {}s.</p>{}"
        ).format(len(self._holders), self.refresh_s, table))
        html = file_html(column(header, p), INLINE, "CRL live focus")
        html = html.replace(
            "<head>",
            '<head>\n  <meta http-equiv="refresh" content="{}">'.format(self.refresh_s), 1)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(html)
        os.replace(tmp, self.path)  # atomic overwrite of the single page

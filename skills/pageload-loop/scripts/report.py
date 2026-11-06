#!/usr/bin/env python3
"""Report for a Pageload Loop: report.html (self-contained) and report.md (PR body).

Reads runs.jsonl (written by compare.py log) and the filmstrips it points to.
Python 3.8+, standard library only. Run it after every iteration; the HTML
reloads itself every 60 seconds while --status is running.

Usage:
  report.py --runs-jsonl .pageload/runs.jsonl --out-dir .pageload
            [--title TEXT] [--goal "mobile:lcp<=2500" | "lcp-20%"] [--status running|finished]
            [--notes .pageload/notes.md] [--primary lcp] [--a11y .pageload/runs/final/a11y.json]

Goal syntax: [profile:]lcp<=MS (final median at or under MS on every chosen page) or
[profile:]lcp-PCT% (confirmed improvement of at least PCT% on every chosen page).
Without a profile prefix the goal applies to every profile.
--a11y takes the diff written by compare.py a11y and adds an accessibility section.
"""
import argparse
import html
import json
import re
import statistics
from pathlib import Path

C = {  # roles, from the dataviz reference palette
    "kept": "var(--series-1)", "base": "var(--muted)", "rejected": "var(--rejected)",
}
CSS = """
:root{color-scheme:light;--bg:#fcfcfb;--card:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;
--line:#e6e5e0;--band:#2a78d61f;--series-1:#2a78d6;--rejected:#b9b8b2;--good:#008300;--bad:#c4342f;--mono:ui-monospace,SFMono-Regular,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#1a1a19;--card:#232321;
--ink:#ffffff;--ink2:#c3c2b7;--muted:#8f8e86;--line:#383835;--band:#3987e526;--series-1:#3987e5;--rejected:#5c5b56;--good:#3fae3f;--bad:#e66767}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--card:#232321;--ink:#ffffff;--ink2:#c3c2b7;--muted:#8f8e86;
--line:#383835;--band:#3987e526;--series-1:#3987e5;--rejected:#5c5b56;--good:#3fae3f;--bad:#e66767}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 12px}
h3{font-size:15px;margin:16px 0 8px}.sub{color:var(--ink2);margin:0 0 20px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{color:var(--ink2);font-size:13px}.card .v{font-size:21px;font-weight:600;font-variant-numeric:tabular-nums}
.card .d{font-variant-numeric:tabular-nums}.good{color:var(--good)}.bad{color:var(--bad)}.mutedt{color:var(--ink2)}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;border:1px solid var(--line)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
svg{width:100%;height:auto;display:block}svg text{fill:var(--ink2);font-size:11px;font-family:inherit}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin:4px 0 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--ink2);font-weight:600}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}code{font-family:var(--mono);font-size:12px}
.film{display:flex;gap:4px;overflow-x:auto;padding-bottom:4px}.film figure{margin:0;flex:0 0 auto;text-align:center}
.film img{height:120px;border:1px solid var(--line);border-radius:4px;display:block}.film figcaption{font-size:11px;color:var(--ink2)}
ul.notes li{margin:4px 0}
"""


def median(xs):
    return statistics.median(xs) if xs else None


def esc(s):
    return html.escape(str(s if s is not None else ""))


def fmt_ms(v):
    return "–" if v is None else f"{v:,.0f} ms"


def fmt_delta(d, pct=None):
    if d is None:
        return "–"
    s = f"{d:+,.0f} ms".replace("-", "−")
    if pct is not None:
        s += f" ({pct:+.1%})".replace("-", "−")
    return s


def fmt_p(p):
    return "p<0.0001" if p < 0.0001 else f"p={p:.4f}"


def load_lines(p):
    out = []
    for ln in Path(p).read_text().splitlines():
        ln = ln.strip()
        if ln:
            out.append(json.loads(ln))
    return out


def iter_key(it):
    try:
        return (0, float(it))
    except (TypeError, ValueError):
        return (1, 0.0)


# ---------- data model ----------

def build(lines, primary):
    cells = sorted({(l["page"], l["profile"]) for l in lines if l["page"] != "*"})
    baseline = [l for l in lines if l["kind"] == "baseline"]
    confirm = [l for l in lines if l["kind"] == "confirm"]
    iters = {}
    for l in lines:
        if l["kind"] != "iteration":
            continue
        # A retry (14 runs) comes after the first measurement of the same iteration; the last one decides.
        d = iters.setdefault(str(l["iter"]), {"lines": [], "ts": []})
        if l["ts"] not in d["ts"]:
            d["ts"].append(l["ts"])
        d["lines"].append(l)
    for it, d in iters.items():
        last = d["ts"][-1]
        d["final"] = [l for l in d["lines"] if l["ts"] == last]
        d["retried"] = len(d["ts"]) > 1
        f0 = d["final"][0]
        d.update(decision=f0["decision"], reason=f0["reason"], hypothesis=f0["hypothesis"], commit=f0["commit"],
                 changes=f0.get("changes") or [], visual=f0.get("visual"), visual_ratio=f0.get("visual_ratio"),
                 n_runs=f0.get("n_runs"))
    order = sorted(iters, key=iter_key)
    return cells, baseline, confirm, iters, order


def runs_of(lines, page, profile, primary, role=None, variant=None):
    vals = []
    for l in lines:
        if l["page"] == page and l["profile"] == profile and (role is None or l.get("role") == role) \
                and (variant is None or l["variant"] == variant):
            vals += l["runs"].get(primary, [])
    return vals


def cell_line(lines, page, profile, role):
    for l in lines:
        if l["page"] == page and l["profile"] == profile and l.get("role") == role:
            return l
    return None


# ---------- charts ----------

def iteration_chart(page, profile, baseline, iters, order, confirm, primary):
    W, H, L, R, T, B = 640, 260, 56, 16, 14, 34
    pts, base_pts = [], []
    b0 = runs_of(baseline, page, profile, primary)
    nf0 = (baseline[0]["noise_floor"] or {}).get(primary) if baseline else None
    if b0:
        base_pts.append((0, median(b0), nf0 or 0))
    for i, it in enumerate(order, start=1):
        d = iters[it]
        b, c = cell_line(d["final"], page, profile, "base"), cell_line(d["final"], page, profile, "cand")
        if b:
            base_pts.append((i, b["medians"].get(primary), (b.get("noise_floor") or {}).get(primary) or 0))
        if c:
            pts.append((i, c["medians"].get(primary), d["decision"], it, c.get("delta"), c.get("p_value"), d["hypothesis"]))
    conf = None
    xmax = len(order) + (1 if confirm else 0)
    if confirm:
        c = cell_line(confirm, page, profile, "cand")
        if c:
            conf = (xmax, c["medians"].get(primary))
    ys = [p[1] for p in pts if p[1] is not None] + [p[1] + p[2] for p in base_pts if p[1] is not None] + \
         [p[1] - p[2] for p in base_pts if p[1] is not None] + ([conf[1]] if conf else [])
    if not ys:
        return "<p class='mutedt'>No data yet.</p>"
    lo, hi = min(ys), max(ys)
    pad = max((hi - lo) * 0.12, 20)
    lo, hi = max(0, lo - pad), hi + pad
    xs = lambda i: L + (W - L - R) * (i / max(xmax, 1))
    ysc = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(primary.upper())} per iteration, {esc(page)} {esc(profile)}">']
    for k in range(5):  # recessive grid
        v = lo + (hi - lo) * k / 4
        y = ysc(v)
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>'
                   f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end">{v:,.0f}</text>')
    # Noise band around the baseline each candidate was compared with.
    if base_pts:
        band = [(xs(i), ysc(m + n), ysc(m - n)) for i, m, n in base_pts if m is not None]
        if len(band) == 1:
            x, y1, y2 = band[0]
            band = [(x - 6, y1, y2), (x + 6, y1, y2)]
        poly = " ".join(f"{x:.1f},{y1:.1f}" for x, y1, _ in band) + " " + \
               " ".join(f"{x:.1f},{y2:.1f}" for x, _, y2 in reversed(band))
        out.append(f'<polygon points="{poly}" fill="var(--band)"/>')
        line = " ".join(f"{xs(i):.1f},{ysc(m):.1f}" for i, m, _ in base_pts if m is not None)
        out.append(f'<polyline points="{line}" fill="none" stroke="var(--muted)" stroke-width="2" stroke-dasharray="4 3"/>')
        i0, m0, _ = base_pts[0]
        out.append(f'<circle cx="{xs(i0):.1f}" cy="{ysc(m0):.1f}" r="5" fill="var(--muted)"><title>Baseline median {m0:,.0f} ms</title></circle>')
    for i, m, dec, it, delta, p, hyp in pts:
        if m is None:
            continue
        x, y = xs(i), ysc(m)
        tip = esc(f"Iteration {it}: {hyp}\n{dec}, median {m:,.0f} ms, Δ {fmt_delta(delta)}" + (f", p={p:.3f}" if p is not None else ""))
        if dec == "keep":
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{C["kept"]}" stroke="var(--card)" stroke-width="2"><title>{tip}</title></circle>')
        elif dec == "inconclusive":
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="none" stroke="var(--muted)" stroke-width="2"><title>{tip}</title></circle>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{C["rejected"]}"><title>{tip}</title></circle>')
        out.append(f'<rect x="{x - 10:.1f}" y="{T}" width="20" height="{H - T - B}" fill="transparent"><title>{tip}</title></rect>')
    if conf and conf[1] is not None:
        x, y = xs(conf[0]), ysc(conf[1])
        out.append(f'<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" rx="2" fill="{C["kept"]}"><title>Confirmation run: final median {conf[1]:,.0f} ms</title></rect>')
    for i in range(xmax + 1):
        lab = "base" if i == 0 else ("final" if confirm and i == xmax else str(order[i - 1]))
        out.append(f'<text x="{xs(i):.1f}" y="{H - 12}" text-anchor="middle">{esc(lab)}</text>')
    out.append(f'<text x="{L}" y="{H - 1}" >iteration</text></svg>')
    out.append('<div class="legend"><span><i style="background:var(--muted)"></i>baseline median (dashed) with noise band</span>'
               '<span><i style="background:var(--series-1)"></i>kept</span><span><i style="background:var(--rejected)"></i>rejected</span>'
               '<span><i style="border:2px solid var(--muted);background:none"></i>inconclusive</span>'
               + ('<span><i style="background:var(--series-1);border-radius:2px"></i>confirmation run</span>' if conf else "") + '</div>')
    return "".join(out)


def strip_plot(page, profile, baseline, iters, order, confirm, primary):
    rows = []
    if baseline:
        va = sorted({l["variant"] for l in baseline})
        rows.append(("A/A", runs_of(baseline, page, profile, primary, variant=va[0]),
                     runs_of(baseline, page, profile, primary, variant=va[-1]), "baseline"))
    for it in order:
        d = iters[it]
        rows.append((f"iter {it}", runs_of(d["final"], page, profile, primary, role="base"),
                     runs_of(d["final"], page, profile, primary, role="cand"), d["decision"]))
    if confirm:
        rows.append(("final", runs_of(confirm, page, profile, primary, role="base"),
                     runs_of(confirm, page, profile, primary, role="cand"), "keep"))
    vals = [v for _, b, c, _ in rows for v in b + c]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    pad = max((hi - lo) * 0.05, 5)
    lo, hi = lo - pad, hi + pad
    W, L, R, rowh = 640, 64, 16, 26
    H = 24 + rowh * len(rows) + 20
    xs = lambda v: L + (W - L - R) * (v - lo) / (hi - lo)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Individual runs, {esc(page)} {esc(profile)}">']
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        out.append(f'<line x1="{xs(v):.1f}" x2="{xs(v):.1f}" y1="14" y2="{H - 20}" stroke="var(--line)"/>'
                   f'<text x="{xs(v):.1f}" y="{H - 6}" text-anchor="middle">{v:,.0f}</text>')
    for r, (lab, b, c, dec) in enumerate(rows):
        y = 24 + r * rowh
        out.append(f'<text x="{L - 8}" y="{y + 8}" text-anchor="end">{esc(lab)}</text>')
        col = C["kept"] if dec in ("keep", "baseline") else C["rejected"]
        for j, v in enumerate(b):
            out.append(f'<circle cx="{xs(v):.1f}" cy="{y:.1f}" r="4" fill="var(--muted)" opacity=".8"><title>{esc(lab)} baseline run {j + 1}: {v:,.0f} ms</title></circle>')
        for j, v in enumerate(c):
            out.append(f'<circle cx="{xs(v):.1f}" cy="{y + 9:.1f}" r="4" fill="{col}"><title>{esc(lab)} candidate run {j + 1}: {v:,.0f} ms</title></circle>')
        for vals_, dy in ((b, 0), (c, 9)):
            if vals_:
                mx = xs(median(vals_))
                out.append(f'<line x1="{mx:.1f}" x2="{mx:.1f}" y1="{y + dy - 6:.1f}" y2="{y + dy + 6:.1f}" stroke="var(--ink)" stroke-width="2"/>')
    out.append("</svg>")
    out.append('<div class="legend"><span><i style="background:var(--muted)"></i>baseline runs (upper dot row; A/A: first server)</span>'
               '<span><i style="background:var(--series-1)"></i>candidate runs, kept</span>'
               '<span><i style="background:var(--rejected)"></i>candidate runs, rejected</span><span>| = median</span></div>')
    return "".join(out)


def load_strips(root, line_list, page, profile, variant_pick):
    for l in line_list:
        f = l.get("filmstrip_file")
        if not f or l["page"] != page or l["profile"] != profile:
            continue
        p = Path(f) if Path(f).is_absolute() else root / f
        if not p.exists():
            continue
        try:
            strips = json.loads(p.read_text())
        except ValueError:
            continue
        variants = [s["variant"] for s in strips if s["page"] == page and s["profile"] == profile]
        want = variant_pick(variants)
        for s in strips:
            if s["page"] == page and s["profile"] == profile and s["variant"] == want:
                return s
    return None


def film_html(strip, label):
    if not strip or not strip.get("frames"):
        return f"<p class='mutedt'>{esc(label)}: no filmstrip recorded.</p>"
    figs = "".join(f'<figure><img alt="{esc(label)} at {f["timing"]} ms" src="{f["data"]}"><figcaption>{f["timing"]:,} ms</figcaption></figure>'
                   for f in strip["frames"])
    return f"<h3>{esc(label)}</h3><div class='film'>{figs}</div>"


# ---------- goal and notes ----------

def parse_goal(g):
    if not g:
        return None
    m = re.match(r"^(?:(mobile|desktop):)?(\w+)\s*(<=\s*([\d.]+)|-\s*([\d.]+)%)$", g.replace(" ", ""))
    if not m:
        return {"text": g, "bad": True}
    return {"text": g, "profile": m.group(1), "metric": m.group(2),
            "max_ms": float(m.group(4)) if m.group(4) else None, "pct": float(m.group(5)) / 100 if m.group(5) else None}


def summary_rows(cells, baseline, iters, order, confirm, primary):
    rows = []
    for page, profile in cells:
        before = median(runs_of(baseline, page, profile, primary)) if baseline else None
        after, delta, pct, ci, p, src = None, None, None, None, None, "latest kept"
        c = cell_line(confirm, page, profile, "cand") if confirm else None
        if c:
            after, delta, pct, ci, p, src = c["medians"].get(primary), c.get("delta"), c.get("delta_pct"), c.get("ci95"), c.get("p_value"), "confirmed"
            if c.get("cell_verdict") == "not confirmed":
                src = "not confirmed"
        else:
            kept = [it for it in order if iters[it]["decision"] == "keep"]
            if kept:
                k = cell_line(iters[kept[-1]]["final"], page, profile, "cand")
                after = k["medians"].get(primary) if k else None
            else:
                after = before
            if after is not None and before:
                delta, pct = after - before, (after - before) / before
        summed = 0.0
        for it in order:
            if iters[it]["decision"] == "keep":
                k = cell_line(iters[it]["final"], page, profile, "cand")
                summed += (k or {}).get("delta") or 0
        rows.append({"page": page, "profile": profile, "before": before, "after": after, "delta": delta,
                     "pct": pct, "ci": ci, "p": p, "src": src, "summed": summed})
    return rows


def goal_met(goal, rows):
    if not goal or goal.get("bad"):
        return None
    sel = [r for r in rows if not goal["profile"] or r["profile"] == goal["profile"]]
    if not sel or any(r["after"] is None for r in sel):
        return None
    if goal["max_ms"] is not None:
        return all(r["after"] <= goal["max_ms"] for r in sel)
    return all(r["src"] == "confirmed" and r["pct"] is not None and -r["pct"] >= goal["pct"] for r in sel)


def auto_notes(rows, baseline, iters, order, confirm, primary):
    n = []
    for r in rows:
        if r["src"] in ("confirmed", "not confirmed") and r["summed"]:
            n.append(f"{r['page']} {r['profile']}: kept iterations add up to {fmt_delta(r['summed'])}; the confirmation run "
                     f"measured {fmt_delta(r['delta'])}. The report states the confirmation number, because per-iteration "
                     f"gains overlap and each one carries its own noise.")
    if not confirm and order:
        n.append("No confirmation run yet: the 'after' numbers come from the last kept iteration, not from a direct "
                 "original-versus-final comparison.")
    if baseline:
        nf = []
        for l in baseline:
            v = (l.get("noise_floor") or {}).get(primary)
            if v is not None:
                nf.append(f"{l['page']} {l['profile']} {v:,.1f} ms")
        if nf:
            n.append("Noise floor from the A/A test (2 × MAD of paired differences): " + "; ".join(sorted(set(nf))) + ".")
    same = [it for it in order if iters[it].get("visual") == "critic-same"]
    if same:
        n.append(f"Iterations {', '.join(same)} changed more than 0.1% of pixels (or a dense patch); a blind critic judged "
                 f"the pages the same, so they were kept.")
    retried = [it for it in order if iters[it]["retried"]]
    if retried:
        n.append(f"Iterations {', '.join(retried)} were inconclusive at first and were re-measured with more runs.")
    n.append("These are lab numbers: Lighthouse with simulated throttling (mobile: Slow 4G with 4× CPU slowdown; "
             "desktop preset), cold cache, on one machine. Field data (CrUX, RUM) can differ. TBT is a lab proxy for "
             "INP; INP itself was not measured.")
    n.append("Filmstrips come from one extra run per variant with DevTools throttling, because simulated runs record "
             "an unthrottled load. Their timings show the visual sequence and do not equal the medians above.")
    n.append("Cache-header changes help repeat visits; Lighthouse loads with a cleared cache, so this loop cannot "
             "measure them.")
    return n


def md_cell(s):
    return str(s).replace("|", "\\|")


def a11y_none(d):
    return (f"No new accessibility violations in the final build (axe {d.get('axe') or '?'}; "
            f"{d['fixed']} fixed, {d['unchanged']} unchanged).")


def a11y_summary(d):
    return (f"{len(d['new'])} new accessibility violations ({d['serious_new']} serious or critical) in the final build "
            f"compared with the original; {d['fixed']} fixed, {d['unchanged']} unchanged (axe {d.get('axe') or '?'}). "
            "Matched by rule and target selector. Informational: no change was reverted because of it.")


# ---------- render ----------

def render(a):
    root = Path(a.runs_jsonl).resolve().parent
    lines = load_lines(a.runs_jsonl)
    primary = a.primary
    cells, baseline, confirm, iters, order = build(lines, primary)
    rows = summary_rows(cells, baseline, iters, order, confirm, primary)
    goal = parse_goal(a.goal)
    met = goal_met(goal, rows)
    kept = [it for it in order if iters[it]["decision"] == "keep"]
    rejected = [it for it in order if iters[it]["decision"] != "keep"]
    notes_extra = Path(a.notes).read_text() if a.notes and Path(a.notes).exists() else ""
    title = a.title or "Page load loop"
    P = primary.upper()

    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{esc(title)}</title>"]
    if a.status == "running":
        h.append('<meta http-equiv="refresh" content="60">')
    h.append(f"<style>{CSS}</style></head><body><main>")
    lhv = next((l.get("lighthouse") for l in lines if l.get("lighthouse")), "?")
    h.append(f"<h1>{esc(title)}</h1><p class='sub'>{'Running — this page reloads every 60 s' if a.status == 'running' else 'Finished'}"
             f" · {len(order)} iterations ({len(kept)} kept, {len(rejected)} rejected) · Lighthouse {esc(lhv)}"
             + (f" · goal <code>{esc(goal['text'])}</code>: " + ("<b class='good'>met</b>" if met else ("<b class='bad'>not met</b>" if a.status == "finished" else "not met yet") if met is False else "not yet known") if goal else "")
             + "</p>")

    h.append("<h2>Summary</h2><div class='cards'>")
    for r in rows:
        cls = "good" if (r["delta"] or 0) < 0 else "bad" if (r["delta"] or 0) > 0 else "mutedt"
        extra = ""
        if r["ci"]:
            extra = f"<div class='mutedt'>95% CI {fmt_delta(r['ci'][0])} to {fmt_delta(r['ci'][1])}, {fmt_p(r['p'])}</div>"
        h.append(f"<div class='card'><div class='k'>{esc(r['page'])} · {esc(r['profile'])} · median {P}</div>"
                 f"<div class='v'>{fmt_ms(r['before'])} → {fmt_ms(r['after'])}</div>"
                 f"<div class='d {cls}'>{fmt_delta(r['delta'], r['pct'])} <span class='badge'>{esc(r['src'])}</span></div>{extra}</div>")
    h.append("</div>")

    h.append(f"<h2>{P} per iteration</h2><p class='sub'>Each dot is the candidate's median {P}. The dashed line is the "
             "baseline it was compared with; the band is ± the noise floor. A change is kept only when the script finds a gain "
             "beyond the noise and no regression on any page.</p><div class='grid2'>")
    for page, profile in cells:
        h.append(f"<div class='chart'><h3>{esc(page)} · {esc(profile)}</h3>{iteration_chart(page, profile, baseline, iters, order, confirm, primary)}</div>")
    h.append("</div>")

    h.append(f"<h2>Every run</h2><p class='sub'>Individual Lighthouse runs. Overlapping clouds mean the difference is noise.</p><div class='grid2'>")
    for page, profile in cells:
        h.append(f"<div class='chart'><h3>{esc(page)} · {esc(profile)}</h3>{strip_plot(page, profile, baseline, iters, order, confirm, primary)}</div>")
    h.append("</div>")

    h.append("<h2>Before and after</h2>")
    for page, profile in cells:
        before = load_strips(root, baseline, page, profile, lambda vs: sorted(vs)[0] if vs else None)
        after_src = confirm if confirm else []
        after = load_strips(root, after_src, page, profile, lambda vs: "cand" if "cand" in vs else (vs[-1] if vs else None))
        h.append(f"<div class='chart' style='margin-bottom:12px'><h3>{esc(page)} · {esc(profile)}</h3>"
                 f"{film_html(before, 'Before')}{film_html(after, 'After') if after else '<p class=mutedt>After: shown once the confirmation run has finished.</p>'}</div>")

    h.append("<h2>Iterations</h2><div class='tablewrap'><table><thead><tr><th>#</th><th>Hypothesis</th><th>Decision</th>"
             f"<th>Δ median {P} per page</th><th>Visual</th><th>Commit</th><th>Reason</th></tr></thead><tbody>")
    for it in order:
        d = iters[it]
        deltas = []
        for page, profile in cells:
            c = cell_line(d["final"], page, profile, "cand")
            if c and c.get("delta") is not None:
                p = c.get("p_value")
                deltas.append(f"{esc(page)} {esc(profile)}: {fmt_delta(c['delta'], c.get('delta_pct'))}" + (f", p={p:.3f}" if p is not None else ""))
        dec = d["decision"] + (" (after retry)" if d["retried"] else "")
        dcls = "good" if d["decision"] == "keep" else "mutedt"
        vis = esc(d.get("visual") or "–") + (f" ({d['visual_ratio']:.3%})" if d.get("visual_ratio") is not None else "")
        h.append(f"<tr><td class='num'>{esc(it)}</td><td>{esc(d['hypothesis'])}</td><td class='{dcls}'>{esc(dec)}</td>"
                 f"<td class='num'>{'<br>'.join(deltas)}</td><td>{vis}</td><td><code>{esc((d['commit'] or '–')[:9])}</code></td>"
                 f"<td>{esc(d['reason'])}</td></tr>")
    h.append("</tbody></table></div>")

    h.append("<h2>Dependency and configuration changes</h2>")
    ch = [(it, iters[it]["decision"], c) for it in order for c in iters[it]["changes"]]
    if ch:
        h.append("<ul>" + "".join(f"<li>Iteration {esc(it)} ({'kept, in the final code' if dec == 'keep' else 'tried and reverted'}): {esc(c)}</li>" for it, dec, c in ch) + "</ul>")
    else:
        h.append("<p class='mutedt'>None.</p>")

    a11y = json.loads(Path(a.a11y).read_text()) if a.a11y and Path(a.a11y).exists() else None
    if a11y:
        h.append("<h2>Accessibility</h2>")
        if not a11y["new"]:
            h.append(f"<p class='mutedt'>{esc(a11y_none(a11y))}</p>")
        else:
            h.append(f"<p class='sub'>{esc(a11y_summary(a11y))}</p><div class='tablewrap'><table><thead><tr><th>Impact</th>"
                     "<th>Page</th><th>Rule</th><th>Target</th><th>Help</th></tr></thead><tbody>")
            for x in a11y["new"]:
                icls = "bad" if x["impact"] in ("serious", "critical") else "mutedt"
                h.append(f"<tr><td class='{icls}'>{esc(x['impact'])}</td><td>{esc(x['page'])} {esc(x['viewport'])}</td>"
                         f"<td><code>{esc(x['rule'])}</code></td><td><code>{esc(x['target'])}</code></td><td>{esc(x['help'])}</td></tr>")
            h.append("</tbody></table></div>")

    h.append("<h2>Notes</h2><ul class='notes'>" + "".join(f"<li>{esc(n)}</li>" for n in auto_notes(rows, baseline, iters, order, confirm, primary)) + "</ul>")
    if notes_extra.strip():
        h.append("".join(f"<p>{esc(p)}</p>" for p in notes_extra.strip().split("\n\n")))
    h.append("</main></body></html>")
    (Path(a.out_dir) / "report.html").write_text("".join(h))

    # report.md for the pull request body
    md = [f"## {title}", ""]
    if goal:
        md.append(f"Goal `{goal['text']}`: " + ("met" if met else ("not met" if a.status == "finished" else "not met yet") if met is False else "not yet known"))
        md.append("")
    md += [f"| Page | Profile | {P} before | {P} after | Change | Basis |", "|---|---|---|---|---|---|"]
    for r in rows:
        basis = r["src"] + (f", 95% CI {fmt_delta(r['ci'][0])} to {fmt_delta(r['ci'][1])}, {fmt_p(r['p'])}" if r["ci"] else "")
        md.append(f"| `{r['page']}` | {r['profile']} | {fmt_ms(r['before'])} | {fmt_ms(r['after'])} | {fmt_delta(r['delta'], r['pct'])} | {basis} |")
    md += ["", f"### Iterations ({len(kept)} kept, {len(rejected)} rejected)", "", "| # | Change | Decision | Commit |", "|---|---|---|---|"]
    for it in order:
        d = iters[it]
        md.append(f"| {it} | {d['hypothesis']} | {d['decision']}{' (after retry)' if d['retried'] else ''}: {d['reason'][:160]} | {(d['commit'] or '–')[:9]} |")
    if ch:
        md += ["", "### Dependency and configuration changes", ""] + [f"- Iteration {it} ({'kept' if dec == 'keep' else 'reverted'}): {c}" for it, dec, c in ch]
    if a11y:
        md += ["", "### Accessibility", ""]
        if not a11y["new"]:
            md.append(a11y_none(a11y))
        else:
            md += [a11y_summary(a11y), "", "| Impact | Page | Rule | Target |", "|---|---|---|---|"]
            md += [f"| {x['impact']} | `{x['page']}` {x['viewport']} | `{x['rule']}` | `{md_cell(x['target'])}` |"
                   for x in a11y["new"]]
    md += ["", "### Notes", ""] + [f"- {n}" for n in auto_notes(rows, baseline, iters, order, confirm, primary)]
    if notes_extra.strip():
        md += ["", notes_extra.strip()]
    (Path(a.out_dir) / "report.md").write_text("\n".join(md) + "\n")
    print(f"wrote {Path(a.out_dir) / 'report.html'} and report.md ({len(order)} iterations, goal "
          f"{'met' if met else 'not met' if met is False else 'unknown'})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-jsonl", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--title")
    ap.add_argument("--goal")
    ap.add_argument("--status", choices=["running", "finished"], default="running")
    ap.add_argument("--notes")
    ap.add_argument("--primary", default="lcp")
    ap.add_argument("--a11y", help="a11y.json from compare.py a11y")
    render(ap.parse_args())


if __name__ == "__main__":
    main()

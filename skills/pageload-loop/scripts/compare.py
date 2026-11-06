#!/usr/bin/env python3
"""Statistics and keep/reject decisions for a Pageload Loop.

The model never decides whether a change helped. This script does, from the
numbers in measure.json (written by measure.mjs). Python 3.8+, standard
library only.

Usage:
  compare.py aa       --measure M.json --out noise.json
  compare.py decide   --measure M.json --noise noise.json --out decision.json [--retry]
  compare.py confirm  --measure M.json --noise noise.json --out confirm.json
  compare.py log      --runs-jsonl .pageload/runs.jsonl --kind baseline|iteration|confirm
                      --iter N --measure M.json [--decision D.json] [--noise noise.json]
                      [--hypothesis TEXT] [--commit SHA] [--visual pass|critic-same|fail|off|skipped]
                      [--visual-ratio R] [--change TEXT ...]
  compare.py log      --runs-jsonl P --iter N --reject-reason TEXT [--hypothesis TEXT] [--change TEXT]
  compare.py final    --decision D.json --visual pass|critic-same|fail|off|skipped
  compare.py insights --insights I.json [--insights I2.json ...] [--only-variant NAME]
  compare.py selftest

Common options: --primary lcp  --min-gain 0.03  --alpha 0.05  --base base  --cand cand

aa       Noise floor per page, profile and metric from an A/A measurement:
         2 x MAD of the paired run differences (run i of A minus run i of B).
         Warns when the A/A pair differs (unstable measurement).
decide   keep | reject | inconclusive, with the reason. Rules:
         win        primary median improves by more than max(noise, min-gain x
                    baseline median) AND one-sided Mann-Whitney p < alpha, with p
                    Holm-corrected across the page x profile cells (--no-holm to skip)
         regression primary median worsens by more than max(noise, 1% of baseline)
         guardrail  CLS above 0.1 (and worse than baseline), or CLS/TBT/TTFB
                    worse by more than max(noise, absolute minimum, relative minimum)
         keep       at least one win, no regression, no guardrail failure
         inconclusive  no win, no regression, no guardrail failure, but a cell is
                    close (size passes with p < 0.2, or p passes with half the size).
                    The lead re-measures once at 14 runs and passes --retry; a second
                    inconclusive becomes reject.
confirm  Original vs final: median delta, one-sided p and a bootstrap 95% interval
         per page and profile. This is the number the report states.
final    Prints "keep<TAB>LCP -x ms (page profile)" (exit 0) or "reject<TAB>reason" /
         "inconclusive<TAB>reason" (exit 1). Run it before committing or reverting.
log      Appends one line per (page, profile, variant) to runs.jsonl. With
         --kind iteration the final decision is computed here: a measured keep
         becomes reject when the visual guard reports "fail".
insights Ranks Lighthouse insights by estimated LCP savings across pages and profiles.
"""
import argparse
import json
import random
import statistics
import sys
import time
from functools import lru_cache
from math import comb, erf, sqrt
from pathlib import Path

METRICS = ["lcp", "cls", "tbt", "ttfb", "fcp", "si", "server_ms"]
GUARDRAILS = {
    # abs_min: smallest change that counts as a regression; rel: same, as share of baseline.
    "cls": {"abs_min": 0.01, "rel": 0.0, "limit": 0.1},
    "tbt": {"abs_min": 30.0, "rel": 0.10},
    "ttfb": {"abs_min": 30.0, "rel": 0.10},
}
PRIMARY_REGRESS_REL = 0.01
NEAR_P = 0.2


# ---------- statistics ----------

def median(xs):
    return statistics.median(xs) if xs else None


def mad(xs):
    if not xs:
        return 0.0
    m = statistics.median(xs)
    return statistics.median([abs(x - m) for x in xs])


@lru_cache(maxsize=None)
def _u_count(n1, n2, u):
    """Number of orderings of n1 x-values and n2 y-values with statistic U = u."""
    if u < 0 or u > n1 * n2:
        return 0
    if n1 == 0 or n2 == 0:
        return 1 if u == 0 else 0
    return _u_count(n1 - 1, n2, u - n2) + _u_count(n1, n2 - 1, u)


def _norm_sf(z):
    return 0.5 * (1 - erf(z / sqrt(2)))


def mw_less(x, y):
    """One-sided Mann-Whitney U test. H1: values in x tend to be smaller than in y.

    Exact distribution when there are no ties and both samples have at most 25
    values; otherwise normal approximation with tie and continuity correction.
    """
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return 1.0
    u = 0.0
    for a in x:
        for b in y:
            u += 1.0 if a < b else (0.5 if a == b else 0.0)
    pooled = list(x) + list(y)
    ties = len(set(pooled)) < len(pooled)
    if not ties and n1 <= 25 and n2 <= 25:
        total = comb(n1 + n2, n1)
        k = int(round(u))
        tail = sum(_u_count(n1, n2, v) for v in range(k, n1 * n2 + 1))
        return tail / total
    n = n1 + n2
    counts = {}
    for v in pooled:
        counts[v] = counts.get(v, 0) + 1
    tie_term = sum(t ** 3 - t for t in counts.values())
    var = n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1)))
    if var <= 0:
        return 1.0
    z = (u - n1 * n2 / 2.0 - 0.5) / sqrt(var)
    return _norm_sf(z)


def mw_two_sided(x, y):
    return min(1.0, 2 * min(mw_less(x, y), mw_less(y, x)))


def bootstrap_ci(base, cand, n=2000, seed=0):
    """95% percentile interval for median(cand) - median(base)."""
    rng = random.Random(seed)
    ds = []
    for _ in range(n):
        b = [rng.choice(base) for _ in base]
        c = [rng.choice(cand) for _ in cand]
        ds.append(statistics.median(c) - statistics.median(b))
    ds.sort()
    return ds[int(0.025 * n)], ds[int(0.975 * n) - 1]


# ---------- data ----------

def load(p):
    return json.loads(Path(p).read_text())


def cells(measure):
    """{(page, profile): {variant: {metric: [values in run order]}}}"""
    out = {}
    for r in measure["runs"]:
        if r.get("error") or not r.get("metrics"):
            continue
        cell = out.setdefault((r["page"], r["profile"]), {})
        v = cell.setdefault(r["variant"], {m: [] for m in METRICS})
        for m in METRICS:
            val = r["metrics"].get(m)
            if val is not None:
                v[m].append(val)
    return out


def variant_names(measure, a):
    names = [v["name"] for v in measure["meta"]["variants"]]
    base = a.base if a.base in names else names[0]
    cand = a.cand if a.cand in names else names[1]
    return base, cand


def key(page, profile):
    return f"{page}|{profile}"


# ---------- commands ----------

def cmd_aa(a):
    m = load(a.measure)
    va, vb = [v["name"] for v in m["meta"]["variants"]]
    noise = {"created": time.strftime("%Y-%m-%dT%H:%M:%S"), "rule": "2 x MAD of paired A/A differences",
             "runs": m["meta"]["runs"], "cells": {}}
    warnings = []
    for (page, profile), c in sorted(cells(m).items()):
        out = {}
        for met in METRICS:
            xa, xb = c.get(va, {}).get(met, []), c.get(vb, {}).get(met, [])
            k = min(len(xa), len(xb))
            if k < 3:
                continue
            d = [xa[i] - xb[i] for i in range(k)]
            out[met] = {
                "noise_floor": 2 * mad(d),
                "median_a": median(xa), "median_b": median(xb),
                "median_diff": median(xa) - median(xb),
                "p_two_sided": mw_two_sided(xa, xb),
            }
        noise["cells"][key(page, profile)] = out
        p = out.get(a.primary)
        if p:
            rel = abs(p["median_diff"]) / p["median_a"] if p["median_a"] else 0
            if p["p_two_sided"] < a.alpha or rel > a.min_gain:
                warnings.append(f"{page} {profile}: A/A {a.primary} medians differ by "
                                f"{p['median_diff']:.0f} ({rel:.1%}), p={p['p_two_sided']:.3f}")
    noise["warnings"] = warnings
    noise["stable"] = not warnings
    Path(a.out).write_text(json.dumps(noise, indent=1))
    for k, out in noise["cells"].items():
        p = out.get(a.primary, {})
        print(f"{k}: {a.primary} median {p.get('median_a', 0):.0f}, noise floor {p.get('noise_floor', 0):.1f}")
    for w in warnings:
        print("UNSTABLE:", w)
    print("A/A stable" if noise["stable"] else "A/A NOT stable: fix the measurement before iteration 1")
    return 0 if noise["stable"] else 3


def noise_for(noise, page, profile, met):
    return noise.get("cells", {}).get(key(page, profile), {}).get(met, {}).get("noise_floor", 0.0)


def holm(ps):
    """Holm-Bonferroni adjusted p-values, same order as the input."""
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj, run = [1.0] * m, 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * ps[i]))
        adj[i] = run
    return adj


def judge_cell(c, base, cand, noise, page, profile, a, p_adj=None):
    b, n = c.get(base, {}), c.get(cand, {})
    pb, pc = b.get(a.primary, []), n.get(a.primary, [])
    res = {"page": page, "profile": profile, "n_base": len(pb), "n_cand": len(pc)}
    if len(pb) < 5 or len(pc) < 5:
        res.update(verdict="error", reason=f"too few valid runs ({len(pb)} base, {len(pc)} cand)")
        return res
    mb, mc = median(pb), median(pc)
    nf = noise_for(noise, page, profile, a.primary)
    gain_needed = max(nf, a.min_gain * mb)
    regress_limit = max(nf, PRIMARY_REGRESS_REL * mb)
    delta = mc - mb
    p_raw = mw_less(pc, pb)
    p = p_raw if p_adj is None else p_adj
    res.update(median_base=mb, median_cand=mc, delta=delta, delta_pct=delta / mb if mb else 0,
               p_value=p, p_raw=p_raw, noise_floor=nf, gain_needed=gain_needed, regress_limit=regress_limit)
    guard = []
    for g, cfg in GUARDRAILS.items():
        xb, xc = b.get(g, []), n.get(g, [])
        if not xb or not xc:
            continue
        gb, gc = median(xb), median(xc)
        lim = max(noise_for(noise, page, profile, g), cfg["abs_min"], cfg["rel"] * gb)
        res[f"{g}_base"], res[f"{g}_cand"] = gb, gc
        if gc - gb > lim:
            guard.append(f"{g} {gb:.3g} -> {gc:.3g} (limit +{lim:.3g})")
        elif "limit" in cfg and gc > cfg["limit"] and gc > gb:
            guard.append(f"{g} {gc:.3g} above {cfg['limit']}")
    res["guardrail_failures"] = guard
    if guard:
        res.update(verdict="guardrail", reason="; ".join(guard))
    elif delta > regress_limit:
        res.update(verdict="regression", reason=f"{a.primary} +{delta:.0f} ms (limit +{regress_limit:.0f})")
    elif -delta > gain_needed and p < a.alpha:
        res.update(verdict="win", reason=f"{a.primary} {delta:.0f} ms ({delta / mb:.1%}), p={p:.3f}")
    elif (-delta > gain_needed and p < NEAR_P) or (p < a.alpha and -delta > 0.5 * gain_needed):
        res.update(verdict="near", reason=f"{a.primary} {delta:.0f} ms, p={p:.3f}, needs -{gain_needed:.0f} and p<{a.alpha}")
    else:
        res.update(verdict="none", reason=f"{a.primary} {delta:+.0f} ms, p={p:.3f}")
    return res


def cmd_decide(a):
    m, noise = load(a.measure), load(a.noise)
    base, cand = variant_names(m, a)
    items = sorted(cells(m).items())
    results = [judge_cell(c, base, cand, noise, pg, pf, a) for (pg, pf), c in items]
    if not a.no_holm and len(results) > 1:
        # Several pages and profiles are tested at once; correct for that so one lucky cell
        # does not keep a change. Cells with errors keep p = 1.
        adj = holm([r.get("p_raw", 1.0) for r in results])
        results = [judge_cell(c, base, cand, noise, pg, pf, a, p_adj=adj[i]) for i, ((pg, pf), c) in enumerate(items)]
    v = [r["verdict"] for r in results]
    bad = [r for r in results if r["verdict"] in ("guardrail", "regression", "error")]
    wins = [r for r in results if r["verdict"] == "win"]
    near = [r for r in results if r["verdict"] == "near"]
    if bad:
        decision, reason = "reject", "; ".join(f"{r['page']} {r['profile']}: {r['reason']}" for r in bad)
    elif wins:
        decision, reason = "keep", "; ".join(f"{r['page']} {r['profile']}: {r['reason']}" for r in wins)
    elif near and not a.retry:
        decision, reason = "inconclusive", "re-measure at 14 runs: " + "; ".join(
            f"{r['page']} {r['profile']}: {r['reason']}" for r in near)
    elif near:
        decision, reason = "reject", "inconclusive after retry: " + "; ".join(
            f"{r['page']} {r['profile']}: {r['reason']}" for r in near)
    else:
        decision, reason = "reject", "no gain above noise: " + "; ".join(
            f"{r['page']} {r['profile']}: {r['reason']}" for r in results)
    out = {"decision": decision, "reason": reason, "primary": a.primary, "base": base, "cand": cand,
           "p_correction": "none" if a.no_holm else "holm",
           "retry": a.retry, "runs": m["meta"]["runs"], "cells": results, "verdicts": v}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"{decision.upper()}: {reason}")
    return 0


def cmd_confirm(a):
    m, noise = load(a.measure), load(a.noise)
    base, cand = variant_names(m, a)
    rows = []
    for (pg, pf), c in sorted(cells(m).items()):
        pb, pc = c.get(base, {}).get(a.primary, []), c.get(cand, {}).get(a.primary, [])
        if len(pb) < 5 or len(pc) < 5:
            rows.append({"page": pg, "profile": pf, "verdict": "error"})
            continue
        mb, mc = median(pb), median(pc)
        lo, hi = bootstrap_ci(pb, pc)
        p = mw_less(pc, pb)
        nf = noise_for(noise, pg, pf, a.primary)
        confirmed = (mb - mc) > max(nf, a.min_gain * mb) and p < a.alpha
        guards = {g: [median(c[base][g]), median(c[cand][g])] for g in GUARDRAILS if c[base].get(g) and c[cand].get(g)}
        rows.append({"page": pg, "profile": pf, "median_base": mb, "median_cand": mc, "delta": mc - mb,
                     "delta_pct": (mc - mb) / mb, "ci95": [lo, hi], "p_value": p, "noise_floor": nf,
                     "confirmed": confirmed, "guardrails": guards,
                     "verdict": "confirmed" if confirmed else "not confirmed"})
    out = {"decision": "confirm", "primary": a.primary, "base": base, "cand": cand, "runs": m["meta"]["runs"],
           "cells": rows, "any_confirmed": any(r.get("confirmed") for r in rows)}
    Path(a.out).write_text(json.dumps(out, indent=1))
    for r in rows:
        if r["verdict"] == "error":
            print(f"{r['page']} {r['profile']}: too few runs")
            continue
        print(f"{r['page']} {r['profile']}: {r['median_base']:.0f} -> {r['median_cand']:.0f} ms "
              f"({r['delta']:+.0f}, {r['delta_pct']:+.1%}; 95% CI {r['ci95'][0]:+.0f}..{r['ci95'][1]:+.0f}; "
              f"p={r['p_value']:.4f}) {r['verdict']}")
    return 0


def final_decision(measured, visual):
    if measured != "keep":
        return measured, None
    if visual in ("pass", "critic-same", "off"):
        return "keep", None
    if visual == "fail":
        return "reject", "visual change detected"
    raise SystemExit("a measured keep needs --visual pass|critic-same|fail|off")


def cmd_final(a):
    """Print the final decision (measurement + visual guard) and a commit-message suffix."""
    dec = load(a.decision)
    decision, override = final_decision(dec["decision"], a.visual)
    if decision == "keep":
        wins = [c for c in dec["cells"] if c.get("verdict") == "win"]
        best = min(wins, key=lambda c: c["delta"])
        print(f"keep\t{dec['primary'].upper()} \u2212{abs(best['delta']):.0f} ms ({best['page']} {best['profile']})")
        return 0
    print(f"{decision}\t{override or dec['reason']}")
    return 1


def cmd_log(a):
    if a.reject_reason:
        # No measurement: the build failed, an off-limits file was touched, or the builder gave up.
        ln = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "iter": a.iter, "kind": "iteration",
              "hypothesis": a.hypothesis, "commit": a.commit, "variant": None, "role": None, "page": "*",
              "profile": "*", "runs": {}, "medians": {}, "noise_floor": {}, "p_value": None, "delta": None,
              "visual": a.visual, "decision": "reject", "measured_decision": None, "reason": a.reject_reason,
              "changes": a.change or []}
        with open(a.runs_jsonl, "a") as f:
            f.write(json.dumps(ln) + "\n")
        print("logged 1 line, decision reject")
        return 0
    m = load(a.measure)
    dec = load(a.decision) if a.decision else {}
    noise = load(a.noise) if a.noise else {}
    measured = dec.get("decision", "baseline" if a.kind == "baseline" else None)
    decision, override = (measured, None)
    if a.kind == "iteration":
        decision, override = final_decision(measured, a.visual)
    reason = override or dec.get("reason", "")
    if override and dec.get("reason"):
        reason = f"{override} (measured: {dec['reason']})"
    by_cell = {(r["page"], r["profile"]): r for r in dec.get("cells", [])}
    film = Path(a.measure).with_name("filmstrips.json")
    root = Path(a.runs_jsonl).resolve().parent
    try:
        film_rel = str(film.resolve().relative_to(root)) if film.exists() else None
    except ValueError:
        film_rel = str(film.resolve()) if film.exists() else None
    elements = {}
    for r in m["runs"]:
        if r.get("lcp_element"):
            elements.setdefault((r["page"], r["profile"], r["variant"]), r["lcp_element"].get("selector"))
    lines = []
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    for (pg, pf), c in sorted(cells(m).items()):
        cell = by_cell.get((pg, pf), {})
        for variant, vals in c.items():
            lines.append({
                "ts": ts, "iter": a.iter, "kind": a.kind, "hypothesis": a.hypothesis, "commit": a.commit,
                "variant": variant, "role": ("base" if variant == dec.get("base") else
                                             "cand" if variant == dec.get("cand") else variant),
                "page": pg, "profile": pf, "runs": {k: v for k, v in vals.items() if v},
                "medians": {k: median(v) for k, v in vals.items() if v},
                "noise_floor": {k: v.get("noise_floor") for k, v in noise.get("cells", {}).get(key(pg, pf), {}).items()},
                "p_value": cell.get("p_value"), "delta": cell.get("delta"), "delta_pct": cell.get("delta_pct"),
                "ci95": cell.get("ci95"), "cell_verdict": cell.get("verdict"),
                "visual": a.visual, "visual_ratio": a.visual_ratio,
                "decision": decision, "measured_decision": measured, "reason": reason,
                "changes": a.change or [], "lcp_element": elements.get((pg, pf, variant)),
                "filmstrip_file": film_rel, "lighthouse": m["meta"].get("lighthouse"),
                "n_runs": m["meta"].get("runs"),
            })
    with open(a.runs_jsonl, "a") as f:
        for ln in lines:
            f.write(json.dumps(ln) + "\n")
    print(f"logged {len(lines)} lines, decision {decision}")
    return 0


def cmd_insights(a):
    agg = {}
    for p in a.insights:
        for block in load(p):
            if a.only_variant and block["variant"] != a.only_variant:
                continue
            for ins in block["insights"]:
                s = ins.get("savings") or {}
                e = agg.setdefault(ins["id"], {"id": ins["id"], "title": ins["title"], "lcp_max": 0, "fcp_max": 0,
                                               "cls_max": 0, "where": [], "items": ins.get("items", [])[:3]})
                e["lcp_max"] = max(e["lcp_max"], s.get("LCP", 0) or 0)
                e["fcp_max"] = max(e["fcp_max"], s.get("FCP", 0) or 0)
                e["cls_max"] = max(e["cls_max"], s.get("CLS", 0) or 0)
                if (ins.get("score") or 0) < 1:
                    e["where"].append(f"{block['page']} {block['profile']}")
    ranked = sorted(agg.values(), key=lambda e: (-e["lcp_max"], -e["fcp_max"], -e["cls_max"]))
    for e in ranked:
        if not e["where"] and not e["lcp_max"]:
            continue
        print(f"{e['lcp_max']:>6.0f} ms LCP  {e['fcp_max']:>6.0f} ms FCP  {e['id']}: {e['title']}  [{', '.join(sorted(set(e['where'])))}]")
    return 0


# ---------- self-test ----------

def _fake_measure(base_vals, cand_vals, page="/", profile="mobile", extra=None):
    runs = []
    for i, (b, c) in enumerate(zip(base_vals, cand_vals)):
        for name, v in (("base", b), ("cand", c)):
            met = {"lcp": v, "cls": 0.01, "tbt": 50.0, "ttfb": 400.0, "fcp": v * 0.7, "si": v * 0.8, "server_ms": 5.0}
            if extra and name == "cand":
                met.update(extra)
            runs.append({"variant": name, "page": page, "profile": profile, "run": i, "metrics": met})
    return {"meta": {"variants": [{"name": "base"}, {"name": "cand"}], "runs": len(base_vals)}, "runs": runs}


def cmd_selftest(_a):
    import tempfile
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name)

    # Mann-Whitney: exact values.
    check("mw complete separation 7v7", abs(mw_less([1] * 0 + list(range(7)), list(range(10, 17))) - 1 / comb(14, 7)) < 1e-12)
    check("mw identical samples -> p=1", mw_less([5.0] * 7, [5.0] * 7) == 1.0)
    # x=[1,3,5,7], y=[2,4,6,8]: U=10 of 16; P(U >= 10) = 24/70 orderings.
    check("mw exact 4v4 interleaved", abs(mw_less([1, 3, 5, 7], [2, 4, 6, 8]) - 24 / 70) < 1e-12)
    # Exact one-sided p for x=[1,2], y=[3,4]: only 1 of C(4,2)=6 orderings is as extreme.
    check("mw exact small case", abs(mw_less([1, 2], [3, 4]) - 1 / 6) < 1e-12)
    check("mw ties use normal approx", 0 < mw_less([1, 1, 2, 2, 3, 3, 4], [3, 3, 4, 4, 5, 5, 6]) < 0.05)
    check("mad", mad([1, 2, 3, 4, 100]) == 1)
    check("holm", [round(x, 3) for x in holm([0.01, 0.04, 0.03, 0.5])] == [0.04, 0.09, 0.09, 0.5])

    rng = random.Random(42)
    tmp = Path(tempfile.mkdtemp())
    base = [2000 + rng.gauss(0, 30) for _ in range(7)]

    def run_case(cand, extra=None, noise_val=40.0, retry=False):
        mpath, npath, dpath = tmp / "m.json", tmp / "n.json", tmp / "d.json"
        mpath.write_text(json.dumps(_fake_measure(base, cand, extra=extra)))
        npath.write_text(json.dumps({"cells": {"/|mobile": {"lcp": {"noise_floor": noise_val},
                                                             "tbt": {"noise_floor": 5}, "cls": {"noise_floor": 0}}}}))
        ns = argparse.Namespace(measure=str(mpath), noise=str(npath), out=str(dpath), retry=retry, no_holm=False,
                                primary="lcp", min_gain=0.03, alpha=0.05, base="base", cand="cand")
        with _quiet():
            cmd_decide(ns)
        return load(dpath)["decision"]

    check("clear 15% gain -> keep", run_case([v * 0.85 for v in base]) == "keep")
    check("no change -> reject", run_case([v + rng.gauss(0, 30) for v in base]) == "reject")
    check("1% gain below 3% threshold -> not keep", run_case([v * 0.99 for v in base]) != "keep")
    check("gain under big noise floor -> not keep", run_case([v * 0.9 for v in base], noise_val=400) != "keep")
    # Shift of 45 ms: significant, but under the 60 ms needed (3% of 2000) and over half of it.
    check("borderline -> inconclusive", run_case([v - 45 for v in base]) == "inconclusive")
    check("borderline on retry -> reject", run_case([v - 45 for v in base], retry=True) == "reject")
    check("LCP regression -> reject", run_case([v * 1.1 for v in base]) == "reject")
    check("gain but TBT +200 -> reject (guardrail)", run_case([v * 0.8 for v in base], extra={"tbt": 250.0}) == "reject")
    check("gain but CLS 0.25 -> reject (guardrail)", run_case([v * 0.8 for v in base], extra={"cls": 0.25}) == "reject")

    # A/A noise floor on identical-distribution data.
    a_vals = [2000 + rng.gauss(0, 30) for _ in range(7)]
    b_vals = [2000 + rng.gauss(0, 30) for _ in range(7)]
    m = _fake_measure(a_vals, b_vals)
    (tmp / "aa.json").write_text(json.dumps(m))
    ns = argparse.Namespace(measure=str(tmp / "aa.json"), out=str(tmp / "noise.json"), primary="lcp",
                            min_gain=0.03, alpha=0.05)
    with _quiet():
        rc = cmd_aa(ns)
    nf = load(tmp / "noise.json")["cells"]["/|mobile"]["lcp"]["noise_floor"]
    check(f"A/A stable and noise floor plausible ({nf:.1f} ms)", rc == 0 and 10 < nf < 200)

    # Final decision: a measured keep with a visual fail is a reject.
    check("visual fail overrides keep", final_decision("keep", "fail")[0] == "reject")
    check("critic-same keeps", final_decision("keep", "critic-same")[0] == "keep")
    lo, hi = bootstrap_ci(base, [v * 0.85 for v in base])
    check(f"bootstrap CI excludes 0 for 15% gain ({lo:.0f}..{hi:.0f})", hi < 0)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


class _quiet:
    def __enter__(self):
        self._o = sys.stdout
        sys.stdout = open("/dev/null", "w") if Path("/dev/null").exists() else self._o

    def __exit__(self, *e):
        if sys.stdout is not self._o:
            sys.stdout.close()
        sys.stdout = self._o


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["aa", "decide", "confirm", "final", "log", "insights", "selftest"])
    ap.add_argument("--measure")
    ap.add_argument("--noise")
    ap.add_argument("--decision")
    ap.add_argument("--out")
    ap.add_argument("--retry", action="store_true")
    ap.add_argument("--no-holm", action="store_true", help="decide: no correction across pages and profiles")
    ap.add_argument("--primary", default="lcp")
    ap.add_argument("--min-gain", type=float, default=0.03)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--base", default="base")
    ap.add_argument("--cand", default="cand")
    ap.add_argument("--runs-jsonl")
    ap.add_argument("--kind", choices=["baseline", "iteration", "confirm"], default="iteration")
    ap.add_argument("--iter")
    ap.add_argument("--hypothesis", default="")
    ap.add_argument("--commit", default="")
    ap.add_argument("--visual", default=None)
    ap.add_argument("--visual-ratio", type=float, default=None)
    ap.add_argument("--change", action="append")
    ap.add_argument("--reject-reason", help="log: reject without a measurement (build failed, off-limits file)")
    ap.add_argument("--insights", action="append")
    ap.add_argument("--only-variant", default=None, help="insights: use one variant's runs only")
    a = ap.parse_args()
    sys.exit({"aa": cmd_aa, "decide": cmd_decide, "confirm": cmd_confirm, "final": cmd_final, "log": cmd_log,
              "insights": cmd_insights, "selftest": cmd_selftest}[a.cmd](a))


if __name__ == "__main__":
    main()

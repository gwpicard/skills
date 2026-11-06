#!/usr/bin/env node
// Lighthouse measurement for a Pageload Loop.
//
// Runs the Lighthouse CLI once per run, each in a fresh process, with simulated
// throttling. Baseline and candidate runs are interleaved (ABBA order) so slow
// drift on the machine hits both sides equally. Never run two measurements in
// parallel on one machine: CPU contention moves the numbers.
//
// Usage:
//   node measure.mjs --variant base=http://localhost:4001 --variant cand=http://localhost:4002 \
//        --pages /,/pricing --profiles mobile,desktop --runs 7 --out .pageload/runs/iter-03
//
// Options:
//   --variant NAME=ORIGIN   repeat; exactly two. For an A/A test, give two servers of the same build.
//   --pages LIST            comma-separated paths, appended to each origin
//   --profiles LIST         mobile (Lighthouse default: Slow 4G, 4x CPU) and/or desktop (--preset=desktop)
//   --runs N                measured runs per variant, page and profile (default 7)
//   --warmup N              discarded runs per variant before measuring (default 1)
//   --filmstrip MODE        none (default) | devtools: one extra run per variant with
//                           devtools throttling, kept only for its filmstrip (not for metrics)
//   --keep-raw MODE         first (default) | all | none: which raw Lighthouse JSON files to keep
//   --lighthouse CMD        command to run Lighthouse (default: ./node_modules/.bin/lighthouse
//                           next to this script, else "npx -y lighthouse@13")
//   --out DIR               output folder; writes measure.json, insights.json, filmstrips.json
//
// Requires Node 22.19+ (Lighthouse 13) and a local Chrome or Chromium (CHROME_PATH to pick one).

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const a = { variant: [], pages: "/", profiles: "mobile,desktop", runs: 7, warmup: 1,
    filmstrip: "none", keepRaw: "first", lighthouse: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    const take = () => { i++; return v; };
    if (k === "--variant") a.variant.push(take());
    else if (k === "--pages") a.pages = take();
    else if (k === "--profiles") a.profiles = take();
    else if (k === "--runs") a.runs = parseInt(take(), 10);
    else if (k === "--warmup") a.warmup = parseInt(take(), 10);
    else if (k === "--filmstrip") a.filmstrip = take();
    else if (k === "--keep-raw") a.keepRaw = take();
    else if (k === "--lighthouse") a.lighthouse = take();
    else if (k === "--out") a.out = take();
    else if (k === "-h" || k === "--help") { console.log(readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").filter(l => l.startsWith("//")).map(l => l.slice(3)).join("\n")); process.exit(0); }
    else { console.error(`unknown argument: ${k}`); process.exit(2); }
  }
  if (a.variant.length !== 2 || !a.out) { console.error("need exactly two --variant NAME=ORIGIN and --out DIR (see --help)"); process.exit(2); }
  return a;
}

function checkNode() {
  const [maj, min] = process.versions.node.split(".").map(Number);
  if (maj < 22 || (maj === 22 && min < 19)) {
    console.error(`warning: Node ${process.versions.node}; Lighthouse 13 requires Node 22.19 or later`);
  }
}

function lighthouseCommand(opt) {
  if (opt) return opt.split(" ");
  const local = join(HERE, "node_modules", ".bin", "lighthouse");
  if (existsSync(local)) return [local];
  return ["npx", "-y", "lighthouse@13"];
}

const CHROME_FLAGS = "--headless=new --no-first-run --no-default-browser-check --disable-extensions";

function runLighthouse(cmd, url, profile, outPath, throttling = "simulate") {
  const args = [...cmd.slice(1), url,
    "--only-categories=performance",
    `--throttling-method=${throttling}`,
    "--output=json", `--output-path=${outPath}`,
    `--chrome-flags=${CHROME_FLAGS}`, "--quiet", "--max-wait-for-load=60000"];
  if (profile === "desktop") args.push("--preset=desktop");
  const r = spawnSync(cmd[0], args, { encoding: "utf8", timeout: 180000 });
  if (r.status !== 0 || !existsSync(outPath)) {
    return { error: `lighthouse exit ${r.status}: ${(r.stderr || r.error || "").toString().slice(-400)}` };
  }
  let lhr;
  try { lhr = JSON.parse(readFileSync(outPath, "utf8")); } catch (e) { return { error: `bad JSON: ${e.message}` }; }
  if (lhr.runtimeError && lhr.runtimeError.code && lhr.runtimeError.code !== "NO_ERROR") {
    return { error: `runtimeError ${lhr.runtimeError.code}: ${lhr.runtimeError.message}`, lhr };
  }
  return { lhr };
}

function num(audits, id) {
  const v = audits[id] && audits[id].numericValue;
  return typeof v === "number" ? v : null;
}

function extractMetrics(lhr) {
  const a = lhr.audits;
  const m = (a.metrics && a.metrics.details && a.metrics.details.items && a.metrics.details.items[0]) || {};
  return {
    lcp: num(a, "largest-contentful-paint"),
    cls: num(a, "cumulative-layout-shift"),
    tbt: num(a, "total-blocking-time"),
    fcp: num(a, "first-contentful-paint"),
    si: num(a, "speed-index"),
    // ttfb: simulated time to first byte (includes the simulated network round trips).
    // server_ms: observed server response time on the real (unthrottled) load.
    ttfb: typeof m.timeToFirstByte === "number" ? m.timeToFirstByte : num(a, "server-response-time"),
    server_ms: num(a, "server-response-time"),
    bytes: num(a, "total-byte-weight"),
    perf_score: lhr.categories && lhr.categories.performance ? lhr.categories.performance.score : null,
  };
}

function lcpElement(lhr) {
  // Lighthouse 13: the LCP element is the "node" item in lcp-breakdown-insight.
  const d = lhr.audits["lcp-breakdown-insight"] && lhr.audits["lcp-breakdown-insight"].details;
  const items = (d && d.items) || [];
  const node = items.find(x => x && x.type === "node");
  const table = items.find(x => x && x.type === "table");
  return {
    selector: node ? node.selector : null,
    snippet: node ? node.snippet : null,
    subparts: table ? Object.fromEntries(table.items.map(r => [r.subpart, r.duration])) : null,
  };
}

function extractInsights(lhr) {
  // Every *-insight audit plus the classic diagnostics that still carry savings.
  const out = [];
  for (const [id, au] of Object.entries(lhr.audits)) {
    const isInsight = id.endsWith("-insight");
    const savings = au.metricSavings || null;
    const hasSavings = savings && Object.values(savings).some(v => v > 0);
    if (!isInsight && !hasSavings) continue;
    if (au.scoreDisplayMode === "notApplicable") continue;
    if (au.score === 1 && !hasSavings) continue;
    const d = au.details || {};
    let items = [];
    const rows = d.type === "table" ? d.items : (d.items || []).flatMap(x => (x && x.type === "table" ? x.items : []));
    for (const r of (rows || []).slice(0, 5)) {
      const row = {};
      for (const k of ["url", "label", "wastedMs", "wastedBytes", "totalBytes", "duration", "entity"]) {
        if (r[k] !== undefined) row[k] = typeof r[k] === "object" ? JSON.stringify(r[k]).slice(0, 120) : r[k];
      }
      items.push(row);
    }
    if (d.type === "list") {
      const check = (d.items || []).find(x => x && x.type === "checklist");
      if (check) items.push({ checklist: Object.fromEntries(Object.entries(check.items).map(([k, v]) => [k, v.value])) });
    }
    out.push({ id, title: au.title, score: au.score, savings, display_value: au.displayValue || null, items });
  }
  return out;
}

function filmstrip(lhr) {
  const d = lhr.audits["screenshot-thumbnails"] && lhr.audits["screenshot-thumbnails"].details;
  const fin = lhr.audits["final-screenshot"] && lhr.audits["final-screenshot"].details;
  return {
    throttling: lhr.configSettings.throttlingMethod,
    frames: d && d.items ? d.items.map(f => ({ timing: f.timing, data: f.data })) : [],
    final: fin ? fin.data : null,
  };
}

function main() {
  const o = parseArgs(process.argv.slice(2));
  checkNode();
  const cmd = lighthouseCommand(o.lighthouse);
  const variants = o.variant.map(s => { const i = s.indexOf("="); return { name: s.slice(0, i), origin: s.slice(i + 1).replace(/\/$/, "") }; });
  const pages = o.pages.split(",").map(s => s.trim()).filter(Boolean);
  const profiles = o.profiles.split(",").map(s => s.trim()).filter(Boolean);
  const out = resolve(o.out);
  const raw = join(out, "raw");
  mkdirSync(raw, { recursive: true });

  const result = { meta: { started: new Date().toISOString(), variants, pages, profiles, runs: o.runs,
    warmup: o.warmup, throttling: "simulate", lighthouse: null, chrome: null, node: process.versions.node }, runs: [] };
  const insights = [];
  const strips = [];
  const total = pages.length * profiles.length * (o.runs * 2 + o.warmup * 2);
  let done = 0, seq = 0;

  const one = (v, page, profile, kind, idx) => {
    const url = v.origin + page;
    const tag = `${v.name}_${page.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "root"}_${profile}_${kind}${idx}`;
    const p = join(raw, `${tag}.json`);
    let r = runLighthouse(cmd, url, profile, p);
    if (r.error) { console.error(`retry ${tag}: ${r.error}`); r = runLighthouse(cmd, url, profile, p); }
    done++;
    process.stderr.write(`\r[${done}/${total}] ${tag}            `);
    return { r, p, url };
  };

  for (const page of pages) {
    for (const profile of profiles) {
      for (let w = 0; w < o.warmup; w++) for (const v of variants) { const { p } = one(v, page, profile, "warm", w); rmSync(p, { force: true }); }
      for (let i = 0; i < o.runs; i++) {
        // ABBA: even runs A then B, odd runs B then A.
        const order = i % 2 === 0 ? variants : [...variants].reverse();
        for (const v of order) {
          const { r, p, url } = one(v, page, profile, "run", i);
          const row = { seq: seq++, variant: v.name, page, profile, run: i, url };
          if (r.error) row.error = r.error;
          if (r.lhr && !r.error) {
            row.metrics = extractMetrics(r.lhr);
            row.lcp_element = lcpElement(r.lhr);
            result.meta.lighthouse = r.lhr.lighthouseVersion;
            result.meta.chrome = r.lhr.environment && r.lhr.environment.hostUserAgent;
            if (i === 0) insights.push({ variant: v.name, page, profile, insights: extractInsights(r.lhr) });
          }
          result.runs.push(row);
          const keep = o.keepRaw === "all" || (o.keepRaw === "first" && i === 0);
          if (!keep) rmSync(p, { force: true });
        }
      }
      if (o.filmstrip === "devtools") {
        for (const v of variants) {
          const p = join(raw, `${v.name}_film_${profile}_${strips.length}.json`);
          const r = runLighthouse(cmd, v.origin + page, profile, p, "devtools");
          if (r.lhr && !r.error) strips.push({ variant: v.name, page, profile, ...filmstrip(r.lhr) });
          rmSync(p, { force: true });
        }
      }
    }
  }
  process.stderr.write("\n");
  result.meta.finished = new Date().toISOString();
  writeFileSync(join(out, "measure.json"), JSON.stringify(result, null, 1));
  writeFileSync(join(out, "insights.json"), JSON.stringify(insights, null, 1));
  if (strips.length) writeFileSync(join(out, "filmstrips.json"), JSON.stringify(strips));
  const errors = result.runs.filter(r => r.error).length;
  console.log(JSON.stringify({ out: join(out, "measure.json"), runs: result.runs.length, errors, lighthouse: result.meta.lighthouse }));
  if (errors > result.runs.length / 4) { console.error("too many failed runs; fix the server or Chrome before trusting this measurement"); process.exit(1); }
}

main();

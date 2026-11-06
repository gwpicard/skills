#!/usr/bin/env node
// Visual guard for a Pageload Loop: screenshots, pixel diff and blind pairs.
//
// Usage:
//   node visual_diff.mjs capture --origin http://localhost:4002 --pages /,/pricing --out DIR [--mask SEL,SEL] [--viewport-only]
//   node visual_diff.mjs compare --base DIR --cand DIR --out DIR [--max-ratio 0.001]
//   node visual_diff.mjs pair    --base DIR --cand DIR --shots NAME,NAME --out DIR [--key-dir DIR]
//   node visual_diff.mjs axe     --origin http://localhost:4001 --pages /,/pricing --out FILE.json
//
// capture  One fresh browser context per shot, at 390x844 (mobile) and 1440x900 (desktop),
//          device scale 1, reduced motion, CSS animations and transitions off, caret hidden.
//          Waits for load, network idle (best effort), document.fonts.ready and images,
//          scrolls once to trigger lazy loading, then takes a full-page shot.
//          Files: <page-slug>_mobile.png, <page-slug>_desktop.png.
//          --mask hides the given selectors behind a solid box (off by default; use only
//          when an A/A capture shows the page differs between identical loads).
// compare  pixelmatch per shot (per-pixel threshold 0.1). A shot passes when the share of
//          differing pixels is at most --max-ratio (default 0.001 = 0.1%). Different sizes
//          are padded, and the padding counts as different. Writes diff PNGs and
//          compare.json; prints JSON. Exit code 0 when every shot passes, 1 otherwise.
//          Cluster check: a shot under the ratio still fails (goes to the critic) when one
//          16x16 tile has at least 10% differing pixels. Scattered anti-aliasing noise does
//          not trip it; a changed word or a missing icon does, though both stay under 0.1%
//          of a full page. Turn it off with --no-cluster-check.
// pair     For shots that failed, copies base and candidate as A.png and B.png in random
//          order into DIR/<shot>/ for a blind critic. The key goes to --key-dir
//          (default ~/.cache/pageload-loop/<project>/keys), outside the project.
// axe      Accessibility scan with axe-core (@axe-core/playwright, default rule set) per page at
//          both viewports, after the same settle steps as capture. Writes FILE.json with one
//          entry per page and viewport: violations as rule id, impact, help and one node per
//          target selector. compare.py a11y diffs two of these files. Informational only.
//
// Dependencies (install next to this script): playwright, pixelmatch, pngjs; @axe-core/playwright for axe.
// If Playwright's own Chromium is not installed, the script falls back to the local Chrome.

import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, join, resolve } from "node:path";
import { randomInt } from "node:crypto";

const VIEWPORTS = {
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};
const FREEZE_CSS = `*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;
animation-iteration-count:1!important;transition:none!important;caret-color:transparent!important;
scroll-behavior:auto!important}`;

function args(argv) {
  const a = { _: argv[0] };
  for (let i = 1; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith("--")) continue;
    const name = k.slice(2);
    if (name === "viewport-only" || name === "no-cluster-check") a[name] = true;
    else a[name] = argv[++i];
  }
  return a;
}

const slug = p => p.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "root";

async function launch() {
  const { chromium } = await import("playwright");
  try { return await chromium.launch(); }
  catch (e) {
    try { return await chromium.launch({ channel: "chrome" }); }
    catch { throw new Error(`no browser: run "npx playwright install chromium" (${e.message.split("\n")[0]})`); }
  }
}

async function settle(page, fullPage) {
  try { await page.waitForLoadState("networkidle", { timeout: 10000 }); } catch { /* best effort */ }
  await page.addStyleTag({ content: FREEZE_CSS });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  if (fullPage) {
    await page.evaluate(async () => {
      const step = window.innerHeight;
      for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, 100));
      }
      window.scrollTo(0, 0);
    });
    try { await page.waitForLoadState("networkidle", { timeout: 5000 }); } catch { /* best effort */ }
  }
  await page.evaluate(() => Promise.all([...document.images].filter(i => !i.complete)
    .map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 5000); }))));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(300);
}

async function capture(a) {
  if (!a.origin || !a.out) throw new Error("capture needs --origin and --out");
  const out = resolve(a.out);
  mkdirSync(out, { recursive: true });
  const pages = (a.pages || "/").split(",").map(s => s.trim()).filter(Boolean);
  const masks = a.mask ? a.mask.split(",").map(s => s.trim()).filter(Boolean) : [];
  const fullPage = !a["viewport-only"];
  const browser = await launch();
  const shots = [];
  try {
    for (const p of pages) {
      for (const [vp, opts] of Object.entries(VIEWPORTS)) {
        const ctx = await browser.newContext({ ...opts, reducedMotion: "reduce", colorScheme: "light",
          locale: "en-US", timezoneId: "UTC" });
        const page = await ctx.newPage();
        const url = a.origin.replace(/\/$/, "") + p;
        await page.goto(url, { waitUntil: "load", timeout: 60000 });
        await settle(page, fullPage);
        const file = join(out, `${slug(p)}_${vp}.png`);
        await page.screenshot({ path: file, fullPage, animations: "disabled", caret: "hide",
          mask: masks.map(s => page.locator(s)), maskColor: "#ff00ff" });
        shots.push({ name: basename(file, ".png"), url, file });
        await ctx.close();
      }
    }
  } finally { await browser.close(); }
  writeFileSync(join(out, "capture.json"), JSON.stringify({ shots, masks, fullPage }, null, 1));
  console.log(JSON.stringify({ out, shots: shots.map(s => s.name) }));
}

async function compare(a) {
  if (!a.base || !a.cand || !a.out) throw new Error("compare needs --base, --cand and --out");
  const { PNG } = await import("pngjs");
  const pixelmatch = (await import("pixelmatch")).default;
  const maxRatio = a["max-ratio"] ? parseFloat(a["max-ratio"]) : 0.001;
  const out = resolve(a.out);
  mkdirSync(out, { recursive: true });
  const names = readdirSync(a.base).filter(f => f.endsWith(".png")).map(f => basename(f, ".png"));
  const results = [];
  for (const name of names) {
    const bp = join(a.base, `${name}.png`), cp = join(a.cand, `${name}.png`);
    if (!existsSync(cp)) { results.push({ name, error: "missing in candidate", pass: false, ratio: 1 }); continue; }
    const b = PNG.sync.read(readFileSync(bp)), c = PNG.sync.read(readFileSync(cp));
    const w = Math.max(b.width, c.width), h = Math.max(b.height, c.height);
    const pad = img => {
      if (img.width === w && img.height === h) return img;
      const p = new PNG({ width: w, height: h });
      p.data.fill(0);
      for (let i = 3; i < p.data.length; i += 4) { p.data[i - 3] = 255; p.data[i - 1] = 255; p.data[i] = 255; }
      PNG.bitblt(img, p, 0, 0, img.width, img.height, 0, 0);
      return p;
    };
    const pb = pad(b), pc = pad(c);
    const diff = new PNG({ width: w, height: h });
    const n = pixelmatch(pb.data, pc.data, diff.data, w, h, { threshold: 0.1 });
    writeFileSync(join(out, `${name}_diff.png`), PNG.sync.write(diff));
    const ratio = n / (w * h);
    const cluster = a["no-cluster-check"] ? null : densestTile(pixelmatch, pb, pc, w, h, PNG);
    const clustered = cluster ? cluster.share >= TILE_SHARE : false;
    results.push({ name, diff_pixels: n, total: w * h, ratio, pass: ratio <= maxRatio && !clustered,
      clustered, densest_tile: cluster,
      size_base: [b.width, b.height], size_cand: [c.width, c.height],
      size_mismatch: b.width !== c.width || b.height !== c.height });
  }
  const summary = { max_ratio: maxRatio, pass: results.every(r => r.pass),
    worst_ratio: Math.max(0, ...results.map(r => r.ratio)), failed: results.filter(r => !r.pass).map(r => r.name), shots: results };
  writeFileSync(join(out, "compare.json"), JSON.stringify(summary, null, 1));
  console.log(JSON.stringify(summary));
  process.exitCode = summary.pass ? 0 : 1;
}

const TILE = 16, TILE_SHARE = 0.10;

function densestTile(pixelmatch, pb, pc, w, h, PNG) {
  // diffMask draws only counted differences (not anti-aliasing) on a transparent image.
  const mask = new PNG({ width: w, height: h });
  pixelmatch(pb.data, pc.data, mask.data, w, h, { threshold: 0.1, diffMask: true });
  const cols = Math.ceil(w / TILE), counts = new Uint32Array(cols * Math.ceil(h / TILE));
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (mask.data[(y * w + x) * 4 + 3] > 0) counts[Math.floor(y / TILE) * cols + Math.floor(x / TILE)]++;
  }
  let best = 0, at = 0;
  for (let i = 0; i < counts.length; i++) if (counts[i] > best) { best = counts[i]; at = i; }
  return { x: (at % cols) * TILE, y: Math.floor(at / cols) * TILE, pixels: best, share: best / (TILE * TILE) };
}

function pair(a) {
  if (!a.base || !a.cand || !a.shots || !a.out) throw new Error("pair needs --base, --cand, --shots and --out");
  const project = basename(process.cwd());
  const keyDir = resolve(a["key-dir"] || join(homedir(), ".cache", "pageload-loop", project, "keys"));
  mkdirSync(keyDir, { recursive: true });
  const key = {};
  for (const name of a.shots.split(",").map(s => s.trim()).filter(Boolean)) {
    const dir = join(resolve(a.out), name);
    mkdirSync(dir, { recursive: true });
    const candIsA = randomInt(2) === 1;
    // copyFileSync copies bytes only; file dates would otherwise hint at which side is new.
    copyFileSync(join(a.base, `${name}.png`), join(dir, candIsA ? "B.png" : "A.png"));
    copyFileSync(join(a.cand, `${name}.png`), join(dir, candIsA ? "A.png" : "B.png"));
    key[name] = { A: candIsA ? "cand" : "base", B: candIsA ? "base" : "cand" };
  }
  const keyFile = join(keyDir, `${basename(resolve(a.out))}.json`);
  writeFileSync(keyFile, JSON.stringify(key, null, 1));
  console.log(JSON.stringify({ pairs: resolve(a.out), key: keyFile }));
}

async function axe(a) {
  if (!a.origin || !a.out) throw new Error("axe needs --origin and --out");
  let AxeBuilder;
  try { AxeBuilder = (await import("@axe-core/playwright")).default; }
  catch { throw new Error('@axe-core/playwright is not installed: run setup_tools.sh without --no-a11y'); }
  const pages = (a.pages || "/").split(",").map(s => s.trim()).filter(Boolean);
  const browser = await launch();
  const results = [];
  let version = null;
  try {
    for (const p of pages) {
      for (const [vp, opts] of Object.entries(VIEWPORTS)) {
        const ctx = await browser.newContext({ ...opts, reducedMotion: "reduce", colorScheme: "light",
          locale: "en-US", timezoneId: "UTC" });
        const page = await ctx.newPage();
        const url = a.origin.replace(/\/$/, "") + p;
        await page.goto(url, { waitUntil: "load", timeout: 60000 });
        await settle(page, true);
        const r = await new AxeBuilder({ page }).analyze();
        version = r.testEngine && r.testEngine.version;
        results.push({ page: p, viewport: vp, url, violations: r.violations.map(v => ({
          id: v.id, impact: v.impact, help: v.help,
          nodes: v.nodes.map(n => ({ target: n.target.flat().join(" >> "), html: (n.html || "").slice(0, 200) })),
        })) });
        await ctx.close();
      }
    }
  } finally { await browser.close(); }
  const out = resolve(a.out);
  mkdirSync(resolve(out, ".."), { recursive: true });
  writeFileSync(out, JSON.stringify({ origin: a.origin, axe: version, results }, null, 1));
  console.log(JSON.stringify({ out, scans: results.length,
    violations: results.reduce((n, r) => n + r.violations.reduce((m, v) => m + v.nodes.length, 0), 0) }));
}

const a = args(process.argv.slice(2));
const run = { capture, compare, pair, axe }[a._];
if (!run) {
  console.log(readFileSync(new URL(import.meta.url), "utf8").split("\n").filter(l => l.startsWith("//")).map(l => l.slice(3)).join("\n"));
  process.exit(a._ ? 2 : 0);
}
Promise.resolve(run(a)).catch(e => { console.error(e.message); process.exit(2); });

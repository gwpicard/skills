#!/usr/bin/env node
// Rendered pass for a website review: screenshots, axe-core and a few measured checks.
//
// Usage:
//   node render_audit.mjs --urls https://example.com,https://example.com/pricing --out DIR [--no-full-page] [--max-nodes 8]
//
// For each URL, one fresh browser context per viewport: mobile 390x844 (touch) and desktop 1440x900,
// device scale 1, reduced motion, CSS animations and transitions off. Waits for load, network idle
// (best effort), document.fonts.ready and images, scrolls once to trigger lazy loading.
//
// Per viewport:
//   screenshots  <slug>_<viewport>_fold.png (first screen) and <slug>_<viewport>.png (full page)
//   axe          @axe-core/playwright with tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice.
//                Each violation: rule id, impact, WCAG success criteria (from axe tags), node count,
//                up to --max-nodes node selectors with a short HTML excerpt and axe's failure summary.
// Mobile only:
//   overflow     horizontal overflow at 390 px (document wider than the viewport) and the elements
//                that cross the right edge while their parent does not (the likely causes).
//   tap_targets  interactive elements smaller than 24x24 CSS px (WCAG 2.2 SC 2.5.8). Inline links in a
//                sentence are skipped (SC exception). Targets whose 24 px circle touches no other target
//                are counted as "spaced" (SC spacing exception) and not listed as failures.
//   reflow_320   the same overflow check at 320 px wide (WCAG SC 1.4.10 Reflow).
// Desktop only:
//   focus        presses Tab up to 25 times; for each stop, records whether any of outline, box-shadow,
//                border, background, color or text-decoration changed against the unfocused state, and
//                whether the focused element is visible on screen (SC 2.4.7, 2.4.11). Also lists elements
//                with a pointer cursor that cannot take keyboard focus (SC 2.1.1 candidates).
// A missing viewport meta tag shows as mobile_layout_width 980: the phone renders a zoomed-out desktop page.
//
// Writes DIR/render_audit.json (full results) and prints a short JSON summary to stdout.
// Exit code 0 when every URL was audited, 1 when some URL failed, 2 when no browser or module is available.
//
// Dependencies (install next to this script with setup_render.sh): playwright, @axe-core/playwright.
// If Playwright's own Chromium is not installed, the script falls back to the local Chrome.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const VIEWPORTS = {
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};
const AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"];
const FREEZE_CSS = `*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;
animation-iteration-count:1!important;transition:none!important;caret-color:transparent!important;
scroll-behavior:auto!important}`;
const NOT_TESTED = [
  "Runtime flows (form submission, checkout, sign-up, menus opened by click) were not exercised.",
  "Logged-in and personalised states were not visited.",
  "No real assistive technology (screen reader, switch, voice control) was used.",
  "Automated checks find only part of WCAG failures; axe 'incomplete' items need a human decision.",
  "Cookie or consent banners may cover content in screenshots and were not dismissed.",
];

function args(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith("--")) continue;
    const name = k.slice(2);
    if (name === "no-full-page" || name === "help") a[name] = true;
    else a[name] = argv[++i];
  }
  return a;
}

const slug = u => {
  const x = new URL(u);
  return (x.hostname + x.pathname).replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "root";
};

// "wcag143" -> "1.4.3", "wcag1410" -> "1.4.10"; level tags such as "wcag2aa" are skipped.
const scFromTags = tags => tags.map(t => /^wcag(\d)(\d)(\d+)$/.exec(t)).filter(Boolean).map(m => `${m[1]}.${m[2]}.${m[3]}`);
const levelFromTags = tags => (tags.find(t => /^wcag2\d?a{1,3}$/.test(t)) || "").replace(/^wcag(2)(\d?)(a+)$/,
  (_, v, m, l) => `WCAG 2.${m || "0"} ${l.toUpperCase()}`) || null;

async function launch() {
  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch { fail("playwright is not installed next to this script; run setup_render.sh first"); }
  try { return { browser: await chromium.launch(), engine: "playwright-chromium" }; }
  catch (e) {
    try { return { browser: await chromium.launch({ channel: "chrome" }), engine: "chrome" }; }
    catch { fail(`no browser: run "npx playwright install chromium" in the tools folder (${e.message.split("\n")[0]})`); }
  }
}

function fail(msg) { console.error(msg); process.exit(2); }

async function settle(page, fullPage) {
  try { await page.waitForLoadState("networkidle", { timeout: 10000 }); } catch { /* best effort */ }
  await page.addStyleTag({ content: FREEZE_CSS }).catch(() => {});
  await page.evaluate(() => document.fonts && document.fonts.ready);
  if (fullPage) {
    await page.evaluate(async () => {
      const step = window.innerHeight;
      const max = Math.min(document.documentElement.scrollHeight, 30000);
      for (let y = 0; y < max; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 80)); }
      window.scrollTo(0, 0);
    });
    try { await page.waitForLoadState("networkidle", { timeout: 5000 }); } catch { /* best effort */ }
  }
  await page.evaluate(() => Promise.all([...document.images].filter(i => !i.complete)
    .map(i => new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 5000); }))));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(300);
}

async function runAxe(page, maxNodes) {
  const { default: AxeBuilder } = await import("@axe-core/playwright");
  const r = await new AxeBuilder({ page }).withTags(AXE_TAGS).analyze();
  const violations = r.violations.map(v => ({
    id: v.id, impact: v.impact, help: v.help, help_url: v.helpUrl,
    wcag_sc: scFromTags(v.tags), wcag_level: levelFromTags(v.tags),
    best_practice_only: v.tags.includes("best-practice") && scFromTags(v.tags).length === 0,
    count: v.nodes.length,
    nodes: v.nodes.slice(0, maxNodes).map(n => ({
      target: n.target.flat().join(" "), html: n.html.slice(0, 200),
      summary: (n.failureSummary || "").split("\n").slice(0, 3).join(" ").slice(0, 300),
    })),
  }));
  const order = { critical: 0, serious: 1, moderate: 2, minor: 3 };
  violations.sort((a, b) => (order[a.impact] ?? 4) - (order[b.impact] ?? 4) || b.count - a.count);
  return {
    engine: `axe-core ${r.testEngine.version}`, tags: AXE_TAGS,
    violation_rules: violations.length, violation_nodes: violations.reduce((s, v) => s + v.count, 0),
    violations,
    incomplete: r.incomplete.map(v => ({ id: v.id, help: v.help, wcag_sc: scFromTags(v.tags), count: v.nodes.length })),
    passes: r.passes.length,
  };
}

// Shared in-page helper: a short, readable CSS selector.
const SELECTOR_FN = `function __sel(el){
  if(!el||el.nodeType!==1)return "";
  if(el.id&&/^[A-Za-z][\\w-]*$/.test(el.id))return "#"+el.id;
  const parts=[];let n=el,depth=0;
  while(n&&n.nodeType===1&&depth<4){
    if(n.id&&/^[A-Za-z][\\w-]*$/.test(n.id)){parts.unshift("#"+n.id);break;}
    let s=n.tagName.toLowerCase();
    const cls=[...n.classList].filter(c=>/^[A-Za-z][\\w-]*$/.test(c)).slice(0,2);
    if(cls.length)s+="."+cls.join(".");
    const p=n.parentElement;
    if(p){const same=[...p.children].filter(c=>c.tagName===n.tagName);if(same.length>1)s+=":nth-of-type("+(same.indexOf(n)+1)+")";}
    parts.unshift(s);n=p;depth++;
  }
  return parts.join(" > ");
}`;

async function overflow(page) {
  return page.evaluate(`(() => { ${SELECTOR_FN}
    const vw = document.documentElement.clientWidth;
    const sw = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
    const offenders = [];
    if (sw > vw + 1) {
      for (const el of document.body.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.right <= vw + 1) continue;
        const p = el.parentElement, pr = p ? p.getBoundingClientRect() : null;
        if (pr && pr.right > vw + 1) continue;
        offenders.push({ selector: __sel(el), right: Math.round(r.right), width: Math.round(r.width) });
        if (offenders.length >= 10) break;
      }
    }
    return { viewport_width: vw, scroll_width: sw, horizontal_overflow: sw > vw + 1, offenders };
  })()`);
}

async function tapTargets(page) {
  return page.evaluate(`(() => { ${SELECTOR_FN}
    const MIN = 24;
    const q = 'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[role=checkbox],[role=radio],[role=tab],[role=switch],[role=menuitem]';
    const items = [];
    for (const el of document.querySelectorAll(q)) {
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none" || el.closest("[aria-hidden=true],[inert]")) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      // SC 2.5.8 inline exception: a link inside a sentence of text.
      if (el.tagName === "A" && cs.display === "inline") {
        const block = el.closest("p,li,td,dd,figcaption,blockquote,label") || el.parentElement;
        const own = (el.textContent || "").trim().length, all = (block ? block.textContent : "").trim().length;
        if (all - own > 20) continue;
      }
      items.push({ el, r });
    }
    const small = items.filter(i => i.r.width < MIN || i.r.height < MIN);
    const center = r => [r.left + r.width / 2, r.top + r.height / 2];
    const distToRect = ([x, y], r) => Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom));
    const failing = [];
    let spaced = 0;
    for (const s of small) {
      const c = center(s.r);
      const clash = items.some(o => o !== s && (small.includes(o)
        ? Math.hypot(c[0] - center(o.r)[0], c[1] - center(o.r)[1]) < MIN
        : distToRect(c, o.r) < MIN / 2));
      if (!clash) { spaced++; continue; }
      failing.push({ selector: __sel(s.el), width: Math.round(s.r.width), height: Math.round(s.r.height),
        text: ((s.el.innerText || s.el.getAttribute("aria-label") || s.el.value || "") + "").trim().slice(0, 60) });
    }
    return { min_px: MIN, checked: items.length, undersized: small.length, spaced_exception: spaced,
      failing_count: failing.length, failing: failing.slice(0, 25) };
  })()`);
}

async function focusCheck(page) {
  const SNAP = `function __snap(el){const c=getComputedStyle(el);return [c.outlineStyle,c.outlineWidth,c.outlineColor,
    c.boxShadow,c.borderTopColor,c.borderBottomColor,c.borderBottomWidth,c.backgroundColor,c.color,c.textDecorationLine].join("|");}`;
  await page.evaluate(`(() => { ${SNAP}
    window.__wrBase = new Map();
    for (const el of document.querySelectorAll('a[href],button,input,select,textarea,summary,[tabindex],[contenteditable=true]'))
      window.__wrBase.set(el, __snap(el));
  })()`);
  await page.mouse.click(1, 1).catch(() => {});
  await page.evaluate(() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); window.scrollTo(0, 0); });
  const stops = [];
  for (let i = 0; i < 25; i++) {
    await page.keyboard.press("Tab");
    const s = await page.evaluate(`(() => { ${SELECTOR_FN} ${SNAP}
      const el = document.activeElement;
      if (!el || el === document.body || el === document.documentElement) return null;
      const r = el.getBoundingClientRect();
      const base = window.__wrBase.get(el);
      return { selector: __sel(el), tag: el.tagName.toLowerCase(),
        text: ((el.innerText || el.getAttribute("aria-label") || "") + "").trim().slice(0, 60),
        indicator_change: base === undefined ? null : base !== __snap(el),
        visible_on_screen: r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth };
    })()`);
    if (!s) break;
    if (stops.length && stops[0].selector === s.selector) break; // wrapped around
    stops.push(s);
  }
  // Elements that look clickable (pointer cursor) but cannot receive keyboard focus (SC 2.1.1 candidates).
  const pointerOnly = await page.evaluate(`(() => { ${SELECTOR_FN}
    const focusable = 'a[href],button,input,select,textarea,summary,[tabindex],[contenteditable=true],label';
    const out = [];
    for (const el of document.body.querySelectorAll("*")) {
      if (el.closest(focusable)) continue;
      const cs = getComputedStyle(el);
      if (cs.cursor !== "pointer" || (el.parentElement && getComputedStyle(el.parentElement).cursor === "pointer")) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0 || el.querySelector(focusable)) continue;
      out.push({ selector: __sel(el), text: (el.innerText || "").trim().slice(0, 60) });
      if (out.length >= 15) break;
    }
    return out;
  })()`);
  return {
    pointer_not_focusable: pointerOnly,
    stops_checked: stops.length,
    no_style_change: stops.filter(s => s.indicator_change === false).map(s => ({ selector: s.selector, text: s.text })),
    focus_off_screen: stops.filter(s => !s.visible_on_screen).map(s => ({ selector: s.selector, text: s.text })),
    first_stops: stops.slice(0, 5).map(s => `${s.tag}: ${s.text || s.selector}`),
    note: "A style change can still be too faint to see; check the focus screenshots or inspect manually. Iframes and shadow DOM are not covered.",
  };
}

async function auditUrl(browser, url, out, opts) {
  const res = { url, viewports: {} };
  for (const [vp, ctxOpts] of Object.entries(VIEWPORTS)) {
    const ctx = await browser.newContext({ ...ctxOpts, reducedMotion: "reduce", colorScheme: "light", locale: "en-US" });
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(String(e.message).slice(0, 200)));
    const v = {};
    try {
      let resp = null;
      try { resp = await page.goto(url, { waitUntil: "load", timeout: 45000 }); }
      catch (e) { if (!/Timeout/i.test(e.message)) throw e; v.load_timeout = true; }
      await settle(page, opts.fullPage);
      if (vp === "mobile") {
        Object.assign(res, await page.evaluate(() => ({
          final_url: location.href, title: document.title, lang: document.documentElement.lang || null,
          viewport_meta: document.querySelector("meta[name=viewport]")?.content || null,
        })));
        res.status = resp ? resp.status() : null;
      }
      const base = join(out, `${slug(url)}_${vp}`);
      await page.screenshot({ path: `${base}_fold.png`, animations: "disabled", caret: "hide" });
      v.screenshot_fold = `${base}_fold.png`;
      if (opts.fullPage) {
        await page.screenshot({ path: `${base}.png`, fullPage: true, animations: "disabled", caret: "hide" });
        v.screenshot_full = `${base}.png`;
      }
      v.axe = await runAxe(page, opts.maxNodes);
      if (vp === "mobile") {
        v.overflow = await overflow(page);
        v.tap_targets = await tapTargets(page);
        await page.setViewportSize({ width: 320, height: 844 });
        await page.waitForTimeout(300);
        res.reflow_320 = await overflow(page);
      } else {
        v.focus = await focusCheck(page);
      }
    } catch (e) {
      v.error = e.message.split("\n")[0];
    }
    v.page_errors = errors.slice(0, 10);
    res.viewports[vp] = v;
    await ctx.close();
  }
  return res;
}

function summarize(r) {
  const m = r.viewports.mobile || {}, d = r.viewports.desktop || {};
  const ids = new Set([...(m.axe?.violations || []), ...(d.axe?.violations || [])].map(v => `${v.id}(${v.impact})`));
  return {
    url: r.url, status: r.status ?? null,
    errors: [m.error, d.error].filter(Boolean),
    axe_rules_failed: [...ids],
    axe_nodes: { mobile: m.axe?.violation_nodes ?? null, desktop: d.axe?.violation_nodes ?? null },
    viewport_meta: r.viewport_meta ?? null,
    mobile_layout_width: m.overflow?.viewport_width ?? null,
    overflow_390: m.overflow?.horizontal_overflow ?? null,
    overflow_320: r.reflow_320?.horizontal_overflow ?? null,
    tap_targets_failing: m.tap_targets?.failing_count ?? null,
    focus_no_style_change: d.focus ? d.focus.no_style_change.length : null,
    pointer_not_focusable: d.focus ? d.focus.pointer_not_focusable.length : null,
  };
}

async function main() {
  const a = args(process.argv.slice(2));
  if (a.help || !a.urls || !a.out) {
    console.log(readFileSync(new URL(import.meta.url), "utf8").split("\n").filter(l => l.startsWith("//")).map(l => l.slice(3)).join("\n"));
    process.exit(a.help ? 0 : 2);
  }
  const urls = a.urls.split(",").map(s => s.trim()).filter(Boolean);
  for (const u of urls) { try { new URL(u); } catch { fail(`not a URL: ${u}`); } }
  const out = resolve(a.out);
  mkdirSync(out, { recursive: true });
  const opts = { fullPage: !a["no-full-page"], maxNodes: parseInt(a["max-nodes"] || "8", 10) };
  const { browser, engine } = await launch();
  const browserVersion = `${engine} ${browser.version()}`;
  const pages = [];
  try { for (const u of urls) pages.push(await auditUrl(browser, u, out, opts)); }
  finally { await browser.close(); }
  const { createRequire } = await import("node:module");
  const req = createRequire(import.meta.url);
  let pw = null; try { pw = req("playwright/package.json").version; } catch { /* unknown */ }
  const result = {
    generated_at: new Date().toISOString(),
    tool: { playwright: pw, browser: browserVersion, viewports: { mobile: "390x844", desktop: "1440x900" } },
    evidence: "measured",
    not_tested: NOT_TESTED,
    pages,
  };
  const file = join(out, "render_audit.json");
  writeFileSync(file, JSON.stringify(result, null, 1));
  const failed = pages.filter(p => Object.values(p.viewports).some(v => v.error));
  console.log(JSON.stringify({ results: file, browser: result.tool.browser, pages: pages.map(summarize) }, null, 1));
  process.exitCode = failed.length ? 1 : 0;
}

main().catch(e => { console.error(e.message); process.exit(2); });

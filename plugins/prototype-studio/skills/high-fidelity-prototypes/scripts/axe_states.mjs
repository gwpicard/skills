// Run axe-core against every named state of a prototype at every viewport, and list the violations.
//
//   node axe_states.mjs <url-or-file>... [--viewports 1440x900,390x844] [--json out.json]
//   node axe_states.mjs --states states.json [--viewports ...] [--json out.json]
//
// states.json lists the states the prototype defines (presets, deep links, open dialogs, forms
// with errors). Steps run in order after the page loads:
//   [{ "name": "default", "url": "index.html" },
//    { "name": "invite dialog", "url": "index.html#team", "steps": [{ "click": "#invite" }] },
//    { "name": "form errors", "url": "index.html?preset=signup",
//      "steps": [{ "fill": ["#email", "not-an-email"] }, { "click": "button[type=submit]" }, { "wait": 300 }] }]
// Step kinds: click (selector), fill ([selector, text]), press (key), wait (ms).
//
// Rules: WCAG 2.0, 2.1 and 2.2 A and AA tags. Exit code 1 when any violation is found or a state fails to load.
// An automated scan finds a subset of WCAG failures; it does not establish conformance.
//
// Needs Playwright and @axe-core/playwright: run `npm i playwright @axe-core/playwright` in a
// scratch folder and run the script from there (or set PLAYWRIGHT_PATH and AXE_PLAYWRIGHT_PATH).
// Set CHROME_PATH to use an installed Chrome instead of Playwright's download.
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
import { pathToFileURL } from 'url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const valued = new Set(['--viewports', '--json', '--states']);
const targets = args.filter((a, i) => !a.startsWith('--') && !valued.has(args[i - 1]));
const states = opt('states') ? JSON.parse(fs.readFileSync(opt('states'), 'utf8')) : targets.map(t => ({ name: t, url: t }));
if (!states.length) { console.log(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(0, 19).join('\n')); process.exit(2); }

// Resolve the dependencies from the folder the script is run in, so they can live in a scratch folder.
const local = createRequire(path.join(process.cwd(), 'noop.js'));
const load = async (env, name) => {
  if (process.env[env]) return import(pathToFileURL(path.resolve(process.env[env])).href);
  try { return await import(pathToFileURL(local.resolve(name)).href); } catch { return import(name); }
};
const pw = await load('PLAYWRIGHT_PATH', 'playwright');
const chromium = pw.chromium || pw.default.chromium;
const axeModule = await load('AXE_PLAYWRIGHT_PATH', '@axe-core/playwright');
const AxeBuilder = axeModule.default?.default || axeModule.default || axeModule.AxeBuilder;

const viewports = opt('viewports', '1440x900,390x844').split(',').map(v => v.split('x').map(Number));
const base = opt('states') ? path.dirname(path.resolve(opt('states'))) : process.cwd();
const toUrl = u => /^https?:|^file:/.test(u) ? u : (() => {
  const [file, rest = ''] = u.split(/(?=[?#])/);
  return pathToFileURL(path.resolve(base, file)).href + rest;
})();

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const results = [];
for (const s of states) {
  for (const [width, height] of viewports) {
    const context = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce' });
    const page = await context.newPage();
    const row = { state: s.name, viewport: `${width}x${height}`, url: toUrl(s.url) };
    try {
      await page.goto(row.url, { waitUntil: 'networkidle', timeout: 60000 });
      for (const step of s.steps || []) {
        if (step.click) await page.click(step.click);
        else if (step.fill) await page.fill(step.fill[0], step.fill[1]);
        else if (step.press) await page.keyboard.press(step.press);
        else if (step.wait) await page.waitForTimeout(step.wait);
      }
      await page.waitForTimeout(200);
      const r = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']).analyze();
      row.violations = r.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.map(n => n.target.join(' ')) }));
      row.incomplete = r.incomplete.length; // needs a human decision (for example contrast over images)
    } catch (e) { row.error = e.message.split('\n')[0]; }
    results.push(row);
    await context.close();
  }
}
await browser.close();

if (opt('json')) fs.writeFileSync(opt('json'), JSON.stringify(results, null, 2));
console.log('| State | Viewport | Violations | Needs review |');
console.log('|---|---|---|---|');
for (const r of results) console.log(`| ${r.state} | ${r.viewport} | ${r.error ? 'error: ' + r.error : r.violations.length} | ${r.incomplete ?? ''} |`);
for (const r of results.filter(r => r.violations?.length)) {
  console.log(`\n${r.state} @ ${r.viewport}`);
  for (const v of r.violations) console.log(`- ${v.impact} ${v.id}: ${v.help} -> ${v.nodes.slice(0, 5).join(', ')}${v.nodes.length > 5 ? ` (+${v.nodes.length - 5})` : ''}`);
}
process.exit(results.some(r => r.error || r.violations?.length) ? 1 : 0);

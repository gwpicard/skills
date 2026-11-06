// Measure the computed anatomy of a page, so references and builds can be compared in numbers.
//
//   node measure_reference.mjs <url-or-file> [--width 1440] [--json out.json]
//   node measure_reference.mjs a.html b.html c.html        # several pages -> one comparison table
//
// Reports: page height in viewports, content width, type sizes and weights in use, headline
// letter-spacing, body line length, section spacing, radii, colour count, and counts of
// common agent defaults (pills, eyebrow labels, uppercase mono labels, accent word in the h1,
// negative headline tracking, cream background). Counts flag patterns; they do not judge them.
//
// Needs Puppeteer (see capture.mjs).
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const valued = new Set(['--width', '--json']);
const targets = args.filter((a, i) => !a.startsWith('--') && !valued.has(args[i - 1]));
if (!targets.length) { console.log(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(0, 11).join('\n')); process.exit(2); }

const { default: puppeteer } = await import(process.env.PUPPETEER_PATH || 'puppeteer');
const w = +opt('width', 1440), vh = 900;
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH, args: ['--hide-scrollbars', '--allow-file-access-from-files'] });
const results = [];

for (const t of targets) {
  const url = /^https?:|^file:/.test(t) ? t : pathToFileURL(path.resolve(t)).href;
  const page = await browser.newPage();
  await page.setViewport({ width: w, height: vh });
  await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await new Promise(r => setTimeout(r, 1000));
  const m = await page.evaluate(vh => {
    const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
    const all = [...document.querySelectorAll('body *')].filter(vis);
    const textEls = all.filter(el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1));
    const px = v => Math.round(parseFloat(v) || 0);
    const tally = arr => Object.entries(arr.reduce((a, k) => (a[k] = (a[k] || 0) + 1, a), {})).sort((a, b) => b[1] - a[1]);
    const sizes = tally(textEls.map(el => px(getComputedStyle(el).fontSize)));
    const weights = tally(textEls.map(el => getComputedStyle(el).fontWeight));
    const families = tally(textEls.map(el => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim()));
    const h1 = document.querySelector('h1');
    const h1s = h1 && getComputedStyle(h1);
    const paras = [...document.querySelectorAll('p')].filter(vis).filter(p => p.textContent.trim().length > 80);
    const lineChars = paras.map(p => { const s = getComputedStyle(p); return Math.round(p.getBoundingClientRect().width / (parseFloat(s.fontSize) * 0.5)); });
    const median = a => a.length ? a.sort((x, y) => x - y)[Math.floor(a.length / 2)] : null;
    const sections = [...document.querySelectorAll('main > section, body > section, main > div > section')].filter(vis);
    const pads = sections.map(s => px(getComputedStyle(s).paddingTop) + px(getComputedStyle(s).paddingBottom));
    const widest = Math.max(0, ...textEls.map(el => el.getBoundingClientRect().width).filter(x => x < innerWidth - 1));
    const colours = new Set();
    all.forEach(el => { const s = getComputedStyle(el); [s.color, s.backgroundColor, s.borderTopColor].forEach(c => { if (c && !/rgba\(.*, 0\)/.test(c) && c !== 'transparent') colours.add(c); }); });
    const radii = tally(all.map(el => px(getComputedStyle(el).borderTopLeftRadius)).filter(r => r > 0));
    const pills = all.filter(el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.height < 48 && r.height > 14 && parseFloat(s.borderTopLeftRadius) >= r.height / 2 - 1; }).length;
    const upperSmall = textEls.filter(el => { const s = getComputedStyle(el); return s.textTransform === 'uppercase' && parseFloat(s.fontSize) <= 14; });
    const mono = upperSmall.filter(el => /mono|courier|code/i.test(getComputedStyle(el).fontFamily)).length;
    const accentInH1 = !!(h1 && [...h1.querySelectorAll('*')].some(el => getComputedStyle(el).color !== h1s.color));
    const bg = getComputedStyle(document.body).backgroundColor;
    const [r, g, b] = (bg.match(/\d+/g) || [255, 255, 255]).map(Number);
    const cream = r > 230 && r - b > 6 && r - b < 40;
    return {
      viewports: +(document.documentElement.scrollHeight / vh).toFixed(1),
      contentWidth: Math.round(widest),
      typeSizes: sizes.slice(0, 10).map(([k, n]) => `${k}px×${n}`).join(' '),
      sizeCount: sizes.length,
      weights: weights.map(([k]) => k).join(' '),
      families: families.slice(0, 4).map(([k]) => k).join(' / '),
      h1: h1s ? `${px(h1s.fontSize)}px w${h1s.fontWeight} ls ${h1s.letterSpacing}` : 'none',
      bodyLineChars: median(lineChars),
      sectionSpacing: median(pads),
      radii: radii.slice(0, 5).map(([k, n]) => `${k}×${n}`).join(' '),
      colourCount: colours.size,
      background: bg,
      defaults: {
        pills,
        uppercaseSmallLabels: upperSmall.length,
        monoUppercaseLabels: mono,
        accentWordInH1: accentInH1,
        negativeH1Tracking: !!(h1s && parseFloat(h1s.letterSpacing) < 0),
        creamBackground: cream,
        breadcrumbs: document.querySelectorAll('nav[aria-label*="read" i], .breadcrumb, .breadcrumbs').length
      }
    };
  }, vh);
  results.push({ page: t, width: w, ...m });
  await page.close();
}
await browser.close();

if (opt('json')) fs.writeFileSync(opt('json'), JSON.stringify(results, null, 2));
const rows = ['viewports', 'contentWidth', 'h1', 'typeSizes', 'sizeCount', 'weights', 'families', 'bodyLineChars', 'sectionSpacing', 'radii', 'colourCount', 'background'];
console.log('| Measure | ' + results.map(r => path.basename(r.page)).join(' | ') + ' |');
console.log('|---|' + results.map(() => '---').join('|') + '|');
for (const k of rows) console.log(`| ${k} | ` + results.map(r => r[k] ?? '').join(' | ') + ' |');
for (const k of Object.keys(results[0].defaults)) console.log(`| default: ${k} | ` + results.map(r => r.defaults[k]).join(' | ') + ' |');

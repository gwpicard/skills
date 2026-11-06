// Capture a page for review: viewport-by-viewport strips, section crops, or one full page.
//
//   node capture.mjs <url-or-file> [--width 1440] [--height 900] [--mode strips|sections|full]
//                    [--out ./captures/<name>] [--scale 1] [--sections "main > section, footer"]
//
// Needs Puppeteer: run `npm i puppeteer` in a scratch folder, or set PUPPETEER_PATH to an
// installed copy. Set CHROME_PATH to use an installed Chrome instead of Puppeteer's download.
// Reduced motion is on, so animated pages settle; pass --motion to leave motion on.
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const valued = new Set(['--width', '--height', '--mode', '--out', '--scale', '--sections']);
const target = args.find((a, i) => !a.startsWith('--') && !valued.has(args[i - 1]));
if (!target) { console.log(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(0, 9).join('\n')); process.exit(2); }

const { default: puppeteer } = await import(process.env.PUPPETEER_PATH || 'puppeteer');
const w = +opt('width', 1440), h = +opt('height', 900), scale = +opt('scale', 1);
const mode = opt('mode', 'strips');
const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(path.resolve(target)).href;
const name = (new URL(url).hostname || path.basename(target, path.extname(target))).replace(/[^\w.-]+/g, '-');
const out = opt('out', `./captures/${name}-${w}`);
fs.mkdirSync(out, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH, args: ['--hide-scrollbars', '--allow-file-access-from-files'] });
const page = await browser.newPage();
page.on('pageerror', e => console.log('PAGEERROR', e.message));
if (!args.includes('--motion')) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
await page.setViewport({ width: w, height: h, deviceScaleFactor: scale });
await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
await sleep(1200);
const H = await page.evaluate(() => document.documentElement.scrollHeight);

if (mode === 'full') {
  await page.screenshot({ path: `${out}/full.png`, fullPage: true });
  console.log(`${out}/full.png`, H, 'px');
} else if (mode === 'sections') {
  const sel = opt('sections', 'main > section, body > section, body > footer, main > footer');
  const boxes = await page.evaluate(sel => [...document.querySelectorAll(sel)].map(el => {
    const r = el.getBoundingClientRect(); return { y: r.top + scrollY, h: r.height };
  }).filter(b => b.h > 40), sel);
  for (const [i, b] of boxes.entries()) {
    await page.screenshot({ path: `${out}/section-${String(i).padStart(2, '0')}.png`, clip: { x: 0, y: b.y, width: w, height: Math.ceil(b.h) }, captureBeyondViewport: true });
  }
  console.log(out, boxes.length, 'sections');
} else {
  let i = 0;
  for (let y = 0; y < H; y += h) {
    await page.evaluate(y => window.scrollTo(0, y), y);
    await sleep(500);
    await page.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}.png` });
    if (y + h >= H) break;
  }
  console.log(out, i, 'screens,', (H / h).toFixed(1), 'viewport heights');
}
await browser.close();

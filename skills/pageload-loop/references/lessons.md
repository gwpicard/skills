# Lessons

Starter list. Each lesson names its evidence. Most come from building and
testing this skill's scripts against a small static page with Lighthouse
13.6 (November 2026); the rest come from Lighthouse's own documentation.
Add lessons from real runs in the same format, and copy the ones that apply
into `.pageload/brief.md`.

## Measurement

- **Prove the A/A before the loop.** Lighthouse's variability notes list
  page nondeterminism, client contention and hardware as high-impact noise
  sources, and no throttling method removes page nondeterminism. Two
  identical builds must measure the same before any change is judged.
  (Lighthouse docs, variability.md)
- **Never run measurements in parallel, and keep the machine quiet.** The
  same notes say not to run concurrent Lighthouse instances on one machine.
  Do not build, install or run tests while measuring. (Lighthouse docs)
- **The noise floor can be almost zero; the 3% minimum then decides.** On a
  static local page the simulated LCP of 7 A/A runs varied by 0.2 ms on
  desktop and 2 ms on mobile. Without a minimum relative gain the script
  would keep 0.1% "wins". (test build)
- **Simulated TTFB is not server time.** `metrics.timeToFirstByte` was
  about 450 ms on mobile for a local server answering in 5 ms, because it
  includes the simulated round trips. Judge server-side changes on
  `server_ms` (`server-response-time`). (test build)
- **Simulated runs have unthrottled filmstrips.** In a simulated run the
  screenshots come from the real, fast load. Before/after filmstrips need
  the extra DevTools-throttled run (`--filmstrip devtools`). (test build)
- **Lighthouse 13 removed the old audit IDs.**
  `largest-contentful-paint-element`, `prioritize-lcp-image`,
  `render-blocking-resources` and `uses-long-cache-ttl` are no longer in the
  JSON; read the `*-insight` audits. Scripts written for Lighthouse 12
  silently find nothing. (Lighthouse 13 release notes; test build)
- **Lighthouse 13 needs Node 22.19+.** Node 22.14 printed an engine
  warning; `setup_tools.sh` stops early instead. (test build)

## Deciding

- **Correct for several pages and profiles.** With 2 pages × 2 profiles,
  "a win on any cell" gave a synthetic 2.5% effect a keep on one desktop
  cell. The Holm correction in `compare.py` stops one lucky cell from
  keeping a change. (test build, synthetic data)
- **Report the confirmation run, not the sum.** In the synthetic test the
  kept iterations added up to −740 ms on one cell and the confirmation run
  measured −809 ms; on another, −177 ms against −159 ms. The two numbers
  differ in both directions. (test build, synthetic data)
- **Do not chase cache-header savings in the loop.** Lighthouse estimated
  850 ms LCP savings from cache lifetimes on a local test page, but it loads
  with a cleared cache, so no cache change can win. Put it in the notes.
  (test build)

## Visual guard

- **A pixel ratio alone misses small real changes.** Adding two characters
  to a headline changed 0.046% of a mobile page and 0.011% of a desktop
  page, under the 0.1% threshold. The 16×16 tile check (18.75% of one tile)
  sent it to the critic. (test build)
- **Compare with the original screenshots, not the previous iteration.**
  Small accepted differences would otherwise add up.
- **Identical builds produced identical screenshots** once each shot used
  a fresh browser context, animations were off and fonts had loaded (0 of
  1.7 million pixels differed). If an A/A capture differs, find the dynamic
  region before offering masks. (test build)

## Setup

- **`npm init` rejects a folder named `.pageload`** ("Invalid name").
  `setup_tools.sh` writes the `package.json` itself. (test build)
- **Playwright may have no browser of its own.** A fresh `playwright`
  install had no matching Chromium; the scripts fall back to the installed
  Chrome (`channel: "chrome"`). (test build)
- **Keep the loop's files out of the commits.** `.pageload/` goes into
  `.git/info/exclude`, so `git add -A` and `git clean -fd` leave it alone and
  the perf commits contain only the change.

# Measurement protocol

How the loop measures, what the numbers mean, and how `compare.py` decides.
Checked against Lighthouse 13.6.

## Contents

1. Servers and targets
2. Lighthouse settings
3. Metrics and where they come from
4. Run plan and interleaving
5. A/A test and noise floor
6. Decision rules
7. Confirmation run
8. Visual guard
9. runs.jsonl format
10. Time cost
11. Lighthouse 13 audit IDs

## 1. Servers and targets

- **Local production build** (default). Two servers at once: the baseline
  from a git worktree on port 4001 and the candidate from the main tree on
  port 4002. Both use the project's real production start command, so
  compression, caching headers and server config are the real ones. Do not
  substitute a generic static server: a change to headers or compression
  would then not be measured.
- **Deployed preview URL.** Baseline is the original deploy; candidate is the
  branch preview, redeployed every iteration. Network noise is larger, so the
  A/A test matters more; run it against two URLs of the same deploy if the
  host allows it. Push only after the user agreed to this target.
- A server that caches the first request (ISR, on-demand rendering) needs the
  warm-up run (`--warmup 1`, the default) so both sides start warm.

## 2. Lighthouse settings

`measure.mjs` runs, per run, in a fresh process:

```
lighthouse <url> --only-categories=performance --throttling-method=simulate \
  --output=json --output-path=<file> --chrome-flags="--headless=new ..." --quiet \
  --max-wait-for-load=60000 [--preset=desktop]
```

- **Mobile** is Lighthouse's default: 412×823 screen at 1.75× device scale,
  Slow 4G simulated network (150 ms RTT, about 1.6 Mbps), 4× CPU slowdown. In Lighthouse source this is `throttling.mobileSlow4G`.
- **Desktop** is `--preset=desktop`: 1350×940, 40 ms RTT, 10 Mbps, no CPU
  slowdown.
- **Simulated throttling** (Lantern) loads the page unthrottled and computes
  the metrics from a model of the network and CPU. Lighthouse's own
  variability notes rank it as the strongest mitigation for network and
  resource-contention noise. It does not remove page nondeterminism (A/B
  tests, random content) or contention from other processes.
- Lighthouse clears the cache before each run (cold load). Changes that help
  only repeat visits cannot show up.
- Lighthouse 13 needs Node 22.19+.

## 3. Metrics and where they come from

| Field | JSON path | Notes |
|---|---|---|
| `lcp` | `audits["largest-contentful-paint"].numericValue` | Primary metric, ms |
| `cls` | `audits["cumulative-layout-shift"].numericValue` | Guardrail, limit 0.1 |
| `tbt` | `audits["total-blocking-time"].numericValue` | Guardrail; lab proxy for INP |
| `ttfb` | `audits.metrics.details.items[0].timeToFirstByte` | Guardrail; **simulated**, includes simulated round trips (about 450 ms on mobile for a local server) |
| `server_ms` | `audits["server-response-time"].numericValue` | Observed server time on the real load; use it to judge server-side changes |
| `fcp`, `si` | `first-contentful-paint`, `speed-index` | Recorded, not judged |
| LCP element | `audits["lcp-breakdown-insight"].details.items[type=node].selector` | Plus subparts (TTFB, load delay, load duration, render delay) in the table item |
| Filmstrip | `audits["screenshot-thumbnails"].details.items[].{timing,data}` | Base64 JPEG; see below |

**Filmstrips.** In a simulated run the screenshots come from the
unthrottled load, so they finish almost at once and do not match the
simulated LCP. With `--filmstrip devtools`, `measure.mjs` adds one run per
variant with DevTools throttling and keeps only its filmstrip. The report
says so. Use it at baseline and in the confirmation run only; it adds two
runs per page and profile.

## 4. Run plan and interleaving

For each page, for each profile: one warm-up run per variant (discarded),
then `runs` measured runs per variant in ABBA order (run 0: A then B; run
1: B then A; ...). Slow drift on the machine (thermal throttling, a
background job starting) then hits both sides equally.

A failed run is retried once. `compare.py` needs at least 5 valid runs per
side and cell; `measure.mjs` exits 1 when more than a quarter of the runs
failed.

Raw Lighthouse JSON is kept only for run 0 of each variant (`--keep-raw
first`), to keep the disk use bounded (about 0.4 MB mobile, 0.9 MB desktop
per file).

## 5. A/A test and noise floor

Before iteration 1, both servers run the same commit and are measured
against each other with the normal run plan (7 runs).

- **Noise floor** per page, profile and metric: 2 × MAD of the paired
  differences (run i of A minus run i of B). MAD is the median absolute
  deviation from the median.
- **Stability check**: the A/A pair must not differ. `compare.py aa` exits 3
  when the two-sided Mann-Whitney p is below 0.05 or the medians differ by
  more than 3%. Fix the cause before iteration 1.
- The noise floor can be close to zero. On a static local page the simulated
  LCP varied by 0.2 ms (desktop) and 2 ms (mobile). The 3% minimum gain is
  then what decides.

## 6. Decision rules

`compare.py decide` judges each page × profile cell, then the change.

For the primary metric (LCP), with `need = max(noise floor, 3% of baseline median)`:

| Cell verdict | Rule |
|---|---|
| win | median improves by more than `need` and one-sided Mann-Whitney p < 0.05 |
| regression | median worsens by more than `max(noise floor, 1% of baseline)` |
| near | not a win, but (size passes and p < 0.2) or (p passes and the gain is over half of `need`) |
| guardrail | CLS, TBT or TTFB worse by more than `max(noise floor, absolute minimum, relative minimum)`, or CLS above 0.1 and worse than baseline |

Guardrail minimums: CLS 0.01; TBT 30 ms or 10%; TTFB 30 ms or 10%. They
exist because a noise floor of nearly zero would otherwise block on a 1 ms
change.

The p-values of all cells are Holm-corrected before the win test (turn off
with `--no-holm`). Without the correction, a change with no real effect gets
4 chances (2 pages × 2 profiles) to look significant on one cell.

The change:

- **reject** if any cell is a regression, a guardrail failure or has too few
  runs;
- **keep** if at least one cell is a win;
- **inconclusive** if at least one cell is near: re-measure once at 14 runs
  and decide with `--retry`, where near becomes reject;
- otherwise **reject** (no gain above noise).

The Mann-Whitney test is exact when there are no ties and both samples have
at most 25 values, otherwise a normal approximation with tie correction.
With 7 against 7 the smallest possible one-sided p is 1/3432.

`compare.py final` combines the measured decision with the visual result: a
measured keep with `--visual fail` becomes a reject.

## 7. Confirmation run

At the end, the original commit (4001) against the final commit (4002), 15
runs per side, both profiles, with filmstrips. `compare.py confirm` reports
per cell: medians, delta, one-sided p, and a bootstrap 95% interval for the
difference of medians (2000 resamples, fixed seed). A cell is "confirmed"
when the gain exceeds `need` and p < 0.05.

The report states this number, not the sum of per-iteration gains.
Per-iteration gains overlap (two changes can fix the same bottleneck) and
each carries its own noise, so their sum is not the total.

## 8. Visual guard

- `visual_diff.mjs capture`: one fresh browser context per shot; 390×844
  (mobile) and 1440×900 (desktop), device scale 1; reduced motion; CSS
  animations, transitions and caret off; waits for load, network idle (best
  effort), `document.fonts.ready` and images; scrolls once to trigger lazy
  loading; full-page shot.
- `compare`: pixelmatch with per-pixel threshold 0.1. A shot passes when at
  most 0.1% of pixels differ **and** no 16×16 tile has 10% or more differing
  pixels. The tile check exists because a changed headline word measured
  0.046% of a mobile page: under the ratio, but a real change.
- Candidates are always compared with the **original** screenshots, so small
  changes cannot add up over iterations.
- Shots that fail go to a blind critic (`assets/critic-visual.md`) with
  random A/B labels; the key is stored outside the project. The critic
  answers same or different.
- Masking (`--mask`) hides selectors behind a solid box. It is off by
  default and only offered when the A/A capture differs.
- Accessibility check (on by default, off with `setup_tools.sh --no-a11y`):
  `visual_diff.mjs axe` runs axe-core's default rules at both viewports after
  the same settle steps, once on the original and once on the final build.
  `compare.py a11y` reports violations whose rule id and target selector are
  absent from the original scan. A DOM change can shift a selector and make
  an old violation look new, so check the HTML snippet in `a11y.json`. It
  never reverts a change; the lead reports new serious or critical ones.

## 9. runs.jsonl format

One JSON line per page × profile × variant per measurement, written only by
`compare.py log`:

```
ts, iter, kind (baseline | iteration | confirm), hypothesis, commit,
variant, role (base | cand | A/A variant name), page, profile,
runs {lcp: [..], cls: [..], tbt: [..], ttfb: [..], fcp, si, server_ms},
medians {...}, noise_floor {...}, p_value (Holm-corrected), delta, delta_pct,
ci95 (confirm only), cell_verdict, visual, visual_ratio,
decision (final), measured_decision, reason, changes [..],
lcp_element, filmstrip_file, lighthouse, n_runs
```

An iteration rejected without a measurement (build failed, off-limits file)
has one line with `page: "*"` and `--reject-reason` as the reason. A retried
iteration has two sets of lines with the same `iter`; the report uses the
later one.

## 10. Time cost

One Lighthouse run took about 10 to 12 s on a laptop for a small page
(longer for heavy pages). Per iteration:
`pages × 2 profiles × (2 × runs + 2 warm-up)` runs, plus build, server
restart and screenshots.

| Pages | Runs per iteration | About |
|---|---|---|
| 1 | 32 | 6–8 min |
| 2 | 64 | 12–15 min |
| 3 | 96 | 18–22 min |

A retry at 14 runs roughly doubles that iteration. The confirmation run with
15 runs and filmstrips costs about twice an iteration.

## 11. Lighthouse 13 audit IDs

Lighthouse 13 removed the older audits from the JSON. Use these IDs (seen in
real 13.6 output):

| Use | Lighthouse 13 ID | Replaced |
|---|---|---|
| LCP element and subparts | `lcp-breakdown-insight` | `largest-contentful-paint-element` |
| LCP discovery, fetchpriority, lazy-loaded LCP | `lcp-discovery-insight` | `prioritize-lcp-image`, `lcp-lazy-loaded` |
| Render-blocking requests | `render-blocking-insight` | `render-blocking-resources` |
| Images: format, size, compression | `image-delivery-insight` | `uses-webp-images`, `uses-optimized-images`, `uses-responsive-images`, `efficient-animated-content` |
| Cache lifetimes | `cache-insight` | `uses-long-cache-ttl` |
| Server time, redirects, compression | `document-latency-insight` | `server-response-time` (still present), `redirects` (still present, hidden group), `uses-text-compression` |
| Request chains, preconnect | `network-dependency-tree-insight` | `critical-request-chains`, `uses-rel-preconnect` |
| Fonts | `font-display-insight` | `font-display` |
| Third parties | `third-parties-insight` | `third-party-summary` |
| Layout shifts | `cls-culprits-insight` | `layout-shifts` (still present) |
| JavaScript | `legacy-javascript-insight`, `duplicated-javascript-insight`, `unused-javascript` | same names without `-insight` |
| HTTP/2+ | `modern-http-insight` | `uses-http2` |
| Other | `dom-size-insight`, `forced-reflow-insight`, `viewport-insight`, `inp-breakdown-insight` | |

Removed without replacement: `third-party-facades`, `uses-rel-preload`,
`preload-fonts`, `offscreen-images`, `no-document-write`,
`uses-passive-event-listeners`. Still present: `unused-css-rules`,
`unused-javascript`, `unminified-css`, `unminified-javascript`,
`total-byte-weight`, `bootup-time`, `mainthread-work-breakdown`,
`long-tasks`, `non-composited-animations`, `unsized-images`, `bf-cache`,
`screenshot-thumbnails`, `final-screenshot`. `redirects` is still computed but
sits in a hidden group, so it does not appear in the HTML report.

Savings estimates are in each audit's `metricSavings` (`LCP`, `FCP`, `CLS`,
`INP` keys). `compare.py insights` ranks them.

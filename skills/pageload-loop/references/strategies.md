# Hypothesis catalogue

Where each hypothesis comes from (the Lighthouse 13 insight), what to change,
how risky it is, and what goes wrong. Use it to build and re-rank
`.pageload/backlog.md`.

## Contents

1. Ranking
2. LCP resource: discovery and priority
3. Images
4. Fonts
5. Render-blocking CSS and JavaScript
6. JavaScript size and main-thread work
7. Third-party scripts
8. Server, compression and protocol
9. Connections
10. Layout shifts (guardrail fixes)
11. What this loop cannot measure
12. Framework notes

## 1. Ranking

Score = estimated LCP ms saved ÷ risk.

- **Estimated saving**: the insight's `metricSavings.LCP`, maximum across
  pages and profiles (`compare.py insights`). When an insight has no LCP
  estimate, use the LCP subpart it targets from `lcp-breakdown-insight`
  (for example the resource load delay for a discovery fix).
- **Risk**: 1 = local markup or attribute change, easy to revert; 2 = build
  config, new dependency, change across many files, or a visible-behaviour
  risk; 3 = server or caching config, architecture, or anything touching
  third parties the user listed.
- Drop hypotheses whose estimate is under the noise floor, and those the
  constraints forbid ("no visual changes", "third parties must load as they
  do", off-limits files).
- Lighthouse savings are estimates from the simulation. Treat them as a
  ranking signal, not as the expected result.

Write each backlog entry as: hypothesis, evidence (insight ID, URL or
selector, estimate), risk, files likely touched.

## 2. LCP resource: discovery and priority

Insight: `lcp-discovery-insight` (checklist: `priorityHinted`,
`requestDiscoverable`, `eagerlyLoaded`), `lcp-breakdown-insight` (large
resource load delay).

| Change | Risk | Notes |
|---|---|---|
| `fetchpriority="high"` on the LCP image | 1 | Often the largest single gain on mobile. Only on the one LCP image per page; on several it cancels out |
| Remove `loading="lazy"` from the LCP image | 1 | Common in carousels and CMS templates |
| Make the LCP image discoverable in the HTML: `<img>` instead of CSS `background-image`, or `<link rel="preload" as="image" imagesrcset=... fetchpriority="high">` | 1–2 | Preload with `imagesrcset`/`imagesizes` must match the `<img>`, or the browser downloads twice |
| Render the LCP element on the server instead of after hydration | 2–3 | Client-rendered hero text or images wait for JavaScript |

The LCP element can differ between mobile and desktop and between pages.
Read the selector per cell from `lcp_element`.

## 3. Images

Insight: `image-delivery-insight` (format, oversizing, compression,
animated GIF).

| Change | Risk | Notes |
|---|---|---|
| Serve AVIF or WebP with fallback | 1–2 | Can add a build dependency (for example an image plugin); announce it. Check that colours and transparency look the same |
| Responsive `srcset`/`sizes` so mobile gets a smaller file | 1 | Wrong `sizes` makes the browser pick too large or blurry images; the visual guard catches blur |
| Recompress at a lower quality | 1–2 | Visual risk: compression artefacts can pass the pixel threshold; look at the diff |
| Replace animated GIF with video | 2 | Visual and behaviour change; needs the user's agreement under "no visual changes" |
| Explicit `width`/`height` | 1 | A CLS fix, not an LCP fix |

## 4. Fonts

Insight: `font-display-insight`, `network-dependency-tree-insight`
(font chains), text LCP elements.

| Change | Risk | Notes |
|---|---|---|
| Self-host fonts instead of a font CDN | 2 | Removes a connection; check the licence |
| Preload the one font used by the LCP text | 1 | Preloading several fonts competes with the LCP image |
| `font-display: swap` or `optional` | 1–2 | `swap` can cause a layout shift and a visible font change during load; the screenshot is taken after fonts load, so check CLS |
| Subset fonts, WOFF2 only | 2 | Missing glyphs for other languages are a visual change |
| Metric-matched fallback (`size-adjust`, framework font helpers) | 2 | Reduces the shift when the font swaps |

## 5. Render-blocking CSS and JavaScript

Insight: `render-blocking-insight` (savings mostly in FCP; LCP gains when
the LCP element is text or the image is discovered early).

| Change | Risk | Notes |
|---|---|---|
| `defer` or `async` on head scripts | 1–2 | Order-dependent scripts break with `async`; prefer `defer` |
| Inline critical CSS, load the rest without blocking | 2 | Can flash unstyled content and add TBT or HTML size; often a visual-diff failure. Inlining all CSS can increase LCP on mobile |
| Remove unused CSS (`unused-css-rules`) | 2 | Dynamic class names (JS-added, CMS) get removed by mistake; test every chosen page |
| Split CSS by route | 2 | Framework config change; announce |

## 6. JavaScript size and main-thread work

Insights: `unused-javascript`, `legacy-javascript-insight`,
`duplicated-javascript-insight`, `bootup-time`, `mainthread-work-breakdown`,
`forced-reflow-insight`, `dom-size-insight`.

| Change | Risk | Notes |
|---|---|---|
| Lazy-load components below the fold or behind interaction (dynamic import) | 2 | Helps TBT more than LCP unless the hero waits for hydration |
| Remove duplicated or legacy polyfills (modern browserslist target) | 2 | Build config change; announce. Check the user's supported browsers first |
| Replace a heavy library (date, icons, lodash) with a lighter one or a deep import | 2 | Dependency change; announce |
| Reduce hydration (islands, server components) | 3 | Architecture; usually too large for one iteration |

On simulated mobile (4× CPU), main-thread work moves LCP when the LCP
element is rendered by JavaScript.

## 7. Third-party scripts

Insight: `third-parties-insight` (transfer size and main-thread time per
entity). Lighthouse 13 removed `third-party-facades`; find embeds (video,
maps, chat) by hand.

| Change | Risk | Notes |
|---|---|---|
| Defer analytics or tag manager until after load or idle | 2–3 | Can lose early events; only with the user's agreement when "third parties must load as they do" is set |
| Facade for video, map or chat embed (static preview, load on click) | 2 | Visual change unless the facade matches the first frame |
| Remove a script nobody uses | 3 | Ask the user; never assume |

A/B testing and personalisation scripts often block rendering on purpose
(to avoid flicker). Moving them changes product behaviour; ask.

## 8. Server, compression and protocol

Insights: `document-latency-insight` (server time, redirects, compression),
`modern-http-insight`.

| Change | Risk | Notes |
|---|---|---|
| Enable gzip or Brotli for text responses | 2 | Server config; announce. Shows in transfer size and LCP on mobile |
| Remove redirect hops (trailing slash, locale redirect) | 2 | Check that old URLs still work |
| Static generation or caching of server-rendered HTML | 3 | Look at `server_ms`, not the simulated `ttfb`, to judge it |
| HTTP/2 or HTTP/3 | 3 | Depends on the host; a local start command often serves HTTP/1.1 while production does not, so the local build cannot measure it |

## 9. Connections

Insight: `network-dependency-tree-insight` (lists preconnect candidates and
unused preconnects).

| Change | Risk | Notes |
|---|---|---|
| `preconnect` to the origin that serves the LCP image or font | 1 | At most 2–3 origins; more competes for bandwidth |
| Remove unused `preconnect` | 1 | Lighthouse lists them |
| Move assets to the main origin | 2 | Removes a connection entirely |

## 10. Layout shifts (guardrail fixes)

Insight: `cls-culprits-insight`, `unsized-images`. These do not count as
wins, but a page with CLS above 0.1 cannot pass the guardrail after a change
that makes it worse, and the user may want CLS fixed. Ask before spending
iterations on them.

## 11. What this loop cannot measure

- **Cache headers** (`cache-insight`, long `max-age`, immutable assets).
  Lighthouse loads with a cleared cache, so repeat-visit gains do not appear.
  In a test page Lighthouse estimated 850 ms LCP savings from cache
  lifetimes. Do not try it as a loop iteration; list it in the notes as a
  recommendation, or make it a separate change outside the loop if the user
  wants it.
- **Field INP.** TBT is the lab proxy. Interaction latency needs real users
  or a scripted interaction.
- **CDN and edge behaviour** on a local build.
- **HTTP/2 or HTTP/3** when the local server does not speak them.

## 12. Framework notes

- **Next.js**: `next/image` with its priority option on the LCP image (the
  prop name has changed across major versions; check the installed docs); `next/font` for self-hosted fonts with
  metric fallbacks; `next build && next start` for the production server.
  `next.config.*` changes are config changes; announce them.
- **Astro**: `<Image>` with `loading="eager"` and `fetchpriority="high"` for
  the hero; `astro build && astro preview` serves the static output, not the
  production host's headers.
- **Vite SPA**: `vite build && vite preview` is a preview server, not the
  production host; check whether it compresses and sets headers like
  production does. A client-rendered LCP usually needs pre-rendering for
  large gains.
- **SvelteKit, Remix, Nuxt**: use the node adapter's start command with
  `PORT`.
- **Static sites**: serve with the server the site uses in production
  (nginx, Caddy, a host's CLI), so headers and compression match.

Check the framework version in the project before applying a framework API:
names change between major versions.

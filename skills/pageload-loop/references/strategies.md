# Hypothesis catalogue

Where each hypothesis comes from (the Lighthouse 13 insight), what to change,
how risky it is, and what goes wrong. Use it to build and re-rank
`.pageload/backlog.md`. Checked against Lighthouse 13.6, web.dev and the
framework docs in November 2026.

## Contents

1. Ranking
2. Insight names
3. LCP resource: discovery and priority
4. Images
5. Fonts
6. Render-blocking CSS and JavaScript
7. JavaScript size, hydration and main-thread work
8. Third-party scripts
9. Server rendering, compression and protocol
10. Connections and resource hints
11. Layout shifts (guardrail fixes)
12. Report-only recommendations (the loop cannot measure them)
13. Framework notes

## 1. Ranking

Score = estimated LCP ms saved ÷ risk.

- **Estimated saving**: the insight's `metricSavings.LCP`, maximum across
  pages and profiles (`compare.py insights`). When an insight has no LCP
  estimate, use the LCP subpart it targets from `lcp-breakdown-insight`
  (for example the resource load delay for a discovery fix).
- **Pick the category from the LCP subparts.** web.dev's rule of thumb for
  an image LCP: TTFB about 40%, resource load delay under 10%, resource load
  duration about 40%, element render delay under 10%. A subpart well above
  its share names the section to work on: TTFB → section 9, load delay →
  sections 3 and 10, load duration → sections 4 and 9, render delay →
  sections 6 and 7. A text LCP has no load delay or load duration; its time
  is TTFB plus render delay.
- **A fix can move time instead of removing it.** Faster image download
  with render-blocking CSS still pending only grows the render delay. Read
  the subparts of the candidate, not just the LCP total, before re-ranking.
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

## 2. Insight names

The JSON uses the IDs; the Lighthouse report and the DevTools Performance
panel show the names. Each name links to its Chrome for Developers page.

| Lighthouse 13 ID | Name in the report and DevTools |
|---|---|
| `lcp-breakdown-insight` | [LCP breakdown](https://developer.chrome.com/docs/performance/insights/lcp-breakdown) |
| `lcp-discovery-insight` | [LCP request discovery](https://developer.chrome.com/docs/performance/insights/lcp-discovery) |
| `render-blocking-insight` | [Render-blocking requests](https://developer.chrome.com/docs/performance/insights/render-blocking) |
| `network-dependency-tree-insight` | [Network dependency tree](https://developer.chrome.com/docs/performance/insights/network-dependency-tree) |
| `image-delivery-insight` | [Improve image delivery](https://developer.chrome.com/docs/performance/insights/image-delivery) |
| `font-display-insight` | [Font display](https://developer.chrome.com/docs/performance/insights/font-display) |
| `document-latency-insight` | [Document request latency](https://developer.chrome.com/docs/performance/insights/document-latency) |
| `modern-http-insight` | [Modern HTTP](https://developer.chrome.com/docs/performance/insights/modern-http) |
| `cache-insight` | [Use efficient cache lifetimes](https://developer.chrome.com/docs/performance/insights/cache) |
| `third-parties-insight` | [Third parties](https://developer.chrome.com/docs/performance/insights/third-parties) |
| `legacy-javascript-insight` | [Legacy JavaScript](https://developer.chrome.com/docs/performance/insights/legacy-javascript) |
| `duplicated-javascript-insight` | [Duplicated JavaScript](https://developer.chrome.com/docs/performance/insights/duplicated-javascript) |
| `forced-reflow-insight` | [Forced reflow](https://developer.chrome.com/docs/performance/insights/forced-reflow) |
| `dom-size-insight` | [Optimize DOM size](https://developer.chrome.com/docs/performance/insights/dom-size) |
| `cls-culprits-insight` | [Layout shift culprits](https://developer.chrome.com/docs/performance/insights/cls-culprit) |
| `viewport-insight` | [Optimize viewport for mobile](https://developer.chrome.com/docs/performance/insights/viewport) |
| `inp-breakdown-insight` | [INP breakdown](https://developer.chrome.com/docs/performance/insights/inp-breakdown) (empty in a navigation run: no interaction happens) |

Lighthouse 13.6 also ships `slow-css-selector-insight`
([CSS selector costs](https://developer.chrome.com/docs/performance/insights/slow-css-selector)),
but the default config does not run it, so it is not in the JSON. Look for
it in a DevTools trace when the render delay is large and the CSS is heavy.

Diagnostics that are not insights but still feed hypotheses:
`unused-javascript`, `unused-css-rules`, `bootup-time`,
`mainthread-work-breakdown`, `long-tasks`, `non-composited-animations`,
`unsized-images`, `bf-cache`, `total-byte-weight`.

## 3. LCP resource: discovery and priority

Insight: `lcp-discovery-insight` (checklist: `priorityHinted`,
`requestDiscoverable`, `eagerlyLoaded`), `lcp-breakdown-insight` (large
resource load delay).

| Change | Risk | Notes |
|---|---|---|
| `fetchpriority="high"` on the LCP image | 1 | Often the largest single gain on mobile. Only on the one LCP image per page; on several it cancels out |
| Remove `loading="lazy"` from the LCP image | 1 | Common in carousels and CMS templates. web.dev measured a 13–15% LCP delay on WordPress pages that lazy-loaded their first image |
| Make the LCP image discoverable in the HTML: `<img>` instead of CSS `background-image`, or `<link rel="preload" as="image" imagesrcset=... fetchpriority="high">` | 1–2 | Preload with `imagesrcset`/`imagesizes` must match the `<img>`, or the browser downloads twice |
| Remove preloads and high priorities that compete with the LCP image | 1 | Preloaded fonts, scripts or below-the-fold images share the bandwidth. Lighthouse 13 removed `uses-rel-preload`; check each `<link rel="preload">` against the network dependency tree |
| `fetchpriority="low"` on hidden carousel slides and other early, non-critical images | 1 | Only for images the user cannot see at load. Keep the first slide eager and high |
| Video hero: a `poster` image that is discoverable and prioritised | 1–2 | The poster (or the first frame of an autoplaying video) can be the LCP element. Preload the poster, not the video |
| Remove an entrance animation that hides the hero (`opacity: 0`, fade-in, slide-in) | 2 | An element is not an LCP candidate while it is invisible, so the animation adds its duration to the render delay. This is a visible-behaviour change; ask under "no visual changes" |
| Render the LCP element on the server instead of after hydration | 2–3 | Client-rendered hero text or images wait for JavaScript |

The LCP element can differ between mobile and desktop and between pages.
Read the selector per cell from `lcp_element`. On mobile it is often a
cookie-consent banner or its text; then the banner's script and styles are
the LCP path, and changing the banner is a third-party change (section 8).

A blurred low-quality placeholder does not end LCP: Chrome ignores images
with very few bits per pixel as LCP candidates, so the real image still
decides.

## 4. Images

Insight: `image-delivery-insight` (format, oversizing, compression,
animated GIF).

| Change | Risk | Notes |
|---|---|---|
| Serve AVIF or WebP with fallback | 1–2 | Can add a build dependency (for example an image plugin); announce it. Check that colours and transparency look the same. AVIF files are usually smaller but slower to encode at build time |
| Responsive `srcset`/`sizes` so mobile gets a smaller file | 1 | Wrong `sizes` makes the browser pick too large or blurry images; the visual guard catches blur |
| Recompress at a lower quality | 1–2 | Visual risk: compression artefacts can pass the pixel threshold; look at the diff |
| `loading="lazy"` on images and iframes below the fold | 1 | Fewer early requests compete with the LCP image. Never on the LCP image or anything in the first viewport of either profile. Lighthouse 13 removed `offscreen-images`, so find candidates by hand |
| Replace large inline `data:` images (base64 in HTML or CSS) with files | 1–2 | Base64 inflates the render-blocking HTML or CSS by about a third and cannot be cached separately. Very small icons can stay inline |
| Replace animated GIF with video | 2 | Visual and behaviour change; needs the user's agreement under "no visual changes" |
| Explicit `width`/`height` | 1 | A CLS fix, not an LCP fix |

## 5. Fonts

Insight: `font-display-insight`, `network-dependency-tree-insight`
(font chains), text LCP elements.

| Change | Risk | Notes |
|---|---|---|
| Self-host fonts instead of a font CDN | 2 | Removes a connection and a CSS request in the chain; check the licence |
| Preload the one font used by the LCP text | 1 | Preloading several fonts competes with the LCP image |
| Replace `font-display: block` or `auto` with `swap` or `optional` | 1–2 | `block` hides text for up to 3 s, which delays a text LCP. `swap` can cause a layout shift and a visible font change during load; `optional` avoids the shift but may show the fallback on a cold load. The screenshot is taken after fonts load, so check CLS |
| Subset fonts (`unicode-range`), WOFF2 only | 2 | Missing glyphs for other languages are a visual change |
| Metric-matched fallback (`size-adjust`, `ascent-override`, framework font helpers) | 2 | Reduces the shift when the font swaps |

## 6. Render-blocking CSS and JavaScript

Insight: `render-blocking-insight` (savings mostly in FCP; LCP gains when
the LCP element is text or the image is discovered early),
`network-dependency-tree-insight` (CSS and script chains).

| Change | Risk | Notes |
|---|---|---|
| `defer` or `async` on head scripts | 1–2 | Order-dependent scripts break with `async`; prefer `defer`. `type="module"` scripts are deferred already |
| Inline small CSS, keep large CSS external | 2 | Inline only the CSS the first viewport needs, or a whole stylesheet of a few kB (framework thresholds in section 13). Inlining large CSS grows every HTML response, loses caching and can increase LCP on mobile |
| Extract critical CSS and load the rest without blocking | 2–3 | Can flash unstyled content and add HTML size; often a visual-diff failure. Prefer the framework's own option over a separate tool |
| Flatten CSS `@import` chains | 1–2 | Each `@import` is a further sequential request before render |
| Remove unused CSS (`unused-css-rules`) | 2 | Dynamic class names (JS-added, CMS) get removed by mistake; test every chosen page |
| Split CSS by route | 2 | Framework config change; announce |

## 7. JavaScript size, hydration and main-thread work

Insights: `legacy-javascript-insight`, `duplicated-javascript-insight`,
`forced-reflow-insight`, `dom-size-insight`, `viewport-insight`;
diagnostics `unused-javascript`, `bootup-time`,
`mainthread-work-breakdown`, `long-tasks`.

| Change | Risk | Notes |
|---|---|---|
| Lazy-load components below the fold or behind interaction (dynamic import) | 2 | Helps TBT more than LCP unless the hero waits for hydration |
| Remove duplicated or legacy polyfills (modern browserslist or build target) | 2 | Build config change; announce. Check the user's supported browsers first |
| Replace a heavy library (date, icons, lodash) with a lighter one or a deep import | 2 | Dependency change; announce |
| `modulepreload` for a deep chain of module imports | 1–2 | Only when the network dependency tree shows sequential script requests on the LCP path. Vite, SvelteKit and most frameworks add these already |
| Delay hydration of individual components (Astro `client:visible`/`client:idle`, Nuxt `hydrate-on-visible` and related props, React `lazy` with `Suspense`) | 2 | Per-component and easy to revert. A component that must react at once to input becomes slow on the first interaction |
| Move components to the server (React Server Components, Astro islands) or drop hydration for static parts | 3 | Architecture; usually too large for one iteration. Split it into one component per iteration |
| Break up long startup tasks (`scheduler.yield()` with a `setTimeout` fallback) | 2 | Targets TBT, the lab proxy for INP. `scheduler.yield()` runs in Chromium and Firefox but not Safari, so feature-detect it |
| Remove forced reflows (layout reads after style writes in a loop) | 2 | `forced-reflow-insight` names the function and its source location |
| Reduce DOM size, or `content-visibility: auto` with `contain-intrinsic-size` on long off-screen sections | 2 | Cuts style and layout work. Without `contain-intrinsic-size` the scroll height jumps; check CLS and the full-page screenshot |
| Add `<meta name="viewport" content="width=device-width, initial-scale=1">` | 1 | Only when `viewport-insight` fails; changes the mobile layout, so expect a visual diff |

On simulated mobile (4× CPU), main-thread work moves LCP when the LCP
element is rendered by JavaScript.

## 8. Third-party scripts

Insight: `third-parties-insight` (transfer size and main-thread time per
entity). Lighthouse 13 removed `third-party-facades`; find embeds (video,
maps, chat) by hand.

| Change | Risk | Notes |
|---|---|---|
| Load with `async` or `defer` instead of a blocking `<script>` | 2 | Only for scripts that do not write to the document while it parses |
| Defer analytics or tag manager until after load or idle (framework script helpers in section 13) | 2–3 | Can lose early events; only with the user's agreement when "third parties must load as they do" is set |
| Facade for video, map or chat embed (static preview, load on click) | 2 | Visual change unless the facade matches the first frame |
| Self-host a small, stable third-party script | 3 | Removes a connection, but the copy no longer receives the vendor's updates; ask |
| Move a script to a web worker (Partytown and similar) | 3 | Many scripts break when they cannot touch the DOM synchronously; test every tag |
| Remove a script nobody uses | 3 | Ask the user; never assume |

A/B testing and personalisation scripts often block rendering on purpose
(to avoid flicker), sometimes with an anti-flicker snippet that hides the
whole page. Moving them changes product behaviour; ask. Consent managers
decide when other tags load: change their loading only with the user.

## 9. Server rendering, compression and protocol

Insights: `document-latency-insight` (server time, redirects, compression),
`modern-http-insight`. Judge server-side changes on `server_ms`, not the
simulated `ttfb`.

| Change | Risk | Notes |
|---|---|---|
| Enable gzip or Brotli for text responses | 2 | Server config; announce. Shows in transfer size and LCP on mobile |
| Pre-compress static assets at build time (Brotli, plus zstd if the server serves it) | 2 | Higher compression than on-the-fly at no request cost. Keep gzip or Brotli as the fallback; only some browsers accept zstd |
| Remove redirect hops (trailing slash, locale redirect) | 2 | Check that old URLs still work |
| Static generation or prerendering of pages that do not change per request | 3 | Removes server render time from TTFB. Framework options in section 13 |
| Stream server-rendered HTML (a static shell first, slow data inside `Suspense` or the framework's equivalent) | 3 | Lowers TTFB and FCP. LCP improves only when the LCP element is in the shell, not in a streamed part |
| Cache server-rendered HTML in the app (ISR, `use cache`, a render cache) | 3 | Needs a warm-up run (the default) so both sides start warm. A response that differs per user must not be cached |
| HTTP/2 or HTTP/3 | 3 | Depends on the host; a local start command often serves HTTP/1.1 while production does not, so the local build cannot measure it (section 12) |

## 10. Connections and resource hints

Insight: `network-dependency-tree-insight` (lists preconnect candidates and
unused preconnects).

| Change | Risk | Notes |
|---|---|---|
| `preconnect` to the origin that serves the LCP image or font | 1 | At most 2–3 origins; more competes for bandwidth. Add `crossorigin` for fonts |
| Remove unused `preconnect` | 1 | Lighthouse lists them |
| Move assets to the main origin | 2 | Removes a connection entirely |
| `dns-prefetch` for later third-party origins | 1 | Cheap, but rarely measurable on LCP |

Hints that help only the next navigation (`prefetch`, Speculation Rules)
and Early Hints are in section 12.

## 11. Layout shifts (guardrail fixes)

Insight: `cls-culprits-insight`; diagnostics `unsized-images`,
`non-composited-animations`. These do not count as wins, but a page with
CLS above 0.1 cannot pass the guardrail after a change that makes it worse,
and the user may want CLS fixed. Ask before spending iterations on them.

| Change | Risk | Notes |
|---|---|---|
| `width`/`height` or CSS `aspect-ratio` on images, video and iframes | 1 | The most common culprit |
| Reserve space for ads, embeds, banners and late content (`min-height`) | 1–2 | Size the box for the most common case; a box too large leaves a gap |
| Insert late content below the viewport or in reserved space, never above existing content | 2 | Cookie banners and promo bars: overlay or reserve space |
| Metric-matched fallback fonts | 2 | See section 5 |
| Animate `transform` and `opacity` instead of `top`, `left`, `width`, `height` or margins | 2 | `non-composited-animations` lists them |

Lab CLS covers only the load. Shifts after scrolling or interaction appear
in field data only.

## 12. Report-only recommendations (the loop cannot measure them)

Lighthouse loads one URL once, with a cleared cache, from a local
production build. Changes whose benefit appears only on a repeat visit, on
the next navigation, on a CDN or in real users' interactions cannot win in
this loop. Do not try them as iterations. List the ones that apply in
`.pageload/notes.md` as recommendations with the evidence, or make them a
separate change outside the loop if the user wants it.

- **Cache headers** (`cache-insight`, long `max-age`, `immutable` on
  hashed assets). In a test page Lighthouse estimated 850 ms LCP savings
  from cache lifetimes; none of it can show on a cold load.
- **CDN and edge caching of HTML.** web.dev names a CDN with cached HTML as
  a top TTFB fix. The local server has no network distance and no edge.
  Unique query parameters on links prevent edge cache hits.
- **Image CDN.** Resizing and format negotiation at the edge. It can be
  measured only when the loop already uses the deployed preview target.
- **103 Early Hints.** Sends `preconnect` and `preload` while the server
  still generates the HTML, so it helps only with real server think time.
  It needs HTTP/2 or later and the host's support; the local start command
  rarely sends it. Chromium and Firefox accept preload hints; Safari does not.
- **Speculation Rules (prefetch, prerender).** Makes the next navigation
  near-instant (`<script type="speculationrules">`, `moderate` eagerness
  for most sites). Chromium-based browsers only; others have it behind
  flags or in previews.
  Prerendered pages run their scripts early, so analytics must handle
  activation. Lighthouse measures a single navigation, so it never sees the
  gain.
- **Back/forward cache.** Remove `unload` listeners (use `pagehide`), avoid
  `Cache-Control: no-store` where it is not needed, close open connections
  in `pagehide`. The `bf-cache` diagnostic in the existing Lighthouse JSON
  lists the failure reasons; quote them as evidence.
- **Service worker caching.** Helps repeat visits only. On a first visit a
  service worker that registers and precaches early competes with the page;
  register it after `load`.
- **zstd or Brotli at the edge** when compression is set on the host or
  CDN, not by the project's start command.
- **HTTP/2 or HTTP/3** when the local server does not speak them.
- **Field INP.** TBT is the lab proxy. Interaction latency needs real users
  (CrUX, a RUM library) or a scripted interaction in DevTools, where
  `inp-breakdown-insight` splits it into input delay, processing and
  presentation delay.

## 13. Framework notes

- **Next.js**: `next/image` with `fetchPriority="high"` (or
  `loading="eager"`) on the LCP image. Next.js 16 deprecated the `priority`
  prop in favour of `preload`, and its docs recommend `fetchPriority` or
  `loading` instead of `preload` in most cases; never combine them.
  `next/font` for self-hosted fonts with metric fallbacks; `next/script`
  `strategy` (`afterInteractive`, `lazyOnload`) for third parties. Next.js
  16 `cacheComponents` (Partial Prerendering) serves a static shell and
  streams the dynamic parts. `next build && next start` for the production
  server. `next.config.*` changes are config changes; announce them.
- **Astro**: `<Image>` with `loading="eager"` and `fetchpriority="high"` for
  the hero; islands load JavaScript only for `client:*` components, so
  prefer `client:visible` or `client:idle` over `client:load`;
  `build.inlineStylesheets` controls CSS inlining. `astro build && astro
  preview` serves the static output, not the production host's headers.
  Prefetch and the experimental `clientPrerender` (Speculation Rules) help
  the next navigation only (section 12).
- **Nuxt**: `@nuxt/image`, `@nuxt/fonts` and `@nuxt/scripts` modules;
  delayed hydration on `Lazy` components (`hydrate-on-visible`,
  `hydrate-on-idle`, `hydrate-on-interaction`, `hydrate-never`) since Nuxt
  3.16. Start with the node server output and `PORT`.
- **SvelteKit**: `kit.inlineStyleThreshold` (default 0) inlines CSS files
  below the given size; `output.bundleStrategy` controls splitting. Use the
  node adapter's start command with `PORT`.
- **React Router v7 / Remix**: `prerender` in `react-router.config.ts`
  generates static HTML at build time; with `ssr: false` the app is a SPA
  and its LCP waits for JavaScript unless the route is prerendered.
- **Vite SPA**: `vite build && vite preview` is a preview server, not the
  production host; check whether it compresses and sets headers like
  production does. Vite 7 and later target `baseline-widely-available` by
  default (Vite 6 and earlier: `modules`), adds `modulepreload` for entry chunks
  and inlines assets under 4 KiB. A client-rendered LCP usually needs
  pre-rendering for large gains.
- **Static sites**: serve with the server the site uses in production
  (nginx, Caddy, a host's CLI), so headers and compression match.

Check the framework version in the project before applying a framework API:
names change between major versions.

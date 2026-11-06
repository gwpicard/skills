---
name: website-review
description: >
  Reviews websites for marketing, SEO, GEO, messaging, conversion, and UX
  best practices. Analyzes personal brand sites, SaaS/B2B products, and
  consulting websites. Evaluates content strategy, CTAs, trust signals,
  technical SEO, AI discoverability (GEO), information architecture,
  accessibility, mobile experience, forms and dark patterns. Renders pages
  with Playwright and axe-core when Node is available, so accessibility and
  mobile findings rest on measurements, not guesses from markup. Use when
  the user says "review my website", "audit my site", "check my SEO",
  "improve my landing page",
  "website feedback", "conversion review", "GEO audit", or wants to analyze
  a website for marketing effectiveness and discoverability.
argument-hint: "[url or repo path]"
allowed-tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, Agent
---

# Website Review

Comprehensive website audit for marketing effectiveness, discoverability, and conversion optimization. Focused on personal brand, SaaS/B2B, and consulting sites.

## Input Handling

**URL provided**: Use WebFetch to retrieve pages. Crawl the full site — start from the root, follow internal navigation links (about, pricing, blog, contact, etc.) to build full context before reviewing. Then run the **Rendered Pass** (below) on the key pages; it is on by default whenever Node is available.

**Repo/local files provided**: Use Read/Glob/Grep to analyze source files (HTML, JSX, templates, CSS, meta tags, structured data, config files). Look for sitemap.xml, robots.txt, and any SEO config. If the site runs locally or has a deployed URL, run the Rendered Pass on it too.

**No input**: Ask the user for a URL or repo path.

## Rendered Pass

WebFetch returns markup only, so contrast, tap-target size, reflow and focus visibility can only be guessed from it. The rendered pass loads each key page in a real browser and measures them.

1. Check `node -v` (18 or later). If Node is missing, skip to the fallback.
2. Set up the tools folder (local npm install of `playwright` and `@axe-core/playwright`, nothing global, nothing in the user's project):
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/setup_render.sh
   ```
   It prints `tools: <dir>` (default `~/.cache/website-review/tools`) and `browser: playwright-chromium | chrome`. Exit 2 means no browser: ask the user before running the printed `npx playwright install chromium` (a ~150 MB download into the user's Playwright cache).
3. Run it on the homepage plus up to 4 key pages (pricing, a product or service page, contact or sign-up), writing to a scratch folder, never into the user's repo:
   ```bash
   node <tools>/render_audit.mjs --urls https://site.com/,https://site.com/pricing --out <scratch>/render
   ```
   Stdout is a per-page summary; `<scratch>/render/render_audit.json` holds the details; `*_fold.png` and full-page PNGs show each page at 390x844 and 1440x900. Read the fold screenshots: they serve the 5-second test and CTA visibility in every scope.
4. Interpret the JSON with the "Rendered Pass" table in [references/ux-architecture.md].
5. **Optional, ask first**: `npx --yes impeccable detect --json <url>` adds design anti-pattern checks (tiny body text, cramped spacing, line length, generic "AI look"). It is a third-party package that downloads its own binary. Use only `detect`; never run `impeccable install` or live mode, which change the user's setup. Exit code 2 means findings, not failure. Some of its rules are aesthetic preferences: report them as inferred opinions, not defects.

**Fallback**: if Node, the npm install or a browser is unavailable (or the user declines), continue with WebFetch only and state in "Scope and evidence base" that no page was rendered, so contrast, target size, reflow and focus findings are inferred from markup.

## Review Scope Selection

Before starting, ask the user:

> **Which review scope would you like?**
> 1. **Essential** — Content & messaging, CTAs & conversion, SEO fundamentals, GEO basics, trust signals (including dark patterns)
> 2. **Full Suite** — Everything in Essential PLUS technical SEO, accessibility, mobile experience, information architecture, forms and interface states, structured data audit, content freshness check, page speed indicators

Default to Essential if the user wants a quick review. Recommend Full Suite for comprehensive audits.

## Crawl Strategy

Gather full site context before writing any findings:

1. Fetch the homepage / root page
2. Identify all primary navigation links and key pages (about, pricing, features, blog, contact, case studies, etc.)
3. Fetch each key page
4. Note any sitemap.xml or robots.txt
5. For repos: glob for all page templates/components, scan for meta tags, structured data, and routing config

Do NOT review page-by-page in isolation. Cross-reference messaging consistency, CTA coherence, and navigation flow across the full site.

## Review Categories

### Always Included (Essential)

Run these for every review. See reference files for detailed criteria:

1. **Content & Messaging** — [references/messaging-conversion.md] sections on messaging
   - Value proposition clarity (above the fold, 5-second test)
   - Audience targeting and language-market fit
   - Brand voice consistency across pages
   - Headline hierarchy and scannability
   - Benefit-driven vs feature-driven framing

2. **CTAs & Conversion** — [references/messaging-conversion.md] sections on conversion
   - CTA clarity, placement, and frequency
   - Conversion funnel logic (awareness > interest > action)
   - Friction points in the user journey
   - Lead capture mechanisms
   - Pricing page effectiveness (if applicable)

3. **Trust Signals** — [references/messaging-conversion.md] sections on trust
   - Social proof (testimonials, logos, case studies, numbers)
   - Authority indicators (credentials, press, partnerships)
   - Security/privacy signals
   - Risk reducers (guarantees, free trials, demos)
   - Trust breakers and dark patterns: fake urgency or scarcity, confirmshaming, pre-checked boxes, consent traps, hidden costs, hard cancellation — [references/forms-states-dark-patterns.md] dark patterns section

4. **SEO Fundamentals** — [references/seo-checklist.md] content SEO section
   - Title tags and meta descriptions (unique, keyword-rich, correct length)
   - Heading hierarchy (single H1, logical H2-H6)
   - Internal linking strategy
   - URL structure and slugs
   - Image alt text
   - Keyword targeting and content gaps

5. **GEO (Generative Engine Optimization)** — [references/geo-checklist.md]
   - Entity clarity and brand definition
   - Question-answer content patterns
   - Citation-worthiness of content
   - Structured claims and data points
   - AI-friendly content formatting
   - Run GEO surface test (see below)

### Full Suite Only

Include these when the user selects Full Suite:

6. **Technical SEO** — [references/seo-checklist.md] technical section
   - Schema markup / structured data (JSON-LD)
   - Canonical tags and duplicate content
   - Sitemap.xml and robots.txt
   - Open Graph and Twitter Card meta
   - Mobile-friendliness signals in markup
   - Hreflang (if multilingual)
   - Crawlability and indexation signals

7. **Accessibility (a11y)** — [references/ux-architecture.md] accessibility and rendered pass sections
   - axe-core violations from the rendered pass, grouped by rule, with WCAG success criteria (measured)
   - Color contrast: measured by axe on the render; from CSS alone it is inferred
   - Keyboard focus: missing focus styles, focus off screen, clickable elements that cannot take focus (measured)
   - Semantic HTML, ARIA labels and roles, alt text completeness and quality
   - Form labels and error states — [references/forms-states-dark-patterns.md] forms section

8. **Mobile Experience** — [references/ux-architecture.md] mobile and rendered pass sections
   - Horizontal overflow at 390 px and reflow at 320 px (measured)
   - Tap targets under 24x24 px without spacing (measured)
   - Viewport meta tag (a 980 px mobile layout width means it is missing)
   - Mobile navigation patterns and content priority, judged from the 390x844 screenshots

9. **Information Architecture** — [references/ux-architecture.md] IA section
   - Navigation clarity and depth
   - Page hierarchy and content flow
   - User journey mapping (entry > goal)
   - Cross-linking between related content
   - Footer utility and sitemap coverage

10. **Forms & States** — [references/forms-states-dark-patterns.md]
    - Labels, instructions, autocomplete, error wording and validation on every form found
    - 404 page (fetch a made-up path), empty, error and loading states
    - Behaviour that needs submission or login goes under "Could not be tested"

11. **Content Freshness** (optional add-on)
    - Blog/content update recency
    - Outdated references or dates
    - Copyright year
    - Changelog or news section currency

12. **Page Speed Indicators** (optional add-on)
    - Large unoptimized images in markup
    - Excessive script/CSS loading
    - Render-blocking resources
    - Lazy loading implementation

## GEO Surface Test

After reviewing content, run a practical GEO assessment:

1. Identify 3-5 queries a potential customer would ask an AI assistant that SHOULD surface this site/brand
2. Evaluate whether the site content would likely be cited based on:
   - Does the content directly answer the query?
   - Is the answer structured clearly (not buried in paragraphs)?
   - Are there specific data points, frameworks, or unique insights an AI would reference?
   - Is the brand/person clearly associated with the topic?
3. For each query, rate likelihood: High / Medium / Low with reasoning
4. Suggest content additions that would improve citation likelihood

## Finding Format

Every issue in the report follows this chain, so the owner can verify it and act on it:

1. **Issue** — the exact problem and where it occurs (page, element, selector or quoted text)
2. **Evidence** — marked **measured** (from the rendered pass: axe, overflow, tap-target or focus checks, screenshots) or **inferred** (from markup, copy or judgment), with what was observed: "axe `color-contrast`, 6 nodes on mobile, e.g. `.hero p` at 3.1:1" or "the H1 reads 'Innovation, delivered'"
3. **Consequence** — what it does to the user's task ("a phone visitor cannot tap the menu icon reliably", "a visitor cannot tell what the product does before scrolling")
4. **Fix** — a change the owner can make with the resources the site shows; give the replacement copy or CSS value when possible
5. **Citation** — a WCAG success criterion (e.g. SC 1.4.3), a Nielsen heuristic (e.g. #1 Visibility of system status), or a named guideline or source (Google Search Central, Baymard, deceptive.design). Omit only when no source fits; do not invent one

## Output Format

Lead with evidence; scores come last and summarise it. Structure the report as follows:

```markdown
# Website Review: [Site Name/URL]

## Overview
- **Site type**: [Personal brand / SaaS / Consulting / ...]
- **Primary audience**: [Who the site targets]
- **Core offering**: [What it sells/promotes]
- **Review scope**: [Essential / Full Suite]

## Scope and Evidence Base
- **Fetched**: [pages fetched with WebFetch or read from the repo]
- **Rendered**: [pages run through the rendered pass, browser and axe version, viewports] — or "No page was rendered (reason); contrast, target size, reflow and focus findings are inferred from markup."
- **Could not be tested**: runtime flows (form submission, checkout, menus behind clicks), logged-in states, real assistive technology (screen readers, voice control), [anything else: blocked pages, consent walls]
- Automated accessibility checks catch only part of WCAG failures and do not replace manual testing with keyboard and screen reader.

## Executive Summary
[3-5 sentences. Lead with the biggest wins and biggest gaps.]

## Priority Issues
[At most 6, ordered by impact on the site's main goal. Each in the finding format.]

### 1. [Issue title]
- **Issue**: ...
- **Evidence** (measured | inferred): ...
- **Consequence**: ...
- **Fix**: ...
- **Citation**: ...

## Detailed Findings

### [Category Name]

**Strengths**
- ...

**Issues** (finding format; one line each is fine for minor issues)
- [Issue] — [measured/inferred: evidence] — [consequence] — [fix] — [citation]

**Quick Wins**
- [Low-effort, high-impact fixes]

[Repeat for each category]

## GEO Surface Test Results

| Query | Likelihood | Reasoning |
|-------|-----------|-----------|
| "..." | High/Med/Low | ... |

## Priority Action Plan

### Immediate (this week)
1. ...

### Short-term (this month)
1. ...

### Strategic (this quarter)
1. ...

## Scores (summary)

| Category | Score | Evidence | Priority |
|----------|-------|----------|----------|
| Content & Messaging | X/10 | inferred | [Critical/High/Medium/Low] |
| Accessibility | X/10 | measured + inferred | ... |
| ... | ... | ... | ... |

**Overall: X/10** — a score summarises the findings above; it is not evidence on its own.

## Appendix: Other Issues
[Remaining issues beyond the top 6, grouped by category, in the short finding format.]

## Questions / Missing Context
[Anything that needs clarification or couldn't be assessed]
```

## Conversational Follow-up

After delivering the report:
- Offer to deep-dive into any specific category
- Ask if the user wants help implementing specific fixes
- If context was missing (e.g., couldn't determine target audience), flag it and ask

## Key Principles

- Follow the finding format: issue, evidence, consequence, fix, citation. A finding without evidence is an opinion; label it as one or drop it
- Mark every finding **measured** or **inferred**. Never present a contrast ratio, target size or overflow as measured unless the rendered pass produced it
- Cap Priority Issues at 6; put the rest in the appendix. Group repeated axe nodes into one finding
- Scores are secondary: they summarise findings, they never replace them
- Automated checks do not replace manual accessibility testing. For a full WCAG audit, suggest the accesslint plugin's skills (`accessibility-audit`, `accessibility-inspect`) if installed; for a review of UI source code, suggest Vercel's `web-design-guidelines` skill. This skill works without either
- Be specific and actionable — "Your H1 on /pricing says X, change it to Y because Z" not "Improve your headlines"
- Reference the actual content found on the site, quote it
- Prioritize by impact — not everything is equally important
- Consider the site type context (personal brand vs SaaS vs consulting have different best practices)
- Score fairly — a 10/10 is rare; a 5/10 means functional but significant room for improvement
- When something is genuinely good, say so — don't manufacture criticism

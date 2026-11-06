# UX, Information Architecture, Accessibility & Mobile

## Table of Contents
- [Information Architecture](#information-architecture)
- [Accessibility](#accessibility)
- [Mobile Experience](#mobile-experience)
- [Rendered Pass: Reading the Measurements](#rendered-pass-reading-the-measurements)

---

## Information Architecture

### Navigation Evaluation

**Primary navigation**:
- [ ] Are all key pages accessible from the main nav?
- [ ] Is the nav limited to 5-7 items? (cognitive load)
- [ ] Are labels clear and descriptive? ("Services" > "What We Do" > "Explore")
- [ ] Is the most important CTA visually prominent in the nav? (usually right-aligned button)
- [ ] Does nav hierarchy match business priorities?

**Common issues**:
- Too many top-level items (decision paralysis)
- Dropdown menus with 20+ items
- Navigation labels that don't match page content
- Missing CTA in navigation
- Logo doesn't link to homepage

### Page Hierarchy & Content Flow

For each key page, evaluate the story arc:

1. **Hook** (above the fold): Does it grab attention and create relevance?
2. **Problem/context**: Does it articulate the visitor's situation?
3. **Solution**: Does it present the offering as the answer?
4. **Evidence**: Does it prove the claims? (social proof, case studies)
5. **Action**: Does it direct to a clear next step?

**Check for**:
- [ ] Does each page have a single clear purpose?
- [ ] Is content ordered by importance (most important first)?
- [ ] Are sections visually distinct with clear breaks?
- [ ] Can a visitor skim the page and get the gist?

### User Journey Mapping

Trace the path from entry to goal:

**Primary journeys to test**:
1. Cold visitor from search > understand offering > convert
2. Referral visitor > validate credibility > convert
3. Returning visitor > find specific info > take action

**Check for**:
- [ ] Are there clear paths for different visitor intents?
- [ ] Is the journey 3 clicks or fewer to conversion?
- [ ] Are there dead-end pages (no clear next step)?
- [ ] Do blog posts link back to service/product pages?

### Footer Evaluation
- [ ] Contains key links not in main nav (privacy, terms, sitemap)
- [ ] Includes contact information
- [ ] Social media links present and working
- [ ] Newsletter signup (if applicable)
- [ ] Not cluttered with excessive links

---

## Accessibility

### Semantic HTML

- [ ] Proper use of `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
- [ ] Headings (`h1`-`h6`) used for structure, not styling
- [ ] Lists used for list content (`<ul>`, `<ol>`)
- [ ] `<button>` for actions, `<a>` for navigation
- [ ] Tables used for tabular data with `<th>` headers

**Common issues**:
- `<div>` and `<span>` used for everything
- Buttons implemented as styled `<div onclick>`
- Links with no `href` or `href="#"`

### ARIA & Roles

- [ ] `role="navigation"` on nav elements (or `<nav>`)
- [ ] `role="main"` on main content (or `<main>`)
- [ ] `aria-label` on icon-only buttons and links
- [ ] `aria-expanded` on toggleable elements (accordions, dropdowns)
- [ ] `aria-live` regions for dynamic content updates
- [ ] Skip navigation link for keyboard users

**Rule**: ARIA is a supplement, not a substitute. Proper HTML semantics first, ARIA for gaps.

### Color & Contrast

Contrast depends on rendered colours, fonts, background images and overlays. Report it as measured only from the rendered pass (axe `color-contrast`); from markup or CSS alone it is inferred.

- [ ] Text meets WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large)
- [ ] Information not conveyed by color alone (add icons, text, patterns)
- [ ] Links distinguishable from body text (not just by color)
- [ ] Focus indicators visible and high-contrast

### Keyboard Navigation

- [ ] All interactive elements reachable via Tab
- [ ] Tab order matches visual order
- [ ] Focus styles are visible (not `outline: none` without replacement)
- [ ] Modals trap focus correctly
- [ ] Escape key closes modals/overlays
- [ ] Custom components (dropdowns, carousels) support arrow keys

### Media

- [ ] All content images have descriptive `alt` text
- [ ] Decorative images have `alt=""` (empty, not missing)
- [ ] Videos have captions or transcripts (if applicable)
- [ ] No auto-playing audio or video

---

## Mobile Experience

### Responsive Design

- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1">` present
- [ ] Layout adapts to narrow viewports: no horizontal scrolling at 320 CSS px wide (WCAG SC 1.4.10 Reflow)
- [ ] Font sizes readable without zooming (minimum 16px body text)
- [ ] Images scale appropriately (no overflow)
- [ ] Tables either scroll horizontally or reformat for mobile

### Touch Targets

- [ ] At least 24x24 CSS px, or enough spacing around smaller targets (WCAG 2.2 SC 2.5.8, AA); 44x44 px is the AAA level (SC 2.5.5) and Apple's guideline; Material recommends 48x48 dp
- [ ] Adequate spacing between adjacent tap targets
- [ ] No hover-dependent interactions without touch alternatives
- [ ] Dropdown menus work via tap (not hover-only)

### Mobile Navigation

- [ ] Hamburger menu (or equivalent) is clearly visible
- [ ] Mobile menu is easy to open AND close
- [ ] CTA remains accessible (sticky header or prominent placement)
- [ ] Phone number is tap-to-call (`tel:` link)
- [ ] No elements hidden on mobile that are important for conversion

### Content Priority

- [ ] Most important content appears first on mobile
- [ ] Long pages have anchor links or jump navigation
- [ ] Forms are simplified for mobile input
- [ ] Large data tables are handled gracefully (horizontal scroll, cards, or collapsible)

---

## Rendered Pass: Reading the Measurements

`scripts/render_audit.mjs` writes `render_audit.json` plus screenshots. Each item below is **measured** evidence; cite the selector, count and viewport. Markup-only observations stay **inferred**.

| JSON field | What it measured | Cite | How to read it |
|---|---|---|---|
| `viewports.*.axe.violations[]` | axe-core rules failed in the rendered DOM, per viewport | `wcag_sc` (e.g. 1.4.3), else "axe best practice" | `count` = affected nodes; `nodes[].target` = selector; `impact` is axe's rating, not yours. Group repeated nodes into one finding |
| `viewports.*.axe.incomplete[]` | Checks axe could not decide (often contrast over images or gradients) | as above | Never report as failures. Look at the screenshot and mark "inferred from screenshot", or list as "needs manual check" |
| `viewports.mobile.overflow` | Document wider than the 390 px viewport; `offenders` = elements crossing the right edge whose parent does not | SC 1.4.10 | `viewport_width` 980 means no viewport meta tag: the phone shows a zoomed-out desktop page, a bigger problem than overflow |
| `reflow_320` | Same check at 320 px | SC 1.4.10 | Failure here but not at 390 px is a narrower-phone and 400% zoom problem |
| `viewports.mobile.tap_targets` | Interactive elements under 24x24 px whose 24 px circle overlaps another target | SC 2.5.8 | `spaced_exception` targets pass the SC. Inline text links are skipped. Icon rows and footer links are the usual offenders |
| `viewports.desktop.focus.no_style_change` | Tab stops where no outline, shadow, border, background, colour or underline changed on focus | SC 2.4.7 | Strong signal of a missing focus indicator; confirm on one element by hand when possible |
| `viewports.desktop.focus.focus_off_screen` | Tab stops outside the visible viewport | SC 2.4.11 | Often hidden menus or off-canvas links that stay focusable |
| `viewports.desktop.focus.pointer_not_focusable` | Elements with a pointer cursor that cannot take keyboard focus | SC 2.1.1 (candidate) | Candidates only: overlays and decorative wrappers also match. Report only when the element does something (opens, submits, navigates) |
| `viewports.*.page_errors` | JavaScript errors thrown during load | (none) | Mention when they break visible features |
| `screenshot_fold` / `screenshot_full` | 390x844 and 1440x900 renders, animations off | (none) | Use the fold shots for the 5-second test, CTA visibility and visual hierarchy. Cookie banners are not dismissed and may cover content |

**Limits to state in the report**: automated rules find only part of WCAG failures; they cannot judge alt-text quality, reading order meaning, screen-reader announcements, focus order logic, or whether error messages help. The pass does not submit forms, open menus, log in or use assistive technology.

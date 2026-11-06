# UX, Information Architecture, Accessibility & Mobile

## Table of Contents
- [Information Architecture](#information-architecture)
- [Accessibility](#accessibility)
- [Mobile Experience](#mobile-experience)

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

### Forms

- [ ] All inputs have associated `<label>` elements
- [ ] Required fields clearly indicated (not just by color)
- [ ] Error messages are specific and associated with the field
- [ ] Form can be submitted via keyboard (Enter key)
- [ ] Autocomplete attributes on common fields (name, email, phone)

### Media

- [ ] All content images have descriptive `alt` text
- [ ] Decorative images have `alt=""` (empty, not missing)
- [ ] Videos have captions or transcripts (if applicable)
- [ ] No auto-playing audio or video

---

## Mobile Experience

### Responsive Design

- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1">` present
- [ ] Layout adapts to narrow viewports (no horizontal scrolling)
- [ ] Font sizes readable without zooming (minimum 16px body text)
- [ ] Images scale appropriately (no overflow)
- [ ] Tables either scroll horizontally or reformat for mobile

### Touch Targets

- [ ] Minimum 44x44px touch targets (WCAG) / 48x48dp (Material)
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

---
name: website-review
description: >
  Reviews websites for marketing, SEO, GEO, messaging, conversion, and UX
  best practices. Analyzes personal brand sites, SaaS/B2B products, and
  consulting websites. Evaluates content strategy, CTAs, trust signals,
  technical SEO, AI discoverability (GEO), information architecture,
  accessibility, and mobile experience. Use when the user says "review my
  website", "audit my site", "check my SEO", "improve my landing page",
  "website feedback", "conversion review", "GEO audit", or wants to analyze
  a website for marketing effectiveness and discoverability.
argument-hint: "[url or repo path]"
allowed-tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, Agent
---

# Website Review

Comprehensive website audit for marketing effectiveness, discoverability, and conversion optimization. Focused on personal brand, SaaS/B2B, and consulting sites.

## Input Handling

**URL provided**: Use WebFetch to retrieve pages. Crawl the full site — start from the root, follow internal navigation links (about, pricing, blog, contact, etc.) to build full context before reviewing.

**Repo/local files provided**: Use Read/Glob/Grep to analyze source files (HTML, JSX, templates, CSS, meta tags, structured data, config files). Look for sitemap.xml, robots.txt, and any SEO config.

**No input**: Ask the user for a URL or repo path.

## Review Scope Selection

Before starting, ask the user:

> **Which review scope would you like?**
> 1. **Essential** — Content & messaging, CTAs & conversion, SEO fundamentals, GEO basics, trust signals
> 2. **Full Suite** — Everything in Essential PLUS technical SEO, accessibility, mobile experience, information architecture, structured data audit, content freshness check, page speed indicators

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

7. **Accessibility (a11y)** — [references/ux-architecture.md] accessibility section
   - Semantic HTML usage
   - ARIA labels and roles
   - Color contrast indicators
   - Keyboard navigation support
   - Form labels and error states
   - Alt text completeness

8. **Mobile Experience** — [references/ux-architecture.md] mobile section
   - Responsive design patterns in markup/CSS
   - Touch target sizing
   - Mobile navigation patterns
   - Viewport meta tag
   - Content priority on small screens

9. **Information Architecture** — [references/ux-architecture.md] IA section
   - Navigation clarity and depth
   - Page hierarchy and content flow
   - User journey mapping (entry > goal)
   - Cross-linking between related content
   - Footer utility and sitemap coverage

10. **Content Freshness** (optional add-on)
    - Blog/content update recency
    - Outdated references or dates
    - Copyright year
    - Changelog or news section currency

11. **Page Speed Indicators** (optional add-on)
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

## Output Format

Structure the report as follows:

```markdown
# Website Review: [Site Name/URL]

## Overview
- **Site type**: [Personal brand / SaaS / Consulting / ...]
- **Primary audience**: [Who the site targets]
- **Core offering**: [What it sells/promotes]
- **Review scope**: [Essential / Full Suite]

## Executive Summary
[3-5 sentence overall assessment. Lead with the biggest wins and biggest gaps.]

## Scores

| Category | Score | Priority |
|----------|-------|----------|
| Content & Messaging | X/10 | [Critical/High/Medium/Low] |
| CTAs & Conversion | X/10 | ... |
| Trust Signals | X/10 | ... |
| SEO | X/10 | ... |
| GEO | X/10 | ... |
| [Full Suite categories if applicable] | ... | ... |

**Overall: X/10**

## Detailed Findings

### [Category Name] — X/10

**Strengths**
- ...

**Issues**
- [Specific issue]: [Where it occurs] — [Why it matters] — [How to fix it]

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

## Questions / Missing Context
[Anything that needs clarification or couldn't be assessed]
```

## Conversational Follow-up

After delivering the report:
- Offer to deep-dive into any specific category
- Ask if the user wants help implementing specific fixes
- If context was missing (e.g., couldn't determine target audience), flag it and ask

## Key Principles

- Be specific and actionable — "Your H1 on /pricing says X, change it to Y because Z" not "Improve your headlines"
- Reference the actual content found on the site, quote it
- Prioritize by impact — not everything is equally important
- Consider the site type context (personal brand vs SaaS vs consulting have different best practices)
- Score fairly — a 10/10 is rare; a 5/10 means functional but significant room for improvement
- When something is genuinely good, say so — don't manufacture criticism

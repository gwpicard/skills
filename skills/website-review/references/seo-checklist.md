# SEO Checklist

## Table of Contents
- [Content SEO](#content-seo)
- [Technical SEO](#technical-seo)

---

## Content SEO

### Title Tags
- Unique per page
- 50-60 characters (Google truncates beyond ~60)
- Primary keyword near the beginning
- Brand name at the end (separated by | or —)
- Compelling for clicks, not just keyword-stuffed
- **Common issues**: Duplicate titles, missing titles, "Home" as title, keyword stuffing

### Meta Descriptions
- Unique per page
- 150-160 characters
- Includes primary keyword naturally
- Contains a call-to-action or value statement
- **Common issues**: Missing descriptions, duplicate across pages, too short/long

### Heading Hierarchy
- Single H1 per page (matches/complements the title tag)
- H2-H6 in logical order (no skipping levels)
- Keywords used naturally in headings
- Headings describe section content (not decorative)
- **Common issues**: Multiple H1s, H1 used for logo/site name, headings skipping from H1 to H4

### URL Structure
- Short, descriptive slugs
- Hyphens between words (not underscores)
- Lowercase only
- No unnecessary parameters or IDs
- Reflects site hierarchy: `/services/consulting/` not `/page?id=42`
- **Common issues**: Auto-generated URLs, dates in non-news URLs, deeply nested paths

### Internal Linking
- Key pages reachable within 3 clicks from homepage
- Contextual links between related content
- Descriptive anchor text (not "click here" or "read more")
- No orphan pages (pages with no internal links pointing to them)
- Blog posts link to service/product pages where relevant
- **Common issues**: No cross-linking between blog and service pages, thin internal link structure

### Image Optimization
- Descriptive alt text on all content images (not decorative images)
- Alt text includes keywords where natural (not stuffed)
- Descriptive file names (`consulting-workshop.jpg` not `IMG_4521.jpg`)
- Appropriate format (WebP/AVIF preferred, SVG for icons/logos)
- **Common issues**: Empty alt attributes, alt text = filename, missing alt on key images

### Keyword Strategy
- Each key page targets a primary keyword/phrase
- No keyword cannibalization (two pages competing for same term)
- Long-tail keywords addressed in blog/resource content
- Keywords match user intent (informational, commercial, navigational)
- **Common issues**: No clear keyword targeting, homepage trying to rank for everything

### Content Quality Signals
- Sufficient depth for the topic (thin content = low ranking potential)
- Original content (not duplicated from elsewhere)
- Updated/current information
- Expert-level content for YMYL topics
- E-E-A-T signals (Experience, Expertise, Authoritativeness, Trustworthiness)

---

## Technical SEO

### Structured Data / Schema Markup
Check for JSON-LD implementation of relevant types:
- **All sites**: `Organization` or `Person`, `WebSite`, `BreadcrumbList`
- **Personal brands**: `Person` with `sameAs` links to social profiles
- **SaaS**: `SoftwareApplication`, `Product`, `FAQPage`, `HowTo`
- **Consulting**: `ProfessionalService`, `Service`, `FAQPage`
- **Blog posts**: `Article` or `BlogPosting` with `author`, `datePublished`
- **Reviews/testimonials**: `Review`, `AggregateRating`

Validate: Structured data should be valid JSON-LD, not Microdata (preferred by Google). Check for required properties per schema type.

### Canonical Tags
- Every page has a `<link rel="canonical">` pointing to its preferred URL
- Consistent protocol (https) and www/non-www
- No self-referencing errors
- Pagination handled correctly (if applicable)

### Sitemap & Robots
- `sitemap.xml` exists at root and is referenced in `robots.txt`
- Sitemap includes all indexable pages
- Sitemap excludes noindex pages
- `robots.txt` exists and doesn't block important content
- No accidental `Disallow: /` on production

### Open Graph & Social Meta
- `og:title`, `og:description`, `og:image` on all pages
- `og:image` is at least 1200x630px
- Twitter Card meta (`twitter:card`, `twitter:title`, etc.)
- Unique social images for key pages (not the same image everywhere)

### Mobile & Indexation
- `<meta name="viewport" content="width=device-width, initial-scale=1">` present
- No `<meta name="robots" content="noindex">` on pages that should be indexed
- No blocked resources in robots.txt that Googlebot needs for rendering
- Responsive design (not separate mobile site)

### Crawlability
- Clean link structure (no JavaScript-only navigation that blocks crawlers)
- No excessive redirects (redirect chains)
- 404 pages return proper 404 status codes
- No soft 404s (200 status on empty/error pages)

### Hreflang (Multilingual Sites)
- `hreflang` tags present if content exists in multiple languages
- Self-referencing hreflang included
- Return links (if page A links to page B with hreflang, B links back to A)
- `x-default` specified for the fallback version

### HTTPS & Security
- All pages served over HTTPS
- HTTP redirects to HTTPS
- No mixed content warnings
- HSTS header present (ideal)

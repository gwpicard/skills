# Forms, Interface States & Dark Patterns

## Table of Contents
- [Forms](#forms)
- [Empty, Error & Loading States](#empty-error--loading-states)
- [Dark Patterns](#dark-patterns)
- [What a Review Can and Cannot See](#what-a-review-can-and-cannot-see)

---

## Forms

Review every lead capture, contact, sign-up, newsletter and checkout form found during the crawl.

### Labels and instructions
- [ ] Every input has a visible label that stays visible while typing; a placeholder alone is not a label (WCAG 1.3.1, 3.3.2)
- [ ] The accessible name contains the visible label text (WCAG 2.5.3 Label in Name)
- [ ] Required and optional fields are marked in text, not by colour or an asterisk alone (WCAG 1.4.1, 3.3.2)
- [ ] Format rules (password rules, date format, phone format) are stated before the user types, not only after an error
- [ ] Common fields carry `autocomplete` tokens (`name`, `email`, `tel`, `street-address`) (WCAG 1.3.5)
- [ ] Inputs use the right `type` (`email`, `tel`, `number`) so phones show the right keyboard

### Errors and validation
- [ ] Errors name the field and say how to fix it ("Enter an email like name@company.com"), not just "Invalid input" (WCAG 3.3.1, 3.3.3)
- [ ] Error text is linked to the field (`aria-describedby`) and announced (`aria-live` or focus moved to an error summary) (WCAG 4.1.3)
- [ ] Validation does not fire on every keystroke or before the user leaves the field
- [ ] Entered data survives an error; the form does not clear itself
- [ ] Legal, financial or data-deleting submissions can be reviewed, corrected or reversed (WCAG 3.3.4)
- [ ] Users are not asked to re-enter information they already gave in the same flow (WCAG 3.3.7 Redundant Entry)
- [ ] Log-in does not depend on a memory or puzzle test without an alternative (WCAG 3.3.8 Accessible Authentication)

### Friction
- [ ] Only fields the business needs now; every optional or premature field adds effort (Baymard Institute checkout usability research)
- [ ] The submit button names the outcome ("Book my call"), not "Submit"
- [ ] The page says what happens after submission (reply time, next step, confirmation email)
- [ ] A success state confirms the submission on the page or on a confirmation page

**Evidence note**: labels, `autocomplete`, `type` and `aria-describedby` are visible in markup (inferred) or in axe results (measured). Error wording, validation timing and data retention appear only when the form is submitted; mark them "not tested" unless you exercised the form.

---

## Empty, Error & Loading States

Look for these on the pages you can reach (search results, blog filters, pricing calculators, dashboards shown in demos, 404 page).

- [ ] **404 page**: exists, keeps the site navigation, offers search or key links, and returns HTTP 404 (fetch a made-up path such as `/this-page-does-not-exist`)
- [ ] **Empty states**: an empty search result or filter explains why it is empty and offers a next step, not a blank area
- [ ] **Error states**: failed loads or submissions say what went wrong in plain words and how to recover; no raw stack traces or error codes alone
- [ ] **Loading states**: content that loads late has a skeleton or progress indicator, and the layout does not jump when it arrives (check the CLS of the page if measured)
- [ ] **Status messages** (added to cart, saved, sent) are announced to screen readers without moving focus (WCAG 4.1.3)
- [ ] **Offline or slow network**: forms do not lose data when the request fails (not testable without runtime access; list under "not tested")

---

## Dark Patterns

Dark patterns are interface designs that push users into choices they would not otherwise make. They damage trust once noticed and several are regulated: for example the EU Digital Services Act (Art. 25), the EU Unfair Commercial Practices Directive, GDPR and ePrivacy consent rules, and US FTC enforcement against hidden fees and hard-to-cancel subscriptions. Name the pattern, quote what the site shows, and say who is harmed and how. Do not give legal advice; say "may conflict with" and suggest the owner checks with counsel.

Reference taxonomy: Harry Brignull, *Deceptive Patterns* (deceptive.design); Mathur et al., "Dark Patterns at Scale" (CSCW 2019); OECD, "Dark Commercial Patterns" (2022).

| Pattern | What to look for | Example evidence |
|---|---|---|
| **Fake urgency** | Countdown timers that reset on reload; "offer ends today" with no date; "sale" that never ends | Reload the page; compare timer values between two fetches |
| **Fake scarcity** | "Only 2 left", "12 people are viewing this" with no source; numbers that change randomly | Same claim on every product; value differs per load |
| **Fake social proof** | Pop-ups "Anna from Berlin just bought…" with no verifiable source | Script names such as `fomo`, `proof`, `salespop` in markup |
| **Confirmshaming** | Decline link worded to shame: "No thanks, I don't want to grow my business" | Quote the exact decline text |
| **Pre-checked boxes** | Newsletter, marketing consent, add-on insurance or donations ticked by default | `<input type="checkbox" checked>` near consent or add-on text |
| **Cookie and consent traps** | "Accept all" prominent while "Reject" is hidden behind a second layer; trackers firing before consent; consent walls; "legitimate interest" toggles on by default | Compare button prominence in the screenshot; note scripts loaded before any choice |
| **Hidden costs** | Fees, taxes or shipping appearing only at the last step; "from" prices that no plan actually costs | Compare advertised price with the price shown later in the flow |
| **Drip pricing / bait and switch** | Advertised plan unavailable; free trial that silently converts to paid | Trial terms in small print; no reminder before charging |
| **Roach motel** | Signing up takes one click, cancelling requires a call, a chat or many screens | Look for a cancellation page or help article; count the steps described |
| **Forced continuity** | Card required for a "free" trial with auto-renewal not stated near the button | Text near the trial CTA |
| **Nagging** | Repeated pop-ups or modals that return after dismissal | Note if the same modal appears on each page |
| **Disguised ads / trick questions** | Ads styled as content or download buttons; double negatives in opt-out text ("Uncheck to not receive…") | Quote the wording |

**Consequence to state**: users pay more, consent to data use or marketing they did not choose, or cannot leave; once noticed, the pattern lowers trust and raises refund, chargeback and complaint rates.

**Feasible fix**: show the real deadline or remove it; neutral decline wording ("No thanks"); unchecked boxes by default; "Reject all" on the first consent layer with equal weight; full price including fees on the first price display; online cancellation in as many steps as sign-up.

---

## What a Review Can and Cannot See

- **Visible in a fetch or render**: wording, default checkbox states, consent banner layout, advertised prices, labels and attributes in markup.
- **Needs runtime interaction**: timers resetting, hidden fees at checkout, cancellation flow length, validation behaviour, trackers firing before consent. Report these as "not tested" unless you exercised them, or as "inferred" with the observation that led you there.

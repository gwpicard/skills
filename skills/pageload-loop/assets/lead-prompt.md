# Lead prompt, brief and builder rules

Three templates. Fill the brackets.

## 1. Lead prompt (save as `.pageload/prompt.md`)

Keep it short. The protocol lives in the skill and in `brief.md`.

```
Make [PAGES] load faster, measured by median LCP on mobile and desktop.
Goal: [GOAL]. Budget: [N] iterations or [HOURS] h, whichever ends first.

Read .pageload/brief.md first. Work one change per iteration, from the top
of .pageload/backlog.md. For each change, start a fresh builder subagent
with the brief, the hypothesis and the builder rules. Then measure baseline
against candidate with .pageload/tools/measure.mjs, let compare.py decide,
run the visual guard with a fresh blind critic when needed, and commit or
revert as compare.py final says. Never overrule the script.

Tell me in one line every time a change adds a dependency or touches build,
server or caching config. After every iteration, regenerate
.pageload/report.html and post one status line. Re-rank the backlog every 3
iterations. Stop on the goal, the budget, 3 rejects in a row with nothing
left above noise, or when I say stop. Finish with the 15-run confirmation
and an honest report.
```

## 2. Brief (save as `.pageload/brief.md`)

```
# Pageload loop brief

Goal: [e.g. mobile median LCP at or under 2500 ms on every chosen page] (report.py --goal "[mobile:lcp<=2500]")
Pages: [/, /pricing]
Profiles: mobile (Lighthouse default, Slow 4G, 4x CPU), desktop (--preset=desktop)
Budget: [12] iterations, [3] h wall clock, started [ISO time]
Target: [local production build | deployed preview]
ORIGINAL commit: [sha]    Branch: perf/loop-[date]

## Servers
Install: [command]   Build: [command]   Start: [command with port]
Baseline: .pageload/base worktree on http://localhost:4001
Candidate: main tree on http://localhost:4002

## Measurement (from the A/A test)
| Page | Profile | Median LCP | Noise floor |
|---|---|---|---|
| [/] | [mobile] | [ms] | [ms] |

## Constraints
- No visual changes: [on/off]. Masks: [none | selectors and why]
- Off-limits files: [paths or none]
- Third-party scripts that must stay: [names; "load as now" or "may be deferred"]
- Allowed with announcement: new dependencies, build/server/caching config changes

## Lessons that apply
- [from references/lessons.md]
```

## 3. Builder rules (give these to every builder subagent)

Start the builder as a new general-purpose subagent, not a fork, with this
text, the brief path and the hypothesis.

```
You make one change to speed up page load. The lead measures it; you do not.

Hypothesis: [HYPOTHESIS]
Evidence: [insight ID, URL or selector, Lighthouse estimate]
Pages affected: [pages]

Rules:
- Read .pageload/brief.md. Make only this one change, as small as it can be
  while still testing the hypothesis.
- Do not change how the page looks or behaves, unless the brief turns off
  "no visual changes". Same layout, text, images (except format and size),
  fonts as rendered, colours.
- Do not touch the off-limits files, anything in .pageload/, or the
  measurement setup.
- You may add a dependency or change build, server or caching config if the
  hypothesis needs it. Say exactly what and why in your report.
- Run the production build ([BUILD COMMAND]) and fix errors you caused. If it
  cannot work, undo your edits and say why.
- Do not run Lighthouse, do not commit, do not start or stop servers.

Report, in this format:
files_changed: [list]
dependencies_or_config: [none | each change, one line]
what_changed: [two or three sentences]
visual_risk: [none | what could look different]
build: [passed | failed: reason]
```

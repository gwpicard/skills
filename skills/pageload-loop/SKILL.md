---
name: pageload-loop
description: Runs a measured loop that speeds up web pages one change at a time, keeps only real LCP gains and reports progress. Use for "make this page load faster", "improve LCP", "page speed loop".
argument-hint: "[optional: pages or goal, e.g. '/ and /pricing, mobile LCP under 2.5 s']"
---

# Pageload Loop

A goal loop for page speed. A builder subagent makes one change, the loop
measures it against the current baseline with Lighthouse, and a script keeps
the change only when the gain is real: larger than the measured noise,
statistically clear, and with no regression on any chosen page. A fresh
critic subagent checks that the page still looks the same. Every iteration
updates a self-contained HTML report.

## Critical rules

- **Scripts decide, not the model.** `compare.py` turns measurements into
  keep, reject or inconclusive. Never overrule it, and never report a gain
  that it did not measure.
- **Measure a production build**, never the dev server. Dev servers skip
  minification, code splitting and compression, so their numbers do not
  transfer.
- **Prove the measurement before iteration 1.** An A/A test (two servers of
  the same build) sets the noise floor and must come out stable.
- **One change per iteration.** Two changes at once make the result
  uninterpretable and the revert ambiguous.
- **Announce every dependency, build-config, server-config or caching-header
  change in the session when it happens**, and log it with `--change`. The
  user agreed to such changes on the condition that they see each one.
- **Report the confirmed gain**: the final 15-run comparison of the original
  against the final code, not the sum of per-iteration gains.
- **Measure one thing at a time on the machine.** Never run Lighthouse in
  parallel, and ask the user to close heavy apps. CPU contention moves lab
  numbers more than most changes do.

## Step 1. Read the project

Before asking anything, find out from the repo:

- framework, package manager, the production **build** and **start** commands,
  and how the start command takes a port (`PORT=4002`, `--port 4002`);
- the routes: `app/` or `pages/` (Next.js), `src/pages/` (Astro, Nuxt),
  `src/routes/` (SvelteKit, Remix), static `*.html` files, `sitemap.xml`;
- third-party scripts (analytics, tag managers, chat, A/B testing, ads);
- whether the working tree is clean (`git status`). The loop works on a
  branch and reverts with git, so uncommitted work must be committed or
  stashed by the user first.

Pick up to four candidate pages: the home page, the highest-traffic template
(product, article, pricing), and any page the user named.

## Step 2. Interview (one round)

One AskUserQuestion call, at most four questions. Skip any question the
request already answers.

1. **Target.** "Local production build (build and start), recommended" or
   "Deployed preview URL". A preview needs a deploy per iteration, so the
   loop pushes the branch each time; say this in the option text.
2. **Pages** (multi-select). The candidates from step 1, each with its route.
   Each chosen page multiplies the measurement time.
3. **Goal and budget.** Offer for example "Mobile LCP at or under 2.5 s
   (Core Web Vitals 'good'), 12 iterations, 3 hours", "LCP −20% on mobile,
   12 iterations, 3 hours", "Best effort, 6 iterations, 1 hour". The goal
   becomes `--goal` for `report.py` (`mobile:lcp<=2500`, `mobile:lcp-20%`).
4. **Constraints** (multi-select): "No visual changes" (recommended, on by
   default), "Third-party scripts must load as they do now", "Off-limits
   files or folders (type them in Other)".

Fixed by design (state them, do not ask): primary metric median LCP;
guardrails CLS at most 0.1, TBT (the lab proxy for INP) and TTFB, which only
block and never count as wins; both mobile and desktop profiles; the loop may
add dependencies or change build, server or caching config, announced each
time; masking dynamic regions is off unless the A/A visual check needs it.

## Step 3. Build the harness and prove it

Read `references/measurement.md` before this step.

1. **Tools.** `bash ${CLAUDE_SKILL_DIR}/scripts/setup_tools.sh .` copies the
   scripts to `.pageload/tools/`, installs Lighthouse 13, Playwright,
   pixelmatch and pngjs there (not globally, not in the project's
   `package.json`), adds `.pageload/` to `.git/info/exclude`, and runs the
   `compare.py` self-test. It needs Node 22.19+ and Python 3.8+.
2. **Branch.** `git switch -c perf/loop-$(date +%Y%m%d)`. Record the start
   commit as ORIGINAL in the brief.
3. **Two servers.** Baseline in a worktree, candidate in the main tree:
   ```
   git worktree add --detach .pageload/base HEAD
   (cd .pageload/base && <install> && <build> && PORT=4001 <start>)   # run in background
   <build> && PORT=4002 <start>                                       # run in background
   ```
   Wait until both answer (`curl -sf http://localhost:4001/`). For a deployed
   preview, the baseline is the original deploy URL and the candidate is the
   branch preview URL.
4. **A/A test.** Both servers run the same commit now. Measure them against
   each other, 7 runs, both profiles, with filmstrips:
   ```
   T=.pageload/tools
   node $T/measure.mjs --variant a=http://localhost:4001 --variant b=http://localhost:4002 \
     --pages /,/pricing --profiles mobile,desktop --runs 7 --filmstrip devtools --out .pageload/runs/iter-00
   python3 $T/compare.py aa --measure .pageload/runs/iter-00/measure.json --out .pageload/noise.json
   ```
   Exit code 3 means the two identical builds measured differently. Find the
   cause (background load, a server that caches the first request, random
   content, a page that depends on the clock) and repeat. Do not start the
   loop on an unstable A/A.
5. **Visual baseline.**
   ```
   node $T/visual_diff.mjs capture --origin http://localhost:4001 --pages /,/pricing --out .pageload/shots/original
   node $T/visual_diff.mjs capture --origin http://localhost:4002 --pages /,/pricing --out .pageload/shots/aa
   node $T/visual_diff.mjs compare --base .pageload/shots/original --cand .pageload/shots/aa --out .pageload/shots/diff-aa
   ```
   If the A/A shots differ, look at the diff PNGs, name the dynamic regions
   (ads, dates, carousels, A/B variants), and only then offer the user
   masking with `--mask "selector,selector"` on every capture.
6. **Log the baseline and render the first report.**
   ```
   python3 $T/compare.py log --runs-jsonl .pageload/runs.jsonl --kind baseline --iter 0 \
     --measure .pageload/runs/iter-00/measure.json --noise .pageload/noise.json --hypothesis "baseline (A/A)" --commit ORIGINAL
   python3 $T/report.py --runs-jsonl .pageload/runs.jsonl --out-dir .pageload --goal "<goal>" --title "<site>: page load loop"
   ```

## Step 4. Write the loop files

```
.pageload/
  brief.md        goal, pages, profiles, budget, start time, constraints, ORIGINAL commit,
                  build/start commands and ports, off-limits files, third parties, lessons
  prompt.md       lead prompt (from assets/lead-prompt.md)
  critic.md       copy of assets/critic-visual.md
  backlog.md      ranked hypotheses
  tools/          scripts and their node_modules (from setup_tools.sh)
  base/           git worktree for the baseline server
  runs/iter-NN/   measure.json, insights.json, decision.json, filmstrips.json
  shots/          screenshots and diffs;  pairs/  blind pairs for the critic
  noise.json      noise floor from the A/A test
  runs.jsonl      one line per page, profile and variant per measurement
  report.html     live report;  report.md  PR body
```

Fill `brief.md` and `prompt.md` from `assets/lead-prompt.md`. Copy
`assets/critic-visual.md` to `critic.md`. Add the lessons from
`references/lessons.md` that apply to this stack.

**Backlog.** Rank the hypotheses with
`python3 $T/compare.py insights --insights .pageload/runs/iter-00/insights.json --only-variant a`
and the catalogue in `references/strategies.md`. Score each one as
estimated LCP ms saved ÷ risk (1 low, 2 medium, 3 high). Drop anything
whose estimate is below the noise floor and anything the constraints
forbid. Write the ranked list to `backlog.md` with the evidence (insight ID,
the URL or element it names).

## Step 5. Confirm and launch

Show the user, briefly:

- pages, profiles, goal, budget, constraints;
- the A/A result: median LCP and noise floor per page and profile;
- the top five hypotheses;
- time per iteration: about 12 s per Lighthouse run, so
  pages × 2 profiles × (2 × 7 + 2 warm-up) runs, plus build and screenshots.
  Two pages take about 15 minutes per iteration;
- that dependency and config changes will be announced as they happen;
- where to watch: `.pageload/report.html` (it reloads every 60 s).

Launch only after a clear yes. The loop runs in this session: you are the
lead and you start builder and critic subagents.

## Step 6. Run the loop (you are the lead)

For iteration N (two-digit folder `iter-NN`):

1. **Pick** the top hypothesis from `backlog.md`.
2. **Build.** Start a fresh general-purpose subagent (never a fork) with
   `brief.md`, the hypothesis and its evidence, and the builder rules from
   `assets/lead-prompt.md`. It makes one change and runs the build.
3. **Check the diff.**
   - `git diff --name-only` touches an off-limits file, or the build fails:
     `git checkout -- . && git clean -fd`, then
     `compare.py log --runs-jsonl .pageload/runs.jsonl --iter N --reject-reason "<why>" --hypothesis "<h>"`.
   - It matches
     `package.json|lock|yarn.lock|pnpm-lock|bun.lock|\.config\.|vercel.json|netlify.toml|_headers|nginx|\.htaccess|server\.|middleware`:
     tell the user now, in one line, what was added or changed and why, and
     pass each one as `--change` when logging.
4. **Restart** the candidate server on port 4002 with the new build.
5. **Measure** baseline (4001) against candidate (4002):
   ```
   node $T/measure.mjs --variant base=http://localhost:4001 --variant cand=http://localhost:4002 \
     --pages <pages> --profiles mobile,desktop --runs 7 --out .pageload/runs/iter-NN
   python3 $T/compare.py decide --measure .pageload/runs/iter-NN/measure.json --noise .pageload/noise.json \
     --out .pageload/runs/iter-NN/decision.json
   ```
   **Inconclusive**: measure once more into `iter-NN-retry` with `--runs 14`
   and decide with `--retry`. A second inconclusive is a reject.
6. **Visual guard** (only when the decision is keep and "no visual changes"
   is on): capture the candidate into `.pageload/shots/iter-NN` and compare
   with `.pageload/shots/original`. Shots that fail go to a blind critic:
   ```
   node $T/visual_diff.mjs pair --base .pageload/shots/original --cand .pageload/shots/iter-NN \
     --shots <failed names> --out .pageload/pairs/iter-NN
   ```
   Start one fresh general-purpose subagent per pair folder with only
   `.pageload/critic.md` and the folder path. Any "different" means
   `--visual fail`; all "same" means `--visual critic-same`; no failed shots
   means `--visual pass`. With the constraint off, use `--visual off`.
7. **Final decision.**
   `python3 $T/compare.py final --decision .pageload/runs/iter-NN/decision.json --visual <v>`
   prints `keep<TAB>LCP −x ms (<page> <profile>)` or `reject<TAB><reason>`.
   Use the retry's `decision.json` when there was a retry.
8. **Apply, then log.**
   - keep: `git add -A && git commit -m "perf(iter-N): <change> LCP −x ms (<page> <profile>)"`,
     using the text `final` printed. Move the baseline:
     `git -C .pageload/base checkout --detach <sha>`, rebuild, restart on 4001.
   - reject: `git checkout -- . && git clean -fd`. Note the reason in
     `backlog.md` so the hypothesis is not retried unchanged.
   ```
   python3 $T/compare.py log --runs-jsonl .pageload/runs.jsonl --iter N --measure .pageload/runs/iter-NN/measure.json \
     --decision .pageload/runs/iter-NN/decision.json --noise .pageload/noise.json --hypothesis "<h>" \
     --visual <v> [--visual-ratio <worst ratio>] [--change "<what>"] [--commit <sha, keep only>]
   ```
   Log the retry measurement, not the first one, when there was a retry.
9. **Report.** `python3 $T/report.py --runs-jsonl .pageload/runs.jsonl --out-dir .pageload --goal "<goal>" --status running`, then one line in
   the session: `Iteration N: <change> → <decision> (<reason>).`
10. **Re-rank every 3 iterations** from the latest kept candidate's
    `insights.json` (`--only-variant cand`). Fixed problems drop out and new
    ones surface.

**Stop** when the first of these is true:
- the goal is met (`report.py` prints it);
- the iteration budget or wall-clock budget is used up (leave time for the
  confirmation run, about 2 × 15 runs per page and profile);
- 3 rejects in a row and no remaining hypothesis estimates a gain above the
  noise floor;
- the user says stop.

If the user asks to stop mid-iteration, revert the uncommitted change first.

## Step 7. Confirm and report

1. Check out ORIGINAL in the base worktree, build, start on 4001. The final
   code runs on 4002.
2. ```
   node $T/measure.mjs --variant base=http://localhost:4001 --variant cand=http://localhost:4002 \
     --pages <pages> --profiles mobile,desktop --runs 15 --filmstrip devtools --out .pageload/runs/final
   python3 $T/compare.py confirm --measure .pageload/runs/final/measure.json --noise .pageload/noise.json \
     --out .pageload/runs/final/confirm.json
   python3 $T/compare.py log --runs-jsonl .pageload/runs.jsonl --kind confirm --iter final \
     --measure .pageload/runs/final/measure.json --decision .pageload/runs/final/confirm.json \
     --noise .pageload/noise.json --hypothesis "original vs final" --commit <head sha>
   ```
3. Write honest notes to `.pageload/notes.md`: what did not work and why,
   what could not be measured (cache headers, field INP), risks the user
   should review. Then
   `python3 $T/report.py --runs-jsonl .pageload/runs.jsonl --out-dir .pageload --goal "<goal>" --status finished --notes .pageload/notes.md`.
4. Tell the user: the confirmed change per page and profile with its 95%
   interval, whether the goal is met, the dependency and config changes, and
   the report path. Offer `report.md` as the PR body. Stop the servers and
   remove the worktree (`git worktree remove .pageload/base`).

## Files

| File | Use |
|---|---|
| `references/measurement.md` | Protocol, metrics, statistics, decision rules, data format |
| `references/strategies.md` | Hypothesis catalogue: insight ID → change, risk, pitfalls |
| `references/lessons.md` | What went wrong or right in real runs |
| `assets/lead-prompt.md` | Lead prompt, brief template, builder rules |
| `assets/critic-visual.md` | Blind same/different brief for the visual critic |
| `scripts/setup_tools.sh` | Installs tools into `.pageload/tools/`, checks Node and browser |
| `scripts/measure.mjs` | Interleaved Lighthouse runs, one fresh process each |
| `scripts/compare.py` | Noise floor, keep/reject decision, confirmation, log, insights |
| `scripts/visual_diff.mjs` | Screenshots, pixel diff with cluster check, blind pairs |
| `scripts/report.py` | `report.html` (self-contained) and `report.md` |

Dependencies: Node 22.19+ with `lighthouse@13`, `playwright@1`,
`pixelmatch@8`, `pngjs@7` (installed locally by `setup_tools.sh`), a Chrome
or Chromium (Playwright falls back to the installed Chrome), and Python 3.8+
with the standard library only.

# Checks

Test every instruction against these checks. Each check gives the signal, why it matters and the fix. Bracketed tags such as [E1] point to the evidence in evidence.md; cite them when the user asks why or pushes back.

## Contents

- How much to trust each check
- A. Best practice: A1 Holds only what the agent cannot work out, A2 Specific and checkable, A3 Gives the reason, A4 Commands and essentials present, A5 Length, order and limits, A6 Structure, A7 One source for CLAUDE.md and AGENTS.md, A8 Accurate, A9 No conflicts, A10 Scoped to where it applies, A11 Shared or personal, A12 Generated text never pruned, A13 Settings agree with the instructions, A14 Nested and shipped instruction files, A15 Required reads
- B. Content in the wrong place: B1 History and changelogs, B2 Prohibitions with no alternative, B3 Rules a tool should enforce, B4 Emphasis instead of reasons, B5 Time-sensitive state, B6 Content for humans, B7 Procedures that belong in a skill

## How much to trust each check

| Basis | Checks |
|---|---|
| Measured in studies of context files | A1 (overviews do not help), A4 (named commands and tools get used), A12 (LLM-written files cost more, gain nothing) |
| Vendor guidance, several vendors agree | A2, A5, A6, A9, A10, A11, A14, B3, B7 |
| Vendor guidance, one vendor or vendors disagree | A3, B2, B4 |
| Inference from the above | A13, A15, B1, B5, B6 |

State a finding with the confidence its basis supports. Do not present a heuristic (the 200-line target) as a measured threshold.

## A. Best practice

### A1. Holds only what the agent cannot work out
Signal: architecture overviews, directory trees, lists of dependencies, descriptions of the language or framework, summaries of the README, persona lines ("You are a senior engineer"), instructions any competent agent follows anyway ("write tests", "use meaningful names").
Why: the agent reads the repository itself. In a controlled study, repository overviews did not reduce the steps agents took to find the relevant files [E2], and files that mostly repeated existing docs added nothing [E4]. Anthropic now lists "describe your architecture and file layout" as retired advice [V3]. Every line costs attention in every session [V2].
Test: would the agent get this wrong without the line? If not, delete it.
Keep: conventions that differ from tool defaults, misleading code ("`utils/legacy.ts` looks unused but is loaded by name at runtime"), decisions not recorded in the repository, and anything the user has had to correct twice [V3, V5].
Before deleting a line that looks like layout, check that it is pure description. A layout line often carries a judgement ("public, and ship as they are" means: do not rewrite these files casually) or points to one specific file the agent would not find by listing the repository ("`tools/inventory.txt` lists every agent"). Keep those parts and delete only the description.
Note: Copilot and agents.md still suggest a short project overview [V3]. For an AGENTS.md read by several agents, a three-line overview of what is surprising is acceptable; a full tree is not.

### A2. Specific and checkable
Signal: "write clean code", "follow best practices", "be careful with the database", "keep functions small".
Why: the agent cannot act on a quality word, and nobody can check whether it was followed. All vendors agree [V1].
Fix: state the observable behaviour. "Format code properly" → "Run `npm run format` before committing". "Be careful with migrations" → "Create migrations with `npm run db:migration:new`; add a new migration instead of editing one already on main."

### A3. Gives the reason
Signal: a non-obvious rule with no "because". About three quarters of directives in real files give none [E14].
Why: a reason lets the agent apply the rule to cases it does not name, and see when it does not apply [V8]. Anthropic's example replaces "NEVER use ellipses" with the reason (the output is read by a text-to-speech engine).
Fix: add one clause. "Store timestamps in UTC; reports convert to the user's zone at render time."
Skip this for rules whose reason is obvious. Basis: Anthropic guidance; no study has measured the effect.

### A4. Commands and essentials present
Check for, and suggest adding when missing and verifiable from the repository:
- install, build, test, lint and type-check commands, exactly as they run, including how to run one test;
- project-specific tools the agent would not guess (`uv`, a custom CLI, a make target);
- directories that are generated and must not be edited;
- required services or environment, and how to start them;
- known traps.
Why: this is where the measured value of these files lies. Agents use a tool about 1.6 times per task when the file names it, and almost never when it does not [E3]. Anthropic calls the test command "the single most useful line" [V4]. Keep these commands even when a hook or CI also runs them, so the agent can check its own work [X1].

### A5. Length, order and limits
Signal: a root file over 200 lines (Claude Code's target, and it warns at startup [V-size]); a Cursor rule over 500 lines; AGENTS.md files whose combined size along the path exceeds 32 KiB (Codex stops reading at that point, so later files are silently dropped [V-size]); the most important rules placed late.
Why: adherence falls as instructions accumulate, mostly through omissions, and models favour earlier instructions [E8]; long input degrades reliability in general [E9]. These studies did not test instruction files directly, so treat the numbers as heuristics.
Fix: delete what fails A1; move area-specific content to path-scoped rules or nested files (A10); move procedures to skills (B7); put the rules that matter most first. `@path` imports load the whole file at startup, so they organise content but do not reduce its cost [V11].

### A6. Structure
Signal: long paragraphs, one rule hidden inside another, no headings.
Fix: short markdown headings by topic (Commands, Code style, Testing, Workflow), one rule per bullet, commands in code spans [V7].

### A7. One source for CLAUDE.md and AGENTS.md
Signal: both files exist with overlapping content (the scanner lists repeated lines), the two disagree, or both exist and CLAUDE.md does not import AGENTS.md.
Why: copies drift, and agents that read different files then behave differently. By default Claude Code reads AGENTS.md only when no CLAUDE.md exists in the directory or above, so an AGENTS.md next to a CLAUDE.md that does not import it is invisible to Claude (unless the user changed the "Project instructions" setting).
Fix: keep the shared instructions in AGENTS.md, which other agents read. Make CLAUDE.md import it with a line `@AGENTS.md`, followed only by Claude-specific instructions. A symlink also works but cannot hold Claude-only additions. If there is only an AGENTS.md, no CLAUDE.md is needed.

### A8. Accurate
Signal: scanner output for missing commands, paths and imports; references to tools or libraries no longer in the dependency files.
Why: the agent follows what the file names [E3], including commands that no longer exist.
Also check that an instruction to run something still matches what it does: read the script's usage text or header. "Run `rehearse.sh` before every push" is stale if the script's header describes a one-off migration.
Fix: correct or delete. Confirm each scanner hit by hand; a path may be an example or a pattern.

### A9. No conflicts
Signal: two lines that disagree (one says `pnpm`, another `npm run`), a nested file that contradicts the root one, or a project line that contradicts the user's `~/.claude/CLAUDE.md`.
Why: Anthropic: "if two instructions contradict each other, Claude may pick one arbitrarily"; user and project instructions do not override each other [V6, V10]. Codex and agents.md do let the nearer file win, so the same conflict behaves differently per agent.
Fix: keep one, or make the override explicit ("This package uses npm, unlike the rest of the repository").

### A10. Scoped to where it applies
Signal: a block that only matters for one directory or file type ("API handlers must...").
Fix: move it to `.claude/rules/<topic>.md` with `paths:` frontmatter, or to a nested CLAUDE.md or AGENTS.md in that directory; prefer the nested AGENTS.md when other agents need it too. All vendors offer scoping [V9]. Syntax is in enforcement.md, "Path-scoped rules".

### A11. Shared or personal
Signal: personal preferences in the committed file ("I like terse answers", a personal sandbox URL); response-style instructions, which Copilot also advises against [V-exclude]; team rules in a personal file; `CLAUDE.local.md` or `.claude/settings.local.json` not git-ignored (the scanner checks).
Fix: personal, per-project preferences go in `CLAUDE.local.md`; preferences across all projects go in `~/.claude/CLAUDE.md` [V12]. Both local files must be git-ignored: 1,379 secrets were found committed in `.claude/settings.local.json` files in public repositories [X-secrets]. Treat any secret in a committed file as urgent and recommend rotating it, since it is already in git history.

### A12. Generated text never pruned
Signal: text that reads like `/init` or template output: a full overview, a tree, a list of every script, generic advice, sections that match other repositories word for word.
Why: LLM-written files did not change success measurably but raised cost by 20-23% and added steps; developer-written files did about 7 points better [E1]. Anthropic: after `/init`, "the work is mostly removing lines" [V5].
Fix: apply A1 strictly to these sections; usually most of them go. Exception: in a repository with no other docs, generated content did help a little [E4].

### A13. Settings agree with the instructions
Signal: the scanner's "Allow rules that may contradict the instructions"; an allow rule for an action the file says needs a person (`gh pr merge` against "a person decides to merge"); a deny list or guard file that claims to mirror a document but does not; a hook that enforces something the file says is optional.
Why: when configuration and prose disagree, configuration wins in practice. An allow rule removes the prompt that would have given the person the decision the file promises; a deny list that half-mirrors its source blocks some spellings of a command and not others.
Fix: first apply the B3 test to the rule. If it passes (no exceptions, checkable, keeps being missed, or irreversible), the fix is code: a deny rule, hook or remote control that makes the rule hold, with the contradicting allow rule removed as part of it. Removing the allow rule alone is not enforcement: it only restores a prompt, and under auto mode or similar permission modes a prompt is not guaranteed. Only for a rule that fails B3, make the setting and the text agree, or write the exception down. Read both `.claude/settings.json` and `.claude/settings.local.json`. A finding in the local file affects only that user's sessions; say so, and ask before changing it, since it may be deliberate (an unattended run, for example). When a document says the settings mirror it, compare the two entry by entry and list each gap; check whether the document already explains an intended difference before reporting one. If a validator pins the settings to an exact list, the fix includes the validator edit; the pin is not a reason to leave the gap.

### A14. Nested and shipped instruction files
Signal: a CLAUDE.md or AGENTS.md below the root, especially under a templates, fixtures or examples folder (the scanner warns about these), or one that contradicts the root file.
Why: Claude Code loads a subdirectory's CLAUDE.md when it reads or edits a file in that directory, including whatever that CLAUDE.md imports. Name the exact way the file gets loaded: a template `CLAUDE.md` containing `@AGENTS.md` pulls in the template AGENTS.md, while a nested AGENTS.md alone is not read by Claude Code when the root has a CLAUDE.md (other agents may still read it). Reproduce it when that is cheap: read a file in the folder and see which instruction files the harness loads. A template meant for another project then enters the session as live instructions, and Claude may follow either set [V6]. Other agents load nested AGENTS.md files too [V10].
Also check whether the folder ships to users (release manifest, plugin packaging). If it does, the same files load in their projects too, beside their own instructions, so a Claude-only exclusion in this repository fixes only half the problem.
Fix: rename the files that cause the load so no agent loads them (`CLAUDE.md.tmpl`) and have the tool that copies them write the real name; this fixes shipped copies too. Size the rename by searching for the exact files renamed. For Claude Code only, `claudeMdExcludes` in settings stops the load in this repository (enforcement.md). Or add a line to the root file saying that files under that folder are material, not instructions. Count what the rename touches (scripts, manifests, tests that reference the path) before recommending it. Review a shipped template on its own terms only if the user asks; it is product, not this repository's instructions.

### A15. Required reads
Signal: "Before any work, read `X`", "Always read `X` first" (the scanner adds these to the per-session load).
Why: the instruction adds the whole of X to every session, including ones that do not need it. A long required read can cost more than the instruction file itself.
Fix: scope the read to the tasks that need it ("Before changing what a command does, read `docs/PHILOSOPHY.md`"), using the document's own statement of when it applies if it has one. If the read matters for behaviour the repository tests (replays, evaluations), run them after the change.

## B. Content in the wrong place

### B1. History and changelogs
Signal: "Changelog", "Recent changes" or "Updates" sections; dated entries; "we switched from Jest to Vitest in March"; "previously", "no longer", "was renamed".
Why: the agent needs the current state. History is derivable from git (A1), goes stale (vendors say to remove outdated rules [V6]), and can mislead: the agent may read an old pattern as an option. Basis: inference; no vendor names changelogs specifically.
Fix: delete it; git history, release notes and ADRs hold it. Keep a line only if old patterns still exist in the code and the agent might copy them, written as current state: "`tests/legacy/` still uses Jest. Write new tests with Vitest in `tests/`."

### B2. Prohibitions with no alternative
Signal: "don't", "never", "avoid" with no "instead", "use", "prefer".
Why: a bare prohibition removes one option and leaves the agent to guess the right one. Anthropic: "Tell Claude what to do instead of what not to do" [V-neg]; negated instructions have tested as less reliable, mostly in older models [E11]. Gemini, by contrast, recommends specific negative constraints over vague positive ones [V-neg]. Both agree on specificity, so keep the constraint and add the alternative.
Fix: state the alternative, then the excluded option and the reason.
- "Don't use axios." → "Use `fetchJson` from `src/lib/http.ts` for HTTP calls instead of axios; it adds auth headers and retries."
- "Never use `any`." → "Type unknown input as `unknown` and narrow it with the zod schemas in `src/schemas/`." (Also B3: a lint rule enforces this.)
- "Don't create new utility files." → "Add shared helpers to the module in `src/lib/` that matches the topic; create a new file only for a new topic."
A plain prohibition is fine when the alternative is to do nothing, but check B3 first.

### B3. Rules a tool should enforce
Move a rule to a tool when any of these hold [X1]:
1. **No exceptions.** It must happen every time, or never. Anthropic: "If something has to happen every time, make it a hook, a deny rule, or a managed setting. CLAUDE.md is for guidelines, and Claude is allowed to decide a guideline doesn't apply."
2. **A program can check it.** Formatting, lint rules, types, tests, secret patterns. "Never send an LLM to do a linter's job."
3. **It keeps being missed.** Emphasis added to the line (B4) is the sign: "If you keep adding emphasis to a CLAUDE.md line and Claude still misses it, that's a sign the line belongs in a hook."
4. **Breaking it is irreversible or costly**: shared git history, data loss, leaked secrets. Here add a control outside the agent too (branch protection, scoped credentials), because agent-side controls can be bypassed [X-bypass] and documented incidents happened despite instructions [X-incidents].
Typical lines: "never push to main", "never force push", "never read `.env`", "don't touch `generated/`", "don't run migrations against production", formatting and style rules, "always run tests before finishing".
Keep as instructions: preferences with exceptions ("prefer named exports"), architecture and naming guidance, when to ask versus proceed, scope discipline. Turning these into hooks blocks legitimate work; keep the enforced set small [X1]. That counter-rule is about preferences: it never argues against enforcing a rule with no exceptions whose breach cannot be undone.
Partial coverage: when one mechanism covers part of a rule (push protection stops a committed secret but not a printed one), look for code for the rest before leaving it to prose, starting with hooks and scripts the repository already has or ships to others.
Fix: pick the mechanism from enforcement.md and give the exact snippet. What stays in the file: nothing for a pure prohibition, the command for a check the agent should run itself (A4), or one line naming the workflow ("Work on a feature branch and open a pull request").

### B4. Emphasis instead of reasons
Signal: IMPORTANT, CRITICAL, MUST, NEVER, ALWAYS in capitals, repeated emphasis, "!!".
Why: Anthropic retired this advice: "Current [models] follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule" [V-emph]. Emphasis also marks a rule that failed before, which is better fixed by a reason (A3) or a tool (B3).
Fix: plain wording plus the reason; if the rule meets the B3 test, move it to a tool.

### B5. Time-sensitive state
Signal: "currently", "for now", "temporarily", "until we finish", TODO lists, open bugs, sprint goals.
Why: the line goes stale silently and then misleads (V6).
Fix: move work in progress to the issue tracker or a plan file. If the agent must know a temporary constraint, state it as a fact with a way to check it: "The payments API is mocked in `src/mocks/payments.ts` while the sandbox is down; check that file before calling the real API."

### B6. Content for humans
Signal: project pitch, contributor etiquette, onboarding prose, setup steps copied from the README, links to wikis with no instruction.
Fix: leave it in the README or CONTRIBUTING file. If the agent needs part of it, point to it with a sentence saying when to read it ("Before changing the release process, read `docs/releasing.md`") instead of copying it [V11].

### B7. Procedures that belong in a skill
Signal: a long step-by-step procedure for one task (release, adding an endpoint, writing a migration).
Why: it loads in every session but is used in few [V9].
Fix: move it to a skill in `.claude/skills/<name>/SKILL.md`, which loads only when the task comes up.

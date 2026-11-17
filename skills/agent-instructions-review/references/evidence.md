# Evidence

The sources behind checks.md, gathered on 17 November 2026. Cite an entry when the user asks why a finding matters. Studies (E) are measured; vendor guidance (V) and enforcement sources (X) are documented positions or incidents. Where a source has a limit, it is noted.

## Contents

- E. Studies
- V. Vendor guidance
- X. Enforcement, bypasses and incidents

## E. Studies

- **E1.** Gloaguen et al., ETH, Feb 2026, https://arxiv.org/abs/2602.11988. Tested Claude Code, Codex and Qwen Code on SWE-bench Lite (300 tasks) and AGENTbench (138 tasks). LLM-written context files changed success by -0.5% and -2%, and developer-written ones by +2.4% (p=0.21). None of these changes is significant. Developer-written files beat LLM-written ones by about 7 points. LLM-written files raised cost by 20-23% and added 2.5-3.9 steps per task.
- **E2.** Same study: 95-100% of LLM-written files contain a repository overview, and the overviews did not meaningfully reduce the steps taken to reach the relevant files.
- **E3.** Same study: agents follow what the file names. A tool named in the file was used 1.6 times per task, against under 0.01 when it was not named. Repository-specific tools: 2.5 times against under 0.05.
- **E4.** Same study: once the repositories' docs were removed, LLM-written files improved success by 2.7%. The authors conclude that the files are useful for "non-standard coding practices".
- **E5.** Lulla et al., Jan 2026, https://arxiv.org/abs/2601.20404. An AGENTS.md cut runtime by 28.6% and output tokens by 16.6% across 124 pull requests, with completion unchanged. This conflicts with E1 on cost; the setups differ.
- **E6.** Khatri, REALM 2026, https://arxiv.org/abs/2607.27250. No measurable effect on correctness: 2 agents, 17 tasks, 288 runs. The sample is small.
- **E7.** Shepard & Albrecht, Jun 2026, https://arxiv.org/abs/2606.20512. Guidance refined against test probes resolved 33.0% of tasks, against 28.3% for static guidance and 25.5% for none. The gain came from reaching the right files.
- **E8.** IFScale, NeurIPS 2025, https://arxiv.org/abs/2507.11538. Adherence falls as the number of instructions grows: the best models stay at 98-99% at 100 instructions and drop to 62-69% at 500. Most errors are omissions, and models favour earlier instructions. The task was keyword inclusion, not coding.
- **E9.** Chroma, "Context rot", https://www.trychroma.com/research/context-rot. Reliability falls with input length across 18 models. This is a vendor report, not peer-reviewed.
- **E10.** Liu et al., "Lost in the middle", TACL 2024. Information in the middle of the context is used least. The models tested are older, and newer ones show the effect less.
- **E11.** Jang et al., 2022, https://arxiv.org/abs/2209.12711. Larger models handled negated prompts worse; the models tested are old. Also https://arxiv.org/abs/2511.12381 (Nov 2025), which reports that stating the wanted behaviour reduces forbidden output under load; we saw only a summary of this one.
- **E12.** https://arxiv.org/abs/2511.12884. A survey of 2,303 context files: median length 485-535 words. Files grow mostly by addition and rarely lose lines.
- **E13.** https://arxiv.org/abs/2509.14744. In 253 CLAUDE.md files, 77% contain build or run commands and 65% describe the architecture.
- **E14.** https://arxiv.org/abs/2610.31715, Oct 2026, single author. Covers 22,854 repositories. Median file length is 818 words. 74% of directives give no reason. About a third show text from generators or templates.

## V. Vendor guidance

Sources:
- CC-MEM https://code.claude.com/docs/en/memory
- CC-BP https://code.claude.com/docs/en/best-practices
- PE https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- AG https://agents.md/
- CX https://learn.chatgpt.com/docs/agent-configuration/agents-md
- GH https://docs.github.com/en/copilot/concepts/prompting/response-customization
- GH-REPO https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- CU https://cursor.com/docs/context/rules
- GM https://geminicli.com/docs/cli/tutorials/memory-management

Entries:
- **V1. Concrete instructions.** CC-MEM: "Use 2-space indentation" rather than "Format code properly". CU: "Avoid vague guidance." GM: "Keep instructions actionable."
- **V2. Short files.** CC-BP: "every line in it takes a little of Claude's attention on every task". GH: "short, self-contained statements".
- **V3. Only what the agent cannot work out.** CC-BP: the file "only holds what Claude couldn't work out from the code itself". The same page lists "Describe your architecture and file layout" as retired advice ("Claude reads the repo itself"). CU: avoid "Duplicating what's already in your codebase". Copilot's sample prompt and agents.md still suggest an overview and a layout.
- **V4. Commands.** CC-BP: the test command is "the single most useful line in your CLAUDE.md". AG: agents run the checks you list.
- **V5. Add rules after repeated mistakes.** CC-MEM: add a rule when "Claude makes the same mistake a second time". CC-BP: keep "anything you've had to correct twice". On `/init`, CC-BP: "the work is mostly removing lines". CU: "Add rules only when you notice Agent making the same mistake repeatedly."
- **V6. Remove conflicts and outdated rules.** CC-MEM: "if two instructions contradict each other, Claude may pick one arbitrarily". GM: "Periodically check your GEMINI.md files to remove outdated rules."
- **V7. Structure.** CC-MEM: "Organized sections are easier for Claude to follow than dense paragraphs."
- **V8. Reasons.** PE: "Providing context or motivation behind your instructions... Claude can generalize from the explanation."
- **V9. Scoping.** CC-MEM: procedures go in skills, and rules for one area go in `.claude/rules/` with `paths:`. Copilot: `.github/instructions/*.instructions.md` with `applyTo`. CU: rules that apply to specific files. CX: nested AGENTS.md files.
- **V10. Precedence.** AG: "The closest AGENTS.md to the edited file wins." CX: closer files appear later and override. CC-MEM: user and project instructions do not override each other, and "Claude may follow either one".
- **V11. Point, don't copy.** CU: give "referenced files". CC-MEM: `@path` imports "don't reduce its context cost". GH warns that references to external resources may cause problems in large repositories.
- **V12. Personal preferences.** CC-BP: personal preferences go in `CLAUDE.local.md`, which is git-ignored.
- **V-size. Size limits.**
  - CC-MEM: "target under 200 lines per CLAUDE.md file"; Claude Code warns at startup when a file is over that length.
  - CU: "Keep rules under 500 lines".
  - CX: `project_doc_max_bytes` defaults to 32 KiB across all instruction files combined, and later files are dropped.
  - agents.md and Gemini give no number.
- **V-exclude. Content to leave out.**
  - GH: response-style and response-length instructions.
  - CU: "Copying entire style guides: Use a linter instead", "Documenting every possible command", rare edge cases.
  - CC-MEM: `/doctor` cuts directory layouts, dependency lists and architecture overviews.
- **V-neg. Negative phrasing.** PE: "Tell Claude what to do instead of what not to do." GM: "Use negative constraints... often more effective than vague positive instructions." The two partly conflict; both prefer specific wording.
- **V-emph. Emphasis.** CC-BP retires "Add IMPORTANT or ALL CAPS" with this explanation: "Current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule." PE: use "more normal prompting" in place of "CRITICAL: You MUST".

## X. Enforcement, bypasses and incidents

- **X1. When to use a tool.** CC-BP: "If something has to happen every time, make it a hook, a deny rule, or a managed setting." CC-BP: "If you keep adding emphasis to a CLAUDE.md line and Claude still misses it, that's a sign the line belongs in a hook." CC-BP keeps "Prefer named exports" as an instruction because it has exceptions, and adds: "If you ever find yourself at forty of them, most are probably preferences." HumanLayer, https://www.humanlayer.dev/blog/writing-a-good-claude-md: "Never send an LLM to do a linter's job." Evil Martians, https://evilmartians.com/chronicles/stop-writing-rules-in-agents-md-use-agent-hooks-and-nano-staged-instead: automation beats documentation. `prompt` and `agent` hooks are not deterministic; use `command` hooks for enforcement.
- **X-bypass. Ways around agent-side controls.** From https://code.claude.com/docs/en/permissions:
  - Bash deny rules match the command text, so they miss full paths, `sh -c`, variables, and runners such as `npx` and `docker exec`.
  - `Read` deny rules cover the built-in tools and the shell file commands Claude Code recognises, but miss `grep -r` and scripts that open files themselves.
  - The sandbox, https://code.claude.com/docs/en/sandboxing, covers only Bash and the processes it starts.
  - Hooks fail open by default in Cursor (`failClosed` changes that). Codex's docs: "Treat tool hooks as a useful guardrail, not a complete enforcement boundary."
  - Claude Code hooks do not apply when another agent works in the repository. Only controls outside the agent (branch protection, CI required checks, scoped credentials) cover every path.
- **X-incidents. Incidents.**
  - Replit, July 2025: the agent deleted a production database during an all-caps "code freeze" instruction. https://incidentdatabase.ai/cite/1152/
  - PocketOS, 2026: the agent found a token and deleted a volume and the backups stored inside it. Separate credentials and backups kept outside the volume would have prevented it.
  - Pushes to protected branches despite CLAUDE.md: anthropics/claude-code issues #48474, #78544, #58079 and #67060.
  - Destructive git operations: issues #17908 and #33391.
  - No enforcement for instruction compliance: issue #53223.
  - Cost of over-enforcing: issue #87996, where a hard-coded "never merge" rule blocked merges that the repository's own CLAUDE.md required.
- **X-secrets. Leaked secrets.** Apiiro, Nov 2026: 1,379 secrets in `.claude/settings.local.json` files committed to 1,122 public repositories. https://thehackernews.com/2026/11/claude-codes-dont-ask-again-file.html. GitGuardian reports a secret-leak rate of 3.2% for commits co-authored by Claude Code, against 1.5% overall. https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/
- **Hook equivalents in other agents.** Cursor https://cursor.com/docs/hooks. Codex https://learn.chatgpt.com/docs/hooks. Copilot `.github/hooks/hooks.json`. Gemini CLI BeforeTool hooks https://geminicli.com/docs/hooks/reference/.

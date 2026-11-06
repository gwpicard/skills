---
name: organize-directory
description: >
  Interactively analyzes any directory and helps organize it through a
  scan, propose, and apply workflow. Use when the user says "organize my
  folder", "clean up my Downloads", "sort this directory", "tidy up my
  desktop", "organize these files", "restructure my projects folder", or
  points at a directory (Downloads, Desktop, invoices, projects, media) and
  wants help deciding how to structure it. Classifies the directory, proposes
  a taxonomy, asks before changing anything, and applies changes reversibly
  with dry-run, copy-verify-delete, quarantine-not-delete, and an undo script.
  Do NOT use for organizing code inside a single project (refactoring),
  cleaning up git history or version control, or cloud-only storage the local
  filesystem cannot see.
argument-hint: "[directory]"
allowed-tools: Read, Glob, Grep
---

# Organize Directory

Help the user organize a directory through three gated phases. The model
supplies judgment (classification, taxonomy, conversation); bundled scripts do
the deterministic and fragile work (scanning, hashing, moving, undo). Never
move or delete files by hand with `mv`/`rm` — always go through `apply.py`, so
every change is previewed, reversible, and logged.

## Critical guardrails (always)

- **Dry-run before commit.** `apply.py` previews by default. Show the preview and
  get explicit confirmation before running with `--commit`.
- **Never delete during a run.** Junk and duplicates are *quarantined* into
  `_REVIEW/`. Emptying it is a separate, explicitly-confirmed step.
- **Reversible.** Every commit writes `_organize-undo-<id>.sh` before touching
  files, and `_organize-summary-<id>.md` after. Tell the user how to undo.
- **Copy-verify-delete across volumes; atomic rename within one.** `apply.py`
  handles this automatically — no data is deleted until a copy is byte-verified.
- **Protected paths are skipped:** `.git`, `node_modules`, project roots,
  symlinks, hidden files, and files modified today. Do not reorganize the
  insides of a recognized project or repo — move it as a unit if at all.
- **Stay in the target.** All destinations must resolve inside the target dir;
  `apply.py` refuses anything that escapes it.
- **One directory at a time.** Confirm the target path before scanning.

## Phase 1 — Scan and classify (read-only)

Classify **before** committing to an expensive scan — a full content-hashing
walk of a workspace full of repos is slow and pointless when the useful unit is
the top-level folders. So go shallow first, then deepen only if warranted.

1. Confirm the absolute target path with the user.
2. **Shallow pass (instant) — classify first:**
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/scan.py "<target>" --max-depth 1 --no-dedup --out "${TMPDIR:-/tmp}/organize-inventory.json"
   ```
   Read that inventory. (Working files go to a temp dir, not the target, so the
   scan never sees its own output.) Classify the directory into one of: `inbox`
   (Downloads/Desktop dumps), `projects` (workspaces), `documents`
   (invoices/receipts/reference), `media` (photos/video), or `mixed`. The class
   drives the recommended taxonomy — see
   [references/philosophies.md](references/philosophies.md).
3. **Choose scan depth from the class — do not blindly deep-scan:**
   - `projects` (or a high `project_roots` flag count): stay shallow. Each
     project root is an atomic unit — the scan already skips inside them, and
     you organize *at the top level* (grouping/archiving project folders,
     handling loose files), never reshuffling files inside a repo. The
     `--max-depth 1 --no-dedup` inventory above is usually all you need.
   - `media`: a deeper pass with dedup is valuable (find duplicate photos).
     Re-run without `--max-depth`; keep the dedup budget so it can't hang:
     `scan.py "<target>" --out ...` (defaults: `--max-hash-files 5000`,
     `--time-budget 60`; add `--no-dedup` to skip byte-reading entirely).
   - `inbox` / `documents` / `mixed`: a full pass is fine; these are usually
     small. Re-run without `--max-depth` if the shallow view isn't enough.
4. Respect the guard rails in the inventory: the `notes` array flags when dedup
   was skipped, capped, or partial — relay that to the user rather than
   claiming a complete duplicate report. `flags.project_roots` lists the
   atomic units.
5. Summarize what's there in plain language: counts by category, age spread,
   duplicate clusters and reclaimable space, and flags (project roots, repos,
   junk, large files). Surface anything surprising.

## Phase 2 — Propose and interrogate (no file changes)

1. Recommend a **primary axis** and **secondary axis** based on the class,
   and state the tradeoff (see philosophies reference). Show a concrete
   proposed before/after tree using real files from the inventory.
2. Use `AskUserQuestion` for the real forks — do not guess:
   - Primary organizing axis (purpose / project / type / date / vendor)?
   - Archive threshold (e.g. move items untouched > 12 months to `_Archive`)?
   - Rename files to a convention, or keep original names?
   - Duplicates: quarantine all-but-one, or leave?
   - Suspected junk: quarantine, or ignore?
   - Anything to protect / leave exactly where it is?
3. Write the agreed decisions into a plan file at
   `${TMPDIR:-/tmp}/organize-move-plan.json`
   following [references/plan-schema.md](references/plan-schema.md). Every entry
   needs a `reason`. Paths are relative to the target. Files only — never list a
   directory as a `src`.

## Phase 3 — Apply (gated, reversible)

1. **Preview first:**
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/apply.py --plan "${TMPDIR:-/tmp}/organize-move-plan.json"
   ```
   Show the user the counts, any collisions, and any skipped problem entries.
2. On explicit confirmation, **commit:**
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/apply.py --plan "${TMPDIR:-/tmp}/organize-move-plan.json" --commit
   ```
   Report moved/skipped/failed counts and how to undo. For speed on large media
   with no cross-volume moves, `--verify size` is acceptable; default `hash` is
   safer when copies cross volumes.
3. **Quarantine cleanup is separate.** Only if the user asks to reclaim space,
   and only after they review `_REVIEW/`:
   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/empty-quarantine.py "<target>"           # list
   python3 ${CLAUDE_SKILL_DIR}/scripts/empty-quarantine.py "<target>" --confirm # to Trash
   ```

## Choosing and blending an organization

Treat organization as composable axes (primary partition, secondary partition,
orthogonal archive axis, orthogonal naming convention, optional numbering
overlay) rather than one rigid method. Recommend a default blend per directory
class, explain the tradeoff, and let the user override. Full guidance and the
PARA / Johnny Decimal / by-type / by-date tradeoffs are in
[references/philosophies.md](references/philosophies.md).

## If something looks risky

Stop and ask when you hit: an ambiguous target, a directory that is mostly one
project or repo, sensitive documents (financial/identity — quarantine to
`_REVIEW/sensitive/` rather than relocating silently), or a plan that would move
thousands of files at once (offer to do a representative subset first).

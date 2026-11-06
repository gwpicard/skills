# Organizing philosophies and how to blend them

## Table of contents
- [The core idea: composable axes](#the-core-idea-composable-axes)
- [The five axes](#the-five-axes)
- [Per-class default blends](#per-class-default-blends)
- [The named methods, and where each fits](#the-named-methods-and-where-each-fits)
- [Renaming conventions](#renaming-conventions)
- [Tradeoffs to voice to the user](#tradeoffs-to-voice-to-the-user)

## The core idea: composable axes

Do not pick one philosophy globally. Organization is a set of orthogonal axes
that layer. Pick a **primary** and **secondary** partition from the directory's
class, apply the archive and naming axes on top, and only add a numbering
overlay if the user wants stable addresses.

## The five axes

1. **Primary partition** — the top-level split. One of: `purpose` (PARA-style),
   `project`, `type` (file category), `date`, `vendor/entity`.
2. **Secondary partition** — within each top folder, usually a *different* axis
   than the primary (e.g. primary `vendor`, secondary `year`).
3. **Archive axis** — orthogonal, cuts across everything: active vs. archived by
   recency. Implemented as an `_Archive/` mirror or a `> N months` threshold.
4. **Naming convention** — orthogonal, applies regardless of location. E.g.
   `YYYY-MM-DD_vendor_description.ext`. See below.
5. **Numbering overlay (optional)** — Johnny Decimal (`12.03 Name`) for people
   who want a stable "address" per folder. Sits on top of any primary axis.

## Per-class default blends

Recommend these as a starting point, then let the user adjust.

| Class | Primary -> Secondary | Archive | Rename? | Notes |
|---|---|---|---|---|
| **inbox** (Downloads/Desktop) | `type` -> `date` | old installers & temp -> `_REVIEW`; stale -> `_Archive` | screenshots only | Treat as a queue to empty. Dedupe aggressively. |
| **projects** | `project` -> `type` | stale projects -> `_Archive` | usually no | Never atomize a project/repo; move as a unit. |
| **documents** (invoices/receipts) | `vendor` or `type` -> `year` | by year | **yes** | Content-based, never by extension. Rename to convention. |
| **media** | `date`/event -> — | by year | optional | Group same-event photos under `YYYY/MM-Event/`. |
| **mixed** | `purpose` (PARA) -> per-area axis | `_Archive` area | selective | First separate the classes, then apply each class's blend. |

## The named methods, and where each fits

- **By type / extension** — simplest, shallow. Good default *secondary* axis;
  good *primary* only for a pure inbox. Fast but tells you nothing about meaning.
- **By content / semantic** — read what's inside (PDF text, image subject) and
  group by topic. The AI-native strength. Best for documents and mixed dumps.
- **By project** — group everything for one project together. Best primary axis
  for workspaces; protect recognized roots (`.git`, `node_modules`, etc.).
- **By date** — `YYYY/MM/`. Best primary for media; best secondary for invoices
  and archives.
- **PARA** (Projects, Areas, Resources, Archive) — a *primary-axis* choice for
  whole-life or mixed directories. Maps to four top folders by actionability.
- **Johnny Decimal** — a *numbering overlay*, not a competitor to PARA. Adds
  `AC.ID` addresses (<=10 areas x <=10 categories). Use only if the user wants
  fixed, memorable locations. You can describe an existing JD scheme in natural
  language and file into it.
- **Archive-everything-old** — the archive axis made primary intent: mirror the
  active tree into `_Archive/` by timeframe, run periodically.

PARA and Johnny Decimal combine cleanly: `10 Projects / 20 Areas / 30 Resources
/ 40 Archive`, JD numbers giving PARA stable addresses.

## Renaming conventions

Only rename when it adds durable value (documents, screenshots). Good defaults:
- Documents: `YYYY-MM-DD_vendor_description.ext`
- Screenshots: `YYYY-MM-DD_HHMM_screenshot.png`
- Keep it short, no spaces or special chars, lowercase where reasonable.
- Always record original -> new in the plan `reason` so nothing is lost.

## Tradeoffs to voice to the user

- **Type vs. project/content:** type is instant and predictable but scatters
  related things; content/project keeps context together but relies on the
  model's judgment (and is occasionally wrong — hence dry-run and undo).
- **Deep vs. flat:** deep taxonomies (JD) are precise but high-maintenance; flat
  ones are forgiving but get cluttered.
- **Rename vs. preserve:** renaming makes files findable but breaks existing
  links/bookmarks. Prefer preserve unless the names are genuinely useless.
- **There is no single best method** — it depends on how the user actually
  retrieves things. When unsure, ask how they *look for* files today.

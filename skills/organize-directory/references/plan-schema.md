# move-plan.json schema

The model writes this file in Phase 2. `apply.py` reads it in Phase 3. It is the
single interface between judgment (the model) and execution (the script): if it
is not in the plan, it does not happen.

## Schema

```json
{
  "target": "/absolute/path/to/directory",
  "mkdirs": ["Documents", "Images/2025", "_REVIEW/duplicates"],
  "moves": [
    {
      "src": "scattered file.pdf",
      "dst": "Documents/scattered file.pdf",
      "action": "move",
      "reason": "PDF report; grouped under Documents"
    },
    {
      "src": "invoice1.pdf",
      "dst": "Invoices/Acme/2025-03-14_acme_invoice.pdf",
      "action": "move",
      "reason": "invoice from Acme; renamed to convention"
    },
    {
      "src": "screenshot copy.png",
      "dst": "_REVIEW/duplicates/screenshot copy.png",
      "action": "quarantine",
      "reason": "exact duplicate of Images/screenshot.png"
    }
  ]
}
```

## Rules

- **`target`** — absolute path. Must match the directory that was scanned.
- **`src` / `dst`** — RELATIVE to `target`. Both must resolve inside `target`;
  `apply.py` refuses anything that escapes it.
- **`src` is always a file**, never a directory. To relocate a whole project or
  folder as a unit, list it as a single move only if it is a file; otherwise
  leave folders in place (do not descend and scatter their contents).
- **`action`**:
  - `move` — normal relocation into the new taxonomy.
  - `quarantine` — send junk/duplicates/sensitive items into `_REVIEW/...`.
    Never delete; deletion is a separate confirmed step.
- **`reason`** — required, short. For renames, note the original name so the
  audit trail preserves it.
- **`mkdirs`** — folders to create first. `apply.py` also creates parent dirs on
  demand, but listing them makes the intended structure explicit and reviewable.
- **No two moves may target the same `dst`.** `apply.py` reports this as a
  problem and refuses to commit until fixed.
- **Collisions with existing files** are never overwritten; by default a
  numeric suffix is added. Prefer choosing non-colliding `dst` paths yourself.

## Good practices

- Keep destinations shallow and predictable; mirror the tree you showed the user
  in the Phase 2 preview.
- Put every duplicate cluster's "keeper" as a normal `move` (or leave in place)
  and only the redundant copies as `quarantine`.
- For sensitive documents, quarantine to `_REVIEW/sensitive/` rather than
  filing them into a shared folder silently.

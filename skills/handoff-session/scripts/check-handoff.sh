#!/usr/bin/env bash
# Lint a written handoff document before handing over the prompt.
#
# The skill's own rules are easy to state and easy to skip under context
# pressure, which is exactly when a handoff gets written. This checks the four
# that fail silently (plus a length warning):
#
#   - a secret written into the document. It lives in ~/.claude/plans/, outside
#     any repo's .gitignore, and the next session reads it verbatim.
#   - a missing delete-header, so the handoff is never cleaned up and a stale
#     one is later read as current.
#   - an empty heading, i.e. template structure manufactured for a session that
#     had nothing to put in it.
#   - a repo path that does not exist, which sends the next session hunting.
#
# With --record (a conversation handoff kept as the user's record, not a
# session snapshot) the delete-header and repo-path checks are skipped.
#
# Read-only. Exit 0 clean, 1 failures found, 2 could not read the file.

set -uo pipefail

usage() {
  cat <<'USAGE'
usage: check-handoff.sh [--record] <path-to-handoff.md>

Lints a written handoff document. Read-only.

  --record   conversation handoff: skip the delete-on-pickup header and
             repo-path checks (the document is a durable record)
  -h, --help show this help

Exit codes: 0 clean (warnings allowed), 1 failures to fix, 2 bad usage or
unreadable file.
USAGE
}

record=0
file=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --record) record=1 ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) file=$1 ;;
  esac
  shift
done

if [ -z "$file" ]; then
  usage >&2
  exit 2
fi
if [ ! -f "$file" ]; then
  echo "no such file: $file" >&2
  exit 2
fi

fails=0
warns=0

fail() { printf 'FAIL  %s\n' "$1"; fails=$((fails + 1)); }
warn() { printf 'WARN  %s\n' "$1"; warns=$((warns + 1)); }
pass() { printf 'ok    %s\n' "$1"; }

# --- secrets ----------------------------------------------------------------
# Shapes, not entropy. A false positive costs a glance; a miss publishes a key.

secret_hits=$(grep -nEi \
  -e 'sk-[A-Za-z0-9_-]{16,}' \
  -e '(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}' \
  -e 'github_pat_[A-Za-z0-9_]{20,}' \
  -e 'AKIA[0-9A-Z]{16}' \
  -e 'xox[baprs]-[A-Za-z0-9-]{10,}' \
  -e 'Bearer[[:space:]]+[A-Za-z0-9._-]{20,}' \
  -e '(api[_-]?key|apikey|auth[_-]?token|access[_-]?token|secret|password|passwd)[[:space:]]*[=:][[:space:]]*[^[:space:]"'"'"'`]{12,}' \
  -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' \
  "$file" 2>/dev/null)

if [ -n "$secret_hits" ]; then
  fail "possible secret in the document — check these lines and replace the value with the variable that holds it:"
  printf '%s\n' "$secret_hits" | sed 's/^/        /'
else
  pass "no secret-shaped strings"
fi

# --- delete header ----------------------------------------------------------

if [ "$record" -eq 1 ]; then
  pass "delete-on-pickup header not required (--record)"
elif head -3 "$file" | grep -qi 'delete this file'; then
  pass "delete-on-pickup header present"
else
  fail "no delete-on-pickup header in the first 3 lines — the next session will leave this file behind"
fi

# --- empty headings ---------------------------------------------------------
# A heading whose next non-blank line is another heading, or end of file.
# Structure invented for a section the session had nothing to say about.

empty=$(awk '
  /^#{2,}[[:space:]]/ {
    if (pending != "") printf "%d: %s\n", pendingline, pending
    pending = $0; pendingline = NR; next
  }
  /^[[:space:]]*$/ { next }
  { pending = "" }
  END { if (pending != "") printf "%d: %s\n", pendingline, pending }
' "$file")

if [ -n "$empty" ]; then
  fail "empty heading(s) — drop the section rather than leaving the heading:"
  printf '%s\n' "$empty" | sed 's/^/        /'
else
  pass "no empty headings"
fi

# --- repo path --------------------------------------------------------------
# Not hypothetical: a project that moves leaves every earlier handoff pointing
# at a directory that is gone.

repo_line=$(grep -m1 -E '^[[:space:]]*(\*\*)?Repo:' "$file" 2>/dev/null)
if [ "$record" -eq 1 ] && [ -z "$repo_line" ]; then
  pass "no repo path to check (--record)"
elif [ -z "$repo_line" ]; then
  warn "no 'Repo:' line found — the next session has to work out where it is"
else
  repo=$(printf '%s' "$repo_line" | sed -E 's/.*`([^`]+)`.*/\1/')
  repo=${repo/#\~/$HOME}
  if [ "$repo" = "$repo_line" ]; then
    warn "could not parse the repo path out of: $repo_line"
  elif [ -d "$repo" ]; then
    pass "repo path exists: $repo"
  else
    fail "repo path does not exist: $repo"
  fi
fi

# --- size -------------------------------------------------------------------

lines=$(wc -l < "$file" | tr -d ' ')
limit=250
[ "$record" -eq 1 ] && limit=600
if [ "$lines" -gt "$limit" ]; then
  warn "$lines lines — long enough to be a narrative of the session. Cut anything re-derivable from git log or the repo's own docs."
else
  pass "$lines lines"
fi

# ----------------------------------------------------------------------------

echo
if [ "$fails" -gt 0 ]; then
  echo "$fails to fix, $warns to consider — fix the failures before printing the prompt."
  exit 1
fi
if [ "$warns" -gt 0 ]; then
  echo "clean — $warns to consider."
else
  echo "clean."
fi
exit 0

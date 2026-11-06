#!/usr/bin/env bash
# Dump the machine-checkable half of a handoff: git, PRs, issues, plan files.
#
# The point is to MEASURE state rather than recall it. Recalled state is the
# main way a handoff misleads — a SHA or PR number that was true forty minutes
# ago sends the next session looking for something that no longer exists.
#
# Everything here is read-only and fast (seconds). Never runs a test suite:
# that can take minutes and can fail for environment reasons unrelated to the
# work. Report the last measured count from the session instead, with when.

set -uo pipefail

say() { printf '\n=== %s ===\n' "$1"; }

root=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "not a git repository — write a conversation handoff (see SKILL.md), nothing to measure"
  exit 0
}
cd "$root" || exit 0
project=$(basename "$root")

echo "project: $project"
echo "root:    $root"

say "branch and HEAD"
echo "branch: $(git branch --show-current 2>/dev/null || echo '(detached)')"
git log -1 --format='HEAD:   %h %s' 2>/dev/null

say "working tree"
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "uncommitted files: $dirty"
[ "$dirty" != "0" ] && git status --short 2>/dev/null | head -20

git fetch origin --quiet 2>/dev/null
if git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  echo "vs upstream (ahead behind): $(git rev-list --left-right --count '@{upstream}...HEAD' 2>/dev/null)"
fi

say "recent commits on the default branch"
default=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)
git log --oneline "$default" -10 2>/dev/null || git log --oneline -10

# --- GitHub, if this repo has it and gh is authenticated --------------------

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  say "open pull requests"
  gh pr list --json number,title,headRefName --limit 20 \
    --jq '.[] | "#\(.number)  \(.headRefName)  — \(.title)"' 2>/dev/null \
    || echo "(none, or not a GitHub remote)"

  # CI state per open PR: the single most perishable fact in a handoff, so it
  # is worth deriving properly. Roll the whole check set up into one verdict —
  # reading the first check's status reports one job as if it were the PR, and
  # a repo with no CI at all must say so rather than "unknown", which reads as
  # a failed lookup and sends the next session to go and check by hand.
  ci_filter='def norm: if (.conclusion // "") != "" then .conclusion elif (.state // "") != "" then .state else (.status // "UNKNOWN") end;
.statusCheckRollup
| if length == 0 then "no checks configured"
  else [ .[] | norm ] as $s
  | ($s | map(select(. == "FAILURE" or . == "TIMED_OUT" or . == "ACTION_REQUIRED" or . == "ERROR" or . == "CANCELLED")) | length) as $bad
  | ($s | map(select(. == "PENDING" or . == "QUEUED" or . == "IN_PROGRESS" or . == "EXPECTED" or . == "WAITING")) | length) as $wait
  | ($s | length) as $n
  | if $bad > 0 then "FAILING (\($bad) of \($n))" elif $wait > 0 then "pending (\($wait) of \($n) still running)" else "passing (\($n))" end
  end'

  for n in $(gh pr list --json number --jq '.[].number' 2>/dev/null); do
    status=$(gh pr view "$n" --json statusCheckRollup --jq "$ci_filter" 2>/dev/null)
    echo "  #$n CI: ${status:-could not read}"
  done

  say "recently merged"
  gh pr list --state merged --limit 10 --json number,title \
    --jq '.[] | "#\(.number)  \(.title)"' 2>/dev/null

  say "open issues"
  gh issue list --state open --limit 40 --json number,title \
    --jq '.[] | "#\(.number)  \(.title)"' 2>/dev/null | sort -t'#' -k2 -n

  say "next free issue number"
  # Issues and PRs share one number space, so check both.
  hi=$( { gh issue list --state all --limit 1 --json number --jq '.[0].number' 2>/dev/null
          gh pr list --state all --limit 1 --json number --jq '.[0].number' 2>/dev/null
        } | sort -n | tail -1 )
  [ -n "${hi:-}" ] && echo "highest used: #$hi  -> next free: #$((hi + 1))"
else
  say "GitHub"
  echo "gh unavailable or not authenticated — skip PR/issue sections"
fi

# --- context the next session will want to find -----------------------------

say "plan and handoff files"
# ~/.claude/plans fills up with generated plan-mode filenames, so list the
# handoffs explicitly first — otherwise the one line that matters is buried.
plans="$HOME/.claude/plans"
if [ -d "$plans" ]; then
  handoffs=$(ls -t "$plans" 2>/dev/null | grep -i handoff)
  if [ -n "$handoffs" ]; then
    echo "  handoffs:"
    printf '%s\n' "$handoffs" | sed 's/^/    /'
  else
    echo "  handoffs: (none)"
  fi
  echo "  most recent plans:"
  ls -t "$plans" 2>/dev/null | grep -iv handoff | head -5 | sed 's/^/    /'

  if [ -f "$plans/$project-handoff.md" ]; then
    echo
    echo "  NOTE: a handoff for $project already exists."
    echo "  It was never picked up, or the last one was not deleted on resume."
    echo "  Overwrite it — never leave two."
  fi
else
  echo "  (no ~/.claude/plans directory yet)"
fi

say "project instructions present"
for f in CLAUDE.md README.md CONTRIBUTING.md; do
  [ -f "$f" ] && echo "  $f — do NOT restate its contents in the handoff; link to it"
done

say "test command"
if [ -f pyproject.toml ] && grep -q pytest pyproject.toml 2>/dev/null; then
  echo "  uv run pytest -q   (do not run it here; cite the session's last count)"
elif [ -f package.json ]; then
  echo "  npm test   (do not run it here; cite the session's last count)"
else
  echo "  (detect from the repo; cite the session's last measured count)"
fi

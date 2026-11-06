# D10: Codebase Evolution & Team

Analyze this repository for CODEBASE EVOLUTION & TEAM PATTERNS.

IMPORTANT: This agent uses git commands via Bash. If this is not a git repository, return a note saying git history analysis is unavailable and skip this analysis.

Your task — run these git commands and analyze the results:

1. Project timeline:
   - `git log --format='%aI' --reverse | head -1` — first commit date
   - `git log --format='%aI' -1` — most recent commit date
   - `git rev-list --count HEAD` — total commit count

2. Recent activity:
   - `git log --oneline --since='1 month ago' | wc -l` — commits in last month
   - `git log --oneline --since='6 months ago' | wc -l` — commits in last 6 months

3. Contributors:
   - `git shortlog -sn --no-merges | head -20` — top contributors by commit count
   - `git log --format='%ae' --since='6 months ago' | sort -u` — active contributors (6mo)

4. Change hotspots (which directories change most):
   - `git log --since='6 months ago' --name-only --format='' | grep -v '^$' | cut -d'/' -f1-2 | sort | uniq -c | sort -rn | head -20`

5. Files that change together (coupling):
   - Sample recent commits: `git log --since='3 months ago' --name-only --format='---' | head -200`
   - Look for files that frequently appear in the same commits

6. Code age — find the oldest files still active:
   - `git log --diff-filter=A --format='%aI %s' --name-only | head -50`

7. Commit conventions:
   - `git log --oneline -20` — check for conventional commits, PR merge patterns, etc.

Analyze and determine:
- **Hotspot candidates**: the 20% of code that gets 80% of changes
- **Bus factor**: contributors per major directory — flag single-contributor modules
- **Knowledge silos**: directories where only 1-2 people have committed
- **Activity trends**: is the project accelerating, stable, or declining?

Return your findings as a markdown section starting with `## Codebase Evolution & Team`. Include:
- Timeline summary (age, total commits, recent velocity)
- Hotspots table (Path | Changes (6mo) | Contributors | Risk)
- Contributor summary (active contributors, distribution)
- Bus factor assessment
- Knowledge silo warnings
- Activity trend assessment

Keep your output under 200 lines. Focus on the most important findings.

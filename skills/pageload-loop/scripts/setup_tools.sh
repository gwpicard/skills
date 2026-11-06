#!/usr/bin/env bash
# Sets up .pageload/tools/ in the project: copies the loop scripts and installs
# their Node dependencies locally (nothing global, the project's package.json is untouched).
#
# Usage: bash setup_tools.sh [PROJECT_ROOT] [--no-a11y]
#
# Installs into .pageload/tools/node_modules: lighthouse@13, playwright@1, pixelmatch@8, pngjs@7,
# and @axe-core/playwright@4 for the accessibility check (skipped with --no-a11y).
# Adds .pageload/ to .git/info/exclude so loop files never land in the perf commits.
# Checks: Node 22.19+ (required by Lighthouse 13), Python 3.8+, a browser Playwright can launch.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
A11Y=1; ROOT_ARG="."
for arg in "$@"; do
  case "$arg" in
    --no-a11y) A11Y=0 ;;
    *) ROOT_ARG="$arg" ;;
  esac
done
ROOT="$(cd "$ROOT_ARG" && pwd)"
TOOLS="$ROOT/.pageload/tools"

node_ok=$(node -e 'const [a,b]=process.versions.node.split(".").map(Number);console.log(a>22||(a===22&&b>=19)?"yes":"no")' 2>/dev/null || echo "missing")
if [ "$node_ok" != "yes" ]; then
  echo "Node $(node -v 2>/dev/null || echo 'not found'): Lighthouse 13 needs Node 22.19 or later." >&2
  echo "Switch version (for example 'nvm use 22' or 'nvm use 24') and run this again." >&2
  exit 1
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || { echo "Python 3.8+ required" >&2; exit 1; }

mkdir -p "$TOOLS"
cp "$HERE/measure.mjs" "$HERE/visual_diff.mjs" "$HERE/compare.py" "$HERE/report.py" "$TOOLS/"
# npm init rejects a folder named ".pageload", so write the manifest directly.
[ -f "$TOOLS/package.json" ] || echo '{"name":"pageload-tools","private":true}' > "$TOOLS/package.json"
PKGS="lighthouse@13 playwright@1 pixelmatch@8 pngjs@7"
[ "$A11Y" = 1 ] && PKGS="$PKGS @axe-core/playwright@4"
(cd "$TOOLS" && npm install --no-audit --no-fund --loglevel=error $PKGS)

if [ -d "$ROOT/.git" ]; then
  grep -qxF ".pageload/" "$ROOT/.git/info/exclude" 2>/dev/null || echo ".pageload/" >> "$ROOT/.git/info/exclude"
fi

browser=$(cd "$TOOLS" && node --input-type=module -e '
import { chromium } from "playwright";
try { const b = await chromium.launch(); await b.close(); console.log("playwright-chromium"); }
catch { try { const b = await chromium.launch({ channel: "chrome" }); await b.close(); console.log("chrome"); }
catch { console.log("none"); } }' 2>/dev/null || echo "none")

echo "tools: $TOOLS"
echo "lighthouse: $("$TOOLS/node_modules/.bin/lighthouse" --version)"
echo "browser for screenshots: $browser"
if [ "$A11Y" = 1 ]; then echo "accessibility check: on (@axe-core/playwright $(node -p "require('$TOOLS/node_modules/@axe-core/playwright/package.json').version"))"
else echo "accessibility check: off (--no-a11y)"; fi
python3 "$TOOLS/compare.py" selftest | tail -1
if [ "$browser" = "none" ]; then
  echo "No browser found. Run: (cd $TOOLS && npx playwright install chromium)" >&2
  exit 2
fi

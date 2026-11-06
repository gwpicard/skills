#!/usr/bin/env bash
# Sets up a local tools folder for the rendered pass: copies render_audit.mjs and installs
# its Node dependencies there (no global install, no project package.json touched).
#
# Usage: bash setup_render.sh [TOOLS_DIR]
#   TOOLS_DIR defaults to ${XDG_CACHE_HOME:-$HOME/.cache}/website-review/tools
#
# Installs into TOOLS_DIR/node_modules: playwright@1, @axe-core/playwright@4.
# Prints "tools: <dir>" and "browser: playwright-chromium | chrome | none".
# Exit codes: 0 ready, 1 Node missing or too old, 2 no browser Playwright can launch.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="${1:-${XDG_CACHE_HOME:-$HOME/.cache}/website-review/tools}"

node_ok=$(node -e 'const [a]=process.versions.node.split(".").map(Number);console.log(a>=18?"yes":"no")' 2>/dev/null || echo "missing")
if [ "$node_ok" != "yes" ]; then
  echo "Node $(node -v 2>/dev/null || echo 'not found'): the rendered pass needs Node 18 or later." >&2
  exit 1
fi

mkdir -p "$TOOLS"
TOOLS="$(cd "$TOOLS" && pwd)"
cp "$HERE/render_audit.mjs" "$TOOLS/"
[ -f "$TOOLS/package.json" ] || echo '{"name":"website-review-tools","private":true}' > "$TOOLS/package.json"
if [ ! -d "$TOOLS/node_modules/@axe-core/playwright" ] || [ ! -d "$TOOLS/node_modules/playwright" ]; then
  (cd "$TOOLS" && npm install --no-audit --no-fund --loglevel=error playwright@1 @axe-core/playwright@4)
fi

browser=$(cd "$TOOLS" && node --input-type=module -e '
import { chromium } from "playwright";
try { const b = await chromium.launch(); await b.close(); console.log("playwright-chromium"); }
catch { try { const b = await chromium.launch({ channel: "chrome" }); await b.close(); console.log("chrome"); }
catch { console.log("none"); } }' 2>/dev/null || echo "none")

echo "tools: $TOOLS"
echo "browser: $browser"
if [ "$browser" = "none" ]; then
  echo "No browser found. With the user's consent, run: (cd $TOOLS && npx playwright install chromium)" >&2
  exit 2
fi

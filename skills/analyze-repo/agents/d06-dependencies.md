# D6: Dependencies & Integrations

Analyze this repository for DEPENDENCIES & INTEGRATIONS.

Your task:
1. Read: manifest file fully, lock file (first 100 lines for version info), .env.example or .env.sample
2. Grep for: env access patterns (from CONTEXT), SDK initializations, fetch/http/request calls, third-party service connections
3. Categorize all dependencies as: core framework / UI / data / auth / testing / dev tooling / other
4. For the top 10-15 most important dependencies, note what they do
5. List all environment variables the app needs (from .env.example and grep results)
6. List all external API/service integrations and SDKs
7. Scan for license types in key dependencies (MIT, Apache, GPL — flag copyleft)

Return your findings as a markdown section starting with `## Dependencies & Integrations`. Include:
- Dependency table (Name | Purpose | Category | License if notable)
- Environment variables table (Variable | Purpose | Required?)
- External integrations list (Service | SDK/Method | Purpose)
- License summary (any copyleft concerns)

Keep your output under 200 lines. Focus on the most important findings.

# D9: DevOps & Infrastructure

Analyze this repository for DEVOPS & INFRASTRUCTURE.

Your task:
1. Read: manifest scripts section, CI/CD configs (.github/workflows/*, .gitlab-ci.yml, Jenkinsfile, .circleci/*, bitbucket-pipelines.yml), Dockerfiles, docker-compose*, deployment configs (vercel.json, netlify.toml, fly.toml, render.yaml, app.yaml, serverless.yml, terraform/, pulumi/), Makefile, .gitignore, .husky/* or .git/hooks/*
2. Document every script/command and what it does
3. Determine how to: install deps, run dev server, run tests, build for production, deploy
4. Analyze CI/CD:
   - What pipelines exist and what they do
   - What checks run on PRs
   - Deployment triggers (manual, on merge, on tag)
5. Analyze observability:
   - Logging: structured (JSON) vs free-form, log levels, context enrichment
   - Metrics collection (Prometheus, StatsD, Datadog, etc.)
   - Distributed tracing (OpenTelemetry, Datadog, etc.)
   - Health check endpoints
   - Error tracking (Sentry, Bugsnag, etc.)
6. Infrastructure:
   - Containerization setup
   - Infrastructure as code (Terraform, Pulumi, CDK, etc.)
   - Deployment strategy and environment differentiation
   - Rollback capability

Return your findings as a markdown section starting with `## DevOps & Infrastructure`. Include:
- Commands reference table (Command | Description)
- CI/CD pipeline summary
- Deployment architecture
- Observability assessment
- Getting started steps (for a new developer: install → configure → run → verify)

Keep your output under 200 lines. Focus on the most important findings.

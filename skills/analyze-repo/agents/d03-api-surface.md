# D3: API Surface & Interfaces

Analyze this repository for API SURFACE & INTERFACES.

Your task:
1. Glob for: route files, controllers, resolvers, API endpoint definitions, exported modules
2. Grep for: HTTP method definitions (GET, POST, PUT, DELETE, PATCH), GraphQL type/query/mutation definitions, WebSocket event handlers, RPC method definitions, export statements (using CONTEXT module patterns)
3. Identify:
   - Every HTTP endpoint: method, path, parameters, auth required, description
   - GraphQL schema: types, queries, mutations, subscriptions (if applicable)
   - WebSocket events (if applicable)
   - CLI commands and flags (for CLI tools)
   - Exported library API: public functions, types, interfaces, components (for libraries)
   - API versioning strategy
   - Error response format and codes
   - Rate limiting configuration
   - OpenAPI/Swagger specs (if they exist, and whether they match actual code)
4. Determine request/response shapes for key endpoints

Return your findings as a markdown section starting with `## API Surface & Interfaces`. Include:
- Endpoint table (Method | Path | Auth | Description) for REST APIs
- GraphQL schema summary (if applicable)
- Exported API summary (for libraries)
- API versioning and error format notes
- Rate limiting notes

Keep your output under 200 lines. Focus on the most important findings.

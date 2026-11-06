# D2: Data Model & Storage

Analyze this repository for DATA MODEL & STORAGE.

Your task:
1. Find and read schema definition files — look for: Prisma schema, SQLAlchemy models, Django models, TypeORM entities, Mongoose schemas, ActiveRecord models, GORM models, Diesel schemas, EF Core models, migrations directories, SQL files
2. Grep for: model/entity/schema definitions, foreign key references, relationship definitions, ORM query patterns
3. Identify:
   - All data entities/models with their key fields
   - Relationships between entities (one-to-one, one-to-many, many-to-many)
   - Data validation rules (at schema level and application level)
   - Migration history — how many migrations, any squashed/reset migrations
   - Data access patterns — repository pattern, active record, raw queries, ORM usage
   - Caching layer — Redis, Memcached, in-memory, CDN caching
   - Seed data / fixtures — does test data setup exist?
   - File/blob storage — S3, local filesystem, CDN integration
4. Create a Mermaid ER diagram showing entity relationships

Return your findings as a markdown section starting with `## Data Model & Storage`. Include:
- Mermaid ER diagram
- Entity table (Entity | Key Fields | Relationships | Business Rules/Validation)
- Migration summary (count, last migration, any concerns)
- Data access pattern assessment
- Caching strategy summary (or note its absence)

Keep your output under 200 lines. Focus on the most important findings.

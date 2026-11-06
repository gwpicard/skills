# PostgreSQL in 100 Seconds

- Source: https://www.youtube.com/watch?v=n2Fluyr3lbc
- Author: Fireship · Published: 2023 · Length: 02:36
- Processed: 2026-09-17 · Transcript: captions-auto · Visual depth: standard (51 frames)
- Cache: ~/.cache/video-notes/postgresql-in-100-seconds-n2Fluyr3lbc (transcript, frames)
- Focus: decide whether to model a product catalog with custom composite types or plain tables

## TL;DR

A fast overview of PostgreSQL for developers who know SQL. The speaker says the point of
Postgres over other relational databases is that it is object-relational: you define
custom types and use arrays, JSON, and key-value columns inside ordinary tables. The
second half is a sponsored walkthrough of creating a database on Neon and running
queries from VS Code. The most useful takeaway is the on-screen schema in the demo, which
the audio only half describes.

## Key learnings

1. [00:02] Postgres started in 1986 at UC Berkeley under Michael Stonebraker. It is the "most trusted" open source relational database in the speaker's words.
2. [00:20] Postgres is object-relational. You create custom data types with properties, and it supports inheritance and polymorphism.
3. [00:35] Writes are ACID transactions. Multiversion concurrency control gives each transaction a snapshot so transactions run in parallel without locks.
4. [00:51] Extensibility: stored procedures, procedures in Python and C, and extensions. Named: PostGIS (geospatial, used by Uber), Citus (sharding, scale-out), pgvector under the name "PG embedding" (AI chatbot memory).
5. [01:14] To start: install locally or use a cloud host. The speaker recommends Neon (sponsor) for autoscaling, a web UI, and database branching.
6. [01:37] Data modeling options beyond plain columns: arrays with `[]`, two-dimensional arrays with `[][]`, JSON columns, and key-value pairs with the `hstore` extension.
7. [01:56] Insert into a table whose column is a custom type with `ROW(...)`. Cast strings to JSON or hstore with `::`.
8. [02:15] Relationships: a primary key on every table, a foreign key column on the many side, then a join on the two ids.

## What was only on screen

- [00:21] (frames/f_006_00-22.jpg) Slide "CUSTOM TYPES" shows the canonical example the audio never spells out: an `address` type with `street`, `city`, `zip`.
- [00:45] (frames/f_014_00-45.jpg) Slide "STORED PROCEDURES" shows the call syntax `CALL insert_user(...)`, not `SELECT`.
- [00:54] (frames/f_016_00-53.jpg) PostGIS example query computes a distance in meters between two points after transforming them to SRID 3857.
- [01:10] (frames/f_022_01-10.jpg) Neon autoscaling architecture diagram. See "Architecture" below.
- [01:14] (frames/f_024_01-16.jpg) Neon marketing slide: "Supercharge your development workflows with branching. Deploy: instantly deploy development, test, and staging environments with an up-to-date copy of your production data."
- [01:17] (frames/f_025_01-19.jpg) Neon console. Left nav: Dashboard, Branches, Tables, SQL Editor, Operations, Settings, Integrations, Roles, Databases, Community. The "Database creation" dialog has three fields: Branch (main, primary), Database name, Owner.
- [01:21] (frames/f_026_01-21.jpg) VS Code extension is SQLTools v0.28.0 by Matheus Teixeira, about 3 million installs. Features listed: formatter, query runner with history and bookmarks, connection explorer, INSERT generator, pluggable drivers.
- [01:47] (frames/f_035_01-48.jpg) The demo type is `Human`, not `address`. It has a 2D `CHAR[4][4]` array for `dna` and a `JSON` column for `bio`. The first line of the file is `CREATE EXTENSION hstore;`. The speaker only says "arrays" and "JSON".
- [02:01] (frames/f_040_02-01.jpg) The insert uses `ROW(...)`, `ARRAY['A','T','G','C']`, a JSON literal cast with `::json`, and an hstore literal `'java=>expert,js=>noob'::hstore`. The table is `programmers` with one column `details`. The audio only says "double colon to cast".
- [02:15] (frames/f_045_02-15.jpg) The second table is `lambo` with `id SERIAL PRIMARY KEY` and `model TEXT`. The foreign key column is being typed and was not captured.

## Code, commands, and config seen

Transcribed from frames 6, 14, 16, 35, 40, 45. Trailing commas are as shown on screen.

```sql
-- 00:21 slide
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    zip INTEGER
);

-- 00:45 slide
CALL insert_user(
  'Jeff',
  'hello@fireship.io'
);

-- 00:54 slide (PostGIS)
SELECT ST_Distance(
  ST_Transform(ST_Point(31.1342, 29.9792)::geography, 3857),
  ST_Transform(ST_Point(-88.5678, 20.6843)::geography, 3857)
) as distance_meters;

-- 01:47 demo file neon.session.sql
CREATE EXTENSION hstore;

CREATE TYPE Human AS (
  name TEXT,
  birthday DATE,
  dna CHAR[4][4],
  bio JSON,
);

-- 02:01
INSERT INTO programmers (details)
VALUES (
    ROW(
        'Jeff',
        '1969-08-15',
        ARRAY['A', 'T', 'G', 'C'],
        '{"about": "Jeff is 10x dev"}'::json,
        'java=>expert,js=>noob'::hstore
    )
);

-- 02:15
CREATE TABLE lambo (
  id SERIAL PRIMARY KEY,
  model TEXT,
);
```

Not captured: the `CREATE TABLE programmers` statement, the dot-notation `SELECT`, and
the final join. Check the frames between 02:05 and 02:12 or rerun with `--depth deep`.

## Architecture, diagrams, and UI

- [01:10] Neon autoscaling diagram. A dashed box labelled "K8s Node" contains an `autoscaler-agent` at the top and two rows of VMs below. One VM is expanded and contains `vm-informant` and `Postgres`. Arrows: `Metrics` flow up from the VM to the agent, `Scaling requests` flow down. The agent has arrows out to `K8s Scheduler (modified)` on the left and `NeonVM` on the right.
- [02:12] Primary key diagram: a grid of rows where the first column `id` holds 1, 2, 3 in green and the other cells are empty.

## Resources mentioned

- Neon (sponsor): free cloud Postgres with autoscaling and branching.
- SQLTools VS Code extension by Matheus Teixeira.
- Extensions: PostGIS, Citus, pgvector ("PG embedding"), hstore.
- PostgreSQL downloads page: Linux, macOS, Windows, BSD, Solaris.
- The speaker names Uber as a Citus user and shows an Uber ride receipt at [00:56].

## Caveats and open questions

- This is a 100-second overview. It shows syntax but no trade-offs.
- The speaker does not say when to prefer a composite type over a separate table. The demo stores a whole person in one `details` column, which makes querying by field harder than plain columns.
- The Neon section is sponsored. Autoscaling and branching claims are marketing slides, not demonstrated.
- The auto captions write "post GIS", "cytus", and "PG embedding". The frames show PostGIS, Citus, and a point cloud that suggests pgvector.

## How this applies to: decide whether to model a product catalog with custom composite types or plain tables

1. Use plain columns for anything you filter or sort on. The video's `programmers.details` composite column would force dot-notation access on every query [02:00].
2. Use a composite type only for a value that always travels together and is never queried alone, such as an address [00:21].
3. Use `JSON` or `JSONB` for attributes that vary per product. The video uses `JSON` [01:47]; prefer `JSONB` for indexing, which the video does not cover.
4. Use arrays for short fixed lists like tags [01:37].
5. Skip `hstore`. `JSONB` covers the same key-value case with better tooling. The video enables it but never uses it [01:47].

## Timeline

- [00:00] History and definition
- [00:20] Object-relational, custom types
- [00:35] ACID and MVCC
- [00:51] Stored procedures and extensions
- [01:10] Neon setup and VS Code
- [01:20] Demo: custom type, arrays, JSON, hstore
- [01:56] Demo: insert, select, primary and foreign keys, join
- [02:29] Outro

---
name: lunar-sql
description: Craft correct SQL queries against the Lunar data model. Use when querying Lunar's PostgreSQL SQL API to analyze components, checks, policies, domains, or PRs. Covers view schemas, join patterns, filtering by component/commit/PR, time series queries, and JSONB path expressions.
---

# Lunar SQL API Skill

Query Lunar's data using SQL. The SQL API provides read-only PostgreSQL access to components, checks, policies, domains, PRs, and catalog data.

## Quick Start

```bash
# Get connection string
lunar sql connection-string

# Connect interactively
psql $(lunar sql connection-string)

# Execute a query
psql $(lunar sql connection-string) -c "SELECT * FROM components_latest LIMIT 5"
```

## Documentation References

### SQL API Views

For complete schema documentation and examples, read:

| View | Documentation |
|------|---------------|
| Overview | [docs/sql-api/sql-api.md](docs/sql-api/sql-api.md) |
| `components` / `components_latest` | [docs/sql-api/views/components.md](docs/sql-api/views/components.md) |
| `component_deltas` / `component_deltas_latest` | [docs/sql-api/views/component-deltas.md](docs/sql-api/views/component-deltas.md) |
| `checks` / `checks_latest` | [docs/sql-api/views/checks.md](docs/sql-api/views/checks.md) |
| `domains` | [docs/sql-api/views/domains.md](docs/sql-api/views/domains.md) |
| `initiatives` | [docs/sql-api/views/initiatives.md](docs/sql-api/views/initiatives.md) |
| `policies` | [docs/sql-api/views/policies.md](docs/sql-api/views/policies.md) |
| `prs` | [docs/sql-api/views/prs.md](docs/sql-api/views/prs.md) |
| `catalog` / `catalog_latest` | [docs/sql-api/views/catalog.md](docs/sql-api/views/catalog.md) |

### Component JSON Schema

The `component_json` column contains the merged Component JSON from all collectors. For schema conventions and structure:

| Topic | Documentation |
|-------|---------------|
| Schema conventions, presence detection, boolean patterns | [references/component-json/conventions.md](references/component-json/conventions.md) |
| Category reference (`.repo`, `.sca`, `.k8s`, etc.) | [references/component-json/structure.md](references/component-json/structure.md) |

## Core View Schemas

### components / components_latest

| Column | Type | Description |
|--------|------|-------------|
| `component_id` | TEXT | Component identifier (e.g., `github.com/foo/bar`) |
| `timestamp` | TIMESTAMPTZ | "Committed at" UTC timestamp of the `git_sha` |
| `git_sha` | TEXT | Git commit SHA |
| `pr` | BIGINT | PR number (NULL = default branch) |
| `domain` | TEXT | Domain in dotted format (e.g., `payments.analytics`) |
| `tags` | TEXT[] | Array of tags |
| `meta` | JSONB | Arbitrary metadata |
| `component_json` | JSONB | Merged Component JSON from all collectors |

### checks / checks_latest

| Column | Type | Description |
|--------|------|-------------|
| `component_id` | TEXT | Component identifier |
| `timestamp` | TIMESTAMPTZ | Commit timestamp |
| `git_sha` | TEXT | Git commit SHA |
| `pr` | BIGINT | PR number (NULL = default branch) |
| `name` | TEXT | Check name |
| `description` | TEXT | Check description |
| `initiative_name` | TEXT | Parent initiative |
| `policy_name` | TEXT | Parent policy |
| `enforcement` | TEXT | `draft`, `score`, `block-pr`, `block-release`, `block-pr-and-release` |
| `status` | TEXT | `pass`, `fail`, `pending`, `error`, `skipped` |
| `failure_reason` | TEXT[] | Failure reasons (NULL if passed) |
| `stale` | INTERVAL | Time since last evaluation (NULL if current) |

## Key Concepts

### Component Identification

A component version is uniquely identified by:
- `component_id`: Full path like `github.com/org/repo/path`
- `git_sha`: Git commit SHA
- `pr`: PR number (NULL for default branch)

```sql
-- Latest data for a component on default branch
SELECT * FROM components_latest
WHERE component_id = 'github.com/foo/bar'
  AND pr IS NULL;

-- Data for a specific PR
SELECT * FROM components_latest
WHERE component_id = 'github.com/foo/bar'
  AND pr = 123;
```

### The `_latest` Views

Views with `_latest` suffix contain only the most recent `git_sha` for each `pr` in each component:
- Use `_latest` views for current state queries
- Use base views for historical/time-series analysis
- Filter by `pr IS NULL` for default branch data

### Timestamp Consistency

The `timestamp` column represents the Git "committed at" time and is consistent across views for the same `component_id` + `git_sha`. Use this for joining time-series data.

### Domain Hierarchy

Domains use dotted notation (e.g., `payments.checkout.api`). Query hierarchies with `LIKE`:

```sql
-- All components in payments domain (including subdomains)
WHERE domain = 'payments' OR domain LIKE 'payments.%'

-- Direct children only
WHERE domain LIKE 'payments.%' AND domain NOT LIKE 'payments.%.%'
```

## JSONB Query Patterns

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `->` | Get field as JSONB | `component_json->'go'` |
| `->>` | Get field as TEXT | `component_json->'go'->>'version'` |
| `jsonb_path_exists()` | Check path exists | `jsonb_path_exists(component_json, '$.go.version')` |
| `@>` | Contains | `component_json @> '{"go": {}}'` |

### Safe Value Extraction

Always check path existence before extraction:

```sql
SELECT component_id,
       component_json->'codecov'->'report'->'result'->'coverage'->>'total' AS coverage
FROM components_latest
WHERE jsonb_path_exists(component_json, '$.codecov.report.result.coverage.total')
  AND pr IS NULL;
```

### Type Casting

The `->>` operator returns TEXT. Cast explicitly:

```sql
-- Numeric comparison
WHERE (component_json->'coverage'->>'percentage')::NUMERIC >= 80

-- Boolean comparison
WHERE (component_json->'repo'->>'has_readme')::BOOLEAN = true
```

## Common Query Patterns

### Failing Checks by Domain

```sql
WITH component_domains AS (
  SELECT component_id, domain
  FROM components_latest
  WHERE pr IS NULL
)
SELECT domain, COUNT(*) AS failing_checks
FROM checks_latest
JOIN component_domains USING (component_id)
WHERE status = 'fail' AND pr IS NULL
GROUP BY domain
ORDER BY failing_checks DESC;
```

### Blocked PRs

```sql
-- PRs blocked by checks
SELECT DISTINCT component_id, pr
FROM checks_latest
WHERE pr IS NOT NULL
  AND status = 'fail'
  AND enforcement = 'block-pr';
```

### Check Status Time Series

```sql
SELECT timestamp,
  SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) AS passed,
  SUM(CASE WHEN status = 'fail' THEN 1 ELSE 0 END) AS failed,
  SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
FROM checks
WHERE component_id = 'github.com/foo/bar' AND pr IS NULL
GROUP BY timestamp
ORDER BY timestamp;
```

### Components by Tag

```sql
SELECT component_id, domain, tags
FROM components_latest
WHERE 'soc2' = ANY(tags) AND pr IS NULL;
```

### Cross-View Joins

Views share `component_id`, `git_sha`, and `pr` columns:

```sql
-- Components with their checks
SELECT c.component_id, c.domain, ch.name AS check_name, ch.status
FROM components_latest c
LEFT JOIN checks_latest ch USING (component_id, git_sha, pr)
WHERE c.pr IS NULL;

-- PRs by author with failing check count
SELECT p.component_id, p.pr, p.title, p.author_name,
       COUNT(*) FILTER (WHERE ch.status = 'fail') AS failing_checks
FROM prs p
LEFT JOIN checks_latest ch ON p.component_id = ch.component_id AND p.pr = ch.pr
GROUP BY p.component_id, p.pr, p.title, p.author_name;
```

## Best Practices

1. **Use `_latest` views** for current state; base views for history
2. **Always filter `pr IS NULL`** when querying default branch
3. **Check path existence** with `jsonb_path_exists()` before extracting JSONB values
4. **Cast JSONB values** explicitly (`::NUMERIC`, `::BOOLEAN`) after `->>` extraction
5. **Use CTEs** for domain lookups to avoid repeated subqueries
6. **Join on `(component_id, git_sha, pr)`** for precise version matching

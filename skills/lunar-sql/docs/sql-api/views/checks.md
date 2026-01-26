# Checks Views

```
checks
checks_latest
```

The `checks` view is a time series representation of the collection of checks that Lunar ran on components.

A subset of this data is available in the `checks_latest` view, which contains only the checks for the latest `git_sha` in each `pr`, in each component. To get the latest row for the default branch, you can filter this view by `pr IS NULL`.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `component_id` | `TEXT` | The identifier for the component - e.g. `github.com/foo/bar/buz` |
| `timestamp` | `TIMESTAMPTZ` | The "committed at" UTC timestamp of the `git_sha` |
| `git_sha` | `TEXT` | The Git commit SHA of the component JSON |
| `pr` | `BIGINT` | The pull request number if the commit is part of a pull request. Set to `NULL` for the default branch |
| `name` | `TEXT` | The name of the check that was run |
| `description` | `TEXT` | The description of the check that was run |
| `initiative_name` | `TEXT` | The identifier of the initiative this check's policy belongs to |
| `policy_name` | `TEXT` | The name of the policy this check is part of |
| `enforcement` | `TEXT` | The enforcement level of the check. Can be one of `draft`, `score`, `block-pr`, `block-release`, `block-pr-and-release` |
| `status` | `TEXT` | The status of the check. Can be one of `pass`, `fail`, `pending`, `error`, `skipped` |
| `failure_reason` | `TEXT[]` | Array of human-readable reasons the check failed. Set to `NULL` if the check passed. |
| `stale` | `INTERVAL` | The time since the check was last evaluated. Set to `NULL` if the check is not stale. |

## Notes

* To get the set of checks for a given component version, you need to filter by `component_id`, and `git_sha`.
* The timestamp is guaranteed to be the same for a given `git_sha` of a `component_id`. This timestamp will also match entries in other views such as [`components`](./components.md) and [`component_deltas`](./component-deltas.md).
* While a certain `git_sha` for a component is being evaluated, the row may use a stale result from a previous version of the code. In such cases, the `stale` column will be set to the time since the check was last evaluated.

## Usage examples

Retrieve the checks associated with the latest `git_sha` for a given component, ordered by status.

```sql
SELECT *
FROM checks_latest
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IS NULL,
ORDER BY  CASE status
            WHEN 'fail' THEN 1
            WHEN 'error' THEN 2
            WHEN 'pending' THEN 3
            WHEN 'pass' THEN 4
            WHEN 'skipped' THEN 5
          END ASC;
```

Retrieve time series data of the number of checks that passed, failed, had no data, or errored out over time.

```sql
SELECT
  timestamp,
  SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) AS passed,
  SUM(CASE WHEN status = 'fail' THEN 1 ELSE 0 END) AS failed,
  SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
  SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS errored,
  SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) AS skipped
FROM checks
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IS NULL
GROUP BY timestamp
ORDER BY timestamp ASC;
```

Retrieve the checks that are failing for all components with the tag `soc2`.

```sql
SELECT *
FROM checks_latest
WHERE component_id IN (
    SELECT component_id
    FROM components_latest
    WHERE 'soc2' = ANY(tags)
      AND pr IS NULL
  )
  AND pr IS NULL
  AND status = 'fail';
```

Retrieve the checks that are blocking PRs right now.

```sql
SELECT *
FROM checks_latest
WHERE pr IS NOT NULL
  AND status = 'fail'
  AND enforcement = 'block-pr';
```

Count the number of PRs that are blocked by checks for each domain.

```sql
WITH component_domains AS (
  SELECT
    component_id,
    domain
  FROM components_latest
  WHERE pr IS NULL
)
SELECT 
  domain,
  COUNT(DISTINCT pr) AS blocked_prs
FROM checks_latest
JOIN component_domains USING (component_id)
WHERE status = 'fail'
  AND enforcement = 'block-pr'
  AND pr IS NOT NULL
GROUP BY domain;
```

Total blocking checks for the domain `payments` over time.

```sql
WITH component_domains AS (
  SELECT
    component_id,
    domain
  FROM components_latest
  WHERE (domain = 'payments' OR domain LIKE 'payments.%')
    AND pr IS NULL
)
SELECT
  timestamp,
  COUNT(*) AS blocking_checks
FROM checks
JOIN component_domains USING (component_id)
WHERE status = 'fail'
  AND enforcement = 'block-pr'
  AND pr IS NOT NULL
GROUP BY timestamp
ORDER BY timestamp ASC;
```

All blocking failing checks of all PRs authored by Jane.

```sql
WITH janes_prs AS (
  SELECT component_id, pr
  FROM prs
  WHERE author_email = 'jane@example.com'
)
SELECT *
FROM checks_latest
JOIN janes_prs USING (component_id, pr)
WHERE status = 'fail'
  AND enforcement = 'block-pr';
```

# Components Views

```
components
components_latest
```

The `components` view is a time series representation of the collection of components that Lunar monitors.

A subset of this data is available in the `components_latest` view, which contains only the latest `git_sha` for each `pr`, in each component. To get the latest row for the default branch, you can filter this view by `pr IS NULL`.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `component_id` | `TEXT` | The identifier for the component - e.g. `github.com/foo/bar/buz` |
| `timestamp` | `TIMESTAMPTZ` | The "committed at" UTC timestamp of the `git_sha` |
| `git_sha` | `TEXT` | The Git commit SHA of the component JSON |
| `pr` | `BIGINT` | The pull request number if the commit is part of a pull request. Set to `NULL` for the default branch |
| `domain` | `TEXT` | The domain of the component in dotted path format (e.g. `payments.analytics.backend`) |
| `tags` | `TEXT[]` | The tags associated with the component |
| `meta` | `JSONB` | Arbitrary metadata associated with the component |
| `component_json` | `JSONB` | The component JSON object resulting from merging component JSON deltas of the different collectors that ran for this component |

## Notes

* To get the component data for a given component version, you need to filter by `component_id`, and `git_sha`. This pair uniquely identifies each row in the table.
* For repeated updates to the same commit SHA, the `component_json` is updated with the latest JSON object. Individual updates (or "deltas") can be accessed through the [`component_deltas` view](./component-deltas.md).

## Usage examples

Find the latest data for a particular component on the default branch. This query is guaranteed to return at most one row.

```sql
SELECT *
FROM components_latest
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IS NULL;
```

Code coverage of a component over time.

```sql
SELECT timestamp,
       component_json->'codecov'->'report'->'result'->'coverage'->>'total' AS coverage
FROM components
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IS NULL
  AND jsonb_path_exists(component_json, '$.codecov.report.result.coverage.total')
ORDER BY timestamp ASC;
```

Histogram of Go versions used across all components within a domain.

```sql
SELECT component_json->'go'->>'version' AS go_version,
       COUNT(*) AS count
FROM components_latest
WHERE jsonb_path_exists(component_json, '$.go.version')
  AND (domain = 'analytics' OR domain LIKE 'analytics.%')
  AND pr IS NULL
GROUP BY go_version
ORDER BY count DESC;
```

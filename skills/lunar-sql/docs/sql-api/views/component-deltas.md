# Component Deltas Views

```
component_deltas
component_deltas_latest
```

The `component_deltas` view is a time series representation of the collection of component metadata deltas that Lunar collects.

A subset of this data is available in the `component_deltas_latest` view, which contains only the deltas for the latest `git_sha` in each `pr`, in each component. To get the latest row for the default branch, you can filter this view by `pr IS NULL`.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `component_id` | `TEXT` | The identifier for the component - e.g. `github.com/foo/bar/buz` |
| `timestamp` | `TIMESTAMPTZ` | The "committed at" UTC timestamp of the `git_sha` |
| `git_sha` | `TEXT` | The Git commit SHA of the component JSON |
| `pr` | `BIGINT` | The pull request number if the commit is part of a pull request. Set to `NULL` for the default branch |
| `collector_name` | `TEXT` | The name of the collector that contributed this delta |
| `collection_timestamp` | `TIMESTAMPTZ` | The UTC timestamp when the collector ran |
| `delta` | `JSONB` | The metadata delta that was contributed by the collector |

## Notes

* To get the set of deltas for a given component version, you need to filter by `component_id`, and `git_sha`. The ordering of these deltas is defined by the `collection_timestamp`.
* Merging these deltas in the order of `collection_timestamp` will give you the final `component_json` object for a given `component_id` and `git_sha` that is found in the [`components` view](./components.md).
* The `timestamp` column (not to be confused with `collection_timestamp`) is guaranteed to be the same for a given `git_sha` of a `component_id`. This timestamp will also match entries in other views such as [`components`](./components.md) and [`checks`](./checks.md).

## Usage example

Retrieve the deltas associated with the latest `git_sha` for a given component on the default branch.

```sql
SELECT *
FROM component_deltas_latest
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IS NULL
ORDER BY collection_timestamp ASC;
```

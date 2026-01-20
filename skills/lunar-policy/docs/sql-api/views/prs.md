
# PRs View

```
prs
```

The `prs` view provides information about component pull requests. The information in this view is largely mirrored from the GitHub API, and is provided for convenience.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `component_id` | `TEXT` | The identifier for the component - e.g. `github.com/foo/bar/buz` |
| `pr` | `BIGINT` | The pull request number |
| `pr_opened_at` | `TIMESTAMPTZ` | The UTC timestamp when the pull request was opened |
| `pr_status` | `TEXT` | The status of the pull request. Can be one of `open`, `closed`, or `merged` |
| `title` | `TEXT` | The title of the pull request |
| `author_name` | `TEXT` | The name of the author of the pull request |
| `author_email` | `TEXT` | The email of the author of the pull request |
| `latest_git_sha` | `TEXT` | The latest Git commit SHA of the pull request |
| `latest_commit_timestamp` | `TIMESTAMPTZ` | The "committed at" UTC timestamp of the latest commit in the pull request |
| `latest_committer_name` | `TEXT` | The name of the committer of the latest commit in the pull request |
| `latest_committer_email` | `TEXT` | The email of the committer of the latest commit in the pull request |

## Usage example

Retrieve PR information for all the PRs that have failing checks in a component.

```sql
WITH failing_prs AS (
  SELECT DISTINCT pr
  FROM checks_latest
  WHERE component_id = 'github.com/foo/bar/buz'
    AND pr IS NOT NULL
    AND status = 'fail'
)
SELECT *
FROM prs
WHERE component_id = 'github.com/foo/bar/buz'
  AND pr IN (SELECT pr FROM failing_prs);
```

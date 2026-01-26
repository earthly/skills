# Policies View

```
policies
```

The `policies` view provides information about all policies defined in Lunar. Policies define specific checks or rules that are applied to components.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `name` | `TEXT` | The identifier for the policy |
| `description` | `TEXT` | A description of the policy |
| `enforcement` | `TEXT` | The enforcement level of the policy. Can be one of `draft`, `score`, `block-pr`, `block-release`, `block-pr-and-release` |
| `initiative_name` | `TEXT` | The identifier of the initiative this policy belongs to |

## Notes

* Policies define specific checks that are applied to components
* Policies can have different enforcement levels that determine how violations are handled
* Policies are organized into initiatives

## Usage examples

List all policies with their enforcement levels:

```sql
SELECT name, description, enforcement
FROM policies
ORDER BY enforcement;
```

Find all blocking policies within a specific initiative:

```sql
SELECT *
FROM policies
WHERE initiative_name = 'security-compliance'
  AND enforcement IN ('block-pr', 'block-release', 'block-pr-and-release');
```

Get a count of policies by enforcement level:

```sql
SELECT 
  enforcement,
  COUNT(*) as policy_count
FROM policies
GROUP BY enforcement
ORDER BY policy_count DESC;
``` 
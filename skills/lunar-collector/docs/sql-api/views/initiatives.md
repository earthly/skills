# Initiatives View

```
initiatives
```

The `initiatives` view provides information about initiatives in Lunar. Initiatives are collections of policies organized around a specific goal or purpose.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `name` | `TEXT` | The identifier for the initiative |
| `description` | `TEXT` | A description of the initiative |
| `owner` | `TEXT` | The owner of the initiative |

## Notes

* Initiatives are organized collections of policies designed around a specific goal or compliance requirement
* Each initiative can contain multiple policies and may span different components

## Usage examples

List all initiatives in the system:

```sql
SELECT *
FROM initiatives
ORDER BY name;
```

Find initiatives owned by a specific person:

```sql
SELECT *
FROM initiatives
WHERE owner = 'security-team@example.com';
```

Get a list of initiatives and the number of policies within each:

```sql
SELECT 
  i.name AS initiative_name,
  i.description,
  COUNT(p.name) AS policy_count
FROM initiatives i
LEFT JOIN policies p ON i.name = p.initiative_name
GROUP BY i.name, i.description
ORDER BY policy_count DESC;
``` 
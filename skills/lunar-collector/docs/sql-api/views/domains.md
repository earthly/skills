# Domains View

```
domains
```

The `domains` view provides information about all domains defined in Lunar. Domains represent logical groupings of components that share similar characteristics or purposes.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `name` | `TEXT` | The identifier for the domain in hierarchical dotted format (e.g. `payments.checkout`) |
| `description` | `TEXT` | A description of the domain |
| `owner` | `TEXT` | The owner of the domain |
| `meta` | `JSONB` | Arbitrary metadata associated with the domain |

## Notes

* Domains are defined primarily in the Lunar configuration but can also come from catalogers
* Domains can be used to organize and categorize components
* Components can be assigned to specific domains to create logical groupings
* Domains can be hierarchical, with a parent-child relationship represented by a dotted notation. For example, in the domain name `auth.sso.providers`, `auth` is the parent domain of `auth.sso`, and `auth.sso` is the parent domain of `auth.sso.providers`. The full domain name is stored in the `name` column using dotted notation.

## Usage examples

List all domains in the system:

```sql
SELECT *
FROM domains
ORDER BY name;
```

Find domains owned by a specific person or team:

```sql
SELECT *
FROM domains
WHERE owner = 'platform-team@example.com';
```

Get a count of components by domain:

```sql
SELECT 
  d.name AS domain_name,
  COUNT(c.name) AS component_count
FROM domains d
LEFT JOIN components c ON c.domain = d.name
GROUP BY d.name
ORDER BY component_count DESC;
```

Find all subdomains of a specific parent domain:

```sql
SELECT *
FROM domains
WHERE name LIKE 'payments.%'
ORDER BY name;
```

Find the direct subdomains of a specific domain (only one level down):

```sql
SELECT *
FROM domains
WHERE name LIKE 'payments.%'
  AND name NOT LIKE 'payments.%.%'
ORDER BY name;
```

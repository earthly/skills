# SQL API Overview

The SQL API provides programmatic access to Lunar's data through SQL queries. Through this interface, you can access and analyze information about your components, domains, policies, and more.

## Accessing the SQL API

To access the SQL API, use the Lunar CLI command `lunar sql connection-string` to get a PostgreSQL connection string that can be used with any PostgreSQL client:

```bash
# Get the connection string
lunar sql connection-string

# Connect using psql (interactive)
psql $(lunar sql connection-string)

# Execute a query directly
psql $(lunar sql connection-string) -c "SELECT * FROM components LIMIT 5"
```

The access is **read-only** and restricted to only the views described in this documentation.

## Available Views

For detailed information about available views, explore these pages:

* [domains](views/domains.md)
* [components](views/components.md)
* [component_deltas](views/component-deltas.md)
* [initiatives](views/initiatives.md)
* [policies](views/policies.md)
* [checks](views/checks.md)
* [prs](views/prs.md)
* [catalog](views/catalog.md)

## AI Skill

An AI skill is available to help you craft SQL queries against the Lunar data model. The [lunar-sql](https://github.com/earthly/skills/tree/main/skills/lunar-sql) skill provides your AI assistant with knowledge of the view schemas, JSONB query patterns, and common query examples.

See [Installing AI Skills](../install/skills.md) for setup instructions.

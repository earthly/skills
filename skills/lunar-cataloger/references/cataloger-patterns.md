# Cataloger Patterns

Concrete patterns for the four hook types — pick the one that matches your trigger and adapt.

For the full surface area (env vars, `lunar catalog` forms, hook field reference, landing-page metadata), see [cataloger-reference.md](cataloger-reference.md).

## Pattern 1: External API sync (cron hook)

```bash
#!/bin/bash
set -e

# Hook: type: cron, schedule: "0 2 * * *"

curl -fsS \
  -H "Authorization: Bearer $LUNAR_SECRET_BACKSTAGE_TOKEN" \
  "https://backstage.example.com/api/catalog/entities?filter=kind=component" | jq '
    [.[] | {
      (.metadata.annotations["github.com/repo"]): {
        owner: .spec.owner,
        domain: .spec.domain,
        tags: .metadata.tags
      }
    }] | add
  ' | lunar catalog --json '.components' -
```

## Pattern 2: GitHub org sync with batching (cron hook)

Pulling many thousands of repos? Use `gh repo list` → temp file → `jq` filter → batched `lunar catalog` calls. See `catalogers/github-org/main.sh` in lunar-lib for a complete reference implementation with:

- Visibility filtering (public/private/internal)
- Include / exclude glob patterns
- Rate-limit retry with exponential backoff
- Streaming through a temp file for memory efficiency
- 1k-component batches into `lunar catalog`

## Pattern 3: Database sync (cron hook)

```bash
#!/bin/bash
set -e

psql "$LUNAR_SECRET_DB_URL" -t -A -c "
  SELECT json_agg(json_build_object(
    repo_url, json_build_object(
      'owner', owner_email,
      'domain', domain_path,
      'tags', ARRAY[tier, team]
    )
  ))
  FROM services WHERE active = true
" | lunar catalog --json '.components' -
```

## Pattern 4: Central catalog repo (repo hook)

```bash
#!/bin/bash
set -e

# Hook: type: repo, repo: github://acme/software-catalog

cat domains.toml | toml2json | jq '.domains' | lunar catalog --json '.domains' -
cat services.yaml | yq -o=json '.components' | lunar catalog --json '.components' -
```

## Pattern 5: Repo-file classification (component-repo hook)

Classify each component automatically from files in its repo. Cannot create new components — only augments existing ones.

```bash
#!/bin/bash
set -e

# Hook: type: component-repo
# LUNAR_COMPONENT_ID is set automatically

# Tag from CI workflow
if grep -q '^name: Production Deploy$' .github/workflows/*.yml 2>/dev/null; then
  lunar catalog component --tag production
fi

# Tag from language detection
if   [ -f go.mod ];           then lunar catalog component --tag go
elif [ -f package.json ];     then lunar catalog component --tag javascript
elif [ -f requirements.txt ]; then lunar catalog component --tag python
fi
```

## Pattern 6: Component-JSON heuristics (component-cron hook)

Read each component's existing Component JSON (gathered by collectors) and classify from those signals — e.g. tag any component whose `k8s.deployments[]` mentions a prod namespace.

```bash
#!/bin/bash
set -e

# Hook: type: component-cron, schedule: "0 3 * * *"

COMPONENT_JSON="$(lunar component get-json "$LUNAR_COMPONENT_ID")"

if echo "$COMPONENT_JSON" | jq -e '.k8s.deployments[]? | select(.namespace == "prod")' >/dev/null; then
  lunar catalog component --tag production
fi

if echo "$COMPONENT_JSON" | jq -e '.sca.dependencies[]? | select(.license == "AGPL-3.0")' >/dev/null; then
  lunar catalog component --tag compliance-review
fi
```

Cannot create new components — only augments existing ones.

## Pattern 7: Multi-source aggregation (cron hook, multiple writes)

```bash
#!/bin/bash
set -e

# Primary source
curl -fsS "$BACKSTAGE_API/entities" | jq '...' | \
  lunar catalog --json '.components' -

# Layer ownership from CSV
curl -fsS "$OWNERSHIP_SHEET_CSV" | csvjson | jq '...' | \
  lunar catalog --json '.components' -

# Domains from internal API
curl -fsS "$INTERNAL_API/domains" | jq '...' | \
  lunar catalog --json '.domains' -
```

`lunar catalog` merges into the catalog cumulatively within a single cataloger run — multiple calls layer on top of each other.

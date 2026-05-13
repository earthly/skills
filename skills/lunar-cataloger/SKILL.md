---
name: lunar-cataloger
description: Create Lunar cataloger plugins that sync software catalog information (domains, components, ownership, tags) from external systems into Lunar. Use when building catalogers (Bash scripts) that pull from GitHub orgs, Backstage, ServiceNow, databases, or repo files and write to the Catalog JSON. Covers hook types (cron, repo, component-repo, component-cron), the `lunar catalog` command (raw/component/domain forms), plugin structure with `lunar-cataloger.yml`, landing-page metadata, and local testing.
---

# Lunar Cataloger Skill

Create cataloger plugins for Earthly Lunar — Bash scripts that sync software catalog information (components, domains, ownership, tags) from external systems into Lunar's Catalog JSON.

## Quick Start

1. Read [about-lunar.md](references/about-lunar.md) for platform overview
2. Read [core-concepts.md](references/core-concepts.md) for architecture and key entities
3. Read [cataloger-reference.md](references/cataloger-reference.md) for comprehensive cataloger documentation

## What a Cataloger Is

A cataloger is a Bash script that:
1. Fetches information about domains and components from an external source (API, database, repo file, etc.)
2. Writes that information to the Catalog JSON using the `lunar catalog` command

The Catalog JSON defines the **structure** of your software portfolio — what components exist, who owns them, which domain they belong to, what tags they have. Collectors (separate primitive) then gather **data** about each component.

| Aspect | Cataloger | Collector |
|--------|-----------|-----------|
| **Purpose** | Define *what* components/domains exist | Gather *data about* components |
| **Output** | Catalog JSON | Component JSON |
| **Scope** | Organization-wide catalog | Per-component data |
| **Trigger** | Cron, repo, component-repo, component-cron | Code changes, CI events, cron |
| **Command** | `lunar catalog` | `lunar collect` |

## Plugin Structure

```
my-cataloger/
├── lunar-cataloger.yml    # Required: plugin config
├── main.sh                # Main script
├── Dockerfile             # Optional: for custom dependencies
├── assets/
│   └── my-cataloger.svg   # Required for public plugins: landing-page icon
├── README.md              # Documentation
└── sample-catalog.json    # Optional: example output for landing page
```

**lunar-cataloger.yml:**
```yaml
version: 0

name: my-cataloger
description: Syncs catalog from external system
author: team@example.com

default_image: earthly/lunar-scripts:1.0.0

landing_page:
  display_name: "My Cataloger"
  long_description: |
    Sync components from XYZ into your Lunar catalog. Automatically
    track ownership, domains, and metadata across your organization.
  category: "repository-and-ownership"
  status: "stable"
  icon: "assets/my-cataloger.svg"

catalogers:
  - name: sync-components
    description: Fetches component list from API
    mainBash: main.sh
    hook:
      type: cron
      schedule: "0 2 * * *"
    keywords: ["service catalog", "auto-discovery", "external sync"]

inputs:
  api_url:
    description: Base URL for the catalog API
    default: "https://api.example.com"
  org_name:
    description: Organization name to sync
    # No default = required input

secrets:
  - name: API_TOKEN
    description: API authentication token
    required: true

example_catalog_json: |
  {
    "components": {
      "github.com/acme/api": {
        "owner": "team@acme.com",
        "domain": "platform.backend",
        "tags": ["go", "production"]
      }
    }
  }
```

## Hook Types

A cataloger's `hook:` defines **when** it runs and **what context** it gets.

| Hook | Trigger | Context | Use Case |
|------|---------|---------|----------|
| `cron` | Schedule | Lunar Runner, no repo clone | External API / DB sync |
| `repo` | Commits to a specific repo | Runner with clone of that repo | Central catalog repo with TOML/YAML definitions |
| `component-repo` | Commits to any component repo | Runner with clone of the component | Augment existing component metadata from repo contents |
| `component-cron` | Per-component, on schedule | Runner with component context | Periodic per-component augmentation from Component JSON |

```yaml
# Cron - daily at 2am UTC
hook:
  type: cron
  schedule: "0 2 * * *"

# Repo - run when central catalog repo changes
hook:
  type: repo
  repo: github://acme/software-catalog

# Component-repo - run on every component repo commit
hook:
  type: component-repo

# Component-cron - daily, once per component
hook:
  type: component-cron
  schedule: "0 3 * * *"
```

**Note:** `component-repo` and `component-cron` cannot **create** new components, only **augment** metadata on existing ones. Use `cron` or `repo` to define new components.

## The `lunar catalog` Command

Three forms for writing to the Catalog JSON:

### Raw form — arbitrary JSON

```bash
# Write components
lunar catalog --json '.components' '{"github.com/acme/api": {"owner": "jane@acme.com"}}'

# Pipe from stdin
gh repo list my-org --json name,owner,url | jq '...' | \
  lunar catalog --json '.components' -

# Write domains
lunar catalog --json '.domains' '{"platform": {"owner": "platform-team@acme.com"}}'
```

### Component form — structured flags for one component

```bash
lunar catalog component \
  --name "github.com/acme/api" \
  --owner "jane@acme.com" \
  --domain "platform.backend" \
  --tag "go" \
  --tag "production" \
  --meta tier=1
```

In `component-repo` or `component-cron` hooks, `--name` is inferred from `LUNAR_COMPONENT_ID`:

```bash
# In a component-repo hook
lunar catalog component --tag production
```

### Domain form — structured flags for one domain

```bash
lunar catalog domain \
  --name "platform" \
  --description "Platform services" \
  --owner "platform-team@acme.com"
```

## Catalog JSON Structure

```json
{
  "domains": {
    "<domain-name>": {
      "description": "<description>",
      "owner": "<owner>",
      "meta": { "<key>": "<value>" }
    }
  },
  "components": {
    "<component-name>": {
      "owner": "<owner>",
      "domain": "<domain>",
      "branch": "<branch>",
      "tags": ["<tag1>", "<tag2>"],
      "ciPipelines": ["<pipeline1>"],
      "meta": { "<key>": "<value>" }
    }
  }
}
```

### Merge Precedence

Catalog data is merged in this order (later wins):

1. **Catalogers** (in declared order — later catalogers override earlier)
2. **`lunar.yml`** files in component repos
3. **`lunar-config.yml`** `domains` and `components` (highest precedence)

This means catalogers can bulk-import, and per-component overrides in `lunar-config.yml` win.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LUNAR_HUB_HOST` | Lunar Hub hostname |
| `LUNAR_HUB_INSECURE` | Skip SSL verification |
| `LUNAR_CATALOGER_NAME` | Current cataloger name |
| `LUNAR_CATALOGER_OWNER` | Cataloger owner |
| `LUNAR_BIN_DIR` | Where the Lunar CLI is installed |
| `LUNAR_PLUGIN_ROOT` | Plugin root directory (plugins only) |
| `LUNAR_COMPONENT_ID` | Current component (only for `component-repo` / `component-cron`) |
| `LUNAR_SECRET_<NAME>` | Secrets set on the cataloger |
| `LUNAR_VAR_<INPUT>` | Input value (uppercase input name) |

## Reference Documentation

| File | Content |
|------|---------|
| [references/about-lunar.md](references/about-lunar.md) | Platform overview |
| [references/core-concepts.md](references/core-concepts.md) | Architecture, Catalog JSON, Component JSON |
| [references/cataloger-reference.md](references/cataloger-reference.md) | **Complete cataloger guide** — hooks, env vars, patterns |
| [references/cataloger-README-template.md](references/cataloger-README-template.md) | README template for cataloger plugins |
| [docs/lunar-config/catalogers.md](docs/lunar-config/catalogers.md) | `lunar-config.yml -> catalogers` reference |
| [docs/lunar-config/cataloger-hooks.md](docs/lunar-config/cataloger-hooks.md) | Hook types in detail |
| [docs/plugins/cataloger-plugins.md](docs/plugins/cataloger-plugins.md) | `lunar-cataloger.yml` plugin manifest reference |
| [docs/bash-sdk/cataloger.md](docs/bash-sdk/cataloger.md) | `lunar catalog` CLI reference |
| [docs/key-concepts/catalog-json.md](docs/key-concepts/catalog-json.md) | Catalog JSON model |

## Full Lunar Documentation

For the full Lunar platform docs — CLI reference, SDKs, installation — see [docs/SUMMARY.md](docs/SUMMARY.md).

## Local Development & Testing

Run from a directory containing `lunar-config.yml`:

**Prerequisites:**
- `LUNAR_HUB_TOKEN` set for authentication
- `lunar-config.yml` references your cataloger via `uses: ./catalogers/my-cataloger`

**Run all catalogers and output the merged Catalog JSON:**
```bash
lunar cataloger dev --output-json
```

**View the current catalog state:**
```bash
lunar cataloger get-json
```

**Iterate on a single cataloger:**
```bash
LUNAR_VAR_ORG_NAME=acme \
  bash ./catalogers/my-cataloger/main.sh
```

(The script writes via `lunar catalog`, which talks to the hub. For dry-run, swap `lunar catalog` for `cat` or `jq` during dev.)

## Best Practices

1. **Use `set -e`** — bail on first error to avoid corrupting the catalog.
2. **Fail on API errors** — `curl -fsS` so HTTP errors abort the script. Slightly outdated > corrupted.
3. **One cataloger per source** — separate catalogers for Backstage, GitHub, DB. Don't multiplex.
4. **Batch large datasets** — for >1k components, use a temp file + jq to transform, then post in batches (see the `github-org` cataloger in lunar-lib for a reference implementation with rate-limit retry and batching).
5. **Log progress** — `echo "Found N components"` between fetch / transform / write so failures are debuggable.
6. **Use structured `jq` transformations** — clearer than `sed`/`awk` for JSON.
7. **Use `earthly/lunar-scripts:1.0.0`** — official base image; pre-loaded with `lunar`, `jq`, `curl`, `gh`.
8. **Document the schema** — list which Catalog JSON paths your cataloger writes (`.components[*].owner`, `.domains[*].description`, etc.).
9. **Pin landing-page categories** — pick one of the six (`repository-and-ownership`, `deployment-and-infrastructure`, `testing-and-quality`, `devex-build-and-ci`, `security-and-compliance`, `operational-readiness`).

## Common Patterns

### Pattern 1: External API sync (cron hook)

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

### Pattern 2: GitHub org sync with batching (cron hook)

Pulling many thousands of repos? Use `gh repo list` → temp file → `jq` filter → batched `lunar catalog` calls. See `catalogers/github-org/main.sh` in lunar-lib for a complete reference implementation with:
- Visibility filtering (public/private/internal)
- Include / exclude glob patterns
- Rate-limit retry with exponential backoff
- Streaming through a temp file for memory efficiency
- 1k-component batches into `lunar catalog`

### Pattern 3: Database sync (cron hook)

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

### Pattern 4: Central catalog repo (repo hook)

```bash
#!/bin/bash
set -e

# Hook: type: repo, repo: github://acme/software-catalog

cat domains.toml | toml2json | jq '.domains' | lunar catalog --json '.domains' -
cat services.yaml | yq -o=json '.components' | lunar catalog --json '.components' -
```

### Pattern 5: Per-component augmentation (component-repo hook)

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
if   [ -f go.mod ];         then lunar catalog component --tag go
elif [ -f package.json ];   then lunar catalog component --tag javascript
elif [ -f requirements.txt ]; then lunar catalog component --tag python
fi
```

### Pattern 6: Multi-source aggregation (cron hook, multiple writes)

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

## Landing Page Metadata (Public Plugins)

Public catalogers (published in `lunar-lib` or another shared repo) need landing-page metadata so they render correctly on earthly.dev/lunar:

```yaml
landing_page:
  display_name: "GitHub Org Cataloger"   # Must end with "Cataloger", ≤50 chars
  long_description: |                    # ≤300 chars
    Sync repositories from GitHub organizations into your Lunar catalog.
  category: "repository-and-ownership"
  status: "stable"                       # stable | beta | experimental | deprecated
  icon: "assets/github-org.svg"
  related:
    - slug: "github"
      type: "collector"
      reason: "Collects detailed settings for each discovered repository"
```

Plus per-cataloger keywords:

```yaml
catalogers:
  - name: repos
    description: |
      Syncs all repositories from a GitHub organization as components.
    mainBash: main.sh
    hook: { type: cron, schedule: "0 2 * * *" }
    keywords: ["service catalog", "auto-discovery", "github"]
```

**Categories** (pick one):

| Slug | Display |
|------|---------|
| `repository-and-ownership` | Repository & Ownership |
| `deployment-and-infrastructure` | Deployment & Infrastructure |
| `testing-and-quality` | Testing & Quality |
| `devex-build-and-ci` | DevEx, Build & CI |
| `security-and-compliance` | Security & Compliance |
| `operational-readiness` | Operational Readiness |

The README's `# title` must match `landing_page.display_name` exactly — both are cross-validated at build time.

## Wiring a Cataloger into `lunar-config.yml`

```yaml
catalogers:
  # Local plugin
  - uses: ./catalogers/my-cataloger
    with:
      org_name: "acme"

  # GitHub plugin (pinned tag — preferred)
  - uses: github://earthly/lunar-lib/catalogers/github-org@v1.1.0
    hook:
      type: cron
      schedule: "0 * * * *"   # override the plugin's default schedule
    with:
      org_name: "acme-corp"
      default_owner: "engineering@acme.com"

  # Pick a subset of sub-catalogers
  - uses: ./catalogers/backstage
    include: [components, domains]
```

See the [lunar-config skill](../lunar-config/SKILL.md) for the surrounding `lunar-config.yml` reference (or if that skill isn't installed, [docs/lunar-config/catalogers.md](docs/lunar-config/catalogers.md)).

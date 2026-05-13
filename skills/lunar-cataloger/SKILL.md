---
name: lunar-cataloger
description: Create Lunar cataloger plugins (Bash scripts) that build the software catalog — syncing components and domains from external systems, or classifying them from custom signals like repo files, CI config, or each component's Component JSON.
---

# Lunar Cataloger Skill

Create cataloger plugins for Earthly Lunar — Bash scripts that build the software catalog (components, domains, ownership, tags) by syncing from external sources, classifying from signals in each component, or both.

## Quick Start

1. Read [references/about-lunar.md](references/about-lunar.md) for platform overview and [references/core-concepts.md](references/core-concepts.md) for architecture.
2. Read [references/cataloger-reference.md](references/cataloger-reference.md) — the full cataloger guide: hooks, env vars, `lunar catalog` forms, landing-page metadata, and Common Patterns.

## What a Cataloger Is

A cataloger is a Bash script that writes to the **Catalog JSON** — the definition of what components and domains exist, who owns them, and how they're tagged. It can do either or both:

- **Sync** from an external source of truth — GitHub orgs, Backstage, ServiceNow, an internal API, a database, files in a central repo.
- **Classify** existing components from custom signals or heuristics — files in the component's repo (e.g. tag `go` when `go.mod` is present), CI config, or **the component's own Component JSON** (e.g. tag `production` when `k8s.deployments[].namespace == "prod"`). Each component's Component JSON is one possible signal among many.

Collectors are the complementary primitive — they gather *data* about each component into the Component JSON. Catalogers define *what's in scope* and how to label it; collectors describe each thing in scope.

| Aspect | Cataloger | Collector |
|--------|-----------|-----------|
| **Purpose** | Define *what* components/domains exist + classify them | Gather *data about* components |
| **Output** | Catalog JSON | Component JSON |
| **Scope** | Organization-wide | Per-component |
| **Trigger** | `cron`, `repo`, `component-repo`, `component-cron` | Code changes, CI events, cron |
| **Command** | `lunar catalog` | `lunar collect` |

## Plugin Structure

```
my-cataloger/
├── lunar-cataloger.yml    # Required: plugin config
├── main.sh                # Main script
├── Dockerfile             # Optional: for custom dependencies
├── assets/my-cataloger.svg  # Required for public plugins
├── README.md
└── sample-catalog.json    # Optional: landing-page example
```

**lunar-cataloger.yml (minimal):**

```yaml
version: 0
name: my-cataloger
description: Syncs catalog from external system
author: team@example.com
default_image: earthly/lunar-scripts:1.0.0

catalogers:
  - name: sync-components
    mainBash: main.sh
    hook:
      type: cron
      schedule: "0 2 * * *"

inputs:
  org_name:
    description: Organization name to sync
    # No default = required input

secrets:
  - name: API_TOKEN
    description: API authentication token
    required: true
```

For public plugins, add `landing_page:` + per-cataloger `keywords:` — see [cataloger-reference.md](references/cataloger-reference.md).

## Hook Types

A cataloger's `hook:` defines **when** it runs and **what context** it gets.

| Hook | Trigger | Context | Typical Use |
|------|---------|---------|-------------|
| `cron` | Schedule | No repo clone | Sync from API / DB / catalog repo |
| `repo` | Commits to a specific repo | Clone of that repo | Central catalog file (TOML/YAML) |
| `component-repo` | Commits to any component repo | Clone of that component | Classify from repo files (presence of `go.mod`, CI workflows, etc.) |
| `component-cron` | Per-component, on schedule | Component context + Component JSON | Classify from each component's collected data |

```yaml
# Cron
hook: { type: cron, schedule: "0 2 * * *" }

# Repo
hook: { type: repo, repo: github://acme/software-catalog }

# Component-repo
hook: { type: component-repo }

# Component-cron
hook: { type: component-cron, schedule: "0 3 * * *" }
```

`component-repo` and `component-cron` **augment** existing components only — they cannot create new ones. Use `cron` or `repo` to define new components.

## The `lunar catalog` Command

Three forms for writing to the Catalog JSON:

```bash
# Raw form — arbitrary JSON
lunar catalog --json '.components' '{"github.com/acme/api": {"owner": "jane@acme.com"}}'
gh repo list my-org --json name,owner,url | jq '...' | lunar catalog --json '.components' -

# Component form — structured flags for one component
lunar catalog component \
  --name "github.com/acme/api" \
  --owner "jane@acme.com" --domain "platform.backend" \
  --tag "go" --tag "production" --meta tier=1

# Domain form — structured flags for one domain
lunar catalog domain --name "platform" --owner "platform-team@acme.com"
```

In `component-repo` / `component-cron` hooks, `--name` is inferred from `LUNAR_COMPONENT_ID`, so `lunar catalog component --tag production` is enough.

Multiple `lunar catalog` calls within a single run layer onto the catalog cumulatively. **Merge precedence across catalogers** (later wins): catalogers in declared order → `lunar.yml` in component repos → `domains:` / `components:` in `lunar-config.yml`.

## Environment Variables

Cataloger-specific (full list in [cataloger-reference.md](references/cataloger-reference.md)):

| Variable | When set |
|----------|----------|
| `LUNAR_CATALOGER_NAME` | Always |
| `LUNAR_COMPONENT_ID` | Only in `component-repo` / `component-cron` hooks |
| `LUNAR_SECRET_<NAME>` | Per declared secret |
| `LUNAR_VAR_<INPUT>` | Per declared input (uppercase name) |

## Reference Documentation

LLM-curated summaries (in this skill):

| File | Content |
|------|---------|
| [references/about-lunar.md](references/about-lunar.md) | Platform overview |
| [references/core-concepts.md](references/core-concepts.md) | Architecture, Catalog JSON, Component JSON |
| [references/cataloger-reference.md](references/cataloger-reference.md) | **Complete cataloger guide** — hooks, env vars, `lunar catalog` forms, landing-page metadata, Common Patterns |
| [references/cataloger-README-template.md](references/cataloger-README-template.md) | README template for cataloger plugins |

Hosted Lunar docs serve raw markdown at `docs-lunar.earthly.dev/<path>.md`:

- <https://docs-lunar.earthly.dev/llms.txt> — Index of every doc page
- <https://docs-lunar.earthly.dev/configuration/lunar-config/catalogers.md> — `lunar-config.yml -> catalogers` reference
- <https://docs-lunar.earthly.dev/configuration/lunar-config/cataloger-hooks.md> — Hook types in detail
- <https://docs-lunar.earthly.dev/plugin-sdks/plugins/cataloger-plugins.md> — `lunar-cataloger.yml` manifest reference
- <https://docs-lunar.earthly.dev/plugin-sdks/bash-sdk/cataloger.md> — `lunar catalog` CLI reference
- <https://docs-lunar.earthly.dev/docs/catalog-json.md> — Catalog JSON model

## Local Development & Testing

Run from a directory containing `lunar-config.yml`. Set `LUNAR_HUB_TOKEN` for authentication, and reference the cataloger via `uses: ./catalogers/my-cataloger`.

```bash
# Run all catalogers and output the merged Catalog JSON
lunar cataloger dev --output-json

# View the current catalog state
lunar cataloger get-json

# Iterate on a single cataloger directly
LUNAR_VAR_ORG_NAME=acme bash ./catalogers/my-cataloger/main.sh
```

For dry-runs, swap `lunar catalog` for `cat` or `jq` so nothing hits the hub.

## Best Practices

1. **`set -e`** — bail on first error to avoid corrupting the catalog.
2. **`curl -fsS`** — fail on HTTP errors. Slightly outdated > corrupted.
3. **One cataloger per source** — separate catalogers for Backstage, GitHub, DB. Don't multiplex.
4. **Batch large datasets** — for >1k components, temp file + `jq` + batched writes (see the `github-org` cataloger in lunar-lib).
5. **Log progress** — `echo "Found N components"` between fetch / transform / write.
6. **Use `earthly/lunar-scripts:1.0.0`** — official base image with `lunar`, `jq`, `curl`, `gh`.
7. **Document the schema** — list which Catalog JSON paths your cataloger writes.

## Wiring into `lunar-config.yml`

```yaml
catalogers:
  - uses: ./catalogers/my-cataloger
    with: { org_name: "acme" }

  - uses: github://earthly/lunar-lib/catalogers/github-org@v1.1.0
    hook: { type: cron, schedule: "0 * * * *" }   # override the plugin default
    with:
      org_name: "acme-corp"
      default_owner: "engineering@acme.com"

  - uses: ./catalogers/backstage
    include: [components, domains]                 # pick sub-catalogers
```

Full `catalogers:` reference: <https://docs-lunar.earthly.dev/configuration/lunar-config/catalogers.md>.

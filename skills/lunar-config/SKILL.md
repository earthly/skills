---
name: lunar-config
description: Edit `lunar-config.yml`, the configuration file that wires together a Lunar deployment. Use when adding or removing components, domains, collectors, policies, catalogers, or initiatives; pinning plugin versions; changing enforcement levels; configuring default images; or setting up tag-based targeting with the `on:` field. Covers the file schema, plugin import forms, tag-matching expressions, and local validation.
---

# Lunar Config Skill

Edit `lunar-config.yml` — the YAML file that defines a Lunar deployment: which components are governed, which collectors gather data, which policies enforce standards, which catalogers sync the catalog, and how enforcement is rolled out.

## Quick Start

1. Read [about-lunar.md](references/about-lunar.md) for platform overview
2. Read [core-concepts.md](references/core-concepts.md) for architecture and key entities
3. Read [docs/lunar-config/lunar-config.md](docs/lunar-config/lunar-config.md) for the complete `lunar-config.yml` schema

## What `lunar-config.yml` Is

A single YAML file, kept in its own repository (e.g. `my-org-lunar-config`), that wires everything together:

```yaml
version: 0

default_image: earthly/lunar-scripts:1.0.0

hub:
  host: lunar.example.com
  grpcPort: 443
  httpPort: 443

domains:
  engineering:
    description: Engineering organization
    owner: eng@example.com

components:
  github.com/example/api:
    owner: api-team@example.com
    domain: engineering
    tags: [backend, go]

catalogers:
  - uses: github://earthly/lunar-lib/catalogers/github-org@v1.1.0
    with:
      org_name: "example"

collectors:
  - uses: github://earthly/lunar-lib/collectors/readme@v1.1.0
    on: ["domain:engineering"]

initiatives:
  - name: standardization
    description: Repo standards
    owner: eng@example.com
    on: ["domain:engineering"]

policies:
  - uses: github://earthly/lunar-lib/policies/readme@v1.1.0
    initiative: standardization
    enforcement: report-pr
```

When the CI in the config repo runs `lunar sync-manifest`, the hub picks up the updated config and applies it to every governed component.

## Top-Level Sections

| Section | Type | Required | Purpose |
|---------|------|----------|---------|
| `version` | int | yes | Schema version (currently `0`) |
| `hub` | object | yes | Lunar Hub connection (`host`, `grpcPort`, `httpPort`) |
| `default_image` | string | no | Container image for collectors / policies / catalogers (overrides per type with `default_image_collectors`, `default_image_policies`, `default_image_catalogers`) |
| `domains` | object | no | Organizational structure with owners |
| `components` | object | no | Repos / monorepo subdirectories under governance, with tags, owners, and domain assignment |
| `catalogers` | array | no | Sync catalog data (components/domains) from external systems |
| `collectors` | array | yes | Gather SDLC data into the Component JSON |
| `initiatives` | array | no | Grouping for related policies (used for scoring) |
| `policies` | array | yes | Evaluate Component JSON and produce checks |

## Plugin Import Forms (`uses:`)

Most real configs are short because they import plugins from `lunar-lib` or another repo:

```yaml
# GitHub plugin pinned to a tag
- uses: github://earthly/lunar-lib/collectors/golang@v1.1.0

# GitHub plugin pinned to a branch (use sparingly — see "Branch Refs" below)
- uses: github://earthly/lunar-lib/collectors/python@main

# Local plugin (path relative to the config repo)
- uses: ./collectors/my-custom-collector
```

The same `uses:` form works for `collectors`, `policies`, and `catalogers`. You can also inline a small collector/policy/cataloger with `runBash` / `runPython` / `mainBash` / `mainPython` instead of `uses:`. See:

- [docs/lunar-config/collectors.md](docs/lunar-config/collectors.md) for collector forms
- [docs/lunar-config/policies.md](docs/lunar-config/policies.md) for policy forms
- [docs/lunar-config/catalogers.md](docs/lunar-config/catalogers.md) for cataloger forms

### Filtering Sub-Plugins with `include` / `exclude`

When a plugin bundles multiple sub-collectors / sub-policies, use `include` or `exclude` to pick which ones run:

```yaml
collectors:
  - uses: github://earthly/lunar-lib/collectors/sonarqube@main
    on: [has-sonarqube]
    include: [api, config, github-app]
    with:
      project_key: "myorg_backend"

policies:
  - uses: github://earthly/lunar-lib/policies/vcs@v1.1.0
    include: [require-default-branch, disallow-force-push]
    enforcement: report-pr
```

If neither is specified, all sub-plugins run.

## Tag Matching with `on:`

Every `collector`, `policy`, and `initiative` uses `on:` to target components. There are two forms.

**Array form** (OR logic — match if component has any tag):

```yaml
on: [backend, go]
```

**Expression form** (with `AND`, `OR`, `NOT`):

```yaml
on: "domain:engineering AND NOT domain:engineering.experimental"
```

Special tags:

| Prefix | Meaning |
|--------|---------|
| `domain:foo` | Component is in domain `foo` (or any sub-domain) |
| `component:github.com/foo/bar` | A specific component |
| `collector:foo` | Same components as the collector named `foo` |
| `policy:foo` | Same components as the policy named `foo` |

Custom tags (`backend`, `go`, `has-sonarqube`, etc.) come from `components[*].tags` or from catalogers like `github-org` (which auto-tags repos by language and visibility).

See [docs/lunar-config/on.md](docs/lunar-config/on.md) for the full reference.

## Common Operations

### Add a new component

```yaml
components:
  github.com/example/new-service:
    owner: team@example.com
    domain: engineering.platform
    branch: "main"
    tags: [backend, go, SOC2]
```

The component starts being governed on the next manifest sync. Any collector / policy whose `on:` matches a tag here will run for the new component.

### Add a new plugin

```yaml
collectors:
  - uses: github://earthly/lunar-lib/collectors/codecov@v1.1.0
    on: [backend]

policies:
  - uses: github://earthly/lunar-lib/policies/testing@v1.1.0
    initiative: code-quality
    enforcement: report-pr
```

Prefer pinned tags (`@v1.1.0`) over `@main` so manifest syncs are reproducible.

### Roll out enforcement gradually

```yaml
policies:
  - uses: github://earthly/lunar-lib/policies/readme@v1.1.0
    enforcement: draft        # invisible to teams; for testing
  # → score                   # contributes to score, no PR comments
  # → report-pr               # comments on PRs, doesn't block
  # → block-pr                # blocks PR merges
  # → block-release           # blocks releases (via `lunar policy ok-release`)
  # → block-pr-and-release    # blocks both
```

Walk a new policy up the enforcement ladder over several weeks rather than starting at `block-pr`.

### Add a new domain

```yaml
domains:
  engineering.payments:
    description: Payments platform
    owner: payments-lead@example.com
```

Domains are hierarchical (`engineering.payments.checkout`). Policies and collectors with `on: ["domain:engineering"]` automatically apply to all sub-domains.

### Configure a default image

```yaml
version: 0
default_image: earthly/lunar-scripts:1.0.0
default_image_ci_collectors: native    # CI collectors run on the host
```

See [docs/lunar-config/images.md](docs/lunar-config/images.md) for image resolution order.

### Branch Refs (testing) — Cleanup is Mandatory

Temporary `@<branch>` refs are fine for testing an unmerged plugin change, but **must be cleaned up** when the branch is deleted, or the manifest sync will fail:

- **Existing plugin already on `@main`**: revert to `@main` after testing.
- **New plugin not yet on `@main`**: remove the entry entirely; re-add with `@main` after the lunar-lib PR merges.

## `runs_on:` — PRs vs Default Branch

By default, collectors and policies run in both contexts. Restrict with:

```yaml
- uses: ./collectors/expensive-scan
  on: ["domain:engineering"]
  runs_on: [default-branch]   # don't run on every PR
```

Values: `prs`, `default-branch`.

## Reference Documentation

| File | Content |
|------|---------|
| [docs/lunar-config/lunar-config.md](docs/lunar-config/lunar-config.md) | Top-level schema (`version`, `hub`, `default_image*`, etc.) |
| [docs/lunar-config/domains.md](docs/lunar-config/domains.md) | Domain hierarchy and ownership |
| [docs/lunar-config/components.md](docs/lunar-config/components.md) | Component declaration (owner, domain, branch, tags) |
| [docs/lunar-config/catalogers.md](docs/lunar-config/catalogers.md) | Cataloger forms and configuration |
| [docs/lunar-config/cataloger-hooks.md](docs/lunar-config/cataloger-hooks.md) | Cataloger hook types (`cron`, `repo`, `component-repo`, `component-cron`) |
| [docs/lunar-config/collectors.md](docs/lunar-config/collectors.md) | Collector forms and configuration |
| [docs/lunar-config/collector-hooks.md](docs/lunar-config/collector-hooks.md) | Collector hook types (`code`, `cron`, `ci-after-command`, etc.) |
| [docs/lunar-config/policies.md](docs/lunar-config/policies.md) | Policy forms, enforcement levels, initiatives |
| [docs/lunar-config/initiatives.md](docs/lunar-config/initiatives.md) | Initiative declaration |
| [docs/lunar-config/on.md](docs/lunar-config/on.md) | Tag-matching syntax (array + expression forms, special prefixes) |
| [docs/lunar-config/images.md](docs/lunar-config/images.md) | Default images, `native` mode, resolution order |
| [references/core-concepts.md](references/core-concepts.md) | Component JSON, hooks, enforcement model |

## Full Lunar Documentation

For the full Lunar platform docs — CLI reference, installation, SDKs — see [docs/SUMMARY.md](docs/SUMMARY.md).

## Local Validation & Testing

Run from a directory containing `lunar-config.yml`:

```bash
# Validate config syntax and structure
lunar config validate

# Show the merged plugin structure
lunar config show

# Test a collector locally before adding it
lunar collector dev <collector-name> --verbose --component github.com/org/repo

# Test a policy locally
lunar policy dev <policy-name> --verbose --component-json path/to/component.json

# End-to-end: pipe collector output into policy
lunar collector dev my-collector --component github.com/org/repo | \
  lunar policy dev my-policy --verbose --component-json -
```

`lunar-config.yml` changes are applied via a sync workflow in CI. After merging a PR to the config repo, check that the **Sync Lunar Config** workflow succeeds — if it fails, the hub will not pick up the changes.

## Best Practices

1. **Pin plugins to tags** (`@v1.1.0`) in production. Reserve `@main` and `@<branch>` for short testing windows.
2. **Clean up branch refs** after testing — they break manifest sync when the branch is deleted.
3. **Walk enforcement up gradually**: `draft` → `score` → `report-pr` → `block-pr`.
4. **Use `domain:` tags over component lists** when targeting groups of components — new components inherit automatically.
5. **Group related policies under an `initiative:`** so the scoring rolls them up.
6. **Comment your `on:` choices** when the expression is non-obvious (`# only services that opted into SonarQube`).
7. **Validate locally first** with `lunar config validate` before pushing.
8. **One config repo per Lunar Hub** — don't try to share a config across hubs.

## Common Patterns

### Per-language enforcement

```yaml
policies:
  - uses: github://earthly/lunar-lib/policies/golang@v1.1.0
    on: [go]
    enforcement: report-pr
    with:
      min_go_version: "1.21"

  - uses: github://earthly/lunar-lib/policies/python@v1.1.0
    on: [python]
    enforcement: report-pr
    with:
      min_python_version: "3.9"
```

### Opt-in via tag

```yaml
collectors:
  - uses: github://earthly/lunar-lib/collectors/sonarqube@main
    on: [has-sonarqube]
    with:
      project_key: "myorg_backend"

policies:
  - uses: github://earthly/lunar-lib/policies/sonarqube@main
    on: [has-sonarqube]
    enforcement: score
```

Components opt in by adding `has-sonarqube` to their `tags:` list.

### Combining cataloger + per-component overrides

Catalog data is merged in this order (later wins):

1. Catalogers (in declared order)
2. `lunar.yml` files in component repos
3. `domains:` / `components:` in `lunar-config.yml` (highest precedence)

Use a cataloger like `github-org` to bulk-import components, then override owner/domain/tags in `components:` for the ones that need bespoke metadata.

### Per-input overrides for shared plugins

```yaml
- uses: github://earthly/lunar-lib/policies/dependencies@v1.1.0
  name: dependency-versions-go
  on: [go]
  with:
    language: "go"
    min_versions: '{"github.com/sirupsen/logrus": "1.9.0"}'

- uses: github://earthly/lunar-lib/policies/dependencies@v1.1.0
  name: dependency-versions-java
  on: [java]
  with:
    language: "java"
    min_versions: '{"org.apache.commons:commons-text": "1.10.0"}'
```

Same plugin, two instances with distinct `name:` and `with:` inputs.

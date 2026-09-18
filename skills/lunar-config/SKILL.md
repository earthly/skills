---
name: lunar-config
description: Edit `lunar-config.yml` — wire together components, domains, collectors, policies, catalogers, and initiatives for a Lunar deployment.
---

# Lunar Config Skill

Edit `lunar-config.yml` — the YAML file that defines a Lunar deployment.

## Quick Start

1. Read [references/about-lunar.md](references/about-lunar.md) and [references/core-concepts.md](references/core-concepts.md).
2. Use the `references/` files first. If they are insufficient, use the hosted docs backup below to find the full `lunar-config.yml` schema.
3. **For a new lunar-config repo**, bootstrap from the official template: <https://github.com/earthly/lunar-config-template>. It ships with a working `lunar-config.yml`, the CI workflow that runs `lunar hub pull`, and the secrets layout already wired up.

## File Structure

A single YAML file kept in its own repo. Minimal example:

```yaml
version: 0
default_image: earthly/lunar-scripts:1.0.0
hub:
  host: lunar.example.com
  grpcPort: 443
  httpPort: 443

components:
  github.com/example/api:
    owner: api-team@example.com
    domain: engineering
    tags: [backend, go]

collectors:
  - uses: github://earthly/lunar-lib/collectors/readme@v1.1.0
    on: ["domain:engineering"]

policies:
  - uses: github://earthly/lunar-lib/policies/readme@v1.1.0
    enforcement: report-pr
```

After a config repo commit, CI runs `lunar hub pull <repo>` to push the new config to the hub. The hub then applies it to every governed component.

| Section | Required | Purpose |
|---------|----------|---------|
| `version` | yes | Schema version (`0`) |
| `hub` | yes | Hub connection (`host`, `grpcPort`, `httpPort`) |
| `default_image` | no | Container image; overridable per type (`default_image_collectors`, `default_image_policies`, `default_image_catalogers`) |
| `domains` | no | Hierarchical organization with owners |
| `components` | no | Repos / subdirs under governance |
| `catalogers` | no | Sync catalog data from external systems |
| `collectors` | yes | Gather SDLC data into Component JSON |
| `initiatives` | no | Group related policies for scoring |
| `policies` | yes | Evaluate Component JSON, produce checks |

## Plugin Imports (`uses:`)

```yaml
- uses: github://earthly/lunar-lib/collectors/golang@v1.1.0   # GitHub plugin, pinned
- uses: github://earthly/lunar-lib/collectors/python@main      # Branch (testing only)
- uses: ./collectors/my-custom-collector                       # Local path
```

Inline alternatives: `runBash` / `runPython` / `mainBash` / `mainPython` instead of `uses:`. For per-type details, use the `references/` files first; if needed, see the hosted documentation backup.

### Filter sub-plugins

```yaml
collectors:
  - uses: github://earthly/lunar-lib/collectors/sonarqube@main
    include: [api, config, github-app]    # or `exclude: [...]`
    with:
      project_key: "myorg_backend"
```

If neither is set, all sub-plugins run.

## Tag Matching with `on:`

Every collector / policy / initiative targets components by tags:

```yaml
on: [backend, go]                                                # array form (OR)
on: "domain:engineering AND NOT domain:engineering.experimental"  # expression form
```

| Prefix | Meaning |
|--------|---------|
| `domain:foo` | Component is in domain `foo` (or sub-domain) |
| `component:github.com/foo/bar` | Specific component |
| `collector:foo` | Same components as collector `foo` |
| `policy:foo` | Same components as policy `foo` |

Custom tags come from `components[*].tags` or from catalogers (e.g., `github-org` auto-tags by language). For edge cases, use the `references/` files first; if needed, see the hosted documentation backup.

## `runs_on:` — PRs vs Default Branch

```yaml
- uses: ./collectors/expensive-scan
  runs_on: [default-branch]   # values: prs, default-branch (default: both)
```

## Enforcement Ladder

Walk new policies up over weeks — never start at `block-pr`:

| Level | Effect |
|-------|--------|
| `draft` | Invisible to teams (for testing) |
| `score` | Contributes to score; no PR comments |
| `report-pr` | Comments on PRs; doesn't block |
| `block-pr` | Blocks PR merges |
| `block-release` | Blocks releases (`lunar policy ok-release`) |
| `block-pr-and-release` | Both |

## Branch Refs — Cleanup is Mandatory

`@<branch>` refs are fine for testing unmerged plugins, but **must be cleaned up** or the next `lunar hub pull` fails:

- **Existing plugin on `@main`**: revert to `@main` after testing.
- **New plugin not yet on `@main`**: remove the entry entirely; re-add after the lunar-lib PR merges.

## Catalog Merge Precedence

When the same component appears in multiple places, later wins:

1. Catalogers (in declared order)
2. `lunar.yml` files in component repos
3. `domains:` / `components:` in `lunar-config.yml`

So bulk-import via a cataloger like `github-org`, then override owner / domain / tags in `components:` for bespoke cases.

## Per-Input Overrides for Shared Plugins

Same plugin, two instances with distinct `name:` and `with:`:

```yaml
policies:
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

## Local Validation & Testing

```bash
lunar config validate                                        # syntax + structure
lunar config show                                            # merged plugin structure
lunar collector dev <name> --component github.com/org/repo   # try a collector
lunar policy dev   <name> --component-json path/to.json      # try a policy

# End-to-end: pipe collector output into policy
lunar collector dev my-collector --component github.com/org/repo \
  | lunar policy dev my-policy --component-json -
```

After merging a config-repo PR, verify the CI step that runs `lunar hub pull` succeeded. If it fails, the hub won't pick up the changes.

## Best Practices

1. Pin plugins to tags (`@v1.1.0`) in production; reserve `@main` / `@<branch>` for short testing windows.
2. Clean up branch refs after testing — they break `lunar hub pull` when the branch is deleted.
3. Walk enforcement up: `draft` → `score` → `report-pr` → `block-pr`.
4. Prefer `domain:` tags over component lists — new components inherit automatically.
5. Group related policies under an `initiative:` so scoring rolls them up.
6. Validate locally with `lunar config validate` before pushing.
7. One config repo per Lunar Hub.

## Reference Documentation

The `references/` files are the primary source:

- [references/about-lunar.md](references/about-lunar.md) — Platform overview
- [references/core-concepts.md](references/core-concepts.md) — Component JSON, hooks, enforcement, catalog basics
- [references/collector-reference.md](references/collector-reference.md) — Collector plugin config
- [references/policy-reference.md](references/policy-reference.md) — Policy plugin config
- [references/cataloger-reference.md](references/cataloger-reference.md) — Cataloger plugin config

## Hosted Documentation Backup

Only if `references/` does not answer the question, fetch:

- <https://docs-lunar.earthly.dev/llms.txt> — Index of every Lunar doc page
- <https://docs-lunar.earthly.dev/configuration/lunar-config.md> — Top-level schema
- <https://docs-lunar.earthly.dev/configuration/lunar-config/collectors.md> / `.../policies.md` / `.../catalogers.md` — Plugin sections
- <https://docs-lunar.earthly.dev/configuration/lunar-config/on.md> — Tag-matching syntax
- <https://docs-lunar.earthly.dev/configuration/lunar-config/images.md> — Default images, `native` mode

If a page still lacks enough context, ask the docs a specific, self-contained question with `?ask=<question>` on that page URL, for example:

```text
GET https://docs-lunar.earthly.dev/configuration/lunar-config.md?ask=How%20do%20I%20configure%20collector%20and%20policy%20targeting%3F
```

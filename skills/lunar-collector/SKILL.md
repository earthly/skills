---
name: lunar-collector
description: Create Lunar collector plugins that gather SDLC metadata for guardrail enforcement. Use when building collectors (Bash scripts) that collect data from repositories, CI pipelines, or external APIs and write to the Component JSON. Covers hook types (code, cron, ci-after-command), the `lunar collect` command, plugin structure, containerization, and best practices.
---

# Lunar Collector Skill

Create collector plugins for Earthly Lunar—Bash scripts that gather SDLC metadata and write it to the Component JSON for policy evaluation.

## Quick Start

1. Read [about-lunar.md](references/about-lunar.md) for platform overview
2. Read [core-concepts.md](references/core-concepts.md) for architecture and key entities
3. Read [collector-reference.md](references/collector-reference.md) for comprehensive collector documentation

## Collector Basics

A collector is a Bash script that:
1. Gathers data (from files, CI artifacts, external APIs)
2. Writes to the Component JSON using `lunar collect`

```bash
#!/bin/bash
set -e

if [ -f ./README.md ]; then
  lunar collect -j ".repo.readme_exists" true \
                   ".repo.readme_num_lines" "$(wc -l < ./README.md)"
else
  lunar collect -j ".repo.readme_exists" false
fi
```

## Plugin Structure

```
my-collector/
├── lunar-collector.yml    # Required: plugin config
├── main.sh                # Main script
├── Dockerfile             # Optional: for containerization
├── README.md              # Documentation
└── install.sh             # Optional: install dependencies
```

**lunar-collector.yml:**
```yaml
version: 0
name: my-collector
description: Collects X data
author: team@example.com

default_image: earthly/lunar-scripts:1.0.0

collectors:
  - name: my-collector
    mainBash: main.sh
    hook:
      type: code  # or: cron, ci-after-command, ci-after-job, etc.

inputs:
  threshold:
    description: Minimum threshold
    default: "10"
```

## Hook Types

| Hook | Trigger | Use Case |
|------|---------|----------|
| `code` | Git push | File analysis, config parsing |
| `cron` | Schedule | External API queries |
| `ci-after-command` | After CI command | Capture test coverage, scan results |
| `ci-after-job` | After CI job | Job-level artifact collection |

### CI Command Hooks — Structured Matching

Command hooks (`ci-before-command` / `ci-after-command`) use **structured matching** instead of regex:

```yaml
hook:
  type: ci-after-command
  binary:
    name: go          # Exact binary name (or name_pattern for regex)
  args:
    - value: test     # Positional arg (or value_pattern for regex)
    - flag: --cover   # Flag arg (or flag_pattern for regex)
```

**Key points:**
- `binary.name` / `binary.name_pattern`: match the binary (exact or regex)
- `args[].value` / `args[].value_pattern`: match positional args (in order)
- `args[].flag` / `args[].flag_pattern`: match flags (any order)
- `envs[].name` + `envs[].value`: match environment variables
- All matchers are AND-ed; use regex alternation for OR (e.g., `flag_pattern: ^(-f|--file)$`)
- Omitting binary/args matches all commands

> The old `pattern: <regex>` form for command hooks is **deprecated**. Always use the structured form.

## The `lunar collect` Command

```bash
# String value
lunar collect ".repo.language" "go"

# JSON values (use -j)
lunar collect -j ".repo.readme_exists" true
lunar collect -j ".coverage.percentage" 85.5

# Multiple values
lunar collect -j ".repo.readme_exists" true ".repo.readme_lines" 150

# Pipe JSON from stdin
cat results.json | lunar collect -j ".test.results" -
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LUNAR_COMPONENT_ID` | Component identifier |
| `LUNAR_COMPONENT_PR` | PR number (if in PR context) |
| `LUNAR_COMPONENT_GIT_SHA` | Git SHA being evaluated |
| `LUNAR_PLUGIN_ROOT` | Plugin root directory |
| `LUNAR_SECRET_<NAME>` | Secrets |

Inputs are available as uppercase environment variables (e.g., `THRESHOLD` for input `threshold`).

## Reference Documentation

For detailed information, read these files in the `references/` directory:

| File | Content |
|------|---------|
| [about-lunar.md](references/about-lunar.md) | Platform overview, why Lunar exists |
| [core-concepts.md](references/core-concepts.md) | Architecture, Component JSON, hooks, enforcement levels |
| [collector-reference.md](references/collector-reference.md) | **Complete collector guide** - hooks, environment variables, patterns |
| [component-json/conventions.md](references/component-json/conventions.md) | Component JSON schema design principles, presence detection, source metadata |
| [component-json/structure.md](references/component-json/structure.md) | Component JSON schema categories (.repo, .k8s, .sca, etc.) with examples |
| [strategies.md](references/strategies.md) | Implementation strategies (CI detection, file parsing, API integration) |
| [collector-README-template.md](references/collector-README-template.md) | README template for collector plugins |

## Full Lunar Documentation

For the complete Lunar platform documentation including installation, configuration, CLI reference, and SDK details, see [docs/SUMMARY.md](docs/SUMMARY.md).

## Local Development & Testing

Run collectors locally to test before deploying. Commands must be run from a directory containing `lunar-config.yml`.

**Prerequisites:**
- Set `LUNAR_HUB_TOKEN` environment variable for authentication
- Be in a directory with a valid `lunar-config.yml`

**Run a collector against a remote component:**
```bash
lunar collector dev <collector-name> --verbose --component github.com/org/repo
```

**Run a collector against a local directory:**
```bash
lunar collector dev <collector-name> --verbose --component-dir ../path/to/local/repo
```

**Test a CI collector with a fake command:**
```bash
lunar collector dev <collector-name> --fake-ci-cmd "npm test" --component github.com/org/repo
```

**Collector names** are dot-separated (e.g., `k8s.yaml-collection`, `dockerfile.base-images`).

The command outputs the resulting Component JSON to stdout, which can be piped to `lunar policy dev` for end-to-end testing:

```bash
# Against a local repo directory
lunar collector dev my-collector --component-dir ../path/to/repo | \
  lunar policy dev my-policy --verbose --component-json -

# Against a remote component
lunar collector dev my-collector --component github.com/org/repo | \
  lunar policy dev my-policy --verbose --component-json -
```

## Best Practices

1. **Always use `set -e`** - Exit on errors
2. **Use structured JSON** - Group related data together
3. **Include source metadata** - Tool name, version, integration type
4. **Document Component JSON paths** - In README.md
5. **Use `earthly/lunar-scripts:1.0.0`** - Official base image for containerized collectors
6. **Handle missing data gracefully** - Check file existence before processing

## Common Patterns

**File parsing with find command input:**
```yaml
inputs:
  find_command:
    description: Command to find files
    default: "find . -type f -name '*.yaml'"
```

**CI artifact collection:**
```bash
# Hook: ci-after-command, binary.name: go, args: [{value: test}]
if [ -f coverage.out ]; then
  COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
  lunar collect -j ".testing.coverage.percentage" "$COVERAGE"
fi
```

**External API query:**
```bash
RESPONSE=$(curl -fsS -H "Authorization: Bearer $LUNAR_SECRET_API_TOKEN" \
  "https://api.example.com/repos/$LUNAR_COMPONENT_ID/status")
echo "$RESPONSE" | lunar collect -j ".external.status" -
```

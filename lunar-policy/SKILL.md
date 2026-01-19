---
name: lunar-policy
description: Create Lunar policy plugins that enforce engineering standards. Use when building policies (Python scripts) that evaluate Component JSON data and produce pass/fail checks. Covers the lunar_policy SDK (Check class, assertions, Node navigation), enforcement levels, handling missing data, plugin structure, and testing patterns.
---

# Lunar Policy Skill

Create policy plugins for Earthly Lunar—Python scripts that evaluate Component JSON data and produce pass/fail checks for guardrail enforcement.

## Quick Start

1. Read [about-lunar.md](references/about-lunar.md) for platform overview
2. Read [core-concepts.md](references/core-concepts.md) for architecture and key entities
3. Read [policy-reference.md](references/policy-reference.md) for comprehensive policy documentation

## Policy Basics

A policy is a Python script that:
1. Reads data from the Component JSON
2. Makes assertions about that data
3. Produces checks (pass/fail/pending/error/skipped)

```python
from lunar_policy import Check

with Check("readme-exists", "Repository should have a README.md") as c:
    c.assert_true(c.get_value(".repo.readme_exists"), "README.md not found")
```

## Plugin Structure

```
my-policy/
├── lunar-policy.yml       # Required: plugin config
├── checks/                # One file per check (recommended)
│   ├── check_one.py
│   └── check_two.py
├── requirements.txt       # Must include lunar-policy
├── Dockerfile             # Optional: for custom dependencies
└── README.md              # Documentation
```

**lunar-policy.yml:**
```yaml
version: 0
name: my-policy
description: Validates X requirements
author: team@example.com

default_image: earthly/lunar-scripts:1.0.0

policies:
  - name: check-one
    description: Validates X exists
    mainPython: checks/check_one.py

  - name: check-two
    description: Ensures Y meets threshold
    mainPython: checks/check_two.py

inputs:
  min_coverage:
    description: Minimum required coverage
    default: "80"
```

**requirements.txt:**
```
lunar-policy==0.2.2
```

## The Check Class

### Data Access

```python
# Get value (raises NoDataError if missing → pending)
readme_exists = c.get_value(".repo.readme_exists")

# Get value with default (never goes pending)
replicas = c.get_value_or_default(".k8s.replicas", 1)

# Check existence
if c.exists(".coverage"):
    # Data is available

# Get node for navigation
k8s = c.get_node(".k8s.workloads")
for workload in k8s:
    name = workload.get_value(".name")
```

### Assertions

```python
c.assert_true(value, "Failure message")
c.assert_false(value, "Failure message")
c.assert_equals(value, expected, "Failure message")
c.assert_exists(".path", "Failure message")  # Path must exist
c.assert_contains(list_or_str, item, "Failure message")
c.assert_greater(value, threshold, "Failure message")
c.assert_greater_or_equal(value, threshold, "Failure message")
c.assert_match(value, r"pattern", "Failure message")
c.fail("Unconditional failure")
c.skip("Check doesn't apply")  # Only for applicability filtering
```

## Enforcement Levels

| Level | PR Comments | Blocks PR | Blocks Release |
|-------|-------------|-----------|----------------|
| `draft` | No | No | No |
| `score` | No | No | No |
| `report-pr` | Yes | No | No |
| `block-pr` | Yes | Yes | No |
| `block-release` | No | No | Yes |
| `block-pr-and-release` | Yes | Yes | Yes |

## Handling Missing Data

**Pattern 1: Required data with assert_exists**
```python
c.assert_exists(".coverage", "Coverage data not found")
coverage = c.get_value(".coverage.percentage")
```

**Pattern 2: Optional data with exists check**
```python
if c.exists(".coverage"):
    coverage = c.get_value(".coverage.percentage")
    c.assert_greater_or_equal(coverage, 80, "Coverage too low")
```

**Pattern 3: Object presence = signal (CI collectors)**
```python
# SCA scanner only writes data when it runs
c.assert_exists(".sca", "SCA scanner must run in CI")
```

## Configurable Inputs

```python
from lunar_policy import Check, variable_or_default

min_coverage = int(variable_or_default("minCoverage", "80"))
c.assert_greater_or_equal(coverage, min_coverage, f"Coverage {coverage}% below {min_coverage}%")
```

## Reference Documentation

For detailed information, read these files in the `references/` directory:

| File | Content |
|------|---------|
| [about-lunar.md](references/about-lunar.md) | Platform overview, why Lunar exists |
| [core-concepts.md](references/core-concepts.md) | Architecture, Component JSON, enforcement levels |
| [policy-reference.md](references/policy-reference.md) | **Complete policy guide** - Check class API, patterns, testing |
| [component-json-conventions.md](references/component-json-conventions.md) | Schema conventions, presence detection, boolean vs object patterns |
| [component-json-structure.md](references/component-json-structure.md) | Standard categories (.repo, .k8s, .sca, etc.) with policy paths |
| [strategies.md](references/strategies.md) | Implementation strategies |
| [policy-README-template.md](references/policy-README-template.md) | README template for policy plugins |

## Local Development & Testing

Run policies locally to test before deploying. Commands must be run from a directory containing `lunar-config.yml`.

**Prerequisites:**
- Set `LUNAR_HUB_TOKEN` environment variable for authentication
- Be in a directory with a valid `lunar-config.yml`

**Run a policy with Component JSON from a file:**
```bash
lunar policy dev <policy-name> --verbose --component-json path/to/component.json
```

**Run a policy with Component JSON from stdin:**
```bash
lunar policy dev <policy-name> --verbose --component-json -
```

**Run a policy against a remote component:**
```bash
lunar policy dev <policy-name> --verbose --component github.com/org/repo
```

**Policy names** are dot-separated (e.g., `k8s.pdb`, `container.no-latest`).

**End-to-end testing** by piping collector output to policy:
```bash
lunar collector dev my-collector --verbose --component github.com/org/repo | \
  lunar policy dev my-policy --verbose --component-json -
```

The command outputs check results as text showing pass/fail status and failure messages.

**Exit codes:** Zero on success (even if checks fail—policy ran correctly), non-zero only on errors (e.g., invalid syntax, missing dependencies, uncaught exception).

## Best Practices

1. **One check per policy entry** - Enables selective `include`/`exclude`
2. **Descriptive check names and messages** - Include context in failures
3. **Use `assert_exists` for required data** - Not `get_value_or_default`
4. **Handle missing data appropriately** - See patterns above
5. **Keep policies fast** - No external API calls (use collectors instead)
6. **Use `earthly/lunar-scripts:1.0.0`** - Official base image

## Common Patterns

**Iterating over collections:**
```python
for workload in c.get_node(".k8s.workloads"):
    name = workload.get_value_or_default(".name", "<unknown>")
    for container in workload.get_node(".containers"):
        has_resources = container.get_value_or_default(".has_resources", False)
        c.assert_true(has_resources, f"{name}: container missing resource limits")
```

**Allow-list validation (error if empty):**
```python
allowed_str = variable_or_default("allowed_registries", "")
allowed = [r.strip() for r in allowed_str.split(",") if r.strip()]
if not allowed:
    raise ValueError("'allowed_registries' must be configured")
if registry not in allowed:
    c.fail(f"Registry '{registry}' not in allowed list")
```

**Testable policy function:**
```python
from lunar_policy import Check, Node, CheckStatus

def check_readme(node=None):
    c = Check("readme-exists", node=node)
    with c:
        c.assert_true(c.get_value(".repo.readme_exists"), "README not found")
    return c

if __name__ == "__main__":
    check_readme()

# Test:
def test_readme_passes():
    node = Node.from_component_json({"repo": {"readme_exists": True}})
    check = check_readme(node)
    assert check.status == CheckStatus.PASS
```

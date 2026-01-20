# Python Policy SDK

The `lunar_policy` Python package provides utilities for working with Lunar policies, allowing you to load, query, and make assertions about component metadata, such as the [component JSON](../key-concepts/component-json.md).

For the reference documentation check out:

* [Check](check.md) - Main class for making assertions about component data
* [Node](node.md) - Navigate and explore JSON data
* [CheckStatus](check-status.md)
* [NoDataError](no-data-error.md)
* [SkippedError](skipped-error.md)

## Installation

When using the official `earthly/lunar-scripts` Docker image (recommended), the `lunar-policy` package is already pre-installed. See [Images](../lunar-config/images.md) for details on configuring default images.

For native execution or custom images, the package is available through pip:

```bash
pip install lunar-policy
```

## Policy environment

Earthly Lunar executes policies in an environment set up with the following variables:

- `LUNAR_HUB_HOST`: The host of the Lunar Hub.
- `LUNAR_HUB_INSECURE`: Whether to skip SSL verification of the Lunar Hub.
- `LUNAR_POLICY_NAME`: The name of the policy being executed.
- `LUNAR_INITIATIVE_NAME`: The name of the initiative the policy belongs to.
- `LUNAR_POLICY_OWNER`: The owner of the policy.
- `LUNAR_COMPONENT_ID`: The ID of the component being checked in `github.com/.../...` format.
- `LUNAR_COMPONENT_DOMAIN`: The domain of the component.
- `LUNAR_COMPONENT_OWNER`: The owner of the component.
- `LUNAR_COMPONENT_PR`: The PR number of the component, if applicable.
- `LUNAR_COMPONENT_GIT_SHA`: The Git SHA of the component that the policy is being executed for.
- `LUNAR_COMPONENT_TAGS`: The tags of the component.
- `LUNAR_COMPONENT_META`: The metadata of the component as a JSON object.
- `LUNAR_BUNDLE_PATH`: Used internally by Lunar to pass in the component JSON and the deltas to the policy.
- `LUNAR_SECRET_<name>`: Any secret set in the Lunar Hub for the policy, via `HUB_POLICY_SECRETS=<name>=<value>;...`.

{% hint style='warn' %}
##### Important

Note that since policies are re-evaluated frequently as each piece of data becomes available, it is strongly recommended to design your policy execution to be fast (no external API calls, no heavy processing, etc.). If you need to perform any expensive operations, consider using a collector instead, and passing the necessary data via the component JSON.
{% endhint %}

{% hint style='warn' %}
##### Important

Policies are re-evaluated between component data collections. This means that not all data is available from the beginning, and your policy should correctly report a `pending` status when it cannot make a decision yet. Much of this is handled automatically for you - see [Handling Missing Data](#handling-missing-data) below for more details.
{% endhint %}

## Core Components

The Policy SDK provides several key classes to help you write policies:

### Check

The `Check` class provides a fluent interface for making assertions about policy data. It tracks accessed data within the component JSON for traceability purposes.

```python
from lunar_policy import Check

# Create a check with a name and optional description
with Check("my-check", "Validates important properties") as check:
    # Get data using JSONPath
    value = check.get_value(".path.to.data")
    
    # Make assertions
    check.assert_equals(check.get_value(".api.endpoints[0].method"), "GET")
    check.assert_greater_or_equal(value, 50)
    check.assert_contains(check.get_value(".api.endpoints[0].path"), "/")
```

👉 For detailed reference, see the [Check reference documentation](check.md).

### Node

The `Node` class is used to navigate and explore JSON data.

```python
from lunar_policy import Check, Node

with Check("my-check", "Validates important properties") as check:
    # Create a node from a check
    node = check.get_node(".path.to.data")
    if node.exists():
        # Get the value of the node
        value = node.get_value()
        # Make assertions on the node
        node.assert_equals(value, "expected_value")
```

👉 For detailed reference, see the [Node reference documentation](node.md).

### NoDataError

The `NoDataError` exception is used to indicate that required data for a policy check is still pending (hasn't been collected yet).

👉 For detailed reference, see the [NoDataError reference documentation](no-data-error.md).

### SkippedError

The `SkippedError` exception is used to indicate that a check should be skipped because it is not applicable to the current component (e.g., Go-specific checks on a Java repository).

👉 For detailed reference, see the [SkippedError reference documentation](skipped-error.md).

## Automatic Data Loading

When a policy is executed through Lunar Hub, Lunar passes in the relevant context via `LUNAR_BUNDLE_PATH`. This context includes the [component JSON](../key-concepts/component-json.md) for the component that is being checked. When you create a `Check` instance, the library automatically loads this data under the hood when `node` is not provided.

## Executing Policies Locally

To execute a policy locally for testing purposes, you can use the `lunar` CLI.

```bash
lunar policy dev --component-json path/to/component.json ./path/to/policy.py
```

If you would like to use the real component JSON of one of your components, you can do so via the command:

```bash
lunar policy dev --component github.com/my-org/my-repo ./path/to/policy.py
```

## Check outcomes

Checks can result in the following possible outcomes:

- `pass`: The check passed successfully. All assertions within the check were satisfied.
- `fail`: The check failed. One or more assertions within the check were not satisfied. This generally means that the developer working on the component needs to fix the issue.
- `pending`: The check could not be completed due to data not being available yet. This is due collection not having finished yet (code or cron collectors are still running, or the CI is still running).
- `error`: The check encountered an error during execution. This indicates an unexpected error occurred during the check execution, such as a runtime exception. This is generally a bug either in the collection logic or in the policy code.
- `skipped`: The check was intentionally skipped because it is not applicable to the current component. Skipped checks are not shown to end-user developers but are available in the SQL API for analysis purposes.

## Handling Missing Data

Lunar makes a clear distinction between temporarily missing component JSON data (data is pending), permanently missing component JSON data, and failing component JSON data. This is needed under the hood to be able to provide partial policy results while collectors are still running. Policies that have enough data will provide accurate results, while policies that don't have enough data will often report a `pending` status.

Here is a breakdown of how the different statuses are determined:

* Temporarily missing data (`pending` status): This is when some or all of the component JSON data required for assertions is not present, but the collector are still running. In this case, the check will report a `pending` status for now, thanks to methods like `get_value`, `exists` and `assert_exists` automatically raising `NoDataError` when not enough data is available and collectors are still running.
* Permanently missing data - sometimes expected on failures (`fail` status): This is when some of the component JSON data required for assertions is not present, and the collectors have finished running. `assert_exists` will report a failure in this case.
* Permanently missing data - unexpected (`error` status): This is when some of the component JSON data required for assertions is not present, and the collectors have finished running. `get_value` will report a `ValueError` after collectors finished, resulting in an `error` status.
* Failing data (`fail` status): This is when the data is present, but the assertions (e.g. `assert_equals`, `assert_true`, etc.) fail.

This means that you should use `get_value` to access data when you are assuming that the data will eventually be provided by a collector. Or use `assert_exists` (or `exists` within an if condition) to test for the existence of data if that's what the pass/fail outcome of the check should depend on.

### Best Practices for Handling Missing Data

Below are examples demonstrating different approaches to handling missing data in policies:

#### Bad Approach: Blindly Assuming Data Exists

This approach incorrectly assumes all fields exist after retrieving an object, which can lead to errors when data is temporarily missing:

```python
with Check("api-security-check") as check:
    # Bad: Gets the entire API object once and assumes all fields exist
    api = check.get_value(".api")
    
    # These will cause policy errors if api is None or missing expected fields
    check.assert_true(api["requires_auth"], "API should require authentication")
    rate_limit = api["rate_limit"]
    check.assert_equals(rate_limit, 100, f"API rate limit should be 100, but found {rate_limit}")
    check.assert_contains(api["security_headers"], "Content-Security-Policy")
```

#### Good Approach: Using get_value, get_node, exists, and assert_exists for Data Access

This approach uses targeted field access and relies on the Check API to handle missing data automatically:

```python
with Check("api-security-check") as check:
    # Direct field access - raises NoDataError if path doesn't exist yet
    check.assert_true(check.get_value(".api.requires_auth"), "API should require authentication")
    
    # Test for data existence when that's the actual requirement
    check.assert_exists(".api.requires_auth", "API is missing requires_auth field")
    
    # Conditional checks using exists() - only run assertions if data exists
    if check.exists(".api"):
        check.assert_true(check.get_value(".api.requires_auth"), "API should require authentication")
    
    # Working with nodes + exists() to navigate and explore data
    api_node = check.get_node(".api")
    if api_node.exists():
        rate_limit = api_node.get_value(".rate_limit") 
        check.assert_equals(rate_limit, 100, f"API rate limit should be 100, but found {rate_limit}")
        check.assert_contains(api_node.get_value(".security_headers"), "Content-Security-Policy")
```

## Writing Unit Tests for Policies

Let's assume that we have the following policy:

```python
from lunar_policy import Check, Node

def verify_readme(node=None):
    check = Check("readme-long-enough", node=node)
    with check:
        lines = check.get_value('.readme.lines')
        check.assert_greater_or_equal(
            lines, 50,
            f'README.md should have at least 50 lines. Current count: {lines}'
        )
    return check

if __name__ == "__main__":
    verify_readme()
```

Here's an example showing how to write unit tests:

```python
import unittest
from lunar_policy import Check, Node, CheckStatus

class TestReadmePolicy(unittest.TestCase):
    def test_not_long_enough(self):
        component_json = {
            "readme": {
                "lines": 49,
                "missing": False
            }
        }
        node = Node.from_component_json(component_json)
        check = verify_readme(node)
        
        # Verify the check failed because the README isn't long enough
        self.assertEqual(check.status, CheckStatus.FAIL)
        self.assertEqual(check.failure_reasons[0], "README.md should have at least 50 lines. Current count: 49")

if __name__ == "__main__":
    unittest.main()
```

You can run the test with:

```bash
python -m unittest test_readme_policy.py
```

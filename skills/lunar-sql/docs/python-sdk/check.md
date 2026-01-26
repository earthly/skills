# Check Class Reference

The `Check` class provides a fluent interface for making assertions about policy data. The object keeps track of accessed data within the component JSON and records that for traceability purposes. The final result of a check will have not just the status (`pass`, `fail`, `pending`, `error`, or `skipped`), but complete information about which JSON paths were used to reach this conclusion. Designed to be used as a context manager with Python's `with` statement, the `Check` class automatically handles `NoDataError` (turns it into `pending` status), `SkippedError` (turns it into `skipped` status), and tracks result statuses.

## Constructor

```python
Check(name, description=None, node=None)
```

Creates a new check instance that can be used to make assertions about the component data. If the component data is not provided, it will be loaded automatically from the environment via `LUNAR_BUNDLE_PATH`.

- **name** (str): A unique identifier for this check
- **description** (str, optional): A human-readable description of what this check validates
- **node** (Node, optional): An alternate Node instance to use for this check, instead of loading it from the environment. Useful for unit testing.

## Context Manager

The `Check` class is designed to be used as a context manager with Python's `with` statement. This is the recommended way to use the class as it ensures proper setup, teardown, and error handling.

```python
with Check("check-name", "Check description") as check:
    # Make assertions using check methods
    check.assert_true(check.get_value(".path.to.data"))
```

When used as a context manager, the `Check` class:

1. **On enter**: Sets up the check context and automatically loads component data if not provided
2. **On exit**: Records the check result with its status and all accessed data paths
3. **Exception handling**:
   - Catches and suppresses `NoDataError`, and sets the check status to `pending`, if collectors are still running.
   - Otherwise, propagates `NoDataError` and records as `error` status since `NoDataError` is unexpected after collectors finished.
   - Catches and suppresses `SkippedError`, sets the check status to `skipped`, and drops any previously recorded assertions.
   - Propagates other exceptions and records them as `error` status with the exception message

## JSONPath Compatibility

We do not support the entirety of JSONPath as defined in RFC 9535. However, we do support a strict subset of the language:

* `$` is implicit at the beginning of paths.
* You can access members of an object by key using either `.dot.syntax` or `['literal']['syntax']`.
* You can index into an array by number only. No wildcards or filters allowed.

## Data Access Methods

### get_value

```python
get_value(path=".")
```

Retrieves data from the component JSON using a JSONPath expression. This method raises `ValueError` if the path is invalid.

Missing data behavior:

* Raises `NoDataError` **before** collectors finished (results in `pending` status).
* Raises `ValueError` **after** collectors finished (results in `error` status).

This means that `get_value` is best used when you are assuming that the data will eventually be provided by a collector.

- **path** (str): JSONPath expression to query the component data (default: "." for root)
- **Returns**: The value at the specified path, or raises `NoDataError` or `ValueError`.

Example:
```python
# Get the number of lines in the README
lines = check.get_value(".readme.lines")

# Get the entire component data
all_data = check.get_value()
```

### get_value_or_default

```python
get_value_or_default(path=".", default=None)
```

Retrieves data from the component JSON using a JSONPath expression. If the value is missing for any reason, it returns the specified default instead.

- **path** (str): JSON path relative to the root of the component JSON (default: ".")
- **default**: The value to return if there is no value at this path

Example:
```python
# Given this component JSON:
# {
#     "existing": {
#         "value": "hello"
#     }
# }

val = node.get_value_or_default(".existing.value", "goodbye") # val will be "hello"
val = node.get_value_or_default(".missing", "goodbye") # val will be "goodbye"
```

### get_all_values

```python
get_all_values(path=".")
```

Retrieves data from the component JSON deltas using a JSONPath expression. Use this when you collect something at the same path multiple times to help assert on all values. This method raises `ValueError` if the path is invalid.

Missing data behavior:

* Raises `NoDataError` **before** collectors finished (results in `pending` status).
* Raises `ValueError` **after** collectors finished (results in `error` status).

This means that `get_all_values` is best used when you are assuming that the data will eventually be provided by a collector.

- **path** (str): JSONPath expression to query the component data (default: "." for root)
- **Returns**: A list of all values found at the specified path, or raises `NoDataError` or `ValueError`.

Example:
```python
# Get the number of lines in the README
lines = check.get_all_values(".readme.lines")
```

### get_node

```python
get_node(path)
```

Gets a Node at the given path. Uses lazy evaluation - no data access or path tracking until value is needed.

- **path** (str): JSONPath expression to query the component data
- **Returns**: A `Node` instance at the specified path
- **Raises**: `ValueError` if the path syntax is invalid

The returned Node object provides methods like `get_value()`, `get_node()`, `exists()`, and supports iteration. See the [Node class documentation](node.md) for complete details.

Example:
```python
config_node = check.get_node(".config")
if config_node.exists():
    config = config_node.get_value()
```


### exists

```python
exists(path=".")
```

Returns `True` if the path exists in the component data.

Missing path behavior:

* Raises `NoDataError` **before** collectors finished (results in `pending` status).
* Returns `False` **after** collectors finished.

## Node-like Iteration Methods

The `Check` class supports iteration methods that make it behave like a Node for duck-typing compatibility. These methods allow you to iterate over the root component data.

### Iterating over Check Fields

```python
for item in check:
    # Process item
```

Makes Check iterable like a Node. For dictionaries, yields keys. For arrays, yields Node objects.

- **For dict-like data**: Yields string keys
- **For array-like data**: Yields Node objects for each array element
- **Raises**: `ValueError` if the component data is not a dict or array, `NoDataError` if data is not available yet

Example:
```python
# Iterate over top-level keys in component data
with Check("iterate-check") as check:
    for key in check:
        print(f"Top-level key: {key}")
```

### items

```python
items()
```

Get key-value pairs when the Check points to dict-like component data.

- **Returns**: Iterator of (key, Node) tuples for dict-like data
- **Raises**: `ValueError` if the component data is not a dictionary, `NoDataError` if data is not available yet

Example:
```python
with Check("items-check") as check:
    for key, value_node in check.items():
        value = value_node.get_value()
        print(f"{key}: {value}")
```

## Control Flow Methods

### skip

```python
skip(reason="")
```

Unconditionally skips the check with an optional reason. When called, this method raises a `SkippedError` exception that is caught by the Check's context manager. The check is effectively canceled - any assertions (passed or failed) that may have been recorded before `skip` is called are dropped/ignored, and the final status of the check is marked as `skipped`.

Skipped checks are not shown to end-user developers but are available in the SQL API for analysis purposes.

- **reason** (str, optional): An optional message explaining why the check was skipped

Example:
```python
if not check.exists(".go"):
    check.skip("No Go files exist in repository")

if not check.exists(".kubernetes.manifests"):
    check.skip("No Kubernetes manifests exist")
```

### fail

```python
fail(message)
```

Unconditionally fails the check with a given message.

- **message** (str): The message to display when the check fails

Example:
```python
if my_complex_condition():
    check.fail("This is a policy failure")
```

## Assertion Methods

All assertion methods have these common parameters:

- **value**: The value to be asserted
- **failure_message** (str, optional): Custom message to display if the assertion fails

Additionally, all assertion methods raise `NoDataError` if the path doesn't exist in the component data.

### assert_true

```python
assert_true(value, failure_message=None)
```

Asserts that a value is `True`.

Example:
```python
# Assert that authentication is required
check.assert_true(check.get_value(".api.auth_required"), "API should require authentication")
```

### assert_false

```python
assert_false(value, failure_message=None)
```

Asserts that a value is `False`.

Example:
```python
# Assert that the README.md file is not missing
check.assert_false(check.get_value(".readme.missing"), "README.md file should exist")
```

### assert_equals

```python
assert_equals(value, expected, failure_message=None)
```

Asserts that a value equals the expected value.

- **expected**: The expected value to compare against

Example:
```python
# Assert that the API endpoint uses GET method
check.assert_equals(check.get_value(".api.endpoints[0].method"), "GET", "Endpoint should use GET method")
```

### assert_exists

```python
assert_exists(path, failure_message=None)
```

Asserts that a path exists in the component data. If the path was not found, this method raises `NoDataError` before collectors finished, and fails the check after collectors finished.

Missing path behavior:

* Raises `NoDataError` **before** collectors finished (results in `pending` status).
* Fails the check **after** collectors finished (results in `FAIL` status).

Example:
```python
check.assert_exists(".api", "API data not found")
```

### assert_contains

```python
assert_contains(value, expected, failure_message=None)
```

Asserts that a value contains the expected value (works for strings, lists, etc.).

- **expected**: The value that should be contained

Example:
```python
# Assert that the endpoint path contains a specific substring
check.assert_contains(check.get_value(".api.endpoints[0].path"), "/users")

# Assert that the tags list contains a specific tag
check.assert_contains(check.get_value(".tags"), "api")
```

### assert_greater

```python
assert_greater(value, expected, failure_message=None)
```

Asserts that a numeric value is greater than the expected value.

- **expected**: The threshold value to compare against

Example:
```python
# Assert that the code coverage is greater than 80%
check.assert_greater(check.get_value(".coverage.percentage"), 80, "Code coverage should be greater than 80%")
```

### assert_greater_or_equal

```python
assert_greater_or_equal(value, expected, failure_message=None)
```

Asserts that a numeric value is greater than or equal to the expected value.

- **expected**: The threshold value to compare against

Example:
```python
# Assert that README has at least 50 lines
check.assert_greater_or_equal(check.get_value(".readme.lines"), 50, "README should have at least 50 lines")
```

### assert_less

```python
assert_less(value, expected, failure_message=None)
```

Asserts that a numeric value is less than the expected value.

- **expected**: The threshold value to compare against

Example:
```python
# Assert that cyclomatic complexity is less than 15
check.assert_less(check.get_value(".complexity.cyclomatic"), 15, "Cyclomatic complexity should be less than 15")
```

### assert_less_or_equal

```python
assert_less_or_equal(value, expected, failure_message=None)
```

Asserts that a numeric value is less than or equal to the expected value.

- **expected**: The threshold value to compare against

Example:
```python
# Assert that build time is at most 5 minutes
check.assert_less_or_equal(check.get_value(".build.duration_minutes"), 5, "Build should take at most 5 minutes")
```

### assert_match

```python
assert_match(value, pattern, failure_message=None)
```

Asserts that a string value matches a regular expression pattern.

- **pattern** (str): A regular expression pattern to match against

Example:
```python
# Assert that version follows semantic versioning
check.assert_match(check.get_value(".version"), r"^\d+\.\d+\.\d+$", "Version should follow semantic versioning")
```

## Instance Properties

After a check has been executed (typically after exiting the `with` context), the following properties are available:

### status

```python
status: CheckStatus
```

The final status of the check after execution.

- **Type**: `CheckStatus`
- **Values**: `PASS`, `FAIL`, `PENDING`, `ERROR`, or `SKIPPED`

### failure_reasons

```python
failure_reasons: List[str]
```

The reasons for failure when the check status is `FAIL`. This property contains an array of detailed error messages from any failed assertions within the check.

- **Type**: `List[str]`
- **Available when**: `status` is `CheckStatus.FAIL`

### name

```python
name: str
```

The name of the check as specified in the constructor.

- **Type**: `str`

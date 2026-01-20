# SkippedError Class Reference

The `SkippedError` exception is used to indicate that a check should be skipped and not evaluated. This is typically used for applicability detection - when a check is not relevant to the current component (e.g., Go-specific checks on a Java repository, or Kubernetes checks when no manifests are present).

This exception is automatically caught by the `Check` context manager, which:
- Sets the check status to `skipped`
- Drops any previously recorded assertions (both passed and failed)
- Suppresses the exception so it doesn't propagate

Skipped checks are not shown to end-user developers but are available in the SQL API for analysis and debugging purposes.

## Constructor

```python
SkippedError(message=None)
```

- **message** (str, optional): A message describing why the check was skipped

## Usage

The `SkippedError` is typically raised automatically by the `Check.skip()` method rather than being raised directly:

```python
# Recommended approach - use Check.skip()
with Check("go-version-check") as check:
    if not check.exists(".go"):
        check.skip("No Go files found in repository")
    
    # This code won't execute if skip() was called
    go_version = check.get_value(".go.version")
    check.assert_match(go_version, r"^1\.(19|20|21)$")
```

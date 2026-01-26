# CheckStatus Class Reference

The `CheckStatus` class defines the possible statuses for a check result. It is used to represent the final outcome of a policy check execution.

## Usage

```python
from lunar_policy import CheckStatus
```

## Available Status Values

### PASS

```python
CheckStatus.PASS
```

The check resulted in `pass` status. It passed successfully, so all assertions within the check were satisfied.

### FAIL  

```python
CheckStatus.FAIL
```

The check resulted in `fail` status. It failed, so one or more assertions within the check were not satisfied.

### PENDING

```python
CheckStatus.PENDING
```

The check resulted in `pending` status. It could not be completed due to data not being available. This occurs when required data is not yet available in the component JSON, typically because a code or cron collector has not finished running yet, or because the CI is still running (and a CI collector hasn't triggered yet).

### ERROR

 ```python
 CheckStatus.ERROR
 ```

 The check resulted in `error` status. It encountered an error during execution. This indicates an unexpected error occurred during the check execution, such as a runtime exception.

### SKIPPED

```python
CheckStatus.SKIPPED
```

The check resulted in `skipped` status. The check was intentionally skipped using the `skip()` method, typically because the check is not applicable to the current component (e.g., Go-specific checks on a Java repository). Skipped checks are not shown to end-user developers but are available in the SQL API for analysis purposes.
 
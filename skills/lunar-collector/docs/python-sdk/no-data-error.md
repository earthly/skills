# NoDataError Class Reference

The `NoDataError` exception is used to indicate that there is not enough data to make a determination on whether the check should pass or fail. This is due to the required data not having been collected yet and thus not being present in the component JSON.

This exception is automatically caught by the `Check` context manager, which sets the check status to `pending` if collectors are still running. Note that the `NoDataError` is unexpected after collectors finished, and will result in an `error` status.

The purpose of `NoDataError` is to distinguish between:

1. **Data is pending**: When required data is yet to be collected (for example, a CI collector hasn't triggered yet, or a code collector hasn't finished running yet)
2. **Failed Assertions**: When data is present but doesn't meet the policy requirements (results in `fail` status)

This distinction is important because Lunar re-evaluates policies as data becomes available. A `pending` status indicates that the policy should be re-evaluated when more data is collected, while a `fail` status indicates a definitive policy violation.

## Constructor

```python
NoDataError(message=None)
```

- **message** (str, optional): A message describing why the data is missing

# validate_schema

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

## What this is for and when to use it

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

- Use before writes to compare a DataFrame schema against an expected schema with strict, allow-new-columns, or monitor-only behavior.

## When not to use it

- Do not use for data-value drift, DQ-rule enforcement, or metadata persistence.

## Example

```python
schema_result = validate_schema(df, {"order_id": "string"}, preset="allow_new_columns")
stop_if_failed(schema_result)
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>dataframe</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark, pandas, or dataframe-like object with schema metadata.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>expected_schema</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Mapping of required column names to expected datatype strings.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>preset</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Schema validation intent. ``strict`` blocks missing columns, datatype changes, and unexpected columns. ``allow_new_columns`` blocks missing columns and datatype changes while reporting additional columns as a warning. ``monitor_only`` reports all differences without blocking.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.

## Errors and side effects

**Errors:** ValueError when preset is not one of the supported schema presets.

**Side effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.

## Related functions

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/drift.py#L109-L198">View validate_schema on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str = "strict") -> dict:
    """Validate a dataframe schema using an intent-based preset.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    expected_schema : dict[str, str]
        Mapping of required column names to expected datatype strings.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Schema validation intent. ``strict`` blocks missing columns, datatype
        changes, and unexpected columns. ``allow_new_columns`` blocks missing
        columns and datatype changes while reporting additional columns as a
        warning. ``monitor_only`` reports all differences without blocking.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``checks``, and ``message`` plus detailed schema difference fields.

    Raises
    ------
    ValueError
        If ``preset`` is not one of the supported schema presets.

    Examples
    --------
    >>> validate_schema(df, {"id": "int"}, preset="allow_new_columns")
    {'status': 'passed', 'can_continue': True, ...}
    """
    normalized_preset = str(preset).lower()
    if normalized_preset not in _SCHEMA_PRESETS:
        raise ValueError("preset must be one of: strict, allow_new_columns, monitor_only")

    actual_columns, actual_types = _actual_schema(dataframe)
    actual_set = set(actual_columns)
    expected_names = [str(column) for column in expected_schema]
    expected_set = set(expected_names)

    missing_columns = [column for column in expected_names if column not in actual_set]
    datatype_mismatches = []
    for column, expected_type in expected_schema.items():
        column_name = str(column)
        if column_name in actual_set and column_name in actual_types:
            expected = _normalize_datatype(expected_type)
            actual = actual_types[column_name]
            if actual != expected:
                datatype_mismatches.append({"column": column_name, "expected": expected, "actual": actual})

    checks = []
    for column in missing_columns:
        checks.append({"check": "missing_column", "column": column, "status": "failed", "passed": False})
    for mismatch in datatype_mismatches:
        checks.append({"check": "datatype_mismatch", **mismatch, "status": "failed", "passed": False})
    actual_unexpected = [column for column in actual_columns if str(column) not in expected_set]
    for column in actual_unexpected:
        checks.append({"check": "unexpected_column", "column": column, "status": "warning" if normalized_preset == "allow_new_columns" else "failed", "passed": normalized_preset == "allow_new_columns"})

    blocking = bool(missing_columns or datatype_mismatches)
    if normalized_preset == "strict":
        blocking = blocking or bool(actual_unexpected)
    if normalized_preset == "monitor_only":
        status = "warning" if checks else "passed"
        can_continue = True
    elif blocking:
        status = "failed"
        can_continue = False
    elif normalized_preset == "allow_new_columns" and actual_unexpected:
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True

    message = (
        "Schema validation passed."
        if status == "passed"
        else f"Schema validation {status}: {len(missing_columns)} missing, {len(actual_unexpected)} unexpected, {len(datatype_mismatches)} datatype mismatch(es)."
    )
    return {
        "status": status,
        "can_continue": can_continue,
        "checks": checks,
        "message": message,
        "missing_columns": missing_columns,
        "unexpected_columns": actual_unexpected,
        "datatype_mismatches": datatype_mismatches,
        "preset": normalized_preset,
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.validate_schema`
- Short name: `validate_schema`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `109`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Use in 02_pipeline before write helpers so schema guardrails run before publishing data.
- **inputs:** dataframe, expected_schema mapping, and preset controlling blocking behavior.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.
- **side_effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when preset is not one of the supported schema presets.
- **verification:** Verify can_continue before calling write helpers and pass the result to stop_if_failed when blocking behavior is required.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/drift.py#L109-L198">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/drift.py#L109-L198</a>
- Start line: `109`
- End line: `198`
- Signature:

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str='strict') -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>

</details>

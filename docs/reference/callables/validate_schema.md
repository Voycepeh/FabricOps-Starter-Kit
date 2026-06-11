# validate_schema

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

## Purpose

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

## At a glance

**Use when:**

- Use before writes to compare a DataFrame schema against an expected schema with strict, allow-new-columns, or monitor-only behavior.

**Do not use when:**

- Do not use for DQ-rule enforcement or metadata persistence.

**Example:**

```python
schema_result = validate_schema(df, {"order_id": "string"}, preset="allow_new_columns")
stop_if_failed(schema_result)
```

**Errors:**

ValueError when preset is not one of the supported schema presets.

**Side effects:**

Inspects DataFrame schema only; it does not write metadata, tables, or files.

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Calls

- `fabricops_kit.guardrails._actual_schema`
- `fabricops_kit.guardrails._normalize_datatype`

??? info "Call flow"

    ```text
    validate_schema(...)
    ├── _actual_schema(...)
    │   └── _normalize_datatype(...)
    └── _normalize_datatype(...)
    ```

## Callable implementation

### Function details

- Module: `guardrails`
- Classification: Callable
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `109`
- Signature:

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str='strict') -> dict
```

### Parameters

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

### Returns

Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.

### Notes

No additional callable notes are documented.

### Public callable source code

- Source file path: `src/fabricops_kit/guardrails.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/guardrails.py#L109-L198">View validate_schema on GitHub</a>

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

## Internal implementation summary

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for rule parsing and other.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_normalize_datatype</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_actual_schema</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Rule parsing helpers"

            **`def _normalize_datatype(data_type) -> str`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/guardrails.py#L37-L83)

            ```python
            def _normalize_datatype(data_type) -> str:
                raw = str(data_type).strip().lower()
                raw = re.sub(r"\s+", "", raw)

                decimal_match = re.search(r"decimaltype\((\d+),(\d+)\)|decimal\((\d+),(\d+)\)", raw)
                if decimal_match:
                    precision = decimal_match.group(1) or decimal_match.group(3)
                    scale = decimal_match.group(2) or decimal_match.group(4)
                    return f"decimal({precision},{scale})"

                aliases = {
                    "integertype()": "int",
                    "integertype": "int",
                    "integer": "int",
                    "int32": "int",
                    "int": "int",
                    "longtype()": "bigint",
                    "longtype": "bigint",
                    "long": "bigint",
                    "int64": "bigint",
                    "bigint": "bigint",
                    "stringtype()": "string",
                    "stringtype": "string",
                    "str": "string",
                    "object": "string",
                    "string": "string",
                    "datetype()": "date",
                    "datetype": "date",
                    "date": "date",
                    "timestamptype()": "timestamp",
                    "timestamptype": "timestamp",
                    "timestamp": "timestamp",
                    "datetime64[ns]": "timestamp",
                    "doubletype()": "double",
                    "doubletype": "double",
                    "double": "double",
                    "float64": "double",
                    "floattype()": "float",
                    "floattype": "float",
                    "float32": "float",
                    "float": "float",
                    "booleantype()": "boolean",
                    "booleantype": "boolean",
                    "bool": "boolean",
                    "boolean": "boolean",
                }
                return aliases.get(raw, raw)
            ```

        ??? example "Other helpers"

            **`def _actual_schema(df) -> tuple[list[str], dict[str, str]]`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/guardrails.py#L86-L101)

            ```python
            def _actual_schema(df) -> tuple[list[str], dict[str, str]]:
                schema = getattr(df, "schema", None)
                if schema is not None and hasattr(schema, "fields"):
                    columns = [str(field.name) for field in schema.fields]
                    types = {str(field.name): _normalize_datatype(getattr(field, "dataType", "")) for field in schema.fields}
                    return columns, types

                dtypes = getattr(df, "dtypes", None)
                if dtypes is not None:
                    dtype_items = dtypes.items() if hasattr(dtypes, "items") else dtypes
                    types = {str(name): _normalize_datatype(dtype) for name, dtype in dtype_items}
                    columns = [str(column) for column in getattr(df, "columns", list(types))]
                    return columns, types

                columns = [str(column) for column in getattr(df, "columns", [])]
                return columns, {}
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.validate_schema`
- Short name: `validate_schema`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `109`
- Inbound references count: 1
- Outbound references count: 2

### AI implementation contract

- **required_context:** Use in 02_pipeline before write helpers so schema guardrails run before publishing data.
- **inputs:** dataframe, expected_schema mapping, and preset controlling blocking behavior.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.
- **side_effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when preset is not one of the supported schema presets.
- **verification:** Verify can_continue before calling write helpers and pass the result to stop_if_failed when blocking behavior is required.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails._actual_schema`
- `fabricops_kit.guardrails._normalize_datatype`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/guardrails.py#L109-L198">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1e1b315d5b95935a662818da57af236b37c14595/src/fabricops_kit/guardrails.py#L109-L198</a>
- Start line: `109`
- End line: `198`
- Signature:

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str='strict') -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>

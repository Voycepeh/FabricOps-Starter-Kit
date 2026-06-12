# validate_schema

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use as an early guardrail when a source or target DataFrame must match a known schema contract.

**Do not use when:**

- Do not use for DQ-rule enforcement or metadata persistence.

**Additional context:**

Checks whether a DataFrame contains the expected columns and compatible types before downstream transformations or writes continue.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def validate_schema(
    dataframe,
    expected_schema: dict[str, str],
    preset: str='strict',
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
schema_result = validate_schema(df, {"order_id": "string"}, preset="allow_new_columns")
stop_if_failed(schema_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark, pandas, or dataframe-like object with schema metadata. |
| `expected_schema` | `dict[str, str]` | Yes | Mapping of required column names to expected datatype strings. |
| `preset` | `str` | No | Schema validation intent. ``strict`` blocks missing columns, datatype changes, and unexpected columns. ``allow_new_columns`` blocks missing columns and datatype changes while reporting additional columns as a warning. ``monitor_only`` reports all differences without blocking. |

## Returns

Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.

### Return interpretation

When can_continue is true, schema checks passed or only non-blocking issues were found. When false, fix missing or mismatched columns before writing data.

## Raises / Errors

ValueError when preset is not one of the supported schema presets.

### Common failure causes

- Required columns are missing.
- Column types differ from expected schema.
- The expected schema configuration is incomplete.
- The DataFrame supplied to the check is not the intended table.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails._actual_schema`
- `fabricops_kit.guardrails._normalize_datatype`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Inspects DataFrame schema only; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    validate_schema(...)
    ├── _actual_schema(...)
    │   └── _normalize_datatype(...)
    └── _normalize_datatype(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for rule parsing and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L37-L83"><code>_normalize_datatype</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L86-L101"><code>_actual_schema</code></a>
        </div>
      </section>
    </div>

    ??? example "View helper source by area"

        ??? example "Rule parsing helpers"

            **`def _normalize_datatype(data_type) -> str`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L37-L83)

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

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L86-L101)

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


<div class="reference-source-card">
  <p><strong>Source:</strong> <code>fabricops_kit/guardrails.py:109</code></p>
  <p><strong>Actions:</strong> <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L109-L198">View on GitHub</a></p>
</div>

??? example "Source code"

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

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

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
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue, source table, target table

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L109-L198">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L109-L198</a>
- Start line: `109`
- End line: `198`
- Signature:

```python
def validate_schema(
    dataframe,
    expected_schema: dict[str, str],
    preset: str='strict',
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

- Source: `fabricops_kit/guardrails.py:109`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/guardrails.py#L109-L198">View validate_schema on GitHub</a>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)

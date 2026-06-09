# display_schema_profile

Display current schema columns, Spark datatypes, nullable flags, and proposed guardrail datatypes.

## What this is for and when to use it

Display current schema columns, Spark datatypes, nullable flags, and proposed guardrail datatypes.

- Use in notebooks to review current schema details before accepting a starter expected_schema.

## When not to use it

- Do not use as a replacement for validate_schema; it is a review aid only.

## Example

```python
display_schema_profile(df, exclude_columns=["_fabricops_run_id"])
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
      <td data-label="Parameter"><code>exclude_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Columns to omit from the displayed profile.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>sort_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When ``True``, sort columns alphabetically. When ``False``, preserve DataFrame schema order.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

List of row dictionaries containing column_name, spark_data_type, nullable, and guardrail_data_type.

## Errors and side effects

**Errors:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.

**Side effects:** Prints a readable schema profile table; it does not write metadata, tables, or files.

## Related functions

- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>
- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L240-L286">View display_schema_profile on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def display_schema_profile(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
) -> list[dict]:
    """Display the observed schema alongside proposed guardrail datatypes.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    exclude_columns : list-like, optional
        Columns to omit from the displayed profile.
    sort_columns : bool, default=False
        When ``True``, sort columns alphabetically. When ``False``, preserve
        DataFrame schema order.

    Returns
    -------
    list[dict]
        Rows containing ``column_name``, ``spark_data_type``, ``nullable``, and
        ``guardrail_data_type``.

    Notes
    -----
    This is a notebook-friendly review aid. It shows a starter schema guardrail
    profile only; users must review the proposed types before treating them as
    approved expectations.
    """
    rows = _schema_profile_rows(
        dataframe,
        exclude_columns=exclude_columns,
        sort_columns=sort_columns,
    )
    headers = ["column_name", "spark_data_type", "nullable", "guardrail_data_type"]
    widths = {header: len(header) for header in headers}
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(str(row.get(header, ""))))
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)
    separator = "-+-".join("-" * widths[header] for header in headers)
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers))
    return rows
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.display_schema_profile`
- Short name: `display_schema_profile`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `240`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Use in 02_pipeline optional helper cells before manual schema guardrail configuration.
- **inputs:** dataframe plus optional exclude_columns and sort_columns.
- **output:** List of row dictionaries containing column_name, spark_data_type, nullable, and guardrail_data_type.
- **side_effects:** Prints a readable schema profile table; it does not write metadata, tables, or files.
- **failure_modes:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.
- **verification:** Check that proposed datatypes and excluded technical columns match the intended contract.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L240-L286">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L240-L286</a>
- Start line: `240`
- End line: `286`
- Signature:

```python
def display_schema_profile(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False) -> list[dict]
```

### Internal relationship graph

### Public related functions

- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>
- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

### Internal implementation helpers

- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

</details>

# generate_schema_guardrail_config

Generate starter schema guardrail config from a DataFrame schema.

## What this is for and when to use it

Generate starter schema guardrail config from a DataFrame schema.

- Use while authoring 02_pipeline to copy the current DataFrame schema into a reviewed expected_schema guardrail.

## When not to use it

- Do not treat the generated output as approved without human review, and do not use it for DQ or stability checks.

## Example

```python
expected_schema = generate_schema_guardrail_config(df, exclude_columns=["_loaded_at"])
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
      <td data-label="Meaning">Columns to omit from the starter expectation, such as runtime audit or technical annotation columns.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>sort_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When ``True``, sort output columns alphabetically. When ``False``, preserve DataFrame schema order.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>output_format</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Return shape. ``&quot;dict&quot;`` returns a mapping suitable for review before passing to :func:`validate_schema`. ``&quot;python&quot;`` returns copy-paste-ready Python code defining ``expected_schema``. ``&quot;rows&quot;`` returns row dictionaries with column name, Spark datatype, nullable flag, and proposed guardrail datatype.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

A starter expected_schema dict, copy-paste Python code, or row dictionaries depending on output_format.

## Errors and side effects

**Errors:** ValueError when output_format is not dict, python, or rows.

**Side effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.

## Related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- `fabricops_kit.config.items`
- <a href="../internal/drift__schema_guardrail_rows/"><code>fabricops_kit.drift._schema_guardrail_rows</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/drift.py#L142-L199">View generate_schema_guardrail_config on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def generate_schema_guardrail_config(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
    output_format: str = "dict",
):
    """Generate starter schema guardrail config from a DataFrame schema.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    exclude_columns : list-like, optional
        Columns to omit from the starter expectation, such as runtime audit or
        technical annotation columns.
    sort_columns : bool, default=False
        When ``True``, sort output columns alphabetically. When ``False``,
        preserve DataFrame schema order.
    output_format : {"dict", "python", "rows"}, default="dict"
        Return shape. ``"dict"`` returns a mapping suitable for review before
        passing to :func:`validate_schema`. ``"python"`` returns copy-paste-ready
        Python code defining ``expected_schema``. ``"rows"`` returns row
        dictionaries with column name, Spark datatype, nullable flag, and
        proposed guardrail datatype.

    Returns
    -------
    dict[str, str] or str or list[dict]
        Starter schema guardrail in the requested output format.

    Raises
    ------
    ValueError
        If ``output_format`` is not one of ``"dict"``, ``"python"``, or
        ``"rows"``.

    Notes
    -----
    This helper captures the current observed schema only. Review and approve
    the returned expectation before using it as a pipeline guardrail. Common
    normalized types include ``string``, ``int``, ``bigint``, ``double``,
    ``decimal(p,s)``, ``date``, ``timestamp``, and ``boolean``.
    """
    rows = _schema_guardrail_rows(dataframe, exclude_columns=exclude_columns, sort_columns=sort_columns)
    config = {str(row["column_name"]): str(row["guardrail_data_type"]) for row in rows}
    normalized_format = str(output_format or "dict").lower()
    if normalized_format == "dict":
        return config
    if normalized_format == "rows":
        return rows
    if normalized_format == "python":
        lines = ["expected_schema = {"]
        for column, data_type in config.items():
            lines.append(f"    {column!r}: {data_type!r},")
        lines.append("}")
        return "\n".join(lines)
    raise ValueError("output_format must be one of: dict, python, rows")
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.generate_schema_guardrail_config`
- Short name: `generate_schema_guardrail_config`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `142`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Use in notebooks after reading a DataFrame and before finalizing the manually reviewed schema guardrail.
- **inputs:** dataframe plus optional exclude_columns, sort_columns, and output_format values dict, python, or rows.
- **output:** A starter expected_schema dict, copy-paste Python code, or row dictionaries depending on output_format.
- **side_effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when output_format is not dict, python, or rows.
- **verification:** Review generated datatypes and remove runtime-only columns before committing the expected schema to a pipeline.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/drift__schema_guardrail_rows/"><code>fabricops_kit.drift._schema_guardrail_rows</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/drift.py#L142-L199">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/drift.py#L142-L199</a>
- Start line: `142`
- End line: `199`
- Signature:

```python
def generate_schema_guardrail_config(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False, output_format: str='dict')
```

### Internal relationship graph

### Public related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

### Internal implementation helpers

- `fabricops_kit.config.items`
- <a href="../internal/drift__schema_guardrail_rows/"><code>fabricops_kit.drift._schema_guardrail_rows</code></a>

</details>

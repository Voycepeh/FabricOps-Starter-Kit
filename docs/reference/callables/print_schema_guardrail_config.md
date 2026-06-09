# print_schema_guardrail_config

Print copy-paste-ready starter expected_schema code from a DataFrame schema.

## What this is for and when to use it

Print copy-paste-ready starter expected_schema code from a DataFrame schema.

- Use in notebooks when a user wants copy-paste-ready expected_schema starter code.

## When not to use it

- Do not use as an approval step; users still need to review the generated schema.

## Example

```python
print_schema_guardrail_config(df, sort_columns=True)
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
      <td data-label="Meaning">Columns to omit from the starter expectation.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>sort_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When ``True``, sort columns alphabetically. When ``False``, preserve DataFrame schema order.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>variable_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Python variable name to use in the printed snippet.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

The generated schema guardrail dictionary after printing Python code.

## Errors and side effects

**Errors:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.

**Side effects:** Prints a Python dictionary snippet; it does not write metadata, tables, or files.

## Related functions

- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>
- <a href="../display_schema_profile/"><code>fabricops_kit.drift.display_schema_profile</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- `fabricops_kit.config.items`
- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L196-L237">View print_schema_guardrail_config on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def print_schema_guardrail_config(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
    variable_name: str = "expected_schema",
) -> dict[str, str]:
    """Print copy-paste-ready starter schema guardrail code.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    exclude_columns : list-like, optional
        Columns to omit from the starter expectation.
    sort_columns : bool, default=False
        When ``True``, sort columns alphabetically. When ``False``, preserve
        DataFrame schema order.
    variable_name : str, default="expected_schema"
        Python variable name to use in the printed snippet.

    Returns
    -------
    dict[str, str]
        The same starter dictionary printed as Python code.

    Notes
    -----
    The printed dictionary is a starting point only. Users should review and
    edit it before treating it as the approved schema guardrail.
    """
    config = generate_schema_guardrail_config(
        dataframe,
        exclude_columns=exclude_columns,
        sort_columns=sort_columns,
    )
    lines = [f"{variable_name} = {{"]
    for column, data_type in config.items():
        lines.append(f"    {column!r}: {data_type!r},")
    lines.append("}")
    print("\n".join(lines))
    return config
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.print_schema_guardrail_config`
- Short name: `print_schema_guardrail_config`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `196`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Use in 02_pipeline helper cells before filling SOURCE_DATASETS or TARGET_DATASETS expected_schema.
- **inputs:** dataframe plus optional exclude_columns, sort_columns, and variable_name.
- **output:** The generated schema guardrail dictionary after printing Python code.
- **side_effects:** Prints a Python dictionary snippet; it does not write metadata, tables, or files.
- **failure_modes:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.
- **verification:** Confirm the printed dictionary was reviewed before pasting into approved guardrails.

### Inbound references

Not documented yet

### Outbound references

- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L196-L237">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/drift.py#L196-L237</a>
- Start line: `196`
- End line: `237`
- Signature:

```python
def print_schema_guardrail_config(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False, variable_name: str='expected_schema') -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>
- <a href="../display_schema_profile/"><code>fabricops_kit.drift.display_schema_profile</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

### Internal implementation helpers

- `fabricops_kit.config.items`
- <a href="../generate_schema_guardrail_config/"><code>fabricops_kit.drift.generate_schema_guardrail_config</code></a>

</details>

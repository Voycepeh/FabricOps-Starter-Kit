# generate_schema_guardrail_config

Generate a reviewed starter expected_schema dictionary from a DataFrame schema.

## What this is for and when to use it

Generate a reviewed starter expected_schema dictionary from a DataFrame schema.

- Use before authoring expected_schema to draft a starter schema guardrail from the current DataFrame schema.

## When not to use it

- Do not treat the generated dictionary as approved without human review.

## Example

```python
expected_schema = generate_schema_guardrail_config(df, exclude_columns=["_fabricops_run_id"])
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
      <td data-label="Meaning">Columns to omit from the generated starter expectation, such as audit or runtime columns managed by the pipeline.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>sort_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When ``True``, sort columns alphabetically. When ``False``, preserve the DataFrame schema order.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Python dictionary mapping column names to normalized guardrail datatypes.

## Errors and side effects

**Errors:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.

**Side effects:** Inspects schema metadata only; it does not write metadata, tables, or files.

## Related functions

- <a href="../display_schema_profile/"><code>fabricops_kit.drift.display_schema_profile</code></a>
- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/drift.py#L143-L183">View generate_schema_guardrail_config on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def generate_schema_guardrail_config(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
) -> dict[str, str]:
    """Generate a starter schema guardrail dictionary from a DataFrame schema.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    exclude_columns : list-like, optional
        Columns to omit from the generated starter expectation, such as audit
        or runtime columns managed by the pipeline.
    sort_columns : bool, default=False
        When ``True``, sort columns alphabetically. When ``False``, preserve
        the DataFrame schema order.

    Returns
    -------
    dict[str, str]
        Mapping of column names to normalized guardrail datatype strings that
        can be reviewed and then passed to :func:`validate_schema`.

    Notes
    -----
    This helper creates a starter schema guardrail from the current observed
    schema. Review the output before treating it as an approved expectation.
    Supported common normalized types include ``string``, ``integer``,
    ``long``, ``double``, ``decimal(p,s)``, ``date``, ``timestamp``, and
    ``boolean``.
    """
    return {
        row["column_name"]: row["guardrail_data_type"]
        for row in _schema_profile_rows(
            dataframe,
            exclude_columns=exclude_columns,
            sort_columns=sort_columns,
        )
    }
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
- Source line: `143`
- Inbound references count: 1
- Outbound references count: 1

### AI implementation contract

- **required_context:** Use in 02_pipeline helper cells to bootstrap expected_schema before validate_schema.
- **inputs:** dataframe plus optional exclude_columns and sort_columns.
- **output:** Python dictionary mapping column names to normalized guardrail datatypes.
- **side_effects:** Inspects schema metadata only; it does not write metadata, tables, or files.
- **failure_modes:** Raises DataFrame/schema inspection errors when schema metadata is unavailable.
- **verification:** Verify excluded columns, nullable business expectations, and normalized types before copying into pipeline guardrails.

### Inbound references

- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>

### Outbound references

- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/drift.py#L143-L183">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/drift.py#L143-L183</a>
- Start line: `143`
- End line: `183`
- Signature:

```python
def generate_schema_guardrail_config(dataframe, *, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, sort_columns: bool=False) -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../display_schema_profile/"><code>fabricops_kit.drift.display_schema_profile</code></a>
- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

### Internal implementation helpers

- <a href="../print_schema_guardrail_config/"><code>fabricops_kit.drift.print_schema_guardrail_config</code></a>
- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

</details>

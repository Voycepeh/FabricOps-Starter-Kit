# read_lakehouse_excel

Read an Excel file from a configured Fabric lakehouse Files path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:761`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/fabric_input_output.py#L761-L850">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when source data arrives as an Excel workbook and should still follow configured Fabric lakehouse routing.

**Do not use when:**

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

**Additional context:**

Reads an Excel file from a configured lakehouse Files path and converts it into a Spark DataFrame for notebook processing.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_excel(
    config,
    env,
    target,
    relative_path,
    sheet_name=0,
    spark_session=None,
    **read_excel_kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `relative_path` | `str` | Yes | Path to the Excel file relative to the lakehouse ``Files`` area, for example ``"reference/faculty_mapping.xlsx"``. A leading ``"Files/"`` prefix is accepted for consistency with notebook examples and is normalized away before the lakehouse path is resolved. |
| `sheet_name` | `str or int, default 0` | No | Worksheet name or index to read. Defaults to the first worksheet. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. **read_excel_kwargs Additional keyword arguments passed directly to :func:`pandas.read_excel`. Common options include ``skiprows`` for title rows above the real header, ``header`` for custom header-row selection, ``usecols`` for column filtering, ``dtype`` for mixed-type columns, and ``nrows`` for sampling or bounded reads. |

## Returns

Spark DataFrame converted from the selected Excel worksheet.

### Return interpretation

The returned DataFrame depends on workbook sheet and parsing options; confirm headers and types before using it as pipeline input.

## Raises / Errors

Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

### Common failure causes

- The workbook path or sheet name is incorrect.
- Excel parsing dependencies are unavailable.
- The workbook layout does not match expected headers.
- The configured lakehouse target cannot be read.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

**Notes:**

Side effects:
- Creates a temporary local file during conversion.
- Materializes rows through pandas before creating a Spark DataFrame.

</details>

??? info "Call flow"

    ```text
    read_lakehouse_excel(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    │   └── _normalize_path_config(...)
    │       └── PathConfig(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 4"

    This callable uses 4 internal helpers for metadata loading, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/fabric_input_output.py#L221-L231"><code>_lakehouse_file_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/config.py#L651-L691"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/config.py#L694-L733"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- Short name: `read_lakehouse_excel`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `761`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires 00_env_config config/env/target context for resolving the configured lakehouse Files path.
- **inputs:** config, env, target, relative_path, optional sheet_name, optional spark_session, and pandas read_excel keyword arguments.
- **output:** Spark DataFrame converted from the selected Excel worksheet.
- **side_effects:** Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.
- **verification:** Verify the DataFrame row count and schema after reading, and confirm the Excel file is appropriate for a small reference-style input.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/fabric_input_output.py#L761-L850">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4ec556ede579d4b9c376214e9ed6fe762ce1867a/src/fabricops_kit/fabric_input_output.py#L761-L850</a>
- Start line: `761`
- End line: `850`
- Signature:

```python
def read_lakehouse_excel(
    config,
    env,
    target,
    relative_path,
    sheet_name=0,
    spark_session=None,
    **read_excel_kwargs,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

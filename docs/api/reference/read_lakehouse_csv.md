# read_lakehouse_csv

Read a CSV file from a configured Fabric lakehouse Files path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:293`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L293-L335">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use for file-based source ingestion when the source is CSV and should be resolved through configured lakehouse paths.

**Do not use when:**

- Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL tables.

**Additional context:**

Reads a CSV file from the Files area of a configured Fabric lakehouse and returns it as a Spark DataFrame.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_csv(
    config,
    env,
    target,
    relative_path,
    spark_session=None,
    header=True,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_csv(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.csv", header=True, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `relative_path` | `str` | Yes | Path to the CSV file or folder under the lakehouse root, for example `"Files/raw/orders.csv"` or `"Files/raw/orders/"`. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |
| `header` | `bool, default True` | No | Whether the first row of the CSV file contains column names. |

## Returns

Spark DataFrame loaded from the lakehouse Files CSV path.

### Return interpretation

The returned DataFrame reflects Spark CSV parsing options; inspect schema and sample rows before profiling or writing.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The file path is wrong or outside the configured lakehouse.
- CSV options do not match the file shape.
- Spark cannot access the file.
- The selected environment is missing the source lakehouse target.

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

- `00_env_config`
- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_lakehouse_csv(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for metadata loading and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L133-L143"><code>_lakehouse_file_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L100-L130"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- Short name: `read_lakehouse_csv`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `293`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 00_env_config, 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, CSV read options, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the lakehouse Files CSV path.
- **side_effects:** Reads from lakehouse Files; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.
- **verification:** Verify relative_path points under Files, then check row count and schema after reading.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L293-L335">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L293-L335</a>
- Start line: `293`
- End line: `335`
- Signature:

```python
def read_lakehouse_csv(
    config,
    env,
    target,
    relative_path,
    spark_session=None,
    header=True,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

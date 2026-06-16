# read_lakehouse_parquet

Read a Parquet path from a configured Fabric lakehouse Files path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:625`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L625-L749">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use for file-based source ingestion when the source is Parquet rather than a managed table.

**Do not use when:**

- Do not use for Delta tables, CSV files, Excel files, or warehouse SQL tables.

**Additional context:**

Reads a Parquet file or folder from the Files area of a configured Fabric lakehouse into a Spark DataFrame.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_parquet(
    config,
    env,
    target,
    relative_path,
    verbose=True,
    spark_session=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_parquet(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.parquet", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `relative_path` | `str` | Yes | Path to the Parquet file under the lakehouse `Files/` folder, without the leading `"Files/"`. For example: `"raw/orders/orders_2026.parquet"`. |
| `verbose` | `bool, default True` | No | Whether to print read and fallback progress. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |

## Returns

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

### Return interpretation

The returned DataFrame uses the Parquet schema read by Spark; validate it before downstream profile or guardrail checks.

## Raises / Errors

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

### Common failure causes

- The Parquet path is missing or misspelled.
- The file is not valid Parquet.
- The configured lakehouse target is unavailable.
- The caller lacks read permission.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.

**Notes:**

Assumes Fabric notebook runtime filesystem conventions for local fallback
conversion paths (``/lakehouse/default/Files/...``).

</details>

??? info "Call flow"

    ```text
    read_lakehouse_parquet(...)
    ├── _convert_single_parquet_ns_to_us(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    │   └── _normalize_path_config(...)
    │       └── PathConfig(...)
    └── _lakehouse_file_path(...)
    ```

??? info "Internal helpers used: 5"

    This callable uses 5 internal helpers for audit timestamp, metadata loading, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L569-L622"><code>_convert_single_parquet_ns_to_us</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L212-L222"><code>_lakehouse_file_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L178-L209"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- Short name: `read_lakehouse_parquet`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `625`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.
- **side_effects:** Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.
- **failure_modes:** Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.
- **verification:** Verify the file path is a lakehouse Files Parquet path and check row count/schema after reading.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._lakehouse_file_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L625-L749">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/fabric_input_output.py#L625-L749</a>
- Start line: `625`
- End line: `749`
- Signature:

```python
def read_lakehouse_parquet(
    config,
    env,
    target,
    relative_path,
    verbose=True,
    spark_session=None,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 5
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

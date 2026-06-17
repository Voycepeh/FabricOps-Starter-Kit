# read_data

Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:235`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/fabric_input_output.py#L235-L320">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use whenever a starter notebook needs to load data from a configured Fabric target.

**Do not use when:**

- Do not use inside package internals that intentionally need a specific storage implementation helper.

**Additional context:**

Provides a stable notebook-facing read orchestrator while format-specific Lakehouse and Warehouse helpers remain implementation details.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_data(
    config,
    env,
    target,
    name=None,
    format='table',
    schema=None,
    table=None,
    relative_path=None,
    spark_session=None,
    options=None,
    **kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df_orders = read_data(CONFIG, ENV_NAME, "source", "orders", schema=SOURCE_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as ``"dev"``. |
| `target` | `str` | Yes | Logical target name such as ``"source"`` or ``"warehouse"``. |
| `name` | `str` | No | Table name for table reads or relative file path for file reads. |
| `format` | `str, default="table"` | No | Read format. Supported values are ``"table"``, ``"delta"``, ``"csv"``, ``"parquet"``, ``"excel"``, and ``"warehouse"``. |
| `schema` | `str` | No | Lakehouse or warehouse schema name. |
| `table` | `str` | No | Explicit table name. Overrides ``name`` for table and warehouse reads. |
| `relative_path` | `str` | No | Explicit lakehouse Files path. Overrides ``name`` for file reads. |
| `spark_session` | `object` | No | Spark session to use. |
| `options` | `dict` | No | Additional reader options passed to the format-specific implementation. **kwargs Additional reader options. |

## Returns

Spark DataFrame loaded from the configured Fabric target.

### Return interpretation

The returned DataFrame is the input for profiling, transformations, guardrails, or exploration.

## Raises / Errors

Raises ValueError for unsupported formats or missing table/path/schema inputs.

### Common failure causes

- Unsupported format value.
- Missing table, relative_path, or schema for the selected format.
- Target kind does not match the selected format.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.fabric_input_output.read_warehouse_table`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`
- `99_explore`

**Side effects:**

Reads data only; it does not write metadata, files, or tables.

**Notes:**

This is the notebook-facing IO orchestrator. It routes through the
configured FabricOps environment target and delegates to implementation
helpers for specific storage formats.

</details>

??? info "Call flow"

    ```text
    read_data(...)
    ├── read_lakehouse_csv(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _lakehouse_file_path(...)
    ├── read_lakehouse_excel(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _lakehouse_file_path(...)
    ├── read_lakehouse_parquet(...)
    │   ├── _convert_single_parquet_ns_to_us(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _lakehouse_file_path(...)
    ├── read_lakehouse_table(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _normalize_table_name(...)
    │   └── _resolve_lakehouse_table_path(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_schema(...)
    │           └── _normalize_schema_name(...)
    └── read_warehouse_table(...)
        ├── _get_spark(...)
        └── _get_store(...)
            └── _normalize_path_config(...)
                └── PathConfig(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `read_data` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_data`
- Short name: `read_data`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `235`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Routes reads through configured FabricOps environment targets instead of an attached/default lakehouse.
- **inputs:** config, env, target, optional name, format, schema, table, relative_path, spark_session, options, and reader kwargs.
- **output:** Spark DataFrame loaded from the configured Fabric target.
- **side_effects:** Reads data only; it does not write metadata, files, or tables.
- **failure_modes:** Raises ValueError for unsupported formats or missing table/path/schema inputs.
- **verification:** Verify target, format, schema, and table/path values come from CONFIG or notebook parameters before generating calls.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.fabric_input_output.read_warehouse_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/fabric_input_output.py#L235-L320">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a44ba80ddd5b368e63951e7e195100e45e5319c2/src/fabricops_kit/fabric_input_output.py#L235-L320</a>
- Start line: `235`
- End line: `320`
- Signature:

```python
def read_data(
    config,
    env,
    target,
    name=None,
    format='table',
    schema=None,
    table=None,
    relative_path=None,
    spark_session=None,
    options=None,
    **kwargs,
):
```

### Internal relationship graph

### Public related functions

- <a href="../write_data/"><code>fabricops_kit.fabric_input_output.write_data</code></a>
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

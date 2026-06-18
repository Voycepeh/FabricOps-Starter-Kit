# read_data

Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:235`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/fabric_input_output.py#L235-L309">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use whenever a starter notebook needs to load data from a configured Fabric target.

### Do not use when

- Do not use inside package internals that intentionally need a specific storage implementation helper.

### Additional context

Provides a stable notebook-facing read orchestrator while format-specific Lakehouse and Warehouse helpers remain implementation details.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_data(
    source: str,
    target: str='source',
    format: str='table',
    schema: str | None=None,
    table: str | None=None,
    relative_path: str | None=None,
    spark_session=None,
    options: dict | None=None,
    context: dict[str, Any] | None=None,
    **kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df_orders = read_data("orders", target="source", schema=SOURCE_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source` | `str` | Yes | Table name for table reads or relative file path for file reads. |
| `target` | `str` | No | Logical target name in ``FABRIC_CONTEXT["config"]``. |
| `format` | `str` | No | Read format. Supported values are ``"table"``, ``"delta"``, ``"csv"``, ``"parquet"``, ``"excel"``, and ``"warehouse"``. |
| `schema` | `str \| None` | No | Lakehouse or warehouse schema name. |
| `table` | `str \| None` | No | Explicit table name. Overrides ``source`` for table and warehouse reads. |
| `relative_path` | `str \| None` | No | Explicit lakehouse Files path. Overrides ``source`` for file reads. |
| `spark_session` | `object` | No | Spark session to use. |
| `options` | `dict \| None` | No | Additional reader options passed to the format-specific implementation. |
| `context` | `dict[str, Any] \| None` | No | Advanced override context. Defaults to the active ``FABRIC_CONTEXT`` initialized by ``00_env_config``. **kwargs Additional reader options. |

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

- `fabricops_kit.config.resolve_fabric_context`
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

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_data(...)
    ├── read_lakehouse_csv(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _lakehouse_file_path(...)
    │   └── resolve_fabric_context(...)
    │       └── get_default_fabric_context(...)
    ├── read_lakehouse_excel(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _lakehouse_file_path(...)
    │   └── resolve_fabric_context(...)
    │       └── get_default_fabric_context(...)
    ├── read_lakehouse_parquet(...)
    │   ├── _convert_single_parquet_ns_to_us(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _lakehouse_file_path(...)
    │   └── resolve_fabric_context(...)
    │       └── get_default_fabric_context(...)
    ├── read_lakehouse_table(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _normalize_table_name(...)
    │   ├── _resolve_lakehouse_table_path(...)
    │   │   ├── _normalize_table_name(...)
    │   │   └── _resolve_lakehouse_schema(...)
    │   │       └── _normalize_schema_name(...)
    │   └── resolve_fabric_context(...)
    │       └── get_default_fabric_context(...)
    ├── read_warehouse_table(...)
    │   ├── _get_spark(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── resolve_fabric_context(...)
    │       └── get_default_fabric_context(...)
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
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
- Outbound references count: 6
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Routes reads through configured FabricOps environment targets instead of an attached/default lakehouse.
- **inputs:** config, env, target, optional name, format, schema, table, relative_path, spark_session, options, and reader kwargs.
- **output:** Spark DataFrame loaded from the configured Fabric target.
- **side_effects:** Reads data only; it does not write metadata, files, or tables.
- **failure_modes:** Raises ValueError for unsupported formats or missing table/path/schema inputs.
- **verification:** Verify target, format, schema, and table/path values are business inputs or come from the active FABRIC_CONTEXT before generating calls.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.fabric_input_output.read_warehouse_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/fabric_input_output.py#L235-L309">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/fabric_input_output.py#L235-L309</a>
- Start line: `235`
- End line: `309`
- Signature:

```python
def read_data(
    source: str,
    target: str='source',
    format: str='table',
    schema: str | None=None,
    table: str | None=None,
    relative_path: str | None=None,
    spark_session=None,
    options: dict | None=None,
    context: dict[str, Any] | None=None,
    **kwargs,
):
```

### Internal relationship graph

### Public related functions

- <a href="write_data/"><code>fabricops_kit.fabric_input_output.write_data</code></a>
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook registry</summary>Metadata inventory of notebooks and responsibilities used for handover and operating context.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

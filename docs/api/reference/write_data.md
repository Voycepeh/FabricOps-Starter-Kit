# write_data

Write Lakehouse or Warehouse targets through one notebook-facing IO function.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:323`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/fabric_input_output.py#L323-L402">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use whenever a starter notebook needs to publish data to a configured Fabric target.

**Do not use when:**

- Do not use inside package metadata persistence helpers that already use configured metadata routing.

**Additional context:**

Provides a stable notebook-facing write orchestrator while format-specific Lakehouse and Warehouse helpers remain implementation details.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_data(
    df,
    config,
    env,
    target,
    name=None,
    format='table',
    schema=None,
    table=None,
    mode='append',
    options=None,
    **kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_data(df_orders, CONFIG, ENV_NAME, "unified", "orders_clean", schema=UNIFIED_SCHEMA, mode="overwrite")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | DataFrame to write. |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as ``"dev"``. |
| `target` | `str` | Yes | Logical target name such as ``"unified"`` or ``"warehouse"``. |
| `name` | `str` | No | Target table name. |
| `format` | `str, default="table"` | No | Write format. Supported values are ``"table"``, ``"delta"``, and ``"warehouse"``. |
| `schema` | `str` | No | Lakehouse or warehouse schema name. |
| `table` | `str` | No | Explicit table name. Overrides ``name``. |
| `mode` | `str, default="append"` | No | Write mode. |
| `options` | `dict` | No | Additional writer options for Lakehouse Delta writes. **kwargs Additional writer options for Lakehouse Delta writes. |

## Returns

None; the DataFrame is written to the configured Fabric target.

### Return interpretation

No value is returned; successful completion means the configured target write completed.

## Raises / Errors

Raises ValueError for unsupported formats or missing table/schema inputs.

### Common failure causes

- Unsupported format value.
- Missing table or schema for the selected format.
- Target kind does not match the selected format.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output.write_lakehouse_table`
- `fabricops_kit.fabric_input_output.write_warehouse_table`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`
- `example_pipeline_demo`
- `example_dq_rule_smoke_test`

**Side effects:**

Writes data to the configured Fabric target.

**Notes:**

This is the notebook-facing IO orchestrator. It keeps starter notebooks on
a stable public API while format-specific helpers remain implementation
details.

</details>

??? info "Call flow"

    ```text
    write_data(...)
    ├── write_lakehouse_table(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   ├── _normalize_table_name(...)
    │   └── _resolve_lakehouse_table_path(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_schema(...)
    │           └── _normalize_schema_name(...)
    └── write_warehouse_table(...)
        └── _get_store(...)
            └── _normalize_path_config(...)
                └── PathConfig(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `write_data` does not have package-local helper descendants in the generated call graph.

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

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_data`
- Short name: `write_data`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `323`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test
- Glossary terms: notebook template

### Implementation contract

- **required_context:** Routes writes through configured FabricOps environment targets instead of an attached/default lakehouse.
- **inputs:** df, config, env, target, optional name, format, schema, table, mode, options, and writer kwargs.
- **output:** None; the DataFrame is written to the configured Fabric target.
- **side_effects:** Writes data to the configured Fabric target.
- **failure_modes:** Raises ValueError for unsupported formats or missing table/schema inputs.
- **verification:** Verify target, format, schema, table, and mode values before generating calls.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output.write_lakehouse_table`
- `fabricops_kit.fabric_input_output.write_warehouse_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/fabric_input_output.py#L323-L402">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b9215c3af8eef0a6cb6a107b64631a41feb48a4/src/fabricops_kit/fabric_input_output.py#L323-L402</a>
- Start line: `323`
- End line: `402`
- Signature:

```python
def write_data(
    df,
    config,
    env,
    target,
    name=None,
    format='table',
    schema=None,
    table=None,
    mode='append',
    options=None,
    **kwargs,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_data/"><code>fabricops_kit.fabric_input_output.read_data</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

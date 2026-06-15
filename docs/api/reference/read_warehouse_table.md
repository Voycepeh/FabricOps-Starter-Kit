# read_warehouse_table

Read a table from a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:438`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L438-L498">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when source data lives in a Fabric Warehouse rather than a lakehouse file or Delta table.

**Do not use when:**

- Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.

**Additional context:**

Reads data from a configured Fabric Warehouse table or query target into a Spark DataFrame.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment name in the config mapping, for example `"Sandbox"` or `"DE"`. |
| `target` | `str` | Yes | Warehouse target name under the selected environment, for example `"Warehouse"` or `"wh_Bronze"`. |
| `schema` | `str` | Yes | Warehouse schema name, for example `"dbo"`. |
| `table` | `str` | Yes | Warehouse table name. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |

## Returns

Spark DataFrame loaded from the configured warehouse table.

### Return interpretation

The returned DataFrame represents the warehouse read result; confirm filters and row counts before profiling or transformation.

## Raises / Errors

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

### Common failure causes

- The warehouse target is not configured.
- The table or SQL text is invalid.
- Warehouse connector context is unavailable.
- The caller lacks warehouse read permission.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `00_env_config`
- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from a warehouse table; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_warehouse_table(...)
    ├── _get_spark(...)
    └── _get_store(...)
        └── _normalize_path_config(...)
            └── PathConfig(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for rule parsing and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L178-L209"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_warehouse_table`
- Short name: `read_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `438`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 00_env_config, 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, schema, table, optional verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the configured warehouse table.
- **side_effects:** Reads from a warehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.
- **verification:** Verify the warehouse target/schema/table are configured and inspect the resulting DataFrame schema before downstream use.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L438-L498">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L438-L498</a>
- Start line: `438`
- End line: `498`
- Signature:

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

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

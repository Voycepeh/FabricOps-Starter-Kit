# write_lakehouse_table

Write a DataFrame to a configured Fabric lakehouse target by ABFSS path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:280`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L280-L389">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use for lakehouse or metadata table writes after guardrails have passed when the destination should be saved by ABFSS Delta path, not saveAsTable or a Spark namespace.

**Do not use when:**

- Do not use for warehouse tables; metadata evidence tables are supported through the configured metadata lakehouse target.

**Additional context:**

Writes a DataFrame to the configured Fabric lakehouse target, resolving to {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} for schema-enabled targets.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_lakehouse_table(
    df,
    config,
    env,
    target,
    table,
    schema=None,
    mode='append',
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_lakehouse_table(curated_df, CONFIG, env="Sandbox", target="Unified", table="orders_curated", schema=UNIFIED_SCHEMA, mode="overwrite", options={"overwriteSchema": "true"})
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `table` | `str` | Yes | Simple target table name. Do not pass ``schema.table``; use ``schema`` separately. |
| `schema` | `str or None` | No | Optional schema override for schema-enabled Lakehouses. When omitted, schema routing comes from the configured lakehouse target. Schema-enabled targets save to ``Tables/<schema>/<table>``; classic targets save to ``Tables/<table>``. |
| `mode` | `str, default "append"` | No | Spark write mode. Supported values are `"append"`, `"overwrite"`, `"errorifexists"`, and `"ignore"`. |
| `partition_by` | `str or list[str]` | No | Column or columns used to physically partition the Delta table. |
| `repartition_by` | `int, str, list, or tuple` | No | Optional repartitioning before write. |
| `options` | `dict` | No | Additional Spark DataFrameWriter options to apply before saving, such as ``{"overwriteSchema": "true"}``. |
| `verbose` | `bool, default=True` | No | Whether to print the resolved output path before writing. |

## Returns

None; the DataFrame is written to the configured lakehouse table.

### Return interpretation

The helper returns the write operation result from the underlying DataFrame writer when available; verify downstream table state for business validation.

## Raises / Errors

Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.

### Common failure causes

- Guardrails were skipped before a target write.
- The target lakehouse is not configured for the environment.
- The write mode is unsupported for the destination.
- The caller lacks write permission or Spark cannot create the table.

## Relationships

### Used by

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.data_agreement._write_row`
- `fabricops_kit.governance_review._review_governance_evidence`
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._register_current_notebook`
- `fabricops_kit.metadata._write_guardrail_result_row`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._resolve_lakehouse_table_path`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `00_env_config`
- `01_agreement`
- `02_pipeline`
- `03_governance`
- `99_explore`

**Side effects:**

Writes data to a Fabric lakehouse Delta table by saving to {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} when the configured lakehouse target has schemas enabled.

**Notes:**

Side effects:
- Persists data to OneLake Delta storage under ``Tables/<table>`` or ``Tables/<schema>/<table>`` when schema routing is enabled.
- Optional repartitioning can change output file sizing and partition
  layout.

</details>

??? info "Call flow"

    ```text
    write_lakehouse_table(...)
    ├── _get_store(...)
    │   └── _normalize_path_config(...)
    │       └── PathConfig(...)
    ├── _normalize_table_name(...)
    └── _resolve_lakehouse_table_path(...)
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_schema(...)
            └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 6"

    This callable uses 6 internal helpers for metadata loading, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L96-L105"><code>_normalize_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L129-L135"><code>_resolve_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L138-L145"><code>_resolve_lakehouse_table_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_lakehouse_table`
- Short name: `write_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `280`
- Inbound references count: 10
- Outbound references count: 3
- Used in templates: 00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore
- Glossary terms: target table, guardrail, metadata lakehouse

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; saves {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} when the configured lakehouse target has schemas enabled.
- **inputs:** df, config, env, target, table, optional schema, mode, partitioning, writer options, and verbose flag.
- **output:** None; the DataFrame is written to the configured lakehouse table.
- **side_effects:** Writes data to a Fabric lakehouse Delta table by saving to {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} when the configured lakehouse target has schemas enabled.
- **failure_modes:** Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.
- **verification:** Verify upstream guardrails passed, confirm target routing from CONFIG, and check the intended write mode before generating code that calls this helper.

### Inbound references

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.data_agreement._write_row`
- `fabricops_kit.governance_review._review_governance_evidence`
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._register_current_notebook`
- `fabricops_kit.metadata._write_guardrail_result_row`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._resolve_lakehouse_table_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L280-L389">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/62335d6d19ea7b929d2220fad2d0a33f2f0b8aca/src/fabricops_kit/fabric_input_output.py#L280-L389</a>
- Start line: `280`
- End line: `389`
- Signature:

```python
def write_lakehouse_table(
    df,
    config,
    env,
    target,
    table,
    schema=None,
    mode='append',
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 6
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Target table:** An output table written by the pipeline.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)

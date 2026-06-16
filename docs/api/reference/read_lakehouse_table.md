# read_lakehouse_table

Read a Delta table from a configured Fabric lakehouse target by ABFSS path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:225`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L225-L277">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when notebook code needs a managed lakehouse Delta table by ABFSS path rather than a file path, registered Spark table name, or warehouse SQL query.

**Do not use when:**

- Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.

**Additional context:**

Reads a Delta table from the configured Fabric lakehouse target, resolving to {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} for schema-enabled targets.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(config, env, target, table, schema=None, spark_session=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", schema=SOURCE_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `table` | `str` | Yes | Simple table name. Do not pass ``schema.table``; use ``schema`` separately. |
| `schema` | `str or None` | No | Optional schema override for schema-enabled Lakehouses. When omitted, schema routing comes from the configured lakehouse target. Schema-enabled targets read from ``Tables/<schema>/<table>``; classic targets read from ``Tables/<table>``. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |

## Returns

Spark DataFrame loaded from the configured lakehouse table.

### Return interpretation

The returned DataFrame represents the resolved lakehouse table; validate row counts and schema before relying on it for guardrails or writes.

## Raises / Errors

Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.

### Common failure causes

- The target or table name is misspelled.
- The selected environment does not define the requested lakehouse target.
- Spark cannot access the table.
- The caller lacks permission to read the lakehouse.

## Relationships

### Used by

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._read_metadata_rows`
- `fabricops_kit.governance_review._read_metadata_table_or_empty`
- `fabricops_kit.governance_review.load_catalogue_profile_rows`
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
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

Reads from a lakehouse table; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_lakehouse_table(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    │   └── _normalize_path_config(...)
    │       └── PathConfig(...)
    ├── _normalize_table_name(...)
    └── _resolve_lakehouse_table_path(...)
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_schema(...)
            └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 7"

    This callable uses 7 internal helpers for metadata loading, rule parsing, and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L96-L105"><code>_normalize_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L129-L135"><code>_resolve_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L138-L145"><code>_resolve_lakehouse_table_path</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/config.py#L653-L693"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L178-L209"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/config.py#L696-L735"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `225`
- Inbound references count: 10
- Outbound references count: 4
- Used in templates: 00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore
- Glossary terms: source table, metadata lakehouse

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; loads {store.root}/Tables/{table} for classic targets or {store.root}/Tables/{schema}/{table} when the configured lakehouse target has schemas enabled.
- **inputs:** config, env, target, table, optional schema, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

### Inbound references

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_guardrail_rule_metadata`
- `fabricops_kit.governance_review._read_metadata_rows`
- `fabricops_kit.governance_review._read_metadata_table_or_empty`
- `fabricops_kit.governance_review.load_catalogue_profile_rows`
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._resolve_lakehouse_table_path`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L225-L277">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a353e064668bed2af14df04c16b5401637ee2d1d/src/fabricops_kit/fabric_input_output.py#L225-L277</a>
- Start line: `225`
- End line: `277`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, schema=None, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation summary

- Internal helper count: 7
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

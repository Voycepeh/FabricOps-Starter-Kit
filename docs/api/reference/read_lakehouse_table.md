# read_lakehouse_table

Read a Delta table from a configured Fabric lakehouse target by ABFSS path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:146`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L146-L192">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when notebook code needs a managed lakehouse Delta table by ABFSS path rather than a file path, registered Spark table name, or warehouse SQL query.

**Do not use when:**

- Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.

**Additional context:**

Reads a Delta table from {store.root}/Tables/{table} for the configured Fabric lakehouse target, including metadata, without requiring an attached default lakehouse.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment key such as `"dev"`. |
| `target` | `str` | Yes | Logical target name such as `"source"` or `"unified"`. |
| `table` | `str` | Yes | Table name under the lakehouse `Tables` area. |
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
- `fabricops_kit.governance_review._read_metadata_rows`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`

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
    └── _normalize_table_name(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for metadata loading and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L81-L90"><code>_normalize_table_name</code></a>
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

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `146`
- Inbound references count: 10
- Outbound references count: 3
- Used in templates: 00_env_config, 01_agreement, 02_pipeline, 03_governance, 99_explore
- Glossary terms: source table, metadata lakehouse

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; loads {store.root}/Tables/{table} and never uses registered Spark table names, partial namespaces, or the current/default lakehouse.
- **inputs:** config, env, target, table, optional schema, verbose flag, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

### Inbound references

- `fabricops_kit.config._setup_metadata_table_registry`
- `fabricops_kit.config._validate_metadata_table_registration`
- `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- `fabricops_kit.data_agreement._list_data_stewards`
- `fabricops_kit.governance_review._read_metadata_rows`
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- `fabricops_kit.metadata._load_notebook_registry`

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`
- `fabricops_kit.fabric_input_output._normalize_table_name`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L146-L192">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/fabric_input_output.py#L146-L192</a>
- Start line: `146`
- End line: `192`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

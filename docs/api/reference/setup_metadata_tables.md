# setup_metadata_tables

??? info "Downstream callables: 26"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>setup_metadata_tables(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L380-L390"><code>_active_steward_count(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L361-L371"><code>_existing_table_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L348-L358"><code>_is_table_not_found_error(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L90-L94"><code>_metadata_schema_field_names(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L307-L323"><code>_metadata_table_definitions(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L300-L304"><code>_metadata_data_access_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L141-L147"><code>_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L77-L87"><code>_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L22-L74"><code>_spark_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L201-L221"><code>_metadata_data_agreement_evidence_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L173-L198"><code>_metadata_data_agreement_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L258-L262"><code>_metadata_data_catalogue_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L286-L290"><code>_metadata_data_lineage_table_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L150-L170"><code>_metadata_data_steward_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L265-L269"><code>_metadata_enrichment_rules_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L279-L283"><code>_metadata_guardrail_results_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L272-L276"><code>_metadata_guardrail_rules_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L224-L255"><code>_metadata_notebook_registry_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L293-L297"><code>_metadata_pipeline_runs_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L326-L335"><code>_metadata_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L116-L138"><code>_resolved_metadata_table_names(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L97-L113"><code>_validate_setup_metadata_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L374-L377"><code>_write_bootstrap_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L338-L340"><code>_empty_dataframe_for_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L600-L639"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L557-L597"><code>_normalize_path_config(...)</code></a></div>
    </div>

Create or validate all FabricOps metadata tables through one setup action.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_metadata_tables.py:393`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L393-L500">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Usage guidance

### Use when

- Use after setup_notebook in 00_env_config when bootstrapping or validating the metadata store for an environment.

### Do not use when

- Do not use for writing business data or pipeline target tables; use write_lakehouse_table or write_warehouse_table for data outputs.

### Additional context

Prepares the canonical FabricOps metadata tables METADATA_DATA_ACCESS, METADATA_DATA_AGREEMENT, METADATA_DATA_AGREEMENT_EVIDENCE, METADATA_DATA_CATALOGUE, METADATA_DATA_LINEAGE_TABLE, METADATA_DATA_STEWARD, METADATA_ENRICHMENT_RULES, METADATA_GUARDRAIL_RESULTS, METADATA_GUARDRAIL_RULES, METADATA_NOTEBOOK_REGISTRY, and METADATA_PIPELINE_RUNS through configured metadata target ABFSS paths, not Spark partial namespaces or an attached default lakehouse.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_metadata_tables(
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None=None,
    require_active_steward: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
setup_metadata_tables(
    spark=spark,
    config=CONFIG,
    env="Sandbox",
)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Fabric Spark session used to create and write empty Delta tables. |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | Shared ``00_env_config`` configuration containing the metadata target. |
| `env` | `str` | Yes | Environment key to prepare. |
| `metadata_schema` | `str \| None` | No | Optional schema name for schema-enabled Fabric Lakehouses. Keep ``None`` for classic Lakehouses that store metadata tables under ``Tables/<table_name>``. |
| `require_active_steward` | `bool` | No | When True, raise if the steward registry does not contain active rows after bootstrap. |

## Returns

Setup result describing metadata table creation or validation status.

### Return interpretation

The returned setup status tells you which metadata tables were created or validated and whether the environment is ready for workflows that write evidence.

## Raises / Errors

Raises configuration, Spark, or storage errors when metadata routing or table preparation fails.

### Common failure causes

- The configured metadata lakehouse ABFSS path is missing or invalid.
- Spark cannot create or inspect metadata tables through the configured ABFSS paths.
- The selected environment does not include metadata routing.
- The caller lacks permission to create or update metadata tables.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)

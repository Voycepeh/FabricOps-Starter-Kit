# write_pipeline_lineage

??? info "Downstream callables: 39"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[pipeline/write_pipeline_lineage.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>write_pipeline_lineage(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L1294-L1406" class="reference-call-tree-callable"><code>_write_pipeline_lineage_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[config/metadata_keys.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_keys.py#L14-L15" class="reference-call-tree-callable"><code>_build_metadata_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[config/metadata_keys.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_keys.py#L9-L11" class="reference-call-tree-callable"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L153-L165" class="reference-call-tree-callable"><code>coerce_metadata_row_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L125-L150" class="reference-call-tree-callable"><code>_coerce_metadata_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L107-L122" class="reference-call-tree-callable"><code>metadata_table_schema_registry(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L87-L99" class="reference-call-tree-callable"><code>_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L32-L84" class="reference-call-tree-callable"><code>spark_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L102-L104" class="reference-call-tree-callable"><code>audit_schema_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108" class="reference-call-tree-callable"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83" class="reference-call-tree-callable"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L239-L247" class="reference-call-tree-callable"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634" class="reference-call-tree-callable"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587" class="reference-call-tree-callable"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60" class="reference-call-tree-callable"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L263-L287" class="reference-call-tree-callable"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L192-L197" class="reference-call-tree-callable"><code>normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150" class="reference-call-tree-callable"><code>resolve_configured_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170" class="reference-call-tree-callable"><code>resolve_lakehouse_table_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46" class="reference-call-tree-callable"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87" class="reference-call-tree-callable"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93" class="reference-call-tree-callable"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29" class="reference-call-tree-callable"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136" class="reference-call-tree-callable"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66" class="reference-call-tree-callable"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72" class="reference-call-tree-callable"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L200-L203" class="reference-call-tree-callable"><code>validate_dataframe_writer(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L229-L236" class="reference-call-tree-callable"><code>write_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L319-L320" class="reference-call-tree-callable"><code>_definition_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L345-L356" class="reference-call-tree-callable"><code>_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L74-L147" class="reference-call-tree-callable"><code>build_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L21-L33" class="reference-call-tree-callable"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L40-L64" class="reference-call-tree-callable"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L36-L37" class="reference-call-tree-callable"><code>_safe_str(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172" class="reference-call-tree-callable"><code>get_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │           └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161" class="reference-call-tree-callable"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │               └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148" class="reference-call-tree-callable"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L310-L316" class="reference-call-tree-callable"><code>_timestamp_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L11-L13" class="reference-call-tree-callable"><code>_audit_timestamp_value(...)</code></a></div>
    </div>

Write many-to-many source-to-target lineage evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/write_pipeline_lineage.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/write_pipeline_lineage.py#L10-L43">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage guidance

### Use when

- Use near the end of 02_pipeline after transformations and target config resolution have produced lineage-ready records.

### Additional context

Persists lineage records for a pipeline run so source tables, target tables, and transformation steps remain traceable.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_pipeline_lineage(
    spark: Any,
    run_id: str,
    context: dict[str, Any] | None=None,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Not documented yet |
| `run_id` | `str` | Yes | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `source_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Not documented yet |
| `target_definitions` | `Mapping[str, Mapping[str, Any]]` | Yes | Not documented yet |
| `relationships` | `list[Mapping[str, Any]] \| None` | No | Not documented yet |
| `dataset_name` | `str` | No | Not documented yet |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `metadata_table` | `str` | No | Not documented yet |
| `mode` | `str` | No | Not documented yet |

## Returns

Status, row count, and lineage rows.

### Return interpretation

A successful result indicates lineage rows were prepared for metadata persistence; review returned counts against expected transformation steps.

## Raises / Errors

Not documented yet

### Common failure causes

- Lineage records are empty or malformed.
- run_id, source, or target identifiers are missing.
- The metadata table cannot be written.
- Audit fields cannot be resolved from configuration.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Target table</span><span class="glossary-chip-definition">A written table produced by a pipeline output.</span> <a href="../../../reference/glossary/#target-table">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)

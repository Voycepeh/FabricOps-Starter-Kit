# write_pipeline_lineage

??? info "Downstream callables: 39"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[pipeline/write_pipeline_lineage.py]</span> <code>write_pipeline_lineage(...)</code> <span class="reference-call-tree-type">[public callable]</span> <span class="reference-call-tree-note">[architecture violation]</span></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L1291-L1403"><span class="reference-call-tree-source">[pipeline/shared.py]</span> <code>_write_pipeline_lineage_workflow(...)</code> <span class="reference-call-tree-type">[private helper]</span></a> <span class="reference-call-tree-note">[architecture violation]</span></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108"><span class="reference-call-tree-source">[config/shared.py]</span> <code>resolve_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_default_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L239-L247"><span class="reference-call-tree-source">[io/shared.py]</span> <code>configured_lakehouse_schema(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587"><span class="reference-call-tree-source">[config/shared.py]</span> <code>_normalize_path_config(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_normalize_schema_name(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L263-L287"><span class="reference-call-tree-source">[io/shared.py]</span> <code>write_lakehouse_table_core(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L192-L197"><span class="reference-call-tree-source">[io/shared.py]</span> <code>normalize_write_mode(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_configured_lakehouse_table(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_lakehouse_table_location(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_normalize_table_name(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_resolve_lakehouse_schema(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_resolve_lakehouse_table_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_join_lakehouse_area_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_target_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_lakehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_warehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L200-L203"><span class="reference-call-tree-source">[io/shared.py]</span> <code>validate_dataframe_writer(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L229-L236"><span class="reference-call-tree-source">[io/shared.py]</span> <code>write_delta_path(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L87-L88"><span class="reference-call-tree-source">[metadata.py]</span> <code>_build_metadata_table_key(...)</code> <span class="reference-call-tree-type">[private helper]</span></a> <span class="reference-call-tree-note">[architecture violation]</span></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L82-L84"><span class="reference-call-tree-source">[metadata.py]</span> <code>_stable_metadata_key(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L56-L68"><span class="reference-call-tree-source">[metadata.py]</span> <code>coerce_metadata_row_types(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L106-L121"><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <code>metadata_table_schema_registry(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L86-L98"><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <code>_schema(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L31-L83"><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <code>spark_types(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L101-L103"><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <code>audit_schema_fields(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L28-L53"><span class="reference-call-tree-source">[metadata.py]</span> <code>_coerce_metadata_value(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L318-L319"><span class="reference-call-tree-source">[pipeline/shared.py]</span> <code>_definition_name(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L344-L355"><span class="reference-call-tree-source">[pipeline/shared.py]</span> <code>_runtime_audit_fields(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L195-L268"><span class="reference-call-tree-source">[metadata.py]</span> <code>build_runtime_audit_fields(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_current_audit_timestamp(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_audit_timezone(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148"><span class="reference-call-tree-source">[config/shared.py]</span> <code>_validate_audit_timezone(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L149-L161"><span class="reference-call-tree-source">[metadata.py]</span> <code>_context_get(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L168-L192"><span class="reference-call-tree-source">[metadata.py]</span> <code>_runtime_context(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L164-L165"><span class="reference-call-tree-source">[metadata.py]</span> <code>_safe_str(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L309-L315"><span class="reference-call-tree-source">[pipeline/shared.py]</span> <code>_timestamp_value(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L23-L25"><span class="reference-call-tree-source">[metadata.py]</span> <code>_audit_timestamp_value(...)</code> <span class="reference-call-tree-type">[private helper]</span></a> <span class="reference-call-tree-note">[architecture violation]</span></div>
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

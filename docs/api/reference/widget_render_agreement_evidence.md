# widget_render_agreement_evidence

??? info "Downstream callables: 47"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[widgets/widget_render_agreement_evidence.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>widget_render_agreement_evidence(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108" class="reference-call-tree-callable"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83" class="reference-call-tree-callable"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[widgets/widget_render_agreement_evidence.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_agreement_evidence.py#L173-L319" class="reference-call-tree-callable"><code>_render_agreement_evidence_widget_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L577-L586" class="reference-call-tree-callable"><code>list_all_data_agreement_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L239-L247" class="reference-call-tree-callable"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634" class="reference-call-tree-callable"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587" class="reference-call-tree-callable"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60" class="reference-call-tree-callable"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L250-L260" class="reference-call-tree-callable"><code>read_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123" class="reference-call-tree-callable"><code>get_spark_session(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L216-L218" class="reference-call-tree-callable"><code>read_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150" class="reference-call-tree-callable"><code>resolve_configured_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170" class="reference-call-tree-callable"><code>resolve_lakehouse_table_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46" class="reference-call-tree-callable"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87" class="reference-call-tree-callable"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93" class="reference-call-tree-callable"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29" class="reference-call-tree-callable"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136" class="reference-call-tree-callable"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │           ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66" class="reference-call-tree-callable"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │           └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72" class="reference-call-tree-callable"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L382-L387" class="reference-call-tree-callable"><code>_coerce_row_dicts(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L316-L321" class="reference-call-tree-callable"><code>config_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L56-L131" class="reference-call-tree-callable"><code>render_searchable_selector(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L49-L53" class="reference-call-tree-callable"><code>_html_escape(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L25-L34" class="reference-call-tree-callable"><code>require_ipywidgets(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L37-L46" class="reference-call-tree-callable"><code>widget_common(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[widgets/widget_render_agreement_evidence.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_agreement_evidence.py#L117-L170" class="reference-call-tree-callable"><code>_save_agreement_evidence_records(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L74-L147" class="reference-call-tree-callable"><code>build_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L21-L33" class="reference-call-tree-callable"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L40-L64" class="reference-call-tree-callable"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L36-L37" class="reference-call-tree-callable"><code>_safe_str(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172" class="reference-call-tree-callable"><code>get_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161" class="reference-call-tree-callable"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148" class="reference-call-tree-callable"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L471-L473" class="reference-call-tree-callable"><code>write_widget_metadata_row(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L153-L165" class="reference-call-tree-callable"><code>coerce_metadata_row_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L125-L150" class="reference-call-tree-callable"><code>_coerce_metadata_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L107-L122" class="reference-call-tree-callable"><code>metadata_table_schema_registry(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L87-L99" class="reference-call-tree-callable"><code>_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L32-L84" class="reference-call-tree-callable"><code>spark_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L102-L104" class="reference-call-tree-callable"><code>audit_schema_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L263-L287" class="reference-call-tree-callable"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L192-L197" class="reference-call-tree-callable"><code>normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L200-L203" class="reference-call-tree-callable"><code>validate_dataframe_writer(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L229-L236" class="reference-call-tree-callable"><code>write_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[widgets/widget_render_agreement_evidence.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_agreement_evidence.py#L62-L114" class="reference-call-tree-callable"><code>_prepare_evidence_file_references(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><span class="reference-call-tree-source">[widgets/widget_render_agreement_evidence.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_agreement_evidence.py#L50-L59" class="reference-call-tree-callable"><code>_get_notebookutils(...)</code></a></div>
    </div>

Render the standalone agreement-evidence widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_render_agreement_evidence.py:26`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_render_agreement_evidence.py#L26-L47">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_agreement</span>
</p>

**Used in notebooks:** `01_agreement`

## Usage guidance

### Use when

- Use in 01_agreement when agreement records need supporting evidence that downstream users can audit.

### Additional context

Renders the supporting-evidence widget for agreement workflows so users can record links or files that justify an agreement.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_render_agreement_evidence(
    spark: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Fabric Spark session used for metadata reads, file writes, and append-only evidence metadata writes. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

## Returns

dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.

### Return interpretation

The widget records evidence references when saved; review the resulting metadata rows before relying on them in handover or audit flows.

## Raises / Errors

Not documented yet

### Common failure causes

- Evidence details are incomplete.
- File or URL references are malformed.
- Widget state is reset before saving.
- The configured metadata target is not writable.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)

# widget_enrich_table_metadata

??? info "Downstream callables: 6"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>widget_enrich_table_metadata(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L146-L166"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L31-L88"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L569-L688"><code>build_enrichment_rule_records(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1699-L1731"><code>guardrail_authoring_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L225-L233"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L334-L353"><code>write_lakehouse_table_core(...)</code></a></div>
    </div>

Render a consolidated column enrichment widget.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Source

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2693-L2708">View source on GitHub</a>

Implemented in `src/fabricops_kit/governance_review.py`:2693.

## Usage guidance

### Use when

- Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.

### Do not use when

- Do not use to author DQ rules or enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.

### Additional context

Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profiles.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    spark_session: Any,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `guardrail_state` | `Mapping[str, Any]` | Yes | Not documented yet |
| `spark_session` | `Any` | Yes | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `source_notebook_type` | `str` | No | Not documented yet |
| `created_by_role` | `str` | No | Not documented yet |

## Returns

Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.

### Return interpretation

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- The selected guardrail target has no column-level evidence.
- Configured custom fields omit a field name.
- Metadata lakehouse writes cannot be routed through 00_env_config.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.

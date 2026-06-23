# widget_author_schema_freshness_profile_rules

??? info "Downstream callables: 5"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>widget_author_schema_freshness_profile_rules(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L146-L166"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L31-L88"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1699-L1731"><code>guardrail_authoring_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L225-L233"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L329-L342"><code>write_lakehouse_table_core(...)</code></a></div>
    </div>

Render interactive schema, freshness, and profile-behavior guardrail authoring controls.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>governance_review</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Usage guidance

### Use when

- Use in 02_pipeline after selecting a guardrail target to save active self-approved rules, submit proposed rules, or bypass approval with a required reason.

### Do not use when

- Do not use to write evidence or runtime outcomes; it writes rule intent only to METADATA_GUARDRAIL_RULES when saving.

### Additional context

Renders interactive controls for authoring schema, freshness, and profile-behavior guardrail rule intent while applying the selected table governance policy.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `bypass_reason` | `str` | No | Not documented yet |
| `source_notebook_type` | `str` | No | Not documented yet |
| `created_by_role` | `str` | No | Not documented yet |
| `commit` | `bool` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget state exposes controls, preview records, and save actions that produce append-only guardrail rule rows under the table policy.

## Raises / Errors

Not documented yet

### Common failure causes

- The handover state is missing columns.
- Changing-data profile behavior has no watermark column.
- Freshness max lag is invalid.
- The metadata target cannot be written.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Profile mode</span><span class="glossary-chip-definition">Configured behavior mode for profile guardrails: static_data, changing_data, or skip.</span> <a href="../../../reference/glossary/#profile-mode">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.

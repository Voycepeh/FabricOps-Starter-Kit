# widget_author_dq_rules

??? info "Downstream callables: 40"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>widget_author_dq_rules(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2329-L2497"><code>_dq_rule_authoring_widget_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L188-L208"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L73-L130"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2290-L2326"><code>_dq_records_from_selection(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1897-L1914"><code>_base_guardrail_rule_record(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1699-L1731"><code>guardrail_authoring_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1685-L1697"><code>_authoring_lifecycle(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1666-L1682"><code>_lifecycle_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1655-L1657"><code>_is_no_approval_required(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L264-L272"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L256-L261"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L248"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │           ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1951-L1964"><code>_latest_rule(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1967-L1973"><code>_rule_params(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1976-L1987"><code>_write_rule_records(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L238-L246"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L754-L793"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L711-L751"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L48-L59"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L262-L286"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L191-L196"><code>normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L145-L149"><code>resolve_configured_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L165-L169"><code>resolve_lakehouse_table_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L36-L45"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L84-L86"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L89-L92"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L26-L28"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L125-L135"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L62-L65"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L68-L71"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L199-L202"><code>validate_dataframe_writer(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io.shared.py#L228-L235"><code>write_delta_path(...)</code></a></div>
    </div>

Render interactive manual DQ guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2738`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2738-L2767">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Usage guidance

### Use when

- Use in 02_pipeline after target selection when engineering needs to batch-create, edit, clear, or draft DQ guardrail rules.

### Do not use when

- Do not use for runtime DQ enforcement or catalogue profiling; use run_table_guardrails for execution and profile helpers for observed evidence.

### Additional context

Renders manual DQ authoring controls that produce editable guardrail rule intent rows under the selected table governance policy.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_dq_rules(
    state: Mapping[str, Any],
    dq_authoring_mode: str='manual',
    rule_type: str='not_null',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
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
| `dq_authoring_mode` | `str` | No | Not documented yet |
| `rule_type` | `str` | No | Not documented yet |
| `selected_columns` | `Iterable[str] \| None` | No | Not documented yet |
| `parameters` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `severity` | `str` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `bypass_reason` | `str` | No | Not documented yet |
| `source_notebook_type` | `str` | No | Not documented yet |
| `created_by_role` | `str` | No | Not documented yet |
| `commit` | `bool` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns mutable preview records; approved saves write guardrail rule intent to METADATA_GUARDRAIL_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- Rule suggestions cannot be parsed.
- Bypass reason is missing when bypass is requested.
- The metadata target cannot be written.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.

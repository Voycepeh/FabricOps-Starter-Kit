# widget_author_dq_rules

??? info "Downstream callables: 5"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>widget_author_dq_rules(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L146-L166"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L31-L88"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1699-L1731"><code>guardrail_authoring_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L225-L233"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L334-L353"><code>write_lakehouse_table_core(...)</code></a></div>
    </div>

Render interactive manual DQ guardrail authoring controls.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Source

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2738-L2767">View source on GitHub</a>

Implemented in `src/fabricops_kit/governance_review.py`:2738.

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

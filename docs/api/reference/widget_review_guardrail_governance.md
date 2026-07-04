# widget_review_guardrail_governance

??? info "Downstream callables: 3"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[widgets/widget_review_guardrail_governance.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>widget_review_guardrail_governance(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[widgets/widget_review_guardrail_governance.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_review_guardrail_governance.py#L42-L143" class="reference-call-tree-callable"><code>_guardrail_governance_review_widget_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108" class="reference-call-tree-callable"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83" class="reference-call-tree-callable"><code>get_default_fabric_context(...)</code></a></div>
    </div>

Render interactive controls for reviewing proposed and bypassed guardrail rules.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_review_guardrail_governance.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_review_guardrail_governance.py#L15-L39">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Usage guidance

### Use when

- Use in 03_governance after selecting a guardrail target to perform human review of enrichment and guardrail rule intent.

### Do not use when

- Do not use for automatic pipeline enforcement or profiles generation; it is an interactive governance review widget.

### Additional context

Renders governance review controls for reviewing proposed or bypass-active enrichment and guardrail rules, and applying approve, reject, or supersede actions.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_guardrail_governance(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Guardrail state with existing enrichment and guardrail rule records to review. |
| `spark_session` | `Any` | No | Fabric Spark session used when saving governance review decisions. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns controls, current rule history, and action helpers that write to enrichment or guardrail rule tables when invoked.

## Raises / Errors

Not documented yet

### Common failure causes

- No target state is selected.
- No proposed or bypassed rules are available for review.
- Unsupported governance action is selected.
- The metadata target cannot be written.

## See also

No related guides documented.

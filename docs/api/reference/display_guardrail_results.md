# display_guardrail_results

??? info "Downstream callables: 14"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>display_guardrail_results(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L431-L463"><code>_display_guardrail_results_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L358-L403"><code>build_guardrail_detail_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L263-L277"><code>_guardrail_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L242-L260"><code>_dq_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L208-L212"><code>_freshness_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L215-L239"><code>_profile_behavior_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L177"><code>_result_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L194-L205"><code>_schema_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L180-L191"><code>_next_action(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L158-L164"><code>_result_can_continue(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L148-L155"><code>_result_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L280-L287"><code>_table_keys(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L143-L145"><code>_yes_no(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L290-L355"><code>build_guardrail_summary_rows(...)</code></a></div>
    </div>

Return summary, detailed, or debug guardrail display output for Fabric notebooks.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:1332`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1332-L1336">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage guidance

### Use when

- Use in 02_pipeline immediately after run_table_guardrails and before stop_if_failed so users see guardrail outcomes before the notebook stops.

### Do not use when

- Do not use to mutate guardrail results or decide active rules; it is presentation-only.

### Additional context

Returns summary, detailed, or debug guardrail display output so Fabric notebooks show readable tables by default while preserving raw result bundles for developers.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def display_guardrail_results(
    result_bundle: Mapping[str, Any],
    mode: str='summary',
    spark_session: Any | None=None,
) -> Any:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `result_bundle` | `Mapping[str, Any]` | Yes | Not documented yet |
| `mode` | `str` | No | Not documented yet |
| `spark_session` | `Any \| None` | No | Not documented yet |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

Summary and detailed modes return display-friendly rows or Spark DataFrames; debug mode returns the raw nested guardrail summary or bundle.

## Raises / Errors

Not documented yet

### Common failure causes

- Mode is not summary, detailed, or debug.
- The Spark session cannot create a DataFrame from display rows.
- The result bundle is malformed.
- The caller expects debug internals while using summary mode.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.

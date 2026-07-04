# display_guardrail_results

??? info "Downstream callables: 14"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[pipeline/display_guardrail_results.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>display_guardrail_results(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L700-L732" class="reference-call-tree-callable"><code>_display_guardrail_results_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L627-L672" class="reference-call-tree-callable"><code>build_guardrail_detail_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L532-L546" class="reference-call-tree-callable"><code>_guardrail_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L511-L529" class="reference-call-tree-callable"><code>_dq_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L477-L481" class="reference-call-tree-callable"><code>_freshness_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L484-L508" class="reference-call-tree-callable"><code>_profile_behavior_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L436-L446" class="reference-call-tree-callable"><code>_result_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L463-L474" class="reference-call-tree-callable"><code>_schema_reason(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L449-L460" class="reference-call-tree-callable"><code>_next_action(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L427-L433" class="reference-call-tree-callable"><code>_result_can_continue(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L417-L424" class="reference-call-tree-callable"><code>_result_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L549-L556" class="reference-call-tree-callable"><code>_table_keys(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L412-L414" class="reference-call-tree-callable"><code>_yes_no(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[pipeline/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/shared.py#L559-L624" class="reference-call-tree-callable"><code>build_guardrail_summary_rows(...)</code></a></div>
    </div>

Return summary, detailed, or debug guardrail display output for Fabric notebooks.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/display_guardrail_results.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/display_guardrail_results.py#L10-L14">View on GitHub</a>
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

## See also

No related guides documented.

# display_guardrail_results

## Call-flow summary

- Downstream callables: 37
- Shared helpers: 2
- Private helpers: 35

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=display_guardrail_results">Open focused call flow in dashboard</a>


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

## Usage notes

Use in 02_pipeline immediately after run_table_guardrails and before stop_if_failed so users see guardrail outcomes before the notebook stops.

Do not use to mutate guardrail results or decide active rules; it is presentation-only.

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

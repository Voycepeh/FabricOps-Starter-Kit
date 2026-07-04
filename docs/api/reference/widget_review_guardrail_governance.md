# widget_review_guardrail_governance

## Call-flow summary

- Downstream callables: 85
- Shared helpers: 41
- Private helpers: 44

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=widget_review_guardrail_governance">Open focused call flow in dashboard</a>


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

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


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

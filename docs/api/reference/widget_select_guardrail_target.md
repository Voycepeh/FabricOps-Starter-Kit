# `widget_select_guardrail_target`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render an interactive target selector for guardrail authoring and governance review.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_select_guardrail_target.py:14`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_select_guardrail_target.py#L14-L32">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_review</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_review`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_guardrail_target(
    spark_session: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `Any` | Yes | Fabric Spark session used to read metadata catalogue, enrichment, and guardrail rule rows. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The returned state includes environment, dataset, table, metadata keys, profile rows, existing rules, and governance policy values for downstream widgets.

## Raises / Errors

Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.

### Common failure causes

- METADATA_DATA_PROFILED has no profiles.
- The selected table lacks metadata identity fields.
- Metadata tables cannot be read.
- ipywidgets is unavailable.

## See also

No related guides documented.


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |


</details>

# `widget_author_guardrails`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render versioned table-level Schema, Freshness, and Changes guardrail controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_author_guardrails.py:139`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_author_guardrails.py#L139-L401">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_governance</span>
</p>

**Used in notebooks:** `01_governance`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_guardrails(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> form = widget_author_guardrails(guardrail_target_state)
>>> form["version"]
1

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Selected table state including its canonical table key, catalogue columns, and existing rules. |
| `spark_session` | `Any` | No | Fabric Spark session used to append saved metadata rows. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active ``FABRIC_CONTEXT``. |
| `commit` | `bool` | No | Save the initial form selection immediately. The default renders a form. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget state exposes controls, preview records, and save actions that produce append-only guardrail rule rows under the table policy.

## Raises / Errors

Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.

### Common failure causes

- The selected table state is missing columns or its canonical key.
- Freshness maximum age is invalid.
- The metadata target cannot be written.

## Notes

<div class="reference-docstring-notes" markdown="1">

Run in Microsoft Fabric after ``00_env_config`` and table selection. The
widget authors configuration only; it has no approval workflow. Select the
required table columns and preserve their expected data types as the schema
guardrail.

</div>

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


</details>

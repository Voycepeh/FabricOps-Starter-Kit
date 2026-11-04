# `widget_activate_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Review and promote manually tested notebooks into separate Governed copies.


## Usage notes

Use to review destination bindings and promote a completed manual Dry Run.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_activate_pipeline(dry_run=preview)
review = ui["actions"]["review"]()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_pipeline(
    *,
    pipeline_id=None,
    dry_run=None,
    context=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Stable Pipeline ID used to filter retained immutable version records. |
| `dry_run` | `PipelineSession \| None` | No | `None` | Completed and finalized manual Dry Run session. Without it the widget displays retained promotions without enabling the promotion action. |
| `context` | `dict \| None` | No | `None` | Configured notebook context; central Metadata routing is preserved. |

</div>

## Returns

dict
    Widget, scoped version records, controls, review action and promotion
    action. Review creates no artifacts; promotion archives and clones before
    conditionally switching the active version.

## Raises / Errors

ValueError
    If pipeline identity or Registry records are ambiguous or invalid.
RuntimeError
    If metadata, widgets or Fabric APIs are unavailable. Action errors remain
    visible without erasing the review or previous active version.

## Notes

<div class="reference-docstring-notes" markdown="1">

Only notebook code is frozen; dependencies are not. Saved-definition checks
have TOCTOU limits. Governed remains blocked pending signed-in Fabric validation.
Engineers manage schedules; this widget never migrates schedules. A Governed
folder organizes same-workspace copies and confers no permissions.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_pipeline.py:16`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_pipeline.py#L16-L130">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
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
| Preview | 0.3.0 |
| Preview | 0.3.1 |


</details>

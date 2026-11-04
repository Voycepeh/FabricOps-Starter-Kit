# `widget_activate_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Import immutable Engineering submissions and independently approve, reject or revoke them.


## Usage notes

Use in Governance to import and review portable submissions without Engineering workspace access.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_activate_pipeline()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_pipeline(*, pipeline_id=None, package=None, context=None) -> dict
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Filter imported candidates and decision history by logical Pipeline ID. |
| `package` | `str \| bytes \| dict \| None` | No | `None` | Portable Engineering submission. The import action persists a verified immutable copy under Governance's identity; opening the widget does not. |
| `context` | `dict \| None` | No | `None` | Configured Governance notebook context and central Metadata routing. |

</div>

## Returns

dict
    Widget, controls, state and import/review/decide/refresh actions. Approval
    grants deployment authority; Engineering must separately deploy it.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

This widget never opens Engineering notebooks or creates deployed items.
Integrity does not attest the truth of engineer-provided test outcomes.
Review source code, Dry Run claims and independently resolved active policies.
Rollback and restoration packages require separate explicit decisions here.
Governance owns the entire Metadata Lakehouse; schema names are routing, not
restrictions on privileged Governance workspace members.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_pipeline.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_pipeline.py#L17-L168">View on GitHub</a>
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

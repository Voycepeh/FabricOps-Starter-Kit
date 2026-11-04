# `widget_deploy_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Export Engineering submissions and deploy exact independently approved snapshots.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_deploy_pipeline(dry_run=preview)
ui = widget_deploy_pipeline(pipeline_id=PIPELINE_ID)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_deploy_pipeline(*, pipeline_id=None, dry_run=None, context=None) -> dict
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Filter approvals and retained versions by logical Pipeline ID. |
| `dry_run` | `PipelineSession \| None` | No | `None` | Completed Engineering Dry Run to export. Deployment uses persisted Governance records and does not depend on this session. |
| `context` | `dict \| None` | No | `None` | Configured Engineering notebook context for the destination workspace. |

</div>

## Returns

dict
    Widget, state, controls and export/review/deploy actions. Portable JSON
    can be downloaded and imported in a separate Governance session.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

Engineering cannot decide approvals through this workflow. Fabric permissions
must deny Engineering writes to Governance tables and accepted package copies.
Rollback exports an earlier implementation for a new approval and version.
Restoration exports the active implementation for explicit recovery approval.
Deployment readback verifies the complete definition, including non-code cells.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_deploy_pipeline.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_deploy_pipeline.py#L17-L146">View on GitHub</a>
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


</details>

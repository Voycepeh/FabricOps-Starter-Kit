# `widget_activate_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Review complete persisted Testing and activate an exact whole pipeline.


## Usage notes

Use after finalize_pipeline commits complete successful governed Test results.


## Example usage

Example usage not documented yet.

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_pipeline(
    *,
    pipeline_id=None,
    spark_session=None,
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
| `pipeline_id` | `—` | No | `None` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |
| `context` | `—` | No | `None` | Not documented yet |

</div>

## Returns

Not documented yet

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Displays environment, current/proposed table contracts, writer ownership,
affected pipelines, missing tests, conflicts and complete release readiness.
Completed Testing runs missing contracts are listed by table ID and excluded
from review. Extra candidate controls appear for shared-table dependencies.
Supply an immutable release version for
every selected pipeline. The backend revalidates complete Testing, exact
contracts, Agreement and processing configuration at review and again at approval.

One explicit approval publishes the entire environment revision atomically.
Stale review, missing tests, competing writers, contract conflicts or affected
running executions block approval. Approval never deploys or writes business
data. Failed commits cannot expose a partial release. Returns widget state,
refresh, review_release and perform_activation. Metadata errors raise or are
displayed by button actions; opening the widget changes no approval.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_pipeline.py:78`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_pipeline.py#L78-L239">View on GitHub</a>
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

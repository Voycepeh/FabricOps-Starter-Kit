# `promote_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Archive and promote one reviewed manually tested notebook into a separate Governed item.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = promote_pipeline(review, governance_confirmed=True)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def promote_pipeline(review: dict, *, governance_confirmed: bool=False) -> dict
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `review` | `dict` | Yes | `—` | Exact candidate returned by the Pipeline Promotion widget review action. Contains the saved notebook, destination physical bindings, exact Contracts and expected active version. Keep this object for safe lost-ack retries. |
| `governance_confirmed` | `bool` | No | `False` | Confirm the displayed review; actual Fabric permissions authorize changes. |

</div>

## Returns

dict
    Frozen per-version METADATA_PIPELINE_REGISTRY row. An active row does not
    override the pending signed-in Fabric validation gate for Governed starts.

## Raises / Errors

ValueError
    If review, bindings, Contracts or expected version changed.
RuntimeError
    If notebook APIs, archive readback or atomic commit cannot be verified.
    Staged artifacts are retained; the prior active version remains intact.

## Notes

<div class="reference-docstring-notes" markdown="1">

The complete notebook is frozen; imported dependencies are not. Same-workspace
promotion creates a separate notebook in Governed/. Folders confer no access
protection. Schedules are engineer-owned and never silently moved. Saved code
checks have a TOCTOU limitation and cannot prevent privileged Spark bypass.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/activated_pipeline/promote_pipeline.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/activated_pipeline/promote_pipeline.py#L5-L44">View on GitHub</a>
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

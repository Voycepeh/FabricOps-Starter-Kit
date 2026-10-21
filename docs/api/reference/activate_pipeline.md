# `activate_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Approve an exact successfully tested whole pipeline.



## Example usage

Example usage not documented yet.

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def activate_pipeline(
    *,
    testing_run_id,
    candidate_fingerprint,
    pipeline_name,
    pipeline_version,
    agreement_id,
    agreement_version,
    executable_path,
    governance_confirmed=False,
    expected_active_id=None,
    spark_session=None,
    context=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `testing_run_id` | `—` | Yes | `—` | Not documented yet |
| `candidate_fingerprint` | `—` | Yes | `—` | Not documented yet |
| `pipeline_name` | `—` | Yes | `—` | Not documented yet |
| `pipeline_version` | `—` | Yes | `—` | Not documented yet |
| `agreement_id` | `—` | Yes | `—` | Not documented yet |
| `agreement_version` | `—` | Yes | `—` | Not documented yet |
| `executable_path` | `—` | Yes | `—` | Not documented yet |
| `governance_confirmed` | `—` | No | `False` | Not documented yet |
| `expected_active_id` | `—` | No | `None` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |
| `context` | `—` | No | `None` | Not documented yet |

</div>

## Returns

Not documented yet

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Requires complete committed Testing evidence, exact candidate and effective
Agreement identity, unchanged executable/dependencies/contracts and explicit
Governance confirmation. A switch also requires expected_active_id. This
action neither deploys artifacts nor publishes data.

Returns the immutable METADATA_ACTIVATED_PIPELINE version and audit fields.
Invalid evidence or a stale switch raises ValueError; metadata failures raise.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/activated_pipeline/activate_pipeline.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/activated_pipeline/activate_pipeline.py#L5-L22">View on GitHub</a>
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

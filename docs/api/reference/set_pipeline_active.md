# `set_pipeline_active`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Explicitly switch or deactivate an immutable approved version.



## Example usage

Example usage not documented yet.

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def set_pipeline_active(
    activated_pipeline_id,
    *,
    active,
    expected_active_id,
    governance_confirmed=False,
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
| `activated_pipeline_id` | `—` | Yes | `—` | Not documented yet |
| `active` | `—` | Yes | `—` | Not documented yet |
| `expected_active_id` | `—` | Yes | `—` | Not documented yet |
| `governance_confirmed` | `—` | No | `False` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |
| `context` | `—` | No | `None` | Not documented yet |

</div>

## Returns

Not documented yet

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Require Governance confirmation and the currently active ID (None for no
active version). Saved environment selections are never changed by this call.
Returns the selected version with its new is_active state; stale state fails.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/activated_pipeline/set_pipeline_active.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/activated_pipeline/set_pipeline_active.py#L5-L27">View on GitHub</a>
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

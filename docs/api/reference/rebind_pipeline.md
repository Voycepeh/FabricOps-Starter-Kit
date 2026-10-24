# `rebind_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Move an existing environment binding to the caller after notebook reupload.


## Usage notes

Explicit administration of an Engineering Pipeline Registry binding.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE_ID = rebind_pipeline(PIPELINE_ID,
    previous_workspace_id=old_workspace_id, previous_notebook_id=old_notebook_id)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def rebind_pipeline(
    pipeline_id,
    *,
    previous_workspace_id,
    previous_notebook_id,
    config_workspace_id=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str` | Yes | `—` | Persisted permanent Pipeline UUIDv4. |
| `previous_workspace_id` | `str` | Yes | `—` | Workspace ID of the existing environment binding being replaced. |
| `previous_notebook_id` | `str` | Yes | `—` | Notebook ID of the existing environment binding being replaced. |
| `config_workspace_id` | `str \| None` | No | `None` | Workspace hosting 00_env_config; defaults to the caller workspace. |

</div>

## Returns

str
    The unchanged Pipeline UUID, now bound to the current notebook.

## Raises / Errors

ValueError
    If the UUID, previous binding or current notebook ownership conflicts.
RuntimeError
    If the registry transaction cannot be confirmed; inspect and retry setup.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Supply the exact previous workspace and notebook IDs from the registry.
Stale expectations and a caller already owned by another pipeline fail.
Approved releases remain immutable. Rerun Test and approve a new release
when processing configuration or physical data destinations differ.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/rebind_pipeline.py:6`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/rebind_pipeline.py#L6-L44">View on GitHub</a>
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

# `create_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Generate and register a UUIDv4 for an independent, unregistered notebook.


## Usage notes

Explicit administration of an Engineering Pipeline Registry binding.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE_ID = create_pipeline()
pipeline = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Test")
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def create_pipeline(*, config_workspace_id=None)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `config_workspace_id` | `str \| None` | No | `None` | Workspace hosting 00_env_config; defaults to the caller workspace. |

</div>

## Returns

str
    Permanent UUIDv4 registered to the caller notebook in its environment.

## Raises / Errors

ValueError
    If the caller is already registered or Fabric notebook identity is missing.
RuntimeError
    If registration cannot be confirmed; rerun setup_pipeline to recover it.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call in an independent notebook copy and save the returned UUID as
PIPELINE_ID. An already registered notebook fails rather than changing identity.
This administrative write grants no activation or Live permission.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/create_pipeline.py:6`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/create_pipeline.py#L6-L36">View on GitHub</a>
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

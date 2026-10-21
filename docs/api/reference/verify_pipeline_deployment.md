# `verify_pipeline_deployment`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Verify deployment artifacts and persist explicit physical bindings.



## Example usage

Example usage not documented yet.

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def verify_pipeline_deployment(
    *,
    deployment_path,
    authority_environment,
    sources,
    targets,
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
| `deployment_path` | `—` | Yes | `—` | Not documented yet |
| `authority_environment` | `—` | Yes | `—` | Not documented yet |
| `sources` | `—` | Yes | `—` | Not documented yet |
| `targets` | `—` | Yes | `—` | Not documented yet |
| `spark_session` | `—` | No | `None` | Not documented yet |
| `context` | `—` | No | `None` | Not documented yet |

</div>

## Returns

Not documented yet

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Run after deploying the tested executable and definitions with Fabric tooling.
Fetches the actual Fabric notebook definition and compares its executable
identity with the approval before recording workspace/notebook/store bindings
in deployment.json. Missing export permission or changed deployed code fails
without creating or updating the binding file.
It does not deploy notebooks, activate versions, select Live or publish data.
Every Live setup rechecks the artifacts, approval, dependencies and bindings.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/activated_pipeline/verify_pipeline_deployment.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/activated_pipeline/verify_pipeline_deployment.py#L10-L46">View on GitHub</a>
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

# `setup_governance`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Initialize registered workspace configuration without starting a pipeline.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_governance()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_governance(*, target_workspace_id: str | None=None, spark_session=None)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `target_workspace_id` | `str \| None` | No | `None` | Registered target workspace; selectable only from the pinned Governance Workspace. |
| `spark_session` | `object` | No | `None` | Fabric Spark session; otherwise the active session is used. |

</div>

## Returns

dict
    Resolved, context-local FrameworkConfig, deployment environment and runtime identity.

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Governance administrators may select a registered engineering workspace from
the Governance Workspace to author contracts and activate its pipelines.
Otherwise the runtime workspace is authoritative. No deployment environment
or resource override is accepted. This function does not create metadata or
grant permissions. Independent public IO can also use an explicit context.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_governance.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_governance.py#L5-L33">View on GitHub</a>
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

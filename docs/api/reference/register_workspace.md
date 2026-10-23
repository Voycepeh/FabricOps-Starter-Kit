# `register_workspace`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Publish one complete workspace registration using an explicit reviewed registry token.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
token = register_workspace(registration, expected_token=reviewed_token, spark_session=spark)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def register_workspace(registration: dict, *, expected_token: str, spark_session=None)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `registration` | `dict` | Yes | `—` | Complete workspace_id, display_name, environment, status, resources, notebooks and settings mapping. Metadata must match the pinned locator. |
| `expected_token` | `str` | Yes | `—` | Registry token reviewed by the administrator. Stale tokens fail closed. |
| `spark_session` | `object` | No | `None` | Fabric Spark session. |

</div>

## Returns

str
    Confirmed registry token for the new snapshot.

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Run in the pinned Governance Workspace with Fabric write permission on the
registry table. The workspace check is a usage guard; Fabric permissions are
the security boundary. Existing entries are replaced atomically, never merged
with notebook parameters. A changed registry requires fresh pipeline setup.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/register_workspace.py:7`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/register_workspace.py#L7-L41">View on GitHub</a>
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

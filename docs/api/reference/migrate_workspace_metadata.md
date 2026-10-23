# `migrate_workspace_metadata`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Assign one legacy environment to exactly one inactive registered workspace.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
token = migrate_workspace_metadata(legacy_environment=legacy_environment, workspace_id=workspace_id, expected_token=reviewed_token, workloads_stopped=True, spark_session=spark)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def migrate_workspace_metadata(
    *,
    legacy_environment: str,
    workspace_id: str,
    expected_token: str,
    workloads_stopped: bool=False,
    spark_session=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `legacy_environment` | `str` | Yes | `—` | Exact previous environment key, without inference or defaults. |
| `workspace_id` | `str` | Yes | `—` | Inactive registered workspace receiving this environment's metadata. |
| `expected_token` | `str` | Yes | `—` | Reviewed activation/reservation token from read_activation_state. |
| `workloads_stopped` | `bool` | No | `False` | Explicit administrator confirmation that native Fabric executions stopped. |
| `spark_session` | `object` | No | `None` | Fabric Spark session with administrator metadata write permissions. |

</div>

## Returns

str
    Confirmed activation/reservation token after migration.

## Raises / Errors

Not documented yet

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Administrators must stop and verify all Fabric jobs first. The registry must
contain no active workspaces during migration. Delta updates are idempotent
per table; rerun after an interrupted migration while registrations remain
inactive. Contract payloads, IDs, versions, manifests and historical outcomes
remain unchanged. Original environment labels are retained in an additive
audit column. No legacy approval can be inherited by a second workspace.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/migrate_workspace_metadata.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/migrate_workspace_metadata.py#L8-L93">View on GitHub</a>
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

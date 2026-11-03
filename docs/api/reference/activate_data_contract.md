# `activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Activate one frozen Contract independently for a workspace/Table ID.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    expected_activation_id=None, activation_id=OPERATION_ID,
    governance_confirmed=True)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def activate_data_contract(
    table_id: str,
    contract_id: str,
    contract_version: int,
    *,
    expected_activation_id: str | None,
    activation_id: str,
    workspace_id: str | None=None,
    governance_confirmed: bool=False,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str` | Yes | `—` | Exact logical Table ID and globally frozen Contract identity. |
| `contract_id` | `str` | Yes | `—` | Not documented yet |
| `contract_version` | `int` | Yes | `—` | Exact frozen positive version; never a latest-version fallback. |
| `expected_activation_id` | `str \| None` | Yes | `—` | Previously reviewed activation ID; None asserts no existing activation. |
| `activation_id` | `str` | Yes | `—` | Unique operation ID retained for safe retry after a lost acknowledgement. |
| `workspace_id` | `str \| None` | No | `None` | Physical table workspace, defaulting to the current execution scope. Metadata continues to use the configured central Metadata Lakehouse. |
| `governance_confirmed` | `bool` | No | `False` | Review confirmation. Actual metadata storage permissions authorize writes; this flag grants no permissions. |

</div>

## Returns

dict
    Committed METADATA_DATA_CONTRACT_ACTIVATION row, including revision.

## Raises / Errors

ValueError
    If the exact frozen Contract, physical binding, operation ID or expected
    activation is invalid, or another Table ID aliases the physical table.
RuntimeError
    If a writer holds the publication claim, Fabric/Spark is unavailable or
    transactional readback fails. Reconcile interrupted writers before retry.

## Notes

<div class="reference-docstring-notes" markdown="1">

Call setup_notebook first. Frozen definitions are immutable and global;
activations are per physical workspace/Table ID. Existing admitted runs keep
captured Contracts; the next run resolves the new version. Normal setup never
drops development metadata. No business target or Processing State is changed.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_contract/activate_data_contract.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_contract/activate_data_contract.py#L5-L65">View on GitHub</a>
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

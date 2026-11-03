# `activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Activate one frozen Contract independently for a workspace/Table ID.



## Example usage

<div class="reference-example-usage" markdown="1">

```python
activated = activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    expected_token=reviewed_token, governance_confirmed=True)
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
    expected_token: str,
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
| `contract_version` | `int` | Yes | `—` | Exact frozen version, never a latest-version fallback. |
| `expected_token` | `str` | Yes | `—` | Current Registry control token from the reviewed snapshot. Stale review is rejected; refresh and review before retrying. |
| `workspace_id` | `str \| None` | No | `None` | Target execution workspace; defaults to the notebook configuration scope. Central Metadata routing remains separate from this activation scope. |
| `governance_confirmed` | `bool` | No | `False` | Explicit confirmation of the reviewed governance change. This is not authentication: metadata write principals must be trusted and restricted by tenant permissions. |

</div>

## Returns

dict
    Committed table_contract_activation record with immutable activation ID.

## Raises / Errors

ValueError
    If confirmation, exact frozen identity, current token, destination or
    active pipeline compatibility fails, or an affected execution must drain.
RuntimeError
    If notebook/Spark context, atomic publication or exact readback fails.
    A failed acknowledgement requires inspecting the Registry and audit
    transaction before another governance decision.

## Notes

<div class="reference-docstring-notes" markdown="1">

Call setup_notebook first. The central configured Metadata Lakehouse is used.
The one Registry transaction retains a durable before/after audit snapshot.
No business data, Processing State or historical Run is changed.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

This action is independent of pipeline activation. It protects the Table ID
and its physical destination from Ungoverned publication. It never unfreezes
or copies a Contract, activates a pipeline or enables Governed execution.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_contract/activate_data_contract.py:5`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_contract/activate_data_contract.py#L5-L67">View on GitHub</a>
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

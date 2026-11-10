# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Review and activate an exact frozen Contract in its physical workspace.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">01_governance</span>
</p>

## Usage notes

Use after widget_data_contract freezes a version to activate it for a physical table and workspace.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
ui = widget_activate_data_contract()
ui = widget_activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    workspace_id=PHYSICAL_WORKSPACE_ID)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    table_id: str | None=None,
    contract_id: str | None=None,
    contract_version: int | None=None,
    *,
    workspace_id: str | None=None,
    context=None,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str \| None` | No | `None` | Preselect an exact logical table and frozen Contract. With no arguments, select from registered physical workspaces/tables and frozen versions. |
| `contract_id` | `str \| None` | No | `None` | Not documented yet |
| `contract_version` | `int \| None` | No | `None` | Exact positive frozen version to preselect; never a latest fallback. |
| `workspace_id` | `str \| None` | No | `None` | Physical table workspace. With a supplied table, defaults to the current configured scope. Governance metadata stays in its central Lakehouse. |
| `context` | `dict \| None` | No | `None` | Configured Governance notebook context. |

</div>

## Returns

dict
    Widget, selection/review state, controls and review/activate/refresh actions.
    Opening changes no metadata. Backend mutation independently revalidates
    exact bindings, policy hashes and the reviewed current activation ID.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

Governance owns all central metadata, so selection uses Catalogue records
without opening Engineering workspaces. Actual Fabric permissions authorize
writes. Each physical activation selects one frozen Contract and at most one
Agreement; cross-workspace execution requires effective associated terms.
Retained revisions provide history independently of notebook promotion.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:18`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L18-L202">View on GitHub</a>
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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |
| Discontinued | 0.3.0 |
| Discontinued | 0.3.1 |
| Live | 0.4.0 |
| Live | 0.4.1 |


</details>

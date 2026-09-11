# `widget_select_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Resolve current-notebook Lineage and select one immutable Data Contract independently per table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_select_data_contract.py:89`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_select_data_contract.py#L89-L288">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_data_contract(*, spark_session=None, context=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> selection = widget_select_data_contract()
>>> selection["select"]("table-orders", "orders-contract", 3)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `dict` | No | FabricOps context normally established by ``00_env_config``. The current ``notebook_id``, optional ``workspace_id``, and environment scope Lineage. |

## Returns

dict
    Notebook scope, role-preserving table states, table-scoped resolved
    contracts, controls, and a Development ``select`` callable.

### Return interpretation

Development selections are stored independently under each discovered table_id in data_contract_overrides; Production returns the read-only active mapping and ignores overrides.

## Raises / Errors

ValueError
    If notebook identity is missing, a requested version is unavailable,
    or Production has no active contract for a Lineage-linked table.
RuntimeError
    If Production has multiple active versions for a lineage-linked table.

### Common failure causes

- The current notebook identity or Lineage is missing.
- A discovered table has no eligible immutable version.
- The selected version belongs to another table.
- The frozen contract payload is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Development may independently select a frozen, active, or superseded
immutable version for each Lineage-linked ``table_id`` and stores it in
``data_contract_overrides``. Draft and rejected versions are excluded.
An unselected Development table runs without contract-backed enforcement.
Production ignores overrides, exposes no picker, and resolves exactly one
active version per linked table. This widget never activates metadata.

</div>

## See also

No related guides documented.


<details>
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

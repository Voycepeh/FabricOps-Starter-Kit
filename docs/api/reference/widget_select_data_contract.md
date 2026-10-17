# `widget_select_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Resolve current-notebook Lineage and select one immutable Data Contract independently per table.


## Usage notes

Use after baseline Lineage exists and before governed checks so Development selects immutable versions per Source/Target table and Production resolves active versions automatically.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
selection = widget_select_data_contract()
selection["set_mode"]("table-orders", "validate", "orders-contract", 3)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_data_contract(*, spark_session=None, context=None)
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `spark_session` | `object` | No | `None` | Spark session override. |
| `context` | `dict` | No | `None` | FabricOps context normally established by ``00_env_config``. The current ``notebook_id``, optional ``workspace_id``, and environment scope Lineage. |

</div>

## Returns

dict
    Notebook scope, role-preserving table states, table-scoped execution
    modes and contract identities, controls, a ``set_mode`` callable, and
    a ``validate`` operation that evaluates the selected target candidate.

### Return interpretation

Each source remains in enforce mode. Each target returns its independent enforce or validate mode and exact contract identity; the validate operation evaluates the selected frozen candidate later against the transformed target DataFrame.

## Raises / Errors

ValueError
    If notebook identity is missing, a requested frozen version is
    unavailable, or Production enforcement has no active contract for a
    Lineage-linked table.
RuntimeError
    If Production has multiple active versions for a lineage-linked table.

### Common failure causes

- The current notebook identity or Lineage is missing.
- A discovered table has no eligible immutable version.
- The selected version belongs to another table.
- The frozen contract payload is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Every Lineage-linked source remains in ``enforce`` mode. Each target can
independently use ``enforce`` or ``validate``. Enforce resolves the
environment's enforceable contract without showing a version picker;
Production requires exactly one frozen version tagged active. Target validation exposes
frozen candidates and never installs the candidate as an enforcement
override. This widget never activates metadata.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_select_data_contract.py:141`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_select_data_contract.py#L141-L507">View on GitHub</a>
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


</details>

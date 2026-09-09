# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Explicitly link an exact Data Agreement version and activate a frozen table Data Contract.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:74`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L74-L281">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_governance</span>
</p>

**Used in notebooks:** `01_governance`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_activate_data_contract(
    table_id: str | None=None,
    contract_id: str | None=None,
    contract_version: int | None=None,
    agreement_id: str | None=None,
    agreement_version: str | None=None,
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> state = widget_activate_data_contract(
...     table_id="orders", contract_version=2,
...     agreement_id="agreement-orders", agreement_version="1.0.0",
... )
>>> state["activate"]()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str \| None` | No | Initial governed table identity. |
| `contract_id` | `str \| None` | No | Initial frozen Data Contract lifecycle identity. |
| `contract_version` | `int \| None` | No | Initial exact immutable Data Contract version. |
| `agreement_id` | `str \| None` | No | Initial Data Agreement lifecycle identity selected at activation time. |
| `agreement_version` | `str \| None` | No | Initial exact Data Agreement version selected at activation time. |
| `target` | `str` | No | Configured metadata Lakehouse target. |
| `schema` | `str \| None` | No | Metadata Lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | FabricOps context normally established by ``00_env_config``. |

## Returns

dict
    Selection state, immutable review, controls, and an ``activate`` callable.

### Return interpretation

review combines the immutable payload with the proposed Agreement linkage; activate writes the linkage and lifecycle fields and reports whether an atomic update occurred.

## Raises / Errors

ValueError
    If the contract or exact Agreement version is missing, mismatched, or ineligible.
RuntimeError
    If active-contract metadata is ambiguous or the atomic Delta update fails.

### Common failure causes

- The selected version does not exist or belongs to another table.
- The selected contract is rejected or its frozen payload is invalid.
- The exact Data Agreement version does not exist.
- The active version is already linked to a different Agreement.
- The metadata table contains multiple active versions.

## Notes

<div class="reference-docstring-notes" markdown="1">

Activation writes Agreement linkage only to the selected contract version,
atomically activates it, and supersedes the prior active version for the same
``table_id``. It never changes the frozen payload and does not deploy notebooks.
Repeating the same activation is idempotent; conflicting relink requests fail.

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

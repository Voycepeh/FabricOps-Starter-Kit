# `widget_activate_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Manually select the frozen Data Contract version used by Production.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_activate_data_contract.py:88`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_activate_data_contract.py#L88-L221">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

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
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> state = widget_activate_data_contract(table_id="orders", contract_version=2)
>>> state["activate"]()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str \| None` | No | Initial governed table identity. |
| `contract_id` | `str \| None` | No | Initial saved contract lifecycle identity. |
| `contract_version` | `int \| None` | No | Initial exact saved version. |
| `target` | `str` | No | Configured metadata Lakehouse target. |
| `schema` | `str \| None` | No | Metadata Lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | FabricOps context normally established by ``00_env_config``. |

## Returns

dict
    Widget state, frozen contract review, controls, and an ``activate`` callable.

### Return interpretation

review is derived only from the frozen payload; activate updates lifecycle fields and reports whether a write occurred.

## Raises / Errors

ValueError
    If the selection is missing, mismatched, rejected, or has an invalid payload.
RuntimeError
    If active-contract metadata is ambiguous or Delta lifecycle updates fail.

### Common failure causes

- The selected version does not exist or belongs to another table.
- The selected contract is rejected or its frozen payload is invalid.
- The metadata table contains multiple active versions.

## Notes

<div class="reference-docstring-notes" markdown="1">

Manual activation currently permits draft, active, and superseded versions.
It atomically marks the selected version active and supersedes the previous
active version without changing any frozen payload or identity field. This
interim workflow performs no external approval and promotes no Fabric item;
a later approved promotion workflow can call the same lifecycle operation.

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

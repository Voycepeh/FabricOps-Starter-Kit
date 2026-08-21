# `widget_select_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Choose whether Development Guardrail checks use current authoring rules or one exact frozen Data Contract version.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_select_data_contract.py:75`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_select_data_contract.py#L75-L226">View on GitHub</a>
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
def widget_select_data_contract(
    table_name: str,
    target: str='source',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> selection = widget_select_data_contract("orders", target="source", schema="dbo")
>>> selection["select"]()  # current authoring Guardrails

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Physical table name within the configured target. |
| `target` | `str` | No | Logical FabricOps target containing the configured physical table. |
| `schema` | `str \| None` | No | Physical schema containing the configured table. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `dict` | No | FabricOps context normally established by ``00_env_config``. |

## Returns

dict
    Read-only selection state, available versions, frozen preview, controls,
    and a ``select`` callable. Each exact selection is stored under its
    canonical table identity in ``data_contract_overrides``; selecting
    current authoring Guardrails removes only that table's entry.

### Return interpretation

The default clears this table’s Development override; an exact selection stores its contract ID and version under the canonical table ID in the active Fabric context.

## Raises / Errors

ValueError
    If the table cannot be resolved, a version belongs to another table,
    or a rejected contract is selected.

### Common failure causes

- The configured physical table has no canonical active Catalogue table identity.
- The selected version is rejected or belongs to another table.
- The frozen contract payload is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

This is a read-only Development testing tool and never activates or changes
Data Contract metadata. Current authoring Guardrails are the default.
Production ignores manual selection and uses its active Data Contract
automatically. Frozen previews are read only from ``contract_payload_json``.

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

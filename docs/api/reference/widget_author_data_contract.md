# `widget_author_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Author one exact Data Contract version through a unified, contract-centric widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_author_data_contract.py:76`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_author_data_contract.py#L76-L351">View on GitHub</a>
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
def widget_author_data_contract(
    contract_id: str,
    contract_version: int,
    spark_session: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> form = widget_author_data_contract(
...     contract_id="orders-contract", contract_version=3, spark_session=spark
... )
>>> form["render_section"]("Review")

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `contract_id` | `str` | Yes | Exact Data Contract lifecycle identity to author. |
| `contract_version` | `int` | Yes | Exact positive draft version to author. Section changes never re-resolve it. |
| `spark_session` | `Any` | Yes | Active Microsoft Fabric Spark session used by the authoring services. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the ``FABRIC_CONTEXT`` created by ``00_env_config``. |

## Returns

Exact-version state, compact controls, the displayed UI, and validation and freeze actions.

### Return interpretation

The returned state remains pinned to the requested contract_id and contract_version; saves delegate to contract-authoring services.

## Raises / Errors

Raises validation, widget, Spark, or configured metadata routing errors.

### Common failure causes

- The exact draft version does not exist.
- The metadata target cannot be read or written.
- A subtype-specific Guardrail value is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

This is the primary contract-centric authoring UX. Passive headers, summaries,
tables, badges, and previews are aggregated HTML; ipywidgets are reserved for
interaction and only the current section/subtype editor is mounted. Governance
validation and persistence remain in the Data Contract authoring service layer.

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

# `widget_view_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 62
- Shared helpers: 35
- Private helpers: 27

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=widget_view_data_contract">Open Preview call flow</a>

Render the governed data contract for one registered dataset.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_data_contract.py:42`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_data_contract.py#L42-L172">View on GitHub</a>
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
def widget_view_data_contract(
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> state = widget_view_data_contract()
>>> views = state["get_views"]()
>>> views["current_contract"].show()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` | `str` | No | Configured FabricStore target containing FabricOps metadata tables. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | Active FabricOps context override. |

## Returns

Mutable widget state containing canonical selections, separate Spark DataFrames, and a get_views callable.

### Return interpretation

The returned state updates as selectors change; call state["get_views"] to retrieve the selected summary, contract, profiling, results, and access DataFrames.

## Raises / Errors

Raises widget, Spark, or metadata routing errors when catalogue metadata cannot be read or required selector inputs are invalid.

### Common failure causes

- No FabricStore targets are configured.
- The metadata catalogue table does not exist yet.
- The selected FabricStore target has no catalogue rows.

## Notes

<div class="reference-docstring-notes" markdown="1">

The environment is fixed to the active FabricOps context. Dataset identity
is the stable ``metadata_table_key``; schema history is selected with the
canonical ``schema_fingerprint``. Each displayed view collects at most 200
preview rows. Its CSV, JSON, and Parquet actions write the complete filtered
Spark DataFrame to a unique ``Files/fabricops_exports`` location under the
configured metadata target; export paths are reported in the widget.

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

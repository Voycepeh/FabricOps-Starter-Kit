# `widget_view_data_catalogue`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select any dataset recorded in the data catalogue, then load its catalogue and profile DataFrames for native Fabric rendering.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_data_catalogue.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_data_catalogue.py#L10-L57">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

Catalogue viewer widgets let users select governed datasets and load catalogue and profile Spark DataFrames for native Fabric notebook rendering.

They are read-only selectors and do not modify metadata.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_view_data_catalogue(
    spark_session=None,
    target: str='metadata',
    schema: str | None=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> view = widget_view_data_catalogue(spark_session=spark)
>>> views = view["get_views"]()
>>> views["catalogue"], views["profile"], views["frequency"]

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `object` | No | Spark session override. |
| `target` | `str` | No | Configured metadata FabricStore target. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `context` | `object` | No | Active FabricOps context override. |

## Returns

dict
    Common catalogue state mapping. ``get_views`` returns a named mapping
    containing the selected ``catalogue``, compact ``profile``, and
    normalized ``frequency`` Spark DataFrames without rendering.

### Return interpretation

Call state["get_views"]() to receive exactly catalogue_df and profile_df for native Fabric display.

## Raises / Errors

Not documented yet

## Notes

<div class="reference-docstring-notes" markdown="1">

Inventory is built only from the current environment's data catalogue.
The compact profile defaults to the latest ``profiled_at`` snapshot.
Frequencies are limited to the selected profile column and matched through
both ``metadata_column_key`` and ``profiled_at`` so historical snapshots
cannot be mixed.

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

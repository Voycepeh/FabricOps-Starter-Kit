# `widget_view_agreement_catalogue`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select a dataset linked to an agreement through its registered data contracts, then load its catalogue and profile DataFrames for native Fabric rendering.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_agreement_catalogue.py:13`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_agreement_catalogue.py#L13-L70">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_agreement</span>
<span class="reference-chip">03_review</span>
</p>

**Used in notebooks:** `01_agreement`, `03_review`

## Usage notes

Catalogue viewer widgets let users select governed datasets and load catalogue and profile Spark DataFrames for native Fabric notebook rendering.

They are read-only selectors and do not modify metadata.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_view_agreement_catalogue(
    agreement: dict[str, Any],
    spark_session=None,
    target: str='metadata',
    schema: str | None=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> view = widget_view_agreement_catalogue(agreement=agreement_widget, spark_session=spark)
>>> catalogue_df, profile_df = view["get_views"]()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement` | `dict[str, Any]` | Yes | Agreement widget state containing the current saved agreement. |
| `spark_session` | `object` | No | Spark session override. |
| `target` | `str` | No | Configured metadata FabricStore target. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `context` | `object` | No | Active FabricOps context override. |

## Returns

dict
    State mapping with ``get_selection``, ``get_views``, and ``refresh``.
    ``get_views`` returns exactly the selected catalogue and profile Spark
    DataFrames and does not render them.

### Return interpretation

Call state["get_views"]() to receive exactly catalogue_df and profile_df for native Fabric display.

## Raises / Errors

ValueError
    If the agreement state has no saved agreement identity.

## Notes

<div class="reference-docstring-notes" markdown="1">

Inventory follows agreement to registered data contracts to catalogue
datasets in the current environment. Spark reads for the returned views
occur only when ``get_views`` is called.

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

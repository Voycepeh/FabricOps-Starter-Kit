# `widget_metadata_explorer`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Inspect persisted metadata by table, Data Agreement, Data Steward, or Pipeline Notebook scope.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_metadata_explorer.py:64`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_metadata_explorer.py#L64-L200">View on GitHub</a>
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
def widget_metadata_explorer(
    spark_session=None,
    store: str='metadata',
    schema: str | None=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> explorer = widget_metadata_explorer(store="metadata", spark_session=spark)
>>> views = explorer["get_views"]()
>>> sorted(views)
['access', 'assets', 'columns', 'execution', 'frequency', 'governance']

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `object` | No | Spark session override. |
| `store` | `str` | No | Configured metadata FabricStore key. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `context` | `object` | No | Explicit FabricOps context. Its current environment is used for every selector and returned view. |

## Returns

dict
    Widget state with ``get_selection``, ``get_views``, and ``refresh``.
    ``get_views`` returns native Spark DataFrames named ``assets``,
    ``columns``, ``governance``, ``execution``, ``frequency``, and
    ``access``. Each preserves its documented metadata grain.

### Return interpretation

Call state["get_views"]() to receive assets, columns, governance, execution, frequency, and access Spark DataFrames.

## Raises / Errors

ValueError
    If no entity is selected or an unsupported scope is requested.

## Notes

<div class="reference-docstring-notes" markdown="1">

This read-only Microsoft Fabric widget routes all reads through the
metadata store configured by ``00_env_config``. It deliberately uses only
the current resolved environment because FabricOps does not provide a
cross-environment metadata-store routing contract.

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

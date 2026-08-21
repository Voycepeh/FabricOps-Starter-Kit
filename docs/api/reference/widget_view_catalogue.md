# `widget_view_catalogue`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select catalogue evidence through an explicit pipeline, agreement, or explore dataset scope.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_catalogue.py:589`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_catalogue.py#L589-L724">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_governance</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `01_governance`, `02_pipeline`, `99_explore`

## Usage notes

Catalogue viewer widgets let users select governed datasets and load catalogue and profile Spark DataFrames for native Fabric notebook rendering.

They are read-only selectors and do not modify metadata.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_view_catalogue(
    mode: str,
    agreement: dict[str, Any] | None=None,
    spark_session=None,
    target: str='metadata',
    schema: str | None=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> view = widget_view_catalogue(mode="explore", spark_session=spark)
>>> sorted(view["get_views"]())
['catalogue', 'frequency', 'guardrail_results', 'guardrail_row_results', 'profile']

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `mode` | `str` | Yes | Explicit dataset-scope strategy. No mode is inferred from other inputs. |
| `agreement` | `dict[str, Any] \| None` | No | Agreement widget state containing the current saved agreement. Required only for ``mode="agreement"``. |
| `spark_session` | `object` | No | Spark session override. |
| `target` | `str` | No | Configured metadata FabricStore target. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `context` | `object` | No | Explicit FabricOps context used for environment and runtime identity. |

## Returns

dict
    Common state with ``get_selection``, ``get_views``, and ``refresh``.
    ``get_views`` returns exactly ``catalogue``, ``profile``, ``frequency``,
    ``guardrail_results``, and ``guardrail_row_results`` Spark DataFrames.
    Catalogue and profile views expose readable asset/column fields first;
    frequency rows are enriched with ``column_name`` through the normalized
    ``profile_id`` relationship.

### Return interpretation

Call state["get_views"]() to receive exactly catalogue, profile, frequency, guardrail_results, and guardrail_row_results for the selected metadata_table_key.

## Raises / Errors

ValueError
    If ``mode`` is unsupported, pipeline notebook identity cannot be
    resolved, or agreement mode has no saved agreement selection.

## Notes

<div class="reference-docstring-notes" markdown="1">

Microsoft Fabric is the execution runtime. Pipeline mode derives its scope
from current-notebook lineage, agreement mode derives it from registered
contracts, and explore mode includes the current environment inventory.
The widget reads the normalized catalogue/profile/frequency tables without
changing their persisted schemas.

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

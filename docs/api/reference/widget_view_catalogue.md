# `widget_view_catalogue`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select catalogue evidence through an explicit pipeline, agreement, or explore dataset scope.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">01_governance</span>
<span class="reference-chip">99_explore</span>
</p>

## Usage notes

Use with mode pipeline for current-notebook lineage, agreement for selected-agreement contracts, or explore for direct current-environment browsing.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
view = widget_view_catalogue(mode="explore", spark_session=spark)
sorted(view["get_views"]())
```

```text
['catalogue', 'frequency', 'guardrail_results', 'profile']
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_view_catalogue(
    *,
    mode: str,
    agreement: dict[str, Any] | None=None,
    spark_session=None,
    store: str='Metadata',
    schema: str | None=None,
    context=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `mode` | `str` | Yes | `—` | Explicit dataset-scope strategy. No mode is inferred from other inputs. |
| `agreement` | `dict[str, Any] \| None` | No | `None` | Agreement widget state containing the current saved agreement. Required only for ``mode="agreement"``. |
| `spark_session` | `object` | No | `None` | Spark session override. |
| `store` | `str` | No | `'Metadata'` | Configured metadata FabricStore key. |
| `schema` | `str \| None` | No | `None` | Metadata lakehouse schema override. |
| `context` | `object` | No | `None` | Explicit FabricOps context used for environment and runtime identity. |

</div>

## Returns

dict
    Common state with ``get_selection``, ``get_views``, ``refresh``, and
    ``show``. ``show(table_id=...)`` refreshes and displays Catalogue,
    Profile, and Frequency metadata for one canonical table identity.
    ``get_views`` returns exactly ``catalogue``, ``profile``, ``frequency``,
    and ``guardrail_results`` Spark DataFrames.
    Catalogue and profile views expose readable asset/column fields first;
    frequency rows are enriched with ``column_name`` through the normalized
    ``profile_id`` relationship.

### Return interpretation

Call state["get_views"]() to receive exactly catalogue, profile, frequency, and guardrail_results for the selected table_id.

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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_catalogue.py:613`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_catalogue.py#L613-L750">View on GitHub</a>
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

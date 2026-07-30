# `widget_view_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render the canonical metadata trace for one registered dataset.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_view_data_contract.py:229`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_view_data_contract.py#L229-L512">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_review</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_review`, `99_explore`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_view_data_contract(
    agreement: dict[str, Any] | None=None,
    agreement_id: str | None=None,
    metadata_id: str | None=None,
    metadata_ids: Mapping[str, str] | Sequence[str] | None=None,
    pipeline_scope: str | None=None,
    schema_version: str | None=None,
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> pipeline_view = widget_view_data_contract(
...     pipeline_scope="current_notebook", target="metadata",
...     schema=METADATA_SCHEMA, spark_session=spark,
... )
>>> governance_view = widget_view_data_contract(
...     agreement=agreement_state, target="metadata",
...     schema=METADATA_SCHEMA, spark_session=spark,
... )
>>> direct_view = widget_view_data_contract(
...     metadata_id="logical-table-key", target="metadata",
...     schema=METADATA_SCHEMA, spark_session=spark,
... )

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement` | `dict[str, Any] \| None` | No | Agreement record or agreement-widget state. This activates strict agreement scope and may also supply a readable agreement label. |
| `agreement_id` | `str \| None` | No | Direct agreement identity. A non-empty trimmed value takes precedence over the identity in ``agreement``. |
| `metadata_id` | `str \| None` | No | Canonical ``metadata_table_key`` to select initially within the allowed scope. It never broadens that scope. |
| `metadata_ids` | `Mapping[str, str] \| Sequence[str] \| None` | No | Logical dataset identities for restricted selection, or fallback scope when current-notebook lineage is empty. Mapping keys are role labels. |
| `pipeline_scope` | `str \| None` | No | Restrict selection to lineage for the active environment and current workspace and notebook. |
| `schema_version` | `str \| None` | No | Full schema fingerprint to select initially when it exists for the selected dataset. |
| `target` | `str` | No | Configured FabricStore target containing FabricOps metadata tables. |
| `schema` | `str \| None` | No | Metadata lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | Active FabricOps context override. |

## Returns

Mutable widget state whose get_views callable returns the selection and raw, filtered canonical metadata DataFrames.

### Return interpretation

The returned state updates as selectors change; call state["get_views"] to retrieve selection details and raw metadata-history DataFrames ordered newest commit first.

## Raises / Errors

Raises Spark or metadata routing errors when metadata cannot be read. A missing optional widget dependency returns a non-breaking error state.

### Common failure causes

- No FabricStore targets are configured.
- The metadata catalogue table does not exist yet.
- The selected FabricStore target has no catalogue rows.

## Notes

<div class="reference-docstring-notes" markdown="1">

The single dataset selector has ``agreement``, ``pipeline``, ``restricted``,
``direct``, and ``discovery`` modes. Agreement scope follows only
``agreement_id -> METADATA_DATA_CONTRACT -> metadata_table_key`` and then
intersects those links with catalogue evidence in the active environment;
unrelated or cross-environment datasets are never offered. Agreement and
other restricted scopes are mutually exclusive. Empty agreement links and
links absent from the active environment return explicit non-breaking empty
states rather than discovery.

Schema versions are newest first and have readable, locale-independent
timestamps while retaining the full fingerprint as their value. Under the
current schema contract, that fingerprint represents ordered column names
and data types. Changing the version refreshes every returned review view
that carries ``schema_fingerprint``; version-agnostic views remain scoped
to the selected dataset. Large Spark DataFrames are returned by
``get_views`` rather than rendered inside the widget.

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

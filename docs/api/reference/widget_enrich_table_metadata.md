# `widget_enrich_table_metadata`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Browse catalogue history and maintain metadata enrichment.

<div class="reference-docstring-intro" markdown="1">

Select a logical table, browse its latest and historical columns, and
maintain table- or column-level enrichment. Current columns are editable;
columns absent from the latest schema fingerprint are shown as removed and
remain read-only for historical reference.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_enrich_table_metadata.py:26`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_enrich_table_metadata.py#L26-L296">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">03_review</span>
</p>

**Used in notebooks:** `03_review`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_enrich_table_metadata(
    spark_session: Any,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> browser = widget_enrich_table_metadata(spark_session=spark)
>>> browser["selected_table_state"]["latest_schema_fingerprint"]

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `Any` | Yes | Fabric Spark session used to read the canonical catalogue and append enrichment records through the configured metadata target. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context initialized by ``00_env_config``. |

## Returns

Standalone three-pane browser state with table and column selectors, draft-aware detail controls, record building, and a save callback.

### Return interpretation

Only non-empty changed values are appended to METADATA_ENRICHMENT; repeated unchanged saves produce no write.

## Raises / Errors

Raises clear catalogue identity, metadata read, or metadata routing errors when canonical catalogue evidence is unavailable.

### Common failure causes

- The metadata catalogue has no logical tables.
- A table or current column lacks its canonical metadata key.
- Metadata lakehouse reads or writes cannot be routed through 00_env_config.

## Notes

<div class="reference-docstring-notes" markdown="1">

Table enrichment supports ``Description`` and ``Classification``. Column
enrichment additionally supports ``Personal_identifier``. Existing values,
including values removed from current dropdown configuration, are preserved.
Saving appends only non-empty changed values to ``METADATA_ENRICHMENT``;
repeated unchanged saves produce no write. This workflow is independent of
guardrail target selection and keeps unsaved drafts in memory while open.

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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |


</details>

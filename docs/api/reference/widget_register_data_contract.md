# `widget_register_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Register dataset-level Data Contract tables under a parent Data Agreement.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_register_data_contract.py:292`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_register_data_contract.py#L292-L995">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_agreement</span>
</p>

**Used in notebooks:** `01_agreement`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_register_data_contract(
    agreement: dict[str, Any] | None=None,
    agreement_id: str | None=None,
    metadata_ids: Sequence[str] | None=None,
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> contract_state = widget_register_data_contract(
...     agreement=agreement_state,
...     target="metadata",
...     schema=METADATA_SCHEMA,
...     spark_session=spark,
... )
>>> contract_state = widget_register_data_contract(
...     agreement_id="agreement-123",
...     metadata_ids=["table-key-1", "table-key-2"],
...     target="metadata",
...     schema=METADATA_SCHEMA,
...     spark_session=spark,
... )

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement` | `dict[str, Any] \| None` | No | Agreement record or agreement-widget state used to resolve the canonical agreement ID and a readable label locally. When the supplied state exposes ``existing_record``, changing that selector reloads the latest inventory without rerunning the cell. The editor remains disabled while no saved agreement is selected. |
| `agreement_id` | `str \| None` | No | Explicit canonical agreement identity. A non-empty trimmed value takes precedence over ``agreement``. |
| `metadata_ids` | `Sequence[str] \| None` | No | Additional unsaved initial inventory identities. Valid active- environment identities extend the latest snapshot only in memory; unknown identities are reported and never written. |
| `target` | `str` | No | Configured FabricStore target containing FabricOps metadata tables. |
| `schema` | `str \| None` | No | Metadata Lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | Active FabricOps context override, normally created by ``00_env_config``. |

## Returns

Mutable inventory state with audit activity details, unsaved edits, structured per-dataset schema reviews, and snapshot getter callables.

### Return interpretation

dataset_reviews exposes complete schemas, removed-column history, stable-key differences, and read-only enrichment; each changed save records one exact schema version per logical dataset without changing enrichment.

## Raises / Errors

Raises when an agreement ID cannot be resolved or configured metadata cannot be read or safely written.

### Common failure causes

- No saved agreement is selected, so the inventory editor remains disabled.
- The active environment has no registered catalogue datasets.
- The metadata target cannot be written.

## Notes

<div class="reference-docstring-notes" markdown="1">

Select an agreement, manage its allocated tables, and review each table's
latest schema and enrichment context. This widget selects catalogue datasets covered by an agreement and freezes
each current schema fingerprint in an immutable inventory snapshot. It
resolves the actual contracted schema from historical catalogue rows,
compares it with the current active-environment catalogue schema, and
displays additive and breaking structural differences. Catalogue datasets
appear once by logical ``metadata_table_key``; selecting one previews the
exact latest active-environment schema and fingerprint before it is added.
Each explicit save
records the currently displayed schema version in the data contract, builds the FabricOps audit fields
once and appends the complete current membership list. ``_activity_id``
groups the save and ``_committed_at`` orders saves, while the widget displays
only the latest inventory. Historical rows are never updated or deleted.
Within each activity, ``agreement_id + metadata_table_key`` is unique and
identifies exactly one recorded ``schema_fingerprint``.
Catalogue discovery is restricted to the active environment, but logical
``metadata_table_key`` membership remains environment-independent.
An unsaved agreement draft cannot create an inventory snapshot; select an
existing agreement or save the new agreement first.

Current and historically removed columns are shown in the detail panel;
removed columns include their last-observed timestamp. Latest table- and
column-level enrichment is resolved by canonical metadata keys and is
strictly read-only. Maintain enrichment with
``widget_enrich_table_metadata``. Saving writes only contract membership
and schema fingerprint metadata; it never writes enrichment records.
Schema comparison is informational, and guardrails and guardrail results remain separate workflows.
Granularity, semantic calculation changes, data quality, freshness,
sensitivity, and PII are not enforced by this widget. This widget does not
claim Open Data Contract Standard completeness.

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

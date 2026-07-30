# `widget_register_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Register authoritative agreement-to-logical-dataset membership.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_register_data_contract.py:152`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_register_data_contract.py#L152-L400">View on GitHub</a>
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
| `agreement` | `dict[str, Any] \| None` | No | Data Agreement record or agreement-widget state. Its selected ``agreement_id`` is used when no non-empty explicit ID is supplied; readable agreement information is reused for display without querying ``METADATA_DATA_AGREEMENT``. |
| `agreement_id` | `str \| None` | No | Explicit canonical agreement identity. Surrounding whitespace is removed and a non-empty value takes precedence over ``agreement``. |
| `metadata_ids` | `Sequence[str] \| None` | No | Initial selector values only. Values are trimmed and de-duplicated; unknown or inactive-environment identities are reported but cannot be selected or written. |
| `target` | `str` | No | Configured FabricStore target containing FabricOps metadata tables. |
| `schema` | `str \| None` | No | Metadata Lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | Active FabricOps context override, normally created by ``00_env_config``. |

## Returns

Mutable widget state with selection and save results plus a get_rows callable for the selected agreement.

### Return interpretation

Saved identities are the authoritative draft membership selected for the agreement; unknown initial identities remain non-writable.

## Raises / Errors

Raises when an agreement ID cannot be resolved or configured metadata cannot be read or safely written.

### Common failure causes

- No agreement ID is selected.
- The active environment has no registered catalogue datasets.
- The metadata target cannot be written.

## Notes

<div class="reference-docstring-notes" markdown="1">

Catalogue discovery is restricted to the active environment, while the
saved relationship is environment-independent: one agreement links once to
each logical ``metadata_table_key``. Saving writes minimal version ``1``
draft rows with the latest active-environment schema fingerprint and normal
runtime audit fields. The selection is authoritative for this agreement:
new memberships are inserted, selected draft memberships are preserved,
and deselected draft memberships are removed. Rows for other agreements and
non-draft rows are preserved. Review, approval, promotion, environment
comparison, and pipeline inspection are outside this draft-only writer.

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

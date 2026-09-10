# `read_pipeline_prep`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Resolve governed source identity and register source Lineage before reading business data.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/read_pipeline_prep.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/read_pipeline_prep.py#L15-L91">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_pipeline_prep(
    source_table_id: str | None=None,
    source_target: str | None=None,
    source_schema: str | None=None,
    source_table: str | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> prep = read_pipeline_prep(
...     source_target="source",
...     source_schema="dbo",
...     source_table="bookings",
... )
>>> prep["table_id"]
'warehouse:source:dbo:bookings'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source_table_id` | `str \| None` | No | Canonical identity of one registered source table. Omit it and supply ``source_target``, ``source_schema``, and ``source_table`` to resolve the same identity deterministically from configured physical identity. |
| `source_target` | `str \| None` | No | Configured source target key. Mutually exclusive with ``source_table_id``. |
| `source_schema` | `str \| None` | No | Physical source schema, when the configured store uses schemas. |
| `source_table` | `str \| None` | No | Physical source table name. Required with ``source_target`` when ``source_table_id`` is omitted. |

## Returns

Canonical source table_id and resolved physical source identity.

## Raises / Errors

ValueError
    If the source identity is incomplete, conflicting, or is not registered.

## Notes

<div class="reference-docstring-notes" markdown="1">

This preparation boundary identifies the source and registers its Lineage;
it does not read business rows or make incremental-processing decisions.
Use the resolved ``table_id`` with :func:`read_lakehouse_table`, or use the
resolved source coordinates when reading a Warehouse query.

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

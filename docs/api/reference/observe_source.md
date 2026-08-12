# `observe_source`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Observe source partitions cheaply and plan a restricted source read.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/observe_source.py:175`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/observe_source.py#L175-L290">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def observe_source(
    source: dict[str, Any],
    partition_columns: list[str],
    range_column: str,
    fingerprint_columns: list[str],
    config: Any,
    env: str,
    spark_session: Any | None=None,
    context: dict[str, Any] | None=None,
    persist: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> plan = observe_source(
...     {"source_type": "warehouse", "target": "warehouse", "schema": "dbo", "table_name": "orders"},
...     partition_columns=["business_date"], range_column="order_id",
...     fingerprint_columns=["order_id", "modified_at"], config=CONFIG, env=ENV,
... )
>>> plan["requires_read"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source` | `dict[str, Any]` | Yes | Explicit source configuration with ``source_type`` (``warehouse`` or ``lakehouse``), logical ``target``, ``table_name``, and optional ``schema`` and ``partition_predicate`` values. |
| `partition_columns` | `list[str]` | Yes | Columns defining independently readable source partitions. |
| `range_column` | `str` | Yes | Column used for compact minimum and maximum evidence. |
| `fingerprint_columns` | `list[str]` | Yes | Narrow columns used by the distributed aggregate checksum. |
| `config` | `Any` | Yes | FabricOps configuration containing the source and metadata targets. |
| `env` | `str` | Yes | Selected FabricOps environment. |
| `spark_session` | `Any \| None` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Fabric context override. ``config`` and ``env`` are supplied by this function to ensure configured target routing. |
| `persist` | `bool` | No | Append the compact observation to FabricOps-owned metadata after a successful comparison. |

## Returns

Compact observations plus changed and new partitions and a restricted read predicate.

## Raises / Errors

ValueError
    If source type, identity, or observation columns are invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Warehouse grouping and checksums execute in the SQL serving engine, so
Spark receives only aggregate rows. ``CHECKSUM_AGG`` is a cheap change
signal rather than collision-proof row evidence; use :func:`check_changes`
on the restricted source slice when deeper comparison is required.
Lakehouse aggregation remains distributed and projects only observation
columns. The source is always read-only; history is appended to
``METADATA_SOURCE_OBSERVATION`` in the configured metadata Lakehouse.

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

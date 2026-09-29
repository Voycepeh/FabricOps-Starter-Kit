# `orchestrate_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Run the observable standard governed source lifecycle.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/orchestrate_read.py:12`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/orchestrate_read.py#L12-L77">View on GitHub</a>
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
def orchestrate_read(
    name: str,
    store: str,
    schema: str | None,
    table_name: str,
    read_mode: str='full',
    query: str | None=None,
    target_table_id: str | None=None,
    spark_session=None,
    verbose: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> source = orchestrate_read(name="orders", store="Bronze", schema="demo", table_name="orders")
>>> orders_df = source["dataframe"]

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Notebook-facing name used in orchestration output. |
| `store` | `str` | Yes | Configured source store key. |
| `schema` | `str \| None` | Yes | Physical source schema. |
| `table_name` | `str` | Yes | Physical source table name. |
| `read_mode` | `str` | No | Source read behaviour forwarded to :func:`pipeline_read`. |
| `query` | `str \| None` | No | Read-only Warehouse query forwarded to :func:`pipeline_read`. |
| `target_table_id` | `str \| None` | No | Governed target identity required for incremental reads. |
| `spark_session` | `object` | No | Spark session used by every stage. |
| `verbose` | `bool` | No | Print stage start, outcome, duration, and failure attribution. |

## Returns

Governed source DataFrame and table identity together with every stage result.

## Raises / Errors

RuntimeError
    If a stage fails. Its name is reported and the original exception is
    retained as ``__cause__``.

## Notes

<div class="reference-docstring-notes" markdown="1">

Stages run as Read, Freshness, Schema, Data Quality, and Profile, matching
canonical ``02_pipeline``. Skipped capability results remain skipped.
DataFrames are never displayed. Incremental batches are not profiled.

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

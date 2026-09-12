# `pipeline_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Read one governed pipeline source through its configured Fabric store.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_read.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_read.py#L17-L134">View on GitHub</a>
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
def pipeline_read(
    target: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    query: str | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = pipeline_read(target="source", schema="sales", table_name="orders")
>>> orders_df = result["dataframe"]
>>> result["table_id"]
'lakehouse:source:sales:orders'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` | `str \| None` | No | Configured source target key. Supply it with ``table_name`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical source schema, when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical source table name. Required with ``target`` when ``table_id`` is omitted. |
| `table_id` | `str \| None` | No | Canonical registered source identity. Mutually exclusive with ``target``, ``schema``, and ``table_name``. |
| `query` | `str \| None` | No | Read-only SQL for a configured Warehouse source. The supplied source identity remains the governed Lineage participant; FabricOps does not infer table identity by parsing SQL. |

## Returns

DataFrame, canonical source table_id, custom-query signal, and whether an environment-selected Data Contract applies.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, the source is not
    registered, its configured store kind is unsupported, or a query is
    supplied for a Lakehouse source.

## Notes

<div class="reference-docstring-notes" markdown="1">

This orchestration resolves canonical and physical source identity,
registers source participation in ``METADATA_DATA_LINEAGE`` exactly once,
establishes source profile-registration context, and delegates the
physical read to the foundational Fabric I/O API. It does not run source
observation, freshness, stability, schema, DQ, or profiling checks.

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

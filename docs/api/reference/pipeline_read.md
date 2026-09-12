# `pipeline_read`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Read one governed pipeline source through its configured Fabric store.

<div class="reference-docstring-intro" markdown="1">

``pipeline_read`` is the governed pipeline-orchestration equivalent of the
foundational :func:`read_lakehouse_table`, :func:`read_warehouse_table`,
and :func:`read_warehouse_query` readers. Describe the governed source
once; FabricOps resolves its identity and configured store, selects the
physical reader, and returns the data needed by the notebook. Callers do
not supply a store type, resolve a canonical table identity first, or
choose between Lakehouse and Warehouse table readers.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/pipeline_read.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/pipeline_read.py#L17-L196">View on GitHub</a>
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

Read a governed table without knowing whether ``source`` resolves to a
Lakehouse or Warehouse:

>>> result = pipeline_read(
...     target="source",
...     schema="demo",
...     table_name="orders",
... )
>>> orders_df = result["dataframe"]
>>> orders_table_id = result["table_id"]

Read a governed Warehouse source through project-owned SQL:

>>> result = pipeline_read(
...     target="product",
...     schema="demo",
...     table_name="order_history",
...     query='''
...         SELECT customer_id, COUNT(*) AS order_count
...         FROM demo.order_history
...         GROUP BY customer_id
...     ''',
... )
>>> history_df = result["dataframe"]
>>> result["is_query"]
True

The query result is marked as derived so later notebook logic can use
``profile_dataframe`` without registering it as the complete physical
``demo.order_history`` source table.

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `target` | `str \| None` | No | Configured source target key, such as ``"source"`` or ``"product"``. Supply it with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical source schema, when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical source table name. Required with ``target`` when ``table_id`` is omitted. ``target``, optional ``schema``, and ``table_name`` form one identity form. |
| `table_id` | `str \| None` | No | Canonical registered source identity. This is the alternative identity form and is mutually exclusive with ``target``, ``schema``, and ``table_name``. |
| `query` | `str \| None` | No | Read-only SQL for a configured Warehouse source. The supplied source identity remains the governed source participant even when the result is a projection, filter, join, or aggregation. FabricOps does not infer arbitrary source identity by parsing SQL. A query may accompany either physical coordinates or ``table_id`` when the resolved store is a Warehouse. |

## Returns

DataFrame, canonical source table_id, custom-query signal, and whether an environment-selected Data Contract applies.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, the source is not
    registered, its configured store kind is unsupported, or a query is
    supplied for a Lakehouse source.

## Notes

<div class="reference-docstring-notes" markdown="1">

The governed orchestration performs these mechanical steps:

1. Resolve the canonical source ``table_id``.
2. Resolve the configured physical source identity.
3. Infer whether that configured source is a Lakehouse or Warehouse.
4. Select and call ``read_lakehouse_table``, ``read_warehouse_table``, or
   ``read_warehouse_query`` as the foundational physical Fabric I/O boundary.
5. Register source participation in ``METADATA_DATA_LINEAGE`` exactly once.
6. Establish the source profile-registration context consumed by a later,
   explicit ``profile_and_register_table`` call.
7. Return the DataFrame and small source metadata required by the notebook.

Higher-level governed pipeline code normally uses ``pipeline_read``.
Foundational readers remain available for direct lower-level or
general-purpose Fabric reads that do not need pipeline orchestration.
``pipeline_read`` orchestrates governed table sources only. Raw Lakehouse
Files do not have a canonical ``table_id`` and should continue to use the
foundational CSV, Excel, JSON, or Parquet readers directly.

This function does not execute source observation, Freshness, Source
Stability, Schema, DQ, or Sensitive Data checks. It also does not profile
data, transform rows, or write a pipeline target. Those meaningful
engineering decisions remain explicit in ``02_pipeline``.

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

# read_warehouse_query


Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Source

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_query.py#L10-L46">View source on GitHub</a>

Implemented in `src/fabricops_kit/io/read_warehouse_query.py`:10.

## Usage guidance

### Use when

- Use when warehouse data should be filtered or projected before Spark processing.

### Do not use when

- Do not use for lakehouse Delta tables, lakehouse Files paths, or non-SELECT warehouse mutations.

### Additional context

Encourages warehouse SQL pushdown for filtered or projected reads instead of full table extracts.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_query(
    query: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_query("SELECT order_id, status FROM dbo.orders WHERE status = 'OPEN'", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | Yes | SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``, to execute through the Fabric warehouse connector. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

Spark DataFrame returned by the Fabric warehouse connector.

### Return interpretation

The returned DataFrame contains the query result from the warehouse SQL serving engine.

## Raises / Errors

Raises ValueError for blank or non-SELECT SQL and RuntimeError when the Fabric connector is unavailable.

### Common failure causes

- The SQL is blank or not a SELECT/CTE.
- The warehouse target is not configured.
- The Fabric connector is unavailable.
- The caller lacks warehouse read permission.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)

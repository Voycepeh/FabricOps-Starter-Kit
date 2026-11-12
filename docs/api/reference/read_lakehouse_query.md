# `read_lakehouse_query`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Run read-only Spark SQL against one configured Lakehouse table.


## Usage notes

Use when selecting or filtering one configured Lakehouse table with Spark SQL.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_query("SELECT TOP (5) order_id FROM demo.orders", table_name="orders", schema="demo", store="Bronze")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_query(
    query: str,
    *,
    table_name: str,
    store: str='Bronze',
    schema: str | None=None,
    context: dict[str, Any] | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | `str` | Yes | `—` | One read-only Spark SQL SELECT or CTE referencing the declared source. Simple integer T-SQL TOP projections are also supported. |
| `table_name` | `str` | Yes | `—` | Required Lakehouse table name referenced by the query. Supply its schema separately with ``schema``. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key configured in ``00_env_config``. |
| `schema` | `str \| None` | No | `None` | Schema for the declared source in a schema-enabled Lakehouse. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override containing an existing Spark session and configured Lakehouse routing. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_query(
    "SELECT TOP (5) order_id FROM demo.orders",
    table_name="orders", schema="demo", store="Bronze",
)
```

</div>

## Returns

pyspark.sql.DataFrame
    Lazy query result bound to the configured physical source. A downstream
    Spark action evaluates the data.

### Return interpretation

The DataFrame represents the bound query; downstream Spark actions evaluate its data.

## Raises / Errors

ValueError
    If the declared source is invalid, SQL is not read-only, another source
    is referenced, or unsupported T-SQL cannot be converted safely.
RuntimeError
    If no active Spark session or configured Lakehouse target is available.

### Common failure causes

- The query references a different physical source.
- T-SQL uses unsupported constructs.
- The Lakehouse target is not configured or readable.
- No active Spark session is available.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

The query must reference the declared table (or schema.table). CTEs,
filters, projections, aggregations and self-joins use Spark SQL.
Simple T-SQL integer TOP projections are translated to LIMIT; unsupported
T-SQL fails rather than silently changing semantics.

The source is bound through the configured physical Lakehouse location,
including cross-workspace stores, not the Spark session's default catalog.
No pipeline setup, metadata mutation, or contract enforcement is performed.

Returns a Spark DataFrame. No Spark session is created.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_query.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_query.py#L10-L89">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
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

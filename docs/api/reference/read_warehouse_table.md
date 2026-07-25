# `read_warehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 8
- Private helpers: 7

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_warehouse_table">Open Live contract call flow</a>

Read a table from a configured Fabric warehouse target.

<div class="reference-docstring-intro" markdown="1">

This is equivalent to ``SELECT * FROM schema.table_name``. The function
returns every column and every row exposed by the resolved Warehouse table.
It does not automatically apply a ``WHERE`` filter, select a subset of
columns, apply a row limit, aggregate the data, or sample the data. The
configured Warehouse target is resolved from ``00_env_config``, and the
read uses the Microsoft Fabric Warehouse Spark connector rather than native
Delta access.

Use this callable only for intentional full-table extracts such as small
lookup tables, reference tables, smoke tests, or cases where every row and
column is genuinely required. Prefer ``read_warehouse_query`` when
projection, filtering, aggregation, joins, row limits, or other SQL
pushdown should occur before data reaches Spark.

``read_warehouse_table`` transfers the complete table result to Spark. For
large or wide Warehouse tables, use ``read_warehouse_query`` so filtering
and column projection occur in the Warehouse SQL engine before rows are
transferred to the notebook. As a rule of thumb, small Warehouse reads are
usually acceptable for reference or ad hoc work, such as narrow tables or
datasets under roughly 1 million rows or 1 GB. For 1 million to 10 million
rows, wide tables, or multi-GB data, benchmark first and prefer Lakehouse
Delta if the data will be reused. For tens of millions of rows, hundreds
of columns, large text columns, or tables over roughly 10 GB, copy or
incrementally load the Warehouse data into Lakehouse Delta before Spark
processing. Avoid a single notebook cell that pulls a very large Warehouse
table because notebook cells can hit runtime limits.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_table.py#L10-L87">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage notes

A complete-table read may transfer a large dataset from the Warehouse into Spark. Use read_warehouse_query when the workload can be reduced through SQL projection, filtering, joins, or aggregation.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_table(
    schema: str,
    table_name: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
student_df = read_warehouse_table("dbo", "student_enrolment", target="warehouse", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `schema` | `str` | Yes | Physical Warehouse schema name for the source table. |
| `table_name` | `str` | Yes | Physical Warehouse table name for the source table. |
| `target` | `str` | No | Logical Warehouse configuration name from ``00_env_config``. This identifies the configured Warehouse target, while ``schema`` and ``table_name`` identify the physical Warehouse table. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Fabric Warehouse Spark connector reader options. Required Fabric connector options are always set from ``00_env_config``. |

## Returns

Spark DataFrame containing the rows and columns of the resolved Warehouse table.

### Return interpretation

The returned DataFrame represents the warehouse read result; confirm filters and row counts before profiling or transformation.

## Raises / Errors

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

### Common failure causes

- The Warehouse connection cannot be resolved.
- The schema or table is not found, the caller lacks permission, or identifiers are invalid.
- The table contains unsupported data types for transfer to Spark.
- Complete-table reads may transfer large datasets; an empty table returns a valid zero-row DataFrame.

## Notes

<div class="reference-docstring-notes" markdown="1">

FabricOps resolves the configured Warehouse target and table name, then
delegates to the Fabric Warehouse Spark connector. Conceptual example:

``df = read_warehouse_table(schema="dbo", table_name="DimDepartment")``

Use ``read_warehouse_query`` instead when you need selected columns, row
filtering, aggregation, joins, row limits, or other caller-controlled SQL
pushdown before Spark receives rows.

</div>

## See also

- [Templates](../../notebook-templates-implementation-guide/index.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 15 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._require_fabric_connector</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
</ul>


</details>

# `read_warehouse_query`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 12
- Shared helpers: 8
- Private helpers: 4

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_warehouse_query">Open Live contract call flow</a>

Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.

<div class="reference-docstring-intro" markdown="1">

Use this instead of ``read_warehouse_table`` when filtering, projection,
aggregation, joins, or row limits should be performed before data reaches
Spark. The supplied SQL is pushed down to the Warehouse SQL serving engine,
and Spark receives only the query result. Column projection and row
filtering should be written directly in the SQL. The function accepts a
``SELECT`` statement or a CTE beginning with ``WITH`` and ending in a
``SELECT``, validates that the query is read-only, and does not
automatically add filters, projections, or limits beyond what the caller
includes in the SQL. Reads use the Fabric Warehouse Spark connector rather
than native Delta access.

``read_warehouse_table`` is equivalent to a full-table ``SELECT *`` read.
``read_warehouse_query`` provides caller-controlled SQL pushdown. For large
or repeated PySpark processing, materialize the filtered result into the
Source Lakehouse as Delta and continue from ``read_lakehouse_table``.

Rule-of-thumb sizing guidance: small filtered or narrow slices under
roughly 1 million rows or 1 GB are usually acceptable for ad hoc work;
1 million to 10 million rows or 1 to 10 GB should be benchmarked first;
and tables over roughly 10 million rows, over 10 GB, with hundreds of
columns, or with large text fields should be loaded incrementally into
Lakehouse Delta before Spark transformations.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_query.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_query.py#L15-L91">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_query(
    query: str,
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
df = read_warehouse_query("SELECT order_id, status FROM dbo.orders WHERE status = 'OPEN'", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | Yes | Read-only SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``, to execute through the Fabric Warehouse SQL serving engine. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Fabric Warehouse Spark connector reader options. Required Fabric connector options are always set from ``00_env_config``. |

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

## Notes

<div class="reference-docstring-notes" markdown="1">

FabricOps resolves the configured Warehouse target, sets the Fabric
connector database to that warehouse artifact, and delegates the read-only
SQL text to the Fabric Warehouse Spark connector for pushdown. Query callers
can use two-part names such as ``dbo.orders`` when the configured target
identifies the warehouse database/artifact. Conceptual example:

``df = read_warehouse_query("""SELECT DepartmentId, DepartmentName FROM dbo.DimDepartment WHERE IsActive = 1""")``

That query returns only the selected columns, filters rows in the
Warehouse engine, and transfers only the resulting dataset to Spark.

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
| Live-critical dependencies | 12 |

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
<li><code>fabricops_kit.io.shared._require_fabric_connector</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_query_target</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.validate_select_query</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 2:26 PM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT

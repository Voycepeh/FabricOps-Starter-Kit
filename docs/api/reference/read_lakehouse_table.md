# `read_lakehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read a Delta table from a configured Fabric lakehouse target.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use when reading managed Delta tables from configured Lakehouse Tables storage.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_table("orders", store="Bronze", schema="demo")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(
    table_name: str | None=None,
    *,
    table_id: str | None=None,
    store: str='Bronze',
    schema: str | None=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_name` | `str \| None` | No | `None` | Required unless table_id is supplied. Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. Omit it when ``table_id`` is supplied. |
| `table_id` | `str \| None` | No | `None` | Canonical registered table identity. When supplied, FabricOps resolves ``table_name``, ``store``, and ``schema`` from the Catalogue. Do not combine with table_name, schema, or a non-default store. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key from ``00_env_config``, such as ``bronze`` or ``silver``. FabricOps resolves this store key to the configured physical Lakehouse and Delta table path. |
| `schema` | `str \| None` | No | `None` | Optional schema override for schema-enabled Lakehouses. Supply it separately from ``table_name``: use ``schema="sales"`` and ``table_name="orders"`` rather than ``table_name="sales.orders"``. This is normally omitted for Lakehouses without schemas. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override. |
| `**options` | `—` | No | `—` | Additional Spark Delta ``DataFrameReader`` options forwarded to the Delta reader. These options do not provide FabricOps-level filtering or projection. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_table("orders", store="Bronze", schema="demo")
recent = orders_df.where("order_date >= '2026-01-01'")
```

</div>

## Returns

pyspark.sql.DataFrame
    A lazy Spark DataFrame representing the governed rows and all columns
    in the resolved Lakehouse Delta table. The data is evaluated when a
    downstream Spark action runs.

### Return interpretation

The returned DataFrame represents the resolved Lakehouse table.

## Raises / Errors

Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.

### Common failure causes

- The target cannot be resolved or is not a lakehouse.
- The table is not found, exists under another lakehouse or schema, or the schema argument is incorrect.
- The caller lacks read permissions or no Spark session is available.
- Spark Delta read failures may be deferred until an action evaluates the DataFrame.

## Notes

<div class="reference-docstring-notes" markdown="1">

Use either table_name with store and optional schema, or table_id to resolve
the registered physical location from METADATA_DATA_CATALOGUE. Reader options
are forwarded to Spark Delta. The call does not register or profile data.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

Use for managed Delta tables. Apply selection and filtering with normal
Spark transformations; Delta can push these into the eventual scan.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_table.py#L10-L104">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 22 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_delta_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
</ul>


</details>

# `profile_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile a Spark DataFrame or complete governed table with one PySpark API.

<div class="reference-docstring-intro" markdown="1">

FabricOps calculates the canonical statistical profile and applicable
frequency distribution with PySpark. An identity may be supplied as a
canonical ``table_id`` or as ``target``, optional ``schema``, and
``table_name``. When an identity is present, FabricOps associates the
result with that governed table and persists Catalogue, profile, and
frequency metadata. Without an identity, the exact supplied DataFrame is
profiled without creating an identity or writing metadata.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_table.py:479`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_table.py#L479-L698">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_table(
    dataframe=None,
    target: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    frequency_columns=None,
    frequency_top_n: int | None=None,
    frequency_max_distinct_percent: float | None=80.0,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

Profile an arbitrary DataFrame without persistence:

>>> result = profile_table(dataframe=raw_df)
>>> statistical_profile = result["profile"]
>>> frequencies = result["frequency_profile"]

Profile a governed complete physical table without knowing its store kind:

>>> result = profile_table(target="source", schema="dbo", table_name="orders")

Profile a transformed DataFrame against an explicit governed identity:

>>> result = profile_table(dataframe=transformed_df, table_id=target_table_id)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | No | Exact Spark DataFrame to profile. If a governed identity is also supplied, FabricOps does not re-read the physical table. |
| `target` | `str \| None` | No | Configured physical target key. Supply with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | Physical schema when the configured store uses schemas. |
| `table_name` | `str \| None` | No | Physical table name. Required with ``target`` when ``table_id`` is omitted. |
| `table_id` | `str \| None` | No | Canonical governed table identity, mutually exclusive with physical coordinates. |
| `frequency_columns` | `sequence of str` | No | Columns to frequency profile. ``None`` automatically selects eligible scalar columns; an empty sequence skips frequency profiling. |
| `frequency_top_n` | `int \| None` | No | Ranked values to retain per frequency column. ``None`` retains all. |
| `frequency_max_distinct_percent` | `float \| None` | No | Maximum distinct-per-non-null percentage for automatically selected columns. ``None`` disables the cardinality filter. |

## Returns

Spark DataFrame containing one compact profiling summary row for each eligible column appended to METADATA_DATA_PROFILED, including profile_id, profile_snapshot_id, stable table_id and column_id identities, environment_name, complete-DataFrame statistics, profiling timestamp, and runtime audit fields.

### Return interpretation

The returned rows are the compact parent summaries. Flattened frequency rows are written separately to METADATA_DATA_PROFILED_FREQUENCY, link to their parent through profile_id, and share the same profile_snapshot_id; frequency and catalogue rows are side effects and are not returned.

## Raises / Errors

Raises ValueError for missing or conflicting identity inputs and invalid frequency settings.

### Common failure causes

- profile_role must be source or target, or the configured target store kind is unsupported.
- target or table_name is blank, or a schema-enabled store has no explicit or configured schema.
- frequency_profile_df is not Spark DataFrame-like, uses an incompatible Spark session, or is missing selected frequency columns.
- The configured metadata target cannot be resolved or written.
- Requested frequency columns are missing or expensive to group; frequency_top_n limits returned values only and does not reduce grouping cost.

## Notes

<div class="reference-docstring-notes" markdown="1">

The orchestration performs these mechanical steps:

1. Validate and resolve the optional canonical governed identity.
2. Use the supplied DataFrame exactly, or read the complete physical table
   through the resolved Lakehouse or Warehouse reader.
3. Calculate canonical statistical metrics with PySpark.
4. Select eligible frequency columns and calculate exact grouped counts,
   including null as a frequency value.
5. When governed, create stable table and column identities, append
   ``METADATA_DATA_PROFILED``, replace the current snapshot rows in
   ``METADATA_DATA_PROFILED_FREQUENCY``, and update
   ``METADATA_DATA_CATALOGUE``.
6. Return both profiling outputs. DataFrame-only mode performs no metadata
   writes and never invents a ``table_id``.

</div>

## See also

- [Pipeline Execution](../../guided-demo/02-run-pipeline.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 59 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.audit._context_get</code></li>
<li><code>fabricops_kit.config.audit._require_audit_values</code></li>
<li><code>fabricops_kit.config.audit._valid_audit_value</code></li>
<li><code>fabricops_kit.config.audit.build_runtime_audit_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas._coerce_metadata_value</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.coerce_metadata_row_types</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.build_column_id</code></li>
<li><code>fabricops_kit.config.shared.build_table_id</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.config.shared.stable_metadata_id</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.normalize_write_mode</code></li>
<li><code>fabricops_kit.io.shared.read_delta_path</code></li>
<li><code>fabricops_kit.io.shared.read_lakehouse_table_core</code></li>
<li><code>fabricops_kit.io.shared.repartition_dataframe_for_write</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_delta_path</code></li>
<li><code>fabricops_kit.io.shared.write_lakehouse_table_core</code></li>
<li><code>fabricops_kit.pipeline.profile_table._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._automatic_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.profile_table._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_table._scalar_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._selected_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_catalogue_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_physical_table_identity</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
</ul>


</details>

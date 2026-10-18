# `profile_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile a Spark DataFrame or complete governed table and return statistical and frequency results.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">99_explore</span>
</p>

## Usage notes

Use for non-persistent DataFrame profiling or governed table profiling and metadata persistence.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = profile_table(dataframe=orders_df)
statistical_profile = result["profile"]
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_table(
    *,
    dataframe=None,
    store: str | None=None,
    schema: str | None=None,
    table_name: str | None=None,
    table_id: str | None=None,
    frequency_columns=None,
    frequency_enabled: bool=True,
    frequency_top_n: int | None=5,
    frequency_max_distinct_percent: float | None=80.0,
    spark_session=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | No | `None` | Required unless a complete governed identity is provided. With no DataFrame and no identity, the call raises ValueError. If an identity is also supplied, FabricOps does not re-read the physical table. |
| `store` | `str \| None` | No | `None` | Configured physical store key. Supply with ``table_name`` and optional ``schema`` instead of ``table_id``. |
| `schema` | `str \| None` | No | `None` | Physical schema when the configured store uses schemas. |
| `table_name` | `str \| None` | No | `None` | Physical table name. Required with ``store`` when ``table_id`` is omitted. |
| `table_id` | `str \| None` | No | `None` | Canonical governed table identity, mutually exclusive with physical coordinates. |
| `frequency_columns` | `sequence of str` | No | `None` | Columns to frequency profile. ``None`` automatically selects eligible scalar columns; an empty sequence skips frequency profiling. |
| `frequency_enabled` | `bool` | No | `True` | Whether to calculate frequency distributions for the table. False skips all frequency columns. |
| `frequency_top_n` | `int \| None` | No | `5` | Ranked values to retain per frequency column. ``None`` retains all. |
| `frequency_max_distinct_percent` | `float \| None` | No | `80.0` | Maximum distinct-per-non-null percentage for automatically selected columns. ``None`` disables the cardinality filter. |
| `spark_session` | `object` | No | `None` | Spark session to use. When omitted, FabricOps uses the supplied DataFrame session or resolves the active session. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

Profile an arbitrary DataFrame without persistence:

```python
result = profile_table(dataframe=raw_df)
statistical_profile = result["profile"]
frequencies = result["frequency_profile"]
```

Profile a governed complete physical table without knowing its store kind:

```python
result = profile_table(store="Bronze", schema="dbo", table_name="orders")
```

Profile a transformed DataFrame against an explicit governed identity:

```python
result = profile_table(dataframe=transformed_df, table_id=target_table_id)
```

</div>

## Returns

dict
    ``profile`` contains the canonical statistical Spark DataFrame and
    ``frequency_profile`` contains the applicable canonical frequency
    Spark DataFrame, or ``None`` when no columns were selected. Governed
    ``profile`` rows additionally contain persisted snapshot identities
    and audit fields.

### Return interpretation

Use result["profile"] for statistical rows and result["frequency_profile"] for selected frequency distributions. Governed rows include snapshot identities and audit fields; DataFrame-only calls do not write metadata.

## Raises / Errors

ValueError
    If identity inputs conflict or are incomplete, neither a DataFrame nor
    identity is supplied, frequency settings are invalid, or the resolved
    store is unsupported.
RuntimeError
    If a governed metadata write requires unavailable Delta support.

### Common failure causes

- Supply dataframe or a complete governed identity; do not mix table_id and physical coordinates.
- Selected frequency columns must exist. frequency_top_n limits retained values, not grouping cost.
- Governed profiling requires configured metadata routing, write permission, and Delta support.

## Notes

<div class="reference-docstring-notes" markdown="1">

The result also includes ``row_count``, reused from an existing aggregate
when available (None otherwise). No additional Spark job is run for this
metric. It describes the profiled dataset, not rows committed by a writer.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

FabricOps calculates the canonical statistical profile and applicable
frequency distribution close to the data. Supplied DataFrames and physical
Lakehouse tables use PySpark; physical Warehouse tables use SQL pushdown for
the calculations while normalizing reported ``DATA_TYPE`` values to the
canonical PySpark schema vocabulary used by downstream schema and Guardrail
checks. An identity may be supplied as a
canonical ``table_id`` or as ``store``, optional ``schema``, and
``table_name``. When an identity is present, FabricOps associates the
result with that governed table and persists Catalogue, profile, and
frequency metadata. Without an identity, the exact supplied DataFrame is
profiled without creating an identity or writing metadata.

</div>

## See also

- [Pipeline Execution](../../guided-demo/02-build-and-run-etl.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_table.py:1089`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_table.py#L1089-L1413">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

The orchestration performs these mechanical steps:

1. Validate and resolve the optional canonical governed identity.
2. Use the supplied DataFrame exactly, read a physical Lakehouse table into
   Spark, or keep physical Warehouse aggregation in Warehouse SQL.
3. Calculate canonical statistical metrics with the selected backend.
4. Select eligible frequency columns and calculate exact grouped counts,
   including null as a frequency value.
5. When governed, create stable table and column identities, replace rows
   in ``METADATA_DATA_PROFILED`` and
   ``METADATA_DATA_PROFILED_FREQUENCY`` idempotently for the current
   Fabric activity, then update
   ``METADATA_DATA_CATALOGUE``.
6. Return both profiling outputs. DataFrame-only mode performs no metadata
   writes and never invents a ``table_id``.

A retry in the same Fabric activity reuses the snapshot and row identities
and replaces that snapshot rather than appending duplicates. Catalogue is
updated only after both profile components succeed; its table-level
``_activity_id`` and non-null ``last_profiled_at`` identify the completed
snapshot for readers. A same-activity retry first clears that completion
marker. If a later stage fails, snapshot removal is best-effort hygiene:
Catalogue remains authoritative even if cleanup also fails, and the
original profiling error is preserved. A later activity receives a
distinct snapshot identity.

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 70 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.audit._audit_timestamp_value</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.pipeline.profile_table._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._automatic_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.profile_table._delete_profile_snapshot</code></li>
<li><code>fabricops_kit.pipeline.profile_table._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._key_candidate_evidence</code></li>
<li><code>fabricops_kit.pipeline.profile_table._key_candidate_payload</code></li>
<li><code>fabricops_kit.pipeline.profile_table._profile_snapshot_id</code></li>
<li><code>fabricops_kit.pipeline.profile_table._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_table._replace_snapshot_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_table._scalar_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._selected_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._spark_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.profile_table._sql_identifier</code></li>
<li><code>fabricops_kit.pipeline.profile_table._sql_string</code></li>
<li><code>fabricops_kit.pipeline.profile_table._stage_catalogue_profile_retry</code></li>
<li><code>fabricops_kit.pipeline.profile_table._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_frequency_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_percentile_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_profile_dataframes</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_profile_key_candidates</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_statistical_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_statistical_query</code></li>
<li><code>fabricops_kit.pipeline.profile_table._warehouse_type_name</code></li>
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

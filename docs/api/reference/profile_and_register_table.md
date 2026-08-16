# `profile_and_register_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile a Spark DataFrame, save a profiling snapshot, update catalogue records, and record source or target activity.

<div class="reference-docstring-intro" markdown="1">

One profiling invocation creates a shared ``profile_snapshot_id``. Each
eligible column receives one ``profile_id`` in ``METADATA_DATA_PROFILED``.
Its frequency distribution is produced in the same workflow and stored
separately as flattened rows in ``METADATA_DATA_PROFILED_FREQUENCY`` to
avoid embedding a large JSON distribution in the compact profile row.

Stable ``table_id`` and ``column_id`` values are environment-independent;
``environment_name`` keeps Development and Production observations
separate. Catalogue writes use that environment-aware grain, and Lineage
records whether the table participated as a pipeline source or target.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_and_register_table.py:506`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_table.py#L506-L630">View on GitHub</a>
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
def profile_and_register_table(
    df,
    profile_role,
    target,
    table_name,
    schema=None,
    frequency_columns=None,
    frequency_top_n: int | None=None,
    frequency_max_distinct_percent: float | None=80.0,
    frequency_profile_df=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
profiled_df = profile_and_register_table(source_df, profile_role="source", target="source", schema=SOURCE_SCHEMA, table_name="student_enrolment", frequency_profile_df=profile_sample_df)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `—` | Yes | Not documented yet |
| `profile_role` | `—` | Yes | Not documented yet |
| `target` | `—` | Yes | Not documented yet |
| `table_name` | `—` | Yes | Not documented yet |
| `schema` | `—` | No | Not documented yet |
| `frequency_columns` | `—` | No | Not documented yet |
| `frequency_top_n` | `int \| None` | No | Not documented yet |
| `frequency_max_distinct_percent` | `float \| None` | No | Not documented yet |
| `frequency_profile_df` | `—` | No | Not documented yet |

## Returns

Spark DataFrame containing one compact profiling summary row for each eligible column appended to METADATA_DATA_PROFILED, including stable identities, complete-DataFrame statistics, schema fingerprint, profiling timestamp, and runtime audit fields.

### Return interpretation

The returned rows are the compact parent summaries. Flattened frequency rows are written separately to METADATA_DATA_PROFILED_FREQUENCY and join to the returned rows through metadata_column_key; frequency, catalogue, and lineage rows are side effects and are not returned.

## Raises / Errors

Raises ValueError for an unsupported profile_role, unknown target, unsupported configured store kind, or invalid table or schema identity.

### Common failure causes

- profile_role must be source or target, or the configured target store kind is unsupported.
- target or table_name is blank, or a schema-enabled store has no explicit or configured schema.
- frequency_profile_df is not Spark DataFrame-like, uses an incompatible Spark session, or is missing selected frequency columns.
- The configured metadata target cannot be resolved or written.
- Requested frequency columns are missing or expensive to group; frequency_top_n limits returned values only and does not reduce grouping cost.
- If lineage registration fails after profile and catalogue writes succeed, RuntimeError is raised and earlier writes remain completed.

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
| Live-critical dependencies | 60 |

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
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._stable_metadata_key</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.build_metadata_column_key</code></li>
<li><code>fabricops_kit.config.shared.build_metadata_table_key</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.configured_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared.normalize_write_mode</code></li>
<li><code>fabricops_kit.io.shared.repartition_dataframe_for_write</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_delta_path</code></li>
<li><code>fabricops_kit.io.shared.write_lakehouse_table_core</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._automatic_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._lineage_event_id</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._normalize_choice</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._require_non_empty_string</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._resolve_physical_identity</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._scalar_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._selected_frequency_columns</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._upsert_catalogue_identities</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._upsert_lineage_event</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._validate_frequency_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
</ul>


</details>

# `profile_and_register_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile a Spark DataFrame, save a profiling snapshot, update catalogue records, and record source or target activity.

<div class="reference-docstring-intro" markdown="1">

The notebook supplies a Spark DataFrame and the table identity that the
DataFrame represents. FabricOps calculates one profiling result row for
each eligible column, saves a new profiling snapshot, creates stable table
and column IDs, updates or adds catalogue records, records whether the
table was used as an input or produced as an output, and returns the
profiling result to the notebook.

The original business DataFrame is not written, sampled, re-read, or
changed by this function. All metadata writes go to the metadata lakehouse
configured in ``00_env_config`` for the active environment.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_and_register_table.py:506`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_and_register_table.py#L506-L850">View on GitHub</a>
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
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile exactly as supplied by the caller. The helper does not sample, re-read, or mutate this DataFrame. |
| `profile_role` | `{"source", "target"}` | Yes | Records whether the profiled asset participated in the notebook activity as an input or an output: ``source`` for an activity input and ``target`` for an activity output. The value is recorded as ``pipeline_role`` in ``METADATA_DATA_LINEAGE`` rather than in ``METADATA_DATA_PROFILED`` or ``METADATA_DATA_CATALOGUE``. |
| `target` | `str` | Yes | Configured FabricStore target key. Its normalized key becomes the physical identity's layer and its store kind determines whether the asset is a Lakehouse or Warehouse table. |
| `table_name` | `str` | Yes | Physical table name of the business asset being profiled. This identifies the asset and does not redirect metadata writes. |
| `schema` | `str` | No | Physical schema name, or ``None`` to use the configured store default. Classic or schema-disabled Lakehouses preserve ``None``. |
| `frequency_columns` | `sequence of str` | No | Selected columns whose flattened frequency rows should be persisted. ``None`` profiles eligible non-technical scalar columns. An empty sequence skips frequency profiling entirely and writes no child rows. Requested columns should also be eligible for the main statistical profile. |
| `frequency_top_n` | `int \| None` | No | Optional number of ranked values to retain per selected frequency column. ``None`` retains every distinct value. |
| `frequency_max_distinct_percent` | `float \| None` | No | Automatic frequency-profiling safeguard used only when ``frequency_columns=None``. Columns whose distinct-per-non-null percentage is greater than this threshold are skipped and produce no child frequency rows. Values must be between ``0.0`` and ``100.0`` when supplied. ``None`` disables the high-cardinality threshold; all-null automatic columns remain skipped. Explicit ``frequency_columns`` selections override this threshold. |
| `frequency_profile_df` | `pyspark.sql.DataFrame` | No | Optional caller-provided Spark DataFrame to use only for frequency distribution calculation. ``None`` preserves full-source frequency profiling. When supplied, it must contain every selected frequency column, may contain extra columns, and must use a compatible Spark session when this can be determined. The caller is responsible for preparing, persisting, refreshing, and governing this DataFrame; this function does not verify whether it is random, representative, sampled, persisted, or otherwise suitable for the caller's purpose. |

## Returns

Spark DataFrame containing one compact profiling summary row for each eligible column appended to METADATA_DATA_PROFILED, including profile_id, profile_snapshot_id, stable table_id and column_id identities, environment_name, complete-DataFrame statistics, profiling timestamp, and runtime audit fields.

### Return interpretation

The returned rows are the compact parent summaries. Flattened frequency rows are written separately to METADATA_DATA_PROFILED_FREQUENCY, link to their parent through profile_id, and share the same profile_snapshot_id; frequency, catalogue, and lineage rows are side effects and are not returned.

## Raises / Errors

Raises ValueError for an unsupported profile_role, unknown target, unsupported configured store kind, or invalid table or schema identity.

### Common failure causes

- profile_role must be source or target, or the configured target store kind is unsupported.
- target or table_name is blank, or a schema-enabled store has no explicit or configured schema.
- frequency_profile_df is not Spark DataFrame-like, uses an incompatible Spark session, or is missing selected frequency columns.
- The configured metadata target cannot be resolved or written.
- Requested frequency columns are missing or expensive to group; frequency_top_n limits returned values only and does not reduce grouping cost.
- If lineage registration fails after profile and catalogue writes succeed, RuntimeError is raised and earlier writes remain completed.

## Notes

<div class="reference-docstring-notes" markdown="1">

Processing flow:

1. Build a statistical profile against the complete supplied DataFrame to
   produce one statistical profile row per eligible input column.
2. Use that statistical profile to choose automatic frequency columns
   when ``frequency_columns=None``: eligible scalar columns at or below
   ``frequency_max_distinct_percent`` are profiled, high-cardinality
   columns and all-null columns produce no child frequency rows. Explicit non-empty
   ``frequency_columns`` bypass this threshold, while
   ``frequency_columns=[]`` skips frequency profiling entirely.
3. Produce flattened frequency rows for the selected columns using the
   same calculation exposed by ``profile_frequency_distribution``.
4. Resolve each frequency row to its parent ``profile_id`` and shared
``profile_snapshot_id``.
5. Save the compact profiling snapshot to ``METADATA_DATA_PROFILED``.
6. Replace rows for the exact ``profile_snapshot_id`` child snapshot and
write the normalized rows to
   ``METADATA_DATA_PROFILED_FREQUENCY``.
7. Create stable table and column IDs, then update matching catalogue
   records or add new records in ``METADATA_DATA_CATALOGUE``.
8. Record whether the table was used as an input or produced as an output
   in ``METADATA_DATA_LINEAGE``.
9. Return only the compact parent Spark DataFrame written to
   ``METADATA_DATA_PROFILED``.

User-facing workflow:

Supplied DataFrame
    ↓
Calculate column statistics and value frequencies
    ↓
Save compact summary and flattened frequency snapshots
``METADATA_DATA_PROFILED`` + ``METADATA_DATA_PROFILED_FREQUENCY``
    ↓
Create stable table and column IDs
    ↓
Update existing catalogue records or add new ones
``METADATA_DATA_CATALOGUE``
    ↓
Record whether the table was used as an input or output
    ↓
``METADATA_DATA_LINEAGE``
    ↓
Return the profiling result to the notebook

Frequency snapshot behavior:

- Every eligible statistical profile row remains in the compact parent
  result whether or not that column produces child frequency rows.
- ``frequency_columns=None`` automatically profiles eligible non-technical
  scalar columns whose distinct-per-non-null percentage is less than or
  equal to ``frequency_max_distinct_percent``. The default threshold is
  ``80.0`` percent.
- Automatically selected columns above the threshold and all-null automatic
  columns produce no child frequency rows. No fake skipped values are stored.
- ``frequency_max_distinct_percent=None`` disables the high-cardinality
  threshold for automatic columns.
- Only columns listed in a non-empty ``frequency_columns`` sequence receive
  generated frequency evidence; explicit selections override the automatic
  threshold. Other profiled columns produce no child rows.
- ``frequency_columns=[]`` skips frequency profiling entirely and writes no
  child rows for the current snapshot.
- ``frequency_profile_df=None`` profiles frequencies against the complete
  supplied source DataFrame. When a caller supplies ``frequency_profile_df``,
  frequency counts, percentages, ranks, profiled row counts, and profiled
  non-null counts describe that caller-provided DataFrame. The compact
  parent statistics still describe the complete source DataFrame.
- ``frequency_top_n`` restricts persisted child rows only when supplied. It
  limits output rows after grouped counts are calculated and does not
  reduce grouping cost.
- Frequency values are ordered deterministically by rank.
- Historical parent and child rows join through ``profile_id``. Replacement
is scoped to the current ``profile_snapshot_id``, so earlier snapshots remain intact.

``METADATA_DATA_PROFILED`` receives one appended row per eligible input
DataFrame column. Repeated executions create additional profiling
snapshots, and the returned DataFrame is the same compact DataFrame
appended to this table. Its logical field groups are:

- Identity fields: ``profile_id``, ``profile_snapshot_id``, ``table_id``,
  ``column_id``, ``environment_name``, ``data_type``.
- Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
  ``null_percent``, ``distinct_count``, ``distinct_percent``,
  ``mean_value``, ``stddev_value``, ``min_value``,
  ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
  ``max_value``.
- Runtime field: ``profiled_at``.
- Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
  ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
  ``_metadata_lakehouse_name``, ``_activity_id``.

``METADATA_DATA_PROFILED`` saves a new compact profiling snapshot. One row
is saved for each eligible DataFrame column. ``METADATA_DATA_PROFILED_FREQUENCY``
saves one flattened row per returned distinct value. Earlier parent and child snapshots are retained. Frequency rows link to
their parent through ``profile_id`` and share the same ``profile_snapshot_id``.

``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
measurements. FabricOps creates a stable ID for the table and each column,
then checks whether the same logical asset already exists in the active
environment. If a matching record exists, it is updated. Otherwise, a new
record is added. Matching uses ``environment_name + metadata_level + table_id
+ column_id``. ``table_id`` and ``column_id`` are stable logical identities
shared across environments, while ``environment_name`` keeps Development and
Production observations separate. Column catalogue rows that disappear from a
new profile are retained but marked inactive rather than silently deleted.

``METADATA_DATA_LINEAGE`` records whether the table was used as an input
or produced as an output during the current notebook activity. A
``profile_role="source"`` value means the DataFrame was used as an input.
A ``profile_role="target"`` value means the DataFrame was produced as an
output. Lineage-specific fields are ``lineage_id``, ``table_id``,
``profile_snapshot_id``, ``environment_name``, ``pipeline_role``, and
``recorded_at``. The standard eight underscore
audit fields are the sole execution-context contract. ``recorded_at`` is the lineage participation time, while ``_committed_at``
is the metadata write time. ``lineage_id`` is deterministically derived from
``_activity_id``, ``table_id``, ``profile_snapshot_id``, and ``pipeline_role``.

What the notebook receives: a Spark DataFrame containing one profiling
result row for each eligible column.

What FabricOps saves:

- ``METADATA_DATA_PROFILED``: a new compact profiling snapshot.
- ``METADATA_DATA_PROFILED_FREQUENCY``: flattened frequency rows linked by
  ``profile_id`` and grouped by ``profile_snapshot_id``.
- ``METADATA_DATA_CATALOGUE``: updated or newly added table and column
  records.
- ``METADATA_DATA_LINEAGE``: the current source or target activity.

Statistical profiling records describe the complete DataFrame supplied
during the notebook activity. If ``frequency_profile_df`` is supplied,
only generated frequency evidence uses that DataFrame. The function does not claim or
verify that the caller-provided DataFrame is sampled, random,
representative, persisted, or governed; those responsibilities stay with
the upstream ingestion or notebook workflow.

The physical identity is the caller-selected configured table identity;
an arbitrary DataFrame does not prove that table exists. Profile a source
after a successful complete-table read, and profile a target only after
its write has succeeded and the persisted target has been confirmed.

Profile and catalogue registration occur before lineage registration. If
lineage registration fails after those writes succeed, the function raises
a ``RuntimeError`` explaining that profile and catalogue registration
succeeded but lineage registration failed. Guardrail execution is a
separate workflow.

This Stage 2 redesign changes the physical schemas for Catalogue, Profile,
Profile Frequency, Lineage, and Source Observation. Existing development
metadata tables may need recreation through the established setup flow; no
compatibility or automatic migration layer is provided.

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
<li><code>fabricops_kit.config.metadata_identity._build_column_id</code></li>
<li><code>fabricops_kit.config.metadata_identity._build_table_id</code></li>
<li><code>fabricops_kit.config.metadata_identity._stable_metadata_id</code></li>
<li><code>fabricops_kit.config.metadata_schemas._coerce_metadata_value</code></li>
<li><code>fabricops_kit.config.metadata_schemas.audit_schema_fields</code></li>
<li><code>fabricops_kit.config.metadata_schemas.build_metadata_schema</code></li>
<li><code>fabricops_kit.config.metadata_schemas.coerce_metadata_row_types</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_schema_registry</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
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
<li><code>fabricops_kit.pipeline.profile_and_register_table._lineage_id</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._normalize_choice</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._replace_frequency_rows</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._require_non_empty_string</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._resolve_physical_identity</code></li>
<li><code>fabricops_kit.pipeline.profile_and_register_table._scalar_frequency_columns</code></li>
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
